# -*- coding: utf-8 -*-
import json


class WSPublisher(object):
    """
    WebSocket connection publisher.

    This class helps to filter input options and data.
    """
    TYPE_JSON = 'json'
    TYPE_BYTES = 'bytes'
    TYPE_TEXT = 'text'
    AVAILABLE_TYPES = (
        TYPE_BYTES,
        TYPE_TEXT,
        TYPE_JSON
    )

    def __init__(self, icid, ws):
        self.icid = icid
        self.ws = ws

    def __str__(self):
        return '<WSPublisher /{}>'.format(self.icid)

    def __repr__(self):
        return str(self)

    async def __call__(self, content, package_type=TYPE_TEXT):
        if package_type not in self.AVAILABLE_TYPES:
            raise TypeError('Can not send undefined WS type.')

        return await getattr(self, 'send_{}'.format(package_type))(content)

    async def send_json(self, data):
        return await self.ws.send_json(json.dumps(data))

    async def send_text(self, data):
        return await self.ws.send_str(data)

    async def send_bytes(self, data):
        return await self.ws.send_bytes(data)
