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

    async def get_fractions(self):
        db = await self.get_async_session().__anext__()
        try:
            async with db.begin():
                stmt = select(Fraction)
                result = await db.execute(stmt)
                fractions = result.scalars().all()
                return fractions

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


database = Database()
