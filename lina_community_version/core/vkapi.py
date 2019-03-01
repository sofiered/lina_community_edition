from typing import Optional
from aiovk import API, TokenSession

from aiohttp import ClientSession


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
        self.api: Optional[API] = None

    async def start(self):
        self.api = API(self.session)
