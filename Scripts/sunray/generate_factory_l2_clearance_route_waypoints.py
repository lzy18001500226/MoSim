#!/usr/bin/env python3
"""Generate Factory L2 same-flight waypoints over source-truth free cells.

This is a support-route generator for Factory indoor map-building runs. It
uses UE collision-truth AABBs as a conservative oracle to avoid selecting
Diff-Planner goals inside low-altitude obstacles. It does not prove runtime
coverage; Gazebo/PX4/MAVROS/px4ctrl metrics and coverage packets remain the
acceptance evidence.
"""

from __future__ import annotations

import argparse
import heapq
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENVELOPE = ROOT / "Config/gazebo/scene_profiles/factory_l2_exploration_envelope.json"
DEFAULT_TRUTH = ROOT / "UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/factoryenvironmentcollect_collision_truth.json"
FLOOR_TERMS = ("factoryfloorlarge", "concretefloor", "rubberfloor")


@dataclass(frozen=True)
class Rect:
    min_x: float
    min_y: float
    max_x: float
    max_y: float


@dataclass(frozen=True)
class Proxy:
    actor: str
    rect: Rect
    min_z: float
    max_z: float
    size_z: float


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path outside MoSim workspace: {value}")
    return resolved


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit(f"JSON root must be object: {path}")
    return payload


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def proxy_name(raw: dict[str, Any]) -> str:
    return str(raw.get("source_actor") or raw.get("source_mesh") or raw.get("collision_proxy_id") or "")


def proxy_from_raw(raw: dict[str, Any]) -> Proxy | None:
    min_m = raw.get("min_m")
    max_m = raw.get("max_m")
    size_m = raw.get("size_m")
    if not isinstance(min_m, list) or not isinstance(max_m, list) or len(min_m) < 3 or len(max_m) < 3:
        return None
    if not isinstance(size_m, list) or len(size_m) < 3:
        size_m = [float(max_m[i]) - float(min_m[i]) for i in range(3)]
    return Proxy(
        actor=proxy_name(raw),
        rect=Rect(float(min_m[0]), float(min_m[1]), float(max_m[0]), float(max_m[1])),
        min_z=float(min_m[2]),
        max_z=float(max_m[2]),
        size_z=float(size_m[2]),
    )


def has_floor_term(name: str) -> bool:
    lower = name.lower()
    return any(term in lower for term in FLOOR_TERMS)


def is_low_floor(proxy: Proxy) -> bool:
    return (
        has_floor_term(proxy.actor)
        and proxy.min_z <= 0.25
        and proxy.max_z <= 0.35
        and (proxy.rect.max_x - proxy.rect.min_x) >= 2.0
        and (proxy.rect.max_y - proxy.rect.min_y) >= 2.0
        and proxy.size_z <= 1.0
    )


def point_inside_rect(x: float, y: float, rect: Rect, shrink: float = 0.0) -> bool:
    return rect.min_x + shrink <= x <= rect.max_x - shrink and rect.min_y + shrink <= y <= rect.max_y - shrink


def point_clear_of_rect(x: float, y: float, rect: Rect, margin: float) -> bool:
    return not (rect.min_x - margin <= x <= rect.max_x + margin and rect.min_y - margin <= y <= rect.max_y + margin)


def load_boundary(envelope_path: Path) -> dict[str, float]:
    envelope = read_json(envelope_path)
    raw = envelope.get("exploration_boundary") or {}
    boundary = {
        "min_x_m": as_float(raw.get("min_x_m")),
        "max_x_m": as_float(raw.get("max_x_m")),
        "min_y_m": as_float(raw.get("min_y_m")),
        "max_y_m": as_float(raw.get("max_y_m")),
        "center_x_m": as_float(raw.get("center_x_m"), (as_float(raw.get("min_x_m")) + as_float(raw.get("max_x_m"))) * 0.5),
        "center_y_m": as_float(raw.get("center_y_m"), (as_float(raw.get("min_y_m")) + as_float(raw.get("max_y_m"))) * 0.5),
    }
    if boundary["max_x_m"] <= boundary["min_x_m"] or boundary["max_y_m"] <= boundary["min_y_m"]:
        raise SystemExit(f"invalid exploration boundary in {envelope_path}")
    return boundary


def build_free_grid(
    boundary: dict[str, float],
    proxies: list[Proxy],
    args: argparse.Namespace,
) -> tuple[dict[tuple[int, int], tuple[float, float]], dict[str, int]]:
    floor_proxies = [p for p in proxies if is_low_floor(p)]
    flight_obstacles = flight_obstacle_proxies(proxies, args)
    min_x = boundary["min_x_m"] + args.boundary_margin_m
    max_x = boundary["max_x_m"] - args.boundary_margin_m
    min_y = boundary["min_y_m"] + args.boundary_margin_m
    max_y = boundary["max_y_m"] - args.boundary_margin_m
    free: dict[tuple[int, int], tuple[float, float]] = {}
    rejected_no_floor = 0
    rejected_obstacle = 0
    ix = 0
    x = min_x
    while x <= max_x + 1e-6:
        iy = 0
        y = min_y
        while y <= max_y + 1e-6:
            has_floor = any(point_inside_rect(x, y, p.rect, args.floor_edge_margin_m) for p in floor_proxies)
            blocked = any(not point_clear_of_rect(x, y, p.rect, args.clearance_margin_m) for p in flight_obstacles)
            if has_floor and not blocked:
                free[(ix, iy)] = (round(x, 6), round(y, 6))
            else:
                rejected_no_floor += 0 if has_floor else 1
                rejected_obstacle += 1 if blocked else 0
            y += args.grid_step_m
            iy += 1
        x += args.grid_step_m
        ix += 1
    return free, {
        "low_floor_proxy_count": len(floor_proxies),
        "flight_obstacle_proxy_count": len(flight_obstacles),
        "free_cell_count": len(free),
        "rejected_no_floor_count": rejected_no_floor,
        "rejected_obstacle_count": rejected_obstacle,
    }


