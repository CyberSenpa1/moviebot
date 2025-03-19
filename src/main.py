import logging
import asyncio

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

from os import getenv

from handlers import start, search


logging.basicConfig(level=logging.INFO)

bot = Bot(token=getenv('BOT_TOKEN'))


async def main():
    dp = Dispatcher()

    dp.include_routers(start.router, search.router)

    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())
