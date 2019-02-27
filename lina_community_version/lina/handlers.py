from aiohttp import web


class BaseView(web.View):
    @property
    def owner(self):
        return self.request.config_dict['owner']


class VkCallback(BaseView):
    async def post(self) -> web.Response:
        data = await self.request.json()
        return await self.owner.process_message(data)
