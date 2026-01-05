"""
Pydantic-схемы (модели) для объектов "задача" (Task).

Этот модуль содержит входные/выходные и вспомогательные модели:
- TaskBase: базовая модель задачи с общими валидациями;
- TaskCreate: модель для создания задачи (наследует TaskBase);
- TaskUpdate: модель для частичного/полного обновления задачи;
- DbTask: модель представления задачи из БД (ответ).
"""

from typing import Literal
from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)


class TaskBase(BaseModel):
    """
    Базовая схема для задачи.

    Attributes:
        title (str): Заголовок задачи.  Обязательное поле, длина от 2 до 200 символов.
        body (str): Описание задачи.  Обязательное поле, длина от 2 до 200 символов.
        status (Literal["New", "In process", "Finished"]): Статус задачи.  Обязательное поле, может принимать одно из предопределенных значений.
        user (int): ID пользователя, которому назначена задача.  Обязательное поле, должно быть больше или равно 1.

    model_config = ConfigDict(extra='forbid') - Запрещает передачу дополнительных полей, не определенных в модели.
    """
    title: str = Field(..., min_length=2, max_length=200)
    body: str = Field(..., min_length=2, max_length=200)
    status: Literal["New", "In process", "Finished"] = Field(...)
    user: int = Field(..., ge=1)

    model_config = ConfigDict(extra='forbid')


class TaskCreate(TaskBase):
    """
    Схема для создания новой задачи.

    Наследуется от TaskBase, поэтому содержит те же поля и валидации.
    """
    pass


class TaskUpdate(BaseModel):
    """
    Схема для обновления существующей задачи.

    Attributes:
        title (str, optional): Новый заголовок задачи. Длина от 2 до 20 символов.
        Если не указан, заголовок не изменяется.
        body (str, optional): Новое описание задачи.  Длина от 20 до 200 символов.
        Если не указан, описание не изменяется.
        status (Literal["New", "In process", "Finished"]): Новый статус задачи. Обязательное поле, может принимать одно
        из предопределенных значений.
    """
    title: str = Field(default=None, min_length=2, max_length=20)
    body: str = Field(default=None, min_length=20, max_length=200)
    status: Literal["New", "In_process", "Finished"] = Field(...)


class DbTask(BaseModel):
    """
    хема для представления задачи в базе данных.

    Attributes:
        id (int): ID задачи.
        title (str): Заголовок задачи.
        body (str): Описание задачи.
        status (str): Статус задачи.
        user (int | str | None): ID пользователя, которому назначена задача.  Может быть целым числом, строкой или None.

    class Config:
        from_attributes = True -  Позволяет создавать объекты DbTask из объектов, имеющих атрибуты с такими же именами.
    """
    id: int
    title: str
    body: str
    status: str
    user: int | str | None

    class Config:
        from_attributes = True
