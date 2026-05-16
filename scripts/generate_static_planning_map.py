#!/usr/bin/env python3
"""Generate static planning-map assets for GUI/background review.

The generated 3D mesh and preview image are visualization assets only. They
must not be used as global knowledge by the online planner; the planner keeps
using local discovered obstacles from the scenario configuration.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import struct
import zlib
from pathlib import Path
from typing import Any

from plan_astar_min_snap import expand_wall_groups, read_yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "planners/astar_min_snap/map_open_blocks.yaml"
DEFAULT_OUTPUT_DIR = ROOT / "results/planning/single_obstacle_astar_awff/figures/static_map"
DEFAULT_STL = ROOT / "QuadrotorModel/Resources/Visualization/map_open_blocks_static_ground_0p5_obstacles_0p4_0p64.stl"


def crc_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)


def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + chunk_type + data + crc_chunk(chunk_type, data)


def write_png(path: Path, width: int, height: int, pixels: bytearray) -> None:
    """Write an RGB PNG with no external image dependency."""
    if len(pixels) != width * height * 3:
        raise ValueError("RGB pixel buffer size mismatch")
    scanlines = bytearray()
    row_bytes = width * 3
    for y in range(height):
        scanlines.append(0)
        start = y * row_bytes
        scanlines.extend(pixels[start : start + row_bytes])

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(bytes(scanlines), level=6))
        + png_chunk(b"IEND", b"")
    )


def terrain_height(ix: int, iy: int) -> float:
    return 0.08 + 0.16 * (0.5 + 0.5 * math.sin(0.73 * ix + 1.19 * iy))


def map_to_pixel(x: float, y: float, bounds: dict[str, Any], px_per_m: float, height_px: int) -> tuple[int, int]:
    x_min, _ = [float(v) for v in bounds["x"]]
    y_min, _ = [float(v) for v in bounds["y"]]
    px = int(round((x - x_min) * px_per_m))
    py = height_px - 1 - int(round((y - y_min) * px_per_m))
    return px, py


def fill_rect(
    pixels: bytearray,
    width_px: int,
    height_px: int,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: tuple[int, int, int],
) -> None:
    x0 = max(0, min(width_px - 1, x0))
    x1 = max(0, min(width_px - 1, x1))
    y0 = max(0, min(height_px - 1, y0))
    y1 = max(0, min(height_px - 1, y1))
    if x1 < x0:
        x0, x1 = x1, x0
    if y1 < y0:
        y0, y1 = y1, y0
    r, g, b = color
    for py in range(y0, y1 + 1):
        base = py * width_px * 3
        for px in range(x0, x1 + 1):
            idx = base + px * 3
            pixels[idx] = r
            pixels[idx + 1] = g
            pixels[idx + 2] = b


def draw_ground(
    pixels: bytearray,
    width_px: int,
    height_px: int,
    bounds: dict[str, Any],
    *,
    px_per_m: float,
    cell_m: float,
) -> None:
    x_min, x_max = [float(v) for v in bounds["x"]]
    y_min, y_max = [float(v) for v in bounds["y"]]
    nx = int(math.ceil((x_max - x_min) / cell_m))
    ny = int(math.ceil((y_max - y_min) / cell_m))
    for ix in range(nx):
        for iy in range(ny):
            x0 = x_min + ix * cell_m
            y0 = y_min + iy * cell_m
            x1 = min(x0 + cell_m, x_max)
            y1 = min(y0 + cell_m, y_max)
            shade = int(231 + 14 * (0.5 + 0.5 * math.sin(0.73 * ix + 1.19 * iy)))
            if (ix + iy) % 2 == 0:
                shade = min(250, shade + 3)
            px0, py1 = map_to_pixel(x0, y0, bounds, px_per_m, height_px)
            px1, py0 = map_to_pixel(x1, y1, bounds, px_per_m, height_px)
            fill_rect(pixels, width_px, height_px, px0, py0, px1, py1, (shade, shade, shade))


def draw_random_obstacles(
    pixels: bytearray,
    width_px: int,
    height_px: int,
    bounds: dict[str, Any],
    obstacles: list[dict[str, Any]],
    *,
    px_per_m: float,
    default_footprint_m: float,
) -> int:
    count = 0
    for obstacle in obstacles:
        if obstacle.get("type") != "cylinder":
            continue
        center = obstacle["center"]
        footprint_m = float(obstacle.get("visual_size_m", default_footprint_m))
        half = max(1, int(round(0.5 * footprint_m * px_per_m)))
        px, py = map_to_pixel(float(center[0]), float(center[1]), bounds, px_per_m, height_px)
        fill_rect(pixels, width_px, height_px, px - half, py - half, px + half, py + half, (92, 92, 92))
        count += 1
    return count


def triangle_normal(a: tuple[float, float, float], b: tuple[float, float, float], c: tuple[float, float, float]) -> tuple[float, float, float]:
    ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length <= 1e-12:
        return (0.0, 0.0, 1.0)
    return (nx / length, ny / length, nz / length)


def add_triangle(
    triangles: list[tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]],
    a: tuple[float, float, float],
    b: tuple[float, float, float],
    c: tuple[float, float, float],
) -> None:
    triangles.append((triangle_normal(a, b, c), a, b, c))


def add_box(
    triangles: list[tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]],
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    z0: float,
    z1: float,
) -> None:
    p000 = (x0, y0, z0)
    p100 = (x1, y0, z0)
    p110 = (x1, y1, z0)
    p010 = (x0, y1, z0)
    p001 = (x0, y0, z1)
    p101 = (x1, y0, z1)
    p111 = (x1, y1, z1)
    p011 = (x0, y1, z1)
    # bottom/top
    add_triangle(triangles, p000, p010, p110)
    add_triangle(triangles, p000, p110, p100)
    add_triangle(triangles, p001, p101, p111)
    add_triangle(triangles, p001, p111, p011)
    # sides
    add_triangle(triangles, p000, p100, p101)
    add_triangle(triangles, p000, p101, p001)
    add_triangle(triangles, p100, p110, p111)
    add_triangle(triangles, p100, p111, p101)
    add_triangle(triangles, p110, p010, p011)
    add_triangle(triangles, p110, p011, p111)
    add_triangle(triangles, p010, p000, p001)
    add_triangle(triangles, p010, p001, p011)


def write_binary_stl(
    path: Path,
    triangles: list[tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header = b"Quadrotor static map: ground 0.5m, obstacle footprint 0.4-0.64m".ljust(80, b" ")
    data = bytearray(header)
    data.extend(struct.pack("<I", len(triangles)))
    for normal, a, b, c in triangles:
        data.extend(struct.pack("<12fH", *normal, *a, *b, *c, 0))
    path.write_bytes(bytes(data))


def build_static_mesh(
    bounds: dict[str, Any],
    obstacles: list[dict[str, Any]],
    *,
    ground_cell_m: float,
    default_obstacle_footprint_m: float,
) -> tuple[list[tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]], int, int]:
    x_min, x_max = [float(v) for v in bounds["x"]]
    y_min, y_max = [float(v) for v in bounds["y"]]
    nx = int(math.ceil((x_max - x_min) / ground_cell_m))
    ny = int(math.ceil((y_max - y_min) / ground_cell_m))
    triangles: list[tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]] = []

    for ix in range(nx):
        for iy in range(ny):
            x0 = x_min + ix * ground_cell_m
            x1 = min(x0 + ground_cell_m, x_max)
            y0 = y_min + iy * ground_cell_m
            y1 = min(y0 + ground_cell_m, y_max)
            z1 = terrain_height(ix, iy)
            add_box(triangles, x0, x1, y0, y1, 0.0, z1)

    random_count = 0
    for obstacle in obstacles:
        if obstacle.get("type") != "cylinder":
            continue
        x, y, _ = [float(v) for v in obstacle["center"]]
        height = float(obstacle.get("height", 3.0))
        z_min = float(obstacle.get("z_min", 0.0))
        footprint_m = float(obstacle.get("visual_size_m", default_obstacle_footprint_m))
        half = 0.5 * footprint_m
        add_box(triangles, x - half, x + half, y - half, y + half, z_min, z_min + height)
        random_count += 1
    return triangles, random_count, nx * ny


def draw_markers(
    pixels: bytearray,
    width_px: int,
    height_px: int,
    bounds: dict[str, Any],
    *,
    px_per_m: float,
    start: list[float],
    goal: list[float],
) -> None:
    for point, color in ((start, (45, 155, 80)), (goal, (220, 70, 55))):
        px, py = map_to_pixel(float(point[0]), float(point[1]), bounds, px_per_m, height_px)
        fill_rect(pixels, width_px, height_px, px - 7, py - 7, px + 7, py + 7, color)


def choose_stratified_grid(count: int, map_width: float, map_height: float) -> tuple[int, int]:
    target_ratio = map_width / map_height
    best = (count, 1)
    best_score = float("inf")
    for gx in range(1, count + 1):
        if count % gx != 0:
            continue
        gy = count // gx
        ratio = gx / gy
        score = abs(ratio - target_ratio)
        if score < best_score:
            best = (gx, gy)
            best_score = score
    return best


def generate_uniform_static_obstacles(
    map_config: dict[str, Any],
    footprint_min_m: float,
    footprint_max_m: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    random_spec = map_config.get("random_obstacles", {})
    if not isinstance(random_spec, dict):
        random_spec = {}
    bounds = map_config["bounds"]
    x_min, x_max = [float(v) for v in bounds["x"]]
    y_min, y_max = [float(v) for v in bounds["y"]]
    z_min = float(bounds.get("z", [0.0, 3.0])[0])
    count = int(random_spec.get("count", 600))
    seed = int(random_spec.get("seed", 20260518))
    edge_margin = float(random_spec.get("edge_margin_m", 2.0))
    height = 3.0

    rng = random.Random(seed)
    usable_x0 = x_min + edge_margin
    usable_x1 = x_max - edge_margin
    usable_y0 = y_min + edge_margin
    usable_y1 = y_max - edge_margin
    grid_x, grid_y = choose_stratified_grid(count, usable_x1 - usable_x0, usable_y1 - usable_y0)
    cell_w = (usable_x1 - usable_x0) / grid_x
    cell_h = (usable_y1 - usable_y0) / grid_y
    jitter_x = max(0.0, min(0.45, 0.20 * cell_w, 0.5 * (cell_w - footprint_max_m) - 0.05))
    jitter_y = max(0.0, min(0.45, 0.20 * cell_h, 0.5 * (cell_h - footprint_max_m) - 0.05))

    obstacles: list[dict[str, Any]] = []
    for iy in range(grid_y):
        for ix in range(grid_x):
            if len(obstacles) >= count:
                break
            footprint_m = rng.uniform(footprint_min_m, footprint_max_m)
            cx = usable_x0 + (ix + 0.5) * cell_w + rng.uniform(-jitter_x, jitter_x)
            cy = usable_y0 + (iy + 0.5) * cell_h + rng.uniform(-jitter_y, jitter_y)
            obstacles.append(
                {
                    "type": "cylinder",
                    "center": [round(cx, 3), round(cy, 3), 1.0],
                    "radius": round(0.5 * footprint_m, 3),
                    "visual_size_m": round(footprint_m, 3),
                    "height": height,
                    "z_min": z_min,
                    "z_max": z_min + height,
                }
            )
    diagnostics = {
        "grid_cells": [grid_x, grid_y],
        "cell_size_m": [cell_w, cell_h],
        "jitter_limit_m": [jitter_x, jitter_y],
        "obstacles_per_cell": 1,
    }
    return obstacles, diagnostics


def generate(
    config_path: Path,
    output_dir: Path,
    stl_path: Path,
    px_per_m: float,
    ground_cell_m: float,
    obstacle_footprint_min_m: float,
    obstacle_footprint_max_m: float,
) -> dict[str, Any]:
    raw_config = read_yaml(config_path)
    expanded_walls = expand_wall_groups(raw_config)
    map_config = expanded_walls["map"]
    bounds = map_config["bounds"]
    x_min, x_max = [float(v) for v in bounds["x"]]
    y_min, y_max = [float(v) for v in bounds["y"]]
    width_px = int(round((x_max - x_min) * px_per_m))
    height_px = int(round((y_max - y_min) * px_per_m))
    pixels = bytearray([255] * width_px * height_px * 3)

    static_obstacles, distribution_diagnostics = generate_uniform_static_obstacles(
        map_config,
        obstacle_footprint_min_m,
        obstacle_footprint_max_m,
    )
    draw_ground(pixels, width_px, height_px, bounds, px_per_m=px_per_m, cell_m=ground_cell_m)
    obstacle_count = draw_random_obstacles(
        pixels,
        width_px,
        height_px,
        bounds,
        static_obstacles,
        px_per_m=px_per_m,
        default_footprint_m=obstacle_footprint_max_m,
    )
    draw_markers(
        pixels,
        width_px,
        height_px,
        bounds,
        px_per_m=px_per_m,
        start=map_config["start"],
        goal=map_config["goal"],
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / "map_open_blocks_static_ground_0p5_obstacles_0p4_0p64.png"
    manifest_path = output_dir / "map_open_blocks_static_ground_0p5_obstacles_0p4_0p64_manifest.json"
    write_png(image_path, width_px, height_px, pixels)
    triangles, mesh_obstacle_count, ground_cell_count = build_static_mesh(
        bounds,
        static_obstacles,
        ground_cell_m=ground_cell_m,
        default_obstacle_footprint_m=obstacle_footprint_max_m,
    )
    write_binary_stl(stl_path, triangles)

    wall_boxes = [item for item in map_config.get("obstacles", []) if item.get("type") == "box"]
    manifest = {
        "source_config": str(config_path.relative_to(ROOT)),
        "image": str(image_path.relative_to(ROOT)),
        "stl": str(stl_path.relative_to(ROOT)),
        "purpose": "static_environment_visualization_only",
        "planner_knowledge_policy": "online_planner_must_use_local_discovered_map_not_this_full_static_image",
        "bounds_m": bounds,
        "image_size_px": [width_px, height_px],
        "pixels_per_meter": px_per_m,
        "ground_cell_size_m": ground_cell_m,
        "ground_cell_count": ground_cell_count,
        "random_obstacle_visual_footprint_range_m": [obstacle_footprint_min_m, obstacle_footprint_max_m, 3.0],
        "random_obstacle_count": obstacle_count,
        "random_obstacle_distribution": "stratified_uniform_one_per_cell_no_wall_reservation",
        "random_obstacle_distribution_diagnostics": distribution_diagnostics,
        "mesh_random_obstacle_count": mesh_obstacle_count,
        "mesh_triangle_count": len(triangles),
        "dynamic_wall_group_count": len(wall_boxes) // 2,
        "dynamic_wall_box_count": len(wall_boxes),
        "walls_baked_into_static_image": False,
        "walls_baked_into_static_mesh": False,
        "start": map_config["start"],
        "goal": map_config["goal"],
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--stl", type=Path, default=DEFAULT_STL)
    parser.add_argument("--pixels-per-meter", type=float, default=20.0)
    parser.add_argument("--ground-cell-m", type=float, default=0.5)
    parser.add_argument("--obstacle-footprint-min-m", type=float, default=0.4)
    parser.add_argument("--obstacle-footprint-max-m", type=float, default=0.64)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = generate(
        args.config,
        args.output_dir,
        args.stl,
        args.pixels_per_meter,
        args.ground_cell_m,
        args.obstacle_footprint_min_m,
        args.obstacle_footprint_max_m,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
