#!/usr/bin/env python3
"""Build a continuous, review-only 3D occupancy surface from a world cloud.

The output is for RViz acceptance only. It never feeds FUEL, Diff-Planner, or
the controller. Sparse isolated voxels are removed and one bounded binary
closing pass joins scan gaps without changing the planner's occupancy map.
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


def write_json(path: str | Path | None, payload: dict[str, Any]) -> None:
    if path is None:
        return
    output = project_path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ensure_ros_log_dir() -> None:
    log_dir = project_path(os.environ.get("ROS_LOG_DIR", str(DEFAULT_ROS_LOG_DIR)))
    log_dir.mkdir(parents=True, exist_ok=True)
    os.environ["ROS_LOG_DIR"] = str(log_dir)


def make_cloud(header_stamp: Any, frame_id: str, points: list[tuple[float, float, float, float]]) -> Any:
    from sensor_msgs.msg import PointCloud2, PointField
    from std_msgs.msg import Header

    output = PointCloud2()
    output.header = Header(stamp=header_stamp, frame_id=frame_id)
    output.height = 1
    output.width = len(points)
    output.fields = [
        PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
        PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
        PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
        PointField(name="intensity", offset=12, datatype=PointField.FLOAT32, count=1),
    ]
    output.is_bigendian = False
    output.point_step = 16
    output.row_step = output.point_step * len(points)
    output.is_dense = True
    packed = bytearray(output.row_step)
    for index, point in enumerate(points):
        struct.pack_into("<ffff", packed, index * output.point_step, *point)
    output.data = bytes(packed)
    return output


def postprocess_voxels(
    voxel_keys: set[tuple[int, int, int]],
    closing_iterations: int,
    min_component_voxels: int,
    connectivity: int,
    max_dense_voxels: int,
) -> tuple[set[tuple[int, int, int]], dict[str, Any]]:
    """Join one-voxel scan gaps and remove isolated components."""
    import numpy as np
    from scipy import ndimage

    if not voxel_keys:
        return set(), {"raw_voxels": 0, "output_voxels": 0, "component_count": 0}

    coords = np.asarray(list(voxel_keys), dtype=np.int32)
    padding = max(1, closing_iterations + 1)
    minimum = coords.min(axis=0) - padding
    maximum = coords.max(axis=0) + padding
    shape = tuple((maximum - minimum + 1).tolist())
    dense_voxels = int(np.prod(shape, dtype=np.int64))
    if dense_voxels > max_dense_voxels:
        return set(voxel_keys), {
            "raw_voxels": len(voxel_keys),
            "output_voxels": len(voxel_keys),
            "dense_shape": list(shape),
            "dense_voxels": dense_voxels,
            "postprocess_skipped": "dense_volume_limit",
        }

    occupied = np.zeros(shape, dtype=bool)
    local = coords - minimum
    occupied[local[:, 0], local[:, 1], local[:, 2]] = True
    structure = ndimage.generate_binary_structure(3, connectivity)
    if closing_iterations > 0:
        occupied = ndimage.binary_closing(
            occupied,
            structure=structure,
            iterations=closing_iterations,
            border_value=0,
        )

    labels, component_count = ndimage.label(occupied, structure=structure)
    component_sizes = np.bincount(labels.ravel())
    if min_component_voxels > 1 and component_count > 0:
        keep = component_sizes >= min_component_voxels
        keep[0] = False
        occupied = keep[labels]

    output_local = np.argwhere(occupied)
    output_global = output_local + minimum
    result = {tuple(int(value) for value in row) for row in output_global}
    kept_components = 0
    if component_count > 0:
        kept_components = int((component_sizes[1:] >= min_component_voxels).sum())
    return result, {
        "raw_voxels": len(voxel_keys),
        "output_voxels": len(result),
        "dense_shape": list(shape),
        "dense_voxels": dense_voxels,
        "component_count": int(component_count),
        "kept_component_count": kept_components,
        "removed_component_count": int(component_count) - kept_components,
        "closing_iterations": closing_iterations,
        "connectivity": 26 if connectivity == 3 else 18 if connectivity == 2 else 6,
        "min_component_voxels": min_component_voxels,
    }


class ContinuousOccupancyReview:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.raw_voxels: set[tuple[int, int, int]] = set()
        self.output_voxels: set[tuple[int, int, int]] = set()
        self.received = 0
        self.published = 0
        self.last_source_stamp: Any = None
        self.last_ingest_wall = 0.0
        self.last_publish_wall = 0.0
        self.last_stats: dict[str, Any] = {}

    def ingest(self, msg: Any) -> None:
        import numpy as np

        self.received += 1
        now = time.time()
        if self.last_ingest_wall and now - self.last_ingest_wall < self.args.min_ingest_interval_s:
            return
        self.last_ingest_wall = now

        offsets = {field.name: int(field.offset) for field in msg.fields}
        if not {"x", "y", "z"}.issubset(offsets):
            raise ValueError("PointCloud2 missing x/y/z fields")
        point_step = int(msg.point_step)
        source_count = min(int(msg.width) * int(msg.height), len(msg.data) // max(1, point_step))
        if source_count <= 0:
            self.last_stats = {
                "source_frame_id": str(msg.header.frame_id),
                "source_point_count": 0,
                "raw_voxels": len(self.raw_voxels),
                "output_voxels": len(self.output_voxels),
            }
            return
        stride = max(1, math.ceil(source_count / self.args.max_points_per_cloud)) if source_count else 1
        endian = ">f4" if msg.is_bigendian else "<f4"
        buffer = memoryview(msg.data)

        def field(name: str) -> Any:
            values = np.ndarray(
                shape=(source_count,),
                dtype=np.dtype(endian),
                buffer=buffer,
                offset=offsets[name],
                strides=(point_step,),
            )
            return values[::stride]

        x = field("x")
        y = field("y")
        z = field("z")
        valid = np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
        valid &= (z >= self.args.min_z) & (z <= self.args.max_z)
        points = np.column_stack((x[valid], y[valid], z[valid]))
        if points.size:
            keys = np.unique(np.floor(points / self.args.voxel_size_m).astype(np.int32), axis=0)
            self.raw_voxels.update(tuple(int(value) for value in row) for row in keys)
        if self.args.max_accumulated_voxels > 0 and len(self.raw_voxels) > self.args.max_accumulated_voxels:
            excess = len(self.raw_voxels) - self.args.max_accumulated_voxels
            for key in list(self.raw_voxels)[:excess]:
                self.raw_voxels.remove(key)

        self.output_voxels, process_stats = postprocess_voxels(
            self.raw_voxels,
            self.args.closing_iterations,
            self.args.min_component_voxels,
            self.args.connectivity,
            self.args.max_dense_voxels,
        )
        self.last_source_stamp = msg.header.stamp
        self.last_stats = {
            "source_frame_id": str(msg.header.frame_id),
            "source_point_count": source_count,
            "sample_stride": stride,
            "accepted_source_points": int(valid.sum()),
            "voxel_size_m": self.args.voxel_size_m,
            "min_z": self.args.min_z,
            "max_z": self.args.max_z,
            **process_stats,
        }

    def points(self) -> list[tuple[float, float, float, float]]:
        size = self.args.voxel_size_m
        return [
            ((ix + 0.5) * size, (iy + 0.5) * size, (iz + 0.5) * size, (iz + 0.5) * size)
            for ix, iy, iz in sorted(self.output_voxels)
        ]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-topic", default="/mosim/goal4/livox_world_accumulated")
    parser.add_argument("--output-topic", default="/mosim/goal4/occupancy_object_review")
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--voxel-size-m", type=float, default=0.20)
    parser.add_argument("--min-z", type=float, default=0.20)
    parser.add_argument("--max-z", type=float, default=4.0)
    parser.add_argument("--closing-iterations", type=int, default=1)
    parser.add_argument("--min-component-voxels", type=int, default=8)
    parser.add_argument("--connectivity", type=int, choices=(1, 2, 3), default=3,
                        help="scipy 3D connectivity: 1=6-neighbor, 2=18-neighbor, 3=26-neighbor")
    parser.add_argument("--max-points-per-cloud", type=int, default=500000)
    parser.add_argument("--max-accumulated-voxels", type=int, default=1000000)
    parser.add_argument("--max-dense-voxels", type=int, default=12000000)
    parser.add_argument("--min-ingest-interval-s", type=float, default=0.8)
    parser.add_argument("--publish-rate-hz", type=float, default=1.0)
    parser.add_argument("--max-runtime-s", type=float, default=0.0)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def validate_args(args: argparse.Namespace) -> None:
    if args.voxel_size_m <= 0 or args.publish_rate_hz <= 0:
        raise SystemExit("voxel size and publish rate must be positive")
    if args.max_z < args.min_z:
        raise SystemExit("--max-z must be >= --min-z")
    if args.closing_iterations < 0 or args.min_component_voxels < 1:
        raise SystemExit("closing iterations must be non-negative and component size must be positive")
    if args.max_points_per_cloud <= 0 or args.max_dense_voxels <= 0:
        raise SystemExit("point and dense-voxel limits must be positive")
    if args.max_accumulated_voxels < 0 or args.max_runtime_s < 0 or args.min_ingest_interval_s < 0:
        raise SystemExit("accumulation/runtime/interval values must be non-negative")


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    validate_args(args)
    config = {
        "schema": "mosim.continuous_occupancy_review.v1",
        "input_topic": args.input_topic,
        "output_topic": args.output_topic,
        "frame_id": args.frame_id,
        "voxel_size_m": args.voxel_size_m,
        "z_range_m": [args.min_z, args.max_z],
        "closing_iterations": args.closing_iterations,
        "connectivity": 26 if args.connectivity == 3 else 18 if args.connectivity == 2 else 6,
        "min_component_voxels": args.min_component_voxels,
        "scope": "review_only_not_planner_input",
    }
    if args.dry_run:
        payload = {**config, "status": "dry_run_ready"}
        write_json(args.output_json, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    ensure_ros_log_dir()
    try:
        import rospy
        from sensor_msgs.msg import PointCloud2
    except Exception as exc:
        payload = {**config, "status": "blocked", "error": f"{exc.__class__.__name__}: {exc}"}
        write_json(args.output_json, payload)
        return 2

    stop_requested = {"value": False}

    def request_stop(_signum: int, _frame: Any) -> None:
        stop_requested["value"] = True

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    rospy.init_node("mosim_continuous_occupancy_review", anonymous=True, disable_signals=True)
    review = ContinuousOccupancyReview(args)
    publisher = rospy.Publisher(args.output_topic, PointCloud2, queue_size=1, latch=True)
    started_at = time.time()

    def report(status: str) -> None:
        write_json(args.output_json, {
            **config,
            "status": status,
            "uptime_s": round(time.time() - started_at, 3),
            "received": review.received,
            "published": review.published,
            "last_stats": review.last_stats,
        })

    def publish(force: bool = False) -> None:
        now = time.time()
        if not force and now - review.last_publish_wall < 1.0 / args.publish_rate_hz:
            return
        points = review.points()
        if not points:
            return
        stamp = review.last_source_stamp or rospy.Time.now()
        publisher.publish(make_cloud(stamp, args.frame_id, points))
        review.published += 1
        review.last_publish_wall = now
        if review.published <= 5 or review.published % 10 == 0:
            report("active")

    def handle_cloud(msg: Any) -> None:
        try:
            review.ingest(msg)
            publish(force=review.published == 0)
        except Exception as exc:
            review.last_stats = {"error": f"{exc.__class__.__name__}: {exc}"}
            report("error")

    rospy.Subscriber(args.input_topic, PointCloud2, handle_cloud, queue_size=1)
    report("started")
    rate = rospy.Rate(max(1.0, min(10.0, args.publish_rate_hz)))
    while not rospy.is_shutdown() and not stop_requested["value"]:
        if args.max_runtime_s > 0 and time.time() - started_at >= args.max_runtime_s:
            stop_requested["value"] = True
            break
        publish()
        rate.sleep()
    publish(force=True)
    report("stopped" if stop_requested["value"] else "shutdown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
