"""
Коллекция маршрутизаторов (APIRouter) приложения.

Этот модуль собирает и экспортирует маршрутизаторы из разных модулей пакета routes.
Предназначен для удобного импорта и регистрации всех маршрутов в основном приложении FastAPI.
"""

from .task_router import router as router_for_tasks
from .user_router import router as router_for_users
from .task_service_router import router as task_router_for_service
from .user_service_router import router as user_router_for_service

__all__ = [
    "router_for_tasks",
    "router_for_users",
    "task_router_for_service",
    "user_router_for_service"
]

"""
Список всех публичных объектов, экспортируемых из этого модуля.
Используется для удобства импорта всех репозиториев сразу с помощью from . import all.
"""
