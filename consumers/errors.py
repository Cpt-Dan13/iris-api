import json
import logging
import broker

logger = logging.getLogger("iris.instance.errors")


async def start() -> None:
    connection = await broker.get_connection()
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue("iris.errors", durable=True)

    async with queue.iterator() as messages:
        async for message in messages:
            async with message.process():
                try:
                    data = json.loads(message.body)
                    logger.error(
                        "[%s/%s] %s — context: %s",
                        data.get("user_id", "?"),
                        data.get("instance_id", "?"),
                        data.get("error", "unknown error"),
                        data.get("context", "none"),
                    )
                except Exception:
                    logger.exception("Failed to process error message")
