#!/usr/bin/env python3
"""Create the S1 competition industrial hybrid blockout render map.

This is a project-owned Unreal preview map for manual renderer review. It is
not final art and it does not feed planner truth back into MWORKS.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "unreal/MworksUnrealRenderer/Content/MworksData/map_competition_industrial_hybrid_render_map.json"


def rounded(value: float, digits: int = 4) -> float:
    return round(float(value), digits)


def box_record(
    box_id: str,
    semantic: str,
    center: tuple[float, float, float],
    extent: tuple[float, float, float],
    *,
    source_note: str = "project_owned_s1_blockout",
) -> dict[str, Any]:
    cx, cy, cz = center
    sx, sy, sz = extent
    return {
        "id": box_id,
        "semantic": semantic,
        "center_m": [rounded(cx), rounded(cy), rounded(cz)],
        "extent_m": [rounded(sx), rounded(sy), rounded(sz)],
        "min_m": [rounded(cx - 0.5 * sx), rounded(cy - 0.5 * sy), rounded(cz - 0.5 * sz)],
        "max_m": [rounded(cx + 0.5 * sx), rounded(cy + 0.5 * sy), rounded(cz + 0.5 * sz)],
        "source": {
            "source_note": source_note,
            "collision_proxy_id": f"proxy_{box_id}",
        },
    }


def terrain_grid() -> dict[str, Any]:
    x_min, x_max = -22.0, 22.0
    y_min, y_max = -14.0, 14.0
    cell = 2.0
    nx = int(round((x_max - x_min) / cell)) + 1
    ny = int(round((y_max - y_min) / cell)) + 1
    heights: list[list[float]] = []
    for iy in range(ny):
        y = y_min + iy * cell
        row = []
        for ix in range(nx):
            x = x_min + ix * cell
            # Lightly uneven concrete/factory floor: visible but cheap to render.
            h = 0.08 + 0.035 * ((ix + 2 * iy) % 4) + 0.015 * ((abs(x) + abs(y)) % 3)
            row.append(rounded(h, 3))
        heights.append(row)
    return {
        "origin_m": [x_min, y_min, 0.0],
        "cell_m": cell,
        "count": [nx, ny],
        "height_m": heights,
        "height_policy": "deterministic low-detail S1 blockout floor; final art replaces this",
    }


def build_map() -> dict[str, Any]:
    random_columns = [
        box_record("s1_pillar_01", "pillar", (-13.0, -5.0, 1.75), (0.5, 0.5, 3.5)),
        box_record("s1_pillar_02", "pillar", (-9.5, 6.5, 1.75), (0.5, 0.5, 3.5)),
        box_record("s1_pillar_03", "pillar", (-3.5, -8.0, 1.75), (0.5, 0.5, 3.5)),
        box_record("s1_pillar_04", "pillar", (2.5, 7.0, 1.75), (0.5, 0.5, 3.5)),
        box_record("s1_pillar_05", "pillar", (8.5, -3.0, 1.75), (0.5, 0.5, 3.5)),
        box_record("s1_pillar_06", "pillar", (14.0, 5.0, 1.75), (0.5, 0.5, 3.5)),
        box_record("s1_crate_01", "box_obstacle", (-6.5, 1.0, 0.6), (1.2, 1.2, 1.2)),
        box_record("s1_crate_02", "box_obstacle", (6.5, -7.0, 0.75), (1.6, 1.0, 1.5)),
        box_record("s1_crate_03", "box_obstacle", (12.0, -9.0, 0.5), (1.0, 1.4, 1.0)),
        box_record("s1_inspection_target_01", "inspection_target", (-1.5, 10.0, 1.0), (1.0, 0.3, 2.0)),
        box_record("s1_inspection_target_02", "inspection_target", (16.0, -1.5, 1.0), (1.0, 0.3, 2.0)),
    ]
    wall_boxes = [
        box_record("s1_wall_l_left_long", "wall", (-14.0, 0.0, 1.75), (0.35, 10.0, 3.5)),
        box_record("s1_wall_l_left_short", "wall", (-10.5, -5.0, 1.75), (7.0, 0.35, 3.5)),
        box_record("s1_wall_t_mid_long", "wall", (1.0, 0.0, 1.75), (10.0, 0.35, 3.5)),
        box_record("s1_wall_t_mid_short", "wall", (-4.0, 3.0, 1.75), (0.35, 6.0, 3.5)),
        box_record("s1_wall_l_right_long", "wall", (12.0, 1.0, 1.75), (0.35, 9.0, 3.5)),
        box_record("s1_wall_l_right_short", "wall", (15.5, 5.5, 1.75), (7.0, 0.35, 3.5)),
        box_record("s1_gate_left_post", "gate", (4.0, -10.0, 1.75), (0.35, 0.35, 3.5)),
        box_record("s1_gate_right_post", "gate", (7.0, -10.0, 1.75), (0.35, 0.35, 3.5)),
        box_record("s1_gate_top_beam", "gate", (5.5, -10.0, 3.35), (3.35, 0.35, 0.3)),
        box_record("s1_takeoff_pad", "marker", (-18.0, -10.0, 0.04), (2.0, 2.0, 0.08)),
        box_record("s1_landing_pad", "marker", (18.0, 10.0, 0.04), (2.0, 2.0, 0.08)),
    ]
    return {
        "schema": "quadrotor.unreal_render_map.v1",
        "source_config": "scripts/create_competition_industrial_hybrid_render_map.py",
        "render_only": True,
        "truth_policy": "S1 blockout visualizes collision-proxy-equivalent geometry but does not feed global truth into MWORKS planning or metrics",
        "units": {"position": "m", "angle": "rad"},
        "bounds_m": {"x": [-22.0, 22.0], "y": [-14.0, 14.0], "z": [0.0, 3.8]},
        "start_m": [-18.0, -10.0, 1.0],
        "goal_m": [18.0, 10.0, 1.0],
        "terrain": terrain_grid(),
        "obstacles": {
            "random_columns": random_columns,
            "wall_boxes": wall_boxes,
            "random_cluster_count": 8,
            "random_column_count": len(random_columns),
            "wall_box_count": len(wall_boxes),
        },
        "materials": {
            "terrain_low": {"color": [0.55, 0.58, 0.56]},
            "terrain_high": {"color": [0.70, 0.72, 0.70]},
            "random_column": {"color": [0.55, 0.58, 0.62]},
            "wall": {"color": [0.74, 0.73, 0.69]},
            "radar_near": {"color": [0.10, 0.65, 1.00], "alpha": 0.32},
            "radar_far": {"color": [0.82, 0.88, 0.92], "alpha": 0.22},
        },
    }


def main() -> int:
    payload = build_map()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    obstacles = payload["obstacles"]
    terrain = payload["terrain"]
    print(
        f"Wrote {OUTPUT.relative_to(ROOT)}: terrain={terrain['count'][0]}x{terrain['count'][1]} "
        f"random_columns={obstacles['random_column_count']} wall_boxes={obstacles['wall_box_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
