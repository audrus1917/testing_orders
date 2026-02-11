"""The routes for :cls:`User`."""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends


from src.database.alchemy import get_session
from src.apps.users.models import User
from src.apps.users.schemas import UserCreate, UserRead
from src.oauth2.passwords import get_password_hash
from src.apps.response_schemas import UniqueConstraint

logger = logging.getLogger(__name__)

users_router = APIRouter()


@users_router.post(
    "/register/",
    responses={
        status.HTTP_201_CREATED: {"model": UserRead},
        status.HTTP_400_BAD_REQUEST: {"model": UniqueConstraint}
    },
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    description="Регистрация нового пользователя"
)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
) -> UserRead:
    """Создает (регистрирует) нового пользователя."""

    to_create = user_data.model_dump()
    password = to_create.pop("password")
    to_create["hashed_password"] = get_password_hash(password)

    new_user = User(**to_create)

    session.add(new_user)
    try:
        await session.commit()
    except IntegrityError as exc:
        response_data = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "detail": f"Ключ <{user_data.email}> уже существует"
        }
        raise HTTPException(**response_data) from exc

    await session.refresh(new_user)

    return UserRead.model_validate(new_user, from_attributes=True)

