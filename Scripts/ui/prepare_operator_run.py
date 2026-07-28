#!/usr/bin/env python3
"""Prepare one QGC-selected operator run without starting its runtime.

The generated command is intentionally executed by the operator in a visible
terminal. This helper freezes the selected published Profile and Factory-map
snapshot before the existing launcher runs. It never starts or supervises
ROS, Gazebo, PX4, MAVROS, QGC, UE, RViz, or MWORKS.
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


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"operator_run_json_object_required:{path}")
    return value


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
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


def _active_pointer_path(root: Path) -> Path:
    return _root_path(root, ACTIVE_POINTER_RELATIVE_PATH)


def _active_pointer_is_live(root: Path) -> bool:
    pointer_path = _active_pointer_path(root)
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
) -> dict[str, Any]:
    root = root.resolve()
    if _active_pointer_is_live(root):
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
            "prepared_by": "qgc_visible_terminal",
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
        "prepared_by": "qgc_visible_terminal",
        "claim_boundary": (
            "This prepares a frozen operator run only. It does not prove that the copied launcher, "
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
        "source": "qgc_visible_terminal",
    }
    _atomic_write_json(_active_pointer_path(root), pointer)
    return {"run_id": selected_run_id, "run_directory": run_directory, "manifest": manifest, "pointer": pointer}


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-id")
    parser.add_argument("--runtime-profile-id")
    parser.add_argument("--run-id")
    parser.add_argument("--print-run-id", action="store_true")
    parser.add_argument("--clear-active", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.clear_active:
            if args.profile_id or args.runtime_profile_id or args.run_id or args.print_run_id:
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
