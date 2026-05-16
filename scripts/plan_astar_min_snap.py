#!/usr/bin/env python3
"""Generate A* obstacle-avoidance references with trackability precheck."""

from __future__ import annotations

import argparse
import csv
import heapq
import json
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


ROOT = Path(__file__).resolve().parents[1]
VERBOSE = False
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


def expand_wall_groups(config: dict[str, Any]) -> dict[str, Any]:
    """Expand reusable L/T wall-group templates into concrete collision boxes."""
    expanded = clone_jsonable(config)
    map_config = require_mapping(expanded, "map")
    wall_spec = map_config.get("wall_groups")
    if not isinstance(wall_spec, dict):
        return expanded
    if wall_spec.get("expanded", False):
        return expanded

    defaults = wall_spec.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ValueError("map.wall_groups.defaults must be a mapping")
    groups = wall_spec.get("groups", [])
    if not isinstance(groups, list):
        raise ValueError("map.wall_groups.groups must be a list")

    long_length = float(defaults.get("long_length_m", 18.0))
    short_length = float(defaults.get("short_length_m", 6.0))
    thickness = float(defaults.get("thickness_m", 0.32))
    height = float(defaults.get("height_m", 3.0))
    z_min = float(defaults.get("z_min", 0.0))
    if long_length <= 0.0 or short_length <= 0.0 or thickness <= 0.0 or height <= 0.0:
        raise ValueError("wall_groups dimensions must be positive")

    obstacles = list(map_config.get("obstacles", []))

    def box(x0: float, y0: float, x1: float, y1: float, group_id: str, arm: str) -> dict[str, Any]:
        return {
            "type": "box",
            "wall_group_id": group_id,
            "wall_arm": arm,
            "min": [round(min(x0, x1), 3), round(min(y0, y1), 3), round(z_min, 3)],
            "max": [round(max(x0, x1), 3), round(max(y0, y1), 3), round(z_min + height, 3)],
        }

    for index, group in enumerate(groups, start=1):
        if not isinstance(group, dict):
            raise ValueError("Each wall_groups.groups item must be a mapping")
        group_id = str(group.get("id", f"wall_{index:02d}"))
        shape = str(group.get("shape", "L")).upper()
        if shape not in {"L", "T"}:
            raise ValueError(f"Unsupported wall group shape: {shape}")
        long_axis = str(group.get("long_axis", "x")).lower()
        if long_axis not in {"x", "y"}:
            raise ValueError(f"Unsupported wall group long_axis: {long_axis}")
        joint = str(group.get("joint", "lower")).lower()
        if joint not in {"lower", "upper"}:
            raise ValueError(f"Unsupported wall group joint: {joint}")
        short_side = str(group.get("short_side", "positive")).lower()
        if short_side not in {"positive", "negative"}:
            raise ValueError(f"Unsupported wall group short_side: {short_side}")
        bbox_min = group.get("bbox_min")
        if not isinstance(bbox_min, list) or len(bbox_min) != 2:
            raise ValueError(f"wall group {group_id} requires bbox_min=[x,y]")
        x0 = float(bbox_min[0])
        y0 = float(bbox_min[1])

        if long_axis == "x":
            bbox_w = long_length
            bbox_h = short_length
            long_center_y = y0 + 0.5 * thickness if short_side == "positive" else y0 + short_length - 0.5 * thickness
            long_x0 = x0 + 0.5 * thickness
            long_x1 = x0 + long_length - 0.5 * thickness
            if joint == "lower":
                joint_x = long_x0
            else:
                joint_x = long_x1
            if shape == "L":
                short_center_x = joint_x
            else:
                short_center_x = joint_x
            short_x0 = short_center_x - 0.5 * thickness
            short_x1 = short_center_x + 0.5 * thickness
            if short_side == "positive":
                if shape == "L":
                    short_center_y0 = long_center_y + 0.5 * thickness
                    short_center_y1 = y0 + short_length - 0.5 * thickness
                else:
                    short_center_y0 = long_center_y - 0.5 * short_length
                    short_center_y1 = long_center_y + 0.5 * short_length
            else:
                if shape == "L":
                    short_center_y0 = y0 + 0.5 * thickness
                    short_center_y1 = long_center_y - 0.5 * thickness
                else:
                    short_center_y0 = long_center_y - 0.5 * short_length
                    short_center_y1 = long_center_y + 0.5 * short_length
            if shape == "L" and short_side == "positive":
                short_y0 = long_center_y
                short_y1 = short_center_y1 + 0.5 * thickness
            elif shape == "L":
                short_y0 = short_center_y0 - 0.5 * thickness
                short_y1 = long_center_y
            else:
                short_y0 = short_center_y0 - 0.5 * thickness
                short_y1 = short_center_y1 + 0.5 * thickness
            long_arm = box(long_x0, long_center_y - 0.5 * thickness, long_x1, long_center_y + 0.5 * thickness, group_id, "long")
            short_arm = box(short_x0, short_y0, short_x1, short_y1, group_id, "short")
        else:
            bbox_w = short_length
            bbox_h = long_length
            long_center_x = x0 + 0.5 * thickness if short_side == "positive" else x0 + short_length - 0.5 * thickness
            long_y0 = y0 + 0.5 * thickness
            long_y1 = y0 + long_length - 0.5 * thickness
            if joint == "lower":
                joint_y = long_y0
            else:
                joint_y = long_y1
            if shape == "L":
                short_center_y = joint_y
            else:
                short_center_y = joint_y
            short_y0 = short_center_y - 0.5 * thickness
            short_y1 = short_center_y + 0.5 * thickness
            if short_side == "positive":
                if shape == "L":
                    short_center_x0 = long_center_x + 0.5 * thickness
                    short_center_x1 = x0 + short_length - 0.5 * thickness
                else:
                    short_center_x0 = long_center_x - 0.5 * short_length
                    short_center_x1 = long_center_x + 0.5 * short_length
            else:
                if shape == "L":
                    short_center_x0 = x0 + 0.5 * thickness
                    short_center_x1 = long_center_x - 0.5 * thickness
                else:
                    short_center_x0 = long_center_x - 0.5 * short_length
                    short_center_x1 = long_center_x + 0.5 * short_length
            if shape == "L" and short_side == "positive":
                short_x0 = long_center_x
                short_x1 = short_center_x1 + 0.5 * thickness
            elif shape == "L":
                short_x0 = short_center_x0 - 0.5 * thickness
                short_x1 = long_center_x
            else:
                short_x0 = short_center_x0 - 0.5 * thickness
                short_x1 = short_center_x1 + 0.5 * thickness
            long_arm = box(long_center_x - 0.5 * thickness, long_y0, long_center_x + 0.5 * thickness, long_y1, group_id, "long")
            short_arm = box(short_x0, short_y0, short_x1, short_y1, group_id, "short")

        group["bbox_max"] = [round(x0 + bbox_w, 3), round(y0 + bbox_h, 3)]
        obstacles.extend([long_arm, short_arm])

    map_config["obstacles"] = obstacles
    wall_spec["expanded"] = True
    wall_spec["expanded_box_count"] = 2 * len(groups)
    return expanded


