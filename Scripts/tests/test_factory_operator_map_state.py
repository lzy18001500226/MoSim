from __future__ import annotations

from pathlib import Path

import pytest

from Scripts.ui.runtime_sidecar import (
    _canonical_hash,
    build_operator_map_state,
    load_operator_map_snapshot,
    resolve_runtime_operator_map,
)
from src.orchestration.operator_map_state import validate_operator_map_state


ROOT = Path(__file__).resolve().parents[2]


def _manifest() -> dict[str, object]:
    snapshot = load_operator_map_snapshot(
        ROOT / "Config" / "control_platform" / "operator_map_catalog.json",
        "factory_l2",
    )
    return {
        "run_id": "run-factory-map-test",
        "experiment_profile_id": "factory_l2_fuel_fixed64_exploration_v1",
        "experiment_profile_hash": "profile-hash-test",
        "operator_map_snapshot": snapshot,
        "operator_map_snapshot_hash": _canonical_hash(snapshot),
        "scenario_snapshot": {
            "exploration_boundary": {
                "min_x_m": -98.4,
                "max_x_m": 77.2,
                "min_y_m": -51.3,
                "max_y_m": 12.6,
            },
            "formation": {"target_center_xy_m": [12.0, -4.0]},
        },
    }


def _snapshot() -> dict[str, object]:
    snapshot = load_operator_map_snapshot(
        ROOT / "Config" / "control_platform" / "operator_map_catalog.json",
        "factory_l2",
    )
    snapshot["coordinate_contract_status"] = "verified"
    return snapshot


def test_live_map_state_keeps_receive_time_distinct_from_ros_source_time() -> None:
    state = build_operator_map_state(
        manifest=_manifest(),
        map_snapshot=_snapshot(),
        transport_mode="live_ros1",
        sequence=7,
        received_at_unix_s=1_784_000_001.5,
        source_timestamp_s=42.25,
        playback_state="playing",
        playback_time_s=None,
        bag_id="",
        vehicles=[{"vehicle_id": "uav1", "state": {"connected": True}}],
        task_paths={
            "expected": {
                "status": "available",
                "frame_id": "mworks_world",
                "points": [{"x": 0, "y": 0}],
            }
        },
    )

    assert state["schema"] == "mosim.operator_map_state.v1"
    assert state["run_id"] == "run-factory-map-test"
    assert state["profile_id"] == "factory_l2_fuel_fixed64_exploration_v1"
    assert state["transport"] == {
        "mode": "live_ros1",
        "sequence": 7,
        "received_at_unix_s": 1_784_000_001.5,
        "source_timestamp_s": 42.25,
        "playback_state": "live",
        "playback_time_s": None,
        "bag_id": "",
    }
    assert state["map"]["map_id"] == "factory_l2"
    assert state["map"]["coordinate_contract_status"] == "verified"
    assert state["map"]["operator_map_snapshot_hash"] == _manifest()["operator_map_snapshot_hash"]
    assert state["task_boundary"]["max_x_m"] == 77.2
    assert state["formation_target"]["target_center_xy_m"] == [12.0, -4.0]


def test_replay_map_state_preserves_a_paused_frame_without_claiming_live_data() -> None:
    state = build_operator_map_state(
        manifest=_manifest(),
        map_snapshot=_snapshot(),
        transport_mode="rosbag_replay",
        sequence=3,
        received_at_unix_s=1_784_000_010.0,
        source_timestamp_s=17.0,
        playback_state="paused",
        playback_time_s=17.0,
        bag_id="factory_l2_fuel_run.bag",
        vehicles=[],
        task_paths={},
    )

    assert state["transport"]["mode"] == "rosbag_replay"
    assert state["transport"]["playback_state"] == "paused"
    assert state["transport"]["bag_id"] == "factory_l2_fuel_run.bag"


def test_replay_requires_a_bag_identity_and_valid_coordinate_status() -> None:
    with pytest.raises(ValueError, match="operator_map_replay_bag_id_missing"):
        build_operator_map_state(
            manifest=_manifest(),
            map_snapshot=_snapshot(),
            transport_mode="rosbag_replay",
            sequence=1,
            received_at_unix_s=1.0,
            source_timestamp_s=None,
            playback_state="playing",
            playback_time_s=0.0,
            bag_id="",
            vehicles=[],
            task_paths={},
        )


