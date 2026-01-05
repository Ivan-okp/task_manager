"""
Этот модуль предоставляет доступ ко всем репозиториям.

Он импортирует репозитории для работы с задачами (TaskRepository),
пользователями (UserRepository) и сервисами (ServiceRepository)
и делает их доступными для импорта из этого модуля.
"""

from .task_repository import TaskRepository
from .user_repository import UserRepository
from .service_repository import ServiceRepository

__all__ = [
    "TaskRepository",
    "UserRepository",
    "ServiceRepository"
]

"""
Список всех публичных объектов, экспортируемых из этого модуля.
Используется для удобства импорта всех репозиториев сразу с помощью from . import all.
"""
