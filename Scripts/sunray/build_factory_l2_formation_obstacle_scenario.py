#!/usr/bin/env python3
"""Select a Factory L2 formation translation whose direct path is obstructed."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import generate_factory_l2_clearance_route_waypoints as clearance


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "Config/scenarios/formation/factory_l2_three_uav_obstacle_crossing.json"


def formation_positions(center: tuple[float, float], scale: float) -> dict[str, list[float]]:
    offsets = ((0.0, 0.0), (1.7321 * scale, -scale), (0.0, -2.0 * scale))
    return {
        str(uid): [center[0] + dx, center[1] + dy]
        for uid, (dx, dy) in enumerate(offsets, start=1)
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--envelope", default=str(clearance.DEFAULT_ENVELOPE))
    parser.add_argument("--scene-truth", default=str(clearance.DEFAULT_TRUTH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--scale", type=float, default=0.75)
    parser.add_argument("--z-m", type=float, default=1.2)
    parser.add_argument("--clearance-margin-m", type=float, default=1.0)
    parser.add_argument("--min-distance-m", type=float, default=8.0)
    parser.add_argument("--max-distance-m", type=float, default=14.0)
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
    runtime_proven_center = (preferred_center[0] - 2.0, preferred_center[1])
    start_centers: list[tuple[float, tuple[float, float], dict[str, list[float]]]] = []
    for dx in range(-12, 13):
        for dy in range(-12, 13):
            center = (preferred_center[0] + float(dx), preferred_center[1] + float(dy))
            positions = formation_positions(center, args.scale)
            if positions_are_clear(positions, floors, obstacles, args.clearance_margin_m):
                start_centers.append((math.hypot(dx, dy), center, positions))
    if not start_centers:
        raise SystemExit("no three-UAV formation-safe start exists near the accepted Factory center")

    candidates: list[dict] = []
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
                target_positions = formation_positions(target_center, args.scale)
                if not positions_are_clear(target_positions, floors, obstacles, args.clearance_margin_m):
                    continue
                hits = [
                    obstacle
                    for obstacle in obstacles
                    if clearance.segment_intersects_rect(
                        start_center,
                        target_center,
                        obstacle.rect,
                        args.clearance_margin_m,
                    )
                ]
                if not hits:
                    continue
                member_hits = {
                    uid: [
                        obstacle
                        for obstacle in obstacles
                        if clearance.segment_intersects_rect(
                            tuple(start_positions[uid]),
                            tuple(target_positions[uid]),
                            obstacle.rect,
                            args.clearance_margin_m,
                        )
                    ]
                    for uid in start_positions
                }
                if any(len(path_hits) > 1 for path_hits in member_hits.values()):
                    continue
                hit_spans = [
                    max(
                        obstacle.rect.max_x - obstacle.rect.min_x,
                        obstacle.rect.max_y - obstacle.rect.min_y,
                    )
                    for path_hits in member_hits.values()
                    for obstacle in path_hits
                ]
                candidates.append(
                    {
                        "start_shift_m": start_shift,
                        "start_center": start_center,
                        "start_positions": start_positions,
                        "center": target_center,
                        "positions": target_positions,
                        "distance_m": float(distance),
                        "angle_deg": angle_deg,
                        "hits": hits,
                        "member_hits": member_hits,
                        "maximum_hit_planar_span_m": max(hit_spans),
                    }
                )

    if not candidates:
        raise SystemExit("no safe target with an obstacle-blocked direct center path was found")
    selected = min(
        candidates,
        key=lambda item: (
            len(item["hits"]),
            item["maximum_hit_planar_span_m"],
            math.dist(item["start_center"], runtime_proven_center),
            abs(item["distance_m"] - args.max_distance_m),
        ),
    )
    start_center = selected["start_center"]
    start_positions = selected["start_positions"]
    target_center = selected["center"]
    payload = {
        "schema": "mosim.factory_l2_three_uav_formation_obstacle_crossing.v1",
        "status": "static_scenario_ready_runtime_pending",
        "world": "Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/worlds/factoryenvironmentcollect_l2_static_review_clean.sdf",
        "formation": {
            "type": "three_uav_equilateral_subset_of_normal_hexagon",
            "scale": args.scale,
            "expected_min_pair_distance_m": 2.0 * args.scale,
            "start_center_xy_m": list(start_center),
            "preferred_single_uav_center_xy_m": list(preferred_center),
            "runtime_proven_start_center_xy_m": list(runtime_proven_center),
            "start_center_shift_from_preferred_m": math.dist(start_center, preferred_center),
            "start_positions_xy_m": start_positions,
            "target_center_xy_m": list(target_center),
            "target_positions_xy_m": selected["positions"],
            "z_m": args.z_m,
        },
        "obstacle_crossing_contract": {
            "direct_center_segment_blocked": True,
            "clearance_margin_m": args.clearance_margin_m,
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
