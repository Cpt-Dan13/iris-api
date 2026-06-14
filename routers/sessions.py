import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from db import get_supabase
import event_bus

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/{user_id}/latest")
async def latest_session(user_id: str):
    supabase = get_supabase()
    liked = supabase.table("liked_profiles").select("id", count="exact").eq("user_id", user_id).execute()
    matched = supabase.table("matched_profiles").select("id", count="exact").eq("user_id", user_id).execute()
    conversations = supabase.table("conversations").select("id", count="exact").eq("user_id", user_id).execute()
    return {
        "user_id": user_id,
        "total_liked": liked.count or 0,
        "total_matched": matched.count or 0,
        "total_conversations": conversations.count or 0,
    }


@router.get("/{user_id}/events")
async def stream_events(user_id: str):
    async def generator():
        q = event_bus.subscribe(user_id)
        try:
            while True:
                try:
                    event = await asyncio.wait_for(q.get(), timeout=30)
                    yield f"data: {json.dumps(event, default=str)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            event_bus.unsubscribe(user_id, q)

    return StreamingResponse(generator(), media_type="text/event-stream")
