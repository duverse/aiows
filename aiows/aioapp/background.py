# -*- coding: utf-8 -*-
from aiows.aioapp.queue import MessagePool


async def message_queue(app):
    """
    Initialize messages pool worker.
    :param app:
    :return:
    """
    app['mp'] = MessagePool()


tasks = (
    ('message_queue', message_queue),
)
