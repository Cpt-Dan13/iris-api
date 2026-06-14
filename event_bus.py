import asyncio
from collections import defaultdict

_subscribers: dict[str, list[asyncio.Queue]] = defaultdict(list)


def subscribe(user_id: str) -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue()
    _subscribers[user_id].append(q)
    return q


def unsubscribe(user_id: str, q: asyncio.Queue) -> None:
    try:
        _subscribers[user_id].remove(q)
    except ValueError:
        pass


async def dispatch(user_id: str, event: dict) -> None:
    for q in list(_subscribers.get(user_id, [])):
        await q.put(event)
