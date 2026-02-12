#!/usr/bin/env python3

"""Обработчик заданий от брокера."""

import asyncio
import logging
import time

import aio_pika
from celery import Celery

from src.core.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=settings.LOGGING_LEVEL,
    format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("aio_pika").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


celery_app = Celery(
    "src.consumer",
    broker=settings.RABBIT.uri,
    backend=settings.REDIS.uri
)


@celery_app.task
def ding_about_order(order_data):
    time.sleep(2)
    print(order_data)


async def main():
    connection = await aio_pika.connect(settings.RABBIT.uri)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)

        queue = await channel.declare_queue(
            settings.RABBIT.RABBIT_QUEUE,
            durable=True
        )

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    msg = message.body.decode()
                    print(f"Получено сообщение: {msg}")
                    ding_about_order.delay(msg)


if __name__ == "__main__":
    asyncio.run(main())
