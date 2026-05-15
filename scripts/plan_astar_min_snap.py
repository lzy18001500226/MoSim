#!/usr/bin/env python3
"""Generate A* obstacle-avoidance references with trackability precheck."""

from __future__ import annotations

import argparse
import csv
import heapq
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


ROOT = Path(__file__).resolve().parents[1]
G = 9.80665


@dataclass(frozen=True)
class Point:
    x: float
    y: float
    z: float

    def as_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)


@dataclass(frozen=True)
class GridIndex:
    ix: int
    iy: int


def read_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Planner config root must be a mapping: {path}")
    return data


def require_mapping(config: dict[str, Any], key: str) -> dict[str, Any]:
    value = config.get(key, {})
    if not isinstance(value, dict):
        raise ValueError(f"`{key}` must be a mapping")
    return value


def clone_jsonable(value: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(value))


def point_from(value: Iterable[float]) -> Point:
    items = [float(item) for item in value]
    if len(items) != 3:
        raise ValueError(f"Expected 3D point, got {value}")
    return Point(items[0], items[1], items[2])


def bounds_value(bounds: dict[str, Any], axis: str) -> tuple[float, float]:
    value = bounds.get(axis)
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError(f"bounds.{axis} must be [min, max]")
    lo = float(value[0])
    hi = float(value[1])
    if hi <= lo:
        raise ValueError(f"bounds.{axis} max must be larger than min")
    return lo, hi


def distance(a: Point, b: Point) -> float:
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)


def obstacle_distance(point: Point, obstacle: dict[str, Any]) -> float:
    kind = obstacle.get("type")
    if kind == "box":
        lo = point_from(obstacle["min"])
        hi = point_from(obstacle["max"])
        dx = max(lo.x - point.x, 0.0, point.x - hi.x)
        dy = max(lo.y - point.y, 0.0, point.y - hi.y)
        dz = max(lo.z - point.z, 0.0, point.z - hi.z)
        outside = math.sqrt(dx * dx + dy * dy + dz * dz)
        if outside > 0.0:
            return outside
        inside_margin = min(point.x - lo.x, hi.x - point.x, point.y - lo.y, hi.y - point.y, point.z - lo.z, hi.z - point.z)
        return -inside_margin
    if kind == "sphere":
        center = point_from(obstacle["center"])
        return distance(point, center) - float(obstacle["radius"])
    if kind == "cylinder":
        center = point_from(obstacle["center"])
        radius = float(obstacle["radius"])
        height = float(obstacle.get("height", 0.0))
        z_min = float(obstacle.get("z_min", center.z - height / 2.0))
        z_max = float(obstacle.get("z_max", center.z + height / 2.0))
        radial = math.hypot(point.x - center.x, point.y - center.y) - radius
        dz = max(z_min - point.z, 0.0, point.z - z_max)
        if radial <= 0.0 and dz <= 0.0:
            return max(radial, -min(point.z - z_min, z_max - point.z))
        return math.hypot(max(radial, 0.0), dz)
    raise ValueError(f"Unsupported obstacle type: {kind}")


def min_obstacle_distance(point: Point, obstacles: list[dict[str, Any]]) -> float:
    if not obstacles:
        return float("inf")
    return min(obstacle_distance(point, obstacle) for obstacle in obstacles)


def obstacle_xy_center(obstacle: dict[str, Any]) -> tuple[float, float]:
    kind = obstacle.get("type")
    if kind == "box":
        lo = point_from(obstacle["min"])
        hi = point_from(obstacle["max"])
        return ((lo.x + hi.x) / 2.0, (lo.y + hi.y) / 2.0)
    if kind in {"cylinder", "sphere"}:
        center = point_from(obstacle["center"])
        return (center.x, center.y)
    raise ValueError(f"Unsupported obstacle type: {kind}")


def obstacle_xy_radius(obstacle: dict[str, Any]) -> float:
    kind = obstacle.get("type")
    if kind == "box":
        lo = point_from(obstacle["min"])
        hi = point_from(obstacle["max"])
        return 0.5 * math.hypot(hi.x - lo.x, hi.y - lo.y)
    if kind in {"cylinder", "sphere"}:
        return float(obstacle["radius"])
    raise ValueError(f"Unsupported obstacle type: {kind}")


