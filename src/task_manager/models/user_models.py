"""
Модуль модели пользователя (UserModel) для SQLAlchemy.

Содержит декларативную модель UserModel, которая описывает таблицу пользователей
в базе данных и связанное с ней ORM-отношение к задачам пользователя.
"""

from sqlalchemy import (
    Column,
    Integer,
    String
)
from sqlalchemy.orm import relationship
from src.task_manager.database_core.database import Base


class UserModel(Base):
    """
    Модель пользователя.

    Атрибуты:
    - id: первичный ключ (целое число).
    - name: имя пользователя.
    - email: адрес электронной почты.
    - password: пароль.
    - tasks: ORM-отношение к задачам пользователя (список TaskModel), двунаправленное
      через backpopulates="author" в TaskModel.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    tasks = relationship("TaskModel", back_populates="author")