def flight_obstacle_proxies(proxies: list[Proxy], args: argparse.Namespace) -> list[Proxy]:
    overhead_max_min_z = float(getattr(args, "overhead_obstacle_max_min_z_m", 0.0) or 0.0)
    return [
        p
        for p in proxies
        if not is_low_floor(p)
        and (
            (
                p.max_z + args.obstacle_z_inflation_m >= args.flight_obstacle_min_z_m
                and p.min_z - args.obstacle_z_inflation_m <= args.flight_obstacle_max_z_m
            )
            or (
                overhead_max_min_z > 0.0
                and p.min_z <= overhead_max_min_z
                and p.max_z >= args.flight_obstacle_max_z_m
            )
        )
    ]


def point_clear_of_flight_obstacles(x: float, y: float, obstacles: list[Proxy], margin: float) -> bool:
    return all(point_clear_of_rect(x, y, obstacle.rect, margin) for obstacle in obstacles)


def transit_grid_step_m(args: argparse.Namespace) -> float:
    configured = float(getattr(args, "transit_grid_step_m", 0.0) or 0.0)
    if configured > 0.0:
        return configured
    return min(float(args.grid_step_m), 1.5)


def build_transit_grid(
    boundary: dict[str, float],
    obstacles: list[Proxy],
    args: argparse.Namespace,
) -> dict[tuple[int, int], tuple[float, float]]:
    step = transit_grid_step_m(args)
    min_x = boundary["min_x_m"] + args.boundary_margin_m
    max_x = boundary["max_x_m"] - args.boundary_margin_m
    min_y = boundary["min_y_m"] + args.boundary_margin_m
    max_y = boundary["max_y_m"] - args.boundary_margin_m
    free: dict[tuple[int, int], tuple[float, float]] = {}
    ix = 0
    x = min_x
    while x <= max_x + 1e-6:
        iy = 0
        y = min_y
        while y <= max_y + 1e-6:
            if point_clear_of_flight_obstacles(x, y, obstacles, args.clearance_margin_m):
                free[(ix, iy)] = (round(x, 6), round(y, 6))
            y += step
            iy += 1
        x += step
        ix += 1
    return free


def nearest_cell(free: dict[tuple[int, int], tuple[float, float]], x: float, y: float) -> tuple[int, int]:
    if not free:
        raise SystemExit("no free cells after clearance filtering")
    return min(free, key=lambda key: math.hypot(free[key][0] - x, free[key][1] - y))


def ordered_targets(free: dict[tuple[int, int], tuple[float, float]], center_y: float) -> list[tuple[int, int]]:
    rows: dict[int, list[tuple[int, int]]] = {}
    for cell in free:
        rows.setdefault(cell[1], []).append(cell)
    ordered_rows = sorted(rows, key=lambda iy: abs(rows[iy][0][1] if False else free[rows[iy][0]][1] - center_y))
    targets: list[tuple[int, int]] = []
    for row_number, iy in enumerate(ordered_rows):
        row = sorted(rows[iy], key=lambda cell: cell[0], reverse=bool(row_number % 2))
        targets.extend(row)
    return targets


def segment_intersects_rect(
    start: tuple[float, float],
    end: tuple[float, float],
    rect: Rect,
    margin: float,
) -> bool:
    """Return true when a 2D segment intersects an inflated AABB."""
    min_x = rect.min_x - margin
    max_x = rect.max_x + margin
    min_y = rect.min_y - margin
    max_y = rect.max_y + margin
    x0, y0 = start
    x1, y1 = end
    dx = x1 - x0
    dy = y1 - y0
    u1 = 0.0
    u2 = 1.0
    for p, q in (
        (-dx, x0 - min_x),
        (dx, max_x - x0),
        (-dy, y0 - min_y),
        (dy, max_y - y0),
    ):
        if abs(p) < 1e-12:
            if q < 0.0:
                return False
            continue
        t = q / p
        if p < 0.0:
            if t > u2:
                return False
            u1 = max(u1, t)
        else:
            if t < u1:
                return False
            u2 = min(u2, t)
    return u1 <= u2


def segment_clear_of_flight_obstacles(
    start: tuple[float, float],
    end: tuple[float, float],
    obstacles: list[Proxy],
    margin: float,
) -> bool:
    return all(not segment_intersects_rect(start, end, obstacle.rect, margin) for obstacle in obstacles)


def neighbors(
    cell: tuple[int, int],
    free: set[tuple[int, int]],
    coordinates: dict[tuple[int, int], tuple[float, float]] | None = None,
    obstacles: list[Proxy] | None = None,
    margin: float = 0.0,
) -> list[tuple[int, int]]:
    x, y = cell
    out = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        cand = (x + dx, y + dy)
        if cand in free:
            if coordinates is not None and obstacles:
                if not segment_clear_of_flight_obstacles(coordinates[cell], coordinates[cand], obstacles, margin):
                    continue
            out.append(cand)
    return out


