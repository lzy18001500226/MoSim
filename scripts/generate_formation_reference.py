#!/usr/bin/env python3
"""Generate Leader-Follower formation references and replay data."""

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


def read_leader_reference(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"time", "x_ref", "y_ref", "z_ref", "yaw_ref"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path} missing columns: {', '.join(sorted(missing))}")
        return [{key: float(value) for key, value in row.items() if value != ""} for row in reader]


def smooth_switch(time: float, start: float, duration: float) -> float:
    if duration <= 0:
        return 1.0 if time >= start else 0.0
    tau = (time - start) / duration
    if tau <= 0.0:
        return 0.0
    if tau >= 1.0:
        return 1.0
    return 3.0 * tau * tau - 2.0 * tau * tau * tau


def formation_offsets(formation_type: str, spacing: float) -> dict[str, list[float]]:
    if formation_type == "triangle":
        return {
            "uav_0": [0.0, 0.0, 0.0],
            "uav_1": [-spacing, -spacing, 0.0],
            "uav_2": [-spacing, spacing, 0.0],
        }
    if formation_type == "line":
        return {
            "uav_0": [0.0, 0.0, 0.0],
            "uav_1": [-spacing, 0.0, 0.0],
            "uav_2": [-2.0 * spacing, 0.0, 0.0],
        }
    raise ValueError(f"Unsupported formation type: {formation_type}")


def interpolate_offsets(
    time: float,
    spacing: float,
    switch: dict[str, Any],
    recover: dict[str, Any],
) -> tuple[dict[str, list[float]], str]:
    base_type = str(switch.get("from", "triangle"))
    current = formation_offsets(base_type, spacing)
    mode = base_type

    if switch.get("enabled", False):
        target_type = str(switch.get("to", "line"))
        target = formation_offsets(target_type, spacing)
        alpha = smooth_switch(time, float(switch.get("start_time_s", 0.0)), float(switch.get("duration_s", 0.0)))
        if alpha > 0.0:
            current = blend_offsets(current, target, alpha)
            mode = "switching_to_" + target_type if alpha < 1.0 else target_type

    if recover.get("enabled", False):
        target_type = str(recover.get("to", base_type))
        start_type = str(switch.get("to", "line"))
        start_offsets = formation_offsets(start_type, spacing)
        target = formation_offsets(target_type, spacing)
        alpha = smooth_switch(time, float(recover.get("start_time_s", 0.0)), float(recover.get("duration_s", 0.0)))
        if alpha > 0.0:
            current = blend_offsets(start_offsets, target, alpha)
            mode = "recovering_to_" + target_type if alpha < 1.0 else target_type

    return current, mode


def blend_offsets(a: dict[str, list[float]], b: dict[str, list[float]], alpha: float) -> dict[str, list[float]]:
    return {
        key: [(1.0 - alpha) * a[key][index] + alpha * b[key][index] for index in range(3)]
        for key in a
    }


def rotate_offset(offset: list[float], yaw: float) -> list[float]:
    c = math.cos(yaw)
    s = math.sin(yaw)
    return [
        c * offset[0] - s * offset[1],
        s * offset[0] + c * offset[1],
        offset[2],
    ]


