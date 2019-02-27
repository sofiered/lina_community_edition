import asyncio
import argparse
from aiohttp.web import Response

from lina_community_version.core.server import Server


class Lina:
    def __init__(self):
        self.server = Server(self)
        parser = argparse.ArgumentParser()
        self.add_args(parser)
        self.args = parser.parse_args()
        print(self.args)

    def add_args(self, parser):
        parser.add_argument('-c', default='config.yml')
        parser.add_argument('--host', default='127.0.0.1')
        parser.add_argument('--port', default=13666, type=int)

    async def start(self):
        asyncio.create_task(self.server.start())

    async def process_message(self, data):
        return Response(text='ok')