def expand_random_obstacles(config: dict[str, Any]) -> dict[str, Any]:
    """Expand a reproducible random obstacle specification into concrete obstacles."""
    expanded = clone_jsonable(config)
    map_config = require_mapping(expanded, "map")
    random_spec = map_config.get("random_obstacles")
    if not isinstance(random_spec, dict) or not random_spec.get("enabled", False):
        return expanded
    start_t = time.perf_counter()

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
    distribution = str(random_spec.get("distribution", "uniform"))
    clear_corridors = random_spec.get("clear_corridors", [])
    if clear_corridors is None:
        clear_corridors = []
    if not isinstance(clear_corridors, list):
        raise ValueError("random_obstacles.clear_corridors must be a list")
    grid_cells = random_spec.get("grid_cells", [1, 1])
    if not isinstance(grid_cells, list) or len(grid_cells) != 2:
        raise ValueError("random_obstacles.grid_cells must be [x_cells, y_cells]")
    grid_x = max(1, int(grid_cells[0]))
    grid_y = max(1, int(grid_cells[1]))
    obstacles = list(map_config.get("obstacles", []))
    random_added = 0

    def distance_to_segment_xy(x: float, y: float, a: Point, b: Point) -> float:
        vx = b.x - a.x
        vy = b.y - a.y
        length2 = vx * vx + vy * vy
        if length2 <= 1e-12:
            return math.hypot(x - a.x, y - a.y)
        t = max(0.0, min(1.0, ((x - a.x) * vx + (y - a.y) * vy) / length2))
        closest_x = a.x + t * vx
        closest_y = a.y + t * vy
        return math.hypot(x - closest_x, y - closest_y)

    def inside_clear_corridor(x: float, y: float, radius: float) -> bool:
        for corridor in clear_corridors:
            if not isinstance(corridor, dict):
                raise ValueError("Each random_obstacles.clear_corridors entry must be a mapping")
            kind = corridor.get("type")
            if kind == "segment":
                a_values = corridor.get("start")
                b_values = corridor.get("end")
                if not isinstance(a_values, list) or not isinstance(b_values, list):
                    raise ValueError("segment clear corridor requires start/end")
                a = Point(float(a_values[0]), float(a_values[1]), start.z)
                b = Point(float(b_values[0]), float(b_values[1]), start.z)
                width = float(corridor.get("width_m", 0.0))
                if distance_to_segment_xy(x, y, a, b) <= 0.5 * width + radius:
                    return True
            elif kind == "box":
                lo = corridor.get("min")
                hi = corridor.get("max")
                if not isinstance(lo, list) or not isinstance(hi, list):
                    raise ValueError("box clear corridor requires min/max")
                x0, x1 = sorted((float(lo[0]), float(hi[0])))
                y0, y1 = sorted((float(lo[1]), float(hi[1])))
                if x0 - radius <= x <= x1 + radius and y0 - radius <= y <= y1 + radius:
                    return True
            else:
                raise ValueError(f"Unsupported clear_corridors type: {kind}")
        return False

    def can_place(x: float, y: float, radius: float) -> bool:
        center = Point(x, y, start.z)
        if distance(center, start) < start_goal_clearance or distance(center, goal) < start_goal_clearance:
            return False
        if inside_clear_corridor(x, y, radius):
            return False
        for obstacle in obstacles:
            ox, oy = obstacle_xy_center(obstacle)
            if math.hypot(x - ox, y - oy) < min_spacing + radius + obstacle_xy_radius(obstacle):
                return False
        return True

    def append_obstacle(x: float, y: float, radius: float) -> None:
        nonlocal random_added
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
        random_added += 1

    if distribution == "stratified":
        x0 = x_min + edge_margin
        x1 = x_max - edge_margin
        y0 = y_min + edge_margin
        y1 = y_max - edge_margin
        if x1 <= x0 or y1 <= y0:
            raise ValueError("random_obstacles edge margin leaves no placement area")
        cell_w = (x1 - x0) / grid_x
        cell_h = (y1 - y0) / grid_y
        cell_indices = [(ix, iy) for iy in range(grid_y) for ix in range(grid_x)]
        attempts_per_cell = int(random_spec.get("attempts_per_cell", 16))
        pass_index = 0
        while random_added < count and pass_index < max(1, math.ceil(count / len(cell_indices))) + 3:
            rng.shuffle(cell_indices)
            for ix, iy in cell_indices:
                if random_added >= count:
                    break
                for _ in range(attempts_per_cell):
                    radius = rng.uniform(radius_min, radius_max)
                    x = rng.uniform(x0 + ix * cell_w + radius, x0 + (ix + 1) * cell_w - radius)
                    y = rng.uniform(y0 + iy * cell_h + radius, y0 + (iy + 1) * cell_h - radius)
                    if can_place(x, y, radius):
                        append_obstacle(x, y, radius)
                        break
            pass_index += 1

    attempts = 0
    while random_added < count and attempts < count * 800:
        attempts += 1
        radius = rng.uniform(radius_min, radius_max)
        x = rng.uniform(x_min + edge_margin, x_max - edge_margin)
        y = rng.uniform(y_min + edge_margin, y_max - edge_margin)
        if can_place(x, y, radius):
            append_obstacle(x, y, radius)

    if random_added < count:
        raise RuntimeError(f"Generated only {random_added} random obstacles, requested {count}")
    map_config["obstacles"] = obstacles
    random_spec["enabled"] = False
    random_spec["expanded"] = True
    random_spec["expanded_count"] = random_added
    if VERBOSE:
        print(f"[planner] random_obstacles expanded fixed={len(map_config.get('obstacles', [])) - random_added} random={random_added} total={len(obstacles)} elapsed={time.perf_counter() - start_t:.3f}s", flush=True)
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
        self._occupied_cache: dict[GridIndex, bool] = {}
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
        cached = self._occupied_cache.get(index)
        if cached is not None:
            return cached
        occupied = self.is_occupied_point(self.point_from_index(index))
        self._occupied_cache[index] = occupied
        return occupied


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
    progress_penalty = float(astar_config.get("progress_penalty", 0.0))
    max_iterations = int(astar_config.get("max_iterations", 200000))
    start_point = grid.point_from_index(start)
    goal_point = grid.point_from_index(goal)
    goal_vector_x = goal_point.x - start_point.x
    goal_vector_y = goal_point.y - start_point.y
    search_margin_m = float(astar_config.get("search_margin_m", 0.0))
    if search_margin_m > 0.0:
        search_x_min = max(grid.x_min, min(start_point.x, goal_point.x) - search_margin_m)
        search_x_max = min(grid.x_max, max(start_point.x, goal_point.x) + search_margin_m)
        search_y_min = max(grid.y_min, min(start_point.y, goal_point.y) - search_margin_m)
        search_y_max = min(grid.y_max, max(start_point.y, goal_point.y) + search_margin_m)
    else:
        search_x_min, search_x_max = grid.x_min, grid.x_max
        search_y_min, search_y_max = grid.y_min, grid.y_max
    goal_norm = math.hypot(goal_vector_x, goal_vector_y)
    if goal_norm > 1e-9:
        goal_vector_x /= goal_norm
        goal_vector_y /= goal_norm
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
            if not (search_x_min <= neighbor_point.x <= search_x_max and search_y_min <= neighbor_point.y <= search_y_max):
                continue
            if not segment_collision_free(grid, current_point, neighbor_point):
                continue
            step_cost = distance(current_point, neighbor_point)
            if progress_penalty > 0.0 and goal_norm > 1e-9:
                progress = (neighbor_point.x - current_point.x) * goal_vector_x + (neighbor_point.y - current_point.y) * goal_vector_y
                if progress < 0.0:
                    step_cost += progress_penalty * abs(progress)
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


