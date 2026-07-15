#!/usr/bin/env python3
"""Audit a Goal4 Diff-Planner single-UAV run for Z-axis safety failures.

The runner records both the raw Diff/traj_server PositionCommand stream and
the px4ctrl-facing stream after the MoSim safety adapter. This audit treats
the raw planner stream as the authority for planner correctness: downstream
altitude clamping is diagnostic protection, not a valid planner fix.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists() or path.stat().st_size == 0:
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"_decode_error": True, "_path": str(path)}


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


def series(rows: list[dict[str, str]], key: str) -> list[float]:
    out: list[float] = []
    for row in rows:
        value = finite_float(row.get(key))
        if value is not None:
            out.append(value)
    return out


def xyz(row: dict[str, str]) -> list[float] | None:
    values = [finite_float(row.get(axis)) for axis in ("x", "y", "z")]
    if any(value is None for value in values):
        return None
    return [float(values[0]), float(values[1]), float(values[2])]


def motion_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    if not rows:
        return {"samples": 0}
    xs = series(rows, "x")
    ys = series(rows, "y")
    zs = series(rows, "z")
    first_xyz = xyz(rows[0])
    last_xyz = xyz(rows[-1])
    summary: dict[str, Any] = {
        "samples": len(rows),
        "first_xyz": first_xyz,
        "last_xyz": last_xyz,
    }
    for key, values in (("x", xs), ("y", ys), ("z", zs)):
        if values:
            summary[f"min_{key}"] = min(values)
            summary[f"max_{key}"] = max(values)
            summary[f"{key}_range_m"] = max(values) - min(values)
    if first_xyz is not None and last_xyz is not None:
        summary["first_to_last_m"] = math.dist(first_xyz, last_xyz)
    return summary


def continuity_summary(
    rows: list[dict[str, str]],
    max_jump_m: float,
    max_jump_speed_mps: float,
    speed_gate_min_dt_s: float,
) -> dict[str, Any]:
    if len(rows) < 2:
        return {
            "samples": len(rows),
            "thresholds": {
                "max_jump_m": max_jump_m,
                "max_jump_speed_mps": max_jump_speed_mps,
                "speed_gate_min_dt_s": speed_gate_min_dt_s,
            },
            "violation_count": 0,
        }
    max_jump = 0.0
    max_xy_jump = 0.0
    max_z_jump = 0.0
    max_jump_speed = 0.0
    max_pair: dict[str, Any] | None = None
    violation_count = 0
    for prev, curr in zip(rows, rows[1:]):
        prev_xyz = xyz(prev)
        curr_xyz = xyz(curr)
        prev_t = finite_float(prev.get("t"))
        curr_t = finite_float(curr.get("t"))
        if prev_xyz is None or curr_xyz is None or prev_t is None or curr_t is None:
            continue
        dt = curr_t - prev_t
        if dt <= 1e-6:
            continue
        dx = curr_xyz[0] - prev_xyz[0]
        dy = curr_xyz[1] - prev_xyz[1]
        dz = curr_xyz[2] - prev_xyz[2]
        jump = math.sqrt(dx * dx + dy * dy + dz * dz)
        xy_jump = math.hypot(dx, dy)
        z_jump = abs(dz)
        jump_speed = jump / dt
        if jump > max_jump:
            max_jump = jump
            max_pair = {
                "t_prev": prev_t,
                "t_curr": curr_t,
                "dt_s": dt,
                "jump_m": jump,
                "xy_jump_m": xy_jump,
                "z_jump_m": z_jump,
                "jump_speed_mps": jump_speed,
                "previous_xyz": prev_xyz,
                "current_xyz": curr_xyz,
                "previous_phase": prev.get("phase"),
                "current_phase": curr.get("phase"),
            }
        max_xy_jump = max(max_xy_jump, xy_jump)
        max_z_jump = max(max_z_jump, z_jump)
        max_jump_speed = max(max_jump_speed, jump_speed)
        violates_distance = max_jump_m > 0.0 and jump > max_jump_m
        violates_speed = (
            max_jump_speed_mps > 0.0
            and dt > speed_gate_min_dt_s
            and jump_speed > max_jump_speed_mps
        )
        if violates_distance or violates_speed:
            violation_count += 1
    return {
        "samples": len(rows),
        "thresholds": {
            "max_jump_m": max_jump_m,
            "max_jump_speed_mps": max_jump_speed_mps,
            "speed_gate_min_dt_s": speed_gate_min_dt_s,
        },
        "max_jump_m": max_jump,
        "max_xy_jump_m": max_xy_jump,
        "max_z_jump_m": max_z_jump,
        "max_jump_speed_mps": max_jump_speed,
        "max_pair": max_pair,
        "violation_count": violation_count,
        "violates_jump_gate": violation_count > 0,
    }


def phase_peak_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for row in rows:
        phase = row.get("phase") or "unknown"
        z = finite_float(row.get("z"))
        vx = finite_float(row.get("vx"))
        vy = finite_float(row.get("vy"))
        vz = finite_float(row.get("vz"))
        roll = finite_float(row.get("roll"))
        pitch = finite_float(row.get("pitch"))
        if None in (z, vx, vy, vz, roll, pitch):
            continue
        item = out.setdefault(
            phase,
            {
                "samples": 0,
                "min_z_m": float("inf"),
                "max_z_m": float("-inf"),
                "max_speed_mps": 0.0,
                "max_abs_vz_mps": 0.0,
                "max_abs_roll_pitch_deg": 0.0,
            },
        )
        item["samples"] += 1
        speed = math.sqrt(float(vx) * float(vx) + float(vy) * float(vy) + float(vz) * float(vz))
        item["min_z_m"] = min(item["min_z_m"], float(z))
        item["max_z_m"] = max(item["max_z_m"], float(z))
        item["max_speed_mps"] = max(item["max_speed_mps"], speed)
        item["max_abs_vz_mps"] = max(item["max_abs_vz_mps"], abs(float(vz)))
        item["max_abs_roll_pitch_deg"] = max(
            item["max_abs_roll_pitch_deg"],
            math.degrees(max(abs(float(roll)), abs(float(pitch)))),
        )
    return out


def target_error_summary(rows: list[dict[str, str]], target: tuple[float, float, float] | None) -> dict[str, Any] | None:
    if not rows or target is None:
        return None
    xyz_err: list[float] = []
    xy_err: list[float] = []
    z_err: list[float] = []
    for row in rows:
        point = xyz(row)
        if point is None:
            continue
        xyz_err.append(math.dist(point, target))
        xy_err.append(math.dist(point[:2], target[:2]))
        z_err.append(point[2] - target[2])
    if not xyz_err:
        return None
    return {
        "samples": len(xyz_err),
        "min_xyz_m": min(xyz_err),
        "end_xyz_m": xyz_err[-1],
        "rmse_xyz_m": math.sqrt(sum(e * e for e in xyz_err) / len(xyz_err)),
        "min_xy_m": min(xy_err),
        "end_xy_m": xy_err[-1],
        "max_abs_z_error_m": max(abs(e) for e in z_err),
        "end_z_error_m": z_err[-1],
    }


ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]|\x1b\].*?\x07")


def log_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"exists": False}
    text = ANSI_RE.sub("", path.read_text(encoding="utf-8", errors="replace"))
    lines = text.splitlines()
    runtime_lines = [line for line in lines if not re.match(r"\s*\*\s+/", line)]
    actual_emergency = [
        line
        for line in runtime_lines
        if re.search(r"Emergency stop|EMERGENCY_STOP|STUCK_DETECT|EMERGENCY_EXIT", line, re.IGNORECASE)
    ]
    stuck_events = [
        line
        for line in runtime_lines
        if re.search(r"Drone stuck|\bSTUCK_DETECT\b", line, re.IGNORECASE)
    ]
    success_no = [line for line in runtime_lines if re.search(r"\bSuccess=no\b", line)]
    fatal_events = [
        line
        for line in runtime_lines
        if re.search(
            r"boost::wrapexcept<boost::lock_error>|terminate called|Aborted|core dumped|process has died|Traceback|segmentation fault",
            line,
            re.IGNORECASE,
        )
    ]
    interesting = [
        line
        for line in lines
        if re.search(
            r"Emergency stop|EMERGENCY_STOP|STUCK_DETECT|EMERGENCY_EXIT|Drone stuck|Success=no|fail|error|warn|received goal|replan|boost::wrapexcept|terminate called|Aborted|core dumped|process has died|Traceback|segmentation fault",
            line,
            re.IGNORECASE,
        )
    ]
    return {
        "exists": True,
        "emergency_count": len(actual_emergency),
        "stuck_count": len(stuck_events),
        "success_no_count": len(success_no),
        "fatal_count": len(fatal_events),
        "received_goal_count": len([line for line in lines if "Received goal" in line]),
        "replan_count": len([line for line in lines if "Replan" in line or "REPLAN_TRAJ" in line]),
        "fatal_tail": fatal_events[-20:],
        "interesting_tail": interesting[-40:],
    }


def target_from_manifest_or_metrics(manifest: dict[str, Any] | None, metrics: dict[str, Any] | None) -> tuple[float, float, float] | None:
    for source in (manifest, metrics):
        if not source:
            continue
        target = source.get("target")
        if not isinstance(target, dict):
            continue
        x = finite_float(target.get("x"))
        y = finite_float(target.get("y"))
        z = finite_float(target.get("z"))
        if x is not None and y is not None and z is not None:
            return (x, y, z)
    return None


def derive_thresholds(args: argparse.Namespace, manifest: dict[str, Any] | None, target: tuple[float, float, float] | None) -> dict[str, float]:
    raw_min_z = args.raw_min_z
    raw_max_z = args.raw_max_z
    adapter_min_z = None
    adapter_max_z = None
    if manifest:
        adapter = manifest.get("position_cmd_safety_adapter")
        if isinstance(adapter, dict):
            adapter_min_z = finite_float(adapter.get("min_z"))
            adapter_max_z = finite_float(adapter.get("max_z"))
    if raw_min_z is None:
        raw_min_z = (adapter_min_z - 0.10) if adapter_min_z is not None else 0.75
    if raw_max_z is None:
        raw_max_z = (adapter_max_z + 0.10) if adapter_max_z is not None else 1.45
    target_z_tol = args.target_z_tol
    if target_z_tol is None:
        target_z_tol = 0.35 if target is not None else 0.50
    return {
        "raw_min_z": float(raw_min_z),
        "raw_max_z": float(raw_max_z),
        "target_z_tol": float(target_z_tol),
        "max_final_target_error_m": float(args.max_final_target_error_m),
        "max_replan_failures": float(args.max_replan_failures),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--output-json", default="")
    parser.add_argument("--raw-min-z", type=float, default=None)
    parser.add_argument("--raw-max-z", type=float, default=None)
    parser.add_argument("--target-z-tol", type=float, default=None)
    parser.add_argument("--max-final-target-error-m", type=float, default=0.45)
    parser.add_argument("--max-replan-failures", type=int, default=0)
    parser.add_argument("--max-position-cmd-jump-m", type=float, default=0.50)
    parser.add_argument("--max-position-cmd-speed-mps", type=float, default=3.0)
    parser.add_argument("--position-cmd-speed-gate-min-dt-s", type=float, default=0.05)
    parser.add_argument("--max-execute-truth-z-m", type=float, default=1.60)
    parser.add_argument("--max-execute-odom-z-m", type=float, default=1.60)
    parser.add_argument("--max-execute-roll-pitch-deg", type=float, default=45.0)
    parser.add_argument("--allow-review-hold", action="store_true")
    args = parser.parse_args()

    result_dir = Path(args.result_dir)
    output_json = Path(args.output_json) if args.output_json else result_dir / "DIFF_SINGLE_Z_AUDIT.json"

    manifest = load_json(result_dir / "RUN_MANIFEST.json")
    metrics = load_json(result_dir / "EGO_SINGLE_METRICS.json")
    adapter = load_json(result_dir / "position_cmd_safety_adapter.json")
    raw_cmd_rows = read_csv_rows(result_dir / "planner_position_cmd_raw.csv")
    adapted_cmd_rows = read_csv_rows(result_dir / "position_cmd.csv")
    odom_rows = read_csv_rows(result_dir / "odom.csv")
    truth_rows = read_csv_rows(result_dir / "truth.csv")
    log = log_summary(result_dir / "ego_single_px4ctrl_goal4.log")

    target = target_from_manifest_or_metrics(manifest, metrics)
    thresholds = derive_thresholds(args, manifest, target)
    blockers: list[str] = []
    warnings: list[str] = []
    pre_diff_gate = metrics.get("pre_diff_gate") if isinstance(metrics, dict) else None
    pre_diff_blocked = False
    pre_diff_snapshot = None
    if isinstance(pre_diff_gate, dict):
        pre_diff_snapshot = pre_diff_gate.get("last_snapshot")

    metric_status = metrics.get("status") if isinstance(metrics, dict) else None
    metric_blockers = metrics.get("blockers") if isinstance(metrics, dict) else None
    accepted_statuses = {"passed", "interactive_passed"}
    successful_interactive = metric_status == "interactive_passed"
    if isinstance(metric_blockers, list) and "pre_diff_hover_not_stable" in metric_blockers:
        pre_diff_blocked = True
        blockers.append("pre_diff_hover_not_stable")
    if metric_status == "review_hold" and not args.allow_review_hold:
        blockers.append("mission_status_review_hold_not_acceptance")
    elif metric_status not in (None, *accepted_statuses, "review_hold"):
        blockers.append(f"mission_status_{metric_status}")
    if isinstance(metric_blockers, list) and metric_blockers:
        blockers.append("mission_metrics_blockers_present")

    raw_z = series(raw_cmd_rows, "z")
    raw_cmd_continuity = continuity_summary(
        raw_cmd_rows,
        args.max_position_cmd_jump_m,
        args.max_position_cmd_speed_mps,
        args.position_cmd_speed_gate_min_dt_s,
    )
    adapted_cmd_continuity = continuity_summary(
        adapted_cmd_rows,
        args.max_position_cmd_jump_m,
        args.max_position_cmd_speed_mps,
        args.position_cmd_speed_gate_min_dt_s,
    )
    if pre_diff_blocked:
        warnings.append("planner_not_triggered_due_to_pre_diff_gate")
    elif not raw_cmd_rows:
        blockers.append("raw_planner_position_cmd_missing")
    elif raw_z:
        if min(raw_z) < thresholds["raw_min_z"]:
            blockers.append("raw_planner_z_below_min")
        if max(raw_z) > thresholds["raw_max_z"]:
            blockers.append("raw_planner_z_above_max")
        if target is not None and max(abs(z - target[2]) for z in raw_z) > thresholds["target_z_tol"]:
            blockers.append("raw_planner_z_far_from_target_height")
    else:
        blockers.append("raw_planner_z_unreadable")
    if raw_cmd_continuity.get("violates_jump_gate"):
        blockers.append("raw_planner_position_cmd_discontinuous")
    if adapted_cmd_continuity.get("violates_jump_gate"):
        blockers.append("adapted_position_cmd_discontinuous")

    if isinstance(adapter, dict):
        low_clamps = int(adapter.get("clamped_low_count") or 0)
        high_clamps = int(adapter.get("clamped_high_count") or 0)
        hold_count = int(adapter.get("hold_publish_count") or 0)
        raw_count = int(adapter.get("raw_count") or 0)
        if low_clamps > 0 or high_clamps > 0:
            blockers.append("adapter_clamped_raw_planner_z")
        if int(adapter.get("jump_rejected_count") or 0) > 0:
            blockers.append("adapter_rejected_raw_planner_jump")
        if raw_count > 0 and hold_count > raw_count * 5:
            warnings.append("adapter_hold_published_long_after_raw_stream")
    elif manifest and manifest.get("planner_variant") == "diff_planner":
        warnings.append("position_cmd_safety_adapter_diagnostics_missing")

    if log.get("emergency_count", 0) > 0:
        blockers.append("planner_log_emergency_stop")
    if log.get("stuck_count", 0) > 0:
        blockers.append("planner_log_stuck_detected")
    if log.get("success_no_count", 0) > args.max_replan_failures:
        if successful_interactive:
            warnings.append("planner_log_replan_failure_seen_but_interactive_chain_passed")
        else:
            blockers.append("planner_log_replan_failure")
    fatal_count = int(log.get("fatal_count", 0) or 0)
    if fatal_count > 0:
        land_metrics = metrics.get("land") if isinstance(metrics, dict) else None
        landed = isinstance(land_metrics, dict) and land_metrics.get("landed_by_truth") is True
        if metric_status in accepted_statuses and landed:
            warnings.append("planner_log_fatal_seen_after_passed_landing_or_shutdown")
        else:
            blockers.append("planner_log_fatal_runtime_event")

    odom_target_error = target_error_summary(odom_rows, target)
    truth_target_error = target_error_summary(truth_rows, target)
    odom_phase_peaks = phase_peak_summary(odom_rows)
    truth_phase_peaks = phase_peak_summary(truth_rows)
    execute_odom = odom_phase_peaks.get("ego_execute")
    execute_truth = truth_phase_peaks.get("ego_execute")
    if isinstance(execute_odom, dict):
        if finite_float(execute_odom.get("max_z_m")) is not None and float(execute_odom["max_z_m"]) > args.max_execute_odom_z_m:
            blockers.append("execute_odom_z_peak_above_gate")
        if (
            finite_float(execute_odom.get("max_abs_roll_pitch_deg")) is not None
            and float(execute_odom["max_abs_roll_pitch_deg"]) > args.max_execute_roll_pitch_deg
        ):
            blockers.append("execute_odom_roll_pitch_peak_above_gate")
    if isinstance(execute_truth, dict):
        if finite_float(execute_truth.get("max_z_m")) is not None and float(execute_truth["max_z_m"]) > args.max_execute_truth_z_m:
            blockers.append("execute_truth_z_peak_above_gate")
        if (
            finite_float(execute_truth.get("max_abs_roll_pitch_deg")) is not None
            and float(execute_truth["max_abs_roll_pitch_deg"]) > args.max_execute_roll_pitch_deg
        ):
            blockers.append("execute_truth_roll_pitch_peak_above_gate")
    if isinstance(metrics, dict) and metric_status == "passed":
        target_hold = metrics.get("target_hold")
        if isinstance(target_hold, dict):
            if target_hold.get("reached") is not True:
                blockers.append("target_hold_not_reached")
            hold_duration = finite_float(target_hold.get("duration_s"))
            required_hold = finite_float(target_hold.get("required_s"))
            if hold_duration is None or required_hold is None or hold_duration + 1e-6 < required_hold:
                blockers.append("target_hold_duration_below_gate")
            end_snapshot = target_hold.get("end_snapshot")
            end_error = None
            if isinstance(end_snapshot, dict):
                end_error = finite_float(end_snapshot.get("error_xyz_m"))
            if end_error is None:
                blockers.append("target_hold_end_error_missing")
            elif end_error > thresholds["max_final_target_error_m"]:
                blockers.append("target_hold_end_error_above_gate")
        else:
            warnings.append("target_hold_metrics_missing_legacy_fallback")
            execute_summary = metrics.get("target_error_summary", {}).get("ego_execute")
            if isinstance(execute_summary, dict):
                execute_end = finite_float(execute_summary.get("end_xyz_m"))
                execute_min = finite_float(execute_summary.get("min_xyz_m"))
                if execute_end is not None and execute_end > thresholds["max_final_target_error_m"]:
                    blockers.append("execute_end_target_error_above_gate")
                if execute_min is not None and execute_min > thresholds["max_final_target_error_m"]:
                    blockers.append("execute_never_reached_target_gate")
            else:
                blockers.append("execute_target_error_summary_missing")
    elif isinstance(metrics, dict) and successful_interactive:
        forwarded_goal_count = int(metrics.get("forwarded_goal_count") or 0)
        if forwarded_goal_count <= 0:
            blockers.append("interactive_forwarded_goal_count_missing")
        interactive_goals = metrics.get("interactive_goals")
        if not isinstance(interactive_goals, dict) or not interactive_goals:
            blockers.append("interactive_goal_metrics_missing")
        else:
            for goal_key, goal_metrics in sorted(interactive_goals.items(), key=lambda item: str(item[0])):
                if not isinstance(goal_metrics, dict):
                    blockers.append(f"interactive_goal_{goal_key}_metrics_invalid")
                    continue
                snapshot = goal_metrics.get("last_snapshot")
                if not isinstance(snapshot, dict):
                    blockers.append(f"interactive_goal_{goal_key}_snapshot_missing")
                    continue
                err = finite_float(snapshot.get("error_xyz_m"))
                z_err = finite_float(snapshot.get("error_z_m"))
                if err is None:
                    blockers.append(f"interactive_goal_{goal_key}_error_missing")
                elif err > thresholds["max_final_target_error_m"]:
                    blockers.append(f"interactive_goal_{goal_key}_error_above_gate")
                if z_err is None:
                    blockers.append(f"interactive_goal_{goal_key}_z_error_missing")
                elif abs(z_err) > thresholds["target_z_tol"]:
                    blockers.append(f"interactive_goal_{goal_key}_z_error_above_gate")
                handoff = goal_metrics.get("handoff")
                handoff_ok = False
                if isinstance(handoff, dict):
                    handoff_mode = handoff.get("mode")
                    handoff_ok = handoff.get("adapter_disabled") is True or handoff_mode == "adapter_hold"
                if not handoff_ok:
                    blockers.append(f"interactive_goal_{goal_key}_handoff_missing")

    audit = {
        "schema": "mosim.sunray_ros1.diff_single_z_audit.v1",
        "status": "failed" if blockers else "passed",
        "result_dir": str(result_dir),
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "thresholds": thresholds,
        "target": list(target) if target is not None else None,
        "mission_metrics": {
            "status": metric_status,
            "blockers": metric_blockers if isinstance(metric_blockers, list) else [],
            "final_target_error_m": metrics.get("final_target_error_m") if isinstance(metrics, dict) else None,
            "post_land_final_target_error_m": metrics.get("post_land_final_target_error_m") if isinstance(metrics, dict) else None,
            "execute_target_error_m": metrics.get("execute_target_error_m") if isinstance(metrics, dict) else None,
            "target_hold": metrics.get("target_hold") if isinstance(metrics, dict) else None,
            "land": metrics.get("land") if isinstance(metrics, dict) else None,
        },
        "pre_diff_gate": {
            "blocked_before_planner": pre_diff_blocked,
            "snapshot": pre_diff_snapshot,
            "history_tail": pre_diff_gate.get("history_tail") if isinstance(pre_diff_gate, dict) else None,
        },
        "raw_planner_position_cmd": motion_summary(raw_cmd_rows),
        "adapted_position_cmd": motion_summary(adapted_cmd_rows),
        "raw_planner_position_cmd_continuity": raw_cmd_continuity,
        "adapted_position_cmd_continuity": adapted_cmd_continuity,
        "odom": {
            "motion": motion_summary(odom_rows),
            "target_error": odom_target_error,
            "phase_peaks": odom_phase_peaks,
        },
        "truth": {
            "motion": motion_summary(truth_rows),
            "target_error": truth_target_error,
            "phase_peaks": truth_phase_peaks,
        },
        "position_cmd_safety_adapter": adapter,
        "planner_log": log,
        "claim_boundary": (
            "Diff-Planner acceptance requires the raw planner/traj_server PositionCommand "
            "Z trajectory to stay in the legal flight envelope; downstream clamping is a "
            "diagnostic failsafe and cannot convert an invalid planner trajectory into a pass."
        ),
    }

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps({"status": audit["status"], "blockers": audit["blockers"], "output_json": str(output_json)}, indent=2))
    return 20 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
