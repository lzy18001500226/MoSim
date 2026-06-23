#!/usr/bin/env python3
"""Build an offline UE-truth fixture for the local voxel-map adapter.

The fixture translates UE scene-truth LiDAR points into a local frame by
subtracting each frame's local map origin. It intentionally does not apply TF,
vehicle attitude, ROS2 message transport, Gazebo sensors, FAST-LIO, planning,
or closed-loop control. Its purpose is to prove that exported UE point frames
can feed the core local voxel/grid map logic before the live ROS2+Gazebo
dependencies are installed.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Scripts.ros.pointcloud_to_local_voxel_map_ros2 import (
    LocalMapConfig,
    project_voxels_to_grid,
    voxelize_points,
)


DEFAULT_MAPPING_ROOT = ROOT / "Results/unreal_scene_mapping"
DEFAULT_OUTPUT_DIR = ROOT / "Results/gazebo_ros2/offline_ue_truth_local_voxel_map_fixture"
DEFAULT_SCENES = ("factoryenvironmentcollect", "derelictcorridormegascans")


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {rel(path)}")
    return data


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        if not isinstance(data, dict):
            raise ValueError(f"JSONL row must be an object: {rel(path)}")
        rows.append(data)
    return rows


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def local_points_from_ue_world(
    points_m: list[list[float]],
    origin_m: list[float],
) -> list[tuple[float, float, float]]:
    if len(origin_m) != 3:
        raise ValueError("origin_m must have 3 values")
    local_points: list[tuple[float, float, float]] = []
    ox, oy, oz = (float(origin_m[0]), float(origin_m[1]), float(origin_m[2]))
    for point in points_m:
        if len(point) != 3:
            continue
        local_points.append((float(point[0]) - ox, float(point[1]) - oy, float(point[2]) - oz))
    return local_points


def build_scene_fixture(
    mapping_root: Path,
    scene_id: str,
    output_dir: Path,
    config: LocalMapConfig,
    max_frames: int | None,
) -> dict[str, Any]:
    scene_dir = mapping_root / scene_id
    planner_path = scene_dir / "planner_summary.json"
    planner = read_json(planner_path)
    outputs = planner.get("outputs") if isinstance(planner.get("outputs"), dict) else {}
    lidar_path = repo_path(str(outputs.get("lidar_point_frames_jsonl", scene_dir / "lidar_point_frames.jsonl")))
    local_map_path = repo_path(str(outputs.get("local_known_map_jsonl", scene_dir / "local_known_map_frames.jsonl")))
    lidar_frames = read_jsonl(lidar_path)
    local_map_frames = read_jsonl(local_map_path)
    if max_frames is not None:
        lidar_frames = lidar_frames[:max_frames]
        local_map_frames = local_map_frames[:max_frames]
    local_by_seq = {int(frame.get("seq")): frame for frame in local_map_frames if "seq" in frame}

    scene_output_dir = output_dir / scene_id
    frames_path = scene_output_dir / "local_voxel_map_fixture_frames.jsonl"
    frame_summaries: list[dict[str, Any]] = []
    issues: list[str] = []

    scene_output_dir.mkdir(parents=True, exist_ok=True)
    with frames_path.open("w", encoding="utf-8", newline="\n") as handle:
        for lidar_frame in lidar_frames:
            seq = int(lidar_frame.get("seq"))
            local_frame = local_by_seq.get(seq)
            if local_frame is None:
                issues.append(f"missing_local_map_frame_seq:{seq}")
                continue
            if lidar_frame.get("coordinate_frame") != "ue_world_m_z_up":
                issues.append(f"unexpected_lidar_coordinate_frame:{seq}:{lidar_frame.get('coordinate_frame')}")
                continue
            origin_m = local_frame.get("origin_m")
            points_m = lidar_frame.get("points_m")
            if not isinstance(origin_m, list) or not isinstance(points_m, list):
                issues.append(f"invalid_frame_payload:{seq}")
                continue
            local_points = local_points_from_ue_world(points_m, origin_m)
            voxels = voxelize_points(local_points, config)
            projection = project_voxels_to_grid(voxels, config)
            occupied_grid_cells = sum(1 for value in projection.data if value == 100)
            frame_report = {
                "schema": "mosim.offline_ue_truth_local_voxel_map_frame.v1",
                "scene_id": scene_id,
                "seq": seq,
                "time": lidar_frame.get("time"),
                "source_coordinate_frame": "ue_world_m_z_up",
                "local_frame_origin_m": origin_m,
                "transform": "point_local_m = point_ue_world_m - local_frame_origin_m; no rotation; no TF lookup",
                "local_map_adapter_assumption": "input_cloud_already_in_local_map_frame_no_tf_transform",
                "source_point_count": len(points_m),
                "local_point_count": len(local_points),
                "voxel_count": len(voxels),
                "projected_grid": asdict(projection) | {"occupied_cell_count": occupied_grid_cells},
                "config": asdict(config),
                "claim_boundary": [
                    "offline core fixture only",
                    "no ROS2 graph, Gazebo process, ros_gz_bridge, TF, RViz, FAST-LIO, planner, or controller loop was started",
                    "does not prove PointCloud2 runtime evidence, Gazebo runtime success, planner_ready, closed_loop, or multi-UAV readiness",
                ],
            }
            handle.write(json.dumps(frame_report, ensure_ascii=False, separators=(",", ":")) + "\n")
            frame_summaries.append(
                {
                    "seq": seq,
                    "source_point_count": len(points_m),
                    "voxel_count": len(voxels),
                    "projected_occupied_grid_cell_count": occupied_grid_cells,
                }
            )

    voxel_counts = [item["voxel_count"] for item in frame_summaries]
    occupied_counts = [item["projected_occupied_grid_cell_count"] for item in frame_summaries]
    point_counts = [item["source_point_count"] for item in frame_summaries]
    frames_with_voxels = sum(1 for count in voxel_counts if count > 0)
    scene_report = {
        "scene_id": scene_id,
        "ok": not issues and bool(frame_summaries) and frames_with_voxels == len(frame_summaries),
        "status": "offline_local_voxel_fixture_ready"
        if not issues and bool(frame_summaries) and frames_with_voxels == len(frame_summaries)
        else "offline_local_voxel_fixture_failed",
        "issues": issues,
        "artifacts": {
            "planner_summary": rel(planner_path),
            "lidar_point_frames_jsonl": rel(lidar_path),
            "local_known_map_jsonl": rel(local_map_path),
            "fixture_frames_jsonl": rel(frames_path),
        },
        "counts": {
            "frame_count": len(frame_summaries),
            "frames_with_voxels": frames_with_voxels,
            "source_point_count_total": sum(point_counts),
            "voxel_count_min": min(voxel_counts) if voxel_counts else 0,
            "voxel_count_max": max(voxel_counts) if voxel_counts else 0,
            "voxel_count_mean": round(mean(voxel_counts), 3) if voxel_counts else 0.0,
            "projected_occupied_grid_cell_count_min": min(occupied_counts) if occupied_counts else 0,
            "projected_occupied_grid_cell_count_max": max(occupied_counts) if occupied_counts else 0,
            "projected_occupied_grid_cell_count_mean": round(mean(occupied_counts), 3) if occupied_counts else 0.0,
        },
    }
    write_json(scene_output_dir / "local_voxel_map_fixture_summary.json", scene_report)
    return scene_report


def build_report(
    mapping_root: Path,
    output_dir: Path,
    scenes: list[str],
    config: LocalMapConfig,
    max_frames: int | None,
) -> dict[str, Any]:
    scene_reports = [
        build_scene_fixture(mapping_root, scene_id, output_dir, config, max_frames) for scene_id in scenes
    ]
    issues = [
        f"{scene['scene_id']}:{issue}"
        for scene in scene_reports
        for issue in scene.get("issues", [])
    ]
    failed = [scene["scene_id"] for scene in scene_reports if not scene.get("ok")]
    report = {
        "schema": "mosim.offline_ue_truth_local_voxel_map_fixture.v1",
        "ok": not issues and not failed,
        "status": "offline_ue_truth_local_voxel_fixture_ready"
        if not issues and not failed
        else "offline_ue_truth_local_voxel_fixture_failed",
        "mapping_root": rel(mapping_root),
        "output_dir": rel(output_dir),
        "scenes": scene_reports,
        "config": asdict(config),
        "coordinate_transform": "ue_world_m_z_up translated by each local_known_map_frame.origin_m; no rotation or TF",
        "issues": issues,
        "claim_boundary": [
            "This fixture exercises the local voxel/grid core with existing UE truth exports.",
            "It does not start UE, MWORKS, ROS2, Gazebo, RViz, FAST-LIO, sockets, or GUI actions.",
            "It does not prove PointCloud2 runtime evidence, Gazebo runtime success, planner_ready, closed_loop, controller performance, or multi-UAV readiness.",
            "Live validation still requires Gazebo Sim plus ros_gz_bridge and a passing RUNTIME_STATUS.json.",
        ],
        "next_allowed_actions": [
            "Use these frames as offline regression fixtures for the local-map adapter core.",
            "After Gazebo/ros_gz_bridge dependencies are authorized and installed, run the bounded Gazebo+ROS2 smoke to obtain real PointCloud2/local-map runtime evidence.",
        ],
    }
    write_json(output_dir / "UE_TRUTH_LOCAL_VOXEL_MAP_FIXTURE.json", report)
    return report


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# UE Truth Local Voxel Map Offline Fixture",
        "",
        f"- status: `{report['status']}`",
        f"- ok: `{str(report['ok']).lower()}`",
        f"- output_dir: `{report['output_dir']}`",
        f"- coordinate_transform: `{report['coordinate_transform']}`",
        "",
        "## Scenes",
        "",
        "| Scene | OK | Frames | Points | Voxel Mean | Grid Occupied Mean | Status |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for scene in report["scenes"]:
        counts = scene.get("counts", {})
        lines.append(
            f"| `{scene['scene_id']}` | `{str(scene['ok']).lower()}` | "
            f"{counts.get('frame_count', 0)} | {counts.get('source_point_count_total', 0)} | "
            f"{counts.get('voxel_count_mean', 0)} | "
            f"{counts.get('projected_occupied_grid_cell_count_mean', 0)} | "
            f"`{scene.get('status', '')}` |"
        )
    lines.extend(["", "## Boundary", ""])
    lines.extend(f"- {item}" for item in report["claim_boundary"])
    if report["issues"]:
        lines.extend(["", "## Issues", ""])
        lines.extend(f"- `{item}`" for item in report["issues"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping-root", default=str(DEFAULT_MAPPING_ROOT))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--scene", action="append", default=[])
    parser.add_argument("--voxel-size-m", type=float, default=0.20)
    parser.add_argument("--grid-resolution-m", type=float, default=0.20)
    parser.add_argument("--local-radius-m", type=float, default=12.0)
    parser.add_argument("--z-min-m", type=float, default=-1.0)
    parser.add_argument("--z-max-m", type=float, default=5.0)
    parser.add_argument("--max-frames", type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.voxel_size_m <= 0 or args.grid_resolution_m <= 0 or args.local_radius_m <= 0:
        raise SystemExit("voxel-size-m, grid-resolution-m, and local-radius-m must be positive")
    config = LocalMapConfig(
        voxel_size_m=args.voxel_size_m,
        grid_resolution_m=args.grid_resolution_m,
        local_radius_m=args.local_radius_m,
        z_min_m=args.z_min_m,
        z_max_m=args.z_max_m,
    )
    output_dir = repo_path(args.output_dir)
    report = build_report(
        repo_path(args.mapping_root),
        output_dir,
        [scene.lower() for scene in (args.scene or list(DEFAULT_SCENES))],
        config,
        args.max_frames,
    )
    write_markdown(output_dir / "UE_TRUTH_LOCAL_VOXEL_MAP_FIXTURE.md", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
