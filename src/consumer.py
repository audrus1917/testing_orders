#!/usr/bin/env python3

"""Обработчик заданий от брокера."""

import asyncio
import logging

import aio_pika
from src.core.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=settings.LOGGING_LEVEL,
    format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("aio_pika").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)


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
                    print(f"Получено сообщение: {message.body.decode()}")


if __name__ == "__main__":
    asyncio.run(main())
