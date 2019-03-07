import asyncio
from aiohttp.web import Application, AppRunner, view
from lina_community_version.core.handlers import VkCallback
from .middleware import check_group_middleware


class Server:
    def __init__(self, owner):
        self.owner = owner
        self.app = Application(middlewares=[check_group_middleware])
        self.app['owner'] = self.owner
        self.app.add_routes(
            (view('/%s/%s/callback' % (owner.cfg['env'],
                                       owner.cfg['callback_code']),
                  VkCallback),))  # type: ignore

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
