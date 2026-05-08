#!/usr/bin/env python3
"""Generate A* obstacle-avoidance references and planning metrics."""

from __future__ import annotations

import argparse
import csv
import heapq
import json
import math
from pathlib import Path
from typing import Any

from generate_planning_reference import (
    allocate_segment_times,
    generate_trackable_rows,
    norm,
    read_yaml,
    vector_sub,
    write_csv,
)


Index3 = tuple[int, int, int]


def as_float_list(values: list[Any]) -> list[float]:
    return [float(value) for value in values]


def map_bounds(map_config: dict[str, Any]) -> tuple[list[float], list[float]]:
    bounds = map_config["bounds"]
    lower = [float(bounds[axis][0]) for axis in ["x", "y", "z"]]
    upper = [float(bounds[axis][1]) for axis in ["x", "y", "z"]]
    return lower, upper


def point_to_index(point: list[float], lower: list[float], resolution: float) -> Index3:
    return tuple(int(round((point[i] - lower[i]) / resolution)) for i in range(3))  # type: ignore[return-value]


def index_to_point(index: Index3, lower: list[float], resolution: float) -> list[float]:
    return [lower[i] + resolution * index[i] for i in range(3)]


def index_limits(lower: list[float], upper: list[float], resolution: float) -> Index3:
    return tuple(int(round((upper[i] - lower[i]) / resolution)) for i in range(3))  # type: ignore[return-value]


def inside_limits(index: Index3, limits: Index3) -> bool:
    return all(0 <= index[i] <= limits[i] for i in range(3))


def sphere_distance(point: list[float], obstacle: dict[str, Any]) -> float:
    center = as_float_list(obstacle["center"])
    radius = float(obstacle["radius"])
    return norm(vector_sub(point, center)) - radius


def box_distance(point: list[float], obstacle: dict[str, Any]) -> float:
    box_min = as_float_list(obstacle["min"])
    box_max = as_float_list(obstacle["max"])
    outside = [
        max(box_min[i] - point[i], 0.0, point[i] - box_max[i])
        for i in range(3)
    ]
    outside_distance = norm(outside)
    if outside_distance > 0.0:
        return outside_distance
    inside_margin = min(point[i] - box_min[i] for i in range(3))
    inside_margin = min(inside_margin, min(box_max[i] - point[i] for i in range(3)))
    return -inside_margin


def obstacle_distance(point: list[float], obstacle: dict[str, Any]) -> float:
    obstacle_type = str(obstacle["type"])
    if obstacle_type == "sphere":
        return sphere_distance(point, obstacle)
    if obstacle_type == "box":
        return box_distance(point, obstacle)
    raise ValueError(f"Unsupported obstacle type: {obstacle_type}")


def minimum_obstacle_distance(point: list[float], obstacles: list[dict[str, Any]]) -> float:
    if not obstacles:
        return math.inf
    return min(obstacle_distance(point, obstacle) for obstacle in obstacles)


def is_collision_free_point(point: list[float], obstacles: list[dict[str, Any]], safety_margin: float) -> bool:
    return minimum_obstacle_distance(point, obstacles) >= safety_margin


def is_collision_free_segment(
    start: list[float],
    end: list[float],
    obstacles: list[dict[str, Any]],
    safety_margin: float,
    sample_step: float,
) -> bool:
    length = norm(vector_sub(end, start))
    steps = max(1, int(math.ceil(length / max(sample_step, 1e-6))))
    for step in range(steps + 1):
        alpha = step / steps
        point = [(1.0 - alpha) * start[i] + alpha * end[i] for i in range(3)]
        if not is_collision_free_point(point, obstacles, safety_margin):
            return False
    return True


def neighbor_offsets(neighbor_type: int) -> list[Index3]:
    offsets: list[Index3] = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                if dx == dy == dz == 0:
                    continue
                manhattan = abs(dx) + abs(dy) + abs(dz)
                if neighbor_type == 6 and manhattan != 1:
                    continue
                offsets.append((dx, dy, dz))
    return offsets


