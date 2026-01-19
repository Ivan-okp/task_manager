"""
Репозиторий сервисных операций над моделями (асинхронный слой доступа к данным).
"""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.task_manager.models import UserModel, TaskModel
from src.task_manager.schemas import TaskUpdate
from src.task_manager.logger_core import logger


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
        :return: UserModel - Объект пользователя,
        если аутентификация прошла успешно, иначе None.
        """
        logger.info(f"User login attempt: {username}")

        stmt = (
            select(UserModel)
            .where(UserModel.name == username)
            .where(UserModel.password == password)
        )
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            logger.warning(f"Failed login for: {username}")

            raise HTTPException(status_code=404, detail="User not found")
        logger.info(f"Login successful: {username}")

        return user

    @classmethod
    async def get_tasks_by_current_user(
        cls,
        user_id: str,
        session: AsyncSession,
    ) -> list[TaskModel] | list[None]:
        """
        Получает список задач, назначенных указанному пользователю.

        :param user_id: ID пользователя.
        :param session: Асинхронная сессия.
        :return: List[TaskModel] - Список объектов задач, назначенных пользователю.
        """
        logger.debug(f"Fetching tasks for user_id: {user_id}")

        stmt = select(TaskModel).where(TaskModel.user == user_id)
        result = await session.execute(stmt)
        tasks: list[TaskModel] | list = result.scalars().all()

        logger.info(f"Found {len(tasks)} tasks for user_id: {user_id}")
        return tasks

    @classmethod
    async def get_task_by_id_or_title(
        cls,
        session: AsyncSession,
        user_id: int,
        task_id: int | None = None,
        task_title: str | None = None,
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
            logger.debug(f"Search task by ID: {task_id} (User: {user_id})")

            stmt = (
                select(TaskModel)
                .where(TaskModel.user == user_id)
                .where(TaskModel.id == task_id)
            )
        elif task_title is not None:
            logger.debug(f"Search task by title: '{task_title}' (User: {user_id})")

            stmt = (
                select(TaskModel)
                .where(TaskModel.user == user_id)
                .where(TaskModel.title == task_title)
            )
        else:
            raise HTTPException(status_code=400, detail="Not enough data")
        result = await session.execute(stmt)
        task: TaskModel | None = result.scalar_one_or_none()
        if task is None:
            logger.warning(f"Task not found for user {user_id}")

            raise HTTPException(status_code=404, detail="Task not found")
        logger.info(f"Found task with task_id: {task.id} for user_id: {user_id}")

        return task

    @classmethod
    async def update_task(
        cls,
        session: AsyncSession,
        user_id: int,
        task_for_update: TaskUpdate,
        task_id: int | None = None,
        task_title: str | None = None,
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
            logger.warning(
                f"Update skipped: No fields provided for task (User: {user_id})"
            )

            raise HTTPException(status_code=422, detail="No fields to update")
        if task_id:
            logger.debug(f"Searching task ID {task_id} for update (User: {user_id})")

            stmt = (
                select(TaskModel)
                .where(TaskModel.user == user_id)
                .where(TaskModel.id == task_id)
            )
        elif task_title:
            logger.debug(f"Searching task '{task_title}' for update (User: {user_id})")

            stmt = (
                select(TaskModel)
                .where(TaskModel.user == user_id)
                .where(TaskModel.title == task_title)
            )
        else:
            logger.error(f"Update failed: Not enough data provided (User: {user_id})")

            raise HTTPException(status_code=400, detail="Not enough data")

        result = await session.execute(stmt)
        updating_task: TaskModel | None = result.scalar_one_or_none()
        if updating_task is None:
            logger.warning(
                f"Update failed: Task not found (User: {user_id}, Search: {task_id or task_title})"
            )

            raise HTTPException(status_code=404, detail="Task not found")
        for key, value in update_data.items():
            setattr(updating_task, key, value)
        await session.commit()
        logger.info(f"Task {updating_task.id} successfully updated by user {user_id}")

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
            logger.debug(f"Searching task ID {task_id} for delete (User: {user_id})")

            task_id = int(task_id)
            stmt = (
                select(TaskModel)
                .where(TaskModel.user == user_id)
                .where(TaskModel.id == task_id)
            )
        elif task_title:
            logger.debug(f"Searching task '{task_title}' for delete (User: {user_id})")

            stmt = (
                select(TaskModel)
                .where(TaskModel.user == user_id)
                .where(TaskModel.title == task_title)
            )
        else:
            logger.error(f"Delete failed: Missing identifiers for user {user_id}")

            raise HTTPException(status_code=400, detail="Not enough data")
        result = await session.execute(stmt)
        task_for_delete: TaskModel | None = result.scalar_one_or_none()
        if task_for_delete is None:
            logger.warning(f"Delete failed: Task not found for user {user_id}")

            raise HTTPException(status_code=404, detail="Task not found")
        logger.info(
            f"Deleting task ID {task_for_delete.id} ('{task_for_delete.title}')"
        )

        await session.delete(task_for_delete)
        await session.commit()
        logger.info(
            f"Task ID {task_for_delete.id} successfully deleted by user {user_id}"
        )

        return task_for_delete
