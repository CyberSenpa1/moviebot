from sqlalchemy import (
    Column, Integer, String, Text, Date, VARCHAR, TIMESTAMP, ForeignKey, Table, BigInteger, UniqueConstraint, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

# Таблица для связи многие-ко-многим между movies и genres
movie_genre_association = Table(
    'movie_genres', Base.metadata,
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(VARCHAR(255), nullable=True, default="unknown")
    first_name = Column(VARCHAR(255))
    last_name = Column(VARCHAR(255))
    age = Column(Integer, nullable=True)
    sex = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    is_active = Column(Boolean, default=True, nullable=False)

    # Связь с избранными фильмами
    favorites = relationship('Favorite', back_populates='user')

class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    overview = Column(Text)
    release_date = Column(Date)
    poster_url = Column(String(255))
    tmdb_id = Column(Integer, unique=True)

    # Связь с избранными фильмами
    favorites = relationship('Favorite', back_populates='movie')

    # Связь с жанрами (многие-ко-многим)
    genres = relationship('Genre', secondary=movie_genre_association, back_populates='movies')

class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

    # Связь с фильмами (многие-ко-многим)
    movies = relationship('Movie', secondary=movie_genre_association, back_populates='genres')

class Favorite(Base):
    __tablename__ = 'favorites'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    added_at = Column(TIMESTAMP, server_default=func.now())

    # Связь с пользователем
    user = relationship('User', back_populates='favorites')

    # Связь с фильмом
    movie = relationship('Movie', back_populates='favorites')

    # Уникальный индекс для пары user_id и movie_id
    __table_args__ = (
        UniqueConstraint('user_id', 'movie_id', name='unique_user_movie'),
    )

class Recommendation(Base):
    __tablename__ = 'recommendations'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Связь с пользователем
    user = relationship('User')

    # Связь с фильмом
    movie = relationship('Movie')

class SearchHistory(Base):
    __tablename__ = 'search_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    query = Column(String(255), nullable=False)
    searched_at = Column(TIMESTAMP, server_default=func.now())

    # Связь с пользователем
    user = relationship('User')