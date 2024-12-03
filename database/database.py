from sqlalchemy.exc import SQLAlchemyError

from .models import *
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import inspect


class Database:
    def __init__(self):
        self.async_engine = create_async_engine("sqlite+aiosqlite:///./database.db", echo=True)
        self.async_session_factory = async_sessionmaker(bind=self.async_engine, expire_on_commit=False)

    async def initialize(self):
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

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
        db = await self.get_async_session().__anext__()
        try:
            async with db.begin():
                stmt = select(Fraction.city_name, Fraction.id).group_by(Fraction.city_name)
                result = await db.execute(stmt)
                cities = result.all()
                return cities

        except SQLAlchemyError as e:
            print(f"Error querying data: {e}")
            return []

    async def get_branches_by_city_name(self, city_name):
        db = await self.get_async_session().__anext__()
        try:
            async with db.begin():
                stmt = select(Fraction.branch_name, Fraction.id).filter(Fraction.city_name == city_name)
                result = await db.execute(stmt)
                branches = result.all()

                if all(x.branch_name is None for x in branches):
                    return None
                return branches

        except SQLAlchemyError as e:
            print(f"Error querying data: {e}")
            return []

    async def get_fraction_by_id(self, id):
        db = await self.get_async_session().__anext__()
        try:
            async with db.begin():
                stmt = select(Fraction).filter(Fraction.id == id)
                result = await db.execute(stmt)
                fraction = result.scalars().first()
                return fraction

        except SQLAlchemyError as e:
            print(f"Error querying data: {e}")
            return []

    async def register_user(self, tgid, login, fraction_id):
        db = await self.get_async_session().__anext__()
        try:
            user = User(tgid=tgid, login=login, fraction_id=fraction_id)
            db.add(user)
            await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            print(f"Error querying data: {e}")
            return []

    async def check_user_exists(self, login):
        db = await self.get_async_session().__anext__()
        try:
            async with db.begin():
                stmt = select(User).filter(User.login == login)
                result = await db.execute(stmt)
                user = result.scalars().first()
                return user is not None

        except SQLAlchemyError as e:
            print(f"Error querying data: {e}")
            return []

    async def add_photohunting_task(self, description):
        db = await self.get_async_session().__anext__()
        try:
            task = Task(type=TaskType.PHOTOHUNTING, description=description)
            db.add(task)
            await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            print(f"Error querying data: {e}")
            return []

    async def add_puzzle_task(self, description, answer):
        db = await self.get_async_session().__anext__()
        try:
            task = Task(type=TaskType.PUZZLE, description=description, answer=answer)
            db.add(task)
            await db.commit()
        except SQLAlchemyError as e:
            await db.rollback()
            print(f"Error querying data: {e}")
            return []

    async def get_all_tasks(self):
        db = await self.get_async_session().__anext__()
        try:
            async with db.begin():
                stmt = select(Task)
                result = await db.execute(stmt)
                tasks = result.scalars().all()
                return tasks

        except SQLAlchemyError as e:
            print(f"Error querying data: {e}")
            return []

database = Database()
