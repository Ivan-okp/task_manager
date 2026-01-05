"""
Pydantic‑схемы (модели) для сущности "пользователь" (User).

Этот модуль содержит входные/выходные и вспомогательные модели:
- UserBase — базовая модель пользователя с валидацией полей;
- UserCreate — модель для создания пользователя (наследует UserBase);
- UserUpdate — модель для частичного обновления пользователя;
- DbUser — модель представления пользователя, возвращаемая из БД (ответ).
"""

from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    ConfigDict
)


class UserBase(BaseModel):
    """
    Базовая схема для пользователя.

    Attributes:
        name (str): Имя пользователя. Обязательное поле, длина от 2 до 20 символов.
        email (EmailStr): Email пользователя. Обязательное поле, должно быть в правильном формате email.
        password (str): Пароль пользователя. Обязательное поле, длина не менее 8 символов.

    model_config = ConfigDict(extra='forbid') - Запрещает передачу дополнительных полей, не определенных в модели.
    """
    name: str = Field(..., min_length=2, max_length=20)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8)

    model_config = ConfigDict(extra='forbid')


class UserCreate(UserBase):
    """
    Схема для создания нового пользователя.

    Наследуется от UserBase, поэтому содержит те же поля и валидации.
    """
    pass


class UserUpdate(UserBase):
    """
    Схема для обновления существующего пользователя.

    Attributes:
        name (str, optional): Новое имя пользователя. Длина от 2 до 20 символов. Если не указано, имя не изменяется.
        email (EmailStr, optional): Новый email пользователя. Если не указан, email не изменяется.
        password (str, optional): Новый пароль пользователя. Длина не менее 8 символов. Если не указан, пароль
        не изменяется.
    """
    name: str = Field(default=None, min_length=2, max_length=20)
    email: EmailStr = Field(default=None)
    password: str = Field(default=None, min_length=8)


class DbUser(UserBase):
    """
    Схема для представления пользователя в базе данных.

    Attributes:
        id (int): ID пользователя.

    class Config:
        from_attributes = True - Позволяет создавать объекты DbUser из объектов, имеющих атрибуты с такими же именами.
    """
    id: int

    class Config:
        from_attributes = True
