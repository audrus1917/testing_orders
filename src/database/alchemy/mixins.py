"""Классы ``mixins``."""

import datetime

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.core.config import get_settings

SETTINGS = get_settings()
TZ = datetime.timezone(datetime.timedelta(hours=SETTINGS.tz_offset))


class ChangedAtMixin:
    """Миксин для полей ``..._at`` (дата / время)."""

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.now(tz=TZ)
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.datetime.now(tz=TZ),
        onupdate=datetime.datetime.now(tz=TZ),
        nullable=True,
    )


class ChangedByMixin:
    """Миксин для полей идентификатора пользовалетя '..._by'."""

    created_by: Mapped[int] = mapped_column(Integer, nullable=True)
    updated_by: Mapped[int] = mapped_column(Integer, nullable=True)


class JSONRepresentationMixin:
    """"""

    def to_json(self) -> dict:
        return {
            column: value
            for column, value in self.__dict__.items()
            if not column.startswith('_')
        }
