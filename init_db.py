from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
from os import getenv
import asyncio
import logging


# Создаём асинхронный движок
engine = create_async_engine(getenv("PG_URL"), echo=True)

# Создаём асинхронную сессию
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы созданы!")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")



# Запуск асинхронной функции
if __name__ == "__main__":
    asyncio.run(create_tables())