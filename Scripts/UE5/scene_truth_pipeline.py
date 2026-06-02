#!/usr/bin/env python3
"""Consume Unreal scene-truth exports for mapping and unknown-map planning.

This is the file-level bridge between validated UE scene collision truth and
the MoSim mapping/planning line. It does not require a live Unreal Editor.
It creates deterministic artifacts that later runtime integrations can replay
through UE, FAST-LIO, and MWORKS.
"""

from __future__ import annotations

import argparse
import csv
import heapq
import html
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TRUTH_DIR = ROOT / "UE5/MoSimSceneLibrary/Content/MworksData/scene_truth"
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"
DEFAULT_REPLAY_STEP_SECONDS = 0.25
DEFAULT_LOCAL_KNOWN_RADIUS_M = 5.0
DEFAULT_LOCAL_KNOWN_MAX_CELLS = 320
DEFAULT_LIDAR_POINTS_MAX = 220
DEFAULT_LOCAL_PLAN_LOOKAHEAD = 8


@dataclass(frozen=True)
class Point2:
    x: float
    y: float


@dataclass(frozen=True)
class Point3:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class BoxProxy:
    proxy_id: str
    semantic_type: str
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float

    @property
    def xy_area(self) -> float:
        return max(0.0, self.max_x - self.min_x) * max(0.0, self.max_y - self.min_y)

    @property
    def height(self) -> float:
        return max(0.0, self.max_z - self.min_z)


@dataclass
class SceneProfile:
    scene_id: str
    truth_path: Path
    preferred_start: Point3
    flight_z_m: float
    roi_radius_m: float
    resolution_m: float
    safety_margin_m: float
    body_half_height_m: float
    lidar_radius_m: float
    lidar_beams: int
    local_commit_m: float
    max_replans: int
    mission_goal_min_m: float
    mission_goal_max_m: float
    control_tracking_buffer_cells: int


@dataclass
class OccupancyGrid:
    x_min: float
    y_min: float
    resolution: float
    width: int
    height: int
    occupied: list[bool]

    @property
    def x_max(self) -> float:
        return self.x_min + (self.width - 1) * self.resolution

    @property
    def y_max(self) -> float:
        return self.y_min + (self.height - 1) * self.resolution

    def index(self, x: int, y: int) -> int:
        return y * self.width + x

    def in_bounds(self, cell: tuple[int, int]) -> bool:
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height

    def is_occupied(self, cell: tuple[int, int]) -> bool:
        if not self.in_bounds(cell):
            return True
        return self.occupied[self.index(cell[0], cell[1])]

    def set_occupied(self, cell: tuple[int, int]) -> None:
        if self.in_bounds(cell):
            self.occupied[self.index(cell[0], cell[1])] = True

    def world_to_cell(self, point: Point2 | Point3) -> tuple[int, int]:
        return (
            int(round((point.x - self.x_min) / self.resolution)),
            int(round((point.y - self.y_min) / self.resolution)),
        )

    def cell_to_world(self, cell: tuple[int, int], z: float) -> Point3:
        return Point3(
            self.x_min + cell[0] * self.resolution,
            self.y_min + cell[1] * self.resolution,
            z,
        )


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def point3(values: Iterable[float]) -> Point3:
    items = [float(value) for value in values]
    if len(items) != 3:
        raise ValueError(f"expected 3 values, got {values}")
    return Point3(items[0], items[1], items[2])


