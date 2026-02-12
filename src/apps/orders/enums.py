"""Перечисление для статуса заказа."""

from enum import Enum


class OrderStatus(str, Enum):
    """Возможный значения статуса заказа."""

    PENDING = "PENDING" 
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    CANCELED = "CANCELED"

