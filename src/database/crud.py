from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from os import getenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
import logging

# Инициализация асинхронного движка
engine = create_async_engine(getenv("PG_URL"), echo=True)

class CRUDBase:
    def __init__(self, model):
        self.model = model

    async def create(self, db: AsyncSession, **kwargs):
        """
        Создает новую запись.
        """
        db_obj = self.model(**kwargs)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: int):
        """
        Возвращает запись по ID.
        """
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def update(self, db: AsyncSession, telegram_id: int, **kwargs):
        """
        Обновляет запись пользователя по telegram_id.
        """
        try:
            logging.info(f"Updating User with telegram_id={telegram_id} and data: {kwargs}")
            db_obj = await self.get_by_telegram_id(db, telegram_id)
            if db_obj:
                logging.info(f"Before update: {db_obj}")
                for key, value in kwargs.items():
                    setattr(db_obj, key, value)
                await db.commit()
                await db.refresh(db_obj)
                logging.info(f"After update: {db_obj}")
            else:
                logging.warning(f"User with telegram_id={telegram_id} not found.")
            return db_obj
        except Exception as e:
            logging.error(f"Error updating User: {e}")
            await db.rollback()
            raise

    async def delete(self, db: AsyncSession, id: int):
        """
        Удаляет запись.
        """
        db_obj = await self.get(db, id)
        if db_obj:
            await db.delete(db_obj)
            await db.commit()
        return db_obj

from src.database.models import User, Movie, Genre, Favorite, Recommendation, SearchHistory

class CRUDUser(CRUDBase):
    def __init__(self):
        super().__init__(User)

    async def get_by_telegram_id(self, db: AsyncSession, telegram_id: int):
        """
        Возвращает пользователя по telegram_id.
        """
        result = await db.execute(select(self.model).filter(self.model.telegram_id == telegram_id))
        return result.scalars().first()
    
    async def get_username_by_telegram_id(self, db: AsyncSession, telegram_id: int):
        """
        Возвращает имя пользователя по его Telegram ID.
        """
        query = select(User).where(User.telegram_id == telegram_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()  # Получаем объект пользователя или None
        return user.first_name if user else None  # Возвращаем имя пользователя или None
    
    async def get_age_by_telegram_id(self, db: AsyncSession, telegram_id: int):
        """
        Возвращает возраст по его Telegram ID.
        """
        query = select(User).where(User.telegram_id == telegram_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        return user.age if user else None
    
    async def get_sex_by_telegram_id(self, db: AsyncSession, telegram_id: int):
        query = select(User).where(User.telegram_id == telegram_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        return user.sex if user else None
    
    async def get_all_user_ids(self, db: AsyncSession):
        """
        Возвращает только telegram_id всех пользователей (оптимизировано для рассылки)
        """
        result = await db.execute(select(self.model.telegram_id))
        return result.scalars().all()
    

class CRUDMovie(CRUDBase):
    def __init__(self):
        super().__init__(Movie)

    async def get_by_tmdb_id(self, db: AsyncSession, tmdb_id: int):
        """
        Возвращает фильм по TMDb ID.
        """
        result = await db.execute(select(self.model).filter(self.model.tmdb_id == tmdb_id))
        return result.scalars().first()

class CRUDGenre(CRUDBase):
    def __init__(self):
        super().__init__(Genre)

    async def get_by_name(self, db: AsyncSession, name: str):
        """
        Возвращает жанр по названию.
        """
        result = await db.execute(select(self.model).filter(self.model.name == name))
        return result.scalars().first()

class CRUDFavorite(CRUDBase):
    def __init__(self):
        super().__init__(Favorite)

    async def get_by_user_and_movie(self, db: AsyncSession, user_id: int, movie_id: int):
        """
        Возвращает запись из избранного по ID пользователя и ID фильма.
        """
        result = await db.execute(select(self.model).filter(self.model.user_id == user_id, self.model.movie_id == movie_id))
        return result.scalars().first()

    async def get_by_user(self, db: AsyncSession, user_id: int):
        """
        Возвращает список избранных фильмов пользователя.
        """
        result = await db.execute(select(self.model).filter(self.model.user_id == user_id))
        return result.scalars().all()

class CRUDRecommendation(CRUDBase):
    def __init__(self):
        super().__init__(Recommendation)

    async def get_by_user(self, db: AsyncSession, user_id: int):
        """
        Возвращает список рекомендаций для пользователя.
        """
        result = await db.execute(select(self.model).filter(self.model.user_id == user_id))
        return result.scalars().all()

class CRUDSearchHistory(CRUDBase):
    def __init__(self):
        super().__init__(SearchHistory)

    async def get_by_user(self, db: AsyncSession, user_id: int):
        """
        Возвращает историю поиска пользователя.
        """
        result = await db.execute(select(self.model).filter(self.model.user_id == user_id))
        return result.scalars().all()