def expand_random_obstacles(config: dict[str, Any]) -> dict[str, Any]:
    """Expand a reproducible random obstacle specification into concrete obstacles."""
    expanded = clone_jsonable(config)
    map_config = require_mapping(expanded, "map")
    random_spec = map_config.get("random_obstacles")
    if not isinstance(random_spec, dict) or not random_spec.get("enabled", False):
        return expanded

    bounds = require_mapping(map_config, "bounds")
    x_min, x_max = bounds_value(bounds, "x")
    y_min, y_max = bounds_value(bounds, "y")
    z_min, _ = bounds_value(bounds, "z")
    start = point_from(map_config["start"])
    goal = point_from(map_config["goal"])
    rng = random.Random(int(random_spec.get("seed", map_config.get("seed", 20260515))))
    count = int(random_spec.get("count", 24))
    radius_min, radius_max = [float(v) for v in random_spec.get("radius_range", [0.28, 0.46])]
    height_min, height_max = [float(v) for v in random_spec.get("height_range", [1.5, 2.4])]
    start_goal_clearance = float(random_spec.get("start_goal_clearance_m", 1.8))
    min_spacing = float(random_spec.get("min_spacing_m", 1.05))
    edge_margin = float(random_spec.get("edge_margin_m", 0.7))
    obstacles = list(map_config.get("obstacles", []))

    attempts = 0
    while len(obstacles) < count and attempts < count * 500:
        attempts += 1
        radius = rng.uniform(radius_min, radius_max)
        x = rng.uniform(x_min + edge_margin, x_max - edge_margin)
        y = rng.uniform(y_min + edge_margin, y_max - edge_margin)
        center = Point(x, y, start.z)
        if distance(center, start) < start_goal_clearance or distance(center, goal) < start_goal_clearance:
            continue
        too_close = False
        for obstacle in obstacles:
            ox, oy = obstacle_xy_center(obstacle)
            if math.hypot(x - ox, y - oy) < min_spacing + radius + obstacle_xy_radius(obstacle):
                too_close = True
                break
        if too_close:
            continue
        height = rng.uniform(height_min, height_max)
        obstacles.append(
            {
                "type": "cylinder",
                "center": [round(x, 3), round(y, 3), round(start.z, 3)],
                "radius": round(radius, 3),
                "height": round(height, 3),
                "z_min": round(z_min, 3),
                "z_max": round(z_min + height, 3),
            }
        )

    if len(obstacles) < count:
        raise RuntimeError(f"Generated only {len(obstacles)} random obstacles, requested {count}")
    map_config["obstacles"] = obstacles
    return expanded


class OccupancyGrid:
    def __init__(self, map_config: dict[str, Any]):
        bounds = require_mapping(map_config, "bounds")
        self.x_min, self.x_max = bounds_value(bounds, "x")
        self.y_min, self.y_max = bounds_value(bounds, "y")
        self.z_min, self.z_max = bounds_value(bounds, "z")
        self.resolution = float(map_config["resolution"])
        self.safety_margin = float(map_config["safety_margin"])
        self.start = point_from(map_config["start"])
        self.goal = point_from(map_config["goal"])
        self.obstacles = list(map_config.get("obstacles", []))
        self.nx = int(round((self.x_max - self.x_min) / self.resolution)) + 1
        self.ny = int(round((self.y_max - self.y_min) / self.resolution)) + 1
        self.z_plan = self.start.z
        if not math.isclose(self.start.z, self.goal.z, abs_tol=1e-9):
            raise ValueError("P1 A* planner expects start.z == goal.z")
        if not self.in_bounds(self.start) or not self.in_bounds(self.goal):
            raise ValueError("start/goal must be inside map bounds")
        if self.is_occupied_point(self.start) or self.is_occupied_point(self.goal):
            raise ValueError("start/goal is inside inflated obstacle")

    def in_bounds(self, point: Point) -> bool:
        return self.x_min <= point.x <= self.x_max and self.y_min <= point.y <= self.y_max and self.z_min <= point.z <= self.z_max

    def index_from_point(self, point: Point) -> GridIndex:
        ix = int(round((point.x - self.x_min) / self.resolution))
        iy = int(round((point.y - self.y_min) / self.resolution))
        return GridIndex(max(0, min(self.nx - 1, ix)), max(0, min(self.ny - 1, iy)))

    def point_from_index(self, index: GridIndex) -> Point:
        return Point(self.x_min + index.ix * self.resolution, self.y_min + index.iy * self.resolution, self.z_plan)

    def is_index_valid(self, index: GridIndex) -> bool:
        return 0 <= index.ix < self.nx and 0 <= index.iy < self.ny

    def is_occupied_point(self, point: Point) -> bool:
        return min_obstacle_distance(point, self.obstacles) <= self.safety_margin

    def is_occupied_index(self, index: GridIndex) -> bool:
        return self.is_occupied_point(self.point_from_index(index))


