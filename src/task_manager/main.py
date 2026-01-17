"""
Главный модуль приложения FastAPI — создание экземпляра приложения, подключение роутеров и
инициализация базы данных при старте.
"""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from src.task_manager.database_core.database import (
    Base,
    async_engine,
)
from src.task_manager.routers import (
    router_for_users,
    router_for_tasks,
    user_router_for_service,
    task_router_for_service,
)
from src.task_manager.logger_core import logger


@asynccontextmanager
async def lifespan(
        app: FastAPI
) -> AsyncGenerator:
    """
        Контекстный менеджер жизненного цикла приложения FastAPI, выполняющий инициализацию базы данных при старте приложения.

    Что делает
    - При старте приложения открывает асинхронную транзакцию через async_engine и:
      - создаёт все таблицы, описанные в Base.metadata (эквивалент CREATE TABLE IF NOT EXISTS),
    - Передаёт управление приложению (yield) — в этот момент приложение принимает и обрабатывает запросы.
    - Не выполняет явной очистки/закрытия движка — при необходимости закрытие/уборку нужно сделать отдельно.

        :param app: Экземпляр класса FastAPI.
        :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    logger.info("Starting application lifespan...")

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully.")
    yield


app = FastAPI(lifespan=lifespan)

logger.info("Initializing FastAPI application...")

app.include_router(router_for_users)
logger.info("Included router: router_for_users")

app.include_router(router_for_tasks)
logger.info("Included router: router_for_tasks")

app.include_router(user_router_for_service)
logger.info("Included router: user_router_for_service")

app.include_router(task_router_for_service)
logger.info("Included router: task_router_for_service")

logger.info("FastAPI application initialized successfully.")
