#!/usr/bin/env python3
"""Summarize Factory L2 FUEL tile evidence without starting runtime systems."""

from __future__ import annotations

import argparse
import csv
import json
import math
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


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def number(value: Any) -> float | None:
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        try:
            parsed = float(text)
        except ValueError:
            return None
        return parsed if math.isfinite(parsed) else None
    return None


def nested(data: dict[str, Any], *keys: str) -> Any:
    cur: Any = data
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def range_from_csv(path: Path, phase_filter: set[str] | None = None) -> dict[str, float | int | str | None]:
    rows = 0
    mins = {"x": math.inf, "y": math.inf, "z": math.inf}
    maxs = {"x": -math.inf, "y": -math.inf, "z": -math.inf}
    if not path.is_file():
        return {"source": rel(path), "samples": 0, "min_x": None, "max_x": None, "min_y": None, "max_y": None, "min_z": None, "max_z": None}
    with path.open(newline="", encoding="utf-8", errors="replace") as handle:
        for row in csv.DictReader(handle):
            if phase_filter is not None and str(row.get("phase") or "") not in phase_filter:
                continue
            values = {axis: number(row.get(axis)) for axis in ("x", "y", "z")}
            if any(v is None for v in values.values()):
                continue
            rows += 1
            for axis, value in values.items():
                assert value is not None
                mins[axis] = min(mins[axis], value)
                maxs[axis] = max(maxs[axis], value)
    if rows == 0:
        return {"source": rel(path), "samples": 0, "min_x": None, "max_x": None, "min_y": None, "max_y": None, "min_z": None, "max_z": None}
    return {
        "source": rel(path),
        "samples": rows,
        "min_x": mins["x"],
        "max_x": maxs["x"],
        "min_y": mins["y"],
        "max_y": maxs["y"],
        "min_z": mins["z"],
        "max_z": maxs["z"],
    }


def first_nonempty_range(path: Path, names: list[str], phase_filter: set[str] | None = None) -> dict[str, float | int | str | None]:
    last: dict[str, float | int | str | None] | None = None
    for name in names:
        candidate = range_from_csv(path / name, phase_filter=phase_filter)
        last = candidate
        if int(candidate.get("samples") or 0) > 0:
            return candidate
    return last or {"source": None, "samples": 0, "min_x": None, "max_x": None, "min_y": None, "max_y": None, "min_z": None, "max_z": None}


