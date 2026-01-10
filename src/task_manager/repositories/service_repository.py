"""
Репозиторий сервисных операций над моделями (асинхронный слой доступа к данным).

Этот модуль содержит класс ServiceRepository с набором classmethod-ов для
выполнения типичных операций над пользователями и задачами:
- аутентификация пользователя (login_user),
- получение списка задач пользователя (get_tasks_by_current_user),
- получение задачи по id или названию (get_task_by_id_or_title),
- обновление задачи (update_task).
"""

from typing import List
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.task_manager.models import (
    UserModel,
    TaskModel
)
from src.task_manager.schemas import TaskUpdate


class ServiceRepository:
    """
    Репозиторий сервиса, предоставляющий методы для работы с пользователями и задачами.

    Этот класс содержит методы для аутентификации пользователей, получения задач,
    получения задачи по ID или названию и обновления задачи.
    """

    @classmethod
    async def login_user(
            cls,
            username: str,
            password: str,
            session: AsyncSession,
    ) -> UserModel | None:
        """
        Аутентифицирует пользователя по имени пользователя и паролю.

        :param username: Имя пользователя.
        :param password: Пароль пользователя.
        :param session: Асинхронная сессия.
        :return: UserModel - Объект пользователя, если аутентификация прошла успешно, иначе None.
        """
        stmt = select(UserModel).where(UserModel.name == username).where(UserModel.password == password)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        return user

    @classmethod
    async def get_tasks_by_current_user(
            cls,
            user_id: str,
            session: AsyncSession,
    ) -> List[TaskModel] | List:
        """
        Получает список задач, назначенных указанному пользователю.

        :param user_id: ID пользователя.
        :param session: Асинхронная сессия.
        :return: List[TaskModel] - Список объектов задач, назначенных пользователю.
        """
        stmt = select(TaskModel).where(TaskModel.user == user_id)
        result = await session.execute(stmt)
        tasks: List[TaskModel] | List = result.scalars().all()
        return tasks

    @classmethod
    async def get_task_by_id_or_title(
            cls,
            session: AsyncSession,
            user_id: int,
            task_id: int = None,
            task_title: str = None,
    ) -> TaskModel | None:
        """
        Получает задачу по ID или названию, принадлежащую указанному пользователю.

        :param session: Асинхронная сессия.
        :param user_id: ID пользователя.
        :param task_id: ID задачи.
        :param task_title: Название задачи.
        :return: TaskModel - Объект задачи, если задача найдена, иначе None.
        """
        if task_id is not None:
            stmt = select(TaskModel).where(TaskModel.user == user_id).where(TaskModel.id == task_id)
        elif task_title is not None:
            stmt = select(TaskModel).where(TaskModel.user == user_id).where(TaskModel.title == task_title)
        else:
            raise HTTPException(
                status_code=400,
                detail="Not enough data"
            )
        result = await session.execute(stmt)
        task: TaskModel | None = result.scalar_one_or_none()
        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        return task

    @classmethod
    async def update_task(
            cls,
            session: AsyncSession,
            user_id: int,
            task_for_update: TaskUpdate,
            task_id: int = None,
            task_title: str = None,
    ) -> TaskModel:
        """
        Обновляет задачу по ID или названию, принадлежащую указанному пользователю.

        :param session: Асинхронная сессия.
        :param user_id: ID пользователя.
        :param task_for_update: Объект TaskUpdate, содержащий новые данные для задачи.
        :param task_id: ID задачи.
        :param task_title: Название задачи.
        :return: TaskModel - Обновленный объект задачи.
        """
        update_data = task_for_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=422,
                detail="No fields to update"
            )
        if task_id:
            stmt = select(TaskModel).where(TaskModel.user == user_id).where(TaskModel.id == task_id)
        elif task_title:
            stmt = select(TaskModel).where(TaskModel.user == user_id).where(TaskModel.title == task_title)
        else:
            raise HTTPException(
                status_code=400,
                detail="Not enough data"
            )

        result = await session.execute(stmt)
        updating_task: TaskModel | None = result.scalar_one_or_none()
        if updating_task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        for key, value in update_data.items():
            setattr(updating_task, key, value)
        await session.commit()
        return updating_task

    @classmethod
    async def delete_task(
            cls,
            session: AsyncSession,
            task_id: int,
            task_title: str,
            user_id: int,
    ) -> TaskModel:
        """
        Удаляет задачу по ID или названию, принадлежащую указанному пользователю.

        :param session: Асинхронная сессия.
        :param task_id: ID задачи.
        :param task_title: Название задачи.
        :param user_id: ID пользователя.
        :return: TaskModel - Удаленный объект задачи.
        """
        if task_id:
            task_id = int(task_id)
            stmt = select(TaskModel).where(TaskModel.user == user_id).where(TaskModel.id == task_id)
        elif task_title:
            stmt = select(TaskModel).where(TaskModel.user == user_id).where(TaskModel.title == task_title)
        else:
            raise HTTPException(
                status_code=400,
                detail="Not enough data"
            )
        result = await session.execute(stmt)
        task_for_delete: TaskModel | None = result.scalar_one_or_none()
        if task_for_delete is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        await session.delete(task_for_delete)
        await session.commit()
        return task_for_delete
