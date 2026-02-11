"""Классы схем для приложения :mod:`users`."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    """Схема для создания пользователя."""

    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: bool = True


class UserRead(BaseModel):
    """Схема для вывода данных пользователя."""

    id: int
    email: EmailStr
    created_at: datetime
    is_active: bool = True
    is_superuser: bool = True

    model_config = ConfigDict(from_attributes=True)    


class UserUpdate(BaseModel):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: bool = True
