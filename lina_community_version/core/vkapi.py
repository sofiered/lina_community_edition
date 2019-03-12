from random import randint
from typing import List, Callable, Awaitable, Any, Dict
from aiohttp import ClientSession
from aiovk import API, TokenSession

from .profiles import UserProfile
from .exceptions import VKException


def vk_exception(func: Callable[..., Awaitable[Dict[str, Any]]]):
    async def wrapped_func(*args, **kwargs):
        result = await func(*args, **kwargs)
        if 'error' in result:
            raise VKException(result['error']['error_msg'],
                              result['error']['error_code'])
        else:
            return result

    return wrapped_func


class LinaTokenSession(TokenSession):
    API_VERSION = '5.92'

    async def send_api_request(self,
                               method_name: str,
                               params: dict = None,
                               timeout: int = None) -> dict:
        # Prepare request
        if not timeout:
            timeout = self.timeout
        if not params:
            params = {}
        if self.access_token:
            params['access_token'] = self.access_token
        params['v'] = self.API_VERSION

        # Send request
        async with ClientSession() as session:
            async with session.get(
                    self.REQUEST_URL + method_name,
                    params=params or {},
                    timeout=timeout or self.timeout) as response:
                return await response.json()


class VkApi:
    def __init__(self, owner) -> None:
        self.owner = owner
        self.token = self.owner.cfg['token']
        self.session = LinaTokenSession(access_token=self.token)
        self.api: API = API(self.session)

    @vk_exception
    async def send_message(self,
                           peer_id: int,
                           message: str) -> Dict[str, Any]:
        self.owner.logger.info(
            '--> send message: peer_id %s, message %s' % (peer_id,
                                                          message))
        return await self.api.messages.send(peer_id=peer_id,
                                            message=message,
                                            random_id=randint(10000, 99999))

    @vk_exception
    async def send_sticker(self, peer_id: int, sticker_id: int):
        self.owner.logger.info(
            '--> send sticker: peer_id %s, sticker_id %s' % (peer_id,
                                                             sticker_id))
        return await self.api.messages.send(peer_id=peer_id,
                                            sticker_id=sticker_id,
                                            random_id=randint(10000, 99999))

    @vk_exception
    async def _get_conversation_members(self, peer_id: int):
        return await self.api.messages.getConversationMembers(peer_id=peer_id)

    async def get_conversation_members(self,
                                       peer_id: int) -> List[UserProfile]:
        response = await self._get_conversation_members(peer_id=peer_id)
        return [UserProfile(**data) for data in
                response['response']['profiles']]

    async def send_error_sticker(self, peer_id: int):
        await self.send_sticker(peer_id=peer_id,
                                sticker_id=8471)
