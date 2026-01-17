"""
API-маршруты для работы с задачами (Task).
"""

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Response,
    status
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.task_manager.database_core.database import get_db
from src.task_manager.repositories import TaskRepository
from src.task_manager.schemas import (
    DbTask,
    TaskCreate,
    TaskUpdate
)
from src.task_manager.logger_core import logger

router = APIRouter(
    prefix="/tasks",
    tags=["Задачи"],
)


@router.get(
    "",
    summary="Получить список всех задач",
    response_model=list[DbTask]
)
async def get_tasks(
        session: AsyncSession = Depends(get_db)
) -> list[DbTask] | list[None]:
    """
    Получает список всех задач.

    :param session: Асинхронная сессия.
    :return: List[DbTask] - Список объектов DbTask, представляющих задачи.
    """
    logger.info("API Request: Fetching all tasks.")

    tasks = await TaskRepository.get_all(
        session=session,
    )
    logger.info(f"API Response: Returning {len(tasks)} tasks.")

    return tasks


@router.get(
    "/{task_id}",
    summary="Получить информацию о конкретной задаче",
    response_model=DbTask,
)
async def get_task(
        task_id: int,
        session: AsyncSession = Depends(get_db)
) -> DbTask:
    """
    Получает информацию о задаче по ее ID.

    :param task_id: ID задачи.
    :param session: Асинхронная сессия.
    :return: DbTask - Объект DbTask, представляющий задачу.
    """
    logger.info(f"API Request: Fetching task with ID: {task_id}")

    task = await TaskRepository.get_one(
        task_id=task_id,
        session=session
    )
    if task:
        logger.info(f"API Response: Task ID {task_id} found and returned.")

        return task
    logger.warning(f"API Response (Error): Task ID {task_id} not found.")

    raise HTTPException(
        status_code=404,
        detail="Task is not exist"
    )


@router.post(
    "",
    summary="Создать новую задачу",
    response_model=DbTask
)
async def add_task(
        task: TaskCreate,
        session: AsyncSession = Depends(get_db),
) -> DbTask:
    """
    Создает новую задачу.

    :param task: Объект TaskCreate, содержащий данные для новой задачи.
    :param session: Асинхронная сессия.
    :return: DbTask - Объект DbTask, представляющий созданную задачу.
    """
    logger.info(
        f"API Request: Creating new task for user ID {task.user} with title '{task.title}'."
    )

    db_task = await TaskRepository.add_task(
        new_task=task,
        session=session,
    )
    if db_task is None:
        logger.error(
            f"API Response Error: Failed to create task for user ID {task.user}. TaskRepository returned None."
        )

        raise HTTPException(
            status_code=400,
            detail="Incorrect request"
        )
    logger.info(
        f"API Response: Task created successfully. Task ID: {db_task.id}, Title: '{db_task.title}'."
    )

    return db_task


@router.put(
    "/{task_id}",
    summary="Обновить информацию о задаче",
    response_model=DbTask
)
async def update_task(
        task_id: int,
        task_for_update: TaskUpdate,
        session: AsyncSession = Depends(get_db)
) -> DbTask:
    """
    Обновляет информацию о задаче по ее ID.

    :param task_id: ID задачи.
    :param task_for_update: Объект TaskUpdate, содержащий новые данные для задачи.
    :param session: Асинхронная сессия.
    :return: DbTask - Объект DbTask, представляющий обновленную задачу.
    """
    logger.info(f"API Request: Updating task ID {task_id}.")

    task = await TaskRepository.update_task(
        task_id=task_id,
        task_for_update=task_for_update,
        session=session,
    )
    if task:
        logger.info(f"API Response: Task ID {task_id} successfully updated.")

        return task

    logger.error(f"API Response Error: Failed to update task ID {task_id}.")
    raise HTTPException(
        status_code=404,
        detail="Task is not exist"
    )


@router.delete(
    "/{task_id}",
    summary="Удалить задачу",
)
async def delete_task(
        task_id: int,
        session: AsyncSession = Depends(get_db),
) -> Response:
    """
    Удаляет задачу по ее ID.

    :param task_id: ID задачи.
    :param session: Асинхронная сессия.
    :return: Dict[str, str] - Словарь с сообщением об успешном удалении.
    """
    logger.info(f"API Request: Deleting task with ID: {task_id}")

    task_for_delete = await TaskRepository.delete_task(
        task_id=task_id,
        session=session,
    )
    if not task_for_delete:
        logger.error(f"API Response Error: Failed to delete task ID {task_id}.")
        raise HTTPException(
            status_code=404,
            detail="Task is not exists"
        )

    logger.info(f"API Response: Task ID {task_id} successfully deleted.")
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
