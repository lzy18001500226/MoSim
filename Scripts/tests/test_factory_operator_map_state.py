from __future__ import annotations

import json
from pathlib import Path

import pytest

from Scripts.ui.runtime_sidecar import (
    _canonical_hash,
    build_live_operator_map_state_or_rejected,
    build_operator_map_state,
    load_operator_map_snapshot,
    project_live_operator_map_frame,
    resolve_runtime_operator_map,
)
from src.orchestration.operator_map_replay import validate_coordinate_evidence
from src.orchestration.operator_map_state import (
    append_operator_map_actual_tracks,
    validate_image_coordinate_contract,
    validate_operator_map_snapshot,
    validate_operator_map_state,
)


ROOT = Path(__file__).resolve().parents[2]
QGC_CUSTOM = ROOT / "src" / "ground_station" / "qgc" / "mosim_extension" / "custom"


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


def test_actual_tracks_are_bounded_real_vehicle_samples_and_bind_the_map_run() -> None:
    manifest = _manifest()
    tracks = append_operator_map_actual_tracks(
        {},
        [
            {
                "vehicle_id": "uav1",
                "state": {
                    "connected": True,
                    "position": {"x": 1.0, "y": -2.0, "z": 0.5},
                    "position_frame": "mworks_world",
                },
            }
        ],
        run_id=str(manifest["run_id"]),
        world_frame="mworks_world",
        updated_at=1_784_000_020.0,
    )
    tracks = append_operator_map_actual_tracks(
        tracks,
        [
            {
                "vehicle_id": "uav1",
                "state": {
                    "connected": True,
                    "position": {"x": 1.01, "y": -2.0, "z": 0.6},
                    "position_frame": "mworks_world",
                },
            }
        ],
        run_id=str(manifest["run_id"]),
        world_frame="mworks_world",
        updated_at=1_784_000_021.0,
    )
    tracks = append_operator_map_actual_tracks(
        tracks,
        [
            {
                "vehicle_id": "uav1",
                "state": {
                    "connected": True,
                    "position": {"x": 1.1, "y": -2.0, "z": 0.7},
                    "position_frame": "mworks_world",
                },
            }
        ],
        run_id=str(manifest["run_id"]),
        world_frame="mworks_world",
        updated_at=1_784_000_022.0,
    )
    assert tracks["uav1"]["semantics"] == "actual_vehicle_track"
    assert tracks["uav1"]["points"] == [
        {"x": 1.0, "y": -2.0, "z": 0.5},
        {"x": 1.1, "y": -2.0, "z": 0.7},
    ]

    state = build_operator_map_state(
        manifest=manifest,
        map_snapshot=_snapshot(),
        transport_mode="live_ros1",
        sequence=10,
        received_at_unix_s=1_784_000_022.0,
        source_timestamp_s=43.0,
        playback_state="live",
        playback_time_s=None,
        bag_id="",
        vehicles=[
            {
                "vehicle_id": "uav1",
                "state": {
                    "connected": True,
                    "position": {"x": 1.1, "y": -2.0, "z": 0.7},
                    "position_frame": "mworks_world",
                    "orientation": {"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0},
                },
            }
        ],
        task_paths={},
        actual_tracks=tracks,
    )
    validate_operator_map_state(state, manifest=manifest)
    state["actual_tracks"]["uav1"]["run_id"] = "other-run"
    with pytest.raises(ValueError, match="operator_map_actual_track_run_id_mismatch"):
        validate_operator_map_state(state, manifest=manifest)


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


def test_image_coordinate_contract_binds_the_catalog_matrix_and_run_manifest_hash() -> None:
    snapshot = load_operator_map_snapshot(
        ROOT / "Config" / "control_platform" / "operator_map_catalog.json",
        "factory_l2",
    )
    contract = validate_image_coordinate_contract(snapshot)

    assert contract["matrix_sha256"] == "44ad1b989e3704b9bccbc1406f57f7112b5729869eb326099022b70f50dd548b"
    assert contract["image_size_px"] == {"width": 2048, "height": 800}
    assert contract["world_to_pixel_3x3"][0][2] == pytest.approx(1037.9992605649718)
    assert contract["pixel_to_world_3x3"][1][2] == pytest.approx(269.43695652173915)

    frozen_hash = _canonical_hash(snapshot)
    tampered_snapshot = json.loads(json.dumps(snapshot))
    tampered_snapshot["image_coordinate_contract"]["world_to_pixel_3x3"][0][2] += 1.0
    assert _canonical_hash(tampered_snapshot) != frozen_hash
    with pytest.raises(ValueError, match="operator_map_image_coordinate_contract_inverse_mismatch"):
        validate_operator_map_snapshot(tampered_snapshot)

    missing_contract = _snapshot()
    missing_contract.pop("image_coordinate_contract")
    with pytest.raises(ValueError, match="operator_map_image_coordinate_contract_missing"):
        validate_operator_map_snapshot(missing_contract)


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


def test_live_sidecar_rejects_out_of_bounds_geometry_without_extending_actual_tracks() -> None:
    manifest = _manifest()
    snapshot = _snapshot()
    evidence = validate_coordinate_evidence(
        _coordinate_evidence(manifest),
        map_snapshot=manifest["operator_map_snapshot"],
        snapshot_hash=str(manifest["operator_map_snapshot_hash"]),
    )
    existing_tracks = append_operator_map_actual_tracks(
        {},
        [
            {
                "vehicle_id": "uav1",
                "state": {
                    "connected": True,
                    "position": {"x": 7.0, "y": -3.0, "z": 1.0},
                    "position_frame": "mworks_world",
                },
            }
        ],
        run_id=str(manifest["run_id"]),
        world_frame="mworks_world",
        updated_at=10.0,
    )

    state, retained_tracks = build_live_operator_map_state_or_rejected(
        manifest=manifest,
        map_snapshot=snapshot,
        transport_mode="live_ros1",
        sequence=5,
        received_at_unix_s=1_784_000_300.0,
        source_timestamp_s=42.0,
        playback_state="live",
        playback_time_s=None,
        bag_id="",
        vehicles=[
            {
                "vehicle_id": "uav1",
                "state": {
                    "connected": True,
                    "position": {"x": 1000.0, "y": 0.0, "z": 0.0},
                    "position_frame": "factory_odom",
                },
            }
        ],
        task_paths={
            "expected": {
                "status": "available",
                "semantics": "mission_reference",
                "vehicle_scope": "uav1",
                "source_topic": "/mosim/reference_path",
                "frame_id": "factory_odom",
                "updated_at": 42.0,
                "points": [
                    {"x": 1.0, "y": 1.0, "z": 1.0},
                    {"x": 3.0, "y": 2.0, "z": 1.0},
                ],
            },
            "future": {
                "status": "available",
                "semantics": "planner_sampled_future_trajectory",
                "vehicle_scope": "uav1",
                "source_topic": "/mosim/future_path",
                "frame_id": "factory_odom",
                "updated_at": 42.0,
                "points": [
                    {"x": 2.0, "y": 1.0, "z": 1.0},
                    {"x": 4.0, "y": 3.0, "z": 1.0},
                ],
            },
        },
        actual_tracks=existing_tracks,
        coordinate_evidence=evidence,
    )

    assert state["map_data_status"] == {
        "state": "rejected",
        "reason_code": "operator_map_vehicle_position_invalid",
    }
    assert state["vehicles"] == [{"vehicle_id": "uav1", "state": {"connected": True}}]
    assert state["task_paths"]["expected"]["status"] == "available"
    assert state["task_paths"]["future"]["status"] == "available"
    assert state["task_paths"]["expected"]["frame_id"] == "mworks_world"
    assert state["task_paths"]["future"]["frame_id"] == "mworks_world"
    assert retained_tracks == existing_tracks
    assert state["actual_tracks"] == existing_tracks
    validate_operator_map_state(state, manifest=manifest)


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
    bridge = (QGC_CUSTOM / "src" / "MoSimOperatorBridge.cc").read_text(encoding="utf-8")
    bridge_header = (QGC_CUSTOM / "src" / "MoSimOperatorBridge.h").read_text(encoding="utf-8")
    fly_map = (QGC_CUSTOM / "src" / "FactoryFlyMap.qml").read_text(encoding="utf-8")
    plan_view = (QGC_CUSTOM / "src" / "PlanView.qml").read_text(encoding="utf-8")
    plan_overlay = (QGC_CUSTOM / "src" / "FactoryPlanMapOverlay.qml").read_text(encoding="utf-8")

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
    assert 'readonly property bool mapContractReady' in fly_map
    assert 'readonly property bool mapStateReady: mapContractReady && mapFrameAccepted' in fly_map
    assert 'visible: root.mapContractReady && (root.showExpectedPath || root.showFuturePath)' in fly_map
    assert '飞机和实际轨迹已隐藏' in fly_map
    assert 'qEnvironmentVariable("MOSIM_QGC_ACTIVE_RUN_POINTER")' in bridge
    assert 'normalizedPointer.startsWith(QStringLiteral("Results/"))' in bridge
    assert '实时地图坐标系与证据不匹配' in fly_map
    assert 'function sourcePixelForWorld(worldX, worldY)' in fly_map
    assert 'worldToPixelMatrix' in fly_map
    assert 'image_coordinate_contract' in fly_map
    assert 'function applyOperatorMapViewport()' in plan_view
    assert 'identity === _appliedOperatorMapIdentity' in plan_view
    assert 'function factoryMissionPublicationAllowed()' in plan_view
    assert '任务上传已阻止' in plan_view
    assert 'mapState: (mosimOperator.runtimeTelemetry || ({})).map_state || ({})' in plan_view
    assert 'visible: !factoryPlanMap.visible' in plan_view
    assert 'function worldForImagePixel(pixelX, pixelY)' in plan_overlay
    assert 'function imageWorldBoundsForPixels()' in plan_overlay
    assert 'pixelToWorldMatrix' in plan_overlay
    assert 'required property var mapState' in plan_overlay
    assert 'readonly property bool mapStateReady' in plan_overlay
    assert 'function appendActualTracks()' in plan_overlay
    assert 'function paintTaskPaths(canvas)' in plan_overlay
    assert 'root.vehicleMapPositionValid(vehicle)' in plan_overlay

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
