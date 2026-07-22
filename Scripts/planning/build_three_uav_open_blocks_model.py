#!/usr/bin/env python3
"""Generate the three-whole-aircraft OpenBlocks MWORKS experiment model."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
HELPER_PATH = ROOT / "Scripts/planning/update_planning_open_blocks_model.py"
DEFAULT_CONFIG = ROOT / "Config/planners/astar_min_snap/map_open_blocks.yaml"
DEFAULT_METRICS = ROOT / "Results/planning/three_uav_open_blocks_mworks_20260720/metrics/three_uav_planning_metrics.json"
DEFAULT_MODEL = ROOT / "Models/MoSimQuadrotorModel/Planning/Scenarios/ThreeUavOpenBlocksReconfigurableFormationLinearMPC.mo"
MODEL_POINT_CAPACITY = 91
MODEL_SEGMENT_CAPACITY = 90
TAKEOFF_DURATION_S = 3.0
LANDING_DURATION_S = 3.0
UAV_GROUND_CENTER_CLEARANCE_M = 0.22


def load_helper() -> Any:
    spec = importlib.util.spec_from_file_location("mosim_update_open_blocks", HELPER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load helper: {HELPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Config root must be a mapping: {path}")
    return payload


def build_reference(helper: Any, vehicle: dict[str, Any], map_config: dict[str, Any], schedule_duration: float) -> dict[str, Any]:
    report = vehicle["planner_report"]
    path = [[float(value) for value in point] for point in report["simplified_path"]]
    path_durations = [float(value) for value in report["segment_durations"]]
    delay = float(vehicle["delay_s"])
    if len(path_durations) != len(path) - 1:
        raise ValueError(f"{vehicle['vehicle_id']} path and duration counts differ")

    start_ground = [
        path[0][0],
        path[0][1],
        helper.terrain_height(path[0][0], path[0][1], map_config) + UAV_GROUND_CENTER_CLEARANCE_M,
    ]
    goal_ground = [
        path[-1][0],
        path[-1][1],
        helper.terrain_height(path[-1][0], path[-1][1], map_config) + UAV_GROUND_CENTER_CLEARANCE_M,
    ]
    points = [start_ground, path[0]]
    durations = [TAKEOFF_DURATION_S]
    if delay > 1e-9:
        points.append(path[0])
        durations.append(delay)
    points.extend(path[1:])
    durations.extend(path_durations)
    arrival_time = delay + sum(path_durations)
    hold_duration = schedule_duration - arrival_time
    if hold_duration > 1e-9:
        points.append(path[-1])
        durations.append(hold_duration)
    points.append(goal_ground)
    durations.append(LANDING_DURATION_S)
    if len(durations) > MODEL_SEGMENT_CAPACITY:
        raise ValueError(f"{vehicle['vehicle_id']} exceeds {MODEL_SEGMENT_CAPACITY} segments")
    return {
        "n_segments": len(durations),
        "p_x": helper.padded([point[0] for point in points], MODEL_POINT_CAPACITY, points[-1][0]),
        "p_y": helper.padded([point[1] for point in points], MODEL_POINT_CAPACITY, points[-1][1]),
        "p_z": helper.padded([point[2] for point in points], MODEL_POINT_CAPACITY, points[-1][2]),
        "segment_duration": helper.padded(durations, MODEL_SEGMENT_CAPACITY, 1.0),
        "initial_position": start_ground,
        "stop_time": sum(durations),
    }


def reference_constructor(helper: Any, name: str, ref: dict[str, Any], origin: tuple[int, int]) -> str:
    return (
        f"  PlannedQuinticReference {name}(\n"
        f"    n_segments = {ref['n_segments']},\n"
        f"    p_x = {helper.modelica_array(ref['p_x'])},\n"
        f"    p_y = {helper.modelica_array(ref['p_y'])},\n"
        f"    p_z = {helper.modelica_array(ref['p_z'])},\n"
        f"    segment_duration = {helper.modelica_array(ref['segment_duration'])})\n"
        f"    annotation(Placement(transformation(origin = {{{origin[0]}, {origin[1]}}}, extent = {{{{-18, -18}}, {{18, 18}}}})));"
    )


def display_constructor(helper: Any, ref: dict[str, Any], map_config: dict[str, Any]) -> str:
    bounds = map_config["bounds"]
    return (
        "  PlanningNavigationDisplay navigationDisplay(\n"
        f"    n_segments = {ref['n_segments']},\n"
        f"    p_x = {helper.modelica_array(ref['p_x'])},\n"
        f"    p_y = {helper.modelica_array(ref['p_y'])},\n"
        f"    p_z = {helper.modelica_array(ref['p_z'])},\n"
        f"    segment_duration = {helper.modelica_array(ref['segment_duration'])},\n"
        f"    x_min = {helper.fmt(float(bounds['x'][0]))},\n"
        f"    x_max = {helper.fmt(float(bounds['x'][1]))},\n"
        f"    y_min = {helper.fmt(float(bounds['y'][0]))},\n"
        f"    y_max = {helper.fmt(float(bounds['y'][1]))},\n"
        "    render_boundary_walls = false,\n"
        "    highlight_local_costmap = true,\n"
        "    local_costmap_radius_m = 6,\n"
        "    local_costmap_fade_radius_m = 9,\n"
        "    show_static_map_mesh = false,\n"
        "    show_static_map_layers = true,\n"
        "    show_static_grid_overlay = false,\n"
        "    render_terrain_blocks = false,\n"
        "    terrain_render_stride = 10,\n"
        "    show_continuous_ground = false)\n"
        "    annotation(Placement(transformation(origin = {0, 72}, extent = {{-22, -22}, {22, 22}})));"
    )


def build_model(config: dict[str, Any], metrics: dict[str, Any]) -> str:
    helper = load_helper()
    map_config = config["map"]
    schedule_duration = float(metrics["schedule"]["duration_s"])
    vehicles = metrics["vehicles"]
    refs = [build_reference(helper, vehicle, map_config, schedule_duration) for vehicle in vehicles]
    stop_time = max(ref["stop_time"] for ref in refs)
    if max(ref["stop_time"] for ref in refs) - min(ref["stop_time"] for ref in refs) > 1e-8:
        raise ValueError("Generated vehicle references do not share one stop time")

    declarations = [
        "within MoSimQuadrotorModel.Planning.Scenarios;",
        "model ThreeUavOpenBlocksReconfigurableFormationLinearMPC",
        '  "Three whole-aircraft Linear-MPC loops following synchronized collision-safe OpenBlocks references"',
        "  parameter Real planned_clearance_m[3] = {"
        + ", ".join(helper.fmt(float(vehicle["min_obstacle_distance_m"])) for vehicle in vehicles)
        + "};",
        f"  parameter Real transit_start_s = {helper.fmt(TAKEOFF_DURATION_S + max(vehicle['delay_s'] for vehicle in vehicles))};",
        f"  parameter Real arrival_phase_s = {helper.fmt(TAKEOFF_DURATION_S + schedule_duration - 6.0)};",
        "",
    ]
    origins = ((-82, 74), (-82, 4), (-82, -66))
    declarations.extend(reference_constructor(helper, f"reference{index + 1}", ref, origins[index]) for index, ref in enumerate(refs))
    declarations.extend(["", display_constructor(helper, refs[0], map_config), ""])
    vehicle_origins = ((70, 74), (70, 4), (70, -66))
    for index, (ref, origin) in enumerate(zip(refs, vehicle_origins), start=1):
        initial = helper.modelica_array(ref["initial_position"])
        declarations.append(
            f"  OpenBlocksLinearMPCVehicle vehicle{index}(initial_position = {initial})\n"
            f"    annotation(Placement(transformation(origin = {{{origin[0]}, {origin[1]}}}, extent = {{{{-22, -22}}, {{22, 22}}}})));"
        )
    declarations.extend(
        [
            "",
            "  Real pair_distance_12_m;",
            "  Real pair_distance_13_m;",
            "  Real pair_distance_23_m;",
            "  Real min_inter_uav_distance_m;",
            "  Real reference_pair_distance_12_m;",
            "  Real reference_pair_distance_13_m;",
            "  Real reference_pair_distance_23_m;",
            "  Real formation_distance_error_m;",
            "  Real actual_clearance_lower_bound_m;",
            "  Integer formation_mode \"1 launch triangle, 2 corridor column, 3 arrival triangle\";",
            "",
            "equation",
        ]
    )
    for index in range(1, 4):
        y_center = 74 - 70 * (index - 1)
        declarations.extend(
            [
                f"  connect(reference{index}.position_command, vehicle{index}.position_reference) annotation(Line(points = {{{{-64, {helper.fmt(y_center + 7.2)}}}, {{18, {helper.fmt(y_center + 7.2)}}}, {{18, {helper.fmt(y_center + 13.2)}}}, {{43.6, {helper.fmt(y_center + 13.2)}}}}}, color = {{0, 0, 127}}));",
                f"  connect(reference{index}.z_ref_rate, vehicle{index}.z_reference_rate) annotation(Line(points = {{{{-64, {helper.fmt(y_center)}}}, {{24, {helper.fmt(y_center)}}}, {{24, {helper.fmt(y_center + 2.2)}}}, {{43.6, {helper.fmt(y_center + 2.2)}}}}}, color = {{0, 0, 127}}));",
                f"  connect(reference{index}.yaw_ref, vehicle{index}.yaw_reference) annotation(Line(points = {{{{-64, {helper.fmt(y_center - 7.2)}}}, {{18, {helper.fmt(y_center - 7.2)}}}, {{18, {helper.fmt(y_center - 8.8)}}}, {{43.6, {helper.fmt(y_center - 8.8)}}}}}, color = {{0, 0, 127}}));",
            ]
        )
    declarations.extend(
        [
            "  connect(vehicle1.position, navigationDisplay.actual_position) annotation(Line(points = {{96.4, 87.2}, {108, 87.2}, {108, 104}, {-34, 104}, {-34, 78.6}, {-26.4, 78.6}}, color = {0, 0, 127}));",
            "  connect(reference1.position_command, navigationDisplay.reference_position) annotation(Line(points = {{-64, 81.2}, {-48, 81.2}, {-48, 65.4}, {-26.4, 65.4}}, color = {0, 0, 127}));",
            "",
            "  pair_distance_12_m = sqrt(sum((vehicle1.position[i] - vehicle2.position[i]) ^ 2 for i in 1:3));",
            "  pair_distance_13_m = sqrt(sum((vehicle1.position[i] - vehicle3.position[i]) ^ 2 for i in 1:3));",
            "  pair_distance_23_m = sqrt(sum((vehicle2.position[i] - vehicle3.position[i]) ^ 2 for i in 1:3));",
            "  min_inter_uav_distance_m = min(pair_distance_12_m, min(pair_distance_13_m, pair_distance_23_m));",
            "  reference_pair_distance_12_m = sqrt(sum((reference1.position_command[i] - reference2.position_command[i]) ^ 2 for i in 1:3));",
            "  reference_pair_distance_13_m = sqrt(sum((reference1.position_command[i] - reference3.position_command[i]) ^ 2 for i in 1:3));",
            "  reference_pair_distance_23_m = sqrt(sum((reference2.position_command[i] - reference3.position_command[i]) ^ 2 for i in 1:3));",
            "  formation_distance_error_m = (abs(pair_distance_12_m - reference_pair_distance_12_m) + abs(pair_distance_13_m - reference_pair_distance_13_m) + abs(pair_distance_23_m - reference_pair_distance_23_m)) / 3;",
            "  actual_clearance_lower_bound_m = min(planned_clearance_m[1] - vehicle1.tracking_error_m, min(planned_clearance_m[2] - vehicle2.tracking_error_m, planned_clearance_m[3] - vehicle3.tracking_error_m));",
            "  formation_mode = if time < transit_start_s then 1 else if time < arrival_phase_s then 2 else 3;",
            "",
            f"  annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = {helper.fmt(stop_time)}, Tolerance = 0.0001, Interval = 0.05));",
            "  annotation(__MWORKS(hide=false));",
            "end ThreeUavOpenBlocksReconfigurableFormationLinearMPC;",
            "",
        ]
    )
    return "\n".join(declarations)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = read_yaml(args.config.resolve())
    metrics = json.loads(args.metrics.resolve().read_text(encoding="utf-8"))
    if metrics.get("status") != "accepted":
        raise RuntimeError("Planning metrics must be accepted before model generation")
    text = build_model(config, metrics)
    model_path = args.model.resolve()
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model_path.write_text(text, encoding="utf-8", newline="\n")
    print(f"Wrote {model_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
