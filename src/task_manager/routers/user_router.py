"""
API-маршруты для управления пользователями.

Этот модуль содержит FastAPI APIRouter с CRUD-эндпоинтами для сущности User.
Каждый эндпоинт использует асинхронную сессию SQLAlchemy через Depends(getdb)
и делегирует операции над данными в слой репозиториев (UserRepository).
"""

from typing import (
    List,
    Dict
)
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Response,
)
from sqlalchemy.ext.asyncio import AsyncSession
from src.task_manager.database_core.database import get_db
from src.task_manager.repositories import UserRepository
from src.task_manager.schemas import (
    DbUser,
    UserCreate,
    UserUpdate
)

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.get(
    "",
    summary="Получить список всех пользователей",
    response_model=List[DbUser]
)
async def get_users(
        session: AsyncSession = Depends(get_db)
) -> List[DbUser | None]:
    """
    Получает список всех пользователей.

    :param session: Асинхронная сессия.
    :return: List[DbUser] - Список объектов DbUser, представляющих пользователей.
    """
    users = await UserRepository.get_all(
        session=session
    )
    return users


@router.get(
    "/{user_id}",
    summary="Получить конкретного пользователя",
    response_model=DbUser
)
async def get_user(
        user_id: int,
        session: AsyncSession = Depends(get_db),
) -> DbUser:
    """
    Получает информацию о пользователе по его ID.

    :param user_id: ID пользователя.
    :param session: Асинхронная сессия.
    :return: DbUser - Объект DbUser, представляющий пользователя.
    """
    user = await UserRepository.get_one(
        user_id=user_id,
        session=session
    )
    if user:
        return user
    raise HTTPException(status_code=404, detail="User is not exist")


@router.post(
    "",
    summary="Создать нового пользователя",
    response_model=DbUser
)
async def add_user(
        user: UserCreate,
        session: AsyncSession = Depends(get_db),
) -> DbUser:
    """
    Создает нового пользователя.

    :param user: Объект UserCreate, содержащий данные для нового пользователя.
    :param session: Асинхронная сессия.
    :return: DbUser - Объект DbUser, представляющий созданного пользователя.
    """
    db_user = await UserRepository.add_user(
        user=user,
        session=session,
    )
    return db_user


@router.put(
    "/{user_id}",
    summary="Обновить информацию о пользователе",
    response_model=DbUser
)
async def update_user(
        user_id: int,
        user_for_update: UserUpdate,
        session: AsyncSession = Depends(get_db),
) -> DbUser:
    """
    Обновляет информацию о пользователе по его ID.

    :param user_id: ID пользователя.
    :param user_for_update:  Объект UserUpdate, содержащий новые данные для пользователя.
    :param session: Асинхронная сессия.
    :return: DbUser - Объект DbUser, представляющий обновленного пользователя.
    """
    user = await UserRepository.update_user(
        user_id=user_id,
        user_update=user_for_update,
        session=session,
    )
    if user:
        return user

    raise HTTPException(status_code=404, detail="User is not exist")


@router.delete(
    "/{user_id}",
    summary="Удалить пользователя"
)
async def delete_user(
        user_id: int,
        session: AsyncSession = Depends(get_db)
) -> Response:
    """
    Удаляет пользователя по его ID.

    :param user_id: ID пользователя.
    :param session: Асинхронная сессия.
    :return: Dict[str, str] - Словарь с сообщением об успешном удалении.
    """
    user_for_delete = await UserRepository.delete_user(
        user_id=user_id,
        session=session,
    )
    if not user_for_delete:
        raise HTTPException(status_code=404, detail="User is not exists")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
