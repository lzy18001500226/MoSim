#!/usr/bin/env python3
"""Compute standard quadrotor tracking metrics from a project CSV file."""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path


REQUIRED_COLUMNS = ["time", "x", "y", "z", "x_ref", "y_ref", "z_ref"]
MOTOR_COLUMNS = ["u1", "u2", "u3", "u4"]
ATTITUDE_COLUMNS = ["roll", "pitch", "yaw"]
DEFAULT_SETTLING_TOLERANCE_M = 0.10
DEFAULT_SETTLING_HOLD_S = 2.0
DEFAULT_MIN_ALTITUDE_M = 0.10
DEFAULT_MAX_TILT_RAD = math.radians(60.0)
DEFAULT_DISTURBANCE_START_S = 15.0
DEFAULT_DISTURBANCE_END_S = 19.0
DEFAULT_DISTURBANCE_RECOVERY_TOLERANCE_M = 0.20
DEFAULT_DISTURBANCE_RECOVERY_HOLD_S = 2.0
STEP_RESPONSE_TIME_S = 15.0
STEP_RESPONSE_EVALUATION_END_S = 45.0
STEP_RESPONSE_SETTLING_FRACTION = 0.05
STEP_RESPONSE_STEADY_STATE_START_S = 40.0
MOTOR_FAULT_TIME_S = 15.0


def parse_metrics_context(raw: str) -> dict[str, float]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"--metrics-context-json must be a JSON object: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("--metrics-context-json must be a JSON object")
    context: dict[str, float] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not isinstance(item, (int, float)) or isinstance(item, bool):
            raise ValueError("--metrics-context-json values must be finite numeric scalars")
        numeric = float(item)
        if not math.isfinite(numeric):
            raise ValueError("--metrics-context-json values must be finite numeric scalars")
        context[key] = numeric
    return context


