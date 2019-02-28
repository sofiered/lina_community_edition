import asyncio
from dataclasses import asdict
import argparse
import yaml

from aiohttp.web import Response
from typing import Union

from lina_community_version.core.server import Server
from .messages import Confirmation, NewMessage


class Lina:
    def __init__(self):
        self.server = Server(self)
        parser = argparse.ArgumentParser()
        self.add_args(parser)
        self.args = parser.parse_args()
        self.cfg = self.read_config(self.args.cfg)
        print(self.cfg)

    def add_args(self, parser):
        parser.add_argument('-c', '--cfg', default='config.yml')
        parser.add_argument('--host', default='127.0.0.1')
        parser.add_argument('--port', default=13666, type=int)

    def read_config(self, path: str):
        with open(path) as stream:
            return yaml.load(stream)

    async def start(self):
        asyncio.create_task(self.server.start())

    async def process_message(self,
                              message: Union[Confirmation,
                                             NewMessage]) -> Response:
        if isinstance(message, Confirmation):
            return await self.process_confirmation_message(message)
        elif isinstance(message, NewMessage):
            return await self.process_new_message(message)
        else:
            raise ValueError

    async def process_confirmation_message(self,
                                           _message: Confirmation) -> Response:
        return Response(text=self.cfg['confirmation_code'])

    async def process_new_message(self, message: NewMessage) -> Response:
        await self._process_new_message(message)
        return Response(text='ok')

    async def _process_new_message(self, message: NewMessage) -> None:
        print(asdict(message))
