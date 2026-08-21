from __future__ import annotations

import importlib.util
import sys
import time
import types
from pathlib import Path

from Scripts.sunray.interactive_goal_frame import interactive_completion_goal_count, resolve_target_for_state_frame


ROOT = Path(__file__).resolve().parents[2]
ADAPTER = ROOT / "Scripts" / "sunray" / "goal4_clicked_goal_adapter.py"


def test_world_goal_uses_declared_offset_for_map_state_evaluation() -> None:
    resolved = resolve_target_for_state_frame(
        (10.0, 20.0, 1.0),
        "world",
        "map",
        world_frame_id="world",
        map_frame_id="map",
        world_to_map_offset_xyz=(6.0, 15.0, 0.0),
        allow_world_map_transform=True,
    )

    assert resolved == ((4.0, 5.0, 1.0), "world_to_map_offset")


def test_world_map_evaluation_requires_an_explicit_transform_contract() -> None:
    resolved = resolve_target_for_state_frame(
        (10.0, 20.0, 1.0),
        "world",
        "map",
        world_frame_id="world",
        map_frame_id="map",
        world_to_map_offset_xyz=(0.0, 0.0, 0.0),
        allow_world_map_transform=False,
    )

    assert resolved is None


def test_initial_automatic_goal_does_not_end_the_manual_goal_session() -> None:
    assert interactive_completion_goal_count(None, False, 1, True) is None
    assert interactive_completion_goal_count(2, False, 1, True) == 2


def load_adapter_module(monkeypatch):
    rospy = types.ModuleType("rospy")
    geometry_msgs = types.ModuleType("geometry_msgs")
    geometry_msgs_msg = types.ModuleType("geometry_msgs.msg")
    nav_msgs = types.ModuleType("nav_msgs")
    nav_msgs_msg = types.ModuleType("nav_msgs.msg")
    std_msgs = types.ModuleType("std_msgs")
    std_msgs_msg = types.ModuleType("std_msgs.msg")

    class Bool:
        def __init__(self, data: bool = False) -> None:
            self.data = data

    class Header:
        pass

    class PointStamped:
        pass

    class PoseStamped:
        pass

    class Odometry:
        pass

    class RosPath:
        pass

    geometry_msgs_msg.PointStamped = PointStamped
    geometry_msgs_msg.PoseStamped = PoseStamped
    nav_msgs_msg.Odometry = Odometry
    nav_msgs_msg.Path = RosPath
    std_msgs_msg.Bool = Bool
    std_msgs_msg.Header = Header
    monkeypatch.setitem(sys.modules, "rospy", rospy)
    monkeypatch.setitem(sys.modules, "geometry_msgs", geometry_msgs)
    monkeypatch.setitem(sys.modules, "geometry_msgs.msg", geometry_msgs_msg)
    monkeypatch.setitem(sys.modules, "nav_msgs", nav_msgs)
    monkeypatch.setitem(sys.modules, "nav_msgs.msg", nav_msgs_msg)
    monkeypatch.setitem(sys.modules, "std_msgs", std_msgs)
    monkeypatch.setitem(sys.modules, "std_msgs.msg", std_msgs_msg)

    spec = importlib.util.spec_from_file_location("goal4_clicked_goal_adapter_for_test", ADAPTER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, Bool


def test_second_manual_goal_is_forwarded_when_completion_reopens_mission_ready(monkeypatch) -> None:
    module, Bool = load_adapter_module(monkeypatch)
    adapter = module.ClickedGoalAdapter.__new__(module.ClickedGoalAdapter)
    adapter.mission_ready = False
    adapter.last_mission_ready_wall = None
    adapter.queued_goal = {
        "source": "nav_goal",
        "x": 5.0,
        "y": -3.0,
        "z": 1.0,
    }
    adapter.queue_release_count = 0
    forwarded = []
    adapter.is_ready_to_forward_goal = lambda: adapter.mission_ready
    adapter.publish_goal = lambda x, y, z, source, allow_queue: forwarded.append(
        (x, y, z, source, allow_queue)
    )

    adapter.on_mission_ready(Bool(True))

    assert adapter.queued_goal is None
    assert adapter.queue_release_count == 1
    assert forwarded == [(5.0, -3.0, 1.0, "nav_goal", False)]


def test_target_path_is_cleared_after_a_stable_arrival(monkeypatch) -> None:
    module, _ = load_adapter_module(monkeypatch)

    class Stamp:
        def __init__(self, value: float) -> None:
            self.value = value

        def to_sec(self) -> float:
            return self.value

    class HeaderValue:
        def __init__(self, stamp=None, frame_id="") -> None:
            self.stamp = stamp
            self.frame_id = frame_id

    class PathValue:
        def __init__(self, header=None) -> None:
            self.header = header
            self.poses = []

    class PoseStampedValue:
        def __init__(self) -> None:
            self.header = None
            self.pose = types.SimpleNamespace(
                position=types.SimpleNamespace(x=0.0, y=0.0, z=0.0),
                orientation=types.SimpleNamespace(x=0.0, y=0.0, z=0.0, w=0.0),
            )

    module.Header = HeaderValue
    module.RosPath = PathValue
    module.PoseStamped = PoseStampedValue
    module.rospy.Time = types.SimpleNamespace(now=lambda: Stamp(time.time()))
    module.rospy.loginfo = lambda *args, **kwargs: None

    position = types.SimpleNamespace(x=4.02, y=-2.98, z=1.01)
    pose = types.SimpleNamespace(
        position=position,
        orientation=types.SimpleNamespace(x=0.0, y=0.0, z=0.0, w=1.0),
    )
    adapter = module.ClickedGoalAdapter.__new__(module.ClickedGoalAdapter)
    adapter.target_path_active = True
    adapter.last_path_goal = (4.0, -3.0, 1.0)
    adapter.last_path_odom = None
    adapter.last_odom = types.SimpleNamespace(pose=types.SimpleNamespace(pose=pose))
    adapter.target_reach_xy_radius_m = 0.35
    adapter.target_reach_z_tolerance_m = 0.12
    adapter.target_reach_required_stable_s = 0.5
    adapter.target_reached_since_wall = time.time() - 1.0
    published = []
    adapter.path_pub = types.SimpleNamespace(publish=published.append)
    adapter.frame_id = "world"

    adapter.refresh_target_path()
    assert len(published) == 1
    assert len(published[0].poses) == 2

    adapter.try_clear_target_path_on_arrival()

    assert adapter.target_path_active is False
    assert adapter.last_path_goal is None
    assert len(published) == 2
    assert published[1].poses == []


def test_goal4_rviz_configs_enable_the_mission_target_segment() -> None:
    for name in (
        "sunray_ros1_goal4_diff_pointcloud_review.rviz",
        "sunray_ros1_goal4_diff_grid3d_review.rviz",
    ):
        text = (ROOT / "Config" / "rviz" / name).read_text(encoding="utf-8")
        segment = text.split("Name: Mission Target Segment", 1)[0].split("- Class: rviz/Path")[-1]
        assert "Enabled: true" in segment
        assert "Topic: /mosim/goal4/target_path" in text

    grid_review = (ROOT / "Config" / "rviz" / "sunray_ros1_goal4_diff_grid3d_review.rviz").read_text(
        encoding="utf-8"
    )
    assert "        Y: 0" in grid_review
    assert "        Y: 120" not in grid_review
