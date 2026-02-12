from typing import Any, Optional

from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.alchemy import get_session
from src.apps.users.models import User
from src.oauth2.tokens import oauth2_scheme, verify_access_token


async def get_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Возвращает пользователя по ID."""
    
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        response_data = {
            "status_code": status.HTTP_404_NOT_FOUND,
            "detail": "Объект не найден"
        }
        raise HTTPException(**response_data)
    return user


async def get_current_user(
    token: Any = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> Optional[User]:
    """Возвращает текущего пользователя по токену."""

    return await get_user_by_id(18, session=session) # token.id)
