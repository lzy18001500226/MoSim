#!/usr/bin/env python3
"""Summarize one three-UAV MWORKS formation CSV without changing source data."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path


UAV_COLUMNS = {
    "uav1": ("x", "y", "z", "x_ref", "y_ref", "z_ref"),
    "uav2": ("uav2_x", "uav2_y", "uav2_z", "uav2_x_ref", "uav2_y_ref", "uav2_z_ref"),
    "uav3": ("uav3_x", "uav3_y", "uav3_z", "uav3_x_ref", "uav3_y_ref", "uav3_z_ref"),
}


def read_rows(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        required = {"time", "formation_error_m", "min_inter_uav_distance_m"}
        for columns in UAV_COLUMNS.values():
            required.update(columns)
        missing = sorted(required.difference(reader.fieldnames))
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")
        return [
            {name: float(value) if value not in (None, "") else math.nan for name, value in row.items()}
            for row in reader
        ]


def finite(values: list[float]) -> list[float]:
    return [value for value in values if math.isfinite(value)]


def vehicle_metrics(rows: list[dict[str, float]], columns: tuple[str, ...]) -> dict[str, float | bool]:
    x, y, z, x_ref, y_ref, z_ref = columns
    errors = [
        math.sqrt(
            (row[x] - row[x_ref]) ** 2
            + (row[y] - row[y_ref]) ** 2
            + (row[z] - row[z_ref]) ** 2
        )
        for row in rows
    ]
    valid = len(errors) == len(rows) and all(math.isfinite(value) for value in errors)
    return {
        "position_rmse_m": math.sqrt(sum(value * value for value in errors) / len(errors)),
        "max_position_error_m": max(errors),
        "terminal_position_error_m": errors[-1],
        "finite": valid,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    rows = read_rows(args.input_csv)
    if not rows:
        raise ValueError("CSV has no samples")
    formation_errors = [row["formation_error_m"] for row in rows]
    minimum_distances = [row["min_inter_uav_distance_m"] for row in rows]
    if not all(math.isfinite(value) for value in formation_errors + minimum_distances):
        raise ValueError("Formation channels contain non-finite values")

    vehicles = {name: vehicle_metrics(rows, columns) for name, columns in UAV_COLUMNS.items()}
    payload = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_csv": str(args.input_csv),
        "row_count": len(rows),
        "duration_s": rows[-1]["time"] - rows[0]["time"],
        "sample_rate_hz": (len(rows) - 1) / (rows[-1]["time"] - rows[0]["time"]),
        "vehicles": vehicles,
        "formation_error_rmse_m": math.sqrt(
            sum(value * value for value in formation_errors) / len(formation_errors)
        ),
        "formation_error_max_m": max(formation_errors),
        "formation_terminal_error_m": formation_errors[-1],
        "minimum_inter_uav_distance_m": min(minimum_distances),
        "valid": all(bool(metrics["finite"]) for metrics in vehicles.values()),
        "scope": "MWORKS nominal PX4CTRL three-UAV virtual-structure triangle figure-eight only",
        "not_claimed": [
            "obstacle avoidance",
            "distributed swarm planning",
            "inter-UAV collision avoidance",
            "Gazebo, PX4, ROS, or QGC runtime validation",
        ],
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
