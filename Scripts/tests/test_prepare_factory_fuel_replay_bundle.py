from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

from Scripts.ui.runtime_sidecar import load_operator_map_snapshot
from src.orchestration.operator_map_replay import validate_coordinate_evidence


ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "Scripts" / "sunray" / "prepare_factory_fuel_replay_bundle.py"
    spec = importlib.util.spec_from_file_location("prepare_factory_fuel_replay_bundle", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_coordinate_evidence_is_bound_to_the_frozen_factory_snapshot() -> None:
    module = load_module()
    snapshot = load_operator_map_snapshot(
        ROOT / "Config" / "control_platform" / "operator_map_catalog.json", "factory_l2"
    )
    evidence = module.build_coordinate_evidence(
        run_id="p4-fixture",
        map_snapshot=snapshot,
        source_frame_id="world",
        source_bag=ROOT / "Results" / "fixture.bag",
        clip_start_s=12.0,
        clip_end_s=42.0,
    )

    checked = validate_coordinate_evidence(
        evidence,
        map_snapshot=snapshot,
        snapshot_hash=evidence["operator_map_snapshot_hash"],
    )
    assert checked["target_frame_id"] == "mworks_world"
    assert checked["transform_target_from_source_4x4"] == [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]
    assert evidence["verification_basis"]["source_truth_topic"] == module.DISPLAY_TRUTH_TOPIC
    assert module.DISPLAY_TRUTH_TOPIC == "/uav1/sunray/gazebo_pose"
    with pytest.raises(ValueError, match="p4_replay_odom_frame_not_world"):
        module.build_coordinate_evidence(
            run_id="p4-fixture",
            map_snapshot=snapshot,
            source_frame_id="odom",
            source_bag=ROOT / "Results" / "fixture.bag",
            clip_start_s=12.0,
            clip_end_s=42.0,
        )


def test_normalized_odom_and_position_command_rows_match_ue_replay_contract() -> None:
    module = load_module()
    message = SimpleNamespace(
        pose=SimpleNamespace(
            pose=SimpleNamespace(
                position=SimpleNamespace(x=1.0, y=-2.0, z=3.0),
                orientation=SimpleNamespace(x=0.0, y=0.0, z=0.0, w=1.0),
            )
        ),
        twist=SimpleNamespace(twist=SimpleNamespace(linear=SimpleNamespace(x=0.4, y=0.5, z=-0.6))),
    )
    command = SimpleNamespace(position=SimpleNamespace(x=1.5, y=-2.5, z=1.2))

    odom_row = module.odom_to_csv_row(message, 31.25, 30.0)
    command_row = module.position_command_to_csv_row(command, 31.5, 30.0)

    assert list(odom_row) == ["t", "phase", "x", "y", "z", "vx", "vy", "vz", "roll", "pitch", "yaw"]
    assert odom_row["t"] == 1.25
    assert odom_row["yaw"] == 0.0
    assert command_row == {"t": 1.5, "phase": "recorded_position_cmd", "x": 1.5, "y": -2.5, "z": 1.2}


def test_run_manifest_freezes_the_scenario_and_source_identity() -> None:
    module = load_module()
    snapshot = load_operator_map_snapshot(
        ROOT / "Config" / "control_platform" / "operator_map_catalog.json", "factory_l2"
    )
    scenario = {
        "id": "factory_l2_fuel_fixed64_exploration_v1",
        "vehicle_count": 1,
        "mission": {"type": "fuel_single_exploration"},
    }
    manifest = module.build_run_manifest(
        run_id="p4-fixture",
        scenario=scenario,
        map_snapshot=snapshot,
        source_run_dir=ROOT / "Results" / "source-run",
        source_bag=ROOT / "Results" / "source-run" / "source.bag",
        source_bag_sha256="a" * 64,
        clip_start_s=12.0,
        clip_end_s=42.0,
        topic_counts={module.DISPLAY_TRUTH_TOPIC: 20},
    )

    assert manifest["experiment_profile_id"] == scenario["id"]
    assert manifest["operator_map_snapshot_hash"] == module.canonical_json_hash(snapshot)
    assert manifest["source_bundle"]["source_bag_sha256"] == "a" * 64
    assert manifest["source_bundle"]["clip_duration_s"] == 30.0
