from fastapi import APIRouter, HTTPException
from models import IrisCommand, StartPayload, InstanceStatus
from consumers import heartbeat
import broker

router = APIRouter(prefix="/instances", tags=["instances"])


@router.post("/{instance_id}/start")
async def start_instance(instance_id: str, body: StartPayload, user_id: str):
    await broker.publish("iris.commands", IrisCommand(
        command="start_automation",
        user_id=user_id,
        instance_id=instance_id,
        payload=body.model_dump(),
    ).model_dump())
    return {"ok": True, "command": "start_automation", "instance_id": instance_id}


@router.post("/{instance_id}/stop")
async def stop_instance(instance_id: str, user_id: str):
    await broker.publish("iris.commands", IrisCommand(
        command="stop_automation",
        user_id=user_id,
        instance_id=instance_id,
    ).model_dump())
    return {"ok": True, "command": "stop_automation", "instance_id": instance_id}


@router.get("/{instance_id}/status", response_model=InstanceStatus)
async def get_instance_status(instance_id: str):
    status = heartbeat.get_status(instance_id)
    if not status:
        raise HTTPException(status_code=404, detail="Instance not found or no heartbeat received yet")
    return status


@router.get("/", response_model=list[InstanceStatus])
async def list_instances():
    return heartbeat.all_statuses()
