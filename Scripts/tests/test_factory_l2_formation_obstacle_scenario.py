from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts/sunray/build_factory_l2_formation_obstacle_scenario.py"
LAUNCH = ROOT / "Scripts/sunray/swarm_formation_swarm_px4ctrl_d3.launch"
OPTIMIZER = (
    ROOT
    / "References/Lab/swarm_coordination/Swarm-Formation/src/planner/traj_opt/src/poly_traj_optimizer.cpp"
)
OPTIMIZER_HEADER = (
    ROOT
    / "References/Lab/swarm_coordination/Swarm-Formation/src/planner/traj_opt/include/optimizer/poly_traj_optimizer.h"
)
REPLAN_FSM = (
    ROOT
    / "References/Lab/swarm_coordination/Swarm-Formation/src/planner/plan_manage/src/ego_replan_fsm.cpp"
)


def load_module():
    sys.path.insert(0, str(SCRIPT.parent))
    spec = importlib.util.spec_from_file_location("formation_scenario", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_formation_positions_preserve_two_meter_minimum_spacing() -> None:
    module = load_module()
    positions = module.formation_positions((3.0, -4.0), 1.0)
    distances = [
        math.dist(positions[first], positions[second])
        for first, second in (("1", "2"), ("1", "3"), ("2", "3"))
    ]
    assert min(distances) == 2.0


def test_scenario_selection_audits_each_member_corridor() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert '"member_hits": member_hits' in source
    assert "any(len(path_hits) > 1" in source
    assert 'item["maximum_hit_planar_span_m"]' in source


def test_runtime_uses_real_three_uav_formation_model() -> None:
    launch = LAUNCH.read_text(encoding="utf-8")
    optimizer = OPTIMIZER.read_text(encoding="utf-8")
    optimizer_header = OPTIMIZER_HEADER.read_text(encoding="utf-8")
    replan_fsm = REPLAN_FSM.read_text(encoding="utf-8")

    assert '<arg name="formation_type" default="2"/>' in launch
    assert launch.count('name="optimization/formation_type"') == 3
    assert "THREE_UAV_TRIANGLE    = 2" in optimizer_header
    assert "formation_ready" in optimizer
    assert "if (formation_ready)" in optimizer
    assert "(pos - start_pos).norm() < obs_clearance_" in optimizer
    assert "if (planFromLocalTraj(true, true))" in replan_fsm
