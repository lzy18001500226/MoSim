#!/usr/bin/env python3
"""Compare FUEL command, odometry, and Gazebo truth timelines."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def load(path: Path) -> list[dict[str, object]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    result: list[dict[str, object]] = []
    for row in rows:
        parsed: dict[str, object] = {}
        for key, value in row.items():
            if key == "phase":
                parsed[key] = value
            else:
                try:
                    parsed[key] = float(value)
                except (TypeError, ValueError):
                    parsed[key] = value
        result.append(parsed)
    return result


def norm(row: dict[str, object], names: tuple[str, ...]) -> float:
    return math.sqrt(sum(float(row[name]) ** 2 for name in names))


def nearest(rows: list[dict[str, object]], timestamp: float) -> dict[str, object]:
    return min(rows, key=lambda row: abs(float(row["t"]) - timestamp))


def peak(rows: list[dict[str, object]], names: tuple[str, ...]) -> dict[str, object]:
    row = max(rows, key=lambda item: norm(item, names))
    return {"t": row["t"], "phase": row.get("phase"), "value": norm(row, names)}


def finite_difference_peak(rows: list[dict[str, object]]) -> dict[str, object]:
    best = {"t": None, "phase": None, "value": 0.0, "dt": None}
    for previous, current in zip(rows, rows[1:]):
        dt = float(current["t"]) - float(previous["t"])
        if dt <= 1e-6 or dt > 0.2:
            continue
        value = math.sqrt(sum(
            ((float(current[name]) - float(previous[name])) / dt) ** 2
            for name in ("x", "y", "z")
        ))
        if value > float(best["value"]):
            best = {"t": current["t"], "phase": current.get("phase"), "value": value, "dt": dt}
    return best


def exploration(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [row for row in rows if row.get("phase") == "exploration_execute"]


def summarize(run: Path) -> dict[str, object]:
    raw = exploration(load(run / "planner_position_cmd_raw.csv"))
    command = exploration(load(run / "position_cmd.csv"))
    odom = exploration(load(run / "odom.csv"))
    truth = exploration(load(run / "truth.csv"))
    if not all((raw, command, odom, truth)):
        raise ValueError(f"{run}: one or more exploration streams are empty")

    truth_speed_peak = peak(truth, ("vx", "vy", "vz"))
    event_t = float(truth_speed_peak["t"])
    event = {
        "truth": nearest(truth, event_t),
        "odom": nearest(odom, event_t),
        "raw_command": nearest(raw, event_t),
        "final_command": nearest(command, event_t),
    }
    for row in event.values():
        row["speed_norm"] = norm(row, ("vx", "vy", "vz"))

    min_truth_z = min(truth, key=lambda row: float(row["z"]))
    z_t = float(min_truth_z["t"])
    return {
        "run": str(run),
        "sample_counts": {"raw": len(raw), "command": len(command), "odom": len(odom), "truth": len(truth)},
        "peaks": {
            "raw_declared_speed": peak(raw, ("vx", "vy", "vz")),
            "raw_declared_acceleration": peak(raw, ("ax", "ay", "az")),
            "raw_position_fd_speed": finite_difference_peak(raw),
            "final_declared_speed": peak(command, ("vx", "vy", "vz")),
            "odom_speed": peak(odom, ("vx", "vy", "vz")),
            "truth_speed": truth_speed_peak,
        },
        "at_truth_speed_peak": event,
        "at_min_truth_z": {
            "truth": min_truth_z,
            "odom": nearest(odom, z_t),
            "raw_command": nearest(raw, z_t),
            "final_command": nearest(command, z_t),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {"runs": [summarize(path.resolve()) for path in args.runs]}
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
