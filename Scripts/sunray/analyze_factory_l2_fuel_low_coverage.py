#!/usr/bin/env python3
"""Build a source/log evidence packet for Factory L2 FUEL low coverage.

This script is intentionally offline: it does not launch ROS, Gazebo, RViz, or
UE. It turns existing FUEL runs into a repeatable diagnosis packet so that the
next runtime probe is driven by evidence instead of visual guessing.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import mean, median
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULT_ROOT = ROOT / "Results/sunray_ros1"

DEFAULT_RUNS = [
    RESULT_ROOT / "factory_l2_fuel_speed08_smoke60_20260708_current",
    RESULT_ROOT / "factory_l2_fuel_same_flight_full_v035_takeoff120_20260706_110303",
]
DEFAULT_OUT = RESULT_ROOT / "factory_l2_fuel_source_level_diagnosis_20260708"

ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
FLOAT_RE = re.compile(r"[-+]?(?:\d+\.\d*|\d*\.\d+|\d+)(?:[eE][-+]?\d+)?")


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8-sig") as f:
        return json.load(f)


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def get_path(obj: dict[str, Any] | None, keys: list[str], default: Any = None) -> Any:
    cur: Any = obj
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def as_float(value: Any, default: float = math.nan) -> float:
    try:
        if value in (None, ""):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def as_percent(value: Any) -> float | None:
    v = as_float(value)
    if math.isnan(v):
        return None
    return v * 100.0


def first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def find_coverage_packet(run_dir: Path) -> Path | None:
    candidates = [
        run_dir / "coverage_packet_full/FACTORY_L2_INDOOR_COVERAGE_PACKET.json",
        run_dir / "coverage_packet_rebuild_after_metrics/FACTORY_L2_INDOOR_COVERAGE_PACKET.json",
        run_dir / "coverage_packet_merged_check/FACTORY_L2_INDOOR_COVERAGE_PACKET.json",
        run_dir / "coverage_packet_manual_stop/FACTORY_L2_INDOOR_COVERAGE_PACKET.json",
        run_dir / "coverage_packet/FACTORY_L2_INDOOR_COVERAGE_PACKET.json",
    ]
    return first_existing(candidates)


def rows_for_phase(rows: list[dict[str, str]], phase: str) -> list[dict[str, str]]:
    selected = [row for row in rows if row.get("phase") == phase]
    return selected if selected else rows


def span(rows: list[dict[str, str]]) -> dict[str, Any]:
    clean: list[tuple[float, float, float, float]] = []
    for row in rows:
        t = as_float(row.get("t"))
        x = as_float(row.get("x"))
        y = as_float(row.get("y"))
        z = as_float(row.get("z"))
        if not any(math.isnan(v) for v in (t, x, y, z)):
            clean.append((t, x, y, z))
    if not clean:
        return {"samples": 0}
    ts = [v[0] for v in clean]
    xs = [v[1] for v in clean]
    ys = [v[2] for v in clean]
    zs = [v[3] for v in clean]
    return {
        "samples": len(clean),
        "t_start": min(ts),
        "t_end": max(ts),
        "duration_s": max(ts) - min(ts),
        "x_min": min(xs),
        "x_max": max(xs),
        "x_range_m": max(xs) - min(xs),
        "y_min": min(ys),
        "y_max": max(ys),
        "y_range_m": max(ys) - min(ys),
        "z_min": min(zs),
        "z_max": max(zs),
        "z_range_m": max(zs) - min(zs),
        "start_xyz": [xs[0], ys[0], zs[0]],
        "end_xyz": [xs[-1], ys[-1], zs[-1]],
        "start_to_end_xyz_m": math.dist((xs[0], ys[0], zs[0]), (xs[-1], ys[-1], zs[-1])),
    }


def speed_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    speeds: list[float] = []
    for row in rows:
        vx = as_float(row.get("vx"))
        vy = as_float(row.get("vy"))
        vz = as_float(row.get("vz"))
        if not any(math.isnan(v) for v in (vx, vy, vz)):
            speeds.append(math.sqrt(vx * vx + vy * vy + vz * vz))
    if not speeds:
        return {"samples": 0}
    speeds.sort()
    p95_idx = min(len(speeds) - 1, max(0, int(math.ceil(len(speeds) * 0.95)) - 1))
    return {
        "samples": len(speeds),
        "mean_mps": mean(speeds),
        "median_mps": median(speeds),
        "p95_mps": speeds[p95_idx],
        "max_mps": max(speeds),
    }


def stats(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"samples": 0}
    ordered = sorted(values)
    return {
        "samples": len(values),
        "min": min(values),
        "max": max(values),
        "mean": mean(values),
        "median": median(values),
        "first": values[0],
        "last": values[-1],
        "p95": ordered[min(len(ordered) - 1, max(0, int(math.ceil(len(ordered) * 0.95)) - 1))],
    }


def bounds_summary(points: list[dict[str, float]], prefix: str = "") -> dict[str, Any]:
    """Summarize x/y/z fields in a small list of parsed log records."""
    if not points:
        return {"samples": 0}
    xs = [p[f"{prefix}x"] for p in points if f"{prefix}x" in p]
    ys = [p[f"{prefix}y"] for p in points if f"{prefix}y" in p]
    zs = [p[f"{prefix}z"] for p in points if f"{prefix}z" in p]
    if not xs or not ys or not zs:
        return {"samples": 0}
    return {
        "samples": min(len(xs), len(ys), len(zs)),
        "x_min": min(xs),
        "x_max": max(xs),
        "x_range_m": max(xs) - min(xs),
        "y_min": min(ys),
        "y_max": max(ys),
        "y_range_m": max(ys) - min(ys),
        "z_min": min(zs),
        "z_max": max(zs),
        "z_range_m": max(zs) - min(zs),
        "first": points[0],
        "last": points[-1],
    }


def kv_floats(line: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for key, value in re.findall(r"([A-Za-z_][A-Za-z0-9_]*)=([-+]?\d+(?:\.\d+)?)", line):
        out[key] = float(value)
    return out


def parse_fuel_log(path: Path) -> dict[str, Any]:
    frontier_counts: list[float] = []
    viewpoint_counts: list[float] = []
    new_frontiers: list[float] = []
    new_dormant: list[float] = []
    to_visit: list[float] = []
    dormant_total: list[float] = []
    next_views: list[dict[str, float]] = []
    viewpoint_diag: list[dict[str, float]] = []
    cluster_viewpoint_diag: list[dict[str, float]] = []
    candidate_pools: list[dict[str, float]] = []
    global_rank0: list[dict[str, float]] = []
    local_refine_selected: list[dict[str, float]] = []
    coverage_expansion_events: Counter[str] = Counter()
    replan_reasons: Counter[str] = Counter()
    fsm_transitions: Counter[str] = Counter()
    path_modes: Counter[str] = Counter()
    no_coverable = 0
    no_path = 0
    trigger_count = 0

    if not path.exists():
        return {"exists": False, "path": str(path)}

    frontier_re = re.compile(r"Frontier:\s*(\d+).*?viewpoint:\s*(\d+)")
    new_re = re.compile(r"new num:\s*(\d+),\s*new dormant:\s*(\d+)")
    visit_re = re.compile(r"to visit:\s*(\d+),\s*dormant:\s*(\d+)")
    replan_re = re.compile(r"Replan:\s*([^=]+)")
    fsm_re = re.compile(r"\[FSM\]: from ([A-Z_]+) to ([A-Z_]+)")
    candidate_pool_re = re.compile(
        r"candidate_pool n=(\d+) pos=\(([^,]+), ([^,]+), ([^)]+)\) "
        r"view_x=\[([^,]+), ([^\]]+)\] view_y=\[([^,]+), ([^\]]+)\] "
        r"view_z=\[([^,]+), ([^\]]+)\] avg_x=\[([^,]+), ([^\]]+)\] "
        r"avg_y=\[([^,]+), ([^\]]+)\] avg_z=\[([^,]+), ([^\]]+)\]"
    )
    global_tour_re = re.compile(
        r"global_tour rank=(\d+) id=(\d+) view=\(([^,]+), ([^,]+), ([^)]+)\) "
        r"avg=\(([^,]+), ([^,]+), ([^)]+)\) yaw=([^ ]+) dist_xy=([^ ]+)"
    )
    local_refine_re = re.compile(
        r"local_refine selected=\(([^,]+), ([^,]+), ([^)]+)\) yaw=([^ ]+) "
        r"unrefined_first_n=(\d+) refined_n=(\d+)"
    )

    with path.open("r", encoding="utf-8", errors="ignore") as f:
        for raw_line in f:
            line = ANSI_RE.sub("", raw_line).strip()
            if not line:
                continue
            if "[FUEL_VIEWPOINT_DIAG] clusters=" in line:
                viewpoint_diag.append(kv_floats(line))
            if "[FUEL_CLUSTER_VIEWPOINT_DIAG]" in line:
                cluster_viewpoint_diag.append(kv_floats(line))
            m = candidate_pool_re.search(line)
            if m:
                vals = [float(m.group(i)) for i in range(2, 17)]
                candidate_pools.append(
                    {
                        "n": float(m.group(1)),
                        "pos_x": vals[0],
                        "pos_y": vals[1],
                        "pos_z": vals[2],
                        "view_x_min": vals[3],
                        "view_x_max": vals[4],
                        "view_y_min": vals[5],
                        "view_y_max": vals[6],
                        "view_z_min": vals[7],
                        "view_z_max": vals[8],
                        "avg_x_min": vals[9],
                        "avg_x_max": vals[10],
                        "avg_y_min": vals[11],
                        "avg_y_max": vals[12],
                        "avg_z_min": vals[13],
                        "avg_z_max": vals[14],
                    }
                )
            m = global_tour_re.search(line)
            if m and int(m.group(1)) == 0:
                global_rank0.append(
                    {
                        "id": float(m.group(2)),
                        "view_x": float(m.group(3)),
                        "view_y": float(m.group(4)),
                        "view_z": float(m.group(5)),
                        "avg_x": float(m.group(6)),
                        "avg_y": float(m.group(7)),
                        "avg_z": float(m.group(8)),
                        "yaw": float(m.group(9)),
                        "dist_xy": float(m.group(10)),
                    }
                )
            m = local_refine_re.search(line)
            if m:
                local_refine_selected.append(
                    {
                        "x": float(m.group(1)),
                        "y": float(m.group(2)),
                        "z": float(m.group(3)),
                        "yaw": float(m.group(4)),
                        "unrefined_first_n": float(m.group(5)),
                        "refined_n": float(m.group(6)),
                    }
                )
            if "[FUEL_COVERAGE_EXPANSION] override" in line:
                coverage_expansion_events["override"] += 1
            elif "[FUEL_COVERAGE_EXPANSION] keep local refine" in line:
                coverage_expansion_events["keep_local_refine"] += 1
            elif "[FUEL_COVERAGE_EXPANSION] span_after" in line:
                coverage_expansion_events["span_after"] += 1
            m = frontier_re.search(line)
            if m:
                frontier_counts.append(float(m.group(1)))
                viewpoint_counts.append(float(m.group(2)))
            m = new_re.search(line)
            if m:
                new_frontiers.append(float(m.group(1)))
                new_dormant.append(float(m.group(2)))
            m = visit_re.search(line)
            if m:
                to_visit.append(float(m.group(1)))
                dormant_total.append(float(m.group(2)))
            m = replan_re.search(line)
            if m:
                replan_reasons[m.group(1).strip()] += 1
            m = fsm_re.search(line)
            if m:
                fsm_transitions[f"{m.group(1)}->{m.group(2)}"] += 1
            if "No coverable frontier" in line:
                no_coverable += 1
            if "No path to next viewpoint" in line or "No path" in line:
                no_path += 1
            if line == "Triggered!":
                trigger_count += 1
            if "Far goal" in line:
                path_modes["far_goal_truncated_to_radius_5m"] += 1
            if "Mid goal" in line:
                path_modes["mid_goal"] += 1
            if "Next viewpoint is very close" in line:
                path_modes["close_goal"] += 1
            if "Next view:" in line:
                nums = [float(x) for x in FLOAT_RE.findall(line)]
                if len(nums) >= 4:
                    next_views.append({"x": nums[0], "y": nums[1], "z": nums[2], "yaw": nums[3]})

    next_view_steps: list[float] = []
    for prev, cur in zip(next_views, next_views[1:]):
        next_view_steps.append(
            math.dist((prev["x"], prev["y"], prev["z"]), (cur["x"], cur["y"], cur["z"]))
        )
    if next_views:
        xs = [v["x"] for v in next_views]
        ys = [v["y"] for v in next_views]
        zs = [v["z"] for v in next_views]
        next_view_summary = {
            "samples": len(next_views),
            "x_min": min(xs),
            "x_max": max(xs),
            "x_range_m": max(xs) - min(xs),
            "y_min": min(ys),
            "y_max": max(ys),
            "y_range_m": max(ys) - min(ys),
            "z_min": min(zs),
            "z_max": max(zs),
            "z_range_m": max(zs) - min(zs),
            "first": next_views[0],
            "last": next_views[-1],
            "step_distance_m": stats(next_view_steps),
        }
    else:
        next_view_summary = {"samples": 0}

    viewpoint_summary: dict[str, Any] = {"samples": len(viewpoint_diag)}
    for key in [
        "clusters",
        "candidates",
        "out_of_box",
        "inflated_occupied",
        "near_unknown",
        "visibility_calls",
        "cells_checked",
        "outside_fov",
        "ray_occupied",
        "ray_unknown",
        "visible_cells",
        "below_min_visib",
        "accepted_viewpoints",
        "max_visib",
        "new_frontiers",
        "new_dormant",
    ]:
        vals = [rec[key] for rec in viewpoint_diag if key in rec]
        viewpoint_summary[key] = stats(vals)
    if viewpoint_diag:
        last = viewpoint_diag[-1]
        candidates = max(1.0, last.get("candidates", 0.0))
        visibility_calls = max(1.0, last.get("visibility_calls", 0.0))
        cells_checked = max(1.0, last.get("cells_checked", 0.0))
        viewpoint_summary["last_ratios"] = {
            "accepted_per_candidate": last.get("accepted_viewpoints", 0.0) / candidates,
            "out_of_box_per_candidate": last.get("out_of_box", 0.0) / candidates,
            "inflated_occupied_per_candidate": last.get("inflated_occupied", 0.0) / candidates,
            "near_unknown_per_candidate": last.get("near_unknown", 0.0) / candidates,
            "below_min_visib_per_visibility_call": last.get("below_min_visib", 0.0) / visibility_calls,
            "outside_fov_per_cell": last.get("outside_fov", 0.0) / cells_checked,
            "ray_occupied_per_cell": last.get("ray_occupied", 0.0) / cells_checked,
            "ray_unknown_per_cell": last.get("ray_unknown", 0.0) / cells_checked,
            "visible_per_cell": last.get("visible_cells", 0.0) / cells_checked,
        }

    cluster_viewpoint_summary: dict[str, Any] = {"samples": len(cluster_viewpoint_diag)}
    for key in [
        "cells",
        "filtered",
        "candidates",
        "accepted",
        "max_visib",
        "below_min_visib",
        "out_of_box",
        "inflated_occupied",
        "near_unknown",
        "visibility_calls",
        "cells_checked",
        "outside_fov",
        "ray_occupied",
        "ray_unknown",
        "visible_cells",
        "min_visib_num",
    ]:
        vals = [rec[key] for rec in cluster_viewpoint_diag if key in rec]
        cluster_viewpoint_summary[key] = stats(vals)
    if cluster_viewpoint_diag:
        zero_accept = [
            rec for rec in cluster_viewpoint_diag if rec.get("accepted", rec.get("accepted_viewpoints", 0.0)) <= 0
        ]
        cluster_viewpoint_summary["zero_accepted_clusters"] = {
            "count": len(zero_accept),
            "ratio": len(zero_accept) / len(cluster_viewpoint_diag),
        }
        latest = cluster_viewpoint_diag[-min(len(cluster_viewpoint_diag), 10):]
        totals = Counter()
        for rec in cluster_viewpoint_diag:
            for key in [
                "out_of_box",
                "inflated_occupied",
                "near_unknown",
                "below_min_visib",
                "outside_fov",
                "ray_occupied",
                "ray_unknown",
            ]:
                totals[key] += rec.get(key, 0.0)
        cluster_viewpoint_summary["rejection_totals"] = dict(totals)
        if totals:
            total_rejections = max(1.0, sum(totals.values()))
            cluster_viewpoint_summary["rejection_ratio"] = {
                key: value / total_rejections for key, value in totals.items()
            }
        cluster_viewpoint_summary["latest"] = latest

    candidate_pool_summary: dict[str, Any] = {"samples": len(candidate_pools)}
    for key in [
        "n",
        "pos_x",
        "pos_y",
        "view_x_min",
        "view_x_max",
        "view_y_min",
        "view_y_max",
        "avg_x_min",
        "avg_x_max",
        "avg_y_min",
        "avg_y_max",
    ]:
        vals = [rec[key] for rec in candidate_pools if key in rec]
        candidate_pool_summary[key] = stats(vals)
    if candidate_pools:
        candidate_pool_summary["last"] = candidate_pools[-1]
        candidate_pool_summary["last_width_m"] = {
            "view_x": candidate_pools[-1]["view_x_max"] - candidate_pools[-1]["view_x_min"],
            "view_y": candidate_pools[-1]["view_y_max"] - candidate_pools[-1]["view_y_min"],
            "avg_x": candidate_pools[-1]["avg_x_max"] - candidate_pools[-1]["avg_x_min"],
            "avg_y": candidate_pools[-1]["avg_y_max"] - candidate_pools[-1]["avg_y_min"],
        }

    return {
        "exists": True,
        "path": str(path),
        "frontier_counts": stats(frontier_counts),
        "viewpoint_counts": stats(viewpoint_counts),
        "new_frontiers": stats(new_frontiers),
        "new_dormant_frontiers": stats(new_dormant),
        "frontiers_to_visit": stats(to_visit),
        "dormant_frontiers_total": stats(dormant_total),
        "next_views": next_view_summary,
        "viewpoint_diag": viewpoint_summary,
        "cluster_viewpoint_diag": cluster_viewpoint_summary,
        "candidate_pool": candidate_pool_summary,
        "global_rank0": {
            "dist_xy": stats([rec["dist_xy"] for rec in global_rank0]),
            "view_bounds": bounds_summary(global_rank0, "view_"),
            "avg_bounds": bounds_summary(global_rank0, "avg_"),
        },
        "local_refine_selected": bounds_summary(local_refine_selected),
        "coverage_expansion_events": dict(coverage_expansion_events),
        "replan_reasons": dict(replan_reasons),
        "fsm_transitions": dict(fsm_transitions),
        "path_modes": dict(path_modes),
        "no_coverable_frontier_count": no_coverable,
        "no_path_count": no_path,
        "trigger_count": trigger_count,
    }


def summarize_supervisor(run_dir: Path) -> dict[str, Any]:
    path = first_existing(
        [
            run_dir / "SUPERVISOR_BEFORE_MANUAL_STOP.json",
            run_dir / "factory_l2_same_flight_coverage_supervisor.json",
        ]
    )
    data = load_json(path) if path else None
    if not data:
        return {"exists": False}

    events = data.get("trigger_events") or []
    event_ratios = [
        as_float(get_path(event, ["coverage", "sensor_footprint_coverage_ratio"]))
        for event in events
    ]
    event_times = [as_float(event.get("elapsed_s", event.get("wall_elapsed_s"))) for event in events]
    growth_segments = []
    for idx in range(1, len(event_ratios)):
        if math.isnan(event_ratios[idx]) or math.isnan(event_ratios[idx - 1]):
            continue
        dt = event_times[idx] - event_times[idx - 1]
        if dt <= 0 or math.isnan(dt):
            continue
        growth_segments.append(
            {
                "from_event": idx - 1,
                "to_event": idx,
                "delta_ratio": event_ratios[idx] - event_ratios[idx - 1],
                "dt_s": dt,
                "ratio_per_min": (event_ratios[idx] - event_ratios[idx - 1]) * 60.0 / dt,
            }
        )

    reason_counts = Counter(str(event.get("reason", "unknown")) for event in events)
    coverage = get_path(data, ["acceptance", "coverage"], {}) or {}
    return {
        "exists": True,
        "path": str(path),
        "status": data.get("status"),
        "elapsed_s": data.get("elapsed_s"),
        "wall_elapsed_s": data.get("wall_elapsed_s"),
        "time_basis": data.get("time_basis"),
        "coverage": coverage,
        "coverage_percent": as_percent(coverage.get("sensor_footprint_coverage_ratio")),
        "counts": data.get("counts", {}),
        "last_seen_age_s": data.get("last_seen_age_s", {}),
        "trigger_event_count": len(events),
        "trigger_reason_counts": dict(reason_counts),
        "trigger_event_coverage_ratio": stats([v for v in event_ratios if not math.isnan(v)]),
        "growth_segments": growth_segments,
        "growth_ratio_per_min": stats([seg["ratio_per_min"] for seg in growth_segments]),
    }


def summarize_coverage(path: Path | None) -> dict[str, Any]:
    data = load_json(path) if path else None
    if not data:
        return {"exists": False}
    acceptance = data.get("acceptance", {})
    runs = data.get("runs", [])
    eligible_run_count = acceptance.get("eligible_run_count")
    merged_sensor_percent = as_percent(
        acceptance.get("merged_sensor_footprint_coverage_ratio")
    )
    best_single_sensor_percent = as_percent(
        acceptance.get("best_single_run_sensor_footprint_coverage_ratio")
    )
    analysis_sensor_percent = (
        merged_sensor_percent
        if as_float(eligible_run_count, 0.0) > 0.0
        else best_single_sensor_percent
    )
    return {
        "exists": True,
        "path": str(path),
        "status": data.get("status"),
        "min_required_ratio": acceptance.get("min_sensor_footprint_coverage_ratio"),
        "merged_sensor_ratio": acceptance.get("merged_sensor_footprint_coverage_ratio"),
        "merged_sensor_percent": merged_sensor_percent,
        "merged_path_ratio": acceptance.get("merged_path_coverage_ratio"),
        "best_single_sensor_ratio": acceptance.get("best_single_run_sensor_footprint_coverage_ratio"),
        "best_single_sensor_percent": best_single_sensor_percent,
        "analysis_sensor_percent": analysis_sensor_percent,
        "analysis_sensor_source": (
            "merged_eligible_runs"
            if as_float(eligible_run_count, 0.0) > 0.0
            else "best_single_diagnostic"
        ),
        "eligible_run_count": eligible_run_count,
        "excluded_run_count": acceptance.get("excluded_run_count"),
        "blockers": acceptance.get("blockers", []),
        "run_truth_bounds": get_path(runs[0], ["truth", "bounds"], {}) if runs else {},
        "cloud_bounds_proxy": get_path(runs[0], ["cloud_bounds_proxy"], {}) if runs else {},
    }


def summarize_run(run_dir: Path) -> dict[str, Any]:
    metrics = load_json(run_dir / "EGO_SINGLE_METRICS.json") or {}
    probe = load_json(run_dir / "FACTORY_L2_FUEL_SAME_FLIGHT_COVERAGE_PROBE.json") or {}
    coverage = summarize_coverage(find_coverage_packet(run_dir))
    supervisor = summarize_supervisor(run_dir)
    log_summary = parse_fuel_log(run_dir / "ego_single_px4ctrl_goal4.log")

    truth_rows = rows_for_phase(load_csv(run_dir / "truth.csv"), "exploration_execute")
    odom_rows = rows_for_phase(load_csv(run_dir / "odom.csv"), "exploration_execute")
    position_cmd_rows = rows_for_phase(load_csv(run_dir / "position_cmd.csv"), "exploration_execute")

    return {
        "run_dir": str(run_dir),
        "exists": run_dir.exists(),
        "probe_status": probe.get("status"),
        "metrics_status": metrics.get("status"),
        "metrics_blockers": metrics.get("blockers", []),
        "counts": metrics.get("counts", supervisor.get("counts", {})),
        "parameters": probe.get("parameters", {}),
        "boundary": probe.get("boundary", get_path(coverage, ["envelope", "boundary"], {})),
        "coverage": coverage,
        "supervisor": supervisor,
        "exploration": metrics.get("exploration", {}),
        "position_cmd_adapter": metrics.get("position_cmd_safety_adapter", {}),
        "motion": {
            "truth_span": span(truth_rows),
            "odom_span": span(odom_rows),
            "position_cmd_span": span(position_cmd_rows),
            "truth_speed": speed_summary(truth_rows),
            "odom_speed": speed_summary(odom_rows),
        },
        "fuel_log": log_summary,
    }


def build_packet(runs: list[Path]) -> dict[str, Any]:
    run_summaries = [summarize_run(run) for run in runs]
    latest = run_summaries[0] if run_summaries else {}
    valid_coverages = [
        as_float(get_path(run, ["coverage", "analysis_sensor_percent"]))
        for run in run_summaries
        if not math.isnan(as_float(get_path(run, ["coverage", "analysis_sensor_percent"])))
    ]
    valid_supervisor_coverages = [
        as_float(get_path(run, ["supervisor", "coverage_percent"]))
        for run in run_summaries
        if not math.isnan(as_float(get_path(run, ["supervisor", "coverage_percent"])))
    ]
    best_coverage_percent = max(valid_coverages) if valid_coverages else None
    best_supervisor_coverage_percent = (
        max(valid_supervisor_coverages) if valid_supervisor_coverages else None
    )
    latest_coverage_percent = get_path(latest, ["coverage", "analysis_sensor_percent"])
    baseline_for_gate = (
        best_coverage_percent
        if best_coverage_percent is not None
        else latest_coverage_percent
    )
    baseline_for_gate = 0.0 if baseline_for_gate is None else baseline_for_gate
    latest_coverage_text = (
        "unavailable" if latest_coverage_percent is None else f"{latest_coverage_percent:.2f}%"
    )
    best_coverage_text = (
        "unavailable" if best_coverage_percent is None else f"{best_coverage_percent:.2f}%"
    )

    packet = {
        "schema": "mosim.factory_l2.fuel_source_level_diagnosis.v2",
        "status": "diagnosis_complete",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "scope": {
            "mainline": "FUEL only; HighStar and Diff target-chain are not used as autonomous-exploration proof.",
            "evidence_surface": "offline source/log/result packet; no live ROS/Gazebo/RViz launched by this script.",
            "acceptance_target_sensor_coverage_ratio": 0.8,
        },
        "runs": run_summaries,
        "source_audit": {
            "frontier_search": {
                "file": "References/Lab/exploration_coverage/FUEL/fuel_planner/active_perception/src/frontier_finder.cpp",
                "finding": "searchFrontiers scans only the updated SDF map box inflated by (1,1,0.5) and clipped to getBox(); new frontier discovery is therefore local to sensor/map updates.",
            },
            "viewpoint_filter": {
                "file": "References/Lab/exploration_coverage/FUEL/fuel_planner/active_perception/src/frontier_finder.cpp",
                "finding": "sampleViewpoints rejects candidates outside box, in inflated occupancy, near unknown, or below min_visib_num after FOV/raycast checks.",
            },
            "unknown_ray_policy": {
                "file": "References/Lab/exploration_coverage/FUEL/fuel_planner/active_perception/src/frontier_finder.cpp",
                "finding": "countVisibleCells marks a candidate invisible if a ray crosses inflated occupancy or UNKNOWN, which is harsh for MID360 point-cloud frontiers and sparse/incremental maps.",
            },
            "far_goal_policy": {
                "file": "References/Lab/exploration_coverage/FUEL/fuel_planner/exploration_manager/src/fast_exploration_manager.cpp",
                "finding": "when the path to the selected viewpoint is longer than radius_far=5.0m, FUEL truncates the path and only plans to an intermediate goal.",
            },
        },
        "upstream_research": [
            {
                "source": "FUEL README",
                "url": "https://github.com/HKUST-Aerial-Robotics/FUEL/blob/main/README.md",
                "relevance": "Official demos use depth-camera style simulation and small office/pillar PCD maps; custom maps require changing explored-space bounding box in exploration.launch.",
            },
            {
                "source": "FUEL issue #22",
                "url": "https://github.com/HKUST-Aerial-Robotics/FUEL/issues/22",
                "relevance": "Reports No coverable frontier after RViz trigger; matches the failure mode to track but our latest runs are not pure no-frontier startup failures.",
            },
            {
                "source": "FUEL issue #37",
                "url": "https://github.com/HKUST-Aerial-Robotics/FUEL/issues/37",
                "relevance": "Different simulator with valid depth/odom/map can still fail frontier clustering or build clusters only after small movement; aligns with source-level frontier/update-box sensitivity.",
            },
            {
                "source": "FUEL issue #90",
                "url": "https://github.com/HKUST-Aerial-Robotics/FUEL/issues/90",
                "relevance": "MID360/FAST-LIO global point-cloud input causes strange frontiers; directly relevant to MoSim using MID360 point cloud instead of the original depth topic path.",
            },
        ],
        "diagnosis": {
            "latest_valid_sensor_coverage_percent": latest_coverage_percent,
            "best_valid_sensor_coverage_percent": best_coverage_percent,
            "best_supervisor_sensor_coverage_percent": best_supervisor_coverage_percent,
            "key_findings": [
                "FUEL is not startup-dead: latest run has nonempty bspline, planner_position_cmd, position_cmd, world_cloud, and internal frontier/viewpoint logs.",
                "Coverage remains below the 80% acceptance target: latest input run reports "
                f"{latest_coverage_text} analysis sensor-footprint coverage; best input run reports "
                f"{best_coverage_text}. Blocked runs use best-single diagnostic coverage and are "
                "not promoted to merged acceptance.",
                "The old 16m-local-window diagnosis is stale for the latest run: latest parameters use the full Factory indoor box, so remaining failure is not just a too-small map box.",
                "The FUEL source is local-update/frontier/viewpoint driven, not a global coverage optimizer. It can follow a narrow frontier strip and plateau even while command streams remain alive.",
                "MID360 point-cloud input is a plausible stressor because FUEL viewpoint visibility is FOV/raycast/unknown sensitive and upstream users report strange frontiers with MID360/FAST-LIO cloud input.",
            ],
            "not_supported_by_evidence": [
                "Do not claim FUEL autonomous full coverage from the Diff known-target chain that reached 80.50%.",
                "Do not treat HighStar as the current answer; it is outside this FUEL mainline goal.",
                "Do not run another long FUEL attempt until a short source-level diagnostic shows changed frontier/viewpoint or coverage-growth behavior.",
            ],
        },
        "execution_decision": {
            "current": "stop_single_uav_fuel_parameter_tuning",
            "next": "port reusable MID360/frame/Hybrid-Z and recovery evidence gates to bounded RACER multi-UAV validation",
            "reopen_condition": "Run the deferred FUEL source experiments only if the user explicitly reopens this lane.",
        },
        "next_minimal_fuel_fixes": [
            {
                "id": "FUEL-DIAG-1",
                "change": "Add temporary FUEL logging around sampleViewpoints/countVisibleCells to count rejection causes: out_of_box, inflated_occupied, near_unknown, below_min_visib_num, outside_fov, ray_unknown, ray_occupied.",
                "why": "Current logs tell how many frontiers/viewpoints survive, not why candidates are discarded or become dormant.",
                "gate": f"Build only, then 60-120s no-RViz Factory run; compare rejection histogram and coverage percent against current best {baseline_for_gate:.2f}%."
            },
            {
                "id": "FUEL-LIDAR-1",
                "change": "Test one bounded LiDAR-compatible visibility relaxation after DIAG-1: reduce/disable near-unknown rejection or allow UNKNOWN along ray for frontier visibility, guarded by inflated-occupancy safety.",
                "why": "MID360 point-cloud frontiers are more ring/sparse than depth-camera frontiers; the current UNKNOWN-as-invisible rule can starve viewpoints.",
                "gate": "60-120s run must increase frontier/viewpoint survival and coverage growth without planner safety blockers."
            },
            {
                "id": "FUEL-GLOBAL-1",
                "change": "If viewpoint survival is healthy but next_views stay in a narrow band, add a coverage-gain or boundary-expansion tie-breaker before TSP/local refine instead of only nearest/low-cost viewpoint selection.",
                "why": "The long run keeps moving but expands too slowly; this points to objective/ranking, not startup.",
                "gate": "Short run next_view and truth spans must expand in both Factory axes, then promote to a bounded 5-min run."
            },
        ],
    }
    return packet


def write_summary(packet: dict[str, Any], out_dir: Path) -> None:
    lines = [
        "# Factory L2 FUEL Source-Level Diagnosis",
        "",
        f"- status: `{packet['status']}`",
        f"- generated_at: `{packet['generated_at']}`",
        f"- scope: {packet['scope']['mainline']}",
        "",
        "## Coverage",
        "",
    ]
    for run in packet["runs"]:
        cov = run.get("coverage", {})
        sup = run.get("supervisor", {})
        lines.append(f"- `{run['run_dir']}`")
        lines.append(f"  - metrics_status: `{run.get('metrics_status')}`; probe_status: `{run.get('probe_status')}`")
        lines.append(
            f"  - analysis coverage: `{cov.get('analysis_sensor_percent')}` percent "
            f"(`{cov.get('analysis_sensor_source')}`); merged eligible coverage: "
            f"`{cov.get('merged_sensor_percent')}` percent; status: `{cov.get('status')}`"
        )
        lines.append(f"  - supervisor coverage: `{sup.get('coverage_percent')}` percent; trigger_events: `{sup.get('trigger_event_count')}`")
        lines.append(f"  - counts: `{run.get('counts')}`")
        lines.append(f"  - next_view span: `{run.get('fuel_log', {}).get('next_views')}`")
    lines.extend(["", "## Diagnosis", ""])
    for item in packet["diagnosis"]["key_findings"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Upstream Research", ""])
    for item in packet["upstream_research"]:
        lines.append(f"- [{item['source']}]({item['url']}): {item['relevance']}")
    decision = packet["execution_decision"]
    lines.extend(
        [
            "",
            "## Execution Decision",
            "",
            f"- current: `{decision['current']}`",
            f"- next: `{decision['next']}`",
            f"- reopen condition: {decision['reopen_condition']}",
            "",
            "## Deferred FUEL Fixes If Reopened",
            "",
        ]
    )
    for item in packet["next_minimal_fuel_fixes"]:
        lines.append(f"- `{item['id']}`: {item['change']} Gate: {item['gate']}")
    lines.extend(["", "## Not Claimed", ""])
    for item in packet["diagnosis"]["not_supported_by_evidence"]:
        lines.append(f"- {item}")
    lines.append("")
    (out_dir / "SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", action="append", type=Path, help="FUEL result directory. Can be repeated.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    runs = args.run_dir if args.run_dir else DEFAULT_RUNS
    args.out_dir.mkdir(parents=True, exist_ok=True)
    packet = build_packet(runs)
    packet_path = args.out_dir / "FACTORY_L2_FUEL_SOURCE_LEVEL_DIAGNOSIS.json"
    packet_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False), encoding="utf-8")
    write_summary(packet, args.out_dir)
    print(packet_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
