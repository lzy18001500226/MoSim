from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Scripts" / "rflysim" / "rflysim_mid360_reactive_avoidance.py"


def load_module():
    saved_modules = {name: sys.modules.get(name) for name in ("UE4CtrlAPI", "VisionCaptureApi")}
    sys.modules["UE4CtrlAPI"] = types.SimpleNamespace(UE4CtrlAPI=object)
    sys.modules["VisionCaptureApi"] = types.SimpleNamespace(VisionCaptureApi=object)
    try:
        spec = importlib.util.spec_from_file_location("mosim_rflysim_reactive_avoidance", SOURCE)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        for name, value in saved_modules.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


def test_front_wall_routes_sideways_without_backward_steps() -> None:
    module = load_module()
    planner = module.LocalGridPlanner(6.0, 3.0, 0.25, 0.45)
    wall = np.array([[2.0, y, 0.0] for y in np.arange(-2.0, 2.01, 0.1)], dtype=float)

    path, info = planner.plan(wall, np.array([6.0, 0.0, 0.0]), z_limit_m=5.0)

    assert info["front_blocked"] is True
    assert info["blocked"] is False
    assert np.max(np.abs(path[:, 1])) > 0.0
    assert np.all(np.diff(path[:, 0]) >= 0.0)


def test_no_route_is_blocked_and_holds_position() -> None:
    module = load_module()
    planner = module.LocalGridPlanner(6.0, 3.0, 0.25, 0.45)
    wall = np.array(
        [[x, y, 0.0] for x in np.arange(1.0, 5.01, 0.1) for y in np.arange(-3.0, 3.01, 0.1)],
        dtype=float,
    )
    path, info = planner.plan(wall, np.array([6.0, 0.0, 0.0]), z_limit_m=5.0)

    assert len(path) == 1
    assert info["blocked"] is True
    velocity, target_yaw = module.command_velocity_from_plan(path, blocked=True, yaw=0.5, speed_mps=1.1)
    assert np.allclose(velocity, np.zeros(3))
    assert target_yaw == 0.5


def test_empty_plan_holds_before_first_cloud() -> None:
    module = load_module()

    velocity, target_yaw = module.command_velocity_from_plan(
        np.empty((0, 2), dtype=float), blocked=True, yaw=-0.25, speed_mps=1.1
    )

    assert np.allclose(velocity, np.zeros(3))
    assert target_yaw == -0.25
