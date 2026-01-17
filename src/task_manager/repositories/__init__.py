"""
Этот модуль предоставляет доступ ко всем репозиториям.
"""

from .task_repository import TaskRepository
from .user_repository import UserRepository
from .service_repository import ServiceRepository

__all__ = [
    "ServiceRepository",
    "TaskRepository",
    "UserRepository"
]

"""
Список всех публичных объектов, экспортируемых из этого модуля.
Используется для удобства импорта всех репозиториев сразу с помощью from . import all.
"""
