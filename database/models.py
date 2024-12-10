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
    user_answer = Column(Text)
    result_url = Column(Text)


class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    type = Column(Enum(TaskType))
    day = Column(Integer)


class Variant(Base):
    __tablename__ = 'variants'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer)
    fraction_name = Column(Text)
    image_url = Column(Text)
    description = Column(Text)
    answer = Column(Text)
    hint = Column(Text)


class Fraction(Base):
    __tablename__ = 'fractions'
    id = Column(Integer, primary_key=True)
    city_name = Column(String)
    fraction_name = Column(String)


# class FractionsTaskTypes(Base):
#     __tablename__ = 'fractions_task_types'
#     id = Column(Integer, primary_key=True)
#     fraction_id = Column(Integer)
#     day = Column(Integer)
#     task_type = Column(Enum(TaskType))


class EventStart(Base):
    __tablename__ = 'events_start'
    id = Column(Integer, primary_key=True)
    date_start = Column(Date)
