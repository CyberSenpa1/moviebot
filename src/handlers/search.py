from aiogram import types
from aiogram.dispatcher.router import Router
from src.utils.tmdb import search_movie

router = Router()

async def find_movie(message: types.Message):
    query = ' '.join(message.get_args())
    if not query:
        await message.reply("Введите название фильма после команды /find.")
        return

    movie = await search_movie(query)
    if movie:
        await message.reply(f"🎬 {movie['title']} ({movie['release_date']})\n\n{movie['overview']}\n\n{movie['poster_url']}")
    else:
        await message.reply("Фильм не найден.")