def test_runtime_map_uses_the_manifest_snapshot_and_rejects_cli_identity_overrides() -> None:
    manifest = _manifest()
    state_map, snapshot_hash = resolve_runtime_operator_map(manifest, requested_map_id="factory_l2")

    assert state_map["map_id"] == "factory_l2"
    assert state_map["coordinate_contract_status"] == "pending_runtime_validation"
    assert snapshot_hash == manifest["operator_map_snapshot_hash"]
    with pytest.raises(ValueError, match="operator_map_coordinate_evidence_required"):
        resolve_runtime_operator_map(manifest, coordinate_contract_status="verified")
    with pytest.raises(ValueError, match="operator_map_cli_map_override_mismatch"):
        resolve_runtime_operator_map(manifest, requested_map_id="city_l3")
    with pytest.raises(ValueError, match="operator_map_cli_coordinate_contract_override_mismatch"):
        resolve_runtime_operator_map(manifest, requested_coordinate_contract_id="other_contract")


def test_tampered_manifest_snapshot_is_rejected_before_map_state_is_emitted() -> None:
    manifest = _manifest()
    manifest["operator_map_snapshot"]["map_version"] = "tampered"

    with pytest.raises(ValueError, match="operator_map_manifest_snapshot_hash_mismatch"):
        resolve_runtime_operator_map(manifest)


def test_map_state_validator_rejects_identity_and_verified_frame_mismatches() -> None:
    state = build_operator_map_state(
        manifest=_manifest(),
        map_snapshot=_snapshot(),
        transport_mode="live_ros1",
        sequence=9,
        received_at_unix_s=1_784_000_100.0,
        source_timestamp_s=43.0,
        playback_state="live",
        playback_time_s=None,
        bag_id="",
        vehicles=[
            {
                "vehicle_id": "uav1",
                "state": {
                    "connected": True,
                    "position": {"x": 1.0, "y": -2.0, "z": 0.5},
                    "position_frame": "mworks_world",
                    "orientation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
                },
            }
        ],
        task_paths={
            "future": {
                "status": "available",
                "frame_id": "mworks_world",
                "updated_at": 1_784_000_100.0,
                "points": [{"x": 1.0, "y": -2.0}, {"x": 2.0, "y": -1.0}],
            }
        },
    )

    validate_operator_map_state(state, manifest=_manifest())
    state["profile_hash"] = "other-profile"
    with pytest.raises(ValueError, match="operator_map_profile_identity_mismatch"):
        validate_operator_map_state(state, manifest=_manifest())

    state["profile_hash"] = "profile-hash-test"
    state["vehicles"][0]["state"]["position_frame"] = "map"
    with pytest.raises(ValueError, match="operator_map_vehicle_frame_mismatch"):
        validate_operator_map_state(state, manifest=_manifest())


def test_qgc_uses_the_frozen_snapshot_and_keeps_native_mission_upload_blocked() -> None:
    bridge = (ROOT / "apps/flight_console/mosim/custom/src/MoSimOrchestratorBridge.cc").read_text(encoding="utf-8")
    bridge_header = (ROOT / "apps/flight_console/mosim/custom/src/MoSimOrchestratorBridge.h").read_text(
        encoding="utf-8"
    )
    fly_map = (ROOT / "apps/flight_console/mosim/custom/src/FactoryFlyMap.qml").read_text(encoding="utf-8")
    plan_view = (ROOT / "apps/flight_console/mosim/custom/src/PlanView.qml").read_text(encoding="utf-8")

    assert 'Q_PROPERTY(QVariantMap operatorMap READ operatorMap NOTIFY responseChanged)' in bridge_header
    assert 'manifestSnapshot = _runManifest.value(QStringLiteral("operator_map_snapshot"))' in bridge
    assert 'manifestSnapshotHash = _runManifest.value(QStringLiteral("operator_map_snapshot_hash"))' in bridge
    assert 'String(mapMetadata.operator_map_snapshot_hash || "")' in fly_map
    assert 'function applyOperatorMapViewport()' in plan_view
    assert 'identity === _appliedOperatorMapIdentity' in plan_view
    assert 'function factoryMissionPublicationAllowed()' in plan_view
    assert '任务上传已阻止' in plan_view

    invalid = _snapshot()
    invalid["coordinate_contract_status"] = "not_a_state"
    with pytest.raises(ValueError, match="operator_map_coordinate_status_invalid"):
        build_operator_map_state(
            manifest=_manifest(),
            map_snapshot=invalid,
            transport_mode="live_ros1",
            sequence=1,
            received_at_unix_s=1.0,
            source_timestamp_s=None,
            playback_state="playing",
            playback_time_s=None,
            bag_id="",
            vehicles=[],
            task_paths={},
        )