def astar(
    start: tuple[int, int],
    goal: tuple[int, int],
    free_cells: set[tuple[int, int]],
    coordinates: dict[tuple[int, int], tuple[float, float]] | None = None,
    obstacles: list[Proxy] | None = None,
    margin: float = 0.0,
) -> list[tuple[int, int]] | None:
    if start == goal:
        return [start]
    queue: list[tuple[float, tuple[int, int]]] = []
    heapq.heappush(queue, (0.0, start))
    came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    cost_so_far: dict[tuple[int, int], float] = {start: 0.0}
    while queue:
        _priority, current = heapq.heappop(queue)
        if current == goal:
            break
        for nxt in neighbors(current, free_cells, coordinates, obstacles, margin):
            new_cost = cost_so_far[current] + 1.0
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                priority = new_cost + abs(goal[0] - nxt[0]) + abs(goal[1] - nxt[1])
                heapq.heappush(queue, (priority, nxt))
                came_from[nxt] = current
    if goal not in came_from:
        return None
    path: list[tuple[int, int]] = []
    current: tuple[int, int] | None = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path


def build_route(
    free: dict[tuple[int, int], tuple[float, float]],
    boundary: dict[str, float],
    args: argparse.Namespace,
    transit: dict[tuple[int, int], tuple[float, float]] | None = None,
    transit_obstacles: list[Proxy] | None = None,
) -> tuple[list[tuple[float, float, float]], dict[str, Any]]:
    free_cells = set(free)
    start_x = args.start_x_m if args.start_x_m is not None else boundary["center_x_m"]
    start_y = args.start_y_m if args.start_y_m is not None else boundary["center_y_m"]
    current = nearest_cell(free, start_x, start_y)
    targets = ordered_targets(free, boundary["center_y_m"])
    if args.min_start_target_distance_m > 0:
        targets = [
            target
            for target in targets
            if math.hypot(free[target][0] - start_x, free[target][1] - start_y) >= args.min_start_target_distance_m
        ]
    if args.max_coverage_targets > 0 and args.route_policy != "nearest_neighbor":
        targets = targets[: args.max_coverage_targets]

    def transit_path(start_xy: tuple[float, float], goal_xy: tuple[float, float]) -> list[tuple[int, int]] | None:
        if not transit:
            return None
        return astar(
            nearest_cell(transit, start_xy[0], start_xy[1]),
            nearest_cell(transit, goal_xy[0], goal_xy[1]),
            set(transit),
            transit,
            transit_obstacles,
            args.clearance_margin_m,
        )

    def route_points_from_cells(cells: list[tuple[int, int]]) -> list[tuple[float, float, float]]:
        points = [(free[cell][0], free[cell][1], args.z_m) for cell in cells]
        if args.min_start_target_distance_m > 0:
            points = [
                point
                for point in points
                if math.hypot(point[0] - start_x, point[1] - start_y) >= args.min_start_target_distance_m
            ]
        if args.include_center_start:
            points.insert(0, (start_x, start_y, args.z_m))
        return points

    if args.route_policy == "coverage_gain_transit":
        rows: dict[int, list[tuple[int, int]]] = {}
        for cell in targets:
            rows.setdefault(cell[1], []).append(cell)
        if args.coverage_order == "bottomup":
            row_indices = sorted(rows, key=lambda iy: free[rows[iy][0]][1])
        elif args.coverage_order == "start_outward":
            row_indices = sorted(rows, key=lambda iy: abs(free[rows[iy][0]][1] - start_y))
        else:
            row_indices = sorted(rows, key=lambda iy: free[rows[iy][0]][1], reverse=True)

        ordered_candidates: list[tuple[int, int]] = []
        reverse_row = False
        for row_index in row_indices:
            row = sorted(rows[row_index], key=lambda cell: free[cell][0], reverse=reverse_row)
            ordered_candidates.extend(row)
            reverse_row = not reverse_row

        covered: set[tuple[int, int]] = set()
        grid_cell_count = sensor_proxy_grid_cell_count(boundary, args.coverage_resolution_m)
        current_xy = (start_x, start_y)
        route_points: list[tuple[float, float, float]] = []
        selected_targets = 0
        skipped_unreachable: list[tuple[int, int]] = []
        skipped_low_gain = 0
        inserted_transit = 0
        stop_ratio = max(0.0, float(args.coverage_target_stop_ratio))
        min_new_cells = max(1, int(args.coverage_target_min_new_cells))

        for candidate in ordered_candidates:
            target_xy = free[candidate]
            target_cells = sensor_proxy_cells_for_point(
                target_xy[0],
                target_xy[1],
                boundary,
                args.coverage_resolution_m,
                args.sensor_radius_m,
            )
            if len(target_cells - covered) < min_new_cells:
                skipped_low_gain += 1
                continue
            path = transit_path(current_xy, target_xy)
            if not path:
                skipped_unreachable.append(candidate)
                continue
            segment_points: list[tuple[float, float, float]] = []
            for cell in path[1:]:
                x, y = transit[cell] if transit else free[cell]
                point = (x, y, args.z_m)
                if not segment_points or point != segment_points[-1]:
                    segment_points.append(point)
            target_point = (target_xy[0], target_xy[1], args.z_m)
            if not segment_points or target_point != segment_points[-1]:
                segment_points.append(target_point)

            segment_cells: set[tuple[int, int]] = set()
            for x, y, _z in segment_points:
                segment_cells.update(
                    sensor_proxy_cells_for_point(x, y, boundary, args.coverage_resolution_m, args.sensor_radius_m)
                )
            if len(segment_cells - covered) < min_new_cells:
                skipped_low_gain += 1
                continue

            for point in segment_points:
                if not route_points or point != route_points[-1]:
                    route_points.append(point)
                    covered.update(
                        sensor_proxy_cells_for_point(
                            point[0],
                            point[1],
                            boundary,
                            args.coverage_resolution_m,
                            args.sensor_radius_m,
                        )
                    )
                    inserted_transit += 1
            current_xy = target_xy
            selected_targets += 1

            if args.max_coverage_targets > 0 and selected_targets >= args.max_coverage_targets:
                break
            if args.max_waypoints > 0 and len(route_points) >= args.max_waypoints:
                route_points = route_points[: args.max_waypoints]
                break
            if stop_ratio > 0.0 and len(covered) / grid_cell_count >= stop_ratio:
                break

        if args.include_center_start:
            route_points.insert(0, (start_x, start_y, args.z_m))
        return route_points, {
            "route_policy": args.route_policy,
            "coverage_order": args.coverage_order,
            "coverage_target_count": len(targets),
            "ordered_candidate_count": len(ordered_candidates),
            "visited_target_count": selected_targets,
            "selected_coverage_target_count": selected_targets,
            "skipped_low_gain_candidate_count": skipped_low_gain,
            "skipped_unreachable_target_count": len(skipped_unreachable),
            "start_cell": list(current),
            "end_cell": nearest_cell(free, current_xy[0], current_xy[1]) if route_points else None,
            "requested_start_xy_m": [start_x, start_y],
            "nearest_start_xy_m": list(free[current]),
            "include_center_start": args.include_center_start,
            "min_start_target_distance_m": args.min_start_target_distance_m,
            "coverage_target_min_new_cells": min_new_cells,
            "coverage_target_stop_ratio": stop_ratio,
            "route_inserted_transit_waypoint_count": inserted_transit,
            "planned_coverage_ratio_at_route_build": len(covered) / grid_cell_count,
            "note": (
                "Coverage targets are ordered as a sweep and accepted only when "
                "the target plus its A* transit segment adds new sensor-footprint "
                "coverage. This keeps one UAV moving through a same-flight map-building route."
            ),
        }

    if args.route_policy == "nearest_neighbor":
        unvisited = set(targets)
        route_cells = [current]
        visited_targets = 0
        while unvisited:
            target = min(
                unvisited,
                key=lambda cell: math.hypot(free[cell][0] - free[current][0], free[cell][1] - free[current][1]),
            )
            route_cells.append(target)
            unvisited.remove(target)
            current = target
            visited_targets += 1
            if args.max_coverage_targets > 0 and visited_targets >= args.max_coverage_targets:
                break
            if args.max_waypoints > 0 and len(route_cells) >= args.max_waypoints:
                route_cells = route_cells[: args.max_waypoints]
                break
        route_points = route_points_from_cells(route_cells)
        return route_points, {
            "route_policy": args.route_policy,
            "coverage_target_count": len(targets),
            "visited_target_count": visited_targets,
            "skipped_unreachable_target_count": 0,
            "start_cell": list(route_cells[0]) if route_cells else None,
            "end_cell": list(route_cells[-1]) if route_cells else None,
            "requested_start_xy_m": [start_x, start_y],
            "nearest_start_xy_m": list(free[route_cells[0]]) if route_cells else None,
            "include_center_start": args.include_center_start,
            "min_start_target_distance_m": args.min_start_target_distance_m,
            "note": "Targets are source-truth clearance-filtered and ordered by nearest neighbor; runtime Diff/EGO must prove transitions are traversable.",
        }

    if args.route_policy == "nearest_neighbor_transit":
        unvisited = set(targets)
        current_xy = free[current]
        route_points: list[tuple[float, float, float]] = []
        visited_targets = 0
        skipped: set[tuple[int, int]] = set()
        inserted_transit = 0
        while unvisited:
            reachable: tuple[float, tuple[int, int], list[tuple[int, int]]] | None = None
            for target in sorted(
                unvisited,
                key=lambda cell: math.hypot(free[cell][0] - current_xy[0], free[cell][1] - current_xy[1]),
            ):
                target_xy = free[target]
                path = transit_path(current_xy, target_xy)
                if not path:
                    continue
                distance = math.hypot(target_xy[0] - current_xy[0], target_xy[1] - current_xy[1])
                reachable = (distance, target, path)
                break
            if reachable is None:
                skipped.update(unvisited)
                break
            _distance, target, path = reachable
            for cell in path[1:-1]:
                x, y = transit[cell] if transit else free[cell]
                point = (x, y, args.z_m)
                if not route_points or point != route_points[-1]:
                    route_points.append(point)
                    inserted_transit += 1
            target_point = (free[target][0], free[target][1], args.z_m)
            if not route_points or target_point != route_points[-1]:
                route_points.append(target_point)
            unvisited.remove(target)
            current_xy = free[target]
            visited_targets += 1
            if args.max_coverage_targets > 0 and visited_targets >= args.max_coverage_targets:
                break
            if args.max_waypoints > 0 and len(route_points) >= args.max_waypoints:
                route_points = route_points[: args.max_waypoints]
                break
        if args.include_center_start:
            route_points.insert(0, (start_x, start_y, args.z_m))
        return route_points, {
            "route_policy": args.route_policy,
            "coverage_target_count": len(targets),
            "visited_target_count": visited_targets,
            "skipped_unreachable_target_count": len(skipped),
            "start_cell": list(current),
            "end_cell": nearest_cell(free, current_xy[0], current_xy[1]) if route_points else None,
            "requested_start_xy_m": [start_x, start_y],
            "nearest_start_xy_m": list(free[current]),
            "include_center_start": args.include_center_start,
            "min_start_target_distance_m": args.min_start_target_distance_m,
            "route_inserted_transit_waypoint_count": inserted_transit,
            "note": "Coverage targets require floor clearance; transitions are connected through flight-obstacle-clear transit grid.",
        }

    if args.route_policy == "ordered_targets":
        route_cells = [current]
        visited_targets = 0
        for target in targets:
            if target == current and len(route_cells) == 1:
                visited_targets += 1
                continue
            route_cells.append(target)
            visited_targets += 1
            if args.max_waypoints > 0 and len(route_cells) >= args.max_waypoints:
                route_cells = route_cells[: args.max_waypoints]
                break
        route_points = route_points_from_cells(route_cells)
        return route_points, {
            "route_policy": args.route_policy,
            "coverage_target_count": len(targets),
            "visited_target_count": visited_targets,
            "skipped_unreachable_target_count": 0,
            "start_cell": list(route_cells[0]) if route_cells else None,
            "end_cell": list(route_cells[-1]) if route_cells else None,
            "requested_start_xy_m": [start_x, start_y],
            "nearest_start_xy_m": list(free[route_cells[0]]) if route_cells else None,
            "include_center_start": args.include_center_start,
            "min_start_target_distance_m": args.min_start_target_distance_m,
            "note": "Targets are source-truth clearance-filtered; runtime Diff/EGO must prove transitions are traversable.",
        }

    route_cells: list[tuple[int, int]] = [current]
    skipped: list[tuple[int, int]] = []
    visited_targets = 0
    for target in targets:
        if target == current:
            visited_targets += 1
            continue
        path = astar(current, target, free_cells)
        if not path:
            skipped.append(target)
            continue
        route_cells.extend(path[1:])
        current = target
        visited_targets += 1
        if args.max_waypoints > 0 and len(route_cells) >= args.max_waypoints:
            route_cells = route_cells[: args.max_waypoints]
            break
    route_points = route_points_from_cells(route_cells)
    return route_points, {
        "route_policy": args.route_policy,
        "coverage_target_count": len(targets),
        "visited_target_count": visited_targets,
        "skipped_unreachable_target_count": len(skipped),
        "start_cell": list(route_cells[0]) if route_cells else None,
        "end_cell": list(route_cells[-1]) if route_cells else None,
        "requested_start_xy_m": [start_x, start_y],
        "nearest_start_xy_m": list(free[route_cells[0]]) if route_cells else None,
        "include_center_start": args.include_center_start,
        "min_start_target_distance_m": args.min_start_target_distance_m,
    }


