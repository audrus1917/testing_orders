from typing import Any, Optional

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.alchemy import get_session
from src.apps.users.models import User
from src.oauth2.tokens import oauth2_scheme, verify_access_token


async def get_current_user(
    token: Any = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> Optional[User]:
    """Возвращает текущего пользователя."""
    
    token = verify_access_token(token)
    result = await session.execute(
        select(User).where(User.id == token.id)
    )
    user = result.scalar_one_or_none()
    return user
