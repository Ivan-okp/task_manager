"""
Тесты для роутера пользователей (users).

Этот модуль содержит интеграционные тесты, проверяющие поведение HTTP-эндпоинтов,
связанных с пользователями в приложении (обновление пользователя, удаление и т.д.).
"""
from typing import List, Dict

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.task_manager.models import UserModel
from tests.test_cases.test_cases_for_user_router import (
    test_cases_user_router_for_add_user,
    test_cases_user_router_for_update_user,
    test_cases_user_router_for_delete_user,
    test_cases_user_router_for_get_user
)


@pytest.mark.asyncio
async def test_get_users(
        client: TestClient,
        create_test_users: List[Dict],
):
    """
    Проверяет, что GET /users возвращает список пользователей,
    и что каждый пользователь соответствует созданным тестовым пользователям.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param create_test_users: Fixture для создания набора тестовых пользователей через API.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    response: Response = client.get(
        "/users",
    )
    assert response.status_code == 200
    users_from_api = response.json()
    assert len(users_from_api) == len(create_test_users)

    for api_user, db_user in zip(users_from_api, create_test_users):
        assert api_user["id"] == db_user["id"]
        assert api_user["name"] == db_user["name"]
        assert api_user["email"] == db_user["email"]
        assert api_user["password"] == db_user["password"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, expected_status_code, expected_result",
    test_cases_user_router_for_get_user,
)
async def test_get_user(
        client: TestClient,
        async_session: AsyncSession,
        user_id: int,
        expected_status_code: int,
        expected_result: dict | None,
        create_test_users: List[Dict],
):
    """
    Параметризованный тест для GET /users/{user_id}.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param user_id: ID пользователя.
    :param expected_status_code: Ожидаемый код теста.
    :param expected_result: Ожидаемый результат теста.
    :param create_test_users: Fixture для создания набора тестовых пользователей через API.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    response: Response = client.get(
        f"/users/{user_id}",
    )
    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()

        for key, value in expected_result.items():
            assert key in response_data
            assert response_data[key] == value

        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await async_session.execute(stmt)
        read_user = result.scalar_one_or_none()

        assert read_user is not None
        assert read_user.name == expected_result["name"]
        assert read_user.email == expected_result["email"]
        assert read_user.password == expected_result["password"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_data, expected_status_code, expected_result",
    test_cases_user_router_for_add_user,
)
async def test_add_user(
        client: TestClient,
        async_session: AsyncSession,
        user_data: dict,
        expected_status_code: int,
        expected_result: dict | None,
):
    """
    Параметризованный тест для POST /users.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param user_data: Данные для создания пользователя.
    :param expected_status_code: Ожидаемый код теста.
    :param expected_result: Ожидаемый результат теста.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    response: Response = client.post(
        "/users",
        json=user_data,
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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, user_data, expected_status_code, expected_result",
    test_cases_user_router_for_update_user,
)
async def test_update_user(
        client: TestClient,
        async_session: AsyncSession,
        user_id: int,
        user_data: dict,
        expected_status_code: int,
        expected_result: dict | None,
        create_test_users: List[Dict],
):
    """
    Параметризованный тест для PUT /users/{user_id} (обновление задачи).

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param user_id: ID пользователя.
    :param user_data: Данные для обновления пользователя.
    :param expected_status_code: Ожидаемый код теста.
    :param expected_result: Ожидаемый результат теста.
    :param create_test_users: Fixture для создания набора тестовых пользователей через API.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    response: Response = client.put(
        f"/users/{user_id}",
        json=user_data,
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
        updated_task = result.scalar_one_or_none()

        assert updated_task is not None
        assert updated_task.name == expected_result["name"]
        assert updated_task.email == expected_result["email"]
        assert updated_task.password == expected_result["password"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, expected_status_code, expected_result",
    test_cases_user_router_for_delete_user,
)
async def test_delete_user(
        client: TestClient,
        async_session: AsyncSession,
        user_id: int,
        expected_status_code: int,
        expected_result: dict | None,
        create_test_users: List[Dict],
):
    """
    Тестирование удаления задачи через эндпоинт DELETE /users/{user_id}.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param user_id: ID пользователя.
    :param expected_status_code: Ожидаемый код теста.
    :param expected_result: Ожидаемый результат теста.
    :param create_test_users: Fixture для создания набора тестовых пользователей через API.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    response: Response = client.delete(
        f"/users/{user_id}",
    )
    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()

        assert response_data == {"message": f"User with ID {user_id} deleted successfully"}

        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await async_session.execute(stmt)
        deleted_user = result.scalar_one_or_none()

        assert deleted_user is None
