"""Validation and file transport shared by the runtime backend and ROS sidecar."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


COMMAND_ID_PATTERN = re.compile(r"^inj-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")


VEHICLE_ID_PATTERN = re.compile(r"^uav([1-9])$")


def resolve_gazebo_body_name(
    configured: str,
    model_names: list[str],
    vehicle_id: str = "uav1",
) -> str | None:
    """Resolve one Gazebo vehicle body without assuming the SDF asset name."""
    explicit = configured.strip()
    if explicit:
        return explicit
    candidates = (vehicle_id, "sunray150") if vehicle_id == "uav1" else (vehicle_id,)
    for candidate in candidates:
        model = next((name for name in model_names if candidate in name.lower()), None)
        if model:
            return f"{model}::base_link"
    return None


def load_contract(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("schema") != "mosim.factory_injection_contract.v1":
        raise ValueError("injection_contract_schema_invalid")
    return value


def validate_command(
    command: dict[str, Any],
    *,
    manifest: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    missing = [field for field in contract.get("required_command_fields", []) if field not in command]
    if missing:
        raise ValueError("injection_command_fields_missing:" + ",".join(missing))
    command_id = command.get("command_id")
    if not isinstance(command_id, str) or not COMMAND_ID_PATTERN.fullmatch(command_id):
        raise ValueError("injection_command_id_invalid")
    if command.get("run_id") != manifest.get("run_id"):
        raise ValueError("injection_run_id_mismatch")
    if command.get("profile_hash") != manifest.get("experiment_profile_hash"):
        raise ValueError("injection_profile_hash_mismatch")
    vehicle_count = manifest.get("vehicle_count", 1)
    if not isinstance(vehicle_count, int) or vehicle_count < 1 or vehicle_count > 9:
        raise ValueError("injection_vehicle_count_invalid")
    vehicle_id = command.get("vehicle_id", "uav1" if vehicle_count == 1 else None)
    match = VEHICLE_ID_PATTERN.fullmatch(vehicle_id) if isinstance(vehicle_id, str) else None
    if match is None or int(match.group(1)) > vehicle_count:
        raise ValueError("injection_vehicle_id_invalid")
    if command.get("apply_mode") not in contract.get("apply_modes", []):
        raise ValueError("injection_apply_mode_invalid")
    if command.get("restore_policy") not in contract.get("restore_policies", []):
        raise ValueError("injection_restore_policy_invalid")

    target = command.get("target")
    target_contract = contract.get("targets", {}).get(target)
    if not isinstance(target_contract, dict):
        raise ValueError("injection_target_unsupported")
    try:
        value = float(command.get("value"))
        ramp_s = float(command.get("ramp_s"))
        duration_s = float(command.get("duration_s"))
    except (TypeError, ValueError) as exc:
        raise ValueError("injection_numeric_value_invalid") from exc
    if ramp_s < 0.0 or duration_s < 0.0:
        raise ValueError("injection_duration_invalid")
    if command.get("apply_mode") == "restore":
        value = 1.0 if target == "motor_effectiveness" else 0.0
    if not float(target_contract["minimum"]) <= value <= float(target_contract["maximum"]):
        raise ValueError("injection_value_out_of_range")

    normalized = dict(command)
    normalized.update(value=value, ramp_s=ramp_s, duration_s=duration_s, vehicle_id=vehicle_id)
    if target_contract.get("requires_rotor_index"):
        rotor_index = command.get("rotor_index")
        if not isinstance(rotor_index, int) or not (
            int(target_contract["rotor_index_min"]) <= rotor_index <= int(target_contract["rotor_index_max"])
        ):
            raise ValueError("injection_rotor_index_invalid")
    return normalized


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)
