import asyncio
import re
import argparse
import yaml

from aiohttp.web import Response
from logging import config, getLogger, StreamHandler, INFO
from typing import Union, Set, Optional

from lina_community_version.core.server import Server
from lina_community_version.core.vkapi import VkApi
from lina_community_version.core.exceptions import VKException, \
    VkSendErrorException
from lina_community_version.core.messages import Confirmation, NewMessage
from lina_community_version.core.handlers import BaseMessageHandler


class Lina:
    _regexp_template = r'(^|\s)(\[club%s\|.+\]|%s)(,|\s|$)'

    def __init__(self):
        self._handler_class: Optional[BaseMessageHandler] = None
        self._handlers: Set[BaseMessageHandler] = set()
        parser = argparse.ArgumentParser()
        self.add_args(parser)
        self.args = parser.parse_args()
        self.cfg = self.read_config(self.args.cfg)
        if 'logger_name' in self.cfg and 'log_config' in self.cfg:
            log_config = self.cfg['log_config']
            config.dictConfig(log_config)
            self.logger = getLogger(self.cfg['logger_name'])
        else:
            self.logger = self.create_logger()
        self.logger.info(self.cfg)

        self.regexp_mention = re.compile(
            self._regexp_template %
            (self.cfg['group_id'], '|'.join(self.cfg['bot_names'])))

        self.server = Server(self)
        self.api = VkApi(self)

    @staticmethod
    def create_logger():
        logger = getLogger()
        logger.addHandler(StreamHandler())
        logger.setLevel(INFO)
        return logger

    def add_args(self, parser):
        parser.add_argument('-c', '--cfg', default='config.yml')
        parser.add_argument('--host', default='127.0.0.1')
        parser.add_argument('--port', default=13666, type=int)

    def setup_handler_class(self, handler_class: BaseMessageHandler):
        self._handler_class = handler_class

    def init_handlers(self):
        self._handlers = {handler(self) for handler in
                          self._handler_class.__subclasses__()}

    def read_config(self, path: str):
        with open(path) as stream:
            return yaml.load(stream)

    async def start(self):
        asyncio.create_task(self.server.start())
        self.init_handlers()

    async def process_message(self,
                              message: Union[Confirmation,
                                             NewMessage]) -> Response:
        self.logger.info('<-- recieved message: %s', message)
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
        if not re.search(self.regexp_mention, message.text):
            return  # message without bot mention
        message.raw_text = re.sub(self.regexp_mention, '', message.text)
        self.logger.info('raw text: %s', message.raw_text)
        await self._handle_new_message(message)

    async def _handle_new_message(self, message: NewMessage):
        for handler in self._handlers:
            try:
                await handler.handler(message)
            except VKException as e:
                self.logger.error('ERROR: ', e)
            except VkSendErrorException:
                await self.api.send_error_sticker(message.peer_id)

    async def add_handler(self, handler: BaseMessageHandler):
        self._handlers.add(handler)
