import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import broker
from consumers import events, heartbeat, errors
from routers import instances, sessions, personas

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.declare_queues()

    tasks = [
        asyncio.create_task(events.start(), name="consumer:events"),
        asyncio.create_task(heartbeat.start(), name="consumer:heartbeat"),
        asyncio.create_task(errors.start(), name="consumer:errors"),
    ]

    yield

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    await broker.close()


app = FastAPI(
    title="IRIS API",
    description="Control plane and event relay for IRIS automation instances",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to iris-portal domain before production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(instances.router)
app.include_router(sessions.router)
app.include_router(personas.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