def insert_transit_waypoints(
    waypoints: list[tuple[float, float, float]],
    boundary: dict[str, float],
    proxies: list[Proxy],
    args: argparse.Namespace,
) -> tuple[list[tuple[float, float, float]], dict[str, Any]]:
    max_segment = float(getattr(args, "max_segment_m", 0.0) or 0.0)
    if max_segment <= 0 or len(waypoints) < 2:
        return waypoints, {
            "enabled": False,
            "max_segment_m": max_segment,
            "inserted_transit_waypoint_count": 0,
            "blocked_transit_candidate_count": 0,
            "max_output_segment_m": max(
                (math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(waypoints, waypoints[1:])),
                default=0.0,
            ),
        }

    flight_obstacles = flight_obstacle_proxies(proxies, args)
    transit = build_transit_grid(boundary, flight_obstacles, args)
    transit_cells = set(transit)
    out: list[tuple[float, float, float]] = [waypoints[0]]
    inserted = 0
    failed_segments = 0
    dropped_blocked_endpoints = 0
    for end in waypoints[1:]:
        start = out[-1]
        dist_xy = math.hypot(end[0] - start[0], end[1] - start[1])
        segment_blocked = not segment_clear_of_flight_obstacles(
            (start[0], start[1]),
            (end[0], end[1]),
            flight_obstacles,
            args.clearance_margin_m,
        )
        if (dist_xy > max_segment or segment_blocked) and transit:
            start_cell = nearest_cell(transit, start[0], start[1])
            end_cell = nearest_cell(transit, end[0], end[1])
            path = astar(
                start_cell,
                end_cell,
                transit_cells,
                transit,
                flight_obstacles,
                args.clearance_margin_m,
            )
            if path and len(path) >= 2:
                for cell in path[1:-1]:
                    x, y = transit[cell]
                    point = (x, y, end[2])
                    if point != out[-1]:
                        out.append(point)
                        inserted += 1
            else:
                failed_segments += 1
                if segment_blocked:
                    dropped_blocked_endpoints += 1
                    continue
        out.append(end)

    return out, {
        "enabled": True,
        "max_segment_m": max_segment,
        "transit_grid_step_m": transit_grid_step_m(args),
        "inserted_transit_waypoint_count": inserted,
        "failed_transit_segment_count": failed_segments,
        "dropped_blocked_endpoint_count": dropped_blocked_endpoints,
        "segment_clearance_checked": True,
        "transit_grid_cell_count": len(transit),
        "max_output_segment_m": max(
            (math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(out, out[1:])),
            default=0.0,
        ),
    }


