"""
Пакет базовых тестовых случаев для приложения управления задачами и пользователями.

Содержит модули с тестовыми данными и базовыми тест-кейсами:
    test_cases_for_task_router.py - Тестовые случаи для роутера задач
    test_cases_for_task_service_router.py - Тестовые случаи для сервисного роутера задач
    test_cases_for_user_router.py - Тестовые случаи для роутера пользователей
    test_cases_for_user_service_router.py - Тестовые случаи для сервисного роутера пользователей

Назначение:
    - Хранение общих тестовых данных

Использование:
    Импортируйте необходимые тестовые случаи в конкретные тестовые модули.
    Не предназначен для прямого запуска тестов.
"""

from .test_cases_for_task_demonstration_router import (
    test_cases_task_router_for_get_task,
    test_cases_task_router_for_add_task,
    test_cases_task_router_for_update_task,
    test_cases_task_router_for_delete_task,
)
from .test_cases_for_task_service_router import (
    test_cases_service_task_router_for_get_task,
    test_cases_service_task_router_for_get_specific_task,
    test_cases_service_task_router_for_create_task,
    test_cases_service_task_router_for_update_task,
    test_cases_service_task_router_for_delete_task,
)
from .test_cases_for_user_demonstration_router import (
    test_cases_user_router_for_get_user,
    test_cases_user_router_for_add_user,
    test_cases_user_router_for_update_user,
    test_cases_user_router_for_delete_user,
)
from .test_cases_for_user_service_router import (
    test_cases_service_user_router_for_create_new_user,
    test_cases_service_user_router_for_login_user,
    test_cases_service_user_router_for_change_user,
    test_cases_service_user_router_for_delete_user,
)

__all__ = [
    "test_cases_task_router_for_get_task",
    "test_cases_task_router_for_add_task",
    "test_cases_task_router_for_update_task",
    "test_cases_task_router_for_delete_task",
    "test_cases_service_task_router_for_get_task",
    "test_cases_service_task_router_for_get_specific_task",
    "test_cases_service_task_router_for_create_task",
    "test_cases_service_task_router_for_update_task",
    "test_cases_service_task_router_for_delete_task",
    "test_cases_user_router_for_get_user",
    "test_cases_user_router_for_add_user",
    "test_cases_user_router_for_update_user",
    "test_cases_user_router_for_delete_user",
    "test_cases_service_user_router_for_create_new_user",
    "test_cases_service_user_router_for_login_user",
    "test_cases_service_user_router_for_change_user",
    "test_cases_service_user_router_for_delete_user",
]

"""
Список всех публичных объектов, экспортируемых из этого модуля.
Используется для удобства импорта всех репозиториев сразу с помощью from . import all.
"""
