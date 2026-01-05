"""
Параметризованные тест-кейсы для сервисного роутера пользователей (service/user-related endpoints).

Модуль содержит набор тест-кейсов, используемых в интеграционных/сервисных тестах для проверки.
"""

test_cases_service_user_router_for_create_new_user = [
    (
        {"name": "test user", "email": "test@mail.com", "password": "123456789"},
        200,
        {"name": "test user", "email": "test@mail.com", "password": "123456789", "id": 1},
    ),
    (
        {"email": "test@mail.com", "password": "123456789"},
        422,
        None,
    ),
    (
        {"name": "test user", "password": "123456789"},
        422,
        None,
    ),
    (
        {"name": "test user", "email": "test@mail.com"},
        422,
        None,
    ),
]

test_cases_service_user_router_for_login_user = [
    (
        0,
        200,
        {"token_value": "access_token", "token_type": "Bearer"}
    ),
    (
        4,
        404,
        None
    ),
]

test_cases_service_user_router_for_change_user = [
    (
        0,
        {"token": "00000000"},
        {"name": "Test update user", "email": "test@update.com", "password": "987654321"},
        200,
        {"name": "Test update user", "email": "test@update.com", "password": "987654321", "id": 1, },
    ),
    (
        1,
        {"token": "00000000"},
        {"name": "Test update user", "email": "test@update.com", "password": "987654321"},
        401,
        None,
    ),
    (
        0,
        {"token": "00000000"},
        {"email": "test@update.com", "password": "987654321"},
        422,
        None,
    ),
    (
        0,
        {"token": "00000000"},
        {"name": "Test update user", "password": "987654321"},
        422,
        None,
    ),
    (
        0,
        {"token": "00000000"},
        {"name": "Test update user", "email": "test@update.com"},
        422,
        None,
    ),
]

test_cases_service_user_router_for_delete_user = [
    (
        0,
        {"token": "00000000"},
        200,
        {"message": "User with ID 1 deleted successfully"}
    ),
    (
        1,
        {"token": "00000000"},
        401,
        None,
    ),
]
