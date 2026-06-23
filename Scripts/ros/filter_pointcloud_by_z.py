#!/usr/bin/env python3
"""Publish a review-only PointCloud2 filtered by map-frame z.

This is for RViz review surfaces. It does not modify the source planner or EGO
map topics and must not be used as planner input unless a future workflow
explicitly promotes it.
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


def write_json(path: str | Path | None, payload: dict[str, Any]) -> None:
    if path is None:
        return
    output = project_path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def compact_xyzi_by_z(source: Any, min_z: float, max_points: int) -> tuple[Any, dict[str, Any]]:
    from sensor_msgs.msg import PointCloud2, PointField
    from std_msgs.msg import Header

    offsets = {field.name: int(field.offset) for field in source.fields}
    if not {"x", "y", "z"}.issubset(offsets):
        raise ValueError("PointCloud2 missing x/y/z fields")
    intensity_offset = offsets.get("intensity")
    endian = ">" if source.is_bigendian else "<"
    source_count = int(source.width) * int(source.height)
    total = min(source_count, int(max_points))
    point_step = int(source.point_step)
    data = bytes(source.data)

    retained: list[tuple[float, float, float, float]] = []
    finite_count = 0
    dropped_below_min_z = 0
    for index in range(total):
        base = index * point_step
        try:
            x = struct.unpack_from(endian + "f", data, base + offsets["x"])[0]
            y = struct.unpack_from(endian + "f", data, base + offsets["y"])[0]
            z = struct.unpack_from(endian + "f", data, base + offsets["z"])[0]
            intensity = (
                struct.unpack_from(endian + "f", data, base + intensity_offset)[0]
                if intensity_offset is not None and base + intensity_offset + 4 <= len(data)
                else z
            )
        except struct.error:
            break
        if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
            continue
        finite_count += 1
        if z < min_z:
            dropped_below_min_z += 1
            continue
        if not math.isfinite(intensity):
            intensity = z
        retained.append((float(x), float(y), float(z), float(intensity)))

    output = PointCloud2()
    output.header = Header()
    output.header.stamp = source.header.stamp
    output.header.frame_id = source.header.frame_id
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
    packed = bytearray(output.row_step)
    for index, point in enumerate(retained):
        struct.pack_into("<ffff", packed, index * output.point_step, *point)
    output.data = bytes(packed)
    stats = {
        "source_point_count": source_count,
        "sampled_point_count": total,
        "finite_point_count": finite_count,
        "retained_point_count": len(retained),
        "dropped_below_min_z": dropped_below_min_z,
        "min_z": min_z,
        "source_frame_id": str(source.header.frame_id),
    }
    return output, stats


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-topic", default="/grid_map/occupancy_inflate")
    parser.add_argument("--output-topic", default="/mosim/review/occupancy_inflate_above_floor")
    parser.add_argument("--min-z", type=float, default=0.95)
    parser.add_argument("--max-points", type=int, default=250000)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.max_points <= 0:
        raise SystemExit("--max-points must be positive")
    if args.dry_run:
        payload = {
            "schema": "mosim.filter_pointcloud_by_z.dryrun.v1",
            "status": "dry_run_ready",
            "input_topic": args.input_topic,
            "output_topic": args.output_topic,
            "min_z": args.min_z,
            "scope": "review_only_not_planner_input",
        }
        write_json(args.output_json, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    ensure_ros_log_dir()
    stop_requested = {"value": False}

    def request_stop(_signum: int, _frame: Any) -> None:
        stop_requested["value"] = True

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)

    try:
        import rclpy
        from rclpy.node import Node
        from sensor_msgs.msg import PointCloud2
    except Exception:
        return run_ros1_filter(args, stop_requested)

    rclpy.init()

    class FilterNode(Node):
        def __init__(self) -> None:
            super().__init__("mosim_filter_pointcloud_by_z")
            self.started_at = time.time()
            self.counts = {"received": 0, "published": 0}
            self.last_stats: dict[str, Any] | None = None
            self.pub = self.create_publisher(PointCloud2, args.output_topic, 10)
            self.create_subscription(PointCloud2, args.input_topic, self.handle_cloud, 10)
            self.write_report("started")

        def handle_cloud(self, msg: Any) -> None:
            self.counts["received"] += 1
            output, stats = compact_xyzi_by_z(msg, args.min_z, args.max_points)
            self.last_stats = stats
            self.pub.publish(output)
            self.counts["published"] += 1
            if self.counts["published"] <= 5 or self.counts["published"] % 20 == 0:
                self.write_report("active")

        def write_report(self, status: str) -> None:
            payload = {
                "schema": "mosim.filter_pointcloud_by_z.v1",
                "status": status,
                "input_topic": args.input_topic,
                "output_topic": args.output_topic,
                "min_z": args.min_z,
                "scope": "review_only_not_planner_input",
                "uptime_s": round(time.time() - self.started_at, 3),
                "counts": self.counts,
                "last_stats": self.last_stats,
            }
            write_json(args.output_json, payload)

    node = FilterNode()
    try:
        while rclpy.ok() and not stop_requested["value"]:
            rclpy.spin_once(node, timeout_sec=0.2)
    finally:
        node.write_report("stopped" if stop_requested["value"] else "shutdown")
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
    return 0


def run_ros1_filter(args: argparse.Namespace, stop_requested: dict[str, bool]) -> int:
    try:
        import rospy
        from sensor_msgs.msg import PointCloud2
    except Exception as exc:
        payload = {
            "schema": "mosim.filter_pointcloud_by_z.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
        }
        write_json(args.output_json, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    ensure_ros_log_dir()
    rospy.init_node("mosim_filter_pointcloud_by_z", anonymous=True, disable_signals=True)

    started_at = time.time()
    counts = {"received": 0, "published": 0}
    last_stats: dict[str, Any] | None = None
    pub = rospy.Publisher(args.output_topic, PointCloud2, queue_size=10)

    def write_report(status: str) -> None:
        payload = {
            "schema": "mosim.filter_pointcloud_by_z.v1",
            "status": status,
            "runtime": "ros1",
            "input_topic": args.input_topic,
            "output_topic": args.output_topic,
            "min_z": args.min_z,
            "scope": "review_only_not_planner_input",
            "uptime_s": round(time.time() - started_at, 3),
            "counts": counts,
            "last_stats": last_stats,
        }
        write_json(args.output_json, payload)

    def handle_cloud(msg: Any) -> None:
        nonlocal last_stats
        counts["received"] += 1
        output, stats = compact_xyzi_by_z(msg, args.min_z, args.max_points)
        last_stats = stats
        pub.publish(output)
        counts["published"] += 1
        if counts["published"] <= 5 or counts["published"] % 20 == 0:
            write_report("active")

    rospy.Subscriber(args.input_topic, PointCloud2, handle_cloud, queue_size=10)
    write_report("started")
    rate = rospy.Rate(10)
    while not rospy.is_shutdown() and not stop_requested["value"]:
        rate.sleep()
    write_report("stopped" if stop_requested["value"] else "shutdown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
