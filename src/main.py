import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from os import getenv

logging.basicConfig(level=logging.INFO)

bot = Bot(token=getenv('BOT_TOKEN'))
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.username}")

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
