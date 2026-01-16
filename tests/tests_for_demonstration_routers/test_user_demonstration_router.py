"""
Тесты для роутера пользователей (users).

Этот модуль содержит интеграционные тесты, проверяющие поведение HTTP-эндпоинтов,
связанных с пользователями в приложении (обновление пользователя, удаление и т.д.).
"""

from typing import (
    List,
    Dict
)

import pytest
from httpx import (
    Response,
    AsyncClient
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.task_manager.models import UserModel
from src.task_manager.logger_core import logger
from tests.test_cases import (
    test_cases_user_router_for_get_user,
    test_cases_user_router_for_add_user,
    test_cases_user_router_for_update_user,
    test_cases_user_router_for_delete_user
)


@pytest.mark.asyncio
async def test_get_users(client: AsyncClient, create_test_users: List[Dict]) -> None:
    """
    Проверяет, что GET /users возвращает список пользователей,
    и что каждый пользователь соответствует созданным тестовым пользователям.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param create_test_users: Fixture для создания набора тестовых пользователей через API.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    logger.info("Starting test_get_users")

    response: Response = await client.get(
        "/users",
    )
    logger.debug(f"GET /users response status code: {response.status_code}")
    assert response.status_code == 200
    users_from_api = response.json()
    logger.debug(f"GET /users response data: {users_from_api}")
    assert len(users_from_api) == len(create_test_users)

    logger.info(f"Found {len(users_from_api)} users from API")

    for api_user, db_user in zip(users_from_api, create_test_users):
        assert api_user["id"] == db_user["id"]
        assert api_user["name"] == db_user["name"]
        assert api_user["email"] == db_user["email"]
        assert api_user["password"] == db_user["password"]

    logger.info("test_get_users completed successfully")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, expected_status_code, expected_result",
    test_cases_user_router_for_get_user,
)
async def test_get_user(
    client: AsyncClient,
    async_session: AsyncSession,
    create_test_users: List[Dict],
    user_id: int,
    expected_status_code: int,
    expected_result: dict | None,
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
    logger.info(
        f"Starting test_get_user with user_id: {user_id}, expected_status_code: {expected_status_code}"
    )

    response: Response = await client.get(
        f"/users/{user_id}",
    )
    logger.debug(f"GET /users/{user_id} response status code: {response.status_code}")

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()
        logger.debug(f"GET /users/{user_id} response data: {response_data}")

        for key, value in expected_result.items():
            assert key in response_data
            assert response_data[key] == value

        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await async_session.execute(stmt)
        read_user = result.scalar_one_or_none()

        assert read_user is not None
        logger.debug(f"User from DB: {read_user}")
        assert read_user.name == expected_result["name"]
        assert read_user.email == expected_result["email"]
        assert read_user.password == expected_result["password"]

    logger.info(f"test_get_user with user_id: {user_id} completed")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_data, expected_status_code, expected_result",
    test_cases_user_router_for_add_user,
)
async def test_add_user(
    client: AsyncClient,
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
    logger.info(
        f"Starting test_add_user with user_data: {user_data}, expected_status_code: {expected_status_code}"
    )

    response: Response = await client.post(
        "/users",
        json=user_data,
    )
    logger.info(
        f"POST /users request completed with status code: {response.status_code}"
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()
        logger.debug(f"Response data: {response_data}")

        for key, value in expected_result.items():
            assert key in response_data
            assert response_data[key] == value

        user_id = expected_result["id"]
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await async_session.execute(stmt)
        created_user = result.scalar_one_or_none()

        assert created_user is not None
        logger.info(f"User created successfully with ID: {user_id}")

        assert created_user.name == expected_result["name"]
        assert created_user.email == expected_result["email"]
        assert created_user.password == expected_result["password"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, user_data, expected_status_code, expected_result",
    test_cases_user_router_for_update_user,
)
async def test_update_user(
    client: AsyncClient,
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
    logger.info(
        f"Starting test_update_user with user_id: {user_id}, user_data: {user_data}, expected_status_code: {expected_status_code}"
    )

    response: Response = await client.put(
        f"/users/{user_id}",
        json=user_data,
    )
    logger.info(
        f"PUT /users/{user_id} request completed with status code: {response.status_code}"
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()
        logger.debug(f"Response data: {response_data}")

        for key, value in expected_result.items():
            assert key in response_data
            assert response_data[key] == value

        user_id = expected_result["id"]
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await async_session.execute(stmt)
        updated_task = result.scalar_one_or_none()

        assert updated_task is not None
        logger.info(f"User updated successfully with ID: {user_id}")
        assert updated_task.name == expected_result["name"]
        assert updated_task.email == expected_result["email"]
        assert updated_task.password == expected_result["password"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, expected_status_code, expected_result",
    test_cases_user_router_for_delete_user,
)
async def test_delete_user(
    client: AsyncClient,
    async_session: AsyncSession,
    user_id: int,
    expected_status_code: int,
    expected_result: str | None,
    create_test_users: List[Dict],
):
    """
    Тестирование удаления пользователя через эндпоинт DELETE /users/{user_id}.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param user_id: ID пользователя.
    :param expected_status_code: Ожидаемый код теста.
    :param expected_result: Ожидаемый результат теста.
    :param create_test_users: Fixture для создания набора тестовых пользователей через API.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    logger.info(
        f"Starting test_delete_user with user_id: {user_id}, expected status code: {expected_status_code}"
    )

    response: Response = await client.delete(
        f"/users/{user_id}",
    )
    logger.info(
        f"DELETE /users/{user_id} request completed with status code: {response.status_code}"
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_text = response.text
        logger.debug(f"Response text: {response_text}")

        assert response_text == expected_result

        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await async_session.execute(stmt)
        deleted_user = result.scalar_one_or_none()

        assert deleted_user is None

    logger.info("Finished test_delete_user")
