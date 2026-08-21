#!/usr/bin/env python3
"""Evaluate whether a finished MWORKS scenario is good enough or needs iteration."""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from run_mworks_scenario import ROOT, default_result_base, read_yaml
except ImportError:  # pragma: no cover
    ROOT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(ROOT / "Scripts" / "mworks"))
    from run_mworks_scenario import default_result_base, read_yaml  # type: ignore


PASS_STATUSES = {"pass", "smoke_only"}
DEFAULT_FAULT_INDEX_START_S = 5.0
DEFAULT_MIN_FAULT_INDEX_ACCURACY = 0.95

SCENE_THRESHOLDS: dict[str, dict[str, float]] = {
    "official_example1": {
        "max_position_rmse_m": 0.35,
        "max_position_error_m": 1.60,
        "min_total_health_score": 45.0,
        "max_tilt_rad": 0.45,
    },
    "official_example2": {
        "max_position_rmse_m": 0.55,
        "max_position_error_m": 3.20,
        "min_total_health_score": 45.0,
        "max_tilt_rad": 0.45,
    },
    "official_example3": {
        "max_position_rmse_m": 0.25,
        "max_position_error_m": 1.30,
        "min_total_health_score": 55.0,
        "max_tilt_rad": 0.45,
    },
    "robust_mass20_example1": {
        "max_position_rmse_m": 0.35,
        "max_position_error_m": 1.60,
        "min_total_health_score": 45.0,
        "max_tilt_rad": 0.45,
    },
    "robust_wind_gust_example1": {
        "max_position_rmse_m": 0.40,
        "max_position_error_m": 1.60,
        "min_total_health_score": 45.0,
        "max_tilt_rad": 0.45,
    },
    "robust_rotor1_loss15_example1": {
        "max_position_rmse_m": 0.45,
        "max_position_error_m": 1.60,
        "min_total_health_score": 40.0,
        "max_tilt_rad": 0.45,
    },
    "robust_rotor2_loss15_example1": {
        "max_position_rmse_m": 0.45,
        "max_position_error_m": 1.60,
        "min_total_health_score": 40.0,
        "max_tilt_rad": 0.45,
    },
    "robust_rotor3_loss15_example1": {
        "max_position_rmse_m": 0.45,
        "max_position_error_m": 1.60,
        "min_total_health_score": 40.0,
        "max_tilt_rad": 0.45,
    },
    "robust_rotor4_loss15_example1": {
        "max_position_rmse_m": 0.45,
        "max_position_error_m": 1.60,
        "min_total_health_score": 40.0,
        "max_tilt_rad": 0.45,
    },
}

DEFAULT_THRESHOLDS = {
    "max_position_rmse_m": 1.00,
    "max_position_error_m": 3.50,
    "min_total_health_score": 45.0,
    "max_tilt_rad": 0.60,
}


def as_float(value: Any) -> float:
    try:
        if value is None or value == "":
            return math.nan
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def repo_path(value: Any) -> Path:
    path = Path(str(value))
    return path if path.is_absolute() else ROOT / path


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def scenario_metrics_path(config: dict[str, Any], scenario_path: Path) -> Path:
    result = config.get("result", {})
    if isinstance(result, dict) and result.get("metrics_file"):
        return repo_path(result["metrics_file"])
    experiment_id = str(config.get("experiment_id", scenario_path.stem))
    return ROOT / default_result_base(config, experiment_id) / "metrics" / f"{experiment_id}.json"


def scenario_raw_path(config: dict[str, Any], metrics: dict[str, Any]) -> Path | None:
    result = config.get("result", {})
    if isinstance(result, dict) and result.get("raw_file"):
        return repo_path(result["raw_file"])
    if metrics.get("raw_file"):
        return repo_path(metrics["raw_file"])
    return None


def find_baseline_metrics(baseline_experiment: str) -> Path | None:
    if not baseline_experiment:
        return None

    for scenario_path in sorted((ROOT / "Config" / "scenarios").glob("**/*.yaml")):
        try:
            config = read_yaml(scenario_path)
        except Exception:
            continue
        if str(config.get("experiment_id", "")) != baseline_experiment:
            continue
        result = config.get("result", {})
        if isinstance(result, dict) and result.get("metrics_file"):
            path = repo_path(result["metrics_file"])
            if path.exists():
                return path

    matches = sorted((ROOT / "Results").glob(f"**/{baseline_experiment}/metrics/{baseline_experiment}.json"))
    return matches[0] if matches else None


