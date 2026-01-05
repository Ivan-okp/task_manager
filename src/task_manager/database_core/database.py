"""
Модуль настроек подключения к базе данных (SQLAlchemy, асинхронный режим).

Здесь определяется:
- базовый класс DeclarativeBase для моделей (Base),
- путь к файлу базы данных SQLite, формирование DATABASEURL,
- асинхронный движок (asyncengine),
- фабрика сессий (asyncsessionlocal),
- и ассинхронный генератор get_db() для получения сессии (удобно использовать как зависимость в FastAPI).
"""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
import os


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.
    Используется для объявления таблиц базы данных.
    """
    pass


current_file_path = os.path.abspath(__file__)
my_app_dir = os.path.dirname(current_file_path)

db_path = os.path.join(my_app_dir, "db_for_tasks_and_users")

DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"
async_engine = create_async_engine(DATABASE_URL)

async_session_local = async_sessionmaker(
    bind=async_engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_db() -> AsyncSession:
    """
        Функция для получения асинхронной сессии базы данных.

        Эта функция создает асинхронную сессию, начинает транзакцию и предоставляет ее
        в качестве генератора.  Это позволяет использовать сессию в блоке async with.
        После выхода из блока async with, сессия автоматически закрывается и транзакция откатывается,
        если не было явно закоммичено.

        Yields:
            AsyncSession: Асинхронная сессия базы данных.
    """
    async with async_session_local() as session:
        async with session.begin():
            yield session
