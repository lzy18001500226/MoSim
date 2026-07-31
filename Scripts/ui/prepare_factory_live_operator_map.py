#!/usr/bin/env python3
"""Bind one frozen QGC run to the reviewed Factory L2 live-map contract."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestration.operator_map_replay import canonical_json_hash, validate_coordinate_evidence
from src.orchestration.run_manifest_contract import validate_run_manifest_v2


FACTORY_WORLD_RELATIVE = Path(
    "Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/worlds/"
    "factoryenvironmentcollect_l2_static_review_clean.sdf"
)
FACTORY_LAUNCH_RELATIVE = Path("Scripts/sunray/factory_l2_sunray_px4_gazebo.launch")
FACTORY_FRAME_CONTRACT_RELATIVE = Path(
    "Results/unreal_scene_mapping/factory_l2_calibration_rig_review_20260702_192443/"
    "FACTORY_L2_CALIBRATION_FRAME_CONTRACT.json"
)
FACTORY_MAP_ID = "factory_l2"
FACTORY_WORLD_FRAME = "mworks_world"
FACTORY_COORDINATE_CONTRACT_ID = "factory_l2_mworks_world_v1"
DISPLAY_POSE_TOPIC = "/uav1/sunray/gazebo_pose"
EXPECTED_PATH_TOPIC = "/mosim/px4ctrl/reference_path"


def _read_object(path: Path, reason_code: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(reason_code) from exc
    if not isinstance(value, dict):
        raise ValueError(reason_code)
    return value


def _project_relative(path: Path, *, root: Path, reason_code: str) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(reason_code) from exc


def _atomic_write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    temporary.replace(path)


def build_coordinate_evidence(
    *,
    manifest: dict[str, Any],
    runtime_world_relative: str,
    runtime_launch_relative: str,
    display_pose_topic: str,
    expected_path_topic: str,
) -> dict[str, Any]:
    run_id = manifest.get("run_id")
    snapshot = manifest.get("operator_map_snapshot")
    snapshot_hash = manifest.get("operator_map_snapshot_hash")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("factory_live_map_run_id_missing")
    if not isinstance(snapshot, dict) or not isinstance(snapshot_hash, str):
        raise ValueError("factory_live_map_snapshot_missing")
    if canonical_json_hash(snapshot) != snapshot_hash:
        raise ValueError("factory_live_map_snapshot_hash_mismatch")
    if snapshot.get("map_id") != FACTORY_MAP_ID:
        raise ValueError("factory_live_map_id_mismatch")
    if snapshot.get("world_frame") != FACTORY_WORLD_FRAME:
        raise ValueError("factory_live_map_world_frame_mismatch")
    if snapshot.get("coordinate_contract_id") != FACTORY_COORDINATE_CONTRACT_ID:
        raise ValueError("factory_live_map_coordinate_contract_mismatch")
    if runtime_world_relative != FACTORY_WORLD_RELATIVE.as_posix():
        raise ValueError("factory_live_map_world_not_factory_l2_clean")
    if runtime_launch_relative != FACTORY_LAUNCH_RELATIVE.as_posix():
        raise ValueError("factory_live_map_launch_not_factory_l2")
    if display_pose_topic != DISPLAY_POSE_TOPIC:
        raise ValueError("factory_live_map_display_pose_topic_mismatch")
    if expected_path_topic != EXPECTED_PATH_TOPIC:
        raise ValueError("factory_live_map_expected_path_topic_mismatch")

    evidence = {
        "schema": "mosim.operator_map_coordinate_evidence.v1",
        "status": "verified",
        "evidence_id": f"{run_id}:factory_l2_live_gazebo_world_identity",
        "operator_map_snapshot_hash": snapshot_hash,
        "map_id": snapshot["map_id"],
        "map_version": snapshot["map_version"],
        "asset_sha256": snapshot["asset_sha256"],
        "world_frame": snapshot["world_frame"],
        "coordinate_contract_id": snapshot["coordinate_contract_id"],
        "source_frame_id": "world",
        "target_frame_id": snapshot["world_frame"],
        "transform_target_from_source_4x4": [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        "verification_basis": {
            "runtime_world_file": runtime_world_relative,
            "runtime_launch_file": runtime_launch_relative,
            "display_pose_topic": display_pose_topic,
            "expected_path_topic": expected_path_topic,
            "source_frame_requirement": "world",
            "static_contract": FACTORY_FRAME_CONTRACT_RELATIVE.as_posix(),
            "contract_summary": (
                "Gazebo world and MWORKS world use meters and z-up; only the independent UE renderer "
                "applies centimetres and Y inversion. The sidecar verifies message frame IDs at runtime."
            ),
        },
        "claim_boundary": (
            "This evidence permits Factory L2 QGC map projection only when live Gazebo pose and reference-path "
            "messages declare the required world frame. It neither changes controller inputs nor proves tracking, "
            "fault tolerance, or UE rendering."
        ),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }
    validate_coordinate_evidence(evidence, map_snapshot=snapshot, snapshot_hash=snapshot_hash)
    return evidence


def prepare_live_factory_operator_map(
    *,
    run_dir: Path,
    manifest_path: Path,
    world_file: Path,
    gazebo_launch_file: Path,
    display_pose_topic: str = DISPLAY_POSE_TOPIC,
    expected_path_topic: str = EXPECTED_PATH_TOPIC,
    root: Path = ROOT,
) -> dict[str, Any]:
    root = root.resolve()
    run_dir = run_dir.resolve()
    manifest_path = manifest_path.resolve()
    expected_manifest_path = run_dir / "RUN_MANIFEST.json"
    if manifest_path != expected_manifest_path:
        raise ValueError("factory_live_map_manifest_path_mismatch")
    if not manifest_path.is_file():
        raise ValueError("factory_live_map_manifest_missing")
    manifest = _read_object(manifest_path, "factory_live_map_manifest_unreadable")
    validate_run_manifest_v2(manifest)

    world_relative = _project_relative(world_file, root=root, reason_code="factory_live_map_world_outside_project")
    launch_relative = _project_relative(
        gazebo_launch_file, root=root, reason_code="factory_live_map_launch_outside_project"
    )
    if world_relative != FACTORY_WORLD_RELATIVE.as_posix():
        raise ValueError("factory_live_map_world_not_factory_l2_clean")
    if launch_relative != FACTORY_LAUNCH_RELATIVE.as_posix():
        raise ValueError("factory_live_map_launch_not_factory_l2")
    if not world_file.is_file() or not gazebo_launch_file.is_file():
        raise ValueError("factory_live_map_runtime_source_missing")
    if not (root / FACTORY_FRAME_CONTRACT_RELATIVE).is_file():
        raise ValueError("factory_live_map_static_contract_missing")

    evidence = build_coordinate_evidence(
        manifest=manifest,
        runtime_world_relative=world_relative,
        runtime_launch_relative=launch_relative,
        display_pose_topic=display_pose_topic,
        expected_path_topic=expected_path_topic,
    )
    evidence_path = run_dir / "OPERATOR_MAP_COORDINATE_EVIDENCE.json"
    _atomic_write_json(evidence_path, evidence)
    return {
        "schema": "mosim.factory_live_operator_map_prepare_result.v1",
        "status": "prepared",
        "run_id": manifest["run_id"],
        "coordinate_evidence": str(evidence_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--world-file", type=Path, required=True)
    parser.add_argument("--gazebo-launch-file", type=Path, required=True)
    parser.add_argument("--display-pose-topic", default=DISPLAY_POSE_TOPIC)
    parser.add_argument("--expected-path-topic", default=EXPECTED_PATH_TOPIC)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = prepare_live_factory_operator_map(
            run_dir=args.run_dir,
            manifest_path=args.manifest,
            world_file=args.world_file,
            gazebo_launch_file=args.gazebo_launch_file,
            display_pose_topic=args.display_pose_topic,
            expected_path_topic=args.expected_path_topic,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "reason_code": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
