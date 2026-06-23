#!/usr/bin/env python3
"""Build a report-ready single-UAV evidence bundle from existing artifacts.

The bundle is an index and visualization aid. It does not start MWORKS, UE,
ROS2, Gazebo, RViz, FAST-LIO, planners, sockets, or GUI actions.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.ros.pointcloud_to_local_voxel_map_ros2 import (  # noqa: E402
    LocalMapConfig,
    voxel_center,
    voxelize_points,
)


DEFAULT_OUTPUT_DIR = ROOT / "Results/gazebo_ros2/single_uav_evidence_bundle_20260615"
SCENES = ("factoryenvironmentcollect", "derelictcorridormegascans")

REQUIRED_BOUNDARY = [
    "This bundle is a report/evidence index built from existing artifacts only.",
    "It does not start or rerun MWORKS, UE, ROS2, Gazebo, RViz, FAST-LIO, planners, sockets, or GUI actions.",
    "It does not prove planner_ready, trajectory tracking, final closed_loop acceptance, competition controller performance from UE/Gazebo, final material acceptance, or multi-UAV readiness.",
    "MWORKS metrics remain the current competition controller-performance source; Gazebo/ROS2 gates are system-validation evidence.",
]


def repo_path(value: str | Path) -> Path:
    raw = Path(value)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {value}")
    return resolved


def rel(path: str | Path) -> str:
    value = Path(path)
    try:
        return value.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return value.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {rel(path)}")
    return data


def read_json_if_exists(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return read_json(path)


def read_jsonl(path: Path, *, limit: int | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        if isinstance(data, dict):
            rows.append(data)
        if limit is not None and len(rows) >= limit:
            break
    return rows


def read_json_from_text(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Single-UAV Evidence Bundle",
        "",
        f"- status: `{report['status']}`",
        f"- generated_at: `{report['generated_at']}`",
        f"- output_dir: `{report['output_dir']}`",
        f"- subagent_plan: `{report['subagent_plan']['decision']}`",
        f"- subagent_plan_reason: `{report['subagent_plan']['reason']}`",
        "",
        "## Gate Summary",
        "",
        "| Gate | Evidence State | Current Status | Current Pass | Prior Pass | Primary Artifact | Notes |",
        "|---|---|---|---:|---:|---|---|",
    ]
    for gate in report["gates"]:
        lines.append(
            "| "
            f"`{gate['gate_id']}` | "
            f"`{gate['evidence_state']}` | "
            f"`{gate.get('current_status', '')}` | "
            f"`{str(gate.get('current_gate_passed', False)).lower()}` | "
            f"`{str(gate.get('prior_gate_passed', False)).lower()}` | "
            f"`{gate['primary_artifact']}` | "
            f"{gate.get('summary', '')} |"
        )

    mworks = report["mworks_summary"]
    lines.extend(
        [
            "",
            "## MWORKS Current Candidate",
            "",
            f"- closeout_status: `{mworks.get('status', '')}`",
            f"- batch_acceptance: `{mworks.get('batch_acceptance_status', '')}`",
            f"- accepted_result_count: `{mworks.get('accepted_result_count', '')}`",
            f"- needs_iteration_count: `{mworks.get('needs_iteration_count', '')}`",
            f"- best_candidate: `{mworks.get('best_candidate_controller_id', '')}`",
            f"- current_rerun_state: `{mworks.get('current_rerun_state', '')}`",
            f"- position_rmse_m: `{mworks.get('position_rmse_m', '')}`",
            f"- total_health_score: `{mworks.get('total_health_score', '')}`",
            "",
            "## Visual Previews",
            "",
            "| Scene/Signal | Kind | Output | Source | Claim Boundary |",
            "|---|---|---|---|---|",
        ]
    )
    for visual in report["visuals"]:
        lines.append(
            "| "
            f"`{visual['id']}` | "
            f"`{visual['kind']}` | "
            f"`{visual['path']}` | "
            f"`{visual['source']}` | "
            f"{visual['claim_boundary']} |"
        )

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            *[f"- {item}" for item in report["claim_boundary"]],
            "",
            "## Next Actions",
            "",
            *[f"- {item}" for item in report["next_actions"]],
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def gate_from_runtime_status(
    gate_id: str,
    runtime_status_path: Path,
    *,
    prior_log_path: Path | None = None,
    summary: str = "",
    selected_artifact_policy: str = "explicit_path",
) -> dict[str, Any]:
    current = read_json_if_exists(runtime_status_path)
    prior = read_json_from_text(prior_log_path) if prior_log_path else None
    current_passed = bool(current and current.get("gate_passed") is True)
    prior_passed = bool(prior and prior.get("gate_passed") is True)
    current_status = str(current.get("status", "missing")) if current else "missing"

    if current_passed:
        evidence_state = "current_runtime_status_passed"
    elif prior_passed:
        evidence_state = "drift_detected_prior_pass_log_available"
    elif current:
        evidence_state = "current_runtime_status_not_passed"
    else:
        evidence_state = "missing_runtime_status"

    return {
        "gate_id": gate_id,
        "primary_artifact": rel(runtime_status_path),
        "prior_artifact": rel(prior_log_path) if prior_log_path else None,
        "evidence_state": evidence_state,
        "current_status": current_status,
        "current_gate_passed": current_passed,
        "prior_status": str(prior.get("status", "")) if prior else "",
        "prior_gate_passed": prior_passed,
        "gate_profile": str((current or prior or {}).get("gate_profile", "")),
        "blockers": (current or {}).get("blockers", []),
        "warnings": (current or {}).get("warnings", []),
        "summary": summary,
        "selected_artifact_policy": selected_artifact_policy,
        "claim_boundary": (current or prior or {}).get("claim_boundary", []),
    }


def gate_from_json(
    gate_id: str,
    path: Path,
    *,
    status_field: str = "status",
    pass_field: str = "gate_passed",
    summary: str = "",
) -> dict[str, Any]:
    data = read_json_if_exists(path)
    gate_passed = bool(data and nested_value(data, pass_field) is True)
    status_value = nested_value(data, status_field) if data else None
    status = str(status_value if status_value is not None else "missing")
    return {
        "gate_id": gate_id,
        "primary_artifact": rel(path),
        "evidence_state": "current_json_passed" if gate_passed else "current_json_not_passed_or_missing",
        "current_status": status,
        "current_gate_passed": gate_passed,
        "prior_status": "",
        "prior_gate_passed": False,
        "gate_profile": str(data.get("gate_profile", "")) if data else "",
        "blockers": data.get("blockers", []) if data else [],
        "warnings": data.get("warnings", []) if data else [],
        "summary": summary,
        "claim_boundary": data.get("claim_boundary", []) if data else [],
    }


def nested_value(data: dict[str, Any] | None, dotted_key: str) -> Any:
    if data is None:
        return None
    current: Any = data
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def latest_passed_runtime_status(
    gazebo_root: Path,
    pattern: str,
    *,
    gate_profile: str | None = None,
) -> Path | None:
    candidates: list[Path] = []
    for path in gazebo_root.glob(pattern):
        try:
            data = read_json(path)
        except (OSError, json.JSONDecodeError, ValueError):
            continue
        if data.get("gate_passed") is not True:
            continue
        if gate_profile is not None and data.get("gate_profile") != gate_profile:
            continue
        candidates.append(path)
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: item.parent.name, reverse=True)[0]


def latest_passed_runtime_status_any(
    gazebo_root: Path,
    patterns: list[str],
    *,
    gate_profile: str | None = None,
) -> Path | None:
    candidates = [
        path
        for pattern in patterns
        for path in [latest_passed_runtime_status(gazebo_root, pattern, gate_profile=gate_profile)]
        if path is not None
    ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda item: item.parent.name, reverse=True)[0]


def latest_passed_map_review(gazebo_root: Path, patterns: list[str]) -> Path | None:
    for pattern in patterns:
        candidates: list[Path] = []
        for path in gazebo_root.glob(pattern):
            try:
                data = read_json(path)
            except (OSError, json.JSONDecodeError, ValueError):
                continue
            if data.get("gate_passed") is not True:
                continue
            candidates.append(path)
        if candidates:
            return sorted(candidates, key=lambda item: item.parents[1].name, reverse=True)[0]
    return None


def read_ascii_ply_vertices(path: Path) -> list[tuple[float, float, float]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    vertex_count = 0
    header_end = None
    for index, line in enumerate(lines):
        if line.startswith("element vertex"):
            parts = line.split()
            if len(parts) >= 3:
                vertex_count = int(parts[2])
        if line.strip() == "end_header":
            header_end = index + 1
            break
    if header_end is None:
        return []
    vertices: list[tuple[float, float, float]] = []
    for line in lines[header_end : header_end + vertex_count]:
        parts = line.split()
        if len(parts) < 3:
            continue
        try:
            x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
        except ValueError:
            continue
        vertices.append((x, y, z))
    return vertices


def finite_points(points: list[tuple[float, float, float]]) -> list[tuple[float, float, float]]:
    return [p for p in points if all(math.isfinite(v) for v in p)]


def import_matplotlib() -> Any:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def set_axes_equal(ax: Any, xs: list[float], ys: list[float], zs: list[float]) -> None:
    if not xs or not ys or not zs:
        return
    ranges = [max(values) - min(values) for values in (xs, ys, zs)]
    radius = max(max(ranges) / 2.0, 0.5)
    centers = [(max(values) + min(values)) / 2.0 for values in (xs, ys, zs)]
    ax.set_xlim(centers[0] - radius, centers[0] + radius)
    ax.set_ylim(centers[1] - radius, centers[1] + radius)
    ax.set_zlim(centers[2] - radius, centers[2] + radius)


def plot_point_cloud(path: Path, points: list[tuple[float, float, float]], title: str) -> None:
    plt = import_matplotlib()
    path.parent.mkdir(parents=True, exist_ok=True)
    points = finite_points(points)
    fig = plt.figure(figsize=(8, 6), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    if points:
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        zs = [p[2] for p in points]
        ax.scatter(xs, ys, zs, c=zs, cmap="viridis", s=4, alpha=0.75)
        set_axes_equal(ax, xs, ys, zs)
    ax.set_title(title)
    ax.set_xlabel("x m")
    ax.set_ylabel("y m")
    ax.set_zlabel("z m")
    ax.view_init(elev=32, azim=-58)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_grid(path: Path, grid: dict[str, Any], title: str) -> None:
    import numpy as np
    from matplotlib.colors import ListedColormap

    plt = import_matplotlib()
    width = int(grid.get("width", 0))
    height = int(grid.get("height", 0))
    data = grid.get("data", [])
    path.parent.mkdir(parents=True, exist_ok=True)
    if width <= 0 or height <= 0 or not isinstance(data, list) or len(data) != width * height:
        array = np.zeros((1, 1), dtype=int)
    else:
        array = np.array(data, dtype=int).reshape((height, width))
    display = np.zeros_like(array, dtype=int)
    display[array == -1] = 0
    display[array == 0] = 1
    display[array == 100] = 2
    fig, ax = plt.subplots(figsize=(6, 6), dpi=140)
    ax.imshow(display, origin="lower", cmap=ListedColormap(["#d8dde6", "#f8fafc", "#c44536"]))
    ax.set_title(title)
    ax.set_xlabel("grid x")
    ax.set_ylabel("grid y")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def local_points_from_ue_world(points_m: list[list[float]], origin_m: list[float]) -> list[tuple[float, float, float]]:
    ox, oy, oz = float(origin_m[0]), float(origin_m[1]), float(origin_m[2])
    local_points: list[tuple[float, float, float]] = []
    for item in points_m:
        if isinstance(item, list) and len(item) == 3:
            local_points.append((float(item[0]) - ox, float(item[1]) - oy, float(item[2]) - oz))
    return local_points


def first_jsonl_by_seq(path: Path) -> dict[int, dict[str, Any]]:
    rows = read_jsonl(path)
    result: dict[int, dict[str, Any]] = {}
    for row in rows:
        if "seq" in row:
            result[int(row["seq"])] = row
    return result


def build_voxel_preview(scene_id: str, output_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    fixture_path = (
        ROOT
        / "Results/gazebo_ros2/offline_ue_truth_local_voxel_map_fixture"
        / scene_id
        / "local_voxel_map_fixture_frames.jsonl"
    )
    lidar_path = ROOT / "Results/unreal_scene_mapping" / scene_id / "lidar_point_frames.jsonl"
    local_map_path = ROOT / "Results/unreal_scene_mapping" / scene_id / "local_known_map_frames.jsonl"
    fixture_rows = read_jsonl(fixture_path, limit=1)
    if not fixture_rows:
        raise ValueError(f"missing fixture frame: {rel(fixture_path)}")
    frame = fixture_rows[0]
    seq = int(frame["seq"])
    lidar_frame = first_jsonl_by_seq(lidar_path).get(seq)
    local_map_frame = first_jsonl_by_seq(local_map_path).get(seq)
    if lidar_frame is None or local_map_frame is None:
        raise ValueError(f"missing matching lidar/local frame for {scene_id} seq={seq}")

    points_m = lidar_frame.get("points_m", [])
    origin_m = local_map_frame.get("origin_m", [])
    config_payload = frame.get("config", {})
    config = LocalMapConfig(
        voxel_size_m=float(config_payload.get("voxel_size_m", 0.2)),
        grid_resolution_m=float(config_payload.get("grid_resolution_m", 0.2)),
        local_radius_m=float(config_payload.get("local_radius_m", 12.0)),
        z_min_m=float(config_payload.get("z_min_m", -1.0)),
        z_max_m=float(config_payload.get("z_max_m", 5.0)),
        center_x_m=float(config_payload.get("center_x_m", 0.0)),
        center_y_m=float(config_payload.get("center_y_m", 0.0)),
        center_z_m=float(config_payload.get("center_z_m", 0.0)),
    )
    local_points = local_points_from_ue_world(points_m, origin_m)
    voxels = voxelize_points(local_points, config)
    centers = [voxel_center(voxel, config.voxel_size_m) for voxel in voxels]

    voxel_png = output_dir / "figures" / f"{scene_id}_local_voxel_3d_preview.png"
    grid_png = output_dir / "figures" / f"{scene_id}_local_grid_2d_preview.png"
    plot_point_cloud(voxel_png, centers, f"{scene_id} local occupied voxels, seq {seq}")
    plot_grid(grid_png, frame["projected_grid"], f"{scene_id} projected local grid, seq {seq}")

    voxel_visual = {
        "id": f"{scene_id}_local_voxel_3d",
        "kind": "offline_ue_truth_local_voxel_3d_preview",
        "path": rel(voxel_png),
        "source": rel(fixture_path),
        "source_seq": seq,
        "voxel_count": len(centers),
        "config": asdict(config),
        "claim_boundary": "offline UE-truth local voxel preview only; not ROS2/Gazebo runtime or planner evidence",
    }
    grid_visual = {
        "id": f"{scene_id}_local_grid_2d",
        "kind": "offline_ue_truth_local_grid_2d_preview",
        "path": rel(grid_png),
        "source": rel(fixture_path),
        "source_seq": seq,
        "occupied_cell_count": frame.get("projected_grid", {}).get("occupied_cell_count"),
        "claim_boundary": "offline UE-truth projected grid preview only; not ROS2/Gazebo runtime or planner evidence",
    }
    return voxel_visual, grid_visual


def plot_fastlio_truth(output_dir: Path) -> dict[str, Any]:
    odom_path = ROOT / "Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_truth_eval/fastlio_runtime/fastlio_odometry.jsonl"
    truth_path = ROOT / "Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_truth_eval/gazebo_truth_pose.jsonl"
    eval_path = ROOT / "Results/gazebo_ros2/sunray150_gazebo_ros2_spark_fastlio_truth_eval/FASTLIO_TRUTH_ERROR_EVAL.json"
    odom = sorted(read_jsonl(odom_path), key=lambda row: float(row.get("time", 0.0)))
    truth = sorted(read_jsonl(truth_path), key=lambda row: float(row.get("time", 0.0)))
    png = output_dir / "figures" / "fastlio_vs_gazebo_truth_xy.png"
    plt = import_matplotlib()
    fig, ax = plt.subplots(figsize=(7, 5), dpi=140)
    if odom:
        t0 = float(odom[0].get("time", 0.0))
        xs = [row.get("position_m", [0, 0, 0])[0] for row in odom]
        ys = [row.get("position_m", [0, 0, 0])[1] for row in odom]
        ax.plot(xs, ys, marker="o", markersize=2, linewidth=1, label=f"FAST-LIO odom rel t0={t0:.3f}s")
    if truth:
        xs = [row.get("position_m", [0, 0, 0])[0] for row in truth]
        ys = [row.get("position_m", [0, 0, 0])[1] for row in truth]
        ax.plot(xs, ys, linewidth=1, label="Gazebo truth")
    ax.set_title("FAST-LIO odometry vs Gazebo truth, XY")
    ax.set_xlabel("x m")
    ax.set_ylabel("y m")
    ax.axis("equal")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png)
    plt.close(fig)
    eval_data = read_json(eval_path)
    return {
        "id": "fastlio_truth_xy",
        "kind": "fastlio_vs_gazebo_truth_xy_plot",
        "path": rel(png),
        "source": f"{rel(odom_path)}; {rel(truth_path)}; {rel(eval_path)}",
        "matched_count": eval_data.get("alignment", {}).get("matched_count"),
        "origin_aligned_rmse_3d_m": eval_data.get("metrics", {}).get("origin_aligned", {}).get("rmse_3d_m"),
        "claim_boundary": "estimator-vs-Gazebo-pose quality plot only; no planner, setpoint, closed-loop, or multi-UAV claim",
    }


def plot_hover_hold(output_dir: Path) -> dict[str, Any]:
    truth_path = ROOT / "Results/gazebo_ros2/sunray150_gazebo_ros2_hover_hold_closed_loop_pre_acceptance_005/gazebo_truth_pose.jsonl"
    eval_path = ROOT / "Results/gazebo_ros2/sunray150_gazebo_ros2_hover_hold_closed_loop_pre_acceptance_005/GAZEBO_HOVER_HOLD_CLOSED_LOOP_EVAL.json"
    rows = read_jsonl(truth_path)
    header_rows = [row for row in rows if row.get("time_source") == "header_stamp"]
    selected = header_rows or rows
    png = output_dir / "figures" / "gazebo_hover_hold_altitude.png"
    eval_data = read_json(eval_path)
    target = float(eval_data.get("target_altitude_m", 1.2))
    plt = import_matplotlib()
    fig, ax = plt.subplots(figsize=(7, 5), dpi=140)
    if selected:
        t0 = float(selected[0].get("time", 0.0))
        times = [float(row.get("time", 0.0)) - t0 for row in selected]
        zs = [float(row.get("position_m", [0, 0, 0])[2]) for row in selected]
        ax.plot(times, zs, linewidth=1.25, label="Gazebo truth z")
    ax.axhline(target, color="#c44536", linestyle="--", linewidth=1, label=f"target {target:.2f} m")
    ax.set_title("Gazebo truth-feedback hover-hold altitude")
    ax.set_xlabel("relative time s")
    ax.set_ylabel("z m")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png)
    plt.close(fig)
    return {
        "id": "gazebo_hover_hold_altitude",
        "kind": "gazebo_truth_feedback_hover_hold_altitude_plot",
        "path": rel(png),
        "source": f"{rel(truth_path)}; {rel(eval_path)}",
        "truth_samples": eval_data.get("counts", {}).get("truth_samples"),
        "final_abs_z_error_m": eval_data.get("altitude", {}).get("final_abs_z_error_m"),
        "claim_boundary": "bounded Gazebo truth-feedback hover-hold pre-acceptance plot only; not final closed-loop or controller-performance evidence",
    }


def plot_figure8_static_obstacle(output_dir: Path) -> dict[str, Any]:
    result_dir = ROOT / "Results/gazebo_ros2/default_48s_same_run_current_recheck_20260618_072626"
    truth_path = result_dir / "gazebo_truth_pose.jsonl"
    reference_path = result_dir / "figure8_position_command.trace.jsonl"
    eval_path = result_dir / "FIGURE8_STATIC_OBSTACLE_GATE.json"
    eval_data = read_json(eval_path)
    reference = read_jsonl(reference_path)
    truth = [
        row
        for row in read_jsonl(truth_path)
        if row.get("time_source") in {"header_stamp", "state_stats_sim_time"}
        and isinstance(row.get("position_m"), list)
        and len(row.get("position_m", [])) == 3
    ]
    png = output_dir / "figures" / "gazebo_figure8_static_obstacle_xy.png"
    plt = import_matplotlib()
    fig, ax = plt.subplots(figsize=(7, 5), dpi=140)
    if reference:
        xs = [float(row.get("position_m", [0, 0, 0])[0]) for row in reference]
        ys = [float(row.get("position_m", [0, 0, 0])[1]) for row in reference]
        ax.plot(xs, ys, linewidth=1, label="reference figure-8")
    if truth:
        xs = [float(row.get("position_m", [0, 0, 0])[0]) for row in truth]
        ys = [float(row.get("position_m", [0, 0, 0])[1]) for row in truth]
        ax.plot(xs, ys, linewidth=1.25, label="Gazebo truth")
    for ox, oy, radius in eval_data.get("obstacles_xy_radius", []):
        circle = plt.Circle((float(ox), float(oy)), float(radius), color="#c44536", fill=False, linewidth=1)
        ax.add_patch(circle)
    ax.set_title("Gazebo figure-8 static-obstacle gate, XY")
    ax.set_xlabel("x m")
    ax.set_ylabel("y m")
    ax.axis("equal")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    fig.tight_layout()
    png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(png)
    plt.close(fig)
    return {
        "id": "gazebo_figure8_static_obstacle_xy",
        "kind": "gazebo_truth_feedback_figure8_static_obstacle_xy_plot",
        "path": rel(png),
        "source": f"{rel(truth_path)}; {rel(reference_path)}; {rel(eval_path)}",
        "truth_samples": eval_data.get("counts", {}).get("truth_samples"),
        "rmse_xy_m": eval_data.get("tracking", {}).get("rmse_xy_m"),
        "truth_min_clearance_m": eval_data.get("obstacle_clearance", {}).get("truth_min_m"),
        "claim_boundary": "bounded Gazebo/ROS2 figure-8 plus static-obstacle pre-acceptance plot only; not final closed-loop or competition controller-performance evidence",
    }


def figure8_review_artifact_visuals() -> list[dict[str, Any]]:
    manifest_path = (
        ROOT
        / "Results/gazebo_ros2/default_48s_same_run_current_recheck_20260618_072626/review/FIGURE8_REVIEW_MANIFEST.json"
    )
    manifest = read_json_if_exists(manifest_path)
    visuals: list[dict[str, Any]] = []
    if not manifest or manifest.get("status") != "ready":
        return visuals
    for artifact in manifest.get("artifacts", []):
        if not isinstance(artifact, dict):
            continue
        path = artifact.get("path")
        kind = artifact.get("kind")
        if not path or not kind:
            continue
        visuals.append(
            {
                "id": f"gazebo_{kind}",
                "kind": kind,
                "path": str(path),
                "source": rel(manifest_path),
                "claim_boundary": "offline review artifact built from existing Gazebo reference and independent truth traces; not GUI animation acceptance or final controller-performance evidence",
            }
        )
    return visuals


def build_visuals(output_dir: Path) -> list[dict[str, Any]]:
    visuals: list[dict[str, Any]] = []
    map_review_path = latest_passed_map_review(
        ROOT / "Results/gazebo_ros2",
        [
            "default_48s_same_run_current_recheck_*/map_review/GAZEBO_ROS2_MAP_REVIEW.json",
            "default_48s_same_run_map_recheck_*/map_review/GAZEBO_ROS2_MAP_REVIEW.json",
            "single_uav_48s_alt10_same_run_map_*/map_review/GAZEBO_ROS2_MAP_REVIEW.json",
            "figure8_full_window_same_run_map_review_*/map_review/GAZEBO_ROS2_MAP_REVIEW.json",
            "sunray150_single_uav_competition_light_sensor_local_map_truth_*/map_review/GAZEBO_ROS2_MAP_REVIEW.json",
            "sunray150_gazebo_ros2_sensor_local_map_refresh_*/map_review/GAZEBO_ROS2_MAP_REVIEW.json",
        ],
    )
    if map_review_path is None:
        map_review_path = (
            ROOT
            / "Results/gazebo_ros2/default_48s_same_run_current_recheck_20260618_072626/map_review/GAZEBO_ROS2_MAP_REVIEW.json"
        )
    map_review = read_json_if_exists(map_review_path)
    if map_review and map_review.get("gate_passed") is True:
        artifacts = map_review.get("artifacts", {})
        for visual_id, artifact_key, kind in [
            ("gazebo_lidar_pointcloud_3d", "lidar_pointcloud", "gazebo_runtime_lidar_pointcloud_3d"),
            ("gazebo_local_occupancy_voxels_3d", "local_occupancy_voxels", "gazebo_runtime_local_occupancy_voxels_3d"),
            ("gazebo_local_occupancy_grid_2d", "local_occupancy_grid", "gazebo_runtime_local_occupancy_grid_2d"),
        ]:
            artifact = artifacts.get(artifact_key, {})
            preview = artifact.get("preview_png")
            if not preview:
                continue
            visuals.append(
                {
                    "id": visual_id,
                    "kind": kind,
                    "path": str(preview),
                    "source": rel(map_review_path),
                    "topic": artifact.get("topic"),
                    "frame_id": artifact.get("frame_id"),
                    "point_count": artifact.get("finite_point_count", artifact.get("occupied_count")),
                    "claim_boundary": "live Gazebo/ROS2 runtime review artifact; UE truth is not used as point-cloud or occupancy-map evidence",
                }
            )
    else:
        visuals.append(
            {
                "id": "gazebo_ros2_map_review_missing",
                "kind": "missing_gazebo_runtime_map_review",
                "path": "",
                "source": rel(map_review_path),
                "claim_boundary": "No Gazebo/ROS2 runtime map-review artifact is available; do not substitute UE truth previews.",
            }
        )
    visuals.append(plot_fastlio_truth(output_dir))
    visuals.append(plot_hover_hold(output_dir))
    visuals.append(plot_figure8_static_obstacle(output_dir))
    visuals.extend(figure8_review_artifact_visuals())
    return visuals


def summarize_mworks() -> dict[str, Any]:
    closeout_path = ROOT / "Results/mworks_model_hygiene/20260612_single_uav_pre_multi_uav_closeout_gate/single_uav_pre_multi_uav_closeout_gate.json"
    closeout = read_json(closeout_path)
    batch = closeout.get("batch_acceptance_summary", {})
    candidate = closeout.get("rotor1_candidate_summary", {}).get("best_rmse_candidate", {})
    rerun = closeout.get("current_candidate_rerun_evidence", {})
    return {
        "artifact": rel(closeout_path),
        "status": closeout.get("status"),
        "scope": closeout.get("scope"),
        "batch_acceptance_status": batch.get("status"),
        "scenario_count": batch.get("scenario_count"),
        "accepted_result_count": batch.get("accepted_result_count"),
        "needs_iteration_count": batch.get("needs_iteration_count"),
        "best_candidate_controller_id": candidate.get("controller_id"),
        "best_candidate_scenario": candidate.get("scenario"),
        "current_rerun_state": rerun.get("state"),
        "current_rerun_accepted": rerun.get("accepted_current_rerun"),
        "metrics_file": rerun.get("metrics_file"),
        "raw_file": rerun.get("raw_file"),
        "position_rmse_m": rerun.get("position_rmse_m"),
        "steady_state_error_m": rerun.get("steady_state_error_m"),
        "disturbance_recovery_time_s": rerun.get("disturbance_recovery_time_s"),
        "total_health_score": rerun.get("total_health_score"),
        "claim_boundary": closeout.get("claim_boundary", []),
    }


def build_gates() -> list[dict[str, Any]]:
    gazebo_root = ROOT / "Results/gazebo_ros2"
    sensor_local_map_status = latest_passed_runtime_status_any(
        gazebo_root,
        [
            "default_48s_same_run_current_recheck_*/RUNTIME_STATUS.json",
            "default_48s_same_run_map_recheck_*/RUNTIME_STATUS.json",
            "sunray150_single_uav_competition_light_sensor_local_map_truth_*/RUNTIME_STATUS.json",
            "sunray150_gazebo_ros2_sensor_local_map_refresh_*/RUNTIME_STATUS.json",
        ],
        gate_profile="sensor_local_map",
    )
    sensor_local_map_summary = (
        "Sensor/local-map profile selected from the latest passing immutable competition-light or refresh directory."
        if sensor_local_map_status
        else "Sensor/local-map profile; current RUNTIME_STATUS may be dry-run drift while prior stdout keeps the measured pass."
    )
    sensor_local_map_policy = (
        "latest_passing_sensor_local_map_truth_or_refresh"
        if sensor_local_map_status
        else "legacy_smoke_with_prior_stdout_drift_fallback"
    )
    return [
        gate_from_json(
            "mworks_single_uav_pre_multi_uav_closeout",
            ROOT / "Results/mworks_model_hygiene/20260612_single_uav_pre_multi_uav_closeout_gate/single_uav_pre_multi_uav_closeout_gate.json",
            pass_field="current_candidate_rerun_evidence.accepted_current_rerun",
            summary="MWORKS current rotor1-loss candidate rerun accepted; two older rows still need iteration.",
        ),
        gate_from_json(
            "ue_truth_replay_contract",
            ROOT / "Results/unreal_scene_mapping/UE_TRUTH_REPLAY_CONTRACT_CHECK.json",
            pass_field="ok",
            summary="File-level UE truth/replay contract for Factory and Derelict scenes.",
        ),
        gate_from_json(
            "offline_ue_truth_local_voxel_fixture",
            gazebo_root / "offline_ue_truth_local_voxel_map_fixture/UE_TRUTH_LOCAL_VOXEL_MAP_FIXTURE.json",
            pass_field="ok",
            summary="Offline UE truth to local voxel/grid adapter fixture.",
        ),
        gate_from_runtime_status(
            "gazebo_ros2_sensor_local_map",
            sensor_local_map_status or gazebo_root / "sunray150_gazebo_ros2_smoke/RUNTIME_STATUS.json",
            prior_log_path=gazebo_root / "sunray150_gazebo_ros2_smoke/runtime_status.stdout.log",
            summary=sensor_local_map_summary,
            selected_artifact_policy=sensor_local_map_policy,
        ),
        gate_from_runtime_status(
            "gazebo_ros2_actuator_handoff",
            gazebo_root / "sunray150_gazebo_ros2_actuator_handoff/RUNTIME_STATUS.json",
            summary="Bounded ROS2/Gazebo actuator topic echo gate.",
        ),
        gate_from_runtime_status(
            "gazebo_ros2_controller_output_node_handoff",
            gazebo_root / "sunray150_gazebo_ros2_controller_output_node_handoff/RUNTIME_STATUS.json",
            summary="ControllerOutput message to Actuators topic visibility gate.",
        ),
        gate_from_runtime_status(
            "gazebo_ros2_fastlio_planner_input",
            gazebo_root / "sunray150_gazebo_ros2_fastlio_planner_input/RUNTIME_STATUS.json",
            summary="Gazebo MID360/IMU republished into FAST-LIO/planner input-shape topics.",
        ),
        gate_from_runtime_status(
            "spark_fastlio_output_surface",
            gazebo_root / "sunray150_gazebo_ros2_spark_fastlio_localization/RUNTIME_STATUS.json",
            summary="Spark FAST-LIO-family output topics are nonempty.",
        ),
        gate_from_json(
            "fastlio_vs_gazebo_truth_error",
            gazebo_root / "sunray150_gazebo_ros2_spark_fastlio_truth_eval/FASTLIO_TRUTH_ERROR_EVAL.json",
            pass_field="gate_passed",
            summary="Estimator odometry versus same-run Gazebo pose truth.",
        ),
        gate_from_runtime_status(
            "planner_handoff_without_setpoint_publication",
            gazebo_root / "sunray150_gazebo_ros2_planner_handoff_without_setpoint_publication/RUNTIME_STATUS.json",
            summary="Planner input handoff topics present while setpoint/controller/actuator topics stay absent.",
        ),
        gate_from_runtime_status(
            "command_acknowledgement_without_closed_loop",
            gazebo_root / "sunray150_gazebo_ros2_command_acknowledgement_without_closed_loop/RUNTIME_STATUS.json",
            summary="ControllerOutput receipt, conversion, actuator echo, and stale-command rejection.",
        ),
        gate_from_runtime_status(
            "gazebo_truth_feedback_hover_hold_pre_acceptance",
            gazebo_root / "sunray150_gazebo_ros2_hover_hold_closed_loop_pre_acceptance_005/RUNTIME_STATUS.json",
            summary="Bounded single-UAV Gazebo truth-feedback hover-hold pre-acceptance.",
        ),
        gate_from_runtime_status(
            "gazebo_figure8_static_obstacle_pre_acceptance",
            gazebo_root / "default_48s_same_run_current_recheck_20260618_072626/RUNTIME_STATUS.json",
            summary="Bounded 48s single-UAV Gazebo/ROS2 figure-8 tracking plus static-obstacle clearance pre-acceptance.",
        ),
    ]


def build_report(output_dir: Path) -> dict[str, Any]:
    output_dir = repo_path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    gates = build_gates()
    visuals = build_visuals(output_dir)
    drifted = [gate["gate_id"] for gate in gates if gate["evidence_state"] == "drift_detected_prior_pass_log_available"]
    not_passed = [
        gate["gate_id"]
        for gate in gates
        if gate["evidence_state"] not in {"current_runtime_status_passed", "current_json_passed", "drift_detected_prior_pass_log_available"}
    ]
    status = "single_uav_evidence_bundle_ready"
    if drifted:
        status = "single_uav_evidence_bundle_ready_with_status_drift"
    if not_passed:
        status = "single_uav_evidence_bundle_needs_refresh"

    report = {
        "schema": "mosim.single_uav_evidence_bundle.v1",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output_dir": rel(output_dir),
        "goal": {
            "scope": "single_uav_full_stack_before_multi_uav",
            "multi_uav": "design_interface_only_not_implemented_in_this_goal",
        },
        "subagent_plan": {
            "decision": "unavailable",
            "reason": "Attempted disposable explorer sidecar for evidence review; native tool returned agent thread limit reached.",
            "critical_path_owner": "current_thread",
        },
        "mworks_summary": summarize_mworks(),
        "gates": gates,
        "visuals": visuals,
        "status_drift": {
            "drifted_gates": drifted,
            "not_passed_gates": not_passed,
            "policy": "Use current status files first; if a later dry-run overwrote a result, keep prior measured stdout as drifted evidence and rerun into a fresh directory before final acceptance.",
        },
        "claim_boundary": REQUIRED_BOUNDARY,
        "next_actions": [
            "Keep new runtime gates in immutable result directories; do not overwrite historical smoke evidence with dry-run probes.",
            "Add the next bounded planner-output gate only with no-actuation or an explicit setpoint guard.",
            "Produce UE close/zoomed Sunray150 visual-review or command-echo live evidence only under the UE workflow gate.",
            "Do not enter multi-UAV implementation until the single-UAV evidence chain is accepted.",
        ],
    }
    write_json(output_dir / "SINGLE_UAV_EVIDENCE_BUNDLE.json", report)
    write_markdown(output_dir / "README.md", report)
    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Project-local output directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(repo_path(args.output_dir))
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if report["status"] in {"single_uav_evidence_bundle_ready", "single_uav_evidence_bundle_ready_with_status_drift"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
