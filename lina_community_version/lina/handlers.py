from typing import Optional, TYPE_CHECKING

from lina_community_version.core.handlers import BaseMessageHandler
from lina_community_version.core.messages import NewMessage

if TYPE_CHECKING:
    from lina_community_version.lina.bot import Lina


class LinaNewMessageHandler(BaseMessageHandler):
    def __init__(self, service: 'Lina') -> None:
        self.service = service

    trigger_word: Optional[str] = None

    async def is_triggered(self, message: NewMessage) -> bool:
        raise NotImplementedError

    async def _handler(self, message: NewMessage):
        raise NotImplementedError


class PingPongMessageHandler(LinaNewMessageHandler):
    trigger_word = 'ping'

    async def is_triggered(self, message: NewMessage) -> bool:
        if self.trigger_word is None or message.raw_text is None:
            return False
        else:
            return self.trigger_word in message.raw_text

    async def _handler(self, message: NewMessage):
        await self.service.api.send_message(peer_id=message.peer_id,
                                            message='pong')