def segment_min_obstacle_distance(grid: OccupancyGrid, a: Point, b: Point) -> float:
    length = distance(a, b)
    steps = max(1, int(math.ceil(length / (grid.resolution / 2.0))))
    best = float("inf")
    for i in range(steps + 1):
        ratio = i / steps
        point = Point(a.x + (b.x - a.x) * ratio, a.y + (b.y - a.y) * ratio, a.z + (b.z - a.z) * ratio)
        best = min(best, min_obstacle_distance(point, grid.obstacles))
    return best


def min_segment_path_distance(grid: OccupancyGrid, path: list[Point]) -> float:
    if len(path) < 2:
        return min_obstacle_distance(path[0], grid.obstacles) if path else float("inf")
    return min(segment_min_obstacle_distance(grid, a, b) for a, b in zip(path[:-1], path[1:]))


def path_smoothness(path: list[Point]) -> float:
    if len(path) < 3:
        return 0.0
    total = 0.0
    for a, b, c in zip(path[:-2], path[1:-1], path[2:]):
        total += (a.x - 2.0 * b.x + c.x) ** 2 + (a.y - 2.0 * b.y + c.y) ** 2
    return total


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


def resample_polyline(path: list[Point], spacing_m: float) -> list[Point]:
    if len(path) <= 2 or spacing_m <= 0.0:
        return path
    total = path_length(path)
    if total <= spacing_m:
        return path
    target_count = max(2, int(math.ceil(total / spacing_m)) + 1)
    samples = [path[0]]
    segment_index = 0
    segment_start_distance = 0.0
    segment_length = distance(path[0], path[1])
    for sample_index in range(1, target_count - 1):
        target_distance = total * sample_index / (target_count - 1)
        while segment_index < len(path) - 2 and segment_start_distance + segment_length < target_distance:
            segment_start_distance += segment_length
            segment_index += 1
            segment_length = distance(path[segment_index], path[segment_index + 1])
        ratio = 0.0 if segment_length <= 1e-9 else (target_distance - segment_start_distance) / segment_length
        a = path[segment_index]
        b = path[segment_index + 1]
        samples.append(Point(a.x + (b.x - a.x) * ratio, a.y + (b.y - a.y) * ratio, a.z + (b.z - a.z) * ratio))
    samples.append(path[-1])
    return samples


