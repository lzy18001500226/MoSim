#!/usr/bin/env python3
"""Evaluate UAV dynamic quality from Gazebo controller / tracker traces.

This is an acceptance-side audit only. It does not launch Gazebo, publish
commands, or alter model/controller behavior.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def project_path(value: str | Path) -> Path:
    raw = Path(value)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {value}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            rows.append(data)
    return rows


def finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def position(row: dict[str, Any]) -> list[float] | None:
    value = row.get("position_m")
    if not isinstance(value, list) or len(value) < 3:
        return None
    xyz = [finite_float(item) for item in value[:3]]
    return [float(item) for item in xyz] if all(item is not None for item in xyz) else None


def target_position(row: dict[str, Any]) -> list[float] | None:
    value = row.get("target_position_m")
    if not isinstance(value, list) or len(value) < 3:
        return None
    xyz = [finite_float(item) for item in value[:3]]
    return [float(item) for item in xyz] if all(item is not None for item in xyz) else None


def yaw(row: dict[str, Any]) -> float | None:
    euler = row.get("euler_rpy_rad")
    if not isinstance(euler, list) or len(euler) < 3:
        return None
    return finite_float(euler[2])


def time_s(row: dict[str, Any]) -> float | None:
    for key in ("elapsed_s", "truth_time_s", "time"):
        value = finite_float(row.get(key))
        if value is not None:
            return value
    return None


def unwrap_delta(a: float, b: float) -> float:
    value = b - a
    while value > math.pi:
        value -= 2.0 * math.pi
    while value < -math.pi:
        value += 2.0 * math.pi
    return value


def sample_rows(rows: list[dict[str, Any]], phase: str | None = None) -> list[dict[str, Any]]:
    samples = [row for row in rows if position(row) is not None]
    if phase:
        samples = [
            row
            for row in samples
            if row.get("phase") == phase
            or row.get("mission_phase") == phase
            or row.get("control_phase") == phase
        ]
    return samples


def basic_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    samples = sample_rows(rows)
    if not samples:
        return {"sample_count": 0}
    poses = [position(row) for row in samples]
    poses = [pose for pose in poses if pose is not None]
    times = [time_s(row) for row in samples]
    times = [item for item in times if item is not None]
    yaws = [yaw(row) for row in samples]
    yaws = [item for item in yaws if item is not None]
    start = poses[0]
    end = poses[-1]
    xy_step = [
        math.hypot(poses[index][0] - poses[index - 1][0], poses[index][1] - poses[index - 1][1])
        for index in range(1, len(poses))
    ]
    z_step = [abs(poses[index][2] - poses[index - 1][2]) for index in range(1, len(poses))]
    return {
        "sample_count": len(poses),
        "duration_s": round(max(times) - min(times), 6) if len(times) >= 2 else None,
        "start_position_m": [round(item, 6) for item in start],
        "final_position_m": [round(item, 6) for item in end],
        "xy_displacement_m": round(math.hypot(end[0] - start[0], end[1] - start[1]), 6),
        "max_xy_from_start_m": round(max(math.hypot(pose[0] - start[0], pose[1] - start[1]) for pose in poses), 6),
        "min_z_m": round(min(pose[2] for pose in poses), 6),
        "max_z_m": round(max(pose[2] for pose in poses), 6),
        "final_z_m": round(end[2], 6),
        "path_length_xy_m": round(sum(xy_step), 6),
        "max_xy_step_m": round(max(xy_step), 6) if xy_step else 0.0,
        "max_z_step_m": round(max(z_step), 6) if z_step else 0.0,
        "yaw_delta_rad": round(unwrap_delta(yaws[0], yaws[-1]), 6) if len(yaws) >= 2 else None,
    }


def phase_metrics(rows: list[dict[str, Any]], phase: str) -> dict[str, Any]:
    return basic_metrics(sample_rows(rows, phase))


def tracking_metrics(rows: list[dict[str, Any]], *, phase: str | None = None) -> dict[str, Any]:
    samples = sample_rows(rows, phase)
    errors_xy: list[float] = []
    errors_z: list[float] = []
    actual: list[list[float]] = []
    target: list[list[float]] = []
    for row in samples:
        p = position(row)
        t = target_position(row)
        if p is None or t is None:
            continue
        actual.append(p)
        target.append(t)
        errors_xy.append(math.hypot(p[0] - t[0], p[1] - t[1]))
        errors_z.append(abs(p[2] - t[2]))
    if not errors_xy:
        return {"sample_count": 0}
    actual_steps = [
        math.hypot(actual[index][0] - actual[index - 1][0], actual[index][1] - actual[index - 1][1])
        for index in range(1, len(actual))
    ]
    target_steps = [
        math.hypot(target[index][0] - target[index - 1][0], target[index][1] - target[index - 1][1])
        for index in range(1, len(target))
    ]
    accel_like = [
        abs(actual_steps[index] - actual_steps[index - 1])
        for index in range(1, len(actual_steps))
    ]
    target_length = sum(target_steps)
    actual_length = sum(actual_steps)
    return {
        "sample_count": len(errors_xy),
        "rmse_xy_m": round(math.sqrt(sum(v * v for v in errors_xy) / len(errors_xy)), 6),
        "max_xy_error_m": round(max(errors_xy), 6),
        "mean_xy_error_m": round(sum(errors_xy) / len(errors_xy), 6),
        "max_z_error_m": round(max(errors_z), 6),
        "mean_z_error_m": round(sum(errors_z) / len(errors_z), 6),
        "actual_path_length_xy_m": round(actual_length, 6),
        "target_path_length_xy_m": round(target_length, 6),
        "path_length_ratio": round(actual_length / target_length, 6) if target_length > 1e-9 else None,
        "max_xy_step_m": round(max(actual_steps), 6) if actual_steps else 0.0,
        "mean_abs_step_delta_m": round(sum(accel_like) / len(accel_like), 6) if accel_like else 0.0,
        "max_abs_step_delta_m": round(max(accel_like), 6) if accel_like else 0.0,
    }


def settled_hover_metrics(rows: list[dict[str, Any]], *, fraction: float) -> dict[str, Any]:
    hover = sample_rows(rows, "hover")
    if not hover:
        hover = sample_rows(rows, "xy_track")
    if not hover:
        hover = sample_rows(rows)
    if not hover:
        return {"sample_count": 0}
    start = max(0, min(len(hover) - 1, int(len(hover) * fraction)))
    settled = hover[start:]
    return {
        "phase_source": "hover" if sample_rows(rows, "hover") else "xy_track" if sample_rows(rows, "xy_track") else "last_fraction_all_position_rows",
        **basic_metrics(settled),
        "tracking": tracking_metrics(settled),
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    trace_path = project_path(args.trace_jsonl)
    rows = read_jsonl(trace_path)
    blockers: list[str] = []
    warnings: list[str] = []

    overall = basic_metrics(rows)
    hover = phase_metrics(rows, "hover")
    land = phase_metrics(rows, "land")
    settle = phase_metrics(rows, "settle")
    figure8 = tracking_metrics(rows, phase="figure8")
    xy_track = tracking_metrics(rows, phase="xy_track")
    tracking_all = tracking_metrics(rows)
    settled_hover = settled_hover_metrics(rows, fraction=args.settled_fraction)

    if overall.get("sample_count", 0) < args.min_samples:
        blockers.append(f"sample_count_below_min:{overall.get('sample_count', 0)}<{args.min_samples}")

    settled_tracking = settled_hover.get("tracking", {}) if isinstance(settled_hover.get("tracking"), dict) else {}
    settled_xy = settled_hover.get("xy_displacement_m")
    settled_z_min = settled_hover.get("min_z_m")
    settled_z_max = settled_hover.get("max_z_m")
    if isinstance(settled_xy, (int, float)) and settled_xy > args.max_hover_xy_displacement_m:
        blockers.append(f"hover_xy_displacement_above_max:{settled_xy}>{args.max_hover_xy_displacement_m}")
    if isinstance(settled_z_min, (int, float)) and isinstance(settled_z_max, (int, float)):
        z_span = float(settled_z_max) - float(settled_z_min)
        if z_span > args.max_hover_z_span_m:
            blockers.append(f"hover_z_span_above_max:{z_span:.6f}>{args.max_hover_z_span_m:.6f}")
    if isinstance(settled_tracking.get("max_z_error_m"), (int, float)) and settled_tracking["max_z_error_m"] > args.max_hover_z_error_m:
        blockers.append(
            f"hover_z_error_above_max:{settled_tracking['max_z_error_m']}>{args.max_hover_z_error_m}"
        )

    land_like = settle if settle.get("sample_count", 0) else land
    if isinstance(land_like.get("xy_displacement_m"), (int, float)) and land_like["xy_displacement_m"] > args.max_landed_xy_slide_m:
        blockers.append(f"landed_xy_slide_above_max:{land_like['xy_displacement_m']}>{args.max_landed_xy_slide_m}")
    if isinstance(land_like.get("yaw_delta_rad"), (int, float)) and abs(land_like["yaw_delta_rad"]) > args.max_landed_yaw_delta_rad:
        blockers.append(f"landed_yaw_delta_above_max:{land_like['yaw_delta_rad']}>{args.max_landed_yaw_delta_rad}")

    figure_source = figure8 if figure8.get("sample_count", 0) else xy_track if xy_track.get("sample_count", 0) else tracking_all
    if figure_source.get("sample_count", 0):
        if isinstance(figure_source.get("rmse_xy_m"), (int, float)) and figure_source["rmse_xy_m"] > args.max_figure8_xy_rmse_m:
            blockers.append(f"figure8_xy_rmse_above_max:{figure_source['rmse_xy_m']}>{args.max_figure8_xy_rmse_m}")
        if isinstance(figure_source.get("max_xy_error_m"), (int, float)) and figure_source["max_xy_error_m"] > args.max_figure8_xy_error_m:
            blockers.append(f"figure8_xy_error_above_max:{figure_source['max_xy_error_m']}>{args.max_figure8_xy_error_m}")
        if isinstance(figure_source.get("mean_abs_step_delta_m"), (int, float)) and figure_source["mean_abs_step_delta_m"] > args.max_mean_abs_step_delta_m:
            blockers.append(
                f"figure8_step_delta_above_max:{figure_source['mean_abs_step_delta_m']}>{args.max_mean_abs_step_delta_m}"
            )
    else:
        warnings.append("no_target_tracking_samples_found")

    return {
        "schema": "mosim.uav_dynamic_quality_eval.v1",
        "status": "passed" if not blockers else "blocked",
        "gate_passed": not blockers,
        "trace_jsonl": rel(trace_path),
        "counts": {"raw_rows": len(rows), "position_rows": overall.get("sample_count", 0)},
        "metrics": {
            "overall": overall,
            "settled_hover": settled_hover,
            "land": land,
            "settle": settle,
            "tracking_all": tracking_all,
            "figure8": figure8,
            "xy_track": xy_track,
        },
        "thresholds": {
            "min_samples": args.min_samples,
            "settled_fraction": args.settled_fraction,
            "max_hover_xy_displacement_m": args.max_hover_xy_displacement_m,
            "max_hover_z_span_m": args.max_hover_z_span_m,
            "max_hover_z_error_m": args.max_hover_z_error_m,
            "max_landed_xy_slide_m": args.max_landed_xy_slide_m,
            "max_landed_yaw_delta_rad": args.max_landed_yaw_delta_rad,
            "max_figure8_xy_rmse_m": args.max_figure8_xy_rmse_m,
            "max_figure8_xy_error_m": args.max_figure8_xy_error_m,
            "max_mean_abs_step_delta_m": args.max_mean_abs_step_delta_m,
        },
        "blockers": blockers,
        "warnings": warnings,
        "claim_boundary": [
            "audit only; no Gazebo, ROS2, MWORKS, PX4, or UE runtime was launched",
            "passing this audit is necessary but not sufficient for final competition controller deployment",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-jsonl", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--min-samples", type=int, default=100)
    parser.add_argument("--settled-fraction", type=float, default=0.5)
    parser.add_argument("--max-hover-xy-displacement-m", type=float, default=0.05)
    parser.add_argument("--max-hover-z-span-m", type=float, default=0.12)
    parser.add_argument("--max-hover-z-error-m", type=float, default=0.12)
    parser.add_argument("--max-landed-xy-slide-m", type=float, default=0.02)
    parser.add_argument("--max-landed-yaw-delta-rad", type=float, default=0.05)
    parser.add_argument("--max-figure8-xy-rmse-m", type=float, default=0.15)
    parser.add_argument("--max-figure8-xy-error-m", type=float, default=0.35)
    parser.add_argument("--max-mean-abs-step-delta-m", type=float, default=0.03)
    args = parser.parse_args()

    output = project_path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = build_report(args)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("gate_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
