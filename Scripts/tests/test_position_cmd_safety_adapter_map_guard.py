from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "Scripts" / "sunray" / "goal4_position_cmd_safety_adapter.py"


class _Stamp:
    def __init__(self, value: float = 0.0) -> None:
        self.value = value

    def to_sec(self) -> float:
        return self.value


class _Vector:
    def __init__(self) -> None:
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0


class _Header:
    def __init__(self) -> None:
        self.stamp = _Stamp()
        self.frame_id = "world"


class _PositionCommand:
    TRAJECTORY_STATUS_READY = 1

    def __init__(self) -> None:
        self.header = _Header()
        self.trajectory_flag = self.TRAJECTORY_STATUS_READY
        self.trajectory_id = 0
        self.position = _Vector()
        self.velocity = _Vector()
        self.acceleration = _Vector()
        self.jerk = _Vector()
        self.yaw = 0.0
        self.yaw_dot = 0.0
        self.kx = []
        self.kv = []


def _load_adapter(monkeypatch):
    rospy = types.ModuleType("rospy")
    rospy.Time = types.SimpleNamespace(now=lambda: _Stamp(10.0))
    nav_msgs = types.ModuleType("nav_msgs")
    nav_msgs_msg = types.ModuleType("nav_msgs.msg")
    nav_msgs_msg.Odometry = type("Odometry", (), {})
    quadrotor_msgs = types.ModuleType("quadrotor_msgs")
    quadrotor_msgs_msg = types.ModuleType("quadrotor_msgs.msg")
    quadrotor_msgs_msg.PositionCommand = _PositionCommand
    sensor_msgs = types.ModuleType("sensor_msgs")
    sensor_msgs_msg = types.ModuleType("sensor_msgs.msg")
    sensor_msgs_msg.PointCloud2 = type("PointCloud2", (), {})
    sensor_msgs_point_cloud2 = types.ModuleType("sensor_msgs.point_cloud2")
    sensor_msgs_point_cloud2.read_points = lambda *args, **kwargs: []
    std_msgs = types.ModuleType("std_msgs")
    std_msgs_msg = types.ModuleType("std_msgs.msg")
    std_msgs_msg.Bool = type("Bool", (), {})
    monkeypatch.setitem(sys.modules, "rospy", rospy)
    monkeypatch.setitem(sys.modules, "nav_msgs", nav_msgs)
    monkeypatch.setitem(sys.modules, "nav_msgs.msg", nav_msgs_msg)
    monkeypatch.setitem(sys.modules, "quadrotor_msgs", quadrotor_msgs)
    monkeypatch.setitem(sys.modules, "quadrotor_msgs.msg", quadrotor_msgs_msg)
    monkeypatch.setitem(sys.modules, "sensor_msgs", sensor_msgs)
    monkeypatch.setitem(sys.modules, "sensor_msgs.msg", sensor_msgs_msg)
    monkeypatch.setitem(sys.modules, "sensor_msgs.point_cloud2", sensor_msgs_point_cloud2)
    monkeypatch.setitem(sys.modules, "std_msgs", std_msgs)
    monkeypatch.setitem(sys.modules, "std_msgs.msg", std_msgs_msg)
    sys.path.insert(0, str(ADAPTER.parent))
    spec = importlib.util.spec_from_file_location("goal4_position_cmd_safety_adapter_map_guard", ADAPTER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _adapter_for_map_guard(module):
    adapter = module.PositionCmdSafetyAdapter.__new__(module.PositionCmdSafetyAdapter)
    adapter.map_guard_enabled = True
    adapter.map_guard_cloud_topic = "/uav1/livox_world"
    adapter.map_guard_occupancy_topic = "/drone_0_ego_planner_node/grid_map/occupancy_inflate"
    adapter.map_guard_timeout_s = 1.0
    adapter.map_guard_min_cloud_points = 1
    adapter.map_guard_min_occupancy_points = 1
    adapter.last_map_cloud_wall = 0.0
    adapter.last_map_cloud_points = 0
    adapter.last_map_cloud_stamp = 0.0
    adapter.last_occupancy_cloud_wall = 0.0
    adapter.last_occupancy_cloud_points = 0
    adapter.last_occupancy_cloud_stamp = 0.0
    adapter.last_map_guard = None
    adapter.map_guard_not_ready_count = 0
    adapter.map_guard_ready_count = 0
    adapter.map_guard_hold_count = 0
    adapter.last_raw = _PositionCommand()
    adapter.map_collision_guard_enabled = False
    adapter.map_collision_radius_m = 0.30
    adapter.map_collision_z_margin_m = 0.25
    adapter.map_collision_sample_step_m = 0.06
    adapter.map_collision_max_points = 10000
    adapter.last_occupancy_points = []
    adapter.last_occupancy_frame_id = "world"
    adapter.map_collision_guard_count = 0
    adapter.map_collision_hold_count = 0
    adapter.last_map_collision = None
    adapter.waiting_fresh_raw_after_enable = False
    adapter.seed_from_odom_on_enable = True
    adapter.last_safe_msg = None
    adapter.last_odom_xyz = [1.0, 2.0, 1.0]
    adapter.fixed_z = None
    adapter.fixed_yaw = None
    adapter.min_z = 0.95
    adapter.max_z = 1.15
    adapter.last_publish_stale = False
    adapter.last_published_xyz = None
    adapter.last_published_wall = 0.0
    adapter.last_published_motion_time = None
    adapter.min_published_z = None
    adapter.max_published_z = None
    adapter.jump_hold_publish_count = 0
    adapter.invalid_z_hold_publish_count = 0
    adapter.hold_publish_count = 0
    adapter.last_accepted_wall = None
    adapter.last_reject_reason = None
    return adapter


def test_missing_planner_map_holds_at_current_odom_instead_of_forwarding_raw_goal(monkeypatch) -> None:
    module = _load_adapter(monkeypatch)
    adapter = _adapter_for_map_guard(module)

    held = adapter.adapted_msg(10.0, 10.0)

    assert held is not None
    assert (held.position.x, held.position.y, held.position.z) == (1.0, 2.0, 1.0)
    assert (held.velocity.x, held.velocity.y, held.velocity.z) == (0.0, 0.0, 0.0)
    assert adapter.last_reject_reason == "planner_map_not_ready"
    assert adapter.map_guard_hold_count == 1
    assert "planner_cloud_empty" in adapter.last_map_guard["reasons"]
    assert "occupancy_inflate_empty" in adapter.last_map_guard["reasons"]


def test_map_guard_requires_fresh_nonempty_cloud_and_occupancy(monkeypatch) -> None:
    module = _load_adapter(monkeypatch)
    adapter = types.SimpleNamespace(
        map_guard_enabled=True,
        map_guard_timeout_s=1.0,
        map_guard_min_cloud_points=1,
        map_guard_min_occupancy_points=1,
        map_guard_cloud_topic="/uav1/livox_world",
        map_guard_occupancy_topic="/drone_0_ego_planner_node/grid_map/occupancy_inflate",
        last_map_cloud_wall=9.5,
        last_map_cloud_points=12,
        last_map_cloud_stamp=5.0,
        last_occupancy_cloud_wall=9.6,
        last_occupancy_cloud_points=4,
        last_occupancy_cloud_stamp=5.0,
    )

    snapshot = module.PositionCmdSafetyAdapter.map_guard_snapshot(adapter, 10.0)

    assert snapshot["ready"] is True
    assert snapshot["reasons"] == []


def test_collision_guard_holds_before_candidate_crosses_inflated_occupancy(monkeypatch) -> None:
    module = _load_adapter(monkeypatch)
    adapter = _adapter_for_map_guard(module)
    adapter.map_collision_guard_enabled = True
    adapter.last_safe_msg = _PositionCommand()
    adapter.last_safe_msg.position.x = 0.0
    adapter.last_safe_msg.position.y = 0.0
    adapter.last_safe_msg.position.z = 1.0
    adapter.last_occupancy_points = [(0.5, 0.0, 1.0)]
    adapter.last_occupancy_frame_id = "world"
    adapter.last_raw.position.x = 1.0
    adapter.last_raw.position.y = 0.0
    adapter.last_raw.position.z = 1.0

    candidate = adapter.apply_map_collision_guard(adapter.last_raw, 10.0, 10.0)

    assert candidate is not None
    assert (candidate.position.x, candidate.position.y, candidate.position.z) == (0.0, 0.0, 1.0)
    assert adapter.map_collision_guard_count == 1
    assert adapter.map_collision_hold_count == 1
    assert adapter.last_map_collision["reason"] == "candidate_intersects_inflated_occupancy"
