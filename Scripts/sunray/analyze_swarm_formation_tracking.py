#!/usr/bin/env python3
"""Gate three-UAV formation tracking from synchronized Gazebo truth CSVs."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def read_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [row for row in csv.DictReader(handle) if row.get("phase") == "ego_execute"]


def nearest_row(rows: list[dict], t: float, start: int) -> tuple[dict | None, int]:
    while start + 1 < len(rows) and abs(float(rows[start + 1]["t"]) - t) <= abs(float(rows[start]["t"]) - t):
        start += 1
    return (rows[start] if rows else None), start


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--output", default="")
    parser.add_argument("--sync-tolerance-s", type=float, default=0.08)
    parser.add_argument("--max-rmse-m", type=float, default=0.35)
    parser.add_argument("--max-peak-error-m", type=float, default=0.80)
    parser.add_argument("--min-inter-uav-distance-m", type=float, default=1.0)
    parser.add_argument("--max-roll-pitch-deg", type=float, default=45.0)
    parser.add_argument("--min-synchronized-samples", type=int, default=30)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_dir = Path(args.run).resolve()
    scenario_path = Path(args.scenario).resolve()
    output_path = Path(args.output).resolve() if args.output else run_dir / "SWARM_FORMATION_TRACKING_GATE.json"
    metrics = json.loads((run_dir / "EGO_SWARM_METRICS.json").read_text(encoding="utf-8"))
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))
    targets = {
        uid: tuple(float(metrics["per_uav"][str(uid)]["target"][axis]) for axis in ("x", "y", "z"))
        for uid in (1, 2, 3)
    }
    rows = {uid: read_rows(run_dir / f"uav{uid}_truth.csv") for uid in (1, 2, 3)}
    indices = {2: 0, 3: 0}
    errors: list[float] = []
    pair_errors: dict[str, list[float]] = {"1-2": [], "1-3": [], "2-3": []}
    for row1 in rows[1]:
        t = float(row1["t"])
        matched = {1: row1}
        valid = True
        for uid in (2, 3):
            row, indices[uid] = nearest_row(rows[uid], t, indices[uid])
            if row is None or abs(float(row["t"]) - t) > args.sync_tolerance_s:
                valid = False
                break
            matched[uid] = row
        if not valid:
            continue
        for uid_a, uid_b in ((1, 2), (1, 3), (2, 3)):
            actual = tuple(float(matched[uid_b][axis]) - float(matched[uid_a][axis]) for axis in ("x", "y", "z"))
            expected = tuple(targets[uid_b][axis] - targets[uid_a][axis] for axis in range(3))
            error = math.dist(actual, expected)
            errors.append(error)
            pair_errors[f"{uid_a}-{uid_b}"].append(error)

    rmse = math.sqrt(sum(value * value for value in errors) / len(errors)) if errors else None
    peak = max(errors) if errors else None
    synchronized_samples = len(errors) // 3
    min_inter_uav_distance = metrics.get("min_inter_uav_distance_m")
    execute_attitude_peaks = {
        str(uid): metrics.get("per_uav", {})
        .get(str(uid), {})
        .get("phase_peak_summary", {})
        .get("truth", {})
        .get("ego_execute", {})
        .get("max_abs_roll_pitch_deg")
        for uid in (1, 2, 3)
    }
    emergency_hold_count = (
        metrics.get("inter_uav_emergency_hold", {}).get("trigger_count", 0)
        if isinstance(metrics.get("inter_uav_emergency_hold"), dict)
        else 0
    )
    blockers = []
    if metrics.get("status") != "passed":
        blockers.append("backend_mission_not_passed")
    if not scenario.get("obstacle_crossing_contract", {}).get("direct_center_segment_blocked"):
        blockers.append("scenario_does_not_require_obstacle_detour")
    if synchronized_samples < args.min_synchronized_samples:
        blockers.append("formation_sample_count_below_gate")
    if rmse is None or rmse > args.max_rmse_m:
        blockers.append("formation_rmse_above_gate")
    if peak is None or peak > args.max_peak_error_m:
        blockers.append("formation_peak_error_above_gate")
    if min_inter_uav_distance is None or min_inter_uav_distance < args.min_inter_uav_distance_m:
        blockers.append("inter_uav_distance_below_gate")
    if any(value is None or value > args.max_roll_pitch_deg for value in execute_attitude_peaks.values()):
        blockers.append("execute_truth_roll_pitch_above_gate")
    if emergency_hold_count != 0:
        blockers.append("inter_uav_emergency_hold_triggered")
    packet = {
        "schema": "mosim.sunray_ros1.swarm_formation_tracking_gate.v1",
        "status": "passed" if not blockers else "blocked",
        "blockers": blockers,
        "backend_status": metrics.get("status"),
        "synchronized_samples": synchronized_samples,
        "formation_error": {
            "rmse_m": rmse,
            "peak_m": peak,
            "threshold_rmse_m": args.max_rmse_m,
            "threshold_peak_m": args.max_peak_error_m,
            "per_pair": {
                pair: {
                    "samples": len(values),
                    "rmse_m": math.sqrt(sum(value * value for value in values) / len(values)) if values else None,
                    "peak_m": max(values) if values else None,
                }
                for pair, values in pair_errors.items()
            },
        },
        "minimum_inter_uav_distance_m": min_inter_uav_distance,
        "minimum_inter_uav_distance_threshold_m": args.min_inter_uav_distance_m,
        "execute_truth_max_abs_roll_pitch_deg": execute_attitude_peaks,
        "execute_truth_max_abs_roll_pitch_threshold_deg": args.max_roll_pitch_deg,
        "inter_uav_emergency_hold_trigger_count": emergency_hold_count,
        "scenario": str(scenario_path),
        "claim_boundary": "Pass requires the normal backend mission gate plus synchronized Gazebo-truth formation error; static collision truth only proves that the direct center segment intersects an obstacle proxy.",
    }
    output_path.write_text(json.dumps(packet, indent=2), encoding="utf-8")
    print(output_path)
    raise SystemExit(0 if not blockers else 1)


if __name__ == "__main__":
    main()
