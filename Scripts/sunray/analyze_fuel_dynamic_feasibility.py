#!/usr/bin/env python3
"""Audit FUEL raw position commands against per-axis dynamic limits."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


AXES = ("x", "y", "z")


def _finite(row: dict[str, str], key: str) -> float:
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError(f"non-finite {key}: {row[key]!r}")
    return value


def analyze(path: Path, max_velocity: float, max_acceleration: float) -> dict:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError(f"no command rows in {path}")

    velocity_peaks = {axis: 0.0 for axis in AXES}
    acceleration_peaks = {axis: 0.0 for axis in AXES}
    velocity_violation_rows = 0
    acceleration_violation_rows = 0
    for row in rows:
        velocity = {axis: abs(_finite(row, f"v{axis}")) for axis in AXES}
        acceleration = {axis: abs(_finite(row, f"a{axis}")) for axis in AXES}
        for axis in AXES:
            velocity_peaks[axis] = max(velocity_peaks[axis], velocity[axis])
            acceleration_peaks[axis] = max(acceleration_peaks[axis], acceleration[axis])
        velocity_violation_rows += int(any(value > max_velocity + 1e-4 for value in velocity.values()))
        acceleration_violation_rows += int(
            any(value > max_acceleration + 1e-4 for value in acceleration.values())
        )

    peak_velocity = max(velocity_peaks.values())
    peak_acceleration = max(acceleration_peaks.values())
    required_time_ratio = max(
        peak_velocity / max_velocity,
        math.sqrt(peak_acceleration / max_acceleration),
    )
    return {
        "schema": "mosim.fuel_dynamic_feasibility.v1",
        "source": str(path.resolve()),
        "row_count": len(rows),
        "limits": {
            "per_axis_velocity_mps": max_velocity,
            "per_axis_acceleration_mps2": max_acceleration,
        },
        "peaks": {
            "velocity_mps": velocity_peaks,
            "acceleration_mps2": acceleration_peaks,
        },
        "violations": {
            "velocity_rows": velocity_violation_rows,
            "velocity_fraction": velocity_violation_rows / len(rows),
            "acceleration_rows": acceleration_violation_rows,
            "acceleration_fraction": acceleration_violation_rows / len(rows),
        },
        "required_uniform_time_scale_lower_bound": required_time_ratio,
        "feasible": velocity_violation_rows == 0 and acceleration_violation_rows == 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command_csv", type=Path)
    parser.add_argument("--max-velocity", type=float, required=True)
    parser.add_argument("--max-acceleration", type=float, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-feasible", action="store_true")
    args = parser.parse_args()
    if args.max_velocity <= 0.0 or args.max_acceleration <= 0.0:
        parser.error("dynamic limits must be positive")

    result = analyze(args.command_csv, args.max_velocity, args.max_acceleration)
    payload = json.dumps(result, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return int(args.require_feasible and not result["feasible"])


if __name__ == "__main__":
    raise SystemExit(main())
