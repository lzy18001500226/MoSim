from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import Scripts.sunray.qgc_realtime_goal_bridge as qgc_goal_bridge
from Scripts.sunray.qgc_realtime_goal_bridge import (
    GOAL_REQUEST_SCHEMA,
    WAYPOINT_PLAN_REQUEST_SCHEMA,
    RealtimeGoalBridge,
    atomic_write_json,
    build_live_goal,
    canonical_json_hash,
    normalize_goal_request,
    ros_time_seconds,
    validate_active_pointer,
    validate_request_freshness,
    waypoint_plan_progress,
)
from Scripts.ui.factory_map_coordinates import coordinate_for_world


ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "Config" / "control_platform" / "operator_map_catalog.json"
OPERATOR_PROFILES = ROOT / "Config" / "profiles" / "operator_profiles.json"
RUNTIME_BACKENDS = ROOT / "Config" / "control_platform" / "runtime_backend_catalog.json"
CUSTOM_QGC = ROOT / "apps" / "flight_console" / "mosim" / "custom" / "src"
QGC_DIFF_PROFILE_ID = "px4ctrl_graphical_c99_factory_diff_interactive_goal_v1"
QGC_DIFF_RUNTIME_PROFILE_ID = "sunray_ros1_factory_l2_graphical_px4ctrl_c99_diff_interactive_goal_v1"
QGC_DIFF_OPERATION_ID = "factory_l2_graphical_px4ctrl_c99_diff_interactive_goal"
QGC_REALTIME_PROFILE_ID = "px4ctrl_graphical_c99_factory_qgc_realtime_goal_v1"
QGC_REALTIME_RUNTIME_PROFILE_ID = "sunray_ros1_factory_l2_graphical_px4ctrl_c99_qgc_realtime_goal_v1"
QGC_REALTIME_OPERATION_ID = "factory_l2_graphical_px4ctrl_c99_qgc_realtime_goal"
QGC_REALTIME_EXPERIMENT = ROOT / "Config" / "profiles" / "experiments" / "px4ctrl_graphical_c99_factory_qgc_realtime_goal_v1.json"


def _snapshot() -> dict:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    return catalog["maps"][0]


def _manifest() -> dict:
    snapshot = _snapshot()
    return {
        "run_id": "qgc-live-goal-test",
        "experiment_profile_id": "test_profile",
        "experiment_profile_hash": "test-profile-hash",
        "runtime_profile_id": "test_runtime_profile",
        "operator_map_snapshot": snapshot,
        "operator_map_snapshot_hash": canonical_json_hash(snapshot),
    }


def _request(manifest: dict, *, submitted_at_unix_s: float = 1000.0) -> dict:
    snapshot = manifest["operator_map_snapshot"]
    return {
        "schema": GOAL_REQUEST_SCHEMA,
        "state": "submitted",
        "request_id": "qgc-goal-live-goal-0001",
        "run_id": manifest["run_id"],
        "experiment_profile_id": manifest["experiment_profile_id"],
        "experiment_profile_hash": manifest["experiment_profile_hash"],
        "runtime_profile_id": manifest["runtime_profile_id"],
        "source": "qgc_plan_view",
        "submitted_at_unix_s": submitted_at_unix_s,
        "operator_map": {
            "map_id": snapshot["map_id"],
            "map_version": snapshot["map_version"],
            "asset_sha256": snapshot["asset_sha256"],
            "world_frame": snapshot["world_frame"],
            "coordinate_contract_id": snapshot["coordinate_contract_id"],
            "operator_map_snapshot_hash": manifest["operator_map_snapshot_hash"],
        },
        "goal": {
            "latitude_deg": 47.397742,
            "longitude_deg": 8.545594,
            "qgc_altitude_m": 50.0,
        },
    }


def _waypoint_plan_request(manifest: dict, *, submitted_at_unix_s: float = 1000.0) -> dict:
    request = _request(manifest, submitted_at_unix_s=submitted_at_unix_s)
    first = request.pop("goal")
    request["schema"] = WAYPOINT_PLAN_REQUEST_SCHEMA
    request["source"] = "qgc_mission_waypoint_plan"
    request["waypoints"] = [
        {"sequence": 1, **first},
        {
            "sequence": 2,
            "latitude_deg": first["latitude_deg"] + 0.0001,
            "longitude_deg": first["longitude_deg"] + 0.0001,
            "qgc_altitude_m": first["qgc_altitude_m"],
        },
    ]
    return request


