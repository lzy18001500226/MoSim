#!/usr/bin/env python3
"""Update OpenBlocks Px4Ctrl reference models from planning CSV files."""

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLANNING_DIR = ROOT / "Results/planning/three_uav_open_blocks_mworks_20260720/raw"
TARGET_WAYPOINTS = 54  # Extract 54 waypoints from ~6000 points


def read_trajectory_csv(csv_path: Path) -> list[dict]:
    """Read trajectory CSV and return list of {time, x, y, z} dicts."""
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                'time': float(row['time']),
                'x': float(row['x_ref']),
                'y': float(row['y_ref']),
                'z': float(row['z_ref']),
            })
    return rows


def extract_waypoints(rows: list[dict], n_waypoints: int) -> tuple[list[float], list[float], list[float], list[float]]:
    """Extract n evenly-spaced waypoints and calculate segment durations."""
    if len(rows) < 2:
        raise ValueError(f"Need at least 2 points, got {len(rows)}")

    indices = [int(i * (len(rows) - 1) / (n_waypoints - 1)) for i in range(n_waypoints)]
    waypoints = [rows[i] for i in indices]

    p_x = [wp['x'] for wp in waypoints]
    p_y = [wp['y'] for wp in waypoints]
    p_z = [wp['z'] for wp in waypoints]

    # Calculate segment durations
    durations = []
    for i in range(len(waypoints) - 1):
        dt = waypoints[i + 1]['time'] - waypoints[i]['time']
        durations.append(dt)

    return p_x, p_y, p_z, durations


def format_modelica_array(values: list[float], per_line: int = 6) -> str:
    """Format array for Modelica with 6 values per line."""
    lines = []
    for i in range(0, len(values), per_line):
        chunk = values[i:i + per_line]
        line = ", ".join(f"{v:.2f}" for v in chunk)
        lines.append(line)
    return "{\n      " + ",\n      ".join(lines) + "}"


def update_reference_model(mo_path: Path, p_x: list[float], p_y: list[float],
                          p_z: list[float], durations: list[float]):
    """Update a reference .mo file with new waypoints and durations."""
    content = mo_path.read_text(encoding='utf-8')

    n_segments = len(durations)

    # Update n_segments
    content = re.sub(
        r'n_segments\s*=\s*\d+',
        f'n_segments = {n_segments}',
        content
    )

    # Update p_x array
    content = re.sub(
        r'p_x\s*=\s*\{[^}]+\}',
        f'p_x = {format_modelica_array(p_x)}',
        content,
        flags=re.DOTALL
    )

    # Update p_y array
    content = re.sub(
        r'p_y\s*=\s*\{[^}]+\}',
        f'p_y = {format_modelica_array(p_y)}',
        content,
        flags=re.DOTALL
    )

    # Update p_z array
    content = re.sub(
        r'p_z\s*=\s*\{[^}]+\}',
        f'p_z = {format_modelica_array(p_z)}',
        content,
        flags=re.DOTALL
    )

    # Update segment_duration array
    content = re.sub(
        r'segment_duration\s*=\s*\{[^}]+\}',
        f'segment_duration = {format_modelica_array(durations)}',
        content,
        flags=re.DOTALL
    )

    mo_path.write_text(content, encoding='utf-8')
    print(f"Updated {mo_path.name}: {n_segments} segments")


def main():
    trajectories_dir = PLANNING_DIR
    models_dir = ROOT / "Models/MoSimQuadrotorModel/Guidance/Trajectories"

    uav_configs = [
        ("uav1_reference.csv", "OpenBlocksPx4CtrlReference.mo"),
        ("uav2_reference.csv", "OpenBlocksUav2Reference.mo"),
        ("uav3_reference.csv", "OpenBlocksUav3Reference.mo"),
    ]

    for csv_name, mo_name in uav_configs:
        csv_path = trajectories_dir / csv_name
        mo_path = models_dir / mo_name

        if not csv_path.exists():
            print(f"CSV not found: {csv_path}")
            continue

        if not mo_path.exists():
            print(f"Model not found: {mo_path}")
            continue

        rows = read_trajectory_csv(csv_path)
        p_x, p_y, p_z, durations = extract_waypoints(rows, TARGET_WAYPOINTS)
        update_reference_model(mo_path, p_x, p_y, p_z, durations)

    print(f"\nAll three Px4Ctrl reference models updated from {trajectories_dir}")


if __name__ == '__main__':
    main()
