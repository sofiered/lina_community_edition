import asyncio

from lina_community_version.lina.bot import Lina

async def main():
    lina = Lina()
    await lina.start()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.run_forever()