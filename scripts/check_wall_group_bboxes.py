#!/usr/bin/env python3
"""Check fixed wall groups as merged 3D bounding boxes.

The open-blocks map encodes each standard L wall as two consecutive box
obstacles. This checker treats each pair as one obstacle volume, which matches
manual visual review better than checking individual wall arms.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAP = ROOT / "planners/astar_min_snap/map_open_blocks.yaml"


def bounds_distance(a: list[float], b: list[float]) -> float:
    dx = max(0.0, max(a[0], b[0]) - min(a[3], b[3]))
    dy = max(0.0, max(a[1], b[1]) - min(a[4], b[4]))
    dz = max(0.0, max(a[2], b[2]) - min(a[5], b[5]))
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def point_distance_to_box(point: list[float], box: list[float]) -> float:
    dx = max(box[0] - point[0], 0.0, point[0] - box[3])
    dy = max(box[1] - point[1], 0.0, point[1] - box[4])
    dz = max(box[2] - point[2], 0.0, point[2] - box[5])
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def box_from_obstacle(obstacle: dict[str, Any]) -> list[float]:
    lo = obstacle["min"]
    hi = obstacle["max"]
    return [
        min(float(lo[0]), float(hi[0])),
        min(float(lo[1]), float(hi[1])),
        min(float(lo[2]), float(hi[2])),
        max(float(lo[0]), float(hi[0])),
        max(float(lo[1]), float(hi[1])),
        max(float(lo[2]), float(hi[2])),
    ]


def merge_boxes(boxes: list[list[float]]) -> list[float]:
    return [
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        min(box[2] for box in boxes),
        max(box[3] for box in boxes),
        max(box[4] for box in boxes),
        max(box[5] for box in boxes),
    ]


def wall_centerline(box: list[float]) -> dict[str, Any]:
    x0, y0, z0, x1, y1, z1 = box
    cx = 0.5 * (x0 + x1)
    cy = 0.5 * (y0 + y1)
    sx = x1 - x0
    sy = y1 - y0
    if sx >= sy:
        return {
            "axis": "x",
            "center": [cx, cy],
            "endpoints": [[x0, cy], [x1, cy]],
            "length": sx,
            "thickness": sy,
            "height": z1 - z0,
        }
    return {
        "axis": "y",
        "center": [cx, cy],
        "endpoints": [[cx, y0], [cx, y1]],
        "length": sy,
        "thickness": sx,
        "height": z1 - z0,
    }


def point_distance_xy(a: list[float], b: list[float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def wall_group_centerline_connection(
    long_box: list[float],
    short_box: list[float],
) -> dict[str, Any]:
    long_line = wall_centerline(long_box)
    short_line = wall_centerline(short_box)
    candidates: list[tuple[str, float, list[float], list[float]]] = []
    for endpoint_index, long_endpoint in enumerate(long_line["endpoints"], start=1):
        for short_endpoint_index, short_endpoint in enumerate(short_line["endpoints"], start=1):
            candidates.append(
                (
                    f"long_endpoint_{endpoint_index}_to_short_endpoint_{short_endpoint_index}",
                    point_distance_xy(long_endpoint, short_endpoint),
                    long_endpoint,
                    short_endpoint,
                )
            )
        candidates.append(
            (
                f"long_endpoint_{endpoint_index}_to_short_center",
                point_distance_xy(long_endpoint, short_line["center"]),
                long_endpoint,
                short_line["center"],
            )
        )
    mode, distance, long_point, short_point = min(candidates, key=lambda item: item[1])
    return {
        "mode": mode,
        "distance": distance,
        "long_line": long_line,
        "short_line": short_line,
        "long_point": long_point,
        "short_point": short_point,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--map", type=Path, default=DEFAULT_MAP)
    parser.add_argument("--wall-box-count", type=int, default=10)
    parser.add_argument("--boxes-per-group", type=int, default=2)
    parser.add_argument("--min-group-distance-m", type=float, default=1.5)
    parser.add_argument("--min-start-goal-distance-m", type=float, default=3.0)
    parser.add_argument("--centerline-connect-tol-m", type=float, default=1e-3)
    args = parser.parse_args()

    config = yaml.safe_load(args.map.read_text(encoding="utf-8"))
    map_config = config["map"]
    map_bounds = map_config["bounds"]
    world = [
        float(map_bounds["x"][0]),
        float(map_bounds["y"][0]),
        float(map_bounds["z"][0]),
        float(map_bounds["x"][1]),
        float(map_bounds["y"][1]),
        float(map_bounds["z"][1]),
    ]
    fixed = map_config["obstacles"][: args.wall_box_count]
    if len(fixed) % args.boxes_per_group != 0:
        raise SystemExit("fixed wall count must be divisible by boxes_per_group")

    groups: list[list[float]] = []
    group_parts: list[list[list[float]]] = []
    for index in range(0, len(fixed), args.boxes_per_group):
        parts = [box_from_obstacle(item) for item in fixed[index:index + args.boxes_per_group]]
        group_parts.append(parts)
        groups.append(merge_boxes(parts))

    ok = True
    print(f"map: {args.map}")
    print(f"world_bbox: {world}")
    start = [float(value) for value in map_config["start"]]
    goal = [float(value) for value in map_config["goal"]]
    for i, box in enumerate(groups, start=1):
        parts = group_parts[i - 1]
        lines = [wall_centerline(part) for part in parts]
        long_index = 0 if lines[0]["length"] >= lines[1]["length"] else 1
        short_index = 1 - long_index
        connection = wall_group_centerline_connection(parts[long_index], parts[short_index])
        out_of_bounds = (
            box[0] < world[0] or box[1] < world[1] or box[2] < world[2]
            or box[3] > world[3] or box[4] > world[4] or box[5] > world[5]
        )
        start_distance = point_distance_to_box(start, box)
        goal_distance = point_distance_to_box(goal, box)
        print(
            f"group {i}: bbox={box} "
            f"start_distance_m={start_distance:.3f} goal_distance_m={goal_distance:.3f} "
            f"out_of_bounds={out_of_bounds} "
            f"centerline_connection={connection['mode']} "
            f"centerline_error_m={connection['distance']:.6f}"
        )
        if out_of_bounds:
            ok = False
        if start_distance < args.min_start_goal_distance_m or goal_distance < args.min_start_goal_distance_m:
            ok = False
        if connection["distance"] > args.centerline_connect_tol_m:
            ok = False

    print("group distances:")
    for i, box_a in enumerate(groups):
        for j, box_b in enumerate(groups[i + 1:], start=i + 1):
            distance = bounds_distance(box_a, box_b)
            print(f"group {i + 1} - group {j + 1}: distance_m={distance:.3f}")
            if distance < args.min_group_distance_m:
                ok = False

    if not ok:
        print("wall group bbox check: FAIL")
        return 1
    print("wall group bbox check: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
