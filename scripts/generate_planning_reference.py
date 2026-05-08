#!/usr/bin/env python3
"""Generate waypoint-based references and trackability reports."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - project fallback
    yaml = None


G = 9.81
MASS_KG = 1.0
THRUST_MAX_N = 18.0


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


def vector_sub(a: list[float], b: list[float]) -> list[float]:
    return [x - y for x, y in zip(a, b)]


def norm(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values))


def smoothstep(s: float) -> tuple[float, float, float, float]:
    position = 10.0 * s**3 - 15.0 * s**4 + 6.0 * s**5
    velocity = 30.0 * s**2 - 60.0 * s**3 + 30.0 * s**4
    acceleration = 60.0 * s - 180.0 * s**2 + 120.0 * s**3
    jerk = 60.0 - 360.0 * s + 360.0 * s**2
    return position, velocity, acceleration, jerk


def allocate_segment_times(waypoints: list[list[float]], v_ref: float, t_min: float) -> list[float]:
    durations = []
    for start, end in zip(waypoints[:-1], waypoints[1:]):
        length = norm(vector_sub(end, start))
        durations.append(max(t_min, length / max(v_ref, 1e-6)))
    return durations


def generate_rows(waypoints: list[list[float]], durations: list[float], dt: float, yaw_mode: str) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    elapsed = 0.0
    for segment_index, (start, end, duration) in enumerate(zip(waypoints[:-1], waypoints[1:], durations)):
        delta = vector_sub(end, start)
        steps = max(1, int(math.ceil(duration / dt)))
        for step in range(steps):
            if segment_index > 0 and step == 0:
                continue
            tau = min(step * dt, duration)
            s = tau / duration
            basis, dbasis, ddbasis, dddbasis = smoothstep(s)
            position = [start[i] + basis * delta[i] for i in range(3)]
            velocity = [dbasis * delta[i] / duration for i in range(3)]
            acceleration = [ddbasis * delta[i] / (duration * duration) for i in range(3)]
            jerk = [dddbasis * delta[i] / (duration**3) for i in range(3)]
            yaw = math.atan2(velocity[1], velocity[0]) if yaw_mode == "face_velocity" and norm(velocity[:2]) > 1e-9 else 0.0
            rows.append({
                "time": round(elapsed + tau, 10),
                "x_ref": position[0],
                "y_ref": position[1],
                "z_ref": position[2],
                "vx_ref": velocity[0],
                "vy_ref": velocity[1],
                "vz_ref": velocity[2],
                "ax_ref": acceleration[0],
                "ay_ref": acceleration[1],
                "az_ref": acceleration[2],
                "jx_ref": jerk[0],
                "jy_ref": jerk[1],
                "jz_ref": jerk[2],
                "yaw_ref": yaw,
            })
        elapsed += duration
    final = waypoints[-1]
    rows.append({
        "time": round(elapsed, 10),
        "x_ref": final[0],
        "y_ref": final[1],
        "z_ref": final[2],
        "vx_ref": 0.0,
        "vy_ref": 0.0,
        "vz_ref": 0.0,
        "ax_ref": 0.0,
        "ay_ref": 0.0,
        "az_ref": 0.0,
        "jx_ref": 0.0,
        "jy_ref": 0.0,
        "jz_ref": 0.0,
        "yaw_ref": rows[-1]["yaw_ref"] if rows else 0.0,
    })
    return rows


def violation_ratio(values: list[float], limit: float) -> float:
    if not values:
        return 0.0
    return sum(1 for value in values if value > limit) / len(values)


def path_length(waypoints: list[list[float]]) -> float:
    return sum(norm(vector_sub(end, start)) for start, end in zip(waypoints[:-1], waypoints[1:]))


def compute_trackability(
    rows: list[dict[str, float]],
    limits: dict[str, float],
    durations: list[float],
    waypoints: list[list[float]],
    iterations: int,
) -> dict[str, Any]:
    velocity = [norm([row["vx_ref"], row["vy_ref"], row["vz_ref"]]) for row in rows]
    acceleration = [norm([row["ax_ref"], row["ay_ref"], row["az_ref"]]) for row in rows]
    jerk = [norm([row["jx_ref"], row["jy_ref"], row["jz_ref"]]) for row in rows]
    tilt = [math.atan2(norm([row["ax_ref"], row["ay_ref"]]), G + row["az_ref"]) for row in rows if G + row["az_ref"] > 1e-9]
    required_thrust = [MASS_KG * norm([row["ax_ref"], row["ay_ref"], G + row["az_ref"]]) for row in rows]

    v_ratio = violation_ratio(velocity, limits["velocity_max_m_s"])
    a_ratio = violation_ratio(acceleration, limits["acceleration_max_m_s2"])
    j_ratio = violation_ratio(jerk, limits["jerk_max_m_s3"])
    tilt_ratio = violation_ratio(tilt, limits["tilt_max_rad"])
    sat_ratio = violation_ratio(required_thrust, THRUST_MAX_N * 0.85)
    score = max(0.0, min(1.0, 1.0 - 0.25 * v_ratio - 0.25 * a_ratio - 0.20 * j_ratio - 0.20 * tilt_ratio - 0.10 * sat_ratio))
    return {
        "planner_id": "waypoint_min_snap",
        "trajectory_model": "quintic_smoothstep",
        "sample_count": len(rows),
        "duration_s": rows[-1]["time"] - rows[0]["time"] if rows else 0.0,
        "iterations": iterations,
        "segment_count": len(durations),
        "segment_durations_s": durations,
        "path_length_m": path_length(waypoints),
        "trajectory_length_m": sum(norm(vector_sub([b["x_ref"], b["y_ref"], b["z_ref"]], [a["x_ref"], a["y_ref"], a["z_ref"]])) for a, b in zip(rows[:-1], rows[1:])),
        "max_velocity_m_s": max(velocity) if velocity else 0.0,
        "max_acceleration_m_s2": max(acceleration) if acceleration else 0.0,
        "max_jerk_m_s3": max(jerk) if jerk else 0.0,
        "max_tilt_rad": max(tilt) if tilt else 0.0,
        "predicted_saturation_ratio": sat_ratio,
        "velocity_violation_ratio": v_ratio,
        "acceleration_violation_ratio": a_ratio,
        "jerk_violation_ratio": j_ratio,
        "tilt_violation_ratio": tilt_ratio,
        "dynamic_violation_count": sum(1 for value in [v_ratio, a_ratio, j_ratio, tilt_ratio, sat_ratio] if value > 0.0),
        "final_trackability_score": score,
        "accepted": score >= 0.8,
    }


def generate_trackable_rows(
    waypoints: list[list[float]],
    base_durations: list[float],
    dt: float,
    yaw_mode: str,
    limits: dict[str, float],
    min_score: float,
    max_iterations: int,
    scale_factor: float,
    require_zero_dynamic_violations: bool,
) -> tuple[list[dict[str, float]], dict[str, Any]]:
    durations = list(base_durations)
    last_rows: list[dict[str, float]] = []
    last_report: dict[str, Any] = {}
    for iteration in range(1, max_iterations + 1):
        rows = generate_rows(waypoints, durations, dt, yaw_mode)
        report = compute_trackability(rows, limits, durations, waypoints, iteration)
        accepted = report["final_trackability_score"] >= min_score
        if require_zero_dynamic_violations:
            accepted = accepted and report["dynamic_violation_count"] == 0
        report["accepted"] = accepted
        last_rows = rows
        last_report = report
        if accepted:
            return rows, report
        durations = [duration * scale_factor for duration in durations]
    return last_rows, last_report


def write_csv(path: Path, rows: list[dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_replay(path: Path, scene_id: str, rows: list[dict[str, float]]) -> None:
    sample_stride = max(1, len(rows) // 600)
    frames = [
        {
            "time": row["time"],
            "uav": [{"id": "planned_reference", "position": [row["x_ref"], row["y_ref"], row["z_ref"]], "yaw": row["yaw_ref"]}],
        }
        for row in rows[::sample_stride]
    ]
    payload = {
        "scene_id": scene_id,
        "model_name": "Waypoint planner reference",
        "description": "Trackability-aware waypoint smoothstep reference",
        "source": "scripts/generate_planning_reference.py",
        "frame_count": len(frames),
        "frames": frames,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, nargs="?", default=Path("scenarios/planning/trackable_waypoint.yaml"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scenario = read_yaml(args.scenario)
    planner = scenario.get("planner", {})
    simulation = scenario.get("simulation", {})
    result = scenario.get("result", {})
    reference = scenario.get("reference", {})
    if not isinstance(planner, dict) or not isinstance(simulation, dict) or not isinstance(result, dict) or not isinstance(reference, dict):
        raise ValueError("scenario must contain planner, simulation, reference, and result mappings")

    params_file = Path(str(planner.get("params_file", "planners/waypoint/default.yaml")))
    params = read_yaml(params_file)
    limits = params.get("limits", {})
    time_alloc = params.get("time_allocation", {})
    if not isinstance(limits, dict) or not isinstance(time_alloc, dict):
        raise ValueError("planner config must contain limits and time_allocation mappings")

    waypoints = [[float(item) for item in waypoint] for waypoint in planner["waypoints"]]
    dt = float(simulation.get("step_size_s", 0.02))
    base_durations = allocate_segment_times(
        waypoints,
        float(time_alloc.get("velocity_reference_m_s", 2.0)),
        float(time_alloc.get("segment_time_min_s", 1.5)),
    )
    trackability = params.get("trackability", {})
    if not isinstance(trackability, dict):
        trackability = {}
    rows, report = generate_trackable_rows(
        waypoints,
        base_durations,
        dt,
        str(planner.get("yaw_mode", "fixed")),
        {key: float(value) for key, value in limits.items()},
        float(trackability.get("min_score", 0.8)),
        int(time_alloc.get("max_rescale_iterations", 5)),
        float(time_alloc.get("infeasible_scale_factor", 1.25)),
        bool(trackability.get("require_zero_dynamic_violations", True)),
    )
    report["scene_id"] = scenario.get("scene_id", "")
    report["experiment_id"] = scenario.get("experiment_id", "")
    report["reference_file"] = reference.get("file", "")

    write_csv(Path(str(reference["file"])), rows)
    report_path = Path(str(result["trackability_report"]))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_replay(Path(str(result["replay_file"])), str(scenario.get("scene_id", "")), rows)
    print(f"Reference CSV: {reference['file']}")
    print(f"Trackability report: {result['trackability_report']}")
    print(f"Replay JSON: {result['replay_file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
