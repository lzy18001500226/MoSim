from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Scripts" / "ros" / "ego_style_planner_output_node.py"


def load_module():
    spec = importlib.util.spec_from_file_location("mosim_ego_style_planner_output_node", SOURCE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_front_wall_routes_sideways_without_backward_steps() -> None:
    module = load_module()
    planner = module.LocalGridPlanner(6.0, 3.0, 0.25, 0.45)
    wall = [(2.0, float(y), 0.0) for y in np.arange(-2.0, 2.01, 0.1)]

    path, info = planner.plan(wall, (6.0, 0.0), -0.6, 2.0)

    assert info["front_blocked"] is True
    assert info["blocked"] is False
    assert max(abs(point[1]) for point in path) > 0.0
    assert all(path[index + 1][0] >= path[index][0] for index in range(len(path) - 1))


def test_no_route_is_reported_as_blocked() -> None:
    module = load_module()
    planner = module.LocalGridPlanner(6.0, 3.0, 0.25, 0.45)
    wall = [(x, y, 0.0) for x in np.arange(1.0, 5.01, 0.1) for y in np.arange(-3.0, 3.01, 0.1)]

    path, info = planner.plan(wall, (6.0, 0.0), -0.6, 2.0)

    assert len(path) == 1
    assert info["blocked"] is True


def test_blocked_target_holds_current_position() -> None:
    module = load_module()

    target = module.command_target_from_plan(
        [4.0, -2.0, 1.7],
        yaw=0.4,
        local_path=[],
        plan_info={"blocked": True},
        cloud_ready=False,
        requested_lookahead=3,
        target_altitude_m=1.2,
    )

    assert target == (4.0, -2.0, 1.7, 0.0, 0.0, True)
