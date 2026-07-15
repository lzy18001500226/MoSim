#!/usr/bin/env python3
"""Build a Factory L2 indoor coverage packet from completed exploration runs.

This is an offline evidence reducer. It does not start ROS, Gazebo, PX4,
MAVROS, RViz, UE, or any planner. The coverage numbers are deliberately named
as proxies unless backed by an explicit mapper output.
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
DEFAULT_ENVELOPE = ROOT / "Config/gazebo/scene_profiles/factory_l2_exploration_envelope.json"


def repo_path(value: str | Path) -> Path:
    text = str(value)
    if text.startswith("/mnt/c/") and not ROOT.as_posix().startswith("/mnt/c/"):
        text = "C:/" + text[len("/mnt/c/") :]
    path = Path(text)
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path outside MoSim workspace: {value}")
    return resolved


def rel(path: str | Path) -> str:
    p = Path(path)
    try:
        return p.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return p.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


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


def xy(row: dict[str, Any]) -> tuple[float, float]:
    return as_float(row.get("x")), as_float(row.get("y"))


def z(row: dict[str, Any]) -> float:
    return as_float(row.get("z"))


def phase_filter(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    filtered = [row for row in rows if row.get("phase") in {"exploration_execute", "ego_execute"}]
    return filtered or rows


def grid_shape(boundary: dict[str, float], resolution: float) -> tuple[int, int]:
    nx = max(1, math.ceil((boundary["max_x_m"] - boundary["min_x_m"]) / resolution))
    ny = max(1, math.ceil((boundary["max_y_m"] - boundary["min_y_m"]) / resolution))
    return nx, ny


def add_cell(cells: set[tuple[int, int]], x: float, y: float, boundary: dict[str, float], resolution: float) -> bool:
    if x < boundary["min_x_m"] or x > boundary["max_x_m"] or y < boundary["min_y_m"] or y > boundary["max_y_m"]:
        return False
    ix = min(max(int((x - boundary["min_x_m"]) / resolution), 0), math.ceil((boundary["max_x_m"] - boundary["min_x_m"]) / resolution) - 1)
    iy = min(max(int((y - boundary["min_y_m"]) / resolution), 0), math.ceil((boundary["max_y_m"] - boundary["min_y_m"]) / resolution) - 1)
    cells.add((ix, iy))
    return True


def add_disc(
    cells: set[tuple[int, int]],
    x: float,
    y: float,
    radius: float,
    boundary: dict[str, float],
    resolution: float,
) -> None:
    r_cells = max(0, math.ceil(radius / resolution))
    cx = int((x - boundary["min_x_m"]) / resolution)
    cy = int((y - boundary["min_y_m"]) / resolution)
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


def summarize_rows(
    rows: list[dict[str, Any]],
    boundary: dict[str, float],
    z_policy: dict[str, float],
    resolution: float,
    sensor_radius: float,
) -> dict[str, Any]:
    used = phase_filter(rows)
    path_cells: set[tuple[int, int]] = set()
    sensor_cells: set[tuple[int, int]] = set()
    inside = 0
    outside = 0
    z_low = 0
    z_high = 0
    for row in used:
        x, y = xy(row)
        zz = z(row)
        if add_cell(path_cells, x, y, boundary, resolution):
            inside += 1
            add_disc(sensor_cells, x, y, sensor_radius, boundary, resolution)
        else:
            outside += 1
        if zz < z_policy["min_cmd_z_m"]:
            z_low += 1
        if zz > z_policy["max_cmd_z_m"]:
            z_high += 1
    xs = [xy(row)[0] for row in used]
    ys = [xy(row)[1] for row in used]
    zs = [z(row) for row in used]
    nx, ny = grid_shape(boundary, resolution)
    total = nx * ny
    return {
        "source_rows": len(rows),
        "used_rows": len(used),
        "inside_boundary_rows": inside,
        "outside_boundary_rows": outside,
        "z_low_rows": z_low,
        "z_high_rows": z_high,
        "path_cells": len(path_cells),
        "path_coverage_ratio": len(path_cells) / total,
        "sensor_radius_m": sensor_radius,
        "sensor_footprint_cells": len(sensor_cells),
        "sensor_footprint_coverage_ratio": len(sensor_cells) / total,
        "bounds": {
            "min_x": min(xs) if xs else None,
            "max_x": max(xs) if xs else None,
            "min_y": min(ys) if ys else None,
            "max_y": max(ys) if ys else None,
            "min_z": min(zs) if zs else None,
            "max_z": max(zs) if zs else None,
        },
    }


def coverage_cells_from_rows(
    rows: list[dict[str, Any]],
    boundary: dict[str, float],
    resolution: float,
    sensor_radius: float,
) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    path_cells: set[tuple[int, int]] = set()
    sensor_cells: set[tuple[int, int]] = set()
    for row in phase_filter(rows):
        x, y = xy(row)
        if add_cell(path_cells, x, y, boundary, resolution):
            add_disc(sensor_cells, x, y, sensor_radius, boundary, resolution)
    return path_cells, sensor_cells


def iter_cloud_history(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                rows.append(data)
    return rows


def cloud_bounds_proxy(rows: list[dict[str, Any]], boundary: dict[str, float], resolution: float) -> dict[str, Any]:
    cells: set[tuple[int, int]] = set()
    published = 0
    rejected = 0
    for row in rows:
        bounds = row.get("world_bounds") or {}
        bmin = bounds.get("min")
        bmax = bounds.get("max")
        if not isinstance(bmin, list) or not isinstance(bmax, list) or len(bmin) < 2 or len(bmax) < 2:
            rejected += 1
            continue
        published += 1
        min_x, min_y = as_float(bmin[0]), as_float(bmin[1])
        max_x, max_y = as_float(bmax[0]), as_float(bmax[1])
        ix0 = math.floor((max(min_x, boundary["min_x_m"]) - boundary["min_x_m"]) / resolution)
        ix1 = math.floor((min(max_x, boundary["max_x_m"]) - boundary["min_x_m"]) / resolution)
        iy0 = math.floor((max(min_y, boundary["min_y_m"]) - boundary["min_y_m"]) / resolution)
        iy1 = math.floor((min(max_y, boundary["max_y_m"]) - boundary["min_y_m"]) / resolution)
        for ix in range(ix0, ix1 + 1):
            for iy in range(iy0, iy1 + 1):
                cells.add((ix, iy))
    nx, ny = grid_shape(boundary, resolution)
    return {
        "history_rows": len(rows),
        "published_bounds_rows": published,
        "rejected_rows": rejected,
        "bounds_union_cells": len(cells),
        "bounds_union_coverage_ratio": len(cells) / (nx * ny),
        "claim_boundary": "This uses per-cloud bounding boxes from pointcloud_to_world_history, so it is an upper-bound proxy and can overestimate true observed free/occupied coverage.",
    }


def detect_run_kind(run_dir: Path) -> str:
    if (run_dir / "EGO_SWARM_METRICS.json").is_file():
        return "swarm"
    if (run_dir / "EGO_SINGLE_METRICS.json").is_file():
        return "single"
    return "unknown"


def run_metrics(run_dir: Path) -> dict[str, Any]:
    kind = detect_run_kind(run_dir)
    if kind == "swarm":
        return load_json(run_dir / "EGO_SWARM_METRICS.json")
    if kind == "single":
        return load_json(run_dir / "EGO_SINGLE_METRICS.json")
    return {}


def metrics_passed(metrics: dict[str, Any]) -> bool:
    blockers = metrics.get("blockers")
    return metrics.get("status") == "passed" and (not isinstance(blockers, list) or len(blockers) == 0)


def manifest_z_policy(run_dirs: list[Path]) -> dict[str, float]:
    min_values: list[float] = []
    max_values: list[float] = []
    for run_dir in run_dirs:
        manifest = load_json(run_dir / "RUN_MANIFEST.json")
        adapter = manifest.get("position_cmd_safety_adapter") or {}
        min_z = as_float(adapter.get("min_z"), math.nan)
        max_z = as_float(adapter.get("max_z"), math.nan)
        if math.isfinite(min_z):
            min_values.append(min_z)
        if math.isfinite(max_z):
            max_values.append(max_z)
    if min_values and max_values:
        return {
            "min_cmd_z_m": min(min_values),
            "max_cmd_z_m": max(max_values),
            "source": "run_manifest.position_cmd_safety_adapter",
        }
    return {}


def collect_run_coverage_cells(
    run_dir: Path,
    boundary: dict[str, float],
    resolution: float,
    sensor_radius: float,
) -> tuple[set[tuple[int, int]], set[tuple[int, int]]]:
    kind = detect_run_kind(run_dir)
    union_path_cells: set[tuple[int, int]] = set()
    union_sensor_cells: set[tuple[int, int]] = set()
    if kind == "swarm":
        for uid in (1, 2, 3):
            path_cells, sensor_cells = coverage_cells_from_rows(
                load_csv(run_dir / f"uav{uid}_truth.csv"),
                boundary,
                resolution,
                sensor_radius,
            )
            union_path_cells.update(path_cells)
            union_sensor_cells.update(sensor_cells)
        return union_path_cells, union_sensor_cells
    if kind == "single":
        return coverage_cells_from_rows(load_csv(run_dir / "truth.csv"), boundary, resolution, sensor_radius)
    return union_path_cells, union_sensor_cells


def evaluate_run(
    run_dir: Path,
    boundary: dict[str, float],
    z_policy: dict[str, float],
    resolution: float,
    sensor_radius: float,
) -> dict[str, Any]:
    kind = detect_run_kind(run_dir)
    metrics = run_metrics(run_dir)
    if kind == "swarm":
        uav_summaries: dict[str, Any] = {}
        union_path_cells: set[tuple[int, int]] = set()
        union_sensor_cells: set[tuple[int, int]] = set()
        for uid in (1, 2, 3):
            rows = load_csv(run_dir / f"uav{uid}_truth.csv")
            summary = summarize_rows(rows, boundary, z_policy, resolution, sensor_radius)
            uav_summaries[f"uav{uid}"] = summary
            # Recompute union from rows to avoid carrying huge cell sets in summaries.
            for row in phase_filter(rows):
                x, y = xy(row)
                add_cell(union_path_cells, x, y, boundary, resolution)
                if boundary["min_x_m"] <= x <= boundary["max_x_m"] and boundary["min_y_m"] <= y <= boundary["max_y_m"]:
                    add_disc(union_sensor_cells, x, y, sensor_radius, boundary, resolution)
        nx, ny = grid_shape(boundary, resolution)
        total = nx * ny
        cloud_histories = {}
        for uid in (1, 2, 3):
            cloud_histories[f"uav{uid}"] = cloud_bounds_proxy(
                iter_cloud_history(run_dir / f"uav{uid}_pointcloud_to_world_history.jsonl"),
                boundary,
                resolution,
            )
        return {
            "path": rel(run_dir),
            "kind": kind,
            "metrics_status": metrics.get("status"),
            "metrics_blockers": metrics.get("blockers", []),
            "eligible_for_merged_coverage": metrics_passed(metrics),
            "uav": uav_summaries,
            "merged": {
                "path_cells": len(union_path_cells),
                "path_coverage_ratio": len(union_path_cells) / total,
                "sensor_footprint_cells": len(union_sensor_cells),
                "sensor_footprint_coverage_ratio": len(union_sensor_cells) / total,
            },
            "cloud_bounds_proxy": cloud_histories,
        }
    rows = load_csv(run_dir / "truth.csv")
    return {
        "path": rel(run_dir),
        "kind": kind,
        "metrics_status": metrics.get("status"),
        "metrics_blockers": metrics.get("blockers", []),
        "eligible_for_merged_coverage": metrics_passed(metrics),
        "truth": summarize_rows(rows, boundary, z_policy, resolution, sensor_radius),
        "cloud_bounds_proxy": cloud_bounds_proxy(
            iter_cloud_history(run_dir / "pointcloud_to_world_history.jsonl"),
            boundary,
            resolution,
        ),
    }


def build_packet(args: argparse.Namespace) -> dict[str, Any]:
    envelope = load_json(args.envelope)
    raw_boundary = envelope.get("exploration_boundary") or {}
    raw_z = envelope.get("z_policy") or {}
    boundary = {
        "min_x_m": as_float(raw_boundary.get("min_x_m")),
        "max_x_m": as_float(raw_boundary.get("max_x_m")),
        "min_y_m": as_float(raw_boundary.get("min_y_m")),
        "max_y_m": as_float(raw_boundary.get("max_y_m")),
    }
    run_dirs = [repo_path(run) for run in args.run]
    inferred_z = manifest_z_policy(run_dirs)
    if args.z_min_m is not None or args.z_max_m is not None:
        z_policy_source = "cli_override"
        base_min_z = as_float(args.z_min_m, as_float(raw_z.get("min_cmd_z_m"), 0.9))
        base_max_z = as_float(args.z_max_m, as_float(raw_z.get("max_cmd_z_m"), 1.6))
    elif inferred_z:
        z_policy_source = str(inferred_z["source"])
        base_min_z = inferred_z["min_cmd_z_m"]
        base_max_z = inferred_z["max_cmd_z_m"]
    else:
        z_policy_source = "envelope.z_policy"
        base_min_z = as_float(raw_z.get("min_cmd_z_m"), 0.9)
        base_max_z = as_float(raw_z.get("max_cmd_z_m"), 1.6)
    z_policy = {
        "min_cmd_z_m": base_min_z - args.z_tolerance_m,
        "max_cmd_z_m": base_max_z + args.z_tolerance_m,
        "source": z_policy_source,
    }
    nx, ny = grid_shape(boundary, args.grid_resolution_m)
    run_packets = [evaluate_run(run_dir, boundary, z_policy, args.grid_resolution_m, args.sensor_radius_m) for run_dir in run_dirs]
    best_sensor = 0.0
    best_path = 0.0
    merged_path_cells: set[tuple[int, int]] = set()
    merged_sensor_cells: set[tuple[int, int]] = set()
    eligible_runs: list[str] = []
    excluded_runs: list[str] = []
    for item in run_packets:
        if item.get("kind") == "swarm":
            merged = item.get("merged") or {}
            best_sensor = max(best_sensor, as_float(merged.get("sensor_footprint_coverage_ratio")))
            best_path = max(best_path, as_float(merged.get("path_coverage_ratio")))
        else:
            truth = item.get("truth") or {}
            best_sensor = max(best_sensor, as_float(truth.get("sensor_footprint_coverage_ratio")))
            best_path = max(best_path, as_float(truth.get("path_coverage_ratio")))
    for run_dir in run_dirs:
        metrics = run_metrics(run_dir)
        if not metrics_passed(metrics):
            excluded_runs.append(rel(run_dir))
            continue
        path_cells, sensor_cells = collect_run_coverage_cells(
            run_dir,
            boundary,
            args.grid_resolution_m,
            args.sensor_radius_m,
        )
        merged_path_cells.update(path_cells)
        merged_sensor_cells.update(sensor_cells)
        eligible_runs.append(rel(run_dir))

    total_cells = nx * ny
    merged_sensor_ratio = len(merged_sensor_cells) / total_cells
    merged_path_ratio = len(merged_path_cells) / total_cells
    status = "passed" if merged_sensor_ratio >= args.min_sensor_coverage_ratio else "blocked"
    blockers = []
    if not eligible_runs:
        blockers.append("no_backend_passed_runs_for_merged_coverage")
    if status != "passed":
        blockers.append("indoor_sensor_footprint_coverage_below_threshold")
    return {
        "schema": "mosim.factory_l2_indoor_coverage_packet.v1",
        "status": status,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "envelope": {
            "path": rel(args.envelope),
            "boundary": boundary,
            "grid_resolution_m": args.grid_resolution_m,
            "grid_shape": [nx, ny],
            "grid_cell_count": nx * ny,
            "sensor_radius_m": args.sensor_radius_m,
            "z_policy_with_tolerance": z_policy,
        },
        "acceptance": {
            "min_sensor_footprint_coverage_ratio": args.min_sensor_coverage_ratio,
            "merged_sensor_footprint_coverage_ratio": merged_sensor_ratio,
            "merged_path_coverage_ratio": merged_path_ratio,
            "best_single_run_sensor_footprint_coverage_ratio": best_sensor,
            "best_single_run_path_coverage_ratio": best_path,
            "eligible_run_count": len(eligible_runs),
            "excluded_run_count": len(excluded_runs),
            "eligible_runs": eligible_runs,
            "excluded_runs": excluded_runs,
            "coverage_merge_policy": "Only runs whose backend metrics status is passed and blockers is empty are merged. Blocked runs remain listed for diagnosis but do not count toward acceptance.",
            "blockers": blockers,
        },
        "runs": run_packets,
        "claim_boundary": [
            "sensor_footprint_coverage_ratio is a trajectory-plus-sensor-radius XY coverage proxy, not a semantic proof that every obstacle surface was scanned.",
            "merged_sensor_footprint_coverage_ratio is the acceptance value for multi-run tile coverage; best_single_run_* values are diagnostics only.",
            "cloud_bounds_proxy uses per-cloud world bounds and can overestimate true observed coverage.",
            "Full acceptance still needs backend safety metrics and optional RViz/UE visual review after this offline packet.",
        ],
    }


def write_summary(packet: dict[str, Any], output_dir: Path) -> None:
    lines = [
        "# Factory L2 Indoor Coverage Packet",
        "",
        f"- status: `{packet['status']}`",
        f"- merged_sensor_footprint_coverage_ratio: `{packet['acceptance']['merged_sensor_footprint_coverage_ratio']:.4f}`",
        f"- merged_path_coverage_ratio: `{packet['acceptance']['merged_path_coverage_ratio']:.4f}`",
        f"- best_single_run_sensor_footprint_coverage_ratio: `{packet['acceptance']['best_single_run_sensor_footprint_coverage_ratio']:.4f}`",
        f"- best_single_run_path_coverage_ratio: `{packet['acceptance']['best_single_run_path_coverage_ratio']:.4f}`",
        f"- min_required: `{packet['acceptance']['min_sensor_footprint_coverage_ratio']:.4f}`",
        f"- eligible_run_count: `{packet['acceptance']['eligible_run_count']}`",
        f"- excluded_run_count: `{packet['acceptance']['excluded_run_count']}`",
        f"- blockers: `{packet['acceptance']['blockers']}`",
        "",
        "## Runs",
    ]
    for item in packet["runs"]:
        lines.append(f"- `{item['path']}`: kind=`{item['kind']}`, metrics_status=`{item.get('metrics_status')}`")
    lines.extend(["", "## Claim Boundary"])
    lines.extend(f"- {entry}" for entry in packet["claim_boundary"])
    (output_dir / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="append", required=True, help="Completed run directory; repeatable.")
    parser.add_argument("--envelope", type=repo_path, default=DEFAULT_ENVELOPE)
    parser.add_argument("--output-dir", type=repo_path, default=None)
    parser.add_argument("--grid-resolution-m", type=float, default=2.0)
    parser.add_argument("--sensor-radius-m", type=float, default=8.0)
    parser.add_argument("--min-sensor-coverage-ratio", type=float, default=0.80)
    parser.add_argument("--z-tolerance-m", type=float, default=0.10)
    parser.add_argument("--z-min-m", type=float, default=None, help="Override minimum command/evaluation Z before tolerance.")
    parser.add_argument("--z-max-m", type=float, default=None, help="Override maximum command/evaluation Z before tolerance.")
    args = parser.parse_args()

    if args.output_dir is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output_dir = ROOT / "Results/sunray_ros1" / f"factory_l2_indoor_coverage_packet_{stamp}"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    packet = build_packet(args)
    (args.output_dir / "FACTORY_L2_INDOOR_COVERAGE_PACKET.json").write_text(
        json.dumps(packet, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    write_summary(packet, args.output_dir)
    print(args.output_dir)
    raise SystemExit(0 if packet["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
