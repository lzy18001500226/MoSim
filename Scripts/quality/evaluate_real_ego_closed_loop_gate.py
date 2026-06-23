#!/usr/bin/env python3
"""Evaluate a real EGO -> Gazebo closed-loop mission gate.

This gate is intentionally stricter than the existing EGO/RViz review checks:
it requires evidence that the Gazebo vehicle actually moved, stayed clear of
obstacles, approached the mission goal, and landed. Planner/RViz topics alone
are not accepted as success.
"""

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


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size == 0:
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
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
    raw = row.get("position_m")
    if not isinstance(raw, list) or len(raw) != 3:
        return None
    try:
        values = [float(raw[0]), float(raw[1]), float(raw[2])]
    except (TypeError, ValueError):
        return None
    return values if all(math.isfinite(item) for item in values) else None


def finite_orientation(row: dict[str, Any]) -> list[float] | None:
    raw = row.get("orientation_xyzw")
    if not isinstance(raw, list) or len(raw) != 4:
        return None
    try:
        values = [float(raw[0]), float(raw[1]), float(raw[2]), float(raw[3])]
    except (TypeError, ValueError):
        return None
    return values if all(math.isfinite(item) for item in values) else None


def quaternion_to_tilt_rad(values: list[float]) -> float:
    x, y, z, w = values
    norm = math.sqrt(x * x + y * y + z * z + w * w)
    if norm <= 0.0:
        return 0.0
    x, y, z, w = x / norm, y / norm, z / norm, w / norm
    roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    sin_pitch = 2.0 * (w * y - z * x)
    pitch = math.asin(max(-1.0, min(1.0, sin_pitch)))
    return math.hypot(roll, pitch)


def finite_time(row: dict[str, Any]) -> float | None:
    raw = row.get("time", row.get("elapsed_s"))
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def truth_samples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for row in rows:
        position = finite_position(row)
        time_s = finite_time(row)
        if position is None or time_s is None:
            continue
        item = dict(row)
        item["_position"] = position
        item["_time"] = time_s
        orientation = finite_orientation(row)
        if orientation is not None:
            item["_tilt_rad"] = quaternion_to_tilt_rad(orientation)
        samples.append(item)
    samples.sort(key=lambda item: (float(item["_time"]), int(item.get("seq", 0))))
    return samples


def parse_obstacle(raw: str) -> tuple[float, float, float]:
    parts = [float(item) for item in raw.split(",")]
    if len(parts) != 3 or parts[2] <= 0 or not all(math.isfinite(item) for item in parts):
        raise argparse.ArgumentTypeError("obstacle must be finite x,y,radius with positive radius")
    return parts[0], parts[1], parts[2]


def min_clearance(position: list[float], obstacles: list[tuple[float, float, float]]) -> float | None:
    if not obstacles:
        return None
    return min(math.hypot(position[0] - ox, position[1] - oy) - radius for ox, oy, radius in obstacles)


def path_metrics(samples: list[dict[str, Any]], obstacles: list[tuple[float, float, float]]) -> dict[str, Any]:
    if not samples:
        return {
            "truth_sample_count": 0,
            "start_position_m": None,
            "final_position_m": None,
            "max_displacement_from_start_m": None,
            "path_length_xy_m": None,
            "min_obstacle_clearance_m": None,
            "max_z_m": None,
            "final_z_m": None,
            "landing_window_xy_displacement_m": None,
        }
    positions = [sample["_position"] for sample in samples]
    start = positions[0]
    final = positions[-1]
    max_displacement = max(math.dist(start, position) for position in positions)
    path_length_xy = sum(
        math.hypot(positions[index][0] - positions[index - 1][0], positions[index][1] - positions[index - 1][1])
        for index in range(1, len(positions))
    )
    clearances = [min_clearance(position, obstacles) for position in positions]
    finite_clearances = [value for value in clearances if value is not None and math.isfinite(value)]
    final_time = float(samples[-1]["_time"])
    landing_window = [
        sample["_position"]
        for sample in samples
        if float(sample["_time"]) >= final_time - 2.0
    ]
    landing_xy = None
    if len(landing_window) >= 2:
        landing_xy = math.hypot(
            landing_window[-1][0] - landing_window[0][0],
            landing_window[-1][1] - landing_window[0][1],
        )
    return {
        "truth_sample_count": len(samples),
        "start_position_m": [round(item, 6) for item in start],
        "final_position_m": [round(item, 6) for item in final],
        "max_displacement_from_start_m": round(max_displacement, 6),
        "path_length_xy_m": round(path_length_xy, 6),
        "min_obstacle_clearance_m": round(min(finite_clearances), 6) if finite_clearances else None,
        "max_z_m": round(max(position[2] for position in positions), 6),
        "final_z_m": round(final[2], 6),
        "max_tilt_rad": round(max(float(sample.get("_tilt_rad", 0.0)) for sample in samples), 6),
        "final_tilt_rad": round(float(samples[-1].get("_tilt_rad", 0.0)), 6),
        "landing_window_xy_displacement_m": round(landing_xy, 6) if landing_xy is not None else None,
    }


