"""
Этот модуль предоставляет доступ к компонентам базы данных.
"""

from .database import (
    Base,
    async_engine,
    async_session_local,
    get_db
)

__all__ = [
    "Base",
    "async_engine",
    "async_session_local",
    "get_db"
]

"""
Список всех публичных объектов, экспортируемых из этого модуля.
Используется для удобства импорта всех объектов сразу с помощью from . import all.
"""
