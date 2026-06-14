from datetime import datetime, timezone
from typing import Optional

_statuses: dict[str, dict] = {}


def set_status(instance_id: str, user_id: str, status: str) -> None:
    _statuses[instance_id] = {
        "instance_id": instance_id,
        "user_id": user_id,
        "status": status,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def get_status(instance_id: str) -> Optional[dict]:
    return _statuses.get(instance_id)


def clear_status(instance_id: str) -> None:
    _statuses.pop(instance_id, None)
