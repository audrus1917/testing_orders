"""Создание и верификация токена."""

from typing import Any
from datetime import datetime, timedelta

import jwt

from fastapi import status, HTTPException
from fastapi.security import OAuth2PasswordBearer


from src.core.config import get_settings

from . import schemas

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.APPLICATION.ACCESS_TOKEN_EXPIRE_SECONDS

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict[str, Any]) -> str:
    """Создает и возвращает JWT-токен."""

    expire = datetime.now(settings.TZ) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise jwt.DecodeError
        token_data = schemas.TokenData(id=user_id)
    except jwt.DecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные данные для аутентификации",
            headers={"WWW-Authenticate": "Bearer"}
        ) from exc

    return token_data
