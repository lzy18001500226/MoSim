#!/usr/bin/env python3
"""Build a HighStar-specific single-UAV exploration evidence packet.

The generic EGO/FUEL metrics file is still useful for vehicle safety and topic
counts, but it can misclassify HighStar because HighStar publishes trajectory
and map evidence on `/Murder/Traj`, `/Murder/Show`, `/Frontier/grid`, and
`/block_map/cloud`/`/murder_demo/block_map/voxvis`. This reducer keeps those
signals explicit so a HighStar run is not judged by FUEL bspline fields.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


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
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return default
    return out if math.isfinite(out) else default


def load_csv(path: Path) -> list[dict[str, Any]]:
    if not path.is_file() or path.stat().st_size == 0:
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


def phase_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = [row for row in rows if row.get("phase") in {"exploration_execute", "ego_execute"}]
    return selected or rows


def span(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"samples": 0}
    xs = [as_float(row.get("x")) for row in rows]
    ys = [as_float(row.get("y")) for row in rows]
    zs = [as_float(row.get("z")) for row in rows]
    start = rows[0]
    end = rows[-1]
    dx = as_float(end.get("x")) - as_float(start.get("x"))
    dy = as_float(end.get("y")) - as_float(start.get("y"))
    dz = as_float(end.get("z")) - as_float(start.get("z"))
    ts = [as_float(row.get("t"), math.nan) for row in rows if math.isfinite(as_float(row.get("t"), math.nan))]
    wall = [
        as_float(row.get("wall_elapsed_s"), math.nan)
        for row in rows
        if math.isfinite(as_float(row.get("wall_elapsed_s"), math.nan))
    ]
    return {
        "samples": len(rows),
        "x_range_m": max(xs) - min(xs),
        "y_range_m": max(ys) - min(ys),
        "z_range_m": max(zs) - min(zs),
        "xy_range_area_m2": (max(xs) - min(xs)) * (max(ys) - min(ys)),
        "start_xyz": [as_float(start.get("x")), as_float(start.get("y")), as_float(start.get("z"))],
        "end_xyz": [as_float(end.get("x")), as_float(end.get("y")), as_float(end.get("z"))],
        "start_to_end_xy_m": math.hypot(dx, dy),
        "start_to_end_xyz_m": math.sqrt(dx * dx + dy * dy + dz * dz),
        "sim_duration_s": (max(ts) - min(ts)) if len(ts) >= 2 else None,
        "wall_duration_s": (max(wall) - min(wall)) if len(wall) >= 2 else None,
    }


def path_length_xy(rows: list[dict[str, Any]]) -> float:
    total = 0.0
    last: tuple[float, float] | None = None
    for row in rows:
        cur = (as_float(row.get("x")), as_float(row.get("y")))
        if last is not None:
            total += math.hypot(cur[0] - last[0], cur[1] - last[1])
        last = cur
    return total


def parse_log(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8", errors="ignore")
    return {
        "local_plan_enter_count": len(re.findall(r"HighStar LocalPlan enter", text)),
        "target_result_count": len(re.findall(r"HighStar LocalPlan target result", text)),
        "traj_plan_fail_count": len(re.findall(r"TrajPlanB fail|opt failed", text)),
        "optimization_failed_count": len(re.findall(r"Optimization Failed", text)),
        "inf_count": len(re.findall(r"\binf\b", text)),
        "fsm_done": "HighStar Murder::init stage=done" in text,
        "frontier_grid_done": "HighStar Murder::init stage=frontier_grid_done" in text,
        "lowres_stats_samples": len(re.findall(r"lowres_obstacle_stats", text)),
        "execute_transition_count": len(re.findall(r"to .*\bEXCUTE\b", text)),
    }


def build_packet(run_dir: Path, output: Path | None = None) -> dict[str, Any]:
    metrics = load_json(run_dir / "EGO_SINGLE_METRICS.json")
    bridge = load_json(run_dir / "highstar_swarmtraj_position_cmd_bridge.json")
    safety = load_json(run_dir / "position_cmd_safety_adapter.json")
    world_stats = load_json(run_dir / "pointcloud_to_world_stats.json")
    accum = load_json(run_dir / "livox_world_accumulated_review.json")
    manifest = load_json(run_dir / "RUN_MANIFEST.json")
    truth = phase_rows(load_csv(run_dir / "truth.csv"))
    odom = phase_rows(load_csv(run_dir / "odom.csv"))
    raw_cmd = phase_rows(load_csv(run_dir / "planner_position_cmd_raw.csv"))
    safe_cmd = phase_rows(load_csv(run_dir / "position_cmd.csv"))
    log = parse_log(run_dir / "ego_single_px4ctrl_goal4.log")

    blockers: list[str] = []
    if as_float(bridge.get("input_count")) <= 0:
        blockers.append("highstar_traj_missing")
    if as_float(safety.get("raw_count")) <= 0:
        blockers.append("highstar_raw_cmd_missing")
    if as_float(safety.get("published_count")) <= 0:
        blockers.append("position_cmd_missing")
    if len(truth) <= 1 or path_length_xy(truth) < 0.5:
        blockers.append("truth_motion_too_small")
    if log.get("traj_plan_fail_count", 0) > max(20, as_float(bridge.get("input_count")) * 2):
        blockers.append("optimizer_failures_excessive")
    if not log.get("fsm_done"):
        blockers.append("highstar_init_not_confirmed")

    packet = {
        "schema": "mosim.sunray_ros1.highstar_single_exploration_packet.v1",
        "created_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "run_dir": rel(run_dir),
        "status": "passed_command_stream" if not blockers else "review_required",
        "blockers": blockers,
        "classification": (
            "HighStar closed-loop command-stream evidence; not full Factory unknown-coverage proof"
            if not blockers
            else "HighStar evidence needs review before promotion"
        ),
        "generic_metrics_status": metrics.get("status"),
        "generic_metrics_blockers": metrics.get("blockers", []),
        "planner": manifest.get("planner"),
        "world_file": manifest.get("world_file"),
        "highstar_topics": {
            "traj_input": bridge.get("input_topic"),
            "raw_cmd": bridge.get("output_topic"),
            "preview_marker": bridge.get("marker_topic"),
            "frontier": "/Frontier/grid",
            "trajectory_vis": "/Murder/Show",
            "block_map": manifest.get("topics", {}).get("occupancy_inflate") or "/block_map/cloud",
        },
        "bridge": {
            "input_count": bridge.get("input_count", 0),
            "accepted_count": bridge.get("accepted_count", 0),
            "published_count": bridge.get("published_count", 0),
            "last_reject_reason": bridge.get("last_reject_reason"),
            "last_msg_summary": bridge.get("last_msg_summary"),
        },
        "safety_adapter": {
            "raw_count": safety.get("raw_count", 0),
            "published_count": safety.get("published_count", 0),
            "clamped_high_count": safety.get("clamped_high_count", 0),
            "jump_rejected_count": safety.get("jump_rejected_count", 0),
            "max_published_jump_m": safety.get("max_published_jump_m"),
            "max_published_jump_speed_mps": safety.get("max_published_jump_speed_mps"),
            "max_observed_target_distance_from_odom_m": safety.get("max_observed_target_distance_from_odom_m"),
        },
        "motion": {
            "truth_path_length_xy_m": path_length_xy(truth),
            "odom_path_length_xy_m": path_length_xy(odom),
            "raw_cmd_path_length_xy_m": path_length_xy(raw_cmd),
            "safe_cmd_path_length_xy_m": path_length_xy(safe_cmd),
            "truth_span": span(truth),
            "odom_span": span(odom),
            "raw_cmd_span": span(raw_cmd),
            "safe_cmd_span": span(safe_cmd),
        },
        "map_and_cloud": {
            "raw_lidar_count": metrics.get("counts", {}).get("raw_lidar"),
            "world_cloud_count": metrics.get("counts", {}).get("world_cloud"),
            "frontier_count": metrics.get("counts", {}).get("frontier"),
            "trajectory_vis_count": metrics.get("counts", {}).get("trajectory_vis"),
            "occupancy_count_generic": metrics.get("counts", {}).get("occupancy_inflate"),
            "pointcloud_to_world": {
                "published_clouds": world_stats.get("published_clouds"),
                "published_points": world_stats.get("published_points"),
                "world_bounds": world_stats.get("world_bounds"),
                "reject_reason": world_stats.get("reject_reason"),
            },
            "accumulated_review": {
                "received": accum.get("received"),
                "published": accum.get("published"),
                "accumulated_voxels": (accum.get("last_stats") or {}).get("accumulated_voxels"),
                "quality_gate_counts": accum.get("quality_gate_counts"),
            },
        },
        "highstar_log": log,
        "claim_boundary": [
            "This packet may prove HighStar runtime command-stream integration.",
            "It does not prove Factory full-indoor autonomous coverage unless a separate coverage packet passes.",
            "Generic EGO occupancy/bspline blockers are reported but are not the HighStar primary acceptance fields.",
        ],
    }
    out_path = output or (run_dir / "HIGHSTAR_SINGLE_EXPLORATION_PACKET.json")
    out_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return packet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir")
    parser.add_argument("--output")
    args = parser.parse_args()
    run_dir = repo_path(args.run_dir)
    output = repo_path(args.output) if args.output else None
    packet = build_packet(run_dir, output)
    print(json.dumps({"status": packet["status"], "blockers": packet["blockers"], "run_dir": packet["run_dir"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
