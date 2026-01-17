"""
Репозиторий операций над сущностью Task — асинхронный слой доступа к данным.
"""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.task_manager.models import (
    TaskModel,
    UserModel
)
from src.task_manager.schemas import (
    TaskCreate,
    TaskUpdate
)
from src.task_manager.logger_core import logger


class TaskRepository:
    """
    Репозиторий для работы с задачами.

    Этот класс предоставляет методы для получения, добавления, обновления и удаления задач
    в базе данных.
    """

    @classmethod
    async def get_all(
            cls,
            session: AsyncSession,
    ) -> list[TaskModel] | list[None]:
        """
        Получает список всех задач из базы данных.

        :param session: Асинхронная сессия.
        :return: List[TaskModel] - Список объектов задач.
        """
        logger.debug("Fetching all tasks from the database.")

        stmt = select(TaskModel)
        result = await session.execute(stmt)
        tasks = result.scalars().all()
        logger.info(f"Retrieved {len(tasks)} tasks in total.")

        return tasks

    @classmethod
    async def get_one(
            cls,
            task_id: int,
            session: AsyncSession,
    ) -> TaskModel | None:
        """
        Получает задачу по ее ID.

        :param task_id: ID задачи.
        :param session: Асинхронная сессия.
        :return: TaskModel - Объект задачи, если задача найдена.
        """
        logger.debug(f"Fetching task with ID: {task_id}")

        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        if task is None:
            logger.warning(f"Task with ID {task_id} not found.")

            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        logger.debug(f"Task found: {task.title}")

        return task

    @classmethod
    async def add_task(
            cls,
            new_task: TaskCreate,
            session: AsyncSession,
    ) -> TaskModel:
        """
        Добавляет новую задачу в базу данных.

        :param new_task: Объект TaskCreate, содержащий данные для новой задачи.
        :param session: Асинхронная сессия.
        :return: TaskModel - Добавленный объект задачи.
        """
        logger.info(f"Attempting to add a new task for user ID: {new_task.user}")

        stmt = select(UserModel).where(UserModel.id == new_task.user)
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()
        if existing_user is None:
            logger.error(
                f"Failed to add task: User with ID {new_task.user} does not exist."
            )

            raise HTTPException(
                status_code=404,
                detail="User not found",
            )
        logger.debug(f"User {new_task.user} validated. Creating task object.")

        task_dict = new_task.dict()
        added_task = TaskModel(**task_dict)
        session.add(added_task)
        await session.commit()
        logger.info(
            f"Task successfully created with ID: {added_task.id} (Title: '{added_task.title}')"
        )

        return added_task

    @classmethod
    async def update_task(
            cls,
            task_id: int,
            task_for_update: TaskUpdate,
            session: AsyncSession,
    ) -> TaskModel | None:
        """
        Обновляет существующую задачу в базе данных.

        :param task_id: ID задачи.
        :param task_for_update: Объект TaskUpdate, содержащий новые данные для задачи.
        :param session: Асинхронная сессия.
        :return: TaskModel - Обновленный объект задачи.
        """
        update_data = task_for_update.model_dump(exclude_unset=True)
        if not update_data:
            logger.warning(f"Update skipped for task ID {task_id}: No fields provided.")

            raise HTTPException(
                status_code=422,
                detail="No data to update"
            )
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        if task is None:
            logger.warning(f"Update failed: Task with ID {task_id} not found.")

            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        for key, value in update_data.items():
            setattr(task, key, value)
        await session.commit()
        logger.info(f"Task ID {task_id} successfully updated.")

        return task

    @classmethod
    async def delete_task(
            cls,
            task_id: int,
            session: AsyncSession,
    ) -> TaskModel | None:
        """
        Удаляет задачу из базы данных.

        :param task_id: ID задачи.
        :param session: Асинхронная сессия.
        :return: TaskModel - Удаленный объект задачи.
        """
        logger.info(f"Attempting to delete task with ID: {task_id}")

        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await session.execute(stmt)
        task_for_delete = result.scalar_one_or_none()
        if task_for_delete is None:
            logger.warning(f"Delete failed: Task with ID {task_id} not found.")

            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )
        logger.info(
            f"Task ID {task_for_delete.id} ('{task_for_delete.title}') successfully deleted."
        )

        await session.delete(task_for_delete)
        await session.commit()
        return task_for_delete