def neighbor_offsets(neighbor_type: int) -> list[tuple[int, int]]:
    base = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if neighbor_type == 4:
        return base
    if neighbor_type == 8:
        return base + [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    raise ValueError("P1 planner supports neighbor_type 4 or 8")


def astar(grid: OccupancyGrid, astar_config: dict[str, Any]) -> tuple[list[Point], int]:
    start = grid.index_from_point(grid.start)
    goal = grid.index_from_point(grid.goal)
    offsets = neighbor_offsets(int(astar_config.get("neighbor_type", 8)))
    tie_breaker = float(astar_config.get("tie_breaker", 1.001))
    max_iterations = int(astar_config.get("max_iterations", 200000))
    open_heap: list[tuple[float, int, GridIndex]] = []
    counter = 0
    g_score: dict[GridIndex, float] = {start: 0.0}
    parent: dict[GridIndex, GridIndex | None] = {start: None}
    heapq.heappush(open_heap, (0.0, counter, start))
    closed: set[GridIndex] = set()
    iterations = 0

    while open_heap:
        iterations += 1
        if iterations > max_iterations:
            raise RuntimeError(f"A* exceeded max_iterations={max_iterations}")
        _, _, current = heapq.heappop(open_heap)
        if current in closed:
            continue
        if current == goal:
            return reconstruct_path(grid, parent, current), iterations
        closed.add(current)
        current_point = grid.point_from_index(current)
        for dx, dy in offsets:
            neighbor = GridIndex(current.ix + dx, current.iy + dy)
            if not grid.is_index_valid(neighbor) or neighbor in closed or grid.is_occupied_index(neighbor):
                continue
            neighbor_point = grid.point_from_index(neighbor)
            step_cost = distance(current_point, neighbor_point)
            tentative = g_score[current] + step_cost
            if tentative >= g_score.get(neighbor, float("inf")):
                continue
            parent[neighbor] = current
            g_score[neighbor] = tentative
            heuristic = distance(neighbor_point, grid.point_from_index(goal))
            counter += 1
            heapq.heappush(open_heap, (tentative + tie_breaker * heuristic, counter, neighbor))
    raise RuntimeError("A* failed to find a path")


def reconstruct_path(grid: OccupancyGrid, parent: dict[GridIndex, GridIndex | None], current: GridIndex) -> list[Point]:
    indices = [current]
    while parent[current] is not None:
        current = parent[current]  # type: ignore[assignment]
        indices.append(current)
    indices.reverse()
    points = [grid.point_from_index(index) for index in indices]
    points[0] = grid.start
    points[-1] = grid.goal
    return points


def segment_collision_free(grid: OccupancyGrid, a: Point, b: Point) -> bool:
    length = distance(a, b)
    steps = max(1, int(math.ceil(length / (grid.resolution / 2.0))))
    for i in range(steps + 1):
        ratio = i / steps
        point = Point(a.x + (b.x - a.x) * ratio, a.y + (b.y - a.y) * ratio, a.z + (b.z - a.z) * ratio)
        if grid.is_occupied_point(point):
            return False
    return True


def line_of_sight_simplify(
    grid: OccupancyGrid,
    path: list[Point],
    max_segment_length_m: float | None = None,
) -> list[Point]:
    if len(path) <= 2:
        return path
    simplified = [path[0]]
    i = 0
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1 and (
            not segment_collision_free(grid, path[i], path[j])
            or (
                max_segment_length_m is not None
                and distance(path[i], path[j]) > max_segment_length_m
            )
        ):
            j -= 1
        simplified.append(path[j])
        i = j
    return simplified


def fit_segment_limit(
    grid: OccupancyGrid,
    path: list[Point],
    max_segments: int,
    max_segment_length_m: float | None = None,
) -> list[Point]:
    """Reduce a collision-free polyline to the model segment limit without inventing a hand-tuned corridor."""
    if len(path) <= max_segments + 1:
        return path
    candidate = line_of_sight_simplify(grid, path, max_segment_length_m)
    if len(candidate) <= max_segments + 1:
        return candidate

    fitted = [candidate[0]]
    current_index = 0
    remaining_segments = max_segments
    while remaining_segments > 1 and current_index < len(candidate) - 1:
        max_index = len(candidate) - remaining_segments
        best_index = current_index + 1
        for next_index in range(max_index, current_index, -1):
            if segment_collision_free(grid, candidate[current_index], candidate[next_index]) and (
                max_segment_length_m is None
                or distance(candidate[current_index], candidate[next_index]) <= max_segment_length_m
            ):
                best_index = next_index
                break
        fitted.append(candidate[best_index])
        current_index = best_index
        remaining_segments -= 1
    if fitted[-1] != candidate[-1]:
        if not segment_collision_free(grid, fitted[-1], candidate[-1]) or (
            max_segment_length_m is not None
            and distance(fitted[-1], candidate[-1]) > max_segment_length_m
        ):
            raise RuntimeError(
                f"Unable to fit path with {len(candidate) - 1} simplified segments into max_segments={max_segments}"
            )
        fitted.append(candidate[-1])
    if len(fitted) > max_segments + 1:
        raise RuntimeError(f"Path fitting exceeded max_segments={max_segments}: {len(fitted) - 1}")
    return fitted


def quintic_coefficients(p0: float, p1: float, duration: float) -> tuple[float, float, float, float, float, float]:
    delta = p1 - p0
    t3 = duration**3
    t4 = duration**4
    t5 = duration**5
    return (p0, 0.0, 0.0, 10.0 * delta / t3, -15.0 * delta / t4, 6.0 * delta / t5)


def sample_quintic(coeff: tuple[float, float, float, float, float, float], tau: float) -> tuple[float, float, float, float]:
    a0, a1, a2, a3, a4, a5 = coeff
    pos = a0 + a1 * tau + a2 * tau**2 + a3 * tau**3 + a4 * tau**4 + a5 * tau**5
    vel = a1 + 2 * a2 * tau + 3 * a3 * tau**2 + 4 * a4 * tau**3 + 5 * a5 * tau**4
    acc = 2 * a2 + 6 * a3 * tau + 12 * a4 * tau**2 + 20 * a5 * tau**3
    jerk = 6 * a3 + 24 * a4 * tau + 60 * a5 * tau**2
    return pos, vel, acc, jerk


def segment_durations(path: list[Point], limits: dict[str, Any], scale: float) -> list[float]:
    v_ref = float(limits["velocity_reference_m_s"])
    t_min = float(limits["segment_time_min_s"])
    return [max(distance(a, b) / v_ref, t_min) * scale for a, b in zip(path[:-1], path[1:])]


def generate_reference(path: list[Point], limits: dict[str, Any], sample_dt: float, scale: float, yaw_mode: str) -> list[dict[str, float]]:
    durations = segment_durations(path, limits, scale)
    rows: list[dict[str, float]] = []
    elapsed = 0.0
    for seg_index, (a, b, duration) in enumerate(zip(path[:-1], path[1:], durations)):
        coeffs = [quintic_coefficients(v0, v1, duration) for v0, v1 in zip(a.as_tuple(), b.as_tuple())]
        sample_count = max(1, int(math.ceil(duration / sample_dt)))
        for k in range(sample_count):
            if seg_index > 0 and k == 0:
                continue
            tau = min(k * sample_dt, duration)
            samples = [sample_quintic(coeff, tau) for coeff in coeffs]
            px, vx, ax, jx = samples[0]
            py, vy, ay, jy = samples[1]
            pz, vz, az, jz = samples[2]
            yaw = math.atan2(vy, vx) if yaw_mode == "face_velocity" and math.hypot(vx, vy) > 1e-6 else 0.0
            rows.append(
                {
                    "time": elapsed + tau,
                    "x_ref": px,
                    "y_ref": py,
                    "z_ref": pz,
                    "vx_ref": vx,
                    "vy_ref": vy,
                    "vz_ref": vz,
                    "ax_ref": ax,
                    "ay_ref": ay,
                    "az_ref": az,
                    "jx_ref": jx,
                    "jy_ref": jy,
                    "jz_ref": jz,
                    "yaw_ref": yaw,
                }
            )
        elapsed += duration
    final = path[-1]
    rows.append(
        {
            "time": elapsed,
            "x_ref": final.x,
            "y_ref": final.y,
            "z_ref": final.z,
            "vx_ref": 0.0,
            "vy_ref": 0.0,
            "vz_ref": 0.0,
            "ax_ref": 0.0,
            "ay_ref": 0.0,
            "az_ref": 0.0,
            "jx_ref": 0.0,
            "jy_ref": 0.0,
            "jz_ref": 0.0,
            "yaw_ref": rows[-1]["yaw_ref"] if rows else 0.0,
        }
    )
    return rows


def norm3(row: dict[str, float], prefix: str) -> float:
    return math.sqrt(row[f"{prefix}x_ref"] ** 2 + row[f"{prefix}y_ref"] ** 2 + row[f"{prefix}z_ref"] ** 2)


def evaluate_reference(grid: OccupancyGrid, rows: list[dict[str, float]], limits: dict[str, Any]) -> dict[str, Any]:
    v_max = float(limits["velocity_max_m_s"])
    a_max = float(limits["acceleration_max_m_s2"])
    j_max = float(limits["jerk_max_m_s3"])
    tilt_max = float(limits["tilt_max_rad"])
    max_v = max(norm3(row, "v") for row in rows)
    max_a = max(norm3(row, "a") for row in rows)
    max_j = max(norm3(row, "j") for row in rows)
    tilts = [math.atan2(math.hypot(row["ax_ref"], row["ay_ref"]), max(1e-6, G + row["az_ref"])) for row in rows]
    max_tilt = max(tilts)
    points = [Point(row["x_ref"], row["y_ref"], row["z_ref"]) for row in rows]
    min_distance = min(min_obstacle_distance(point, grid.obstacles) for point in points)
    collision_count = sum(1 for point in points if min_obstacle_distance(point, grid.obstacles) <= 0.0)
    inflated_collision_count = sum(1 for point in points if min_obstacle_distance(point, grid.obstacles) < grid.safety_margin)
    violation_count = 0
    violation_count += sum(1 for row in rows if norm3(row, "v") > v_max)
    violation_count += sum(1 for row in rows if norm3(row, "a") > a_max)
    violation_count += sum(1 for row in rows if norm3(row, "j") > j_max)
    violation_count += sum(1 for tilt in tilts if tilt > tilt_max)
    violation_count += inflated_collision_count
    predicted_saturation_ratio = sum(1 for row in rows if math.sqrt(row["ax_ref"] ** 2 + row["ay_ref"] ** 2 + (G + row["az_ref"]) ** 2) > G * 1.45) / len(rows)
    penalties = [
        max(0.0, max_v / v_max - 1.0),
        max(0.0, max_a / a_max - 1.0),
        max(0.0, max_j / j_max - 1.0),
        max(0.0, max_tilt / tilt_max - 1.0),
        max(0.0, predicted_saturation_ratio / 0.2 - 1.0),
        max(0.0, (grid.safety_margin - min_distance) / max(grid.safety_margin, 1e-9)),
    ]
    score = max(0.0, min(1.0, 1.0 - 0.25 * sum(penalties)))
    return {
        "sample_count": len(rows),
        "duration_s": rows[-1]["time"] if rows else 0.0,
        "max_velocity_m_s": max_v,
        "max_acceleration_m_s2": max_a,
        "max_jerk_m_s3": max_j,
        "max_tilt_rad": max_tilt,
        "min_obstacle_distance_m": min_distance,
        "collision_count": collision_count,
        "inflated_collision_count": inflated_collision_count,
        "dynamic_violation_count": violation_count,
        "predicted_saturation_ratio": predicted_saturation_ratio,
        "trackability_score": score,
        "accepted": violation_count == 0 and score >= 0.8,
    }


def plan_trackable(config: dict[str, Any]) -> tuple[list[Point], list[Point], list[dict[str, float]], dict[str, Any]]:
    config = expand_random_obstacles(config)
    grid = OccupancyGrid(require_mapping(config, "map"))
    local_config = require_mapping(config, "local_planning")
    if local_config.get("enabled", False):
        raw_path, simplified, iterations, local_report, planning_grid = plan_receding_horizon(config, grid, local_config)
        max_segment_length_m = float(local_config.get("max_simplified_segment_length_m", 0.0))
        if max_segment_length_m <= 0.0:
            max_segment_length_m = None
    else:
        raw_path, iterations = astar(grid, require_mapping(config, "astar"))
        simplified = line_of_sight_simplify(grid, raw_path)
        local_report = {"local_planning_enabled": False}
        planning_grid = grid
        max_segment_length_m = None
    max_model_segments = int(config.get("model_segment_limit", 5))
    simplified_before_fit = simplified
    simplified = fit_segment_limit(planning_grid, simplified, max_model_segments, max_segment_length_m)
    limits = require_mapping(config, "limits")
    smoothing = require_mapping(config, "smoothing")
    sample_dt = float(smoothing.get("sample_dt_s", 0.05))
    yaw_mode = str(smoothing.get("yaw_mode", "face_velocity"))
    scale = 1.0
    report: dict[str, Any] = {}
    for attempt in range(int(limits.get("max_rescale_iterations", 5)) + 1):
        rows = generate_reference(simplified, limits, sample_dt, scale, yaw_mode)
        report = evaluate_reference(grid, rows, limits)
        report.update({"time_scale": scale, "rescale_iteration": attempt})
        if report["accepted"]:
            break
        scale *= float(limits.get("infeasible_scale_factor", 1.25))
    report.update(
        {
            "planner_id": config.get("planner_id", "astar_min_snap"),
            "map_id": config.get("map_id", "unknown"),
            "planning_success": True,
            "astar_iterations": iterations,
            "truth_obstacle_count": len(grid.obstacles),
            "raw_path_points": len(raw_path),
            "simplified_path_points_before_fit": len(simplified_before_fit),
            "simplified_path_points": len(simplified),
            "model_segment_limit": max_model_segments,
            "path_length_m": path_length(simplified),
            "safety_margin_m": grid.safety_margin,
            "truth_obstacles": grid.obstacles,
            "simplified_path": [point.as_tuple() for point in simplified],
            "segment_durations": segment_durations(simplified, limits, scale),
            **local_report,
        }
    )
    return raw_path, simplified, rows, report


def discovered_obstacles(
    truth_obstacles: list[dict[str, Any]],
    position: Point,
    known_indices: set[int],
    window_radius_m: float,
) -> set[int]:
    discovered = set(known_indices)
    for index, obstacle in enumerate(truth_obstacles):
        x, y = obstacle_xy_center(obstacle)
        if abs(x - position.x) <= window_radius_m and abs(y - position.y) <= window_radius_m:
            discovered.add(index)
    return discovered


def plan_receding_horizon(
    config: dict[str, Any],
    truth_grid: OccupancyGrid,
    local_config: dict[str, Any],
) -> tuple[list[Point], list[Point], int, dict[str, Any], OccupancyGrid]:
    """Plan with only locally discovered obstacles, then validate against truth."""
    map_config = clone_jsonable(require_mapping(config, "map"))
    truth_obstacles = list(map_config.get("obstacles", []))
    window_radius_m = float(local_config.get("window_radius_m", 2.5))
    commit_distance_m = float(local_config.get("commit_distance_m", 1.2))
    goal_tolerance_m = float(local_config.get("goal_tolerance_m", truth_grid.resolution))
    max_replans = int(local_config.get("max_replans", 80))
    astar_config = require_mapping(config, "astar")
    current = truth_grid.start
    goal = truth_grid.goal
    known_indices: set[int] = set()
    raw_path = [current]
    committed_path = [current]
    total_iterations = 0
    replan_count = 0

    while distance(current, goal) > goal_tolerance_m:
        if replan_count >= max_replans:
            raise RuntimeError(f"local planning exceeded max_replans={max_replans}")
        known_indices = discovered_obstacles(truth_obstacles, current, known_indices, window_radius_m)
        local_map = clone_jsonable(map_config)
        local_map["start"] = [current.x, current.y, current.z]
        local_map["obstacles"] = [truth_obstacles[index] for index in sorted(known_indices)]
        local_grid = OccupancyGrid(local_map)
        segment_raw, iterations = astar(local_grid, astar_config)
        total_iterations += iterations
        raw_path.extend(segment_raw[1:])
        if len(segment_raw) < 2:
            break
        committed = segment_raw[-1]
        traveled = 0.0
        for point in segment_raw[1:]:
            step = distance(current, point)
            traveled += step
            committed = point
            if traveled >= commit_distance_m:
                break
        if distance(committed, current) <= 1e-9:
            raise RuntimeError("local planner did not advance")
        if truth_grid.is_occupied_point(committed):
            known_indices = discovered_obstacles(truth_obstacles, committed, known_indices, window_radius_m)
            continue
        committed_path.append(committed)
        current = committed
        replan_count += 1

    if distance(committed_path[-1], goal) > 1e-9:
        committed_path.append(goal)
    final_known_map = clone_jsonable(map_config)
    final_known_map["obstacles"] = [truth_obstacles[index] for index in sorted(known_indices)]
    planning_grid = OccupancyGrid(final_known_map)
    max_segment_length_m = float(local_config.get("max_simplified_segment_length_m", 0.0))
    if max_segment_length_m <= 0.0:
        max_segment_length_m = None
    simplified = line_of_sight_simplify(planning_grid, committed_path, max_segment_length_m)
    return raw_path, simplified, total_iterations, {
        "local_planning_enabled": True,
        "local_window_radius_m": window_radius_m,
        "local_commit_distance_m": commit_distance_m,
        "local_replan_count": replan_count,
        "known_obstacle_count_final": len(known_indices),
        "truth_obstacle_count": len(truth_obstacles),
    }, planning_grid


def path_length(path: list[Point]) -> float:
    return sum(distance(a, b) for a, b in zip(path[:-1], path[1:]))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_path_csv(path: Path, points: list[Point]) -> None:
    rows = [{"index": i, "x": p.x, "y": p.y, "z": p.z} for i, p in enumerate(points)]
    write_csv(path, ["index", "x", "y", "z"], rows)


def write_reference_csv(path: Path, rows: list[dict[str, float]]) -> None:
    fields = [
        "time",
        "x_ref",
        "y_ref",
        "z_ref",
        "vx_ref",
        "vy_ref",
        "vz_ref",
        "ax_ref",
        "ay_ref",
        "az_ref",
        "jx_ref",
        "jy_ref",
        "jz_ref",
        "yaw_ref",
    ]
    write_csv(path, fields, rows)


def write_preview_svg(path: Path, grid: OccupancyGrid, raw_path: list[Point], simplified: list[Point]) -> None:
    width, height = 900, 520
    pad = 45

    def sx(x: float) -> float:
        return pad + (x - grid.x_min) / (grid.x_max - grid.x_min) * (width - 2 * pad)

    def sy(y: float) -> float:
        return height - pad - (y - grid.y_min) / (grid.y_max - grid.y_min) * (height - 2 * pad)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fbfcff"/>',
        '<style>text{font-family:Arial,Microsoft YaHei,sans-serif;font-size:14px}.label{fill:#263445}.grid{stroke:#d9e0ea;stroke-width:0.8}.obs{fill:#f08a8a;fill-opacity:.42;stroke:#b83b3b;stroke-width:2}.safe{fill:none;stroke:#d96a6a;stroke-width:1.2;stroke-dasharray:5 4}.raw{fill:none;stroke:#9aa7b8;stroke-width:1.8;stroke-dasharray:4 3}.path{fill:none;stroke:#1769aa;stroke-width:4}.pt{stroke:#102030;stroke-width:1.5}</style>',
    ]
    x = math.ceil(grid.x_min)
    while x <= grid.x_max:
        parts.append(f'<line class="grid" x1="{sx(x):.1f}" y1="{sy(grid.y_min):.1f}" x2="{sx(x):.1f}" y2="{sy(grid.y_max):.1f}"/>')
        x += 1
    y = math.ceil(grid.y_min)
    while y <= grid.y_max:
        parts.append(f'<line class="grid" x1="{sx(grid.x_min):.1f}" y1="{sy(y):.1f}" x2="{sx(grid.x_max):.1f}" y2="{sy(y):.1f}"/>')
        y += 1
    for obstacle in grid.obstacles:
        if obstacle.get("type") == "box":
            lo = point_from(obstacle["min"])
            hi = point_from(obstacle["max"])
            x0, y0 = sx(lo.x), sy(hi.y)
            x1, y1 = sx(hi.x), sy(lo.y)
            parts.append(f'<rect class="obs" x="{x0:.1f}" y="{y0:.1f}" width="{x1-x0:.1f}" height="{y1-y0:.1f}"/>')
            x0s, y0s = sx(lo.x - grid.safety_margin), sy(hi.y + grid.safety_margin)
            x1s, y1s = sx(hi.x + grid.safety_margin), sy(lo.y - grid.safety_margin)
            parts.append(f'<rect class="safe" x="{x0s:.1f}" y="{y0s:.1f}" width="{x1s-x0s:.1f}" height="{y1s-y0s:.1f}"/>')
        elif obstacle.get("type") == "cylinder":
            c = point_from(obstacle["center"])
            r = float(obstacle["radius"])
            scale_x = (width - 2 * pad) / (grid.x_max - grid.x_min)
            scale_y = (height - 2 * pad) / (grid.y_max - grid.y_min)
            parts.append(f'<circle class="obs" cx="{sx(c.x):.1f}" cy="{sy(c.y):.1f}" r="{r * min(scale_x, scale_y):.1f}"/>')
            parts.append(f'<circle class="safe" cx="{sx(c.x):.1f}" cy="{sy(c.y):.1f}" r="{(r + grid.safety_margin) * min(scale_x, scale_y):.1f}"/>')
    raw_points = " ".join(f"{sx(p.x):.1f},{sy(p.y):.1f}" for p in raw_path)
    simp_points = " ".join(f"{sx(p.x):.1f},{sy(p.y):.1f}" for p in simplified)
    parts.append(f'<polyline class="raw" points="{raw_points}"/>')
    parts.append(f'<polyline class="path" points="{simp_points}"/>')
    parts.append(f'<circle class="pt" cx="{sx(grid.start.x):.1f}" cy="{sy(grid.start.y):.1f}" r="7" fill="#2ca02c"/>')
    parts.append(f'<circle class="pt" cx="{sx(grid.goal.x):.1f}" cy="{sy(grid.goal.y):.1f}" r="7" fill="#ffbf00"/>')
    parts.append(f'<text class="label" x="{pad}" y="28">{grid.start.as_tuple()} -> {grid.goal.as_tuple()}, safety margin {grid.safety_margin:g} m</text>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def output_paths(config: dict[str, Any], output_dir: Path | None) -> dict[str, Path]:
    base = output_dir or ROOT / str(require_mapping(config, "outputs").get("base_dir", f"results/planning/{config.get('map_id', 'astar')}"))
    return {
        "raw_path": base / "raw" / "path_raw.csv",
        "path": base / "raw" / "path_simplified.csv",
        "reference": base / "raw" / "reference.csv",
        "summary": base / "metrics" / "planning_summary.json",
        "trackability": base / "metrics" / "trackability_report.json",
        "preview": base / "figures" / "map_preview.svg",
        "manifest": base / "figures" / "figure_manifest.md",
    }


def write_outputs(config_path: Path, config: dict[str, Any], output_dir: Path | None) -> dict[str, Path]:
    expanded_config = expand_random_obstacles(config)
    grid = OccupancyGrid(require_mapping(expanded_config, "map"))
    raw_path, simplified, rows, report = plan_trackable(expanded_config)
    paths = output_paths(config, output_dir)
    write_path_csv(paths["raw_path"], raw_path)
    write_path_csv(paths["path"], simplified)
    write_reference_csv(paths["reference"], rows)
    report_payload = dict(report)
    report_payload["config_file"] = str(config_path)
    report_payload["reference_csv"] = str(paths["reference"].relative_to(ROOT) if paths["reference"].is_relative_to(ROOT) else paths["reference"])
    paths["summary"].parent.mkdir(parents=True, exist_ok=True)
    paths["summary"].write_text(json.dumps(report_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    paths["trackability"].parent.mkdir(parents=True, exist_ok=True)
    paths["trackability"].write_text(json.dumps(report_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_preview_svg(paths["preview"], grid, raw_path, simplified)
    paths["manifest"].write_text(
        "# Planning Figures\n\n"
        f"- `map_preview.svg`: A* raw path, simplified path, obstacles, and safety margins for `{config.get('map_id')}`.\n",
        encoding="utf-8",
    )
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, help="Planner YAML config")
    parser.add_argument("--output-dir", type=Path, default=None, help="Override output base directory")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = args.config
    config = read_yaml(config_path)
    paths = write_outputs(config_path, config, args.output_dir)
    print(f"Wrote {paths['reference']}")
    print(f"Wrote {paths['trackability']}")
    print(f"Wrote {paths['preview']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
