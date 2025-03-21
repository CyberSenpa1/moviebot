from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from os import getenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

engine = create_engine(getenv("PG_URL"))


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

    async def update(self, db: AsyncSession, id: int, **kwargs):
        """
        Обновляет запись.
        """
        db_obj = await self.get(db, id)
        if db_obj:
            for key, value in kwargs.items():
                setattr(db_obj, key, value)
            await db.commit()
            await db.refresh(db_obj)
        return db_obj

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
    
class CRUDMovie(CRUDBase):
    def __init__(self):
        super().__init__(Movie)

    def get_by_tmdb_id(self, db: Session, tmdb_id: int):
        """
        Возвращает фильм по TMDb ID.
        """
        return db.query(self.model).filter(self.model.tmdb_id == tmdb_id).first()

class CRUDGenre(CRUDBase):
    def __init__(self):
        super().__init__(Genre)

    def get_by_name(self, db: Session, name: str):
        """
        Возвращает жанр по названию.
        """
        return db.query(self.model).filter(self.model.name == name).first()

class CRUDFavorite(CRUDBase):
    def __init__(self):
        super().__init__(Favorite)

    def get_by_user_and_movie(self, db: Session, user_id: int, movie_id: int):
        """
        Возвращает запись из избранного по ID пользователя и ID фильма.
        """
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.movie_id == movie_id).first()

    def get_by_user(self, db: Session, user_id: int):
        """
        Возвращает список избранных фильмов пользователя.
        """
        return db.query(self.model).filter(self.model.user_id == user_id).all()

class CRUDRecommendation(CRUDBase):
    def __init__(self):
        super().__init__(Recommendation)

    def get_by_user(self, db: Session, user_id: int):
        """
        Возвращает список рекомендаций для пользователя.
        """
        return db.query(self.model).filter(self.model.user_id == user_id).all()

class CRUDSearchHistory(CRUDBase):
    def __init__(self):
        super().__init__(SearchHistory)

    def get_by_user(self, db: Session, user_id: int):
        """
        Возвращает историю поиска пользователя.
        """
        return db.query(self.model).filter(self.model.user_id == user_id).all()