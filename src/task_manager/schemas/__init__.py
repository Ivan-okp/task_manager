"""
Модуль-пакет экспорта Pydantic‑схем (aggregate exports).
"""

from .task_schemas import (
    TaskBase,
    TaskCreate,
    TaskUpdate,
    DbTask
)
from .user_schemas import (
    UserBase,
    UserCreate,
    UserUpdate,
    DbUser
)
from .service_schemas import (
    UserLogin,
    TokenInfo,
    TaskStatus,
    TaskCreateService
)

__all__ = [
    "DbTask",
    "DbUser",
    "TaskBase",
    "TaskCreate",
    "TaskCreateService",
    "TaskStatus",
    "TaskUpdate",
    "TokenInfo",
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserUpdate",
]

"""
Список всех публичных объектов, экспортируемых из этого модуля.
Используется для удобства импорта всех репозиториев сразу с помощью from . import all.
"""
