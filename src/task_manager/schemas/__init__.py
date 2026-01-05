"""
Модуль-пакет экспорта Pydantic‑схем (aggregate exports).

Этот файл собирает и переэкспортирует все схемы (модели) для удобного импорта из
одного места. Вместо:
    from myproject.schemas.taskschemas import TaskBase
    from myproject.schemas.userschemas import UserBase
можно использовать:
    from task_manager.schemas import TaskBase, UserBase
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
    "TaskBase", "TaskCreate", "TaskUpdate", "DbTask",
    "UserBase", "UserCreate", "UserUpdate", "DbUser",
    "UserLogin", "TokenInfo", "TaskStatus", "TaskCreateService"
]

"""
Список всех публичных объектов, экспортируемых из этого модуля.
Используется для удобства импорта всех репозиториев сразу с помощью from . import all.
"""
