import json
import logging
import aio_pika
import broker
import event_bus
from db import get_supabase

logger = logging.getLogger(__name__)


async def _handle_profile_liked(payload: dict, user_id: str) -> None:
    get_supabase().table("liked_profiles").insert({
        "user_id": user_id,
        "name": payload.get("name"),
        "age": payload.get("age"),
        "location": payload.get("location"),
        "bio": payload.get("bio"),
        "photo": payload.get("photo_url"),
        "allure_score": payload.get("allure_score"),
        "personality_tags": payload.get("personality_tags", []),
    }).execute()


async def _handle_match_found(payload: dict, user_id: str) -> None:
    get_supabase().table("matched_profiles").insert({
        "user_id": user_id,
        "name": payload.get("name"),
        "age": payload.get("age"),
        "location": payload.get("location"),
        "bio": payload.get("bio"),
        "photo": payload.get("photo_url"),
        "allure_score": payload.get("allure_score"),
        "prospective_score": payload.get("prospective_score"),
        "prospective_level": payload.get("prospective_level"),
        "personality_tags": payload.get("personality_tags", []),
        "matched_at": payload.get("matched_at"),
        "conversation_status": "active",
    }).execute()


async def _handle_message_sent(payload: dict, user_id: str) -> None:
    profile_id = payload.get("profile_id")
    new_message = {
        "role": payload.get("role", "assistant"),
        "content": payload.get("content"),
    }
    supabase = get_supabase()
    existing = (
        supabase.table("conversations")
        .select("id, messages")
        .eq("profile_id", profile_id)
        .maybe_single()
        .execute()
    )
    if existing.data:
        updated = existing.data["messages"] + [new_message]
        supabase.table("conversations").update({"messages": updated}).eq("id", existing.data["id"]).execute()
    else:
        supabase.table("conversations").insert({
            "user_id": user_id,
            "profile_id": profile_id,
            "messages": [new_message],
        }).execute()


_HANDLERS = {
    "profile_liked": _handle_profile_liked,
    "match_found": _handle_match_found,
    "message_sent": _handle_message_sent,
}


async def start() -> None:
    connection = await broker.get_connection()
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    queue = await channel.declare_queue("iris.events", durable=True)

    async with queue.iterator() as messages:
        async for message in messages:
            async with message.process():
                try:
                    data = json.loads(message.body)
                    event = data.get("event")
                    user_id = data.get("user_id", "")

                    handler = _HANDLERS.get(event)
                    if handler:
                        await handler(data.get("payload", {}), user_id)
                    else:
                        logger.warning("Unhandled event type: %s", event)

                    await event_bus.dispatch(user_id, data)
                except Exception:
                    logger.exception("Failed to process event message")
