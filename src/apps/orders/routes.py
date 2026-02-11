"""Набор ендпойнтов для приложения `Заказы`."""

from __future__ import annotations

import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends


from src.database.alchemy import get_session
from src.apps.orders.models import Order
from src.apps.users.models import User
from src.apps.orders.schemas import OrderCreate, OrderRead, OrderStatus

from src.apps.users.depends import get_current_user

logger = logging.getLogger(__name__)

orders_router = APIRouter()


@orders_router.post(
    "/",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    description="Регистрация нового пользователя"
)
async def create_order(
    order_data: OrderCreate,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user)
) -> OrderRead:
    """Создает (регистрирует) нового пользователя."""

    to_create_json = order_data.model_dump_json()
    to_create = json.loads(to_create_json)
    new_order = Order(**to_create)

    session.add(new_order)
    try:
        await session.commit()
    except SQLAlchemyError as exc:
        response_data = {
            "status_code": status.HTTP_400_BAD_REQUEST,
            "detail": f"Ошибка SQLAlchemy: {exc}"
        }
        raise HTTPException(**response_data) from exc

    await session.refresh(new_order)

    return OrderRead.model_validate(new_order, from_attributes=True)

