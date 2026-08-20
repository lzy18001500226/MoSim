from __future__ import annotations

import importlib.util
import sys
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
