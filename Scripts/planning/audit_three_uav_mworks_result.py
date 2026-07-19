#!/usr/bin/env python3
"""Audit the exported three-UAV OpenBlocks MWORKS result."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE = ROOT / "Results/planning/three_uav_open_blocks_mworks_20260720"
DEFAULT_RAW = DEFAULT_BUNDLE / "raw/mworks_full_conservative_304p84s.csv"
DEFAULT_PLANNING = DEFAULT_BUNDLE / "metrics/three_uav_planning_metrics.json"
DEFAULT_JSON = DEFAULT_BUNDLE / "metrics/mworks_full_conservative_metrics.json"
DEFAULT_CSV = DEFAULT_BUNDLE / "metrics/mworks_full_conservative_metrics.csv"

MIN_PAIR_DISTANCE_M = 1.0
MIN_COLLISION_CLEARANCE_M = 0.0
PLANNING_MARGIN_M = 0.35
MAX_TRACKING_RMSE_M = 0.20
MAX_TRACKING_ERROR_M = 0.50
MAX_FINAL_TRACKING_ERROR_M = 0.15


def read_numeric_csv(path: Path) -> dict[str, list[float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        data = {name: [] for name in reader.fieldnames}
        for row_index, row in enumerate(reader, start=2):
            for name in reader.fieldnames:
                try:
                    data[name].append(float(row[name]))
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"Invalid numeric value at row {row_index}, column {name}") from exc
    return data


def rmse(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / len(values))


def audit(raw_path: Path, planning_path: Path) -> dict[str, Any]:
    data = read_numeric_csv(raw_path)
    required = {
        "time_s",
        "minimum_pair_distance_m",
        "formation_distance_error_m",
        "clearance_lower_bound_m",
    }
    for index in range(1, 4):
        required.add(f"uav{index}_tracking_error_m")
        for axis in "xyz":
            required.add(f"uav{index}_{axis}_m")
            required.add(f"uav{index}_ref_{axis}_m")
    missing = sorted(required - data.keys())
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    times = data["time_s"]
    if len(times) < 11:
        raise ValueError(f"Expected more than 10 samples, got {len(times)}")
    if any(right <= left for left, right in zip(times, times[1:])):
        raise ValueError("time_s must be strictly increasing")

    non_finite_count = sum(
        1 for values in data.values() for value in values if not math.isfinite(value)
    )
    planning = json.loads(planning_path.read_text(encoding="utf-8"))
    metrics: dict[str, Any] = {
        "schema": "mosim.mworks.three_uav_open_blocks.metrics.v1",
        "source": "MWORKS_MCP",
        "model_name": "QuadrotorExperiments.PlanningScenarios.ThreeUavOpenBlocksReconfigurableFormationLinearMPC",
        "raw_result": str(raw_path.resolve()),
        "planning_result": str(planning_path.resolve()),
        "sample_count": len(times),
        "time_start_s": times[0],
        "time_end_s": times[-1],
        "nan_or_inf_count": non_finite_count,
        "thresholds": {
            "minimum_pair_distance_m": MIN_PAIR_DISTANCE_M,
            "minimum_collision_clearance_m": MIN_COLLISION_CLEARANCE_M,
            "planning_margin_m": PLANNING_MARGIN_M,
            "maximum_tracking_rmse_m": MAX_TRACKING_RMSE_M,
            "maximum_tracking_error_m": MAX_TRACKING_ERROR_M,
            "maximum_final_tracking_error_m": MAX_FINAL_TRACKING_ERROR_M,
        },
        "reference_schedule": planning["schedule"],
    }

    tracking_pass = True
    for index in range(1, 4):
        errors = data[f"uav{index}_tracking_error_m"]
        vehicle = {
            "tracking_rmse_m": rmse(errors),
            "tracking_max_m": max(errors),
            "tracking_final_m": errors[-1],
            "final_position_m": [data[f"uav{index}_{axis}_m"][-1] for axis in "xyz"],
            "final_reference_m": [data[f"uav{index}_ref_{axis}_m"][-1] for axis in "xyz"],
        }
        vehicle["accepted"] = (
            vehicle["tracking_rmse_m"] <= MAX_TRACKING_RMSE_M
            and vehicle["tracking_max_m"] <= MAX_TRACKING_ERROR_M
            and vehicle["tracking_final_m"] <= MAX_FINAL_TRACKING_ERROR_M
        )
        tracking_pass = tracking_pass and bool(vehicle["accepted"])
        metrics[f"uav{index}"] = vehicle

    pair_values = data["minimum_pair_distance_m"]
    clearance_values = data["clearance_lower_bound_m"]
    formation_values = data["formation_distance_error_m"]
    pair_index = min(range(len(times)), key=pair_values.__getitem__)
    clearance_index = min(range(len(times)), key=clearance_values.__getitem__)
    metrics.update({
        "minimum_actual_pair_distance_m": pair_values[pair_index],
        "minimum_actual_pair_distance_time_s": times[pair_index],
        "minimum_clearance_lower_bound_m": clearance_values[clearance_index],
        "minimum_clearance_lower_bound_time_s": times[clearance_index],
        "maximum_formation_distance_error_m": max(formation_values),
        "formation_distance_error_rmse_m": rmse(formation_values),
    })
    pair_pass = metrics["minimum_actual_pair_distance_m"] >= MIN_PAIR_DISTANCE_M
    collision_clearance_pass = metrics["minimum_clearance_lower_bound_m"] >= MIN_COLLISION_CLEARANCE_M
    planning_margin_preserved = metrics["minimum_clearance_lower_bound_m"] >= PLANNING_MARGIN_M
    accepted = non_finite_count == 0 and tracking_pass and pair_pass and collision_clearance_pass
    metrics["gates"] = {
        "finite_values": non_finite_count == 0,
        "tracking": tracking_pass,
        "pair_separation": pair_pass,
        "collision_clearance": collision_clearance_pass,
        "planning_margin_preserved": planning_margin_preserved,
    }
    metrics["accepted"] = accepted
    metrics["status"] = (
        "accepted" if accepted and planning_margin_preserved
        else "accepted_with_reduced_clearance_margin" if accepted
        else "blocked"
    )
    metrics["claim_boundary"] = (
        "Offline global A* plus EGO-smoothed references tracked by three MWORKS whole-aircraft "
        "Linear-MPC loops; this is not online replanning, unknown-environment exploration, or Gazebo evidence."
    )
    return metrics


def write_outputs(metrics: dict[str, Any], json_path: Path, csv_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        ("status", metrics["status"]),
        ("accepted", metrics["accepted"]),
        ("sample_count", metrics["sample_count"]),
        ("minimum_actual_pair_distance_m", metrics["minimum_actual_pair_distance_m"]),
        ("minimum_clearance_lower_bound_m", metrics["minimum_clearance_lower_bound_m"]),
        ("formation_distance_error_rmse_m", metrics["formation_distance_error_rmse_m"]),
    ]
    for index in range(1, 4):
        rows.extend([
            (f"uav{index}_tracking_rmse_m", metrics[f"uav{index}"]["tracking_rmse_m"]),
            (f"uav{index}_tracking_max_m", metrics[f"uav{index}"]["tracking_max_m"]),
            (f"uav{index}_tracking_final_m", metrics[f"uav{index}"]["tracking_final_m"]),
        ])
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["metric", "value"])
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--planning", type=Path, default=DEFAULT_PLANNING)
    parser.add_argument("--metrics-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--metrics-csv", type=Path, default=DEFAULT_CSV)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    metrics = audit(args.raw.resolve(), args.planning.resolve())
    write_outputs(metrics, args.metrics_json.resolve(), args.metrics_csv.resolve())
    print(json.dumps({
        "status": metrics["status"],
        "accepted": metrics["accepted"],
        "minimum_actual_pair_distance_m": metrics["minimum_actual_pair_distance_m"],
        "minimum_clearance_lower_bound_m": metrics["minimum_clearance_lower_bound_m"],
    }, indent=2))
    return 0 if metrics["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