def get_baseline_experiment(config: dict[str, Any]) -> str:
    controller = config.get("controller", {})
    if isinstance(controller, dict):
        if controller.get("require_baseline_improvement") is False:
            return ""
        explicit = str(controller.get("baseline_experiment", "") or "")
        if explicit:
            return explicit
    controller_id = str(config.get("controller_id", ""))
    scene_id = str(config.get("scene_id", ""))
    experiment_id = str(config.get("experiment_id", ""))
    if controller_id in {"", "pid_baseline"} or experiment_id.endswith("_pid_baseline"):
        return ""
    if scene_id.startswith("official_example") or scene_id.startswith("robust_"):
        return f"{scene_id}_pid_baseline"
    return ""


def corr(values: list[float], refs: list[float]) -> float:
    if len(values) < 2 or len(refs) < 2:
        return math.nan
    mean_v = sum(values) / len(values)
    mean_r = sum(refs) / len(refs)
    var_v = sum((value - mean_v) ** 2 for value in values)
    var_r = sum((value - mean_r) ** 2 for value in refs)
    if var_v <= 1e-18 or var_r <= 1e-18:
        return math.nan
    return sum((value - mean_v) * (ref - mean_r) for value, ref in zip(values, refs)) / math.sqrt(var_v * var_r)


def sign_changes(values: list[float], eps: float = 0.03) -> int:
    last = 0
    count = 0
    for value in values:
        sign = 1 if value > eps else -1 if value < -eps else 0
        if sign and last and sign != last:
            count += 1
        if sign:
            last = sign
    return count


def figure8_shape_quality(raw_path: Path) -> tuple[bool, dict[str, float]]:
    with raw_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows or not {"x", "y", "x_ref", "y_ref"}.issubset(rows[0].keys()):
        return False, {"figure8_xy_rmse_m": math.nan}

    x: list[float] = []
    y: list[float] = []
    xr: list[float] = []
    yr: list[float] = []
    for row in rows:
        try:
            values = [float(row[name]) for name in ["x", "y", "x_ref", "y_ref"]]
        except (TypeError, ValueError):
            continue
        x.append(values[0])
        y.append(values[1])
        xr.append(values[2])
        yr.append(values[3])

    active = [index for index, (x_ref, y_ref) in enumerate(zip(xr, yr)) if abs(x_ref) > 0.03 or abs(y_ref) > 0.03]
    if len(active) < 100:
        return False, {"figure8_xy_rmse_m": math.nan}

    xs = [x[index] for index in active]
    ys = [y[index] for index in active]
    xrs = [xr[index] for index in active]
    yrs = [yr[index] for index in active]
    xy_rmse = math.sqrt(sum((a - b) ** 2 + (c - d) ** 2 for a, b, c, d in zip(xs, xrs, ys, yrs)) / len(xs))
    corr_x = corr(xs, xrs)
    corr_y = corr(ys, yrs)
    act_x_range = max(xs) - min(xs)
    act_y_range = max(ys) - min(ys)
    ref_x_range = max(xrs) - min(xrs)
    ref_y_range = max(yrs) - min(yrs)
    act_x_cross = sign_changes(xs)
    left = sum(1 for value in xs if value < -0.05)
    right = sum(1 for value in xs if value > 0.05)
    passed = (
        ref_x_range > 10.0
        and ref_y_range > 10.0
        and act_x_range > 10.0
        and act_y_range > 10.0
        and corr_x > 0.98
        and corr_y > 0.98
        and xy_rmse < 1.0
        and act_x_cross >= 2
        and left > 1000
        and right > 1000
    )
    return passed, {
        "figure8_xy_rmse_m": xy_rmse,
        "figure8_corr_x": corr_x,
        "figure8_corr_y": corr_y,
        "figure8_x_crossings": float(act_x_cross),
        "figure8_act_x_range_m": act_x_range,
        "figure8_act_y_range_m": act_y_range,
    }


