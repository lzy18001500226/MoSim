#!/usr/bin/env python3
"""Synchronize the open-blocks planning model with the latest planner output."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
TERRAIN_HEIGHT_MIN_M = 0.10
TERRAIN_HEIGHT_MAX_M = 1.50
TERRAIN_HEIGHT_SPAN_M = TERRAIN_HEIGHT_MAX_M - TERRAIN_HEIGHT_MIN_M
TERRAIN_VIS_CELL_M = 0.20
TERRAIN_STEP_M = 0.01
MODEL_POINT_CAPACITY = 91
MODEL_SEGMENT_CAPACITY = 90
GUI_RENDER_RANDOM_OBSTACLE_LIMIT = 0
GUI_RENDER_ROUTE_BUFFER_M = 9.5
DUMMY_DISABLED_PILLAR_SIZE_M = 0.16
LOCAL_SENSOR_CELL_SIZE_M = 0.20
TAKEOFF_DURATION_S = 3.0
LANDING_DURATION_S = 3.0
GROUND_CLEARANCE_M = 0.0
UAV_GROUND_CENTER_CLEARANCE_M = 0.22


def read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def fmt(value: float) -> str:
    if abs(value) < 5e-13:
        value = 0.0
    return f"{value:.12g}"


def modelica_array(values: list[float], *, per_line: int = 6) -> str:
    chunks = []
    for index in range(0, len(values), per_line):
        chunks.append(", ".join(fmt(value) for value in values[index : index + per_line]))
    if len(chunks) == 1:
        return "{" + chunks[0] + "}"
    return "{\n      " + ",\n      ".join(chunks) + "}"


def modelica_matrix(rows: list[list[float]], *, per_line: int = 3) -> str:
    row_text = ["{" + ", ".join(fmt(value) for value in row) + "}" for row in rows]
    chunks = []
    for index in range(0, len(row_text), per_line):
        chunks.append(", ".join(row_text[index : index + per_line]))
    return "{\n      " + ",\n      ".join(chunks) + "}"


def terrain_height(x: float, y: float, map_config: dict[str, Any]) -> float:
    ix = math.floor((x + 45.0) / TERRAIN_VIS_CELL_M)
    iy = math.floor((y + 30.0) / TERRAIN_VIS_CELL_M)
    cell_jitter = math.sin(ix * 12.9898 + iy * 78.233) * 43758.5453
    cell_jitter = 0.24 * (cell_jitter - math.floor(cell_jitter) - 0.5)
    parity_jitter = 0.035 * (((ix + 2 * iy) % 5) - 2)
    value = (
        0.30 * math.sin(0.075 * x + 0.031 * y + 0.4)
        + 0.24 * math.sin(-0.044 * x + 0.089 * y + 1.7)
        + 0.22 * math.sin(0.210 * x - 0.135 * y + 2.1)
        + 0.16 * math.sin(0.390 * x + 0.310 * y)
        + 0.08 * math.sin(0.770 * x - 0.570 * y + 0.8)
        + cell_jitter
        + parity_jitter
    )
    normalized = max(0.0, min(1.0, 0.5 + 0.62 * math.tanh(1.55 * value)))
    smooth_height = TERRAIN_HEIGHT_MIN_M + TERRAIN_HEIGHT_SPAN_M * normalized
    stepped_height = round(smooth_height / TERRAIN_STEP_M) * TERRAIN_STEP_M
    return max(TERRAIN_HEIGHT_MIN_M, min(TERRAIN_HEIGHT_MAX_M, stepped_height))


def padded(values: list[float], target: int, pad_value: float) -> list[float]:
    if len(values) > target:
        raise ValueError(f"Too many values for model capacity {target}: {len(values)}")
    return values + [pad_value] * (target - len(values))


def pillar_cluster(obstacle: dict[str, Any]) -> list[tuple[float, float, float, float, float, float]]:
    center = obstacle["center"]
    x = float(center[0])
    y = float(center[1])
    radius = float(obstacle["radius"])
    height = float(obstacle.get("height", obstacle.get("z_max", 1.8)))
    z_min = float(obstacle.get("z_min", 0.0))
    width = max(0.16, min(0.42, 0.75 * radius))
    spread = 0.55 * radius
    return [
        (x - spread, y, width, width, height, z_min),
        (x + spread, y, width, width, height, z_min),
        (x, y + 0.95 * spread, width, width, height, z_min),
    ]


def wall_pillars(obstacle: dict[str, Any]) -> list[tuple[float, float, float, float, float, float]]:
    lo = obstacle["min"]
    hi = obstacle["max"]
    x0, x1 = sorted((float(lo[0]), float(hi[0])))
    y0, y1 = sorted((float(lo[1]), float(hi[1])))
    z0, z1 = sorted((float(lo[2]), float(hi[2])))
    length_x = x1 - x0
    length_y = y1 - y0
    height = z1 - z0
    if height <= 0.0 or length_x <= 0.0 or length_y <= 0.0:
        return []

    return [(0.5 * (x0 + x1), 0.5 * (y0 + y1), length_x, length_y, height, z0)]


def build_reference(report: dict[str, Any], map_config: dict[str, Any]) -> dict[str, Any]:
    path = [[float(value) for value in point] for point in report["simplified_path"]]
    durations = [float(value) for value in report["segment_durations"]]
    if len(path) < 2 or len(durations) != len(path) - 1:
        raise ValueError("simplified_path and segment_durations are inconsistent")

    start_ground = [
        path[0][0],
        path[0][1],
        terrain_height(path[0][0], path[0][1], map_config) + GROUND_CLEARANCE_M + UAV_GROUND_CENTER_CLEARANCE_M,
    ]
    goal_ground = [
        path[-1][0],
        path[-1][1],
        terrain_height(path[-1][0], path[-1][1], map_config) + GROUND_CLEARANCE_M + UAV_GROUND_CENTER_CLEARANCE_M,
    ]
    points = [start_ground, *path, goal_ground]
    segment_duration = [TAKEOFF_DURATION_S, *durations, LANDING_DURATION_S]
    n_segments = len(segment_duration)
    if n_segments > MODEL_SEGMENT_CAPACITY:
        raise ValueError(f"n_segments={n_segments} exceeds {MODEL_SEGMENT_CAPACITY}")

    return {
        "n_segments": n_segments,
        "p_x": padded([point[0] for point in points], MODEL_POINT_CAPACITY, points[-1][0]),
        "p_y": padded([point[1] for point in points], MODEL_POINT_CAPACITY, points[-1][1]),
        "p_z": padded([point[2] for point in points], MODEL_POINT_CAPACITY, points[-1][2]),
        "segment_duration": padded(segment_duration, MODEL_SEGMENT_CAPACITY, 1.0),
        "start": points[0],
        "takeoff_ground_z": start_ground[2],
        "landing_ground_z": goal_ground[2],
        "stop_time": sum(segment_duration),
    }


def point_segment_distance_xy(point: tuple[float, float], a: list[float], b: list[float]) -> float:
    px, py = point
    ax, ay = float(a[0]), float(a[1])
    bx, by = float(b[0]), float(b[1])
    vx = bx - ax
    vy = by - ay
    denom = vx * vx + vy * vy
    if denom <= 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / denom))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def route_distance_xy(point: tuple[float, float], path: list[list[float]]) -> float:
    if len(path) < 2:
        return math.inf
    return min(point_segment_distance_xy(point, path[i], path[i + 1]) for i in range(len(path) - 1))


def build_pillars(report: dict[str, Any], ref: dict[str, Any]) -> dict[str, Any]:
    pillars: list[tuple[float, float, float, float, float, float]] = []
    random_boxes = [
        obstacle
        for obstacle in report["truth_obstacles"]
        if obstacle.get("type") == "box" and obstacle.get("random_cluster")
    ]
    cylinders = [obstacle for obstacle in report["truth_obstacles"] if obstacle.get("type") == "cylinder"]
    render_obstacles: list[dict[str, Any]] = []
    if random_boxes:
        grouped: dict[int, list[dict[str, Any]]] = {}
        for obstacle in random_boxes:
            grouped.setdefault(int(obstacle.get("random_cluster_id", len(grouped) + 1)), []).append(obstacle)
        for cluster_id in sorted(grouped):
            group = grouped[cluster_id]
            x0 = min(float(item["min"][0]) for item in group)
            y0 = min(float(item["min"][1]) for item in group)
            z0 = min(float(item["min"][2]) for item in group)
            x1 = max(float(item["max"][0]) for item in group)
            y1 = max(float(item["max"][1]) for item in group)
            z1 = max(float(item["max"][2]) for item in group)
            render_obstacles.append({
                "type": "box",
                "random_cluster": True,
                "random_cluster_id": cluster_id,
                "min": [x0, y0, z0],
                "max": [x1, y1, z1],
            })
        route_path = [[ref["p_x"][i], ref["p_y"][i]] for i in range(ref["n_segments"] + 1)]
        filtered_obstacles = []
        for obstacle in render_obstacles:
            lo = obstacle["min"]
            hi = obstacle["max"]
            center = (0.5 * (float(lo[0]) + float(hi[0])), 0.5 * (float(lo[1]) + float(hi[1])))
            half_diag = 0.5 * math.hypot(float(hi[0]) - float(lo[0]), float(hi[1]) - float(lo[1]))
            if route_distance_xy(center, route_path) - half_diag <= GUI_RENDER_ROUTE_BUFFER_M:
                filtered_obstacles.append(obstacle)
        render_obstacles = filtered_obstacles
    elif len(cylinders) > GUI_RENDER_RANDOM_OBSTACLE_LIMIT:
        step = max(1, math.floor(len(cylinders) / GUI_RENDER_RANDOM_OBSTACLE_LIMIT))
        render_obstacles = cylinders[::step][:GUI_RENDER_RANDOM_OBSTACLE_LIMIT]
    else:
        render_obstacles = cylinders
    for obstacle in render_obstacles:
        if obstacle.get("type") == "box":
            lo = obstacle["min"]
            hi = obstacle["max"]
            x0, x1 = sorted((float(lo[0]), float(hi[0])))
            y0, y1 = sorted((float(lo[1]), float(hi[1])))
            z0, z1 = sorted((float(lo[2]), float(hi[2])))
            pillars.append((0.5 * (x0 + x1), 0.5 * (y0 + y1), x1 - x0, y1 - y0, z1 - z0, z0))
        else:
            center = obstacle["center"]
            x = float(center[0])
            y = float(center[1])
            height = float(obstacle.get("height", obstacle.get("z_max", 1.8)))
            z_min = float(obstacle.get("z_min", 0.0))
            width = DUMMY_DISABLED_PILLAR_SIZE_M
            pillars.append((x, y, width, width, height, z_min))
    if not pillars:
        pillars.append((0.0, 0.0, DUMMY_DISABLED_PILLAR_SIZE_M, DUMMY_DISABLED_PILLAR_SIZE_M, 3.0, 0.0))
    return {
        "max_pillars": max(1, len(pillars)),
        "pillar_count": len(render_obstacles),
        "truth_cylinder_count": len(cylinders),
        "truth_random_box_count": len(random_boxes),
        "rendered_random_obstacle_count": len(render_obstacles),
        "rendered_cylinder_count": sum(1 for obstacle in render_obstacles if obstacle.get("type") == "cylinder"),
        "centers": [[x, y] for x, y, _, _, _, _ in pillars],
        "lengths": [length for _, _, length, _, _, _ in pillars],
        "widths": [width for _, _, _, width, _, _ in pillars],
        "heights": [height for _, _, _, _, height, _ in pillars],
        "z_min": [z_min for _, _, _, _, _, z_min in pillars],
    }


def build_wall_groups(report: dict[str, Any]) -> dict[str, Any]:
    boxes: list[dict[str, Any]] = [
        obstacle
        for obstacle in report["truth_obstacles"]
        if obstacle.get("type") == "box" and "wall_group_id" in obstacle
    ]
    if len(boxes) % 2 != 0:
        raise ValueError(f"Fixed wall box count must be even, got {len(boxes)}")

    arm1_min: list[list[float]] = []
    arm1_max: list[list[float]] = []
    arm2_min: list[list[float]] = []
    arm2_max: list[list[float]] = []
    for index in range(0, len(boxes), 2):
        first = boxes[index]
        second = boxes[index + 1]
        arm1_min.append([float(value) for value in first["min"]])
        arm1_max.append([float(value) for value in first["max"]])
        arm2_min.append([float(value) for value in second["min"]])
        arm2_max.append([float(value) for value in second["max"]])

    count = len(arm1_min)
    max_wall_groups = max(8, count)
    pad = [[0.0, 0.0, 0.0] for _ in range(max_wall_groups - count)]
    return {
        "max_wall_groups": max_wall_groups,
        "wall_group_count": count,
        "arm1_min": arm1_min + pad,
        "arm1_max": arm1_max + pad,
        "arm2_min": arm2_min + pad,
        "arm2_max": arm2_max + pad,
    }


def build_constructor(name: str, ref: dict[str, Any], map_config: dict[str, Any], pillars: dict[str, Any]) -> str:
    bounds = map_config["bounds"]
    x_min = float(bounds["x"][0])
    x_max = float(bounds["x"][1])
    y_min = float(bounds["y"][0])
    y_max = float(bounds["y"][1])
    return f"""  {name}(
    n_segments = {ref["n_segments"]},
    p_x = {modelica_array(ref["p_x"])},
    p_y = {modelica_array(ref["p_y"])},
    p_z = {modelica_array(ref["p_z"])},
    segment_duration = {modelica_array(ref["segment_duration"])}"""


def build_display_constructor(
    ref: dict[str, Any],
    map_config: dict[str, Any],
    pillars: dict[str, Any],
    walls: dict[str, Any],
) -> str:
    base = build_constructor("PlanningNavigationDisplay navigationDisplay", ref, map_config, pillars)
    bounds = map_config["bounds"]
    local_radius_m = float(map_config.get("display_radar_radius_m", map_config.get("local_planning_radius_m", 2.5)))
    local_fade_radius_m = float(map_config.get("display_radar_fade_radius_m", max(local_radius_m, 1.5 * local_radius_m)))
    local_cell_size_m = float(map_config.get("display_radar_cell_size_m", LOCAL_SENSOR_CELL_SIZE_M))
    local_half_cells = max(1, math.ceil(local_fade_radius_m / local_cell_size_m))
    return f"""{base},
    x_min = {fmt(float(bounds["x"][0]))},
    x_max = {fmt(float(bounds["x"][1]))},
    y_min = {fmt(float(bounds["y"][0]))},
    y_max = {fmt(float(bounds["y"][1]))},
    boundary_line_diameter_m = 0.0,
    render_boundary_walls = false,
    boundary_wall_height_m = 0.0,
    boundary_wall_thickness_m = 0.0,
    highlight_local_costmap = true,
    local_costmap_radius_m = {fmt(local_radius_m)},
    local_costmap_fade_radius_m = {fmt(local_fade_radius_m)},
    local_costmap_front_half_angle_rad = 3.141592653589793,
    local_costmap_update_period_s = 0.05,
    local_costmap_half_cells = {local_half_cells},
    local_costmap_cell_size_m = {fmt(local_cell_size_m)},
    local_sensed_cell_size_m = {fmt(local_cell_size_m)},
    local_sensed_half_cells = {local_half_cells},
    local_plan_horizon_s = 4.0,
    local_plan_point_count = 12,
    local_plan_max_length_m = 3.5,
    terrain_cell_size_m = 3.0,
    terrain_fill_scale = 1.02,
    render_terrain_blocks = false,
    show_static_map_mesh = false,
    terrain_x_offset_m = 0.0,
    terrain_y_offset_m = 0.0,
    terrain_render_stride = 2,
    local_terrain_half_cells = 6,
    show_continuous_ground = false,
    show_static_map_layers = false,
    max_pillars = {pillars["max_pillars"]},
    pillar_count = {pillars["pillar_count"]},
    pillar_center = {modelica_matrix(pillars["centers"])},
    pillar_length = {modelica_array(pillars["lengths"])},
    pillar_width = {modelica_array(pillars["widths"])},
    pillar_height = {modelica_array(pillars["heights"])},
    pillar_z_min = {modelica_array(pillars["z_min"])},
    max_wall_groups = {walls["max_wall_groups"]},
    wall_group_count = {walls["wall_group_count"]},
    wall_arm1_min = {modelica_matrix(walls["arm1_min"])},
    wall_arm1_max = {modelica_matrix(walls["arm1_max"])},
    wall_arm2_min = {modelica_matrix(walls["arm2_min"])},
    wall_arm2_max = {modelica_matrix(walls["arm2_max"])})"""


def replace_between(text: str, pattern: str, replacement: str) -> str:
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Pattern replacement failed: {pattern[:60]}")
    return new_text


def update_model(model_path: Path, planner_config_path: Path, report_path: Path) -> None:
    config = read_yaml(planner_config_path)
    map_config = dict(config["map"])
    local_config = config.get("local_planning", {})
    if isinstance(local_config, dict):
        map_config["local_planning_radius_m"] = float(local_config.get("window_radius_m", 2.5))
    visualization_config = config.get("visualization", {})
    if isinstance(visualization_config, dict):
        radar_radius_m = float(
            visualization_config.get("radar_radius_m", map_config.get("local_planning_radius_m", 2.5))
        )
        map_config["display_radar_radius_m"] = radar_radius_m
        map_config["display_radar_fade_radius_m"] = float(
            visualization_config.get("radar_fade_radius_m", max(radar_radius_m, 1.5 * radar_radius_m))
        )
        map_config["display_radar_cell_size_m"] = float(
            visualization_config.get("radar_cell_size_m", LOCAL_SENSOR_CELL_SIZE_M)
        )
    report = json.loads(report_path.read_text(encoding="utf-8"))
    ref = build_reference(report, map_config)
    pillars = build_pillars(report, ref)
    walls = build_wall_groups(report)
    text = model_path.read_text(encoding="utf-8")

    planning_ref = build_constructor("PlannedQuinticReference planningReference", ref, map_config, pillars) + ")"
    display = build_display_constructor(ref, map_config, pillars, walls)
    text = replace_between(
        text,
        r"  PlannedQuinticReference planningReference\([\s\S]*?\);\n  PlanningNavigationDisplay navigationDisplay\([\s\S]*?\);",
        planning_ref + ";\n" + display + ";",
    )
    start = ref["start"]
    text = replace_between(
        text,
        r"body\(color = \{135, 206, 235\}, r_0\(start = \{[^}]+\}, fixed = \{true, true, true\}\)\)",
        f"body(color = {{135, 206, 235}}, r_0(start = {{{fmt(start[0])}, {fmt(start[1])}, {fmt(start[2])}}}, fixed = {{true, true, true}}))",
    )
    text = replace_between(
        text,
        r"annotation\(experiment\(Algorithm = Dassl, StartTime = 0, StopTime = [^,]+, Tolerance = 0.0001, Interval = [^)]+\)\);",
        f"annotation(experiment(Algorithm = Dassl, StartTime = 0, StopTime = {fmt(ref['stop_time'])}, Tolerance = 0.0001, Interval = 0.05));",
    )
    model_path.write_text(text, encoding="utf-8")
    print(f"Updated {model_path}")
    print(
        f"segments={ref['n_segments']} stop_time={fmt(ref['stop_time'])} "
        f"rendered_pillars={pillars['pillar_count']} truth_cylinders={pillars['truth_cylinder_count']} "
        f"wall_groups={walls['wall_group_count']} wall_boxes={walls['wall_group_count'] * 2}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=ROOT / "models/QuadrotorExperiments/Sunray150PlanningOpenBlocksLinearMPCSysblockClosedLoop.mo")
    parser.add_argument("--planner-config", type=Path, default=ROOT / "planners/astar_min_snap/map_open_blocks.yaml")
    parser.add_argument("--report", type=Path, default=ROOT / "results/planning/single_obstacle_astar_awff/metrics/trackability_report.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    update_model(args.model, args.planner_config, args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
