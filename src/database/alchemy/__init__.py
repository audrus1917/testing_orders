from typing import Final

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.core.config import get_settings

SETTINGS = get_settings()

METADATA: Final = MetaData()


class Base(DeclarativeBase):
    metadata = METADATA


engine: AsyncEngine = create_async_engine(
    SETTINGS.DB.uri,
    future=True,
)


async def get_session():
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
