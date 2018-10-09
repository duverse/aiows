# -*- coding: utf-8 -*-
import logging
from random import randint

import aiohttp
from aiohttp import web

from aiows.aioapp.publisher import WSPublisher


log = logging.getLogger('aiows.api')


async def channel_publish(request):
    """
    Publisher endpoint.

      Request Headers:
       - Package-Type(Text/bytes/json) - which type of package will be sent.

      Query Params:
       - pwd(str) - publishing password (by default: None)

      Request body:
       - any(bytes) - publishing message

      Responses:
       - 403 - Wrong password
       - 400 - Failed to read request body
       - 201 - Published

    :param request:
    :return:
    """
    host, port = request.transport.get_extra_info('peername') or ('Unknown', 'Unknown')
    log.info('[SHARE][{}] {}:{}'.format(request.path, host, port))

    # Check request password
    password = request.query.get('pwd')
    if request.app['pwd'] and password != request.app['pwd']:
        log.warning('Invalid publisher password "{}"'.format(password))
        return web.Response(
            body='"Not authorized"',
            status=403,
            content_type='application/json'
        )

    # Recognize sending package type
    package_type = request.headers.get('package-type', WSPublisher.TYPE_TEXT).lower()

    # Publish message
    mm = request.app['mp']
    try:
        if package_type == WSPublisher.TYPE_TEXT:
            message = await request.text()
        elif package_type == WSPublisher.TYPE_JSON:
            message = await request.json()
        else:
            message = await request.read()

        await mm.share(
            channel=request.match_info['channel'],
            content=message,
            package_type=package_type
        )

        return web.Response(
            body='"OK"',
            status=201,
            content_type='application/json'
        )
    except Exception as e:
        log.error('Bad request', exc_info=True)
        return web.Response(
            body='"Bad request"',
            status=400,
            content_type='application/json'
        )


async def channel_publish_bulk(request):
    """
    Bulk publisher endpoint.

      Query Params:
       - pwd(str) - publishing password (by default: None)

      Request body:
       - json(str) - publishing channels and messages as key=>value. Example:

            {
                "room:1": [{"text": "Hi all"}],
                "user:22": [{"json": {"notification": "You've got new friend"}}],
                "video:stream": [{"bytes": "\x031\x032\x033..."}, {"bytes": "\x031\x032\x033..."}]
            }

      Responses:
       - 403 - Wrong password
       - 400 - Failed to read request body
       - 201 - Published

    :param request:
    :return:
    """
    host, port = request.transport.get_extra_info('peername') or ('Unknown', 'Unknown')
    log.info('[SHARE][{}] {}:{}'.format(request.path, host, port))

    password = request.query.get('pwd')
    if request.app['pwd'] and password != request.app['pwd']:
        log.warning('Invalid publisher password "{}"'.format(password))
        return web.Response(
            body='"Not authorized"',
            status=403,
            content_type='application/json'
        )

    try:
        data = await request.json()

        mm = request.app['mp']
        for channel, messages in data.items():
            for pack in messages:
                package_type, content = pack.items()[0]
                await mm.share(channel, content, package_type)

        return web.Response(
            body='"OK"',
            status=201,
            content_type='application/json'
        )
    except Exception as e:
        log.error('Bad request', exc_info=True)
        return web.Response(
            body='"Bad request"',
            status=400,
            content_type='application/json'
        )


async def channel_subscribe(request):
    """
    WebSockets subscribe endpoint.

      URL Params:
       - channel_name - channel to subscribe

    :param request:
    :return:
    """
    host, port = request.transport.get_extra_info('peername') or ('Unknown', 'Unknown')
    log.info('[LISTEN][{}] {}:{}'.format(request.path, host, port))

    mm = request.app['mp']
    channel_name = request.match_info['channel']

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Create internal connection id
    icid = '{}:{}'.format(channel_name, randint(0, 99999999))

    # Subscribe to a channel
    mm.subscribe(channel_name, icid, WSPublisher(icid, ws))
    log.debug('[{}] Created new handler'.format(icid))

    # Subscribe client messages
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                    log.info('[{}] Connection closed'.format(icid))
            elif msg.type == aiohttp.WSMsgType.ERROR:
                log.error('[{}] Connection closed with exception: {}'.format(icid, str(ws.exception())))
    except Exception as e:
        log.error('[{}] Connection broken'.format(icid), exc_info=True)

    # Closing connection
    try:
        mm.unsubscribe(channel_name, icid)
    except Exception as e:
        log.error('[{}] Failed to unsubscribe listener'.format(icid), exc_info=True)

    return ws
