#!/usr/bin/env python3
"""Bridge MoSim Gazebo sensor topics to FAST-LIO/planner input topics.

This adapter prepares input surfaces for the Sunray/YunZong-style FAST-LIO and
EGO-planner stack. It republishes Gazebo PointCloud2/IMU samples to compatible
topic names and publishes a map-frame point cloud plus an odometry-shape topic
from same-run TF. The runner writes its summary to
fastlio_planner_input_adapter.json. It does not run FAST-LIO, EGO-planner,
setpoint publication, flight control, or closed-loop validation.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import signal
import struct
import sys
import time
from collections import deque
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


def repo_path(value: str | Path | None) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def write_json(path: str | Path | None, payload: dict[str, Any]) -> None:
    output = repo_path(path)
    if output is None:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: str | Path | None, payload: dict[str, Any]) -> None:
    output = repo_path(path)
    if output is None:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


@dataclass(frozen=True)
class Transform3D:
    translation_xyz: tuple[float, float, float]
    rotation_xyzw: tuple[float, float, float, float]


@dataclass
class PlannerCloudFilterStats:
    sampled_point_count: int = 0
    finite_before_filter: int = 0
    finite_after_filter: int = 0
    removed_invalid_range: int = 0
    removed_ground: int = 0
    removed_self: int = 0
    min_z_before_filter: float | None = None
    max_z_before_filter: float | None = None
    min_z_after_filter: float | None = None
    max_z_after_filter: float | None = None

    def _record_z(self, z: float, *, after_filter: bool) -> None:
        min_key = "min_z_after_filter" if after_filter else "min_z_before_filter"
        max_key = "max_z_after_filter" if after_filter else "max_z_before_filter"
        current_min = getattr(self, min_key)
        current_max = getattr(self, max_key)
        setattr(self, min_key, z if current_min is None else min(current_min, z))
        setattr(self, max_key, z if current_max is None else max(current_max, z))

    def to_dict(self) -> dict[str, Any]:
        return {
            "sampled_point_count": self.sampled_point_count,
            "finite_before_filter": self.finite_before_filter,
            "finite_after_filter": self.finite_after_filter,
            "removed_invalid_range": self.removed_invalid_range,
            "removed_ground": self.removed_ground,
            "removed_self": self.removed_self,
            "min_z_before_filter": self.min_z_before_filter,
            "max_z_before_filter": self.max_z_before_filter,
            "min_z_after_filter": self.min_z_after_filter,
            "max_z_after_filter": self.max_z_after_filter,
        }


def normalize_quaternion_xyzw(quaternion: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    x, y, z, w = quaternion
    norm = math.sqrt(x * x + y * y + z * z + w * w)
    if norm <= 0.0:
        raise ValueError("quaternion norm must be positive")
    return (x / norm, y / norm, z / norm, w / norm)


def rotate_point_by_quaternion(
    point: tuple[float, float, float],
    quaternion_xyzw: tuple[float, float, float, float],
) -> tuple[float, float, float]:
    x, y, z, w = normalize_quaternion_xyzw(quaternion_xyzw)
    px, py, pz = point
    tx = 2.0 * (y * pz - z * py)
    ty = 2.0 * (z * px - x * pz)
    tz = 2.0 * (x * py - y * px)
    return (
        px + w * tx + (y * tz - z * ty),
        py + w * ty + (z * tx - x * tz),
        pz + w * tz + (x * ty - y * tx),
    )


def transform_point(point: tuple[float, float, float], transform: Transform3D) -> tuple[float, float, float]:
    rx, ry, rz = rotate_point_by_quaternion(point, transform.rotation_xyzw)
    tx, ty, tz = transform.translation_xyz
    return (rx + tx, ry + ty, rz + tz)


def transform_from_ros_message(transform_msg: Any) -> Transform3D:
    translation = transform_msg.translation
    rotation = transform_msg.rotation
    return Transform3D(
        translation_xyz=(float(translation.x), float(translation.y), float(translation.z)),
        rotation_xyzw=(float(rotation.x), float(rotation.y), float(rotation.z), float(rotation.w)),
    )


def point_is_valid_lidar_return(point: tuple[float, float, float], max_valid_range_m: float | None) -> bool:
    if not all(math.isfinite(item) for item in point):
        return False
    if max_valid_range_m is None or max_valid_range_m <= 0.0:
        return True
    x, y, z = point
    return (x * x + y * y + z * z) <= (max_valid_range_m * max_valid_range_m)


def transformed_pointcloud2(
    source: Any,
    transform: Transform3D,
    output_frame: str,
    max_points: int,
    *,
    max_valid_range_m: float | None = None,
    planner_min_z: float | None = None,
    self_filter_center_xyz: tuple[float, float, float] | None = None,
    self_filter_radius_xy: float = 0.0,
    self_filter_z_min: float | None = None,
    self_filter_z_max: float | None = None,
) -> tuple[Any, PlannerCloudFilterStats]:
    from sensor_msgs.msg import PointCloud2

    output = PointCloud2()
    output.header.stamp = source.header.stamp
    output.header.frame_id = output_frame
    output.height = source.height
    output.width = source.width
    output.fields = source.fields
    output.is_bigendian = source.is_bigendian
    output.point_step = source.point_step
    output.row_step = source.row_step
    output.is_dense = source.is_dense
    data = bytearray(bytes(source.data))

    offsets = {field.name: int(field.offset) for field in source.fields}
    if not {"x", "y", "z"}.issubset(offsets):
        raise ValueError("PointCloud2 missing x/y/z fields")
    endian = ">" if source.is_bigendian else "<"
    total_points = min(int(source.width) * int(source.height), int(max_points))
    point_step = int(source.point_step)
    stats = PlannerCloudFilterStats(sampled_point_count=total_points)
    nan = float("nan")
    for index in range(total_points):
        base = index * point_step
        try:
            point = (
                struct.unpack_from(endian + "f", data, base + offsets["x"])[0],
                struct.unpack_from(endian + "f", data, base + offsets["y"])[0],
                struct.unpack_from(endian + "f", data, base + offsets["z"])[0],
            )
        except struct.error:
            break
        if not point_is_valid_lidar_return(point, max_valid_range_m):
            stats.removed_invalid_range += 1
            struct.pack_into(endian + "f", data, base + offsets["x"], nan)
            struct.pack_into(endian + "f", data, base + offsets["y"], nan)
            struct.pack_into(endian + "f", data, base + offsets["z"], nan)
            continue
        x, y, z = transform_point(point, transform)
        stats.finite_before_filter += 1
        stats._record_z(float(z), after_filter=False)
        remove_ground = planner_min_z is not None and z < planner_min_z
        remove_self = False
        if self_filter_center_xyz is not None and self_filter_radius_xy > 0.0:
            center_x, center_y, center_z = self_filter_center_xyz
            dz = z - center_z
            z_lower_ok = self_filter_z_min is None or dz >= self_filter_z_min
            z_upper_ok = self_filter_z_max is None or dz <= self_filter_z_max
            dx = x - center_x
            dy = y - center_y
            remove_self = (dx * dx + dy * dy) <= (self_filter_radius_xy * self_filter_radius_xy) and z_lower_ok and z_upper_ok
        if remove_ground or remove_self:
            if remove_ground:
                stats.removed_ground += 1
            if remove_self:
                stats.removed_self += 1
            struct.pack_into(endian + "f", data, base + offsets["x"], nan)
            struct.pack_into(endian + "f", data, base + offsets["y"], nan)
            struct.pack_into(endian + "f", data, base + offsets["z"], nan)
            continue
        stats.finite_after_filter += 1
        stats._record_z(float(z), after_filter=True)
        struct.pack_into(endian + "f", data, base + offsets["x"], float(x))
        struct.pack_into(endian + "f", data, base + offsets["y"], float(y))
        struct.pack_into(endian + "f", data, base + offsets["z"], float(z))
    output.data = bytes(data)
    output.is_dense = False if stats.removed_invalid_range or stats.removed_ground or stats.removed_self else source.is_dense
    return output, stats


def extract_transformed_finite_xyzi(
    source: Any,
    transform: Transform3D,
    max_points: int,
    *,
    max_valid_range_m: float | None,
    intensity_policy: str,
) -> list[tuple[float, float, float, float]]:
    offsets = {field.name: int(field.offset) for field in source.fields}
    if not {"x", "y", "z"}.issubset(offsets):
        raise ValueError("PointCloud2 missing x/y/z fields")
    intensity_offset = offsets.get("intensity")
    endian = ">" if source.is_bigendian else "<"
    total_points = min(int(source.width) * int(source.height), int(max_points))
    point_step = int(source.point_step)
    data = bytes(source.data)
    points: list[tuple[float, float, float, float]] = []
    for index in range(total_points):
        base = index * point_step
        try:
            point = (
                struct.unpack_from(endian + "f", data, base + offsets["x"])[0],
                struct.unpack_from(endian + "f", data, base + offsets["y"])[0],
                struct.unpack_from(endian + "f", data, base + offsets["z"])[0],
            )
        except struct.error:
            break
        if not point_is_valid_lidar_return(point, max_valid_range_m):
            continue
        x, y, z = transform_point(point, transform)
        if intensity_policy == "source" and intensity_offset is not None:
            try:
                intensity = struct.unpack_from(endian + "f", data, base + intensity_offset)[0]
            except struct.error:
                intensity = float(z)
            if not math.isfinite(intensity):
                intensity = float(z)
        elif intensity_policy == "range":
            intensity = math.sqrt(x * x + y * y + z * z)
        else:
            intensity = float(z)
        points.append((float(x), float(y), float(z), float(intensity)))
    return points


def make_xyzi_pointcloud2(
    points: list[tuple[float, float, float, float]],
    output_frame: str,
    stamp: Any,
    *,
    max_points: int,
) -> Any:
    from sensor_msgs.msg import PointCloud2, PointField
    from std_msgs.msg import Header

    retained = points[-max_points:] if max_points > 0 and len(points) > max_points else points
    output = PointCloud2()
    output.header = Header()
    output.header.stamp = stamp
    output.header.frame_id = output_frame
    output.height = 1
    output.width = len(retained)
    output.fields = [
        PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
        PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
        PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
        PointField(name="intensity", offset=12, datatype=PointField.FLOAT32, count=1),
    ]
    output.is_bigendian = False
    output.point_step = 16
    output.row_step = output.point_step * len(retained)
    output.is_dense = True
    data = bytearray(output.row_step)
    for index, (x, y, z, intensity) in enumerate(retained):
        struct.pack_into("<ffff", data, index * output.point_step, x, y, z, intensity)
    output.data = bytes(data)
    return output


def clone_pointcloud2_with_frame(source: Any, output_frame: str | None = None) -> Any:
    from sensor_msgs.msg import PointCloud2

    output = PointCloud2()
    output.header = source.header
    if output_frame:
        output.header.frame_id = output_frame
    output.height = source.height
    output.width = source.width
    output.fields = source.fields
    output.is_bigendian = source.is_bigendian
    output.point_step = source.point_step
    output.row_step = source.row_step
    output.data = bytes(source.data)
    output.is_dense = source.is_dense
    return output


def pointcloud2_to_livox_custom_msg(
    source: Any,
    output_frame: str,
    max_points: int,
    spark_livox_scan_lines: int,
    spark_livox_scan_rate_hz: float,
    max_valid_range_m: float | None,
) -> Any:
    from livox_ros_driver2.msg import CustomMsg, CustomPoint

    offsets = {field.name: int(field.offset) for field in source.fields}
    if not {"x", "y", "z"}.issubset(offsets):
        raise ValueError("PointCloud2 missing x/y/z fields")
    scan_lines = max(1, int(spark_livox_scan_lines))
    intensity_offset = offsets.get("intensity")
    endian = ">" if source.is_bigendian else "<"
    point_step = int(source.point_step)
    data = bytes(source.data)
    total_points = min(int(source.width) * int(source.height), int(max_points))
    source_width = max(1, int(source.width) or 1)
    source_height = max(1, int(source.height) or 1)
    valid_points: list[tuple[int, float, float, float, float]] = []
    for index in range(total_points):
        base = index * point_step
        if base + point_step > len(data):
            break
        try:
            x = struct.unpack_from(endian + "f", data, base + offsets["x"])[0]
            y = struct.unpack_from(endian + "f", data, base + offsets["y"])[0]
            z = struct.unpack_from(endian + "f", data, base + offsets["z"])[0]
            intensity = (
                struct.unpack_from(endian + "f", data, base + intensity_offset)[0]
                if intensity_offset is not None and base + intensity_offset + 4 <= len(data)
                else 0.0
            )
        except struct.error:
            break
        if not point_is_valid_lidar_return((x, y, z), max_valid_range_m):
            continue
        valid_points.append((index, float(x), float(y), float(z), float(intensity)))

    message = CustomMsg()
    message.header = source.header
    message.header.frame_id = output_frame
    message.timebase = int(source.header.stamp.sec) * 1_000_000_000 + int(source.header.stamp.nanosec)
    message.lidar_id = 0
    message.rsvd = [0, 0, 0]
    points = []
    denominator = max(1, len(valid_points) - 1)
    scan_period_ns = int(round(1_000_000_000.0 / float(spark_livox_scan_rate_hz)))
    for emitted_index, (source_index, x, y, z, intensity) in enumerate(valid_points):
        source_row = source_index // source_width
        if source_height >= scan_lines:
            line = min(scan_lines - 1, int(source_row * scan_lines / source_height))
        else:
            line = source_row % scan_lines
        point = CustomPoint()
        point.offset_time = int(round(emitted_index * scan_period_ns / denominator))
        point.x = x
        point.y = y
        point.z = z
        point.reflectivity = max(0, min(255, int(round(float(intensity)))))
        point.tag = 0x10
        point.line = int(line)
        points.append(point)
    message.points = points
    message.point_num = len(points)
    return message


def clone_imu_with_frame(source: Any, output_frame: str | None = None) -> Any:
    from sensor_msgs.msg import Imu

    output = Imu()
    output.header = source.header
    if output_frame:
        output.header.frame_id = output_frame
    output.orientation = source.orientation
    output.orientation_covariance = source.orientation_covariance
    output.angular_velocity = source.angular_velocity
    output.angular_velocity_covariance = source.angular_velocity_covariance
    output.linear_acceleration = source.linear_acceleration
    output.linear_acceleration_covariance = source.linear_acceleration_covariance
    return output


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lidar-input-topic", default="/mosim/gazebo/lidar_points/points")
    parser.add_argument("--imu-input-topic", default="/mosim/gazebo/imu")
    parser.add_argument("--fastlio-lidar-topic", default="/mosim/fastlio/livox/lidar")
    parser.add_argument("--fastlio-imu-topic", default="/mosim/fastlio/livox/imu")
    parser.add_argument("--spark-livox-custom-topic", default="/mosim/spark_fastlio/livox/lidar")
    parser.add_argument("--sunray-lidar-topic", default="/uav1/livox/lidar")
    parser.add_argument("--sunray-imu-topic", default="/uav1/livox/imu")
    parser.add_argument("--planner-global-points-topic", default="/uav1/global_points")
    parser.add_argument("--mosim-planner-global-points-topic", default="/mosim/planner/global_points")
    parser.add_argument("--review-map-cloud-topic", default="/mosim/review/lidar_points_map")
    parser.add_argument("--review-accumulated-cloud-topic", default="/mosim/review/lidar_points_map_accumulated")
    parser.add_argument("--review-accumulated-frames", type=int, default=10)
    parser.add_argument("--review-accumulated-max-points", type=int, default=120000)
    parser.add_argument(
        "--review-accumulated-intensity-policy",
        choices=("z", "range", "source"),
        default="z",
        help="Review-only intensity channel for accumulated map-frame cloud.",
    )
    parser.add_argument("--planner-odom-topic", default="/uav1/sunray/gazebo_pose")
    parser.add_argument("--mosim-planner-odom-topic", default="/mosim/planner/odom")
    parser.add_argument("--map-frame", default="map")
    parser.add_argument("--global-frame", default="map")
    parser.add_argument("--sensor-frame", default="sunray150_assembled/base_link/mid360_lidar")
    parser.add_argument("--imu-frame", default="sunray150_assembled/base_link/forward_imu")
    parser.add_argument("--odom-child-frame", default="uav1/base_link")
    parser.add_argument("--tf-lookup-timeout-s", type=float, default=0.2)
    parser.add_argument("--max-points-per-cloud", type=int, default=200000)
    parser.add_argument(
        "--max-valid-range-m",
        type=float,
        default=40.0,
        help=(
            "Maximum raw LiDAR Euclidean range treated as a valid return. Gazebo gpu_lidar can encode "
            "no-return rays as huge finite floats rather than NaN; these must be dropped before FAST-LIO, "
            "planner, or review clouds."
        ),
    )
    parser.add_argument(
        "--planner-filter-ground-min-z",
        type=float,
        default=None,
        help=(
            "Planner-cloud-only map-frame ground filter. Finite points below this z are written as NaN "
            "before publishing /global_points; raw LiDAR/FAST-LIO topics are unchanged."
        ),
    )
    parser.add_argument(
        "--planner-self-filter-radius-xy",
        type=float,
        default=0.0,
        help="Planner-cloud-only XY radius around the latest sensor TF translation to blank possible self/body hits.",
    )
    parser.add_argument(
        "--planner-self-filter-z-min",
        type=float,
        default=-0.6,
        help="Planner self-filter lower z offset relative to the latest sensor TF translation.",
    )
    parser.add_argument(
        "--planner-self-filter-z-max",
        type=float,
        default=0.4,
        help="Planner self-filter upper z offset relative to the latest sensor TF translation.",
    )
    parser.add_argument("--spark-livox-scan-lines", type=int, default=4)
    parser.add_argument("--spark-livox-scan-rate-hz", type=float, default=10.0)
    parser.add_argument("--odom-rate-hz", type=float, default=20.0)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--trace-jsonl", type=Path)
    parser.add_argument(
        "--disable-imu-output",
        action="store_true",
        help="Do not subscribe/publish IMU topics; use the separate high-rate IMU passthrough instead.",
    )
    parser.add_argument(
        "--disable-spark-livox-custom-output",
        action="store_true",
        help=(
            "Do not import livox_ros_driver2 or publish the Spark FAST-LIO CustomMsg output; "
            "use when only planner odom/global cloud topics are needed."
        ),
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def claim_boundary() -> list[str]:
    return [
        "FAST-LIO/planner input adapter only; no FAST-LIO node is launched",
        "PointCloud2 and IMU topic visibility does not prove FAST-LIO localization success",
        "Planner cloud and odometry-shape topics do not prove planner_ready or valid trajectory generation",
        "No setpoint publication, no command authority, no flight-control acknowledgement, and no closed_loop claim",
        "The first gate may use map-frame smoke odometry from same-run TF; real localization/odometry remains a later gate",
    ]


def dry_run(args: argparse.Namespace) -> int:
    report = {
        "schema": "mosim.fastlio_planner_input_adapter.dryrun.v1",
        "status": "dry_run_ready",
        "inputs": {
            "lidar": args.lidar_input_topic,
            "imu": args.imu_input_topic,
            "tf_source": "/tf and /tf_static",
        },
        "outputs": {
            "fastlio_lidar": args.fastlio_lidar_topic,
            "spark_livox_custom": (
                None if args.disable_spark_livox_custom_output else args.spark_livox_custom_topic
            ),
            "sunray_lidar": args.sunray_lidar_topic,
            "planner_global_points": args.planner_global_points_topic,
            "mosim_planner_global_points": args.mosim_planner_global_points_topic,
            "review_map_cloud": args.review_map_cloud_topic,
            "review_accumulated_cloud": args.review_accumulated_cloud_topic,
            "planner_odom": args.planner_odom_topic,
            "mosim_planner_odom": args.mosim_planner_odom_topic,
        },
        "imu_output": (
            {
                "enabled": False,
                "source": "disabled_for_separate_fastlio_imu_passthrough",
            }
            if args.disable_imu_output
            else {
                "enabled": True,
                "fastlio_imu": args.fastlio_imu_topic,
                "sunray_imu": args.sunray_imu_topic,
            }
        ),
        "frames": {
            "map_frame": args.map_frame,
            "global_frame": args.global_frame,
            "sensor_frame": args.sensor_frame,
            "imu_frame": args.imu_frame,
            "odom_child_frame": args.odom_child_frame,
        },
        "livox_custom_shape": {
            "enabled": not args.disable_spark_livox_custom_output,
            "spark_livox_scan_lines": args.spark_livox_scan_lines,
            "spark_livox_scan_rate_hz": args.spark_livox_scan_rate_hz,
            "line_policy": "source_pointcloud_row_bucketed_to_scan_lines",
            "offset_time_policy": "retained_point_ordinal_spread_over_one_scan_period_nanoseconds",
            "point_num_policy": "valid_finite_xyz_points_after_max_points_limit",
        },
        "planner_cloud_filter": {
            "scope": "planner_global_points_only",
            "ground_min_z": args.planner_filter_ground_min_z,
            "self_filter_radius_xy": args.planner_self_filter_radius_xy,
            "self_filter_z_min": args.planner_self_filter_z_min,
            "self_filter_z_max": args.planner_self_filter_z_max,
            "raw_lidar_topics_unchanged": True,
        },
        "review_accumulated_cloud": {
            "topic": args.review_accumulated_cloud_topic,
            "frames": args.review_accumulated_frames,
            "max_points": args.review_accumulated_max_points,
            "intensity_policy": args.review_accumulated_intensity_policy,
            "scope": "human_review_only_not_planner_input",
        },
        "claim_boundary": claim_boundary(),
    }
    write_json(args.output_json, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def run_node(args: argparse.Namespace) -> int:
    ensure_ros_log_dir()
    try:
        import rclpy
        import tf2_ros
        from nav_msgs.msg import Odometry
        from rclpy.duration import Duration
        from rclpy.node import Node
        from rclpy.time import Time
        from sensor_msgs.msg import Imu, PointCloud2
    except Exception as exc:
        report = {
            "schema": "mosim.fastlio_planner_input_adapter.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
            "claim_boundary": claim_boundary(),
        }
        write_json(args.output_json, report)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 1

    stop_requested = {"value": False}

    def request_stop(_signum: int, _frame: Any) -> None:
        stop_requested["value"] = True

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    rclpy.init()

    class FastlioPlannerInputAdapter(Node):
        def __init__(self) -> None:
            super().__init__("mosim_gazebo_fastlio_planner_input_adapter")
            self.started_at = time.time()
            self.last_lidar_stamp = None
            self.last_imu_stamp = None
            self.last_transform: Transform3D | None = None
            self.last_planner_cloud_filter_stats: PlannerCloudFilterStats | None = None
            self.review_accumulated_frames: deque[list[tuple[float, float, float, float]]] = deque(
                maxlen=max(1, int(args.review_accumulated_frames))
            )
            self.last_report_write_at = 0.0
            self.last_report_status: str | None = None
            self.report_interval_s = 1.0
            self.counts = {
                "lidar_received": 0,
                "imu_received": 0,
                "fastlio_lidar_published": 0,
                "fastlio_imu_published": 0,
                "spark_livox_custom_published": 0,
                "sunray_lidar_published": 0,
                "sunray_imu_published": 0,
                "planner_global_points_published": 0,
                "mosim_planner_global_points_published": 0,
                "review_map_cloud_published": 0,
                "review_accumulated_cloud_published": 0,
                "review_accumulated_last_point_count": 0,
                "planner_odom_published": 0,
                "mosim_planner_odom_published": 0,
                "tf_lookup_failures": 0,
                "frame_mismatch_count": 0,
                "planner_cloud_finite_before_filter": 0,
                "planner_cloud_finite_after_filter": 0,
                "planner_cloud_removed_invalid_range": 0,
                "planner_cloud_removed_ground": 0,
                "planner_cloud_removed_self": 0,
            }
            self.tf_buffer = tf2_ros.Buffer()
            self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
            self.fastlio_lidar_pub = self.create_publisher(PointCloud2, args.fastlio_lidar_topic, 10)
            self.spark_livox_custom_pub = None
            if not args.disable_spark_livox_custom_output:
                from livox_ros_driver2.msg import CustomMsg

                self.spark_livox_custom_pub = self.create_publisher(CustomMsg, args.spark_livox_custom_topic, 10)
            self.fastlio_imu_pub = (
                None if args.disable_imu_output else self.create_publisher(Imu, args.fastlio_imu_topic, 10)
            )
            self.sunray_lidar_pub = self.create_publisher(PointCloud2, args.sunray_lidar_topic, 10)
            self.sunray_imu_pub = (
                None if args.disable_imu_output else self.create_publisher(Imu, args.sunray_imu_topic, 10)
            )
            self.planner_global_points_pub = self.create_publisher(PointCloud2, args.planner_global_points_topic, 10)
            self.mosim_planner_global_points_pub = self.create_publisher(
                PointCloud2, args.mosim_planner_global_points_topic, 10
            )
            self.review_map_cloud_pub = self.create_publisher(PointCloud2, args.review_map_cloud_topic, 10)
            self.review_accumulated_cloud_pub = self.create_publisher(
                PointCloud2, args.review_accumulated_cloud_topic, 10
            )
            self.planner_odom_pub = self.create_publisher(Odometry, args.planner_odom_topic, 10)
            self.mosim_planner_odom_pub = self.create_publisher(Odometry, args.mosim_planner_odom_topic, 10)
            self.create_subscription(PointCloud2, args.lidar_input_topic, self.handle_lidar, 10)
            if not args.disable_imu_output:
                self.create_subscription(Imu, args.imu_input_topic, self.handle_imu, 50)
            odom_period = 1.0 / args.odom_rate_hz if args.odom_rate_hz > 0 else 0.05
            self.create_timer(odom_period, self.publish_odom_from_last_tf)
            self.write_report("started", force=True)

        def lookup_sensor_to_map(self, stamp: Any) -> Transform3D | None:
            try:
                transform_msg = self.tf_buffer.lookup_transform(
                    args.map_frame,
                    args.sensor_frame,
                    Time.from_msg(stamp),
                    timeout=Duration(seconds=float(args.tf_lookup_timeout_s)),
                )
            except Exception as exc:
                self.counts["tf_lookup_failures"] += 1
                if self.counts["tf_lookup_failures"] <= 5:
                    self.get_logger().warning(f"TF lookup failed {args.sensor_frame}->{args.map_frame}: {exc}")
                return None
            transform = transform_from_ros_message(transform_msg.transform)
            self.last_transform = transform
            return transform

        def handle_lidar(self, message: Any) -> None:
            self.counts["lidar_received"] += 1
            self.last_lidar_stamp = message.header.stamp
            input_frame = str(message.header.frame_id)
            if input_frame != args.sensor_frame:
                self.counts["frame_mismatch_count"] += 1
                if self.counts["frame_mismatch_count"] <= 5:
                    self.get_logger().warning(
                        f"LiDAR frame mismatch: expected {args.sensor_frame!r}, got {input_frame!r}"
                    )
            fastlio_message = clone_pointcloud2_with_frame(message, args.sensor_frame)
            self.fastlio_lidar_pub.publish(fastlio_message)
            if self.spark_livox_custom_pub is not None:
                self.spark_livox_custom_pub.publish(
                    pointcloud2_to_livox_custom_msg(
                        message,
                        args.sensor_frame,
                        args.max_points_per_cloud,
                        args.spark_livox_scan_lines,
                        args.spark_livox_scan_rate_hz,
                        args.max_valid_range_m,
                    )
                )
                self.counts["spark_livox_custom_published"] += 1
            self.sunray_lidar_pub.publish(clone_pointcloud2_with_frame(message, args.sensor_frame))
            self.counts["fastlio_lidar_published"] += 1
            self.counts["sunray_lidar_published"] += 1

            transform = self.lookup_sensor_to_map(message.header.stamp)
            if transform is not None:
                review_cloud, _review_stats = transformed_pointcloud2(
                    message,
                    transform,
                    args.global_frame,
                    args.max_points_per_cloud,
                    max_valid_range_m=args.max_valid_range_m,
                )
                self.review_map_cloud_pub.publish(review_cloud)
                self.counts["review_map_cloud_published"] += 1
                review_points = extract_transformed_finite_xyzi(
                    message,
                    transform,
                    args.max_points_per_cloud,
                    max_valid_range_m=args.max_valid_range_m,
                    intensity_policy=args.review_accumulated_intensity_policy,
                )
                self.review_accumulated_frames.append(review_points)
                accumulated_points = [
                    point for frame_points in self.review_accumulated_frames for point in frame_points
                ]
                accumulated_cloud = make_xyzi_pointcloud2(
                    accumulated_points,
                    args.global_frame,
                    message.header.stamp,
                    max_points=args.review_accumulated_max_points,
                )
                self.review_accumulated_cloud_pub.publish(accumulated_cloud)
                self.counts["review_accumulated_cloud_published"] += 1
                self.counts["review_accumulated_last_point_count"] = int(accumulated_cloud.width)
                global_cloud, filter_stats = transformed_pointcloud2(
                    message,
                    transform,
                    args.global_frame,
                    args.max_points_per_cloud,
                    max_valid_range_m=args.max_valid_range_m,
                    planner_min_z=args.planner_filter_ground_min_z,
                    self_filter_center_xyz=transform.translation_xyz,
                    self_filter_radius_xy=args.planner_self_filter_radius_xy,
                    self_filter_z_min=args.planner_self_filter_z_min,
                    self_filter_z_max=args.planner_self_filter_z_max,
                )
                self.last_planner_cloud_filter_stats = filter_stats
                self.counts["planner_cloud_finite_before_filter"] += filter_stats.finite_before_filter
                self.counts["planner_cloud_finite_after_filter"] += filter_stats.finite_after_filter
                self.counts["planner_cloud_removed_invalid_range"] += filter_stats.removed_invalid_range
                self.counts["planner_cloud_removed_ground"] += filter_stats.removed_ground
                self.counts["planner_cloud_removed_self"] += filter_stats.removed_self
                self.planner_global_points_pub.publish(global_cloud)
                self.mosim_planner_global_points_pub.publish(
                    clone_pointcloud2_with_frame(global_cloud, args.global_frame)
                )
                self.counts["planner_global_points_published"] += 1
                self.counts["mosim_planner_global_points_published"] += 1
            self.write_report("active")

        def handle_imu(self, message: Any) -> None:
            self.counts["imu_received"] += 1
            self.last_imu_stamp = message.header.stamp
            output = clone_imu_with_frame(message, args.imu_frame or None)
            if self.fastlio_imu_pub is None or self.sunray_imu_pub is None:
                return
            self.fastlio_imu_pub.publish(output)
            self.sunray_imu_pub.publish(output)
            self.counts["fastlio_imu_published"] += 1
            self.counts["sunray_imu_published"] += 1
            self.write_report("active")

        def publish_odom_from_last_tf(self) -> None:
            transform = self.last_transform
            if transform is None:
                try:
                    transform_msg = self.tf_buffer.lookup_transform(
                        args.map_frame,
                        args.sensor_frame,
                        Time(),
                        timeout=Duration(seconds=float(args.tf_lookup_timeout_s)),
                    )
                except Exception:
                    self.counts["tf_lookup_failures"] += 1
                    return
                transform = transform_from_ros_message(transform_msg.transform)
                self.last_transform = transform
            message = Odometry()
            message.header.stamp = self.get_clock().now().to_msg()
            message.header.frame_id = args.global_frame
            message.child_frame_id = args.odom_child_frame
            message.pose.pose.position.x = transform.translation_xyz[0]
            message.pose.pose.position.y = transform.translation_xyz[1]
            message.pose.pose.position.z = transform.translation_xyz[2]
            x, y, z, w = transform.rotation_xyzw
            message.pose.pose.orientation.x = x
            message.pose.pose.orientation.y = y
            message.pose.pose.orientation.z = z
            message.pose.pose.orientation.w = w
            self.planner_odom_pub.publish(message)
            self.mosim_planner_odom_pub.publish(message)
            self.counts["planner_odom_published"] += 1
            self.counts["mosim_planner_odom_published"] += 1

        def write_report(self, status: str, force: bool = False) -> None:
            now = time.time()
            if (
                not force
                and self.last_report_status == status
                and now - self.last_report_write_at < self.report_interval_s
            ):
                return
            self.last_report_status = status
            self.last_report_write_at = now
            report = {
                "schema": "mosim.fastlio_planner_input_adapter.v1",
                "status": status,
                "node": "mosim_gazebo_fastlio_planner_input_adapter",
                "uptime_s": round(now - self.started_at, 3),
                "inputs": {
                    "lidar": args.lidar_input_topic,
                    "imu": args.imu_input_topic,
                    "tf_source": "/tf and /tf_static",
                },
                "outputs": {
                    "fastlio_lidar": args.fastlio_lidar_topic,
                    "spark_livox_custom": (
                        None if args.disable_spark_livox_custom_output else args.spark_livox_custom_topic
                    ),
                    "sunray_lidar": args.sunray_lidar_topic,
                    "planner_global_points": args.planner_global_points_topic,
                    "mosim_planner_global_points": args.mosim_planner_global_points_topic,
                    "review_map_cloud": args.review_map_cloud_topic,
                    "review_accumulated_cloud": args.review_accumulated_cloud_topic,
                    "planner_odom": args.planner_odom_topic,
                    "mosim_planner_odom": args.mosim_planner_odom_topic,
                },
                "imu_output": (
                    {
                        "enabled": False,
                        "source": "disabled_for_separate_fastlio_imu_passthrough",
                    }
                    if args.disable_imu_output
                    else {
                        "enabled": True,
                        "fastlio_imu": args.fastlio_imu_topic,
                        "sunray_imu": args.sunray_imu_topic,
                    }
                ),
                "frames": {
                    "map_frame": args.map_frame,
                    "global_frame": args.global_frame,
                    "sensor_frame": args.sensor_frame,
                    "imu_frame": args.imu_frame,
                    "odom_child_frame": args.odom_child_frame,
                    "global_frame_policy": "first_gate_uses_map_frame_for_planner_cloud_and_odom",
                },
                "livox_custom_shape": {
                    "enabled": not args.disable_spark_livox_custom_output,
                    "spark_livox_scan_lines": args.spark_livox_scan_lines,
                    "spark_livox_scan_rate_hz": args.spark_livox_scan_rate_hz,
                    "line_policy": "source_pointcloud_row_bucketed_to_scan_lines",
                    "offset_time_policy": "retained_point_ordinal_spread_over_one_scan_period_nanoseconds",
                    "point_num_policy": "valid_finite_xyz_points_after_max_points_limit",
                },
                "planner_cloud_filter": {
                    "scope": "planner_global_points_only",
                    "ground_min_z": args.planner_filter_ground_min_z,
                    "self_filter_radius_xy": args.planner_self_filter_radius_xy,
                    "self_filter_z_min": args.planner_self_filter_z_min,
                    "self_filter_z_max": args.planner_self_filter_z_max,
                    "raw_lidar_topics_unchanged": True,
                    "max_valid_range_m": args.max_valid_range_m,
                    "last_stats": (
                        self.last_planner_cloud_filter_stats.to_dict()
                        if self.last_planner_cloud_filter_stats is not None
                        else None
                    ),
                },
                "review_accumulated_cloud": {
                    "topic": args.review_accumulated_cloud_topic,
                    "frames": args.review_accumulated_frames,
                    "max_points": args.review_accumulated_max_points,
                    "intensity_policy": args.review_accumulated_intensity_policy,
                    "scope": "human_review_only_not_planner_input",
                    "last_point_count": self.counts["review_accumulated_last_point_count"],
                },
                "counts": self.counts,
                "last_transform": (
                    {
                        "translation_xyz": list(self.last_transform.translation_xyz),
                        "rotation_xyzw": list(self.last_transform.rotation_xyzw),
                    }
                    if self.last_transform is not None
                    else None
                ),
                "claim_boundary": claim_boundary(),
            }
            write_json(args.output_json, report)
            append_jsonl(args.trace_jsonl, report)

    node = FastlioPlannerInputAdapter()
    try:
        while rclpy.ok() and not stop_requested["value"]:
            rclpy.spin_once(node, timeout_sec=0.2)
    finally:
        node.write_report("stopped" if stop_requested["value"] else "shutdown", force=True)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.tf_lookup_timeout_s <= 0:
        raise SystemExit("--tf-lookup-timeout-s must be positive")
    if args.max_points_per_cloud <= 0:
        raise SystemExit("--max-points-per-cloud must be positive")
    if args.planner_self_filter_radius_xy < 0:
        raise SystemExit("--planner-self-filter-radius-xy must be non-negative")
    if args.review_accumulated_frames <= 0:
        raise SystemExit("--review-accumulated-frames must be positive")
    if args.review_accumulated_max_points <= 0:
        raise SystemExit("--review-accumulated-max-points must be positive")
    if args.spark_livox_scan_lines <= 0:
        raise SystemExit("--spark-livox-scan-lines must be positive")
    if args.spark_livox_scan_rate_hz <= 0:
        raise SystemExit("--spark-livox-scan-rate-hz must be positive")
    if args.odom_rate_hz <= 0:
        raise SystemExit("--odom-rate-hz must be positive")
    if args.dry_run:
        return dry_run(args)
    return run_node(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
