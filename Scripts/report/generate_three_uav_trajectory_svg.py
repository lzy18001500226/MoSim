#!/usr/bin/env python3
"""Generate SVG trajectory preview from three-UAV CSV result."""

import csv
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT_CSV = ROOT / "Results/formation/heterogeneous_openblocks/three_uav_heterogeneous_openblocks_20260818_current_turn/raw/three_uav.csv"
OUTPUT_SVG = ROOT / "Docs/报告/图/三机编队/02_OpenBlocks三机规划轨迹.svg"
MAP_CONFIG = ROOT / "Config/planners/astar_min_snap/map_open_blocks.yaml"
PLANNER_SCRIPT = ROOT / "Scripts/planning/plan_astar_min_snap.py"

# Map bounds from OpenBlocks config
X_MIN, X_MAX = -60.0, 50.0
Y_MIN, Y_MAX = -40.0, 35.0


def load_planner():
    """Load the project planner so the figure uses its exact map expansion."""
    spec = importlib.util.spec_from_file_location("mosim_astar_min_snap", PLANNER_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load planner: {PLANNER_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_openblocks_map(path: Path):
    """Expand wall templates and seeded columns using the planner implementation."""
    planner = load_planner()
    config = planner.read_yaml(path)
    config = planner.expand_wall_groups(config)
    config = planner.expand_random_obstacles(config)
    map_config = config["map"]
    bounds = map_config["bounds"]
    map_bounds = (
        float(bounds["x"][0]),
        float(bounds["x"][1]),
        float(bounds["y"][0]),
        float(bounds["y"][1]),
    )
    return planner, map_config["obstacles"], map_bounds

def read_positions(path: Path) -> tuple[list, list, list]:
    """Read UAV positions from CSV."""
    uav1, uav2, uav3 = [], [], []
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            uav1.append((float(row["pos_1_x"]), float(row["pos_1_y"])))
            uav2.append((float(row["pos_2_x"]), float(row["pos_2_y"])))
            uav3.append((float(row["pos_3_x"]), float(row["pos_3_y"])))
    return uav1, uav2, uav3

def generate_svg(
    uav1: list,
    uav2: list,
    uav3: list,
    output: Path,
    planner,
    obstacles: list,
    map_bounds: tuple[float, float, float, float],
) -> None:
    """Generate SVG with the OpenBlocks map and three UAV trajectories."""
    width, height, pad = 1200, 800, 45
    sx = lambda x: pad + (x - X_MIN) / (X_MAX - X_MIN) * (width - 2 * pad)
    sy = lambda y: height - pad - (y - Y_MIN) / (Y_MAX - Y_MIN) * (height - 2 * pad)

    colors = ("#0072B2", "#D55E00", "#009E73")  # Blue, Orange, Green
    trajectories = [uav1, uav2, uav3]

    # Downsample for SVG (every 50th point, ~1 point per 0.25s at 200Hz)
    downsampled = []
    for traj in trajectories:
        sampled = traj[::50]
        # Remove consecutive duplicate points (hovering at goal)
        deduplicated = [sampled[0]]
        for pt in sampled[1:]:
            if pt != deduplicated[-1]:
                deduplicated.append(pt)
        downsampled.append(deduplicated)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f7f8fa"/>',
    ]

    map_x_min, map_x_max, map_y_min, map_y_max = map_bounds
    parts.append(
        f'<rect x="{sx(map_x_min):.2f}" y="{sy(map_y_max):.2f}" '
        f'width="{sx(map_x_max) - sx(map_x_min):.2f}" '
        f'height="{sy(map_y_min) - sy(map_y_max):.2f}" '
        'fill="#eef1f4" stroke="#6b7280" stroke-width="2" stroke-dasharray="7 5"/>'
    )

    for obstacle in obstacles:
        x0, y0, x1, y1 = planner.obstacle_xy_bounds(obstacle)
        parts.append(
            f'<rect x="{sx(x0):.2f}" y="{sy(y1):.2f}" '
            f'width="{sx(x1) - sx(x0):.2f}" height="{sy(y0) - sy(y1):.2f}" '
            'fill="#4b5563" opacity="0.55"/>'
        )

    # Draw trajectories
    for traj, color in zip(downsampled, colors):
        points = " ".join(f"{sx(x):.2f},{sy(y):.2f}" for x, y in traj)
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
        # Start marker (filled circle)
        parts.append(f'<circle cx="{sx(traj[0][0]):.2f}" cy="{sy(traj[0][1]):.2f}" r="6" fill="{color}"/>')
        # End marker (hollow circle)
        parts.append(f'<circle cx="{sx(traj[-1][0]):.2f}" cy="{sy(traj[-1][1]):.2f}" r="6" fill="none" stroke="{color}" stroke-width="3"/>')

    parts.append(
        '<text x="45" y="28" font-family="Segoe UI, sans-serif" font-size="18">'
        'Three-UAV OpenBlocks map and trajectories (MWORKS simulation)</text>'
    )
    parts.append("</svg>")

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")

if __name__ == "__main__":
    uav1, uav2, uav3 = read_positions(INPUT_CSV)
    planner, obstacles, map_bounds = read_openblocks_map(MAP_CONFIG)
    generate_svg(uav1, uav2, uav3, OUTPUT_SVG, planner, obstacles, map_bounds)
    print(f"Generated: {OUTPUT_SVG}")
    print(f"  OpenBlocks obstacles: {len(obstacles)}")
    print(f"  UAV1: {len(uav1)} points")
    print(f"  UAV2: {len(uav2)} points")
    print(f"  UAV3: {len(uav3)} points")
