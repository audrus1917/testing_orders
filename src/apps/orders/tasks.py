"""Передача данных о новом заказе."""

import logging

from aio_pika.connection import Connection
from aio_pika import Message, DeliveryMode

from src.apps.orders.schemas import OrderRead
from src.core.config import get_settings


settings = get_settings()
logger = logging.getLogger(__name__)


async def new_order_notify(
    brocker_connection: Connection,
    order_data: OrderRead
) -> None:
    """Передача данных брокеру о новом заказе."""

    channel = await brocker_connection.channel()

    queue_name = settings.RABBIT.RABBIT_QUEUE
    await channel.declare_queue(queue_name, durable=True)
    
    message_body = order_data.model_dump_json()
        
    message = Message(
        message_body.encode(),
        content_type="application/json",
        delivery_mode=DeliveryMode.PERSISTENT
    )
        
    await channel.default_exchange.publish(
        message,
        routing_key=queue_name
    )
    logger.debug(f"Отправлено: {message_body}")
