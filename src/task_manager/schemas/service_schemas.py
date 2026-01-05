"""
Pydantic-схемы и вспомогательные типы для сервиса аутентификации и управления задачами.

Этот модуль содержит расширения и вспомогательные модели поверх базовых схем из
src.myproject.schemas, используемые в сервисных эндпоинтах (например, для логина,
выдачи токенов и передачи статуса задачи).
"""

from enum import Enum
from pydantic import (
    EmailStr,
    BaseModel,
    Field
)
from src.task_manager.schemas import (
    UserBase,
    TaskCreate
)


class UserLogin(UserBase):
    """
    Схема для данных, необходимых для входа пользователя в систему.

    Attributes:
        email (EmailStr | None, optional): Email пользователя. Defaults to None.
    """
    email: EmailStr | None = None


class TokenInfo(BaseModel):
    """
    Схема для информации о токене доступа.

    Attributes:
        access_token (str): Токен доступа.
        token_type (str): Тип токена (например, "Bearer").
    """
    access_token: str
    token_type: str


class TaskStatus(str, Enum):
    """
    Перечисление для представления возможных статусов задачи.

    Attributes:
        New (str): Задача новая.
        In_process (str): Задача в процессе выполнения.
        Finished (str): Задача завершена.
    """
    New = "New"
    In_process = "In_process"
    Finished = "Finished"


class TaskCreateService(TaskCreate):
    """
    Схема для создания задачи, используемая в сервисе.

    Attributes:
        status (TaskStatus): Статус задачи.  Обязательное поле.
    """
    status: TaskStatus = Field(...)
