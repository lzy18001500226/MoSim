#!/usr/bin/env python3
"""Align RACER attitude peaks with odometry, command, and px4ctrl telemetry."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def read_phase(path: Path, phase: str) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [row for row in csv.DictReader(handle) if row.get("phase") == phase]


def nearest(rows: list[dict[str, str]], event_t: float) -> dict[str, str] | None:
    return min(rows, key=lambda row: abs(float(row["t"]) - event_t)) if rows else None


def horizontal_norm(row: dict[str, str], x: str, y: str) -> float:
    return math.hypot(float(row[x]), float(row[y]))


def vehicle_report(run_dir: Path, uid: int, phase: str, attitude_gate_deg: float) -> dict:
    truth = read_phase(run_dir / f"uav{uid}_truth.csv", phase)
    odom = read_phase(run_dir / f"uav{uid}_odom.csv", phase)
    command = read_phase(run_dir / f"uav{uid}_position_cmd.csv", phase)
    raw_command = read_phase(run_dir / f"uav{uid}_raw_position_cmd.csv", phase)
    debug = read_phase(run_dir / f"uav{uid}_debug_px4ctrl.csv", phase)
    if not truth:
        raise ValueError(f"uav{uid} has no truth rows in phase {phase}")

    def attitude_deg(row: dict[str, str]) -> float:
        return math.degrees(max(abs(float(row["roll"])), abs(float(row["pitch"]))))

    peak = max(truth, key=attitude_deg)
    event_t = float(peak["t"])
    aligned_odom = nearest(odom, event_t)
    aligned_command = nearest(command, event_t)
    aligned_raw = nearest(raw_command, event_t)
    aligned_debug = nearest(debug, event_t)
    above = [row for row in truth if attitude_deg(row) > attitude_gate_deg]

    report = {
        "uav_id": uid,
        "phase": phase,
        "event_t": event_t,
        "peak_abs_roll_pitch_deg": attitude_deg(peak),
        "roll_deg": math.degrees(float(peak["roll"])),
        "pitch_deg": math.degrees(float(peak["pitch"])),
        "truth_speed_mps": math.sqrt(
            float(peak["vx"]) ** 2 + float(peak["vy"]) ** 2 + float(peak["vz"]) ** 2
        ),
        "samples_above_gate": len(above),
        "time_above_gate_span_s": (
            0.0 if not above else float(above[-1]["t"]) - float(above[0]["t"])
        ),
    }
    if aligned_odom and aligned_command:
        position_error_xy = math.hypot(
            float(aligned_command["x"]) - float(aligned_odom["x"]),
            float(aligned_command["y"]) - float(aligned_odom["y"]),
        )
        velocity_error_xy = math.hypot(
            float(aligned_command["vx"]) - float(aligned_odom["vx"]),
            float(aligned_command["vy"]) - float(aligned_odom["vy"]),
        )
        report["aligned_tracking"] = {
            "odom_dt_s": float(aligned_odom["t"]) - event_t,
            "command_dt_s": float(aligned_command["t"]) - event_t,
            "position_error_xy_m": position_error_xy,
            "velocity_error_xy_mps": velocity_error_xy,
            "odom_velocity_xy_mps": [float(aligned_odom["vx"]), float(aligned_odom["vy"])],
            "command_velocity_xy_mps": [
                float(aligned_command["vx"]),
                float(aligned_command["vy"]),
            ],
            "command_acceleration_xy_mps2": horizontal_norm(aligned_command, "ax", "ay"),
        }
    if aligned_raw:
        report["aligned_raw_command"] = {
            "dt_s": float(aligned_raw["t"]) - event_t,
            "velocity_xy_mps": horizontal_norm(aligned_raw, "vx", "vy"),
            "acceleration_xy_mps2": horizontal_norm(aligned_raw, "ax", "ay"),
        }
    if aligned_debug:
        report["aligned_px4ctrl"] = {
            "dt_s": float(aligned_debug["t"]) - event_t,
            "desired_acceleration_xy_mps2": horizontal_norm(
                aligned_debug, "des_a_x", "des_a_y"
            ),
            "desired_acceleration_xyz_mps2": math.sqrt(
                float(aligned_debug["des_a_x"]) ** 2
                + float(aligned_debug["des_a_y"]) ** 2
                + float(aligned_debug["des_a_z"]) ** 2
            ),
        }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--uav-num", type=int, default=3)
    parser.add_argument("--phase", default="ego_execute")
    parser.add_argument("--attitude-gate-deg", type=float, default=45.0)
    args = parser.parse_args()

    vehicles = [
        vehicle_report(args.run_dir, uid, args.phase, args.attitude_gate_deg)
        for uid in range(1, args.uav_num + 1)
    ]
    report = {
        "schema": "mosim.racer.attitude_event_alignment.v1",
        "source_run": str(args.run_dir),
        "attitude_gate_deg": args.attitude_gate_deg,
        "status": (
            "blocked"
            if any(item["peak_abs_roll_pitch_deg"] > args.attitude_gate_deg for item in vehicles)
            else "passed"
        ),
        "vehicles": vehicles,
        "claim_boundary": (
            "Nearest-sample alignment diagnoses recorded command and controller demand around each "
            "truth-attitude peak; it does not prove causality or replace a live regression gate."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
