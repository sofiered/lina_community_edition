import asyncio

from lina_community_version.core.server import Server


class Lina:
    def __init__(self):
        self.server = Server()

    async def start(self):
        asyncio.create_task(self.server.start())
        print('111')
