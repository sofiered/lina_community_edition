from abc import ABC, abstractmethod
from aiohttp import web
from logging import Logger

from .messages import message_factory, NewMessage


class VkCallback(web.View):
    @property
    def owner(self):
        return self.request.config_dict['owner']

    @property
    def logger(self) -> Logger:
        return self.owner.logger

    async def post(self) -> web.Response:
        data = await self.request.json()
        try:
            message = message_factory(data.get('type'),
                                      data.get('object', dict()))
            return await self.owner.process_message(message)
        except (TypeError, ValueError):
            self.logger.exception('Error with data: %s', data)
            return web.Response(status=504)


class BaseMessageHandler(ABC):
    @abstractmethod
    async def is_triggered(self, message: NewMessage) -> bool:
        ...

    @abstractmethod
    async def _handler(self, message: NewMessage):
        ...

    async def handler(self, message: NewMessage):
        if not await self.is_triggered(message):
            return
        await self._handler(message)
