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

from plan_astar_min_snap import expand_random_obstacles, expand_wall_groups, read_yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ROOT / "Config/planners/astar_min_snap/map_open_blocks.yaml"
DEFAULT_OUTPUT_DIR = ROOT / "Results/planning/single_obstacle_astar_awff/figures/static_map"
DEFAULT_STL = ROOT / "Results/planning/single_obstacle_astar_awff/figures/static_map/map_open_blocks_static_ground_0p2_obstacle_columns_0p2_h2p8_3p5_combined_review_only.stl"
DEFAULT_ASSET_DIR = ROOT / "References/MWORKS/QuadrotorModel/Resources/Visualization"
TERRAIN_BAND_COUNT = 5
TERRAIN_BAND_STLS = [
    DEFAULT_ASSET_DIR / f"map_open_blocks_static_terrain_band_{index}_ground_0p2.stl"
    for index in range(1, TERRAIN_BAND_COUNT + 1)
]
OBSTACLE_STL = DEFAULT_ASSET_DIR / "map_open_blocks_static_obstacle_columns_0p2_h2p8_3p5.stl"
GRID_STL = DEFAULT_ASSET_DIR / "map_open_blocks_static_terrain_grid_2m_patch0p2.stl"


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


TERRAIN_HEIGHT_MIN_M = 0.10
TERRAIN_HEIGHT_MAX_M = 1.50
TERRAIN_HEIGHT_SPAN_M = TERRAIN_HEIGHT_MAX_M - TERRAIN_HEIGHT_MIN_M
TERRAIN_VIS_CELL_M = 0.20
TERRAIN_STEP_M = 0.01


def terrain_height_xy(x: float, y: float) -> float:
    """Deterministic stepped height field in the configured terrain range."""
    ix = math.floor((x + 45.0) / TERRAIN_VIS_CELL_M)
    iy = math.floor((y + 30.0) / TERRAIN_VIS_CELL_M)
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
    smooth_height = TERRAIN_HEIGHT_MIN_M + TERRAIN_HEIGHT_SPAN_M * normalized
    stepped_height = round(smooth_height / TERRAIN_STEP_M) * TERRAIN_STEP_M
    return max(TERRAIN_HEIGHT_MIN_M, min(TERRAIN_HEIGHT_MAX_M, stepped_height))


def terrain_height(ix: int, iy: int, cell_m: float = 0.2, x_min: float = -45.0, y_min: float = -30.0) -> float:
    return terrain_height_xy(x_min + ix * cell_m, y_min + iy * cell_m)


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
            normalized_height = (
                terrain_height_xy(0.5 * (x0 + x1), 0.5 * (y0 + y1)) - TERRAIN_HEIGHT_MIN_M
            ) / TERRAIN_HEIGHT_SPAN_M
            shade = int(246 - 28 * normalized_height)
            if (ix + iy) % 2 == 0:
                shade = min(250, shade + 1)
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
        if obstacle.get("random_cluster") and obstacle.get("type") == "box":
            lo = obstacle["min"]
            hi = obstacle["max"]
            px0, py1 = map_to_pixel(float(lo[0]), float(lo[1]), bounds, px_per_m, height_px)
            px1, py0 = map_to_pixel(float(hi[0]), float(hi[1]), bounds, px_per_m, height_px)
            fill_rect(pixels, width_px, height_px, px0, py0, px1, py1, (92, 92, 92))
            count += 1
            continue
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
    *,
    ground_cell_m: float,
    obstacle_height_min_m: float,
    obstacle_height_max_m: float,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    header_text = f"Quadrotor static map ground={ground_cell_m:g}m obstacle_h={obstacle_height_min_m:g}-{obstacle_height_max_m:g}m"
    header = header_text.encode("ascii", errors="ignore")[:80].ljust(80, b" ")
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
            z_top = terrain_height_xy(0.5 * (x0 + x1), 0.5 * (y0 + y1))
            add_box(triangles, x0, x1, y0, y1, 0.0, z_top)

    random_count = 0
    for obstacle in obstacles:
        if obstacle.get("random_cluster") and obstacle.get("type") == "box":
            lo = [float(v) for v in obstacle["min"]]
            hi = [float(v) for v in obstacle["max"]]
            add_box(triangles, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])
            random_count += 1
            continue
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


