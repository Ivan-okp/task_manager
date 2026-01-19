"""
Фикстуры pytest для интеграционных/функциональных тестов приложения.
"""

from httpx import Response, AsyncClient, ASGITransport
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.task_manager.database_core import get_db
from src.task_manager.main import app
from src.task_manager.models import UserModel, TaskModel
from src.task_manager.logger_core import logger
from tests.test_database import create_test_tables, drop_test_tables, test_session_local


@pytest.fixture(
    scope="session",
)
async def async_test_db() -> None:
    """
    Fixture для создания/удаления таблиц тестовой базы данных.

    Scope: session — выполняется один раз для всего набора тестов.

    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    logger.info("Starting async_test_db fixture")

    await create_test_tables()
    yield
    await drop_test_tables()

    logger.info("Finished async_test_db fixture")


@pytest.fixture(
    scope="function",
)
async def async_session(
    async_test_db: None,
) -> AsyncSession:
    """
     Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.

    Scope: function — новая сессия для каждой тестовой функции.

    :param async_test_db: Fixture для создания/удаления таблиц тестовой базы данных.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    logger.info("Starting async_session fixture")

    async with test_session_local() as session:
        logger.info("Created async session")

        yield session

        logger.info("Finished async_session fixture, session closed")


@pytest.fixture(scope="function")
async def client(
    async_session: AsyncSession,
) -> AsyncClient:
    """
    Fixture, создающая TestClient с переопределенной зависимостью getdb.

    Возвращает TestClient для выполнения синхронных HTTP-запросов к приложению.

    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :return: Функция не содержит return, поэтому по завершении возвращает None (неявно).
    """
    logger.info("Starting client fixture")

    async def override_get_db() -> AsyncSession:
        yield async_session

    app.dependency_overrides[get_db] = override_get_db
    logger.info("Overrode get_db dependency")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
        logger.info("Finished client fixture, AsyncClient closed")

    app.dependency_overrides.clear()
    logger.info("Cleared dependency overrides")


@pytest.fixture(
    scope="function",
)
async def create_test_users(
    async_session: AsyncSession, client: AsyncClient, num_users: int = 3
) -> list[dict]:
    """
    Fixture для создания набора тестовых пользователей через API.

    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param num_users: Требуемое количество создаваемых пользователей (по умолчанию равно трем).
    :return: Возвращает список созданных пользователей (декодированный JSON ответ).
    После теста выполняется удаление пользователей через соответствующий API-эндпоинт.
    """
    logger.info("Starting create_test_users fixture")

    users_to_create = []
    for i in range(num_users):
        user_data = {
            "name": f"testuser_{i + 1}",
            "email": f"testuser_{i + 1}@example.com",
            "password": f"123456789{i + 1}",
        }
        logger.info(f"Creating user: {user_data}")
        response: Response = await client.post("/users", json=user_data)
        assert response.status_code == 200
        logger.info(f"User created successfully, status code: {response.status_code}")

        response_json = response.json()
        users_to_create.append(response_json)

    yield users_to_create
    logger.info("Starting cleanup of created users")

    for user in users_to_create:
        user_id = user["id"]

        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await async_session.execute(stmt)
        user_to_delete = result.scalar_one_or_none()

        if user_to_delete is not None:
            logger.info(f"Deleting user with ID: {user_id}")
            response: Response = await client.delete(
                f"/users/{user_id}",
            )
            assert response.status_code == 204
            assert response.text == ""
            logger.info(
                f"User with ID {user_id} deleted successfully, status code: {response.status_code}"
            )


@pytest.fixture(
    scope="function",
)
async def get_user_and_jwt(
    client: AsyncClient,
    async_session: AsyncSession,
    create_test_users: list[dict],
) -> dict[str, dict | str]:
    """
    Fixture для получения первого созданного пользователя и JWT-токена аутентификации.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param create_test_users: Fixture для создания набора тестовых пользователей через API.
    :return: Возвращает словарь {"user": <user_json>, "token": "<access_token>"}.
    """
    logger.info("Starting get_user_and_jwt fixture")

    user_one = create_test_users[0]
    logger.info(f"Getting user: {user_one['name']}")

    user_data = {"username": user_one["name"], "password": user_one["password"]}
    logger.info(f"Sending login request with data: {user_data}")

    response: Response = await client.post(
        "/service_user/login",
        data=user_data,
    )
    assert response.status_code == 200
    logger.info(f"Login request successful, status code: {response.status_code}")
    response_data = response.json()
    token = response_data["access_token"]
    logger.info(f"Received token: {token}")

    return {"user": user_one, "token": token}


@pytest.fixture(
    scope="function",
)
async def create_test_tasks(
    client: AsyncClient,
    async_session: AsyncSession,
    create_test_users: list[dict],
    num_tasks: int = 3,
) -> list[dict]:
    """
     Fixture для создания набора тестовых задач (tasks) через API.

    :param client: Fixture, создающая TestClient с переопределенной зависимостью get_db.
    :param async_session: Fixture, предоставляющая асинхронную SQLAlchemy-сессию для теста.
    :param create_test_users: Fixture для создания набора тестовых пользователей через API.
    :param num_tasks: Требуемое количество создаваемых задач (по умолчанию равно трем).
    :return: Возвращает список созданных задач (JSON). После теста задачи удаляются через API.
    """
    logger.info("Starting create_test_tasks fixture")

    user_one = create_test_users[0]
    user_id = user_one["id"]
    tasks_to_create = []
    for i in range(num_tasks):
        task_data = {
            "title": f"testtask_{i + 1}",
            "body": f"testbody_{i + 1}_for_testtask{i + 1}",
            "status": "New",
            "user": user_id,
        }
        logger.info(f"Creating task: {task_data}")

        response: Response = await client.post("/tasks", json=task_data)
        assert response.status_code == 200
        logger.info(f"Task created successfully, status code: {response.status_code}")

        response_json = response.json()
        tasks_to_create.append(response_json)

    yield tasks_to_create

    logger.info("Starting cleanup of created tasks")

    for task in tasks_to_create:
        task_id = task["id"]

        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await async_session.execute(stmt)
        task_for_delete = result.scalar_one_or_none()

        if task_for_delete is not None:
            logger.info(f"Deleting task with ID: {task_id}")

            response: Response = await client.delete(
                f"/tasks/{task_id}",
            )
            assert response.status_code == 204
            assert response.text == ""

            logger.info(
                f"Task with ID {task_id} deleted successfully, status code: {response.status_code}"
            )


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
    logger.info(f"Deleting task with ID: {task_id}")

    response: Response = await client.delete(
        f"/tasks/{task_id}",
    )
    assert response.status_code == 204
    assert response.text == ""
    logger.info(
        f"Task with ID {task_id} deleted successfully, status code: {response.status_code}"
    )

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
    logger.info(f"Deleting user with ID: {user_id}")

    response: Response = await client.delete(
        f"/users/{user_id}",
    )
    assert response.status_code == 204
    assert response.text == ""
    logger.info(
        f"User with ID {user_id} deleted successfully, status code: {response.status_code}"
    )

    return response.status_code