def astar_plan(config: dict[str, Any]) -> tuple[list[list[float]], int]:
    planner = config["planner"]
    astar = planner["astar"]
    map_config = planner["map"]
    lower, upper = map_bounds(map_config)
    resolution = float(astar["grid_resolution_m"])
    limits = index_limits(lower, upper, resolution)
    start = point_to_index(as_float_list(planner["start"]), lower, resolution)
    goal = point_to_index(as_float_list(planner["goal"]), lower, resolution)
    obstacles = list(map_config.get("obstacles", []))
    safety_margin = float(map_config.get("safety_margin_m", 0.0))
    offsets = neighbor_offsets(int(astar.get("neighbor_type", 26)))
    max_iterations = int(astar.get("max_iterations", 100000))
    tie_breaker = float(astar.get("tie_breaker", 1.0))

    if not inside_limits(start, limits) or not inside_limits(goal, limits):
        raise ValueError("start or goal is outside map bounds")
    for label, index in [("start", start), ("goal", goal)]:
        if not is_collision_free_point(index_to_point(index, lower, resolution), obstacles, safety_margin):
            raise ValueError(f"{label} is inside an inflated obstacle")

    open_heap: list[tuple[float, float, Index3]] = []
    heapq.heappush(open_heap, (0.0, 0.0, start))
    parent: dict[Index3, Index3 | None] = {start: None}
    g_cost: dict[Index3, float] = {start: 0.0}
    closed: set[Index3] = set()
    iterations = 0

    while open_heap:
        _, current_g, current = heapq.heappop(open_heap)
        if current in closed:
            continue
        closed.add(current)
        iterations += 1
        if current == goal:
            return reconstruct_path(parent, current, lower, resolution), iterations
        if iterations > max_iterations:
            break

        current_point = index_to_point(current, lower, resolution)
        for offset in offsets:
            neighbor = tuple(current[i] + offset[i] for i in range(3))  # type: ignore[assignment]
            if not inside_limits(neighbor, limits) or neighbor in closed:
                continue
            neighbor_point = index_to_point(neighbor, lower, resolution)
            if not is_collision_free_point(neighbor_point, obstacles, safety_margin):
                continue
            step_cost = norm(vector_sub(neighbor_point, current_point))
            tentative_g = current_g + step_cost
            if tentative_g >= g_cost.get(neighbor, math.inf):
                continue
            parent[neighbor] = current
            g_cost[neighbor] = tentative_g
            heuristic = norm(vector_sub(neighbor_point, index_to_point(goal, lower, resolution)))
            heapq.heappush(open_heap, (tentative_g + tie_breaker * heuristic, tentative_g, neighbor))

    raise RuntimeError(f"A* failed after {iterations} iterations")


def reconstruct_path(parent: dict[Index3, Index3 | None], current: Index3, lower: list[float], resolution: float) -> list[list[float]]:
    indices = [current]
    while parent[current] is not None:
        current = parent[current]  # type: ignore[assignment]
        indices.append(current)
    indices.reverse()
    return [index_to_point(index, lower, resolution) for index in indices]


def simplify_path(
    path: list[list[float]],
    obstacles: list[dict[str, Any]],
    safety_margin: float,
    sample_step: float,
) -> list[list[float]]:
    if len(path) <= 2:
        return path
    simplified = [path[0]]
    index = 0
    while index < len(path) - 1:
        next_index = len(path) - 1
        while next_index > index + 1:
            if is_collision_free_segment(path[index], path[next_index], obstacles, safety_margin, sample_step):
                break
            next_index -= 1
        simplified.append(path[next_index])
        index = next_index
    return simplified


