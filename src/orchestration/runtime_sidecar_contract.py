"""Validation and file transport shared by the runtime backend and ROS sidecar."""

from __future__ import annotations

import json
import math
import re
import time
from pathlib import Path
from typing import Any


COMMAND_ID_PATTERN = re.compile(r"^inj-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")


VEHICLE_ID_PATTERN = re.compile(r"^uav([1-9])$")

OPERATOR_RUNTIME_STATUS_SCHEMA = "mosim.operator_runtime_status.v1"
OPERATOR_RUNTIME_OBSERVABILITY_FIELDS = (
    "rtt_ms",
    "jitter_ms",
    "command_age_ms",
    "packet_loss_rate",
)


def evaluate_readiness_status(
    *,
    ready: bool,
    ever_ready: bool,
    elapsed_s: float,
    timeout_s: float,
) -> tuple[str, str, bool]:
    """Keep initial readiness failure separate from transient runtime degradation."""
    if ready:
        return "running", "runtime_ready", True
    if ever_ready:
        return "running", "runtime_readiness_degraded", True
    if elapsed_s >= timeout_s:
        return "blocked", "runtime_readiness_timeout", False
    return "starting", "runtime_readiness_pending", False


def build_operator_runtime_status(
    *,
    manifest: dict[str, Any],
    state: str,
    reason_code: str,
    updated_at_unix_s: float,
    observability: dict[str, Any] | None = None,
    alerts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create the identity-bound status envelope consumed by the operator UI.

    This deliberately carries only values measured by an attached runtime
    producer. Missing metrics and alerts stay absent so a UI can distinguish
    them from measured zero values or an explicit empty alert report.
    """
    run_id = manifest.get("run_id")
    profile_id = manifest.get("experiment_profile_id")
    profile_hash = manifest.get("experiment_profile_hash")
    controller_backend = manifest.get("controller_backend")
    if any(not isinstance(value, str) or not value for value in (run_id, profile_id, profile_hash, controller_backend)):
        raise ValueError("operator_runtime_status_manifest_identity_invalid")
    if not isinstance(state, str) or not state:
        raise ValueError("operator_runtime_status_state_invalid")
    if not isinstance(reason_code, str) or not reason_code:
        raise ValueError("operator_runtime_status_reason_code_invalid")
    if not isinstance(updated_at_unix_s, (int, float)) or not math.isfinite(updated_at_unix_s) or updated_at_unix_s < 0:
        raise ValueError("operator_runtime_status_updated_at_invalid")

    payload: dict[str, Any] = {
        "schema": OPERATOR_RUNTIME_STATUS_SCHEMA,
        "run_id": run_id,
        "experiment_profile_id": profile_id,
        "experiment_profile_hash": profile_hash,
        "controller_backend": controller_backend,
        "state": state,
        "reason_code": reason_code,
        "updated_at_unix_s": float(updated_at_unix_s),
    }
    if observability is not None:
        if not isinstance(observability, dict):
            raise ValueError("operator_runtime_status_observability_invalid")
        normalized = {
            key: float(value)
            for key, value in observability.items()
            if key in OPERATOR_RUNTIME_OBSERVABILITY_FIELDS
            and isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(value)
        }
        if normalized:
            payload["observability"] = normalized
    if alerts is not None:
        if not isinstance(alerts, list) or any(not isinstance(alert, dict) for alert in alerts):
            raise ValueError("operator_runtime_status_alerts_invalid")
        payload["alerts"] = alerts
    return payload


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
    for attempt in range(10):
        try:
            temporary.replace(path)
            return
        except PermissionError:
            if attempt == 9:
                raise
            # Windows readers can briefly hold the destination while the WSL
            # sidecar replaces it. Keep this bounded and preserve atomicity.
            time.sleep(0.05)
