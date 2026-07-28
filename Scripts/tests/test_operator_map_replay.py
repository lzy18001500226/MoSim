from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

import Scripts.ui.replay_rosbag_operator_map as replay_entry
from Scripts.ui.replay_rosbag_operator_map import _telemetry_payload, run_replay
from Scripts.ui.runtime_sidecar import _canonical_hash, build_operator_map_state, load_operator_map_snapshot
from src.orchestration.operator_map_replay import (
    build_replay_manifest,
    derive_replay_frames,
    validate_coordinate_evidence,
)
from src.orchestration.operator_map_state import validate_operator_map_state


ROOT = Path(__file__).resolve().parents[2]


def _manifest(vehicle_count: int = 1) -> dict[str, object]:
    snapshot = load_operator_map_snapshot(
        ROOT / "Config" / "control_platform" / "operator_map_catalog.json",
        "factory_l2",
    )
    return {
        "run_id": "run-operator-map-replay-test",
        "experiment_profile_id": "factory_l2_fuel_fixed64_exploration_v1",
        "experiment_profile_hash": "profile-hash-replay-test",
        "operator_map_snapshot": snapshot,
        "operator_map_snapshot_hash": _canonical_hash(snapshot),
        "vehicle_count": vehicle_count,
        "scenario_snapshot": {},
    }


