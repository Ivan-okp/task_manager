"""
Фикстуры pytest для интеграционных/функциональных тестов приложения.

Этот модуль содержит набор асинхронных фикстур, которые:
- подготавливают тестовую in-memory БД и сессии;
- перекрывают зависимость getdb в FastAPI приложении для использования тестовой сессии;
- создают тестовые сущности (пользователи и задачи) через HTTP API приложения;
- обеспечивают очистку созданных сущностей после тестов.
"""

from typing import (
    List,
    Dict
)
from httpx import (
    Response,
    AsyncClient,
    ASGITransport
)
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.task_manager.database_core import get_db
from src.task_manager.main import app
from src.task_manager.models import (
    UserModel,
    TaskModel
)
from tests.test_database import (
    create_test_tables,
    drop_test_tables,
    test_session_local
)


@pytest.fixture(
    scope="session",
)
async def async_test_db() -> None:
    """
    Fixture для создания/удаления таблиц тестовой базы данных.

    Scope: session — выполняется один раз для всего набора тестов.

    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    await create_test_tables()
    yield
    await drop_test_tables()


@pytest.fixture(
    scope="function",
)
async def async_session(
        async_test_db,
) -> AsyncSession:
    """
     Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.

    Scope: function — новая сессия для каждой тестовой функции.

    :param async_test_db: Fixture для создания/удаления таблиц тестовой базы данных.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    async with test_session_local() as session:
        yield session


@pytest.fixture(scope="function")
async def client(
        async_session: AsyncSession,
):
    """
    Fixture, создающая TestClient с переопределенной зависимостью getdb.

    Возвращает TestClient для выполнения синхронных HTTP-запросов к приложению.

    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """

    async def override_get_db():
        yield async_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(
    scope="function",
)
async def create_test_users(
        async_session: AsyncSession,
        client: AsyncClient,
        num_users: int = 3
) -> List[Dict]:
    """
    Fixture для создания набора тестовых пользователей через API.

    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param num_users: Требуемое количество создаваемых пользователей (по умолчанию равно трем).
    :return: Возвращает список созданных пользователей (декодированный JSON ответ).
    После теста выполняется удаление пользователей через соответствующий API-эндпоинт.
    """
    users_to_create = []
    for i in range(num_users):
        user_data = {
            "name": f"testuser_{i + 1}",
            "email": f"testuser_{i + 1}@example.com",
            "password": f"123456789{i + 1}"
        }
        response: Response = await client.post(
            "/users",
            json=user_data
        )
        assert response.status_code == 200
        response_json = response.json()
        users_to_create.append(response_json)

    yield users_to_create

    for user in users_to_create:
        user_id = user["id"]

        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await async_session.execute(stmt)
        user_to_delete = result.scalar_one_or_none()

        if user_to_delete is not None:
            response: Response = await client.delete(
                f"/users/{user_id}",
            )
            assert response.status_code == 204
            assert response.text == ""


@pytest.fixture(
    scope="function",
)
async def get_user_and_jwt(
        client: AsyncClient,
        async_session: AsyncSession,
        create_test_users,
) -> Dict[str, Dict | str]:
    """
    Fixture для получения первого созданного пользователя и JWT-токена аутентификации.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param create_test_users: Fixture для создания набора тестовых пользователей через API.
    :return: Возвращает словарь {"user": <user_json>, "token": "<access_token>"}.
    """
    user_one = create_test_users[0]
    user_data = {"username": user_one["name"], "password": user_one["password"]}
    response: Response = await client.post(
        "/service_user/login",
        data=user_data,
    )
    assert response.status_code == 200
    response_data = response.json()
    token = response_data["access_token"]

    return {"user": user_one, "token": token}


@pytest.fixture(
    scope="function",
)
async def create_test_tasks(
        client: AsyncClient,
        async_session: AsyncSession,
        create_test_users,
        num_tasks: int = 3,
) -> List[Dict]:
    """
     Fixture для создания набора тестовых задач (tasks) через API.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param create_test_users: Fixture для создания набора тестовых пользователей через API.
    :param num_tasks: Требуемое количество создаваемых задач (по умолчанию равно трем).
    :return: Возвращает список созданных задач (JSON). После теста задачи удаляются через API.
    """
    user_one = create_test_users[0]
    user_id = user_one["id"]
    tasks_to_create = []
    for i in range(num_tasks):
        task_data = {
            "title": f"testtask_{i + 1}",
            "body": f"testbody_{i + 1}_for_testtask{i + 1}",
            "status": "New",
            "user": user_id
        }
        response: Response = await client.post(
            "/tasks",
            json=task_data
        )
        assert response.status_code == 200
        response_json = response.json()
        tasks_to_create.append(response_json)

    yield tasks_to_create

    for task in tasks_to_create:
        task_id = task["id"]

        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await async_session.execute(stmt)
        task_for_delete = result.scalar_one_or_none()

        if task_for_delete is not None:
            response: Response = await client.delete(
                f"/tasks/{task_id}",
            )
            assert response.status_code == 204
            assert response.text == ""


async def delete_test_task(
        client: AsyncClient,
        task_id: int,
) -> int:
    """
    Fixture для удаления задачи.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param task_id: ID задачи для удаления.
    :return: Статус код удаления задачи.
    """
    response: Response = await client.delete(
        f"/tasks/{task_id}",
    )
    assert response.status_code == 204
    assert response.text == ""

    return response.status_code


async def delete_test_user(
        client: AsyncClient,
        user_id: int,
) -> int:
    """
    Fixture для удаления пользователя.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param user_id: ID пользователя для удаления.
    :return: Статус код удаления пользователя.
    """
    response: Response = await client.delete(
        f"/users/{user_id}",
    )
    assert response.status_code == 204
    assert response.text == ""

    return response.status_code
