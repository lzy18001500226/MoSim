#!/usr/bin/env python3
"""Accumulate a bounded PointCloud2 stream for RViz review.

This node is review-only. It does not feed planners or controllers. The current
Goal4/Diff-Planner review uses it to display the same world-frame cloud that
the planner receives, without mixing in FAST-LIO internal `/Laser_map` state.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import signal
import struct
import sys
import threading
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


def quaternion_to_rpy_xyzw(x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    sinp = 2.0 * (w * y - z * x)
    pitch = math.copysign(math.pi / 2.0, sinp) if abs(sinp) >= 1.0 else math.asin(sinp)

    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    return roll, pitch, yaw


def angle_delta_rad(current: float, previous: float) -> float:
    return math.atan2(math.sin(current - previous), math.cos(current - previous))


class ReviewQualityGate:
    """Gate only the clean RViz review accumulator, never the planner input."""

    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.enabled = bool(str(args.quality_odom_topic).strip())
        self.lock = threading.Lock()
        self.latest: dict[str, Any] | None = None
        self.previous: dict[str, Any] | None = None
        self.accepted = 0
        self.skipped = 0
        self.last_quality: dict[str, Any] | None = None
        self.last_skip_reason = ""

    def update_odom(self, msg: Any) -> None:
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        roll, pitch, yaw = quaternion_to_rpy_xyzw(float(q.x), float(q.y), float(q.z), float(q.w))
        stamp = msg.header.stamp.to_sec()
        linear = msg.twist.twist.linear
        angular = msg.twist.twist.angular
        speed_xy = math.sqrt(float(linear.x) ** 2 + float(linear.y) ** 2)
        speed_z = abs(float(linear.z))
        yaw_rate = abs(float(angular.z))

        current = {
            "stamp": stamp,
            "position": [float(p.x), float(p.y), float(p.z)],
            "rpy_rad": [roll, pitch, yaw],
            "speed_xy_mps": speed_xy,
            "speed_z_mps": speed_z,
            "yaw_rate_rad_s": yaw_rate,
            "frame_id": str(msg.header.frame_id),
            "child_frame_id": str(msg.child_frame_id),
        }

        with self.lock:
            previous = self.latest
            if previous is not None:
                dt = stamp - float(previous.get("stamp", 0.0))
                if dt > 1e-4:
                    current["computed_speed_xy_mps"] = math.hypot(
                        current["position"][0] - previous["position"][0],
                        current["position"][1] - previous["position"][1],
                    ) / dt
                    current["computed_speed_z_mps"] = abs(current["position"][2] - previous["position"][2]) / dt
                    current["computed_yaw_rate_rad_s"] = abs(
                        angle_delta_rad(current["rpy_rad"][2], previous["rpy_rad"][2])
                    ) / dt
                    speed_xy = max(speed_xy, float(current["computed_speed_xy_mps"]))
                    speed_z = max(speed_z, float(current["computed_speed_z_mps"]))
                    yaw_rate = max(yaw_rate, float(current["computed_yaw_rate_rad_s"]))
                    current["speed_xy_mps"] = speed_xy
                    current["speed_z_mps"] = speed_z
                    current["yaw_rate_rad_s"] = yaw_rate
            self.previous = previous
            self.latest = current

    def evaluate(self, cloud_stamp: Any) -> tuple[bool, dict[str, Any]]:
        if not self.enabled:
            return True, {"enabled": False}

        with self.lock:
            latest = dict(self.latest) if self.latest is not None else None

        reasons: list[str] = []
        if latest is None:
            reasons.append("no_quality_odom")
            quality = {
                "enabled": True,
                "topic": self.args.quality_odom_topic,
                "accepted": self.accepted,
                "skipped": self.skipped,
                "reasons": reasons,
            }
            self._record(False, quality)
            return False, quality

        cloud_time = cloud_stamp.to_sec() if hasattr(cloud_stamp, "to_sec") else 0.0
        odom_stamp = float(latest.get("stamp", 0.0))
        odom_age_s = None
        if cloud_time > 0.0 and odom_stamp > 0.0:
            odom_age_s = abs(cloud_time - odom_stamp)
            if odom_age_s > self.args.max_odom_age_s:
                reasons.append("quality_odom_stale")

        z = float(latest["position"][2])
        roll_deg = abs(math.degrees(float(latest["rpy_rad"][0])))
        pitch_deg = abs(math.degrees(float(latest["rpy_rad"][1])))
        roll_pitch_deg = max(roll_deg, pitch_deg)
        yaw_rate_deg_s = abs(math.degrees(float(latest.get("yaw_rate_rad_s", 0.0))))
        speed_xy_mps = abs(float(latest.get("speed_xy_mps", 0.0)))
        speed_z_mps = abs(float(latest.get("speed_z_mps", 0.0)))

        if z < self.args.min_odom_z_for_accumulation:
            reasons.append("odom_z_below_accumulation_gate")
        if roll_pitch_deg > self.args.max_accum_roll_pitch_deg:
            reasons.append("roll_pitch_too_large_for_clean_accumulation")
        if yaw_rate_deg_s > self.args.max_accum_yaw_rate_deg_s:
            reasons.append("yaw_rate_too_large_for_clean_accumulation")
        if speed_xy_mps > self.args.max_accum_speed_xy_mps:
            reasons.append("xy_speed_too_large_for_clean_accumulation")
        if speed_z_mps > self.args.max_accum_speed_z_mps:
            reasons.append("z_speed_too_large_for_clean_accumulation")

        quality = {
            "enabled": True,
            "topic": self.args.quality_odom_topic,
            "accepted": self.accepted,
            "skipped": self.skipped,
            "cloud_stamp": cloud_time,
            "odom_stamp": odom_stamp,
            "odom_age_s": odom_age_s,
            "odom_z": z,
            "roll_pitch_deg": roll_pitch_deg,
            "yaw_rate_deg_s": yaw_rate_deg_s,
            "speed_xy_mps": speed_xy_mps,
            "speed_z_mps": speed_z_mps,
            "thresholds": {
                "max_odom_age_s": self.args.max_odom_age_s,
                "min_odom_z_for_accumulation": self.args.min_odom_z_for_accumulation,
                "max_accum_roll_pitch_deg": self.args.max_accum_roll_pitch_deg,
                "max_accum_yaw_rate_deg_s": self.args.max_accum_yaw_rate_deg_s,
                "max_accum_speed_xy_mps": self.args.max_accum_speed_xy_mps,
                "max_accum_speed_z_mps": self.args.max_accum_speed_z_mps,
            },
            "reasons": reasons,
        }
        ok = not reasons
        self._record(ok, quality)
        return ok, quality

    def _record(self, ok: bool, quality: dict[str, Any]) -> None:
        if ok:
            self.accepted += 1
            quality["accepted"] = self.accepted
            quality["skipped"] = self.skipped
            self.last_skip_reason = ""
        else:
            self.skipped += 1
            quality["accepted"] = self.accepted
            quality["skipped"] = self.skipped
            self.last_skip_reason = ",".join(quality.get("reasons", []))
        self.last_quality = quality


class Accumulator:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.voxels: dict[tuple[int, int, int], tuple[float, float, float, float]] = {}
        self.received = 0
        self.published = 0
        self.last_stats: dict[str, Any] | None = None
        self.last_publish_wall = 0.0

    def ingest(self, msg: Any, quality: dict[str, Any] | None = None) -> tuple[bool, dict[str, Any]]:
        offsets = {field.name: int(field.offset) for field in msg.fields}
        if not {"x", "y", "z"}.issubset(offsets):
            raise ValueError("PointCloud2 missing x/y/z fields")
        intensity_offset = offsets.get("intensity")
        endian = ">" if msg.is_bigendian else "<"
        point_step = int(msg.point_step)
        data = bytes(msg.data)
        source_count = min(int(msg.width) * int(msg.height), len(data) // max(1, point_step))
        sample_stride = max(1, math.ceil(source_count / int(self.args.max_points_per_cloud))) if source_count > 0 else 1
        voxel_size = float(self.args.voxel_size_m)

        sampled = 0
        finite = 0
        added_or_updated = 0
        z_filtered = 0
        range_filtered = 0
        for index in range(0, source_count, sample_stride):
            sampled += 1
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
            finite += 1
            if z < self.args.min_z or z > self.args.max_z:
                z_filtered += 1
                continue
            if math.sqrt(x * x + y * y + z * z) < self.args.min_range_m:
                range_filtered += 1
                continue
            key = (
                math.floor(x / voxel_size),
                math.floor(y / voxel_size),
                math.floor(z / voxel_size),
            )
            self.voxels[key] = (float(x), float(y), float(z), float(intensity) if math.isfinite(intensity) else float(z))
            added_or_updated += 1

        if self.args.max_accumulated_points > 0 and len(self.voxels) > self.args.max_accumulated_points:
            drop_count = len(self.voxels) - self.args.max_accumulated_points
            for key in list(self.voxels.keys())[:drop_count]:
                del self.voxels[key]

        stats = {
            "source_frame_id": str(msg.header.frame_id),
            "source_point_count": source_count,
            "sampled_point_count": sampled,
            "sample_stride": sample_stride,
            "finite_point_count": finite,
            "z_filtered": z_filtered,
            "range_filtered": range_filtered,
            "added_or_updated_points": added_or_updated,
            "accumulated_voxels": len(self.voxels),
            "voxel_size_m": self.args.voxel_size_m,
            "min_z": self.args.min_z,
            "max_z": self.args.max_z,
        }
        if quality is not None:
            stats["quality_gate"] = quality
        if self.voxels:
            xs = [p[0] for p in self.voxels.values()]
            ys = [p[1] for p in self.voxels.values()]
            zs = [p[2] for p in self.voxels.values()]
            stats["bounds"] = {
                "min": [min(xs), min(ys), min(zs)],
                "max": [max(xs), max(ys), max(zs)],
            }
        self.last_stats = stats
        return added_or_updated > 0, stats

    def points(self) -> list[tuple[float, float, float, float]]:
        return list(self.voxels.values())


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-topic", default="/uav1/livox_world")
    parser.add_argument("--output-topic", default="/mosim/goal4/livox_world_accumulated")
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--voxel-size-m", type=float, default=0.02)
    parser.add_argument("--min-z", type=float, default=0.20)
    parser.add_argument("--max-z", type=float, default=2.20)
    parser.add_argument("--min-range-m", type=float, default=0.0)
    parser.add_argument("--max-points-per-cloud", type=int, default=20000)
    parser.add_argument("--max-accumulated-points", type=int, default=300000,
                        help="maximum retained voxels; 0 disables trimming for review stress tests")
    parser.add_argument("--publish-rate-hz", type=float, default=2.0)
    parser.add_argument("--max-runtime-s", type=float, default=0.0)
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--quality-odom-topic", default="")
    parser.add_argument("--max-odom-age-s", type=float, default=0.25)
    parser.add_argument("--min-odom-z-for-accumulation", type=float, default=0.85)
    parser.add_argument("--max-accum-roll-pitch-deg", type=float, default=5.0)
    parser.add_argument("--max-accum-yaw-rate-deg-s", type=float, default=30.0)
    parser.add_argument("--max-accum-speed-xy-mps", type=float, default=0.45)
    parser.add_argument("--max-accum-speed-z-mps", type=float, default=0.30)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.voxel_size_m <= 0:
        raise SystemExit("--voxel-size-m must be positive")
    if args.max_points_per_cloud <= 0:
        raise SystemExit("--max-points-per-cloud must be positive")
    if args.max_accumulated_points < 0:
        raise SystemExit("--max-accumulated-points must be non-negative")
    if args.max_z < args.min_z:
        raise SystemExit("--max-z must be >= --min-z")
    if args.publish_rate_hz <= 0:
        raise SystemExit("--publish-rate-hz must be positive")
    if args.max_runtime_s < 0:
        raise SystemExit("--max-runtime-s must be non-negative")
    if args.max_odom_age_s <= 0:
        raise SystemExit("--max-odom-age-s must be positive")
    if args.min_odom_z_for_accumulation < 0:
        raise SystemExit("--min-odom-z-for-accumulation must be non-negative")
    if args.max_accum_roll_pitch_deg < 0 or args.max_accum_yaw_rate_deg_s < 0:
        raise SystemExit("--max-accum-roll-pitch-deg and --max-accum-yaw-rate-deg-s must be non-negative")
    if args.max_accum_speed_xy_mps < 0 or args.max_accum_speed_z_mps < 0:
        raise SystemExit("--max-accum-speed-xy-mps and --max-accum-speed-z-mps must be non-negative")
    if args.dry_run:
        payload = {
            "schema": "mosim.accumulate_pointcloud_review.dryrun.v1",
            "status": "dry_run_ready",
            "input_topic": args.input_topic,
            "output_topic": args.output_topic,
            "frame_id": args.frame_id,
            "voxel_size_m": args.voxel_size_m,
            "max_runtime_s": args.max_runtime_s,
            "scope": "review_only_not_planner_input",
            "quality_gate": {
                "enabled": bool(str(args.quality_odom_topic).strip()),
                "quality_odom_topic": args.quality_odom_topic,
                "max_odom_age_s": args.max_odom_age_s,
                "min_odom_z_for_accumulation": args.min_odom_z_for_accumulation,
                "max_accum_roll_pitch_deg": args.max_accum_roll_pitch_deg,
                "max_accum_yaw_rate_deg_s": args.max_accum_yaw_rate_deg_s,
                "max_accum_speed_xy_mps": args.max_accum_speed_xy_mps,
                "max_accum_speed_z_mps": args.max_accum_speed_z_mps,
            },
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
        import rospy
        from nav_msgs.msg import Odometry
        from sensor_msgs.msg import PointCloud2
    except Exception as exc:
        payload = {
            "schema": "mosim.accumulate_pointcloud_review.v1",
            "status": "blocked",
            "error": f"{exc.__class__.__name__}: {exc}",
        }
        write_json(args.output_json, payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2

    rospy.init_node("mosim_accumulate_pointcloud_review", anonymous=True, disable_signals=True)
    accumulator = Accumulator(args)
    quality_gate = ReviewQualityGate(args)
    pub = rospy.Publisher(args.output_topic, PointCloud2, queue_size=1, latch=True)
    started_at = time.time()

    def write_report(status: str) -> None:
        payload = {
            "schema": "mosim.accumulate_pointcloud_review.v1",
            "status": status,
            "runtime": "ros1",
            "input_topic": args.input_topic,
            "output_topic": args.output_topic,
            "scope": "review_only_not_planner_input",
            "uptime_s": round(time.time() - started_at, 3),
            "received": accumulator.received,
            "published": accumulator.published,
            "last_stats": accumulator.last_stats,
            "quality_gate": quality_gate.last_quality,
            "quality_gate_counts": {
                "enabled": quality_gate.enabled,
                "accepted": quality_gate.accepted,
                "skipped": quality_gate.skipped,
                "last_skip_reason": quality_gate.last_skip_reason,
            },
        }
        write_json(args.output_json, payload)

    def maybe_publish(stamp: Any, force: bool = False) -> None:
        now = time.time()
        if not force and now - accumulator.last_publish_wall < 1.0 / args.publish_rate_hz:
            return
        points = accumulator.points()
        if not points:
            return
        pub.publish(make_cloud(stamp, args.frame_id, points))
        accumulator.published += 1
        accumulator.last_publish_wall = now
        if accumulator.published <= 5 or accumulator.published % 10 == 0:
            write_report("active")

    def handle_cloud(msg: Any) -> None:
        accumulator.received += 1
        quality_ok, quality = quality_gate.evaluate(msg.header.stamp)
        if not quality_ok:
            accumulator.last_stats = {
                "source_frame_id": str(msg.header.frame_id),
                "source_stamp": msg.header.stamp.to_sec(),
                "skip_reason": "quality_gate",
                "quality_gate": quality,
                "accumulated_voxels": len(accumulator.voxels),
            }
            if quality_gate.skipped <= 5 or quality_gate.skipped % 20 == 0:
                write_report("active_quality_skipping")
            maybe_publish(msg.header.stamp, force=accumulator.published == 0)
            return
        try:
            added, _stats = accumulator.ingest(msg, quality=quality)
        except Exception as exc:
            accumulator.last_stats = {"error": f"{exc.__class__.__name__}: {exc}"}
            write_report("error")
            return
        maybe_publish(msg.header.stamp, force=added and accumulator.published == 0)

    if quality_gate.enabled:
        rospy.Subscriber(args.quality_odom_topic, Odometry, quality_gate.update_odom, queue_size=20)
    rospy.Subscriber(args.input_topic, PointCloud2, handle_cloud, queue_size=5)
    write_report("started")
    rate = rospy.Rate(max(1.0, min(10.0, float(args.publish_rate_hz))))
    while not rospy.is_shutdown() and not stop_requested["value"]:
        if args.max_runtime_s > 0 and time.time() - started_at >= args.max_runtime_s:
            stop_requested["value"] = True
            break
        maybe_publish(rospy.Time.now())
        rate.sleep()
    maybe_publish(rospy.Time.now(), force=True)
    write_report("stopped" if stop_requested["value"] else "shutdown")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
