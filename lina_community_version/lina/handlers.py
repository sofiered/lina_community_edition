from random import SystemRandom
from typing import Optional, TYPE_CHECKING

from lina_community_version.core.handlers import BaseMessageHandler
from lina_community_version.core.messages import NewMessage
from lina_community_version.core.exceptions import VkSendErrorException

if TYPE_CHECKING:
    from lina_community_version.lina.bot import Lina


class LinaNewMessageHandler(BaseMessageHandler):
    def __init__(self, service: 'Lina') -> None:
        self.service = service

    trigger_word: Optional[str] = None

    async def is_triggered(self, message: NewMessage) -> bool:
        if self.trigger_word is None or message.raw_text is None:
            return False
        else:
            return self.trigger_word in message.raw_text

    async def _handler(self, message: NewMessage):
        await self.service.api.send_message(
            peer_id=message.peer_id,
            message=await self.get_content(message))

    async def get_content(self, message: NewMessage):
        raise NotImplementedError


class PingPongMessageHandler(LinaNewMessageHandler):
    trigger_word = 'ping'

    async def get_content(self, message: NewMessage):
        return 'pong'


class SimpleDiceMessageHandler(LinaNewMessageHandler):
    trigger_word = 'дайс'

    async def get_content(self, _message: NewMessage):
        return SystemRandom().randint(1, 20)


class RaiseErrorMessageHandler(LinaNewMessageHandler):
    trigger_word = 'умри'

    async def get_content(self, message: NewMessage):
        raise VkSendErrorException