def nearest_obstacle_gradient(point: Point, obstacle: dict[str, Any]) -> tuple[float, float]:
    kind = obstacle.get("type")
    if kind == "box":
        lo = point_from(obstacle["min"])
        hi = point_from(obstacle["max"])
        cx = min(max(point.x, lo.x), hi.x)
        cy = min(max(point.y, lo.y), hi.y)
        vx = point.x - cx
        vy = point.y - cy
        norm = math.hypot(vx, vy)
        if norm > 1e-9:
            return vx / norm, vy / norm
        clearances = [
            (abs(point.x - lo.x), -1.0, 0.0),
            (abs(hi.x - point.x), 1.0, 0.0),
            (abs(point.y - lo.y), 0.0, -1.0),
            (abs(hi.y - point.y), 0.0, 1.0),
        ]
        _, gx, gy = min(clearances, key=lambda item: item[0])
        return gx, gy
    if kind in {"cylinder", "sphere"}:
        center = point_from(obstacle["center"])
        vx = point.x - center.x
        vy = point.y - center.y
        norm = math.hypot(vx, vy)
        if norm > 1e-9:
            return vx / norm, vy / norm
    return 1.0, 0.0


def min_obstacle_distance_and_gradient(point: Point, obstacles: list[dict[str, Any]]) -> tuple[float, tuple[float, float]]:
    if not obstacles:
        return float("inf"), (1.0, 0.0)
    nearest = min(obstacles, key=lambda obstacle: obstacle_distance(point, obstacle))
    return obstacle_distance(point, nearest), nearest_obstacle_gradient(point, nearest)