def _identity_evidence(manifest: dict) -> dict:
    snapshot = manifest["operator_map_snapshot"]
    return {
        "source_frame_id": "world",
        "target_frame_id": snapshot["world_frame"],
        "transform_target_from_source_4x4": [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
    }


class _FakePoseStamped:
    def __init__(self) -> None:
        self.header = SimpleNamespace(stamp=None, frame_id="")
        self.pose = SimpleNamespace(
            position=SimpleNamespace(x=0.0, y=0.0, z=0.0),
            orientation=SimpleNamespace(w=0.0),
        )


class _FakePublisher:
    def __init__(self) -> None:
        self.subscriber_count = 0
        self.messages: list[object] = []

    def get_num_connections(self) -> int:
        return self.subscriber_count

    def publish(self, message: object) -> None:
        self.messages.append(message)


class _FakeRospy:
    class Time:
        current = 1001.0

        @staticmethod
        def now() -> float:
            return _FakeRospy.Time.current

    def __init__(self) -> None:
        self.Time.current = 1001.0
        self.publisher = _FakePublisher()
        self.plan_size_publisher = _FakePublisher()
        self.publisher_options: dict[str, object] = {}
        self.subscribers: dict[str, object] = {}

    def Publisher(
        self,
        topic: str,
        message_type: type[_FakePoseStamped],
        *,
        queue_size: int,
        latch: bool,
    ) -> _FakePublisher:
        if topic == "/mosim/goal4/interactive_goal_waypoint_count":
            return self.plan_size_publisher
        self.publisher_options = {
            "topic": topic,
            "message_type": message_type,
            "queue_size": queue_size,
            "latch": latch,
        }
        return self.publisher

    def Subscriber(
        self,
        topic: str,
        message_type: object,
        callback: object,
        *,
        queue_size: int,
    ) -> object:
        self.subscribers[topic] = callback
        return object()

    def emit_ready(self, topic: str, ready: bool) -> None:
        callback = self.subscribers[topic]
        callback(SimpleNamespace(data=ready))  # type: ignore[operator]


class _FakeBool:
    pass


class _FakeUInt16:
    def __init__(self) -> None:
        self.data = 0


def _bridge_args(tmp_path: Path) -> SimpleNamespace:
    return SimpleNamespace(
        run_dir=tmp_path,
        coordinate_evidence=tmp_path / "OPERATOR_MAP_COORDINATE_EVIDENCE.json",
        active_pointer=tmp_path / "qgc_active_run.json",
        goal_topic="/move_base_simple/goal",
        goal_frame="world",
        mission_ready_topic="/mosim/goal4/interactive_goal_ready",
        waypoint_plan_size_topic="/mosim/goal4/interactive_goal_waypoint_count",
        ground_z_m=0.0,
        poll_hz=10.0,
        max_request_age_s=5.0,
        max_waypoint_plan_duration_s=600.0,
        max_waypoint_plan_wall_stall_s=120.0,
        max_future_skew_s=1.0,
    )


def test_qgc_goal_is_converted_to_the_same_world_xy_as_the_factory_map() -> None:
    manifest = _manifest()
    snapshot = manifest["operator_map_snapshot"]
    coordinate = coordinate_for_world(
        snapshot["simulation_geodetic_anchor"],
        32.5,
        -11.25,
        altitude_m=50.0,
    )
    request = _request(manifest)
    request["goal"] = {
        "latitude_deg": coordinate["latitude_deg"],
        "longitude_deg": coordinate["longitude_deg"],
        "qgc_altitude_m": coordinate["altitude_m"],
    }

    outgoing = build_live_goal(
        request,
        manifest=manifest,
        coordinate_evidence=_identity_evidence(manifest),
        goal_frame="world",
        ground_z_m=0.0,
    )

    assert outgoing["frame_id"] == "world"
    assert outgoing["position"]["x"] == pytest.approx(32.5, abs=1.0e-6)
    assert outgoing["position"]["y"] == pytest.approx(-11.25, abs=1.0e-6)
    assert outgoing["position"]["z"] == 0.0
    assert outgoing["qgc_goal"]["qgc_altitude_m"] == 50.0


def test_published_qgc_realtime_goal_profile_passes_static_contract_validation() -> None:
    completed = subprocess.run(
        [sys.executable, "Scripts/quality/check_experiment_profile.py", str(QGC_REALTIME_EXPERIMENT)],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_qgc_goal_request_requires_the_exact_frozen_map_identity() -> None:
    manifest = _manifest()
    request = _request(manifest)
    request["operator_map"]["map_id"] = "another_map"

    with pytest.raises(ValueError, match="qgc_realtime_goal_request_map_identity_mismatch"):
        normalize_goal_request(request, manifest=manifest)


def test_qgc_waypoint_plan_rejects_targets_outside_the_frozen_task_boundary() -> None:
    manifest = _manifest()
    request = _waypoint_plan_request(manifest)
    anchor = manifest["operator_map_snapshot"]["simulation_geodetic_anchor"]
    outside = coordinate_for_world(anchor, 100.0, 0.0, altitude_m=50.0)
    request["waypoints"][1].update(
        {
            "latitude_deg": outside["latitude_deg"],
            "longitude_deg": outside["longitude_deg"],
            "qgc_altitude_m": outside["altitude_m"],
        }
    )

    with pytest.raises(ValueError, match="qgc_realtime_goal_request_outside_task_boundary"):
        normalize_goal_request(request, manifest=manifest)


def test_qgc_goal_request_is_fresh_and_never_reused_as_a_replay_input() -> None:
    request = _request(_manifest(), submitted_at_unix_s=1000.0)

    assert validate_request_freshness(
        request,
        now_unix_s=1004.9,
        max_request_age_s=5.0,
        max_future_skew_s=1.0,
    ) == pytest.approx(4.9)
    with pytest.raises(ValueError, match="qgc_realtime_goal_request_stale"):
        validate_request_freshness(
            request,
            now_unix_s=1005.1,
            max_request_age_s=5.0,
            max_future_skew_s=1.0,
        )


def test_waypoint_plan_progress_uses_ros_sim_time_and_detects_a_stalled_clock() -> None:
    slow = waypoint_plan_progress(
        started_sim_time_s=100.0,
        current_sim_time_s=291.0,
        started_wall_time_s=1000.0,
        current_wall_time_s=1600.0,
        last_sim_time_s=100.0,
        last_sim_progress_wall_time_s=1000.0,
        max_sim_duration_s=600.0,
        max_wall_stall_s=120.0,
    )
    assert slow["state"] == "running"
    assert slow["actual_rtf"] == pytest.approx(191.0 / 600.0)

    stalled = waypoint_plan_progress(
        started_sim_time_s=100.0,
        current_sim_time_s=100.0,
        started_wall_time_s=1000.0,
        current_wall_time_s=1120.0,
        last_sim_time_s=100.0,
        last_sim_progress_wall_time_s=1000.0,
        max_sim_duration_s=600.0,
        max_wall_stall_s=120.0,
    )
    assert stalled["state"] == "sim_clock_stalled"

    expired = waypoint_plan_progress(
        started_sim_time_s=100.0,
        current_sim_time_s=700.1,
        started_wall_time_s=1000.0,
        current_wall_time_s=2600.0,
        last_sim_time_s=100.0,
        last_sim_progress_wall_time_s=1000.0,
        max_sim_duration_s=600.0,
        max_wall_stall_s=120.0,
    )
    assert expired["state"] == "sim_duration_exceeded"
    assert ros_time_seconds(12.5, "test") == pytest.approx(12.5)


def test_qgc_goal_requires_an_active_running_pointer() -> None:
    manifest = _manifest()
    pointer = {
        "schema": "mosim.qgc_active_run_pointer.v1",
        "state": "replaying",
        "run_id": manifest["run_id"],
        "run_directory": f"Results/runs/{manifest['run_id']}",
        "experiment_profile_id": manifest["experiment_profile_id"],
        "experiment_profile_hash": manifest["experiment_profile_hash"],
        "runtime_profile_id": manifest["runtime_profile_id"],
    }

    with pytest.raises(ValueError, match="qgc_realtime_goal_active_run_not_running"):
        validate_active_pointer(pointer, manifest=manifest)


def test_pending_qgc_goal_is_revalidated_before_live_ros_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = _manifest()
    context = {"manifest": manifest, "coordinate_evidence": _identity_evidence(manifest), "coordinate_evidence_sha256": "evidence"}
    calls: list[str] = []

    def _load_context(**_: object) -> dict:
        calls.append("load")
        if len(calls) == 3:
            raise ValueError("qgc_realtime_goal_active_run_not_running")
        return context

    monkeypatch.setattr(qgc_goal_bridge, "load_runtime_context", _load_context)
    monkeypatch.setattr(qgc_goal_bridge.time, "time", lambda: 1001.0)
    rospy = _FakeRospy()
    bridge = RealtimeGoalBridge(args=_bridge_args(tmp_path), rospy=rospy, pose_stamped_type=_FakePoseStamped)
    atomic_write_json(tmp_path / "operator_goal" / "REQUEST.json", _request(manifest))

    bridge._read_new_request()
    rospy.publisher.subscriber_count = 1
    bridge._forward_pending_request()

    status = json.loads((tmp_path / "operator_goal" / "STATUS.json").read_text(encoding="utf-8"))
    assert calls == ["load", "load", "load"]
    assert status["state"] == "rejected"
    assert status["reason_code"] == "qgc_realtime_goal_active_run_not_running"
    assert rospy.publisher.messages == []
    assert rospy.publisher_options["latch"] is False


def test_new_qgc_goal_forwards_once_after_a_live_subscriber_is_present(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = _manifest()
    context = {"manifest": manifest, "coordinate_evidence": _identity_evidence(manifest), "coordinate_evidence_sha256": "evidence"}
    monkeypatch.setattr(qgc_goal_bridge, "load_runtime_context", lambda **_: context)
    monkeypatch.setattr(qgc_goal_bridge.time, "time", lambda: 1001.0)
    rospy = _FakeRospy()
    bridge = RealtimeGoalBridge(args=_bridge_args(tmp_path), rospy=rospy, pose_stamped_type=_FakePoseStamped)
    atomic_write_json(tmp_path / "operator_goal" / "REQUEST.json", _request(manifest))

    bridge._read_new_request()
    bridge._forward_pending_request()
    awaiting = json.loads((tmp_path / "operator_goal" / "STATUS.json").read_text(encoding="utf-8"))
    assert awaiting["state"] == "awaiting_subscriber"

    rospy.publisher.subscriber_count = 1
    bridge._forward_pending_request()
    bridge._forward_pending_request()

    status = json.loads((tmp_path / "operator_goal" / "STATUS.json").read_text(encoding="utf-8"))
    assert status["state"] == "forwarded"
    assert status["details"]["transport"] == "live_ros1"
    assert status["details"]["goal_topic"] == "/move_base_simple/goal"
    assert len(rospy.publisher.messages) == 1
    assert rospy.publisher.messages[0].header.frame_id == "world"


def test_qgc_waypoint_plan_releases_one_goal_per_live_ready_cycle(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = _manifest()
    context = {"manifest": manifest, "coordinate_evidence": _identity_evidence(manifest), "coordinate_evidence_sha256": "evidence"}
    monkeypatch.setattr(qgc_goal_bridge, "load_runtime_context", lambda **_: context)
    monkeypatch.setattr(qgc_goal_bridge.time, "time", lambda: 1001.0)
    rospy = _FakeRospy()
    bridge = RealtimeGoalBridge(
        args=_bridge_args(tmp_path),
        rospy=rospy,
        pose_stamped_type=_FakePoseStamped,
        bool_type=_FakeBool,
        uint16_type=_FakeUInt16,
    )
    rospy.publisher.subscriber_count = 1
    rospy.plan_size_publisher.subscriber_count = 1
    bridge._refresh_idle_readiness()
    rospy.emit_ready("/mosim/goal4/interactive_goal_ready", True)
    atomic_write_json(tmp_path / "operator_goal" / "REQUEST.json", _waypoint_plan_request(manifest))

    bridge._read_new_request()
    bridge._forward_pending_request()
    first = json.loads((tmp_path / "operator_goal" / "STATUS.json").read_text(encoding="utf-8"))
    assert first["state"] == "forwarded"
    assert first["details"]["request_kind"] == "waypoint_plan"
    assert first["details"]["forwarded_waypoint_count"] == 1
    assert len(rospy.publisher.messages) == 1
    assert len(rospy.plan_size_publisher.messages) == 1
    assert rospy.plan_size_publisher.messages[0].data == 2

    bridge._forward_pending_request()
    rospy.emit_ready("/mosim/goal4/interactive_goal_ready", True)
    bridge._forward_pending_request()
    waiting = json.loads((tmp_path / "operator_goal" / "STATUS.json").read_text(encoding="utf-8"))
    assert waiting["state"] == "awaiting_mission_ready"
    assert len(rospy.publisher.messages) == 1

    rospy.emit_ready("/mosim/goal4/interactive_goal_ready", False)
    rospy.emit_ready("/mosim/goal4/interactive_goal_ready", True)
    bridge._forward_pending_request()
    final = json.loads((tmp_path / "operator_goal" / "STATUS.json").read_text(encoding="utf-8"))
    assert final["state"] == "forwarded"
    assert final["details"]["forwarded_waypoint_count"] == 2
    assert final["details"]["goal"]["waypoint_index"] == 1
    assert len(rospy.publisher.messages) == 2
    assert len(rospy.plan_size_publisher.messages) == 1


def test_stalled_qgc_waypoint_plan_cancels_the_mission_sequence_before_retry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = _manifest()
    context = {"manifest": manifest, "coordinate_evidence": _identity_evidence(manifest), "coordinate_evidence_sha256": "evidence"}
    now = [1001.0]
    monkeypatch.setattr(qgc_goal_bridge, "load_runtime_context", lambda **_: context)
    monkeypatch.setattr(qgc_goal_bridge.time, "time", lambda: now[0])
    rospy = _FakeRospy()
    bridge = RealtimeGoalBridge(
        args=_bridge_args(tmp_path),
        rospy=rospy,
        pose_stamped_type=_FakePoseStamped,
        bool_type=_FakeBool,
        uint16_type=_FakeUInt16,
    )
    rospy.publisher.subscriber_count = 1
    rospy.plan_size_publisher.subscriber_count = 1
    bridge._refresh_idle_readiness()
    rospy.emit_ready("/mosim/goal4/interactive_goal_ready", True)
    atomic_write_json(tmp_path / "operator_goal" / "REQUEST.json", _waypoint_plan_request(manifest))

    bridge._read_new_request()
    bridge._forward_pending_request()
    rospy.emit_ready("/mosim/goal4/interactive_goal_ready", False)
    now[0] = 1121.0
    bridge._forward_pending_request()

    rejected = json.loads((tmp_path / "operator_goal" / "STATUS.json").read_text(encoding="utf-8"))
    assert rejected["state"] == "rejected"
    assert rejected["reason_code"] == "qgc_realtime_waypoint_plan_sim_clock_stalled"
    assert rejected["details"]["waypoint_plan_cancel_published"] is True
    assert rejected["details"]["sim_clock_stall_s"] == pytest.approx(120.0)
    assert [message.data for message in rospy.plan_size_publisher.messages] == [2, 0]

    rospy.emit_ready("/mosim/goal4/interactive_goal_ready", True)
    bridge._refresh_idle_readiness()
    ready = json.loads((tmp_path / "operator_goal" / "STATUS.json").read_text(encoding="utf-8"))
    assert ready["state"] == "ready"
    assert ready["reason_code"] == "waiting_for_new_qgc_goal_after_rejection"

    retry = _waypoint_plan_request(manifest, submitted_at_unix_s=1121.0)
    retry["request_id"] = "qgc-goal-live-goal-0002"
    atomic_write_json(tmp_path / "operator_goal" / "REQUEST.json", retry)
    bridge._read_new_request()
    bridge._forward_pending_request()

    assert [message.data for message in rospy.plan_size_publisher.messages] == [2, 0, 2]
    assert len(rospy.publisher.messages) == 2


def test_slow_qgc_waypoint_plan_uses_sim_time_after_the_first_release(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = _manifest()
    context = {"manifest": manifest, "coordinate_evidence": _identity_evidence(manifest), "coordinate_evidence_sha256": "evidence"}
    now = [1001.0]
    monkeypatch.setattr(qgc_goal_bridge, "load_runtime_context", lambda **_: context)
    monkeypatch.setattr(qgc_goal_bridge.time, "time", lambda: now[0])
    rospy = _FakeRospy()
    bridge = RealtimeGoalBridge(
        args=_bridge_args(tmp_path),
        rospy=rospy,
        pose_stamped_type=_FakePoseStamped,
        bool_type=_FakeBool,
        uint16_type=_FakeUInt16,
    )
    rospy.publisher.subscriber_count = 1
    rospy.plan_size_publisher.subscriber_count = 1
    bridge._refresh_idle_readiness()
    rospy.emit_ready("/mosim/goal4/interactive_goal_ready", True)
    atomic_write_json(tmp_path / "operator_goal" / "REQUEST.json", _waypoint_plan_request(manifest))

    bridge._read_new_request()
    bridge._forward_pending_request()
    rospy.emit_ready("/mosim/goal4/interactive_goal_ready", False)
    rospy.emit_ready("/mosim/goal4/interactive_goal_ready", True)
    now[0] = 1601.0
    rospy.Time.current = 1192.0
    bridge._forward_pending_request()

    status = json.loads((tmp_path / "operator_goal" / "STATUS.json").read_text(encoding="utf-8"))
    assert status["state"] == "forwarded"
    assert status["details"]["forwarded_waypoint_count"] == 2
    assert status["details"]["actual_rtf"] == pytest.approx(191.0 / 600.0)


def test_bridge_spin_uses_wall_clock_sleep_when_the_sim_clock_can_stall(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = _manifest()
    context = {
        "manifest": manifest,
        "coordinate_evidence": _identity_evidence(manifest),
        "coordinate_evidence_sha256": "evidence",
    }
    monkeypatch.setattr(qgc_goal_bridge, "load_runtime_context", lambda **_: context)
    rospy = _FakeRospy()
    bridge = RealtimeGoalBridge(
        args=_bridge_args(tmp_path),
        rospy=rospy,
        pose_stamped_type=_FakePoseStamped,
    )
    iterations = iter((False, True))
    rospy.is_shutdown = lambda: next(iterations)  # type: ignore[attr-defined]
    calls: list[str] = []
    sleeps: list[float] = []
    monkeypatch.setattr(bridge, "_refresh_idle_readiness", lambda: calls.append("ready"))
    monkeypatch.setattr(bridge, "_read_new_request", lambda: calls.append("read"))
    monkeypatch.setattr(bridge, "_forward_pending_request", lambda: calls.append("forward"))
    monkeypatch.setattr(qgc_goal_bridge.time, "sleep", lambda interval_s: sleeps.append(interval_s))

    bridge.spin()

    assert calls == ["ready", "read", "forward"]
    assert sleeps == [pytest.approx(0.1)]


def test_qgc_waypoint_plan_requires_a_live_plan_size_subscriber(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = _manifest()
    context = {"manifest": manifest, "coordinate_evidence": _identity_evidence(manifest), "coordinate_evidence_sha256": "evidence"}
    monkeypatch.setattr(qgc_goal_bridge, "load_runtime_context", lambda **_: context)
    rospy = _FakeRospy()
    bridge = RealtimeGoalBridge(
        args=_bridge_args(tmp_path),
        rospy=rospy,
        pose_stamped_type=_FakePoseStamped,
        bool_type=_FakeBool,
        uint16_type=_FakeUInt16,
    )

    rospy.publisher.subscriber_count = 1
    bridge._refresh_idle_readiness()
    awaiting = json.loads((tmp_path / "operator_goal" / "STATUS.json").read_text(encoding="utf-8"))
    assert awaiting["state"] == "awaiting_subscriber"
    assert awaiting["reason_code"] == "qgc_realtime_goal_waypoint_plan_size_subscriber_missing"

    rospy.plan_size_publisher.subscriber_count = 1
    bridge._refresh_idle_readiness()
    ready = json.loads((tmp_path / "operator_goal" / "STATUS.json").read_text(encoding="utf-8"))
    assert ready["state"] == "ready"


def test_bridge_waits_for_the_planner_subscriber_before_marking_plan_goal_ready(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest = _manifest()
    context = {"manifest": manifest, "coordinate_evidence": _identity_evidence(manifest), "coordinate_evidence_sha256": "evidence"}
    monkeypatch.setattr(qgc_goal_bridge, "load_runtime_context", lambda **_: context)
    rospy = _FakeRospy()
    bridge = RealtimeGoalBridge(args=_bridge_args(tmp_path), rospy=rospy, pose_stamped_type=_FakePoseStamped)

    awaiting = json.loads((tmp_path / "operator_goal" / "STATUS.json").read_text(encoding="utf-8"))
    assert awaiting["state"] == "awaiting_subscriber"

    rospy.publisher.subscriber_count = 1
    bridge._refresh_idle_readiness()

    ready = json.loads((tmp_path / "operator_goal" / "STATUS.json").read_text(encoding="utf-8"))
    assert ready["state"] == "ready"
    assert ready["details"]["goal_topic"] == "/move_base_simple/goal"


def test_qgc_and_ros_sources_keep_the_goal_lane_live_and_planner_only() -> None:
    bridge = (ROOT / "Scripts" / "sunray" / "qgc_realtime_goal_bridge.py").read_text(encoding="utf-8")
    qml = (CUSTOM_QGC / "PlanView.qml").read_text(encoding="utf-8")
    qgc_bridge = (CUSTOM_QGC / "MoSimOperatorBridge.cc").read_text(encoding="utf-8")
    factory_overlay = (CUSTOM_QGC / "FactoryPlanMapOverlay.qml").read_text(encoding="utf-8")

    assert 'default="/move_base_simple/goal"' in bridge
    assert "latch=False" in bridge
    assert "get_num_connections()" in bridge
    assert "qgc_realtime_goal_request_stale" in bridge
    assert "rosbag.Bag" not in bridge
    assert "--bag" not in bridge
    assert "submitRealtimePlanningGoal" in qml
    assert "submitRealtimeWaypointPlan" in qml
    assert "realtimeMissionWaypoints" in qml
    assert "Submit Waypoints" in qml
    assert "_realtimePlanningGoalOnClick" in qml
    assert "Plan Goal 必须位于青色任务边界内" in qml
    assert "Submit Waypoints 只接受青色任务边界内的航点" in qml
    assert "worldForMapPoint" in factory_overlay
    assert "worldPointInExplorationBoundary" in factory_overlay
    assert "copyRealtimePlanningGoalBridgeCommand" not in qml
    assert "QSaveFile" in qgc_bridge
    assert "operator_goal/REQUEST.json" in qgc_bridge
    assert "realtimePlanningGoalReady" in qgc_bridge
    assert 'runtimeBackendForProfile(\n        profile.value(QStringLiteral("profile_id")).toString())' in qgc_bridge
    assert "_activePointerRelativePath" in qgc_bridge
    assert "OPERATOR_MAP_COORDINATE_EVIDENCE.json" in qgc_bridge
    assert 'coordinateEvidence.value(QStringLiteral("source_frame_id")).toString() == goalFrame' in qgc_bridge
    assert 'coordinateEvidence.value(QStringLiteral("target_frame_id")).toString() == mapFrame' in qgc_bridge
    assert 'QStringLiteral("realtime_goal")' in qgc_bridge
    assert 'QStringLiteral("qgc_plan_view")' in qgc_bridge
    assert 'QStringLiteral("qgc_mission_waypoint_plan")' in qgc_bridge
    assert "mosim.qgc_realtime_goal_request.v2" in qgc_bridge
    assert 'if (state == QStringLiteral("ready")) {' in qgc_bridge
    assert 'state == QStringLiteral("ready") || state == QStringLiteral("rejected")' not in qgc_bridge
    assert "runtimeBackendForProfile(_selectedProfileId)" not in qgc_bridge
    assert "QProcess" not in qgc_bridge
    assert "awaiting_mission_ready" in bridge
    assert "mission_ready_topic" in bridge
    assert "waypoint_plan_size_topic" in bridge
    assert "qgc_realtime_goal_waypoint_plan_size_subscriber_missing" in bridge
    assert "qgc_realtime_waypoint_plan_ros_published" in bridge
    assert "waypoint_plan_cancel_published" in bridge
    assert 'message.data = 0' in bridge
    assert "forwardedWaypointCount >= waypointCount" in qgc_bridge


def test_qgc_interactive_mission_waits_for_px4ctrl_takeoff_subscriber() -> None:
    mission = (ROOT / "Scripts" / "sunray" / "px4ctrl_ego_single_mission_node.py").read_text(encoding="utf-8")
    wait_for_ready = mission.split("    def wait_for_ready(self) -> bool:\n", 1)[1].split("\n    def ", 1)[0]

    assert "self.takeoff_land_pub.get_num_connections() > 0" in wait_for_ready
    interactive_loop = mission.split("        if self.args.interactive_goal_review:\n", 1)[1].split(
        "\n        self.phase = \"ego_triggered\"", 1
    )[0]
    assert "self.set_interactive_goal_ready(False, repeats=1)" in interactive_loop


def test_qgc_diff_goal_keeps_world_evaluation_separate_from_local_control() -> None:
    mission = (ROOT / "Scripts" / "sunray" / "px4ctrl_ego_single_mission_node.py").read_text(encoding="utf-8")
    runner = (ROOT / "Scripts" / "sunray" / "run_px4ctrl_ego_single_gate.sh").read_text(encoding="utf-8")
    sidecar = (ROOT / "Scripts" / "ui" / "runtime_sidecar.py").read_text(encoding="utf-8")

    assert "self.last_path_odom_row" in mission
    assert "def interactive_goal_state_row" in mission
    assert 'goal_frame_id = str(goal.get("frame_id") or self.args.path_frame)' in mission
    assert "state_row = self.interactive_goal_state_row(goal_frame_id" in mission
    assert "interactive_goal_state_frame_mismatch" in mission
    assert "snapshot = self.interactive_goal_snapshot()" in mission
    assert "control_snapshot = self.last_odom" in mission
    assert 'parser.add_argument("--control-frame", default="map")' in mission
    world_odom_bridge = runner.split("_direction:=local_to_world", 1)[1].split("PIDS+=(\"$!\")", 1)[0]
    local_command_bridge = runner.split("_direction:=world_to_local", 1)[1].split(
        "DIFF_GOAL4_COMMAND_BRIDGE_PID", 1
    )[0]
    assert "_output_frame_id:=world" in world_odom_bridge
    assert "_output_frame_id:=map" in local_command_bridge
    assert '"position_frame": str(msg.header.frame_id or "")' in sidecar
    assert "position_command_frame_mismatch" in sidecar


def test_qgc_realtime_goal_profiles_are_bound_to_the_live_goal_wrapper() -> None:
    profiles = json.loads(OPERATOR_PROFILES.read_text(encoding="utf-8"))["profiles"]
    backends = json.loads(RUNTIME_BACKENDS.read_text(encoding="utf-8"))["runtime_profiles"]
    profile = next(item for item in profiles if item["profile_id"] == QGC_DIFF_PROFILE_ID)
    backend = next(item for item in backends if item["runtime_profile_id"] == QGC_DIFF_RUNTIME_PROFILE_ID)
    realtime_profile = next(item for item in profiles if item["profile_id"] == QGC_REALTIME_PROFILE_ID)
    realtime_backend = next(
        item for item in backends if item["runtime_profile_id"] == QGC_REALTIME_RUNTIME_PROFILE_ID
    )
    wrapper = (ROOT / backend["project_script"]).read_text(encoding="utf-8")

    assert profile["enabled"] is False
    assert "非交付入口" in profile["label"]
    assert profile["operator_mode"] == "mission_adapter"
    assert backend["experiment_profile_ids"] == [QGC_DIFF_PROFILE_ID]
    assert backend["operation_id"] == QGC_DIFF_OPERATION_ID
    assert backend["operator_invocation"]["arguments"] == ["interactive_goal"]
    assert backend["project_script"] == "Scripts/sunray/run_qgc_diff_realtime_goal_gate.sh"
    assert backend["realtime_goal"] == {
        "input": "qgc_plan_view",
        "goal_topic": "/move_base_simple/goal",
        "goal_frame": "world",
    }
    assert realtime_profile["enabled"] is True
    assert realtime_profile["label"] == "QGC实时目标单机规划闭环"
    assert realtime_backend["experiment_profile_ids"] == [QGC_REALTIME_PROFILE_ID]
    assert realtime_backend["operation_id"] == QGC_REALTIME_OPERATION_ID
    assert realtime_backend["operator_invocation"]["arguments"] == ["qgc_realtime_goal"]
    assert realtime_backend["result_gate"] == "QGC_REALTIME_GOAL_RUNTIME_STATUS.json"
    assert realtime_backend["realtime_goal"] == backend["realtime_goal"]
    assert 'RUNTIME_STATUS_FILE_NAME=QGC_DIFF_REALTIME_GOAL_RUNTIME_STATUS.json' in wrapper
    assert 'RUNTIME_STATUS_FILE_NAME=QGC_REALTIME_GOAL_RUNTIME_STATUS.json' in wrapper
    assert 'RUNTIME_STATUS_FILE="$RESULT_DIR/$RUNTIME_STATUS_FILE_NAME"' in wrapper
    assert 'ACCEPTANCE_FILE="$RESULT_DIR/$ACCEPTANCE_FILE_NAME"' in wrapper
    assert "prepare_local_ros1_runtime_overlay.sh" in wrapper
    assert 'RUNTIME_OVERLAY_WORKSPACE="$PROJECT_ROOT/build/ros1/runtime_overlays/$RUN_ID"' in wrapper
    assert "qgc_diff_realtime_goal_runtime_overlay_prepare_failed" in wrapper
    assert 'ln -s "$LOCAL_ROS1_DEVEL" "$RUNTIME_OVERLAY_WORKSPACE/devel"' in wrapper
    assert "qgc_diff_realtime_goal_runtime_overlay_devel_link_mismatch" in wrapper
    assert 'QGC_DIFF_FASTLIO_WS="${QGC_DIFF_FASTLIO_WS:-$PROJECT_ROOT/build/ros1/qgc_diff_fastlio_ws}"' in wrapper
    assert "removed_stale_local_fastlio_link" in wrapper
    assert 'FAST_LIO) fastlio_source="$PROJECT_ROOT/src/perception/fast_lio"' in wrapper
    assert 'livox_ros_driver_compat) fastlio_source="$PROJECT_ROOT/src/perception/livox_ros_driver_compat"' in wrapper
    assert "created_fastlio_source_link" in wrapper
    assert "created_fastlio_catkin_link" in wrapper
    assert 'FASTLIO_WS="$QGC_DIFF_FASTLIO_WS"' in wrapper
    assert "qgc_diff_realtime_goal_fastlio_workspace_guard_failed" in wrapper
    assert 'QGC_DIFF_FASTLIO_BUILD_TIMEOUT_S="${QGC_DIFF_FASTLIO_BUILD_TIMEOUT_S:-900}"' in wrapper
    assert "qgc_diff_realtime_goal_fastlio_prebuild_failed" in wrapper
    assert 'QGC_DIFF_FASTLIO_START_TIMEOUT_S="${QGC_DIFF_FASTLIO_START_TIMEOUT_S:-150}"' in wrapper
    assert 'FASTLIO_START_TIMEOUT_S="$QGC_DIFF_FASTLIO_START_TIMEOUT_S"' in wrapper
    assert 'QGC_DIFF_FASTLIO_SENSOR_START_TIMEOUT_S="${QGC_DIFF_FASTLIO_SENSOR_START_TIMEOUT_S:-300}"' in wrapper
    assert 'FASTLIO_SENSOR_START_TIMEOUT_S="$QGC_DIFF_FASTLIO_SENSOR_START_TIMEOUT_S"' in wrapper
    assert "fastlio_package_audit.txt" in wrapper
    assert "fastlio_sensor_phase_extended" in wrapper
    assert "qgc_fastlio_sensor_phase.txt" in wrapper
    assert "start_qgc_roscore" in wrapper
    assert "qgc_diff_realtime_goal_roscore_start_failed" in wrapper
    assert wrapper.index("start_qgc_roscore") < wrapper.index("run_inner_gate\n)")
    assert "trap '' HUP" in wrapper
    assert "trap 'exit 130' INT" in wrapper
    assert "trap 'exit 143' TERM" in wrapper
    assert "(\n  # Preserve the parent's ignored SIGHUP disposition" in wrapper
    assert "  trap '' HUP\n  run_inner_gate\n) >" in wrapper
    assert "PRESERVE_EXISTING_ROSCORE=true" in wrapper
    assert "qgc_diff_realtime_goal_active_pointer_activate_failed" in wrapper
    assert wrapper.index("--activate-active") < wrapper.index("if ! wait_for_interactive_chain")
    assert "READINESS_TIMEOUT_S=300" in wrapper
    assert "STARTUP_TIMEOUT_S=300" in wrapper
    assert "QGC_DIFF_PLANNER_PARAM_TIMEOUT_S=30" in wrapper
    assert "wait_for_planner_launch" in wrapper
    assert "qgc_diff_realtime_goal_planner_start_not_ready" in wrapper
    assert 'OPEN_RVIZ="$OPEN_RVIZ_FOR_PHASE"' in wrapper
    assert "OPEN_RVIZ_FOR_PHASE=false" in wrapper
    assert "OPEN_RVIZ_FOR_PHASE=true" in wrapper
    assert "PX4CTRL_HOVER_PERCENTAGE=0.294" in wrapper
    assert "FASTLIO_FILTER_SIZE_SURF=0.5" in wrapper
    assert "FASTLIO_FILTER_SIZE_MAP=0.5" in wrapper
    assert "DIFF_CMD_SMOOTH_ENABLE=true" in wrapper
    assert "DIFF_CMD_MOTION_TIME_BASIS=ros_sim_time" in wrapper
    assert "DIFF_CMD_MAX_VELOCITY_MPS=0.6" in wrapper
    assert "DIFF_CMD_MAX_ACCELERATION_MPS2=0.8" in wrapper
    assert "DIFF_CMD_MAX_XY_TARGET_DISTANCE_FROM_ODOM_M=0.5" in wrapper
    assert "DIFF_EXECUTE_MAX_TRUTH_ODOM_Z_ERROR_M=0.35" in wrapper
    assert 'FASTLIO_FILTER_SIZE_SURF="$FASTLIO_FILTER_SIZE_SURF"' in wrapper
    assert 'FASTLIO_FILTER_SIZE_MAP="$FASTLIO_FILTER_SIZE_MAP"' in wrapper
    assert "SUNRAY_GPS_SENSOR_MODE=removed" in wrapper
    assert "PX4CTRL_ENABLE_FASTLIO_EKF_FUSION=true" in wrapper
    assert "PX4CTRL_EKF2_EV_CTRL_OVERRIDE=15" in wrapper
    assert "PX4CTRL_EKF2_HGT_REF_OVERRIDE=3" in wrapper
    assert "FASTLIO_ALIGNMENT_Z_SOURCE=truth" in wrapper
    assert "FASTLIO_ALIGNMENT_REQUIRED=true" in wrapper
    assert "REVIEW_START_FASTLIO=true" in wrapper
    assert 'QGC_DIFF_PX4_SIM_SPEED_FACTOR="${QGC_DIFF_PX4_SIM_SPEED_FACTOR:-1.0}"' in wrapper
    assert 'PX4_SIM_SPEED_FACTOR="$QGC_DIFF_PX4_SIM_SPEED_FACTOR"' in wrapper
    assert 'QGC_DIFF_TAKEOFF_TIMEOUT_S="${QGC_DIFF_TAKEOFF_TIMEOUT_S:-90}"' in wrapper
    assert 'GOAL4_TAKEOFF_TIMEOUT_S="$QGC_DIFF_TAKEOFF_TIMEOUT_S"' in wrapper
    assert "qgc_diff_realtime_goal_inner_runtime_exited" in wrapper
    assert "DIFF_PUBLISH_HOVER_DURING_TAKEOFF=true" in wrapper
    assert "DIFF_PUBLISH_HOVER_DURING_TAKEOFF_DELAY_S=0.5" in wrapper
    assert "DIFF_GOAL4_COMMON_WORLD_FRAME=true" in wrapper
    assert "DIFF_CLICK_READY_Z_TOL=0.30" in wrapper
    assert "QGC_DIFF_MAP_SIZE_X=32.0" in wrapper
    assert "QGC_DIFF_MAP_SIZE_Y=44.0" in wrapper
    assert "QGC_DIFF_MAP_SIZE_Z=2.5" in wrapper
    assert 'EGO_MAP_SIZE_X="$QGC_DIFF_MAP_SIZE_X"' in wrapper
    assert 'EGO_MAP_SIZE_Y="$QGC_DIFF_MAP_SIZE_Y"' in wrapper
    assert 'EGO_MAP_SIZE_Z="$QGC_DIFF_MAP_SIZE_Z"' in wrapper
    assert "verify_qgc_planner_map_extent" in wrapper
    assert "QGC_DIFF_PLANNER_MAP_EXTENT_GATE.json" in wrapper
    assert "qgc_diff_realtime_goal_planner_map_extent_mismatch" in wrapper
    assert '"observed_from": "rosparam"' in wrapper
    assert '["rosparam", "get", param_path]' in wrapper
    assert "REASON_PREFIX=qgc_diff_realtime_goal" in wrapper
    assert "REASON_PREFIX=qgc_realtime_goal" in wrapper
    assert 'f"{reason_prefix}_planner_map_param_timeout:"' in wrapper
    assert "time.monotonic() + timeout_s" in wrapper
    assert 'QGC_DIFF_AUTO_PASS_GOAL_COUNT="${QGC_DIFF_AUTO_PASS_GOAL_COUNT:-1}"' in wrapper
    assert 'QGC_DIFF_FINAL_HOVER_HOLD_S="${QGC_DIFF_FINAL_HOVER_HOLD_S:-8.0}"' in wrapper
    assert "verify_qgc_goal_acceptance" in wrapper
    assert "QGC_DIFF_REALTIME_GOAL_ACCEPTANCE.json" in wrapper
    assert "qgc_diff_realtime_goal_acceptance_verified" in wrapper
    assert "finalize_operator_run completed qgc_diff_realtime_goal_acceptance_verified" in wrapper
    assert "start_qgc_realtime_goal_bridge()" in wrapper
    assert "qgc_realtime_goal_bridge.py" in wrapper
    assert 'QGC_REALTIME_MISSION_READY_TOPIC="${QGC_REALTIME_MISSION_READY_TOPIC:-/mosim/goal4/interactive_goal_ready}"' in wrapper
    assert 'QGC_REALTIME_WAYPOINT_PLAN_SIZE_TOPIC="${QGC_REALTIME_WAYPOINT_PLAN_SIZE_TOPIC:-/mosim/goal4/interactive_goal_waypoint_count}"' in wrapper
    assert 'DIFF_INTERACTIVE_GOAL_READY_TOPIC="$QGC_REALTIME_MISSION_READY_TOPIC"' in wrapper
    assert 'DIFF_INTERACTIVE_WAYPOINT_PLAN_SIZE_TOPIC="$QGC_REALTIME_WAYPOINT_PLAN_SIZE_TOPIC"' in wrapper
    assert '--waypoint-plan-size-topic "$QGC_REALTIME_WAYPOINT_PLAN_SIZE_TOPIC"' in wrapper
    assert "qgc_waypoint_plan_not_fully_forwarded" in wrapper
    assert "qgc_waypoint_plan_mission_handoff_missing" in wrapper
    assert "GOAL_BRIDGE_PID=" in wrapper
    assert "stop_process GOAL_BRIDGE_PID" in wrapper
    assert "qgc_realtime_goal_bridge_start_failed" in wrapper
    active_pointer_at = wrapper.index("--activate-active")
    bridge_start_at = wrapper.index("if ! start_qgc_realtime_goal_bridge", active_pointer_at)
    readiness_wait_at = wrapper.index("if ! wait_for_interactive_chain", active_pointer_at)
    assert active_pointer_at < bridge_start_at < readiness_wait_at
    assert "Copy and run the bridge command" not in wrapper
    assert '"$RUNTIME_RESULT_DIR/RUN_MANIFEST.json"' not in wrapper
    assert "--expected-path-topic /mosim/goal4/target_path" in wrapper
    assert "--future-polytraj-topic /drone_0_planning/trajectory" in wrapper
    assert "--future-polytraj-frame-id world" in wrapper
    assert 'source "$GOAL4_DIFF_PLANNER_WS/devel/setup.bash"' in wrapper
    assert "--skip-actuator-telemetry-readiness" in wrapper
    assert "ENABLE_POINTCLOUD_REVIEW_ACCUMULATION=false" in wrapper
    assert "ENABLE_OCCUPANCY_REVIEW_ACCUMULATION=false" in wrapper
    assert "qgc_diff_realtime_goal_profile_mismatch" in wrapper
    assert "qgc_diff_realtime_goal_runtime_profile_mismatch" in wrapper
    assert "qgc_diff_realtime_goal_planner_profile_mismatch" in wrapper

    generic_runner = (ROOT / "Scripts" / "sunray" / "run_px4ctrl_ego_single_gate.sh").read_text(encoding="utf-8")
    mission = (ROOT / "Scripts" / "sunray" / "px4ctrl_ego_single_mission_node.py").read_text(encoding="utf-8")
    assert 'DIFF_INTERACTIVE_WAYPOINT_PLAN_SIZE_TOPIC="${DIFF_INTERACTIVE_WAYPOINT_PLAN_SIZE_TOPIC:-}"' in generic_runner
    assert 'MISSION_ADAPTER_ARGS+=(--interactive-waypoint-plan-size-topic "${DIFF_INTERACTIVE_WAYPOINT_PLAN_SIZE_TOPIC}")' in generic_runner
    assert "--interactive-require-waypoint-plan-size" in generic_runner
    assert "interactive_completion_goal_count" in mission
    assert "interactive_waypoint_plan_cancel_requested" in mission
    assert "qgc_waypoint_plan_cancelled" in mission
    assert 'FASTLIO_PATH_START_TIMEOUT_S="${FASTLIO_PATH_START_TIMEOUT_S:-${FASTLIO_START_TIMEOUT_S}}"' in generic_runner
    assert '--topic /path \\' in generic_runner
    assert 'fastlio_path_wait_pid=$!' in generic_runner
    assert 'if ! wait "${fastlio_path_wait_pid}"; then' in generic_runner
    assert "stop_owned_processes" in generic_runner
    assert 'pkill -f "rosmaster"' not in generic_runner
    assert 'pkill -f "rosout"' not in generic_runner
    assert 'DIFF_GOAL4_COMMON_WORLD_FRAME="${DIFF_GOAL4_COMMON_WORLD_FRAME:-false}"' in generic_runner
    assert 'DIFF_GOAL4_PLANNER_ODOM_TOPIC="${DIFF_GOAL4_PLANNER_ODOM_TOPIC:-/uav1/mosim/diff_goal4/planner_odom_world}"' in generic_runner
    assert 'DIFF_GOAL4_PLANNER_POSITION_CMD_WORLD_TOPIC="${DIFF_GOAL4_PLANNER_POSITION_CMD_WORLD_TOPIC:-/uav1/mosim/diff_goal4/planner_position_cmd_world}"' in generic_runner
    assert 'DIFF_CMD_SMOOTH_ENABLE="${DIFF_CMD_SMOOTH_ENABLE:-false}"' in generic_runner
    assert 'PLANNER_CMD_SMOOTH_ENABLE="${DIFF_CMD_SMOOTH_ENABLE}"' in generic_runner
    assert 'PLANNER_CMD_ODOM_TARGET_GUARD_ENABLE="${DIFF_CMD_ODOM_TARGET_GUARD_ENABLE}"' in generic_runner
    assert 'MISSION_ADAPTER_ARGS+=(--execute-max-truth-odom-z-error-m "${DIFF_EXECUTE_MAX_TRUTH_ODOM_Z_ERROR_M}")' in generic_runner
    assert '_direction:=local_to_world' in generic_runner
    assert '_direction:=world_to_local' in generic_runner
    assert '_path_odom_topic:="${DIFF_GOAL4_PATH_ODOM_TOPIC}"' in generic_runner
    assert '--path-odom-topic "${DIFF_GOAL4_PATH_ODOM_TOPIC}"' in generic_runner
    assert 'PLANNER_EXTRA_LAUNCH_ARGS+=(map_size_x:="${EGO_MAP_SIZE_X}")' in generic_runner
    assert 'PLANNER_EXTRA_LAUNCH_ARGS+=(map_size_y:="${EGO_MAP_SIZE_Y}")' in generic_runner
    assert 'PLANNER_EXTRA_LAUNCH_ARGS+=(map_size_z:="${EGO_MAP_SIZE_Z}")' in generic_runner

    goal_adapter = (ROOT / "Scripts" / "sunray" / "goal4_clicked_goal_adapter.py").read_text(encoding="utf-8")
    assert 'self.path_odom_topic = str(rospy.get_param("~path_odom_topic", "")).strip()' in goal_adapter
    assert "def on_path_odom" in goal_adapter
    assert "path_odom = self.last_path_odom or self.last_odom" in goal_adapter

    mission = (ROOT / "Scripts" / "sunray" / "px4ctrl_ego_single_mission_node.py").read_text(encoding="utf-8")
    assert 'parser.add_argument("--path-odom-topic", default="")' in mission
    assert "def on_path_odom" in mission
    assert "start_x, start_y, start_z = self.display_path_start()" in mission
    assert "target_x, target_y, target_z = self.display_path_target()" in mission
    assert "if self.last_path_odom is not None:" in mission
    assert "if self.last_forwarded_goal is not None:" in mission

    sunray_launch = (ROOT / "src" / "simulation" / "gazebo" / "sunray" / "launch_basic" / "sunray_px4_basic.launch").read_text(encoding="utf-8")
    assert '<arg name="px4_sim_speed_factor" default="$(optenv PX4_SIM_SPEED_FACTOR 1.0)" />' in sunray_launch
    assert '<env name="PX4_SIM_SPEED_FACTOR" value="$(arg px4_sim_speed_factor)" />' in sunray_launch
