import os
import json
import aio_pika
from typing import Any
from dotenv import load_dotenv

load_dotenv()

_connection: aio_pika.RobustConnection | None = None

QUEUES = [
    "iris.events",
    "iris.commands",
    "iris.errors",
    "iris.heartbeat",
]


async def get_connection() -> aio_pika.RobustConnection:
    global _connection
    if _connection is None or _connection.is_closed:
        _connection = await aio_pika.connect_robust(
            os.getenv("RABBITMQ_URL", "amqp://iris:iris@localhost:5672/")
        )
    return _connection


async def declare_queues() -> None:
    connection = await get_connection()
    async with connection.channel() as channel:
        for name in QUEUES:
            await channel.declare_queue(name, durable=True)


async def publish(queue_name: str, message: dict[str, Any]) -> None:
    connection = await get_connection()
    async with connection.channel() as channel:
        await channel.declare_queue(queue_name, durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message, default=str).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue_name,
        )


async def close() -> None:
    global _connection
    if _connection and not _connection.is_closed:
        await _connection.close()
    _connection = None
