import json
import logging
from datetime import datetime
import aio_pika
import broker
from models import InstanceStatus

logger = logging.getLogger(__name__)

# In-memory store — repopulates within one heartbeat interval on restart
_statuses: dict[str, InstanceStatus] = {}


def get_status(instance_id: str) -> InstanceStatus | None:
    return _statuses.get(instance_id)


def all_statuses() -> list[InstanceStatus]:
    return list(_statuses.values())


async def start() -> None:
    connection = await broker.get_connection()
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue("iris.heartbeat", durable=True)

    async with queue.iterator() as messages:
        async for message in messages:
            async with message.process():
                try:
                    data = json.loads(message.body)
                    instance_id = data.get("instance_id", "")
                    _statuses[instance_id] = InstanceStatus(
                        instance_id=instance_id,
                        user_id=data.get("user_id", ""),
                        status=data.get("status", "unknown"),
                        likes_today=data.get("likes_today", 0),
                        last_seen=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.utcnow(),
                    )
                except Exception:
                    logger.exception("Failed to process heartbeat message")