def drop_immediate_backtracks(
    waypoints: list[tuple[float, float, float]],
    epsilon_m: float = 1e-6,
) -> tuple[list[tuple[float, float, float]], dict[str, Any]]:
    """Drop A-B-A route fragments that make coverage routes bounce at obstacle edges."""
    if len(waypoints) < 3:
        return waypoints, {
            "enabled": False,
            "removed_waypoint_count": 0,
            "epsilon_m": epsilon_m,
        }

    out: list[tuple[float, float, float]] = []
    removed: list[dict[str, Any]] = []
    for point in waypoints:
        if len(out) >= 2:
            previous_previous = out[-2]
            same_xy = math.hypot(point[0] - previous_previous[0], point[1] - previous_previous[1]) <= epsilon_m
            same_z = abs(point[2] - previous_previous[2]) <= epsilon_m
            if same_xy and same_z:
                removed.append(
                    {
                        "output_index_before_drop": len(out) + 1,
                        "dropped": list(point),
                        "middle": list(out[-1]),
                        "matched_previous_previous": list(previous_previous),
                    }
                )
                continue
        out.append(point)

    return out, {
        "enabled": True,
        "removed_waypoint_count": len(removed),
        "epsilon_m": epsilon_m,
        "first_removed": removed[:20],
    }


