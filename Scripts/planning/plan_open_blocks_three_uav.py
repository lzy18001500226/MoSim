#!/usr/bin/env python3
"""Plan and audit a synchronized three-UAV OpenBlocks formation route."""

from __future__ import annotations

import argparse
import copy
import csv
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
PLANNER_PATH = ROOT / "Scripts/planning/plan_astar_min_snap.py"
DEFAULT_CONFIG = ROOT / "Config/planners/astar_min_snap/map_open_blocks.yaml"
DEFAULT_OUTPUT = ROOT / "Results/planning/three_uav_open_blocks_mworks_20260720"
UAV_SPECS = (
    {"vehicle_id": "uav1", "start": [-41.0, -26.0, 1.0], "goal": [41.0, 26.0, 1.0]},
    {"vehicle_id": "uav2", "start": [-43.0, -26.0, 1.0], "goal": [43.0, 26.0, 1.0]},
    {"vehicle_id": "uav3", "start": [-41.0, -28.0, 1.0], "goal": [41.0, 28.0, 1.0]},
)
MIN_PAIR_DISTANCE_M = 1.0
SAMPLE_DT_S = 0.05


def load_planner() -> Any:
    spec = importlib.util.spec_from_file_location("mosim_astar_min_snap", PLANNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load planner: {PLANNER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_config(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Config root must be a mapping: {path}")
    return payload


def fixed_map_config(planner: Any, config: dict[str, Any]) -> dict[str, Any]:
    expanded = planner.expand_random_obstacles(planner.expand_wall_groups(config))
    random_spec = expanded["map"].get("random_obstacles")
    if isinstance(random_spec, dict):
        random_spec["enabled"] = False
    expanded["map"]["planning_safety_margin"] = 0.4
    expanded["local_planning"]["enabled"] = False
    expanded["limits"].update({
        "velocity_reference_m_s": 2.5,
        "velocity_max_m_s": 3.5,
        "acceleration_max_m_s2": 4.0,
        "jerk_max_m_s3": 12.0,
        "tilt_max_rad": 0.55,
    })
    return expanded


def plan_vehicle(planner: Any, fixed_config: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    config = copy.deepcopy(fixed_config)
    config["map"]["start"] = list(spec["start"])
    config["map"]["goal"] = list(spec["goal"])
    raw_path, path, rows, report = planner.plan_trackable(config)
    if not report.get("accepted", False):
        raise RuntimeError(
            f"{spec['vehicle_id']} trackability gate failed: "
            f"min_clearance={report.get('min_obstacle_distance_m')}, "
            f"violations={report.get('dynamic_violation_count')}, "
            f"score={report.get('trackability_score')}"
        )
    return {
        "vehicle_id": spec["vehicle_id"],
        "raw_path": raw_path,
        "path": path,
        "rows": rows,
        "report": report,
    }


def interpolate_row(rows: list[dict[str, float]], query_time: float) -> dict[str, float]:
    if query_time <= 0.0:
        return dict(rows[0])
    if query_time >= rows[-1]["time"]:
        return dict(rows[-1])
    lo = 0
    hi = len(rows) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if rows[mid]["time"] <= query_time:
            lo = mid
        else:
            hi = mid
    a = rows[lo]
    b = rows[hi]
    ratio = (query_time - a["time"]) / max(1e-12, b["time"] - a["time"])
    result = {"time": query_time}
    for key in a:
        if key != "time":
            result[key] = a[key] + ratio * (b[key] - a[key])
    return result


def synchronized_rows(
    rows: list[dict[str, float]], delay_s: float, total_duration_s: float
) -> list[dict[str, float]]:
    sample_count = int(math.ceil(total_duration_s / SAMPLE_DT_S))
    synchronized: list[dict[str, float]] = []
    for index in range(sample_count + 1):
        now = min(total_duration_s, index * SAMPLE_DT_S)
        source_time = min(rows[-1]["time"], max(0.0, now - delay_s))
        row = interpolate_row(rows, source_time)
        row["time"] = now
        synchronized.append(row)
    return synchronized


def pair_distance(a: dict[str, float], b: dict[str, float]) -> float:
    return math.sqrt(
        (a["x_ref"] - b["x_ref"]) ** 2
        + (a["y_ref"] - b["y_ref"]) ** 2
        + (a["z_ref"] - b["z_ref"]) ** 2
    )


def evaluate_schedule(plans: list[dict[str, Any]], delays: list[float]) -> tuple[list[list[dict[str, float]]], dict[str, Any]]:
    total_duration = max(delay + plan["rows"][-1]["time"] for plan, delay in zip(plans, delays))
    rows = [synchronized_rows(plan["rows"], delay, total_duration) for plan, delay in zip(plans, delays)]
    minimum = float("inf")
    minimum_pair = ""
    minimum_time = 0.0
    violations = 0
    for index in range(len(rows[0])):
        for first, second in ((0, 1), (0, 2), (1, 2)):
            value = pair_distance(rows[first][index], rows[second][index])
            if value < minimum:
                minimum = value
                minimum_pair = f"uav{first + 1}-uav{second + 1}"
                minimum_time = rows[0][index]["time"]
            if value < MIN_PAIR_DISTANCE_M:
                violations += 1
    return rows, {
        "delays_s": delays,
        "duration_s": total_duration,
        "minimum_pair_distance_m": minimum,
        "minimum_pair": minimum_pair,
        "minimum_pair_distance_time_s": minimum_time,
        "pair_distance_threshold_m": MIN_PAIR_DISTANCE_M,
        "pair_distance_violation_count": violations,
        "accepted": violations == 0,
    }


def choose_schedule(plans: list[dict[str, Any]]) -> tuple[list[list[dict[str, float]]], dict[str, Any]]:
    for spacing in (8.0, 10.0, 12.0, 14.0, 16.0):
        delays = [0.0, spacing, 2.0 * spacing]
        rows, report = evaluate_schedule(plans, delays)
        if report["accepted"]:
            report["schedule_search_spacing_s"] = spacing
            return rows, report
    raise RuntimeError(f"No collision-safe temporal schedule found; last report={report}")


def write_csv(path: Path, rows: list[dict[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_lf(path: Path) -> None:
    path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")


def write_preview(path: Path, planner: Any, config: dict[str, Any], plans: list[dict[str, Any]]) -> None:
    grid = planner.OccupancyGrid(config["map"])
    width, height, pad = 1200, 800, 45
    sx = lambda x: pad + (x - grid.x_min) / (grid.x_max - grid.x_min) * (width - 2 * pad)
    sy = lambda y: height - pad - (y - grid.y_min) / (grid.y_max - grid.y_min) * (height - 2 * pad)
    colors = ("#0072B2", "#D55E00", "#009E73")
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f7f8fa"/>',
    ]
    for obstacle in grid.obstacles:
        x0, y0, x1, y1 = planner.obstacle_xy_bounds(obstacle)
        parts.append(
            f'<rect x="{sx(x0):.2f}" y="{sy(y1):.2f}" width="{sx(x1)-sx(x0):.2f}" '
            f'height="{sy(y0)-sy(y1):.2f}" fill="#4b5563" opacity="0.55"/>'
        )
    for plan, color in zip(plans, colors):
        points = " ".join(f"{sx(p.x):.2f},{sy(p.y):.2f}" for p in plan["path"])
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
        parts.append(f'<circle cx="{sx(plan["path"][0].x):.2f}" cy="{sy(plan["path"][0].y):.2f}" r="6" fill="{color}"/>')
        parts.append(f'<circle cx="{sx(plan["path"][-1].x):.2f}" cy="{sy(plan["path"][-1].y):.2f}" r="6" fill="none" stroke="{color}" stroke-width="3"/>')
    parts.append('<text x="45" y="28" font-family="Segoe UI, sans-serif" font-size="18">90 x 60 m OpenBlocks three-UAV preplanned formation route</text>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts) + "\n", encoding="utf-8", newline="\n")


def compact_planner_report(report: dict[str, Any]) -> dict[str, Any]:
    omitted = {"truth_obstacles"}
    return {key: value for key, value in report.items() if key not in omitted}


def run(config_path: Path, output_dir: Path) -> dict[str, Any]:
    planner = load_planner()
    source_config = read_config(config_path)
    fixed_config = fixed_map_config(planner, source_config)
    plans = [plan_vehicle(planner, fixed_config, spec) for spec in UAV_SPECS]
    synchronized, schedule = choose_schedule(plans)

    raw_dir = output_dir / "raw"
    for plan, rows in zip(plans, synchronized):
        write_csv(raw_dir / f"{plan['vehicle_id']}_reference.csv", rows)
        path_csv = raw_dir / f"{plan['vehicle_id']}_path_simplified.csv"
        planner.write_path_csv(path_csv, plan["path"])
        normalize_lf(path_csv)
    write_preview(output_dir / "figures" / "three_uav_open_blocks_preview.svg", planner, fixed_config, plans)

    result = {
        "schema": "mosim.planning.three_uav_open_blocks.v1",
        "status": "accepted" if schedule["accepted"] else "blocked",
        "claim_boundary": "offline global planning plus synchronized collision audit; MWORKS plant tracking is a separate gate",
        "forbidden_claims": [
            "online replanning",
            "unknown-environment exploration",
            "live MID360 obstacle avoidance",
            "MWORKS whole-aircraft tracking before a real solver run",
        ],
        "map": {
            "map_id": source_config.get("map_id"),
            "bounds_m": source_config["map"]["bounds"],
            "truth_obstacle_count": len(fixed_config["map"]["obstacles"]),
            "safety_margin_m": fixed_config["map"]["safety_margin"],
        },
        "schedule": schedule,
        "formation_schedule": [
            {"phase": "launch_triangle", "description": "three separated launch points"},
            {"phase": "obstacle_corridor_column", "description": "time-separated independent A* references"},
            {"phase": "arrival_triangle", "description": "three separated goal points"},
        ],
        "vehicles": [
            {
                "vehicle_id": plan["vehicle_id"],
                "start": list(UAV_SPECS[index]["start"]),
                "goal": list(UAV_SPECS[index]["goal"]),
                "delay_s": schedule["delays_s"][index],
                "path_length_m": plan["report"]["path_length_m"],
                "path_point_count": plan["report"]["simplified_path_points"],
                "min_obstacle_distance_m": plan["report"]["min_obstacle_distance_m"],
                "trackability_score": plan["report"]["trackability_score"],
                "planner_report": compact_planner_report(plan["report"]),
            }
            for index, plan in enumerate(plans)
        ],
    }
    metrics_path = output_dir / "metrics" / "three_uav_planning_metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run(args.config.resolve(), args.output_dir.resolve())
    print(json.dumps({
        "status": result["status"],
        "minimum_pair_distance_m": result["schedule"]["minimum_pair_distance_m"],
        "duration_s": result["schedule"]["duration_s"],
        "output_dir": str(args.output_dir.resolve()),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
