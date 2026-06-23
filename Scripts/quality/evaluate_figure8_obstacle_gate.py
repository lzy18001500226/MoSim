#!/usr/bin/env python3
"""Evaluate a bounded figure-8 plus static-obstacle Gazebo/ROS2 gate."""

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
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "invalid_json", "error": f"{exc.__class__.__name__}: {exc}"}
    return data if isinstance(data, dict) else {}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
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


def finite_position(row: dict[str, Any]) -> list[float] | None:
    value = row.get("position_m")
    if not isinstance(value, list) or len(value) != 3:
        return None
    try:
        position = [float(value[0]), float(value[1]), float(value[2])]
    except (TypeError, ValueError):
        return None
    return position if all(math.isfinite(item) for item in position) else None


def finite_time(row: dict[str, Any]) -> float | None:
    raw = row.get("time", row.get("elapsed_s"))
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def timed_truth(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for row in rows:
        if row.get("time_source") not in {"header_stamp", "state_stats_sim_time"}:
            continue
        time_s = finite_time(row)
        position = finite_position(row)
        if time_s is None or position is None:
            continue
        item = dict(row)
        item["_time"] = time_s
        item["_position"] = position
        samples.append(item)
    samples.sort(key=lambda item: (float(item["_time"]), int(item.get("seq", 0))))
    return samples


def tracker_observed_truth(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for row in rows:
        try:
            time_s = float(row.get("truth_time_s"))
        except (TypeError, ValueError):
            time_s = finite_time(row)
        position = finite_position(row)
        if time_s is None or position is None:
            continue
        item = {
            "_time": time_s,
            "_position": position,
            "_source": "controller_observed_truth_fallback",
        }
        samples.append(item)
    samples.sort(key=lambda item: float(item["_time"]))
    return samples


def reference_samples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for row in rows:
        time_s = finite_time(row)
        position = finite_position(row)
        if time_s is None or position is None:
            continue
        item = dict(row)
        item["_time"] = time_s
        item["_position"] = position
        samples.append(item)
    samples.sort(key=lambda item: float(item["_time"]))
    return samples


def phase_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        phase = row.get("mission_phase")
        if isinstance(phase, str) and phase:
            counts[phase] = counts.get(phase, 0) + 1
    return counts


def reference_phase_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = phase_counts(rows)
    phases = list(counts)
    positions_by_phase: dict[str, list[list[float]]] = {}
    for row in rows:
        phase = row.get("mission_phase")
        position = finite_position(row)
        if isinstance(phase, str) and position is not None:
            positions_by_phase.setdefault(phase, []).append(position)
    final_position = finite_position(rows[-1]) if rows else None
    figure8_positions = positions_by_phase.get("figure8", [])
    figure8_duration_s = 0.0
    figure8_trajectory_time_span_s = 0.0
    if figure8_positions:
        figure8_rows = [row for row in rows if row.get("mission_phase") == "figure8"]
        times = [finite_time(row) for row in figure8_rows]
        finite_times = [float(item) for item in times if item is not None]
        if len(finite_times) >= 2:
            figure8_duration_s = max(finite_times) - min(finite_times)
        trajectory_times: list[float] = []
        for row in figure8_rows:
            try:
                value = float(row.get("trajectory_time_s"))
            except (TypeError, ValueError):
                continue
            if math.isfinite(value):
                trajectory_times.append(value)
        if len(trajectory_times) >= 2:
            figure8_trajectory_time_span_s = max(trajectory_times) - min(trajectory_times)
    return {
        "phase_counts": counts,
        "phases": phases,
        "final_position_m": [round(item, 6) for item in final_position] if final_position is not None else None,
        "figure8_duration_s": round(figure8_duration_s, 6),
        "figure8_trajectory_time_span_s": round(figure8_trajectory_time_span_s, 6),
    }


def end_state_metrics(samples: list[dict[str, Any]]) -> dict[str, Any]:
    if not samples:
        return {
            "final_position_m": None,
            "final_time_s": None,
            "final_speed_mps": None,
            "last_window_min_z_m": None,
            "last_window_max_z_m": None,
            "last_window_xy_displacement_m": None,
        }
    final = samples[-1]
    final_position = final["_position"]
    final_time = float(final["_time"])
    previous = samples[-2] if len(samples) >= 2 else None
    final_speed = None
    if previous is not None:
        dt = final_time - float(previous["_time"])
        if dt > 0:
            final_speed = math.dist(final_position, previous["_position"]) / dt
    window_start = final_time - 2.0
    last_window = [sample["_position"] for sample in samples if float(sample["_time"]) >= window_start]
    z_values = [position[2] for position in last_window]
    last_window_xy_displacement = None
    if len(last_window) >= 2:
        first_xy = last_window[0]
        last_xy = last_window[-1]
        last_window_xy_displacement = math.hypot(last_xy[0] - first_xy[0], last_xy[1] - first_xy[1])
    return {
        "final_position_m": [round(float(item), 6) for item in final_position],
        "final_time_s": round(final_time, 6),
        "final_speed_mps": round(final_speed, 6) if final_speed is not None else None,
        "last_window_min_z_m": round(min(z_values), 6) if z_values else None,
        "last_window_max_z_m": round(max(z_values), 6) if z_values else None,
        "last_window_xy_displacement_m": round(last_window_xy_displacement, 6)
        if last_window_xy_displacement is not None
        else None,
    }


def center_revisit_metrics(
    samples: list[dict[str, Any]],
    *,
    center_xy: tuple[float, float],
    radius_m: float,
) -> dict[str, Any]:
    center_x, center_y = center_xy
    entries = 0
    in_band = False
    first_entry_time: float | None = None
    second_entry_time: float | None = None
    for sample in samples:
        position = sample["_position"]
        inside = math.hypot(position[0] - center_x, position[1] - center_y) <= radius_m
        if inside and not in_band:
            entries += 1
            if entries == 1:
                first_entry_time = float(sample["_time"])
            elif entries == 2:
                second_entry_time = float(sample["_time"])
        in_band = inside
    return {
        "center_xy_m": [round(center_x, 6), round(center_y, 6)],
        "radius_m": radius_m,
        "entry_count": entries,
        "first_entry_time_s": round(first_entry_time, 6) if first_entry_time is not None else None,
        "second_entry_time_s": round(second_entry_time, 6) if second_entry_time is not None else None,
        "highlight_required": True,
        "highlight_rule": "second and later entries within center_revisit_radius_m should be rendered in a distinct color for visual review",
    }


def crop_truth_to_reference_window(
    truth: list[dict[str, Any]],
    refs: list[dict[str, Any]],
    *,
    tolerance_s: float = 0.1,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not truth or not refs:
        return truth, {
            "reference_window_policy": "no_reference_window_crop",
            "truth_samples_before_reference_crop": len(truth),
            "truth_samples_after_reference_crop": len(truth),
        }
    start = float(refs[0]["_time"])
    end = float(refs[-1]["_time"])
    cropped = [
        sample
        for sample in truth
        if start - tolerance_s <= float(sample["_time"] - truth[0]["_time"]) <= end + tolerance_s
    ]
    return cropped, {
        "reference_window_policy": "truth_samples_cropped_to_reference_elapsed_window",
        "reference_first_elapsed_s": round(start, 6),
        "reference_last_elapsed_s": round(end, 6),
        "reference_window_tolerance_s": tolerance_s,
        "truth_samples_before_reference_crop": len(truth),
        "truth_samples_after_reference_crop": len(cropped),
    }


def nearest_reference(time_s: float, refs: list[dict[str, Any]], cursor: int) -> tuple[dict[str, Any] | None, int]:
    if not refs:
        return None, cursor
    cursor = max(0, min(cursor, len(refs) - 1))
    while cursor + 1 < len(refs) and abs(refs[cursor + 1]["_time"] - time_s) <= abs(refs[cursor]["_time"] - time_s):
        cursor += 1
    return refs[cursor], cursor


def parse_obstacle(raw: str) -> tuple[float, float, float]:
    parts = [float(item) for item in raw.split(",")]
    if len(parts) != 3 or parts[2] <= 0.0 or not all(math.isfinite(item) for item in parts):
        raise argparse.ArgumentTypeError("obstacle must be finite x,y,radius with positive radius")
    return parts[0], parts[1], parts[2]


def min_clearance(position: list[float], obstacles: list[tuple[float, float, float]]) -> float | None:
    if not obstacles:
        return None
    return min(math.hypot(position[0] - ox, position[1] - oy) - radius for ox, oy, radius in obstacles)


def adapter_published_count(rows: list[dict[str, Any]]) -> int:
    return len([row for row in rows if row.get("status") == "published"])


def tracker_xy_track_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    samples: list[float] = []
    z_errors: list[float] = []
    saturated = 0
    for row in rows:
        if row.get("control_phase") != "xy_track":
            continue
        raw_error = row.get("reference_xy_error_m", row.get("xy_error_m"))
        try:
            xy_error = float(raw_error)
        except (TypeError, ValueError):
            continue
        if not math.isfinite(xy_error):
            continue
        samples.append(abs(xy_error))
        try:
            z_error = abs(float(row.get("z_error_m")))
            if math.isfinite(z_error):
                z_errors.append(z_error)
        except (TypeError, ValueError):
            pass
        if row.get("saturation") is True:
            saturated += 1
    if not samples:
        return {
            "sample_count": 0,
            "rmse_xy_m": None,
            "max_xy_error_m": None,
            "max_z_error_m": max(z_errors) if z_errors else None,
            "saturation_count": saturated,
        }
    return {
        "sample_count": len(samples),
        "rmse_xy_m": math.sqrt(sum(value * value for value in samples) / len(samples)),
        "max_xy_error_m": max(samples),
        "max_z_error_m": max(z_errors) if z_errors else None,
        "saturation_count": saturated,
    }


def tracker_figure8_phase_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    xy_errors: list[float] = []
    z_errors: list[float] = []
    for row in rows:
        if row.get("control_phase") != "xy_track":
            continue
        raw_ref = row.get("raw_reference_position_m", row.get("target_position_m"))
        if not isinstance(raw_ref, list) or len(raw_ref) != 3:
            continue
        try:
            ref_z = float(raw_ref[2])
            raw_xy_error = float(row.get("reference_xy_error_m", row.get("xy_error_m")))
            raw_z_error = abs(float(row.get("z_error_m")))
        except (TypeError, ValueError):
            continue
        if not all(math.isfinite(item) for item in (ref_z, raw_xy_error, raw_z_error)):
            continue
        # The figure-8 phase is the only sustained XY-tracking phase at the
        # cruise altitude. Takeoff/landing ramps can also be xy_track after the
        # latch engages, so exclude them using the reference altitude.
        if ref_z < 0.95:
            continue
        xy_errors.append(abs(raw_xy_error))
        z_errors.append(raw_z_error)
    if not xy_errors:
        return {
            "sample_count": 0,
            "rmse_xy_m": None,
            "max_xy_error_m": None,
            "max_z_error_m": max(z_errors) if z_errors else None,
            "metric_source": "tracker_trace_reference_error_at_cruise_altitude",
        }
    return {
        "sample_count": len(xy_errors),
        "rmse_xy_m": math.sqrt(sum(value * value for value in xy_errors) / len(xy_errors)),
        "max_xy_error_m": max(xy_errors),
        "max_z_error_m": max(z_errors) if z_errors else None,
        "metric_source": "tracker_trace_reference_error_at_cruise_altitude",
    }


def xy_shape_metrics(
    samples: list[dict[str, Any]],
    *,
    center_xy: tuple[float, float],
    nominal_span_x_m: float,
    nominal_span_y_m: float,
) -> dict[str, Any]:
    positions = [sample["_position"] for sample in samples]
    if len(positions) < 2:
        return {
            "sample_count": len(positions),
            "span_x_m": 0.0,
            "span_y_m": 0.0,
            "path_length_xy_m": 0.0,
            "left_lobe_fraction": 0.0,
            "right_lobe_fraction": 0.0,
            "upper_lobe_fraction": 0.0,
            "lower_lobe_fraction": 0.0,
            "center_crossings_x": 0,
        }

    xs = [float(position[0]) for position in positions]
    ys = [float(position[1]) for position in positions]
    center_x, center_y = center_xy
    span_x = max(xs) - min(xs)
    span_y = max(ys) - min(ys)
    path_length = sum(
        math.hypot(xs[index] - xs[index - 1], ys[index] - ys[index - 1])
        for index in range(1, len(xs))
    )
    x_deadband = max(0.05, 0.15 * nominal_span_x_m)
    y_deadband = max(0.05, 0.15 * nominal_span_y_m)
    left_count = sum(1 for x in xs if x < center_x - x_deadband)
    right_count = sum(1 for x in xs if x > center_x + x_deadband)
    upper_count = sum(1 for y in ys if y > center_y + y_deadband)
    lower_count = sum(1 for y in ys if y < center_y - y_deadband)
    signs: list[int] = []
    for x in xs:
        if x < center_x - x_deadband:
            signs.append(-1)
        elif x > center_x + x_deadband:
            signs.append(1)
        else:
            signs.append(0)
    crossings = 0
    previous = 0
    for sign in signs:
        if sign == 0:
            continue
        if previous and sign != previous:
            crossings += 1
        previous = sign
    count = len(xs)
    return {
        "sample_count": count,
        "span_x_m": round(span_x, 6),
        "span_y_m": round(span_y, 6),
        "path_length_xy_m": round(path_length, 6),
        "left_lobe_fraction": round(left_count / count, 6),
        "right_lobe_fraction": round(right_count / count, 6),
        "upper_lobe_fraction": round(upper_count / count, 6),
        "lower_lobe_fraction": round(lower_count / count, 6),
        "center_crossings_x": crossings,
    }


def tracker_time_window(rows: list[dict[str, Any]]) -> tuple[float | None, float | None, dict[str, Any]]:
    values: list[float] = []
    for row in rows:
        try:
            value = float(row.get("truth_time_s"))
        except (TypeError, ValueError):
            continue
        if math.isfinite(value):
            values.append(value)
    if not values:
        return None, None, {
            "tracker_window_policy": "all_truth_samples_no_tracker_truth_time_window",
            "tracker_sample_count_with_time": 0,
        }
    return min(values), max(values), {
        "tracker_window_policy": "truth_samples_cropped_to_tracker_truth_time_window",
        "tracker_sample_count_with_time": len(values),
        "tracker_first_truth_time_s": round(min(values), 6),
        "tracker_last_truth_time_s": round(max(values), 6),
    }


def crop_truth_to_tracker_window(
    truth: list[dict[str, Any]],
    tracker_trace: list[dict[str, Any]],
    *,
    tolerance_s: float = 0.05,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    start, end, policy = tracker_time_window(tracker_trace)
    if start is None or end is None:
        policy["truth_samples_before_tracker_crop"] = len(truth)
        policy["truth_samples_after_tracker_crop"] = len(truth)
        return truth, policy
    cropped = [
        sample
        for sample in truth
        if start - tolerance_s <= float(sample["_time"]) <= end + tolerance_s
    ]
    policy["tracker_window_tolerance_s"] = tolerance_s
    policy["truth_samples_before_tracker_crop"] = len(truth)
    policy["truth_samples_after_tracker_crop"] = len(cropped)
    return cropped, policy


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    reference_report_path = project_path(args.reference_report_json)
    reference_trace_path = project_path(args.reference_trace_jsonl)
    tracker_report_path = project_path(args.tracker_report_json)
    tracker_trace_path = project_path(args.tracker_trace_jsonl)
    adapter_trace_path = project_path(args.adapter_trace_jsonl)
    truth_pose_path = project_path(args.truth_pose_jsonl)
    truth_summary_path = project_path(args.truth_summary_json)

    reference_report = read_json(reference_report_path)
    tracker_report = read_json(tracker_report_path)
    truth_summary = read_json(truth_summary_path)
    raw_reference_rows = read_jsonl(reference_trace_path)
    refs = reference_samples(raw_reference_rows)
    tracker_trace = read_jsonl(tracker_trace_path)
    tracker_xy_track = tracker_xy_track_metrics(tracker_trace)
    tracker_figure8_phase = tracker_figure8_phase_metrics(tracker_trace)
    adapter_trace = read_jsonl(adapter_trace_path)
    raw_truth = timed_truth(read_jsonl(truth_pose_path))
    truth_source = "independent_gazebo_truth"
    truth, tracker_window_policy = crop_truth_to_tracker_window(raw_truth, tracker_trace)
    truth, reference_window_policy = crop_truth_to_reference_window(truth, refs)
    if len(truth) < args.min_truth_samples:
        fallback_truth = tracker_observed_truth(tracker_trace)
        if len(fallback_truth) > len(truth):
            truth = fallback_truth
            truth_source = "controller_observed_truth_fallback"
            tracker_window_policy = {
                "tracker_window_policy": "controller_observed_truth_fallback_from_tracker_trace",
                "fallback_reason": "cropped_independent_truth_below_min",
                "truth_samples_before_tracker_crop": len(raw_truth),
                "truth_samples_after_tracker_crop": len(truth),
                "cropped_independent_truth_samples": tracker_window_policy.get(
                    "truth_samples_after_tracker_crop"
                ),
                "truth_fallback_used": True,
            }

    blockers: list[str] = []
    warnings: list[str] = []
    if not reference_report.get("gate_passed"):
        blockers.append(f"reference_publisher_not_passed:{reference_report.get('status')}")
    if tracker_report.get("status") != "completed":
        blockers.append(f"tracker_not_completed:{tracker_report.get('status')}")
    if len(refs) < args.min_reference_samples:
        blockers.append(f"reference_samples_below_min:{len(refs)}<{args.min_reference_samples}")
    if len(truth) < args.min_truth_samples:
        blockers.append(f"truth_samples_below_min:{len(truth)}<{args.min_truth_samples}")
    if len(tracker_trace) < args.min_tracker_samples:
        blockers.append(f"tracker_samples_below_min:{len(tracker_trace)}<{args.min_tracker_samples}")
    if int(tracker_xy_track["sample_count"]) < args.min_xy_track_samples:
        blockers.append(
            f"xy_track_samples_below_min:{tracker_xy_track['sample_count']}<{args.min_xy_track_samples}"
        )
    if adapter_published_count(adapter_trace) < args.min_adapter_samples:
        blockers.append(
            f"adapter_published_below_min:{adapter_published_count(adapter_trace)}<{args.min_adapter_samples}"
        )

    duration_s = truth[-1]["_time"] - truth[0]["_time"] if len(truth) >= 2 else 0.0
    if duration_s < args.min_duration_s:
        blockers.append(f"truth_duration_below_min:{duration_s:.3f}<{args.min_duration_s:.3f}")

    reference_mission = reference_phase_metrics(raw_reference_rows)
    for phase in args.required_mission_phase:
        count = int(reference_mission["phase_counts"].get(phase, 0))
        if count < args.min_samples_per_required_phase:
            blockers.append(f"reference_phase_{phase}_samples_below_min:{count}<{args.min_samples_per_required_phase}")
    if float(reference_mission["figure8_trajectory_time_span_s"]) < args.min_figure8_trajectory_time_span_s:
        blockers.append(
            "figure8_trajectory_time_span_below_min:"
            f"{float(reference_mission['figure8_trajectory_time_span_s']):.6f}<"
            f"{args.min_figure8_trajectory_time_span_s:.6f}"
        )

    cursor = 0
    matched_errors: list[float] = []
    matched_xy_errors: list[float] = []
    matched_z_errors: list[float] = []
    figure8_phase_xy_errors: list[float] = []
    figure8_phase_z_errors: list[float] = []
    max_ref_time_delta = 0.0
    truth_clearances: list[float] = []
    ref_clearances: list[float] = []
    for sample in truth:
        sample_time = float(sample["_time"] - truth[0]["_time"])
        ref, cursor = nearest_reference(sample_time, refs, cursor)
        if ref is not None:
            ref_time = float(ref["_time"])
            max_ref_time_delta = max(max_ref_time_delta, abs(ref_time - sample_time))
            error = [sample["_position"][i] - ref["_position"][i] for i in range(3)]
            matched_errors.append(math.sqrt(sum(item * item for item in error)))
            matched_xy_errors.append(math.hypot(error[0], error[1]))
            matched_z_errors.append(abs(error[2]))
            if ref.get("mission_phase") == "figure8":
                figure8_phase_xy_errors.append(math.hypot(error[0], error[1]))
                figure8_phase_z_errors.append(abs(error[2]))
        clearance = min_clearance(sample["_position"], args.obstacle)
        if clearance is not None:
            truth_clearances.append(clearance)
    for ref in refs:
        clearance = min_clearance(ref["_position"], args.obstacle)
        if clearance is not None:
            ref_clearances.append(clearance)

    rmse_3d = math.sqrt(sum(item * item for item in matched_errors) / len(matched_errors)) if matched_errors else None
    rmse_xy = math.sqrt(sum(item * item for item in matched_xy_errors) / len(matched_xy_errors)) if matched_xy_errors else None
    max_xy = max(matched_xy_errors) if matched_xy_errors else None
    max_z = max(matched_z_errors) if matched_z_errors else None
    figure8_phase_rmse_xy = (
        math.sqrt(sum(item * item for item in figure8_phase_xy_errors) / len(figure8_phase_xy_errors))
        if figure8_phase_xy_errors
        else None
    )
    figure8_phase_max_xy = max(figure8_phase_xy_errors) if figure8_phase_xy_errors else None
    figure8_phase_max_z = max(figure8_phase_z_errors) if figure8_phase_z_errors else None
    min_truth_clearance = min(truth_clearances) if truth_clearances else None
    min_ref_clearance = min(ref_clearances) if ref_clearances else None

    ref_positions = [sample["_position"] for sample in refs]
    if ref_positions:
        ref_xs = [float(position[0]) for position in ref_positions]
        ref_ys = [float(position[1]) for position in ref_positions]
        reference_center_xy = ((min(ref_xs) + max(ref_xs)) / 2.0, (min(ref_ys) + max(ref_ys)) / 2.0)
    else:
        reference_center_xy = (0.0, 0.0)
    reference_shape = xy_shape_metrics(
        refs,
        center_xy=reference_center_xy,
        nominal_span_x_m=args.expected_figure8_span_x_m,
        nominal_span_y_m=args.expected_figure8_span_y_m,
    )
    truth_shape = xy_shape_metrics(
        truth,
        center_xy=reference_center_xy,
        nominal_span_x_m=args.expected_figure8_span_x_m,
        nominal_span_y_m=args.expected_figure8_span_y_m,
    )
    reference_length = max(float(reference_shape["path_length_xy_m"]), 1e-9)
    truth_path_length_ratio = float(truth_shape["path_length_xy_m"]) / reference_length
    truth_end_state = end_state_metrics(truth)
    reference_end_state = end_state_metrics(refs)
    truth_center_revisit = center_revisit_metrics(
        truth,
        center_xy=reference_center_xy,
        radius_m=args.center_revisit_radius_m,
    )
    if int(truth_center_revisit["entry_count"]) < args.min_center_revisit_entries:
        blockers.append(
            f"center_revisit_entries_below_min:{truth_center_revisit['entry_count']}<{args.min_center_revisit_entries}"
        )
    truth_final_position = truth_end_state["final_position_m"]
    if not isinstance(truth_final_position, list):
        blockers.append("truth_final_position_missing")
    else:
        final_z = float(truth_final_position[2])
        if final_z > args.max_final_altitude_m:
            blockers.append(f"truth_final_altitude_above_max:{final_z:.6f}>{args.max_final_altitude_m:.6f}")
    last_window_max_z = truth_end_state["last_window_max_z_m"]
    if last_window_max_z is None:
        blockers.append("truth_landing_window_missing")
    elif float(last_window_max_z) > args.max_landing_window_altitude_m:
        blockers.append(
            f"truth_landing_window_altitude_above_max:{float(last_window_max_z):.6f}>"
            f"{args.max_landing_window_altitude_m:.6f}"
        )
    last_window_xy_displacement = truth_end_state["last_window_xy_displacement_m"]
    if last_window_xy_displacement is None:
        blockers.append("truth_landing_window_xy_displacement_missing")
    elif float(last_window_xy_displacement) > args.max_landing_window_xy_displacement_m:
        blockers.append(
            f"truth_landing_window_xy_displacement_above_max:{float(last_window_xy_displacement):.6f}>"
            f"{args.max_landing_window_xy_displacement_m:.6f}"
        )
    if truth_shape["span_x_m"] < args.min_truth_span_x_m:
        blockers.append(f"truth_span_x_below_min:{truth_shape['span_x_m']:.6f}<{args.min_truth_span_x_m:.6f}")
    if truth_shape["span_y_m"] < args.min_truth_span_y_m:
        blockers.append(f"truth_span_y_below_min:{truth_shape['span_y_m']:.6f}<{args.min_truth_span_y_m:.6f}")
    if truth_path_length_ratio < args.min_truth_path_length_ratio:
        blockers.append(
            f"truth_path_length_ratio_below_min:{truth_path_length_ratio:.6f}<{args.min_truth_path_length_ratio:.6f}"
        )
    for key, value in (
        ("left_lobe_fraction", truth_shape["left_lobe_fraction"]),
        ("right_lobe_fraction", truth_shape["right_lobe_fraction"]),
        ("upper_lobe_fraction", truth_shape["upper_lobe_fraction"]),
        ("lower_lobe_fraction", truth_shape["lower_lobe_fraction"]),
    ):
        if value < args.min_lobe_fraction:
            blockers.append(f"{key}_below_min:{value:.6f}<{args.min_lobe_fraction:.6f}")
    if int(truth_shape["center_crossings_x"]) < args.min_center_crossings_x:
        blockers.append(
            f"center_crossings_x_below_min:{truth_shape['center_crossings_x']}<{args.min_center_crossings_x}"
        )

    if matched_errors and max_ref_time_delta > args.max_reference_time_delta_s:
        warnings.append(f"reference_time_delta_high:{max_ref_time_delta:.3f}>{args.max_reference_time_delta_s:.3f}")
    if rmse_xy is None:
        blockers.append("tracking_rmse_missing")
    elif rmse_xy > args.max_xy_rmse_m:
        blockers.append(f"xy_rmse_above_max:{rmse_xy:.6f}>{args.max_xy_rmse_m:.6f}")
    if max_xy is None:
        blockers.append("tracking_max_xy_error_missing")
    elif max_xy > args.max_xy_error_m:
        blockers.append(f"max_xy_error_above_max:{max_xy:.6f}>{args.max_xy_error_m:.6f}")
    if max_z is None:
        blockers.append("tracking_max_z_error_missing")
    elif max_z > args.max_z_error_m:
        blockers.append(f"max_z_error_above_max:{max_z:.6f}>{args.max_z_error_m:.6f}")
    if int(tracker_figure8_phase["sample_count"]) < args.min_figure8_phase_samples:
        blockers.append(
            f"figure8_phase_samples_below_min:{tracker_figure8_phase['sample_count']}<{args.min_figure8_phase_samples}"
        )
    if tracker_figure8_phase["rmse_xy_m"] is None:
        blockers.append("figure8_phase_xy_rmse_missing")
    elif float(tracker_figure8_phase["rmse_xy_m"]) > args.max_figure8_phase_xy_rmse_m:
        blockers.append(
            f"figure8_phase_xy_rmse_above_max:{float(tracker_figure8_phase['rmse_xy_m']):.6f}>"
            f"{args.max_figure8_phase_xy_rmse_m:.6f}"
        )
    if tracker_figure8_phase["max_xy_error_m"] is None:
        blockers.append("figure8_phase_max_xy_error_missing")
    elif float(tracker_figure8_phase["max_xy_error_m"]) > args.max_figure8_phase_xy_error_m:
        blockers.append(
            f"figure8_phase_max_xy_error_above_max:{float(tracker_figure8_phase['max_xy_error_m']):.6f}>"
            f"{args.max_figure8_phase_xy_error_m:.6f}"
        )
    if tracker_figure8_phase["max_z_error_m"] is None:
        blockers.append("figure8_phase_max_z_error_missing")
    elif float(tracker_figure8_phase["max_z_error_m"]) > args.max_figure8_phase_z_error_m:
        blockers.append(
            f"figure8_phase_max_z_error_above_max:{float(tracker_figure8_phase['max_z_error_m']):.6f}>"
            f"{args.max_figure8_phase_z_error_m:.6f}"
        )
    if min_ref_clearance is None:
        blockers.append("reference_obstacle_clearance_missing")
    elif min_ref_clearance < args.min_reference_obstacle_clearance_m:
        blockers.append(
            f"reference_clearance_below_min:{min_ref_clearance:.6f}<{args.min_reference_obstacle_clearance_m:.6f}"
        )
    if min_truth_clearance is None:
        warnings.append("truth_obstacle_clearance_missing")
    elif min_truth_clearance < args.min_truth_obstacle_clearance_m:
        blockers.append(f"truth_clearance_below_min:{min_truth_clearance:.6f}<{args.min_truth_obstacle_clearance_m:.6f}")
    if tracker_xy_track["rmse_xy_m"] is None:
        blockers.append("xy_track_rmse_missing")
    elif float(tracker_xy_track["rmse_xy_m"]) > args.max_xy_track_rmse_m:
        blockers.append(
            f"xy_track_rmse_above_max:{float(tracker_xy_track['rmse_xy_m']):.6f}>"
            f"{args.max_xy_track_rmse_m:.6f}"
        )
    if tracker_xy_track["max_xy_error_m"] is None:
        blockers.append("xy_track_max_xy_error_missing")
    elif float(tracker_xy_track["max_xy_error_m"]) > args.max_xy_track_error_m:
        blockers.append(
            f"xy_track_max_xy_error_above_max:{float(tracker_xy_track['max_xy_error_m']):.6f}>"
            f"{args.max_xy_track_error_m:.6f}"
        )

    gate_passed = not blockers
    return {
        "schema": "mosim.figure8_static_obstacle_gate_eval.v1",
        "status": "passed" if gate_passed else "blocked",
        "gate_passed": gate_passed,
        "inputs": {
            "reference_report_json": rel(reference_report_path),
            "reference_trace_jsonl": rel(reference_trace_path),
            "tracker_report_json": rel(tracker_report_path),
            "tracker_trace_jsonl": rel(tracker_trace_path),
            "adapter_trace_jsonl": rel(adapter_trace_path),
            "truth_pose_jsonl": rel(truth_pose_path),
            "truth_summary_json": rel(truth_summary_path),
        },
        "counts": {
            "reference_samples": len(refs),
            "truth_samples": len(truth),
            "raw_truth_samples": len(raw_truth),
            "tracker_samples": len(tracker_trace),
            "adapter_published": adapter_published_count(adapter_trace),
            "matched_truth_reference_samples": len(matched_errors),
            "truth_summary_count": truth_summary.get("count"),
        },
        "truth_recording": {
            "truth_source": truth_source,
            "tracker_window_policy": tracker_window_policy,
            "reference_window_policy": reference_window_policy,
        },
        "duration_s": round(duration_s, 6),
        "tracking": {
            "rmse_3d_m": round(rmse_3d, 6) if rmse_3d is not None else None,
            "rmse_xy_m": round(rmse_xy, 6) if rmse_xy is not None else None,
            "max_xy_error_m": round(max_xy, 6) if max_xy is not None else None,
            "max_z_error_m": round(max_z, 6) if max_z is not None else None,
            "max_reference_time_delta_s": round(max_ref_time_delta, 6),
            "figure8_phase": {
                "sample_count": tracker_figure8_phase["sample_count"],
                "rmse_xy_m": round(float(tracker_figure8_phase["rmse_xy_m"]), 6)
                if tracker_figure8_phase["rmse_xy_m"] is not None
                else None,
                "max_xy_error_m": round(float(tracker_figure8_phase["max_xy_error_m"]), 6)
                if tracker_figure8_phase["max_xy_error_m"] is not None
                else None,
                "max_z_error_m": round(float(tracker_figure8_phase["max_z_error_m"]), 6)
                if tracker_figure8_phase["max_z_error_m"] is not None
                else None,
                "phase_source": tracker_figure8_phase["metric_source"],
                "independent_truth_reference_diagnostic": {
                    "sample_count": len(figure8_phase_xy_errors),
                    "rmse_xy_m": round(figure8_phase_rmse_xy, 6) if figure8_phase_rmse_xy is not None else None,
                    "max_xy_error_m": round(figure8_phase_max_xy, 6) if figure8_phase_max_xy is not None else None,
                    "max_z_error_m": round(figure8_phase_max_z, 6) if figure8_phase_max_z is not None else None,
                    "phase_source": "nearest_reference_sample_with_mission_phase_figure8",
                },
            },
            "xy_track_only": {
                "sample_count": tracker_xy_track["sample_count"],
                "rmse_xy_m": round(float(tracker_xy_track["rmse_xy_m"]), 6)
                if tracker_xy_track["rmse_xy_m"] is not None
                else None,
                "max_xy_error_m": round(float(tracker_xy_track["max_xy_error_m"]), 6)
                if tracker_xy_track["max_xy_error_m"] is not None
                else None,
                "max_z_error_m": round(float(tracker_xy_track["max_z_error_m"]), 6)
                if tracker_xy_track["max_z_error_m"] is not None
                else None,
                "saturation_count": tracker_xy_track["saturation_count"],
            },
        },
        "figure8_shape": {
            "reference_center_xy_m": [round(reference_center_xy[0], 6), round(reference_center_xy[1], 6)],
            "reference": reference_shape,
            "truth": truth_shape,
            "truth_path_length_ratio": round(truth_path_length_ratio, 6),
        },
        "mission_profile": {
            "reference": reference_mission,
            "reference_end_state": reference_end_state,
            "truth_end_state": truth_end_state,
            "truth_center_revisit": truth_center_revisit,
        },
        "obstacles_xy_radius": [list(item) for item in args.obstacle],
        "obstacle_clearance": {
            "reference_min_m": round(min_ref_clearance, 6) if min_ref_clearance is not None else None,
            "truth_min_m": round(min_truth_clearance, 6) if min_truth_clearance is not None else None,
        },
        "thresholds": {
            "min_reference_samples": args.min_reference_samples,
            "min_truth_samples": args.min_truth_samples,
            "min_tracker_samples": args.min_tracker_samples,
            "min_xy_track_samples": args.min_xy_track_samples,
            "min_adapter_samples": args.min_adapter_samples,
            "min_duration_s": args.min_duration_s,
            "max_xy_rmse_m": args.max_xy_rmse_m,
            "max_xy_error_m": args.max_xy_error_m,
            "max_z_error_m": args.max_z_error_m,
            "max_xy_track_rmse_m": args.max_xy_track_rmse_m,
            "max_xy_track_error_m": args.max_xy_track_error_m,
            "min_figure8_phase_samples": args.min_figure8_phase_samples,
            "max_figure8_phase_xy_rmse_m": args.max_figure8_phase_xy_rmse_m,
            "max_figure8_phase_xy_error_m": args.max_figure8_phase_xy_error_m,
            "max_figure8_phase_z_error_m": args.max_figure8_phase_z_error_m,
            "expected_figure8_span_x_m": args.expected_figure8_span_x_m,
            "expected_figure8_span_y_m": args.expected_figure8_span_y_m,
            "min_truth_span_x_m": args.min_truth_span_x_m,
            "min_truth_span_y_m": args.min_truth_span_y_m,
            "min_truth_path_length_ratio": args.min_truth_path_length_ratio,
            "min_lobe_fraction": args.min_lobe_fraction,
            "min_center_crossings_x": args.min_center_crossings_x,
            "required_mission_phase": args.required_mission_phase,
            "min_samples_per_required_phase": args.min_samples_per_required_phase,
            "min_figure8_trajectory_time_span_s": args.min_figure8_trajectory_time_span_s,
            "center_revisit_radius_m": args.center_revisit_radius_m,
            "min_center_revisit_entries": args.min_center_revisit_entries,
            "max_final_altitude_m": args.max_final_altitude_m,
            "max_landing_window_altitude_m": args.max_landing_window_altitude_m,
            "max_landing_window_xy_displacement_m": args.max_landing_window_xy_displacement_m,
            "min_reference_obstacle_clearance_m": args.min_reference_obstacle_clearance_m,
            "min_truth_obstacle_clearance_m": args.min_truth_obstacle_clearance_m,
        },
        "blockers": blockers,
        "warnings": warnings,
        "claim_boundary": [
            "bounded single-UAV Gazebo/ROS2 figure-8 plus static-obstacle pre-acceptance gate",
            "truth-feedback tracker and current Gazebo plant limitations mean this is not final competition controller-performance evidence",
            "no multi-UAV readiness, UE acceptance, or final plant closed-loop acceptance is claimed",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-report-json", required=True, type=Path)
    parser.add_argument("--reference-trace-jsonl", required=True, type=Path)
    parser.add_argument("--tracker-report-json", required=True, type=Path)
    parser.add_argument("--tracker-trace-jsonl", required=True, type=Path)
    parser.add_argument("--adapter-trace-jsonl", required=True, type=Path)
    parser.add_argument("--truth-pose-jsonl", required=True, type=Path)
    parser.add_argument("--truth-summary-json", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--obstacle", action="append", type=parse_obstacle, default=[])
    parser.add_argument("--min-reference-samples", type=int, default=100)
    parser.add_argument("--min-truth-samples", type=int, default=100)
    parser.add_argument("--min-tracker-samples", type=int, default=20)
    parser.add_argument("--min-xy-track-samples", type=int, default=50)
    parser.add_argument("--min-adapter-samples", type=int, default=20)
    parser.add_argument("--min-duration-s", type=float, default=8.0)
    parser.add_argument("--max-reference-time-delta-s", type=float, default=0.1)
    parser.add_argument("--max-xy-rmse-m", type=float, default=2.5)
    parser.add_argument("--max-xy-error-m", type=float, default=4.0)
    parser.add_argument("--max-z-error-m", type=float, default=1.25)
    parser.add_argument("--max-xy-track-rmse-m", type=float, default=0.12)
    parser.add_argument("--max-xy-track-error-m", type=float, default=0.25)
    parser.add_argument("--min-figure8-phase-samples", type=int, default=100)
    parser.add_argument("--max-figure8-phase-xy-rmse-m", type=float, default=0.20)
    parser.add_argument("--max-figure8-phase-xy-error-m", type=float, default=0.45)
    parser.add_argument("--max-figure8-phase-z-error-m", type=float, default=0.55)
    parser.add_argument("--expected-figure8-span-x-m", type=float, default=1.2)
    parser.add_argument("--expected-figure8-span-y-m", type=float, default=0.6)
    parser.add_argument("--min-truth-span-x-m", type=float, default=0.9)
    parser.add_argument("--min-truth-span-y-m", type=float, default=0.45)
    parser.add_argument("--min-truth-path-length-ratio", type=float, default=0.8)
    parser.add_argument("--min-lobe-fraction", type=float, default=0.18)
    parser.add_argument("--min-center-crossings-x", type=int, default=2)
    parser.add_argument(
        "--required-mission-phase",
        action="append",
        default=[
            "pre_takeoff_hold",
            "takeoff",
            "pre_figure8_hold",
            "figure8",
            "post_figure8_hold",
            "land",
            "post_land_hold",
        ],
    )
    parser.add_argument("--min-samples-per-required-phase", type=int, default=2)
    parser.add_argument("--min-figure8-trajectory-time-span-s", type=float, default=35.0)
    parser.add_argument("--center-revisit-radius-m", type=float, default=0.02)
    parser.add_argument("--min-center-revisit-entries", type=int, default=2)
    parser.add_argument("--max-final-altitude-m", type=float, default=0.20)
    parser.add_argument("--max-landing-window-altitude-m", type=float, default=0.25)
    parser.add_argument("--max-landing-window-xy-displacement-m", type=float, default=0.05)
    parser.add_argument("--min-reference-obstacle-clearance-m", type=float, default=0.35)
    parser.add_argument("--min-truth-obstacle-clearance-m", type=float, default=0.0)
    args = parser.parse_args()

    output = project_path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    report = build_report(args)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("gate_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