def write_path(path: Path, waypoints: list[list[float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["index", "x", "y", "z"], lineterminator="\n")
        writer.writeheader()
        for index, point in enumerate(waypoints):
            writer.writerow({"index": index, "x": point[0], "y": point[1], "z": point[2]})


def obstacle_metrics(rows: list[dict[str, float]], obstacles: list[dict[str, Any]], safety_margin: float) -> dict[str, Any]:
    distances = [minimum_obstacle_distance([row["x_ref"], row["y_ref"], row["z_ref"]], obstacles) for row in rows]
    min_distance = min(distances) if distances else math.inf
    violations = sum(1 for value in distances if value < safety_margin)
    clearance_ratio = max(0.0, min(1.0, min_distance / max(safety_margin, 1e-9))) if math.isfinite(min_distance) else 1.0
    return {
        "minimum_obstacle_distance_m": min_distance if math.isfinite(min_distance) else 0.0,
        "safety_margin_m": safety_margin,
        "obstacle_violation_count": violations,
        "obstacle_avoidance_score": 100.0 * clearance_ratio,
    }


def write_replay(path: Path, config: dict[str, Any], rows: list[dict[str, float]]) -> None:
    sample_stride = max(1, len(rows) // 600)
    frames = [
        {
            "time": row["time"],
            "uav": [{"id": "astar_reference", "position": [row["x_ref"], row["y_ref"], row["z_ref"]], "yaw": row["yaw_ref"]}],
        }
        for row in rows[::sample_stride]
    ]
    payload = {
        "scene_id": config.get("scene_id", ""),
        "model_name": "A* obstacle avoidance reference",
        "description": "3D grid A* path with trackability-aware smoothstep timing",
        "source": "scripts/generate_obstacle_planning_reference.py",
        "frame_count": len(frames),
        "obstacles": config["planner"]["map"].get("obstacles", []),
        "safety_margin_m": config["planner"]["map"].get("safety_margin_m", 0.0),
        "frames": frames,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, nargs="?", default=Path("scenarios/planning/obstacle_corridor.yaml"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scenario = read_yaml(args.scenario)
    planner = scenario["planner"]
    result = scenario["result"]
    reference = scenario["reference"]
    params = read_yaml(Path(str(planner.get("params_file", "planners/waypoint/default.yaml"))))
    limits = params["limits"]
    time_alloc = params["time_allocation"]
    trackability = params.get("trackability", {})
    astar = planner["astar"]
    map_config = planner["map"]
    obstacles = list(map_config.get("obstacles", []))
    safety_margin = float(map_config.get("safety_margin_m", 0.0))

    raw_path, planning_iterations = astar_plan(scenario)
    waypoints = simplify_path(
        raw_path,
        obstacles,
        safety_margin,
        float(astar.get("collision_sample_step_m", float(astar["grid_resolution_m"]) * 0.5)),
    )
    dt = float(scenario["simulation"].get("step_size_s", 0.02))
    base_durations = allocate_segment_times(
        waypoints,
        float(time_alloc.get("velocity_reference_m_s", 2.0)),
        float(time_alloc.get("segment_time_min_s", 1.5)),
    )
    rows, report = generate_trackable_rows(
        waypoints,
        base_durations,
        dt,
        str(planner.get("yaw_mode", "fixed")),
        {key: float(value) for key, value in limits.items()},
        float(trackability.get("min_score", 0.8)),
        int(time_alloc.get("max_rescale_iterations", 5)),
        float(time_alloc.get("infeasible_scale_factor", 1.25)),
        bool(trackability.get("require_zero_dynamic_violations", True)),
    )
    obs_report = obstacle_metrics(rows, obstacles, safety_margin)
    report.update(obs_report)
    report.update({
        "planner_id": scenario.get("planner_id", "astar_min_snap"),
        "scene_id": scenario.get("scene_id", ""),
        "experiment_id": scenario.get("experiment_id", ""),
        "controller_id": scenario.get("controller_id", ""),
        "raw_path_node_count": len(raw_path),
        "simplified_waypoint_count": len(waypoints),
        "planning_iterations": planning_iterations,
        "grid_resolution_m": float(astar["grid_resolution_m"]),
        "reference_file": reference.get("file", ""),
        "raw_file": result.get("raw_file", ""),
    })
    report["accepted"] = bool(report["accepted"]) and obs_report["obstacle_violation_count"] == 0
    report["total_health_score"] = 0.65 * (100.0 * float(report["final_trackability_score"])) + 0.35 * float(obs_report["obstacle_avoidance_score"])

    write_path(Path(str(result["path_file"])), raw_path)
    write_csv(Path(str(reference["file"])), rows)
    metrics_path = Path(str(result["metrics_file"]))
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_replay(Path(str(result["replay_file"])), scenario, rows)
    print(f"A* path CSV: {result['path_file']}")
    print(f"Reference CSV: {reference['file']}")
    print(f"Planning metrics: {result['metrics_file']}")
    print(f"Replay JSON: {result['replay_file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
