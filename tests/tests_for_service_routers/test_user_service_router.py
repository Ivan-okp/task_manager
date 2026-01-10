"""
Тесты для service-роутера пользователей (закрытые эндпоинты, требующие аутентификации).

Этот модуль содержит интеграционные тесты, проверяющие поведение эндпоинтов под
пространством имён service_user, а именно:
- создание нового пользователя через /service_user/create_user;
- вход (логин) через /service_user/login;
- изменение данных пользователя через /service_user/change_user;
- удаление пользователя через /service_user/delete_user.
"""

from typing import (
    List,
    Dict
)

import pytest
from httpx import (
    AsyncClient,
    Response
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.task_manager.models import UserModel
from tests.conftest import delete_test_user
from tests.test_cases import (
    test_cases_service_user_router_for_create_new_user,
    test_cases_service_user_router_for_login_user,
    test_cases_service_user_router_for_change_user,
    test_cases_service_user_router_for_delete_user
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_data, expected_status_code, expected_result",
    test_cases_service_user_router_for_create_new_user,
)
async def test_create_new_user(
        client: AsyncClient,
        async_session: AsyncSession,
        user_data: dict,
        expected_status_code: int,
        expected_result: dict | None,
):
    """
    Тест создания нового пользователя через /service_user/create_user.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param user_data: Данные для создания нового пользователя.
    :param expected_status_code: Ожидаемый код теста.
    :param expected_result: Ожидаемый результат теста.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    response: Response = await client.post(
        "/service_user/create_user",
        data=user_data
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()

        for key, value in expected_result.items():
            assert key in response_data
            assert response_data[key] == value

        user_id = expected_result["id"]
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await async_session.execute(stmt)
        created_user = result.scalar_one_or_none()

        assert created_user is not None
        assert created_user.name == expected_result["name"]
        assert created_user.email == expected_result["email"]
        assert created_user.password == expected_result["password"]

        code_delete = await delete_test_user(
            client=client,
            user_id=user_id,
        )
        assert code_delete == 204


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_index, expected_status_code, expected_result",
    test_cases_service_user_router_for_login_user,
)
async def test_login_for_create_task(
        client: AsyncClient,
        async_session: AsyncSession,
        create_test_users: List[Dict],
        user_index: int,
        expected_status_code: int,
        expected_result: dict | None,
):
    """
    Тест логина /service_user/login.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param create_test_users: Fixture для создания набора тестовых пользователей через API.
    :param user_index: Индекс пользователя.
    :param expected_status_code: Ожидаемый код теста.
    :param expected_result: Ожидаемый результат теста.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    user_data = {"username": "unknown user", "password": "987654321"}
    if user_index == 0:
        user_one = create_test_users[user_index]
        user_data = {"username": user_one["name"], "password": user_one["password"]}
    response: Response = await client.post(
        "/service_user/login",
        data=user_data,
    )
    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()
        assert expected_result["token_value"] in response_data
        assert "token_type" in response_data
        assert response_data["token_type"] == expected_result["token_type"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_case, token, user_update_data, expected_status_code, expected_result",
    test_cases_service_user_router_for_change_user,
)
async def test_change_user(
        client: AsyncClient,
        async_session: AsyncSession,
        get_user_and_jwt: dict,
        user_case: int,
        token: dict,
        user_update_data: dict,
        expected_status_code: int,
        expected_result: dict,
):
    """
    Тест изменения данных пользователя через /service_user/change_user.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param get_user_and_jwt: Fixture для получения первого созданного пользователя и JWT-токена аутентификации.
    :param user_case: Вариант сценария тестирования.
    :param token: JWT токен пользователя.
    :param user_update_data: Данные для обновления пользователя.
    :param expected_status_code: Ожидаемый код статус код теста.
    :param expected_result: Ожидаемый результат теста.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    if user_case == 0:
        token = get_user_and_jwt["token"]

    headers = {"Authorization": f"Bearer {token}"}
    response: Response = await client.put(
        "/service_user/change_user",
        headers=headers,
        data=user_update_data,
    )
    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()

        for key, value in expected_result.items():
            assert key in response_data
            assert response_data[key] == value

        user_id = expected_result["id"]
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await async_session.execute(stmt)
        updated_user = result.scalar_one_or_none()

        assert updated_user is not None
        assert updated_user.name == expected_result["name"]
        assert updated_user.email == expected_result["email"]
        assert updated_user.password == expected_result["password"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_case, token, expected_status_code, expected_result",
    test_cases_service_user_router_for_delete_user,
)
async def test_delete_user(
        client: AsyncClient,
        async_session: AsyncSession,
        get_user_and_jwt: dict,
        user_case: int,
        token: dict,
        expected_status_code: int,
        expected_result: str | None,
):
    """
     Тест для удаления текущего пользователя через сервисный роутер (/service_user/delete_user).

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param get_user_and_jwt: Fixture для получения первого созданного пользователя и JWT-токена аутентификации.
    :param user_case: Вариант сценария тестирования.
    :param token: JWT токен пользователя.
    :param expected_status_code: Ожидаемый статус код теста.
    :param expected_result: Ожидаемый результат теста.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    if user_case == 0:
        token = get_user_and_jwt["token"]

    headers = {"Authorization": f"Bearer {token}"}
    response: Response = await client.delete(
        "/service_user/delete_user",
        headers=headers,
    )
    assert response.status_code == expected_status_code

    if expected_status_code == 204:
        response_text = response.text

        assert response_text == expected_result

        user_id = get_user_and_jwt["user"]["id"]

        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await async_session.execute(stmt)
        deleted_user = result.scalar_one_or_none()

        assert deleted_user is None
