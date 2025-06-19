import requests
import random
import logging
from os import getenv
from typing import Dict, Any, Optional, List

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()
HEADERS = {"X-API-KEY": getenv("KNP_API")}
KINOPOISK_API_URL = "https://api.kinopoisk.dev/v1.4"

class MovieStates(StatesGroup):
    waiting_for_title = State()


MAIN_GENRES = {
    "фантастика": "sci-fi",
    "комедия": "comedy",
    "боевик": "action",
    "драма": "drama",
    "ужасы": "horror"
}

async def get_random_movie(genre: str = None) -> Optional[Dict[str, Any]]:
    logging.debug(f"Searching for genre: {genre}")
    try:
        # Базовые параметры запроса
        params = {
            "limit": 10,
            "selectFields": ["id", "name", "year", "rating", "genres", "poster"],
            "type": "movie",
            "notNullFields": ["name", "poster.url"]
        }
        
        if genre:
            # Исправлено: передаем жанр как строку, а не список
            params["genres.name"] = genre
            
        # Логируем URL перед запросом для отладки
        logging.debug(f"Request params: {params}")
        
        response = requests.get(
            f"{KINOPOISK_API_URL}/movie",
            headers=HEADERS,
            params=params,
            timeout=15
        )
        
        logging.debug(f"Full request URL: {response.url}")
        logging.debug(f"Response status: {response.status_code}")
        
        if response.status_code == 400:
            error_data = response.json()
            logging.error(f"API validation error: {error_data}")
            return None
            
        response.raise_for_status()
        
        films = response.json().get('docs', [])
        logging.debug(f"Found {len(films)} films for genre '{genre}'")
        
        if not films:
            return None
            
        selected_film = random.choice(films)
        return normalize_film_data(selected_film)
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}", exc_info=True)
        return None
    

def normalize_film_data(film_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Нормализация с учетом групповых полей"""
    if not film_data:
        return None
    
    # Обработка рейтинга
    rating = film_data.get('rating', {})
    rating_kp = str(round(rating.get('kp', 0), 1)) if rating.get('kp') else 'нет'
    
    # Обработка постера
    poster = film_data.get('poster', {})
    poster_url = poster.get('url', '') if poster else ''
    
    # Обработка жанров
    genres = film_data.get('genres', [])
    genre_names = [g.get('name', '') for g in genres if isinstance(g, dict)]
    
    return {
        'id': str(film_data.get('id', '')),
        'name': film_data.get('name') or film_data.get('alternativeName', '') or 'Без названия',
        'year': str(film_data.get('year', '')),
        'rating': rating_kp,
        'poster': poster_url,
        'genre': ', '.join(genre_names) if genre_names else 'не указан'
    }

async def search_movies(title: str) -> List[Dict[str, Any]]:
    try:
        response = requests.get(
            f"{KINOPOISK_API_URL}/movie/search",
            headers=HEADERS,
            params={
                "query": title,
                "limit": 5,
                "selectFields": ["id", "name", "alternativeName", "year", "rating.kp", "poster.url", "genres"]
            },
            timeout=10
        )
        response.raise_for_status()
        
        films = response.json().get('docs', [])
        return [normalize_film_data(f) for f in films if f]
        
    except Exception as e:
        logging.error(f"Search error: {e}")
        return []

async def send_movie_info(message: Message, film: Dict[str, Any]):
    if not film:
        await message.answer("Не удалось загрузить информацию о фильме")
        return
    
    text = (
        f"🎬 <b>{film['name']}</b>\n"
        f"📅 {film['year']} | ⭐ {film['rating']} | 🎭 {film['genre']}\n"
        f"🔗 https://www.kinopoisk.ru/film/{film['id']}/"
    )
    
    try:
        if film.get('poster'):
            await message.answer_photo(film['poster'], caption=text, parse_mode="HTML")
        else:
            await message.answer(text, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Send error: {e}")
        await message.answer(text, parse_mode="HTML")

@router.callback_query(F.data == "random_movie")
async def handle_random(callback: CallbackQuery):
    await callback.answer("Ищем случайный фильм...")
    
    film = await get_random_movie()
    if film:
        await send_movie_info(callback.message, film)
    else:
        await callback.message.answer("Не удалось найти фильм. Попробуйте ещё раз или выберите жанр")

@router.callback_query(F.data.startswith("genre_"))
async def handle_genre(callback: CallbackQuery):
    genre_id = callback.data.split("_")[1]
    genre_name = next((k for k, v in MAIN_GENRES.items() if v == genre_id), "фильм")
    
    await callback.answer(f"Ищем {genre_name} фильм...")
    
    film = await get_random_movie(genre_id)
    if film:
        await send_movie_info(callback.message, film)
    else:
        await callback.message.answer(f"Не удалось найти {genre_name} фильм. Попробуйте другой жанр")

@router.callback_query(F.data == "find_movie")
async def start_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название:")
    await state.set_state(MovieStates.waiting_for_title)
    await callback.answer()

@router.message(MovieStates.waiting_for_title)
async def process_search(message: Message, state: FSMContext):
    title = message.text.strip()
    if len(title) < 2:
        await message.answer("Слишком короткое название")
        return
    
    films = await search_movies(title)
    
    if not films:
        await message.answer("Ничего не найдено")
    elif len(films) == 1:
        await send_movie_info(message, films[0])
    else:
        builder = InlineKeyboardBuilder()
        for film in films:
            builder.button(
                text=f"{film['name']} ({film['year']})",
                callback_data=f"film_{film['id']}"
            )
        builder.adjust(1)
        await message.answer("Выберите фильм:", reply_markup=builder.as_markup())
    
    await state.clear()

@router.callback_query(F.data.startswith("film_"))
async def show_details(callback: CallbackQuery):
    film_id = callback.data.split("_")[1]
    
    try:
        response = requests.get(
            f"{KINOPOISK_API_URL}/movie/{film_id}",
            headers=HEADERS,
            params={
                "selectFields": ["id", "name", "alternativeName", "year", "rating.kp", "poster.url", "genres"]
            },
            timeout=10
        )
        response.raise_for_status()
        
        film = normalize_film_data(response.json())
        if film:
            await send_movie_info(callback.message, film)
        else:
            await callback.message.answer("Ошибка загрузки")
            
    except Exception as e:
        logging.error(f"Film details error: {e}")
        await callback.message.answer("Ошибка загрузки")
    
    await callback.answer()

@router.callback_query(F.data == "random_movie_genre")
async def show_genres(callback: CallbackQuery):
    builder = InlineKeyboardBuilder()
    for name, genre_id in MAIN_GENRES.items():
        builder.button(text=name.capitalize(), callback_data=f"genre_{genre_id}")
    builder.adjust(2)
    await callback.message.answer("Выберите жанр:", reply_markup=builder.as_markup())
    await callback.answer()