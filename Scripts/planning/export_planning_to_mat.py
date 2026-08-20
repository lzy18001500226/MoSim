#!/usr/bin/env python3
"""Export planning CSV results to MAT format for MWORKS CombiTimeTable.

This allows MWORKS models to directly read planning results at simulation time,
eliminating the need to update hardcoded waypoints in .mo files.
"""

import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.io import savemat

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT_DIR = ROOT / "Results/planning/three_uav_open_blocks_mworks_20260720/raw"
DEFAULT_OUTPUT_DIR = ROOT / "Results/planning/three_uav_open_blocks_mworks_20260720/mat"


def csv_to_mat(csv_path: Path, mat_path: Path, table_name: str = "reference"):
    """Convert planning CSV to MAT format for CombiTimeTable."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        data = list(reader)

    if not data:
        raise ValueError(f"Empty CSV file: {csv_path}")

    # Extract columns: time, x_ref, y_ref, z_ref, yaw_ref
    time = np.array([float(row['time']) for row in data])
    x_ref = np.array([float(row['x_ref']) for row in data])
    y_ref = np.array([float(row['y_ref']) for row in data])
    z_ref = np.array([float(row['z_ref']) for row in data])

    # Check if yaw_ref exists (some CSVs might not have it)
    has_yaw = 'yaw_ref' in data[0]
    if has_yaw:
        yaw_ref = np.array([float(row['yaw_ref']) for row in data])
        table = np.column_stack([time, x_ref, y_ref, z_ref, yaw_ref])
    else:
        table = np.column_stack([time, x_ref, y_ref, z_ref])

    # Save to MAT file
    # CombiTimeTable expects a variable matching tableName parameter
    savemat(mat_path, {table_name: table}, oned_as='column')

    return {
        'points': len(time),
        'duration': float(time[-1]),
        'dt': float(time[1] - time[0]) if len(time) > 1 else 0.0,
        'columns': 5 if has_yaw else 4,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument('--output-dir', type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    uav_files = [
        ('uav1_reference.csv', 'uav1_reference.mat', 'uav1_ref'),
        ('uav2_reference.csv', 'uav2_reference.mat', 'uav2_ref'),
        ('uav3_reference.csv', 'uav3_reference.mat', 'uav3_ref'),
    ]

    print(f"Converting planning CSVs to MAT format")
    print(f"Input:  {input_dir}")
    print(f"Output: {output_dir}\n")

    for csv_name, mat_name, table_name in uav_files:
        csv_path = input_dir / csv_name
        mat_path = output_dir / mat_name

        if not csv_path.exists():
            print(f"WARNING: {csv_name} not found, skipping")
            continue

        info = csv_to_mat(csv_path, mat_path, table_name)
        print(f"{mat_name}: {info['points']} points, {info['duration']:.2f}s, {info['columns']} columns")

    print(f"\nMAT files ready for MWORKS CombiTimeTable")
    print(f"Use in model: tableOnFile=true, fileName=\"{output_dir.as_posix()}/uav1_reference.mat\"")


if __name__ == '__main__':
    main()
