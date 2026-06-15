from fastapi import APIRouter, HTTPException
from models import IrisCommand, StartPayload, InstanceStatus, LinkPayload, OtpPayload, LinkStatus
from consumers import heartbeat
import broker
import link_status_store
import phase_store

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
    phase_store.clear_phase(instance_id)
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


@router.post("/{instance_id}/link")
async def start_link(instance_id: str, body: LinkPayload, user_id: str):
    await broker.publish("iris.commands", IrisCommand(
        command="link_account",
        user_id=user_id,
        instance_id=instance_id,
        payload=body.model_dump(),
    ).model_dump())
    return {"ok": True, "command": "link_account", "instance_id": instance_id}


@router.post("/{instance_id}/otp")
async def submit_otp(instance_id: str, body: OtpPayload, user_id: str):
    command = "submit_phone_otp" if body.type == "phone" else "submit_email_otp"
    await broker.publish("iris.commands", IrisCommand(
        command=command,
        user_id=user_id,
        instance_id=instance_id,
        payload={"code": body.code},
    ).model_dump())
    return {"ok": True, "command": command}


@router.get("/{instance_id}/phase")
async def get_phase(instance_id: str):
    phase = phase_store.get_phase(instance_id)
    if not phase:
        raise HTTPException(status_code=404, detail="No phase data available")
    return phase


@router.get("/{instance_id}/link-status", response_model=LinkStatus)
async def get_link_status(instance_id: str):
    status = link_status_store.get_status(instance_id)
    if not status:
        raise HTTPException(status_code=404, detail="No link flow active")
    return status
