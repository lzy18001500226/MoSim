#!/usr/bin/env python3
"""Record FAST-LIO ROS2 runtime evidence for later truth comparison.

This recorder subscribes to FAST-LIO output topics and writes compact JSONL
inside a scene result directory. It is intended for the Ubuntu 22.04 ROS2
Humble/RViz2 route.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import struct
import sys
import time
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


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def yaw_from_quaternion(x: float, y: float, z: float, w: float) -> float:
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


def stamp_to_sec(stamp: Any) -> float:
    return float(getattr(stamp, "sec", 0)) + float(getattr(stamp, "nanosec", 0)) * 1e-9


def sample_cloud_points(msg: Any, max_points: int) -> tuple[int, list[list[float]]]:
    point_step = int(getattr(msg, "point_step", 0) or 0)
    data = bytes(getattr(msg, "data", b""))
    width = int(getattr(msg, "width", 0) or 0)
    height = int(getattr(msg, "height", 0) or 0)
    count = width * max(1, height)
    if point_step < 12 or not data:
        return count, []
    sample_count = min(count, max_points)
    step = max(1, count // sample_count) if sample_count else 1
    points: list[list[float]] = []
    for index in range(0, count, step):
        if len(points) >= sample_count:
            break
        offset = index * point_step
        if offset + 12 > len(data):
            break
        x, y, z = struct.unpack_from("<fff", data, offset)
        points.append([round(float(x), 5), round(float(y), 5), round(float(z), 5)])
    return count, points


def dry_run(args: argparse.Namespace) -> int:
    output_dir = project_path(args.output_dir)
    print(
        json.dumps(
            {
                "schema": "mosim.fastlio_ros2_runtime_record_dryrun.v1",
                "scene_id": args.scene_id,
                "output_dir": rel(output_dir),
                "topics": {
                    "odometry": args.odom_topic,
                    "path": args.path_topic,
                    "registered_cloud": args.cloud_topic,
                },
                "claim": "dry-run only; no ROS2 topics were subscribed and no runtime evidence was recorded",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def record_ros2(args: argparse.Namespace) -> int:
    ensure_ros_log_dir()
    try:
        import rclpy  # type: ignore
        from nav_msgs.msg import Odometry, Path as RosPath  # type: ignore
        from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy  # type: ignore
        from sensor_msgs.msg import PointCloud2  # type: ignore
    except ImportError as exc:
        print(
            "ROS2 Python modules are unavailable. Source /opt/ros/humble/setup.bash first.",
            file=sys.stderr,
        )
        print(str(exc), file=sys.stderr)
        return 2

    output_dir = project_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    odom_path = output_dir / "fastlio_odometry.jsonl"
    path_path = output_dir / "fastlio_path.jsonl"
    cloud_path = output_dir / "fastlio_registered_cloud_summary.jsonl"
    summary_path = output_dir / "FASTLIO_RUNTIME_RECORDING.json"
    counters = {"odometry": 0, "path": 0, "registered_cloud": 0}

    odom_handle = odom_path.open("w", encoding="utf-8", newline="\n")
    path_handle = path_path.open("w", encoding="utf-8", newline="\n")
    cloud_handle = cloud_path.open("w", encoding="utf-8", newline="\n")

    def write_line(handle: Any, payload: dict[str, Any]) -> None:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
        handle.flush()

    def on_odom(msg: Odometry) -> None:
        pose = msg.pose.pose
        q = pose.orientation
        counters["odometry"] += 1
        write_line(
            odom_handle,
            {
                "schema": "mosim.fastlio_odometry_sample.v1",
                "seq": counters["odometry"] - 1,
                "time": round(stamp_to_sec(msg.header.stamp), 6),
                "frame_id": msg.header.frame_id,
                "child_frame_id": msg.child_frame_id,
                "position_m": [
                    round(float(pose.position.x), 6),
                    round(float(pose.position.y), 6),
                    round(float(pose.position.z), 6),
                ],
                "yaw_rad": round(yaw_from_quaternion(q.x, q.y, q.z, q.w), 6),
            },
        )

    def on_path(msg: RosPath) -> None:
        counters["path"] += 1
        poses = []
        for pose_stamped in msg.poses[-min(len(msg.poses), args.max_path_tail) :]:
            pose = pose_stamped.pose
            q = pose.orientation
            poses.append(
                {
                    "time": round(stamp_to_sec(pose_stamped.header.stamp), 6),
                    "position_m": [
                        round(float(pose.position.x), 6),
                        round(float(pose.position.y), 6),
                        round(float(pose.position.z), 6),
                    ],
                    "yaw_rad": round(yaw_from_quaternion(q.x, q.y, q.z, q.w), 6),
                }
            )
        write_line(
            path_handle,
            {
                "schema": "mosim.fastlio_path_sample.v1",
                "seq": counters["path"] - 1,
                "time": round(stamp_to_sec(msg.header.stamp), 6),
                "frame_id": msg.header.frame_id,
                "pose_count": len(msg.poses),
                "tail": poses,
            },
        )

    def on_cloud(msg: PointCloud2) -> None:
        counters["registered_cloud"] += 1
        point_count, sample = sample_cloud_points(msg, args.max_cloud_sample)
        write_line(
            cloud_handle,
            {
                "schema": "mosim.fastlio_registered_cloud_summary.v1",
                "seq": counters["registered_cloud"] - 1,
                "time": round(stamp_to_sec(msg.header.stamp), 6),
                "frame_id": msg.header.frame_id,
                "point_count": point_count,
                "sample_points": sample,
            },
        )

    qos = QoSProfile(
        history=HistoryPolicy.KEEP_LAST,
        depth=32,
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
    )
    rclpy.init()
    node = rclpy.create_node("mosim_fastlio_ros2_runtime_recorder")
    node.create_subscription(Odometry, args.odom_topic, on_odom, qos)
    node.create_subscription(RosPath, args.path_topic, on_path, qos)
    node.create_subscription(PointCloud2, args.cloud_topic, on_cloud, qos)

    deadline = time.monotonic() + float(args.duration_seconds)
    try:
        while rclpy.ok() and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.1)
    finally:
        node.destroy_node()
        rclpy.shutdown()
        odom_handle.close()
        path_handle.close()
        cloud_handle.close()

    summary = {
        "schema": "mosim.fastlio_ros2_runtime_recording.v1",
        "scene_id": args.scene_id,
        "duration_seconds": args.duration_seconds,
        "topics": {
            "odometry": args.odom_topic,
            "path": args.path_topic,
            "registered_cloud": args.cloud_topic,
        },
        "counts": counters,
        "outputs": {
            "odometry_jsonl": rel(odom_path),
            "path_jsonl": rel(path_path),
            "registered_cloud_summary_jsonl": rel(cloud_path),
        },
        "claim_boundary": [
            "This records ROS2 runtime output; localization quality still requires comparison against replay truth.",
            "A nonzero point-cloud count alone does not prove accurate localization.",
        ],
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if any(counters[name] <= 0 for name in counters):
        return 3
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-id", default="factoryenvironmentcollect")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "Results/unreal_scene_mapping/factoryenvironmentcollect/fastlio_runtime",
    )
    parser.add_argument("--duration-seconds", type=float, default=20.0)
    parser.add_argument("--odom-topic", default="/odometry")
    parser.add_argument("--path-topic", default="/path")
    parser.add_argument("--cloud-topic", default="/cloud_registered")
    parser.add_argument("--max-path-tail", type=int, default=100)
    parser.add_argument("--max-cloud-sample", type=int, default=128)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.duration_seconds <= 0:
        raise ValueError("--duration-seconds must be positive")
    if args.max_path_tail <= 0 or args.max_cloud_sample <= 0:
        raise ValueError("--max-path-tail and --max-cloud-sample must be positive")
    if args.dry_run:
        return dry_run(args)
    return record_ros2(args)


if __name__ == "__main__":
    raise SystemExit(main())