def fault_index_quality(
    raw_path: Path,
    *,
    expected_fault_index: int,
    start_s: float = DEFAULT_FAULT_INDEX_START_S,
) -> dict[str, float]:
    with raw_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or "time" not in reader.fieldnames or "fault_index" not in reader.fieldnames:
            return {
                "fault_index_expected": float(expected_fault_index),
                "fault_index_accuracy": math.nan,
                "fault_index_samples": 0.0,
                "fault_index_last": math.nan,
            }
        values: list[float] = []
        for row in reader:
            try:
                t = float(row["time"])
                fault_index = float(row["fault_index"])
            except (TypeError, ValueError):
                continue
            if t >= start_s and math.isfinite(fault_index):
                values.append(fault_index)

    if not values:
        return {
            "fault_index_expected": float(expected_fault_index),
            "fault_index_accuracy": math.nan,
            "fault_index_samples": 0.0,
            "fault_index_last": math.nan,
        }
    matches = sum(1 for value in values if int(round(value)) == expected_fault_index)
    return {
        "fault_index_expected": float(expected_fault_index),
        "fault_index_accuracy": matches / len(values),
        "fault_index_samples": float(len(values)),
        "fault_index_last": values[-1],
    }


def collect_raw_values(raw_path: Path, key: str) -> list[float]:
    with raw_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or key not in reader.fieldnames:
            return []
        values: list[float] = []
        for row in reader:
            value = as_float(row.get(key))
            if math.isfinite(value):
                values.append(value)
        return values


def has_rounded_code(values: list[float], expected: int) -> bool:
    return any(int(round(value)) == expected for value in values if math.isfinite(value))


SYSTEM_MODE_EXPECTATIONS: dict[str, dict[str, Any]] = {
    "system_gps_dropout": {
        "trigger": "degraded_nav_active",
        "expected_source": 90,
        "expected_safety": 3,
        "expected_event": 60,
        "extra_required": ["gps_valid"],
    },
    "system_battery_low": {
        "trigger": "battery_low_active",
        "expected_source": 91,
        "expected_safety": 4,
        "expected_event": 61,
        "extra_required": ["voltage_margin"],
    },
    "system_offboard_loss": {
        "trigger": "offboard_loss_active",
        "expected_source": 92,
        "expected_safety": 5,
        "expected_event": 62,
        "extra_required": [],
    },
    "system_mission_failure": {
        "trigger": "mission_failure_active",
        "expected_source": 93,
        "expected_safety": 6,
        "expected_event": 63,
        "extra_required": [],
    },
    "system_geofence_breach": {
        "trigger": "geofence_breach_active",
        "expected_source": 94,
        "expected_safety": 7,
        "expected_event": 64,
        "extra_required": [],
    },
}


def system_mode_quality(raw_path: Path | None, scene_id: str = "") -> tuple[list[str], list[str], dict[str, float]]:
    issues: list[str] = []
    recommendations: list[str] = []
    metrics: dict[str, float] = {}

    if raw_path is None or not raw_path.exists():
        return (
            ["system_mode quality requested but raw result is missing"],
            ["rerun the system scenario and export trigger_active, flight_mode, active_setpoint_source, safety_status, and event_code"],
            metrics,
        )

    expectation = SYSTEM_MODE_EXPECTATIONS.get(scene_id, SYSTEM_MODE_EXPECTATIONS["system_gps_dropout"])
    trigger_key = str(expectation["trigger"])
    expected_source = int(expectation["expected_source"])
    expected_safety = int(expectation["expected_safety"])
    expected_event = int(expectation["expected_event"])
    required = [
        trigger_key,
        "flight_mode",
        "event_code",
        *list(expectation.get("extra_required", [])),
    ]
    values_by_key = {key: collect_raw_values(raw_path, key) for key in required}
    for key, values in values_by_key.items():
        if not values:
            issues.append(f"{key} missing or has no valid samples")
            continue
        metrics[f"{key}_min"] = min(values)
        metrics[f"{key}_max"] = max(values)

    trigger_values = values_by_key.get(trigger_key, [])
    mode_values = values_by_key.get("flight_mode", [])
    event_values = values_by_key.get("event_code", [])

    if scene_id == "system_gps_dropout":
        gps_values = values_by_key.get("gps_valid", [])
        if gps_values and not (min(gps_values) <= 0.1 and max(gps_values) >= 0.9):
            issues.append("gps_valid does not show both healthy and dropout states")
    if scene_id == "system_battery_low":
        voltage_margin_values = values_by_key.get("voltage_margin", [])
        if voltage_margin_values and not (min(voltage_margin_values) <= 0.1 and max(voltage_margin_values) >= 0.9):
            issues.append("voltage_margin does not cross the low-battery threshold")
    if trigger_values and not has_rounded_code(trigger_values, 1):
        issues.append(f"{trigger_key} did not enter active state 1")
    if mode_values and not has_rounded_code(mode_values, 6):
        issues.append("flight_mode did not enter return/failsafe mode 6")
    if event_values and not has_rounded_code(event_values, expected_event):
        issues.append(f"event_code did not reach expected code {expected_event}")
    if event_values and has_rounded_code(event_values, expected_event):
        metrics["active_setpoint_source_inferred"] = float(expected_source)
        metrics["safety_status_inferred"] = float(expected_safety)

    if issues:
        recommendations.append(
            "inspect system supervisor equations and exported variables before using this scenario as failsafe evidence"
        )
    else:
        recommendations.append(f"system-mode evidence reached trigger={trigger_key}, source={expected_source}, safety={expected_safety}, event={expected_event}")

    return issues, recommendations, metrics


