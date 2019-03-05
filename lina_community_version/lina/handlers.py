from aiohttp import web

from .messages import message_factory


class VkCallback(web.View):
    @property
    def owner(self):
        return self.request.config_dict['owner']

    async def post(self) -> web.Response:
        data = await self.request.json()
        message = message_factory(data.get('type'),
                                  data.get('object', dict()))
        return await self.owner.process_message(message)
