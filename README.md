# iris-api

FastAPI control plane and event relay for IRIS automation instances.

Sits between the IRIS Android app and Supabase — receives events from the Android automation via RabbitMQ, writes results to the database, and exposes REST endpoints for iris-portal to control instances and stream live activity.

## Stack

- **FastAPI** — API server
- **RabbitMQ** — message broker (AMQP)
- **Supabase** — PostgreSQL database (via service role key)
- **aio-pika** — async RabbitMQ client
- **uvicorn** — ASGI server

## Architecture

```
iris-portal  →  iris-api  →  RabbitMQ  →  IRIS Android (AVD)
                    │                            │
                    └──── Supabase ◄─────────────┘
```

Events flow from the Android automation → `iris.events` queue → FastAPI consumer → Supabase.  
Commands flow from iris-portal → FastAPI → `iris.commands` queue → Android automation.

## Queues

| Queue | Direction | Purpose |
|---|---|---|
| `iris.events` | Android → API | Profile liked, match found, message sent |
| `iris.commands` | API → Android | Start, stop, configure persona |
| `iris.heartbeat` | Android → API | Instance health ping every 30s |
| `iris.errors` | Android → API | Errors and crashes |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # fill in your credentials
uvicorn main:app --reload       # dev
uvicorn main:app --host 0.0.0.0 --port 8000  # production
```

## Environment Variables

```
RABBITMQ_URL=amqp://iris:<password>@localhost:5672/
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
```

## API Docs

Available at `http://localhost:8000/docs` when the server is running.

## Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/instances/{id}/start` | Start automation on an instance |
| `POST` | `/instances/{id}/stop` | Stop automation |
| `GET` | `/instances/{id}/status` | Last known instance health |
| `GET` | `/instances/` | All active instances |
| `GET` | `/sessions/{user_id}/latest` | Session stats for a user |
| `GET` | `/sessions/{user_id}/events` | SSE stream of live events |
| `GET` | `/personas/{user_id}` | Fetch active persona config |
| `PUT` | `/personas/{user_id}` | Update persona config |

## Related Repos

- [`iris`](https://github.com/Cpt-Dan13/iris) — Android automation app
- [`iris-portal`](https://github.com/Cpt-Dan13/iris-portal) — Web dashboard
