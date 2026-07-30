#!/usr/bin/env python3
"""Deterministic tests for the frozen seven-scenario metric definitions."""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
METRICS = ROOT / "Scripts" / "results" / "calc_metrics.py"


def load_metrics_module():
    spec = importlib.util.spec_from_file_location("calc_metrics", METRICS)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {METRICS}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def base_data(end_s: int = 50) -> dict[str, list[float]]:
    time = [float(value) for value in range(end_s + 1)]
    return {
        "time": time,
        "x": [0.0 for _ in time],
        "y": [0.0 for _ in time],
        "z": [2.0 for _ in time],
        "x_ref": [0.0 for _ in time],
        "y_ref": [0.0 for _ in time],
        "z_ref": [2.0 for _ in time],
    }


def test_step_response_metrics_use_signed_axes_and_persistent_band() -> None:
    metrics_module = load_metrics_module()
    data = base_data(end_s=45)
    for index, time_s in enumerate(data["time"]):
        if time_s >= 15.0:
            data["x_ref"][index] = 1.0
            data["y_ref"][index] = -1.0
        if time_s == 16.0:
            data["x"][index] = 0.8
            data["y"][index] = -0.8
        elif time_s == 17.0:
            data["x"][index] = 1.1
            data["y"][index] = -1.1
        elif time_s == 18.0:
            data["x"][index] = 0.96
            data["y"][index] = -0.96
        elif time_s == 19.0:
            data["x"][index] = 1.06
            data["y"][index] = -1.06
        elif time_s >= 20.0:
            data["x"][index] = 1.0
            data["y"][index] = -1.0
    metrics = metrics_module.compute_metrics(data, ROOT / "step.csv", "step_response", "fixture")
    assert math.isclose(metrics["overshoot_percent_x"], 10.0, rel_tol=1e-12)
    assert math.isclose(metrics["overshoot_percent_y"], 10.0, rel_tol=1e-12)
    assert math.isclose(metrics["settling_time_s"], 5.0, rel_tol=1e-12)
    assert math.isclose(metrics["steady_state_error_m"], 0.0, abs_tol=1e-12)


def test_wind_and_fault_windows_have_frozen_boundaries() -> None:
    metrics_module = load_metrics_module()
    wind_data = base_data(end_s=50)
    wind_data["x"] = [1.0 for _ in wind_data["time"]]
    wind_metrics = metrics_module.compute_metrics(
        wind_data,
        ROOT / "wind.csv",
        "wind_disturbance",
        "fixture",
    )
    assert math.isclose(wind_metrics["disturbance_window_rmse_m"], 1.0, rel_tol=1e-12)

    fault_data = base_data(end_s=50)
    fault_data["x"] = [0.0 if time_s < 15.0 else 2.0 for time_s in fault_data["time"]]
    fault_metrics = metrics_module.compute_metrics(
        fault_data,
        ROOT / "fault.csv",
        "motor_efficiency_fault",
        "fixture",
    )
    assert math.isclose(fault_metrics["pre_fault_rmse_m"], 0.0, abs_tol=1e-12)
    assert math.isclose(fault_metrics["post_fault_rmse_m"], 2.0, rel_tol=1e-12)
    assert math.isclose(fault_metrics["post_fault_peak_error_m"], 2.0, rel_tol=1e-12)


def test_profile_context_controls_v2_disturbance_and_fault_windows() -> None:
    metrics_module = load_metrics_module()
    wind_data = base_data(end_s=50)
    wind_data["x"] = [0.0 if time_s < 15.0 else 3.0 for time_s in wind_data["time"]]
    wind_metrics = metrics_module.compute_metrics(
        wind_data,
        ROOT / "wind_v2.csv",
        "wind_disturbance",
        "fixture",
        {"gust_start_s": 15.0, "gust_duration_s": 35.0},
    )
    assert math.isclose(wind_metrics["disturbance_window_start_s"], 15.0, rel_tol=1e-12)
    assert math.isclose(wind_metrics["disturbance_window_end_s"], 50.0, rel_tol=1e-12)
    assert math.isclose(wind_metrics["disturbance_window_rmse_m"], 3.0, rel_tol=1e-12)

    fault_data = base_data(end_s=50)
    fault_data["x"] = [0.0 if time_s < 20.0 else 4.0 for time_s in fault_data["time"]]
    fault_metrics = metrics_module.compute_metrics(
        fault_data,
        ROOT / "fault_v2.csv",
        "motor_efficiency_fault",
        "fixture",
        {"fault_start_s": 20.0},
    )
    assert math.isclose(fault_metrics["fault_start_s"], 20.0, rel_tol=1e-12)
    assert math.isclose(fault_metrics["pre_fault_rmse_m"], 0.0, abs_tol=1e-12)
    assert math.isclose(fault_metrics["post_fault_rmse_m"], 4.0, rel_tol=1e-12)


def main() -> int:
    test_step_response_metrics_use_signed_axes_and_persistent_band()
    test_wind_and_fault_windows_have_frozen_boundaries()
    test_profile_context_controls_v2_disturbance_and_fault_windows()
    print("[OK] seven-scenario metrics")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