def count_jsonl_status(path: Path, status: str) -> int:
    return sum(1 for row in read_jsonl(path) if row.get("status") == status)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--truth-jsonl", required=True, type=Path)
    parser.add_argument("--truth-summary-json", required=True, type=Path)
    parser.add_argument("--ego-topic-recorder-json", required=True, type=Path)
    parser.add_argument("--traj-server-log", required=True, type=Path)
    parser.add_argument("--traj-server-stderr-log", type=Path)
    parser.add_argument("--controller-adapter-json", required=True, type=Path)
    parser.add_argument("--controller-adapter-trace-jsonl", required=True, type=Path)
    parser.add_argument("--start", default="0,0,1.2")
    parser.add_argument("--goal", default="7,0,1.2")
    parser.add_argument("--obstacle", action="append", type=parse_obstacle, default=[])
    parser.add_argument("--min-truth-samples", type=int, default=120)
    parser.add_argument("--min-displacement-m", type=float, default=2.0)
    parser.add_argument("--min-path-length-xy-m", type=float, default=2.0)
    parser.add_argument("--goal-tolerance-xy-m", type=float, default=1.0)
    parser.add_argument("--min-clearance-m", type=float, default=0.05)
    parser.add_argument("--max-final-z-m", type=float, default=0.25)
    parser.add_argument("--max-final-tilt-rad", type=float, default=0.45)
    parser.add_argument("--max-flight-tilt-rad", type=float, default=1.0)
    parser.add_argument("--min-position-cmd-count", type=int, default=20)
    parser.add_argument("--min-controller-publish-count", type=int, default=20)
    parser.add_argument("--output-json", required=True, type=Path)
    return parser.parse_args()


def parse_xyz(raw: str) -> list[float]:
    values = [float(item) for item in raw.split(",")]
    if len(values) != 3 or not all(math.isfinite(item) for item in values):
        raise SystemExit(f"invalid xyz: {raw}")
    return values


