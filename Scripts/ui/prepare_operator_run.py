#!/usr/bin/env python3
"""Prepare one published operator run without starting its runtime.

The prepared invocation is intentionally executed by the operator in a visible
terminal. It may originate from QGC's copy command or a project-owned explicit
terminal wrapper. This helper freezes the selected published Profile and
Factory-map snapshot before the existing launcher runs. It never starts or
supervises ROS, Gazebo, PX4, MAVROS, QGC, UE, RViz, or MWORKS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestration.operator_map_state import validate_operator_map_snapshot
from src.orchestration.runtime_sidecar_contract import build_operator_runtime_status
from src.orchestration.run_manifest_contract import (
    RUN_MANIFEST_V2_SCHEMA,
    artifact_slot,
    open_action,
    validate_run_manifest_v2,
)


RUNS_RELATIVE_ROOT = Path("Results") / "runs"
ACTIVE_POINTER_RELATIVE_PATH = Path("Results") / "ui_platform" / "qgc_active_run.json"
RUN_ID_PATTERN = re.compile(r"^qgc-[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")
ACTIVE_STATES = {"launch_prepared", "running", "replaying"}
TERMINAL_STATES = {"completed", "blocked", "failed"}
PREPARATION_SOURCES = {"qgc_visible_terminal", "terminal_rviz_qgc_display_phase1"}


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"operator_run_json_object_required:{path}")
    return value


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    temporary.replace(path)


def _root_path(root: Path, relative: str | Path) -> Path:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError("operator_run_path_outside_project") from exc
    return candidate


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha256_value(value: dict[str, Any]) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _generated_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"qgc-{stamp}-{uuid.uuid4().hex[:10]}"


def _utc_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _load_operator_profile(root: Path, profile_id: str) -> tuple[dict[str, Any], Path, dict[str, Any]]:
    catalog = _read_object(_root_path(root, "Config/profiles/operator_profiles.json"))
    matches = [item for item in catalog.get("profiles", []) if isinstance(item, dict) and item.get("profile_id") == profile_id]
    if len(matches) != 1:
        raise ValueError("operator_run_profile_not_published")
    operator_profile = matches[0]
    if operator_profile.get("enabled") is not True:
        raise ValueError("operator_run_profile_disabled")
    profile_path = _root_path(root, str(operator_profile.get("profile_path", "")))
    if not profile_path.is_file():
        raise ValueError("operator_run_profile_file_missing")
    document = _read_object(profile_path)
    experiment = document.get("experiment_profile")
    if not isinstance(experiment, dict) or experiment.get("id") != profile_id:
        raise ValueError("operator_run_profile_identity_mismatch")
    return operator_profile, profile_path, experiment


def _load_runtime_backend(root: Path, profile_id: str, runtime_profile_id: str) -> dict[str, Any]:
    catalog = _read_object(_root_path(root, "Config/control_platform/runtime_backend_catalog.json"))
    matches = [
        item
        for item in catalog.get("runtime_profiles", [])
        if isinstance(item, dict)
        and profile_id in item.get("experiment_profile_ids", [])
        and item.get("runtime_profile_id") == runtime_profile_id
    ]
    if len(matches) != 1:
        raise ValueError("operator_run_runtime_backend_mismatch")
    backend = matches[0]
    invocation = backend.get("operator_invocation")
    if not isinstance(invocation, dict) or invocation.get("schema") != "mosim.operator_invocation.v1":
        raise ValueError("operator_run_runtime_invocation_missing")
    return backend


def _load_operator_map(root: Path, map_id: str) -> dict[str, Any]:
    catalog = _read_object(_root_path(root, "Config/control_platform/operator_map_catalog.json"))
    matches = [
        item
        for item in catalog.get("maps", [])
        if isinstance(item, dict) and item.get("map_id") == map_id and item.get("enabled") is True
    ]
    if len(matches) != 1:
        raise ValueError("operator_run_map_not_enabled")
    snapshot = deepcopy(matches[0])
    validate_operator_map_snapshot(snapshot, project_root=root)
    return snapshot


def _load_scenario_snapshot(root: Path, experiment: dict[str, Any]) -> dict[str, Any]:
    relative_path = experiment.get("scenario_path")
    if not isinstance(relative_path, str) or not relative_path:
        return {}
    scenario_path = _root_path(root, relative_path)
    if not scenario_path.is_file():
        raise ValueError("operator_run_scenario_file_missing")
    return _read_object(scenario_path)


def _pointer_relative_path(value: str | Path) -> Path:
    relative = Path(value)
    if (
        relative.is_absolute()
        or not relative.parts
        or relative.parts[0] != "Results"
        or ".." in relative.parts
        or relative.suffix != ".json"
    ):
        raise ValueError("operator_run_active_pointer_path_invalid")
    return relative


def _active_pointer_path(root: Path, relative_path: str | Path = ACTIVE_POINTER_RELATIVE_PATH) -> Path:
    return _root_path(root, _pointer_relative_path(relative_path))


def _active_pointer_is_live(root: Path, relative_path: str | Path = ACTIVE_POINTER_RELATIVE_PATH) -> bool:
    pointer_path = _active_pointer_path(root, relative_path)
    if not pointer_path.is_file():
        return False
    try:
        pointer = _read_object(pointer_path)
    except (OSError, json.JSONDecodeError, ValueError):
        return False
    return (
        pointer.get("schema") == "mosim.qgc_active_run_pointer.v1"
        and pointer.get("state") in ACTIVE_STATES
        and isinstance(pointer.get("run_id"), str)
    )


def prepare_run(
    *,
    profile_id: str,
    runtime_profile_id: str,
    root: Path = ROOT,
    run_id: str | None = None,
    now: float | None = None,
    active_pointer_relative_path: str | Path = ACTIVE_POINTER_RELATIVE_PATH,
    prepared_by: str = "qgc_visible_terminal",
) -> dict[str, Any]:
    root = root.resolve()
    pointer_relative_path = _pointer_relative_path(active_pointer_relative_path)
    if prepared_by not in PREPARATION_SOURCES:
        raise ValueError("operator_run_prepared_by_invalid")
    if _active_pointer_is_live(root, pointer_relative_path):
        raise ValueError("operator_run_already_active")
    selected_run_id = run_id or _generated_run_id()
    if not RUN_ID_PATTERN.fullmatch(selected_run_id):
        raise ValueError("operator_run_id_invalid")

    operator_profile, profile_path, experiment = _load_operator_profile(root, profile_id)
    backend = _load_runtime_backend(root, profile_id, runtime_profile_id)
    vehicle_count = experiment.get("vehicle_count", 1)
    if not isinstance(vehicle_count, int) or not 1 <= vehicle_count <= 9:
        raise ValueError("operator_run_vehicle_count_invalid")
    map_id = experiment.get("operator_map_id")
    if not isinstance(map_id, str) or not map_id:
        raise ValueError("operator_run_map_id_missing")
    map_snapshot = _load_operator_map(root, map_id)
    timestamp = time.time() if now is None else now
    if not isinstance(timestamp, (int, float)) or timestamp < 0:
        raise ValueError("operator_run_timestamp_invalid")

    profile_hash = _sha256_file(profile_path)
    map_hash = _sha256_value(map_snapshot)
    scenario_snapshot = _load_scenario_snapshot(root, experiment)
    controller_ids = backend.get("controller_ids")
    controller_id = controller_ids[0] if isinstance(controller_ids, list) and controller_ids else ""
    controller_backend = experiment.get("controller_backend", controller_id)
    if not isinstance(controller_backend, str) or not controller_backend:
        raise ValueError("operator_run_controller_backend_missing")
    scenario_path = experiment.get("scenario_path", "")
    if not isinstance(scenario_path, str):
        scenario_path = ""
    manifest = {
        "schema": RUN_MANIFEST_V2_SCHEMA,
        "run_id": selected_run_id,
        "run_kind": "operator_runtime",
        "created_at": _utc_timestamp(float(timestamp)),
        "status": "prepared",
        "profile": {
            "id": profile_id,
            "sha256": profile_hash,
            "controller_id": controller_id,
            "controller_profile": experiment.get("controller_profile", ""),
            "runtime_profile_id": runtime_profile_id,
        },
        "map": {
            "status": "frozen",
            "id": map_id,
            "snapshot": map_snapshot,
            "snapshot_sha256": map_hash,
        },
        "scenario": {
            "status": "frozen" if scenario_path else "not_applicable",
            "id": scenario_path,
            "path": scenario_path,
            "snapshot": scenario_snapshot,
            "snapshot_sha256": _sha256_value(scenario_snapshot) if scenario_path else "",
        },
        "source_state": {
            "profile_path": profile_path.relative_to(root).as_posix(),
            "runtime_backend_catalog": "Config/control_platform/runtime_backend_catalog.json",
            "operator_map_catalog": "Config/control_platform/operator_map_catalog.json",
            "prepared_by": prepared_by,
        },
        "artifacts": {
            "mworks_model": artifact_slot(status="not_requested"),
            "native_result_msr": artifact_slot(status="not_requested"),
            "raw_csv": artifact_slot(status="not_requested"),
            "metrics_json": artifact_slot(status="not_requested"),
            "rosbag": artifact_slot(status="pending"),
            "px4_ulog": artifact_slot(status="pending"),
            "operator_map_replay": artifact_slot(status="pending", path="OPERATOR_MAP_REPLAY_MANIFEST.json"),
            "telemetry": artifact_slot(status="pending", path="telemetry.json"),
            "logs_directory": artifact_slot(status="pending", path="logs"),
        },
        "open_actions": {
            "open_model": open_action(enabled=False, reason_code="mworks_model_not_bound"),
            "open_native_result": open_action(enabled=False, reason_code="native_result_not_available"),
            "replay_rviz": open_action(enabled=False, reason_code="rosbag_not_available"),
            "replay_operator_map": open_action(enabled=False, reason_code="rosbag_not_available"),
            "open_result_directory": open_action(enabled=True, reason_code="run_directory_available", path="."),
        },
        "experiment_profile_id": profile_id,
        "experiment_profile_hash": profile_hash,
        "runtime_profile_id": runtime_profile_id,
        "runtime_operation_id": backend.get("operation_id", ""),
        "controller_backend": controller_backend,
        "controller_id": controller_id,
        "controller_profile": experiment.get("controller_profile", ""),
        "vehicle_count": vehicle_count,
        "planner_profile": experiment.get("planner_profile", ""),
        "safety_profile": experiment.get("safety_profile", ""),
        "fault_profile": experiment.get("fault_profile", ""),
        "operator_mode": operator_profile.get("operator_mode", ""),
        "operator_map_snapshot": map_snapshot,
        "operator_map_snapshot_hash": map_hash,
        "scenario_snapshot": scenario_snapshot,
        "state": "launch_prepared",
        "prepared_at_unix_s": timestamp,
        "prepared_by": prepared_by,
        "claim_boundary": (
            "This prepares a frozen operator run only. It does not prove that the launcher, "
            "ROS, Gazebo, PX4, MAVROS, controller, planner, sidecar, or vehicle accepted execution."
        ),
    }
    validate_run_manifest_v2(manifest)
    run_directory = _root_path(root, RUNS_RELATIVE_ROOT / selected_run_id)
    if run_directory.exists():
        raise ValueError("operator_run_directory_exists")
    run_directory.mkdir(parents=True, exist_ok=False)
    _atomic_write_json(run_directory / "RUN_MANIFEST.json", manifest)
    run_directory_relative = (RUNS_RELATIVE_ROOT / selected_run_id).as_posix()
    pointer = {
        "schema": "mosim.qgc_active_run_pointer.v1",
        "state": "launch_prepared",
        "run_id": selected_run_id,
        "run_directory": run_directory_relative,
        "manifest_path": f"{run_directory_relative}/RUN_MANIFEST.json",
        "experiment_profile_id": profile_id,
        "experiment_profile_hash": profile_hash,
        "runtime_profile_id": runtime_profile_id,
        "updated_at_unix_s": timestamp,
        "source": prepared_by,
    }
    pointer_path = _active_pointer_path(root, pointer_relative_path)
    _atomic_write_json(pointer_path, pointer)
    return {
        "run_id": selected_run_id,
        "run_directory": run_directory,
        "manifest": manifest,
        "pointer": pointer,
        "pointer_path": pointer_path,
    }


def activate_active_run(
    *,
    expected_run_id: str,
    source: str,
    root: Path = ROOT,
    now: float | None = None,
) -> dict[str, Any]:
    """Expose a prepared run to QGC after its runtime launcher is ready.

    The immutable RunManifest remains the identity authority. A launcher may
    advance only its own ``launch_prepared`` pointer after it has established
    the ROS-side readiness needed by its declared operator mode.
    """

    root = root.resolve()
    if not RUN_ID_PATTERN.fullmatch(expected_run_id):
        raise ValueError("operator_run_id_invalid")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", source):
        raise ValueError("operator_run_activation_source_invalid")

    pointer_path = _active_pointer_path(root)
    if not pointer_path.is_file():
        raise ValueError("operator_run_active_pointer_missing")
    pointer = _read_object(pointer_path)
    if (
        pointer.get("schema") != "mosim.qgc_active_run_pointer.v1"
        or pointer.get("state") != "launch_prepared"
        or pointer.get("run_id") != expected_run_id
    ):
        raise ValueError("operator_run_active_pointer_not_launch_prepared")

    run_directory_relative = f"Results/runs/{expected_run_id}"
    if pointer.get("run_directory") != run_directory_relative:
        raise ValueError("operator_run_active_pointer_directory_invalid")
    manifest = _read_object(_root_path(root, run_directory_relative) / "RUN_MANIFEST.json")
    if (
        manifest.get("run_id") != expected_run_id
        or manifest.get("experiment_profile_id") != pointer.get("experiment_profile_id")
        or manifest.get("experiment_profile_hash") != pointer.get("experiment_profile_hash")
        or manifest.get("runtime_profile_id") != pointer.get("runtime_profile_id")
    ):
        raise ValueError("operator_run_activation_manifest_identity_mismatch")
    validate_run_manifest_v2(manifest)

    timestamp = time.time() if now is None else now
    if not isinstance(timestamp, (int, float)) or timestamp < 0:
        raise ValueError("operator_run_timestamp_invalid")
    activated = dict(pointer)
    activated["state"] = "running"
    activated["updated_at_unix_s"] = float(timestamp)
    activated["activated_at_unix_s"] = float(timestamp)
    activated["source"] = source
    _atomic_write_json(pointer_path, activated)
    return activated


def clear_active_run(*, root: Path = ROOT, now: float | None = None) -> dict[str, Any]:
    root = root.resolve()
    pointer_path = _active_pointer_path(root)
    if not pointer_path.is_file():
        raise ValueError("operator_run_active_pointer_missing")
    pointer = _read_object(pointer_path)
    if pointer.get("schema") != "mosim.qgc_active_run_pointer.v1" or not isinstance(pointer.get("run_id"), str):
        raise ValueError("operator_run_active_pointer_invalid")
    pointer = dict(pointer)
    pointer["state"] = "cleared"
    pointer["cleared_at_unix_s"] = time.time() if now is None else now
    pointer["cleared_by"] = "qgc_visible_terminal"
    _atomic_write_json(pointer_path, pointer)
    return pointer


def finalize_active_run(
    *,
    expected_run_id: str,
    terminal_state: str,
    reason_code: str,
    source: str,
    root: Path = ROOT,
    now: float | None = None,
) -> dict[str, Any]:
    """Mark the prepared run terminal after the live sidecar has stopped.

    The frozen RunManifest stays unchanged. The terminal status tells QGC that
    the final map frame is historical, not current MAVLink telemetry.
    """
    root = root.resolve()
    if not RUN_ID_PATTERN.fullmatch(expected_run_id):
        raise ValueError("operator_run_id_invalid")
    if terminal_state not in TERMINAL_STATES:
        raise ValueError("operator_run_terminal_state_invalid")
    if not re.fullmatch(r"[a-z0-9_]+", reason_code):
        raise ValueError("operator_run_terminal_reason_invalid")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", source):
        raise ValueError("operator_run_terminal_source_invalid")

    pointer_path = _active_pointer_path(root)
    if not pointer_path.is_file():
        raise ValueError("operator_run_active_pointer_missing")
    pointer = _read_object(pointer_path)
    if (
        pointer.get("schema") != "mosim.qgc_active_run_pointer.v1"
        or pointer.get("state") not in ACTIVE_STATES | TERMINAL_STATES
        or pointer.get("run_id") != expected_run_id
    ):
        raise ValueError("operator_run_active_pointer_invalid")

    run_directory_relative = f"Results/runs/{expected_run_id}"
    if pointer.get("run_directory") != run_directory_relative:
        raise ValueError("operator_run_active_pointer_directory_invalid")
    run_directory = _root_path(root, run_directory_relative)
    manifest = _read_object(run_directory / "RUN_MANIFEST.json")
    if (
        manifest.get("run_id") != expected_run_id
        or manifest.get("experiment_profile_id") != pointer.get("experiment_profile_id")
        or manifest.get("experiment_profile_hash") != pointer.get("experiment_profile_hash")
        or manifest.get("runtime_profile_id") != pointer.get("runtime_profile_id")
    ):
        raise ValueError("operator_run_terminal_manifest_identity_mismatch")
    validate_run_manifest_v2(manifest)

    timestamp = time.time() if now is None else now
    if not isinstance(timestamp, (int, float)) or timestamp < 0:
        raise ValueError("operator_run_timestamp_invalid")
    status_payload = {
        "schema": "mosim.runtime_status.v1",
        "run_id": expected_run_id,
        "status": terminal_state,
        "reason_code": reason_code,
        "vehicle_count": manifest["vehicle_count"],
        "missing_readiness": [],
        "updated_at": float(timestamp),
    }
    _atomic_write_json(run_directory / "RUNTIME_STATUS.json", status_payload)

    telemetry_path = run_directory / "telemetry.json"
    if telemetry_path.is_file():
        telemetry = _read_object(telemetry_path)
        if telemetry.get("run_id") != expected_run_id:
            raise ValueError("operator_run_terminal_telemetry_identity_mismatch")
        telemetry = dict(telemetry)
        telemetry["timestamp"] = float(timestamp)
        telemetry["readiness"] = status_payload
        telemetry["mission_status"] = {
            "transport_state": terminal_state,
            "fresh": False,
            "terminal": True,
            "reason_code": reason_code,
        }
        telemetry["operator_runtime_status"] = build_operator_runtime_status(
            manifest=manifest,
            state=terminal_state,
            reason_code=reason_code,
            updated_at_unix_s=float(timestamp),
        )
        _atomic_write_json(telemetry_path, telemetry)

    pointer = dict(pointer)
    pointer["state"] = terminal_state
    pointer["updated_at_unix_s"] = float(timestamp)
    pointer["terminal_at_unix_s"] = float(timestamp)
    pointer["terminal_reason_code"] = reason_code
    pointer["source"] = source
    _atomic_write_json(pointer_path, pointer)
    return {
        "pointer": pointer,
        "runtime_status": status_payload,
        "telemetry_present": telemetry_path.is_file(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-id")
    parser.add_argument("--runtime-profile-id")
    parser.add_argument("--run-id")
    parser.add_argument("--prepared-by", default="qgc_visible_terminal")
    parser.add_argument("--active-pointer-path")
    parser.add_argument("--print-run-id", action="store_true")
    parser.add_argument("--clear-active", action="store_true")
    parser.add_argument("--activate-active", action="store_true")
    parser.add_argument("--finalize-active", action="store_true")
    parser.add_argument("--expected-run-id")
    parser.add_argument("--activation-source", default="terminal_runtime")
    parser.add_argument("--terminal-state", choices=tuple(sorted(TERMINAL_STATES)))
    parser.add_argument("--reason-code")
    parser.add_argument("--terminal-source", default="terminal_runtime")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.finalize_active:
            if (args.clear_active or args.activate_active or args.profile_id or args.runtime_profile_id or args.run_id
                    or args.print_run_id or args.active_pointer_path
                    or args.prepared_by != "qgc_visible_terminal"):
                raise ValueError("operator_run_finalize_arguments_invalid")
            if not args.expected_run_id or not args.terminal_state or not args.reason_code:
                raise ValueError("operator_run_finalize_arguments_missing")
            result = finalize_active_run(
                expected_run_id=args.expected_run_id,
                terminal_state=args.terminal_state,
                reason_code=args.reason_code,
                source=args.terminal_source,
            )
            print(
                json.dumps(
                    {
                        "schema": "mosim.qgc_operator_run_result.v1",
                        "state": result["pointer"]["state"],
                        "run_id": result["pointer"]["run_id"],
                        "telemetry_present": result["telemetry_present"],
                    }
                )
            )
            return 0
        if args.activate_active:
            if (
                args.clear_active
                or args.profile_id
                or args.runtime_profile_id
                or args.run_id
                or args.active_pointer_path
                or args.print_run_id
                or args.terminal_state
                or args.reason_code
                or args.prepared_by != "qgc_visible_terminal"
            ):
                raise ValueError("operator_run_activate_arguments_invalid")
            if not args.expected_run_id:
                raise ValueError("operator_run_activate_arguments_missing")
            result = activate_active_run(
                expected_run_id=args.expected_run_id,
                source=args.activation_source,
            )
            print(
                json.dumps(
                    {
                        "schema": "mosim.qgc_operator_run_result.v1",
                        "state": result["state"],
                        "run_id": result["run_id"],
                    }
                )
            )
            return 0
        if args.clear_active:
            if (
                args.activate_active
                or args.profile_id
                or args.runtime_profile_id
                or args.run_id
                or args.active_pointer_path
                or args.print_run_id
                or args.expected_run_id
                or args.terminal_state
                or args.reason_code
                or args.prepared_by != "qgc_visible_terminal"
            ):
                raise ValueError("operator_run_clear_arguments_invalid")
            result = clear_active_run()
            print(json.dumps({"schema": "mosim.qgc_operator_run_result.v1", "state": "cleared", "run_id": result["run_id"]}))
            return 0
        if not args.profile_id or not args.runtime_profile_id:
            raise ValueError("operator_run_profile_and_runtime_required")
        result = prepare_run(
            profile_id=args.profile_id,
            runtime_profile_id=args.runtime_profile_id,
            run_id=args.run_id,
            active_pointer_relative_path=args.active_pointer_path or ACTIVE_POINTER_RELATIVE_PATH,
            prepared_by=args.prepared_by,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if args.print_run_id:
        print(result["run_id"])
    else:
        print(
            json.dumps(
                {
                    "schema": "mosim.qgc_operator_run_result.v1",
                    "state": "launch_prepared",
                    "run_id": result["run_id"],
                    "run_directory": str(result["run_directory"]),
                }
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
