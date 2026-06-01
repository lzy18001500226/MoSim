#!/usr/bin/env python3
"""Publish a MoSim FAST-LIO replay dataset to ROS2 input topics.

This publishes only FAST-LIO-family inputs (`PointCloud2` and `Imu`). It does
not fabricate `/cloud_registered`, `/Odometry`, or `/path`; those must come from
a real FAST-LIO/FAST-LIO2 runtime before localization can be claimed.
"""

from __future__ import annotations

import argparse
import json
import math
import struct
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def load_frames(path: Path) -> list[dict[str, Any]]:
    frames = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if payload.get("schema") != "mosim.fastlio_replay_frame.v1":
                raise ValueError(f"unsupported schema at {path}:{line_number}: {payload.get('schema')}")
            frames.append(payload)
    if not frames:
        raise ValueError(f"empty dataset: {path}")
    return frames


def quaternion_from_rpy(roll: float, pitch: float, yaw: float) -> tuple[float, float, float, float]:
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    return (
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    )


def dry_run(frames: list[dict[str, Any]], args: argparse.Namespace) -> int:
    selected = frames[: args.max_frames if args.max_frames > 0 else len(frames)]
    point_count = sum(len(frame.get("points_lidar_m", [])) for frame in selected)
    print(
        json.dumps(
            {
                "schema": "mosim.fastlio_ros2_publish_dryrun.v1",
                "frames": len(selected),
                "points": point_count,
                "topics": {"pointcloud2": args.lidar_topic, "imu": args.imu_topic},
                "not_published": ["/cloud_registered", "/Odometry", "/path"],
                "claim": "dry-run only; no ROS2 messages were published",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def publish_ros2(frames: list[dict[str, Any]], args: argparse.Namespace) -> int:
    try:
        import rclpy  # type: ignore
        from builtin_interfaces.msg import Time  # type: ignore
        from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy  # type: ignore
        from sensor_msgs.msg import Imu, PointCloud2, PointField  # type: ignore
        from std_msgs.msg import Header  # type: ignore
    except ImportError as exc:
        print(
            "ROS2 Python modules are unavailable. Source /opt/ros/humble/setup.bash first, "
            "then rerun without --dry-run.",
            file=sys.stderr,
        )
        print(str(exc), file=sys.stderr)
        return 2

    qos = QoSProfile(
        history=HistoryPolicy.KEEP_LAST,
        depth=16,
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
    )
    rclpy.init()
    node = rclpy.create_node("mosim_fastlio_replay_publisher")
    cloud_pub = node.create_publisher(PointCloud2, args.lidar_topic, qos)
    imu_pub = node.create_publisher(Imu, args.imu_topic, qos)

    def stamp_from_seconds(seconds: float) -> Any:
        msg = Time()
        whole = math.floor(seconds)
        msg.sec = int(whole)
        msg.nanosec = int(round((seconds - whole) * 1_000_000_000))
        if msg.nanosec >= 1_000_000_000:
            msg.sec += 1
            msg.nanosec -= 1_000_000_000
        return msg

    def current_stamp(frame: dict[str, Any]) -> Any:
        if args.wall_time:
            return node.get_clock().now().to_msg()
        return stamp_from_seconds(float(frame["time"]))

    def make_cloud(frame: dict[str, Any], stamp: Any) -> Any:
        points = frame.get("points_lidar_m", [])
        data = bytearray()
        for point in points:
            data.extend(struct.pack("<ffff", float(point[0]), float(point[1]), float(point[2]), 0.0))
        msg = PointCloud2()
        msg.header = Header(stamp=stamp, frame_id=args.lidar_frame)
        msg.height = 1
        msg.width = len(points)
        msg.fields = [
            PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name="time", offset=12, datatype=PointField.FLOAT32, count=1),
        ]
        msg.is_bigendian = False
        msg.point_step = 16
        msg.row_step = msg.point_step * msg.width
        msg.data = bytes(data)
        msg.is_dense = True
        return msg

    def make_imu(frame: dict[str, Any], stamp: Any) -> Any:
        synthetic = frame["synthetic_imu"]
        roll, pitch, yaw = synthetic["orientation_rpy_rad"]
        qx, qy, qz, qw = quaternion_from_rpy(roll, pitch, yaw)
        msg = Imu()
        msg.header = Header(stamp=stamp, frame_id=args.imu_frame)
        msg.orientation.x = qx
        msg.orientation.y = qy
        msg.orientation.z = qz
        msg.orientation.w = qw
        msg.angular_velocity.x = synthetic["angular_velocity_rad_s"][0]
        msg.angular_velocity.y = synthetic["angular_velocity_rad_s"][1]
        msg.angular_velocity.z = synthetic["angular_velocity_rad_s"][2]
        msg.linear_acceleration.x = synthetic["linear_acceleration_m_s2"][0]
        msg.linear_acceleration.y = synthetic["linear_acceleration_m_s2"][1]
        msg.linear_acceleration.z = synthetic["linear_acceleration_m_s2"][2]
        return msg

    selected = frames[: args.max_frames if args.max_frames > 0 else len(frames)]
    period_s = 1.0 / args.fps
    try:
        while rclpy.ok():
            for frame in selected:
                if not rclpy.ok():
                    break
                stamp = current_stamp(frame)
                imu_pub.publish(make_imu(frame, stamp))
                cloud_pub.publish(make_cloud(frame, stamp))
                rclpy.spin_once(node, timeout_sec=0.0)
                time.sleep(period_s)
            if not args.loop:
                break
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--lidar-topic", default="/velodyne_points")
    parser.add_argument("--imu-topic", default="/imu/data")
    parser.add_argument("--lidar-frame", default="velodyne")
    parser.add_argument("--imu-frame", default="imu")
    parser.add_argument("--fps", type=float, default=10.0)
    parser.add_argument("--max-frames", type=int, default=0)
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--wall-time", action="store_true", help="Publish stamps near current wall time instead of replay time.")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.fps <= 0:
        raise ValueError("--fps must be positive")
    frames = load_frames(project_path(args.dataset))
    if args.dry_run:
        return dry_run(frames, args)
    return publish_ros2(frames, args)


if __name__ == "__main__":
    raise SystemExit(main())
