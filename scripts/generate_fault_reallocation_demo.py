#!/usr/bin/env python3
"""Generate fault-aware control allocation comparison data."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

from generate_planning_reference import read_yaml


Matrix = list[list[float]]
Vector = list[float]


def allocation_matrix(arm: float, yaw_coeff: float) -> Matrix:
    return [
        [1.0, 1.0, 1.0, 1.0],
        [arm, -arm, -arm, arm],
        [-arm, -arm, arm, arm],
        [yaw_coeff, -yaw_coeff, yaw_coeff, -yaw_coeff],
    ]


def mat_vec(matrix: Matrix, vector: Vector) -> Vector:
    return [sum(row[i] * vector[i] for i in range(len(vector))) for row in matrix]


def diag_scale_columns(matrix: Matrix, eta: Vector) -> Matrix:
    return [[row[i] * eta[i] for i in range(len(eta))] for row in matrix]


def solve_linear(matrix: Matrix, rhs: Vector) -> Vector:
    size = len(rhs)
    aug = [list(matrix[row]) + [rhs[row]] for row in range(size)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(aug[row][col]))
        if abs(aug[pivot][col]) < 1e-12:
            raise ValueError("Singular allocation matrix")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [value / scale for value in aug[col]]
        for row in range(size):
            if row == col:
                continue
            factor = aug[row][col]
            aug[row] = [aug[row][i] - factor * aug[col][i] for i in range(size + 1)]
    return [aug[row][-1] for row in range(size)]


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def clamp_vector(values: Vector, lower: float, upper: float) -> Vector:
    return [clamp(value, lower, upper) for value in values]


def vec_sub(a: Vector, b: Vector) -> Vector:
    return [x - y for x, y in zip(a, b)]


def norm(values: Vector) -> float:
    return math.sqrt(sum(value * value for value in values))


def desired_wrench(time: float, params: dict[str, Any]) -> Vector:
    omega = 2.0 * math.pi * float(params.get("frequency_hz", 0.35))
    return [
        float(params["thrust_base"]) + float(params["thrust_amp"]) * math.sin(omega * time),
        float(params["roll_moment_amp"]) * math.sin(omega * time + 0.4),
        float(params["pitch_moment_amp"]) * math.cos(0.8 * omega * time),
        float(params["yaw_moment_amp"]) * math.sin(1.3 * omega * time),
    ]


def eta_at(time: float, fault: dict[str, Any]) -> Vector:
    if float(fault["start_time_s"]) <= time < float(fault["end_time_s"]):
        return [float(value) for value in fault["eta_fault"]]
    return [float(value) for value in fault["eta_nominal"]]


def saturation_ratio(commands: list[Vector], lower: float, upper: float) -> float:
    if not commands:
        return 0.0
    total = len(commands) * len(commands[0])
    saturated = sum(1 for row in commands for value in row if value <= lower + 1e-9 or value >= upper - 1e-9)
    return saturated / total


def build_events(config: dict[str, Any]) -> list[dict[str, Any]]:
    fault = config["fault"]
    return [
        {"time": float(config["simulation"]["start_time_s"]), "event": "mode_switch", "from": "", "to": "NORMAL", "reason": "scenario_start"},
        {"time": float(fault["start_time_s"]), "event": "motor_fault", "fault_type": fault["type"], "motor_index": int(fault["motor_index"]), "eta": fault["eta_fault"]},
        {"time": float(fault["start_time_s"]), "event": "mode_switch", "from": "NORMAL", "to": "FAULT_TOLERANT", "reason": "eta_min_below_threshold"},
        {"time": float(fault["start_time_s"]), "event": "reallocator_enabled", "method": "fault_matrix_inverse", "eta": fault["eta_fault"]},
        {"time": float(fault["end_time_s"]), "event": "fault_clear", "fault_type": fault["type"]},
        {"time": float(fault["end_time_s"]), "event": "mode_switch", "from": "FAULT_TOLERANT", "to": "NORMAL", "reason": "eta_recovered"},
    ]


def build_rows(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    simulation = config["simulation"]
    allocation = config["allocation"]
    fault = config["fault"]
    dt = float(simulation["step_size_s"])
    steps = int(round((float(simulation["stop_time_s"]) - float(simulation["start_time_s"])) / dt))
    lower = float(allocation["motor_cmd_min"])
    upper = float(allocation["motor_cmd_max"])
    matrix_nominal = allocation_matrix(float(allocation["arm_length_m"]), float(allocation["yaw_moment_coeff"]))
    desired_params = allocation["desired_wrench"]

    rows: list[dict[str, Any]] = []
    reference_rows: list[dict[str, Any]] = []
    no_errors: list[float] = []
    realloc_errors: list[float] = []
    no_torque_errors: list[float] = []
    realloc_torque_errors: list[float] = []
    no_commands_fault: list[Vector] = []
    realloc_commands_fault: list[Vector] = []

    for index in range(steps + 1):
        time = round(float(simulation["start_time_s"]) + index * dt, 10)
        desired = desired_wrench(time, desired_params)
        eta = eta_at(time, fault)
        fault_active = eta != [float(value) for value in fault["eta_nominal"]]
        matrix_fault = diag_scale_columns(matrix_nominal, eta)
        no_cmd = clamp_vector(solve_linear(matrix_nominal, desired), lower, upper)
        realloc_cmd = clamp_vector(solve_linear(matrix_fault, desired), lower, upper)
        no_actual = mat_vec(matrix_fault, no_cmd)
        realloc_actual = mat_vec(matrix_fault, realloc_cmd)
        no_error_vec = vec_sub(no_actual, desired)
        realloc_error_vec = vec_sub(realloc_actual, desired)
        no_error = norm(no_error_vec)
        realloc_error = norm(realloc_error_vec)
        no_torque_error = norm(no_error_vec[1:])
        realloc_torque_error = norm(realloc_error_vec[1:])
        if fault_active:
            no_errors.append(no_error)
            realloc_errors.append(realloc_error)
            no_torque_errors.append(no_torque_error)
            realloc_torque_errors.append(realloc_torque_error)
            no_commands_fault.append(no_cmd)
            realloc_commands_fault.append(realloc_cmd)
        reference_rows.append({
            "time": time,
            "desired_thrust": desired[0],
            "desired_roll_moment": desired[1],
            "desired_pitch_moment": desired[2],
            "desired_yaw_moment": desired[3],
        })
        rows.append({
            "time": time,
            "eta1": eta[0],
            "eta2": eta[1],
            "eta3": eta[2],
            "eta4": eta[3],
            "fault_active": int(fault_active),
            "controller_mode": "FAULT_TOLERANT" if fault_active else "NORMAL",
            "desired_thrust": desired[0],
            "desired_roll_moment": desired[1],
            "desired_pitch_moment": desired[2],
            "desired_yaw_moment": desired[3],
            "no_realloc_motor_1": no_cmd[0],
            "no_realloc_motor_2": no_cmd[1],
            "no_realloc_motor_3": no_cmd[2],
            "no_realloc_motor_4": no_cmd[3],
            "realloc_motor_1": realloc_cmd[0],
            "realloc_motor_2": realloc_cmd[1],
            "realloc_motor_3": realloc_cmd[2],
            "realloc_motor_4": realloc_cmd[3],
            "no_realloc_wrench_error": no_error,
            "realloc_wrench_error": realloc_error,
            "no_realloc_torque_error": no_torque_error,
            "realloc_torque_error": realloc_torque_error,
        })

    no_rmse = math.sqrt(sum(value * value for value in no_errors) / max(len(no_errors), 1))
    realloc_rmse = math.sqrt(sum(value * value for value in realloc_errors) / max(len(realloc_errors), 1))
    no_torque_rmse = math.sqrt(sum(value * value for value in no_torque_errors) / max(len(no_torque_errors), 1))
    realloc_torque_rmse = math.sqrt(sum(value * value for value in realloc_torque_errors) / max(len(realloc_torque_errors), 1))
    improvement = 100.0 * (no_rmse - realloc_rmse) / no_rmse if no_rmse > 1e-12 else 0.0
    torque_improvement = 100.0 * (no_torque_rmse - realloc_torque_rmse) / no_torque_rmse if no_torque_rmse > 1e-12 else 0.0
    metrics = {
        "experiment_id": config.get("experiment_id", ""),
        "scene_id": config.get("scene_id", ""),
        "controller_id": config.get("controller_id", ""),
        "duration_s": rows[-1]["time"] - rows[0]["time"] if rows else 0.0,
        "sample_count": len(rows),
        "fault_type": fault["type"],
        "fault_motor_index": int(fault["motor_index"]),
        "eta_min": min(float(value) for value in fault["eta_fault"]),
        "fault_start_time_s": float(fault["start_time_s"]),
        "fault_duration_s": float(fault["end_time_s"]) - float(fault["start_time_s"]),
        "no_realloc_wrench_rmse": no_rmse,
        "realloc_wrench_rmse": realloc_rmse,
        "wrench_error_reduction_pct": improvement,
        "no_realloc_torque_rmse": no_torque_rmse,
        "realloc_torque_rmse": realloc_torque_rmse,
        "torque_error_reduction_pct": torque_improvement,
        "no_realloc_saturation_ratio": saturation_ratio(no_commands_fault, lower, upper),
        "realloc_saturation_ratio": saturation_ratio(realloc_commands_fault, lower, upper),
        "controller_mode_switch_count": sum(1 for event in build_events(config) if event["event"] == "mode_switch"),
        "reallocator_enabled": True,
        "fault_tolerance_score": max(0.0, min(100.0, improvement)),
        "total_health_score": max(0.0, min(100.0, improvement)),
        "accepted": improvement >= 80.0 and realloc_rmse < no_rmse,
    }
    return rows, build_events(config), metrics, reference_rows


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
    frames = []
    for row in rows[::sample_stride]:
        x = 0.55 * math.cos(0.6 * row["time"])
        y = 0.55 * math.sin(0.6 * row["time"])
        z = 1.8 + 0.25 * math.sin(0.35 * row["time"])
        frames.append({
            "time": row["time"],
            "mode": row["controller_mode"],
            "uav": [{"id": "fault_reallocation_compare", "position": [x, y, z], "yaw": 0.0}],
        })
    payload = {
        "scene_id": config.get("scene_id", ""),
        "model_name": "Fault-aware control allocation comparison",
        "description": "Motor eta=0.7 comparison between nominal allocation and eta-aware reallocation",
        "source": "scripts/generate_fault_reallocation_demo.py",
        "frame_count": len(frames),
        "events": events,
        "frames": frames,
    }
    write_json(path, payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, nargs="?", default=Path("scenarios/fault/reallocation_compare.yaml"))
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
    print(f"Reallocation reference CSV: {config['reference']['file']}")
    print(f"Reallocation raw CSV: {result['raw_file']}")
    print(f"Reallocation metrics: {result['metrics_file']}")
    print(f"Reallocation event log: {result['event_log']}")
    print(f"Reallocation replay: {result['replay_file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
