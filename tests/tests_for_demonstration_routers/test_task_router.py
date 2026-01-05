"""
Тесты для роутера задач (tasks).

Этот модуль содержит интеграционные тесты, проверяющие HTTP-эндпоинты /tasks и /tasks/{id} приложения:
- Получение списка задач (GET /tasks)
- Получение задачи по ID (GET /tasks/{id}) — параметризованные кейсы
- Создание задачи (POST /tasks) — параметризованные кейсы и проверка сохранения в БД
- Обновление задачи (PUT /tasks/{id}) — параметризованные кейсы
- (Удаление задач проверяется как cleanup через вспомогательную функцию deletetesttask)
"""
from typing import List, Dict

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.task_manager.models import TaskModel
from tests.conftest import delete_test_task
from tests.test_cases.test_cases_for_task_router import test_cases_task_router_for_get_task, \
    test_cases_task_router_for_add_task, test_cases_task_router_for_update_task, test_cases_task_router_for_delete_task


@pytest.mark.asyncio
async def test_get_tasks(
        client: TestClient,
        create_test_tasks: List[Dict],
):
    """
    Проверяет, что GET /tasks возвращает список задач,
    и что каждая задача соответствует созданным тестовым задачам.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param create_test_tasks: Fixture для создания набора тестовых задач (tasks) через API.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    response: Response = client.get(
        "/tasks",
    )
    assert response.status_code == 200
    tasks_from_api = response.json()
    assert len(tasks_from_api) == len(create_test_tasks)

    for api_task, db_task in zip(tasks_from_api, create_test_tasks):
        assert api_task["id"] == db_task["id"]
        assert api_task["title"] == db_task["title"]
        assert api_task["body"] == db_task["body"]
        assert api_task["status"] == db_task["status"]
        assert api_task["user"] == db_task["user"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "task_id, expected_status_code, expected_result",
    test_cases_task_router_for_get_task,
)
async def test_get_task(
        client: TestClient,
        async_session: AsyncSession,
        task_id: int,
        expected_status_code: int,
        expected_result: dict | None,
        create_test_tasks: List[Dict],
):
    """
    Параметризованный тест для GET /tasks/{task_id}.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param task_id: ID нужной задачи.
    :param expected_status_code: Ожидаемый статус код теста.
    :param expected_result: Ожидаемый результат теста.
    :param create_test_tasks: Fixture для создания набора тестовых задач (tasks) через API.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    response: Response = client.get(
        f"/tasks/{task_id}",
    )
    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()

        for key, value in expected_result.items():
            assert key in response_data
            assert response_data[key] == value


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "task_data, expected_status_code, expected_result",
    test_cases_task_router_for_add_task,
)
async def test_add_task(
        client: TestClient,
        async_session: AsyncSession,
        task_data: dict,
        expected_status_code: int,
        expected_result: dict | None,
        create_test_users: List[Dict],
):
    """
    Параметризованный тест для POST /tasks.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param task_data: Данные для создания задачи.
    :param expected_status_code: Ожидаемый статус код теста.
    :param expected_result: Ожидаемый результат теста.
    :param create_test_users: Fixture для создания набора тестовых пользователей через API.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    if "user" in task_data:
        if task_data["user"] != "user":
            user_id = create_test_users[0]["id"]
            task_data["user"] = user_id
    response: Response = client.post(
        "/tasks",
        json=task_data,
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()

        for key, value in expected_result.items():
            assert key in response_data
            assert response_data[key] == value

        task_id = expected_result["id"]
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await async_session.execute(stmt)
        created_task = result.scalar_one_or_none()

        assert created_task is not None
        assert created_task.title == expected_result["title"]
        assert created_task.body == expected_result["body"]
        assert created_task.status == expected_result["status"]
        assert created_task.user == expected_result["user"]

        code_delete = await delete_test_task(
            client=client,
            task_id=task_id
        )
        assert code_delete == 200


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "task_index, task_id, task_data, expected_status_code, expected_result",
    test_cases_task_router_for_update_task,
)
async def test_task_update(
        client: TestClient,
        async_session: AsyncSession,
        create_test_tasks: List[Dict],
        task_index: int,
        task_id: int,
        task_data: dict,
        expected_status_code: int,
        expected_result: dict | None,
):
    """
    Параметризованный тест для PUT /tasks/{task_id} (обновление задачи).

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param create_test_tasks: Fixture для создания набора тестовых задач (tasks) через API.
    :param task_index: Индекс задачи.
    :param task_id: ID задачи.
    :param task_data: Данные задачи для обновления.
    :param expected_status_code: Ожидаемый код теста.
    :param expected_result: Ожидаемый результат теста.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    task_one = create_test_tasks[task_index]
    if task_id == 1:
        task_id = task_one["id"]

    response: Response = client.put(
        f"/tasks/{task_id}",
        json=task_data,
    )
    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()

        for key, value in expected_result.items():
            assert key in response_data
            assert response_data[key] == value

        task_id = expected_result["id"]
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await async_session.execute(stmt)
        updated_task = result.scalar_one_or_none()

        assert updated_task is not None
        assert updated_task.title == expected_result["title"]
        assert updated_task.body == expected_result["body"]
        assert updated_task.status == expected_result["status"]
        assert updated_task.user == expected_result["user"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "task_index, task_id, expected_status_code, expected_result",
    test_cases_task_router_for_delete_task,
)
async def test_task_delete(
        client: TestClient,
        async_session: AsyncSession,
        create_test_tasks: List[Dict],
        task_index: int,
        task_id: int,
        expected_status_code: int,
        expected_result: dict | None,
):
    """
    Тестирование удаления задачи через эндпоинт DELETE /tasks/{task_id}.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param create_test_tasks: Fixture для создания набора тестовых задач (tasks) через API.
    :param task_index: Индекс задачи.
    :param task_id: ID задачи.
    :param expected_status_code: Ожидаемый код теста.
    :param expected_result: Ожидаемый результат теста.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    task_one = create_test_tasks[task_index]
    if task_id == 1:
        task_id = task_one["id"]

    response: Response = client.delete(
        f"/tasks/{task_id}",
    )
    assert response.status_code == expected_status_code
