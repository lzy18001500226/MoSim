#!/usr/bin/env python3
"""Convert a ROS2 PointCloud2 stream into simple local voxel/grid map topics.

This is the first MoSim local-map adapter for the Gazebo+ROS2 validation lane.
It is intentionally simple: occupied voxels are derived directly from the input
cloud. It does not perform localization, ESDF generation, planning, or
closed-loop control.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import struct
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


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


@dataclass(frozen=True)
class Voxel:
    ix: int
    iy: int
    iz: int


@dataclass(frozen=True)
class Transform3D:
    translation_xyz: tuple[float, float, float]
    rotation_xyzw: tuple[float, float, float, float]


@dataclass(frozen=True)
class LocalMapConfig:
    voxel_size_m: float
    grid_resolution_m: float
    local_radius_m: float
    z_min_m: float
    z_max_m: float
    ground_min_z_m: float | None = None
    self_filter_radius_xy_m: float = 0.0
    self_filter_z_min_m: float | None = None
    self_filter_z_max_m: float | None = None
    center_x_m: float = 0.0
    center_y_m: float = 0.0
    center_z_m: float = 0.0


@dataclass(frozen=True)
class GridProjection:
    resolution_m: float
    width: int
    height: int
    origin_x_m: float
    origin_y_m: float
    data: list[int]


def local_map_config_from_args(
    args: argparse.Namespace,
    center_xyz: tuple[float, float, float] | None = None,
) -> LocalMapConfig:
    center = center_xyz or (0.0, 0.0, 0.0)
    return LocalMapConfig(
        voxel_size_m=float(args.voxel_size_m),
        grid_resolution_m=float(args.grid_resolution_m),
        local_radius_m=float(args.local_radius_m),
        z_min_m=float(args.z_min_m),
        z_max_m=float(args.z_max_m),
        ground_min_z_m=args.ground_min_z_m,
        self_filter_radius_xy_m=float(args.self_filter_radius_xy_m),
        self_filter_z_min_m=args.self_filter_z_min_m,
        self_filter_z_max_m=args.self_filter_z_max_m,
        center_x_m=float(center[0]),
        center_y_m=float(center[1]),
        center_z_m=float(center[2]),
    )


def dry_run(args: argparse.Namespace) -> int:
    expected_input_frame = args.expected_input_frame or args.map_frame
    report = {
        "schema": "mosim.pointcloud_to_local_voxel_map_dryrun.v1",
        "mode": "dry_run_static_contract",
        "input_topic": args.input_topic,
        "voxel_topic": args.voxel_topic,
        "grid_topic": args.grid_topic,
        "frame_id": args.map_frame,
        "input_frame_policy": args.input_frame_policy,
        "expected_input_frame": expected_input_frame,
        "tf_lookup_timeout_s": args.tf_lookup_timeout_s,
        "local_map_center_source": args.local_map_center_source,
        "voxel_size_m": args.voxel_size_m,
        "local_radius_m": args.local_radius_m,
        "z_bounds_m": [args.z_min_m, args.z_max_m],
        "ground_min_z_m": args.ground_min_z_m,
        "self_filter": {
            "radius_xy_m": args.self_filter_radius_xy_m,
            "z_min_m": args.self_filter_z_min_m,
            "z_max_m": args.self_filter_z_max_m,
        },
        "max_points_per_cloud": args.max_points_per_cloud,
        "publish_rate_limit_hz": args.publish_rate_limit_hz,
        "outputs": {
            "local_voxels": "sensor_msgs/msg/PointCloud2 occupied voxel centers",
            "local_2d_grid": "nav_msgs/msg/OccupancyGrid projected occupied cells",
        },
        "claim_boundary": [
            "dry-run only; no ROS2 graph was started",
            "raw input PointCloud2 is unchanged; ground/self filters apply only to local occupancy outputs",
            "direct occupied-voxel adapter only; no FAST-LIO or localization success is claimed",
            "no-TF mode requires the input PointCloud2 header.frame_id to match the map frame",
            "TF mode requires a same-run transform from the input PointCloud2 frame to the map frame",
            "planner handoff requires a later run manifest proving topic rates, TF, frame, and consumer input",
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def point_field_offsets(msg: Any) -> dict[str, tuple[int, int]]:
    offsets: dict[str, tuple[int, int]] = {}
    for field in msg.fields:
        offsets[field.name] = (int(field.offset), int(field.datatype))
    for name in ("x", "y", "z"):
        if name not in offsets:
            raise ValueError(f"PointCloud2 missing {name} field")
    return offsets


def iter_xyz_points(msg: Any, max_points: int) -> Iterable[tuple[float, float, float]]:
    offsets = point_field_offsets(msg)
    x_offset = offsets["x"][0]
    y_offset = offsets["y"][0]
    z_offset = offsets["z"][0]
    point_step = int(msg.point_step)
    total = min(int(msg.width) * int(msg.height), max_points)
    data = bytes(msg.data)
    endian = ">" if msg.is_bigendian else "<"
    for index in range(total):
        base = index * point_step
        try:
            x = struct.unpack_from(endian + "f", data, base + x_offset)[0]
            y = struct.unpack_from(endian + "f", data, base + y_offset)[0]
            z = struct.unpack_from(endian + "f", data, base + z_offset)[0]
        except struct.error:
            break
        if math.isfinite(x) and math.isfinite(y) and math.isfinite(z):
            yield (x, y, z)


def voxel_center(voxel: Voxel, voxel_size_m: float) -> tuple[float, float, float]:
    return (
        (voxel.ix + 0.5) * voxel_size_m,
        (voxel.iy + 0.5) * voxel_size_m,
        (voxel.iz + 0.5) * voxel_size_m,
    )


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

    # q * p * q^-1, expanded to avoid an optional numpy dependency.
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


def transform_points(points: Iterable[tuple[float, float, float]], transform: Transform3D) -> Iterable[tuple[float, float, float]]:
    for point in points:
        yield transform_point(point, transform)


def transform_from_ros_message(transform_msg: Any) -> Transform3D:
    translation = transform_msg.translation
    rotation = transform_msg.rotation
    return Transform3D(
        translation_xyz=(float(translation.x), float(translation.y), float(translation.z)),
        rotation_xyzw=(float(rotation.x), float(rotation.y), float(rotation.z), float(rotation.w)),
    )


def voxelize_points(points: Iterable[tuple[float, float, float]], config: LocalMapConfig) -> set[Voxel]:
    voxels: set[Voxel] = set()
    radius_sq = config.local_radius_m * config.local_radius_m
    size = config.voxel_size_m
    for x, y, z in points:
        dx = x - config.center_x_m
        dy = y - config.center_y_m
        dz = z - config.center_z_m
        if dx * dx + dy * dy > radius_sq:
            continue
        if dz < config.z_min_m or dz > config.z_max_m:
            continue
        if config.ground_min_z_m is not None and z < config.ground_min_z_m:
            continue
        if config.self_filter_radius_xy_m > 0.0:
            self_radius_sq = config.self_filter_radius_xy_m * config.self_filter_radius_xy_m
            z_lower_ok = config.self_filter_z_min_m is None or dz >= config.self_filter_z_min_m
            z_upper_ok = config.self_filter_z_max_m is None or dz <= config.self_filter_z_max_m
            if dx * dx + dy * dy <= self_radius_sq and z_lower_ok and z_upper_ok:
                continue
        voxels.add(Voxel(math.floor(x / size), math.floor(y / size), math.floor(z / size)))
    return voxels


def voxelize(
    points: Iterable[tuple[float, float, float]],
    args: argparse.Namespace,
    center_xyz: tuple[float, float, float] | None = None,
) -> set[Voxel]:
    return voxelize_points(points, local_map_config_from_args(args, center_xyz=center_xyz))


def project_voxels_to_grid(voxels: set[Voxel], config: LocalMapConfig) -> GridProjection:
    resolution = config.grid_resolution_m
    width = int(math.ceil((2.0 * config.local_radius_m) / resolution))
    height = width
    origin_x = config.center_x_m - config.local_radius_m
    origin_y = config.center_y_m - config.local_radius_m
    data = [-1] * (width * height)
    for voxel in voxels:
        x, y, _ = voxel_center(voxel, config.voxel_size_m)
        gx = int(math.floor((x - origin_x) / resolution))
        gy = int(math.floor((y - origin_y) / resolution))
        if 0 <= gx < width and 0 <= gy < height:
            data[gy * width + gx] = 100
    return GridProjection(
        resolution_m=resolution,
        width=width,
        height=height,
        origin_x_m=origin_x,
        origin_y_m=origin_y,
        data=data,
    )


def publish_ros2(args: argparse.Namespace) -> int:
    ensure_ros_log_dir()
    try:
        import rclpy  # type: ignore
        from nav_msgs.msg import OccupancyGrid  # type: ignore
        from rclpy.duration import Duration  # type: ignore
        from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy  # type: ignore
        from rclpy.time import Time  # type: ignore
        from sensor_msgs.msg import PointCloud2, PointField  # type: ignore
        from std_msgs.msg import Header  # type: ignore
    except ImportError as exc:
        print("ROS2 Python modules are unavailable. Source /opt/ros/humble/setup.bash first.", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 2

    qos = QoSProfile(
        history=HistoryPolicy.KEEP_LAST,
        depth=4,
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
    )
    rclpy.init()
    node = rclpy.create_node("mosim_pointcloud_to_local_voxel_map")
    voxel_pub = node.create_publisher(PointCloud2, args.voxel_topic, qos)
    grid_pub = node.create_publisher(OccupancyGrid, args.grid_topic, qos)
    tf_buffer = None
    tf_listener = None
    if args.input_frame_policy == "transform_input_frame_to_map_with_tf":
        try:
            import tf2_ros  # type: ignore
        except ImportError as exc:
            print("tf2_ros is unavailable; TF transform mode cannot run.", file=sys.stderr)
            print(str(exc), file=sys.stderr)
            node.destroy_node()
            if rclpy.ok():
                rclpy.shutdown()
            return 2
        tf_buffer = tf2_ros.Buffer()
        tf_listener = tf2_ros.TransformListener(tf_buffer, node)
    state = {
        "published": 0,
        "last_publish_time": 0.0,
        "frame_mismatch_count": 0,
        "tf_lookup_failure_count": 0,
    }
    expected_input_frame = args.expected_input_frame or args.map_frame

    def make_voxel_cloud(input_msg: Any, voxels: set[Voxel]) -> Any:
        size = args.voxel_size_m
        data = bytearray()
        for voxel in sorted(voxels, key=lambda item: (item.ix, item.iy, item.iz)):
            x, y, z = voxel_center(voxel, size)
            data.extend(struct.pack("<ffff", float(x), float(y), float(z), 1.0))
        msg = PointCloud2()
        msg.header = Header(stamp=input_msg.header.stamp, frame_id=args.map_frame)
        msg.height = 1
        msg.width = len(voxels)
        msg.fields = [
            PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name="intensity", offset=12, datatype=PointField.FLOAT32, count=1),
        ]
        msg.is_bigendian = False
        msg.point_step = 16
        msg.row_step = msg.point_step * msg.width
        msg.data = bytes(data)
        msg.is_dense = True
        return msg

    def make_grid(input_msg: Any, voxels: set[Voxel], center_xyz: tuple[float, float, float] | None) -> Any:
        projection = project_voxels_to_grid(voxels, local_map_config_from_args(args, center_xyz=center_xyz))
        msg = OccupancyGrid()
        msg.header = Header(stamp=input_msg.header.stamp, frame_id=args.map_frame)
        msg.info.resolution = float(projection.resolution_m)
        msg.info.width = projection.width
        msg.info.height = projection.height
        msg.info.origin.position.x = float(projection.origin_x_m)
        msg.info.origin.position.y = float(projection.origin_y_m)
        msg.info.origin.position.z = 0.0
        msg.info.origin.orientation.w = 1.0
        msg.data = projection.data
        return msg

    def on_cloud(msg: Any) -> None:
        input_frame = str(getattr(msg.header, "frame_id", ""))
        points: Iterable[tuple[float, float, float]] = iter_xyz_points(msg, args.max_points_per_cloud)
        local_center_xyz: tuple[float, float, float] | None = None
        if args.input_frame_policy == "require_input_frame_equals_map_frame" and input_frame != expected_input_frame:
            state["frame_mismatch_count"] += 1
            if state["frame_mismatch_count"] <= 5:
                print(
                    "input PointCloud2 frame mismatch: "
                    f"expected {expected_input_frame!r}, got {input_frame!r}; "
                    "no-TF local-map adapter will not publish",
                    file=sys.stderr,
                    flush=True,
                )
            if args.once:
                rclpy.shutdown()
            return
        if args.input_frame_policy == "transform_input_frame_to_map_with_tf":
            if not input_frame:
                state["frame_mismatch_count"] += 1
                if state["frame_mismatch_count"] <= 5:
                    print("input PointCloud2 frame_id is empty; TF transform cannot be resolved", file=sys.stderr, flush=True)
                if args.once:
                    rclpy.shutdown()
                return
            if args.expected_input_frame and input_frame != args.expected_input_frame:
                state["frame_mismatch_count"] += 1
                if state["frame_mismatch_count"] <= 5:
                    print(
                        "input PointCloud2 frame mismatch: "
                        f"expected {args.expected_input_frame!r}, got {input_frame!r}; "
                        "TF local-map adapter will not publish",
                        file=sys.stderr,
                        flush=True,
                    )
                if args.once:
                    rclpy.shutdown()
                return
            if input_frame != args.map_frame:
                try:
                    assert tf_buffer is not None
                    transform_msg = tf_buffer.lookup_transform(
                        args.map_frame,
                        input_frame,
                        Time.from_msg(msg.header.stamp),
                        timeout=Duration(seconds=float(args.tf_lookup_timeout_s)),
                    )
                except Exception as exc:
                    state["tf_lookup_failure_count"] += 1
                    if state["tf_lookup_failure_count"] <= 5:
                        print(
                            "input PointCloud2 TF lookup failed: "
                            f"{input_frame!r} -> {args.map_frame!r}: {exc}",
                            file=sys.stderr,
                            flush=True,
                        )
                    if args.once:
                        rclpy.shutdown()
                    return
                transform = transform_from_ros_message(transform_msg.transform)
                points = transform_points(points, transform)
                if args.local_map_center_source == "tf_translation_in_map":
                    local_center_xyz = transform.translation_xyz
        now = node.get_clock().now().nanoseconds / 1_000_000_000.0
        min_period = 1.0 / args.publish_rate_limit_hz if args.publish_rate_limit_hz > 0 else 0.0
        if now - state["last_publish_time"] < min_period:
            return
        state["last_publish_time"] = now
        voxels = voxelize(points, args, center_xyz=local_center_xyz)
        voxel_pub.publish(make_voxel_cloud(msg, voxels))
        grid_pub.publish(make_grid(msg, voxels, local_center_xyz))
        state["published"] += 1
        if args.once and state["published"] >= 1:
            rclpy.shutdown()

    node.create_subscription(PointCloud2, args.input_topic, on_cloud, qos)
    try:
        rclpy.spin(node)
    except rclpy.executors.ExternalShutdownException:
        pass
    finally:
        _ = tf_listener
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-topic", default="/mosim/gazebo/lidar_points")
    parser.add_argument("--voxel-topic", default="/mosim/local_occupancy_voxels")
    parser.add_argument("--grid-topic", default="/mosim/local_occupancy_grid")
    parser.add_argument("--map-frame", default="map")
    parser.add_argument("--voxel-size-m", type=float, default=0.20)
    parser.add_argument("--grid-resolution-m", type=float, default=0.20)
    parser.add_argument("--local-radius-m", type=float, default=12.0)
    parser.add_argument("--z-min-m", type=float, default=-1.0)
    parser.add_argument("--z-max-m", type=float, default=5.0)
    parser.add_argument(
        "--ground-min-z-m",
        type=float,
        default=None,
        help="Map-frame ground filter for local occupancy outputs only. Raw LiDAR input is not modified.",
    )
    parser.add_argument(
        "--self-filter-radius-xy-m",
        type=float,
        default=0.0,
        help="XY radius around the local-map center to suppress possible self/body hits in occupancy outputs only.",
    )
    parser.add_argument(
        "--self-filter-z-min-m",
        type=float,
        default=-0.6,
        help="Lower z offset for self filtering relative to the local-map center.",
    )
    parser.add_argument(
        "--self-filter-z-max-m",
        type=float,
        default=0.4,
        help="Upper z offset for self filtering relative to the local-map center.",
    )
    parser.add_argument("--max-points-per-cloud", type=int, default=200000)
    parser.add_argument("--publish-rate-limit-hz", type=float, default=5.0)
    parser.add_argument(
        "--input-frame-policy",
        choices=[
            "require_input_frame_equals_map_frame",
            "transform_input_frame_to_map_with_tf",
            "allow_input_frame_without_tf_debug",
        ],
        default="require_input_frame_equals_map_frame",
    )
    parser.add_argument("--expected-input-frame", default="")
    parser.add_argument("--tf-lookup-timeout-s", type=float, default=0.20)
    parser.add_argument(
        "--local-map-center-source",
        choices=["map_origin", "tf_translation_in_map"],
        default="map_origin",
    )
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.voxel_size_m <= 0 or args.grid_resolution_m <= 0 or args.local_radius_m <= 0:
        raise SystemExit("voxel-size-m, grid-resolution-m, and local-radius-m must be positive")
    if args.self_filter_radius_xy_m < 0:
        raise SystemExit("--self-filter-radius-xy-m must be non-negative")
    if args.dry_run:
        return dry_run(args)
    return publish_ros2(args)


if __name__ == "__main__":
    raise SystemExit(main())
