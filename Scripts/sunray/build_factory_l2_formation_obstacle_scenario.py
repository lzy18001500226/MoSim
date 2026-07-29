#!/usr/bin/env python3
"""Select a Factory L2 formation translation whose direct path is obstructed."""

from __future__ import annotations

import argparse
import heapq
import json
import math
from pathlib import Path

import generate_factory_l2_clearance_route_waypoints as clearance


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "Config/scenarios/formation/factory_l2_three_uav_obstacle_crossing.json"
# The 1.20 m nominal layout can compress near the predictive 1.10 m guard
# during a live formation turn. Keep the hard 1.0 m separation gate unchanged
# and use a statically verified 1.40 m nominal layout for the Factory route.
DEFAULT_SCALE = 0.70
DEFAULT_ROTATION_DEG = -4.0
# r52 measured a maximum 1.676 s age between the relayed trajectory start time
# and a receiving planner. Keep this Factory-L2-only envelope explicit rather
# than changing the shared Swarm-Formation launch default.
SWARM_TRAJECTORY_RECEIVER_TIME_TOLERANCE_S = 2.0
SWARM_TRAJECTORY_R52_MAX_RECEIVE_AGE_S = 1.676
# The former r46 leader target is not clear for all three translated members
# under the live planner's 1.70 m inflated obstacle field.  This northbound
# target keeps the grounded r46 UAV2 spawn anchor, crosses CargoCart for every
# member, and has a conservative local static A* detour for each member.
DEFAULT_PREFERRED_TARGET_CENTER = (-12.27082453062655, -5.44209645694079)
R46_LEADER_ROUTE_TARGET_CENTER = (-16.679266719908025, -8.0868185505691)
# r46 is the last complete Factory formation run.  Its second vehicle was
# grounded and attitude-stable at this requested spawn before takeoff.
R46_STABLE_UAV2_REQUESTED_START = (-11.27595, -20.11313)
R46_STABLE_UAV2_OBSERVED_TRUTH_START = (-11.316647810326522, -20.11095083884625)
STATIC_ASTAR_CLEARANCE_MARGIN_M = 1.70
STATIC_ASTAR_GRID_STEP_M = 0.20
STATIC_ASTAR_SEARCH_PADDING_M = 5.0
# The live Swarm-Formation planner reaches this static corridor reliably only
# when each known center target stays within one local-horizon-sized segment.
# This does not alter the route, obstacle inflation, or formation footprint.
RIGID_CENTER_MAX_WAYPOINT_SEGMENT_M = 2.0
RIGID_CENTER_FIXED_PATH_SAMPLE_STEP_M = 0.05
FACTORY_TARGET_REACHED_RADIUS_M = 0.25
FACTORY_TARGET_HOLD_S = 2.0
# These candidates are selected only after both the per-UAV and common rigid
# center-path audits pass. The live planner receives only the final formation
# center; it must still avoid the pallet from its own MID360 occupancy map.
STATIC_RIGID_ROUTE_CATALOG = (
    {
        "id": "container_west_aisle_lower_corridor_v2",
        "source": "static_rigid_catalog_container_west_aisle_lower_corridor_v2",
        "start_center_xy_m": (-72.4, 5.04),
        "target_center_xy_m": (-85.6, 3.44),
        "center_waypoints_xy_m": (
            (-72.4, 5.04),
            (-74.4, 5.04),
            (-76.4, 5.04),
            (-78.4, 5.04),
            (-80.4, 5.04),
            (-80.8, 3.44),
            (-82.8, 3.44),
            (-84.8, 3.44),
            (-85.6, 3.44),
        ),
        "selection_rationale": (
            "Leader UAV direct path is blocked by SM_Container01_100. "
            "This fixed lower corridor remains statically clear for the complete rigid formation "
            "at the live 1.70 m field and moves the container passage 0.40 m south of r60's route."
        ),
    },
)


def formation_relative_positions(rotation_deg: float = 0.0) -> dict[str, list[float]]:
    angle = math.radians(rotation_deg)
    cosine = math.cos(angle)
    sine = math.sin(angle)
    canonical = ((0.0, 0.0), (1.7321, -1.0), (0.0, -2.0))
    return {
        str(uid): [cosine * x - sine * y, sine * x + cosine * y]
        for uid, (x, y) in enumerate(canonical, start=1)
    }


def formation_positions(
    center: tuple[float, float], scale: float, rotation_deg: float = 0.0
) -> dict[str, list[float]]:
    relative_positions = formation_relative_positions(rotation_deg)
    return {
        uid: [center[0] + scale * offset[0], center[1] + scale * offset[1]]
        for uid, offset in relative_positions.items()
    }


def center_for_uav2_start(
    uav2_start: tuple[float, float], scale: float, rotation_deg: float
) -> tuple[float, float]:
    relative = formation_relative_positions(rotation_deg)["2"]
    return (
        uav2_start[0] - scale * relative[0],
        uav2_start[1] - scale * relative[1],
    )


