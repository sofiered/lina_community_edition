import asyncio

from lina_community_version.lina.bot import Lina
from lina_community_version.lina.handlers import LinaNewMessageHandler

async def main():
    lina = Lina()
    lina.setup_handler_class(LinaNewMessageHandler)
    await lina.start()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()