def simplify_clear_segments(
    waypoints: list[tuple[float, float, float]],
    obstacles: list[Proxy],
    args: argparse.Namespace,
) -> tuple[list[tuple[float, float, float]], dict[str, Any]]:
    max_segment = float(getattr(args, "max_segment_m", 0.0) or 0.0)
    if max_segment <= 0.0 or len(waypoints) < 3:
        return waypoints, {
            "enabled": False,
            "input_waypoint_count": len(waypoints),
            "output_waypoint_count": len(waypoints),
            "removed_waypoint_count": 0,
        }

    cumulative = [0.0]
    for start, end in zip(waypoints, waypoints[1:]):
        cumulative.append(cumulative[-1] + math.hypot(end[0] - start[0], end[1] - start[1]))

    out = [waypoints[0]]
    current_index = 0
    while current_index < len(waypoints) - 1:
        next_index = current_index + 1
        for candidate_index in range(len(waypoints) - 1, current_index, -1):
            if cumulative[candidate_index] - cumulative[current_index] > max_segment + 1e-6:
                continue
            start = waypoints[current_index]
            end = waypoints[candidate_index]
            if math.hypot(end[0] - start[0], end[1] - start[1]) > max_segment + 1e-6:
                continue
            if not segment_clear_of_flight_obstacles(
                (start[0], start[1]),
                (end[0], end[1]),
                obstacles,
                args.clearance_margin_m,
            ):
                continue
            next_index = candidate_index
            break
        if waypoints[next_index] != out[-1]:
            out.append(waypoints[next_index])
        current_index = next_index

    return out, {
        "enabled": True,
        "input_waypoint_count": len(waypoints),
        "output_waypoint_count": len(out),
        "removed_waypoint_count": len(waypoints) - len(out),
        "max_segment_m": max_segment,
        "clearance_margin_m": args.clearance_margin_m,
    }


