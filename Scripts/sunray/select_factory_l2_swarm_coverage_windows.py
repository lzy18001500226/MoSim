#!/usr/bin/env python3
"""Rank Factory L2 multi-UAV coverage windows before live swarm runs.

This is an offline selector. It does not start ROS, Gazebo, PX4, MAVROS, RViz,
or any planner. Its purpose is to stop blind start-index trials by rejecting
windows that look similar to recent takeoff/first-planning failures and by
ranking the remaining windows with simple geometry checks.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path outside MoSim workspace: {value}")
    return resolved


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def load_csv(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            parsed: dict[str, Any] = {}
            for key, value in row.items():
                if value is None or value == "":
                    parsed[key] = value
                    continue
                try:
                    parsed[key] = float(value)
                except ValueError:
                    parsed[key] = value
            rows.append(parsed)
    return rows


def as_waypoints(raw: Any) -> list[list[float]]:
    if not isinstance(raw, list):
        raise SystemExit("waypoints must be a list")
    out: list[list[float]] = []
    for item in raw:
        if not isinstance(item, list) or len(item) < 3:
            raise SystemExit(f"invalid waypoint: {item!r}")
        out.append([float(item[0]), float(item[1]), float(item[2])])
    return out


def load_boundary(path: Path) -> dict[str, float]:
    data = load_json(path)
    raw = data.get("exploration_boundary") or data.get("boundary") or {}
    boundary = {
        "min_x_m": as_float(raw.get("min_x_m")),
        "max_x_m": as_float(raw.get("max_x_m")),
        "min_y_m": as_float(raw.get("min_y_m")),
        "max_y_m": as_float(raw.get("max_y_m")),
    }
    if boundary["max_x_m"] <= boundary["min_x_m"] or boundary["max_y_m"] <= boundary["min_y_m"]:
        raise SystemExit(f"invalid coverage boundary in {path}")
    return boundary


def grid_shape(boundary: dict[str, float], resolution: float) -> tuple[int, int]:
    nx = max(1, math.ceil((boundary["max_x_m"] - boundary["min_x_m"]) / resolution))
    ny = max(1, math.ceil((boundary["max_y_m"] - boundary["min_y_m"]) / resolution))
    return nx, ny


def cell_for_xy(
    x: float,
    y: float,
    boundary: dict[str, float],
    resolution: float,
) -> tuple[int, int] | None:
    if x < boundary["min_x_m"] or x > boundary["max_x_m"] or y < boundary["min_y_m"] or y > boundary["max_y_m"]:
        return None
    nx, ny = grid_shape(boundary, resolution)
    ix = min(max(int((x - boundary["min_x_m"]) / resolution), 0), nx - 1)
    iy = min(max(int((y - boundary["min_y_m"]) / resolution), 0), ny - 1)
    return ix, iy


def add_disc_cells(
    cells: set[tuple[int, int]],
    x: float,
    y: float,
    radius: float,
    boundary: dict[str, float],
    resolution: float,
) -> None:
    center = cell_for_xy(x, y, boundary, resolution)
    if center is None:
        return
    cx, cy = center
    r_cells = max(0, math.ceil(radius / resolution))
    for ix in range(cx - r_cells, cx + r_cells + 1):
        px = boundary["min_x_m"] + (ix + 0.5) * resolution
        if px < boundary["min_x_m"] or px > boundary["max_x_m"]:
            continue
        for iy in range(cy - r_cells, cy + r_cells + 1):
            py = boundary["min_y_m"] + (iy + 0.5) * resolution
            if py < boundary["min_y_m"] or py > boundary["max_y_m"]:
                continue
            if math.hypot(px - x, py - y) <= radius:
                cells.add((ix, iy))


def phase_filter(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    filtered = [row for row in rows if row.get("phase") in {"exploration_execute", "ego_execute"}]
    return filtered or rows


def cells_from_waypoints(
    waypoints: list[list[float]],
    boundary: dict[str, float],
    resolution: float,
    sensor_radius: float,
) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    path_cells: set[tuple[int, int]] = set()
    sensor_cells: set[tuple[int, int]] = set()
    for waypoint in waypoints:
        cell = cell_for_xy(waypoint[0], waypoint[1], boundary, resolution)
        if cell is not None:
            path_cells.add(cell)
            add_disc_cells(sensor_cells, waypoint[0], waypoint[1], sensor_radius, boundary, resolution)
    return path_cells, sensor_cells


def collect_run_sensor_cells(
    run_dir: Path,
    boundary: dict[str, float],
    resolution: float,
    sensor_radius: float,
) -> set[tuple[int, int]]:
    sensor_cells: set[tuple[int, int]] = set()
    for uid in (1, 2, 3):
        rows = load_csv(run_dir / f"uav{uid}_truth.csv")
        for row in phase_filter(rows):
            x = as_float(row.get("x"))
            y = as_float(row.get("y"))
            add_disc_cells(sensor_cells, x, y, sensor_radius, boundary, resolution)
    if sensor_cells:
        return sensor_cells
    rows = load_csv(run_dir / "truth.csv")
    for row in phase_filter(rows):
        x = as_float(row.get("x"))
        y = as_float(row.get("y"))
        add_disc_cells(sensor_cells, x, y, sensor_radius, boundary, resolution)
    return sensor_cells


def metrics_passed(run_dir: Path) -> bool:
    metrics = load_json(run_dir / "EGO_SWARM_METRICS.json") or load_json(run_dir / "EGO_SINGLE_METRICS.json")
    blockers = metrics.get("blockers")
    return metrics.get("status") == "passed" and (not isinstance(blockers, list) or not blockers)


def collect_baseline_sensor_cells(
    run_dirs: list[Path],
    boundary: dict[str, float],
    resolution: float,
    sensor_radius: float,
) -> set[tuple[int, int]]:
    cells: set[tuple[int, int]] = set()
    for run_dir in run_dirs:
        if not metrics_passed(run_dir):
            continue
        cells.update(collect_run_sensor_cells(run_dir, boundary, resolution, sensor_radius))
    return cells


def dist_xy(a: list[float], b: list[float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def contiguous_partition(waypoints: list[list[float]], uav_num: int) -> list[list[list[float]]]:
    parts: list[list[list[float]]] = []
    n = len(waypoints)
    for idx in range(uav_num):
        start = round(idx * n / uav_num)
        stop = round((idx + 1) * n / uav_num)
        parts.append(waypoints[start:stop])
    return parts


def contiguous_swap_23_partition(waypoints: list[list[float]], uav_num: int) -> list[list[list[float]]]:
    parts = contiguous_partition(waypoints, uav_num)
    if uav_num == 3:
        parts[1], parts[2] = parts[2], parts[1]
    return parts


def round_robin_partition(waypoints: list[list[float]], uav_num: int) -> list[list[list[float]]]:
    parts: list[list[list[float]]] = [[] for _ in range(uav_num)]
    for idx, waypoint in enumerate(waypoints):
        parts[idx % uav_num].append(waypoint)
    return parts


def spatial_y_bands_partition(waypoints: list[list[float]], uav_num: int) -> list[list[list[float]]]:
    if not waypoints:
        return [[] for _ in range(uav_num)]
    min_y = min(wp[1] for wp in waypoints)
    max_y = max(wp[1] for wp in waypoints)
    span = max(max_y - min_y, 1e-9)
    parts: list[list[list[float]]] = [[] for _ in range(uav_num)]
    for waypoint in waypoints:
        band = min(uav_num - 1, max(0, int(((max_y - waypoint[1]) / span) * uav_num)))
        parts[band].append(waypoint)
    return parts


def spatial_x_bands_partition(waypoints: list[list[float]], uav_num: int) -> list[list[list[float]]]:
    if not waypoints:
        return [[] for _ in range(uav_num)]
    min_x = min(wp[0] for wp in waypoints)
    max_x = max(wp[0] for wp in waypoints)
    span = max(max_x - min_x, 1e-9)
    parts: list[list[list[float]]] = [[] for _ in range(uav_num)]
    for waypoint in waypoints:
        band = min(uav_num - 1, max(0, int(((waypoint[0] - min_x) / span) * uav_num)))
        parts[band].append(waypoint)
    return parts


def partition(policy: str, waypoints: list[list[float]], uav_num: int) -> list[list[list[float]]]:
    if policy == "contiguous_swap_23":
        return contiguous_swap_23_partition(waypoints, uav_num)
    if policy == "round_robin":
        return round_robin_partition(waypoints, uav_num)
    if policy == "spatial_y_bands":
        return spatial_y_bands_partition(waypoints, uav_num)
    if policy == "spatial_x_bands":
        return spatial_x_bands_partition(waypoints, uav_num)
    return contiguous_partition(waypoints, uav_num)


def min_same_round_distance(parts: list[list[list[float]]]) -> float:
    min_len = min((len(part) for part in parts), default=0)
    best = float("inf")
    for round_idx in range(min_len):
        round_points = [part[round_idx] for part in parts]
        for i, a in enumerate(round_points):
            for b in round_points[i + 1 :]:
                best = min(best, dist_xy(a, b))
    return best if math.isfinite(best) else 0.0


def max_step_distance(parts: list[list[list[float]]]) -> float:
    best = 0.0
    for part in parts:
        for a, b in zip(part, part[1:]):
            best = max(best, dist_xy(a, b))
    return best


def min_failed_distance(parts: list[list[list[float]]], failed_points: list[list[float]]) -> float | None:
    if not failed_points:
        return None
    best = float("inf")
    for part in parts:
        for waypoint in part:
            for failed in failed_points:
                best = min(best, dist_xy(waypoint, failed))
    return best if math.isfinite(best) else None


def collect_failed_points(run_dirs: list[Path]) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    for run_dir in run_dirs:
        chain = load_json(run_dir / "SWARM_TARGET_CHAIN_PROBE.json")
        metrics = load_json(run_dir / "EGO_SWARM_METRICS.json")
        probe = load_json(run_dir / "FACTORY_L2_DIFF_SWARM_COVERAGE_PROBE.json")
        blockers = chain.get("blockers") or metrics.get("blockers") or []
        if not blockers:
            continue
        # Pre-takeoff failures do not have blocked target-chain rounds. Keep
        # their spawn/initial target points out of the next live window.
        if not chain.get("rounds"):
            for source_key in ("uav_starts", "initial_targets"):
                for uav_key, point in (probe.get(source_key) or {}).items():
                    if isinstance(point, list) and len(point) >= 2:
                        points.append(
                            {
                                "run": str(run_dir),
                                "kind": f"pre_chain_{source_key}",
                                "uav": uav_key,
                                "point": [
                                    float(point[0]),
                                    float(point[1]),
                                    float(point[2]) if len(point) > 2 else 0.0,
                                ],
                                "blockers": blockers,
                            }
                        )
        for round_item in chain.get("rounds", []) or []:
            if round_item.get("status") != "blocked":
                continue
            for uav_key, target in (round_item.get("targets") or {}).items():
                if isinstance(target, list) and len(target) >= 2:
                    points.append(
                        {
                            "run": str(run_dir),
                            "kind": "blocked_target",
                            "uav": uav_key,
                            "point": [float(target[0]), float(target[1]), float(target[2]) if len(target) > 2 else 0.0],
                            "blockers": blockers,
                        }
                    )
            for uav_key, snap in (round_item.get("last_snapshots") or {}).items():
                if not isinstance(snap, dict):
                    continue
                if float(snap.get("error_xy_m") or 0.0) < 0.75:
                    continue
                points.append(
                    {
                        "run": str(run_dir),
                        "kind": "stuck_snapshot",
                        "uav": uav_key,
                        "point": [
                            float(snap.get("x") or 0.0),
                            float(snap.get("y") or 0.0),
                            float(snap.get("z") or 0.0),
                        ],
                        "blockers": blockers,
                    }
                )
    return points


def evaluate_window(
    waypoints: list[list[float]],
    start_index: int,
    args: argparse.Namespace,
    failed_xyz: list[list[float]],
    boundary: dict[str, float] | None,
    baseline_sensor_cells: set[tuple[int, int]],
    total_coverage_cells: int,
) -> dict[str, Any] | None:
    window_count = args.partition_window_goals_per_uav * args.uav_num
    subset = waypoints[start_index : start_index + window_count]
    if len(subset) < args.uav_num:
        return None
    parts = partition(args.policy, subset, args.uav_num)
    if args.max_goals_per_uav > 0:
        parts = [part[: args.max_goals_per_uav] for part in parts]
    if any(not part for part in parts):
        return None
    flattened = [point for part in parts for point in part]

    min_round = min_same_round_distance(parts)
    max_step = max_step_distance(parts)
    failed_dist = min_failed_distance(parts, failed_xyz)
    first_points = [part[0] for part in parts]
    first_round_spread = min_same_round_distance([[point] for point in first_points])

    reject_reasons: list[str] = []
    if min_round < args.min_same_round_target_distance_m:
        reject_reasons.append("same_round_distance_below_threshold")
    if first_round_spread < args.min_first_round_distance_m:
        reject_reasons.append("first_round_distance_below_threshold")
    if failed_dist is not None and failed_dist < args.min_failed_point_distance_m:
        reject_reasons.append("near_recent_failed_point")
    if max_step > args.max_per_uav_step_m:
        reject_reasons.append("per_uav_step_too_large")

    candidate_path_cells: set[tuple[int, int]] = set()
    candidate_sensor_cells: set[tuple[int, int]] = set()
    marginal_sensor_cells: set[tuple[int, int]] = set()
    marginal_sensor_ratio = 0.0
    candidate_sensor_ratio = 0.0
    baseline_sensor_ratio = 0.0
    if boundary is not None and total_coverage_cells > 0:
        candidate_path_cells, candidate_sensor_cells = cells_from_waypoints(
            flattened,
            boundary,
            args.coverage_grid_resolution_m,
            args.coverage_sensor_radius_m,
        )
        marginal_sensor_cells = candidate_sensor_cells - baseline_sensor_cells
        candidate_sensor_ratio = len(candidate_sensor_cells) / total_coverage_cells
        baseline_sensor_ratio = len(baseline_sensor_cells) / total_coverage_cells
        marginal_sensor_ratio = len(marginal_sensor_cells) / total_coverage_cells
        if args.min_marginal_sensor_cells > 0 and len(marginal_sensor_cells) < args.min_marginal_sensor_cells:
            reject_reasons.append("marginal_coverage_below_threshold")

    score = 0.0
    score += min(min_round, 30.0) * 2.0
    score += min(first_round_spread, 30.0)
    score += min(failed_dist or args.min_failed_point_distance_m, 40.0)
    score -= max(0.0, max_step - args.preferred_max_step_m) * 1.5
    score += len(marginal_sensor_cells) * args.marginal_sensor_cell_weight

    return {
        "start_index": start_index,
        "status": "candidate" if not reject_reasons else "rejected",
        "reject_reasons": reject_reasons,
        "score": round(score, 4),
        "min_same_round_distance_m": min_round,
        "first_round_min_distance_m": first_round_spread,
        "max_per_uav_step_m": max_step,
        "min_distance_to_failed_point_m": failed_dist,
        "coverage_proxy": {
            "baseline_sensor_cells": len(baseline_sensor_cells),
            "baseline_sensor_footprint_ratio": baseline_sensor_ratio,
            "candidate_path_cells": len(candidate_path_cells),
            "candidate_sensor_footprint_cells": len(candidate_sensor_cells),
            "candidate_sensor_footprint_ratio": candidate_sensor_ratio,
            "marginal_sensor_footprint_cells": len(marginal_sensor_cells),
            "marginal_sensor_footprint_ratio": marginal_sensor_ratio,
            "grid_resolution_m": args.coverage_grid_resolution_m,
            "sensor_radius_m": args.coverage_sensor_radius_m,
        },
        "first_points": {
            f"uav{idx + 1}": point for idx, point in enumerate(first_points)
        },
        "per_uav_goal_count": [len(part) for part in parts],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--uav-num", type=int, default=3, choices=[1, 2, 3])
    parser.add_argument(
        "--policy",
        choices=["contiguous", "contiguous_swap_23", "round_robin", "spatial_y_bands", "spatial_x_bands"],
        default="contiguous_swap_23",
    )
    parser.add_argument("--partition-window-goals-per-uav", type=int, default=76)
    parser.add_argument("--max-goals-per-uav", type=int, default=5)
    parser.add_argument("--start-min", type=int, default=0)
    parser.add_argument("--start-max", type=int, default=0)
    parser.add_argument("--step", type=int, default=10)
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument("--min-same-round-target-distance-m", type=float, default=8.0)
    parser.add_argument("--min-first-round-distance-m", type=float, default=8.0)
    parser.add_argument("--min-failed-point-distance-m", type=float, default=8.0)
    parser.add_argument("--preferred-max-step-m", type=float, default=8.0)
    parser.add_argument("--max-per-uav-step-m", type=float, default=20.0)
    parser.add_argument("--failed-run", action="append", default=[])
    parser.add_argument("--baseline-run", action="append", default=[])
    parser.add_argument("--coverage-envelope", default="Config/gazebo/scene_profiles/factory_l2_exploration_envelope.json")
    parser.add_argument("--coverage-grid-resolution-m", type=float, default=2.0)
    parser.add_argument("--coverage-sensor-radius-m", type=float, default=8.0)
    parser.add_argument("--min-marginal-sensor-cells", type=int, default=0)
    parser.add_argument("--marginal-sensor-cell-weight", type=float, default=0.2)
    args = parser.parse_args()

    packet = load_json(repo_path(args.input_json))
    waypoints = as_waypoints(packet.get("waypoints"))
    start_max = args.start_max if args.start_max > 0 else max(0, len(waypoints) - args.uav_num)
    if args.step <= 0:
        raise SystemExit("--step must be positive")
    if args.partition_window_goals_per_uav <= 0:
        raise SystemExit("--partition-window-goals-per-uav must be positive")

    failed_details = collect_failed_points([repo_path(path) for path in args.failed_run])
    failed_xyz = [item["point"] for item in failed_details]
    boundary: dict[str, float] | None = None
    baseline_sensor_cells: set[tuple[int, int]] = set()
    total_coverage_cells = 0
    if args.baseline_run:
        boundary = load_boundary(repo_path(args.coverage_envelope))
        nx, ny = grid_shape(boundary, args.coverage_grid_resolution_m)
        total_coverage_cells = nx * ny
        baseline_sensor_cells = collect_baseline_sensor_cells(
            [repo_path(path) for path in args.baseline_run],
            boundary,
            args.coverage_grid_resolution_m,
            args.coverage_sensor_radius_m,
        )
    evaluations: list[dict[str, Any]] = []
    for start_index in range(args.start_min, start_max + 1, args.step):
        item = evaluate_window(
            waypoints,
            start_index,
            args,
            failed_xyz,
            boundary,
            baseline_sensor_cells,
            total_coverage_cells,
        )
        if item is not None:
            evaluations.append(item)

    candidates = [item for item in evaluations if item["status"] == "candidate"]
    candidates.sort(key=lambda item: item["score"], reverse=True)
    rejected = [item for item in evaluations if item["status"] == "rejected"]
    rejected.sort(key=lambda item: (len(item["reject_reasons"]), -item["score"]))

    output = {
        "schema": "mosim.factory_l2_swarm_coverage_window_selection.v1",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_packet": str(repo_path(args.input_json)),
        "source_waypoint_count": len(waypoints),
        "scan": {
            "start_min": args.start_min,
            "start_max": start_max,
            "step": args.step,
            "policy": args.policy,
            "uav_num": args.uav_num,
            "partition_window_goals_per_uav": args.partition_window_goals_per_uav,
            "max_goals_per_uav": args.max_goals_per_uav,
        },
        "thresholds": {
            "min_same_round_target_distance_m": args.min_same_round_target_distance_m,
            "min_first_round_distance_m": args.min_first_round_distance_m,
            "min_failed_point_distance_m": args.min_failed_point_distance_m,
            "preferred_max_step_m": args.preferred_max_step_m,
            "max_per_uav_step_m": args.max_per_uav_step_m,
            "min_marginal_sensor_cells": args.min_marginal_sensor_cells,
        },
        "coverage_proxy": {
            "enabled": bool(args.baseline_run),
            "envelope": str(repo_path(args.coverage_envelope)) if args.baseline_run else None,
            "baseline_run_count": len(args.baseline_run),
            "baseline_sensor_cells": len(baseline_sensor_cells),
            "baseline_sensor_footprint_ratio": (
                len(baseline_sensor_cells) / total_coverage_cells if total_coverage_cells else 0.0
            ),
            "grid_resolution_m": args.coverage_grid_resolution_m,
            "sensor_radius_m": args.coverage_sensor_radius_m,
            "marginal_sensor_cell_weight": args.marginal_sensor_cell_weight,
            "claim_boundary": (
                "Offline route waypoint sensor-footprint proxy for ranking only; "
                "live run coverage must still be rebuilt from truth logs."
            ),
        },
        "failed_points": failed_details,
        "candidate_count": len(candidates),
        "rejected_count": len(rejected),
        "recommended": candidates[: args.top_n],
        "top_rejected": rejected[: args.top_n],
        "claim_boundary": (
            "Offline geometry/history selector only. A recommended start_index "
            "still needs live g5/g23 ROS1 Sunray/PX4/MAVROS/Diff-Planner evidence."
        ),
    }
    out_path = repo_path(args.output_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(out_path)
    if candidates:
        print(f"recommended_start_index={candidates[0]['start_index']}")
    print(f"candidate_count={len(candidates)} rejected_count={len(rejected)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
