#!/usr/bin/env python3
"""Build an offline FUEL-D4 evaluation package from a completed D3 run.

The package is evidence indexing and metric extraction only. It does not start
ROS, Gazebo, PX4, MAVROS, RViz, FUEL, or any GUI process.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from bisect import bisect_left
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "Results/sunray_ros1/sunray_ros1_goal4_ego_single_20260701_072618"
DEFAULT_OUTPUT_ROOT = ROOT / "Results/sunray_ros1"


def repo_path(value: str | Path) -> Path:
    path = Path(value)
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


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
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


def maybe_float(value: str) -> float | str:
    if value == "":
        return value
    try:
        return float(value)
    except ValueError:
        return value


def load_csv(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        return [{key: maybe_float(value) for key, value in row.items()} for row in csv.DictReader(f)]


def phase_rows(rows: list[dict[str, Any]], phase: str) -> list[dict[str, Any]]:
    return [r for r in rows if r.get("phase") == phase]


def row_t(row: dict[str, Any]) -> float:
    value = row.get("t", 0.0)
    return float(value) if isinstance(value, (int, float)) else 0.0


def xyz(row: dict[str, Any]) -> tuple[float, float, float]:
    return (float(row.get("x", 0.0)), float(row.get("y", 0.0)), float(row.get("z", 0.0)))


def duration(rows: list[dict[str, Any]]) -> float | None:
    if len(rows) < 2:
        return None
    return row_t(rows[-1]) - row_t(rows[0])


def path_length(rows: list[dict[str, Any]]) -> float:
    if len(rows) < 2:
        return 0.0
    total = 0.0
    prev = xyz(rows[0])
    for row in rows[1:]:
        cur = xyz(row)
        total += math.dist(prev, cur)
        prev = cur
    return total


def numeric_values(rows: list[dict[str, Any]], key: str) -> list[float]:
    values = []
    for row in rows:
        value = row.get(key)
        if isinstance(value, (int, float)) and math.isfinite(float(value)):
            values.append(float(value))
    return values


def quantile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    vals = sorted(values)
    idx = (len(vals) - 1) * q
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return vals[lo]
    return vals[lo] * (hi - idx) + vals[hi] * (idx - lo)


def rmse(values: list[float]) -> float | None:
    if not values:
        return None
    return math.sqrt(sum(v * v for v in values) / len(values))


def max_abs_roll_pitch_deg(rows: list[dict[str, Any]]) -> float | None:
    vals = []
    for row in rows:
        roll = row.get("roll")
        pitch = row.get("pitch")
        if isinstance(roll, (int, float)) and isinstance(pitch, (int, float)):
            vals.append(max(abs(float(roll)), abs(float(pitch))) * 180.0 / math.pi)
    return max(vals) if vals else None


def phase_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"samples": 0}
    speed = [
        math.sqrt(float(r.get("vx", 0.0)) ** 2 + float(r.get("vy", 0.0)) ** 2 + float(r.get("vz", 0.0)) ** 2)
        for r in rows
    ]
    z_values = numeric_values(rows, "z")
    return {
        "samples": len(rows),
        "start_t": row_t(rows[0]),
        "end_t": row_t(rows[-1]),
        "duration_s": duration(rows),
        "path_length_m": path_length(rows),
        "min_z_m": min(z_values) if z_values else None,
        "max_z_m": max(z_values) if z_values else None,
        "max_speed_mps": max(speed) if speed else None,
        "max_abs_vz_mps": max((abs(float(r.get("vz", 0.0))) for r in rows), default=None),
        "max_abs_roll_pitch_deg": max_abs_roll_pitch_deg(rows),
        "start_xyz": list(xyz(rows[0])),
        "end_xyz": list(xyz(rows[-1])),
    }


def nearest_tracking(
    reference_rows: list[dict[str, Any]],
    measured_rows: list[dict[str, Any]],
    *,
    max_dt_s: float,
) -> dict[str, Any]:
    if not reference_rows or not measured_rows:
        return {"samples": 0, "max_dt_s": max_dt_s}
    measured_times = [row_t(r) for r in measured_rows]
    errors_xyz: list[float] = []
    errors_xy: list[float] = []
    errors_z: list[float] = []
    dts: list[float] = []
    for ref in reference_rows:
        t = row_t(ref)
        idx = bisect_left(measured_times, t)
        candidates = []
        if idx < len(measured_rows):
            candidates.append(measured_rows[idx])
        if idx > 0:
            candidates.append(measured_rows[idx - 1])
        if not candidates:
            continue
        meas = min(candidates, key=lambda r: abs(row_t(r) - t))
        dt = abs(row_t(meas) - t)
        if dt > max_dt_s:
            continue
        rx, ry, rz = xyz(ref)
        mx, my, mz = xyz(meas)
        ex = mx - rx
        ey = my - ry
        ez = mz - rz
        errors_xy.append(math.hypot(ex, ey))
        errors_z.append(abs(ez))
        errors_xyz.append(math.sqrt(ex * ex + ey * ey + ez * ez))
        dts.append(dt)
    return {
        "samples": len(errors_xyz),
        "max_dt_s": max_dt_s,
        "observed_max_dt_s": max(dts) if dts else None,
        "mean_dt_s": (sum(dts) / len(dts)) if dts else None,
        "rmse_xyz_m": rmse(errors_xyz),
        "rmse_xy_m": rmse(errors_xy),
        "rmse_z_m": rmse(errors_z),
        "p95_xyz_m": quantile(errors_xyz, 0.95),
        "p95_xy_m": quantile(errors_xy, 0.95),
        "p95_z_m": quantile(errors_z, 0.95),
        "max_xyz_m": max(errors_xyz) if errors_xyz else None,
        "max_xy_m": max(errors_xy) if errors_xy else None,
        "max_z_m": max(errors_z) if errors_z else None,
    }


def bounds_union(history: list[dict[str, Any]]) -> dict[str, Any]:
    mins = [math.inf, math.inf, math.inf]
    maxs = [-math.inf, -math.inf, -math.inf]
    count = 0
    for row in history:
        world_bounds = row.get("world_bounds")
        if not isinstance(world_bounds, dict):
            continue
        bmin = world_bounds.get("min")
        bmax = world_bounds.get("max")
        if not (isinstance(bmin, list) and isinstance(bmax, list) and len(bmin) >= 3 and len(bmax) >= 3):
            continue
        count += 1
        for i in range(3):
            mins[i] = min(mins[i], float(bmin[i]))
            maxs[i] = max(maxs[i], float(bmax[i]))
    if count == 0:
        return {"samples": 0}
    span = [maxs[i] - mins[i] for i in range(3)]
    return {
        "samples": count,
        "min_xyz": mins,
        "max_xyz": maxs,
        "span_xyz_m": span,
        "envelope_volume_m3": span[0] * span[1] * span[2],
        "footprint_area_m2": span[0] * span[1],
    }


def map_proxy(
    history: list[dict[str, Any]],
    metrics: dict[str, Any],
    manifest: dict[str, Any],
    accum_review: dict[str, Any],
) -> dict[str, Any]:
    published_points = [
        float(row.get("published_points", 0.0))
        for row in history
        if isinstance(row.get("published_points"), (int, float))
    ]
    last_history = history[-1] if history else {}
    pointcloud_review = manifest.get("pointcloud_review", {}) if isinstance(manifest.get("pointcloud_review"), dict) else {}
    ego = manifest.get("ego", {}) if isinstance(manifest.get("ego"), dict) else {}
    voxel_size = float(pointcloud_review.get("voxel_size_m", 0.08))
    grid_resolution = float(ego.get("grid_resolution", 0.12))
    accum_voxels = None
    if isinstance(accum_review.get("last_stats"), dict):
        accum_voxels = accum_review["last_stats"].get("accumulated_voxels")
    if accum_voxels is None and isinstance(accum_review.get("quality_gate"), dict):
        accum_voxels = accum_review["quality_gate"].get("accumulated_voxels")
    occupancy_points = (metrics.get("last_point_counts") or {}).get("occupancy_inflate")
    return {
        "world_cloud_history": {
            "samples": len(history),
            "received_clouds_last": last_history.get("received_clouds"),
            "published_clouds_last": last_history.get("published_clouds"),
            "published_points_last": last_history.get("published_points"),
            "published_points_mean": (sum(published_points) / len(published_points)) if published_points else None,
            "published_points_max": max(published_points) if published_points else None,
            "z_filtered_last": last_history.get("z_filtered"),
            "world_z_low_filtered_last": last_history.get("world_z_low_filtered"),
            "world_z_high_filtered_last": last_history.get("world_z_high_filtered"),
            "odom_warning_count_last": last_history.get("warning_odom_gate"),
            "attitude_warning_count_last": last_history.get("warning_attitude_gate"),
            "bounds_union": bounds_union(history),
        },
        "accumulated_review_cloud": {
            "topic": pointcloud_review.get("topic"),
            "source": pointcloud_review.get("source"),
            "voxel_size_m": voxel_size,
            "received": accum_review.get("received"),
            "published": accum_review.get("published"),
            "accepted_frames": (accum_review.get("quality_gate_counts") or {}).get("accepted"),
            "skipped_frames": (accum_review.get("quality_gate_counts") or {}).get("skipped"),
            "last_skip_reason": (accum_review.get("quality_gate_counts") or {}).get("last_skip_reason"),
            "accumulated_voxels": accum_voxels,
            "voxel_volume_proxy_m3": (float(accum_voxels) * voxel_size**3) if isinstance(accum_voxels, (int, float)) else None,
        },
        "occupancy_proxy": {
            "topic": (manifest.get("topics") or {}).get("occupancy_inflate"),
            "grid_resolution_m": grid_resolution,
            "last_points": occupancy_points,
            "voxel_volume_proxy_m3": (float(occupancy_points) * grid_resolution**3)
            if isinstance(occupancy_points, (int, float))
            else None,
            "semantics": "local inflated occupancy point-count proxy, not global explored volume",
        },
    }


def log_diagnostics(result_dir: Path) -> dict[str, Any]:
    patterns = {
        "planner_total_time_too_long": re.compile(r"Total time too long", re.IGNORECASE),
        "planner_lower_bound_not_satisfied": re.compile(r"Lower bound not sat", re.IGNORECASE),
        "planner_yaw_change_rapidly": re.compile(r"Yaw change rapidly", re.IGNORECASE),
        "planner_replan_collision_detected": re.compile(r"Replan: collision detected|collision at:", re.IGNORECASE),
        "planner_cluster_covered": re.compile(r"cluster covered", re.IGNORECASE),
        "offboard_mentions": re.compile(r"OFFBOARD", re.IGNORECASE),
        "failsafe_or_loss_mentions": re.compile(r"failsafe|lost|disconnected|timeout", re.IGNORECASE),
    }
    counts = {key: 0 for key in patterns}
    scanned_files = []
    for path in sorted(result_dir.glob("*.log")):
        text = path.read_text(encoding="utf-8", errors="replace")
        scanned_files.append(rel(path))
        for key, pattern in patterns.items():
            counts[key] += len(pattern.findall(text))
    return {
        "scanned_files": scanned_files,
        "counts": counts,
        "notes": [
            "FUEL planner 'collision detected' lines are internal replanning diagnostics, not Gazebo contact proof.",
            "No dedicated Gazebo contact sensor log is parsed by this offline evaluator.",
        ],
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_summary(path: Path, report: dict[str, Any]) -> None:
    source = report["source"]
    metrics = report["source_metrics"]
    phases = report["trajectory_summary"]["truth_phases"]
    exploration = phases.get("exploration_execute", {})
    map_eval = report["map_and_coverage_proxy"]
    safety = report["safety_assessment"]
    tracking = report["tracking_proxy"]
    figures = report["figures"]
    mission_timing = report["mission_timing"]
    lines = [
        "# FUEL-D4 Evaluation Package",
        "",
        f"- status: `{report['status']}`",
        f"- source_result_dir: `{source['result_dir']}`",
        f"- generated_at: `{report['generated_at']}`",
        f"- source_run_status: `{metrics.get('status')}`",
        f"- source_blockers: `{metrics.get('blockers')}`",
        "",
        "## Mission Summary",
        "",
        f"- configured_execute_duration_s: `{mission_timing.get('configured_execute_duration_s')}`",
        f"- measured_execute_wall_duration_s: `{mission_timing.get('measured_execute_wall_duration_s')}`",
        f"- truth_exploration_phase_sim_duration_s: `{exploration.get('duration_s')}`",
        f"- truth_exploration_path_length_m: `{exploration.get('path_length_m')}`",
        f"- raw_fuel_command_count: `{metrics.get('counts', {}).get('planner_position_cmd')}`",
        f"- px4ctrl_facing_command_count: `{metrics.get('counts', {}).get('position_cmd')}`",
        f"- bspline_count: `{metrics.get('counts', {}).get('bspline')}`",
        f"- landed_by_truth: `{metrics.get('land', {}).get('landed_by_truth')}`",
        "",
        "## Safety And Tracking",
        "",
        f"- safety_status: `{safety['status']}`",
        f"- min_truth_z_explore_m: `{safety.get('min_truth_z_explore_m')}`",
        f"- max_truth_roll_pitch_explore_deg: `{safety.get('max_truth_roll_pitch_explore_deg')}`",
        f"- flight_safety_violation: `{safety.get('flight_safety_violation')}`",
        f"- contact_sensor_evidence: `{safety.get('contact_sensor_evidence')}`",
        f"- command_to_odom_rmse_xyz_m: `{tracking['position_cmd_to_odom'].get('rmse_xyz_m')}`",
        f"- command_to_odom_max_xyz_m: `{tracking['position_cmd_to_odom'].get('max_xyz_m')}`",
        "",
        "## Map / Coverage Proxy",
        "",
        f"- accumulated_cloud_voxels: `{map_eval['accumulated_review_cloud'].get('accumulated_voxels')}`",
        f"- accumulated_cloud_voxel_volume_proxy_m3: `{map_eval['accumulated_review_cloud'].get('voxel_volume_proxy_m3')}`",
        f"- occupancy_last_points: `{map_eval['occupancy_proxy'].get('last_points')}`",
        f"- occupancy_voxel_volume_proxy_m3: `{map_eval['occupancy_proxy'].get('voxel_volume_proxy_m3')}`",
        f"- world_cloud_envelope_volume_m3: `{map_eval['world_cloud_history']['bounds_union'].get('envelope_volume_m3')}`",
        "",
        "## Figures",
        "",
    ]
    if figures:
        lines.extend(f"- `{key}`: `{rel(value)}`" for key, value in figures.items())
    else:
        lines.append("- No figures were generated; see `warnings` in JSON.")
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            *[f"- {item}" for item in report["claim_boundary"]],
            "",
            "## Next",
            "",
            *[f"- {item}" for item in report["next_actions"]],
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_figures(output_dir: Path, truth: list[dict[str, Any]], odom: list[dict[str, Any]], cmd: list[dict[str, Any]], raw_cmd: list[dict[str, Any]], history: list[dict[str, Any]]) -> tuple[dict[str, str], list[str]]:
    figures: dict[str, str] = {}
    warnings: list[str] = []
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover - depends on local optional package
        return figures, [f"matplotlib unavailable: {exc}"]

    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    truth_exec = phase_rows(truth, "exploration_execute") or truth
    odom_exec = phase_rows(odom, "exploration_execute") or odom
    cmd_exec = phase_rows(cmd, "exploration_execute") or cmd
    raw_exec = phase_rows(raw_cmd, "exploration_execute") or raw_cmd

    fig, ax = plt.subplots(figsize=(7, 7))
    if raw_exec:
        ax.plot([r["x"] for r in raw_exec], [r["y"] for r in raw_exec], color="orange", lw=0.8, label="raw FUEL cmd")
    if cmd_exec:
        ax.plot([r["x"] for r in cmd_exec], [r["y"] for r in cmd_exec], color="green", lw=1.2, label="px4ctrl cmd")
    if odom_exec:
        ax.plot([r["x"] for r in odom_exec], [r["y"] for r in odom_exec], color="blue", lw=1.0, label="odom")
    if truth_exec:
        ax.plot([r["x"] for r in truth_exec], [r["y"] for r in truth_exec], color="red", lw=1.0, label="truth")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_title("FUEL-D4 exploration XY path")
    ax.axis("equal")
    ax.grid(True)
    ax.legend()
    path = figures_dir / "fuel_d4_xy_path.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    figures["xy_path"] = str(path)

    fig, ax = plt.subplots(figsize=(9, 4))
    if truth:
        t0 = row_t(truth[0])
        ax.plot([row_t(r) - t0 for r in truth], [r["z"] for r in truth], color="red", lw=1.0, label="truth z")
    if odom:
        t0 = row_t(odom[0])
        ax.plot([row_t(r) - t0 for r in odom], [r["z"] for r in odom], color="blue", lw=0.9, label="odom z")
    ax.axhline(1.0, color="gray", linestyle="--", lw=0.8, label="nominal z")
    ax.set_xlabel("time since first sample [s]")
    ax.set_ylabel("z [m]")
    ax.set_title("FUEL-D4 altitude")
    ax.grid(True)
    ax.legend()
    path = figures_dir / "fuel_d4_altitude.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    figures["altitude"] = str(path)

    if cmd_exec and odom_exec:
        odom_times = [row_t(r) for r in odom_exec]
        times: list[float] = []
        errors: list[float] = []
        t0 = row_t(cmd_exec[0])
        for ref in cmd_exec:
            idx = bisect_left(odom_times, row_t(ref))
            candidates = []
            if idx < len(odom_exec):
                candidates.append(odom_exec[idx])
            if idx > 0:
                candidates.append(odom_exec[idx - 1])
            if not candidates:
                continue
            meas = min(candidates, key=lambda r: abs(row_t(r) - row_t(ref)))
            if abs(row_t(meas) - row_t(ref)) > 0.05:
                continue
            errors.append(math.dist(xyz(ref), xyz(meas)))
            times.append(row_t(ref) - t0)
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(times, errors, color="purple", lw=1.0)
        ax.set_xlabel("exploration command time [s]")
        ax.set_ylabel("nearest odom error [m]")
        ax.set_title("FUEL-D4 px4ctrl command vs odom error")
        ax.grid(True)
        path = figures_dir / "fuel_d4_command_tracking_error.png"
        fig.savefig(path, dpi=180)
        plt.close(fig)
        figures["command_tracking_error"] = str(path)

    if history:
        t = [float(r.get("ros_time", i)) for i, r in enumerate(history)]
        t0 = t[0]
        points = [float(r.get("published_points", 0.0)) for r in history]
        z_filtered = [float(r.get("z_filtered", 0.0)) for r in history]
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot([v - t0 for v in t], points, color="teal", lw=1.0, label="published world points")
        ax.plot([v - t0 for v in t], z_filtered, color="gray", lw=0.8, label="z-filtered points")
        ax.set_xlabel("cloud time [s]")
        ax.set_ylabel("points/frame")
        ax.set_title("FUEL-D4 world-cloud transform proxy")
        ax.grid(True)
        ax.legend()
        path = figures_dir / "fuel_d4_world_cloud_points.png"
        fig.savefig(path, dpi=180)
        plt.close(fig)
        figures["world_cloud_points"] = str(path)

    return figures, warnings


def build_report(source_dir: Path, output_dir: Path) -> dict[str, Any]:
    metrics = load_json(source_dir / "EGO_SINGLE_METRICS.json")
    manifest = load_json(source_dir / "RUN_MANIFEST.json")
    adapter = load_json(source_dir / "position_cmd_safety_adapter.json")
    accum_review = load_json(source_dir / "livox_world_accumulated_review.json")
    pointcloud_stats = load_json(source_dir / "pointcloud_to_world_stats.json")
    truth = load_csv(source_dir / "truth.csv")
    odom = load_csv(source_dir / "odom.csv")
    cmd = load_csv(source_dir / "position_cmd.csv")
    raw_cmd = load_csv(source_dir / "planner_position_cmd_raw.csv")
    history = load_jsonl(source_dir / "pointcloud_to_world_history.jsonl")

    truth_exec = phase_rows(truth, "exploration_execute")
    odom_exec = phase_rows(odom, "exploration_execute")
    cmd_exec = phase_rows(cmd, "exploration_execute")
    raw_exec = phase_rows(raw_cmd, "exploration_execute")

    figures, figure_warnings = generate_figures(output_dir, truth, odom, cmd, raw_cmd, history)

    safety_status = "passed"
    safety_reasons = []
    min_truth_z = phase_summary(truth_exec).get("min_z_m")
    max_truth_rp = phase_summary(truth_exec).get("max_abs_roll_pitch_deg")
    if metrics.get("status") != "passed" or metrics.get("blockers"):
        safety_status = "failed"
        safety_reasons.append("source metrics status/blockers are not passed/empty")
    if metrics.get("flight_safety_violation"):
        safety_status = "failed"
        safety_reasons.append("flight_safety_violation is present")
    if isinstance(min_truth_z, (int, float)) and min_truth_z < 0.5:
        safety_status = "failed"
        safety_reasons.append("truth z dropped below execute safety gate during exploration")
    if isinstance(max_truth_rp, (int, float)) and max_truth_rp > 45.0:
        safety_status = "failed"
        safety_reasons.append("roll/pitch exceeded execute safety gate during exploration")
    if not metrics.get("land", {}).get("landed_by_truth"):
        safety_status = "review_required"
        safety_reasons.append("landed_by_truth is not true")
    if not safety_reasons:
        safety_reasons.append("source metrics passed, no flight safety violation, exploration z/attitude gates inside limits, landed_by_truth=true")

    report = {
        "schema": "mosim.sunray_ros1.fuel_d4_evaluation.v1",
        "status": "review_ready" if safety_status in {"passed", "review_required"} else "failed",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": {
            "result_dir": rel(source_dir),
            "metrics": rel(source_dir / "EGO_SINGLE_METRICS.json"),
            "manifest": rel(source_dir / "RUN_MANIFEST.json"),
        },
        "source_metrics": {
            "status": metrics.get("status"),
            "blockers": metrics.get("blockers"),
            "mission_mode": metrics.get("mission_mode"),
            "counts": metrics.get("counts"),
            "last_point_counts": metrics.get("last_point_counts"),
            "land": metrics.get("land"),
            "flight_safety_violation": metrics.get("flight_safety_violation"),
        },
        "mission_timing": {
            "configured_execute_duration_s": (manifest.get("fuel") or {}).get("exploration_execute_s"),
            "measured_execute_wall_duration_s": (metrics.get("exploration") or {}).get("wall_duration_s"),
            "exploration_started_sim_t": (metrics.get("exploration") or {}).get("started_t"),
            "exploration_ended_sim_t": (metrics.get("exploration") or {}).get("ended_t"),
            "truth_exploration_phase_sim_duration_s": duration(truth_exec),
            "semantics": "Configured/measured execute duration comes from the mission node wall-clock gate; truth phase duration is Gazebo sim-time span in truth.csv.",
        },
        "run_configuration": {
            "planner": manifest.get("planner"),
            "planner_variant": manifest.get("planner_variant"),
            "mission_mode": manifest.get("mission_mode"),
            "fuel": manifest.get("fuel"),
            "position_cmd_safety_adapter": manifest.get("position_cmd_safety_adapter"),
            "pointcloud_to_world": manifest.get("pointcloud_to_world"),
            "pointcloud_review": manifest.get("pointcloud_review"),
        },
        "trajectory_summary": {
            "truth_phases": {phase: phase_summary(phase_rows(truth, phase)) for phase in sorted({str(r.get("phase")) for r in truth})},
            "odom_phases": {phase: phase_summary(phase_rows(odom, phase)) for phase in sorted({str(r.get("phase")) for r in odom})},
            "position_cmd_exploration": phase_summary(cmd_exec),
            "raw_fuel_cmd_exploration": phase_summary(raw_exec),
        },
        "tracking_proxy": {
            "position_cmd_to_odom": nearest_tracking(cmd_exec, odom_exec, max_dt_s=0.05),
            "position_cmd_to_truth": nearest_tracking(cmd_exec, truth_exec, max_dt_s=0.05),
            "semantics": "nearest-time command tracking proxy during exploration stream; not a fixed-goal tracking acceptance metric",
        },
        "command_continuity": {
            "metrics_position_cmd_continuity": metrics.get("position_cmd_continuity"),
            "metrics_raw_planner_position_cmd_continuity": metrics.get("planner_position_cmd_continuity"),
            "adapter": adapter,
        },
        "map_and_coverage_proxy": map_proxy(history, metrics, manifest, accum_review),
        "pointcloud_transform_last_stats": pointcloud_stats,
        "safety_assessment": {
            "status": safety_status,
            "reasons": safety_reasons,
            "min_truth_z_explore_m": min_truth_z,
            "max_truth_roll_pitch_explore_deg": max_truth_rp,
            "flight_safety_violation": metrics.get("flight_safety_violation"),
            "landed_by_truth": metrics.get("land", {}).get("landed_by_truth"),
            "contact_sensor_evidence": "not_recorded",
            "contact_claim_boundary": "No Gazebo contact-sensor or collision-state stream is parsed by this offline package; absence of crash is inferred only from mission metrics, safety gates, and successful landing.",
        },
        "log_diagnostics": log_diagnostics(source_dir),
        "figures": {key: rel(value) for key, value in figures.items()},
        "warnings": figure_warnings,
        "claim_boundary": [
            "This package evaluates one completed FUEL-D3 run and builds report-ready D4 metrics/figures offline.",
            "It proves bounded single-UAV FUEL exploration command-stream execution evidence, map/coverage proxies, path length, and safety-gate status for the referenced run.",
            "Coverage is estimated from accumulated review voxels, occupancy point counts, and world-cloud envelopes; it is not a formal full-map completion percentage.",
            "Planner log collision/replan messages are internal FUEL diagnostics and are not Gazebo physical-contact proof.",
            "This package does not prove RACER multi-UAV exploration, Swarm-Formation, UE map import, QGC UI, or final competition performance.",
        ],
        "next_actions": [
            "Use this D4 package as the FUEL single-UAV exploration evidence index.",
            "Start RACER-D0 source audit and RACER-D1/D2 adapter planning for three-UAV autonomous exploration.",
            "Only rerun FUEL if a later review requires live RViz screenshots or a longer/full-coverage exploration run.",
        ],
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="completed FUEL-D3 result directory")
    parser.add_argument("--output-dir", type=Path, default=None, help="evaluation package output directory")
    args = parser.parse_args()

    source_dir = repo_path(args.source)
    if not source_dir.is_dir():
        raise SystemExit(f"source result directory not found: {source_dir}")
    if args.output_dir is None:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = DEFAULT_OUTPUT_ROOT / f"fuel_d4_evaluation_{stamp}"
    else:
        output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(source_dir, output_dir)
    report["output_dir"] = rel(output_dir)
    write_json(output_dir / "FUEL_D4_EVALUATION.json", report)
    write_summary(output_dir / "SUMMARY.md", report)
    print(json.dumps({"status": report["status"], "output_dir": rel(output_dir)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
