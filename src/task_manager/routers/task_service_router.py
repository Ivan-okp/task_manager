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

router = APIRouter(
    prefix="/service",
    tags=["Сервис (работа с задачами пользователя)"],
)


@router.get(
    "/get_all_tasks",
    summary="Список задач пользователя",
    response_model=List[DbTask]
)
async def get_all_tasks(
        user=Depends(get_current_user),
        session: AsyncSession = Depends(get_db)
) -> List[DbTask] | List:
    """
    Получает список всех задач, принадлежащих текущему пользователю.

    :param user: Объект текущего пользователя, полученный через Dependency Injection.
    :param session: Асинхронная сессия.
    :return: List[DbTask] - Список объектов DbTask, представляющих задачи
    """
    tasks = await ServiceRepository.get_tasks_by_current_user(
        user_id=user.id,
        session=session,
    )
    return tasks


@router.get(
    "/get_specific_task",
    summary="Прочесть конкретную задачу",
    response_model=DbTask
)
async def get_specific_task(
        task_id: int | str | None = Query(
            default=None,
            description="ID задачи для чтения"
        ),
        task_title: str | None = Query(
            default=None,
            description="Название задачи для чтения"
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
        task = await ServiceRepository.get_task_by_id_or_title(
            task_id=int(task_id),
            user_id=int(user.id),
            session=session,
        )
        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        return task
    elif task_title:
        task = await ServiceRepository.get_task_by_id_or_title(
            task_title=task_title,
            user_id=int(user.id),
            session=session,
        )
        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        return task
    else:
        raise HTTPException(
            status_code=400,
            detail="Incorrect request"
        )



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
        session: AsyncSession = Depends(get_db)
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
    if db_task is None:
        raise HTTPException(
            status_code=400,
            detail="Incorrect request"
        )

    return db_task


@router.put(
    "/update_task",
    summary="Обновить существующую задачу",
    response_model=DbTask
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
        task = await ServiceRepository.update_task(
            user_id=int(user.id),
            task_for_update=task_for_update,
            task_id=int(task_id),
            session=session,
        )
        return task

    if task_title:
        task = await ServiceRepository.update_task(
            user_id=int(user.id),
            task_for_update=task_for_update,
            task_title=task_title,
            session=session,
        )
        return task


@router.delete(
    "/delete_task",
    summary="Удалить задачу",
    response_model=Dict[str, str]
)
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
    deleted_task = await ServiceRepository.delete_task(
        task_id=task_id,
        task_title=task_title,
        user_id=int(user.id),
        session=session,
    )
    if not deleted_task:
        raise HTTPException(status_code=404, detail="Task is not exists")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
