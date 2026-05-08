#!/usr/bin/env python3
"""Generate motor-fault return references, event logs, metrics, and replay data."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return {}
    if value in {"true", "false"}:
        return value == "true"
    if value.startswith("[") and value.endswith("]"):
        items = [item.strip() for item in value[1:-1].split(",") if item.strip()]
        return [parse_scalar(item) for item in items]
    try:
        if any(token in value for token in [".", "e", "E"]):
            return float(value)
        return int(value)
    except ValueError:
        return value.strip('"').strip("'")


def read_simple_yaml(path: Path) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any] | list[Any]]] = [(-1, root)]
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, raw_line in enumerate(lines):
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if stripped.startswith("- "):
            value = parse_scalar(stripped[2:])
            if isinstance(parent, list):
                parent.append(value)
            continue
        if ":" not in stripped:
            continue
        key, value_text = stripped.split(":", 1)
        value = parse_scalar(value_text)
        if isinstance(parent, dict):
            parent[key] = value
            if value == {}:
                child_is_list = False
                for next_line in lines[index + 1:]:
                    if not next_line.strip() or next_line.lstrip().startswith("#"):
                        continue
                    next_indent = len(next_line) - len(next_line.lstrip(" "))
                    child_is_list = next_indent > indent and next_line.strip().startswith("- ")
                    break
                child: dict[str, Any] | list[Any] = [] if child_is_list else {}
                parent[key] = child
                stack.append((indent, child))
            elif isinstance(value, list):
                stack.append((indent, value))
    if not root:
        raise ValueError(f"YAML root must be a mapping: {path}")
    return root


def read_yaml(path: Path) -> dict[str, Any]:
    if yaml is None:
        return read_simple_yaml(path)
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def read_reference(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"time", "x_ref", "y_ref", "z_ref", "yaw_ref"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} missing columns: {', '.join(sorted(missing))}")
        rows: list[dict[str, float]] = []
        for row in reader:
            rows.append({key: float(row[key]) for key in required})
    return rows


def interpolate(a: list[float], b: list[float], alpha: float) -> list[float]:
    return [(1.0 - alpha) * x + alpha * y for x, y in zip(a, b)]


def smoothstep(alpha: float) -> float:
    alpha = max(0.0, min(1.0, alpha))
    return 3.0 * alpha * alpha - 2.0 * alpha * alpha * alpha


def distance(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def nearest_row(rows: list[dict[str, float]], target_time: float) -> dict[str, float]:
    return min(rows, key=lambda row: abs(row["time"] - target_time))


def build_events(config: dict[str, Any]) -> list[dict[str, Any]]:
    fault = config["fault"]
    safety = config["safety"]
    recovery = config["recovery"]
    start = float(fault["start_time_s"])
    end = float(fault["end_time_s"])
    return_delay = float(recovery.get("trigger_delay_s", 0.0))
    eta_fault = [float(value) for value in fault["eta_fault"]]
    return [
        {
            "time": float(config["simulation"]["start_time_s"]),
            "event": "mode_switch",
            "mode": "NORMAL",
            "reason": "scenario_start",
        },
        {
            "time": start,
            "event": "motor_fault",
            "fault_type": fault["type"],
            "motor_index": int(fault["motor_index"]),
            "eta": eta_fault,
        },
        {
            "time": start,
            "event": "mode_switch",
            "mode": "FAULT_TOLERANT",
            "reason": f"eta_min_below_{float(safety['fault_eta_threshold']):.2f}",
        },
        {
            "time": start + return_delay,
            "event": "degraded_return_start",
            "mode": "FAULT_TOLERANT",
            "return_point_m": recovery["return_point_m"],
        },
        {
            "time": end,
            "event": "fault_clear",
            "fault_type": fault["type"],
        },
        {
            "time": end,
            "event": "mode_switch",
            "mode": "DISTURBANCE_REJECTION",
            "reason": "post_fault_recovery_monitoring",
        },
    ]


def generate_rows(config: dict[str, Any], leader_rows: list[dict[str, float]]) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    simulation = config["simulation"]
    fault = config["fault"]
    safety = config["safety"]
    recovery = config["recovery"]
    start = float(fault["start_time_s"])
    end = float(fault["end_time_s"])
    return_start = start + float(recovery.get("trigger_delay_s", 0.0))
    eta_nominal = [float(value) for value in fault["eta_nominal"]]
    eta_fault = [float(value) for value in fault["eta_fault"]]
    return_point = [float(value) for value in recovery["return_point_m"]]
    return_altitude = float(safety["return_altitude_m"])
    return_point[2] = max(return_point[2], return_altitude)
    min_altitude = float(safety["min_altitude_m"])

    start_pos_row = nearest_row(leader_rows, return_start)
    return_start_pos = [
        start_pos_row["x_ref"],
        start_pos_row["y_ref"],
        max(start_pos_row["z_ref"], return_altitude),
    ]
    return_duration = max(
        distance(return_start_pos, return_point) / max(float(safety["max_return_speed_m_s"]), 1e-6),
        float(simulation["stop_time_s"]) - return_start,
        1e-6,
    )

    rows: list[dict[str, Any]] = []
    altitude_violations = 0
    return_completed = False
    for leader in leader_rows:
        time = leader["time"]
        if time < float(simulation["start_time_s"]) or time > float(simulation["stop_time_s"]) + 1e-9:
            continue

        eta = eta_fault if start <= time < end else eta_nominal
        eta_min = min(eta)
        if time < start:
            mode = "NORMAL"
            status = "nominal_tracking"
            target = [leader["x_ref"], leader["y_ref"], leader["z_ref"]]
            safety_active = False
        elif time < return_start:
            mode = "FAULT_TOLERANT"
            status = "fault_detected"
            target = [leader["x_ref"], leader["y_ref"], max(leader["z_ref"], return_altitude)]
            safety_active = True
        else:
            alpha = smoothstep((time - return_start) / return_duration)
            target = interpolate(return_start_pos, return_point, alpha)
            mode = "FAULT_TOLERANT" if time < end else "DISTURBANCE_REJECTION"
            status = "degraded_return" if alpha < 0.995 else "return_hold"
            return_completed = return_completed or alpha >= 0.995
            safety_active = True

        if eta_min < float(safety["emergency_eta_threshold"]):
            mode = "EMERGENCY_LAND"
            status = "emergency_land"

        z_ref = max(target[2], min_altitude)
        if z_ref <= min_altitude + 1e-9 and target[2] < min_altitude:
            altitude_violations += 1
        rows.append({
            "time": time,
            "x_ref": target[0],
            "y_ref": target[1],
            "z_ref": z_ref,
            "yaw_ref": leader["yaw_ref"],
            "eta1": eta[0],
            "eta2": eta[1],
            "eta3": eta[2],
            "eta4": eta[3],
            "eta_min": eta_min,
            "controller_mode": mode,
            "fault_type": fault["type"] if start <= time < end else "none",
            "return_or_land_status": status,
            "safety_active": int(safety_active),
        })

    events = build_events(config)
    mode_switch_count = sum(1 for event in events if event["event"] == "mode_switch")
    eta_min_overall = min(float(row["eta_min"]) for row in rows) if rows else 1.0
    fault_duration = max(0.0, end - start)
    safety_score = 100.0 if altitude_violations == 0 else max(0.0, 100.0 - 5.0 * altitude_violations)
    eta_score = 100.0 * max(0.0, min(1.0, (eta_min_overall - float(safety["emergency_eta_threshold"])) / (1.0 - float(safety["emergency_eta_threshold"]))))
    completion_score = 100.0 if rows and distance([rows[-1]["x_ref"], rows[-1]["y_ref"], rows[-1]["z_ref"]], return_point) <= 0.05 else 80.0
    fault_tolerance_score = 0.35 * safety_score + 0.30 * eta_score + 0.35 * completion_score
    metrics = {
        "experiment_id": config.get("experiment_id", ""),
        "scene_id": config.get("scene_id", ""),
        "controller_id": config.get("controller_id", ""),
        "fault_type": fault["type"],
        "fault_motor_index": int(fault["motor_index"]),
        "fault_start_time_s": start,
        "fault_duration_s": fault_duration,
        "eta_min": eta_min_overall,
        "controller_mode_switch_count": mode_switch_count,
        "event_count": len(events),
        "return_or_land_status": rows[-1]["return_or_land_status"] if rows else "",
        "degraded_task_completion": 1.0 if return_completed else 0.8,
        "minimum_altitude_m": min(float(row["z_ref"]) for row in rows) if rows else 0.0,
        "altitude_violation_count": altitude_violations,
        "safety_score": safety_score,
        "fault_tolerance_score": fault_tolerance_score,
        "total_health_score": fault_tolerance_score,
        "sample_count": len(rows),
        "duration_s": rows[-1]["time"] - rows[0]["time"] if rows else 0.0,
        "accepted": fault_tolerance_score >= 80.0 and altitude_violations == 0,
    }
    return rows, metrics, events


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_events(path: Path, events: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(event, ensure_ascii=False, sort_keys=True) for event in events]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_replay(path: Path, config: dict[str, Any], rows: list[dict[str, Any]], events: list[dict[str, Any]]) -> None:
    sample_stride = max(1, len(rows) // 600)
    frames = [
        {
            "time": row["time"],
            "mode": row["controller_mode"],
            "fault_type": row["fault_type"],
            "eta_min": row["eta_min"],
            "uav": [{"id": "fault_reference", "position": [row["x_ref"], row["y_ref"], row["z_ref"]], "yaw": row["yaw_ref"]}],
        }
        for row in rows[::sample_stride]
    ]
    payload = {
        "scene_id": config.get("scene_id", ""),
        "model_name": "Motor fault tolerant return reference",
        "description": "Single-UAV motor efficiency drop with degraded return and event log",
        "source": "scripts/generate_fault_scenario.py",
        "frame_count": len(frames),
        "events": events,
        "frames": frames,
    }
    write_json(path, payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, nargs="?", default=Path("scenarios/fault/motor_fault_return.yaml"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = read_yaml(args.scenario)
    leader_ref = config.get("leader_reference", {})
    reference = config.get("reference", {})
    result = config.get("result", {})
    if not isinstance(leader_ref, dict) or not isinstance(reference, dict) or not isinstance(result, dict):
        raise ValueError("scenario must contain leader_reference, reference, and result mappings")

    leader_rows = read_reference(Path(str(leader_ref["file"])))
    rows, metrics, events = generate_rows(config, leader_rows)
    write_csv(Path(str(reference["file"])), rows)
    write_json(Path(str(result["metrics_file"])), metrics)
    write_events(Path(str(result["event_log"])), events)
    write_replay(Path(str(result["replay_file"])), config, rows, events)
    print(f"Fault reference CSV: {reference['file']}")
    print(f"Fault metrics: {result['metrics_file']}")
    print(f"Fault event log: {result['event_log']}")
    print(f"Fault replay: {result['replay_file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