def route_candidate(
    *,
    start_center: tuple[float, float],
    target_center: tuple[float, float],
    start_positions: dict[str, list[float]],
    target_positions: dict[str, list[float]],
    obstacles: list[clearance.Proxy],
    margin: float,
    start_shift_m: float,
    source: str,
    allow_multiple_member_hits: bool = False,
) -> dict | None:
    hits = [
        obstacle
        for obstacle in obstacles
        if clearance.segment_intersects_rect(start_center, target_center, obstacle.rect, margin)
    ]
    if not hits:
        return None
    member_hits = {
        uid: [
            obstacle
            for obstacle in obstacles
            if clearance.segment_intersects_rect(
                tuple(start_positions[uid]),
                tuple(target_positions[uid]),
                obstacle.rect,
                margin,
            )
        ]
        for uid in start_positions
    }
    if not allow_multiple_member_hits and any(
        len(path_hits) > 1 for path_hits in member_hits.values()
    ):
        return None
    hit_spans = [
        max(obstacle.rect.max_x - obstacle.rect.min_x, obstacle.rect.max_y - obstacle.rect.min_y)
        for path_hits in member_hits.values()
        for obstacle in path_hits
    ]
    if not hit_spans:
        return None
    return {
        "start_shift_m": start_shift_m,
        "start_center": start_center,
        "start_positions": start_positions,
        "center": target_center,
        "positions": target_positions,
        "distance_m": math.dist(start_center, target_center),
        "angle_deg": math.degrees(
            math.atan2(target_center[1] - start_center[1], target_center[0] - start_center[0])
        ),
        "hits": hits,
        "member_hits": member_hits,
        "maximum_hit_planar_span_m": max(hit_spans),
        "obstacle_intersection_clearance_margin_m": margin,
        "allow_multiple_member_hits": allow_multiple_member_hits,
        "source": source,
    }


def positions_are_clear(
    positions: dict[str, list[float]],
    floors: list[clearance.Proxy],
    obstacles: list[clearance.Proxy],
    margin: float,
) -> bool:
    for x, y in positions.values():
        if not any(clearance.point_inside_rect(x, y, floor.rect, 0.35) for floor in floors):
            return False
        if not clearance.point_clear_of_flight_obstacles(x, y, obstacles, margin):
            return False
    return True


def static_astar_member_audit(
    *,
    boundary: dict[str, float],
    start_positions: dict[str, list[float]],
    target_positions: dict[str, list[float]],
    obstacles: list[clearance.Proxy],
    clearance_margin_m: float,
    grid_step_m: float,
    search_padding_m: float,
) -> dict:
    """Prove that every translated member has a conservative static XY detour.

    The test intentionally uses collision truth only while choosing a scenario.
    It is not a planner input: the live route still consumes per-UAV MID360
    clouds and occupancy maps.  A local bounded grid avoids making scenario
    generation proportional to the full Factory map area.
    """
    per_uav: dict[str, dict] = {}
    boundary_min_x = boundary["min_x_m"] + 2.0
    boundary_max_x = boundary["max_x_m"] - 2.0
    boundary_min_y = boundary["min_y_m"] + 2.0
    boundary_max_y = boundary["max_y_m"] - 2.0

    for uid, start in start_positions.items():
        target = target_positions[uid]
        start_xy = (float(start[0]), float(start[1]))
        target_xy = (float(target[0]), float(target[1]))
        start_clear = clearance.point_clear_of_flight_obstacles(
            *start_xy, obstacles, clearance_margin_m
        )
        target_clear = clearance.point_clear_of_flight_obstacles(
            *target_xy, obstacles, clearance_margin_m
        )
        details: dict = {
            "start_endpoint_clear": start_clear,
            "target_endpoint_clear": target_clear,
            "path_found": False,
            "direct_distance_m": math.dist(start_xy, target_xy),
        }
        if not start_clear or not target_clear:
            per_uav[uid] = details
            continue

        min_x = max(boundary_min_x, min(start_xy[0], target_xy[0]) - search_padding_m)
        max_x = min(boundary_max_x, max(start_xy[0], target_xy[0]) + search_padding_m)
        min_y = max(boundary_min_y, min(start_xy[1], target_xy[1]) - search_padding_m)
        max_y = min(boundary_max_y, max(start_xy[1], target_xy[1]) + search_padding_m)
        relevant_obstacles = [
            obstacle
            for obstacle in obstacles
            if not (
                obstacle.rect.max_x + clearance_margin_m < min_x
                or obstacle.rect.min_x - clearance_margin_m > max_x
                or obstacle.rect.max_y + clearance_margin_m < min_y
                or obstacle.rect.min_y - clearance_margin_m > max_y
            )
        ]
        free: dict[tuple[int, int], tuple[float, float]] = {}
        ix = 0
        x = min_x
        while x <= max_x + 1e-9:
            iy = 0
            y = min_y
            while y <= max_y + 1e-9:
                if clearance.point_clear_of_flight_obstacles(
                    x, y, relevant_obstacles, clearance_margin_m
                ):
                    free[(ix, iy)] = (x, y)
                y += grid_step_m
                iy += 1
            x += grid_step_m
            ix += 1

        if not free:
            details["relevant_obstacle_count"] = len(relevant_obstacles)
            details["free_cell_count"] = 0
            per_uav[uid] = details
            continue
        start_cell = clearance.nearest_cell(free, *start_xy)
        target_cell = clearance.nearest_cell(free, *target_xy)
        path = clearance.astar(
            start_cell,
            target_cell,
            set(free),
            free,
            relevant_obstacles,
            clearance_margin_m,
        )
        details["relevant_obstacle_count"] = len(relevant_obstacles)
        details["free_cell_count"] = len(free)
        if path is not None:
            points = [free[cell] for cell in path]
            length = sum(math.dist(first, second) for first, second in zip(points, points[1:]))
            details.update(
                {
                    "path_found": True,
                    "waypoint_count": len(points),
                    "path_length_m": length,
                    "detour_excess_m": length - details["direct_distance_m"],
                    "start_snap_error_m": math.dist(start_xy, points[0]),
                    "target_snap_error_m": math.dist(target_xy, points[-1]),
                }
            )
        per_uav[uid] = details

    return {
        "status": "passed" if all(item["path_found"] for item in per_uav.values()) else "blocked",
        "clearance_margin_m": clearance_margin_m,
        "grid_step_m": grid_step_m,
        "search_padding_m": search_padding_m,
        "per_uav": per_uav,
        "claim_boundary": (
            "Static UE collision truth is used only to select a feasible obstacle-crossing "
            "scenario. Live Swarm-Formation still consumes per-UAV MID360 world clouds "
            "and occupancy maps."
        ),
    }


