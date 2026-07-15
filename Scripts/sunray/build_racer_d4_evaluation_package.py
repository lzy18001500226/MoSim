#!/usr/bin/env python3
"""Build an offline RACER-D4 evaluation package from a completed D3 run.

This script indexes and evaluates already-recorded evidence only. It does not
start ROS, Gazebo, PX4, MAVROS, RViz, RACER, or any GUI process.
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
from statistics import mean, pstdev
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = ROOT / "Results/sunray_ros1/racer_d3_pair_opt_enabled_30s_cutofffix_20260701_161557"
DEFAULT_OUTPUT_ROOT = ROOT / "Results/sunray_ros1"
DEFAULT_OCCUPANCY_RESOLUTION_M = 0.1


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
    with path.open(encoding="utf-8", newline="") as handle:
        return [{key: maybe_float(value) for key, value in row.items()} for row in csv.DictReader(handle)]


def row_t(row: dict[str, Any]) -> float:
    value = row.get("t", 0.0)
    return float(value) if isinstance(value, (int, float)) else 0.0


def xyz(row: dict[str, Any]) -> tuple[float, float, float]:
    return (
        float(row.get("x", 0.0)),
        float(row.get("y", 0.0)),
        float(row.get("z", 0.0)),
    )


def phase_rows(rows: list[dict[str, Any]], phase: str) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("phase") == phase]


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


def finite_values(rows: list[dict[str, Any]], key: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        value = row.get(key)
        if isinstance(value, (int, float)) and math.isfinite(float(value)):
            values.append(float(value))
    return values


def rmse(values: list[float]) -> float | None:
    if not values:
        return None
    return math.sqrt(sum(v * v for v in values) / len(values))


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


def max_abs_roll_pitch_deg(rows: list[dict[str, Any]]) -> float | None:
    vals: list[float] = []
    for row in rows:
        roll = row.get("roll")
        pitch = row.get("pitch")
        if isinstance(roll, (int, float)) and isinstance(pitch, (int, float)):
            vals.append(max(abs(float(roll)), abs(float(pitch))) * 180.0 / math.pi)
    return max(vals) if vals else None


def phase_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"samples": 0}
    z_values = finite_values(rows, "z")
    speeds = [
        math.sqrt(float(r.get("vx", 0.0)) ** 2 + float(r.get("vy", 0.0)) ** 2 + float(r.get("vz", 0.0)) ** 2)
        for r in rows
    ]
    return {
        "samples": len(rows),
        "start_t": row_t(rows[0]),
        "end_t": row_t(rows[-1]),
        "duration_s": duration(rows),
        "path_length_m": path_length(rows),
        "min_z_m": min(z_values) if z_values else None,
        "max_z_m": max(z_values) if z_values else None,
        "max_speed_mps": max(speeds) if speeds else None,
        "max_abs_vz_mps": max((abs(float(r.get("vz", 0.0))) for r in rows), default=None),
        "max_abs_roll_pitch_deg": max_abs_roll_pitch_deg(rows),
        "start_xyz": list(xyz(rows[0])),
        "end_xyz": list(xyz(rows[-1])),
    }


def coefficient_of_variation(values: list[float]) -> float | None:
    clean = [float(v) for v in values if math.isfinite(float(v))]
    if not clean:
        return None
    avg = mean(clean)
    if abs(avg) < 1e-12:
        return None
    return pstdev(clean) / abs(avg)


def nearest_tracking(
    reference_rows: list[dict[str, Any]],
    measured_rows: list[dict[str, Any]],
    *,
    max_dt_s: float,
) -> dict[str, Any]:
    if not reference_rows or not measured_rows:
        return {"samples": 0, "max_dt_s": max_dt_s}
    measured_times = [row_t(row) for row in measured_rows]
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
        meas = min(candidates, key=lambda row: abs(row_t(row) - t))
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
        "max_xyz_m": max(errors_xyz) if errors_xyz else None,
        "max_xy_m": max(errors_xy) if errors_xy else None,
        "max_z_m": max(errors_z) if errors_z else None,
        "p95_xyz_m": quantile(errors_xyz, 0.95),
        "p95_xy_m": quantile(errors_xy, 0.95),
        "p95_z_m": quantile(errors_z, 0.95),
    }


def pair_key(row: dict[str, Any]) -> str:
    a = int(row.get("uav_a", 0)) if isinstance(row.get("uav_a"), (int, float)) else row.get("uav_a", "")
    b = int(row.get("uav_b", 0)) if isinstance(row.get("uav_b"), (int, float)) else row.get("uav_b", "")
    return f"uav{a}-uav{b}"


def separation_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    distances = finite_values(rows, "distance_m")
    by_pair: dict[str, list[float]] = {}
    by_phase: dict[str, list[float]] = {}
    for row in rows:
        value = row.get("distance_m")
        if not isinstance(value, (int, float)):
            continue
        dist = float(value)
        by_pair.setdefault(pair_key(row), []).append(dist)
        phase = str(row.get("phase") or "unknown")
        by_phase.setdefault(phase, []).append(dist)
    return {
        "samples": len(distances),
        "min_m": min(distances) if distances else None,
        "p05_m": quantile(distances, 0.05),
        "mean_m": mean(distances) if distances else None,
        "by_pair": {
            key: {
                "samples": len(vals),
                "min_m": min(vals),
                "p05_m": quantile(vals, 0.05),
                "mean_m": mean(vals),
            }
            for key, vals in sorted(by_pair.items())
        },
        "by_phase": {
            key: {
                "samples": len(vals),
                "min_m": min(vals),
                "p05_m": quantile(vals, 0.05),
                "mean_m": mean(vals),
            }
            for key, vals in sorted(by_phase.items())
        },
    }


def trajectory_envelope(rows_by_uav: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    points = [xyz(row) for rows in rows_by_uav.values() for row in phase_rows(rows, "ego_execute")]
    if not points:
        return {"samples": 0}
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    zs = [p[2] for p in points]
    span_x = max(xs) - min(xs)
    span_y = max(ys) - min(ys)
    span_z = max(zs) - min(zs)
    return {
        "samples": len(points),
        "min_xyz": [min(xs), min(ys), min(zs)],
        "max_xyz": [max(xs), max(ys), max(zs)],
        "span_xyz_m": [span_x, span_y, span_z],
        "bbox_volume_proxy_m3": span_x * span_y * max(span_z, 0.0),
        "xy_area_proxy_m2": span_x * span_y,
    }


def parse_revisit_proxy(log_path: Path) -> dict[str, Any]:
    if not log_path.is_file():
        return {
            "log_exists": False,
            "rediscovered_grid_events": 0,
            "unique_rediscovered_grids": 0,
            "cluster_covered_events": 0,
        }
    text = log_path.read_text(encoding="utf-8", errors="replace")
    grids = re.findall(r"Grid\s+(\d+)\s+is rediscovered", text)
    cluster_covered = len(re.findall(r"Replan:\s+cluster covered", text))
    repeated_grids = len(grids) - len(set(grids))
    repeat_ratio = (repeated_grids / len(grids)) if grids else None
    return {
        "log_exists": True,
        "rediscovered_grid_events": len(grids),
        "unique_rediscovered_grids": len(set(grids)),
        "repeated_grid_events": repeated_grids,
        "rediscovered_repeat_ratio": repeat_ratio,
        "cluster_covered_events": cluster_covered,
        "claim_boundary": "This is a planner-log revisit/rediscovery proxy, not a formal coverage-overlap ratio.",
    }


def make_figures(output_dir: Path, per_uav: dict[str, dict[str, Any]], separation_rows: list[dict[str, Any]]) -> dict[str, str]:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # pragma: no cover - depends on local plotting stack
        return {"error": f"matplotlib unavailable: {exc}"}

    figures: dict[str, str] = {}
    figures_dir = output_dir / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)

    path = figures_dir / "racer_d4_xy_paths.png"
    fig, ax = plt.subplots(figsize=(7, 6))
    for label, item in sorted(per_uav.items()):
        truth_rows = item["rows"]["truth"]
        exec_rows = phase_rows(truth_rows, "ego_execute") or truth_rows
        if exec_rows:
            ax.plot([float(r.get("x", 0.0)) for r in exec_rows], [float(r.get("y", 0.0)) for r in exec_rows], label=label)
    ax.set_title("RACER-D4 truth XY paths")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.axis("equal")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    figures["xy_paths"] = rel(path)

    path = figures_dir / "racer_d4_altitude.png"
    fig, ax = plt.subplots(figsize=(8, 4))
    for label, item in sorted(per_uav.items()):
        truth_rows = item["rows"]["truth"]
        if truth_rows:
            t0 = row_t(truth_rows[0])
            ax.plot([row_t(r) - t0 for r in truth_rows], [float(r.get("z", 0.0)) for r in truth_rows], label=label)
    ax.set_title("RACER-D4 truth altitude")
    ax.set_xlabel("time from first sample [s]")
    ax.set_ylabel("z [m]")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    figures["altitude"] = rel(path)

    if separation_rows:
        path = figures_dir / "racer_d4_inter_uav_separation.png"
        fig, ax = plt.subplots(figsize=(8, 4))
        by_pair: dict[str, list[dict[str, Any]]] = {}
        for row in separation_rows:
            by_pair.setdefault(pair_key(row), []).append(row)
        for key, rows in sorted(by_pair.items()):
            t0 = row_t(rows[0])
            ax.plot([row_t(r) - t0 for r in rows], [float(r.get("distance_m", 0.0)) for r in rows], label=key)
        ax.axhline(1.2, color="tab:red", linestyle="--", linewidth=1.0, label="1.2m gate")
        ax.set_title("RACER-D4 inter-UAV separation")
        ax.set_xlabel("time from first pair sample [s]")
        ax.set_ylabel("distance [m]")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(path, dpi=160)
        plt.close(fig)
        figures["inter_uav_separation"] = rel(path)

    path = figures_dir / "racer_d4_workload_proxy.png"
    labels = sorted(per_uav.keys())
    path_lengths = [per_uav[label]["summary"]["truth_execute"].get("path_length_m") or 0.0 for label in labels]
    frontier_counts = [per_uav[label]["counts"].get("frontier") or 0 for label in labels]
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    axes[0].bar(labels, path_lengths, color="tab:blue")
    axes[0].set_title("Execute path length")
    axes[0].set_ylabel("m")
    axes[1].bar(labels, frontier_counts, color="tab:green")
    axes[1].set_title("Frontier topic count")
    axes[1].set_ylabel("count")
    for ax in axes:
        ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)
    figures["workload_proxy"] = rel(path)

    return figures


def build_package(source_dir: Path, output_dir: Path) -> dict[str, Any]:
    manifest = load_json(source_dir / "RUN_MANIFEST.json")
    metrics = load_json(source_dir / "EGO_SWARM_METRICS.json")
    audit = load_json(source_dir / "planner_runtime_log_audit.json")
    startup = load_json(source_dir / "STARTUP_ATTEMPT_SUMMARY.json")
    separation_rows = load_csv(source_dir / "inter_uav_separation.csv")

    uav_ids = sorted((metrics.get("per_uav") or {}).keys(), key=lambda v: int(v))
    per_uav: dict[str, dict[str, Any]] = {}
    truth_rows_by_uav: dict[str, list[dict[str, Any]]] = {}
    workload_values = {
        "truth_execute_path_length_m": [],
        "frontier_count": [],
        "raw_position_cmd_rows": [],
        "position_cmd_rows": [],
        "bspline_count": [],
    }

    for uid in uav_ids:
        label = f"uav{uid}"
        truth_rows = load_csv(source_dir / f"{label}_truth.csv")
        odom_rows = load_csv(source_dir / f"{label}_odom.csv")
        position_cmd_rows = load_csv(source_dir / f"{label}_position_cmd.csv")
        raw_position_cmd_rows = load_csv(source_dir / f"{label}_raw_position_cmd.csv")
        truth_execute = phase_rows(truth_rows, "ego_execute")
        odom_execute = phase_rows(odom_rows, "ego_execute")
        position_cmd_execute = phase_rows(position_cmd_rows, "ego_execute")
        raw_position_cmd_execute = phase_rows(raw_position_cmd_rows, "ego_execute")
        counts = (metrics.get("per_uav") or {}).get(uid, {}).get("counts", {})
        last_point_counts = (metrics.get("per_uav") or {}).get(uid, {}).get("last_point_counts", {})
        summary = {
            "truth_all": phase_summary(truth_rows),
            "truth_execute": phase_summary(truth_execute),
            "truth_land": phase_summary(phase_rows(truth_rows, "land")),
            "odom_execute": phase_summary(odom_execute),
            "position_cmd_execute": phase_summary(position_cmd_execute),
            "raw_position_cmd_execute": phase_summary(raw_position_cmd_execute),
        }
        tracking = {
            "position_cmd_to_odom_execute": nearest_tracking(position_cmd_execute, odom_execute, max_dt_s=0.15),
            "position_cmd_to_truth_execute": nearest_tracking(position_cmd_execute, truth_execute, max_dt_s=0.15),
            "raw_position_cmd_to_odom_execute": nearest_tracking(raw_position_cmd_execute, odom_execute, max_dt_s=0.15),
        }
        per_uav[label] = {
            "summary": summary,
            "tracking": tracking,
            "counts": counts,
            "last_point_counts": last_point_counts,
            "planner_command_audit": (metrics.get("per_uav") or {}).get(uid, {}).get("planner_command_audit", {}),
            "rows": {
                "truth": truth_rows,
                "odom": odom_rows,
                "position_cmd": position_cmd_rows,
                "raw_position_cmd": raw_position_cmd_rows,
            },
        }
        truth_rows_by_uav[label] = truth_rows
        workload_values["truth_execute_path_length_m"].append(summary["truth_execute"].get("path_length_m") or 0.0)
        workload_values["frontier_count"].append(counts.get("frontier") or 0)
        workload_values["raw_position_cmd_rows"].append(counts.get("raw_position_cmd_rows") or 0)
        workload_values["position_cmd_rows"].append(counts.get("position_cmd_rows") or 0)
        workload_values["bspline_count"].append(counts.get("bspline") or 0)

    occupancy_resolution = float(
        (((manifest.get("racer_d3_constraints") or {}).get("sdf_map_resolution_m")) or DEFAULT_OCCUPANCY_RESOLUTION_M)
    )
    occupancy_last_points = sum((item["last_point_counts"].get("occupancy") or 0) for item in per_uav.values())
    coverage_proxy = {
        "occupancy_resolution_m_assumed": occupancy_resolution,
        "occupancy_last_points_sum": occupancy_last_points,
        "occupancy_voxel_volume_proxy_m3": occupancy_last_points * occupancy_resolution**3,
        "frontier_topic_count_sum": sum((item["counts"].get("frontier") or 0) for item in per_uav.values()),
        "world_cloud_message_count_sum": sum((item["counts"].get("world_cloud") or 0) for item in per_uav.values()),
        "raw_lidar_message_count_sum": sum((item["counts"].get("raw_lidar") or 0) for item in per_uav.values()),
        "trajectory_envelope": trajectory_envelope(truth_rows_by_uav),
        "claim_boundary": "Coverage is a proxy from recorded occupancy/frontier/world-cloud counts and flight envelope, not a formal full-map completion percentage.",
    }

    workload_balance = {
        key: {
            "values": values,
            "mean": mean(values) if values else None,
            "coefficient_of_variation": coefficient_of_variation([float(v) for v in values]),
        }
        for key, values in workload_values.items()
    }

    safety = {
        "status_from_d3": metrics.get("status"),
        "source_blockers": metrics.get("blockers"),
        "mission_exit_code": manifest.get("mission_exit_code"),
        "min_inter_uav_distance_m": metrics.get("min_inter_uav_distance_m"),
        "min_inter_uav_pair": metrics.get("min_inter_uav_pair"),
        "safe_distance_gate_m": (manifest.get("racer_d3_constraints") or {}).get("swarm_safe_dist", 1.2),
        "runtime_audit_status": audit.get("status"),
        "fatal_event_count": audit.get("fatal_event_count"),
        "semantic_blockers": audit.get("semantic_blockers"),
        "inter_uav_separation": separation_summary(separation_rows),
    }

    topic_evidence = {
        "per_uav_counts": {
            label: {
                "raw_lidar": item["counts"].get("raw_lidar"),
                "world_cloud": item["counts"].get("world_cloud"),
                "occupancy": item["counts"].get("occupancy"),
                "frontier": item["counts"].get("frontier"),
                "trajectory_vis": item["counts"].get("trajectory_vis"),
                "swarm_traj": item["counts"].get("swarm_traj"),
                "bspline": item["counts"].get("bspline"),
                "raw_position_cmd_rows": item["counts"].get("raw_position_cmd_rows"),
                "position_cmd_rows": item["counts"].get("position_cmd_rows"),
            }
            for label, item in sorted(per_uav.items())
        },
        "startup_attempts": len(startup.get("attempts") or []),
        "gazebo_livox_marker_count": ((startup.get("attempts") or [{}])[-1]).get("gazebo_livox_marker_count"),
    }

    revisit_proxy = parse_revisit_proxy(source_dir / "planner_swarm_px4ctrl_goal5.log")

    figures = make_figures(output_dir, per_uav, separation_rows)

    # Drop raw rows from the persisted JSON.
    per_uav_for_json = {
        label: {key: value for key, value in item.items() if key != "rows"}
        for label, item in sorted(per_uav.items())
    }

    warnings: list[str] = []
    if metrics.get("status") != "passed":
        warnings.append("source_d3_status_not_passed")
    if metrics.get("blockers"):
        warnings.append("source_d3_has_blockers")
    if audit.get("status") != "passed":
        warnings.append("runtime_audit_not_passed")
    if not figures or "error" in figures:
        warnings.append("figures_incomplete")

    evaluation = {
        "schema": "mosim.sunray_ros1.racer_d4_evaluation.v1",
        "status": "review_ready" if not warnings[:3] else "blocked",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_result_dir": rel(source_dir),
        "source_run_status": metrics.get("status"),
        "source_blockers": metrics.get("blockers"),
        "run_settings": {
            "planner_variant": manifest.get("planner_variant"),
            "uav_num": manifest.get("uav_num"),
            "mission_completion_mode": metrics.get("mission_completion_mode"),
            "exploration_duration_s": (metrics.get("per_uav") or {}).get("1", {}).get("exploration_stream", {}).get("duration_target_s"),
            "controller_core_profile": manifest.get("controller_core_profile"),
            "racer_d3_constraints": manifest.get("racer_d3_constraints"),
        },
        "safety": safety,
        "coverage_proxy": coverage_proxy,
        "revisit_overlap_proxy": revisit_proxy,
        "workload_balance": workload_balance,
        "per_uav": per_uav_for_json,
        "topic_evidence": topic_evidence,
        "runtime_log_audit": {
            "status": audit.get("status"),
            "fatal_event_count": audit.get("fatal_event_count"),
            "semantic_event_counts": audit.get("semantic_event_counts"),
            "ignored_semantic_blocker_counts": audit.get("ignored_semantic_blocker_counts"),
            "semantic_blocker_max_ros_time_s": audit.get("semantic_blocker_max_ros_time_s"),
        },
        "figures": figures,
        "warnings": warnings,
        "claim_boundary": (
            "RACER-D4 is an offline evaluation package for one completed D3 run. "
            "It reports coverage, revisit and workload proxies plus safety/tracking "
            "metrics. It does not prove full-map completion, RViz manual acceptance, "
            "Swarm-Formation, UE map import, QGC UI, or final competition performance."
        ),
    }
    return evaluation


def write_summary(evaluation: dict[str, Any], output_dir: Path) -> None:
    safety = evaluation["safety"]
    coverage = evaluation["coverage_proxy"]
    revisit = evaluation["revisit_overlap_proxy"]
    workload = evaluation["workload_balance"]
    topic = evaluation["topic_evidence"]
    figures = evaluation.get("figures") or {}

    lines = [
        "# RACER-D4 Evaluation Package",
        "",
        f"- status: `{evaluation.get('status')}`",
        f"- source_result_dir: `{evaluation.get('source_result_dir')}`",
        f"- generated_at: `{evaluation.get('generated_at')}`",
        f"- source_run_status: `{evaluation.get('source_run_status')}`",
        f"- source_blockers: `{evaluation.get('source_blockers')}`",
        "",
        "## Mission And Safety",
        "",
        f"- mission_completion_mode: `{evaluation.get('run_settings', {}).get('mission_completion_mode')}`",
        f"- mission_exit_code: `{safety.get('mission_exit_code')}`",
        f"- min_inter_uav_distance_m: `{safety.get('min_inter_uav_distance_m')}`",
        f"- min_inter_uav_pair: `{safety.get('min_inter_uav_pair')}`",
        f"- safe_distance_gate_m: `{safety.get('safe_distance_gate_m')}`",
        f"- runtime_audit_status: `{safety.get('runtime_audit_status')}`",
        f"- fatal_event_count: `{safety.get('fatal_event_count')}`",
        "",
        "## Coverage / Map Proxy",
        "",
        f"- occupancy_last_points_sum: `{coverage.get('occupancy_last_points_sum')}`",
        f"- occupancy_voxel_volume_proxy_m3: `{coverage.get('occupancy_voxel_volume_proxy_m3')}`",
        f"- frontier_topic_count_sum: `{coverage.get('frontier_topic_count_sum')}`",
        f"- world_cloud_message_count_sum: `{coverage.get('world_cloud_message_count_sum')}`",
        f"- raw_lidar_message_count_sum: `{coverage.get('raw_lidar_message_count_sum')}`",
        f"- trajectory_xy_area_proxy_m2: `{coverage.get('trajectory_envelope', {}).get('xy_area_proxy_m2')}`",
        "",
        "## Revisit / Overlap Proxy",
        "",
        f"- rediscovered_grid_events: `{revisit.get('rediscovered_grid_events')}`",
        f"- unique_rediscovered_grids: `{revisit.get('unique_rediscovered_grids')}`",
        f"- rediscovered_repeat_ratio: `{revisit.get('rediscovered_repeat_ratio')}`",
        f"- cluster_covered_events: `{revisit.get('cluster_covered_events')}`",
        "",
        "## Workload Balance",
        "",
        f"- execute_path_length_cv: `{workload.get('truth_execute_path_length_m', {}).get('coefficient_of_variation')}`",
        f"- frontier_count_cv: `{workload.get('frontier_count', {}).get('coefficient_of_variation')}`",
        f"- bspline_count_cv: `{workload.get('bspline_count', {}).get('coefficient_of_variation')}`",
        "",
        "## Per-UAV Evidence",
        "",
        "| UAV | execute_path_m | cmd_to_odom_rmse_xyz_m | frontier | occupancy | bspline | raw_cmd_rows | cmd_rows |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, item in sorted(evaluation.get("per_uav", {}).items()):
        execute_path = item["summary"]["truth_execute"].get("path_length_m")
        rmse_xyz = item["tracking"]["position_cmd_to_odom_execute"].get("rmse_xyz_m")
        counts = item.get("counts") or {}
        lines.append(
            f"| {label} | {execute_path} | {rmse_xyz} | {counts.get('frontier')} | "
            f"{counts.get('occupancy')} | {counts.get('bspline')} | "
            f"{counts.get('raw_position_cmd_rows')} | {counts.get('position_cmd_rows')} |"
        )

    lines.extend(
        [
            "",
            "## Topic Evidence",
            "",
            f"- startup_attempts: `{topic.get('startup_attempts')}`",
            f"- gazebo_livox_marker_count: `{topic.get('gazebo_livox_marker_count')}`",
            "",
            "## Figures",
            "",
        ]
    )
    if figures:
        for key, value in figures.items():
            lines.append(f"- `{key}`: `{value}`")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- This package evaluates one completed RACER-D3 run offline.",
            "- Coverage is reported through occupancy/frontier/world-cloud counts and trajectory-envelope proxies; it is not a formal full-map completion percentage.",
            "- Revisit/overlap is estimated from RACER planner logs such as rediscovered grids and cluster-covered replans; it is not a formal overlap ratio.",
            "- RViz manual visual acceptance is not claimed unless separate screenshots are captured.",
            "- This package does not prove Swarm-Formation, UE map import, QGC UI, or final competition performance.",
            "",
            "## Next",
            "",
            "- Use this D4 package as the RACER three-UAV autonomous-exploration evidence index.",
            "- Proceed to Swarm-Formation-style known-target cluster/formation planning, unless a RACER RViz visual review or rerun is requested first.",
            "",
        ]
    )
    (output_dir / "SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), help="Completed RACER-D3 result directory.")
    parser.add_argument("--output", default="", help="Output directory. Defaults to Results/sunray_ros1/racer_d4_evaluation_<timestamp>.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    source_dir = repo_path(args.source)
    if not source_dir.is_dir():
        raise SystemExit(f"source directory not found: {source_dir}")
    if args.output:
        output_dir = repo_path(args.output)
    else:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = DEFAULT_OUTPUT_ROOT / f"racer_d4_evaluation_{stamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    evaluation = build_package(source_dir, output_dir)
    (output_dir / "RACER_D4_EVALUATION.json").write_text(
        json.dumps(evaluation, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_summary(evaluation, output_dir)
    print(rel(output_dir))
    return 0 if evaluation.get("status") == "review_ready" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