def build_static_mesh_layers(
    bounds: dict[str, Any],
    obstacles: list[dict[str, Any]],
    *,
    ground_cell_m: float,
    default_obstacle_footprint_m: float,
    band_count: int,
) -> tuple[
    list[list[tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]]],
    list[tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]],
    list[tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]],
    int,
    int,
]:
    x_min, x_max = [float(v) for v in bounds["x"]]
    y_min, y_max = [float(v) for v in bounds["y"]]
    nx = int(math.ceil((x_max - x_min) / ground_cell_m))
    ny = int(math.ceil((y_max - y_min) / ground_cell_m))
    terrain_bands = [[] for _ in range(band_count)]
    obstacle_triangles: list[
        tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]
    ] = []
    grid_triangles: list[
        tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]
    ] = []

    for ix in range(nx):
        for iy in range(ny):
            x0 = x_min + ix * ground_cell_m
            x1 = min(x0 + ground_cell_m, x_max)
            y0 = y_min + iy * ground_cell_m
            y1 = min(y0 + ground_cell_m, y_max)
            z_center = terrain_height_xy(0.5 * (x0 + x1), 0.5 * (y0 + y1))
            normalized = (z_center - TERRAIN_HEIGHT_MIN_M) / TERRAIN_HEIGHT_SPAN_M
            band = max(0, min(band_count - 1, int(normalized * band_count)))
            add_box(terrain_bands[band], x0, x1, y0, y1, 0.0, z_center)

    random_count = 0
    for obstacle in obstacles:
        if obstacle.get("random_cluster") and obstacle.get("type") == "box":
            lo = [float(v) for v in obstacle["min"]]
            hi = [float(v) for v in obstacle["max"]]
            add_box(obstacle_triangles, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])
            random_count += 1
            continue
        if obstacle.get("type") != "cylinder":
            continue
        x, y, _ = [float(v) for v in obstacle["center"]]
        height = float(obstacle.get("height", 3.0))
        z_min = float(obstacle.get("z_min", 0.0))
        footprint_m = float(obstacle.get("visual_size_m", default_obstacle_footprint_m))
        half = 0.5 * footprint_m
        add_box(obstacle_triangles, x - half, x + half, y - half, y + half, z_min, z_min + height)
        random_count += 1

    return terrain_bands, obstacle_triangles, grid_triangles, random_count, nx * ny


def add_terrain_grid_overlay(
    triangles: list[tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]],
    bounds: dict[str, Any],
    *,
    global_spacing_m: float,
    local_patch_center: tuple[float, float],
    local_patch_size_m: float,
    local_spacing_m: float,
    strip_width_m: float,
    z_lift_m: float,
) -> None:
    x_min, x_max = [float(v) for v in bounds["x"]]
    y_min, y_max = [float(v) for v in bounds["y"]]

    def add_strip_x(x: float, y0: float, y1: float, step: float) -> None:
        half = 0.5 * strip_width_m
        segments = max(1, int(math.ceil((y1 - y0) / step)))
        for index in range(segments):
            ya = y0 + index * step
            yb = min(y1, ya + step)
            p00 = (x - half, ya, terrain_height_xy(x, ya) + z_lift_m)
            p10 = (x + half, ya, terrain_height_xy(x, ya) + z_lift_m)
            p11 = (x + half, yb, terrain_height_xy(x, yb) + z_lift_m)
            p01 = (x - half, yb, terrain_height_xy(x, yb) + z_lift_m)
            add_triangle(triangles, p00, p10, p11)
            add_triangle(triangles, p00, p11, p01)

    def add_strip_y(y: float, x0: float, x1: float, step: float) -> None:
        half = 0.5 * strip_width_m
        segments = max(1, int(math.ceil((x1 - x0) / step)))
        for index in range(segments):
            xa = x0 + index * step
            xb = min(x1, xa + step)
            p00 = (xa, y - half, terrain_height_xy(xa, y) + z_lift_m)
            p10 = (xb, y - half, terrain_height_xy(xb, y) + z_lift_m)
            p11 = (xb, y + half, terrain_height_xy(xb, y) + z_lift_m)
            p01 = (xa, y + half, terrain_height_xy(xa, y) + z_lift_m)
            add_triangle(triangles, p00, p10, p11)
            add_triangle(triangles, p00, p11, p01)

    x = math.ceil(x_min / global_spacing_m) * global_spacing_m
    while x <= x_max + 1e-9:
        add_strip_x(x, y_min, y_max, step=1.0)
        x += global_spacing_m
    y = math.ceil(y_min / global_spacing_m) * global_spacing_m
    while y <= y_max + 1e-9:
        add_strip_y(y, x_min, x_max, step=1.0)
        y += global_spacing_m

    cx, cy = local_patch_center
    patch_x0 = max(x_min, cx - 0.5 * local_patch_size_m)
    patch_x1 = min(x_max, cx + 0.5 * local_patch_size_m)
    patch_y0 = max(y_min, cy - 0.5 * local_patch_size_m)
    patch_y1 = min(y_max, cy + 0.5 * local_patch_size_m)
    x = patch_x0
    while x <= patch_x1 + 1e-9:
        add_strip_x(x, patch_y0, patch_y1, step=local_spacing_m)
        x += local_spacing_m
    y = patch_y0
    while y <= patch_y1 + 1e-9:
        add_strip_y(y, patch_x0, patch_x1, step=local_spacing_m)
        y += local_spacing_m


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


