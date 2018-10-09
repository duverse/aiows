# -*- coding: utf-8 -*-
from random import randint

import aiohttp
from aiohttp import web

from aiows.aioapp.publisher import WSPublisher


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
    # Check request password
    password = request.query.get('pwd')
    if request.app['pwd'] and password != request.app['pwd']:
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

        await mm.publish(
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
    password = request.query.get('pwd')
    if request.app['pwd'] and password != request.app['pwd']:
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
                await mm.publish(channel, content, package_type)

        return web.Response(
            body='"OK"',
            status=201,
            content_type='application/json'
        )
    except Exception as e:
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
    mm = request.app['mp']
    channel_name = request.match_info['channel']

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Create internal connection id
    icid = '{}:{}'.format(channel_name, randint(0, 99999999))

    # Subscribe to a channel
    mm.subscribe(channel_name, icid, WSPublisher(ws))

    # Subscribe client messages
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                    print('[ws:{}] Closing connection: {}'.format(icid, ws))
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('[ws:{}] Connection closed with exception: {}'.format(icid, ws.exception()))
    except Exception as e:
        print('[ws:{}] {}: {}'.format(icid, type(e).__name__, str(e)))

    # Closing connection
    try:
        mm.unsubscribe(channel_name, icid)
    except Exception as e:
        print(e)

    return ws
