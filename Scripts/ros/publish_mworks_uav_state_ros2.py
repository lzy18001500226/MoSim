#!/usr/bin/env python3
"""Publish MWORKS UAV replay output to ROS2 truth, IMU, TF, and LiDAR topics.

This is a bridge from real MWORKS/MCP simulation output into the native ROS2
review path. It is still replay evidence, not a closed real-time co-simulation:
do not use it to claim final FAST-LIO or controller closure without a live
runtime and recorded FAST-LIO output topics.
"""

from __future__ import annotations

import argparse
import csv
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
SUPPORTED_LIDAR_SCHEMAS = {"mosim.lidar_point_frame.v1", "mosim.livox_like_lidar_frame.v1"}


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


def read_mworks_raw(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [
            {key: float(value) for key, value in row.items() if value not in ("", None)}
            for row in csv.DictReader(handle)
        ]
    if len(rows) < 2:
        raise ValueError(f"MWORKS raw CSV needs at least two rows: {path}")
    required = {"time", "x", "y", "z", "roll", "pitch", "yaw"}
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"MWORKS raw CSV missing columns {sorted(missing)}: {path}")
    return rows


def read_jsonl(path: Path, schemas: str | set[str]) -> list[dict[str, Any]]:
    allowed = {schemas} if isinstance(schemas, str) else schemas
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if payload.get("schema") not in allowed:
                raise ValueError(f"unsupported schema at {path}:{line_number}: {payload.get('schema')}")
            rows.append(payload)
    if not rows:
        raise ValueError(f"empty JSONL: {path}")
    return rows


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


def finite_diff(rows: list[dict[str, float]], index: int, key: str) -> float:
    if index <= 0:
        left, right = rows[0], rows[1]
    elif index >= len(rows) - 1:
        left, right = rows[-2], rows[-1]
    else:
        left, right = rows[index - 1], rows[index + 1]
    dt = float(right["time"] - left["time"])
    if abs(dt) < 1e-9:
        return 0.0
    return float(right.get(key, 0.0) - left.get(key, 0.0)) / dt


def euler_rate(rows: list[dict[str, float]], index: int, key: str) -> float:
    return finite_diff(rows, index, key)


def velocity(rows: list[dict[str, float]], index: int) -> tuple[float, float, float]:
    return (
        finite_diff(rows, index, "x"),
        finite_diff(rows, index, "y"),
        finite_diff(rows, index, "z"),
    )


def acceleration(rows: list[dict[str, float]], index: int) -> tuple[float, float, float]:
    if index <= 0:
        v0 = velocity(rows, 0)
        v1 = velocity(rows, 1)
        dt = rows[1]["time"] - rows[0]["time"]
    elif index >= len(rows) - 1:
        v0 = velocity(rows, len(rows) - 2)
        v1 = velocity(rows, len(rows) - 1)
        dt = rows[-1]["time"] - rows[-2]["time"]
    else:
        v0 = velocity(rows, index - 1)
        v1 = velocity(rows, index + 1)
        dt = rows[index + 1]["time"] - rows[index - 1]["time"]
    if abs(dt) < 1e-9:
        return (0.0, 0.0, 0.0)
    return tuple((v1[i] - v0[i]) / dt for i in range(3))


def interpolate_rows(rows: list[dict[str, float]], index: int, alpha: float) -> dict[str, float]:
    left = rows[index]
    right = rows[min(index + 1, len(rows) - 1)]
    alpha = max(0.0, min(1.0, alpha))
    keys = set(left) | set(right)
    return {
        key: float(left.get(key, 0.0)) * (1.0 - alpha) + float(right.get(key, 0.0)) * alpha
        for key in keys
    }


