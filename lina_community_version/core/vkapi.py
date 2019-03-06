from random import randint
from typing import List
from aiohttp import ClientSession
from aiovk import API, TokenSession

from .profiles import UserProfile


class VKException(Exception):
    def __init__(self, error_text: str, error_code: int) -> None:
        super().__init__(error_text)
        self.code = error_code


def vk_exception(func):
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
    def __init__(self, token: str) -> None:
        self.token = token
        self.session = LinaTokenSession(access_token=token)
        self.api: API = API(self.session)

    async def send_message(self, peer_id: int, message: str):
        await self.api.messages.send(peer_id=peer_id,
                                     message=message,
                                     random_id=randint(10000, 99999))

    async def send_sticker(self, peer_id: int, sticker_id: int):
        await self.api.messages.send(peer_id=peer_id,
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
