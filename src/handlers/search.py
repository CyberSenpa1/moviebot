from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import requests
import logging
import random
from os import getenv
from typing import Dict, Any, Optional

router = Router()
HEADERS = {"X-API-KEY": getenv("KNP_TOKEN")}
KINOPOISK_API_URL = "https://kinopoiskapiunofficial.tech/api"

# Состояния для FSM
class MovieStates(StatesGroup):
    waiting_for_title = State()

# Основные жанры
MAIN_GENRES = {
    "комедия": 13,
    "драма": 2,
    "боевик": 11,
    "фантастика": 6,
    "ужасы": 17,
    "триллер": 1,
    "мелодрама": 4,
    "детектив": 5,
    "мультфильм": 18,
    "фэнтези": 12
}

def normalize_film_data(film_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Нормализация данных фильма из разных API endpoints"""
    if not film_data:
        return None
    
    # Данные из поиска (v2.1)
    if 'filmId' in film_data or 'kinopoiskId' in film_data:
        return {
            'id': str(film_data.get('filmId') or film_data.get('kinopoiskId')),
            'name': film_data.get('nameRu') or film_data.get('nameEn') or 'Без названия',
            'year': film_data.get('year', ''),
            'rating': film_data.get('rating', 'нет данных'),
            'poster': film_data.get('posterUrlPreview') or film_data.get('posterUrl')
        }
    
    # Данные из детальной информации (v2.2)
    if 'kinopoiskId' in film_data:
        return {
            'id': str(film_data.get('kinopoiskId')),
            'name': film_data.get('nameRu') or film_data.get('nameOriginal') or 'Без названия',
            'year': film_data.get('year', ''),
            'rating': film_data.get('ratingKinopoisk') or film_data.get('ratingImdb') or 'нет данных',
            'poster': film_data.get('posterUrlPreview') or film_data.get('posterUrl')
        }
    
    return None

async def search_movies(title: str) -> list[Dict[str, Any]]:
    """Поиск фильмов по названию"""
    try:
        response = requests.get(
            f"{KINOPOISK_API_URL}/v2.1/films/search-by-keyword",
            headers=HEADERS,
            params={"keyword": title, "page": 1}
        )
        response.raise_for_status()
        
        films = []
        for film in response.json().get('films', [])[:5]:
            if normalized := normalize_film_data(film):
                films.append(normalized)
        
        return films
    except Exception as e:
        logging.error(f"Ошибка поиска: {str(e)}")
        return []

async def get_movie_details(film_id: str) -> Optional[Dict[str, Any]]:
    """Получение деталей фильма по ID"""
    try:
        response = requests.get(
            f"{KINOPOISK_API_URL}/v2.2/films/{film_id}",
            headers=HEADERS
        )
        response.raise_for_status()
        return normalize_film_data(response.json())
    except Exception as e:
        logging.error(f"Ошибка получения фильма: {str(e)}")
        return None

async def get_random_movie(genre: str = None) -> Optional[Dict[str, Any]]:
    """Получение случайного фильма (опционально по жанру)"""
    try:
        params = {
            "order": "RATING",
            "type": "FILM",
            "page": random.randint(1, 5)
        }
        
        if genre and genre in MAIN_GENRES:
            params["genre"] = MAIN_GENRES[genre]
        
        response = requests.get(
            f"{KINOPOISK_API_URL}/v2.1/films/search-by-filters",
            headers=HEADERS,
            params=params
        )
        response.raise_for_status()
        
        films = response.json().get('films', [])
        if films:
            return normalize_film_data(random.choice(films))
        
        return None
    except Exception as e:
        logging.error(f"Ошибка случайного фильма: {str(e)}")
        return None

async def send_movie_info(message: Message, film: Dict[str, Any]):
    """Отправка информации о фильме"""
    if not film:
        await message.answer("Информация о фильме недоступна")
        return
    
    info = [
        f"🎬 {film['name']}",
        f"📅 Год: {film['year']}" if film.get('year') else "",
        f"⭐ Рейтинг: {film['rating']}",
        f"🔗 https://www.kinopoisk.ru/film/{film['id']}/"
    ]
    
    caption = "\n".join(filter(None, info))
    
    try:
        if film.get('poster'):
            await message.answer_photo(film['poster'], caption=caption)
        else:
            await message.answer(caption)
    except Exception as e:
        logging.error(f"Ошибка отправки: {str(e)}")
        await message.answer(caption)

# Обработчики для поиска по названию
@router.callback_query(F.data == "find_movie")
async def start_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название фильма:")
    await state.set_state(MovieStates.waiting_for_title)
    await callback.answer()

@router.message(MovieStates.waiting_for_title)
async def process_search(message: Message, state: FSMContext):
    title = message.text.strip()
    if len(title) < 2:
        await message.answer("Введите минимум 2 символа")
        return
    
    await message.answer("🔍 Ищем фильмы...")
    films = await search_movies(title)
    
    if not films:
        await message.answer("Ничего не найдено")
    elif len(films) == 1:
        await send_movie_info(message, films[0])
    else:
        builder = InlineKeyboardBuilder()
        for film in films:
            text = f"{film['name']}"
            if film.get('year'):
                text += f" ({film['year']})"
            builder.button(text=text, callback_data=f"film_{film['id']}")
        
        builder.adjust(1)
        await message.answer("Выберите фильм:", reply_markup=builder.as_markup())
    
    await state.clear()

@router.callback_query(F.data.startswith("film_"))
async def show_movie_details(callback: CallbackQuery):
    film_id = callback.data.split("_")[1]
    film = await get_movie_details(film_id)
    
    if film:
        await send_movie_info(callback.message, film)
    else:
        await callback.message.answer("Не удалось загрузить информацию о фильме")
    
    await callback.answer()

# Обработчики для работы с жанрами
@router.callback_query(F.data == "random_movie")
async def send_random_movie_handler(callback: CallbackQuery):
    film = await get_random_movie()
    if film:
        await send_movie_info(callback.message, film)
    else:
        await callback.message.answer("Не удалось найти случайный фильм")
    await callback.answer()

@router.callback_query(F.data == "random_movie_genre")
async def show_genres_handler(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    for genre in MAIN_GENRES:
        builder.button(text=genre.capitalize(), callback_data=f"genre_{genre}")
    builder.adjust(2)
    await callback.message.answer("Выберите жанр:", reply_markup=builder.as_markup())
    await callback.answer()

@router.callback_query(F.data.startswith("genre_"))
async def send_movie_by_genre_handler(callback: CallbackQuery):
    genre = callback.data.split("_")[1]
    film = await get_random_movie(genre)
    if film:
        await send_movie_info(callback.message, film)
    else:
        await callback.message.answer(f"Не удалось найти фильм в жанре {genre}")
    await callback.answer()