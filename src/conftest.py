from typing import AsyncGenerator

import pytest

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.pool import NullPool

from src.core.config import get_settings
from src.database.alchemy import Base

from sqlalchemy.ext.asyncio import AsyncEngine


settings = get_settings()


@pytest.fixture(scope='session')
def anyio_backend() -> str:
    """Returns the backends and their options that tests and fixtures are run with."""

    return 'asyncio'


@pytest.fixture(scope='session')
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    async_engine_main = create_async_engine(
        'postgresql+asyncpg://postgres@localhost/postgres',
        poolclass=NullPool,
    )
    async with async_engine_main.connect() as connection:
        await connection.execute(text('COMMIT;'))
        await connection.execute(text(f'CREATE DATABASE {settings.db.DATABASE};'))

    async_engine = create_async_engine(settings.db.uri)
    async with async_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield async_engine

    await async_engine.dispose()
    async with async_engine_main.connect() as connection:
        await connection.execute(text('COMMIT;'))
        await connection.execute(text(f'DROP DATABASE {settings.db.DATABASE};'))


@pytest.fixture(scope='session')
def async_session_class(engine: AsyncEngine):
    """Returns session maker."""

    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


@pytest.fixture(scope='function')
def decl_base():
    yield Base
    Base.registry.dispose()


@pytest.fixture(scope='function', autouse=True)
async def session(async_session_class) -> AsyncGenerator[AsyncSession, None]:
    """Yields the sessiom."""

    async with async_session_class() as async_session:
        yield async_session
        for table in reversed(Base.metadata.sorted_tables):
            await async_session.execute(text(f'TRUNCATE {table.name} CASCADE;'))
        await async_session.commit()
