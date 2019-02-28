import asyncio
from aiohttp.web import Application, AppRunner, view
from lina_community_version.lina.handlers import VkCallback
from .middleware import check_group_middleware

ROUTES = (view('/8moidkh1/callback', VkCallback),)  # type: ignore


class Server:
    def __init__(self, owner):
        self.owner = owner
        self.app = Application(middlewares=[check_group_middleware])
        self.app['owner'] = self.owner
        self.app.add_routes(ROUTES)

        self.runner = AppRunner(self.app)
        self.loop = asyncio.get_event_loop()

        self.server = None

    async def start(self):
        print('create server')
        await self.runner.setup()
        self.server = await self.loop.create_server(self.runner.server,
                                                    self.owner.args.host,
                                                    self.owner.args.port)

    async def stop(self):
        await self.runner.shutdown()
