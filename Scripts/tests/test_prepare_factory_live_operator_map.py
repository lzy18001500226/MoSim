from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from Scripts.ui.prepare_factory_live_operator_map import (
    EXPECTED_PATH_TOPIC,
    FACTORY_LAUNCH_RELATIVE,
    FACTORY_WORLD_RELATIVE,
    build_coordinate_evidence,
)
from Scripts.ui.runtime_sidecar import load_operator_map_snapshot
from src.orchestration.operator_map_replay import validate_coordinate_evidence


ROOT = Path(__file__).resolve().parents[2]


def _manifest() -> dict[str, object]:
    snapshot = load_operator_map_snapshot(
        ROOT / "Config" / "control_platform" / "operator_map_catalog.json",
        "factory_l2",
    )
    snapshot_hash = hashlib.sha256(
        json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return {
        "run_id": "qgc-factory-live-map-test",
        "operator_map_snapshot": snapshot,
        "operator_map_snapshot_hash": snapshot_hash,
    }


def test_factory_live_coordinate_evidence_binds_the_reviewed_world_and_topics() -> None:
    manifest = _manifest()
    evidence = build_coordinate_evidence(
        manifest=manifest,
        runtime_world_relative=FACTORY_WORLD_RELATIVE.as_posix(),
        runtime_launch_relative=FACTORY_LAUNCH_RELATIVE.as_posix(),
        display_pose_topic="/uav1/sunray/gazebo_pose",
        expected_path_topic=EXPECTED_PATH_TOPIC,
    )

    assert evidence["source_frame_id"] == "world"
    assert evidence["target_frame_id"] == "mworks_world"
    assert evidence["verification_basis"]["runtime_world_file"] == FACTORY_WORLD_RELATIVE.as_posix()
    validate_coordinate_evidence(
        evidence,
        map_snapshot=manifest["operator_map_snapshot"],
        snapshot_hash=manifest["operator_map_snapshot_hash"],
    )


def test_factory_live_coordinate_evidence_rejects_non_factory_runtime_source() -> None:
    with pytest.raises(ValueError, match="factory_live_map_world_not_factory_l2_clean"):
        build_coordinate_evidence(
            manifest=_manifest(),
            runtime_world_relative="References/Sunray/planning_test.world",
            runtime_launch_relative=FACTORY_LAUNCH_RELATIVE.as_posix(),
            display_pose_topic="/uav1/sunray/gazebo_pose",
            expected_path_topic=EXPECTED_PATH_TOPIC,
        )
