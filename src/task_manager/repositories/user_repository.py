"""
Репозиторий операций над сущностью User — асинхронный слой доступа к данным.
"""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.task_manager.models import UserModel
from src.task_manager.schemas import UserCreate, UserUpdate
from src.task_manager.logger_core import logger


class UserRepository:
    """
    Репозиторий для работы с пользователями.

    Этот класс предоставляет методы для получения, добавления, обновления и удаления пользователей
    в базе данных.
    """

    @classmethod
    async def get_all(
        cls,
        session: AsyncSession,
    ) -> list[UserModel] | list[None]:
        """
        Получает список всех пользователей из базы данных.

        :param session: Асинхронная сессия
        :return: List[UserModel] - Список объектов пользователей.
        """
        logger.debug("Fetching all users from the database.")

        stmt = select(UserModel)
        result = await session.execute(stmt)
        users = result.scalars().all()
        logger.info(f"Retrieved {len(users)} users in total.")

        return users

    @classmethod
    async def get_one(
        cls,
        user_id: int,
        session: AsyncSession,
    ) -> UserModel | None:
        """
        Получает пользователя по его ID.

        :param user_id: ID пользователя.
        :param session: Асинхронная сессия.
        :return: UserModel - Объект пользователя, если пользователь найден.
        """
        logger.debug(f"Fetching user with ID: {user_id}")

        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            logger.warning(f"User with ID {user_id} not found.")

            raise HTTPException(status_code=404, detail="User not found")
        logger.debug(f"User found: {user.name}")

        return user

    @classmethod
    async def add_user(
        cls,
        user: UserCreate,
        session: AsyncSession,
    ) -> UserModel:
        """
        Добавляет нового пользователя в базу данных.

        :param user: Объект UserCreate, содержащий данные для нового пользователя.
        :param session: Асинхронная сессия.
        :return: UserModel - Добавленный объект пользователя.
        """
        logger.info(f"Attempting to add new user. Email: {user.email}")

        user_dict = user.dict()
        new_user = UserModel(**user_dict)
        session.add(new_user)
        await session.commit()
        logger.info(
            f"User successfully added. ID: {new_user.id}, Email: {new_user.email}"
        )

        return new_user

    @classmethod
    async def update_user(
        cls,
        user_id: int,
        user_update: UserUpdate,
        session: AsyncSession,
    ) -> UserModel | None:
        """
        Обновляет существующего пользователя в базе данных.

        :param user_id: ID пользователя.
        :param user_update: Объект UserUpdate, содержащий новые данные для пользователя.
        :param session: Асинхронная сессия.
        :return: UserModel - Обновленный объект пользователя.
        """
        update_data = user_update.model_dump(exclude_unset=True)
        if not update_data:
            logger.warning(f"Update skipped for user ID {user_id}: No fields provided.")

            raise HTTPException(status_code=422, detail="No fields to update")
        logger.info(f"Attempting to update user ID {user_id}.")

        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(stmt)
        user_for_update = result.scalar_one_or_none()
        if user_for_update is None:
            logger.warning(f"Update failed: User with ID {user_id} not found.")

            raise HTTPException(
                status_code=404,
                detail="User not found",
            )
        for key, value in update_data.items():
            setattr(user_for_update, key, value)

        await session.commit()
        logger.info(f"User ID {user_id} successfully updated.")

        return user_for_update

    @classmethod
    async def delete_user(
        cls,
        user_id: int,
        session: AsyncSession,
    ) -> UserModel | None:
        """
        Удаляет пользователя из базы данных.

        :param user_id: ID пользователя.
        :param session: Асинхронная сессия.
        :return: UserModel - Удаленный объект пользователя.
        """
        logger.info(f"Attempting to delete user with ID: {user_id}")

        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(stmt)
        user_for_delete = result.scalar_one_or_none()
        if user_for_delete is None:
            logger.warning(f"Delete failed: User with ID {user_id} not found.")

            raise HTTPException(status_code=404, detail="User not found")
        await session.delete(user_for_delete)
        await session.commit()
        logger.info(f"Deletion committed for user ID {user_id}.")

        return user_for_delete
