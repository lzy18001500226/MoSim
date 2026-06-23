#!/usr/bin/env python3
"""Build review plots from an existing Gazebo/ROS2 figure-8 gate run.

This script is evidence packaging only. It reads an already completed result
directory and does not start Gazebo, ROS2, RViz, planners, or controllers.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.quality.evaluate_figure8_obstacle_gate import (  # noqa: E402
    crop_truth_to_reference_window,
    crop_truth_to_tracker_window,
    read_json,
    read_jsonl,
    reference_samples,
    rel,
    timed_truth,
    tracker_observed_truth,
)


DEFAULT_RESULT_DIR = (
    ROOT
    / "Results/gazebo_ros2/figure8_headless_after_gui_blocker_20260618_053129"
)


CLAIM_BOUNDARY = [
    "Review artifacts are built from an existing headless Gazebo/ROS2 figure-8 run.",
    "LiDAR point cloud remains raw radar/sensor output for localization and mapping inputs; local voxel/grid maps are downstream products.",
    "These plots help review trajectory shape, obstacle clearance, and altitude from recorded truth/reference traces.",
    "They do not replace Gazebo GUI animation acceptance and do not prove final competition controller performance, final closed_loop acceptance, UE acceptance, or multi-UAV readiness.",
]


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def import_matplotlib() -> Any:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def finite_xyz(row: dict[str, Any], key: str = "position_m") -> tuple[float, float, float] | None:
    value = row.get(key)
    if not isinstance(value, list) or len(value) != 3:
        return None
    try:
        return float(value[0]), float(value[1]), float(value[2])
    except (TypeError, ValueError):
        return None


def load_cropped_truth(
    result_dir: Path,
    refs: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], str]:
    raw_truth = timed_truth(read_jsonl(result_dir / "gazebo_truth_pose.jsonl"))
    tracker_trace = read_jsonl(result_dir / "figure8_setpoint_tracker.trace.jsonl")
    truth, _policy = crop_truth_to_tracker_window(raw_truth, tracker_trace)
    truth, _reference_policy = crop_truth_to_reference_window(truth, refs)
    truth_source = "independent_gazebo_truth"
    if not truth:
        fallback = tracker_observed_truth(tracker_trace)
        if fallback:
            truth = fallback
            truth_source = "controller_observed_truth_fallback"
    return truth, truth_source


def plot_topdown(
    output_path: Path,
    refs: list[dict[str, Any]],
    truth: list[dict[str, Any]],
    gate: dict[str, Any],
) -> dict[str, Any]:
    plt = import_matplotlib()
    fig, ax = plt.subplots(figsize=(7.5, 6.0), dpi=150)

    if refs:
        xs = [float(row["_position"][0]) for row in refs]
        ys = [float(row["_position"][1]) for row in refs]
        ax.plot(xs, ys, linewidth=1.2, color="#2f6fed", label="reference figure-8")
        ax.scatter(xs[0], ys[0], s=24, color="#2f6fed", marker="o", label="reference start")

    if truth:
        xs = [float(row["_position"][0]) for row in truth]
        ys = [float(row["_position"][1]) for row in truth]
        ax.plot(xs, ys, linewidth=1.4, color="#d14d2a", label="Gazebo truth")
        ax.scatter(xs[0], ys[0], s=24, color="#d14d2a", marker="^", label="truth start")
        ax.scatter(xs[-1], ys[-1], s=24, color="#8b1e3f", marker="s", label="truth end")

    for idx, obstacle in enumerate(gate.get("obstacles_xy_radius", []), start=1):
        if not isinstance(obstacle, list) or len(obstacle) != 3:
            continue
        ox, oy, radius = [float(value) for value in obstacle]
        circle = plt.Circle((ox, oy), radius, color="#111111", fill=False, linewidth=1.1)
        ax.add_patch(circle)
        ax.text(ox, oy, f"O{idx}", ha="center", va="center", fontsize=8)

    clearance = gate.get("obstacle_clearance", {})
    ax.set_title(
        "Figure-8 static-obstacle review, XY\n"
        f"truth clearance={clearance.get('truth_min_m')} m, reference clearance={clearance.get('reference_min_m')} m"
    )
    ax.set_xlabel("x m")
    ax.set_ylabel("y m")
    ax.axis("equal")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    return {
        "path": rel(output_path),
        "kind": "figure8_truth_reference_topdown",
        "reference_samples": len(refs),
        "truth_samples": len(truth),
    }


def plot_altitude(
    output_path: Path,
    refs: list[dict[str, Any]],
    truth: list[dict[str, Any]],
    gate: dict[str, Any],
) -> dict[str, Any]:
    plt = import_matplotlib()
    fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=150)

    if refs:
        times = [float(row["_time"]) for row in refs]
        zs = [float(row["_position"][2]) for row in refs]
        ax.plot(times, zs, linewidth=1.0, color="#2f6fed", label="reference z")

    if truth:
        t0 = float(truth[0]["_time"])
        times = [float(row["_time"]) - t0 for row in truth]
        zs = [float(row["_position"][2]) for row in truth]
        ax.plot(times, zs, linewidth=1.2, color="#d14d2a", label="Gazebo truth z")

    tracking = gate.get("tracking", {})
    ax.set_title(
        "Figure-8 altitude review\n"
        f"max z error={tracking.get('max_z_error_m')} m"
    )
    ax.set_xlabel("relative time s")
    ax.set_ylabel("z m")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)
    return {
        "path": rel(output_path),
        "kind": "figure8_altitude_time",
        "reference_samples": len(refs),
        "truth_samples": len(truth),
    }


def sample_by_time(rows: list[dict[str, Any]], time_s: float, cursor: int) -> tuple[dict[str, Any] | None, int]:
    if not rows:
        return None, cursor
    cursor = max(0, min(cursor, len(rows) - 1))
    while cursor + 1 < len(rows) and abs(float(rows[cursor + 1]["_time"]) - time_s) <= abs(
        float(rows[cursor]["_time"]) - time_s
    ):
        cursor += 1
    return rows[cursor], cursor


def build_trajectory_gif(
    output_path: Path,
    refs: list[dict[str, Any]],
    truth: list[dict[str, Any]],
    gate: dict[str, Any],
    *,
    frame_count: int = 80,
) -> dict[str, Any]:
    from matplotlib.animation import PillowWriter

    plt = import_matplotlib()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not refs or not truth:
        return {
            "path": rel(output_path),
            "kind": "figure8_truth_reference_topdown_animation_gif",
            "status": "skipped",
            "reason": "missing_reference_or_truth_samples",
            "frame_count": 0,
        }

    ref_start = float(refs[0]["_time"])
    ref_end = float(refs[-1]["_time"])
    truth_start = float(truth[0]["_time"])
    truth_elapsed_end = max(0.0, float(truth[-1]["_time"]) - truth_start)
    elapsed_end = max(0.1, min(ref_end - ref_start, truth_elapsed_end))
    frame_count = max(12, min(frame_count, 160))
    frame_times = [elapsed_end * index / max(frame_count - 1, 1) for index in range(frame_count)]

    ref_xs = [float(row["_position"][0]) for row in refs]
    ref_ys = [float(row["_position"][1]) for row in refs]
    truth_xs = [float(row["_position"][0]) for row in truth]
    truth_ys = [float(row["_position"][1]) for row in truth]
    xs_all = ref_xs + truth_xs
    ys_all = ref_ys + truth_ys

    fig, ax = plt.subplots(figsize=(7.5, 6.0), dpi=110)
    ax.plot(ref_xs, ref_ys, linewidth=1.0, color="#2f6fed", alpha=0.55, label="reference")
    truth_line, = ax.plot([], [], linewidth=1.8, color="#d14d2a", label="Gazebo truth")
    ref_marker, = ax.plot([], [], marker="o", markersize=6, color="#2f6fed", linestyle="None")
    truth_marker, = ax.plot([], [], marker="^", markersize=7, color="#d14d2a", linestyle="None")
    title = ax.set_title("")

    for idx, obstacle in enumerate(gate.get("obstacles_xy_radius", []), start=1):
        if not isinstance(obstacle, list) or len(obstacle) != 3:
            continue
        ox, oy, radius = [float(value) for value in obstacle]
        ax.add_patch(plt.Circle((ox, oy), radius, color="#111111", fill=False, linewidth=1.2))
        ax.text(ox, oy, f"O{idx}", ha="center", va="center", fontsize=8)

    margin = 0.4
    ax.set_xlim(min(xs_all) - margin, max(xs_all) + margin)
    ax.set_ylim(min(ys_all) - margin, max(ys_all) + margin)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x m")
    ax.set_ylabel("y m")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best", fontsize=8)

    ref_cursor = 0
    truth_cursor = 0
    truth_path_x: list[float] = []
    truth_path_y: list[float] = []

    def update(frame_index: int) -> list[Any]:
        nonlocal ref_cursor, truth_cursor, truth_path_x, truth_path_y
        elapsed = frame_times[frame_index]
        ref_sample, ref_cursor = sample_by_time(refs, ref_start + elapsed, ref_cursor)
        truth_sample, truth_cursor = sample_by_time(truth, truth_start + elapsed, truth_cursor)
        if truth_sample is not None:
            truth_path_x.append(float(truth_sample["_position"][0]))
            truth_path_y.append(float(truth_sample["_position"][1]))
            truth_line.set_data(truth_path_x, truth_path_y)
            truth_marker.set_data([truth_path_x[-1]], [truth_path_y[-1]])
        if ref_sample is not None:
            ref_marker.set_data([float(ref_sample["_position"][0])], [float(ref_sample["_position"][1])])
        title.set_text(f"Figure-8 Gazebo truth review, t={elapsed:05.2f}s")
        return [truth_line, ref_marker, truth_marker, title]

    from matplotlib.animation import FuncAnimation

    animation = FuncAnimation(fig, update, frames=len(frame_times), interval=100, blit=False)
    animation.save(output_path, writer=PillowWriter(fps=10))
    plt.close(fig)
    return {
        "path": rel(output_path),
        "kind": "figure8_truth_reference_topdown_animation_gif",
        "status": "ready",
        "frame_count": len(frame_times),
        "fps": 10,
        "duration_s": round(elapsed_end, 6),
        "source": "reference_trace_plus_independent_gazebo_truth",
    }


def build(result_dir: Path, output_dir: Path) -> dict[str, Any]:
    gate_path = result_dir / "FIGURE8_STATIC_OBSTACLE_GATE.json"
    reference_path = result_dir / "figure8_position_command.trace.jsonl"
    tracker_path = result_dir / "figure8_setpoint_tracker.trace.jsonl"
    truth_path = result_dir / "gazebo_truth_pose.jsonl"

    gate = read_json(gate_path)
    refs = reference_samples(read_jsonl(reference_path))
    truth, truth_source = load_cropped_truth(result_dir, refs)

    artifacts = [
        plot_topdown(output_dir / "figure8_truth_reference_topdown.png", refs, truth, gate),
        plot_altitude(output_dir / "figure8_altitude_time.png", refs, truth, gate),
        build_trajectory_gif(output_dir / "figure8_truth_reference_topdown_animation.gif", refs, truth, gate),
    ]

    manifest = {
        "schema": "mosim.figure8_gazebo_review_artifacts.v1",
        "status": "ready" if gate.get("gate_passed") is True and truth and refs else "incomplete",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "result_dir": rel(result_dir),
        "output_dir": rel(output_dir),
        "inputs": {
            "gate_json": rel(gate_path),
            "reference_trace_jsonl": rel(reference_path),
            "tracker_trace_jsonl": rel(tracker_path),
            "truth_pose_jsonl": rel(truth_path),
        },
        "gate_summary": {
            "gate_passed": gate.get("gate_passed"),
            "status": gate.get("status"),
            "duration_s": gate.get("duration_s"),
            "counts": gate.get("counts", {}),
            "tracking": gate.get("tracking", {}),
            "obstacle_clearance": gate.get("obstacle_clearance", {}),
            "warnings": gate.get("warnings", []),
            "blockers": gate.get("blockers", []),
        },
        "truth_source": truth_source,
        "artifacts": artifacts,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(output_dir / "FIGURE8_REVIEW_MANIFEST.json", manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-dir", default=DEFAULT_RESULT_DIR, type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    result_dir = project_path(args.result_dir)
    output_dir = project_path(args.output_dir) if args.output_dir else result_dir / "review"
    manifest = build(result_dir, output_dir)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if manifest.get("status") == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
