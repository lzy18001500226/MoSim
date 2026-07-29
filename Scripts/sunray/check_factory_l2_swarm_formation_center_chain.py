#!/usr/bin/env python3
"""Validate the Factory L2 shared-center target-chain contract without ROS."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario",
        type=Path,
        default=ROOT / "Config/scenarios/formation/factory_l2_three_uav_obstacle_crossing.json",
    )
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument(
        "--mission-source",
        type=Path,
        default=ROOT / "Scripts/sunray/px4ctrl_ego_swarm_mission_node.py",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def triplets(raw: Any, label: str) -> list[tuple[float, float, float]]:
    if not isinstance(raw, list):
        raise ValueError(f"{label} must be a list")
    result: list[tuple[float, float, float]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, list) or len(item) < 3:
            raise ValueError(f"{label}[{index}] must contain x, y, z")
        result.append((float(item[0]), float(item[1]), float(item[2])))
    return result


def same_points(left: list[tuple[float, float, float]], right: list[tuple[float, float, float]]) -> bool:
    return len(left) == len(right) and all(
        abs(a - b) <= 1e-6
        for actual, expected in zip(left, right)
        for a, b in zip(actual, expected)
    )


def find_method(tree: ast.AST, name: str) -> ast.FunctionDef | None:
    return next(
        (node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name),
        None,
    )


def call_names(statements: list[ast.stmt]) -> set[str]:
    return {
        node.func.attr
        for statement in statements
        for node in ast.walk(statement)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }


def reads_json_with_utf8_sig(method: ast.FunctionDef) -> bool:
    """Require mission chain files to accept the Windows PowerShell UTF-8 BOM."""
    for node in ast.walk(method):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "read_text":
            continue
        for keyword in node.keywords:
            if (
                keyword.arg == "encoding"
                and isinstance(keyword.value, ast.Constant)
                and keyword.value.value == "utf-8-sig"
            ):
                return True
    return False


def mission_semantics_ok(path: Path) -> tuple[bool, list[str]]:
    source_text = path.read_text(encoding="utf-8")
    tree = ast.parse(source_text, filename=str(path))
    blockers: list[str] = []
    if find_method(tree, "validate_target_chain_contract") is None:
        blockers.append("mission_target_chain_validator_missing")
    chain_loader = find_method(tree, "load_waypoint_chain_file")
    if chain_loader is None or not reads_json_with_utf8_sig(chain_loader):
        blockers.append("formation_center_chain_bom_reader_missing")
    member_loader = find_method(tree, "load_target_chains")
    if member_loader is None or not reads_json_with_utf8_sig(member_loader):
        blockers.append("member_target_chain_bom_reader_missing")
    runner = find_method(tree, "run_target_chains")
    if runner is None:
        return False, blockers + ["mission_target_chain_runner_missing"]
    branch = next(
        (
            node
            for node in ast.walk(runner)
            if isinstance(node, ast.If)
            and isinstance(node.test, ast.Name)
            and node.test.id == "formation_center_mode"
            and "publish_formation_center_goal" in call_names(node.body)
        ),
        None,
    )
    if branch is None:
        blockers.append("formation_center_publish_branch_missing")
    else:
        if "publish_target_goals" in call_names(branch.body):
            blockers.append("member_targets_published_inside_shared_center_branch")
        if "publish_target_goals" not in call_names(branch.orelse):
            blockers.append("per_uav_goal_fallback_branch_missing")
    for marker in (
        "round_start_sim = self.now()",
        "round_start_wall = time.monotonic()",
        "self.args.target_chain_goal_wall_timeout_s",
        "goal_republish_time_basis",
    ):
        if marker not in source_text:
            blockers.append("target_chain_sim_time_contract_missing")
            break
    return not blockers, blockers

def leader_follower_execution_topology_ok(path: Path, mission_path: Path) -> tuple[bool, list[str]]:
    source_text = path.read_text(encoding="utf-8")
    mission_text = mission_path.read_text(encoding="utf-8")
    blockers: list[str] = []
    for marker in (
        'SAFETY_ADAPTER_UIDS=(1)',
        'bridge_input_topic="/uav1/position_cmd"',
        'bridge_output_topic="/uav${uid}/position_cmd"',
        'leader_safety_adapter_with_spawn_offset_follower_relay',
        'uav${uid}_leader_follower_position_cmd_relay.json',
    ):
        if marker not in source_text:
            blockers.append("leader_follower_executed_command_topology_missing")
            break
    for marker in (
        "MISSION_TOPOLOGY_ARGS+=(--leader-follower-commands)",
        'parser.add_argument(',
        '        "--leader-follower-commands"',
        "def planner_takeover_ready(self) -> bool:",
        "return self.first_planner_trajectory_time(self.uavs[1]) is not None",
        "self.leader_adapter_takeover_active = False",
        "if self.leader_adapter_takeover_active:",
        "self.leader_adapter_takeover_suppressed_hover_call_count += 1",
        "self.direct_hover_publish_count_during_adapter_takeover = 0",
        '"direct_hover_publish_count_during_adapter_takeover": self.direct_hover_publish_count_during_adapter_takeover',
    ):
        source = source_text if marker.startswith("MISSION_") else mission_text
        if marker not in source:
            blockers.append("leader_follower_single_command_owner_missing")
            break
    return not blockers, blockers


def main() -> int:
    args = parse_args()
    run_dir = args.run.resolve()
    scenario = load_json(args.scenario.resolve())
    formation = scenario.get("formation") if isinstance(scenario.get("formation"), dict) else {}
    rigid = scenario.get("rigid_center_path_contract") if isinstance(scenario.get("rigid_center_path_contract"), dict) else {}
    blockers: list[str] = []
    raw_center = rigid.get("center_waypoints_xy_m")
    if rigid.get("status") != "passed" or not isinstance(raw_center, list) or len(raw_center) < 2:
        blockers.append("rigid_center_path_contract_invalid")
        expected_center: list[tuple[float, float, float]] = []
    else:
        z_m = float(formation.get("z_m", 0.0))
        expected_center = [(float(point[0]), float(point[1]), z_m) for point in raw_center[1:]]

    center_path = run_dir / "formation_center_chain.json"
    if not center_path.exists():
        blockers.append("formation_center_chain_missing")
    else:
        center = load_json(center_path)
        actual_center = triplets(center.get("waypoints"), "formation_center_chain.waypoints")
        if center.get("target_transport") != "single_global_formation_center":
            blockers.append("formation_center_chain_transport_invalid")
        if center.get("skipped_spawn_waypoint") is not True:
            blockers.append("formation_center_chain_spawn_waypoint_not_skipped")
        if expected_center and not same_points(actual_center, expected_center):
            blockers.append("formation_center_chain_does_not_match_rigid_center_path")

    relative = formation.get("relative_positions_unit") if isinstance(formation.get("relative_positions_unit"), dict) else {}
    scale = float(formation.get("scale", 0.0))
    for uid in range(1, 4):
        path = run_dir / f"uav{uid}_formation_acceptance_chain.json"
        if not path.exists():
            blockers.append(f"uav{uid}_member_acceptance_chain_missing")
            continue
        payload = load_json(path)
        actual = triplets(payload.get("waypoints"), f"uav{uid}.waypoints")
        offset = relative.get(str(uid))
        if not isinstance(offset, list) or len(offset) < 2:
            blockers.append(f"uav{uid}_relative_offset_missing")
            continue
        expected = [(x + scale * float(offset[0]), y + scale * float(offset[1]), z) for x, y, z in expected_center]
        if payload.get("target_transport") != "acceptance_only_member_target_chain":
            blockers.append(f"uav{uid}_member_chain_transport_invalid")
        if not same_points(actual, expected):
            blockers.append(f"uav{uid}_member_chain_not_derived_from_center")

    semantics_ok, semantics_blockers = mission_semantics_ok(args.mission_source.resolve())
    blockers.extend(semantics_blockers)
    topology_ok, topology_blockers = leader_follower_execution_topology_ok(
        ROOT / "Scripts/sunray/run_px4ctrl_ego_swarm_gate.sh", args.mission_source.resolve()
    )
    blockers.extend(topology_blockers)
    packet = {
        "schema": "mosim.factory_l2_swarm_formation_center_chain_static_gate.v1",
        "status": "passed" if not blockers else "blocked",
        "blockers": list(dict.fromkeys(blockers)),
        "scenario": str(args.scenario.resolve()),
        "run_dir": str(run_dir),
        "expected_center_waypoint_count": len(expected_center),
        "mission_semantics_static_check": "passed" if semantics_ok else "blocked",
        "leader_follower_executed_command_topology_static_check": "passed" if topology_ok else "blocked",
        "claim_boundary": "Static only. Runtime acceptance still requires live MID360, Gazebo/PX4/MAVROS, tracking, obstacle-clearance, inter-UAV and landing gates.",
    }
    output = run_dir / "FORMATION_CENTER_CHAIN_STATIC_GATE.json"
    output.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
