from .models import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import inspect


class Database:
    def __init__(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///./database.db", echo=True)
        self.Session = async_sessionmaker(self.engine, expire_on_commit=False)

    async def initialize(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self):
        async with self.Session() as session:
            yield session

    async def is_exist(self):
        async with self.engine.connect() as conn:
            return await conn.run_sync(self._check_tables_exist)

    def _check_tables_exist(self, conn):
        inspector = inspect(conn)
        table_names = inspector.get_table_names()
        expected_tables = [table.name for table in Base.metadata.sorted_tables]

        return all(table in table_names for table in expected_tables)


db = Database()
