from sqlalchemy import create_engine
from src.database.models import Base
from os import getenv


# Укажи строку подключения к PostgreSQL
DATABASE_URL = getenv("PG_URL")

# Создай движок
engine = create_engine(DATABASE_URL)

# Создай все таблицы
Base.metadata.create_all(engine)
print("Таблицы созданы!")