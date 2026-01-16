"""
Тесты для сервисного роутера задач (service).

Этот модуль содержит параметризованные интеграционные тесты, которые проверяют
поведение закрытых (требующих аутентификации) сервисных эндпоинтов:
- получение всех задач пользователя (/service/get_all_tasks);
- получение конкретной задачи по id или title (/service/get_specific_task);
- создание задачи (/service/create_task);
- обновление задачи (update_task);
- удаление задачи (delete_task).
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

from src.task_manager.models import TaskModel
from src.task_manager.logger_core import logger
from tests.conftest import delete_test_task
from tests.test_cases import (
    test_cases_service_task_router_for_get_task,
    test_cases_service_task_router_for_get_specific_task,
    test_cases_service_task_router_for_create_task,
    test_cases_service_task_router_for_update_task,
    test_cases_service_task_router_for_delete_task
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "task_case, token, expected_status_code, expected_result",
    test_cases_service_task_router_for_get_task,
)
async def test_get_all_tasks(
    client: AsyncClient,
    get_user_and_jwt: dict,
    task_case: int,
    token: dict,
    expected_status_code: int,
    expected_result: dict | None,
    create_test_tasks: List[Dict],
):
    """
    Проверяет, что GET /tasks возвращает список задач конкретного пользователя,
    и что каждая задача соответствует созданным тестовым задачам.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param get_user_and_jwt: Fixture для получения первого созданного пользователя и JWT-токена аутентификации.
    :param task_case: Вариант сценария тестирования.
    :param token: JWT токен пользователя.
    :param expected_status_code: Ожидаемый статус код теста.
    :param expected_result: Ожидаемый результат теста.
    :param create_test_tasks: Fixture для создания набора тестовых задач (tasks) через API.
    :return:  Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    logger.info(
        f"Starting test_get_all_tasks with task_case: {task_case}, expected_status_code: {expected_status_code}"
    )

    if task_case == 0:
        token = get_user_and_jwt["token"]

    headers = {"Authorization": f"Bearer {token}"}
    response: Response = await client.get(
        "/service/get_all_tasks",
        headers=headers,
    )
    logger.info(
        f"GET /service/get_all_tasks request completed with status code: {response.status_code}"
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()
        logger.debug(f"Response data: {response_data}")
        assert isinstance(response_data, list)
        assert len(response_data) == len(expected_result)
        for i, exp in enumerate(expected_result):
            item = response_data[i]
            assert item.get("title") == exp["title"]
            assert item.get("body") == exp["body"]
            assert item.get("status") == exp["status"]
            assert item.get("user") == exp["user"]
            assert item.get("id") == exp["id"]

    logger.info("Finished test_get_all_tasks")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "task_case, token, task_id, task_title, expected_status_code, expected_result",
    test_cases_service_task_router_for_get_specific_task,
)
async def test_get_specific_task(
    client: AsyncClient,
    get_user_and_jwt: dict,
    task_case: int,
    token: dict,
    task_id: int,
    task_title: str,
    expected_status_code: int,
    expected_result: dict | None,
    create_test_tasks: List[Dict],
):
    """
    Тест для /service/get_specific_task — проверяет поиск задачи конкретного пользователя по id и по title.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param get_user_and_jwt: Fixture для получения первого созданного пользователя и JWT-токена аутентификации.
    :param task_case: Вариант сценария тестирования.
    :param token: JWT токен пользователя.
    :param task_id: ID требуемой задачи.
    :param task_title: Название требуемой задачи.
    :param expected_status_code: Ожидаемый статус код теста.
    :param expected_result: Ожидаемый результат теста.
    :param create_test_tasks: Fixture для создания набора тестовых задач (tasks) через API.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    logger.info(
        f"Starting test_get_specific_task with task_case: {task_case}, task_id: {task_id}, expected_status_code: {expected_status_code}"
    )

    if task_case == 0:
        token = get_user_and_jwt["token"]

    headers = {"Authorization": f"Bearer {token}"}
    data = {"task_id": task_id}
    response: Response = await client.get(
        "/service/get_specific_task", params=data, headers=headers
    )
    logger.info(
        f"GET /service/get_specific_task request completed with status code: {response.status_code}"
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()
        logger.debug(f"Response data: {response_data}")

        for key, value in expected_result.items():
            assert key in response_data
            assert response_data[key] == value

    if task_case == 0:
        token = get_user_and_jwt["token"]

    headers = {"Authorization": f"Bearer {token}"}
    data = {"task_title": task_title}
    response: Response = await client.get(
        "/service/get_specific_task", params=data, headers=headers
    )
    logger.info(
        f"GET /service/get_specific_task request completed with status code: {response.status_code}"
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()
        logger.debug(f"Response data: {response_data}")

        for key, value in expected_result.items():
            assert key in response_data
            assert response_data[key] == value

    logger.info("Finished test_get_specific_task")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "task_case, token, task_data, expected_status_code, expected_result",
    test_cases_service_task_router_for_create_task,
)
async def test_create_task(
    client: AsyncClient,
    async_session: AsyncSession,
    get_user_and_jwt,
    task_case: int,
    token: dict,
    task_data: dict,
    expected_status_code: int,
    expected_result: dict,
):
    """
    Тест для /service/create_task — создание задачи от имени аутентифицированного пользователя.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param get_user_and_jwt: Fixture для получения первого созданного пользователя и JWT-токена аутентификации.
    :param task_case: Вариант сценария тестирования.
    :param token: JWT токен пользователя.
    :param task_data: Данные для создания задачи.
    :param expected_status_code: Ожидаемый статус код теста.
    :param expected_result: Ожидаемый результат теста.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    logger.info(
        f"Starting test_create_task with task_case: {task_case}, expected_status_code: {expected_status_code}"
    )

    if task_case == 1:
        token = get_user_and_jwt["token"]

    headers = {"Authorization": f"Bearer {token}"}
    logger.debug(f"Task data: {task_data}")

    response: Response = await client.post(
        "/service/create_task", data=task_data, headers=headers
    )
    logger.info(
        f"POST /service/create_task request completed with status code: {response.status_code}"
    )
    assert response.status_code == expected_status_code

    if response.status_code == 200:
        response_data = response.json()
        logger.debug(f"Response data: {response_data}")

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

        code_delete = await delete_test_task(client=client, task_id=task_id)
        logger.info(
            f"DELETE task with id {task_id} returned status code: {code_delete}"
        )

        assert code_delete == 204

    logger.info("Finished test_create_task")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "task_case, task_case_2, token, task_data, task_id, task_title, expected_status_code, expected_result",
    test_cases_service_task_router_for_update_task,
)
async def test_update_task(
    client: AsyncClient,
    async_session: AsyncSession,
    create_test_tasks: List[Dict],
    get_user_and_jwt: dict,
    task_case: int,
    task_case_2: int,
    token: dict,
    task_data: dict,
    task_id: int,
    task_title: str,
    expected_status_code: int,
    expected_result: dict | None,
):
    """
    Тест для /service/update_task — изменение задачи от имени аутентифицированного пользователя.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param create_test_tasks: Fixture для создания набора тестовых задач (tasks) через API.
    :param get_user_and_jwt: Fixture для получения первого созданного пользователя и JWT-токена аутентификации.
    :param task_case: Вариант сценария тестирования, используемый для изменения JWT токена.
    :param task_case_2: Вариант сценария тестирования, используемый для изменения ID задачи.
    :param token: JWT токен пользователя.
    :param task_data: Данные для изменения задачи.
    :param task_id: ID задачи.
    :param task_title: Название задачи.
    :param expected_status_code: Ожидаемый статус код теста.
    :param expected_result: Ожидаемый результат теста.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    logger.info(
        f"Starting test_update_task with task_case: {task_case}, task_case_2: {task_case_2}, expected_status_code: {expected_status_code}"
    )

    if task_case == 1:
        token = get_user_and_jwt["token"]

    if task_case_2 == 1:
        task_id = create_test_tasks[0]["id"]
        logger.info(f"Updating task by ID: {task_id}")

    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "task_id": task_id,
    }
    response: Response = await client.put(
        "/service/update_task", json=task_data, params=params, headers=headers
    )
    logger.info(
        f"PUT /service/update_task request completed with status code: {response.status_code}"
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()
        logger.debug(f"Response data: {response_data}")

        for key, value in expected_result.items():
            assert key in response_data
            assert response_data[key] == value

        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await async_session.execute(stmt)
        updated_task = result.scalar_one_or_none()

        assert updated_task is not None
        assert updated_task.title == expected_result["title"]
        assert updated_task.body == expected_result["body"]
        assert updated_task.status == expected_result["status"]
        assert updated_task.user == expected_result["user"]

    if task_case == 1:
        token = get_user_and_jwt["token"]

    if task_case_2 == 1:
        task_title = create_test_tasks[1]["title"]
        logger.info(f"Updating task by title: {task_title}")

    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "task_title": task_title,
    }
    logger.info(
        f"PUT /service/update_task request completed with status code: {response.status_code}"
    )

    response: Response = await client.put(
        "/service/update_task", json=task_data, params=params, headers=headers
    )
    assert response.status_code == expected_status_code

    if expected_status_code == 200:
        response_data = response.json()
        logger.debug(f"Response data: {response_data}")

        for key, value in expected_result.items():
            assert key in response_data
            assert response_data[key] == value

        task_id = response_data["id"]
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await async_session.execute(stmt)
        updated_task = result.scalar_one_or_none()

        assert updated_task is not None
        assert updated_task.title == expected_result["title"]
        assert updated_task.body == expected_result["body"]
        assert updated_task.status == expected_result["status"]
        assert updated_task.user == expected_result["user"]

    logger.info("Finished test_update_task")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "task_case, task_case_2, token, task_id, task_title, expected_status_code, expected_result, expected_result_2",
    test_cases_service_task_router_for_delete_task,
)
async def test_delete_task(
    client: AsyncClient,
    async_session: AsyncSession,
    get_user_and_jwt: dict,
    create_test_tasks: List[Dict],
    task_case: int,
    task_case_2: int,
    token: dict,
    task_id: int,
    task_title: str,
    expected_status_code: int,
    expected_result: dict,
    expected_result_2: dict,
):
    """
    Интеграционный тест для /service/deletetask, проверяющий удаление задач, принадлежащих конкретному пользователю,
    по id и по title.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param get_user_and_jwt: Fixture для получения первого созданного пользователя и JWT-токена аутентификации.
    :param create_test_tasks: Fixture для создания набора тестовых задач (tasks) через API.
    :param task_case: Вариант сценария тестирования, используемый для изменения JWT токена.
    :param task_case_2: Вариант сценария тестирования, используемый для изменения ID задачи.
    :param token: JWT токен пользователя.
    :param task_id: ID задачи.
    :param task_title: Название задачи.
    :param expected_status_code: Ожидаемый статус код.
    :param expected_result: Ожидаемый результат теста при удалении по ID задачи.
    :param expected_result_2: Ожидаемый результат теста при удалении по названию задачи.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    logger.info(f"Test case: task_case={task_case}, task_case_2={task_case_2}")

    if task_case == 1:
        token = get_user_and_jwt["token"]
        logger.debug("Using JWT token from get_user_and_jwt fixture.")

    if task_case_2 == 1:
        task_id = create_test_tasks[0]["id"]
        logger.debug(f"Using task ID from create_test_tasks: {task_id}")

    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "task_id": task_id,
    }
    logger.debug(
        f"Sending DELETE request to /service/delete_task with params: {params} and headers: {headers}"
    )

    response: Response = await client.delete(
        "/service/delete_task",
        params=params,
        headers=headers,
    )
    logger.info(
        f"Status code assertion: {response.status_code} == {expected_status_code}"
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 204:
        response_text = response.text

        assert "" in response_text
        logger.info(
            f"Response body assertion: Expected empty response, received: '{response.text}'"
        )

        assert response_text == expected_result

        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await async_session.execute(stmt)
        deleted_task = result.scalar_one_or_none()
        logger.info(
            f"Checking if task with ID {task_id} was deleted from the database."
        )

        assert deleted_task is None
        logger.info(f"Task with ID {task_id} successfully deleted from the database.")

    if task_case == 1:
        token = get_user_and_jwt["token"]

    if task_case_2 == 1:
        task_title = create_test_tasks[1]["title"]
        logger.debug(f"Using task title from create_test_tasks: {task_title}")

    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "task_title": task_title,
    }
    logger.debug(
        f"Sending DELETE request to /service/delete_task with params: {params} and headers: {headers}"
    )

    response: Response = await client.delete(
        "/service/delete_task",
        params=params,
        headers=headers,
    )
    logger.info(
        f"Status code assertion: {response.status_code} == {expected_status_code}"
    )

    assert response.status_code == expected_status_code

    if expected_status_code == 204:
        response_text = response.text
        logger.info(
            f"Response body assertion: Expected empty response, received: '{response.text}'"
        )

        assert "" in response_text
        assert response_text == expected_result_2

        task_id = create_test_tasks[1]["id"]
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await async_session.execute(stmt)
        deleted_task = result.scalar_one_or_none()
        logger.info(
            f"Checking if task with ID {task_id} was deleted from the database."
        )

        assert deleted_task is None
        logger.info(f"Task with ID {task_id} successfully deleted from the database.")
