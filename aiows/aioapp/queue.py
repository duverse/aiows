# -*- coding: utf-8 -*-


class HandlerPool(object):
    """
    Channel subscribers manager.

    Allows to add or remove handler to specific channel as well,
    as trigger channel and publish specific package.
    """
    def __init__(self):
        self._handlers = {}

    def add_handler(self, channel, icid, handler):
        if channel not in self._handlers:
            self._handlers[channel] = {}
        self._handlers[channel][icid] = handler

        print('Registered new handler: {}'.format(icid))

    def remove_handler(self, channel, icid):
        if channel in self._handlers and icid in self._handlers[channel]:
            del self._handlers[channel][icid]

            if not len(self._handlers[channel]):
                del self._handlers[channel]

        print('Unregistered handler: {}'.format(icid))

    async def trigger_channel(self, channel, *args, **kwargs):
        print('Can not publish to {}'.format(channel))
        print(self._handlers)
        if channel not in self._handlers:
            return

        success, errors = (0, 0)

        for icid, send in self._handlers[channel].items():
            try:
                await send(*args, **kwargs)
                success += 1
            except Exception as e:
                errors += 1
                self.remove_handler(channel, icid)

        print('[{}] Published: {}'.format(channel, (success, errors)))

        return success, errors


class MessagePool(object):
    """
    Message manager.

    Allows to subscribe or unsubscribe client and publish messages.
    """
    def __init__(self, app):
        self.app = app
        self.queue = HandlerPool()

    def subscribe(self, channel, icid, handler):
        self.queue.add_handler(
            channel=self.clean_channel_name(channel),
            icid=icid,
            handler=handler
        )

    def unsubscribe(self, channel, icid):
        self.queue.remove_handler(
            channel=self.clean_channel_name(channel),
            icid=icid
        )

    async def publish(self, channel, content, package_type='text'):
        channel = self.clean_channel_name(channel)
        return await self.queue.trigger_channel(channel, content, package_type)

    @classmethod
    def clean_channel_name(cls, name):
        if isinstance(name, bytes):
            name = name.decode('utf-8')

        return name.strip().lower().replace('_', ':') if name else '__all__'