def summarize_run(path: Path) -> dict[str, Any]:
    manifest = load_json(path / "RUN_MANIFEST.json")
    metrics = load_json(path / "EGO_SINGLE_METRICS.json")
    fuel = manifest.get("fuel") if isinstance(manifest.get("fuel"), dict) else {}
    target = manifest.get("target") if isinstance(manifest.get("target"), dict) else {}
    box_min = fuel.get("box_min") if isinstance(fuel.get("box_min"), dict) else {}
    box_max = fuel.get("box_max") if isinstance(fuel.get("box_max"), dict) else {}
    truth_range = first_nonempty_range(path, ["truth.csv", "sunray_truth.csv"])
    explore_truth_range = first_nonempty_range(path, ["truth.csv", "sunray_truth.csv"], phase_filter={"exploration_execute"})
    counts = metrics.get("counts") if isinstance(metrics.get("counts"), dict) else {}
    phase_summary = metrics.get("phase_peak_summary") if isinstance(metrics.get("phase_peak_summary"), dict) else {}
    truth_phase = nested(phase_summary, "truth", "exploration_execute")
    if not isinstance(truth_phase, dict):
        truth_phase = {}
    odom_phase = nested(phase_summary, "odom", "exploration_execute")
    if not isinstance(odom_phase, dict):
        odom_phase = {}
    return {
        "run_id": path.name,
        "path": rel(path),
        "status": metrics.get("status"),
        "blockers": metrics.get("blockers", []),
        "world_file": manifest.get("world_file"),
        "target_x": target.get("x"),
        "target_y": target.get("y"),
        "target_z": target.get("z"),
        "window_min_x": box_min.get("x"),
        "window_max_x": box_max.get("x"),
        "window_min_y": box_min.get("y"),
        "window_max_y": box_max.get("y"),
        "window_min_z": box_min.get("z"),
        "window_max_z": box_max.get("z"),
        "map_size_x": nested(fuel, "map_size", "x"),
        "map_size_y": nested(fuel, "map_size", "y"),
        "map_size_z": nested(fuel, "map_size", "z"),
        "grid_resolution_m": fuel.get("grid_resolution_m"),
        "bspline_count": counts.get("bspline"),
        "planner_position_cmd_count": counts.get("planner_position_cmd"),
        "raw_lidar_count": counts.get("raw_lidar"),
        "world_cloud_count": counts.get("world_cloud"),
        "occupancy_last_points": metrics.get("occupancy_last_points"),
        "truth_source": truth_range["source"],
        "truth_samples": truth_range["samples"],
        "truth_min_x": truth_range["min_x"],
        "truth_max_x": truth_range["max_x"],
        "truth_min_y": truth_range["min_y"],
        "truth_max_y": truth_range["max_y"],
        "truth_min_z": truth_range["min_z"],
        "truth_max_z": truth_range["max_z"],
        "explore_truth_source": explore_truth_range["source"],
        "explore_truth_samples": explore_truth_range["samples"],
        "explore_truth_min_x": explore_truth_range["min_x"],
        "explore_truth_max_x": explore_truth_range["max_x"],
        "explore_truth_min_y": explore_truth_range["min_y"],
        "explore_truth_max_y": explore_truth_range["max_y"],
        "explore_truth_min_z": truth_phase.get("min_z_m", explore_truth_range["min_z"]),
        "explore_truth_max_z": truth_phase.get("max_z_m", explore_truth_range["max_z"]),
        "explore_truth_max_speed_mps": truth_phase.get("max_speed_mps"),
        "explore_truth_max_roll_pitch_deg": truth_phase.get("max_abs_roll_pitch_deg"),
        "explore_odom_min_z": odom_phase.get("min_z_m"),
        "explore_odom_max_z": odom_phase.get("max_z_m"),
        "explore_odom_max_speed_mps": odom_phase.get("max_speed_mps"),
        "explore_odom_max_roll_pitch_deg": odom_phase.get("max_abs_roll_pitch_deg"),
    }


def span_area(rows: list[dict[str, Any]], min_x_key: str, max_x_key: str, min_y_key: str, max_y_key: str) -> dict[str, float | None]:
    xs_min = [number(row.get(min_x_key)) for row in rows]
    xs_max = [number(row.get(max_x_key)) for row in rows]
    ys_min = [number(row.get(min_y_key)) for row in rows]
    ys_max = [number(row.get(max_y_key)) for row in rows]
    xs_min = [v for v in xs_min if v is not None]
    xs_max = [v for v in xs_max if v is not None]
    ys_min = [v for v in ys_min if v is not None]
    ys_max = [v for v in ys_max if v is not None]
    if not xs_min or not xs_max or not ys_min or not ys_max:
        return {"min_x": None, "max_x": None, "min_y": None, "max_y": None, "span_x": None, "span_y": None, "area_proxy_m2": None}
    min_x = min(xs_min)
    max_x = max(xs_max)
    min_y = min(ys_min)
    max_y = max(ys_max)
    span_x = max(0.0, max_x - min_x)
    span_y = max(0.0, max_y - min_y)
    return {"min_x": min_x, "max_x": max_x, "min_y": min_y, "max_y": max_y, "span_x": span_x, "span_y": span_y, "area_proxy_m2": span_x * span_y}


def rows_outside_range(rows: list[dict[str, Any]], min_key: str, max_key: str, lower: float | None, upper: float | None) -> list[str]:
    if lower is None or upper is None:
        return []
    bad: list[str] = []
    for row in rows:
        row_min = number(row.get(min_key))
        row_max = number(row.get(max_key))
        if row_min is None or row_max is None:
            continue
        if row_min < lower or row_max > upper:
            bad.append(str(row.get("run_id")))
    return bad


