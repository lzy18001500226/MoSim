#!/usr/bin/env python3
"""Publish a MoSim FAST-LIO replay dataset to ROS2 input topics.

This publishes only FAST-LIO-family inputs (`PointCloud2` and `Imu`). It does
not fabricate `/cloud_registered`, `/odometry`, or `/path`; those must come from
a real FAST-LIO/FAST-LIO2 runtime before localization can be claimed.
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
    period_s = 1.0 / float(args.fps)
    scan_duration_s = effective_scan_duration_s(args)
    imu_span_s = effective_imu_span_s(args, period_s, scan_duration_s)
    requested_imu_span_s = requested_imu_span(args, period_s, scan_duration_s)
    imu_rate_hz = float(args.fps) * float(args.imu_substeps_per_frame)
    print(
        json.dumps(
            {
                "schema": "mosim.fastlio_ros2_publish_dryrun.v1",
                "frames": len(selected),
                "points": point_count,
                "topics": {"pointcloud2": args.lidar_topic, "imu": args.imu_topic},
                "pointcloud2_fields": ["offset_time", "x", "y", "z", "intensity", "tag", "line"],
                "scan_lines": args.scan_lines,
                "scan_duration_s": scan_duration_s,
                "imu_span_s": imu_span_s,
                "requested_imu_span_s": requested_imu_span_s,
                "imu_span_capped": imu_span_s < requested_imu_span_s,
                "imu_substeps_per_frame": args.imu_substeps_per_frame,
                "imu_lead_sleep_s": args.imu_lead_sleep_s,
                "nominal_imu_rate_hz": round(imu_rate_hz, 6),
                "publish_order": "imu_burst_before_pointcloud",
                "not_published": ["/cloud_registered", "/odometry", "/path"],
                "claim": "dry-run only; no ROS2 messages were published",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def publish_ros2(frames: list[dict[str, Any]], args: argparse.Namespace) -> int:
    ensure_ros_log_dir()
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

    replay_start_s = node.get_clock().now().nanoseconds / 1_000_000_000 if args.wall_time else None

    def current_stamp(frame: dict[str, Any], sequence: int) -> Any:
        if args.wall_time:
            assert replay_start_s is not None
            return stamp_from_seconds(replay_start_s + sequence * period_s)
        return stamp_from_seconds(float(frame["time"]))

    def offset_stamp(stamp: Any, offset_s: float) -> Any:
        seconds = float(stamp.sec) + float(stamp.nanosec) / 1_000_000_000 + offset_s
        return stamp_from_seconds(seconds)

    def make_cloud(frame: dict[str, Any], stamp: Any) -> Any:
        points = frame.get("points_lidar_m", [])
        data = bytearray()
        count = max(len(points) - 1, 1)
        for index, point in enumerate(points):
            offset_time = int(float(index) / float(count) * scan_duration_s * 1_000_000_000.0)
            line = int(index % args.scan_lines)
            data.extend(
                struct.pack(
                    "<IffffBB",
                    max(0, min(offset_time, 4_294_967_295)),
                    float(point[0]),
                    float(point[1]),
                    float(point[2]),
                    float(args.intensity),
                    0x10,
                    line,
                )
            )
        msg = PointCloud2()
        msg.header = Header(stamp=stamp, frame_id=args.lidar_frame)
        msg.height = 1
        msg.width = len(points)
        msg.fields = [
            PointField(name="offset_time", offset=0, datatype=PointField.UINT32, count=1),
            PointField(name="x", offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name="y", offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name="z", offset=12, datatype=PointField.FLOAT32, count=1),
            PointField(name="intensity", offset=16, datatype=PointField.FLOAT32, count=1),
            PointField(name="tag", offset=20, datatype=PointField.UINT8, count=1),
            PointField(name="line", offset=21, datatype=PointField.UINT8, count=1),
        ]
        msg.is_bigendian = False
        msg.point_step = 22
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

    def imu_offsets() -> list[float]:
        if args.imu_substeps_per_frame <= 1:
            return [0.0]
        return [
            imu_span_s * float(index) / float(args.imu_substeps_per_frame - 1)
            for index in range(args.imu_substeps_per_frame)
        ]

    selected = frames[: args.max_frames if args.max_frames > 0 else len(frames)]
    period_s = 1.0 / args.fps
    scan_duration_s = effective_scan_duration_s(args)
    imu_span_s = effective_imu_span_s(args, period_s, scan_duration_s)
    imu_sample_offsets_s = imu_offsets()
    global_sequence = 0
    try:
        while rclpy.ok():
            for frame in selected:
                if not rclpy.ok():
                    break
                stamp = current_stamp(frame, global_sequence)
                for offset_s in imu_sample_offsets_s:
                    imu_pub.publish(make_imu(frame, offset_stamp(stamp, offset_s)))
                if args.imu_lead_sleep_s > 0:
                    time.sleep(args.imu_lead_sleep_s)
                cloud_pub.publish(make_cloud(frame, stamp))
                rclpy.spin_once(node, timeout_sec=0.0)
                global_sequence += 1
                time.sleep(max(0.0, period_s - max(0.0, args.imu_lead_sleep_s)))
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
    parser.add_argument(
        "--scan-duration-s",
        type=float,
        default=0.0,
        help="Per-scan duration. Default 0 means min(0.09 s, 80 percent of frame period).",
    )
    parser.add_argument("--scan-lines", type=int, default=16)
    parser.add_argument(
        "--imu-substeps-per-frame",
        type=int,
        default=10,
        help="Synthetic IMU messages published before each LiDAR scan; 10 at 10Hz gives a nominal 100Hz IMU.",
    )
    parser.add_argument(
        "--imu-span-s",
        type=float,
        default=0.0,
        help="Synthetic IMU time span per frame. Default 0 covers one full frame period.",
    )
    parser.add_argument(
        "--imu-lead-sleep-s",
        type=float,
        default=0.005,
        help="Short delay after the IMU burst and before the point cloud, so FAST-LIO receives scan-tail IMU first.",
    )
    parser.add_argument("--intensity", type=float, default=50.0)
    parser.add_argument("--max-frames", type=int, default=0)
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--wall-time", action="store_true", help="Publish stamps near current wall time instead of replay time.")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.fps <= 0:
        raise ValueError("--fps must be positive")
    if args.scan_duration_s < 0:
        raise ValueError("--scan-duration-s must be nonnegative")
    if args.scan_lines <= 0:
        raise ValueError("--scan-lines must be positive")
    if args.imu_substeps_per_frame <= 0:
        raise ValueError("--imu-substeps-per-frame must be positive")
    if args.imu_span_s < 0:
        raise ValueError("--imu-span-s must be nonnegative")
    if args.imu_lead_sleep_s < 0:
        raise ValueError("--imu-lead-sleep-s must be nonnegative")
    frames = load_frames(project_path(args.dataset))
    if args.dry_run:
        return dry_run(frames, args)
    return publish_ros2(frames, args)


def effective_scan_duration_s(args: argparse.Namespace) -> float:
    period_s = 1.0 / float(args.fps)
    if args.scan_duration_s > 0:
        if args.scan_duration_s >= period_s:
            return max(period_s * 0.8, period_s - 1e-3)
        return float(args.scan_duration_s)
    return min(0.09, period_s * 0.8)


def effective_imu_span_s(args: argparse.Namespace, period_s: float, scan_duration_s: float) -> float:
    requested = requested_imu_span(args, period_s, scan_duration_s)
    # FAST-LIO rejects timestamp loopback. Keep each frame's IMU burst inside
    # that frame period so the next frame cannot start before the previous
    # frame's last IMU sample, even when callers pass an overlong span.
    safe_max = max(0.0, period_s - 1e-6)
    return min(requested, safe_max)


def requested_imu_span(args: argparse.Namespace, period_s: float, scan_duration_s: float) -> float:
    if args.imu_span_s > 0:
        return float(args.imu_span_s)
    return max(period_s, scan_duration_s)


if __name__ == "__main__":
    raise SystemExit(main())
