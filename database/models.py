from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, delete, Column, Integer, String, Boolean, ForeignKey, Date, inspect, select, Enum, \
    Text
import enum

Base = declarative_base()


class TaskType(enum.Enum):
    PHOTOHUNTING = "PHOTOHUNTING"
    PUZZLE = "PUZZLE"


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
    day = Column(Integer)
    result_url = Column(Text)


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    type = Column(Enum(TaskType))
    description = Column(Text)
    answer = Column(Text)


class Fraction(Base):
    __tablename__ = 'fractions'
    id = Column(Integer, primary_key=True)
    city_name = Column(String)
    branch_name = Column(Text)
    fraction_name = Column(String)


class FractionsTaskTypes(Base):
    __tablename__ = 'fractions_task_types'
    id = Column(Integer, primary_key=True)
    fraction_id = Column(Integer)
    day = Column(Integer)
    task_type = Column(Enum(TaskType))



class EventStart(Base):
    __tablename__ = 'events_start'
    id = Column(Integer, primary_key=True)
    date_start = Column(Date)
