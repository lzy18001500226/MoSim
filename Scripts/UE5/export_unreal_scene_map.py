#!/usr/bin/env python3
"""Export the planning map truth into a compact Unreal-renderer JSON asset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from generate_static_planning_map import terrain_height_xy
from plan_astar_min_snap import expand_random_obstacles, expand_wall_groups, read_yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "Config/planners/astar_min_snap/map_open_blocks.yaml"
DEFAULT_OUTPUT = ROOT / "UE5/MworksUnrealRenderer/Content/MworksData/map_open_blocks_render_map.json"


def rounded(value: float, digits: int = 4) -> float:
    return round(float(value), digits)


def box_record(obstacle: dict[str, Any], *, semantic: str, index: int) -> dict[str, Any]:
    lo = [float(v) for v in obstacle["min"]]
    hi = [float(v) for v in obstacle["max"]]
    return {
        "id": obstacle.get("wall_group_id") or f"{semantic}_{index:05d}",
        "semantic": semantic,
        "center_m": [rounded(0.5 * (lo[0] + hi[0])), rounded(0.5 * (lo[1] + hi[1])), rounded(0.5 * (lo[2] + hi[2]))],
        "extent_m": [rounded(hi[0] - lo[0]), rounded(hi[1] - lo[1]), rounded(hi[2] - lo[2])],
        "min_m": [rounded(v) for v in lo],
        "max_m": [rounded(v) for v in hi],
        "source": {
            "wall_group_id": obstacle.get("wall_group_id", ""),
            "wall_arm": obstacle.get("wall_arm", ""),
            "random_cluster_id": obstacle.get("random_cluster_id", 0),
        },
    }


def build_terrain_grid(bounds: dict[str, Any], cell_m: float) -> dict[str, Any]:
    x_min, x_max = [float(v) for v in bounds["x"]]
    y_min, y_max = [float(v) for v in bounds["y"]]
    nx = int(round((x_max - x_min) / cell_m)) + 1
    ny = int(round((y_max - y_min) / cell_m)) + 1
    heights: list[list[float]] = []
    for iy in range(ny):
        y = y_min + iy * cell_m
        row = []
        for ix in range(nx):
            x = x_min + ix * cell_m
            row.append(rounded(terrain_height_xy(x, y), 3))
        heights.append(row)
    return {
        "origin_m": [rounded(x_min), rounded(y_min), 0.0],
        "cell_m": rounded(cell_m),
        "count": [nx, ny],
        "height_m": heights,
        "height_policy": "same deterministic terrain_height_xy as MWORKS static planning map",
    }


def export_map(config_path: Path, output_path: Path, terrain_cell_m: float) -> dict[str, Any]:
    config_path = config_path.resolve()
    output_path = output_path.resolve()
    raw_config = read_yaml(config_path)
    expanded_config = expand_random_obstacles(expand_wall_groups(raw_config))
    map_config = expanded_config["map"]
    bounds = map_config["bounds"]
    obstacles = map_config.get("obstacles", [])
    random_boxes = [
        obstacle for obstacle in obstacles
        if obstacle.get("type") == "box" and obstacle.get("random_cluster")
    ]
    wall_boxes = [
        obstacle for obstacle in obstacles
        if obstacle.get("type") == "box"
        and (obstacle.get("wall_group_id") or obstacle.get("semantic") == "wall")
    ]
    static_boxes = [
        obstacle for obstacle in obstacles
        if obstacle.get("type") == "box"
        and not obstacle.get("random_cluster")
        and not obstacle.get("wall_group_id")
        and obstacle.get("semantic") != "wall"
    ]
    payload = {
        "schema": "quadrotor.unreal_render_map.v1",
        "source_config": str(config_path.relative_to(ROOT)),
        "render_only": True,
        "truth_policy": "Unreal visualizes this data but never feeds it back into MWORKS planning or metrics",
        "units": {"position": "m", "angle": "rad"},
        "bounds_m": bounds,
        "start_m": map_config.get("start"),
        "goal_m": map_config.get("goal"),
        "terrain": build_terrain_grid(bounds, terrain_cell_m),
        "obstacles": {
            "random_columns": [box_record(obstacle, semantic="random_column", index=i) for i, obstacle in enumerate(random_boxes, start=1)],
            "wall_boxes": [
                box_record(obstacle, semantic=obstacle.get("semantic", "wall"), index=i)
                for i, obstacle in enumerate(wall_boxes + static_boxes, start=1)
            ],
            "random_cluster_count": len({obstacle.get("random_cluster_id") for obstacle in random_boxes}),
            "random_column_count": len(random_boxes),
            "wall_box_count": len(wall_boxes) + len(static_boxes),
        },
        "materials": {
            "terrain_low": {"color": [0.78, 0.86, 0.78]},
            "terrain_high": {"color": [0.52, 0.68, 0.48]},
            "random_column": {"color": [0.62, 0.62, 0.62]},
            "wall": {"color": [0.72, 0.72, 0.70]},
            "radar_near": {"color": [0.10, 0.65, 1.00], "alpha": 0.32},
            "radar_far": {"color": [0.82, 0.88, 0.92], "alpha": 0.22},
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--terrain-cell-m", type=float, default=1.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = export_map(args.config, args.output, args.terrain_cell_m)
    obstacles = payload["obstacles"]
    terrain = payload["terrain"]
    print(
        f"Wrote {args.output}: terrain={terrain['count'][0]}x{terrain['count'][1]} "
        f"random_columns={obstacles['random_column_count']} wall_boxes={obstacles['wall_box_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
