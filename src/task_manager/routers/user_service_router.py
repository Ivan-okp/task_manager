"""
Маршруты сервиса для работы с учетной записью пользователя.
"""

from fastapi import (
    APIRouter,
    Form,
    Depends,
    HTTPException,
    status,
    Response
)
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from src.task_manager.database_core.database import get_db
from src.task_manager.repositories import (
    UserRepository,
    ServiceRepository
)
from src.task_manager.schemas import (
    DbUser,
    UserCreate,
    TokenInfo,
    UserUpdate
)
from src.task_manager.security import (
    encode_jwt,
    get_current_user
)

from src.task_manager.logger_core import logger
from src.task_manager.models import UserModel

router = APIRouter(
    prefix="/service_user",
    tags=["Сервис (работа с учетной записью)"]
)


@router.post(
    "/create_user",
    summary="Создание учетной записи",
    response_model=DbUser
)
async def create_new_user(
    session: AsyncSession = Depends(get_db),
    name: str | None = Form(...),
    email: str | EmailStr = Form(...),
    password: str | None = Form(...),
) -> DbUser:
    """
    Создать нового пользователя.

    :param session: Асинхронная сессия.
    :param name: Имя пользователя.
    :param email: Email пользователя.
    :param password: Пароль пользователя.
    :return: DbUser - Объект DbUser, представляющий пользователя.
    """
    logger.info(
        f"API Request: Attempting to create new user. Name: '{name}', Email: '{email}'."
    )

    if name is None or email is None or password is None:
        raise HTTPException(
            status_code=422,
            detail="Incomplete content "
        )
    new_user = UserCreate(
        name=name,
        email=email,
        password=password
    )
    db_user = await UserRepository.add_user(
        user=new_user,
        session=session,
    )
    logger.info(
        f"API Response: User successfully created. User ID: {db_user.id}, Name: '{db_user.name}', Email: '{db_user.email}'."
    )

    return db_user


@router.post(
    "/login",
    summary="Регистрация для работы с задачами",
    response_model=TokenInfo
)
async def login_for_create_task(
    session: AsyncSession = Depends(get_db),
    username: str | None = Form(...),
    password: str | None = Form(...),
) -> TokenInfo:
    """
    Выполнить аутентификацию пользователя и вернуть JWT.

    :param session: Асинхронная сессия.
    :param username: Имя пользователя.
    :param password: Пароль пользователя.
    :return: DbUser - Объект DbUser, представляющий пользователя.
    """
    logger.info(f"API Request: User login attempt for username: '{username}'.")

    user_for_encode = await ServiceRepository.login_user(
        username=username,
        password=password,
        session=session,
    )
    if user_for_encode is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    jwt_payload = {"sub": str(user_for_encode.id), "username": user_for_encode.name}
    token = await encode_jwt(
        payload=jwt_payload
    )
    logger.info(
        f"API Response: User '{username}' (ID: {user_for_encode.id}) successfully logged in. JWT issued."
    )

    return TokenInfo(
        access_token=token,
        token_type="Bearer"
    )


@router.put(
    "/change_user",
    summary="Изменение учетной записи",
    response_model=DbUser
)
async def change_user(
    session: AsyncSession = Depends(get_db),
    name: str | None = Form(...),
    email: EmailStr | str = Form(...),
    password: str | None = Form(...),
    user: UserModel = Depends(get_current_user),
) -> DbUser:
    """
    Обновить данные текущего пользователя.

    :param session: Асинхронная сессия.
    :param name: Имя пользователя.
    :param email: Email пользователя.
    :param password: Пароль пользователя.
    :param user: Объект текущего пользователя, полученный через Dependency Injection.
    :return: DbUser - Объект DbUser, представляющий пользователя.
    """
    logger.info(f"Received request to update user with ID: {user.id}")

    user_for_change = UserUpdate(
        name=name,
        email=email,
        password=password
    )
    changed_user = await UserRepository.update_user(
        user_id=user.id,
        user_update=user_for_change,
        session=session,
    )
    logger.info(f"Successfully updated user with ID: {user.id}")

    return changed_user


@router.delete(
    "/delete_user",
    summary="Удалить учетную запись",
)
async def delete_current_user(
    session: AsyncSession = Depends(get_db),
    user: UserModel =Depends(get_current_user),
) -> Response:
    """
    Удалить учетную запись текущего пользователя.

    :param session: Асинхронная сессия.
    :param user: Объект текущего пользователя, полученный через Dependency Injection.
    :return: Dict[str, str] - Словарь с сообщением об успешном удалении.
    """
    logger.info(f"Received request to delete user with ID: {user.id}")

    user_for_delete = await UserRepository.delete_user(
        user_id=user.id,
        session=session
    )
    if not user_for_delete:
        logger.warning(f"User with ID: {user.id} not found for deletion.")

        raise HTTPException(
            status_code=404,
            detail="User is not exists"
        )

    logger.info(f"Successfully deleted user with ID: {user.id}")
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )
