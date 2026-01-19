"""
Этот модуль предоставляет доступ к моделям данных для пользователей и задач.
"""

from .user_models import UserModel
from .task_models import TaskModel

__all__ = ["TaskModel", "UserModel"]

"""
Список всех публичных объектов, экспортируемых из этого модуля.
Используется для удобства импорта всех моделей сразу с помощью from . import all.
"""
