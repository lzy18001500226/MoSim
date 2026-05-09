#!/usr/bin/env python3
"""Generate L1-inspired disturbance residual and mode-switch demo data."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

from generate_planning_reference import read_yaml


def vector_norm(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values))


def clamp(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


def lpf(previous: float, value: float, alpha: float) -> float:
    return alpha * previous + (1.0 - alpha) * value


def wind_at(time: float, wind_config: dict[str, Any]) -> list[float]:
    start = float(wind_config["start_time_s"])
    stop = float(wind_config["stop_time_s"])
    force = [float(item) for item in wind_config["force_n"]]
    return force if start <= time <= stop else [0.0, 0.0, 0.0]


def generate_figure8_reference(
    start_time: float,
    stop_time: float,
    dt: float,
    amplitude_x: float,
    amplitude_y: float,
    altitude: float,
    angular_rate: float,
) -> list[dict[str, float]]:
    steps = int(round((stop_time - start_time) / dt))
    rows: list[dict[str, float]] = []
    for index in range(steps + 1):
        time = round(start_time + index * dt, 10)
        tau = time - start_time
        x = amplitude_x * math.sin(angular_rate * tau)
        y = amplitude_y * math.sin(2.0 * angular_rate * tau)
        vx = amplitude_x * angular_rate * math.cos(angular_rate * tau)
        vy = 2.0 * amplitude_y * angular_rate * math.cos(2.0 * angular_rate * tau)
        yaw = math.atan2(vy, vx) if abs(vx) + abs(vy) > 1e-12 else 0.0
        rows.append({"time": time, "x_ref": x, "y_ref": y, "z_ref": altitude, "yaw_ref": yaw})
    return rows


def mode_for_residual(residual_xy: float, previous_mode: str, config: dict[str, float], time_in_mode: float) -> str:
    if previous_mode == "WIND_REJECTION":
        if residual_xy < config["wind_recover_threshold_m_s2"] and time_in_mode >= config["min_hold_time_s"]:
            return "NORMAL"
        return "WIND_REJECTION"
    if residual_xy > config["wind_enter_threshold_m_s2"] and time_in_mode >= config["enter_debounce_s"]:
        return "WIND_REJECTION"
    return "NORMAL"


def build_rows(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    simulation = config["simulation"]
    reference_cfg = config["reference"]
    wind_cfg = config["disturbance"]["wind"]
    estimator = config["disturbance_estimator"]
    dt = float(simulation["step_size_s"])
    rows_ref = generate_figure8_reference(
        float(simulation["start_time_s"]),
        float(simulation["stop_time_s"]),
        dt,
        float(reference_cfg["amplitude_x_m"]),
        float(reference_cfg["amplitude_y_m"]),
        float(reference_cfg["altitude_m"]),
        float(reference_cfg["angular_rate_rad_s"]),
    )
    mass = float(estimator.get("mass_kg", 1.0))
    alpha = float(estimator.get("residual_filter_alpha", 0.9))
    comp_limit = float(estimator.get("compensation_limit_m_s2", 2.0))
    compensation_gain = float(estimator.get("compensation_gain", 0.85))
    mode_cfg = {
        "wind_enter_threshold_m_s2": float(estimator.get("wind_enter_threshold_m_s2", 0.45)),
        "wind_recover_threshold_m_s2": float(estimator.get("wind_recover_threshold_m_s2", 0.18)),
        "enter_debounce_s": float(estimator.get("enter_debounce_s", 0.2)),
        "min_hold_time_s": float(estimator.get("min_hold_time_s", 1.0)),
    }

    residual_hat = [0.0, 0.0, 0.0]
    mode = "NORMAL"
    mode_enter_time = float(simulation["start_time_s"])
    events: list[dict[str, Any]] = [{
        "time": mode_enter_time,
        "event": "mode_switch",
        "from": "",
        "to": "NORMAL",
        "reason": "scenario_start",
    }]
    rows: list[dict[str, Any]] = []
    max_raw_residual = 0.0
    max_compensated_residual = 0.0
    sum_raw_error_sq = 0.0
    sum_comp_error_sq = 0.0
    wind_samples = 0
    compensation_energy = 0.0

    for ref in rows_ref:
        time = float(ref["time"])
        wind_force = wind_at(time, wind_cfg)
        residual_raw = [component / mass for component in wind_force]
        residual_hat = [lpf(residual_hat[i], residual_raw[i], alpha) for i in range(3)]
        residual_comp = [clamp(value * compensation_gain, comp_limit) for value in residual_hat]
        residual_after_comp = [residual_raw[i] - residual_comp[i] for i in range(3)]
        residual_xy = vector_norm(residual_hat[:2])
        candidate_mode = mode_for_residual(residual_xy, mode, mode_cfg, time - mode_enter_time)
        if candidate_mode != mode:
            events.append({
                "time": time,
                "event": "mode_switch",
                "from": mode,
                "to": candidate_mode,
                "reason": "wind_enter" if candidate_mode == "WIND_REJECTION" else "mode_recover",
                "residual_xy_m_s2": residual_xy,
            })
            mode = candidate_mode
            mode_enter_time = time

        wind_active = int(any(abs(value) > 1e-12 for value in wind_force))
        raw_error = vector_norm(residual_raw[:2])
        comp_error = vector_norm(residual_after_comp[:2])
        max_raw_residual = max(max_raw_residual, raw_error)
        max_compensated_residual = max(max_compensated_residual, comp_error)
        if wind_active:
            sum_raw_error_sq += raw_error * raw_error
            sum_comp_error_sq += comp_error * comp_error
            wind_samples += 1
        compensation_energy += vector_norm(residual_comp) * dt
        rows.append({
            "time": time,
            "x_ref": ref["x_ref"],
            "y_ref": ref["y_ref"],
            "z_ref": ref["z_ref"],
            "yaw_ref": ref["yaw_ref"],
            "wind_force_x_n": wind_force[0],
            "wind_force_y_n": wind_force[1],
            "wind_force_z_n": wind_force[2],
            "acc_residual_raw_x_m_s2": residual_raw[0],
            "acc_residual_raw_y_m_s2": residual_raw[1],
            "acc_residual_raw_z_m_s2": residual_raw[2],
            "disturbance_hat_x_m_s2": residual_hat[0],
            "disturbance_hat_y_m_s2": residual_hat[1],
            "disturbance_hat_z_m_s2": residual_hat[2],
            "disturbance_comp_x_m_s2": residual_comp[0],
            "disturbance_comp_y_m_s2": residual_comp[1],
            "disturbance_comp_z_m_s2": residual_comp[2],
            "acc_residual_after_comp_x_m_s2": residual_after_comp[0],
            "acc_residual_after_comp_y_m_s2": residual_after_comp[1],
            "acc_residual_after_comp_z_m_s2": residual_after_comp[2],
            "controller_mode": mode,
            "disturbance_type": "WIND" if wind_active else "NONE",
        })

    raw_rmse = math.sqrt(sum_raw_error_sq / max(wind_samples, 1))
    comp_rmse = math.sqrt(sum_comp_error_sq / max(wind_samples, 1))
    improvement = 100.0 * (raw_rmse - comp_rmse) / raw_rmse if raw_rmse > 1e-12 else 0.0
    wind_duration = max(0.0, float(wind_cfg["stop_time_s"]) - float(wind_cfg["start_time_s"]))
    mode_switch_count = sum(1 for event in events if event["event"] == "mode_switch")
    wind_enter_events = [event for event in events if event.get("to") == "WIND_REJECTION"]
    recover_events = [event for event in events if event.get("to") == "NORMAL" and event.get("from")]
    first_wind_enter_delay = (
        wind_enter_events[0]["time"] - float(wind_cfg["start_time_s"]) if wind_enter_events else math.inf
    )
    recovery_delay = (
        recover_events[-1]["time"] - float(wind_cfg["stop_time_s"]) if recover_events else math.inf
    )
    metrics = {
        "experiment_id": config.get("experiment_id", ""),
        "scene_id": config.get("scene_id", ""),
        "controller_id": config.get("controller_id", ""),
        "duration_s": rows[-1]["time"] - rows[0]["time"] if rows else 0.0,
        "sample_count": len(rows),
        "wind_start_time_s": float(wind_cfg["start_time_s"]),
        "wind_stop_time_s": float(wind_cfg["stop_time_s"]),
        "wind_duration_s": wind_duration,
        "wind_force_norm_n": vector_norm([float(item) for item in wind_cfg["force_n"]]),
        "raw_residual_rmse_m_s2": raw_rmse,
        "compensated_residual_rmse_m_s2": comp_rmse,
        "residual_reduction_pct": improvement,
        "max_raw_residual_m_s2": max_raw_residual,
        "max_compensated_residual_m_s2": max_compensated_residual,
        "compensation_energy": compensation_energy,
        "controller_mode_switch_count": mode_switch_count,
        "wind_rejection_entered": bool(wind_enter_events),
        "first_wind_enter_delay_s": first_wind_enter_delay if math.isfinite(first_wind_enter_delay) else None,
        "recovery_delay_s": recovery_delay if math.isfinite(recovery_delay) else None,
        "total_health_score": max(0.0, min(100.0, 60.0 + 0.4 * improvement)),
        "accepted": bool(wind_enter_events) and comp_rmse < raw_rmse and improvement >= 20.0,
    }
    return rows, events, metrics


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_events(path: Path, events: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(event, ensure_ascii=False, sort_keys=True) for event in events) + "\n", encoding="utf-8")


def write_replay(path: Path, config: dict[str, Any], rows: list[dict[str, Any]], events: list[dict[str, Any]]) -> None:
    sample_stride = max(1, len(rows) // 600)
    frames = [
        {
            "time": row["time"],
            "mode": row["controller_mode"],
            "disturbance_type": row["disturbance_type"],
            "uav": [{"id": "wind_disturbance_demo", "position": [row["x_ref"], row["y_ref"], row["z_ref"]], "yaw": row["yaw_ref"]}],
        }
        for row in rows[::sample_stride]
    ]
    payload = {
        "scene_id": config.get("scene_id", ""),
        "model_name": "L1-inspired wind disturbance compensation demo",
        "description": "Figure-8 reference with acceleration residual, low-pass compensation, and mode switch events",
        "source": "scripts/generate_disturbance_mode_demo.py",
        "frame_count": len(frames),
        "events": events,
        "frames": frames,
    }
    write_json(path, payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, nargs="?", default=Path("scenarios/wind/nmpc_indi_l1.yaml"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = read_yaml(args.scenario)
    result = config["result"]
    rows, events, metrics = build_rows(config)
    write_csv(Path(str(result["raw_file"])), rows)
    write_json(Path(str(result["metrics_file"])), metrics)
    write_events(Path(str(result["event_log"])), events)
    write_replay(Path(str(result["replay_file"])), config, rows, events)
    print(f"Disturbance CSV: {result['raw_file']}")
    print(f"Disturbance metrics: {result['metrics_file']}")
    print(f"Disturbance event log: {result['event_log']}")
    print(f"Disturbance replay: {result['replay_file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
