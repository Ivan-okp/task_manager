"""
Репозиторий операций над сущностью User — асинхронный слой доступа к данным.

Модуль предоставляет CRUD-операции для модели UserModel с использованием
AsyncSession SQLAlchemy. Методы бросают HTTPException для простоты интеграции
с FastAPI-эндпоинтами.
"""

from typing import List
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.task_manager.models import UserModel
from src.task_manager.schemas import (
    UserCreate,
    UserUpdate
)


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
    ) -> List[UserModel] | List:
        """
        Получает список всех пользователей из базы данных.

        :param session: Асинхронная сессия
        :return: List[UserModel] - Список объектов пользователей.
        """
        stmt = select(UserModel)
        result = await session.execute(stmt)
        users = result.scalars().all()
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
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
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
        user_dict = user.dict()
        new_user = UserModel(**user_dict)
        session.add(new_user)
        await session.commit()
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
            raise HTTPException(
                status_code=422,
                detail="No fields to update"
            )
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(stmt)
        user_for_update = result.scalar_one_or_none()
        if user_for_update is None:
            raise HTTPException(
                status_code=404,
                detail="User not found",
            )
        for key, value in update_data.items():
            setattr(user_for_update, key, value)

        await session.commit()
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
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(stmt)
        user_for_delete = result.scalar_one_or_none()
        if user_for_delete is None:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        await session.delete(user_for_delete)
        await session.commit()
        return user_for_delete
