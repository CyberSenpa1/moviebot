from aiogram.dispatcher.router import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(f'Вас приветствует - moviebot!')
    