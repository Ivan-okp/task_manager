"""
Главный модуль приложения FastAPI — создание экземпляра приложения, подключение роутеров и
инициализация базы данных при старте.

Задачи этого файла:
- создать FastAPI app;
- подключить все маршрутизаторы (routers) приложения;
- при старте приложения обеспечить создание таблиц (Base.metadata.create_all) и
  настроить нужные параметры СУБД.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер жизненного цикла приложения FastAPI, выполняющий инициализацию базы данных при старте приложения.

Что делает
- При старте приложения открывает асинхронную транзакцию через async_engine и:
  - создаёт все таблицы, описанные в Base.metadata (эквивалент CREATE TABLE IF NOT EXISTS),
  - устанавливает режим журналирования SQLite в WAL (выполняет PRAGMA journal_mode=WAL).
- Передаёт управление приложению (yield) — в этот момент приложение принимает и обрабатывает запросы.
- Не выполняет явной очистки/закрытия движка — при необходимости закрытие/уборку нужно сделать отдельно.

    :param app: Экземпляр класса FastAPI.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("PRAGMA journal_mode=WAL"))
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router_for_users)
app.include_router(router_for_tasks)
app.include_router(user_router_for_service)
app.include_router(task_router_for_service)