def nearest_obstacle(point: Point, obstacles: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not obstacles:
        return None
    return min(obstacles, key=lambda obstacle: obstacle_distance(point, obstacle))


def clamp_to_bounds(point: Point, grid: OccupancyGrid) -> Point:
    return Point(
        max(grid.x_min, min(grid.x_max, point.x)),
        max(grid.y_min, min(grid.y_max, point.y)),
        grid.z_plan,
    )


def segment_closest_sample(grid: OccupancyGrid, a: Point, b: Point) -> tuple[float, Point, dict[str, Any] | None]:
    length = distance(a, b)
    steps = max(1, int(math.ceil(length / (grid.resolution / 3.0))))
    best_distance = float("inf")
    best_point = a
    best_obstacle: dict[str, Any] | None = None
    for i in range(steps + 1):
        ratio = i / steps
        point = Point(a.x + (b.x - a.x) * ratio, a.y + (b.y - a.y) * ratio, a.z + (b.z - a.z) * ratio)
        obstacle = nearest_obstacle(point, grid.obstacles)
        current_distance = obstacle_distance(point, obstacle) if obstacle is not None else float("inf")
        if current_distance < best_distance:
            best_distance = current_distance
            best_point = point
            best_obstacle = obstacle
    return best_distance, best_point, best_obstacle


def insert_clearance_waypoints(
    grid: OccupancyGrid,
    path: list[Point],
    required_margin: float,
    max_segments: int,
    max_insertions: int = 24,
) -> tuple[list[Point], int]:
    """Insert local detour points for segments that are safe as a polyline but unsafe after smoothing."""
    repaired = list(path)
    insertions = 0
    while insertions < max_insertions and len(repaired) < max_segments + 1:
        worst_index = -1
        worst_distance = float("inf")
        worst_point = repaired[0]
        worst_obstacle: dict[str, Any] | None = None
        for index, (a, b) in enumerate(zip(repaired[:-1], repaired[1:])):
            current_distance, point, obstacle = segment_closest_sample(grid, a, b)
            if current_distance < worst_distance:
                worst_distance = current_distance
                worst_index = index
                worst_point = point
                worst_obstacle = obstacle
        if worst_distance >= required_margin or worst_index < 0 or worst_obstacle is None:
            break

        grad_x, grad_y = nearest_obstacle_gradient(worst_point, worst_obstacle)
        gap = required_margin - worst_distance
        detour = clamp_to_bounds(
            Point(
                worst_point.x + grad_x * max(0.45, gap + 0.35),
                worst_point.y + grad_y * max(0.45, gap + 0.35),
                worst_point.z,
            ),
            grid,
        )
        a = repaired[worst_index]
        b = repaired[worst_index + 1]
        if (
            segment_min_obstacle_distance(grid, a, detour) >= required_margin
            and segment_min_obstacle_distance(grid, detour, b) >= required_margin
        ):
            repaired.insert(worst_index + 1, detour)
            insertions += 1
        else:
            break
    return repaired, insertions


def ego_optimize_path(
    grid: OccupancyGrid,
    guide_path: list[Point],
    ego_config: dict[str, Any],
) -> tuple[list[Point], dict[str, Any]]:
    """EGO-inspired ESDF-free local smoothing around an A* guide path.

    This ports the useful planner behavior into a dependency-free project script:
    keep the A* guide as the topological seed, optimize intermediate waypoints with
    smoothness, guide-fitness, and geometric collision-clearance costs, then only
    accept the result if the final path is still collision-free against the truth map.
    """
    if not ego_config.get("enabled", False) or len(guide_path) <= 2:
        return guide_path, {"ego_planner_enabled": bool(ego_config.get("enabled", False)), "ego_optimizer_accepted": False}

    spacing = float(ego_config.get("control_point_spacing_m", 1.2))
    max_segments = int(ego_config.get("max_segments", ego_config.get("max_control_points", 20)))
    max_points = max_segments + 1
    control_points = list(guide_path) if len(guide_path) <= max_points else resample_polyline(guide_path, spacing)
    if len(control_points) > max_points:
        control_points = resample_polyline(guide_path, max(path_length(guide_path) / max(1, max_points - 1), spacing))
    guide_points = list(control_points)
    iterations = int(ego_config.get("max_iterations", 80))
    step_size = float(ego_config.get("step_size", 0.08))
    clearance = float(ego_config.get("clearance_m", grid.safety_margin))
    lambda_smooth = float(ego_config.get("lambda_smooth", 0.35))
    lambda_collision = float(ego_config.get("lambda_collision", 1.8))
    lambda_fitness = float(ego_config.get("lambda_fitness", 0.18))
    max_step = float(ego_config.get("max_step_m", 0.12))
    accept_margin = float(ego_config.get("accept_safety_margin_m", grid.safety_margin))

    points = list(control_points)
    best_points = list(points)
    best_min_distance = min_segment_path_distance(grid, points)
    best_objective = path_smoothness(points)
    for _ in range(iterations):
        updated = list(points)
        max_delta = 0.0
        for i in range(1, len(points) - 1):
            p = points[i]
            prev_p = points[i - 1]
            next_p = points[i + 1]
            guide_p = guide_points[i]
            grad_x = lambda_smooth * (2.0 * p.x - prev_p.x - next_p.x) + lambda_fitness * (p.x - guide_p.x)
            grad_y = lambda_smooth * (2.0 * p.y - prev_p.y - next_p.y) + lambda_fitness * (p.y - guide_p.y)
            clearance_distance, clearance_grad = min_obstacle_distance_and_gradient(p, grid.obstacles)
            if clearance_distance < clearance:
                gap = clearance - clearance_distance
                grad_x -= lambda_collision * gap * clearance_grad[0]
                grad_y -= lambda_collision * gap * clearance_grad[1]
            delta_x = max(-max_step, min(max_step, -step_size * grad_x))
            delta_y = max(-max_step, min(max_step, -step_size * grad_y))
            candidate = clamp_to_bounds(Point(p.x + delta_x, p.y + delta_y, p.z), grid)
            if (
                segment_min_obstacle_distance(grid, updated[i - 1], candidate) >= accept_margin
                and segment_min_obstacle_distance(grid, candidate, points[i + 1]) >= accept_margin
            ):
                updated[i] = candidate
                max_delta = max(max_delta, math.hypot(candidate.x - p.x, candidate.y - p.y))
        points = updated
        current_min_distance = min_segment_path_distance(grid, points)
        current_objective = path_smoothness(points) + max(0.0, accept_margin - current_min_distance) * 1000.0
        if current_min_distance >= accept_margin and current_objective <= best_objective:
            best_min_distance = current_min_distance
            best_objective = current_objective
            best_points = list(points)
        if max_delta < float(ego_config.get("convergence_tol_m", 1e-3)):
            break

    optimized = list(best_points)
    for _ in range(3):
        changed = False
        for i in range(1, len(optimized) - 1):
            if (
                segment_min_obstacle_distance(grid, optimized[i - 1], optimized[i]) < accept_margin
                or segment_min_obstacle_distance(grid, optimized[i], optimized[i + 1]) < accept_margin
            ):
                optimized[i] = guide_points[i]
                changed = True
        if not changed:
            break
    segment_min_distance = min_segment_path_distance(grid, optimized)
    collision_free = segment_min_distance > 0.0
    accepted = segment_min_distance >= accept_margin
    report = {
        "ego_planner_enabled": True,
        "ego_optimizer_accepted": accepted,
        "ego_source": "EGO-Planner-inspired ESDF-free B-spline/local trajectory optimization",
        "ego_control_point_count": len(optimized),
        "ego_clearance_m": clearance,
        "ego_accept_safety_margin_m": accept_margin,
        "ego_min_control_point_distance_m": best_min_distance,
        "ego_min_segment_distance_m": segment_min_distance,
        "ego_iterations": iterations,
    }
    if not accepted:
        report["ego_reject_reason"] = "optimized path failed segment collision or safety-margin check; using A* guide path"
        return guide_path, report
    return optimized, report


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


def generate_reference(
    path: list[Point],
    limits: dict[str, Any],
    sample_dt: float,
    scale: float,
    yaw_mode: str,
    smoothing_type: str = "quintic_segment",
) -> list[dict[str, float]]:
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
            if smoothing_type == "linear_segment":
                ratio = min(1.0, max(0.0, tau / max(duration, 1e-9)))
                px = a.x + (b.x - a.x) * ratio
                py = a.y + (b.y - a.y) * ratio
                pz = a.z + (b.z - a.z) * ratio
                vx = (b.x - a.x) / max(duration, 1e-9)
                vy = (b.y - a.y) / max(duration, 1e-9)
                vz = (b.z - a.z) / max(duration, 1e-9)
                ax = ay = az = 0.0
                jx = jy = jz = 0.0
            else:
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


def planning_terrain_height_xy(x: float, y: float) -> float:
    """Match the static planning-map terrain used by generate_static_planning_map.py."""
    terrain_height_min_m = 0.10
    terrain_height_max_m = 0.80
    terrain_height_span_m = terrain_height_max_m - terrain_height_min_m
    terrain_vis_cell_m = 0.20
    terrain_step_m = 0.01
    ix = math.floor((x + 45.0) / terrain_vis_cell_m)
    iy = math.floor((y + 30.0) / terrain_vis_cell_m)
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
    smooth_height = terrain_height_min_m + terrain_height_span_m * normalized
    stepped_height = round(smooth_height / terrain_step_m) * terrain_step_m
    return max(terrain_height_min_m, min(terrain_height_max_m, stepped_height))


def apply_altitude_profile(path: list[Point], altitude_config: dict[str, Any] | None) -> tuple[list[Point], dict[str, Any]]:
    if not altitude_config or altitude_config.get("mode", "constant") == "constant":
        return path, {"altitude_profile_mode": "constant"}
    mode = str(altitude_config.get("mode", "constant"))
    if mode != "terrain_follow_agl":
        raise ValueError(f"Unsupported altitude_profile.mode: {mode}")
    agl_m = float(altitude_config.get("agl_m", 1.0))
    min_z_m = float(altitude_config.get("min_z_m", agl_m))
    max_z_m = float(altitude_config.get("max_z_m", agl_m + 1.0))
    profiled = [
        Point(point.x, point.y, max(min_z_m, min(max_z_m, planning_terrain_height_xy(point.x, point.y) + agl_m)))
        for point in path
    ]
    z_values = [point.z for point in profiled]
    return profiled, {
        "altitude_profile_mode": mode,
        "altitude_terrain_source": str(altitude_config.get("terrain_source", "static_planning_map")),
        "altitude_agl_m": agl_m,
        "altitude_min_z_m": min_z_m,
        "altitude_max_z_m": max_z_m,
        "altitude_reference_min_z_m": min(z_values) if z_values else 0.0,
        "altitude_reference_max_z_m": max(z_values) if z_values else 0.0,
    }


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
    start_t = time.perf_counter()
    config = expand_wall_groups(config)
    config = expand_random_obstacles(config)
    if VERBOSE:
        print(f"[planner] expand done elapsed={time.perf_counter() - start_t:.3f}s", flush=True)
    grid = OccupancyGrid(require_mapping(config, "map"))
    planning_config = clone_jsonable(config)
    planning_map = require_mapping(planning_config, "map")
    if "planning_safety_margin" in planning_map:
        planning_map["safety_margin"] = float(planning_map["planning_safety_margin"])
    local_config = require_mapping(config, "local_planning")
    if local_config.get("enabled", False):
        if VERBOSE:
            print("[planner] local receding-horizon start", flush=True)
        raw_path, simplified, iterations, local_report, planning_grid = plan_receding_horizon(planning_config, grid, local_config)
        if VERBOSE:
            print(f"[planner] local receding-horizon done raw={len(raw_path)} simplified={len(simplified)} iterations={iterations} replans={local_report.get('local_replan_count')} elapsed={time.perf_counter() - start_t:.3f}s", flush=True)
        max_segment_length_m = float(local_config.get("max_simplified_segment_length_m", 0.0))
        if max_segment_length_m <= 0.0:
            max_segment_length_m = None
    else:
        planning_grid = OccupancyGrid(planning_map)
        raw_path, iterations = astar(planning_grid, require_mapping(config, "astar"))
        simplified = line_of_sight_simplify(planning_grid, raw_path)
        local_report = {"local_planning_enabled": False}
        max_segment_length_m = None
    ego_config = require_mapping(config, "ego_planner")
    if VERBOSE:
        print("[planner] ego optimize start", flush=True)
    simplified, ego_report = ego_optimize_path(planning_grid, simplified, ego_config)
    if VERBOSE:
        print(f"[planner] ego optimize done points={len(simplified)} accepted={ego_report.get('ego_optimizer_accepted')} elapsed={time.perf_counter() - start_t:.3f}s", flush=True)
    max_model_segments = int(config.get("model_segment_limit", 5))
    simplified_before_fit = simplified
    simplified = fit_segment_limit(planning_grid, simplified, max_model_segments, max_segment_length_m)
    repair_margin = max(float(config["map"]["safety_margin"]), float(ego_config.get("accept_safety_margin_m", config["map"]["safety_margin"])))
    simplified, clearance_repair_insertions = insert_clearance_waypoints(
        planning_grid,
        simplified,
        repair_margin,
        max_model_segments,
    )
    simplified, altitude_report = apply_altitude_profile(
        simplified,
        config.get("altitude_profile") if isinstance(config.get("altitude_profile"), dict) else None,
    )
    limits = require_mapping(config, "limits")
    smoothing = require_mapping(config, "smoothing")
    smoothing_type = str(smoothing.get("type", "quintic_segment"))
    sample_dt = float(smoothing.get("sample_dt_s", 0.05))
    yaw_mode = str(smoothing.get("yaw_mode", "face_velocity"))
    scale = 1.0
    report: dict[str, Any] = {}
    for attempt in range(int(limits.get("max_rescale_iterations", 5)) + 1):
        if VERBOSE:
            print(f"[planner] evaluate attempt={attempt} scale={scale:.3f}", flush=True)
        rows = generate_reference(simplified, limits, sample_dt, scale, yaw_mode, smoothing_type)
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
            "clearance_repair_insertions": clearance_repair_insertions,
            "clearance_repair_margin_m": repair_margin,
            "path_length_m": path_length(simplified),
            "safety_margin_m": grid.safety_margin,
            "smoothing_type": smoothing_type,
            "truth_obstacles": grid.obstacles,
            "simplified_path": [point.as_tuple() for point in simplified],
            "segment_durations": segment_durations(simplified, limits, scale),
            **local_report,
            **ego_report,
            **altitude_report,
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
        if obstacle_distance(position, obstacle) <= window_radius_m:
            discovered.add(index)
    return discovered


def discovered_obstacles_along_segment(
    truth_obstacles: list[dict[str, Any]],
    start: Point,
    end: Point,
    known_indices: set[int],
    window_radius_m: float,
    step_m: float,
) -> set[int]:
    discovered = set(known_indices)
    length = distance(start, end)
    steps = max(1, int(math.ceil(length / max(step_m, 1e-6))))
    for step in range(steps + 1):
        ratio = step / steps
        position = Point(
            start.x + (end.x - start.x) * ratio,
            start.y + (end.y - start.y) * ratio,
            start.z + (end.z - start.z) * ratio,
        )
        discovered = discovered_obstacles(truth_obstacles, position, discovered, window_radius_m)
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
    local_goal_horizon_m = float(local_config.get("local_goal_horizon_m", 0.0))
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
    blocked_retry_count = 0

    while distance(current, goal) > goal_tolerance_m:
        if replan_count >= max_replans:
            raise RuntimeError(f"local planning exceeded max_replans={max_replans}")
        known_indices = discovered_obstacles(truth_obstacles, current, known_indices, window_radius_m)
        local_map = clone_jsonable(map_config)
        distance_to_goal = distance(current, goal)
        local_goal = goal
        if local_goal_horizon_m > 0.0 and distance_to_goal > local_goal_horizon_m:
            ratio = local_goal_horizon_m / distance_to_goal
            local_goal = Point(
                current.x + (goal.x - current.x) * ratio,
                current.y + (goal.y - current.y) * ratio,
                current.z + (goal.z - current.z) * ratio,
            )
        local_map["start"] = [current.x, current.y, current.z]
        local_map["obstacles"] = [truth_obstacles[index] for index in sorted(known_indices)]
        local_grid: OccupancyGrid | None = None
        segment_raw: list[Point] | None = None
        iterations = 0
        goal_candidates = [local_goal]
        if local_goal_horizon_m > 0.0 and distance_to_goal > local_goal_horizon_m:
            for horizon_scale in [0.75, 0.5, 0.3]:
                ratio = horizon_scale * local_goal_horizon_m / distance_to_goal
                goal_candidates.append(
                    Point(
                        current.x + (goal.x - current.x) * ratio,
                        current.y + (goal.y - current.y) * ratio,
                        current.z + (goal.z - current.z) * ratio,
                    )
                )
        last_error: Exception | None = None
        for candidate_goal in goal_candidates:
            try:
                local_map["goal"] = [candidate_goal.x, candidate_goal.y, candidate_goal.z]
                candidate_grid = OccupancyGrid(local_map)
                if VERBOSE and (replan_count < 5 or replan_count % 10 == 0):
                    print(
                        f"[planner] replan={replan_count} current=({current.x:.2f},{current.y:.2f}) local_goal=({candidate_goal.x:.2f},{candidate_goal.y:.2f}) known={len(known_indices)}",
                        flush=True,
                    )
                candidate_raw, candidate_iterations = astar(candidate_grid, astar_config)
                local_goal = candidate_goal
                local_grid = candidate_grid
                segment_raw = candidate_raw
                iterations = candidate_iterations
                break
            except (RuntimeError, ValueError) as exc:
                last_error = exc
                continue
        if segment_raw is None or local_grid is None:
            raise RuntimeError(f"local planner failed for all local-goal candidates near ({current.x:.2f},{current.y:.2f}): {last_error}")
        total_iterations += iterations
        raw_path.extend(segment_raw[1:])
        if len(segment_raw) < 2:
            break
        committed = segment_raw[-1]
        traveled = 0.0
        previous_point = current
        commit_polyline = [current]
        for point in segment_raw[1:]:
            step = distance(previous_point, point)
            traveled += step
            committed = point
            commit_polyline.append(point)
            known_indices = discovered_obstacles_along_segment(
                truth_obstacles,
                previous_point,
                point,
                known_indices,
                window_radius_m,
                max(truth_grid.resolution, 0.4),
            )
            previous_point = point
            if traveled >= commit_distance_m:
                break
        if distance(committed, current) <= 1e-9:
            raise RuntimeError("local planner did not advance")
        post_commit_map = clone_jsonable(map_config)
        post_commit_map["start"] = [committed.x, committed.y, committed.z]
        post_commit_map["goal"] = [local_goal.x, local_goal.y, local_goal.z]
        post_commit_map["obstacles"] = [truth_obstacles[index] for index in sorted(known_indices)]
        try:
            post_commit_grid = OccupancyGrid(post_commit_map)
            committed_unsafe = post_commit_grid.is_occupied_point(committed)
            committed_segment_unsafe = min_segment_path_distance(post_commit_grid, commit_polyline) < post_commit_grid.safety_margin
        except ValueError:
            committed_unsafe = True
            committed_segment_unsafe = True
        truth_segment_unsafe = min_segment_path_distance(truth_grid, commit_polyline) < truth_grid.safety_margin
        if truth_grid.is_occupied_point(committed) or committed_unsafe or committed_segment_unsafe or truth_segment_unsafe:
            previous_known_count = len(known_indices)
            segment_distance = float("inf")
            segment_point = commit_polyline[0]
            segment_obstacle = None
            for segment_start, segment_end in zip(commit_polyline[:-1], commit_polyline[1:]):
                current_distance, current_point, current_obstacle = segment_closest_sample(truth_grid, segment_start, segment_end)
                if current_distance < segment_distance:
                    segment_distance = current_distance
                    segment_point = current_point
                    segment_obstacle = current_obstacle
            known_indices = discovered_obstacles_along_segment(
                truth_obstacles,
                current,
                committed,
                known_indices,
                window_radius_m,
                max(truth_grid.resolution, 0.4),
            )
            blocked_retry_count += 1
            if VERBOSE:
                obstacle_label = None
                if segment_obstacle is not None:
                    obstacle_label = {
                        "type": segment_obstacle.get("type"),
                        "wall_group_id": segment_obstacle.get("wall_group_id"),
                        "wall_arm": segment_obstacle.get("wall_arm"),
                    }
                print(
                    f"[planner] blocked current=({current.x:.2f},{current.y:.2f}) committed=({committed.x:.2f},{committed.y:.2f}) "
                    f"known {previous_known_count}->{len(known_indices)} retry={blocked_retry_count} "
                    f"flags point_truth={truth_grid.is_occupied_point(committed)} point_known={committed_unsafe} "
                    f"segment_known={committed_segment_unsafe} segment_truth={truth_segment_unsafe} "
                    f"segment_min={segment_distance:.3f} nearest_point=({segment_point.x:.2f},{segment_point.y:.2f}) "
                    f"nearest_obstacle={obstacle_label}",
                    flush=True,
                )
            if blocked_retry_count > 20 and len(known_indices) == previous_known_count:
                raise RuntimeError("local planner stuck on an undiscoverable blocked segment")
            continue
        blocked_retry_count = 0
        committed_path.extend(commit_polyline[1:])
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
    expanded_config = expand_random_obstacles(expand_wall_groups(config))
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
    parser.add_argument("--verbose", action="store_true", help="Print planner stage timing")
    return parser.parse_args()


def main() -> int:
    global VERBOSE
    args = parse_args()
    VERBOSE = bool(args.verbose)
    config_path = args.config
    config = read_yaml(config_path)
    paths = write_outputs(config_path, config, args.output_dir)
    print(f"Wrote {paths['reference']}")
    print(f"Wrote {paths['trackability']}")
    print(f"Wrote {paths['preview']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
