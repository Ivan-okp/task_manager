"""
Утилиты для тестовой (в памяти) базы данных.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.task_manager.database_core import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL)

test_session_local = async_sessionmaker(
    bind=test_engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)


async def create_test_tables() -> None:
    """
    Создать все таблицы, описанные в Base.metadata, в тестовой БД.

    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("PRAGMA journal_mode=WAL"))
        print("Test tables created.")


async def drop_test_tables() -> None:
    """
    Удалить все таблицы, описанные в Base.metadata, из тестовой БД.

    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("Test tables dropped")