def main() -> int:
    args = parse_args()
    truth_path = project_path(args.truth_jsonl)
    truth_summary_path = project_path(args.truth_summary_json)
    recorder_path = project_path(args.ego_topic_recorder_json)
    traj_log_path = project_path(args.traj_server_log)
    traj_stderr_path = project_path(args.traj_server_stderr_log) if args.traj_server_stderr_log else None
    adapter_json_path = project_path(args.controller_adapter_json)
    adapter_trace_path = project_path(args.controller_adapter_trace_jsonl)
    output_path = project_path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    start = parse_xyz(args.start)
    goal = parse_xyz(args.goal)
    samples = truth_samples(read_jsonl(truth_path))
    metrics = path_metrics(samples, list(args.obstacle))
    final = metrics.get("final_position_m")
    final_goal_xy_error = None
    if isinstance(final, list) and len(final) == 3:
        final_goal_xy_error = math.hypot(float(final[0]) - goal[0], float(final[1]) - goal[1])

    recorder = read_json(recorder_path)
    topic_counts = recorder.get("message_counts", {}) if isinstance(recorder, dict) else {}
    adapter = read_json(adapter_json_path)
    truth_summary = read_json(truth_summary_path)
    traj_log = traj_log_path.read_text(encoding="utf-8", errors="replace") if traj_log_path.exists() else ""
    if traj_stderr_path is not None and traj_stderr_path.exists():
        traj_log += "\n" + traj_stderr_path.read_text(encoding="utf-8", errors="replace")
    controller_published_count = count_jsonl_status(adapter_trace_path, "published")

    position_cmd_count = int(topic_counts.get("position_cmd", 0) or 0)
    setpoint_count = int(topic_counts.get("planner_setpoint", 0) or 0)
    controller_output_count = int(topic_counts.get("controller_output", 0) or 0)

    blockers: list[str] = []
    if int(metrics["truth_sample_count"] or 0) < args.min_truth_samples:
        blockers.append(f"truth_samples_below_min:{metrics['truth_sample_count']}<{args.min_truth_samples}")
    if (metrics["max_displacement_from_start_m"] or 0.0) < args.min_displacement_m:
        blockers.append(
            f"uav_did_not_move_enough:{metrics['max_displacement_from_start_m']}<{args.min_displacement_m}"
        )
    if (metrics["path_length_xy_m"] or 0.0) < args.min_path_length_xy_m:
        blockers.append(f"path_length_too_short:{metrics['path_length_xy_m']}<{args.min_path_length_xy_m}")
    if final_goal_xy_error is None or final_goal_xy_error > args.goal_tolerance_xy_m:
        blockers.append(f"goal_not_reached_xy:{final_goal_xy_error}>{args.goal_tolerance_xy_m}")
    if args.obstacle:
        clearance = metrics.get("min_obstacle_clearance_m")
        if clearance is None or float(clearance) < args.min_clearance_m:
            blockers.append(f"obstacle_clearance_failed:{clearance}<{args.min_clearance_m}")
    if metrics.get("final_z_m") is None or float(metrics["final_z_m"]) > args.max_final_z_m:
        blockers.append(f"landing_not_completed:final_z={metrics.get('final_z_m')}>{args.max_final_z_m}")
    if metrics.get("final_tilt_rad") is None or float(metrics["final_tilt_rad"]) > args.max_final_tilt_rad:
        blockers.append(f"final_tilt_too_large:{metrics.get('final_tilt_rad')}>{args.max_final_tilt_rad}")
    if metrics.get("max_tilt_rad") is None or float(metrics["max_tilt_rad"]) > args.max_flight_tilt_rad:
        blockers.append(f"flight_tilt_too_large:{metrics.get('max_tilt_rad')}>{args.max_flight_tilt_rad}")
    if position_cmd_count < args.min_position_cmd_count:
        blockers.append(f"position_cmd_count_below_min:{position_cmd_count}<{args.min_position_cmd_count}")
    if setpoint_count < args.min_position_cmd_count:
        blockers.append(f"planner_setpoint_count_below_min:{setpoint_count}<{args.min_position_cmd_count}")
    if controller_output_count < args.min_controller_publish_count:
        blockers.append(
            f"controller_output_count_below_min:{controller_output_count}<{args.min_controller_publish_count}"
        )
    if controller_published_count < args.min_controller_publish_count:
        blockers.append(
            f"actuator_adapter_publish_count_below_min:{controller_published_count}<{args.min_controller_publish_count}"
        )
    if "received Bspline" not in traj_log:
        blockers.append("traj_server_did_not_receive_bspline")
    if adapter.get("status") not in {"published", None}:
        blockers.append(f"controller_adapter_bad_status:{adapter.get('status')}")

    gate_passed = not blockers
    payload = {
        "schema": "mosim.real_ego_closed_loop_gate.v1",
        "status": "runtime_gate_passed" if gate_passed else "runtime_gate_blocked",
        "gate_passed": gate_passed,
        "start_position_target_m": start,
        "goal_position_target_m": goal,
        "obstacles_xy_radius_m": [list(item) for item in args.obstacle],
        "metrics": metrics,
        "final_goal_xy_error_m": round(final_goal_xy_error, 6) if final_goal_xy_error is not None else None,
        "topic_counts": {
            "position_cmd": position_cmd_count,
            "planner_setpoint": setpoint_count,
            "controller_output": controller_output_count,
            "controller_adapter_published": controller_published_count,
        },
        "truth_summary_status": truth_summary.get("status"),
        "truth_summary_count": truth_summary.get("count"),
        "ego_topic_recorder_status": recorder.get("status"),
        "controller_adapter_status": adapter.get("status"),
        "blockers": blockers,
        "artifacts": {
            "truth_jsonl": str(truth_path),
            "truth_summary_json": str(truth_summary_path),
            "ego_topic_recorder_json": str(recorder_path),
            "traj_server_log": str(traj_log_path),
            "traj_server_stderr_log": str(traj_stderr_path) if traj_stderr_path is not None else None,
            "controller_adapter_json": str(adapter_json_path),
            "controller_adapter_trace_jsonl": str(adapter_trace_path),
        },
        "claim_boundary": [
            "This gate requires Gazebo truth movement, planner command topics, ControllerOutput, actuator-adapter publication, obstacle clearance, goal approach, and landing.",
            "Passing this gate is still truth-feedback pre-acceptance, not final MWORKS controller-performance proof or multi-UAV readiness.",
        ],
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if gate_passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