def rows_above(rows: list[dict[str, Any]], key: str, threshold: float) -> list[str]:
    bad: list[str] = []
    for row in rows:
        value = number(row.get(key))
        if value is not None and value > threshold:
            bad.append(str(row.get("run_id")))
    return bad


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="Results/sunray_ros1/factory_l2_f5c_fuel_tile_summary")
    parser.add_argument("--envelope", default="Config/gazebo/scene_profiles/factory_l2_exploration_envelope.json")
    parser.add_argument("runs", nargs="*")
    args = parser.parse_args()

    if args.runs:
        run_dirs = [repo_path(item) for item in args.runs]
    else:
        root = ROOT / "Results/sunray_ros1"
        run_dirs = sorted(root.glob("factory_l2_f5c*_fuel*"))
        run_dirs = [path for path in run_dirs if (path / "EGO_SINGLE_METRICS.json").is_file()]

    rows = [summarize_run(path) for path in run_dirs]
    passed = [row for row in rows if row.get("status") == "passed" and not row.get("blockers")]
    envelope = load_json(repo_path(args.envelope))
    boundary = nested(envelope, "exploration_boundary") or {}
    boundary_area = None
    min_x = number(boundary.get("min_x_m"))
    max_x = number(boundary.get("max_x_m"))
    min_y = number(boundary.get("min_y_m"))
    max_y = number(boundary.get("max_y_m"))
    if None not in (min_x, max_x, min_y, max_y):
        boundary_area = max(0.0, max_x - min_x) * max(0.0, max_y - min_y)  # type: ignore[operator]

    window_span = span_area(passed, "window_min_x", "window_max_x", "window_min_y", "window_max_y")
    truth_span = span_area(passed, "truth_min_x", "truth_max_x", "truth_min_y", "truth_max_y")
    explore_truth_span = span_area(passed, "explore_truth_min_x", "explore_truth_max_x", "explore_truth_min_y", "explore_truth_max_y")
    z_policy = nested(envelope, "z_policy") or {}
    min_cmd_z = number(z_policy.get("min_cmd_z_m"))
    max_cmd_z = number(z_policy.get("max_cmd_z_m"))
    z_violations = rows_outside_range(passed, "explore_truth_min_z", "explore_truth_max_z", min_cmd_z, max_cmd_z)
    high_attitude_runs = rows_above(passed, "explore_truth_max_roll_pitch_deg", 12.0)
    summary = {
        "schema": "mosim.factory_l2_fuel_tile_summary.v1",
        "status": "passed_representative_tiles_only" if passed else "blocked_no_passed_tiles",
        "claim_boundary": [
            "This is an offline evidence summary from completed FUEL tile runs.",
            "window_area_proxy_m2 is configured local-map window span, not proven explored area.",
            "truth_area_proxy_m2 is actual vehicle trajectory span, not full-map coverage.",
            "Do not claim full Factory exploration until the tile matrix covers the accepted envelope with backend pass evidence.",
        ],
        "input_run_count": len(rows),
        "passed_run_count": len(passed),
        "blocked_run_count": len(rows) - len(passed),
        "boundary_area_m2": boundary_area,
        "window_span": window_span,
        "truth_span": truth_span,
        "explore_truth_span": explore_truth_span,
        "window_area_ratio_to_boundary": None if not boundary_area or not window_span.get("area_proxy_m2") else window_span["area_proxy_m2"] / boundary_area,
        "truth_area_ratio_to_boundary": None if not boundary_area or not truth_span.get("area_proxy_m2") else truth_span["area_proxy_m2"] / boundary_area,
        "explore_truth_area_ratio_to_boundary": None if not boundary_area or not explore_truth_span.get("area_proxy_m2") else explore_truth_span["area_proxy_m2"] / boundary_area,
        "z_policy": {
            "min_cmd_z_m": min_cmd_z,
            "max_cmd_z_m": max_cmd_z,
            "violating_passed_runs": z_violations,
            "status": "needs_height_policy_review" if z_violations else "passed_for_passed_tiles",
        },
        "attitude_policy": {
            "review_threshold_deg": 12.0,
            "high_roll_pitch_passed_runs": high_attitude_runs,
            "status": "needs_safety_review" if high_attitude_runs else "passed_for_passed_tiles",
        },
        "runs": rows,
    }

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "FACTORY_L2_FUEL_TILE_SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if rows:
        with (output_dir / "factory_l2_fuel_tile_summary.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    print(json.dumps({"status": summary["status"], "output_dir": rel(output_dir), "passed_run_count": len(passed)}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
