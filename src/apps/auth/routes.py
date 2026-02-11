"""Аутентификация через `OAuth2 Password Flow`."""

from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.alchemy import get_session
from src.apps.users.models import User
from src.oauth2.tokens import schemas, create_access_token
from src.oauth2.passwords import verify_password
from src.apps.response_schemas import InvalidCredentials

auth_router = APIRouter(tags=["Authentication"])


@auth_router.post(
    "/token/",
    response_model=schemas.Token,
    responses={
        status.HTTP_200_OK: {"model": schemas.Token},
        status.HTTP_403_FORBIDDEN: {"model": InvalidCredentials}
    },
    description="Получение токена"
)
async def token(
    user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session)
):
    """Получение токена."""

    stmt = select(User).where(User.email == user_credentials.username)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(
        user_credentials.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ошибка учетных данных"
        )

    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
