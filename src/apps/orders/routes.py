"""Набор ендпойнтов для приложения `Заказы`."""

from __future__ import annotations

import json
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from fastapi import BackgroundTasks, Request
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, Depends
from fastapi_cache.decorator import cache

from src.core.config import get_settings
from src.core.cache_key_builder import custom_key_builder
from src.database.alchemy import get_session
from src.apps.orders.models import Order
from src.apps.users.models import User
from src.apps.orders.schemas import (
    OrderCreate, 
    OrderRead, 
    OrderUpdateStatus,
    OrderListRead
)

from src.apps.orders.depends import get_order_by_id
from src.apps.users.depends import get_current_user, get_user_by_id
from src.apps.orders.tasks import new_order_notify

logger = logging.getLogger(__name__)
settings = get_settings()
orders_router = APIRouter()


@orders_router.post(
    "/",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    description="Добавление нового заказа"
)
async def create_order(
    request: Request,
    background_tasks: BackgroundTasks,
    order_data: OrderCreate,
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user)
) -> OrderRead:
    """Добавляет новый ордер."""

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

    result = OrderRead.model_validate(new_order, from_attributes=True)
    print('Here')
    background_tasks.add_task(
        new_order_notify, 
        request.app.state.broker_connection, 
        result
    )
    print("Here 2")
    return result


@orders_router.get(
    "/{order_id}",
    response_model=OrderRead,
    description="Получение детализированных данных о заказе"
)
@cache(
    expire=settings.APPLICATION.CACHE_TTL * 60, 
    key_builder=custom_key_builder
)
async def get_order(
    session: AsyncSession = Depends(get_session),
    order: Order = Depends(get_order_by_id),
    user: User = Depends(get_current_user),
) -> OrderRead:
    """Возвращает данные о заказе."""

    return OrderRead.model_validate(order, from_attributes=True)


@orders_router.patch(
    "/{order_id}",
    response_model=OrderRead,
    description="Добавление нового заказа"
)
async def update_order_status(
    order_status_data: OrderUpdateStatus,
    order_model: Order = Depends(get_order_by_id),
    session: AsyncSession = Depends(get_session),
    _: User = Depends(get_current_user)
) -> Order:
    """Добавляет новый ордер."""

    if order_model and order_model.status != order_status_data.status:
        order_model.status = order_status_data.status
        try:
            await session.commit()
        except SQLAlchemyError as exc:
            response_data = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "detail": f"Ошибка SQLAlchemy: {exc}"
            }
            raise HTTPException(**response_data) from exc
    return order_model


@orders_router.get(
    "/user/{user_id}",
    response_model=OrderListRead,
    description="Список заказов пользователя"
)
async def get_user_orders(
    user_model: User = Depends(get_user_by_id),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Возвращает cписок заказов пользователя."""

    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )

    stmt = select(Order).where(Order.user_id == user_model.id)
    result = await session.execute(stmt)
    rows = result.scalars()
    items = [OrderRead.model_validate(rows) for rows in rows]
    return {"items": items, "total": len(items)}
