import logging
import asyncio
from os import getenv

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.handlers import start, search, admin

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и хранилища
storage = MemoryStorage()
bot = Bot(token=getenv('BOT_TOKEN'))

# Инициализация асинхронного движка и сессии
engine = create_async_engine(getenv("PG_URL"), echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    """
    Возвращает асинхронную сессию для DI.
    """
    async with async_session() as session:
        yield session


async def main():
    # Инициализация диспетчера
    dp = Dispatcher(storage=storage)

    # Регистрация роутеров
    dp.include_routers(admin.admin_router, start.router, search.router,)

    from aiogram import types
    from aiogram.dispatcher.middlewares.base import BaseMiddleware

    class DBSessionMiddleware(BaseMiddleware):
        async def __call__(self, handler, event, data):
            async with async_session() as session:
                data["session"] = session
                return await handler(event, data)

    dp.update.middleware(DBSessionMiddleware())


    # Запуск бота
    logger.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())