from __future__ import annotations

import json
from pathlib import Path

from Scripts.ui.prepare_qgc_online_waypoint_audit import (
    DEFAULT_PROFILE_ID,
    DEFAULT_RUNTIME_PROFILE_ID,
    build_coordinate_fixture,
)
from Scripts.ui.runtime_sidecar import _canonical_hash, load_operator_map_snapshot
from src.orchestration.operator_map_replay import validate_coordinate_evidence


ROOT = Path(__file__).resolve().parents[2]


def test_online_waypoint_audit_defaults_select_an_enabled_single_vehicle_factory_profile() -> None:
    profile_catalog = json.loads(
        (ROOT / "Config/profiles/operator_profiles.json").read_text(encoding="utf-8")
    )
    profile = next(item for item in profile_catalog["profiles"] if item["profile_id"] == DEFAULT_PROFILE_ID)
    experiment = json.loads((ROOT / profile["profile_path"]).read_text(encoding="utf-8"))["experiment_profile"]
    runtime_catalog = json.loads(
        (ROOT / "Config/control_platform/runtime_backend_catalog.json").read_text(encoding="utf-8")
    )
    runtime = next(
        item
        for item in runtime_catalog["runtime_profiles"]
        if item["runtime_profile_id"] == DEFAULT_RUNTIME_PROFILE_ID
    )

    assert profile["enabled"] is True
    assert experiment["operator_map_id"] == "factory_l2"
    assert DEFAULT_PROFILE_ID in runtime["experiment_profile_ids"]
    assert runtime["vehicle_counts"] == [1]


def test_online_waypoint_fixture_is_bound_to_the_factory_snapshot() -> None:
    snapshot = load_operator_map_snapshot(
        ROOT / "Config" / "control_platform" / "operator_map_catalog.json",
        "factory_l2",
    )
    manifest = {
        "run_id": "qgc-online-waypoint-audit-test",
        "operator_map_snapshot": snapshot,
        "operator_map_snapshot_hash": _canonical_hash(snapshot),
    }

    evidence = build_coordinate_fixture(manifest)

    assert evidence["source_frame_id"] == "mworks_world"
    assert evidence["target_frame_id"] == "mworks_world"
    assert evidence["transform_target_from_source_4x4"][0][0] == 1.0
    assert validate_coordinate_evidence(
        evidence,
        map_snapshot=snapshot,
        snapshot_hash=manifest["operator_map_snapshot_hash"],
    ) == evidence


def test_online_waypoint_audit_launchers_keep_the_fixture_read_only() -> None:
    runner = (ROOT / "Scripts/ui/run_qgc_online_waypoint_fixture.sh").read_text(encoding="utf-8")
    publisher = (ROOT / "Scripts/ui/publish_qgc_online_waypoint_fixture.py").read_text(encoding="utf-8")
    launcher = (ROOT / "Scripts/ui/start_qgc_online_waypoint_audit.ps1").read_text(encoding="utf-8")
    runtime_launcher = (ROOT / "Scripts/ui/run_flight_console.ps1").read_text(encoding="utf-8")

    assert "--read-only" in runner
    assert "--expected-path-topic /mosim/qgc_audit/expected_path" in runner
    assert "--future-marker-topic /mosim/qgc_audit/future_path" in runner
    assert "--rate-hz 2" in runner
    assert "--max-track-points 240" in runner
    assert "PX4, Gazebo, MAVROS control" in runner
    assert runner.index("source /opt/ros/noetic/setup.bash") < runner.index("set -u")
    assert "trap cleanup EXIT" in runner
    assert "trap 'cleanup; exit 0' INT TERM" in runner
    assert "Refusing to reuse a ROS master already reachable" in runner
    assert runner.index("if rosparam list >/dev/null 2>&1; then") < runner.index('roscore -p "$ros_master_port"')
    assert 'if ! kill -0 "$roscore_pid" 2>/dev/null; then' in runner
    assert 'if [[ "$roscore_ready" != "1" ]] || ! kill -0 "$roscore_pid" 2>/dev/null; then' in runner
    assert 'marker.ns = "B-Spline"' in publisher
    assert 'parser.add_argument("--rate-hz", type=float, default=2.0)' in publisher
    assert 'state.mode = "FIXTURE_READ_ONLY"' in publisher
    assert "MOSIM_QGC_ACTIVE_RUN_POINTER" in launcher
    assert "run_flight_console.ps1" in launcher
    assert "build\\flight-console-qgc-audit\\Release\\MoSimGroundControlAudit.exe" in launcher
    assert "-AuditInstance" in launcher
    assert "MoSimGroundControlAudit" in launcher
    assert "& $runtimeLauncher -Executable $qgcExe -AuditInstance -StartupTimeoutSeconds 15" in launcher
    assert "$quotedFixtureCommand = " in launcher
    assert '"bash", "-lc", $quotedFixtureCommand)' in launcher
    assert '"bash", "-lc", $fixtureCommand)' not in launcher
    assert launcher.index("& $runtimeLauncher") < launcher.index('Start-Process -FilePath "wsl.exe"')
    assert "[switch]$AuditInstance" in runtime_launcher
    assert "build/flight-console-qgc-audit/Release/MoSimGroundControlAudit.exe" in runtime_launcher
    assert 'Get-Process -Name "MoSimGroundControlAudit"' in runtime_launcher

    build_launcher = (ROOT / "Scripts/ui/build_flight_console.ps1").read_text(encoding="utf-8")
    assert "[switch]$AuditInstance" in build_launcher
    assert "MOSIM_QGC_AUDIT_APP_NAME=MoSimGroundControlAudit" in build_launcher
    assert "QGC_CPM_SOURCE_CACHE" in build_launcher
    assert "CPM_geographiclib_SOURCE" in build_launcher
    assert "FETCHCONTENT_SOURCE_DIR_GEOGRAPHICLIB=" in build_launcher
    assert "GeographicLib_SOURCE_DIR:STATIC" in build_launcher
    assert "CPM_PACKAGE_geographiclib_VERSION:INTERNAL=2\\.5" in build_launcher
    assert "Replace('\\', '/')" in build_launcher
    assert "DirectorySeparatorChar" in build_launcher
    assert "AltDirectorySeparatorChar" in build_launcher
    assert "git clone --no-checkout --local" in build_launcher
    assert "geographiclib-r2.5-" in build_launcher
    assert "apply --check" in build_launcher

    bridge = (ROOT / "src/ground_station/qgc/mosim_extension/custom/src/MoSimOperatorBridge.cc").read_text(
        encoding="utf-8"
    )
    fly_map = (ROOT / "src/ground_station/qgc/mosim_extension/custom/src/FactoryFlyMap.qml").read_text(
        encoding="utf-8"
    )
    assert "qgc_received_at_unix_s" in bridge
    assert "mapSequence != _lastMapSequence" in bridge
    assert "futurePathUpdatedAt != _lastFuturePathUpdatedAt" in bridge
    assert "qgc_received_at_unix_s" in fly_map
