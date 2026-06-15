_phases: dict[str, dict] = {}


def set_phase(instance_id: str, label: str, progress: int) -> None:
    _phases[instance_id] = {
        "instance_id": instance_id,
        "label": label,
        "progress": progress,
    }


def get_phase(instance_id: str) -> dict | None:
    return _phases.get(instance_id)


def clear_phase(instance_id: str) -> None:
    _phases.pop(instance_id, None)
