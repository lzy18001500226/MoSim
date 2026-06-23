#!/usr/bin/env python3
"""Evaluate whether a bounded ControllerOutput command moved the Gazebo plant.

This gate is intentionally narrower than closed-loop acceptance. It only
checks that a MoSim ControllerOutput fixture, adapter report, actuator echo
evidence, and same-run Gazebo truth-pose recording are consistent with a
measurable single-UAV plant response.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean
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
        position = [float(value[0]), float(value[1]), float(value[2])]
    except (TypeError, ValueError):
        return None
    if not all(math.isfinite(item) for item in position):
        return None
    return position


def finite_time(row: dict[str, Any]) -> float | None:
    try:
        value = float(row.get("time"))
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def valid_pose_samples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for row in rows:
        t = finite_time(row)
        p = finite_position(row)
        if t is None or p is None:
            continue
        sample = dict(row)
        sample["_time"] = t
        sample["_position"] = p
        samples.append(sample)
    samples.sort(key=lambda item: int(item.get("seq", len(samples))))
    return samples


def analysis_samples(samples: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    header_samples = [sample for sample in samples if sample.get("time_source") == "header_stamp"]
    if not header_samples:
        return samples, {
            "sample_policy": "all_samples_by_record_order",
            "synthetic_prefix_dropped": 0,
            "header_stamp_sample_count": 0,
        }

    first_header_seq = int(header_samples[0].get("seq", 0))
    selected = [sample for sample in samples if int(sample.get("seq", 0)) >= first_header_seq]
    return selected, {
        "sample_policy": "drop_synthetic_or_paused_prefix_before_first_header_stamp",
        "synthetic_prefix_dropped": first_header_seq,
        "header_stamp_sample_count": len(header_samples),
    }


def window(samples: list[dict[str, Any]], count: int, *, tail: bool = False) -> list[dict[str, Any]]:
    if not samples:
        return []
    bounded = max(1, min(count, len(samples)))
    return samples[-bounded:] if tail else samples[:bounded]


def axis_values(samples: list[dict[str, Any]], axis: int) -> list[float]:
    return [float(sample["_position"][axis]) for sample in samples]


def distance_xy(left: list[float], right: list[float]) -> float:
    return math.hypot(left[0] - right[0], left[1] - right[1])


def max_vector_delta(samples: list[dict[str, Any]], origin: list[float]) -> float:
    if not samples:
        return 0.0
    return max(
        math.sqrt(sum((float(sample["_position"][idx]) - origin[idx]) ** 2 for idx in range(3)))
        for sample in samples
    )


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    truth_pose_jsonl = project_path(args.truth_pose_jsonl)
    truth_summary_json = project_path(args.truth_summary_json)
    controller_report_json = project_path(args.controller_report_json)
    fixture_report_json = project_path(args.fixture_report_json)

    raw_samples = valid_pose_samples(read_jsonl(truth_pose_jsonl))
    samples, sample_policy = analysis_samples(raw_samples)
    truth_summary = read_json(truth_summary_json)
    controller_report = read_json(controller_report_json)
    fixture_report = read_json(fixture_report_json)

    blockers: list[str] = []
    warnings: list[str] = []

    if len(samples) < args.min_samples:
        blockers.append(f"truth_pose_sample_count_below_min:{len(samples)}<{args.min_samples}")

    duration_s = 0.0
    if samples:
        duration_s = float(samples[-1]["_time"]) - float(samples[0]["_time"])
    if duration_s < args.min_duration_s:
        blockers.append(f"truth_pose_duration_below_min:{duration_s:.3f}<{args.min_duration_s:.3f}")

    window_count = max(args.min_window_samples, int(len(samples) * args.window_fraction))
    first_window = window(samples, window_count, tail=False)
    last_window = window(samples, window_count, tail=True)

    first_mean = [mean(axis_values(first_window, idx)) if first_window else None for idx in range(3)]
    last_mean = [mean(axis_values(last_window, idx)) if last_window else None for idx in range(3)]
    first_position = finite_position(samples[0]) if samples else None
    last_position = finite_position(samples[-1]) if samples else None
    z_delta_m = None
    xy_delta_m = None
    max_3d_delta_m = 0.0
    max_z_delta_m = 0.0
    min_z_delta_m = 0.0
    max_abs_z_delta_m = 0.0
    early_z_range_m = None

    if first_mean[2] is not None and last_mean[2] is not None:
        z_delta_m = float(last_mean[2]) - float(first_mean[2])
        if z_delta_m < args.min_z_delta_m:
            blockers.append(f"plant_z_response_below_min:{z_delta_m:.6f}<{args.min_z_delta_m:.6f}")
    if first_position and last_position:
        xy_delta_m = distance_xy(first_position, last_position)
        max_3d_delta_m = max_vector_delta(samples, first_position)
        z_excursions = [float(sample["_position"][2]) - first_position[2] for sample in samples]
        max_z_delta_m = max(z_excursions)
        min_z_delta_m = min(z_excursions)
        max_abs_z_delta_m = max(abs(item) for item in z_excursions)
    if first_window:
        early_z_values = axis_values(first_window, 2)
        early_z_range_m = max(early_z_values) - min(early_z_values)
        if early_z_range_m > args.max_early_z_range_warning_m:
            warnings.append(
                "early_truth_pose_window_moved_before_command_window_assumption:"
                f"{early_z_range_m:.6f}>{args.max_early_z_range_warning_m:.6f}"
            )
    if max_3d_delta_m < args.min_3d_delta_m:
        blockers.append(f"plant_3d_response_below_min:{max_3d_delta_m:.6f}<{args.min_3d_delta_m:.6f}")
    if max_z_delta_m < args.min_z_delta_m:
        blockers.append(f"plant_max_z_response_below_min:{max_z_delta_m:.6f}<{args.min_z_delta_m:.6f}")

    controller_status = controller_report.get("status")
    fixture_status = fixture_report.get("status")
    if controller_status != "published":
        blockers.append(f"controller_adapter_status_not_published:{controller_status}")
    if fixture_status != "published":
        blockers.append(f"controller_fixture_status_not_published:{fixture_status}")

    try:
        velocity = [float(item) for item in controller_report.get("velocity", [])]
    except (TypeError, ValueError):
        velocity = []
    if len(velocity) != args.expected_actuator_count:
        blockers.append(
            f"controller_velocity_count_mismatch:{len(velocity)}!={args.expected_actuator_count}"
        )
    elif max(abs(item) for item in velocity) <= 0.0:
        blockers.append("controller_velocity_all_zero")

    gate_passed = not blockers
    return {
        "schema": "mosim.gazebo_plant_response_eval.v1",
        "status": "passed" if gate_passed else "blocked",
        "gate_passed": gate_passed,
        "blockers": blockers,
        "warnings": warnings,
        "inputs": {
            "truth_pose_jsonl": rel(truth_pose_jsonl),
            "truth_summary_json": rel(truth_summary_json),
            "controller_report_json": rel(controller_report_json),
            "fixture_report_json": rel(fixture_report_json),
        },
        "truth_recording": {
            "summary_status": truth_summary.get("status"),
            "summary_count": truth_summary.get("count"),
            "raw_valid_sample_count": len(raw_samples),
            "valid_sample_count": len(samples),
            "sample_policy": sample_policy,
            "duration_s": round(duration_s, 6),
            "first_time_s": round(float(samples[0]["_time"]), 6) if samples else None,
            "last_time_s": round(float(samples[-1]["_time"]), 6) if samples else None,
            "model_name": truth_summary.get("model_name"),
            "frame_id": truth_summary.get("frame_id"),
        },
        "plant_response": {
            "window_fraction": args.window_fraction,
            "window_sample_count": len(first_window),
            "first_mean_position_m": [round(float(item), 6) if item is not None else None for item in first_mean],
            "last_mean_position_m": [round(float(item), 6) if item is not None else None for item in last_mean],
            "z_delta_m": round(z_delta_m, 6) if z_delta_m is not None else None,
            "xy_delta_m": round(xy_delta_m, 6) if xy_delta_m is not None else None,
            "max_3d_delta_m": round(max_3d_delta_m, 6),
            "max_z_delta_m": round(max_z_delta_m, 6),
            "min_z_delta_m": round(min_z_delta_m, 6),
            "max_abs_z_delta_m": round(max_abs_z_delta_m, 6),
            "early_z_range_m": round(early_z_range_m, 6) if early_z_range_m is not None else None,
            "thresholds": {
                "min_samples": args.min_samples,
                "min_duration_s": args.min_duration_s,
                "min_z_delta_m": args.min_z_delta_m,
                "min_3d_delta_m": args.min_3d_delta_m,
            },
        },
        "controller_output": {
            "fixture_status": fixture_status,
            "adapter_status": controller_status,
            "input_sequence": controller_report.get("input_sequence"),
            "input_vehicle_id": controller_report.get("input_vehicle_id"),
            "input_command": controller_report.get("input_command"),
            "velocity": velocity,
            "command_age_s": controller_report.get("command_age_s"),
        },
        "claim_boundary": [
            "This proves only bounded ControllerOutput-to-Gazebo plant response evidence.",
            "It does not prove hover, trajectory tracking, controller performance, planner_ready, final closed_loop acceptance, or multi-UAV readiness.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--truth-pose-jsonl", required=True, type=Path)
    parser.add_argument("--truth-summary-json", required=True, type=Path)
    parser.add_argument("--controller-report-json", required=True, type=Path)
    parser.add_argument("--fixture-report-json", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--min-samples", type=int, default=20)
    parser.add_argument("--min-duration-s", type=float, default=2.0)
    parser.add_argument("--window-fraction", type=float, default=0.2)
    parser.add_argument("--min-window-samples", type=int, default=5)
    parser.add_argument("--min-z-delta-m", type=float, default=0.05)
    parser.add_argument("--min-3d-delta-m", type=float, default=0.05)
    parser.add_argument("--max-early-z-range-warning-m", type=float, default=0.02)
    parser.add_argument("--expected-actuator-count", type=int, default=4)
    args = parser.parse_args()

    output = project_path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = build_report(args)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("gate_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
