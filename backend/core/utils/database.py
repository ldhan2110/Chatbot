from sqlalchemy import Engine, create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker
from settings import settings
from core.models.db_models import Base


# Init Database Engine
blueprint_db_engine = create_engine(settings.blueprint_database_url)
chatbot_db_engine = create_async_engine(settings.database_url)


class DatabaseTool:
    def __init__(self, engine: Engine):
        self.engine = engine

    def run(self, sql: str, params: dict = None):
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            return [dict(row._mapping) for row in result]

    async def migration(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


class AsyncDatabaseTool:
    def __init__(self,  engine: AsyncEngine):
        self.engine = engine

    def get_session(self):
        return sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )()

    async def run(self, sql: str, params: dict = None):
        async with self.engine.connect() as conn:
            result = await conn.execute(text(sql), params or {})
            return [dict(row._mapping) for row in result]

    async def migration(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
