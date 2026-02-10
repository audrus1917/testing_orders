"""Классы ``mixins``."""

import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.core.config import get_settings

SETTINGS = get_settings()
TZ = datetime.timezone(datetime.timedelta(hours=SETTINGS.TZ_OFFSET))


class ChangedAtMixin:
    """Миксин для полей ``..._at`` (дата / время)."""

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.datetime.now(tz=TZ)
    )


class JSONRepresentationMixin:
    def to_json(self) -> dict:
        return {
            column: value
            for column, value in self.__dict__.items()
            if not column.startswith('_')
        }
