from aiogram import types, F
from aiogram.dispatcher.router import Router
from aiogram.filters import Command
from src.utils.tmdb import search_movie
from aiogram.types import Message

router = Router()

@router.message(Command('find'))
async def cmd_cl(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply("Пожалуйста, укажите название фильма после команды /find")
        return

    else:
        movie = args[1]
        await message.answer(movie)
