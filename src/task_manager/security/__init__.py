"""
Экспорт JWT‑зависимостей и утилит для пакета.
"""

from .jwt_core import (
    encode_jwt,
    decode_jwt,
    get_token,
    get_current_user
)

__all__ = [
    "decode_jwt",
    "encode_jwt",
    "get_current_user",
    "get_token"
]

"""
Список всех публичных объектов, экспортируемых из этого модуля.
Используется для удобства импорта всех репозиториев сразу с помощью from . import all.
"""
