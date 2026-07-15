#!/usr/bin/env python3
"""Partition a Factory L2 coverage waypoint packet into per-UAV target chains."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def load_packet(path: Path) -> dict[str, Any]:
    packet = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(packet, dict):
        raise SystemExit(f"packet root must be an object: {path}")
    waypoints = packet.get("waypoints")
    if not isinstance(waypoints, list):
        raise SystemExit(f"packet has no waypoints list: {path}")
    return packet


def as_waypoints(raw: list[Any]) -> list[list[float]]:
    out: list[list[float]] = []
    for item in raw:
        if not isinstance(item, list) or len(item) < 3:
            raise SystemExit(f"invalid waypoint: {item!r}")
        out.append([float(item[0]), float(item[1]), float(item[2])])
    return out


def contiguous_partition(waypoints: list[list[float]], uav_num: int) -> list[list[list[float]]]:
    n = len(waypoints)
    parts: list[list[list[float]]] = []
    for i in range(uav_num):
        start = round(i * n / uav_num)
        stop = round((i + 1) * n / uav_num)
        parts.append(waypoints[start:stop])
    return parts


def contiguous_swap_23_partition(waypoints: list[list[float]], uav_num: int) -> list[list[list[float]]]:
    parts = contiguous_partition(waypoints, uav_num)
    if uav_num == 3:
        parts[1], parts[2] = parts[2], parts[1]
    return parts


def round_robin_partition(waypoints: list[list[float]], uav_num: int) -> list[list[list[float]]]:
    parts: list[list[list[float]]] = [[] for _ in range(uav_num)]
    for idx, waypoint in enumerate(waypoints):
        parts[idx % uav_num].append(waypoint)
    return parts


def spatial_y_bands_partition(waypoints: list[list[float]], uav_num: int) -> list[list[list[float]]]:
    """Assign waypoints to top-to-bottom Y bands while preserving route order."""
    if not waypoints:
        return [[] for _ in range(uav_num)]
    min_y = min(wp[1] for wp in waypoints)
    max_y = max(wp[1] for wp in waypoints)
    y_span = max(max_y - min_y, 1e-9)
    parts: list[list[list[float]]] = [[] for _ in range(uav_num)]
    for waypoint in waypoints:
        normalized_from_top = (max_y - waypoint[1]) / y_span
        band = min(uav_num - 1, max(0, int(normalized_from_top * uav_num)))
        parts[band].append(waypoint)
    return parts


def spatial_x_bands_partition(waypoints: list[list[float]], uav_num: int) -> list[list[list[float]]]:
    """Assign waypoints to left-to-right X bands while preserving route order."""
    if not waypoints:
        return [[] for _ in range(uav_num)]
    min_x = min(wp[0] for wp in waypoints)
    max_x = max(wp[0] for wp in waypoints)
    x_span = max(max_x - min_x, 1e-9)
    parts: list[list[list[float]]] = [[] for _ in range(uav_num)]
    for waypoint in waypoints:
        normalized_from_left = (waypoint[0] - min_x) / x_span
        band = min(uav_num - 1, max(0, int(normalized_from_left * uav_num)))
        parts[band].append(waypoint)
    return parts


def route_length(waypoints: list[list[float]]) -> float:
    total = 0.0
    for a, b in zip(waypoints, waypoints[1:]):
        total += math.dist(a[:3], b[:3])
    return total


def min_xy_distance(points: list[list[float]]) -> float | None:
    if len(points) < 2:
        return None
    return min(math.dist(a[:2], b[:2]) for i, a in enumerate(points) for b in points[i + 1 :])


def resolve_same_round_conflicts(
    parts: list[list[list[float]]],
    min_distance_m: float,
) -> dict[str, Any]:
    """Swap later same-chain waypoints forward when multiple UAVs target the same area."""
    if len(parts) < 2 or min_distance_m <= 0:
        return {
            "enabled": False,
            "min_same_round_target_distance_m": min_distance_m,
            "swap_count": 0,
            "unresolved_rounds": [],
        }
    min_len = min(len(part) for part in parts)
    swaps: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []

    for round_idx in range(min_len):
        guard = 0
        while guard < len(parts):
            guard += 1
            round_points = [part[round_idx] for part in parts]
            closest_pair: tuple[int, int] | None = None
            closest_distance = float("inf")
            for i, a in enumerate(round_points):
                for j, b in enumerate(round_points[i + 1 :], start=i + 1):
                    dist = math.dist(a[:2], b[:2])
                    if dist < closest_distance:
                        closest_distance = dist
                        closest_pair = (i, j)
            if closest_pair is None or closest_distance >= min_distance_m:
                break

            move_idx = closest_pair[1]
            other_points = [part[round_idx] for idx, part in enumerate(parts) if idx != move_idx]
            swap_idx: int | None = None
            for candidate_idx in range(round_idx + 1, len(parts[move_idx])):
                candidate = parts[move_idx][candidate_idx]
                if all(math.dist(candidate[:2], other[:2]) >= min_distance_m for other in other_points):
                    swap_idx = candidate_idx
                    break
            if swap_idx is None:
                unresolved.append(
                    {
                        "round_index": round_idx + 1,
                        "uav_id": move_idx + 1,
                        "min_xy_distance_m": closest_distance,
                        "points": round_points,
                    }
                )
                break

            parts[move_idx][round_idx], parts[move_idx][swap_idx] = (
                parts[move_idx][swap_idx],
                parts[move_idx][round_idx],
            )
            swaps.append(
                {
                    "round_index": round_idx + 1,
                    "uav_id": move_idx + 1,
                    "swap_with_round_index": swap_idx + 1,
                    "previous_min_xy_distance_m": closest_distance,
                }
            )

    return {
        "enabled": True,
        "min_same_round_target_distance_m": min_distance_m,
        "swap_count": len(swaps),
        "swaps": swaps,
        "unresolved_rounds": unresolved,
    }


def write_packet(path: Path, source: Path, source_packet: dict[str, Any], uav_id: int, waypoints: list[list[float]]) -> None:
    packet = {
        "schema": "mosim.factory_l2_swarm_partitioned_waypoints.v1",
        "source_packet": str(source),
        "uav_id": uav_id,
        "boundary": source_packet.get("boundary"),
        "planned_coverage_proxy": source_packet.get("planned_coverage_proxy"),
        "waypoint_count": len(waypoints),
        "first_waypoint": waypoints[0] if waypoints else None,
        "last_waypoint": waypoints[-1] if waypoints else None,
        "route_length_m": route_length(waypoints),
        "waypoints": waypoints,
        "claim_boundary": (
            "Per-UAV known-scene target chain split from a source-truth clearance route; "
            "not autonomous task allocation."
        ),
    }
    path.write_text(json.dumps(packet, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--uav-num", type=int, default=3, choices=[1, 2, 3])
    parser.add_argument(
        "--policy",
        choices=["contiguous", "contiguous_swap_23", "round_robin", "spatial_y_bands", "spatial_x_bands"],
        default="contiguous",
    )
    parser.add_argument("--max-goals-per-uav", type=int, default=0)
    parser.add_argument(
        "--partition-window-goals-per-uav",
        type=int,
        default=0,
        help=(
            "Optional pre-partition route window size per UAV. Use this when "
            "the partition should match a longer batch, while the emitted "
            "per-UAV chains are trimmed by --max-goals-per-uav after partition."
        ),
    )
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--min-same-round-target-distance-m", type=float, default=4.0)
    parser.add_argument("--prefix", default="factory_l2_swarm")
    args = parser.parse_args()

    input_json = Path(args.input_json)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    packet = load_packet(input_json)
    waypoints = as_waypoints(packet["waypoints"])
    if args.start_index < 0:
        raise SystemExit(f"start-index must be non-negative: {args.start_index}")
    if args.start_index:
        waypoints = waypoints[args.start_index :]
    trim_after_partition = args.policy in {"spatial_y_bands", "spatial_x_bands"}
    if args.partition_window_goals_per_uav > 0:
        waypoints = waypoints[: args.partition_window_goals_per_uav * args.uav_num]
        trim_after_partition = True
    elif args.max_goals_per_uav > 0 and not trim_after_partition:
        waypoints = waypoints[: args.max_goals_per_uav * args.uav_num]
    if len(waypoints) < args.uav_num:
        raise SystemExit(f"not enough waypoints for {args.uav_num} UAVs: {len(waypoints)}")

    if args.policy == "round_robin":
        parts = round_robin_partition(waypoints, args.uav_num)
    elif args.policy == "contiguous_swap_23":
        parts = contiguous_swap_23_partition(waypoints, args.uav_num)
    elif args.policy == "spatial_y_bands":
        parts = spatial_y_bands_partition(waypoints, args.uav_num)
    elif args.policy == "spatial_x_bands":
        parts = spatial_x_bands_partition(waypoints, args.uav_num)
    else:
        parts = contiguous_partition(waypoints, args.uav_num)
    if args.max_goals_per_uav > 0 and trim_after_partition:
        parts = [part[: args.max_goals_per_uav] for part in parts]
    conflict_resolution = resolve_same_round_conflicts(parts, args.min_same_round_target_distance_m)

    outputs: list[str] = []
    summary_parts = []
    for idx, part in enumerate(parts, start=1):
        path = output_dir / f"{args.prefix}_uav{idx}_waypoints.json"
        write_packet(path, input_json, packet, idx, part)
        outputs.append(str(path))
        summary_parts.append(
            {
                "uav_id": idx,
                "waypoint_count": len(part),
                "first_waypoint": part[0] if part else None,
                "last_waypoint": part[-1] if part else None,
                "route_length_m": route_length(part),
            }
        )

    summary = {
        "schema": "mosim.factory_l2_swarm_waypoint_partition.v1",
        "source_packet": str(input_json),
        "policy": args.policy,
        "uav_num": args.uav_num,
        "source_waypoint_count": len(packet["waypoints"]),
        "start_index": args.start_index,
        "partition_window_goals_per_uav": args.partition_window_goals_per_uav,
        "max_goals_per_uav": args.max_goals_per_uav,
        "partitioned_waypoint_count": sum(len(part) for part in parts),
        "outputs": outputs,
        "parts": summary_parts,
        "same_round_conflict_resolution": conflict_resolution,
        "claim_boundary": (
            "Known-scene Factory L2 support-route partition for multi-UAV coverage. "
            "It does not prove unknown exploration or task allocation by itself."
        ),
    }
    summary_path = output_dir / f"{args.prefix}_partition_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
