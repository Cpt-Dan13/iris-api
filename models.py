from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


class IrisEvent(BaseModel):
    event: str
    user_id: str
    instance_id: str
    payload: dict[str, Any] = {}
    timestamp: datetime


class IrisCommand(BaseModel):
    command: str
    user_id: str
    instance_id: str
    payload: dict[str, Any] = {}


class HeartbeatEvent(BaseModel):
    user_id: str
    instance_id: str
    status: str  # "running" | "idle" | "error"
    likes_today: int = 0
    timestamp: datetime


class IrisError(BaseModel):
    user_id: str
    instance_id: str
    error: str
    context: Optional[str] = None
    timestamp: datetime


class InstanceStatus(BaseModel):
    instance_id: str
    user_id: str
    status: str
    likes_today: int
    last_seen: Optional[datetime]


class StartPayload(BaseModel):
    persona_id: Optional[str] = None
    daily_like_limit: int = 25
