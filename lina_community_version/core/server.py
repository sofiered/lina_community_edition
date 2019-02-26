import asyncio
from aiohttp.web import Application, Response, AppRunner, View, view, TCPSite


class VerificationView(View):
    async def post(self):
        return Response(text='2d840b43')


ROUTES = (view('/verification', VerificationView),)


class Server:
    def __init__(self):
        self.app = Application(loop=asyncio.get_event_loop())
        self.app.add_routes(ROUTES)

        self.runner = AppRunner(self.app)
        self.loop = asyncio.get_event_loop()

        self.server = None

    async def start(self):
        print('create server')
        await self.runner.setup()
        self.server = await self.loop.create_server(self.runner.server,
                                                    'localhost',
                                                    13444)

    async def stop(self):
        await self.runner.shutdown()
