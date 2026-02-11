"""Класс модели `Заказы`."""

from __future__ import annotations
from typing import TYPE_CHECKING, Dict, Any

import uuid

from decimal import Decimal

from sqlalchemy import Numeric, Enum, Index, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID

from src.database.alchemy import Base
from src.database.alchemy.mixins import JSONRepresentationMixin, ChangedAtMixin

from .enums import OrderStatus


if TYPE_CHECKING:
    from src.apps.users.models import User


class Order(
    ChangedAtMixin,
    JSONRepresentationMixin,
    Base
):
    """Класс модели для пользователей."""

    __tablename__ = 'orders'

    id: Mapped[UUID] = mapped_column(
        UUID, 
        primary_key=True, 
        default=uuid.uuid4
    )
    user: Mapped["User"] = relationship(
        "User",
        back_populates='person',
        lazy='select',
        uselist=False,
    )
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        default=0.
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), 
        nullable=False, 
        default=OrderStatus.PENDING,
        index=True
    )
    items: Mapped[Dict[str, Any]] = mapped_column(JSONB)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id")
    )
    user: Mapped["User"] = relationship("User", lazy="select")
    __table_args__ = (
        Index(
            'idx_items_product_id_gin',
            items['products'],
            postgresql_using='gin',
            postgresql_ops={'products': 'jsonb_ops'} 
        ),
    )

    def __repr__(self) -> str:
        return f"Order(id={self.id})"
