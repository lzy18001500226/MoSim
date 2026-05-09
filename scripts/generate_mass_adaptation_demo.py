#!/usr/bin/env python3
"""Generate delivery mass-change adaptation demo data."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

from generate_planning_reference import (
    allocate_segment_times,
    generate_rows,
    read_yaml,
    vector_sub,
    norm,
)


G = 9.81


def lpf(previous: float, value: float, alpha: float) -> float:
    return alpha * previous + (1.0 - alpha) * value


def clamp(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


def mass_scale_at(time: float, schedule: list[dict[str, Any]]) -> tuple[float, str]:
    current = schedule[0]
    for item in schedule:
        if time >= float(item["time_s"]):
            current = item
        else:
            break
    return float(current["mass_scale"]), str(current.get("phase", ""))


def generate_delivery_reference(config: dict[str, Any]) -> list[dict[str, float]]:
    task = config["task"]
    simulation = config["simulation"]
    waypoints = [[float(value) for value in point] for point in task["waypoints"]]
    dt = float(simulation["step_size_s"])
    total_time = float(simulation["stop_time_s"]) - float(simulation["start_time_s"])
    base_durations = allocate_segment_times(waypoints, v_ref=1.2, t_min=3.0)
    scale = total_time / max(sum(base_durations), 1e-9)
    durations = [duration * scale for duration in base_durations]
    return generate_rows(waypoints, durations, dt, str(task.get("yaw_mode", "fixed")))


def mode_for_mass(residual_z: float, delivery_seen: bool, previous_mode: str, estimator: dict[str, Any], time_in_mode: float) -> str:
    enter_threshold = float(estimator.get("mass_enter_threshold_m_s2", 0.45))
    recover_threshold = float(estimator.get("mass_recover_threshold_m_s2", 0.12))
    min_hold = float(estimator.get("min_hold_time_s", 2.0))
    if previous_mode == "MASS_ADAPTATION":
        if abs(residual_z) < recover_threshold and time_in_mode >= min_hold:
            return "NORMAL"
        return "MASS_ADAPTATION"
    if delivery_seen and abs(residual_z) > enter_threshold:
        return "MASS_ADAPTATION"
    return "NORMAL"


def build_rows(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    reference_rows = generate_delivery_reference(config)
    disturbance = config["disturbance"]
    schedule = list(disturbance["mass_schedule"])
    estimator = config["mass_adaptation"]
    delivery_time = float(config["task"]["delivery_time_s"])
    nominal_mass = float(estimator.get("nominal_mass_kg", 1.0))
    baseline_mass_estimate = float(estimator.get("initial_mass_estimate_scale", 1.2)) * nominal_mass
    mass_hat = baseline_mass_estimate
    residual_hat_z = 0.0
    residual_alpha = float(estimator.get("residual_filter_alpha", 0.92))
    mass_alpha = float(estimator.get("mass_estimate_filter_alpha", 0.96))
    comp_limit = float(estimator.get("compensation_limit_m_s2", 2.5))

    mode = "NORMAL"
    mode_enter_time = float(config["simulation"]["start_time_s"])
    delivery_seen = False
    events: list[dict[str, Any]] = [{
        "time": mode_enter_time,
        "event": "mode_switch",
        "from": "",
        "to": "NORMAL",
        "reason": "scenario_start",
    }]
    rows: list[dict[str, Any]] = []
    raw_sq = 0.0
    comp_sq = 0.0
    post_delivery_samples = 0
    max_raw = 0.0
    max_comp = 0.0
    mass_error_sum = 0.0

    for ref in reference_rows:
        time = float(ref["time"])
        actual_mass_scale, phase = mass_scale_at(time, schedule)
        actual_mass = actual_mass_scale * nominal_mass
        if not delivery_seen and time >= delivery_time:
            delivery_seen = True
            events.append({
                "time": delivery_time,
                "event": "delivery",
                "phase": "payload_released",
                "mass_scale_before": float(schedule[0]["mass_scale"]),
                "mass_scale_after": actual_mass_scale,
            })

        raw_residual_z = G * (baseline_mass_estimate / actual_mass - 1.0)
        mass_hat = lpf(mass_hat, actual_mass, mass_alpha) if delivery_seen else baseline_mass_estimate
        residual_hat_z = lpf(residual_hat_z, raw_residual_z, residual_alpha)
        compensation_z = clamp(residual_hat_z * (mass_hat / max(baseline_mass_estimate, 1e-9)), comp_limit)
        residual_after_comp_z = raw_residual_z - compensation_z

        candidate_mode = mode_for_mass(residual_hat_z, delivery_seen, mode, estimator, time - mode_enter_time)
        if candidate_mode != mode:
            events.append({
                "time": time,
                "event": "mode_switch",
                "from": mode,
                "to": candidate_mode,
                "reason": "mass_change" if candidate_mode == "MASS_ADAPTATION" else "mode_recover",
                "residual_z_m_s2": residual_hat_z,
            })
            mode = candidate_mode
            mode_enter_time = time

        if delivery_seen:
            raw_sq += raw_residual_z * raw_residual_z
            comp_sq += residual_after_comp_z * residual_after_comp_z
            post_delivery_samples += 1
            mass_error_sum += abs(mass_hat - actual_mass)
        max_raw = max(max_raw, abs(raw_residual_z))
        max_comp = max(max_comp, abs(residual_after_comp_z))

        rows.append({
            "time": time,
            "x_ref": ref["x_ref"],
            "y_ref": ref["y_ref"],
            "z_ref": ref["z_ref"],
            "yaw_ref": ref["yaw_ref"],
            "task_phase": "DELIVERY" if abs(time - delivery_time) <= float(config["simulation"]["step_size_s"]) else ("RETURN" if time > delivery_time else "OUTBOUND"),
            "actual_mass_scale": actual_mass_scale,
            "mass_estimate_scale": mass_hat / nominal_mass,
            "mass_phase": phase,
            "acc_residual_raw_z_m_s2": raw_residual_z,
            "disturbance_hat_z_m_s2": residual_hat_z,
            "disturbance_comp_z_m_s2": compensation_z,
            "acc_residual_after_comp_z_m_s2": residual_after_comp_z,
            "controller_mode": mode,
            "disturbance_type": "MASS_CHANGE" if delivery_seen else "NONE",
        })

    raw_rmse = math.sqrt(raw_sq / max(post_delivery_samples, 1))
    comp_rmse = math.sqrt(comp_sq / max(post_delivery_samples, 1))
    reduction = 100.0 * (raw_rmse - comp_rmse) / raw_rmse if raw_rmse > 1e-12 else 0.0
    mode_switch_count = sum(1 for event in events if event["event"] == "mode_switch")
    mass_events = [event for event in events if event.get("to") == "MASS_ADAPTATION"]
    recover_events = [event for event in events if event.get("to") == "NORMAL" and event.get("from")]
    final_position = [rows[-1]["x_ref"], rows[-1]["y_ref"], rows[-1]["z_ref"]]
    start_position = [rows[0]["x_ref"], rows[0]["y_ref"], rows[0]["z_ref"]]
    return_error = norm(vector_sub(final_position, start_position))
    metrics = {
        "experiment_id": config.get("experiment_id", ""),
        "scene_id": config.get("scene_id", ""),
        "controller_id": config.get("controller_id", ""),
        "duration_s": rows[-1]["time"] - rows[0]["time"] if rows else 0.0,
        "sample_count": len(rows),
        "delivery_time_s": delivery_time,
        "mass_scale_before": float(schedule[0]["mass_scale"]),
        "mass_scale_after": float(schedule[-1]["mass_scale"]),
        "raw_vertical_residual_rmse_m_s2": raw_rmse,
        "compensated_vertical_residual_rmse_m_s2": comp_rmse,
        "vertical_residual_reduction_pct": reduction,
        "max_raw_vertical_residual_m_s2": max_raw,
        "max_compensated_vertical_residual_m_s2": max_comp,
        "mean_mass_estimate_error_kg": mass_error_sum / max(post_delivery_samples, 1),
        "controller_mode_switch_count": mode_switch_count,
        "mass_adaptation_entered": bool(mass_events),
        "mass_adaptation_enter_delay_s": mass_events[0]["time"] - delivery_time if mass_events else None,
        "recovery_delay_s": recover_events[-1]["time"] - delivery_time if recover_events else None,
        "return_position_error_m": return_error,
        "degraded_task_completion": 1.0 if return_error < 0.05 else 0.8,
        "total_health_score": max(0.0, min(100.0, 60.0 + 0.4 * reduction)),
        "accepted": bool(mass_events) and comp_rmse < raw_rmse and reduction >= 20.0 and return_error < 0.05,
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
            "task_phase": row["task_phase"],
            "disturbance_type": row["disturbance_type"],
            "uav": [{"id": "delivery_mass_demo", "position": [row["x_ref"], row["y_ref"], row["z_ref"]], "yaw": row["yaw_ref"]}],
        }
        for row in rows[::sample_stride]
    ]
    payload = {
        "scene_id": config.get("scene_id", ""),
        "model_name": "Delivery mass-change adaptation demo",
        "description": "Delivery mission with payload release, vertical residual compensation, and MASS_ADAPTATION mode",
        "source": "scripts/generate_mass_adaptation_demo.py",
        "frame_count": len(frames),
        "events": events,
        "frames": frames,
    }
    write_json(path, payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, nargs="?", default=Path("scenarios/mass/delivery_mass_change.yaml"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = read_yaml(args.scenario)
    result = config["result"]
    rows, events, metrics = build_rows(config)
    write_csv(Path(str(config["reference"]["file"])), [
        {key: row[key] for key in ["time", "x_ref", "y_ref", "z_ref", "yaw_ref"]}
        for row in rows
    ])
    write_csv(Path(str(result["raw_file"])), rows)
    write_json(Path(str(result["metrics_file"])), metrics)
    write_events(Path(str(result["event_log"])), events)
    write_replay(Path(str(result["replay_file"])), config, rows, events)
    print(f"Reference CSV: {config['reference']['file']}")
    print(f"Mass adaptation CSV: {result['raw_file']}")
    print(f"Mass adaptation metrics: {result['metrics_file']}")
    print(f"Mass adaptation event log: {result['event_log']}")
    print(f"Mass adaptation replay: {result['replay_file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
