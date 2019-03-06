from abc import ABC, abstractmethod
from aiohttp import web

from .messages import message_factory, NewMessage


class VkCallback(web.View):
    @property
    def owner(self):
        return self.request.config_dict['owner']

    async def post(self) -> web.Response:
        data = await self.request.json()
        message = message_factory(data.get('type'),
                                  data.get('object', dict()))
        return await self.owner.process_message(message)


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
