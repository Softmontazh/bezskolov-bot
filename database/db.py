# database/db.py

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv
from database.models import Base  # ← твоя база с моделями

load_dotenv()  # Загружаем переменные из .env файла

DATABASE_URL = os.environ.get("URL_DB")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# Асинхронная инициализация базы
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
