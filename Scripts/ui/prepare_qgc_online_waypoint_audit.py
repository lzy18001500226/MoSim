#!/usr/bin/env python3
"""Prepare an isolated QGC online-waypoint display audit run.

This creates only a frozen run, a scoped QGC pointer, and deterministic
coordinate-fixture metadata. It does not start QGC, ROS, PX4, Gazebo, MAVROS,
or a mission. The companion runner supplies a controlled ROS1 display stream.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.ui.prepare_operator_run import prepare_run
from src.orchestration.operator_map_replay import validate_coordinate_evidence


# The audit needs a currently selectable Factory L2 identity, not a disabled
# mission profile. The ROS messages below remain a controlled display fixture.
DEFAULT_PROFILE_ID = "px4ctrl_ground_standby_v1"
DEFAULT_RUNTIME_PROFILE_ID = "sunray_ros1_px4ctrl_ground_standby_single_v1"
AUDIT_ROOT = Path("Results") / "ui_platform" / "qgc_online_waypoint_audits"


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    temporary.replace(path)


def _default_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"qgc-online-waypoint-audit-{stamp}"


def build_coordinate_fixture(manifest: dict[str, Any]) -> dict[str, Any]:
    snapshot = manifest.get("operator_map_snapshot")
    snapshot_hash = manifest.get("operator_map_snapshot_hash")
    run_id = manifest.get("run_id")
    if not isinstance(snapshot, dict) or not isinstance(snapshot_hash, str) or not isinstance(run_id, str):
        raise ValueError("online_waypoint_audit_manifest_map_missing")
    world_frame = snapshot.get("world_frame")
    if not isinstance(world_frame, str) or not world_frame:
        raise ValueError("online_waypoint_audit_world_frame_missing")
    evidence = {
        "schema": "mosim.operator_map_coordinate_evidence.v1",
        "status": "verified",
        "evidence_id": f"{run_id}-controlled-ros1-display-fixture",
        "operator_map_snapshot_hash": snapshot_hash,
        "map_id": snapshot.get("map_id"),
        "map_version": snapshot.get("map_version"),
        "asset_sha256": snapshot.get("asset_sha256"),
        "world_frame": world_frame,
        "coordinate_contract_id": snapshot.get("coordinate_contract_id"),
        "source_frame_id": world_frame,
        "target_frame_id": world_frame,
        "transform_target_from_source_4x4": [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        "claim_boundary": (
            "Controlled ROS1 display fixture only. This identity transform proves neither the "
            "Gazebo/PX4/MAVROS coordinate chain nor mission-publication safety."
        ),
    }
    return validate_coordinate_evidence(evidence, map_snapshot=snapshot, snapshot_hash=snapshot_hash)


def prepare_online_waypoint_audit(
    *,
    root: Path = ROOT,
    profile_id: str = DEFAULT_PROFILE_ID,
    runtime_profile_id: str = DEFAULT_RUNTIME_PROFILE_ID,
    run_id: str | None = None,
    now: float | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    selected_run_id = run_id or _default_run_id()
    pointer_relative_path = AUDIT_ROOT / selected_run_id / "qgc_active_run.json"
    prepared = prepare_run(
        root=root,
        profile_id=profile_id,
        runtime_profile_id=runtime_profile_id,
        run_id=selected_run_id,
        now=now,
        active_pointer_relative_path=pointer_relative_path,
    )
    manifest = prepared["manifest"]
    run_directory = prepared["run_directory"]
    fixture = build_coordinate_fixture(manifest)
    evidence_path = run_directory / "ONLINE_WAYPOINT_DISPLAY_COORDINATE_FIXTURE.json"
    _atomic_write_json(evidence_path, fixture)

    audit_directory = root / AUDIT_ROOT / selected_run_id
    audit_manifest_path = audit_directory / "ONLINE_WAYPOINT_DISPLAY_AUDIT.json"
    audit_manifest = {
        "schema": "mosim.qgc_online_waypoint_display_audit.v1",
        "status": "prepared",
        "run_id": selected_run_id,
        "run_directory": run_directory.relative_to(root).as_posix(),
        "pointer_relative_path": pointer_relative_path.as_posix(),
        "coordinate_fixture_path": evidence_path.relative_to(root).as_posix(),
        "transport": {
            "mode": "live_ros1",
            "source": "controlled_ros1_display_fixture",
            "expected_path_topic": "/mosim/qgc_audit/expected_path",
            "future_marker_topic": "/mosim/qgc_audit/future_path",
        },
        "qgc_environment": {
            "MOSIM_PROJECT_ROOT": str(root),
            "MOSIM_QGC_ACTIVE_RUN_POINTER": pointer_relative_path.as_posix(),
        },
        "runner": "Scripts/ui/run_qgc_online_waypoint_fixture.sh",
        "launcher": "Scripts/ui/start_qgc_online_waypoint_audit.ps1",
        "prepared_at_unix_s": time.time() if now is None else now,
        "claim_boundary": (
            "This audit exercises a live ROS1 display stream, sidecar projection, and QGC polling. "
            "It is not PX4, MAVROS, Gazebo, controller, planner, or mission-upload acceptance."
        ),
    }
    _atomic_write_json(audit_manifest_path, audit_manifest)
    return {
        **prepared,
        "coordinate_fixture_path": evidence_path,
        "audit_manifest_path": audit_manifest_path,
        "audit_manifest": audit_manifest,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-id", default=DEFAULT_PROFILE_ID)
    parser.add_argument("--runtime-profile-id", default=DEFAULT_RUNTIME_PROFILE_ID)
    parser.add_argument("--run-id")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = prepare_online_waypoint_audit(
            profile_id=args.profile_id,
            runtime_profile_id=args.runtime_profile_id,
            run_id=args.run_id,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "schema": "mosim.qgc_online_waypoint_display_audit_result.v1",
                "run_id": result["run_id"],
                "pointer_relative_path": result["audit_manifest"]["pointer_relative_path"],
                "audit_manifest_path": str(result["audit_manifest_path"]),
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
