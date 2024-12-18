from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from .models import *
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import inspect, text, func
from contextlib import asynccontextmanager


class Database:
    def __init__(self):
        self.async_engine = create_async_engine("sqlite+aiosqlite:///./database.db", echo=True)
        self.async_session_factory = async_sessionmaker(bind=self.async_engine, expire_on_commit=False)

    async def initialize(self):
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def get_async_session(self):
        async with self.async_session_factory() as session:
            yield session

    async def is_exist(self):
        async with self.async_engine.connect() as conn:
            return await conn.run_sync(self._check_tables_exist)

    def _check_tables_exist(self, conn):
        inspector = inspect(conn)
        table_names = inspector.get_table_names()
        expected_tables = [table.name for table in Base.metadata.sorted_tables]

        return all(table in table_names for table in expected_tables)

    async def execute_raw_sql(self, sql_query, *params):
        """
        Выполняет чистый SQL-запрос.

        :param sql_query: Строка с SQL-запросом
        :param params: Дополнительные параметры для запроса
        :return: Результат выполнения запроса
        """
        async with self.get_async_session() as db:
            try:

                result = await db.execute(text(sql_query), params)
                await db.commit()
                if result.returns_rows:
                    return await result.fetchall()
                return result.rowcount  # Возвращает количество затронутых строк
            except SQLAlchemyError as e:
                print(f"Ошибка выполнения SQL-запроса: {e}")
                return None

    # async def get_fractions(self):
    #     db = await self.get_async_session().__anext__()
    #     try:
    #         async with db.begin():
    #             stmt = select(Fraction)
    #             result = await db.execute(stmt)
    #             fractions = result.scalars().all()
    #             return fractions
    #
    #     except SQLAlchemyError as e:
    #         print(f"Error querying data: {e}")
    #         return []

    async def get_unique_cities(self):
        async with self.get_async_session() as db:
            try:

                stmt = select(Fraction.city_name, Fraction.id).group_by(Fraction.city_name)
                result = await db.execute(stmt)
                cities = result.all()
                return cities

            except SQLAlchemyError as e:
                print(f"Error querying data: {e}")
                return []

    # async def get_branches_by_city_name(self, city_name):
    #     async with self.get_async_session() as db:
    #         try:
    #
    #             stmt = select(Fraction.branch_name, Fraction.id).filter(Fraction.city_name == city_name)
    #             result = await db.execute(stmt)
    #             branches = result.all()
    #
    #             if all(x.branch_name is None for x in branches):
    #                 return None
    #             return branches
    #
    #         except SQLAlchemyError as e:
    #             print(f"Error querying data: {e}")
    #             return []

    async def get_fraction_by_id(self, id):
        async with self.get_async_session() as db:
            try:

                stmt = select(Fraction).filter(Fraction.id == id)
                result = await db.execute(stmt)
                fraction = result.scalars().first()
                return fraction

            except SQLAlchemyError as e:
                print(f"Error querying data: {e}")
                return []

    async def register_user(self, tgid, login, fraction_id):
        async with self.get_async_session() as db:
            try:
                user = User(tgid=tgid, login=login, fraction_id=fraction_id)
                db.add(user)
                await db.commit()
            except SQLAlchemyError as e:
                await db.rollback()
                print(f"Error querying data: {e}")
                return []

    async def check_user_exists(self, login=None, tgid=None):
        async with self.get_async_session() as db:
            if login and not tgid:
                try:
                    stmt = select(User).filter(User.login == login)
                    result = await db.execute(stmt)
                    user = result.scalars().first()
                    return user is not None

                except SQLAlchemyError as e:
                    print(f"Error querying data: {e}")
                    return []
            elif tgid and not login:
                try:
                    stmt = select(User).filter(User.tgid == tgid)
                    result = await db.execute(stmt)
                    user = result.scalars().first()
                    return user is not None

                except SQLAlchemyError as e:
                    print(f"Error querying data: {e}")
                    return []
            elif tgid and login:
                try:
                    stmt = select(User).filter(User.tgid == tgid, User.login == login)
                    result = await db.execute(stmt)
                    user = result.scalars().first()
                    return user is not None

                except SQLAlchemyError as e:
                    print(f"Error querying data: {e}")
                    return []

    async def add_photohunting_task(self, description):
        async with self.get_async_session() as db:
            try:
                task = Task(type=TaskType.PHOTOHUNTING, description=description)
                db.add(task)
                await db.commit()
            except SQLAlchemyError as e:
                await db.rollback()
                print(f"Error querying data: {e}")
                return []

    async def add_puzzle_task(self, description, answer):
        async with self.get_async_session() as db:
            try:
                task = Task(type=TaskType.PUZZLE, description=description, answer=answer)
                db.add(task)
                await db.commit()
            except SQLAlchemyError as e:
                await db.rollback()
                print(f"Error querying data: {e}")
                return []

    async def get_all_tasks(self):
        async with self.get_async_session() as db:
            try:

                stmt = select(Variant)
                result = await db.execute(stmt)
                tasks = result.scalars().all()
                return tasks

            except SQLAlchemyError as e:
                print(f"Error querying data: {e}")
                return []

    async def set_date_start(self, date_start: datetime.date):
        async with self.get_async_session() as db:
            try:

                # Проверяем, есть ли запись в таблице EventStart
                stmt = select(EventStart).limit(1)
                result = await db.execute(stmt)
                existing_date = result.scalars().first()

                if existing_date:
                    # Если запись существует, обновляем её
                    existing_date.date_start = date_start
                else:
                    # Если записи нет, добавляем новую
                    date = EventStart(date_start=date_start)
                    db.add(date)

                # Сохраняем изменения
                await db.commit()

            except SQLAlchemyError as e:
                await db.rollback()
                print(f"Error querying data: {e}")

    async def get_date_start(self):
        async with self.get_async_session() as db:
            try:

                stmt = select(EventStart)
                result = await db.execute(stmt)
                date = result.scalars().first()
                if date is not None:
                    return date.date_start
                return None

            except SQLAlchemyError as e:
                print(f"Error querying data: {e}")
                return []

    async def get_task_variants_by_day_and_fraction_name(self, day, fraction_name):
        async with self.get_async_session() as db:
            try:
                # Первичная фильтрация по дню
                base_stmt = (
                    select(
                        Variant.id,
                        Task.type,
                        Task.day,
                        Variant.image_url,
                        Variant.description,
                        Variant.answer,
                        Variant.hint,
                        Variant.fraction_name,
                    )
                    .join(Variant, Task.id == Variant.task_id)
                    .filter(Task.day == day)
                )

                # Проверяем, есть ли записи с fraction_name == None
                result = await db.execute(base_stmt)
                filtered_tasks = result.fetchall()

                if any(row.fraction_name is None for row in filtered_tasks):
                    # Если есть записи с fraction_name == None, возвращаем все без фильтрации по fraction_name
                    stmt = base_stmt
                else:
                    # Если таких записей нет, фильтруем дополнительно по fraction_name
                    stmt = base_stmt.filter(Variant.fraction_name == fraction_name)

                # Выполняем финальный запрос
                final_result = await db.execute(stmt)
                tasks_with_variants = final_result.fetchall()

                # Формируем результат
                return [
                    {
                        "id": row.id,
                        "type": row.type,
                        "day": row.day,
                        "image_url": row.image_url,
                        "description": row.description,
                        "answer": row.answer,
                        "hint": row.hint,
                    }
                    for row in tasks_with_variants
                ]
            except SQLAlchemyError as e:
                print(f"Error querying data: {e}")
                return []

    async def create_user_task(self, user_id, task_id, day):
        async with self.get_async_session() as db:
            try:
                user_task = UserTask(user_id=user_id, points=0, task_id=task_id, day=day, result_url=None)
                db.add(user_task)
                await db.commit()
            except SQLAlchemyError as e:
                await db.rollback()
                print(f"Error querying data: {e}")
                return []

    async def get_all_tasks_by_type(self, task_type: TaskType):
        async with self.get_async_session() as db:
            try:

                stmt = select(Task).where(Task.type == task_type.value)
                result = await db.execute(stmt)
                tasks = result.scalars().all()
                return tasks
            except SQLAlchemyError as e:
                print(f"Error querying data: {e}")
                return []

    async def get_user_tasks(self, user_id):
        async with self.get_async_session() as db:
            try:

                stmt = select(UserTask).where(UserTask.user_id == user_id)
                result = await db.execute(stmt)
                tasks = result.scalars().all()
                return tasks

            except SQLAlchemyError as e:
                print(f"Error querying data: {e}")
                return []

    async def get_distributed_tasks(self):
        async with self.get_async_session() as db:
            try:

                stmt = select(UserTask)
                result = await db.execute(stmt)
                tasks = result.scalars().all()
                return tasks

            except SQLAlchemyError as e:
                print(f"Error querying data: {e}")
                return []

    async def get_user_tasks_by_day(self, user_id, day):
        async with self.get_async_session() as db:
            try:

                stmt = (
                    select(UserTask)
                    .join(Task, UserTask.task_id == Task.id)
                    .where(UserTask.user_id == user_id, UserTask.day == day)
                )
                result = await db.execute(stmt)
                tasks = result.scalars().all()
                return tasks

            except SQLAlchemyError as e:
                print(f"Error querying data: {e}")
                return []

    async def get_user_task_by_day(self, user_id, day):
        async with self.get_async_session() as db:
            try:
                stmt = (
                    select(Variant.description,
                           Variant.image_url,
                           Variant.hint,
                           Task.type,
                           Variant.answer,
                           UserTask.points,
                           UserTask.id.label("user_task_id"),
                           Variant.id.label("variant_id")
                           ).join(UserTask, UserTask.task_id == Variant.id
                                  ).join(Task, Variant.task_id == Task.id)
                    .where(UserTask.user_id == user_id, UserTask.day == day)
                )
                result = await db.execute(stmt)
                task = result.first()
                return task

            except SQLAlchemyError as e:
                print(f"Error querying data: {e}")
                return []

    async def get_fraction_points(self, fraction_id):
        async with self.get_async_session() as db:
            try:
                stmt = (
                    select(func.sum(UserTask.points))  # Сумма очков из users_tasks
                    .join(User, UserTask.user_id == User.tgid)  # Присоединяем пользователей
                    .join(Fraction, User.fraction_id == Fraction.id)  # Присоединяем фракции
                    .where(Fraction.id == fraction_id)  # Условие: ID фракции
                )
                result = await db.execute(stmt)
                total_points = result.scalar()
                return total_points or 0

            except SQLAlchemyError as e:
                print(f"Error querying data: {e}")
                return []

    async def get_user_by_id(self, user_id):
        async with self.get_async_session() as db:
            try:

                stmt = select(User, User.tgid == user_id)
                result = await db.execute(stmt)
                user = result.scalars().first()
                return user

            except SQLAlchemyError as e:
                print(f"Error querying data: {e}")
                return []

    async def get_fractions_points(self):
        async with self.get_async_session() as db:
            try:
                stmt = (
                    select(Fraction.id, Fraction.fraction_name,
                           func.sum(UserTask.points))  # Сумма очков для каждой фракции
                    .join(User, UserTask.user_id == User.tgid)  # Присоединяем пользователей
                    .join(Fraction, User.fraction_id == Fraction.id)  # Присоединяем фракции
                    .group_by(Fraction.id, Fraction.fraction_name)  # Группируем по ID и названию фракции
                )
                result = await db.execute(stmt)
                fractions_points = result.all()  # Получаем список всех фракций с их очками
                return fractions_points

            except SQLAlchemyError as e:
                print(f"Error querying data: {e}")
                return []

    async def get_all_users(self):
        async with self.get_async_session() as db:
            try:
                stmt = select(User)
                result = await db.execute(stmt)
                users = result.scalars().all()
                return users
            except SQLAlchemyError as e:
                print(f"Error querying data: {e}")
                return []

    async def add_points(self, user_task_id, points):
        async with self.get_async_session() as db:
            try:

                stmt = select(UserTask).where(UserTask.id == user_task_id)
                result = await db.execute(stmt)
                user_task = result.scalars().first()
                if user_task:
                    # Если запись существует, обновляем её
                    user_task.points = points
                # Сохраняем изменения
                await db.commit()

                answer = user_task.user_id
                return answer

            except SQLAlchemyError as e:
                await db.rollback()
                print(f"Error querying data: {e}")

    async def get_hint_by_variant_id(self, variant_id):
        async with self.get_async_session() as db:
            try:
                stmt = select(Variant.hint).where(Variant.id == variant_id)
                result = await db.execute(stmt)
                hint = result.scalars().first()
                return hint

            except SQLAlchemyError as e:
                await db.rollback()
                print(f"Error querying data: {e}")

    async def set_user_answer(self, user_task_id, answer=None, result_url=None):
        async with self.get_async_session() as db:
            try:
                stmt = select(UserTask).where(UserTask.id == user_task_id)
                result = await db.execute(stmt)
                user_task = result.scalars().first()

                # обновляем запись
                user_task.result_url = result_url
                user_task.user_answer = answer

                # Сохраняем изменения
                await db.commit()

            except SQLAlchemyError as e:
                await db.rollback()
                print(f"Error querying data: {e}")


database = Database()
