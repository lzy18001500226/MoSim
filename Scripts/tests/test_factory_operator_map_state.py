from __future__ import annotations

from pathlib import Path

import pytest

from Scripts.ui.runtime_sidecar import (
    _canonical_hash,
    build_operator_map_state,
    load_operator_map_snapshot,
    project_live_operator_map_frame,
    resolve_runtime_operator_map,
)
from src.orchestration.operator_map_replay import validate_coordinate_evidence
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


def _coordinate_evidence(manifest: dict[str, object], *, source_frame_id: str = "factory_odom") -> dict[str, object]:
    snapshot = manifest["operator_map_snapshot"]
    assert isinstance(snapshot, dict)
    return {
        "schema": "mosim.operator_map_coordinate_evidence.v1",
        "status": "verified",
        "evidence_id": "factory-l2-live-fixture",
        "operator_map_snapshot_hash": manifest["operator_map_snapshot_hash"],
        "map_id": snapshot["map_id"],
        "map_version": snapshot["map_version"],
        "asset_sha256": snapshot["asset_sha256"],
        "world_frame": snapshot["world_frame"],
        "coordinate_contract_id": snapshot["coordinate_contract_id"],
        "source_frame_id": source_frame_id,
        "target_frame_id": "mworks_world",
        "transform_target_from_source_4x4": [
            [0.0, -1.0, 0.0, 10.0],
            [1.0, 0.0, 0.0, -5.0],
            [0.0, 0.0, 1.0, 1.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
    }


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


def test_live_sidecar_projects_only_evidence_bound_geometry() -> None:
    manifest = _manifest()
    snapshot = manifest["operator_map_snapshot"]
    assert isinstance(snapshot, dict)
    evidence = validate_coordinate_evidence(
        _coordinate_evidence(manifest),
        map_snapshot=snapshot,
        snapshot_hash=str(manifest["operator_map_snapshot_hash"]),
    )
    vehicles, task_paths, map_data_status = project_live_operator_map_frame(
        vehicles=[
            {
                "vehicle_id": "uav1",
                "state": {
                    "connected": True,
                    "position": {"x": 2.0, "y": 3.0, "z": 0.0},
                    "position_frame": "factory_odom",
                    "orientation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
                    "linear_velocity": {"x": 1.0, "y": 0.0, "z": 0.0},
                    "linear_velocity_frame": "factory_odom",
                    "angular_velocity": {"x": 0.0, "y": 0.0, "z": 0.1},
                    "angular_velocity_frame": "factory_odom",
                },
            }
        ],
        task_paths={
            "expected": {
                "semantics": "mission_reference",
                "vehicle_scope": "uav1",
                "source_topic": "/mosim/reference_path",
                "updated_at": 10.0,
                "frame_id": "factory_odom",
                "points": [{"x": 2.0, "y": 3.0, "z": 0.0}, {"x": 4.0, "y": 3.0, "z": 0.0}],
            }
        },
        coordinate_evidence=evidence,
        run_id=str(manifest["run_id"]),
    )

    assert map_data_status == {"state": "accepted", "reason_code": ""}
    assert vehicles[0]["state"]["position"] == {"x": 7.0, "y": -3.0, "z": 1.0}
    assert vehicles[0]["state"]["position_frame"] == "mworks_world"
    assert vehicles[0]["state"]["linear_velocity"] == {"x": 0.0, "y": 1.0, "z": 0.0}
    assert vehicles[0]["state"]["linear_velocity_frame"] == "mworks_world"
    assert vehicles[0]["state"]["orientation"]["z"] == pytest.approx(2**-0.5)
    assert task_paths["expected"]["status"] == "available"
    assert task_paths["expected"]["frame_id"] == "mworks_world"
    assert task_paths["expected"]["points"][1] == {"x": 7.0, "y": -1.0, "z": 1.0}


def test_live_sidecar_hides_unverified_or_source_mismatched_geometry_without_stopping_telemetry() -> None:
    manifest = _manifest()
    raw_vehicles = [
        {
            "vehicle_id": "uav1",
            "state": {
                "connected": True,
                "position": {"x": 2.0, "y": 3.0, "z": 0.0},
                "position_frame": "factory_odom",
            },
        }
    ]
    pending_vehicles, pending_paths, pending_status = project_live_operator_map_frame(
        vehicles=raw_vehicles,
        task_paths={
            "future": {
                "frame_id": "factory_odom",
                "points": [{"x": 2.0, "y": 3.0, "z": 0.0}],
            }
        },
        coordinate_evidence=None,
        run_id=str(manifest["run_id"]),
    )
    assert pending_status == {"state": "accepted", "reason_code": ""}
    assert pending_vehicles == [{"vehicle_id": "uav1", "state": {"connected": True}}]
    assert pending_paths["future"]["status"] == "pending_coordinate_evidence"

    snapshot = manifest["operator_map_snapshot"]
    assert isinstance(snapshot, dict)
    evidence = validate_coordinate_evidence(
        _coordinate_evidence(manifest, source_frame_id="other_frame"),
        map_snapshot=snapshot,
        snapshot_hash=str(manifest["operator_map_snapshot_hash"]),
    )
    rejected_vehicles, _, rejected_status = project_live_operator_map_frame(
        vehicles=raw_vehicles,
        task_paths={},
        coordinate_evidence=evidence,
        run_id=str(manifest["run_id"]),
    )
    assert rejected_status == {
        "state": "rejected",
        "reason_code": "operator_map_coordinate_evidence_source_frame_mismatch",
    }
    assert rejected_vehicles == [{"vehicle_id": "uav1", "state": {"connected": True}}]


def test_map_state_can_report_a_display_only_rejection() -> None:
    state = build_operator_map_state(
        manifest=_manifest(),
        map_snapshot=_snapshot(),
        transport_mode="live_ros1",
        sequence=2,
        received_at_unix_s=1_784_000_200.0,
        source_timestamp_s=None,
        playback_state="live",
        playback_time_s=None,
        bag_id="",
        vehicles=[],
        task_paths={},
        map_data_status={
            "state": "rejected",
            "reason_code": "operator_map_coordinate_evidence_source_frame_mismatch",
        },
    )
    validate_operator_map_state(state, manifest=_manifest())
    assert state["map_data_status"]["state"] == "rejected"


def test_qgc_uses_the_frozen_snapshot_and_keeps_native_mission_upload_blocked() -> None:
    bridge = (ROOT / "apps/flight_console/mosim/custom/src/MoSimOperatorBridge.cc").read_text(encoding="utf-8")
    bridge_header = (ROOT / "apps/flight_console/mosim/custom/src/MoSimOperatorBridge.h").read_text(
        encoding="utf-8"
    )
    fly_map = (ROOT / "apps/flight_console/mosim/custom/src/FactoryFlyMap.qml").read_text(encoding="utf-8")
    plan_view = (ROOT / "apps/flight_console/mosim/custom/src/PlanView.qml").read_text(encoding="utf-8")

    assert 'Q_PROPERTY(QVariantMap operatorMap READ operatorMap NOTIFY stateChanged)' in bridge_header
    assert 'Q_PROPERTY(QVariantList operatorMaps READ operatorMaps NOTIFY stateChanged)' in bridge_header
    assert 'Q_PROPERTY(QString selectedMapId READ selectedMapId NOTIFY stateChanged)' in bridge_header
    assert 'const QVariantMap snapshot = manifest.value(QStringLiteral("operator_map_snapshot")).toMap()' in bridge
    assert '_operatorMap.insert(QStringLiteral("operator_map_snapshot_hash"), snapshotHash)' in bridge
    assert 'void MoSimOperatorBridge::selectOperatorMap(const QString &mapId)' in bridge
    assert 'map_locked_by_run_manifest' in bridge
    refresh_start = bridge.index('void MoSimOperatorBridge::refreshRuntimeState()')
    refresh_end = bridge.index('\nQVariantMap MoSimOperatorBridge::profileForId', refresh_start)
    refresh_body = bridge[refresh_start:refresh_end]
    unlocked_selection = refresh_body.index('_selectedProfileId = selected;')
    assert 'syncSelectedMapFromProfile();' in refresh_body[unlocked_selection:]
    assert 'String(mapMetadata.operator_map_snapshot_hash || "")' in fly_map
    assert 'readonly property bool mapFrameAccepted' in fly_map
    assert '实时地图坐标系与证据不匹配' in fly_map
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