def write_yaml(path: Path, section: str, waypoints: list[tuple[float, float, float]]) -> None:
    lines = [
        "# Generated by Scripts/sunray/generate_factory_l2_clearance_route_waypoints.py",
        "# Mode 1: x y z. Diff-Planner multipoint only reads fixed keys such as test1/test_back.",
        f"{section}:",
    ]
    for x, y, z in waypoints:
        lines.append(f"  - [{x:.6f}, {y:.6f}, {z:.6f}]")
    if section != "test_back":
        x0, y0, z0 = waypoints[0]
        lines.extend(["", "test_back:", f"  - [{x0:.6f}, {y0:.6f}, {z0:.6f}]"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def planned_sensor_proxy(
    waypoints: list[tuple[float, float, float]], boundary: dict[str, float], resolution: float, sensor_radius: float
) -> dict[str, Any]:
    nx = max(1, math.ceil((boundary["max_x_m"] - boundary["min_x_m"]) / resolution))
    ny = max(1, math.ceil((boundary["max_y_m"] - boundary["min_y_m"]) / resolution))
    cells: set[tuple[int, int]] = set()
    radius_cells = max(0, math.ceil(sensor_radius / resolution))
    sample_step = max(0.5, min(resolution, sensor_radius * 0.25))
    samples: list[tuple[float, float]] = []
    if waypoints:
        samples.append((waypoints[0][0], waypoints[0][1]))
    for start, end in zip(waypoints, waypoints[1:]):
        dist = math.hypot(end[0] - start[0], end[1] - start[1])
        steps = max(1, math.ceil(dist / sample_step))
        for step in range(1, steps + 1):
            t = step / steps
            samples.append((start[0] + (end[0] - start[0]) * t, start[1] + (end[1] - start[1]) * t))
    for x, y in samples:
        cx = int((x - boundary["min_x_m"]) / resolution)
        cy = int((y - boundary["min_y_m"]) / resolution)
        for ix in range(cx - radius_cells, cx + radius_cells + 1):
            px = boundary["min_x_m"] + (ix + 0.5) * resolution
            if px < boundary["min_x_m"] or px > boundary["max_x_m"]:
                continue
            for iy in range(cy - radius_cells, cy + radius_cells + 1):
                py = boundary["min_y_m"] + (iy + 0.5) * resolution
                if py < boundary["min_y_m"] or py > boundary["max_y_m"]:
                    continue
                if math.hypot(px - x, py - y) <= sensor_radius:
                    cells.add((ix, iy))
    return {
        "grid_resolution_m": resolution,
        "sensor_radius_m": sensor_radius,
        "grid_shape": [nx, ny],
        "grid_cell_count": nx * ny,
        "path_sample_step_m": sample_step,
        "path_sample_count": len(samples),
        "planned_sensor_footprint_cells": len(cells),
        "planned_sensor_footprint_coverage_ratio": len(cells) / (nx * ny),
    }


def sensor_proxy_cells_for_point(
    x: float,
    y: float,
    boundary: dict[str, float],
    resolution: float,
    sensor_radius: float,
) -> set[tuple[int, int]]:
    cx = int((x - boundary["min_x_m"]) / resolution)
    cy = int((y - boundary["min_y_m"]) / resolution)
    radius_cells = max(0, math.ceil(sensor_radius / resolution))
    cells: set[tuple[int, int]] = set()
    for ix in range(cx - radius_cells, cx + radius_cells + 1):
        px = boundary["min_x_m"] + (ix + 0.5) * resolution
        if px < boundary["min_x_m"] or px > boundary["max_x_m"]:
            continue
        for iy in range(cy - radius_cells, cy + radius_cells + 1):
            py = boundary["min_y_m"] + (iy + 0.5) * resolution
            if py < boundary["min_y_m"] or py > boundary["max_y_m"]:
                continue
            if math.hypot(px - x, py - y) <= sensor_radius:
                cells.add((ix, iy))
    return cells


def sensor_proxy_grid_cell_count(boundary: dict[str, float], resolution: float) -> int:
    nx = max(1, math.ceil((boundary["max_x_m"] - boundary["min_x_m"]) / resolution))
    ny = max(1, math.ceil((boundary["max_y_m"] - boundary["min_y_m"]) / resolution))
    return nx * ny


def route_quality(waypoints: list[tuple[float, float, float]]) -> dict[str, Any]:
    duplicate_xy = 0
    seen_xy: set[tuple[float, float]] = set()
    sharp_reversal_count = 0
    max_segment_m = 0.0
    path_length_m = 0.0
    for point in waypoints:
        key = (round(point[0], 3), round(point[1], 3))
        if key in seen_xy:
            duplicate_xy += 1
        seen_xy.add(key)
    for start, end in zip(waypoints, waypoints[1:]):
        segment = math.hypot(end[0] - start[0], end[1] - start[1])
        path_length_m += segment
        max_segment_m = max(max_segment_m, segment)
    for index in range(1, len(waypoints) - 1):
        previous = waypoints[index - 1]
        current = waypoints[index]
        following = waypoints[index + 1]
        ax = current[0] - previous[0]
        ay = current[1] - previous[1]
        bx = following[0] - current[0]
        by = following[1] - current[1]
        norm_a = math.hypot(ax, ay)
        norm_b = math.hypot(bx, by)
        if norm_a <= 1e-9 or norm_b <= 1e-9:
            continue
        cosine = (ax * bx + ay * by) / (norm_a * norm_b)
        if cosine < -0.70710678118:
            sharp_reversal_count += 1
    return {
        "path_length_m": path_length_m,
        "max_segment_m": max_segment_m,
        "duplicate_xy_occurrence_count": duplicate_xy,
        "unique_xy_count": len(seen_xy),
        "sharp_reversal_count": sharp_reversal_count,
    }


def segment_clearance_audit(
    waypoints: list[tuple[float, float, float]],
    obstacles: list[Proxy],
    margin: float,
) -> dict[str, Any]:
    blocked: list[dict[str, Any]] = []
    for index, (start, end) in enumerate(zip(waypoints, waypoints[1:])):
        start_xy = (start[0], start[1])
        end_xy = (end[0], end[1])
        hits = [
            obstacle
            for obstacle in obstacles
            if segment_intersects_rect(start_xy, end_xy, obstacle.rect, margin)
        ]
        if hits:
            blocked.append(
                {
                    "segment_index": index,
                    "start": list(start),
                    "end": list(end),
                    "obstacle_count": len(hits),
                    "first_obstacles": [
                        {
                            "actor": hit.actor,
                            "min_xy": [hit.rect.min_x, hit.rect.min_y],
                            "max_xy": [hit.rect.max_x, hit.rect.max_y],
                            "min_z": hit.min_z,
                            "max_z": hit.max_z,
                        }
                        for hit in hits[:5]
                    ],
                }
            )
    return {
        "segment_clearance_checked": True,
        "clearance_margin_m": margin,
        "blocked_segment_count": len(blocked),
        "first_blocked_segments": blocked[:20],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope", default=str(DEFAULT_ENVELOPE))
    parser.add_argument("--scene-truth", default=str(DEFAULT_TRUTH))
    parser.add_argument("--output-yaml", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--section", default="test1")
    parser.add_argument("--z-m", type=float, default=1.2)
    parser.add_argument("--start-x-m", type=float, default=None)
    parser.add_argument("--start-y-m", type=float, default=None)
    parser.add_argument("--grid-step-m", type=float, default=5.0)
    parser.add_argument(
        "--transit-grid-step-m",
        type=float,
        default=0.0,
        help=(
            "Grid step for obstacle-avoiding transit A*. Defaults to "
            "min(grid-step-m, 1.5). Keep this finer than the coverage grid so "
            "Factory wall/beam detours do not collapse into dropped endpoints."
        ),
    )
    parser.add_argument("--boundary-margin-m", type=float, default=2.0)
    parser.add_argument("--floor-edge-margin-m", type=float, default=0.5)
    parser.add_argument("--clearance-margin-m", type=float, default=1.0)
    parser.add_argument("--flight-obstacle-min-z-m", type=float, default=0.7)
    parser.add_argument("--flight-obstacle-max-z-m", type=float, default=1.7)
    parser.add_argument(
        "--obstacle-z-inflation-m",
        type=float,
        default=0.0,
        help=(
            "Inflate obstacle z ranges before flight-layer filtering. Use this "
            "for Diff/EGO runs where occupancy inflation makes low obstacles "
            "near the commanded layer unsafe as final goals."
        ),
    )
    parser.add_argument(
        "--overhead-obstacle-max-min-z-m",
        type=float,
        default=0.0,
        help=(
            "When positive, also exclude XY projections of non-floor objects "
            "whose lower face is below this height and whose upper face reaches "
            "the flight obstacle band. This avoids low ceilings/platforms that "
            "make the lidar/ESDF route unsafe even when the nominal flight layer "
            "is not inside the source-truth AABB."
        ),
    )
    parser.add_argument(
        "--route-policy",
        choices=(
            "nearest_neighbor",
            "nearest_neighbor_transit",
            "coverage_gain_transit",
            "ordered_targets",
            "astar_connected",
        ),
        default="nearest_neighbor",
    )
    parser.add_argument(
        "--coverage-order",
        choices=("topdown", "bottomup", "start_outward"),
        default="topdown",
    )
    parser.add_argument("--include-center-start", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--min-start-target-distance-m", type=float, default=4.0)
    parser.add_argument("--max-coverage-targets", type=int, default=0)
    parser.add_argument("--max-waypoints", type=int, default=0)
    parser.add_argument("--max-segment-m", type=float, default=0.0)
    parser.add_argument("--drop-immediate-backtracks", action="store_true")
    parser.add_argument("--coverage-resolution-m", type=float, default=2.0)
    parser.add_argument("--sensor-radius-m", type=float, default=8.0)
    parser.add_argument("--coverage-target-min-new-cells", type=int, default=15)
    parser.add_argument("--coverage-target-stop-ratio", type=float, default=0.82)
    args = parser.parse_args()

    envelope = repo_path(args.envelope)
    scene_truth = repo_path(args.scene_truth)
    output_yaml = repo_path(args.output_yaml)
    output_json = repo_path(args.output_json)
    boundary = load_boundary(envelope)
    truth = read_json(scene_truth)
    proxies = [proxy_from_raw(p) for p in truth.get("collision_proxies", []) if isinstance(p, dict)]
    proxies = [p for p in proxies if p is not None]
    free, grid_stats = build_free_grid(boundary, proxies, args)
    flight_obstacles = flight_obstacle_proxies(proxies, args)
    transit = build_transit_grid(boundary, flight_obstacles, args)
    waypoints, route_stats = build_route(free, boundary, args, transit, flight_obstacles)
    waypoints, transit_stats = insert_transit_waypoints(waypoints, boundary, proxies, args)
    if args.drop_immediate_backtracks:
        waypoints, backtrack_stats = drop_immediate_backtracks(waypoints)
    else:
        backtrack_stats = {
            "enabled": False,
            "removed_waypoint_count": 0,
            "epsilon_m": 0.0,
        }
    waypoints, simplification_stats = simplify_clear_segments(waypoints, flight_obstacles, args)
    if not waypoints:
        raise SystemExit("no clearance-route waypoints generated")
    write_yaml(output_yaml, args.section, waypoints)
    packet = {
        "schema": "mosim.factory_l2_clearance_route_waypoints.v1",
        "status": "planned" if route_stats["skipped_unreachable_target_count"] == 0 else "planned_with_skipped_unreachable_targets",
        "envelope": str(envelope),
        "scene_truth": str(scene_truth),
        "output_yaml": str(output_yaml),
        "section": args.section,
        "boundary": boundary,
        "parameters": {
            "z_m": args.z_m,
            "start_x_m": args.start_x_m,
            "start_y_m": args.start_y_m,
            "grid_step_m": args.grid_step_m,
            "transit_grid_step_m": transit_grid_step_m(args),
            "boundary_margin_m": args.boundary_margin_m,
            "floor_edge_margin_m": args.floor_edge_margin_m,
            "clearance_margin_m": args.clearance_margin_m,
            "flight_obstacle_min_z_m": args.flight_obstacle_min_z_m,
            "flight_obstacle_max_z_m": args.flight_obstacle_max_z_m,
            "obstacle_z_inflation_m": args.obstacle_z_inflation_m,
            "overhead_obstacle_max_min_z_m": args.overhead_obstacle_max_min_z_m,
            "route_policy": args.route_policy,
            "coverage_order": args.coverage_order,
            "max_coverage_targets": args.max_coverage_targets,
            "max_waypoints": args.max_waypoints,
            "max_segment_m": args.max_segment_m,
            "drop_immediate_backtracks": bool(args.drop_immediate_backtracks),
            "coverage_resolution_m": args.coverage_resolution_m,
            "sensor_radius_m": args.sensor_radius_m,
            "coverage_target_min_new_cells": args.coverage_target_min_new_cells,
            "coverage_target_stop_ratio": args.coverage_target_stop_ratio,
        },
        "grid_stats": grid_stats,
        "route_stats": route_stats,
        "transit_stats": transit_stats,
        "backtrack_stats": backtrack_stats,
        "simplification_stats": simplification_stats,
        "waypoint_count": len(waypoints),
        "first_waypoint": list(waypoints[0]),
        "last_waypoint": list(waypoints[-1]),
        "waypoints": [list(point) for point in waypoints],
        "route_quality": route_quality(waypoints),
        "segment_clearance_audit": segment_clearance_audit(waypoints, flight_obstacles, args.clearance_margin_m),
        "planned_coverage_proxy": planned_sensor_proxy(waypoints, boundary, args.coverage_resolution_m, args.sensor_radius_m),
        "claim_boundary": [
            "This is a source-truth clearance-filtered support route, not autonomous unknown exploration.",
            "UE collision truth is used only to keep scripted goals out of known obstacles before runtime.",
            "Acceptance still requires ROS1/Sunray/PX4/MAVROS/px4ctrl runtime metrics and FACTORY_L2_INDOOR_COVERAGE_PACKET.json.",
        ],
    }
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    print(output_yaml)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