def rigid_center_segment_clear(
    start_center: tuple[float, float],
    end_center: tuple[float, float],
    *,
    scale: float,
    rotation_deg: float,
    floors: list[clearance.Proxy],
    obstacles: list[clearance.Proxy],
    clearance_margin_m: float,
    sample_step_m: float,
) -> bool:
    """Check the complete translated three-UAV footprint along one center segment."""
    distance = math.dist(start_center, end_center)
    steps = max(1, math.ceil(distance / max(sample_step_m, 0.02)))
    for index in range(steps + 1):
        fraction = index / steps
        center = (
            start_center[0] + (end_center[0] - start_center[0]) * fraction,
            start_center[1] + (end_center[1] - start_center[1]) * fraction,
        )
        if not positions_are_clear(
            formation_positions(center, scale, rotation_deg),
            floors,
            obstacles,
            clearance_margin_m,
        ):
            return False
    return True


def rigid_center_astar_audit(
    *,
    boundary: dict[str, float],
    start_center: tuple[float, float],
    target_center: tuple[float, float],
    scale: float,
    rotation_deg: float,
    floors: list[clearance.Proxy],
    obstacles: list[clearance.Proxy],
    clearance_margin_m: float,
    grid_step_m: float,
    search_padding_m: float,
    max_waypoint_segment_m: float,
) -> dict:
    """Prove one common detour is free for every member of the rigid formation.

    The earlier per-UAV A* contract establishes that each vehicle can find a
    route by itself.  It does not establish that leader-following offsets can
    remain rigid through the same corridor.  This center-space A* checks all
    three translated positions at every grid cell and along every accepted
    edge, then returns a short waypoint chain for the global center-goal API.
    """
    if not positions_are_clear(
        formation_positions(start_center, scale, rotation_deg),
        floors,
        obstacles,
        clearance_margin_m,
    ):
        return {"status": "blocked", "blockers": ["start_formation_not_clear"]}
    if not positions_are_clear(
        formation_positions(target_center, scale, rotation_deg),
        floors,
        obstacles,
        clearance_margin_m,
    ):
        return {"status": "blocked", "blockers": ["target_formation_not_clear"]}

    relative_positions = formation_relative_positions(rotation_deg)
    footprint_radius_m = max(
        math.hypot(scale * offset[0], scale * offset[1])
        for offset in relative_positions.values()
    )
    boundary_min_x = boundary["min_x_m"] + 2.0 + footprint_radius_m
    boundary_max_x = boundary["max_x_m"] - 2.0 - footprint_radius_m
    boundary_min_y = boundary["min_y_m"] + 2.0 + footprint_radius_m
    boundary_max_y = boundary["max_y_m"] - 2.0 - footprint_radius_m
    min_x = max(boundary_min_x, min(start_center[0], target_center[0]) - search_padding_m)
    max_x = min(boundary_max_x, max(start_center[0], target_center[0]) + search_padding_m)
    min_y = max(boundary_min_y, min(start_center[1], target_center[1]) - search_padding_m)
    max_y = min(boundary_max_y, max(start_center[1], target_center[1]) + search_padding_m)
    if min_x >= max_x or min_y >= max_y:
        return {"status": "blocked", "blockers": ["rigid_search_window_empty"]}

    relevant_obstacles = [
        obstacle
        for obstacle in obstacles
        if not (
            obstacle.rect.max_x + clearance_margin_m + footprint_radius_m < min_x
            or obstacle.rect.min_x - clearance_margin_m - footprint_radius_m > max_x
            or obstacle.rect.max_y + clearance_margin_m + footprint_radius_m < min_y
            or obstacle.rect.min_y - clearance_margin_m - footprint_radius_m > max_y
        )
    ]
    free: dict[tuple[int, int], tuple[float, float]] = {}
    ix = 0
    x = min_x
    while x <= max_x + 1e-9:
        iy = 0
        y = min_y
        while y <= max_y + 1e-9:
            center = (x, y)
            if positions_are_clear(
                formation_positions(center, scale, rotation_deg),
                floors,
                relevant_obstacles,
                clearance_margin_m,
            ):
                free[(ix, iy)] = center
            y += grid_step_m
            iy += 1
        x += grid_step_m
        ix += 1
    if not free:
        return {
            "status": "blocked",
            "blockers": ["rigid_free_space_empty"],
            "relevant_obstacle_count": len(relevant_obstacles),
        }

    start_cell = clearance.nearest_cell(free, *start_center)
    target_cell = clearance.nearest_cell(free, *target_center)

    def edge_clear(left: tuple[float, float], right: tuple[float, float]) -> bool:
        return rigid_center_segment_clear(
            left,
            right,
            scale=scale,
            rotation_deg=rotation_deg,
            floors=floors,
            obstacles=relevant_obstacles,
            clearance_margin_m=clearance_margin_m,
            sample_step_m=grid_step_m / 2.0,
        )

    if not edge_clear(start_center, free[start_cell]):
        return {"status": "blocked", "blockers": ["rigid_start_snap_not_clear"]}
    if not edge_clear(free[target_cell], target_center):
        return {"status": "blocked", "blockers": ["rigid_target_snap_not_clear"]}

    open_nodes: list[tuple[float, float, tuple[int, int]]] = []
    heapq.heappush(open_nodes, (math.dist(free[start_cell], free[target_cell]), 0.0, start_cell))
    cost: dict[tuple[int, int], float] = {start_cell: 0.0}
    previous: dict[tuple[int, int], tuple[int, int]] = {}
    found = False
    while open_nodes:
        _, current_cost, cell = heapq.heappop(open_nodes)
        if current_cost > cost.get(cell, float("inf")) + 1e-9:
            continue
        if cell == target_cell:
            found = True
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            next_cell = (cell[0] + dx, cell[1] + dy)
            if next_cell not in free or not edge_clear(free[cell], free[next_cell]):
                continue
            next_cost = current_cost + math.dist(free[cell], free[next_cell])
            if next_cost + 1e-9 >= cost.get(next_cell, float("inf")):
                continue
            cost[next_cell] = next_cost
            previous[next_cell] = cell
            priority = next_cost + math.dist(free[next_cell], free[target_cell])
            heapq.heappush(open_nodes, (priority, next_cost, next_cell))
    if not found:
        return {
            "status": "blocked",
            "blockers": ["rigid_center_path_not_found"],
            "relevant_obstacle_count": len(relevant_obstacles),
            "free_cell_count": len(free),
        }

    cells = [target_cell]
    while cells[-1] != start_cell:
        cells.append(previous[cells[-1]])
    cells.reverse()
    raw_points = [start_center, *(free[cell] for cell in cells), target_center]
    compact_points: list[tuple[float, float]] = []
    for point in raw_points:
        if not compact_points or math.dist(compact_points[-1], point) > 1e-9:
            compact_points.append(point)

    simplified = [compact_points[0]]
    current_index = 0
    while current_index < len(compact_points) - 1:
        furthest = current_index + 1
        for candidate_index in range(current_index + 1, len(compact_points)):
            if math.dist(compact_points[current_index], compact_points[candidate_index]) > max_waypoint_segment_m + 1e-9:
                break
            if edge_clear(compact_points[current_index], compact_points[candidate_index]):
                furthest = candidate_index
        simplified.append(compact_points[furthest])
        current_index = furthest

    raw_length = sum(math.dist(left, right) for left, right in zip(compact_points, compact_points[1:]))
    simplified_length = sum(math.dist(left, right) for left, right in zip(simplified, simplified[1:]))
    return {
        "status": "passed",
        "clearance_margin_m": clearance_margin_m,
        "grid_step_m": grid_step_m,
        "search_padding_m": search_padding_m,
        "max_waypoint_segment_m": max_waypoint_segment_m,
        "formation_footprint_radius_m": footprint_radius_m,
        "relevant_obstacle_count": len(relevant_obstacles),
        "free_cell_count": len(free),
        "grid_path_waypoint_count": len(compact_points),
        "grid_path_length_m": raw_length,
        "center_waypoints_xy_m": [[round(x, 6), round(y, 6)] for x, y in simplified],
        "center_waypoint_count": len(simplified),
        "center_path_length_m": simplified_length,
        "detour_excess_m": simplified_length - math.dist(start_center, target_center),
        "start_snap_error_m": math.dist(start_center, free[start_cell]),
        "target_snap_error_m": math.dist(target_center, free[target_cell]),
        "claim_boundary": (
            "The common center path is selected from static collision truth only. "
            "At runtime, each UAV still uses its own MID360/FAST-LIO/local occupancy input; "
            "the chain is a known-route formation traversal, not autonomous exploration."
        ),
    }


