#!/usr/bin/env python3
"""Evaluate a bounded Gazebo truth-feedback hover-hold closed-loop smoke run.

This gate checks that the single-UAV runtime chain executed with feedback:
Gazebo truth -> hover-hold ControllerOutput -> adapter -> Gazebo actuators ->
Gazebo truth response. It is still a pre-acceptance gate, not a competition
controller-performance result.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        if isinstance(data, dict):
            rows.append(data)
    return rows


def finite_position(row: dict[str, Any]) -> list[float] | None:
    value = row.get("position_m")
    if not isinstance(value, list) or len(value) != 3:
        return None
    try:
        result = [float(value[0]), float(value[1]), float(value[2])]
    except (TypeError, ValueError):
        return None
    return result if all(math.isfinite(item) for item in result) else None


def finite_orientation(row: dict[str, Any]) -> list[float] | None:
    value = row.get("orientation_xyzw")
    if not isinstance(value, list) or len(value) != 4:
        return None
    try:
        result = [float(value[0]), float(value[1]), float(value[2]), float(value[3])]
    except (TypeError, ValueError):
        return None
    return result if all(math.isfinite(item) for item in result) else None


def finite_time(row: dict[str, Any]) -> float | None:
    try:
        value = float(row.get("time"))
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def quaternion_tilt_rad(values: list[float] | None) -> float:
    if values is None:
        return 0.0
    x, y, z, w = values
    norm = math.sqrt(x * x + y * y + z * z + w * w)
    if norm <= 0.0:
        return 0.0
    x, y = x / norm, y / norm
    body_z_in_world_z = max(-1.0, min(1.0, 1.0 - 2.0 * (x * x + y * y)))
    return math.acos(body_z_in_world_z)


def valid_truth_samples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for row in rows:
        time_s = finite_time(row)
        position = finite_position(row)
        if time_s is None or position is None:
            continue
        sample = dict(row)
        sample["_time"] = time_s
        sample["_position"] = position
        sample["_orientation"] = finite_orientation(row)
        samples.append(sample)
    samples.sort(key=lambda item: int(item.get("seq", len(samples))))
    return samples


def drop_synthetic_prefix(samples: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    header = [sample for sample in samples if sample.get("time_source") == "header_stamp"]
    if not header:
        return samples, {
            "sample_policy": "all_samples_by_record_order",
            "synthetic_prefix_dropped": 0,
            "header_stamp_sample_count": 0,
        }
    first_header_seq = int(header[0].get("seq", 0))
    return [sample for sample in samples if int(sample.get("seq", 0)) >= first_header_seq], {
        "sample_policy": "drop_synthetic_or_paused_prefix_before_first_header_stamp",
        "synthetic_prefix_dropped": first_header_seq,
        "header_stamp_sample_count": len(header),
    }


def commands_from_trace(rows: list[dict[str, Any]]) -> list[float]:
    values: list[float] = []
    for row in rows:
        command = row.get("command")
        if not isinstance(command, list) or not command:
            continue
        for item in command:
            try:
                number = float(item)
            except (TypeError, ValueError):
                continue
            if math.isfinite(number):
                values.append(number)
    return values


def controller_truth_time_window(rows: list[dict[str, Any]]) -> tuple[float | None, float | None, dict[str, Any]]:
    values: list[float] = []
    for row in rows:
        if row.get("truth_time_source") != "header_stamp":
            continue
        try:
            value = float(row.get("truth_time_s"))
        except (TypeError, ValueError):
            continue
        if math.isfinite(value):
            values.append(value)
    if not values:
        return None, None, {
            "controller_window_policy": "all_truth_samples_no_controller_header_stamp_window",
            "controller_header_stamp_count": 0,
        }
    return min(values), max(values), {
        "controller_window_policy": "truth_samples_cropped_to_controller_header_stamp_window",
        "controller_header_stamp_count": len(values),
        "controller_first_truth_time_s": round(min(values), 6),
        "controller_last_truth_time_s": round(max(values), 6),
    }


def crop_truth_to_controller_window(
    samples: list[dict[str, Any]],
    controller_trace: list[dict[str, Any]],
    *,
    tolerance_s: float = 0.05,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    start, end, policy = controller_truth_time_window(controller_trace)
    if start is None or end is None:
        policy["truth_samples_before_controller_crop"] = len(samples)
        policy["truth_samples_after_controller_crop"] = len(samples)
        return samples, policy
    cropped = [
        sample
        for sample in samples
        if start - tolerance_s <= float(sample["_time"]) <= end + tolerance_s
    ]
    policy["controller_window_tolerance_s"] = tolerance_s
    policy["truth_samples_before_controller_crop"] = len(samples)
    policy["truth_samples_after_controller_crop"] = len(cropped)
    return cropped, policy


def adapter_published_count(rows: list[dict[str, Any]]) -> int:
    return len([row for row in rows if row.get("status") == "published"])


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    controller_report_path = project_path(args.controller_report_json)
    controller_trace_path = project_path(args.controller_trace_jsonl)
    adapter_trace_path = project_path(args.adapter_trace_jsonl)
    truth_pose_path = project_path(args.truth_pose_jsonl)
    truth_summary_path = project_path(args.truth_summary_json)

    controller_report = read_json(controller_report_path)
    controller_trace = read_jsonl(controller_trace_path)
    adapter_trace = read_jsonl(adapter_trace_path)
    raw_truth = valid_truth_samples(read_jsonl(truth_pose_path))
    truth_samples_after_prefix, sample_policy = drop_synthetic_prefix(raw_truth)
    truth_samples, controller_window_policy = crop_truth_to_controller_window(
        truth_samples_after_prefix,
        controller_trace,
    )
    truth_summary = read_json(truth_summary_path)

    blockers: list[str] = []
    warnings: list[str] = []

    if controller_report.get("status") != "completed":
        blockers.append(f"controller_status_not_completed:{controller_report.get('status')}")
    if len(controller_trace) < args.min_controller_samples:
        blockers.append(f"controller_sample_count_below_min:{len(controller_trace)}<{args.min_controller_samples}")
    if adapter_published_count(adapter_trace) < args.min_adapter_samples:
        blockers.append(
            f"adapter_published_count_below_min:{adapter_published_count(adapter_trace)}<{args.min_adapter_samples}"
        )
    if len(truth_samples) < args.min_truth_samples:
        blockers.append(f"truth_sample_count_below_min:{len(truth_samples)}<{args.min_truth_samples}")

    duration_s = 0.0
    z_values: list[float] = []
    if truth_samples:
        duration_s = float(truth_samples[-1]["_time"]) - float(truth_samples[0]["_time"])
        z_values = [float(sample["_position"][2]) for sample in truth_samples]
    if duration_s < args.min_duration_s:
        blockers.append(f"truth_duration_below_min:{duration_s:.3f}<{args.min_duration_s:.3f}")

    final_z = z_values[-1] if z_values else None
    min_z = min(z_values) if z_values else None
    max_z = max(z_values) if z_values else None
    xy_distances: list[float] = []
    tilt_values: list[float] = []
    if truth_samples:
        origin_x = float(truth_samples[0]["_position"][0])
        origin_y = float(truth_samples[0]["_position"][1])
        for sample in truth_samples:
            position = sample["_position"]
            xy_distances.append(math.hypot(float(position[0]) - origin_x, float(position[1]) - origin_y))
            tilt_values.append(quaternion_tilt_rad(sample.get("_orientation")))
    max_xy_distance = max(xy_distances) if xy_distances else None
    final_xy_distance = xy_distances[-1] if xy_distances else None
    max_tilt = max(tilt_values) if tilt_values else None
    final_abs_error = abs(final_z - args.target_altitude_m) if final_z is not None else None
    max_abs_error = max(abs(value - args.target_altitude_m) for value in z_values) if z_values else None
    if final_abs_error is None:
        blockers.append("final_altitude_missing")
    elif final_abs_error > args.max_final_abs_z_error_m:
        blockers.append(
            f"final_abs_z_error_above_max:{final_abs_error:.6f}>{args.max_final_abs_z_error_m:.6f}"
        )
    if max_abs_error is None:
        blockers.append("max_abs_altitude_error_missing")
    elif max_abs_error > args.max_abs_z_error_m:
        blockers.append(f"max_abs_z_error_above_max:{max_abs_error:.6f}>{args.max_abs_z_error_m:.6f}")
    if min_z is not None and min_z < args.min_allowed_z_m:
        blockers.append(f"min_z_below_allowed:{min_z:.6f}<{args.min_allowed_z_m:.6f}")
    if max_z is not None and max_z > args.max_allowed_z_m:
        blockers.append(f"max_z_above_allowed:{max_z:.6f}>{args.max_allowed_z_m:.6f}")
    if max_xy_distance is None:
        blockers.append("max_xy_distance_missing")
    elif max_xy_distance > args.max_xy_distance_m:
        blockers.append(f"max_xy_distance_above_max:{max_xy_distance:.6f}>{args.max_xy_distance_m:.6f}")
    if max_tilt is None:
        blockers.append("max_tilt_missing")
    elif max_tilt > args.max_tilt_rad:
        blockers.append(f"max_tilt_above_max:{max_tilt:.6f}>{args.max_tilt_rad:.6f}")

    commands = commands_from_trace(controller_trace)
    if not commands:
        blockers.append("controller_command_trace_missing")
    else:
        if min(commands) < args.command_min - 1e-9:
            blockers.append(f"controller_command_below_min:{min(commands):.9f}<{args.command_min:.9f}")
        if max(commands) > args.command_max + 1e-9:
            blockers.append(f"controller_command_above_max:{max(commands):.9f}>{args.command_max:.9f}")
        if max(commands) - min(commands) <= args.min_command_span:
            warnings.append(
                f"controller_command_span_low:{max(commands) - min(commands):.9f}<={args.min_command_span:.9f}"
            )

    gate_passed = not blockers
    return {
        "schema": "mosim.gazebo_hover_hold_closed_loop_eval.v1",
        "status": "passed" if gate_passed else "blocked",
        "gate_passed": gate_passed,
        "inputs": {
            "controller_report_json": rel(controller_report_path),
            "controller_trace_jsonl": rel(controller_trace_path),
            "adapter_trace_jsonl": rel(adapter_trace_path),
            "truth_pose_jsonl": rel(truth_pose_path),
            "truth_summary_json": rel(truth_summary_path),
        },
        "target_altitude_m": args.target_altitude_m,
        "counts": {
            "controller_samples": len(controller_trace),
            "adapter_published": adapter_published_count(adapter_trace),
            "raw_truth_samples": len(raw_truth),
            "truth_samples": len(truth_samples),
        },
        "truth_recording": {
            "summary_status": truth_summary.get("status"),
            "summary_count": truth_summary.get("count"),
            "sample_policy": sample_policy,
            "controller_window_policy": controller_window_policy,
            "duration_s": round(duration_s, 6),
            "first_time_s": round(float(truth_samples[0]["_time"]), 6) if truth_samples else None,
            "last_time_s": round(float(truth_samples[-1]["_time"]), 6) if truth_samples else None,
        },
        "altitude": {
            "min_z_m": round(min_z, 6) if min_z is not None else None,
            "max_z_m": round(max_z, 6) if max_z is not None else None,
            "final_z_m": round(final_z, 6) if final_z is not None else None,
            "final_abs_z_error_m": round(final_abs_error, 6) if final_abs_error is not None else None,
            "max_abs_z_error_m": round(max_abs_error, 6) if max_abs_error is not None else None,
        },
        "horizontal_and_attitude": {
            "final_xy_distance_m": round(final_xy_distance, 6) if final_xy_distance is not None else None,
            "max_xy_distance_m": round(max_xy_distance, 6) if max_xy_distance is not None else None,
            "max_tilt_rad": round(max_tilt, 6) if max_tilt is not None else None,
        },
        "controller_output": {
            "report_status": controller_report.get("status"),
            "published_count": controller_report.get("counts", {}).get("published")
            if isinstance(controller_report.get("counts"), dict)
            else None,
            "command_min": round(min(commands), 9) if commands else None,
            "command_max": round(max(commands), 9) if commands else None,
            "command_span": round(max(commands) - min(commands), 9) if commands else None,
            "command_bounds": [args.command_min, args.command_max],
        },
        "thresholds": {
            "min_controller_samples": args.min_controller_samples,
            "min_adapter_samples": args.min_adapter_samples,
            "min_truth_samples": args.min_truth_samples,
            "min_duration_s": args.min_duration_s,
            "max_final_abs_z_error_m": args.max_final_abs_z_error_m,
            "max_abs_z_error_m": args.max_abs_z_error_m,
            "min_allowed_z_m": args.min_allowed_z_m,
            "max_allowed_z_m": args.max_allowed_z_m,
            "max_xy_distance_m": args.max_xy_distance_m,
            "max_tilt_rad": args.max_tilt_rad,
        },
        "blockers": blockers,
        "warnings": warnings,
        "claim_boundary": [
            "This proves only a bounded single-UAV Gazebo truth-feedback hover-hold pre-acceptance loop.",
            "It does not prove competition controller performance, trajectory tracking, planner_ready, final closed_loop acceptance, or multi-UAV readiness.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controller-report-json", required=True, type=Path)
    parser.add_argument("--controller-trace-jsonl", required=True, type=Path)
    parser.add_argument("--adapter-trace-jsonl", required=True, type=Path)
    parser.add_argument("--truth-pose-jsonl", required=True, type=Path)
    parser.add_argument("--truth-summary-json", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--target-altitude-m", type=float, default=1.2)
    parser.add_argument("--command-min", type=float, default=0.05480)
    parser.add_argument("--command-max", type=float, default=0.05490)
    parser.add_argument("--min-command-span", type=float, default=0.0)
    parser.add_argument("--min-controller-samples", type=int, default=20)
    parser.add_argument("--min-adapter-samples", type=int, default=20)
    parser.add_argument("--min-truth-samples", type=int, default=100)
    parser.add_argument("--min-duration-s", type=float, default=8.0)
    parser.add_argument("--max-final-abs-z-error-m", type=float, default=0.65)
    parser.add_argument("--max-abs-z-error-m", type=float, default=1.05)
    parser.add_argument("--min-allowed-z-m", type=float, default=0.15)
    parser.add_argument("--max-allowed-z-m", type=float, default=2.50)
    parser.add_argument("--max-xy-distance-m", type=float, default=1.50)
    parser.add_argument("--max-tilt-rad", type=float, default=0.70)
    args = parser.parse_args()

    output = project_path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = build_report(args)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("gate_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
