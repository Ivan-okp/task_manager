"""
Утилиты для тестовой (в памяти) базы данных.

Этот модуль предоставляет:
- асинхронный движок testengine для SQLite в памяти;
- фабрику сессий testsessionlocal (asyncsessionmaker) для получения AsyncSession в тестах;
- вспомогательные функции createtesttables() и droptesttables() для создания/удаления
  таблиц, описанных в Base.metadata.

Назначение:
- Быстро подготовить изолированную БД для юнит/интеграционных тестов без необходимости внешнего СУБД.
- Упростить написание фикстур pytest/asyncio.
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from src.task_manager.database_core import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL)

test_session_local = async_sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession
)


async def create_test_tables() -> None:
    """
    Создать все таблицы, описанные в Base.metadata, в тестовой БД.

    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text("PRAGMA journal_mode=WAL"))
        print("Test tables created.")


async def drop_test_tables() -> None:
    """
    Удалить все таблицы, описанные в Base.metadata, из тестовой БД.

    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("Test tables dropped")
