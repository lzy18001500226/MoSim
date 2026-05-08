#!/usr/bin/env python3
"""Compute standard quadrotor tracking metrics from a project CSV file."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path


REQUIRED_COLUMNS = ["time", "x", "y", "z", "x_ref", "y_ref", "z_ref"]
MOTOR_COLUMNS = ["u1", "u2", "u3", "u4"]


def read_csv(path: Path) -> dict[str, list[float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        missing = [name for name in REQUIRED_COLUMNS if name not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns in {path}: {', '.join(missing)}")
        data = {name: [] for name in reader.fieldnames}
        for row in reader:
            for name in reader.fieldnames:
                value = row.get(name, "")
                data[name].append(float(value) if value != "" else math.nan)
        return data


def mean(values: list[float]) -> float:
    return math.nan if not values else sum(values) / len(values)


def rmse(values: list[float]) -> float:
    return math.sqrt(mean([value * value for value in values]))


def trapezoid_integral(time: list[float], values: list[float]) -> float:
    if len(time) < 2 or len(values) < 2:
        return math.nan
    total = 0.0
    for index in range(1, len(time)):
        dt = time[index] - time[index - 1]
        total += 0.5 * dt * (values[index] + values[index - 1])
    return total


def compute_metrics(data: dict[str, list[float]], raw_file: Path, scene_id: str, controller_id: str) -> dict[str, object]:
    time = data["time"]
    ex = [x - xr for x, xr in zip(data["x"], data["x_ref"])]
    ey = [y - yr for y, yr in zip(data["y"], data["y_ref"])]
    ez = [z - zr for z, zr in zip(data["z"], data["z_ref"])]
    ep = [math.sqrt(x * x + y * y + z * z) for x, y, z in zip(ex, ey, ez)]

    if time:
        final_window_start = max(time) - max(5.0, 0.2 * (max(time) - min(time)))
        final_error = [error for t, error in zip(time, ep) if t >= final_window_start]
    else:
        final_error = []

    motor_cols = [name for name in MOTOR_COLUMNS if name in data]
    control_norm_sq = []
    saturation_samples = 0
    if motor_cols:
        for index in range(len(time)):
            total = 0.0
            for name in motor_cols:
                value = data[name][index]
                total += value * value
                if value <= 1e-9 or value >= 1.0 - 1e-9:
                    saturation_samples += 1
            control_norm_sq.append(total)

    nan_count = sum(1 for values in data.values() for value in values if math.isnan(value))
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "raw_file": str(raw_file),
        "scene_id": scene_id,
        "controller_id": controller_id,
        "row_count": len(time),
        "duration_s": (max(time) - min(time)) if time else math.nan,
        "position_rmse_m": rmse(ep),
        "x_rmse_m": rmse(ex),
        "y_rmse_m": rmse(ey),
        "z_rmse_m": rmse(ez),
        "max_position_error_m": max(ep) if ep else math.nan,
        "steady_state_error_m": mean(final_error),
        "control_energy": trapezoid_integral(time, control_norm_sq) if control_norm_sq else math.nan,
        "saturation_ratio": saturation_samples / (len(time) * len(motor_cols)) if motor_cols else math.nan,
        "nan_count": nan_count,
        "valid": len(time) > 10 and nan_count == 0,
    }


def write_outputs(metrics: dict[str, object], json_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    csv_path = json_path.with_suffix(".csv")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        for key in sorted(metrics):
            writer.writerow([key, metrics[key]])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_csv", type=Path)
    parser.add_argument("metrics_json", type=Path)
    parser.add_argument("scene_id", nargs="?", default=None)
    parser.add_argument("controller_id", nargs="?", default="unknown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scene_id = args.scene_id or args.raw_csv.stem
    data = read_csv(args.raw_csv)
    metrics = compute_metrics(data, args.raw_csv, scene_id, args.controller_id)
    write_outputs(metrics, args.metrics_json)
    print(f"Metrics written: {args.metrics_json}")
    print(f"Metrics CSV: {args.metrics_json.with_suffix('.csv')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
