#!/usr/bin/env python3
"""Generate safety-filter demo data with before/after constraint metrics."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

from generate_obstacle_planning_reference import minimum_obstacle_distance
from generate_planning_reference import (
    allocate_segment_times,
    generate_rows,
    norm,
    read_yaml,
    vector_sub,
)


def clamp_norm(vector: list[float], limit: float) -> list[float]:
    value = norm(vector)
    if value <= limit or value <= 1e-12:
        return vector
    return [item * limit / value for item in vector]


def obstacle_push(point: list[float], obstacles: list[dict[str, Any]], margin: float, gain: float) -> tuple[list[float], bool]:
    if not obstacles:
        return point, False
    adjusted = list(point)
    active = False
    for obstacle in obstacles:
        if obstacle["type"] != "sphere":
            continue
        center = [float(value) for value in obstacle["center"]]
        radius = float(obstacle["radius"])
        required = radius + margin + 0.01
        offset = vector_sub(adjusted, center)
        dist = norm(offset)
        if dist >= required:
            continue
        active = True
        direction = [0.0, 1.0, 0.0] if dist <= 1e-9 else [value / dist for value in offset]
        push = max(required - dist, gain * (required - dist))
        adjusted = [adjusted[i] + direction[i] * push for i in range(3)]
    return adjusted, active


def obstacle_push_above_floor(
    point: list[float],
    obstacles: list[dict[str, Any]],
    margin: float,
    floor_z: float,
) -> tuple[list[float], bool]:
    adjusted = [point[0], point[1], max(point[2], floor_z)]
    active = adjusted[2] != point[2]
    for obstacle in obstacles:
        if obstacle["type"] != "sphere":
            continue
        center = [float(value) for value in obstacle["center"]]
        radius = float(obstacle["radius"])
        required = radius + margin + 0.01
        dz = adjusted[2] - center[2]
        horizontal_required_sq = required * required - dz * dz
        if horizontal_required_sq <= 0.0:
            continue
        horizontal_required = math.sqrt(horizontal_required_sq)
        dx = adjusted[0] - center[0]
        dy = adjusted[1] - center[1]
        horizontal = math.sqrt(dx * dx + dy * dy)
        if horizontal >= horizontal_required:
            continue
        active = True
        if horizontal <= 1e-9:
            dx, dy, horizontal = 0.0, 1.0, 1.0
        scale = horizontal_required / horizontal
        adjusted[0] = center[0] + dx * scale
        adjusted[1] = center[1] + dy * scale
    return adjusted, active


def limit_velocity(prev: list[float], current: list[float], dt: float, max_velocity: float) -> tuple[list[float], bool]:
    delta = vector_sub(current, prev)
    velocity = [value / dt for value in delta]
    limited_velocity = clamp_norm(velocity, max_velocity)
    active = limited_velocity != velocity
    return [prev[i] + limited_velocity[i] * dt for i in range(3)], active


def derivative(values: list[list[float]], dt: float) -> list[list[float]]:
    output: list[list[float]] = []
    for index, value in enumerate(values):
        if index == 0:
            output.append([0.0, 0.0, 0.0])
        else:
            output.append([(value[i] - values[index - 1][i]) / dt for i in range(3)])
    return output


def generate_reference(config: dict[str, Any]) -> list[dict[str, float]]:
    unsafe = config["unsafe_reference"]
    simulation = config["simulation"]
    waypoints = [[float(value) for value in point] for point in unsafe["waypoints"]]
    dt = float(simulation["step_size_s"])
    total_time = float(simulation["stop_time_s"]) - float(simulation["start_time_s"])
    base_durations = allocate_segment_times(waypoints, v_ref=1.5, t_min=2.0)
    scale = total_time / max(sum(base_durations), 1e-9)
    return generate_rows(waypoints, [duration * scale for duration in base_durations], dt, str(unsafe.get("yaw_mode", "fixed")))


def build_rows(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], list[dict[str, float]]]:
    reference_rows = generate_reference(config)
    safety = config["safety_filter"]
    obstacles = list(safety.get("obstacles", []))
    min_altitude = float(safety["min_altitude_m"])
    max_velocity = float(safety["max_velocity_m_s"])
    margin = float(safety["obstacle_safety_margin_m"])
    push_gain = float(safety.get("obstacle_push_gain", 1.0))
    smoothing_alpha = float(safety.get("smoothing_alpha", 0.0))
    dt = float(config["simulation"]["step_size_s"])

    safe_positions: list[list[float]] = []
    rows: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = [{
        "time": float(config["simulation"]["start_time_s"]),
        "event": "mode_switch",
        "from": "",
        "to": "NORMAL",
        "reason": "scenario_start",
    }]
    safety_mode_active = False
    activation_count = 0

    for row in reference_rows:
        time = float(row["time"])
        raw = [float(row["x_ref"]), float(row["y_ref"]), float(row["z_ref"])]
        safe = list(raw)
        altitude_active = safe[2] < min_altitude
        if altitude_active:
            safe[2] = min_altitude
        safe, obstacle_active = obstacle_push(safe, obstacles, margin, push_gain)
        velocity_active = False
        if safe_positions:
            safe, velocity_active = limit_velocity(safe_positions[-1], safe, dt, max_velocity)
        if safe_positions and smoothing_alpha > 0.0:
            safe = [(1.0 - smoothing_alpha) * safe[i] + smoothing_alpha * safe_positions[-1][i] for i in range(3)]
            if safe[2] < min_altitude:
                safe[2] = min_altitude
        safe, final_obstacle_active = obstacle_push(safe, obstacles, margin, 1.0)
        safe, floor_obstacle_active = obstacle_push_above_floor(safe, obstacles, margin, min_altitude)
        obstacle_active = obstacle_active or final_obstacle_active or floor_obstacle_active

        active = altitude_active or obstacle_active or velocity_active
        if active and not safety_mode_active:
            events.append({
                "time": time,
                "event": "mode_switch",
                "from": "NORMAL",
                "to": "SAFETY_PROTECTION",
                "reason": "safety_guard",
            })
            safety_mode_active = True
            activation_count += 1
        if not active and safety_mode_active:
            events.append({
                "time": time,
                "event": "mode_switch",
                "from": "SAFETY_PROTECTION",
                "to": "NORMAL",
                "reason": "safety_margin_recovered",
            })
            safety_mode_active = False

        safe_positions.append(safe)
        rows.append({
            "time": time,
            "x_raw_ref": raw[0],
            "y_raw_ref": raw[1],
            "z_raw_ref": raw[2],
            "x_safe_ref": safe[0],
            "y_safe_ref": safe[1],
            "z_safe_ref": safe[2],
            "yaw_ref": row["yaw_ref"],
            "raw_obstacle_distance_m": minimum_obstacle_distance(raw, obstacles),
            "safe_obstacle_distance_m": minimum_obstacle_distance(safe, obstacles),
            "altitude_filter_active": int(altitude_active),
            "obstacle_filter_active": int(obstacle_active),
            "velocity_filter_active": int(velocity_active),
            "safety_active": int(active),
            "controller_mode": "SAFETY_PROTECTION" if active or safety_mode_active else "NORMAL",
        })

    raw_positions = [[row["x_raw_ref"], row["y_raw_ref"], row["z_raw_ref"]] for row in rows]
    safe_positions = [[row["x_safe_ref"], row["y_safe_ref"], row["z_safe_ref"]] for row in rows]
    raw_velocity = derivative(raw_positions, dt)
    safe_velocity = derivative(safe_positions, dt)
    raw_acceleration = derivative(raw_velocity, dt)
    safe_acceleration = derivative(safe_velocity, dt)

    raw_alt_violations = sum(1 for row in rows if row["z_raw_ref"] < min_altitude)
    safe_alt_violations = sum(1 for row in rows if row["z_safe_ref"] < min_altitude)
    raw_obs_violations = sum(1 for row in rows if row["raw_obstacle_distance_m"] < margin)
    safe_obs_violations = sum(1 for row in rows if row["safe_obstacle_distance_m"] < margin)
    raw_vel_violations = sum(1 for velocity in raw_velocity if norm(velocity) > max_velocity)
    safe_vel_violations = sum(1 for velocity in safe_velocity if norm(velocity) > max_velocity)
    raw_acc_violations = sum(1 for accel in raw_acceleration if norm(accel) > float(safety["max_acceleration_m_s2"]))
    safe_acc_violations = sum(1 for accel in safe_acceleration if norm(accel) > float(safety["max_acceleration_m_s2"]))
    raw_total = raw_alt_violations + raw_obs_violations + raw_vel_violations + raw_acc_violations
    safe_total = safe_alt_violations + safe_obs_violations + safe_vel_violations + safe_acc_violations
    reduction = 100.0 * (raw_total - safe_total) / raw_total if raw_total else 0.0
    metrics = {
        "experiment_id": config.get("experiment_id", ""),
        "scene_id": config.get("scene_id", ""),
        "controller_id": config.get("controller_id", ""),
        "duration_s": rows[-1]["time"] - rows[0]["time"] if rows else 0.0,
        "sample_count": len(rows),
        "min_altitude_limit_m": min_altitude,
        "raw_minimum_altitude_m": min(row["z_raw_ref"] for row in rows),
        "safe_minimum_altitude_m": min(row["z_safe_ref"] for row in rows),
        "raw_minimum_obstacle_distance_m": min(row["raw_obstacle_distance_m"] for row in rows),
        "safe_minimum_obstacle_distance_m": min(row["safe_obstacle_distance_m"] for row in rows),
        "obstacle_safety_margin_m": margin,
        "raw_constraint_violation_count": raw_total,
        "safe_constraint_violation_count": safe_total,
        "constraint_violation_reduction_pct": reduction,
        "raw_altitude_violation_count": raw_alt_violations,
        "safe_altitude_violation_count": safe_alt_violations,
        "raw_obstacle_violation_count": raw_obs_violations,
        "safe_obstacle_violation_count": safe_obs_violations,
        "raw_velocity_violation_count": raw_vel_violations,
        "safe_velocity_violation_count": safe_vel_violations,
        "raw_acceleration_violation_count": raw_acc_violations,
        "safe_acceleration_violation_count": safe_acc_violations,
        "safety_filter_activation_count": activation_count,
        "controller_mode_switch_count": sum(1 for event in events if event["event"] == "mode_switch"),
        "total_health_score": max(0.0, min(100.0, reduction)),
        "accepted": safe_total < raw_total and safe_alt_violations == 0 and safe_obs_violations == 0,
    }
    reference = [
        {
            "time": row["time"],
            "x_ref": row["x_safe_ref"],
            "y_ref": row["y_safe_ref"],
            "z_ref": row["z_safe_ref"],
            "yaw_ref": row["yaw_ref"],
        }
        for row in rows
    ]
    return rows, events, metrics, reference


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
            "uav": [
                {"id": "raw_reference", "position": [row["x_raw_ref"], row["y_raw_ref"], row["z_raw_ref"]], "yaw": row["yaw_ref"]},
                {"id": "safe_reference", "position": [row["x_safe_ref"], row["y_safe_ref"], row["z_safe_ref"]], "yaw": row["yaw_ref"]},
            ],
        }
        for row in rows[::sample_stride]
    ]
    payload = {
        "scene_id": config.get("scene_id", ""),
        "model_name": "Safety filter guard demo",
        "description": "Unsafe reference projected by altitude, velocity, and obstacle safety filters",
        "source": "scripts/generate_safety_filter_demo.py",
        "frame_count": len(frames),
        "obstacles": config["safety_filter"].get("obstacles", []),
        "events": events,
        "frames": frames,
    }
    write_json(path, payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, nargs="?", default=Path("scenarios/safety/filter_guard.yaml"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = read_yaml(args.scenario)
    result = config["result"]
    rows, events, metrics, reference = build_rows(config)
    write_csv(Path(str(config["reference"]["file"])), reference)
    write_csv(Path(str(result["raw_file"])), rows)
    write_json(Path(str(result["metrics_file"])), metrics)
    write_events(Path(str(result["event_log"])), events)
    write_replay(Path(str(result["replay_file"])), config, rows, events)
    print(f"Safety reference CSV: {config['reference']['file']}")
    print(f"Safety raw CSV: {result['raw_file']}")
    print(f"Safety metrics: {result['metrics_file']}")
    print(f"Safety event log: {result['event_log']}")
    print(f"Safety replay: {result['replay_file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