def generate(
    config_path: Path,
    output_dir: Path,
    stl_path: Path,
    px_per_m: float,
    ground_cell_m: float,
    obstacle_footprint_min_m: float,
    obstacle_footprint_max_m: float,
    obstacle_height_min_m: float,
    obstacle_height_max_m: float,
) -> dict[str, Any]:
    config_path = config_path.resolve()
    raw_config = read_yaml(config_path)
    expanded_config = expand_random_obstacles(expand_wall_groups(raw_config))
    map_config = expanded_config["map"]
    bounds = map_config["bounds"]
    x_min, x_max = [float(v) for v in bounds["x"]]
    y_min, y_max = [float(v) for v in bounds["y"]]
    width_px = int(round((x_max - x_min) * px_per_m))
    height_px = int(round((y_max - y_min) * px_per_m))
    pixels = bytearray([255] * width_px * height_px * 3)

    static_obstacles = [obstacle for obstacle in map_config.get("obstacles", []) if obstacle.get("random_cluster")]
    distribution_diagnostics = {
        "source": "planner_truth_random_clusters",
        "random_cluster_count": len({obstacle.get("random_cluster_id") for obstacle in static_obstacles}),
        "random_column_count": len(static_obstacles),
        "column_size_m": map_config.get("random_obstacles", {}).get("column_size_m", 0.2),
    }
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
    image_path = output_dir / "map_open_blocks_static_ground_0p2_obstacle_columns_0p2_h2p8_3p5.png"
    manifest_path = output_dir / "map_open_blocks_static_ground_0p2_obstacle_columns_0p2_h2p8_3p5_manifest.json"
    write_png(image_path, width_px, height_px, pixels)
    triangles, mesh_obstacle_count, ground_cell_count = build_static_mesh(
        bounds,
        static_obstacles,
        ground_cell_m=ground_cell_m,
        default_obstacle_footprint_m=obstacle_footprint_max_m,
    )
    write_binary_stl(
        stl_path,
        triangles,
        ground_cell_m=ground_cell_m,
        obstacle_height_min_m=obstacle_height_min_m,
        obstacle_height_max_m=obstacle_height_max_m,
    )
    terrain_band_triangles, obstacle_triangles, grid_triangles, layered_obstacle_count, layered_ground_cell_count = build_static_mesh_layers(
        bounds,
        static_obstacles,
        ground_cell_m=ground_cell_m,
        default_obstacle_footprint_m=obstacle_footprint_max_m,
        band_count=TERRAIN_BAND_COUNT,
    )
    for band_path, band_triangles in zip(TERRAIN_BAND_STLS, terrain_band_triangles):
        write_binary_stl(
            band_path,
            band_triangles,
            ground_cell_m=ground_cell_m,
            obstacle_height_min_m=obstacle_height_min_m,
            obstacle_height_max_m=obstacle_height_max_m,
        )
    write_binary_stl(
        OBSTACLE_STL,
        obstacle_triangles,
        ground_cell_m=ground_cell_m,
        obstacle_height_min_m=obstacle_height_min_m,
        obstacle_height_max_m=obstacle_height_max_m,
    )
    write_binary_stl(
        GRID_STL,
        [],
        ground_cell_m=ground_cell_m,
        obstacle_height_min_m=obstacle_height_min_m,
        obstacle_height_max_m=obstacle_height_max_m,
    )
    if layered_obstacle_count != mesh_obstacle_count or layered_ground_cell_count != ground_cell_count:
        raise RuntimeError("Layered mesh counts do not match the combined static mesh counts")

    wall_boxes = [
        item
        for item in map_config.get("obstacles", [])
        if item.get("type") == "box" and "wall_group_id" in item
    ]
    manifest = {
        "source_config": str(config_path.relative_to(ROOT)),
        "image": str(image_path.relative_to(ROOT)),
        "stl": str(stl_path.relative_to(ROOT)),
        "combined_stl_policy": "review_only_not_used_by_Sysplorer_model; model uses terrain_band_stls plus obstacle_stl to keep individual files below GitHub hard limit",
        "terrain_band_stls": [str(path.relative_to(ROOT)) for path in TERRAIN_BAND_STLS],
        "obstacle_stl": str(OBSTACLE_STL.relative_to(ROOT)),
        "grid_overlay_stl": str(GRID_STL.relative_to(ROOT)),
        "purpose": "static_environment_visualization_only",
        "planner_knowledge_policy": "online_planner_must_use_local_discovered_map_not_this_full_static_image",
        "bounds_m": bounds,
        "image_size_px": [width_px, height_px],
        "pixels_per_meter": px_per_m,
        "ground_cell_size_m": ground_cell_m,
        "ground_cell_count": ground_cell_count,
        "terrain_height_range_m": [TERRAIN_HEIGHT_MIN_M, TERRAIN_HEIGHT_MAX_M],
        "random_obstacle_visual_footprint_range_m": [0.2, 0.2],
        "random_obstacle_height_range_m": [obstacle_height_min_m, obstacle_height_max_m],
        "random_obstacle_count": len({obstacle.get("random_cluster_id") for obstacle in static_obstacles}),
        "random_obstacle_column_count": obstacle_count,
        "random_obstacle_distribution": "planner_truth_column_clusters",
        "random_obstacle_distribution_diagnostics": distribution_diagnostics,
        "mesh_random_obstacle_count": mesh_obstacle_count,
        "mesh_triangle_count": len(triangles),
        "terrain_band_triangle_counts": [len(item) for item in terrain_band_triangles],
        "obstacle_triangle_count": len(obstacle_triangles),
        "grid_overlay_triangle_count": len(grid_triangles),
        "terrain_visualization": {
            "mode": "volumetric_ground_columns_five_height_bands_plus_grid_overlay",
            "terrain_geometry": "0.2 m x 0.2 m cuboid columns; each cell samples its own center-point height, starts at z=0, and uses 0.01 m stair-step height quantization plus deterministic per-cell height jitter",
            "height_band_count": TERRAIN_BAND_COUNT,
            "height_step_m": TERRAIN_STEP_M,
            "height_band_policy": "bands split STL files and colors only; visible stair steps come from per-cell height quantization, not from shared band heights",
            "grid_overlay_policy": "disabled in the GUI STL to remove dark grid lines; terrain height bands keep color coding",
            "global_grid_spacing_m": 2.0,
            "local_resolution_patch": {
                "center_m": [-41.0, -26.0],
                "size_m": 4.0,
                "grid_spacing_m": ground_cell_m,
            },
        },
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
    parser.add_argument("--ground-cell-m", type=float, default=0.2)
    parser.add_argument("--obstacle-footprint-min-m", type=float, default=0.2)
    parser.add_argument("--obstacle-footprint-max-m", type=float, default=0.2)
    parser.add_argument("--obstacle-height-min-m", type=float, default=2.8)
    parser.add_argument("--obstacle-height-max-m", type=float, default=3.5)
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
        args.obstacle_height_min_m,
        args.obstacle_height_max_m,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