def rigid_center_fixed_path_audit(
    *,
    center_waypoints: tuple[tuple[float, float], ...],
    start_center: tuple[float, float],
    target_center: tuple[float, float],
    scale: float,
    rotation_deg: float,
    floors: list[clearance.Proxy],
    obstacles: list[clearance.Proxy],
    clearance_margin_m: float,
    segment_sample_step_m: float,
) -> dict:
    """Audit a catalogued rigid-formation route without changing it via A*.

    This is a static scenario-selection check only. It samples every catalogued
    segment against the complete translated formation at the same 1.70 m
    obstacle field used by the live planner, but it never supplies scene truth
    to the runtime planner or controller.
    """
    points = tuple((float(point[0]), float(point[1])) for point in center_waypoints)
    blockers: list[str] = []
    if len(points) < 2:
        blockers.append("fixed_center_path_too_short")
    if segment_sample_step_m <= 0.0:
        blockers.append("fixed_center_path_sample_step_invalid")
    if points and math.dist(points[0], start_center) > 1e-6:
        blockers.append("fixed_center_path_start_mismatch")
    if points and math.dist(points[-1], target_center) > 1e-6:
        blockers.append("fixed_center_path_target_mismatch")

    waypoint_checks: list[dict] = []
    for index, point in enumerate(points):
        clear = positions_are_clear(
            formation_positions(point, scale, rotation_deg),
            floors,
            obstacles,
            clearance_margin_m,
        )
        if not clear:
            blockers.append(f"fixed_center_waypoint_{index}_not_clear")
        waypoint_checks.append(
            {
                "index": index,
                "xy_m": [round(point[0], 6), round(point[1], 6)],
                "status": "passed" if clear else "blocked",
            }
        )

    segment_checks: list[dict] = []
    for index, (left, right) in enumerate(zip(points, points[1:])):
        clear = rigid_center_segment_clear(
            left,
            right,
            scale=scale,
            rotation_deg=rotation_deg,
            floors=floors,
            obstacles=obstacles,
            clearance_margin_m=clearance_margin_m,
            sample_step_m=segment_sample_step_m,
        )
        if not clear:
            blockers.append(f"fixed_center_segment_{index}_not_clear")
        segment_checks.append(
            {
                "start_index": index,
                "end_index": index + 1,
                "length_m": math.dist(left, right),
                "status": "passed" if clear else "blocked",
            }
        )

    path_length_m = sum(math.dist(left, right) for left, right in zip(points, points[1:]))
    relative_positions = formation_relative_positions(rotation_deg)
    footprint_radius_m = max(
        math.hypot(scale * offset[0], scale * offset[1])
        for offset in relative_positions.values()
    )
    return {
        "status": "passed" if not blockers else "blocked",
        "route_selection": "explicit_catalog_fixed_path",
        "clearance_margin_m": clearance_margin_m,
        "segment_sample_step_m": segment_sample_step_m,
        "formation_footprint_radius_m": footprint_radius_m,
        "center_waypoints_xy_m": [[round(x, 6), round(y, 6)] for x, y in points],
        "center_waypoint_count": len(points),
        "center_path_length_m": path_length_m,
        "detour_excess_m": path_length_m - math.dist(start_center, target_center),
        "waypoint_checks": waypoint_checks,
        "segment_checks": segment_checks,
        "blockers": list(dict.fromkeys(blockers)),
        "claim_boundary": (
            "The exact common center path is selected and audited from static collision truth only. "
            "At runtime, each UAV still uses its own MID360/FAST-LIO/local occupancy input; "
            "the fixed chain is a known-route formation traversal, not autonomous exploration."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope", default=str(clearance.DEFAULT_ENVELOPE))
    parser.add_argument("--scene-truth", default=str(clearance.DEFAULT_TRUTH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--scale", type=float, default=DEFAULT_SCALE)
    parser.add_argument("--rotation-deg", type=float, default=DEFAULT_ROTATION_DEG)
    parser.add_argument("--z-m", type=float, default=1.2)
    parser.add_argument("--clearance-margin-m", type=float, default=1.0)
    parser.add_argument("--min-distance-m", type=float, default=8.0)
    parser.add_argument("--max-distance-m", type=float, default=14.0)
    parser.add_argument(
        "--preferred-target-x-m", type=float, default=DEFAULT_PREFERRED_TARGET_CENTER[0]
    )
    parser.add_argument(
        "--preferred-target-y-m", type=float, default=DEFAULT_PREFERRED_TARGET_CENTER[1]
    )
    parser.add_argument(
        "--static-astar-clearance-margin-m",
        type=float,
        default=STATIC_ASTAR_CLEARANCE_MARGIN_M,
    )
    parser.add_argument("--static-astar-grid-step-m", type=float, default=STATIC_ASTAR_GRID_STEP_M)
    parser.add_argument(
        "--static-astar-search-padding-m", type=float, default=STATIC_ASTAR_SEARCH_PADDING_M
    )
    parser.add_argument(
        "--rigid-center-max-waypoint-segment-m",
        type=float,
        default=RIGID_CENTER_MAX_WAYPOINT_SEGMENT_M,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    envelope_path = clearance.repo_path(args.envelope)
    truth_path = clearance.repo_path(args.scene_truth)
    output_path = clearance.repo_path(args.output)
    boundary = clearance.load_boundary(envelope_path)
    truth = clearance.read_json(truth_path)
    proxies = [
        proxy
        for raw in truth.get("collision_proxies", [])
        if isinstance(raw, dict) and (proxy := clearance.proxy_from_raw(raw)) is not None
    ]
    floors = [proxy for proxy in proxies if clearance.is_low_floor(proxy)]

    obstacle_args = argparse.Namespace(
        flight_obstacle_min_z_m=0.70,
        flight_obstacle_max_z_m=1.70,
        obstacle_z_inflation_m=0.0,
        overhead_obstacle_max_min_z_m=0.0,
    )
    obstacles = clearance.flight_obstacle_proxies(proxies, obstacle_args)
    preferred_center = (boundary["center_x_m"], boundary["center_y_m"])
    runtime_proven_center = center_for_uav2_start(
        R46_STABLE_UAV2_REQUESTED_START, args.scale, args.rotation_deg
    )
    preferred_target = (args.preferred_target_x_m, args.preferred_target_y_m)
    runtime_proven_positions = formation_positions(
        runtime_proven_center, args.scale, args.rotation_deg
    )
    preferred_target_positions = formation_positions(
        preferred_target, args.scale, args.rotation_deg
    )
    candidates: list[dict] = []
    if positions_are_clear(
        runtime_proven_positions, floors, obstacles, args.clearance_margin_m
    ) and positions_are_clear(
        preferred_target_positions, floors, obstacles, args.clearance_margin_m
    ):
        runtime_proven_candidate = route_candidate(
            start_center=runtime_proven_center,
            target_center=preferred_target,
            start_positions=runtime_proven_positions,
            target_positions=preferred_target_positions,
            obstacles=obstacles,
            margin=args.clearance_margin_m,
            start_shift_m=math.dist(runtime_proven_center, preferred_center),
            source="r46_uav2_gazebo_spawn_anchor_preferred_target",
        )
        if runtime_proven_candidate is not None:
            candidates.append(runtime_proven_candidate)

    for catalog_entry in STATIC_RIGID_ROUTE_CATALOG:
        catalog_start = tuple(catalog_entry["start_center_xy_m"])
        catalog_target = tuple(catalog_entry["target_center_xy_m"])
        catalog_start_positions = formation_positions(
            catalog_start, args.scale, args.rotation_deg
        )
        catalog_target_positions = formation_positions(
            catalog_target, args.scale, args.rotation_deg
        )
        if not positions_are_clear(
            catalog_start_positions,
            floors,
            obstacles,
            args.static_astar_clearance_margin_m,
        ) or not positions_are_clear(
            catalog_target_positions,
            floors,
            obstacles,
            args.static_astar_clearance_margin_m,
        ):
            continue
        catalog_candidate = route_candidate(
            start_center=catalog_start,
            target_center=catalog_target,
            start_positions=catalog_start_positions,
            target_positions=catalog_target_positions,
            obstacles=obstacles,
            margin=args.static_astar_clearance_margin_m,
            start_shift_m=math.dist(catalog_start, preferred_center),
            source=str(catalog_entry["source"]),
            allow_multiple_member_hits=True,
        )
        if catalog_candidate is not None:
            catalog_candidate["catalog_id"] = str(catalog_entry["id"])
            catalog_candidate["selection_rationale"] = str(
                catalog_entry["selection_rationale"]
            )
            raw_center_waypoints = catalog_entry.get("center_waypoints_xy_m")
            if raw_center_waypoints is not None:
                catalog_candidate["catalog_center_waypoints_xy_m"] = tuple(
                    (float(point[0]), float(point[1])) for point in raw_center_waypoints
                )
            candidates.append(catalog_candidate)

    # The explicit preferred candidate is the normal path. Only fall back to
    # a finite grid search when a future scene edit invalidates that route.
    if not candidates:
        start_centers: list[tuple[float, tuple[float, float], dict[str, list[float]]]] = []
        for dx in range(-12, 13):
            for dy in range(-12, 13):
                center = (preferred_center[0] + float(dx), preferred_center[1] + float(dy))
                positions = formation_positions(center, args.scale, args.rotation_deg)
                if positions_are_clear(positions, floors, obstacles, args.clearance_margin_m):
                    start_centers.append((math.hypot(dx, dy), center, positions))
        for start_shift, start_center, start_positions in start_centers:
            for distance in range(math.ceil(args.min_distance_m), math.floor(args.max_distance_m) + 1, 2):
                for angle_deg in range(0, 360, 10):
                    angle = math.radians(angle_deg)
                    target_center = (
                        start_center[0] + distance * math.cos(angle),
                        start_center[1] + distance * math.sin(angle),
                    )
                    if not (
                        boundary["min_x_m"] + 2.0 <= target_center[0] <= boundary["max_x_m"] - 2.0
                        and boundary["min_y_m"] + 2.0 <= target_center[1] <= boundary["max_y_m"] - 2.0
                    ):
                        continue
                    target_positions = formation_positions(target_center, args.scale, args.rotation_deg)
                    if not positions_are_clear(target_positions, floors, obstacles, args.clearance_margin_m):
                        continue
                    candidate = route_candidate(
                        start_center=start_center,
                        target_center=target_center,
                        start_positions=start_positions,
                        target_positions=target_positions,
                        obstacles=obstacles,
                        margin=args.clearance_margin_m,
                        start_shift_m=start_shift,
                        source="static_grid_search",
                    )
                    if candidate is not None:
                        candidates.append(candidate)

    if not candidates:
        raise SystemExit("no safe target with an obstacle-blocked direct center path was found")
    candidate_order = sorted(
        candidates,
        key=lambda item: (
            item["source"] != "r46_uav2_gazebo_spawn_anchor_preferred_target",
            not item["source"].startswith("static_rigid_catalog_"),
            len(item["hits"]),
            item["maximum_hit_planar_span_m"],
            math.dist(item["start_center"], runtime_proven_center),
            abs(item["distance_m"] - args.max_distance_m),
        ),
    )
    selected: dict | None = None
    for candidate in candidate_order:
        static_path_audit = static_astar_member_audit(
            boundary=boundary,
            start_positions=candidate["start_positions"],
            target_positions=candidate["positions"],
            obstacles=obstacles,
            clearance_margin_m=args.static_astar_clearance_margin_m,
            grid_step_m=args.static_astar_grid_step_m,
            search_padding_m=args.static_astar_search_padding_m,
        )
        catalog_center_waypoints = candidate.get("catalog_center_waypoints_xy_m")
        if catalog_center_waypoints is not None:
            rigid_center_path_audit = rigid_center_fixed_path_audit(
                center_waypoints=catalog_center_waypoints,
                start_center=candidate["start_center"],
                target_center=candidate["center"],
                scale=args.scale,
                rotation_deg=args.rotation_deg,
                floors=floors,
                obstacles=obstacles,
                clearance_margin_m=args.static_astar_clearance_margin_m,
                segment_sample_step_m=RIGID_CENTER_FIXED_PATH_SAMPLE_STEP_M,
            )
        else:
            rigid_center_path_audit = rigid_center_astar_audit(
                boundary=boundary,
                start_center=candidate["start_center"],
                target_center=candidate["center"],
                scale=args.scale,
                rotation_deg=args.rotation_deg,
                floors=floors,
                obstacles=obstacles,
                clearance_margin_m=args.static_astar_clearance_margin_m,
                grid_step_m=args.static_astar_grid_step_m,
                search_padding_m=args.static_astar_search_padding_m,
                max_waypoint_segment_m=args.rigid_center_max_waypoint_segment_m,
            )
        if static_path_audit["status"] == "passed" and rigid_center_path_audit["status"] == "passed":
            selected = {
                **candidate,
                "static_path_audit": static_path_audit,
                "rigid_center_path_audit": rigid_center_path_audit,
            }
            break
    if selected is None:
        raise SystemExit(
            "no obstacle-crossing candidate has both independent and rigid-center static A* detours "
            f"at {args.static_astar_clearance_margin_m:.2f} m clearance"
        )
    start_center = selected["start_center"]
    start_positions = selected["start_positions"]
    target_center = selected["center"]
    relative_positions = formation_relative_positions(args.rotation_deg)
    footprint_radius = max(
        math.hypot(args.scale * offset[0], args.scale * offset[1])
        for offset in relative_positions.values()
    )
    payload = {
        "schema": "mosim.factory_l2_three_uav_formation_obstacle_crossing.v1",
        "status": "static_scenario_ready_runtime_pending",
        "runtime_contract": {
            "swarm_trajectory_receiver_time_tolerance_s": SWARM_TRAJECTORY_RECEIVER_TIME_TOLERANCE_S,
            "r52_observed_max_receive_age_s": SWARM_TRAJECTORY_R52_MAX_RECEIVE_AGE_S,
            "receiver_age_safety_margin_s": (
                SWARM_TRAJECTORY_RECEIVER_TIME_TOLERANCE_S
                - SWARM_TRAJECTORY_R52_MAX_RECEIVE_AGE_S
            ),
            "semantics": (
                "Factory-L2-only receive-age envelope. The relay keeps its configured "
                "future offset, and the receiving planner preserves the received trajectory "
                "start_time and phase; this does not rewrite timestamps or reset trajectory phase."
            ),
        },
        "mission_target_contract": {
            "target_reached_radius_m": FACTORY_TARGET_REACHED_RADIUS_M,
            "target_hold_s": FACTORY_TARGET_HOLD_S,
            "semantics": (
                "A shared center waypoint may advance only after the translated formation holds "
                "within this radius and velocity gate. The radius is intentionally tighter than "
                "the generic mission default because the container corridor is narrow."
            ),
        },
        "world": "Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf",
        "formation": {
            "type": "three_uav_equilateral_subset_of_normal_hexagon",
            "scale": args.scale,
            "rotation_deg": args.rotation_deg,
            "relative_positions_unit": relative_positions,
            "rigid_footprint_radius_m": footprint_radius,
            "expected_min_pair_distance_m": 2.0 * args.scale,
            "start_center_xy_m": list(start_center),
            "preferred_single_uav_center_xy_m": list(preferred_center),
            "legacy_r46_start_center_xy_m": list(runtime_proven_center),
            "start_center_shift_from_preferred_m": math.dist(start_center, preferred_center),
            "start_positions_xy_m": start_positions,
            "target_center_xy_m": list(target_center),
            "target_positions_xy_m": selected["positions"],
            "z_m": args.z_m,
        },
        "scenario_selection": {
            "preferred_target_center_xy_m": list(preferred_target),
            "selected_replay_compatible_leader_route": (
                math.dist(selected["center"], R46_LEADER_ROUTE_TARGET_CENTER) <= 1e-6
            ),
            "selected_static_astar_ready": True,
            "selected_center_route_kind": selected["rigid_center_path_audit"].get("route_selection", "static_astar"),
            "selected_start_source": selected["source"],
            "selected_catalog_id": selected.get("catalog_id"),
            "selected_rationale": selected.get("selection_rationale"),
            "legacy_r46_spawn_anchor": {
                "reference_run_id": "factory_l2_swarm_formation_envelope_r46_20260722",
                "uav_id": "2",
                "requested_start_xy_m": list(R46_STABLE_UAV2_REQUESTED_START),
                "observed_truth_start_xy_m": list(R46_STABLE_UAV2_OBSERVED_TRUTH_START),
                "semantics": "Historical stable spawn only. It is not evidence that the selected catalog start is physically ready.",
            },
            "selected_spawn_preflight": {
                "status": "required",
                "semantics": "Gazebo truth pose, takeoff and hover gates must pass for all selected start positions before obstacle traversal is attempted.",
            },
            "semantics": "The selected route is statically clear for every member and for the common rigid center path at the live 1.70 m inflated field. It remains runtime-pending until the Gazebo/PX4/MAVROS/MID360 gate passes.",
        },
        "static_path_contract": selected["static_path_audit"],
        "rigid_center_path_contract": selected["rigid_center_path_audit"],
        "obstacle_crossing_contract": {
            "direct_center_segment_blocked": True,
            "clearance_margin_m": selected["obstacle_intersection_clearance_margin_m"],
            "intersecting_proxy_count": len(selected["hits"]),
            "intersecting_proxies": [proxy.actor for proxy in selected["hits"][:20]],
            "maximum_hit_planar_span_m": selected["maximum_hit_planar_span_m"],
            "member_intersecting_proxies": {
                uid: [proxy.actor for proxy in path_hits]
                for uid, path_hits in selected["member_hits"].items()
            },
            "endpoint_formation_positions_clear": True,
            "runtime_requirement": "all UAVs must reach the translated formation through live MID360 occupancy while preserving the formation-error and safety gates",
        },
        "source_truth": str(truth_path.relative_to(ROOT)).replace("\\", "/"),
        "claim_boundary": "Static UE collision proxies select candidate endpoints only; Gazebo pre-takeoff truth pose and the PX4/MAVROS/px4ctrl runtime gates remain authoritative for vehicle-footprint clearance.",
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2))
        handle.write("\n")
    print(output_path)


if __name__ == "__main__":
    main()
