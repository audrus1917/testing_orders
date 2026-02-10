"""The dependencies for User."""

from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.alchemy import get_session

from src.apps.users.models import User
from src.apps.users.manager import UserManager


async def _get_user_db(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(
    user_db=Depends(_get_user_db)
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


__all__ = ['get_user_manager']

