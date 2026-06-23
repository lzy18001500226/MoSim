#!/usr/bin/env python3
"""Record Gazebo/ROS2 point-cloud and local-map review artifacts.

This recorder subscribes to the live Gazebo LiDAR PointCloud2 stream and the
local occupancy PointCloud2/OccupancyGrid outputs, then writes review-ready
PNG previews and a JSON summary. It does not publish commands, setpoints, or
planner outputs.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import struct
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROS_LOG_DIR = ROOT / "Results" / "tmp" / "ros_logs"


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def ensure_ros_log_dir() -> None:
    log_dir = Path(os.environ.get("ROS_LOG_DIR", str(DEFAULT_ROS_LOG_DIR)))
    resolved = project_path(log_dir)
    resolved.mkdir(parents=True, exist_ok=True)
    os.environ["ROS_LOG_DIR"] = str(resolved)


def rel(path: str | Path) -> str:
    value = Path(path)
    try:
        return value.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return value.as_posix()


@dataclass
class CloudSample:
    topic: str
    frame_id: str
    width: int
    height: int
    point_step: int
    finite_points: list[tuple[float, float, float]]
    raw_point_count: int
    finite_point_count: int
    nonfinite_point_count: int


@dataclass
class GridSample:
    topic: str
    frame_id: str
    width: int
    height: int
    resolution_m: float
    origin_xy_m: tuple[float, float]
    data: list[int]
    occupied_count: int
    free_count: int
    unknown_count: int


def point_field_offsets(msg: Any) -> dict[str, int]:
    offsets: dict[str, int] = {}
    for field in msg.fields:
        offsets[str(field.name)] = int(field.offset)
    for name in ("x", "y", "z"):
        if name not in offsets:
            raise ValueError(f"PointCloud2 missing {name} field")
    return offsets


def decode_cloud(msg: Any, *, topic: str, max_points: int) -> CloudSample:
    offsets = point_field_offsets(msg)
    point_step = int(msg.point_step)
    width = int(msg.width)
    height = int(msg.height)
    raw_count = width * height
    total = min(raw_count, max_points)
    data = bytes(msg.data)
    endian = ">" if msg.is_bigendian else "<"
    finite: list[tuple[float, float, float]] = []
    nonfinite = 0
    for index in range(total):
        base = index * point_step
        try:
            x = struct.unpack_from(endian + "f", data, base + offsets["x"])[0]
            y = struct.unpack_from(endian + "f", data, base + offsets["y"])[0]
            z = struct.unpack_from(endian + "f", data, base + offsets["z"])[0]
        except struct.error:
            break
        if math.isfinite(x) and math.isfinite(y) and math.isfinite(z):
            finite.append((float(x), float(y), float(z)))
        else:
            nonfinite += 1
    return CloudSample(
        topic=topic,
        frame_id=str(msg.header.frame_id),
        width=width,
        height=height,
        point_step=point_step,
        finite_points=finite,
        raw_point_count=raw_count,
        finite_point_count=len(finite),
        nonfinite_point_count=nonfinite,
    )


def decode_grid(msg: Any, *, topic: str) -> GridSample:
    data = [int(item) for item in msg.data]
    occupied = sum(1 for item in data if item > 50)
    free = sum(1 for item in data if item == 0)
    unknown = sum(1 for item in data if item < 0)
    return GridSample(
        topic=topic,
        frame_id=str(msg.header.frame_id),
        width=int(msg.info.width),
        height=int(msg.info.height),
        resolution_m=float(msg.info.resolution),
        origin_xy_m=(float(msg.info.origin.position.x), float(msg.info.origin.position.y)),
        data=data,
        occupied_count=occupied,
        free_count=free,
        unknown_count=unknown,
    )


def import_matplotlib() -> Any:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def set_axes_equal(ax: Any, points: list[tuple[float, float, float]]) -> None:
    if not points:
        return
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    zs = [p[2] for p in points]
    ranges = [max(values) - min(values) for values in (xs, ys, zs)]
    radius = max(max(ranges) / 2.0, 0.5)
    centers = [(max(values) + min(values)) / 2.0 for values in (xs, ys, zs)]
    ax.set_xlim(centers[0] - radius, centers[0] + radius)
    ax.set_ylim(centers[1] - radius, centers[1] + radius)
    ax.set_zlim(centers[2] - radius, centers[2] + radius)


def plot_cloud(path: Path, sample: CloudSample, title: str, *, color_by_z: bool = True) -> None:
    plt = import_matplotlib()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(8, 6), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    points = sample.finite_points
    if points:
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        zs = [p[2] for p in points]
        colors = zs if color_by_z else "#5b2a86"
        ax.scatter(xs, ys, zs, c=colors, cmap="viridis" if color_by_z else None, s=2, alpha=0.72)
        set_axes_equal(ax, points)
    ax.set_title(title)
    ax.set_xlabel("x m")
    ax.set_ylabel("y m")
    ax.set_zlabel("z m")
    ax.view_init(elev=28, azim=-55)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_grid(path: Path, sample: GridSample) -> None:
    import numpy as np
    from matplotlib.colors import ListedColormap

    plt = import_matplotlib()
    path.parent.mkdir(parents=True, exist_ok=True)
    if sample.width > 0 and sample.height > 0 and len(sample.data) == sample.width * sample.height:
        array = np.array(sample.data, dtype=int).reshape((sample.height, sample.width))
    else:
        array = np.zeros((1, 1), dtype=int)
    display = np.zeros_like(array, dtype=int)
    display[array < 0] = 0
    display[array == 0] = 1
    display[array > 50] = 2
    fig, ax = plt.subplots(figsize=(6, 6), dpi=140)
    ax.imshow(display, origin="lower", cmap=ListedColormap(["#c7cdd8", "#f7fafc", "#d64032"]))
    ax.set_title("Gazebo/ROS2 local occupancy grid")
    ax.set_xlabel("grid x")
    ax.set_ylabel("grid y")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def sample_summary(sample: CloudSample, *, include_points: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "topic": sample.topic,
        "frame_id": sample.frame_id,
        "width": sample.width,
        "height": sample.height,
        "raw_point_count": sample.raw_point_count,
        "finite_point_count": sample.finite_point_count,
        "nonfinite_point_count": sample.nonfinite_point_count,
        "point_step": sample.point_step,
    }
    if sample.finite_points:
        xs = [p[0] for p in sample.finite_points]
        ys = [p[1] for p in sample.finite_points]
        zs = [p[2] for p in sample.finite_points]
        payload["bounds_m"] = {
            "x": [min(xs), max(xs)],
            "y": [min(ys), max(ys)],
            "z": [min(zs), max(zs)],
        }
    if include_points:
        payload["finite_points_xyz_m"] = [list(item) for item in sample.finite_points]
    return payload


def grid_summary(sample: GridSample, *, include_data: bool = False) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "topic": sample.topic,
        "frame_id": sample.frame_id,
        "width": sample.width,
        "height": sample.height,
        "resolution_m": sample.resolution_m,
        "origin_xy_m": list(sample.origin_xy_m),
        "occupied_count": sample.occupied_count,
        "free_count": sample.free_count,
        "unknown_count": sample.unknown_count,
    }
    if include_data:
        payload["data"] = sample.data
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lidar-topic", default="/mosim/gazebo/lidar_points/points")
    parser.add_argument("--voxel-topic", default="/mosim/local_occupancy_voxels")
    parser.add_argument("--grid-topic", default="/mosim/local_occupancy_grid")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--duration-seconds", type=float, default=10.0)
    parser.add_argument("--max-points", type=int, default=200000)
    parser.add_argument("--include-point-data", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_ros_log_dir()
    try:
        import rclpy  # type: ignore
        from nav_msgs.msg import OccupancyGrid  # type: ignore
        from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy  # type: ignore
        from sensor_msgs.msg import PointCloud2  # type: ignore
    except ImportError as exc:
        print("ROS2 Python modules are unavailable. Source /opt/ros/humble/setup.bash first.", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2

    output_dir = project_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir = output_dir / "figures"
    samples_dir = output_dir / "samples"
    samples_dir.mkdir(parents=True, exist_ok=True)

    samples: dict[str, CloudSample | GridSample] = {}
    errors: list[str] = []

    rclpy.init()
    node = rclpy.create_node("mosim_gazebo_ros2_map_review_recorder")
    qos = QoSProfile(
        history=HistoryPolicy.KEEP_LAST,
        depth=4,
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
    )

    def on_lidar(msg: Any) -> None:
        if "lidar" in samples:
            return
        try:
            samples["lidar"] = decode_cloud(msg, topic=args.lidar_topic, max_points=args.max_points)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"lidar_decode:{exc.__class__.__name__}:{exc}")

    def on_voxel(msg: Any) -> None:
        if "voxel" in samples:
            return
        try:
            samples["voxel"] = decode_cloud(msg, topic=args.voxel_topic, max_points=args.max_points)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"voxel_decode:{exc.__class__.__name__}:{exc}")

    def on_grid(msg: Any) -> None:
        if "grid" in samples:
            return
        try:
            samples["grid"] = decode_grid(msg, topic=args.grid_topic)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"grid_decode:{exc.__class__.__name__}:{exc}")

    node.create_subscription(PointCloud2, args.lidar_topic, on_lidar, qos)
    node.create_subscription(PointCloud2, args.voxel_topic, on_voxel, qos)
    node.create_subscription(OccupancyGrid, args.grid_topic, on_grid, qos)

    deadline = time.monotonic() + max(float(args.duration_seconds), 0.1)
    try:
        while rclpy.ok() and time.monotonic() < deadline and not all(key in samples for key in ("lidar", "voxel", "grid")):
            rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

    artifacts: dict[str, Any] = {}
    if isinstance(samples.get("lidar"), CloudSample):
        lidar = samples["lidar"]
        lidar_json = samples_dir / "gazebo_lidar_pointcloud_sample.json"
        write_json(lidar_json, sample_summary(lidar, include_points=args.include_point_data))
        lidar_png = figures_dir / "gazebo_lidar_pointcloud_3d.png"
        plot_cloud(lidar_png, lidar, "Gazebo MID360 PointCloud2 finite returns")
        artifacts["lidar_pointcloud"] = {
            **sample_summary(lidar),
            "sample_json": rel(lidar_json),
            "preview_png": rel(lidar_png),
        }
    if isinstance(samples.get("voxel"), CloudSample):
        voxel = samples["voxel"]
        voxel_json = samples_dir / "local_occupancy_voxels_sample.json"
        write_json(voxel_json, sample_summary(voxel, include_points=True))
        voxel_png = figures_dir / "gazebo_local_occupancy_voxels_3d.png"
        plot_cloud(voxel_png, voxel, "Gazebo/ROS2 local occupied voxels", color_by_z=False)
        artifacts["local_occupancy_voxels"] = {
            **sample_summary(voxel),
            "sample_json": rel(voxel_json),
            "preview_png": rel(voxel_png),
        }
    if isinstance(samples.get("grid"), GridSample):
        grid = samples["grid"]
        grid_json = samples_dir / "local_occupancy_grid_sample.json"
        write_json(grid_json, grid_summary(grid, include_data=True))
        grid_png = figures_dir / "gazebo_local_occupancy_grid_2d.png"
        plot_grid(grid_png, grid)
        artifacts["local_occupancy_grid"] = {
            **grid_summary(grid),
            "sample_json": rel(grid_json),
            "preview_png": rel(grid_png),
        }

    missing = [key for key in ("lidar", "voxel", "grid") if key not in samples]
    blockers: list[str] = []
    for key in missing:
        blockers.append(f"missing_runtime_sample:{key}")
    if errors:
        blockers.extend(errors)
    for key in ("lidar_pointcloud", "local_occupancy_voxels"):
        if key in artifacts and int(artifacts[key].get("finite_point_count", 0)) <= 0:
            blockers.append(f"empty_finite_points:{key}")
    if "local_occupancy_grid" in artifacts and int(artifacts["local_occupancy_grid"].get("occupied_count", 0)) <= 0:
        blockers.append("empty_occupied_cells:local_occupancy_grid")

    report = {
        "schema": "mosim.gazebo_ros2_map_review.v1",
        "status": "gazebo_ros2_map_review_ready" if not blockers else "gazebo_ros2_map_review_blocked",
        "gate_passed": not blockers,
        "output_dir": rel(output_dir),
        "duration_seconds": args.duration_seconds,
        "topics": {
            "lidar": args.lidar_topic,
            "voxel": args.voxel_topic,
            "grid": args.grid_topic,
        },
        "artifacts": artifacts,
        "blockers": blockers,
        "claim_boundary": [
            "Review artifacts are captured from live Gazebo/ROS2 runtime topics.",
            "Gazebo is the point-cloud and occupancy-map source for this review lane.",
            "UE truth artifacts are not used as point-cloud or occupancy-map review evidence here.",
            "This does not prove planner_ready, trajectory tracking, final closed_loop acceptance, controller performance, or multi-UAV readiness.",
        ],
    }
    write_json(output_dir / "GAZEBO_ROS2_MAP_REVIEW.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
