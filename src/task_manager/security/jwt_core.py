"""
JWT‑утилиты и зависимости FastAPI для аутентификации пользователей.

Этот модуль предоставляет:
- создание (encodejwt) и разбор (decodejwt) JWT токенов;
- dependency gettoken — извлекает и декодирует токен из заголовка Authorization;
- dependency getcurrentuser — получает текущего пользователя из БД по payload токена.
"""

from datetime import (
    timedelta,
    datetime,
    timezone
)
import jwt
from fastapi import (
    Depends,
    HTTPException
)
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession
from src.task_manager.database_core.database import get_db
from src.task_manager.repositories import UserRepository
from src.task_manager.schemas import DbUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/service_user/login")

# Настройки JWT
SECRET_KEY = "my_secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10


async def encode_jwt(
        payload: dict,
        algorithm: str = ALGORITHM,
        expire_timedelta: timedelta | None = None,
        expire_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
        secret_key: str = SECRET_KEY
) -> str | bytes:
    """
    Создаёт JWT на основе payload.

    :param payload: Собственная полезная нагрузка токена.
    :param algorithm: Алгоритм подписи (по умолчанию HS256).
    :param expire_timedelta: Явный таймаут для срока годности токена (если указан, имеет приоритет).
    :param expire_minutes: Если expiretimedelta не указан, используется это число минут.
    :param secret_key: Секретный ключ для подписи токена.
    :return: Закодированный JWT (str).
    """
    to_encode = payload.copy()
    now = datetime.now(timezone.utc)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)
    to_encode.update(
        exp=expire,
    )
    encoded = jwt.encode(to_encode, secret_key, algorithm)
    return encoded


async def decode_jwt(
        access_token: str | bytes,
        algorithm: str = ALGORITHM,
        secret_key: str = SECRET_KEY
) -> dict:
    """
    Декодирует и верифицирует JWT.

    :param access_token: Входной токен (str или bytes).
    :param algorithm: Алгоритм проверки.
    :param secret_key: Секрет для проверки подписи.
    :return: Декодированный payload (dict) при успешной валидации.
    """
    try:
        decode = jwt.decode(access_token, secret_key, algorithms=[algorithm])
        return decode
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


async def get_token(
        token: str = Depends(oauth2_scheme),
) -> dict:
    """
    FastAPI dependency: извлекает токен из заголовка Authorization и возвращает декодированный payload.

    :param token: передаётся автоматически через Depends(oauth2scheme)).
    :return: payload (dict) полученный из decodejwt.
    """
    try:
        payload = await decode_jwt(
            access_token=token,
        )
    except InvalidTokenError as error:
        raise HTTPException(
            status_code=401,
            detail=f"invalid token error: {error}"
        )
    return payload


async def get_current_user(
        payload: dict = Depends(get_token),
        session: AsyncSession = Depends(get_db)
) -> DbUser:
    """
    FastAPI dependency: по payload токена получает объект пользователя из репозитория.

    :param payload: Словарь claims токена, ожидается наличие ключа "sub" (идентификатор пользователя).
    :param session: Асинхронная сессия.
    :return: Объект пользователя, возвращаемый UserRepository.get_one.
    """
    user_id: int | None = payload.get("sub")
    if user := await UserRepository.get_one(
            user_id,
            session=session,
    ):
        return user
    raise HTTPException(
        status_code=401,
        detail="user not found"
    )