def read_csv(path: Path) -> dict[str, list[float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        missing = [name for name in REQUIRED_COLUMNS if name not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns in {path}: {', '.join(missing)}")
        data = {name: [] for name in reader.fieldnames}
        for row in reader:
            for name in reader.fieldnames:
                value = row.get(name, "")
                data[name].append(float(value) if value != "" else math.nan)
        return data


def mean(values: list[float]) -> float:
    return math.nan if not values else sum(values) / len(values)


def rmse(values: list[float]) -> float:
    return math.sqrt(mean([value * value for value in values]))


def trapezoid_integral(time: list[float], values: list[float]) -> float:
    if len(time) < 2 or len(values) < 2:
        return math.nan
    total = 0.0
    for index in range(1, len(time)):
        dt = time[index] - time[index - 1]
        total += 0.5 * dt * (values[index] + values[index - 1])
    return total


def finite(values: list[float]) -> list[float]:
    return [value for value in values if not math.isnan(value) and not math.isinf(value)]


def max_or_nan(values: list[float]) -> float:
    filtered = finite(values)
    return max(filtered) if filtered else math.nan


def min_or_nan(values: list[float]) -> float:
    filtered = finite(values)
    return min(filtered) if filtered else math.nan


def derivative_energy(time: list[float], series_list: list[list[float]]) -> float:
    if len(time) < 2 or not series_list:
        return math.nan
    rate_norm_sq = []
    rate_time = []
    for index in range(1, len(time)):
        dt = time[index] - time[index - 1]
        if dt <= 0:
            continue
        total = 0.0
        valid = True
        for series in series_list:
            value = (series[index] - series[index - 1]) / dt
            if math.isnan(value) or math.isinf(value):
                valid = False
                break
            total += value * value
        if valid:
            rate_time.append(time[index])
            rate_norm_sq.append(total)
    return trapezoid_integral(rate_time, rate_norm_sq)


def settling_time(time: list[float], error: list[float], tolerance: float, hold_s: float) -> float:
    if not time or not error or len(time) != len(error):
        return math.nan
    for index, current_time in enumerate(time):
        hold_until = current_time + hold_s
        if hold_until > time[-1] + 1e-9:
            break
        window_ok = True
        for t, value in zip(time[index:], error[index:]):
            if t > hold_until + 1e-9:
                break
            if math.isnan(value) or value > tolerance:
                window_ok = False
                break
        if window_ok:
            return current_time - time[0]
    return math.nan


def disturbance_peak_error(time: list[float], error: list[float], start_s: float, end_s: float) -> float:
    values = [value for t, value in zip(time, error) if start_s <= t <= end_s and not math.isnan(value)]
    return max(values) if values else math.nan


def disturbance_recovery_time(
    time: list[float],
    error: list[float],
    end_s: float,
    tolerance: float,
    hold_s: float,
) -> float:
    if not time or not error or len(time) != len(error):
        return math.nan
    for index, current_time in enumerate(time):
        if current_time < end_s:
            continue
        hold_until = current_time + hold_s
        if hold_until > time[-1] + 1e-9:
            break
        window_ok = True
        for t, value in zip(time[index:], error[index:]):
            if t > hold_until + 1e-9:
                break
            if math.isnan(value) or value > tolerance:
                window_ok = False
                break
        if window_ok:
            return current_time - end_s
    return math.nan


def axis_overshoot(response: list[float], reference: list[float]) -> float:
    if len(response) < 2 or len(reference) < 2:
        return math.nan
    initial = reference[0]
    target = reference[-1]
    amplitude = target - initial
    if abs(amplitude) < 1e-9:
        return math.nan
    direction = 1.0 if amplitude > 0 else -1.0
    peak = max(direction * (value - initial) for value in response)
    overshoot = max(0.0, peak - abs(amplitude))
    return 100.0 * overshoot / abs(amplitude)


def windowed(time: list[float], values: list[float], start_s: float, end_s: float) -> list[float]:
    """Return finite samples whose timestamps are inside the inclusive window."""
    return [
        value
        for current_time, value in zip(time, values)
        if start_s - 1e-9 <= current_time <= end_s + 1e-9
        and math.isfinite(value)
    ]


def value_before(time: list[float], values: list[float], event_time_s: float) -> float:
    candidates = [
        value
        for current_time, value in zip(time, values)
        if current_time < event_time_s - 1e-9 and math.isfinite(value)
    ]
    return candidates[-1] if candidates else math.nan


def value_at_or_after(time: list[float], values: list[float], event_time_s: float) -> float:
    for current_time, value in zip(time, values):
        if current_time >= event_time_s - 1e-9 and math.isfinite(value):
            return value
    return math.nan


def signed_step_overshoot_percent(
    time: list[float],
    response: list[float],
    reference: list[float],
    step_time_s: float,
    evaluation_end_s: float,
) -> float:
    """Overshoot relative to the signed XY step defined by the reference."""
    initial_ref = value_before(time, reference, step_time_s)
    target_ref = value_at_or_after(time, reference, step_time_s)
    amplitude = target_ref - initial_ref
    if not math.isfinite(amplitude) or abs(amplitude) < 1e-9:
        return math.nan
    direction = 1.0 if amplitude > 0 else -1.0
    responses = windowed(time, response, step_time_s, evaluation_end_s)
    if not responses:
        return math.nan
    signed_peak = max(direction * (value - initial_ref) for value in responses)
    return 100.0 * max(0.0, signed_peak - abs(amplitude)) / abs(amplitude)


def persistent_step_settling_time(
    time: list[float],
    x: list[float],
    y: list[float],
    x_ref: list[float],
    y_ref: list[float],
    step_time_s: float,
    evaluation_end_s: float,
    fraction: float,
) -> float:
    """Return first post-step time where both XY axes remain inside their 5% bands."""
    x_initial = value_before(time, x_ref, step_time_s)
    y_initial = value_before(time, y_ref, step_time_s)
    x_target = value_at_or_after(time, x_ref, step_time_s)
    y_target = value_at_or_after(time, y_ref, step_time_s)
    x_band = fraction * abs(x_target - x_initial)
    y_band = fraction * abs(y_target - y_initial)
    if not all(math.isfinite(value) for value in (x_band, y_band, x_target, y_target)):
        return math.nan
    if x_band <= 0 or y_band <= 0:
        return math.nan

    post_indices = [
        index
        for index, current_time in enumerate(time)
        if step_time_s - 1e-9 <= current_time <= evaluation_end_s + 1e-9
    ]
    if not post_indices:
        return math.nan
    for index in post_indices:
        remains_inside = True
        for later_index in post_indices:
            if later_index < index:
                continue
            if (
                not math.isfinite(x[later_index])
                or not math.isfinite(y[later_index])
                or abs(x[later_index] - x_target) > x_band + 1e-9
                or abs(y[later_index] - y_target) > y_band + 1e-9
            ):
                remains_inside = False
                break
        if remains_inside:
            return time[index] - step_time_s
    return math.nan


def compute_step_response_metrics(
    time: list[float],
    x: list[float],
    y: list[float],
    x_ref: list[float],
    y_ref: list[float],
    position_error: list[float],
) -> dict[str, float]:
    """Compute the competition step metrics using the frozen 15--45 s contract."""
    steady_state = windowed(
        time,
        position_error,
        STEP_RESPONSE_STEADY_STATE_START_S,
        STEP_RESPONSE_EVALUATION_END_S,
    )
    overshoot_x = signed_step_overshoot_percent(
        time, x, x_ref, STEP_RESPONSE_TIME_S, STEP_RESPONSE_EVALUATION_END_S
    )
    overshoot_y = signed_step_overshoot_percent(
        time, y, y_ref, STEP_RESPONSE_TIME_S, STEP_RESPONSE_EVALUATION_END_S
    )
    return {
        "overshoot_percent_x": overshoot_x,
        "overshoot_percent_y": overshoot_y,
        "settling_time_s": persistent_step_settling_time(
            time,
            x,
            y,
            x_ref,
            y_ref,
            STEP_RESPONSE_TIME_S,
            STEP_RESPONSE_EVALUATION_END_S,
            STEP_RESPONSE_SETTLING_FRACTION,
        ),
        "steady_state_error_m": mean(steady_state),
        "step_response_time_s": STEP_RESPONSE_TIME_S,
        "step_response_evaluation_end_s": STEP_RESPONSE_EVALUATION_END_S,
        "step_response_settling_fraction": STEP_RESPONSE_SETTLING_FRACTION,
    }


def score_lower_better(value: float, target: float, fail: float) -> float:
    if math.isnan(value) or math.isinf(value):
        return 0.0
    if value <= target:
        return 100.0
    if value >= fail:
        return 0.0
    return 100.0 * (fail - value) / (fail - target)


def score_higher_better(value: float, target: float, fail: float) -> float:
    if math.isnan(value) or math.isinf(value):
        return 0.0
    if value >= target:
        return 100.0
    if value <= fail:
        return 0.0
    return 100.0 * (value - fail) / (target - fail)


def compute_health_scores(metrics: dict[str, object]) -> dict[str, float]:
    tracking_score = (
        0.50 * score_lower_better(float(metrics["position_rmse_m"]), 0.15, 2.0)
        + 0.30 * score_lower_better(float(metrics["max_position_error_m"]), 0.30, 5.0)
        + 0.20 * score_lower_better(float(metrics["steady_state_error_m"]), 0.10, 1.5)
    )
    safety_score = (
        0.45 * score_higher_better(float(metrics["minimum_altitude_m"]), 0.50, 0.10)
        + 0.35 * score_lower_better(float(metrics["max_tilt_rad"]), math.radians(25.0), math.radians(60.0))
        + 0.20 * score_lower_better(float(metrics["constraint_violation_count"]), 0.0, 10.0)
    )
    energy_score = (
        0.55 * score_lower_better(float(metrics["saturation_ratio"]), 0.10, 0.80)
        + 0.45 * score_lower_better(float(metrics["control_energy"]), 1.0, 200.0)
    )
    smoothness_score = score_lower_better(float(metrics["control_smoothness"]), 1.0, 500.0)
    robustness_score = score_lower_better(float(metrics["settling_time_s"]), 2.0, 15.0)
    fault_tolerance_score = safety_score
    total = (
        0.30 * tracking_score
        + 0.25 * robustness_score
        + 0.20 * safety_score
        + 0.10 * energy_score
        + 0.05 * smoothness_score
        + 0.10 * fault_tolerance_score
    )
    return {
        "tracking_score": tracking_score,
        "robustness_score": robustness_score,
        "safety_score": safety_score,
        "energy_score": energy_score,
        "smoothness_score": smoothness_score,
        "fault_tolerance_score": fault_tolerance_score,
        "total_health_score": total,
    }


def compute_formation_metrics(data: dict[str, list[float]]) -> dict[str, object]:
    formation_keys = [
        "formation_error_m",
        "follower1_formation_error_m",
        "follower2_formation_error_m",
        "min_inter_uav_distance_m",
    ]
    if not any(key in data for key in formation_keys):
        return {}

    metrics: dict[str, object] = {}
    if "formation_error_m" in data:
        formation_error = finite(data["formation_error_m"])
        metrics["formation_error_rmse_m"] = rmse(formation_error)
        metrics["formation_error_max_m"] = max_or_nan(formation_error)
        metrics["formation_keeping_rate"] = (
            sum(1 for value in formation_error if value <= 0.35) / len(formation_error)
            if formation_error
            else math.nan
        )
    if "follower1_formation_error_m" in data:
        values = finite(data["follower1_formation_error_m"])
        metrics["follower1_formation_error_rmse_m"] = rmse(values)
        metrics["follower1_formation_error_max_m"] = max_or_nan(values)
    if "follower2_formation_error_m" in data:
        values = finite(data["follower2_formation_error_m"])
        metrics["follower2_formation_error_rmse_m"] = rmse(values)
        metrics["follower2_formation_error_max_m"] = max_or_nan(values)
    if "min_inter_uav_distance_m" in data:
        metrics["min_inter_uav_distance_m"] = min_or_nan(data["min_inter_uav_distance_m"])

    if "formation_error_rmse_m" in metrics and "min_inter_uav_distance_m" in metrics:
        metrics["formation_score"] = (
            0.65 * score_lower_better(float(metrics["formation_error_rmse_m"]), 0.20, 0.80)
            + 0.35 * score_higher_better(float(metrics["min_inter_uav_distance_m"]), 0.80, 0.35)
        )
    return metrics


def to_jsonable(value: object) -> object:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def to_csv_value(value: object) -> object:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return ""
    return value


def compute_metrics(
    data: dict[str, list[float]],
    raw_file: Path,
    scene_id: str,
    controller_id: str,
    metrics_context: dict[str, float] | None = None,
) -> dict[str, object]:
    context = metrics_context or {}
    time = data["time"]
    if not time:
        raise ValueError(f"Metrics input has no data rows: {raw_file}")
    duration_s = (max(time) - min(time)) if time else math.nan
    ex = [x - xr for x, xr in zip(data["x"], data["x_ref"])]
    ey = [y - yr for y, yr in zip(data["y"], data["y_ref"])]
    ez = [z - zr for z, zr in zip(data["z"], data["z_ref"])]
    ep = [math.sqrt(x * x + y * y + z * z) for x, y, z in zip(ex, ey, ez)]

    if time:
        final_window_start = max(time) - max(5.0, 0.2 * (max(time) - min(time)))
        final_error = [error for t, error in zip(time, ep) if t >= final_window_start]
        tail_error = [error for t, error in zip(time, ep) if t >= max(time) - 5.0]
    else:
        final_error = []
        tail_error = []

    motor_cols = [name for name in MOTOR_COLUMNS if name in data]
    control_norm_sq = []
    saturation_samples = 0
    motor_values = []
    if motor_cols:
        for index in range(len(time)):
            total = 0.0
            for name in motor_cols:
                value = data[name][index]
                motor_values.append(value)
                total += value * value
            control_norm_sq.append(total)
        normalized_motor_commands = all(
            not math.isnan(value) and not math.isinf(value) and -1e-9 <= value <= 1.0 + 1e-9
            for value in motor_values
        )
        if normalized_motor_commands:
            saturation_samples = sum(1 for value in motor_values if value <= 1e-9 or value >= 1.0 - 1e-9)
    else:
        normalized_motor_commands = False

    control_energy = trapezoid_integral(time, control_norm_sq) if control_norm_sq else math.nan
    control_smoothness = derivative_energy(time, [data[name] for name in motor_cols]) if motor_cols else math.nan

    attitude_cols = [name for name in ATTITUDE_COLUMNS if name in data]
    tilt = []
    if "roll" in data and "pitch" in data:
        tilt = [math.sqrt(roll * roll + pitch * pitch) for roll, pitch in zip(data["roll"], data["pitch"])]

    altitude = data["z"]
    min_altitude = min_or_nan(altitude)
    max_tilt = max_or_nan(tilt) if tilt else math.nan
    altitude_violations = sum(1 for value in altitude if not math.isnan(value) and value < DEFAULT_MIN_ALTITUDE_M)
    tilt_violations = sum(1 for value in tilt if not math.isnan(value) and value > DEFAULT_MAX_TILT_RAD)
    constraint_violation_count = altitude_violations + tilt_violations

    nan_count = sum(1 for values in data.values() for value in values if math.isnan(value))
    metrics = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "raw_file": str(raw_file),
        "scene_id": scene_id,
        "controller_id": controller_id,
        "row_count": len(time),
        "duration_s": duration_s,
        "sample_rate_hz": (len(time) - 1) / duration_s if duration_s and duration_s > 0 and len(time) > 1 else math.nan,
        "position_rmse_m": rmse(ep),
        "x_rmse_m": rmse(ex),
        "y_rmse_m": rmse(ey),
        "z_rmse_m": rmse(ez),
        "xy_rmse_m": rmse([math.sqrt(x * x + y * y) for x, y in zip(ex, ey)]),
        "max_position_error_m": max(ep) if ep else math.nan,
        "steady_state_error_m": mean(final_error),
        "tail_rmse_m": rmse(tail_error),
        "terminal_position_error_m": ep[-1] if ep else math.nan,
        "settling_time_s": settling_time(time, ep, DEFAULT_SETTLING_TOLERANCE_M, DEFAULT_SETTLING_HOLD_S),
        "disturbance_window_start_s": DEFAULT_DISTURBANCE_START_S,
        "disturbance_window_end_s": DEFAULT_DISTURBANCE_END_S,
        "disturbance_peak_error_m": disturbance_peak_error(
            time,
            ep,
            DEFAULT_DISTURBANCE_START_S,
            DEFAULT_DISTURBANCE_END_S,
        ),
        "disturbance_recovery_time_s": disturbance_recovery_time(
            time,
            ep,
            DEFAULT_DISTURBANCE_END_S,
            DEFAULT_DISTURBANCE_RECOVERY_TOLERANCE_M,
            DEFAULT_DISTURBANCE_RECOVERY_HOLD_S,
        ),
        "overshoot_x_pct": axis_overshoot(data["x"], data["x_ref"]),
        "overshoot_y_pct": axis_overshoot(data["y"], data["y_ref"]),
        "overshoot_z_pct": axis_overshoot(data["z"], data["z_ref"]),
        "overshoot_max_pct": max_or_nan([
            axis_overshoot(data["x"], data["x_ref"]),
            axis_overshoot(data["y"], data["y_ref"]),
            axis_overshoot(data["z"], data["z_ref"]),
        ]),
        "roll_rmse_rad": rmse(data["roll"]) if "roll" in data else math.nan,
        "pitch_rmse_rad": rmse(data["pitch"]) if "pitch" in data else math.nan,
        "yaw_rmse_rad": rmse(data["yaw"]) if "yaw" in data else math.nan,
        "max_tilt_rad": max_tilt,
        "minimum_altitude_m": min_altitude,
        "altitude_violation_count": altitude_violations,
        "tilt_violation_count": tilt_violations,
        "constraint_violation_count": constraint_violation_count,
        "constraint_violation_rate_hz": constraint_violation_count / duration_s if duration_s and duration_s > 0 else math.nan,
        "altitude_violation_rate_hz": altitude_violations / duration_s if duration_s and duration_s > 0 else math.nan,
        "tilt_violation_rate_hz": tilt_violations / duration_s if duration_s and duration_s > 0 else math.nan,
        "control_energy": control_energy,
        "control_energy_per_second": control_energy / duration_s if duration_s and duration_s > 0 else math.nan,
        "control_smoothness": control_smoothness,
        "control_smoothness_per_second": control_smoothness / duration_s if duration_s and duration_s > 0 else math.nan,
        "control_command_min": min_or_nan(motor_values) if motor_values else math.nan,
        "control_command_max": max_or_nan(motor_values) if motor_values else math.nan,
        "control_command_normalized": normalized_motor_commands,
        "saturation_ratio": saturation_samples / (len(time) * len(motor_cols))
        if motor_cols and normalized_motor_commands and time
        else math.nan,
        "nan_count": nan_count,
        "valid": len(time) > 10 and nan_count == 0,
        "scenario_metric_context": context,
    }
    if scene_id == "step_response":
        metrics.update(
            compute_step_response_metrics(
                time,
                data["x"],
                data["y"],
                data["x_ref"],
                data["y_ref"],
                ep,
            )
        )
    else:
        metrics.update(
            {
                "overshoot_percent_x": math.nan,
                "overshoot_percent_y": math.nan,
                "step_response_time_s": math.nan,
                "step_response_evaluation_end_s": math.nan,
                "step_response_settling_fraction": math.nan,
            }
        )

    if scene_id == "wind_disturbance":
        disturbance_start_s = context.get("gust_start_s", 0.0)
        disturbance_duration_s = context.get("gust_duration_s", 50.0)
        disturbance_end_s = min(disturbance_start_s + disturbance_duration_s, max(time))
        metrics["disturbance_window_rmse_m"] = rmse(
            windowed(time, ep, disturbance_start_s, disturbance_end_s)
        )
        metrics["disturbance_window_start_s"] = disturbance_start_s
        metrics["disturbance_window_end_s"] = disturbance_end_s
    else:
        metrics["disturbance_window_rmse_m"] = math.nan

    if scene_id == "motor_efficiency_fault":
        fault_start_s = context.get("fault_start_s", MOTOR_FAULT_TIME_S)
        pre_fault_error = [
            error
            for current_time, error in zip(time, ep)
            if current_time < fault_start_s - 1e-9 and math.isfinite(error)
        ]
        post_fault_error = windowed(time, ep, fault_start_s, max(time))
        metrics.update(
            {
                "fault_start_s": fault_start_s,
                "pre_fault_rmse_m": rmse(pre_fault_error),
                "post_fault_rmse_m": rmse(post_fault_error),
                "post_fault_peak_error_m": max_or_nan(post_fault_error),
            }
        )
    else:
        metrics.update(
            {
                "fault_start_s": math.nan,
                "pre_fault_rmse_m": math.nan,
                "post_fault_rmse_m": math.nan,
                "post_fault_peak_error_m": math.nan,
            }
        )
    metrics.update(compute_health_scores(metrics))
    metrics.update(compute_formation_metrics(data))
    return metrics


def write_outputs(metrics: dict[str, object], json_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_metrics = {key: to_jsonable(value) for key, value in metrics.items()}
    json_path.write_text(json.dumps(json_metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    csv_path = json_path.with_suffix(".csv")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["metric", "value"])
        for key in sorted(metrics):
            writer.writerow([key, to_csv_value(metrics[key])])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_csv", type=Path)
    parser.add_argument("metrics_json", type=Path)
    parser.add_argument("scene_id", nargs="?", default=None)
    parser.add_argument("controller_id", nargs="?", default="unknown")
    parser.add_argument(
        "--metrics-context-json",
        default="{}",
        help="Optional JSON object with profile-driven metric windows such as gust_start_s.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scene_id = args.scene_id or args.raw_csv.stem
    data = read_csv(args.raw_csv)
    metrics = compute_metrics(
        data,
        args.raw_csv,
        scene_id,
        args.controller_id,
        parse_metrics_context(args.metrics_context_json),
    )
    write_outputs(metrics, args.metrics_json)
    print(f"Metrics written: {args.metrics_json}")
    print(f"Metrics CSV: {args.metrics_json.with_suffix('.csv')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