def _evidence(manifest: dict[str, object], *, source_frame_id: str = "mworks_world") -> dict[str, object]:
    snapshot = manifest["operator_map_snapshot"]
    assert isinstance(snapshot, dict)
    return {
        "schema": "mosim.operator_map_coordinate_evidence.v1",
        "status": "verified",
        "evidence_id": "factory-l2-replay-fixture",
        "operator_map_snapshot_hash": manifest["operator_map_snapshot_hash"],
        "map_id": snapshot["map_id"],
        "map_version": snapshot["map_version"],
        "asset_sha256": snapshot["asset_sha256"],
        "world_frame": snapshot["world_frame"],
        "coordinate_contract_id": snapshot["coordinate_contract_id"],
        "source_frame_id": source_frame_id,
        "target_frame_id": "mworks_world",
        "transform_target_from_source_4x4": [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
    }


def _sample(vehicle_id: str, bag_time_s: float, x: float, y: float) -> dict[str, object]:
    return {
        "vehicle_id": vehicle_id,
        "bag_time_s": bag_time_s,
        "source_timestamp_s": bag_time_s + 100.0,
        "frame_id": "mworks_world",
        "position": {"x": x, "y": y, "z": 1.2},
        "orientation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
        "linear_velocity": {"x": 1.0, "y": 0.0, "z": 0.0},
        "angular_velocity": {"x": 0.0, "y": 0.0, "z": 0.1},
    }


def test_verified_coordinate_evidence_projects_a_drawable_replay_frame() -> None:
    manifest = _manifest()
    snapshot = manifest["operator_map_snapshot"]
    assert isinstance(snapshot, dict)
    evidence = validate_coordinate_evidence(
        _evidence(manifest), map_snapshot=snapshot, snapshot_hash=str(manifest["operator_map_snapshot_hash"])
    )
    frames = derive_replay_frames(
        [_sample("uav1", 10.0, 2.0, -3.0), _sample("uav1", 10.5, 3.0, -3.0)],
        vehicle_count=1,
        coordinate_evidence=evidence,
    )

    assert frames[-1]["playback_time_s"] == 0.5
    assert frames[-1]["bag_time_s"] == 10.5
    assert frames[-1]["vehicles"][0]["state"]["position_frame"] == "mworks_world"
    state_map = dict(snapshot)
    state_map["coordinate_contract_status"] = "verified"
    state = build_operator_map_state(
        manifest=manifest,
        map_snapshot=state_map,
        transport_mode="rosbag_replay",
        sequence=2,
        received_at_unix_s=1_784_000_000.0,
        source_timestamp_s=frames[-1]["source_timestamp_s"],
        playback_state="playing",
        playback_time_s=frames[-1]["playback_time_s"],
        bag_id="rosbag:fixture:1234567890abcdef",
        vehicles=frames[-1]["vehicles"],
        task_paths={},
    )
    validate_operator_map_state(state, manifest=manifest)
    assert state["map"]["coordinate_contract_status"] == "verified"
    assert state["vehicles"][0]["state"]["position"] == {"x": 3.0, "y": -3.0, "z": 1.2}


def test_multivehicle_replay_never_invents_missing_vehicle_positions() -> None:
    manifest = _manifest(vehicle_count=3)
    snapshot = manifest["operator_map_snapshot"]
    assert isinstance(snapshot, dict)
    evidence = validate_coordinate_evidence(
        _evidence(manifest), map_snapshot=snapshot, snapshot_hash=str(manifest["operator_map_snapshot_hash"])
    )
    frames = derive_replay_frames(
        [
            _sample("uav1", 1.0, 0.0, 0.0),
            _sample("uav2", 1.1, 1.0, 0.0),
            _sample("uav3", 1.2, 2.0, 0.0),
        ],
        vehicle_count=3,
        coordinate_evidence=evidence,
    )

    assert frames[0]["vehicles"] == []
    assert frames[1]["vehicles"] == []
    assert [vehicle["vehicle_id"] for vehicle in frames[2]["vehicles"]] == ["uav1", "uav2", "uav3"]


def test_coordinate_evidence_cannot_be_reused_for_another_map_snapshot() -> None:
    manifest = _manifest()
    snapshot = manifest["operator_map_snapshot"]
    assert isinstance(snapshot, dict)
    evidence = _evidence(manifest)
    evidence["map_id"] = "city_l3"

    with pytest.raises(ValueError, match="operator_map_coordinate_evidence_identity_mismatch"):
        validate_coordinate_evidence(
            evidence, map_snapshot=snapshot, snapshot_hash=str(manifest["operator_map_snapshot_hash"])
        )


def test_replay_entry_writes_completed_run_bound_telemetry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    manifest = _manifest()
    manifest["controller_backend"] = "fixture_replay_backend_v1"
    (run_dir / "RUN_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    evidence_path = tmp_path / "coordinate_evidence.json"
    evidence_path.write_text(json.dumps(_evidence(manifest)), encoding="utf-8")
    records_path = tmp_path / "records.jsonl"
    records_path.write_text(
        "\n".join(
            json.dumps(record)
            for record in [
                _sample("uav1", 2.0, 0.0, 0.0),
                {
                    "record_type": "expected_path",
                    "bag_time_s": 2.1,
                    "source_timestamp_s": 102.1,
                    "source_topic": "/mosim/reference_path",
                    "frame_id": "mworks_world",
                    "points": [{"x": 0.0, "y": 0.0, "z": 1.2}, {"x": 1.0, "y": 0.0, "z": 1.2}],
                },
                _sample("uav1", 2.2, 1.0, 0.0),
                {
                    "record_type": "future_path",
                    "bag_time_s": 2.4,
                    "source_timestamp_s": 102.4,
                    "source_topic": "/planning/bspline",
                    "frame_id": "mworks_world",
                    "points": [{"x": 1.0, "y": 0.0, "z": 1.2}, {"x": 2.0, "y": 0.5, "z": 1.2}],
                },
                _sample("uav1", 2.3, 1.5, 0.0),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    args = argparse.Namespace(
        run_dir=run_dir,
        manifest=None,
        bag=None,
        records_jsonl=records_path,
        odom_topic=[],
        coordinate_evidence=evidence_path,
        speed=1.0,
        no_wait=True,
    )

    original_atomic_write = replay_entry.atomic_write_json
    written_map_states: list[dict[str, object]] = []

    def capture_atomic_write(path: Path, payload: object) -> None:
        original_atomic_write(path, payload)
        if path.name == "telemetry.json" and isinstance(payload, dict):
            written_map_states.append(json.loads(json.dumps(payload["map_state"])))

    monkeypatch.setattr(replay_entry, "atomic_write_json", capture_atomic_write)
    assert run_replay(args) == 0
    telemetry = json.loads((run_dir / "telemetry.json").read_text(encoding="utf-8"))
    replay_manifest = json.loads((run_dir / "OPERATOR_MAP_REPLAY_MANIFEST.json").read_text(encoding="utf-8"))
    status = json.loads((run_dir / "OPERATOR_MAP_REPLAY_STATUS.json").read_text(encoding="utf-8"))

    validate_operator_map_state(telemetry["map_state"], manifest=manifest)
    assert telemetry["map_state"]["transport"]["playback_state"] == "completed"
    assert telemetry["map_state"]["map"]["coordinate_contract_status"] == "verified"
    assert telemetry["map_state"]["task_paths"]["expected"]["status"] == "available"
    assert telemetry["map_state"]["task_paths"]["expected"]["semantics"] == "exploration_target_sequence"
    assert telemetry["map_state"]["task_paths"]["expected"]["points"][-1] == {"x": 1.0, "y": 0.0, "z": 1.2}
    assert telemetry["map_state"]["task_paths"]["future"]["status"] == "available"
    assert telemetry["map_state"]["task_paths"]["future"]["semantics"] == "planner_sampled_future_trajectory"
    assert telemetry["map_state"]["task_paths"]["future"]["points"][-1] == {"x": 2.0, "y": 0.5, "z": 1.2}
    states_by_playback_time = {
        round(float(state["transport"]["playback_time_s"]), 4): state for state in written_map_states
    }
    assert states_by_playback_time[0.0]["task_paths"] == {}
    assert set(states_by_playback_time[0.1]["task_paths"]) == {"expected"}
    assert set(states_by_playback_time[0.2]["task_paths"]) == {"expected"}
    assert set(states_by_playback_time[0.3]["task_paths"]) == {"expected"}
    assert set(states_by_playback_time[0.4]["task_paths"]) == {"expected", "future"}
    assert telemetry["operator_runtime_status"] == {
        "schema": "mosim.operator_runtime_status.v1",
        "run_id": manifest["run_id"],
        "experiment_profile_id": manifest["experiment_profile_id"],
        "experiment_profile_hash": manifest["experiment_profile_hash"],
        "controller_backend": "fixture_replay_backend_v1",
        "state": "replaying",
        "reason_code": "operator_map_rosbag_replay",
        "updated_at_unix_s": pytest.approx(telemetry["timestamp"]),
    }
    assert replay_manifest["source"]["kind"] == "normalized_rosbag_export_test_only"
    assert replay_manifest["output"]["transport_mode"] == "rosbag_replay"
    assert replay_manifest["frame_count"] == 5
    assert replay_manifest["odom_frame_count"] == 3
    assert replay_manifest["duration_s"] == pytest.approx(0.4)
    assert status["state"] == "completed"


def test_legacy_manifest_replay_keeps_map_data_without_runtime_status() -> None:
    manifest = _manifest()
    map_state = {
        "vehicles": [],
        "task_paths": {},
        "transport": {"playback_state": "completed"},
    }

    telemetry = _telemetry_payload(manifest, map_state, now=123.0)

    assert telemetry["map_state"] is map_state
    assert "operator_runtime_status" not in telemetry


def test_replay_manifest_binds_the_source_hash_and_coordinate_status() -> None:
    manifest = _manifest()
    frames = [{"playback_time_s": 0.0, "source_timestamp_s": 10.0, "vehicles": []}]
    replay_manifest = build_replay_manifest(
        manifest=manifest,
        source_kind="ros1_bag",
        source_path=Path("factory.bag"),
        source_sha256="a" * 64,
        bag_id="rosbag:factory.bag:aaaaaaaaaaaaaaaa",
        odom_topics={"uav1": "/uav1/mavros/local_position/odom"},
        coordinate_evidence=None,
        coordinate_evidence_sha256="",
        frames=frames,
    )

    assert replay_manifest["schema"] == "mosim.operator_map_replay_manifest.v1"
    assert replay_manifest["coordinate_evidence"]["status"] == "pending_runtime_validation"
    assert replay_manifest["source"]["sha256"] == "a" * 64
