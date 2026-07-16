#!/usr/bin/env python3
"""Replay recorded RACER command positions through the PVA limiter."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from trajectory_dynamics import constrain_kinematic_step, enforce_position_z_bounds


def vector(row: dict[str, str], prefix: str) -> tuple[float, float, float]:
    names = (prefix + "x", prefix + "y", prefix + "z")
    return tuple(float(row[name]) for name in names)


def norm(values: tuple[float, float, float]) -> float:
    return math.sqrt(sum(value * value for value in values))


def replay_file(
    path: Path,
    max_velocity: float,
    max_acceleration: float,
    max_lateral_acceleration: float,
    max_jerk: float,
    min_z: float,
    max_z: float,
    event_start: float,
    event_end: float,
) -> dict:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("phase") == "ego_execute"]
    if len(rows) < 2:
        raise ValueError(f"{path} has fewer than two ego_execute rows")

    previous_position = vector(rows[0], "")
    previous_velocity = vector(rows[0], "v")
    previous_acceleration = vector(rows[0], "a")
    previous_time = float(rows[0]["t"])
    maxima = {
        "velocity_mps": norm(previous_velocity),
        "acceleration_mps2": norm(previous_acceleration),
        "lateral_acceleration_mps2": math.hypot(*previous_acceleration[:2]),
        "jerk_mps3": 0.0,
        "candidate_position_error_m": 0.0,
    }
    event_maxima = {key: 0.0 for key in maxima}
    limited_count = 0
    z_clamp_count = 0
    nonpositive_dt_count = 0

    for row in rows[1:]:
        now = float(row["t"])
        dt = now - previous_time
        if dt <= 0.0:
            nonpositive_dt_count += 1
            continue
        candidate = vector(row, "")
        result = constrain_kinematic_step(
            previous_position,
            previous_velocity,
            previous_acceleration,
            candidate,
            dt,
            max_velocity,
            max_acceleration,
            max_lateral_acceleration,
            max_jerk,
        )
        bounded = enforce_position_z_bounds(
            result["position"],
            result["velocity"],
            result["acceleration"],
            result["jerk"],
            min_z,
            max_z,
        )
        if result["limited"]:
            limited_count += 1
        if bounded["corrected"]:
            z_clamp_count += 1

        current = {
            "velocity_mps": norm(bounded["velocity"]),
            "acceleration_mps2": norm(bounded["acceleration"]),
            "lateral_acceleration_mps2": math.hypot(*bounded["acceleration"][:2]),
            "jerk_mps3": norm(bounded["jerk"]),
            "candidate_position_error_m": math.dist(bounded["position"], candidate),
        }
        for key, value in current.items():
            maxima[key] = max(maxima[key], value)
            if event_start <= now <= event_end:
                event_maxima[key] = max(event_maxima[key], value)

        previous_position = bounded["position"]
        previous_velocity = bounded["velocity"]
        previous_acceleration = bounded["acceleration"]
        previous_time = now

    tolerance = 1e-6
    checks = {
        "velocity_within_limit": max_velocity <= 0.0 or maxima["velocity_mps"] <= max_velocity + tolerance,
        "acceleration_within_limit": max_acceleration <= 0.0 or maxima["acceleration_mps2"] <= max_acceleration + tolerance,
        "lateral_acceleration_within_limit": max_lateral_acceleration <= 0.0
        or maxima["lateral_acceleration_mps2"] <= max_lateral_acceleration + tolerance,
        "jerk_within_limit": max_jerk <= 0.0 or maxima["jerk_mps3"] <= max_jerk + tolerance,
        "altitude_within_bounds": min_z - tolerance <= previous_position[2] <= max_z + tolerance,
    }
    return {
        "input": str(path),
        "ego_execute_rows": len(rows),
        "time_range_s": [float(rows[0]["t"]), float(rows[-1]["t"])],
        "limited_rows": limited_count,
        "post_dynamics_z_clamps": z_clamp_count,
        "nonpositive_dt_rows_skipped": nonpositive_dt_count,
        "maxima": maxima,
        "event_window_s": [event_start, event_end],
        "event_window_maxima": event_maxima,
        "checks": checks,
        "status": "passed" if all(checks.values()) else "blocked",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--uav-num", type=int, default=3)
    parser.add_argument("--max-velocity-mps", type=float, default=2.0)
    parser.add_argument("--max-acceleration-mps2", type=float, default=1.2)
    parser.add_argument("--max-lateral-acceleration-mps2", type=float, default=1.2)
    parser.add_argument("--max-jerk-mps3", type=float, default=6.0)
    parser.add_argument("--min-z", type=float, default=0.9)
    parser.add_argument("--max-z", type=float, default=1.35)
    parser.add_argument("--event-start-s", type=float, default=100.0)
    parser.add_argument("--event-end-s", type=float, default=105.0)
    args = parser.parse_args()

    vehicles = []
    for uid in range(1, args.uav_num + 1):
        result = replay_file(
            args.run_dir / f"uav{uid}_position_cmd.csv",
            args.max_velocity_mps,
            args.max_acceleration_mps2,
            args.max_lateral_acceleration_mps2,
            args.max_jerk_mps3,
            args.min_z,
            args.max_z,
            args.event_start_s,
            args.event_end_s,
        )
        result["uav_id"] = uid
        vehicles.append(result)

    report = {
        "schema": "mosim.racer.command_dynamics_replay.v1",
        "status": "passed" if all(item["status"] == "passed" for item in vehicles) else "blocked",
        "source_run": str(args.run_dir),
        "limits": {
            "max_velocity_mps": args.max_velocity_mps,
            "max_acceleration_mps2": args.max_acceleration_mps2,
            "max_lateral_acceleration_mps2": args.max_lateral_acceleration_mps2,
            "max_jerk_mps3": args.max_jerk_mps3,
            "min_z_m": args.min_z,
            "max_z_m": args.max_z,
        },
        "vehicles": vehicles,
        "claim_boundary": (
            "Offline replay proves only that recorded RACER command positions can be passed through "
            "the configured PVA limiter without violating its declared numeric bounds. It does not "
            "prove Gazebo flight stability, controller performance, collision avoidance, trajectory "
            "freshness, or coverage."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
