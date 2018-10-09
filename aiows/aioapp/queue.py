# -*- coding: utf-8 -*-
import logging


log = logging.getLogger('aiows.queue')


class MessagePool(object):
    """
    Message pool manager.

    Allows to add or remove handler to specific channel as well,
    as trigger channel and publish specific package.
    """
    def __init__(self):
        self._handlers = {}

    def subscribe(self, channel, icid, handler):
        channel = self.clean_channel_name(channel)
        if channel not in self._handlers:
            self._handlers[channel] = {}
        self._handlers[channel][icid] = handler

    def unsubscribe(self, channel, icid):
        channel = self.clean_channel_name(channel)
        if channel in self._handlers and icid in self._handlers[channel]:
            del self._handlers[channel][icid]

            if not len(self._handlers[channel]):
                del self._handlers[channel]

    async def share(self, channel, *args, **kwargs):
        channel = self.clean_channel_name(channel)
        if channel not in self._handlers:
            return

        # Sharing package
        success, errors = (0, 0)
        unsubscribe = []

        for icid, send in self._handlers[channel].items():
            try:
                await send(*args, **kwargs)
                success += 1
            except Exception as e:
                unsubscribe.append(icid)
                errors += 1

        # Removing invalid channels
        for icid in unsubscribe:
            self.unsubscribe(channel, icid)

        log.debug('[] Published: {} / {}'.format(channel, args, kwargs))

        return success, errors

    @classmethod
    def clean_channel_name(cls, name):
        if isinstance(name, bytes):
            name = name.decode('utf-8')

        return name.strip().lower().replace('_', ':') if name else '__all__'
