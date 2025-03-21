from sqlalchemy import create_engine
from src.database.models import Base
from os import getenv
from sqlalchemy.orm import Session
from src.database.crud import CRUDUser

# Создай движок
engine = create_engine(getenv("PG_URL"))

# Создай все таблицы
Base.metadata.create_all(engine)
print("Таблицы созданы!")

crud_user = CRUDUser()