def formation_quality(metrics: dict[str, Any]) -> tuple[list[str], list[str]]:
    checks = [
        ("formation_error_rmse_m", "max", 0.35),
        ("formation_error_max_m", "max", 1.00),
        ("min_inter_uav_distance_m", "min", 0.80),
        ("formation_score", "min", 60.0),
    ]
    issues: list[str] = []
    for key, direction, limit in checks:
        value = as_float(metrics.get(key))
        if not math.isfinite(value):
            issues.append(f"{key} missing or non-finite")
            continue
        if direction == "max" and value > limit:
            issues.append(f"{key}={value:.6g} exceeds {limit:.6g}")
        if direction == "min" and value < limit:
            issues.append(f"{key}={value:.6g} below {limit:.6g}")
    if issues:
        return issues, ["retune follower offsets/controllers or inspect follower signal export before using formation evidence"]
    return [], ["formation evidence meets current keeping and separation gates"]


def planning_display_collision_quality(config: dict[str, Any]) -> dict[str, Any]:
    model = config.get("model", {})
    if not isinstance(model, dict):
        return {"ok": True, "skipped": True, "reason": "missing model mapping"}
    model_path = model.get("model_path_hint")
    if not model_path:
        return {"ok": True, "skipped": True, "reason": "missing model_path_hint"}
    path = repo_path(model_path)
    if not path.exists():
        return {"ok": False, "skipped": False, "reason": f"model file missing: {path.relative_to(ROOT)}"}

    checker = ROOT / "Scripts" / "planning" / "check_planning_display_collision.py"
    if not checker.exists():
        return {"ok": False, "skipped": False, "reason": "collision checker missing"}
    display_config = config.get("planning_display", {})
    clearance_m = 0.35
    if isinstance(display_config, dict):
        clearance_m = as_float(display_config.get("collision_clearance_m", clearance_m))
        if not math.isfinite(clearance_m) or clearance_m <= 0.0:
            clearance_m = 0.35
    completed = subprocess.run(
        [
            sys.executable,
            str(checker),
            str(path),
            "--required-clearance-m",
            f"{clearance_m:g}",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return {
        "ok": completed.returncode == 0,
        "skipped": False,
        "reason": completed.stdout.strip(),
    }


def evaluate_quality(config: dict[str, Any], scenario_path: Path, *, min_rmse_improvement_pct: float) -> dict[str, Any]:
    experiment_id = str(config.get("experiment_id", scenario_path.stem))
    scene_id = str(config.get("scene_id", ""))
    controller_id = str(config.get("controller_id", ""))
    priority = str(config.get("priority", ""))
    evidence_level = str(config.get("evidence_level", ""))
    metrics_path = scenario_metrics_path(config, scenario_path)

    result: dict[str, Any] = {
        "quality_checked_at": datetime.now().isoformat(timespec="seconds"),
        "quality_experiment_id": experiment_id,
        "quality_scene_id": scene_id,
        "quality_controller_id": controller_id,
        "quality_status": "invalid",
        "quality_pass": False,
        "quality_issues": [],
        "quality_recommendations": [],
    }

    if not metrics_path.exists():
        result["quality_issues"].append(f"missing metrics file: {metrics_path.relative_to(ROOT)}")
        result["quality_recommendations"].append("rerun simulation and metrics export before judging performance")
        return result

    metrics = read_json(metrics_path)
    raw_path = scenario_raw_path(config, metrics)
    thresholds = {**DEFAULT_THRESHOLDS, **SCENE_THRESHOLDS.get(scene_id, {})}
    issues: list[str] = []
    recommendations: list[str] = []

    valid = bool(metrics.get("valid", False))
    nan_count = as_float(metrics.get("nan_count", 0))
    row_count = as_float(metrics.get("row_count"))
    duration_s = as_float(metrics.get("duration_s"))
    expected_stop = as_float(config.get("simulation", {}).get("stop_time_s") if isinstance(config.get("simulation"), dict) else math.nan)
    expected_start = as_float(config.get("simulation", {}).get("start_time_s") if isinstance(config.get("simulation"), dict) else 0.0)
    expected_duration = expected_stop - expected_start if math.isfinite(expected_stop) else math.nan

    if not valid:
        issues.append("metrics valid=false")
    if math.isfinite(nan_count) and nan_count > 0:
        issues.append(f"nan_count={nan_count:g}")
    if not math.isfinite(row_count) or row_count <= 10:
        issues.append(f"row_count too small: {row_count}")
    if math.isfinite(expected_duration) and expected_duration > 0 and (
        not math.isfinite(duration_s) or duration_s < 0.98 * expected_duration
    ):
        issues.append(f"duration_s={duration_s:g} shorter than expected {expected_duration:g}s")

    if "smoke" in priority or "smoke" in experiment_id or "smoke" in evidence_level:
        result["quality_status"] = "smoke_only" if not issues else "invalid"
        result["quality_pass"] = not issues
        result["quality_issues"] = issues
        result["quality_recommendations"] = [
            "smoke evidence only validates the automation chain; run full scenario before making performance claims"
        ] if not issues else ["fix smoke evidence validity before extending to full simulation"]
        return result

    quality_profile = str(config.get("quality_profile", ""))
    if quality_profile == "system_mode" or scene_id.startswith("system_"):
        profile_issues, profile_recommendations, profile_metrics = system_mode_quality(raw_path, scene_id)
        result.update(profile_metrics)
        issues.extend(profile_issues)
        recommendations.extend(profile_recommendations)
        result["quality_status"] = "needs_iteration" if issues else "pass"
        result["quality_pass"] = not issues
        result["quality_issues"] = issues
        result["quality_recommendations"] = recommendations
        return result

    if quality_profile == "formation" or scene_id.startswith("formation_"):
        thresholds = {
            **thresholds,
            "max_position_rmse_m": min(thresholds["max_position_rmse_m"], 0.35),
            "max_position_error_m": min(thresholds["max_position_error_m"], 1.60),
        }

    metric_checks = [
        ("position_rmse_m", "max", thresholds["max_position_rmse_m"]),
        ("max_position_error_m", "max", thresholds["max_position_error_m"]),
        ("total_health_score", "min", thresholds["min_total_health_score"]),
        ("max_tilt_rad", "max", thresholds["max_tilt_rad"]),
    ]
    for key, direction, limit in metric_checks:
        value = as_float(metrics.get(key))
        if not math.isfinite(value):
            issues.append(f"{key} missing or non-finite")
            continue
        if direction == "max" and value > limit:
            issues.append(f"{key}={value:.6g} exceeds {limit:.6g}")
        if direction == "min" and value < limit:
            issues.append(f"{key}={value:.6g} below {limit:.6g}")

    if quality_profile == "formation" or scene_id.startswith("formation_"):
        profile_issues, profile_recommendations = formation_quality(metrics)
        issues.extend(profile_issues)
        recommendations.extend(profile_recommendations)

    if scene_id == "official_example3" and raw_path and raw_path.exists():
        figure8_ok, figure8_metrics = figure8_shape_quality(raw_path)
        result.update(figure8_metrics)
        if not figure8_ok:
            issues.append("figure8 shape check failed")
            recommendations.append("inspect x/y reference mapping and trajectory export before using this result in video")

    if scene_id.startswith("planning_"):
        collision_quality = planning_display_collision_quality(config)
        result["planning_display_collision_ok"] = bool(collision_quality["ok"])
        result["planning_display_collision_skipped"] = bool(collision_quality["skipped"])
        result["planning_display_collision_report"] = str(collision_quality["reason"])
        if not collision_quality["ok"]:
            issues.append("planning display collision check failed")
            recommendations.append(
                "do not claim obstacle avoidance; align planner map, rendered obstacles, and reference trajectory"
            )

    disturbance = config.get("disturbance", {})
    expected_fault_index = None
    if isinstance(disturbance, dict) and disturbance.get("expected_fault_index") is not None:
        try:
            expected_fault_index = int(disturbance["expected_fault_index"])
        except (TypeError, ValueError):
            issues.append(f"invalid expected_fault_index: {disturbance.get('expected_fault_index')}")
    if expected_fault_index is not None:
        if raw_path is None or not raw_path.exists():
            issues.append("fault_index check requested but raw result is missing")
        else:
            fault_metrics = fault_index_quality(raw_path, expected_fault_index=expected_fault_index)
            result.update(fault_metrics)
            accuracy = as_float(fault_metrics.get("fault_index_accuracy"))
            if not math.isfinite(accuracy):
                issues.append("fault_index column missing or has no valid samples")
            elif accuracy < DEFAULT_MIN_FAULT_INDEX_ACCURACY:
                issues.append(
                    f"fault_index accuracy {accuracy:.3f} below {DEFAULT_MIN_FAULT_INDEX_ACCURACY:.3f}"
                )
                recommendations.append("retune fault signatures or inspect rotor-to-axis mapping before claiming isolation")

    baseline_id = get_baseline_experiment(config)
    if baseline_id:
        baseline_path = find_baseline_metrics(baseline_id)
        if not baseline_path:
            issues.append(f"baseline metrics missing: {baseline_id}")
        else:
            baseline = read_json(baseline_path)
            rmse = as_float(metrics.get("position_rmse_m"))
            baseline_rmse = as_float(baseline.get("position_rmse_m"))
            if math.isfinite(rmse) and math.isfinite(baseline_rmse) and baseline_rmse > 1e-12:
                improvement = 100.0 * (baseline_rmse - rmse) / baseline_rmse
                result["quality_baseline_experiment"] = baseline_id
                result["quality_rmse_improvement_pct"] = improvement
                if improvement < min_rmse_improvement_pct:
                    issues.append(
                        f"RMSE improvement {improvement:.3f}% vs {baseline_id} below {min_rmse_improvement_pct:.3f}%"
                    )
                    recommendations.append("retune controller or revise the control structure before marking this scenario complete")
            else:
                issues.append(f"cannot compare RMSE against baseline {baseline_id}")

    if issues:
        result["quality_status"] = "needs_iteration"
        recommendations.append("preserve current evidence, update controller/scenario, rerun, and compare against this result")
    else:
        result["quality_status"] = "pass"
        recommendations.append("result meets current quality gate; it can be used as evidence if the report claim matches the scene")

    result["quality_pass"] = not issues
    result["quality_issues"] = issues
    result["quality_recommendations"] = recommendations
    return result


def write_quality_to_metrics(config: dict[str, Any], scenario_path: Path, quality: dict[str, Any]) -> None:
    metrics_path = scenario_metrics_path(config, scenario_path)
    metrics = read_json(metrics_path)
    for key in list(metrics):
        if key.startswith("quality_") or key.startswith("figure8_") or key.startswith("fault_index_"):
            metrics.pop(key)
    metrics.update(quality)
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, help="Scenario YAML path")
    parser.add_argument("--write-metrics", action="store_true", help="Persist quality fields into the metrics JSON")
    parser.add_argument(
        "--min-rmse-improvement-pct",
        type=float,
        default=0.5,
        help="Minimum required RMSE improvement for scenarios with controller.baseline_experiment",
    )
    parser.add_argument("--json", action="store_true", help="Print the full quality object as JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = read_yaml(args.scenario)
    quality = evaluate_quality(config, args.scenario, min_rmse_improvement_pct=args.min_rmse_improvement_pct)
    if args.write_metrics and (scenario_metrics_path(config, args.scenario)).exists():
        write_quality_to_metrics(config, args.scenario, quality)

    if args.json:
        print(json.dumps(quality, ensure_ascii=False, indent=2))
    else:
        print(f"[QUALITY] {args.scenario}: {quality['quality_status']}")
        for issue in quality["quality_issues"]:
            print(f"- issue: {issue}")
        for recommendation in quality["quality_recommendations"]:
            print(f"- next: {recommendation}")

    return 0 if quality["quality_status"] in PASS_STATUSES else 2


if __name__ == "__main__":
    raise SystemExit(main())
