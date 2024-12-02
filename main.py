from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, delete, Column, Integer, String, Boolean, ForeignKey, Date, inspect, select, Enum
import enum

Base = declarative_base()


class TaskType(enum.Enum):
    PHOTOHUNTING = "photo_hunting"
    PUZZLE = "puzzle"


class User(Base):
    __tablename__ = 'users'
    tgid = Column(Integer, primary_key=True)
    login = Column(String)
    fraction_id = Column(Integer)


class UserTask(Base):
    __tablename__ = 'users_tasks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    points = Column(Integer)
    task_id = Column(Integer)


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    type = Column(Enum(TaskType))
    description = Column(String)
    answer = Column(String)


class Fraction(Base):
    __tablename__ = 'fractions'
    id = Column(Integer, primary_key=True)
    city_name = Column(Enum(TaskType))
    fraction_name = Column(String)