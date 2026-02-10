"""Класс модели :cls:`User`."""

from __future__ import annotations

from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable

from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.database.alchemy import Base
from src.database.alchemy.mixins import JSONRepresentationMixin, ChangedAtMixin


class User(
    ChangedAtMixin, 
    JSONRepresentationMixin, 
    SQLAlchemyBaseUserTable[int], 
    Base
):
    """Класс модели для пользователей."""

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(length=320),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(length=1024),
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False
    )
    last_login: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f'User(email={self.email})'

