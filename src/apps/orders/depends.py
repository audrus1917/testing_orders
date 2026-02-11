import uuid

from fastapi import Depends, status
from fastapi.exceptions import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.alchemy import get_session
from src.apps.orders.models import Order


async def get_order_by_id(
    order_id: uuid.UUID, 
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        response_data = {
            "status_code": status.HTTP_404_NOT_FOUND,
            "detail": "Объект не найден"
        }
        raise HTTPException(**response_data)
    yield order
