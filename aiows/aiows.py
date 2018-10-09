# -*- coding: utf-8 -*-
import uuid
import argparse

from aiohttp import web


def set_session(app):
    """
    Sets unique session ID
    :param app:
    :return:
    """
    app['ssid'] = 's{}'.format(str(uuid.uuid4())[:8])
    print('[APP] Session: {}'.format(app['ssid']))


def set_push_password(app, pwd):
    """
    Sets push notifications action password
    :param app:
    :return:
    """
    app['pwd'] = pwd
    print('[APP] Push password: "{}"'.format(pwd or 'not set'))


def load_settings(app, args):
    """
    Define application settings
    :param app:
    :param args:
    :return:
    """
    app['args'] = args


def load_urls(app):
    """
    Load applications routes
    :param app:
    :return:
    """
    from aiows.aioapp.urls import patterns
    for method, pattern in patterns:
        pattern[0] = app['args'].url_prefix + pattern[0]
        getattr(app.router, 'add_{method}'.format(method=method))(*pattern)


def load_tasks(app):
    """
    Register applications background tasks
    :param app:
    :return:
    """
    from aiows.aioapp.background import tasks

    async def bg_start(root):
        for identify, callback in tasks:
            if isinstance(callback, str):
                callback = getattr(tasks, callback)
            root[identify] = root.loop.create_task(callback(root))

    async def bg_stop(root):
        for identify, callback in tasks:
            root[identify].cancel()
            await root[identify]

    app.on_startup.append(bg_start)
    app.on_cleanup.append(bg_stop)


def main():
    # Define arguments
    parser = argparse.ArgumentParser(description="AIOHttp WebSocket server")
    parser.add_argument('--pwd', type=str, default=None, help='Password to be able to publish messages.')

    parser.add_argument('--usock', type=str, default=None, help='UNIX Socket file for aiows server')
    parser.add_argument('--host', type=str, default=None, help='Server host')
    parser.add_argument('--port', type=int, default=None, help='Server port')
    parser.add_argument('--reuse-addr', type=int, default=1, help='Reuse host')
    parser.add_argument('--reuse-port', type=int, default=1, help='Reuse port')
    parser.add_argument('--url-prefix', type=str, default='', help='API Endpoints prefix')

    # Parse arguments
    args = parser.parse_args()

    # Create application
    app = web.Application()

    # Register settings
    load_settings(app, args)

    # Set running session
    set_session(app)

    # Register routes
    load_urls(app)

    # Register background tasks
    load_tasks(app)

    # Set push password
    set_push_password(app, args.pwd)

    # Run server
    web.run_app(
        app=app,
        path=args.usock,
        host=args.host,
        port=args.port,
        reuse_address=args.reuse_addr,
        reuse_port=args.reuse_port
    )