def pack_livox_like_cloud(points: list[list[float]], scan_duration_s: float, scan_lines: int, intensity: float) -> bytes:
    data = bytearray()
    count = max(len(points) - 1, 1)
    for index, point in enumerate(points):
        point_time_us = float(index) / float(count) * scan_duration_s * 1_000_000.0
        ring = int(index % scan_lines)
        data.extend(
            struct.pack(
                "<fffffHxx",
                float(point[0]),
                float(point[1]),
                float(point[2]),
                float(intensity),
                point_time_us,
                ring,
            )
        )
    return bytes(data)


def selected_count(total: int, max_frames: int) -> int:
    if max_frames > 0:
        return min(total, max_frames)
    return total


def dry_run(args: argparse.Namespace) -> int:
    rows = read_mworks_raw(project_path(args.mworks_raw_csv))
    lidar = read_jsonl(project_path(args.lidar_point_frames_jsonl), SUPPORTED_LIDAR_SCHEMAS)
    count = selected_count(min(len(rows), len(lidar)), args.max_frames)
    duration = rows[count - 1]["time"] - rows[0]["time"] if count > 1 else 0.0
    source_dt = [rows[i + 1]["time"] - rows[i]["time"] for i in range(min(count - 1, 20))]
    nominal_source_hz = 1.0 / (sum(source_dt) / len(source_dt)) if source_dt else 0.0
    imu_rate = args.imu_rate_hz
    lidar_rate = args.lidar_rate_hz
    print(
        json.dumps(
            {
                "schema": "mosim.mworks_uav_state_ros2_dryrun.v1",
                "frames": count,
                "source": "MWORKS_MCP_raw_replay",
                "source_duration_s": round(duration, 6),
                "nominal_source_hz": round(nominal_source_hz, 6),
                "target_rates_hz": {
                    "truth_odometry": args.truth_rate_hz,
                    "imu": imu_rate,
                    "lidar": lidar_rate,
                    "controller_setpoint_contract": args.controller_rate_hz,
                },
                "topics": {
                    "truth_odometry": args.truth_odom_topic,
                    "imu": args.imu_topic,
                    "lidar": args.lidar_topic,
                    "tf": "/tf",
                },
                "pointcloud2_fields": ["x", "y", "z", "intensity", "time", "ring"],
                "scan_lines": args.scan_lines,
                "scan_duration_s": args.scan_duration_s,
                "rate_note": (
                    "IMU messages are currently resampled from MWORKS state rows; "
                    "this is not final high-rate raw PX4/IMU sensor evidence."
                ),
                "not_published": ["/cloud_registered", "/odometry", "/path", "planner_command"],
                "claim": "dry-run only; no ROS2 messages were published; replay bridge only, not closed-loop co-simulation",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def publish_ros2(args: argparse.Namespace) -> int:
    ensure_ros_log_dir()
    try:
        import rclpy  # type: ignore
        from builtin_interfaces.msg import Time  # type: ignore
        from geometry_msgs.msg import TransformStamped  # type: ignore
        from nav_msgs.msg import Odometry  # type: ignore
        from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy  # type: ignore
        from sensor_msgs.msg import Imu, PointCloud2, PointField  # type: ignore
        from std_msgs.msg import Header  # type: ignore
        from tf2_ros import TransformBroadcaster  # type: ignore
    except ImportError as exc:
        print("ROS2 Python modules are unavailable. Source /opt/ros/humble/setup.bash first.", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2

    rows = read_mworks_raw(project_path(args.mworks_raw_csv))
    lidar = read_jsonl(project_path(args.lidar_point_frames_jsonl), SUPPORTED_LIDAR_SCHEMAS)
    frame_count = selected_count(min(len(rows), len(lidar)), args.max_frames)
    rows = rows[:frame_count]
    lidar = lidar[:frame_count]

    qos = QoSProfile(
        history=HistoryPolicy.KEEP_LAST,
        depth=16,
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
    )
    rclpy.init()
    node = rclpy.create_node("mosim_mworks_uav_state_publisher")
    tf_broadcaster = TransformBroadcaster(node)
    odom_pub = node.create_publisher(Odometry, args.truth_odom_topic, qos)
    imu_pub = node.create_publisher(Imu, args.imu_topic, qos)
    lidar_pub = node.create_publisher(PointCloud2, args.lidar_topic, qos)

    def stamp_from_seconds(seconds: float) -> Any:
        msg = Time()
        whole = math.floor(seconds)
        msg.sec = int(whole)
        msg.nanosec = int(round((seconds - whole) * 1_000_000_000))
        if msg.nanosec >= 1_000_000_000:
            msg.sec += 1
            msg.nanosec -= 1_000_000_000
        return msg

    start_wall_s = node.get_clock().now().nanoseconds / 1_000_000_000

    def row_stamp(row: dict[str, float], sequence: int) -> Any:
        if args.wall_time:
            return stamp_from_seconds(start_wall_s + sequence / args.truth_rate_hz)
        return stamp_from_seconds(float(row["time"]))

    def offset_stamp(stamp: Any, offset_s: float) -> Any:
        return stamp_from_seconds(float(stamp.sec) + float(stamp.nanosec) / 1_000_000_000 + offset_s)

    def header(stamp: Any, frame_id: str) -> Any:
        return Header(stamp=stamp, frame_id=frame_id)

    def make_odom(row: dict[str, float], index: int, stamp: Any) -> Any:
        qx, qy, qz, qw = quaternion_from_rpy(row["roll"], row["pitch"], row["yaw"])
        vx, vy, vz = velocity(rows, index)
        odom = Odometry()
        odom.header = header(stamp, args.world_frame)
        odom.child_frame_id = args.body_frame
        odom.pose.pose.position.x = row["x"]
        odom.pose.pose.position.y = row["y"]
        odom.pose.pose.position.z = row["z"]
        odom.pose.pose.orientation.x = qx
        odom.pose.pose.orientation.y = qy
        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw
        odom.twist.twist.linear.x = vx
        odom.twist.twist.linear.y = vy
        odom.twist.twist.linear.z = vz
        odom.twist.twist.angular.x = euler_rate(rows, index, "roll")
        odom.twist.twist.angular.y = euler_rate(rows, index, "pitch")
        odom.twist.twist.angular.z = euler_rate(rows, index, "yaw")
        return odom

    def make_imu(row: dict[str, float], index: int, stamp: Any) -> Any:
        qx, qy, qz, qw = quaternion_from_rpy(row["roll"], row["pitch"], row["yaw"])
        ax, ay, az = acceleration(rows, index)
        imu = Imu()
        imu.header = header(stamp, args.imu_frame)
        imu.orientation.x = qx
        imu.orientation.y = qy
        imu.orientation.z = qz
        imu.orientation.w = qw
        imu.angular_velocity.x = euler_rate(rows, index, "roll")
        imu.angular_velocity.y = euler_rate(rows, index, "pitch")
        imu.angular_velocity.z = euler_rate(rows, index, "yaw")
        imu.linear_acceleration.x = ax
        imu.linear_acceleration.y = ay
        imu.linear_acceleration.z = az + 9.81
        return imu

    def publish_tf(row: dict[str, float], stamp: Any) -> None:
        qx, qy, qz, qw = quaternion_from_rpy(row["roll"], row["pitch"], row["yaw"])
        transform = TransformStamped()
        transform.header = header(stamp, args.world_frame)
        transform.child_frame_id = args.body_frame
        transform.transform.translation.x = row["x"]
        transform.transform.translation.y = row["y"]
        transform.transform.translation.z = row["z"]
        transform.transform.rotation.x = qx
        transform.transform.rotation.y = qy
        transform.transform.rotation.z = qz
        transform.transform.rotation.w = qw
        tf_broadcaster.sendTransform(transform)

    def make_cloud(frame: dict[str, Any], stamp: Any) -> Any:
        points = frame.get("points_m", [])
        msg = PointCloud2()
        msg.header = header(stamp, args.lidar_frame)
        msg.height = 1
        msg.width = len(points)
        msg.fields = [
            PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name="intensity", offset=12, datatype=PointField.FLOAT32, count=1),
            PointField(name="time", offset=16, datatype=PointField.FLOAT32, count=1),
            PointField(name="ring", offset=20, datatype=PointField.UINT16, count=1),
        ]
        msg.is_bigendian = False
        msg.point_step = 24
        msg.row_step = msg.point_step * msg.width
        msg.data = pack_livox_like_cloud(points, args.scan_duration_s, args.scan_lines, args.intensity)
        msg.is_dense = True
        return msg

    imu_period_s = 1.0 / args.imu_rate_hz
    source_period_s = 1.0 / args.truth_rate_hz
    imu_substeps = max(1, int(round(args.imu_rate_hz / max(args.truth_rate_hz, 1e-9))))
    lidar_truth_stride = max(1, int(round(args.truth_rate_hz / args.lidar_rate_hz)))
    global_sequence = 0
    truth_sequence = 0
    try:
        while rclpy.ok():
            next_tick = time.perf_counter()
            for index in range(len(rows)):
                for step in range(imu_substeps):
                    if not rclpy.ok():
                        break
                    alpha = step / float(imu_substeps)
                    row = interpolate_rows(rows, index, alpha)
                    source_elapsed_s = float(rows[index]["time"] - rows[0]["time"]) + step * imu_period_s
                    if args.wall_time:
                        stamp = stamp_from_seconds(start_wall_s + global_sequence * imu_period_s)
                    else:
                        stamp = stamp_from_seconds(float(rows[0]["time"]) + source_elapsed_s)
                    if step == 0:
                        publish_tf(row, stamp)
                        odom_pub.publish(make_odom(row, index, stamp))
                        if (truth_sequence % lidar_truth_stride) == 0:
                            lidar_index = min(index, len(lidar) - 1)
                            lidar_pub.publish(make_cloud(lidar[lidar_index], stamp))
                        truth_sequence += 1
                    imu_pub.publish(make_imu(row, index, stamp))
                    rclpy.spin_once(node, timeout_sec=0.0)
                    global_sequence += 1
                    next_tick += imu_period_s
                    sleep_s = next_tick - time.perf_counter()
                    if sleep_s > 0:
                        time.sleep(sleep_s)
                if not rclpy.ok():
                    break
            if not args.loop:
                break
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mworks-raw-csv", type=Path, required=True)
    parser.add_argument("--lidar-point-frames-jsonl", type=Path, required=True)
    parser.add_argument("--world-frame", default="ue_world")
    parser.add_argument("--body-frame", default="base_link")
    parser.add_argument("--imu-frame", default="base/forward_imu_optical_frame")
    parser.add_argument("--lidar-frame", default="base/velodyne_link")
    parser.add_argument("--truth-odom-topic", default="/mosim/truth/odometry")
    parser.add_argument("--imu-topic", default="/mosim/imu")
    parser.add_argument("--lidar-topic", default="/mosim/lidar_points")
    parser.add_argument("--truth-rate-hz", type=float, default=20.0)
    parser.add_argument("--imu-rate-hz", type=float, default=200.0)
    parser.add_argument("--lidar-rate-hz", type=float, default=10.0)
    parser.add_argument("--controller-rate-hz", type=float, default=20.0)
    parser.add_argument("--scan-duration-s", type=float, default=0.09)
    parser.add_argument("--scan-lines", type=int, default=4)
    parser.add_argument("--intensity", type=float, default=50.0)
    parser.add_argument("--max-frames", type=int, default=0)
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--wall-time", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.truth_rate_hz <= 0 or args.imu_rate_hz <= 0 or args.lidar_rate_hz <= 0:
        raise ValueError("rates must be positive")
    if args.scan_duration_s <= 0:
        raise ValueError("--scan-duration-s must be positive")
    if args.scan_lines <= 0:
        raise ValueError("--scan-lines must be positive")
    if args.dry_run:
        return dry_run(args)
    return publish_ros2(args)


if __name__ == "__main__":
    raise SystemExit(main())