def distance(a: list[float], b: list[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def generate_rows(config: dict[str, Any], leader_rows: list[dict[str, float]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    formation = config["formation"]
    spacing = float(formation.get("spacing_m", 1.5))
    switch = formation.get("switch", {})
    recover = formation.get("recover", {})
    if not isinstance(switch, dict):
        switch = {}
    if not isinstance(recover, dict):
        recover = {}

    ids = ["uav_0", "uav_1", "uav_2"]
    rows: list[dict[str, Any]] = []
    min_distance = math.inf
    error_sq_sum = 0.0
    error_count = 0
    max_error = 0.0
    mode_switches = 0
    last_mode = ""

    for leader in leader_rows:
        time = leader["time"]
        yaw = leader.get("yaw_ref", 0.0)
        offsets, mode = interpolate_offsets(time, spacing, switch, recover)
        if mode != last_mode:
            mode_switches += 1 if last_mode else 0
            last_mode = mode
        positions: dict[str, list[float]] = {}
        leader_pos = [leader["x_ref"], leader["y_ref"], leader["z_ref"]]
        for uav_id in ids:
            rotated = rotate_offset(offsets[uav_id], yaw)
            positions[uav_id] = [leader_pos[index] + rotated[index] for index in range(3)]

        for first, second in [("uav_0", "uav_1"), ("uav_0", "uav_2"), ("uav_1", "uav_2")]:
            min_distance = min(min_distance, distance(positions[first], positions[second]))

        for follower in ["uav_1", "uav_2"]:
            expected = offsets[follower]
            rel = rotate_offset([
                positions[follower][0] - positions["uav_0"][0],
                positions[follower][1] - positions["uav_0"][1],
                positions[follower][2] - positions["uav_0"][2],
            ], -yaw)
            err = distance(rel, expected)
            error_sq_sum += err * err
            error_count += 1
            max_error = max(max_error, err)

        row: dict[str, Any] = {"time": time, "formation_mode": mode}
        for uav_id in ids:
            row[f"{uav_id}_x_ref"] = positions[uav_id][0]
            row[f"{uav_id}_y_ref"] = positions[uav_id][1]
            row[f"{uav_id}_z_ref"] = positions[uav_id][2]
            row[f"{uav_id}_yaw_ref"] = yaw
        rows.append(row)

    safety_distance = float(formation.get("safety_distance_m", 0.8))
    metrics = {
        "experiment_id": config.get("experiment_id", ""),
        "scene_id": config.get("scene_id", ""),
        "formation_type": str(formation.get("initial_type", "triangle")),
        "uav_count": 3,
        "sample_count": len(rows),
        "duration_s": rows[-1]["time"] - rows[0]["time"] if rows else 0.0,
        "formation_error_rmse": math.sqrt(error_sq_sum / error_count) if error_count else 0.0,
        "formation_error_max": max_error,
        "minimum_inter_uav_distance": min_distance if math.isfinite(min_distance) else 0.0,
        "safety_distance_m": safety_distance,
        "formation_keeping_rate": 1.0 if max_error <= 1e-9 else 0.0,
        "formation_mode_switch_count": mode_switches,
        "switching_time_s": float(switch.get("duration_s", 0.0)) + float(recover.get("duration_s", 0.0)),
        "accepted": min_distance >= safety_distance,
    }
    safety_score = min(1.0, max(0.0, min_distance / max(safety_distance, 1e-9)))
    keeping_score = max(0.0, 1.0 - metrics["formation_error_rmse"])
    metrics["formation_score"] = 100.0 * (0.6 * safety_score + 0.4 * keeping_score)
    return rows, metrics


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_replay(path: Path, config: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    sample_stride = max(1, len(rows) // 600)
    frames = []
    for row in rows[::sample_stride]:
        uav = []
        for uav_id in ["uav_0", "uav_1", "uav_2"]:
            uav.append({
                "id": uav_id,
                "position": [row[f"{uav_id}_x_ref"], row[f"{uav_id}_y_ref"], row[f"{uav_id}_z_ref"]],
                "yaw": row[f"{uav_id}_yaw_ref"],
            })
        frames.append({"time": row["time"], "mode": row["formation_mode"], "uav": uav})
    payload = {
        "scene_id": config.get("scene_id", ""),
        "model_name": "Leader-Follower formation reference",
        "description": "Three-UAV triangle-line-triangle formation reference",
        "source": "scripts/generate_formation_reference.py",
        "frame_count": len(frames),
        "frames": frames,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path, nargs="?", default=Path("scenarios/formation/triangle_switch.yaml"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = read_yaml(args.scenario)
    leader_ref = config.get("leader_reference", {})
    reference = config.get("reference", {})
    result = config.get("result", {})
    if not isinstance(leader_ref, dict) or not isinstance(reference, dict) or not isinstance(result, dict):
        raise ValueError("scenario must contain leader_reference, reference, and result mappings")
    leader_rows = read_leader_reference(Path(str(leader_ref["file"])))
    rows, metrics = generate_rows(config, leader_rows)
    write_csv(Path(str(reference["file"])), rows)
    metrics_path = Path(str(result["metrics_file"]))
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_replay(Path(str(result["replay_file"])), config, rows)
    print(f"Formation CSV: {reference['file']}")
    print(f"Formation metrics: {result['metrics_file']}")
    print(f"Formation replay: {result['replay_file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
