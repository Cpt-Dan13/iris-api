from fastapi import APIRouter, HTTPException
from db import get_supabase

router = APIRouter(prefix="/personas", tags=["personas"])


@router.get("/{user_id}")
async def get_persona(user_id: str):
    result = (
        get_supabase()
        .table("users")
        .select("persona")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="No persona found for this user")
    return result.data.get("persona") or {}


@router.put("/{user_id}")
async def update_persona(user_id: str, persona: dict):
    result = (
        get_supabase()
        .table("users")
        .update({"persona": persona})
        .eq("user_id", user_id)
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    return {"ok": True}
