"""
Модуль модели задач (TaskModel) для SQLAlchemy.

"""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.task_manager.database_core.database import Base


class TaskModel(Base):
    """
    Модель задачи.

    Атрибуты:
    - id: первичный ключ (целое число).
    - title: заголовок задачи (строка).
    - body: подробное описание задачи (строка).
    - status: строковое поле для статуса задачи.
    - user: целочисленное поле, содержащее внешний ключ на таблицу users (users.id).
    - author: ORM-отношение (relationship) к модели UserModel; связывает задачу с её автором.
      Свойство back_populates должно соответствовать атрибуту в UserModel, который содержит
      список задач (например, tasks).
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    body = Column(String)
    status = Column(String)
    user = Column(Integer, ForeignKey("users.id"))
    author = relationship("UserModel", back_populates="tasks")
