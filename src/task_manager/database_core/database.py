"""
Модуль настроек подключения к базе данных (SQLAlchemy, асинхронный режим).
"""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
import os
from dotenv import load_dotenv

from src.task_manager.logger_core import logger

load_dotenv()


class Base(DeclarativeBase):
    """
    Базовый класс для всех моделей SQLAlchemy.
    Используется для объявления таблиц базы данных.
    """

    pass


db_user = os.environ.get("POSTGRES_USER")
db_password = os.environ.get("POSTGRES_PASSWORD")
db_host = os.environ.get("POSTGRES_HOST")
db_name = os.environ.get("POSTGRES_NAME")

DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}/{db_name}"

if not all([db_user, db_password, db_host, db_name]):
    logger.warning("PostgreSQL environment variables are missing!")

    current_file_path = os.path.abspath(__file__)
    my_app_dir = os.path.dirname(current_file_path)
    db_path = os.path.join(my_app_dir, "db_for_tasks_and_users")
    DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"
    logger.info(f"Fallback: Using SQLite database at {db_path}")
else:
    DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}/{db_name}"
    logger.info(f"Connecting to PostgreSQL at {db_host} (DB: {db_name})")

try:
    async_engine = create_async_engine(DATABASE_URL)
    logger.info("Database engine successfully initialized")
except Exception as e:
    logger.critical(f"Failed to initialize database engine: {e}")
    raise

async_session_local = async_sessionmaker(
    bind=async_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
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
    logger.debug("Creating new database session...")
    async with async_session_local() as session:
        async with session.begin():
            yield session
