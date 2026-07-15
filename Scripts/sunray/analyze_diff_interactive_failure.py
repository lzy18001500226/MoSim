#!/usr/bin/env python3
"""Analyze a Goal4 Diff-Planner interactive failure window.

The mission gate can stop on a safety violation after a goal-switch or hold
phase. This script keeps the postmortem repeatable by summarizing the recorded
truth/odom/command/controller streams around the exact violation time.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any


CSV_FILES = {
    "truth": "truth.csv",
    "sunray_truth": "sunray_truth.csv",
    "odom": "odom.csv",
    "position_cmd": "position_cmd.csv",
    "planner_position_cmd_raw": "planner_position_cmd_raw.csv",
    "target_attitude": "target_attitude.csv",
    "debug_px4ctrl": "debug_px4ctrl.csv",
}


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"decode_error": str(exc), "path": str(path)}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def numeric_keys(rows: list[dict[str, str]]) -> list[str]:
    keys: set[str] = set()
    for row in rows[:1000]:
        for key, value in row.items():
            if finite_float(value) is not None:
                keys.add(key)
    return sorted(keys)


def row_time(row: dict[str, str]) -> float | None:
    return finite_float(row.get("t"))


def nearest_row(rows: list[dict[str, str]], t_ref: float) -> dict[str, Any] | None:
    best: dict[str, str] | None = None
    best_dt = float("inf")
    for row in rows:
        t = row_time(row)
        if t is None:
            continue
        dt = abs(t - t_ref)
        if dt < best_dt:
            best = row
            best_dt = dt
    if best is None:
        return None
    return normalize_row(best) | {"dt_to_ref_s": best_dt}


def normalize_row(row: dict[str, str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in row.items():
        number = finite_float(value)
        out[key] = number if number is not None else value
    if all(k in out for k in ("vx", "vy", "vz")):
        out["speed_mps"] = math.sqrt(float(out["vx"]) ** 2 + float(out["vy"]) ** 2 + float(out["vz"]) ** 2)
        out["abs_vz_mps"] = abs(float(out["vz"]))
    if all(k in out for k in ("roll", "pitch")):
        out["abs_roll_pitch_deg"] = math.degrees(max(abs(float(out["roll"])), abs(float(out["pitch"]))))
    if all(k in out for k in ("des_a_x", "des_a_y", "des_a_z")):
        out["des_a_xy_mps2"] = math.hypot(float(out["des_a_x"]), float(out["des_a_y"]))
        out["des_a_norm_mps2"] = math.sqrt(
            float(out["des_a_x"]) ** 2 + float(out["des_a_y"]) ** 2 + float(out["des_a_z"]) ** 2
        )
    return out


def window_rows(rows: list[dict[str, str]], t_ref: float, before_s: float, after_s: float) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    lo = t_ref - before_s
    hi = t_ref + after_s
    for row in rows:
        t = row_time(row)
        if t is None:
            continue
        if lo <= t <= hi:
            out.append(row)
    return out


def summarize_window(rows: list[dict[str, str]], t_ref: float, before_s: float, after_s: float) -> dict[str, Any]:
    subset = window_rows(rows, t_ref, before_s, after_s)
    summary: dict[str, Any] = {
        "samples": len(rows),
        "window_samples": len(subset),
        "nearest": nearest_row(rows, t_ref),
    }
    if not subset:
        return summary
    keys = numeric_keys(subset)
    extrema: dict[str, Any] = {}
    for key in keys:
        values = [finite_float(row.get(key)) for row in subset]
        nums = [float(value) for value in values if value is not None]
        if not nums:
            continue
        extrema[key] = {
            "min": min(nums),
            "max": max(nums),
            "mean": sum(nums) / len(nums),
        }
    derived: dict[str, Any] = {}
    speeds: list[float] = []
    abs_vzs: list[float] = []
    roll_pitch: list[float] = []
    des_a_xy: list[float] = []
    for row in subset:
        norm = normalize_row(row)
        if "speed_mps" in norm:
            speeds.append(float(norm["speed_mps"]))
        if "abs_vz_mps" in norm:
            abs_vzs.append(float(norm["abs_vz_mps"]))
        if "abs_roll_pitch_deg" in norm:
            roll_pitch.append(float(norm["abs_roll_pitch_deg"]))
        if "des_a_xy_mps2" in norm:
            des_a_xy.append(float(norm["des_a_xy_mps2"]))
    if speeds:
        derived["max_speed_mps"] = max(speeds)
    if abs_vzs:
        derived["max_abs_vz_mps"] = max(abs_vzs)
    if roll_pitch:
        derived["max_abs_roll_pitch_deg"] = max(roll_pitch)
    if des_a_xy:
        derived["max_des_a_xy_mps2"] = max(des_a_xy)
    summary["extrema"] = extrema
    summary["derived"] = derived
    return summary


def infer_failure(metric: dict[str, Any] | None, streams: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    violation = (metric or {}).get("flight_safety_violation") or {}
    blockers = (metric or {}).get("blockers") or []
    if violation:
        findings.append(f"Mission stopped on {blockers} at t={violation.get('t')}.")

    raw = streams.get("planner_position_cmd_raw", {}).get("extrema", {})
    cmd = streams.get("position_cmd", {}).get("extrema", {})
    debug = streams.get("debug_px4ctrl", {}).get("derived", {})
    truth = streams.get("truth", {}).get("derived", {})
    odom = streams.get("odom", {}).get("derived", {})

    raw_z = raw.get("z", {})
    cmd_z = cmd.get("z", {})
    if raw_z and cmd_z:
        if raw_z.get("min", 0.0) > 0.8 and raw_z.get("max", 9.0) < 1.5 and cmd_z.get("min", 0.0) > 0.8:
            findings.append("Planner/adapted PositionCommand Z stayed inside the hover envelope; this is not a raw Z dive.")
        else:
            findings.append("PositionCommand Z left the nominal hover envelope; inspect planner Z and adapter policy first.")

    max_des_a_xy = debug.get("max_des_a_xy_mps2")
    max_truth_rp = truth.get("max_abs_roll_pitch_deg")
    max_odom_rp = odom.get("max_abs_roll_pitch_deg")
    if max_des_a_xy is not None and max_des_a_xy > 5.0:
        findings.append(
            f"px4ctrl desired horizontal acceleration peaked at {max_des_a_xy:.3f} m/s^2 in the failure window."
        )
    if (max_truth_rp is not None and max_truth_rp > 40.0) or (max_odom_rp is not None and max_odom_rp > 40.0):
        findings.append("Failure is dominated by aggressive attitude/XY correction, with Z loss as a consequence.")

    adapter = load_json(Path(streams.get("_result_dir", "")) / "clicked_goal_adapter.json") if streams.get("_result_dir") else None
    last_goal = (adapter or {}).get("last_goal") or {}
    if last_goal.get("clamped_by_distance"):
        findings.append(
            "The latest interactive goal was distance-clamped; acceptance against the intermediate target can hide the original requested goal."
        )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--output-json", default="")
    parser.add_argument("--window-before-s", type=float, default=6.0)
    parser.add_argument("--window-after-s", type=float, default=2.0)
    parser.add_argument("--event-time", type=float, default=None)
    args = parser.parse_args()

    result_dir = Path(args.result_dir)
    metric = load_json(result_dir / "EGO_SINGLE_METRICS.json")
    violation = (metric or {}).get("flight_safety_violation") or {}
    event_time = args.event_time if args.event_time is not None else finite_float(violation.get("t"))
    if event_time is None:
        output = {
            "schema": "mosim.sunray_ros1.diff_interactive_failure_analysis.v1",
            "result_dir": str(result_dir),
            "status": "blocked",
            "blockers": ["event_time_missing"],
        }
    else:
        streams: dict[str, Any] = {"_result_dir": str(result_dir)}
        for name, filename in CSV_FILES.items():
            rows = read_csv_rows(result_dir / filename)
            streams[name] = summarize_window(rows, event_time, args.window_before_s, args.window_after_s)
        output = {
            "schema": "mosim.sunray_ros1.diff_interactive_failure_analysis.v1",
            "result_dir": str(result_dir),
            "event_time_s": event_time,
            "window": {
                "before_s": args.window_before_s,
                "after_s": args.window_after_s,
            },
            "mission_status": (metric or {}).get("status"),
            "mission_blockers": (metric or {}).get("blockers"),
            "flight_safety_violation": violation,
            "clicked_goal_adapter": load_json(result_dir / "clicked_goal_adapter.json"),
            "position_cmd_safety_adapter": load_json(result_dir / "position_cmd_safety_adapter.json"),
            "interactive_probe": load_json(result_dir / "DIFF_INTERACTIVE_GOAL_SWITCH_CHAIN_PROBE.json"),
            "streams": {key: value for key, value in streams.items() if not key.startswith("_")},
            "findings": infer_failure(metric, streams),
            "status": "passed",
        }

    output_json = Path(args.output_json) if args.output_json else result_dir / "DIFF_INTERACTIVE_FAILURE_ANALYSIS.json"
    output_json.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(output_json)
    return 0 if output.get("status") == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