def load_truth(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "mosim.unreal_scene_truth.v1":
        raise ValueError(f"unsupported truth schema in {path}: {payload.get('schema')}")
    proxies = payload.get("collision_proxies")
    if not isinstance(proxies, list) or not proxies:
        raise ValueError(f"truth file has no collision_proxies: {path}")
    return payload


def proxy_from_payload(proxy: dict[str, Any]) -> BoxProxy:
    min_m = point3(proxy["min_m"])
    max_m = point3(proxy["max_m"])
    return BoxProxy(
        proxy_id=str(proxy.get("collision_proxy_id", "")),
        semantic_type=str(proxy.get("semantic_type", "obstacle")),
        min_x=min(min_m.x, max_m.x),
        min_y=min(min_m.y, max_m.y),
        min_z=min(min_m.z, max_m.z),
        max_x=max(min_m.x, max_m.x),
        max_y=max(min_m.y, max_m.y),
        max_z=max(min_m.z, max_m.z),
    )


def default_profile(scene_id: str, truth_path: Path) -> SceneProfile:
    key = scene_id.lower()
    if key == "factoryenvironmentcollect":
        return SceneProfile(
            scene_id=key,
            truth_path=truth_path,
            preferred_start=Point3(-55.33, -24.23, 1.90),
            flight_z_m=1.90,
            roi_radius_m=70.0,
            resolution_m=0.75,
            safety_margin_m=0.55,
            body_half_height_m=0.45,
            lidar_radius_m=14.0,
            lidar_beams=180,
            local_commit_m=2.5,
            max_replans=260,
            mission_goal_min_m=18.0,
            mission_goal_max_m=32.0,
            control_tracking_buffer_cells=1,
        )
    if key == "derelictcorridormegascans":
        return SceneProfile(
            scene_id=key,
            truth_path=truth_path,
            preferred_start=Point3(87.04, 22.40, 2.20),
            flight_z_m=2.20,
            roi_radius_m=38.0,
            resolution_m=0.35,
            safety_margin_m=0.40,
            body_half_height_m=0.40,
            lidar_radius_m=10.0,
            lidar_beams=180,
            local_commit_m=1.4,
            max_replans=220,
            mission_goal_min_m=10.0,
            mission_goal_max_m=22.0,
            control_tracking_buffer_cells=2,
        )
    raise ValueError(f"no default pipeline profile for scene_id={scene_id}")


def scene_truth_path(scene_id: str, truth_dir: Path = DEFAULT_TRUTH_DIR) -> Path:
    path = truth_dir / f"{scene_id.lower()}_collision_truth.json"
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def relevant_for_flight(proxy: BoxProxy, profile: SceneProfile) -> bool:
    band_min = profile.flight_z_m - profile.body_half_height_m
    band_max = profile.flight_z_m + profile.body_half_height_m
    if proxy.max_z < band_min or proxy.min_z > band_max:
        return False
    if proxy.semantic_type in {"sensor", "marker"}:
        return False
    # Floors and ground meshes usually intersect the lower band through their
    # AABB, but they are not lateral obstacles at the selected flight height.
    if proxy.semantic_type == "terrain" and proxy.max_z < profile.flight_z_m - 0.15:
        return False
    return proxy.xy_area > 1e-6


def truth_bounds(proxies: list[BoxProxy]) -> tuple[float, float, float, float]:
    return (
        min(proxy.min_x for proxy in proxies),
        min(proxy.min_y for proxy in proxies),
        max(proxy.max_x for proxy in proxies),
        max(proxy.max_y for proxy in proxies),
    )


def roi_bounds(profile: SceneProfile, proxies: list[BoxProxy]) -> tuple[float, float, float, float]:
    truth_x0, truth_y0, truth_x1, truth_y1 = truth_bounds(proxies)
    start = profile.preferred_start
    radius = profile.roi_radius_m
    return (
        max(truth_x0, start.x - radius),
        max(truth_y0, start.y - radius),
        min(truth_x1, start.x + radius),
        min(truth_y1, start.y + radius),
    )


def box_intersects_bounds(proxy: BoxProxy, bounds: tuple[float, float, float, float]) -> bool:
    x0, y0, x1, y1 = bounds
    return not (proxy.max_x < x0 or proxy.min_x > x1 or proxy.max_y < y0 or proxy.min_y > y1)


def build_occupancy_grid(
    profile: SceneProfile,
    proxies: list[BoxProxy],
) -> tuple[OccupancyGrid, list[BoxProxy], dict[str, Any]]:
    bounds = roi_bounds(profile, proxies)
    x0, y0, x1, y1 = bounds
    res = profile.resolution_m
    width = int(math.ceil((x1 - x0) / res)) + 1
    height = int(math.ceil((y1 - y0) / res)) + 1
    grid = OccupancyGrid(x0, y0, res, width, height, [False] * (width * height))
    selected = [
        proxy for proxy in proxies
        if relevant_for_flight(proxy, profile) and box_intersects_bounds(proxy, bounds)
    ]
    for proxy in selected:
        min_cell = grid.world_to_cell(Point2(proxy.min_x - profile.safety_margin_m, proxy.min_y - profile.safety_margin_m))
        max_cell = grid.world_to_cell(Point2(proxy.max_x + profile.safety_margin_m, proxy.max_y + profile.safety_margin_m))
        for cy in range(min(min_cell[1], max_cell[1]), max(min_cell[1], max_cell[1]) + 1):
            for cx in range(min(min_cell[0], max_cell[0]), max(min_cell[0], max_cell[0]) + 1):
                grid.set_occupied((cx, cy))
    summary = {
        "roi_bounds_m": [round(value, 3) for value in bounds],
        "resolution_m": res,
        "grid_size": [width, height],
        "truth_proxy_count": len(proxies),
        "flight_relevant_proxy_count": len(selected),
        "occupied_cell_count": sum(1 for value in grid.occupied if value),
        "occupied_cell_ratio": round(sum(1 for value in grid.occupied if value) / max(1, len(grid.occupied)), 6),
    }
    return grid, selected, summary


def occupied_cell_set(grid: OccupancyGrid) -> set[tuple[int, int]]:
    return {
        (index % grid.width, index // grid.width)
        for index, value in enumerate(grid.occupied)
        if value
    }


def inflate_cells(
    grid: OccupancyGrid,
    cells: set[tuple[int, int]],
    radius_cells: int,
) -> set[tuple[int, int]]:
    if radius_cells <= 0:
        return set(cells)
    inflated: set[tuple[int, int]] = set()
    for cell in cells:
        for dy in range(-radius_cells, radius_cells + 1):
            for dx in range(-radius_cells, radius_cells + 1):
                candidate = (cell[0] + dx, cell[1] + dy)
                if grid.in_bounds(candidate):
                    inflated.add(candidate)
    return inflated


def nearest_free(
    grid: OccupancyGrid,
    preferred: Point3,
    blocked: set[tuple[int, int]] | None = None,
) -> tuple[int, int]:
    blocked = blocked or set()
    start = grid.world_to_cell(preferred)
    if grid.in_bounds(start) and start not in blocked and not grid.is_occupied(start):
        return start
    queue = [start]
    seen = {start}
    cursor = 0
    while cursor < len(queue):
        current = queue[cursor]
        cursor += 1
        for nb in neighbors8(current):
            if nb in seen or not grid.in_bounds(nb):
                continue
            if nb not in blocked and not grid.is_occupied(nb):
                return nb
            seen.add(nb)
            queue.append(nb)
    raise RuntimeError("no free cell found near preferred start")


def neighbors8(cell: tuple[int, int]) -> list[tuple[int, int]]:
    x, y = cell
    return [
        (x - 1, y),
        (x + 1, y),
        (x, y - 1),
        (x, y + 1),
        (x - 1, y - 1),
        (x - 1, y + 1),
        (x + 1, y - 1),
        (x + 1, y + 1),
    ]


def is_valid_step(
    grid: OccupancyGrid,
    current: tuple[int, int],
    candidate: tuple[int, int],
    blocked: set[tuple[int, int]] | None = None,
    *,
    use_truth: bool = True,
) -> bool:
    if not grid.in_bounds(candidate):
        return False
    blocked = blocked or set()
    if candidate in blocked or (use_truth and grid.is_occupied(candidate)):
        return False
    dx = candidate[0] - current[0]
    dy = candidate[1] - current[1]
    if abs(dx) == 1 and abs(dy) == 1:
        side_a = (current[0] + dx, current[1])
        side_b = (current[0], current[1] + dy)
        if (
            not grid.in_bounds(side_a)
            or not grid.in_bounds(side_b)
            or side_a in blocked
            or side_b in blocked
            or (use_truth and grid.is_occupied(side_a))
            or (use_truth and grid.is_occupied(side_b))
        ):
            return False
    return True


def reachable_free_cells(
    grid: OccupancyGrid,
    start: tuple[int, int],
    blocked: set[tuple[int, int]] | None = None,
) -> dict[tuple[int, int], float]:
    blocked = blocked or set()
    queue: list[tuple[float, int, tuple[int, int]]] = []
    distances = {start: 0.0}
    heapq.heappush(queue, (0.0, 0, start))
    counter = 0
    while queue:
        dist, _, current = heapq.heappop(queue)
        if dist > distances[current]:
            continue
        for nb in neighbors8(current):
            if not is_valid_step(grid, current, nb, blocked):
                continue
            step = math.hypot(nb[0] - current[0], nb[1] - current[1]) * grid.resolution
            cand = dist + step
            if cand < distances.get(nb, float("inf")):
                counter += 1
                distances[nb] = cand
                heapq.heappush(queue, (cand, counter, nb))
    return distances


def choose_goal(
    grid: OccupancyGrid,
    start: tuple[int, int],
    profile: SceneProfile,
    blocked: set[tuple[int, int]] | None = None,
) -> tuple[int, int]:
    blocked = blocked or set()
    distances = reachable_free_cells(grid, start, blocked)
    if len(distances) < 10:
        raise RuntimeError("free connected component is too small for planning")
    edge_margin_cells = max(2, int(round(2.0 / grid.resolution)))
    candidates = [
        (distance, cell) for cell, distance in distances.items()
        if edge_margin_cells <= cell[0] < grid.width - edge_margin_cells
        and edge_margin_cells <= cell[1] < grid.height - edge_margin_cells
        and profile.mission_goal_min_m <= distance <= profile.mission_goal_max_m
    ]
    if not candidates:
        candidates = [
            (distance, cell) for cell, distance in distances.items()
            if edge_margin_cells <= cell[0] < grid.width - edge_margin_cells
            and edge_margin_cells <= cell[1] < grid.height - edge_margin_cells
        ]
    if not candidates:
        candidates = [(distance, cell) for cell, distance in distances.items()]
    target_distance = 0.5 * (profile.mission_goal_min_m + profile.mission_goal_max_m)
    candidates.sort(
        key=lambda item: (
            abs(item[0] - target_distance),
            -item[0],
            abs(item[1][1] - start[1]),
        )
    )
    return candidates[0][1]


def astar_cells(
    grid: OccupancyGrid,
    start: tuple[int, int],
    goal: tuple[int, int],
    blocked: set[tuple[int, int]],
    visit_penalty: dict[tuple[int, int], float] | None = None,
) -> list[tuple[int, int]]:
    def h(cell: tuple[int, int]) -> float:
        return math.hypot(cell[0] - goal[0], cell[1] - goal[1])

    open_heap: list[tuple[float, int, tuple[int, int]]] = []
    parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    g_score = {start: 0.0}
    counter = 0
    heapq.heappush(open_heap, (h(start), counter, start))
    closed: set[tuple[int, int]] = set()
    while open_heap:
        _, _, current = heapq.heappop(open_heap)
        if current in closed:
            continue
        if current == goal:
            path = [current]
            while parent[current] is not None:
                current = parent[current]  # type: ignore[assignment]
                path.append(current)
            path.reverse()
            return path
        closed.add(current)
        for nb in neighbors8(current):
            if nb in closed or not is_valid_step(grid, current, nb, blocked, use_truth=False):
                continue
            step = math.hypot(nb[0] - current[0], nb[1] - current[1])
            if visit_penalty:
                step += visit_penalty.get(nb, 0.0)
            cand = g_score[current] + step
            if cand >= g_score.get(nb, float("inf")):
                continue
            parent[nb] = current
            g_score[nb] = cand
            counter += 1
            heapq.heappush(open_heap, (cand + 1.001 * h(nb), counter, nb))
    raise RuntimeError("A* failed on currently known map")


def reveal_cells(
    grid: OccupancyGrid,
    center: tuple[int, int],
    known_free: set[tuple[int, int]],
    known_occupied: set[tuple[int, int]],
    radius_m: float,
) -> int:
    radius_cells = max(1, int(math.ceil(radius_m / grid.resolution)))
    newly_known = 0
    for dy in range(-radius_cells, radius_cells + 1):
        for dx in range(-radius_cells, radius_cells + 1):
            if math.hypot(dx, dy) * grid.resolution > radius_m:
                continue
            cell = (center[0] + dx, center[1] + dy)
            if not grid.in_bounds(cell):
                continue
            if grid.is_occupied(cell):
                if cell not in known_occupied:
                    newly_known += 1
                known_occupied.add(cell)
            else:
                if cell not in known_free:
                    newly_known += 1
                known_free.add(cell)
    return newly_known


def reveal_ray_until_collision(
    grid: OccupancyGrid,
    cells: list[tuple[int, int]],
    known_free: set[tuple[int, int]],
    known_occupied: set[tuple[int, int]],
    radius_m: float,
) -> tuple[tuple[int, int] | None, int]:
    """Update the discovered map along a planned segment.

    A LiDAR-like observation proves free space before the first hit and proves
    occupied space at the hit. This prevents repeated replans through the same
    newly discovered wall face without leaking the whole global truth map.
    """
    newly_known = 0
    first_collision: tuple[int, int] | None = None
    for index, cell in enumerate(cells):
        if not grid.in_bounds(cell):
            first_collision = cell
            break
        previous = cells[index - 1] if index else None
        if previous is not None and not is_valid_step(grid, previous, cell):
            first_collision = cell
            newly_known += reveal_cells(grid, cell, known_free, known_occupied, radius_m)
            break
        if grid.is_occupied(cell):
            first_collision = cell
            newly_known += reveal_cells(grid, cell, known_free, known_occupied, radius_m)
            break
        if cell not in known_free:
            known_free.add(cell)
            newly_known += 1
    return first_collision, newly_known


def segment_cells(a: tuple[int, int], b: tuple[int, int]) -> list[tuple[int, int]]:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    steps = max(abs(dx), abs(dy), 1)
    cells: list[tuple[int, int]] = []
    for step in range(steps + 1):
        t = step / steps
        cell = (int(round(a[0] + dx * t)), int(round(a[1] + dy * t)))
        if not cells or cells[-1] != cell:
            cells.append(cell)
    return cells


def run_unknown_map_planner(
    profile: SceneProfile,
    grid: OccupancyGrid,
    start: tuple[int, int],
    goal: tuple[int, int],
) -> tuple[list[tuple[int, int]], dict[str, Any], set[tuple[int, int]], set[tuple[int, int]]]:
    known_free: set[tuple[int, int]] = set()
    known_occupied: set[tuple[int, int]] = set()
    current = start
    path = [current]
    visits: dict[tuple[int, int], int] = {current: 1}
    replan_count = 0
    blocked_attempts = 0
    reveal_cells(grid, current, known_free, known_occupied, profile.lidar_radius_m)
    commit_cells = max(1, int(round(profile.local_commit_m / grid.resolution)))
    while current != goal:
        if replan_count >= profile.max_replans:
            raise RuntimeError(f"unknown-map planner exceeded max_replans={profile.max_replans}")
        visit_penalty = {cell: 0.35 * count for cell, count in visits.items() if cell != current and cell != goal}
        known_blocked = inflate_cells(grid, known_occupied, profile.control_tracking_buffer_cells)
        planned = astar_cells(grid, current, goal, known_blocked, visit_penalty)
        commit_index = min(commit_cells, len(planned) - 1)
        travel = planned[: commit_index + 1]
        collision_cell, newly_known = reveal_ray_until_collision(
            grid,
            travel,
            known_free,
            known_occupied,
            profile.lidar_radius_m,
        )
        if collision_cell is not None:
            blocked_attempts += 1
            replan_count += 1
            if blocked_attempts > 80 and newly_known == 0:
                raise RuntimeError("unknown-map planner repeatedly targeted a known blocked segment")
            continue
        for cell in travel[1:]:
            reveal_cells(grid, cell, known_free, known_occupied, profile.lidar_radius_m)
            visits[cell] = visits.get(cell, 0) + 1
            if cell != path[-1]:
                path.append(cell)
        if current == path[-1]:
            raise RuntimeError("unknown-map planner did not advance")
        current = path[-1]
        blocked_attempts = 0
        replan_count += 1
    truth_occupied_known = sum(1 for value in grid.occupied if value)
    validation_buffer = inflate_cells(grid, occupied_cell_set(grid), profile.control_tracking_buffer_cells)
    report = {
        "planner_policy": "unknown_global_map_receding_astar_known_obstacles_only",
        "global_truth_available_to_planner": False,
        "goal_known": True,
        "path_cells": len(path),
        "replan_count": replan_count,
        "known_free_cells_final": len(known_free),
        "known_occupied_cells_final": len(known_occupied),
        "truth_occupied_cells": truth_occupied_known,
        "known_occupied_ratio_of_truth": round(len(known_occupied) / max(1, truth_occupied_known), 6),
        "control_tracking_buffer_cells": profile.control_tracking_buffer_cells,
        "collision_free_against_truth": all(not grid.is_occupied(cell) for cell in path),
        "buffered_collision_free_against_truth": all(cell not in validation_buffer for cell in path),
    }
    return path, report, known_free, known_occupied


def cast_lidar_frame(
    profile: SceneProfile,
    grid: OccupancyGrid,
    pose: tuple[int, int],
    beams: int,
    radius_m: float,
) -> list[Point3]:
    points: list[Point3] = []
    step_m = max(grid.resolution * 0.5, 0.12)
    max_steps = int(math.ceil(radius_m / step_m))
    for beam in range(beams):
        angle = 2.0 * math.pi * beam / beams
        dx = math.cos(angle)
        dy = math.sin(angle)
        hit: Point3 | None = None
        origin = grid.cell_to_world(pose, profile.flight_z_m)
        for step in range(1, max_steps + 1):
            x = origin.x + dx * step * step_m
            y = origin.y + dy * step * step_m
            cell = grid.world_to_cell(Point2(x, y))
            if not grid.in_bounds(cell):
                break
            if grid.is_occupied(cell):
                hit = grid.cell_to_world(cell, profile.flight_z_m)
                break
        if hit is not None:
            points.append(hit)
    return points


def sample_path_cells(path: list[tuple[int, int]], count: int) -> list[tuple[int, int]]:
    if len(path) <= count:
        return path
    samples: list[tuple[int, int]] = []
    for index in range(count):
        raw = round(index * (len(path) - 1) / max(1, count - 1))
        cell = path[int(raw)]
        if not samples or samples[-1] != cell:
            samples.append(cell)
    return samples


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_ply(path: Path, points: list[Point3]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "ply",
        "format ascii 1.0",
        f"element vertex {len(points)}",
        "property float x",
        "property float y",
        "property float z",
        "end_header",
    ]
    lines.extend(f"{point.x:.5f} {point.y:.5f} {point.z:.5f}" for point in points)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_occupancy_json(path: Path, profile: SceneProfile, grid: OccupancyGrid, selected: list[BoxProxy], summary: dict[str, Any]) -> None:
    occupied_cells = [
        [index % grid.width, index // grid.width]
        for index, value in enumerate(grid.occupied)
        if value
    ]
    payload = {
        "schema": "mosim.ue_scene_occupancy.v1",
        "scene_id": profile.scene_id,
        "source_truth": rel(profile.truth_path),
        "frame": "mworks_world",
        "units": "m",
        "flight_z_m": profile.flight_z_m,
        "safety_margin_m": profile.safety_margin_m,
        "grid": {
            "origin_xy_m": [round(grid.x_min, 5), round(grid.y_min, 5)],
            "resolution_m": grid.resolution,
            "size": [grid.width, grid.height],
            "occupied_cells_xy": occupied_cells,
        },
        "selected_proxy_ids": [proxy.proxy_id for proxy in selected],
        "summary": summary,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_path_csv(path: Path, grid: OccupancyGrid, cells: list[tuple[int, int]], z: float) -> None:
    rows = []
    for index, cell in enumerate(cells):
        point = grid.cell_to_world(cell, z)
        rows.append({"index": index, "x_m": point.x, "y_m": point.y, "z_m": point.z, "cell_x": cell[0], "cell_y": cell[1]})
    write_csv(path, ["index", "x_m", "y_m", "z_m", "cell_x", "cell_y"], rows)


def yaw_between(a: Point3, b: Point3, fallback: float) -> float:
    dx = b.x - a.x
    dy = b.y - a.y
    if abs(dx) < 1e-9 and abs(dy) < 1e-9:
        return fallback
    return math.atan2(dy, dx)


def write_render_replay_csv(
    path: Path,
    grid: OccupancyGrid,
    cells: list[tuple[int, int]],
    z: float,
    *,
    step_seconds: float = DEFAULT_REPLAY_STEP_SECONDS,
    first_point_override: Point3 | None = None,
) -> None:
    points = [grid.cell_to_world(cell, z) for cell in cells]
    if not points:
        raise ValueError("cannot write render replay with an empty path")
    if first_point_override is not None:
        points[0] = first_point_override

    rows: list[dict[str, Any]] = []
    yaw = 0.0
    for index, point in enumerate(points):
        if index + 1 < len(points):
            yaw = yaw_between(point, points[index + 1], yaw)
        reference = points[min(index + 1, len(points) - 1)]
        rows.append(
            {
                "time": round(index * step_seconds, 4),
                "x": round(point.x, 5),
                "y": round(point.y, 5),
                "z": round(point.z, 5),
                "x_ref": round(reference.x, 5),
                "y_ref": round(reference.y, 5),
                "z_ref": round(reference.z, 5),
                "roll": 0.0,
                "pitch": 0.0,
                "yaw": round(yaw, 6),
                "u1": 1.0,
                "u2": 1.0,
                "u3": 1.0,
                "u4": 1.0,
            }
        )
    write_csv(
        path,
        ["time", "x", "y", "z", "x_ref", "y_ref", "z_ref", "roll", "pitch", "yaw", "u1", "u2", "u3", "u4"],
        rows,
    )


def local_known_cells_for_pose(
    grid: OccupancyGrid,
    center: tuple[int, int],
    radius_m: float,
    max_cells: int,
) -> list[dict[str, Any]]:
    radius_cells = max(1, int(math.ceil(radius_m / grid.resolution)))
    candidates: list[tuple[float, tuple[int, int]]] = []
    for dy in range(-radius_cells, radius_cells + 1):
        for dx in range(-radius_cells, radius_cells + 1):
            distance = math.hypot(dx, dy) * grid.resolution
            if distance > radius_m:
                continue
            cell = (center[0] + dx, center[1] + dy)
            if not grid.in_bounds(cell):
                continue
            candidates.append((distance, cell))
    candidates.sort(key=lambda item: item[0])
    if max_cells > 0:
        candidates = candidates[:max_cells]

    cells: list[dict[str, Any]] = []
    for _, cell in candidates:
        cells.append(
            {
                "offset": [cell[0] - center[0], cell[1] - center[1], 0],
                "state": "observed_occupied" if grid.is_occupied(cell) else "observed_free",
                "source": "scene_truth_pipeline_local_lidar",
            }
        )
    return cells


def write_local_known_map_frames_jsonl(
    path: Path,
    profile: SceneProfile,
    grid: OccupancyGrid,
    cells: list[tuple[int, int]],
    z: float,
    *,
    radius_m: float = DEFAULT_LOCAL_KNOWN_RADIUS_M,
    max_cells: int = DEFAULT_LOCAL_KNOWN_MAX_CELLS,
    step_seconds: float = DEFAULT_REPLAY_STEP_SECONDS,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for index, cell in enumerate(cells):
            origin = grid.cell_to_world(cell, z)
            payload = {
                "schema": "mosim.local_known_map_frame.v1",
                "scene_id": profile.scene_id,
                "seq": index,
                "time": round(index * step_seconds, 4),
                "origin_m": [round(origin.x, 5), round(origin.y, 5), round(origin.z, 5)],
                "grid_m": grid.resolution,
                "radius_m": radius_m,
                "max_cells": max_cells,
                "render_only": False,
                "evidence_backed": True,
                "source": "scene_truth_pipeline_local_lidar",
                "cells": local_known_cells_for_pose(grid, cell, radius_m, max_cells),
            }
            handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_lidar_point_frames_jsonl(
    path: Path,
    profile: SceneProfile,
    grid: OccupancyGrid,
    cells: list[tuple[int, int]],
    *,
    max_points: int = DEFAULT_LIDAR_POINTS_MAX,
    step_seconds: float = DEFAULT_REPLAY_STEP_SECONDS,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for index, cell in enumerate(cells):
            frame_points = cast_lidar_frame(profile, grid, cell, profile.lidar_beams, profile.lidar_radius_m)
            if max_points > 0:
                frame_points = frame_points[:max_points]
            payload = {
                "schema": "mosim.lidar_point_frame.v1",
                "scene_id": profile.scene_id,
                "seq": index,
                "time": round(index * step_seconds, 4),
                "coordinate_frame": "ue_world_m_z_up",
                "source": "scene_truth_pipeline_lidar_replay",
                "render_only": False,
                "evidence_backed": True,
                "points_m": [
                    [round(point.x, 5), round(point.y, 5), round(point.z, 5)]
                    for point in frame_points
                ],
            }
            handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_local_plan_frames_jsonl(
    path: Path,
    profile: SceneProfile,
    grid: OccupancyGrid,
    cells: list[tuple[int, int]],
    z: float,
    *,
    lookahead: int = DEFAULT_LOCAL_PLAN_LOOKAHEAD,
    step_seconds: float = DEFAULT_REPLAY_STEP_SECONDS,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for index, _cell in enumerate(cells):
            plan_cells = cells[index : min(len(cells), index + max(1, lookahead) + 1)]
            points = [
                grid.cell_to_world(cell, z)
                for cell in plan_cells
            ]
            payload = {
                "schema": "mosim.local_plan_frame.v1",
                "scene_id": profile.scene_id,
                "seq": index,
                "time": round(index * step_seconds, 4),
                "coordinate_frame": "ue_world_m_z_up",
                "source": "scene_truth_pipeline_unknown_map_receding_astar",
                "render_only": False,
                "evidence_backed": True,
                "valid": True,
                "global_truth_available_to_planner": False,
                "points_m": [
                    [round(point.x, 5), round(point.y, 5), round(point.z, 5)]
                    for point in points
                ],
            }
            handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_svg(
    path: Path,
    profile: SceneProfile,
    grid: OccupancyGrid,
    start: tuple[int, int],
    goal: tuple[int, int],
    path_cells: list[tuple[int, int]],
    known_occupied: set[tuple[int, int]],
    cloud_points: list[Point3],
) -> None:
    width = 1100
    height = 760
    pad = 50

    def sx(x: float) -> float:
        return pad + (x - grid.x_min) / max(1e-9, grid.x_max - grid.x_min) * (width - 2 * pad)

    def sy(y: float) -> float:
        return height - pad - (y - grid.y_min) / max(1e-9, grid.y_max - grid.y_min) * (height - 2 * pad)

    cell_px = max(0.6, (width - 2 * pad) / max(1, grid.width))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#fcfcfb"/>',
        '<style>text{font-family:Arial,Microsoft YaHei,sans-serif;font-size:14px}.occ{fill:#444}.known{fill:#c45}.path{fill:none;stroke:#0b6fba;stroke-width:4}.cloud{fill:#19a974;fill-opacity:.65}.pt{stroke:#111;stroke-width:1.5}</style>',
        f'<text x="{pad}" y="28">scene={html.escape(profile.scene_id)} unknown-map local planning, global truth hidden from planner</text>',
    ]
    for index, occ in enumerate(grid.occupied):
        if not occ:
            continue
        cx = index % grid.width
        cy = index // grid.width
        world = grid.cell_to_world((cx, cy), profile.flight_z_m)
        klass = "known" if (cx, cy) in known_occupied else "occ"
        parts.append(f'<rect class="{klass}" x="{sx(world.x):.2f}" y="{sy(world.y):.2f}" width="{cell_px:.2f}" height="{cell_px:.2f}"/>')
    if cloud_points:
        for point in cloud_points[:3000]:
            parts.append(f'<circle class="cloud" cx="{sx(point.x):.2f}" cy="{sy(point.y):.2f}" r="1.6"/>')
    if path_cells:
        points = []
        for cell in path_cells:
            point = grid.cell_to_world(cell, profile.flight_z_m)
            points.append(f"{sx(point.x):.1f},{sy(point.y):.1f}")
        parts.append(f'<polyline class="path" points="{" ".join(points)}"/>')
    start_p = grid.cell_to_world(start, profile.flight_z_m)
    goal_p = grid.cell_to_world(goal, profile.flight_z_m)
    parts.append(f'<circle class="pt" cx="{sx(start_p.x):.1f}" cy="{sy(start_p.y):.1f}" r="7" fill="#2ca02c"/>')
    parts.append(f'<circle class="pt" cx="{sx(goal_p.x):.1f}" cy="{sy(goal_p.y):.1f}" r="7" fill="#ffbf00"/>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def write_fastlio_handoff(path: Path, profile: SceneProfile, outputs: dict[str, Path], planner_report: dict[str, Any]) -> None:
    payload = {
        "schema": "mosim.fastlio_handoff.v1",
        "scene_id": profile.scene_id,
        "status": "offline_simulated_sensor_handoff_ready",
        "truth_source": rel(profile.truth_path),
        "coordinate_frame": "mworks_world_m_z_up",
        "generated_inputs": {
            key: rel(value) for key, value in outputs.items()
            if key in {
                "trajectory_csv",
                "render_replay_csv",
                "local_known_map_jsonl",
                "local_plan_jsonl",
                "lidar_point_frames_jsonl",
                "merged_pointcloud_ply",
                "lidar_frames_dir",
                "occupancy_json",
            }
        },
        "fast_lio_reference_repo": "References/Lab/FAST_LIO",
        "integration_notes": [
            "FAST-LIO itself is ROS/Catkin based; this handoff currently provides deterministic offline point clouds and trajectory poses.",
            "The next runtime adapter should publish PointCloud2 plus IMU/odometry timestamps in the same frame or with a documented TF transform.",
            "This artifact is not a FAST-LIO localization result yet; it is the input contract for the FAST-LIO integration step.",
        ],
        "planner_report": planner_report,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_scene(profile: SceneProfile, output_root: Path) -> dict[str, Any]:
    truth = load_truth(profile.truth_path)
    proxies = [proxy_from_payload(proxy) for proxy in truth["collision_proxies"]]
    grid, selected, occ_summary = build_occupancy_grid(profile, proxies)
    validation_blocked = inflate_cells(grid, occupied_cell_set(grid), profile.control_tracking_buffer_cells)
    start = nearest_free(grid, profile.preferred_start, validation_blocked)
    goal = choose_goal(grid, start, profile, validation_blocked)
    path_cells, planner_report, known_free, known_occupied = run_unknown_map_planner(profile, grid, start, goal)
    scene_dir = output_root / profile.scene_id
    lidar_dir = scene_dir / "lidar_frames"
    sample_cells = sample_path_cells(path_cells, count=12)
    merged_cloud: list[Point3] = []
    frame_paths: list[Path] = []
    for index, cell in enumerate(sample_cells):
        frame_points = cast_lidar_frame(profile, grid, cell, profile.lidar_beams, profile.lidar_radius_m)
        merged_cloud.extend(frame_points)
        frame_path = lidar_dir / f"frame_{index:04d}.ply"
        write_ply(frame_path, frame_points)
        frame_paths.append(frame_path)
    outputs = {
        "occupancy_json": scene_dir / "occupancy_grid.json",
        "trajectory_csv": scene_dir / "trajectory.csv",
        "render_replay_csv": scene_dir / "render_replay.csv",
        "local_known_map_jsonl": scene_dir / "local_known_map_frames.jsonl",
        "local_plan_jsonl": scene_dir / "local_plan_frames.jsonl",
        "lidar_point_frames_jsonl": scene_dir / "lidar_point_frames.jsonl",
        "planner_summary_json": scene_dir / "planner_summary.json",
        "preview_svg": scene_dir / "preview.svg",
        "merged_pointcloud_ply": scene_dir / "pointcloud_merged.ply",
        "fastlio_handoff_json": scene_dir / "fastlio_handoff.json",
        "lidar_frames_dir": lidar_dir,
    }
    write_occupancy_json(outputs["occupancy_json"], profile, grid, selected, occ_summary)
    write_path_csv(outputs["trajectory_csv"], grid, path_cells, profile.flight_z_m)
    write_render_replay_csv(
        outputs["render_replay_csv"],
        grid,
        path_cells,
        profile.flight_z_m,
        first_point_override=profile.preferred_start,
    )
    write_local_known_map_frames_jsonl(outputs["local_known_map_jsonl"], profile, grid, path_cells, profile.flight_z_m)
    write_local_plan_frames_jsonl(outputs["local_plan_jsonl"], profile, grid, path_cells, profile.flight_z_m)
    write_lidar_point_frames_jsonl(outputs["lidar_point_frames_jsonl"], profile, grid, path_cells)
    write_ply(outputs["merged_pointcloud_ply"], merged_cloud)
    write_svg(outputs["preview_svg"], profile, grid, start, goal, path_cells, known_occupied, merged_cloud)
    full_report = {
        "schema": "mosim.ue_scene_mapping_summary.v1",
        "scene_id": profile.scene_id,
        "truth_source": rel(profile.truth_path),
        "occupancy": occ_summary,
        "start_m": list(grid.cell_to_world(start, profile.flight_z_m).__dict__.values()),
        "goal_m": list(grid.cell_to_world(goal, profile.flight_z_m).__dict__.values()),
        "outputs": {key: rel(value) for key, value in outputs.items()},
        "lidar_frame_count": len(frame_paths),
        "merged_lidar_point_count": len(merged_cloud),
        **planner_report,
    }
    outputs["planner_summary_json"].write_text(json.dumps(full_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_fastlio_handoff(outputs["fastlio_handoff_json"], profile, outputs, planner_report)
    return full_report


def write_run_summary(path: Path, reports: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# UE Scene Mapping Pipeline Run",
        "",
        "This run consumes exported Unreal collision truth and produces file-level mapping/planning artifacts.",
        "",
        "| Scene | Grid | Path Cells | Replans | Known Occupied / Truth | Lidar Points | Point Cloud Artifact |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for report in reports:
        occ = report["occupancy"]
        lines.append(
            f"| `{report['scene_id']}` | {occ['grid_size'][0]}x{occ['grid_size'][1]} | "
            f"{report['path_cells']} | {report['replan_count']} | "
            f"{report['known_occupied_cells_final']}/{report['truth_occupied_cells']} | "
            f"{report['merged_lidar_point_count']} | `{report['outputs']['merged_pointcloud_ply']}` |"
        )
    lines.extend(
        [
            "",
            "Policy:",
            "- Planner uses a local discovered map and does not receive the full global occupancy grid.",
            "- Collision validation is still checked against exported UE truth.",
            "- FAST-LIO artifacts are input handoff files, not a completed FAST-LIO localization result.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scene",
        action="append",
        default=[],
        help="Scene id to process. Default: factoryenvironmentcollect and derelictcorridormegascans.",
    )
    parser.add_argument("--truth-dir", type=Path, default=DEFAULT_TRUTH_DIR)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    truth_dir = project_path(args.truth_dir)
    output_root = project_path(args.output_root)
    scene_ids = args.scene or ["factoryenvironmentcollect", "derelictcorridormegascans"]
    reports = []
    for scene_id in scene_ids:
        truth_path = scene_truth_path(scene_id, truth_dir)
        truth = load_truth(truth_path)
        profile = default_profile(str(truth["scene_id"]), truth_path)
        report = run_scene(profile, output_root)
        reports.append(report)
        print(f"{scene_id}: path_cells={report['path_cells']} lidar_points={report['merged_lidar_point_count']} ply={report['outputs']['merged_pointcloud_ply']}")
    write_run_summary(output_root / "RUN_SUMMARY.md", reports)
    print(f"Wrote {rel(output_root / 'RUN_SUMMARY.md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
