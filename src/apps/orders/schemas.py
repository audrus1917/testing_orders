"""Классы схем для приложения `Заказы`."""

from typing import Optional, List, Dict, Any

import uuid

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from .enums import OrderStatus


class ProductRead(BaseModel):
    """Схема для Продукта в Заказе"""

    product_id: uuid.UUID = Field(..., description="ID продукта")
    quantity: Decimal = Field(..., description="Количество")
    price: Decimal = Field(..., description="Цена")
    added_at : datetime = Field(..., description="Дата добавления товара в Заказ")

    model_config = ConfigDict(extra="allow")


class OrderCreate(BaseModel):
    """Схема для создания заказа."""

    user_id: int
    total_price: Decimal
    status: OrderStatus
    items: List[ProductRead]


class OrderRead(BaseModel):
    """Схема для вывода данных пользователя."""

    id: uuid.UUID
    user_id: int
    total_price: Decimal
    status: OrderStatus
    items: List[ProductRead]

    model_config = ConfigDict(from_attributes=True)


class OrdeUpdateStatus(BaseModel):
    status: OrderStatus
