"""
API-эндпоинты сервиса работы с задачами текущего аутентифицированного пользователя.

Модуль предоставляет набор маршрутов (FastAPI APIRouter) для операций, которые
относятся к задачам конкретного пользователя: получение всех задач пользователя,
чтение конкретной задачи по id или title, создание и обновление задач.
"""

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Query,
    status,
    Response
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.task_manager.database_core.database import get_db
from src.task_manager.repositories import (
    TaskRepository,
    ServiceRepository
)
from src.task_manager.schemas import (
    TaskUpdate,
    TaskStatus,
    TaskCreateService,
    DbTask
)
from src.task_manager.security import get_current_user
from typing import (
    List,
    Dict
)

from src.task_manager.logger_core import logger

router = APIRouter(
    prefix="/service",
    tags=["Сервис (работа с задачами пользователя)"],
)


@router.get(
    "/get_all_tasks", summary="Список задач пользователя", response_model=List[DbTask]
)
async def get_all_tasks(
    user=Depends(get_current_user), session: AsyncSession = Depends(get_db)
) -> List[DbTask] | List:
    """
    Получает список всех задач, принадлежащих текущему пользователю.

    :param user: Объект текущего пользователя, полученный через Dependency Injection.
    :param session: Асинхронная сессия.
    :return: List[DbTask] - Список объектов DbTask, представляющих задачи
    """
    logger.info(f"API Request: User ID {user.id} fetching all their tasks.")

    tasks = await ServiceRepository.get_tasks_by_current_user(
        user_id=user.id,
        session=session,
    )
    logger.info(f"API Response: User ID {user.id} received {len(tasks)} tasks.")

    return tasks


@router.get(
    "/get_specific_task", summary="Прочесть конкретную задачу", response_model=DbTask
)
async def get_specific_task(
    task_id: int | str | None = Query(default=None, description="ID задачи для чтения"),
    task_title: str | None = Query(
        default=None, description="Название задачи для чтения"
    ),
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> DbTask:
    """
    Получает конкретную задачу по ее ID или названию, принадлежащую текущему пользователю.

    :param task_id: ID задачи.
    :param task_title: Название задачи.
    :param user:  Объект текущего пользователя, полученный через Dependency Injection.
    :param session: Асинхронная сессия.
    :return: DbTask - Объект DbTask, представляющий задачу.
    """
    if task_id:
        logger.info(f"API Request: User ID {user.id} requesting task by ID: {task_id}.")

        task = await ServiceRepository.get_task_by_id_or_title(
            task_id=int(task_id),
            user_id=int(user.id),
            session=session,
        )
        if task is None:
            logger.warning(
                f"API Response Error: User ID {user.id} failed to get task ID {task_id}."
            )

            raise HTTPException(status_code=404, detail="Task not found")
        logger.info(f"API Response: User ID {user.id} received task ID {task_id}.")

        return task

    elif task_title:
        logger.info(
            f"API Request: User ID {user.id} requesting task by title: '{task_title}'."
        )

        task = await ServiceRepository.get_task_by_id_or_title(
            task_title=task_title,
            user_id=int(user.id),
            session=session,
        )
        if task is None:
            logger.warning(
                f"API Response Error: User ID {user.id} failed to get task title '{task_title}'."
            )

            raise HTTPException(status_code=404, detail="Task not found")
        logger.info(
            f"API Response: User ID {user.id} received task with title '{task_title}'."
        )

        return task
    else:
        logger.warning(
            f"API Response Error: User ID {user.id} made a bad request - no task ID or title provided."
        )

        raise HTTPException(status_code=400, detail="Incorrect request")


@router.post(
    "/create_task",
    summary="Создать новую задачу",
    response_model=DbTask,
)
async def create_task(
    title: str = Form(...),
    body: str = Form(...),
    status: TaskStatus = Form(...),
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> DbTask:
    """
    Создает новую задачу для текущего пользователя.

    :param title: Название задачи.
    :param body: Описание задачи.
    :param status: Статус задачи.
    :param user: Объект текущего пользователя, полученный через Dependency Injection.
    :param session: Асинхронная сессия.
    :return: DbTask - Объект DbTask, представляющий созданную задачу.
    """
    user = int(user.id)
    logger.info(
        f"API Request: User ID {user} creating a new task. Title: '{title}', Status: {status.value}."
    )

    task = TaskCreateService(
        title=title,
        body=body,
        status=status,
        user=user,
    )
    db_task = await TaskRepository.add_task(
        new_task=task,
        session=session,
    )
    logger.info(
        f"API Response: Task successfully created for user ID {user}. New task ID: {db_task.id}."
    )

    if db_task is None:
        logger.error(f"API Response Error: User ID {user} failed to create task.")

        raise HTTPException(status_code=400, detail="Incorrect request")

    return db_task


@router.put(
    "/update_task", summary="Обновить существующую задачу", response_model=DbTask
)
async def update_task(
    task_for_update: TaskUpdate,
    task_id: int = None,
    task_title: str = None,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> DbTask:
    """
    Обновляет существующую задачу, принадлежащую текущему пользователю.

    :param task_for_update: Объект TaskUpdate, содержащий новые данные для задачи.
    :param task_id: ID задачи.
    :param task_title: Название задачи.
    :param user:  Объект текущего пользователя, полученный через Dependency Injection.
    :param session: Асинхронная сессия.
    :return: DbTask - Объект DbTask, представляющий обновленную задачу.
    """
    if task_id:
        logger.info(f"API Request: User ID {user.id} updating task {task_id}.")

        task = await ServiceRepository.update_task(
            user_id=int(user.id),
            task_for_update=task_for_update,
            task_id=int(task_id),
            session=session,
        )
        logger.info(
            f"API Response: Task with id: {task_id} successfully updated by user ID {user.id}."
        )

        return task

    elif task_title:
        logger.info(f"API Request: User ID {user.id} updating task {task_title}.")

        task = await ServiceRepository.update_task(
            user_id=int(user.id),
            task_for_update=task_for_update,
            task_title=task_title,
            session=session,
        )
        logger.info(
            f"API Response: Task '{task_title}' successfully updated by user ID {user.id}."
        )

        return task

    else:
        logger.error(
            f"API Request Error: User ID {user.id} provided neither task_id nor task_title for update."
        )

        raise HTTPException(status_code=400, detail="Incorrect request")


@router.delete("/delete_task", summary="Удалить задачу", response_model=Dict[str, str])
async def delete_task(
    task_id: int = None,
    task_title: str = None,
    user=Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Response:
    """
    Удаляет существующую задачу, принадлежащую текущему пользователю.

    :param task_id: ID задачи.
    :param task_title: Название задачи.
    :param user: Объект текущего пользователя, полученный через Dependency Injection.
    :param session: Асинхронная сессия.
    :return: DbTask - Объект DbTask, представляющий удаленную задачу.
    """
    logger.info(f"API Request: User ID {user.id} attempting to delete task.")

    deleted_task = await ServiceRepository.delete_task(
        task_id=task_id,
        task_title=task_title,
        user_id=int(user.id),
        session=session,
    )
    if not deleted_task:
        logger.error(
            f"API Response Error: Unexpected error deleting task  for user ID {user.id}."
        )

        raise HTTPException(status_code=404, detail="Task is not exists")

    logger.info(f"API Response: Task successfully deleted for user ID {user.id}.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
