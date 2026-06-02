#!/usr/bin/env python3
"""Generate dense Livox-like LiDAR replay frames from UE scene truth.

This is a sensor-oracle replay generator. It reuses the local Sunray Mid360
scan-mode CSV contract and MoSim UE collision truth, but it is not a live UE
raycast sensor and not final FAST-LIO evidence by itself.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCAN_MODE = (
    ROOT
    / "References/Sunray/simulation/gazebo_plugin/livox_laser_simulation/scan_mode/mid360-real-centr.csv"
)
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"


def load_scene_truth_pipeline():
    path = ROOT / "Scripts" / "UE5" / "scene_truth_pipeline.py"
    spec = importlib.util.spec_from_file_location("scene_truth_pipeline", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["scene_truth_pipeline"] = module
    spec.loader.exec_module(module)
    return module


scene_truth = load_scene_truth_pipeline()


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def atomic_jsonl_path(path: Path) -> Path:
    return path.with_name(f".{path.name}.tmp.{os.getpid()}")


def read_pose_csv(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [
            {key: float(value) for key, value in row.items() if value not in ("", None)}
            for row in csv.DictReader(handle)
        ]
    if not rows:
        raise ValueError(f"empty pose CSV: {path}")
    if {"time", "x", "y", "z"}.issubset(rows[0]):
        return rows
    ref_required = {"time", "x_ref", "y_ref", "z_ref"}
    missing = ref_required - set(rows[0])
    if missing:
        raise ValueError(f"pose CSV missing columns {sorted(missing)}: {path}")
    for row in rows:
        row["x"] = row["x_ref"]
        row["y"] = row["y_ref"]
        row["z"] = row["z_ref"]
        if "yaw" not in row and "yaw_ref" in row:
            row["yaw"] = row["yaw_ref"]
    return rows


def read_scan_mode(path: Path, *, limit: int, start: int = 0) -> list[tuple[float, float, int, int]]:
    rays: list[tuple[float, float, int, int]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for index, row in enumerate(reader):
            if index < start:
                continue
            if limit > 0 and len(rays) >= limit:
                break
            azimuth = math.radians(float(row["Azimuth/deg"]))
            zenith = math.radians(float(row["Zenith/deg"])) - math.pi / 2.0
            rays.append((azimuth, zenith, index % 4, index))
    if not rays:
        raise ValueError(f"empty scan mode slice: {path}")
    return rays


class HeightGrid:
    def __init__(self, grid: Any, intervals: dict[tuple[int, int], list[tuple[float, float]]]) -> None:
        self.grid = grid
        self.intervals = intervals

    def is_occupied_at_z(self, cell: tuple[int, int], z: float) -> bool:
        if not self.grid.in_bounds(cell):
            return True
        intervals = self.intervals.get(cell)
        if not intervals:
            return self.grid.is_occupied(cell)
        return any(low <= z <= high for low, high in intervals)


def merge_intervals(intervals: list[tuple[float, float]]) -> list[tuple[float, float]]:
    if not intervals:
        return []
    merged: list[tuple[float, float]] = []
    for low, high in sorted(intervals):
        if not merged or low > merged[-1][1] + 1e-6:
            merged.append((low, high))
        else:
            merged[-1] = (merged[-1][0], max(merged[-1][1], high))
    return merged


def build_height_grid(grid: Any, proxies: list[Any], profile: Any, *, z_padding_m: float) -> HeightGrid:
    raw: dict[tuple[int, int], list[tuple[float, float]]] = {}
    for proxy in proxies:
        semantic_type = str(proxy.semantic_type)
        if semantic_type == "sensor":
            continue
        if proxy.max_z < profile.flight_z_m - z_padding_m:
            continue
        if proxy.min_z > profile.flight_z_m + z_padding_m:
            continue
        x0 = max(0, int(math.floor((proxy.min_x - grid.x_min) / grid.resolution)))
        x1 = min(grid.width - 1, int(math.ceil((proxy.max_x - grid.x_min) / grid.resolution)))
        y0 = max(0, int(math.floor((proxy.min_y - grid.y_min) / grid.resolution)))
        y1 = min(grid.height - 1, int(math.ceil((proxy.max_y - grid.y_min) / grid.resolution)))
        if x0 > x1 or y0 > y1:
            continue
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                raw.setdefault((x, y), []).append((proxy.min_z, proxy.max_z))
    return HeightGrid(grid, {cell: merge_intervals(intervals) for cell, intervals in raw.items()})


def rotate_body_to_world(direction: tuple[float, float, float], yaw: float) -> tuple[float, float, float]:
    c = math.cos(yaw)
    s = math.sin(yaw)
    return (
        c * direction[0] - s * direction[1],
        s * direction[0] + c * direction[1],
        direction[2],
    )


def world_point_to_body(point: list[float], pose: dict[str, float]) -> list[float]:
    yaw = pose.get("yaw", 0.0)
    dx = float(point[0]) - pose["x"]
    dy = float(point[1]) - pose["y"]
    dz = float(point[2]) - pose["z"]
    c = math.cos(yaw)
    s = math.sin(yaw)
    return [
        round(c * dx + s * dy, 5),
        round(-s * dx + c * dy, 5),
        round(dz, 5),
    ]


def ray_direction(azimuth: float, zenith: float) -> tuple[float, float, float]:
    horizontal = math.cos(zenith)
    return (
        math.cos(azimuth) * horizontal,
        math.sin(azimuth) * horizontal,
        math.sin(zenith),
    )


def cast_scan(
    *,
    pose: dict[str, float],
    profile: Any,
    grid: Any,
    height_grid: HeightGrid,
    rays: list[tuple[float, float, int, int]],
    max_range_m: float,
    min_range_m: float,
    step_m: float,
    reflectivity: int,
) -> tuple[list[list[float]], list[dict[str, Any]]]:
    origin = (pose["x"], pose["y"], pose["z"])
    yaw = pose.get("yaw", 0.0)
    max_steps = int(math.ceil(max_range_m / step_m))
    points: list[list[float]] = []
    attrs: list[dict[str, Any]] = []
    for point_index, (azimuth, zenith, line, _scan_index) in enumerate(rays):
        local_dir = ray_direction(azimuth, zenith)
        direction = rotate_body_to_world(local_dir, yaw)
        hit: tuple[float, float, float] | None = None
        for step in range(1, max_steps + 1):
            distance = step * step_m
            if distance < min_range_m:
                continue
            x = origin[0] + direction[0] * distance
            y = origin[1] + direction[1] * distance
            z = origin[2] + direction[2] * distance
            cell = grid.world_to_cell(scene_truth.Point2(x, y))
            if not grid.in_bounds(cell):
                break
            if height_grid.is_occupied_at_z(cell, z):
                hit = (x, y, z)
                break
        if hit is None:
            continue
        points.append([round(hit[0], 5), round(hit[1], 5), round(hit[2], 5)])
        attrs.append(
            {
                "offset_time_ns": int(round(point_index * 1_000_000_000.0 / max(1, len(rays)))),
                "line": int(line),
                "reflectivity": int(reflectivity),
                "tag": 16,
            }
        )
    return points, attrs


def write_truth_dataset(path: Path, scene_id: str, poses: list[dict[str, float]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for seq, pose in enumerate(poses):
            payload = {
                "schema": "mosim.fastlio_replay_frame.v1",
                "scene_id": scene_id,
                "seq": seq,
                "time": round(float(pose.get("time", seq * 0.1)), 6),
                "world_frame_id": "ue_world",
                "body_frame_id": "base_link",
                "lidar_frame_id": "base/mid360_link",
                "pose_world_m": [
                    round(float(pose.get("x", 0.0)), 5),
                    round(float(pose.get("y", 0.0)), 5),
                    round(float(pose.get("z", 0.0)), 5),
                ],
                "rpy_rad": [
                    round(float(pose.get("roll", 0.0)), 6),
                    round(float(pose.get("pitch", 0.0)), 6),
                    round(float(pose.get("yaw", 0.0)), 6),
                ],
                "points_lidar_m": [],
                "synthetic_imu": {
                    "source": "mworks_raw_pose_truth_only",
                    "is_measured_imu": False,
                },
                "input_trace": {
                    "pose_source": "mworks_raw_csv",
                    "lidar_source": "not_used_for_truth_evaluation",
                    "fixed_yaw_for_fastlio_input": False,
                },
            }
            handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def generate_scene(args: argparse.Namespace, scene_id: str) -> dict[str, Any]:
    truth_path = scene_truth.scene_truth_path(scene_id, project_path(args.truth_dir))
    truth = scene_truth.load_truth(truth_path)
    profile = scene_truth.default_profile(str(truth["scene_id"]), truth_path)
    proxies = [scene_truth.proxy_from_payload(proxy) for proxy in truth["collision_proxies"]]
    grid, selected, occ_summary = scene_truth.build_occupancy_grid(profile, proxies)
    height_grid = build_height_grid(grid, selected, profile, z_padding_m=args.vertical_span_m * 0.5)
    pose_csv = (
        project_path(args.pose_csv)
        if args.pose_csv
        else DEFAULT_OUTPUT_ROOT / scene_id / "render_replay.csv"
    )
    poses = read_pose_csv(pose_csv)
    if args.pose_start_index > 0:
        poses = poses[args.pose_start_index :]
    if args.pose_stride > 1:
        poses = poses[:: args.pose_stride]
    if args.max_frames > 0:
        poses = poses[: args.max_frames]
    rays = read_scan_mode(project_path(args.scan_mode), limit=args.points_per_frame, start=args.scan_start_index)
    output_dir = project_path(args.output_root) / scene_id
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / args.output_name
    counts: list[int] = []
    tmp_jsonl_path = atomic_jsonl_path(jsonl_path)
    with tmp_jsonl_path.open("w", encoding="utf-8", newline="\n") as handle:
        for seq, pose in enumerate(poses):
            points, attrs = cast_scan(
                pose=pose,
                profile=profile,
                grid=grid,
                height_grid=height_grid,
                rays=rays,
                max_range_m=args.max_range_m,
                min_range_m=args.min_range_m,
                step_m=args.raycast_step_m,
                reflectivity=args.reflectivity,
            )
            counts.append(len(points))
            output_points = points
            coordinate_frame = "ue_world_m_z_up"
            if args.points_frame == "body":
                output_points = [world_point_to_body(point, pose) for point in points]
                coordinate_frame = "body_lidar_m_z_up"
            payload = {
                "schema": "mosim.livox_like_lidar_frame.v1",
                "scene_id": profile.scene_id,
                "seq": seq,
                "time": round(float(pose.get("time", seq / args.lidar_rate_hz)), 6),
                "coordinate_frame": coordinate_frame,
                "source": "sunray_mid360_scan_mode_plus_ue_collision_truth_replay",
                "render_only": False,
                "evidence_backed": True,
                "scan_mode_csv": rel(project_path(args.scan_mode)),
                "lidar_rate_hz": args.lidar_rate_hz,
                "point_rate_hz": args.point_rate_hz,
                "points_m": output_points,
                "point_attributes": attrs,
            }
            handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    tmp_jsonl_path.replace(jsonl_path)
    truth_dataset_path: Path | None = None
    if args.truth_dataset_name:
        truth_dataset_path = output_dir / args.truth_dataset_name
        tmp_truth_dataset_path = atomic_jsonl_path(truth_dataset_path)
        write_truth_dataset(tmp_truth_dataset_path, profile.scene_id, poses)
        tmp_truth_dataset_path.replace(truth_dataset_path)
    manifest = {
        "schema": "mosim.livox_like_lidar_replay_manifest.v1",
        "scene_id": profile.scene_id,
        "truth_source": rel(truth_path),
        "pose_csv": rel(pose_csv),
        "scan_mode_csv": rel(project_path(args.scan_mode)),
        "output_jsonl": rel(jsonl_path),
        "truth_dataset_jsonl": rel(truth_dataset_path) if truth_dataset_path else None,
        "frame_count": len(poses),
        "pose_start_index": args.pose_start_index,
        "pose_stride": args.pose_stride,
        "points_frame": args.points_frame,
        "points_per_frame_requested": args.points_per_frame,
        "points_per_frame_min": min(counts) if counts else 0,
        "points_per_frame_max": max(counts) if counts else 0,
        "points_per_frame_avg": round(sum(counts) / max(1, len(counts)), 3),
        "lidar_rate_hz": args.lidar_rate_hz,
        "point_rate_hz": args.point_rate_hz,
        "claim": "dense replay sensor oracle only; not live UE raycast and not FAST-LIO runtime output",
        "occupancy_summary": occ_summary,
    }
    manifest_path = output_dir / args.manifest_name
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene", action="append", default=[])
    parser.add_argument("--truth-dir", type=Path, default=scene_truth.DEFAULT_TRUTH_DIR)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--pose-csv", type=Path, default=None)
    parser.add_argument("--scan-mode", type=Path, default=DEFAULT_SCAN_MODE)
    parser.add_argument("--scan-start-index", type=int, default=0)
    parser.add_argument("--points-per-frame", type=int, default=20000)
    parser.add_argument("--point-rate-hz", type=float, default=200000.0)
    parser.add_argument("--lidar-rate-hz", type=float, default=10.0)
    parser.add_argument("--max-range-m", type=float, default=30.0)
    parser.add_argument("--min-range-m", type=float, default=0.5)
    parser.add_argument("--raycast-step-m", type=float, default=0.12)
    parser.add_argument("--vertical-span-m", type=float, default=8.0)
    parser.add_argument("--reflectivity", type=int, default=100)
    parser.add_argument("--max-frames", type=int, default=0)
    parser.add_argument("--pose-start-index", type=int, default=0)
    parser.add_argument("--pose-stride", type=int, default=1)
    parser.add_argument("--points-frame", choices=("world", "body"), default="world")
    parser.add_argument("--output-name", default="livox_like_lidar_frames.jsonl")
    parser.add_argument("--manifest-name", default="livox_like_lidar_manifest.json")
    parser.add_argument("--truth-dataset-name", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.points_per_frame <= 0:
        raise ValueError("--points-per-frame must be positive")
    if args.point_rate_hz <= 0 or args.lidar_rate_hz <= 0:
        raise ValueError("rates must be positive")
    if args.max_range_m <= args.min_range_m:
        raise ValueError("--max-range-m must be greater than --min-range-m")
    if args.pose_stride <= 0:
        raise ValueError("--pose-stride must be positive")
    if args.pose_start_index < 0:
        raise ValueError("--pose-start-index must be non-negative")
    scene_ids = args.scene or ["factoryenvironmentcollect"]
    reports = [generate_scene(args, scene_id.lower()) for scene_id in scene_ids]
    print(json.dumps({"schema": "mosim.livox_like_lidar_replay_run.v1", "reports": reports}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
