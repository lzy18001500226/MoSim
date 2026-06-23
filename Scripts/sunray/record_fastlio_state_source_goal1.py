#!/usr/bin/env python3
"""Record Goal 1 FAST-LIO state-source gate metrics.

This recorder is intentionally limited to localization/state-source evidence.
It does not publish setpoints, arm PX4, or run a controller mission.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import rospy
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, PointCloud2
from visualization_msgs.msg import MarkerArray

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from fastlio_frame_transform import (  # noqa: E402
    Pose3,
    livox_pose_to_base_pose,
    quat_from_rpy,
)


def stamp_to_sec(stamp: Any) -> float | None:
    try:
        return float(stamp.secs) + float(stamp.nsecs) * 1e-9
    except Exception:
        return None


def quat_norm(q: Any) -> float:
    return math.sqrt(float(q.x) ** 2 + float(q.y) ** 2 + float(q.z) ** 2 + float(q.w) ** 2)


def rpy_from_quat(q: Any) -> tuple[float, float, float]:
    x, y, z, w = float(q.x), float(q.y), float(q.z), float(q.w)
    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)
    sinp = 2.0 * (w * y - z * x)
    pitch = math.copysign(math.pi / 2.0, sinp) if abs(sinp) >= 1.0 else math.asin(sinp)
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    return roll, pitch, yaw


def gap_stats(values: list[float]) -> dict[str, Any]:
    if len(values) < 2:
        return {"count": len(values)}
    gaps = [b - a for a, b in zip(values, values[1:])]
    elapsed = values[-1] - values[0]
    return {
        "count": len(values),
        "avg_hz": (len(values) - 1) / elapsed if elapsed > 0 else None,
        "max_gap_s": max(gaps),
        "negative_gap_count": sum(1 for gap in gaps if gap < -1e-6),
        "first": values[0],
        "last": values[-1],
    }


def odom_sample(msg: Odometry) -> dict[str, Any]:
    p = msg.pose.pose.position
    q = msg.pose.pose.orientation
    v = msg.twist.twist.linear
    roll, pitch, yaw = rpy_from_quat(q)
    return {
        "frame_id": msg.header.frame_id,
        "child_frame_id": msg.child_frame_id,
        "stamp": stamp_to_sec(msg.header.stamp),
        "position": {"x": float(p.x), "y": float(p.y), "z": float(p.z)},
        "velocity": {"x": float(v.x), "y": float(v.y), "z": float(v.z)},
        "quaternion": {"x": float(q.x), "y": float(q.y), "z": float(q.z), "w": float(q.w)},
        "quaternion_norm": quat_norm(q),
        "rpy_rad": {"roll": roll, "pitch": pitch, "yaw": yaw},
    }


class Goal1Recorder:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.records: dict[str, dict[str, Any]] = {}
        self.latest: dict[str, Any] = {}
        self.mount_pose = Pose3(args.mount_xyz, quat_from_rpy(*args.mount_rpy))

    def ensure(self, name: str) -> dict[str, Any]:
        return self.records.setdefault(
            name,
            {
                "wall": [],
                "header": [],
                "frame_ids": [],
                "child_frame_ids": [],
                "first": None,
                "last": None,
                "quaternion_norms": [],
            },
        )

    def on_odom(self, name: str, msg: Odometry) -> None:
        rec = self.ensure(name)
        sample = odom_sample(msg)
        rec["wall"].append(time.time())
        if sample["stamp"] is not None:
            rec["header"].append(sample["stamp"])
        rec["frame_ids"].append(sample["frame_id"])
        rec["child_frame_ids"].append(sample["child_frame_id"])
        rec["quaternion_norms"].append(sample["quaternion_norm"])
        if rec["first"] is None:
            rec["first"] = sample
        rec["last"] = sample
        self.latest[name] = msg

    def on_imu(self, name: str, msg: Imu) -> None:
        rec = self.ensure(name)
        sample = {
            "frame_id": msg.header.frame_id,
            "stamp": stamp_to_sec(msg.header.stamp),
            "angular_velocity": {
                "x": float(msg.angular_velocity.x),
                "y": float(msg.angular_velocity.y),
                "z": float(msg.angular_velocity.z),
            },
            "linear_acceleration": {
                "x": float(msg.linear_acceleration.x),
                "y": float(msg.linear_acceleration.y),
                "z": float(msg.linear_acceleration.z),
            },
        }
        rec["wall"].append(time.time())
        if sample["stamp"] is not None:
            rec["header"].append(sample["stamp"])
        rec["frame_ids"].append(sample["frame_id"])
        if rec["first"] is None:
            rec["first"] = sample
        rec["last"] = sample

    def on_cloud(self, name: str, msg: PointCloud2) -> None:
        rec = self.ensure(name)
        sample = {
            "frame_id": msg.header.frame_id,
            "stamp": stamp_to_sec(msg.header.stamp),
            "height": int(msg.height),
            "width": int(msg.width),
            "fields": [field.name for field in msg.fields],
            "point_step": int(msg.point_step),
            "row_step": int(msg.row_step),
        }
        rec["wall"].append(time.time())
        if sample["stamp"] is not None:
            rec["header"].append(sample["stamp"])
        rec["frame_ids"].append(sample["frame_id"])
        if rec["first"] is None:
            rec["first"] = sample
        rec["last"] = sample

    def on_axes(self, msg: MarkerArray) -> None:
        rec = self.ensure("uav_axes")
        starts = []
        ends = []
        frame_id = ""
        stamp = None
        for marker in msg.markers:
            frame_id = marker.header.frame_id
            stamp = stamp_to_sec(marker.header.stamp)
            if len(marker.points) >= 2:
                starts.append(
                    {
                        "x": float(marker.points[0].x),
                        "y": float(marker.points[0].y),
                        "z": float(marker.points[0].z),
                    }
                )
                ends.append(
                    {
                        "x": float(marker.points[1].x),
                        "y": float(marker.points[1].y),
                        "z": float(marker.points[1].z),
                    }
                )
        sample = {"frame_id": frame_id, "stamp": stamp, "marker_count": len(msg.markers), "starts": starts, "ends": ends}
        rec["wall"].append(time.time())
        if stamp is not None:
            rec["header"].append(stamp)
        rec["frame_ids"].append(frame_id)
        if rec["first"] is None:
            rec["first"] = sample
        rec["last"] = sample

    def run(self) -> dict[str, Any]:
        rospy.init_node("mosim_fastlio_state_source_goal1_recorder", anonymous=True, disable_signals=True)
        subscribers = [
            rospy.Subscriber(self.args.raw_odom_topic, Odometry, lambda msg: self.on_odom("fastlio_raw_odom", msg), queue_size=100),
            rospy.Subscriber(self.args.aligned_odom_topic, Odometry, lambda msg: self.on_odom("fastlio_aligned_odom", msg), queue_size=100),
            rospy.Subscriber(self.args.local_odom_topic, Odometry, lambda msg: self.on_odom("mavros_local_odom", msg), queue_size=100),
            rospy.Subscriber(self.args.truth_topic, Odometry, lambda msg: self.on_odom("gazebo_truth_odom", msg), queue_size=100),
            rospy.Subscriber(self.args.lidar_topic, PointCloud2, lambda msg: self.on_cloud("mid360_lidar", msg), queue_size=50),
            rospy.Subscriber(self.args.laser_map_topic, PointCloud2, lambda msg: self.on_cloud("fastlio_laser_map", msg), queue_size=20),
            rospy.Subscriber(self.args.imu_topic, Imu, lambda msg: self.on_imu("mid360_imu", msg), queue_size=200),
            rospy.Subscriber(self.args.axes_topic, MarkerArray, self.on_axes, queue_size=20),
        ]
        start = time.time()
        while not rospy.is_shutdown() and time.time() - start < self.args.duration_s:
            time.sleep(0.05)
        for subscriber in subscribers:
            subscriber.unregister()
        return self.summary(time.time() - start)

    def marker_start_error_to_raw_base(self) -> float | None:
        raw = self.latest.get("fastlio_raw_odom")
        axes = self.records.get("uav_axes", {}).get("last")
        if raw is None or not axes or not axes.get("starts"):
            return None
        p = raw.pose.pose.position
        q = raw.pose.pose.orientation
        raw_pose = Pose3((float(p.x), float(p.y), float(p.z)), (float(q.x), float(q.y), float(q.z), float(q.w)))
        base_pose = livox_pose_to_base_pose(raw_pose, self.mount_pose)
        start = axes["starts"][0]
        return math.sqrt(
            (base_pose.p[0] - start["x"]) ** 2
            + (base_pose.p[1] - start["y"]) ** 2
            + (base_pose.p[2] - start["z"]) ** 2
        )

    def summary(self, duration_wall_s: float) -> dict[str, Any]:
        topics: dict[str, Any] = {}
        for name, rec in self.records.items():
            topic = {
                "wall_stats": gap_stats(rec["wall"]),
                "header_stats": gap_stats(rec["header"]),
                "unique_frame_ids": sorted(set(rec["frame_ids"])),
                "unique_child_frame_ids": sorted(set(rec["child_frame_ids"])) if rec["child_frame_ids"] else [],
                "first": rec["first"],
                "last": rec["last"],
            }
            norms = rec.get("quaternion_norms") or []
            if norms:
                topic["quaternion_norm_minmax"] = [min(norms), max(norms)]
            topics[name] = topic

        checks = {
            "raw_odom_present": topics.get("fastlio_raw_odom", {}).get("wall_stats", {}).get("count", 0) > 0,
            "aligned_odom_present": topics.get("fastlio_aligned_odom", {}).get("wall_stats", {}).get("count", 0) > 0,
            "gazebo_z_surrogate_present": topics.get("gazebo_truth_odom", {}).get("wall_stats", {}).get("count", 0) > 0,
            "uav_axes_present": topics.get("uav_axes", {}).get("wall_stats", {}).get("count", 0) > 0,
            "raw_frame_camera_init": "camera_init" in topics.get("fastlio_raw_odom", {}).get("unique_frame_ids", []),
            "aligned_frame_world": self.args.expected_aligned_frame in topics.get("fastlio_aligned_odom", {}).get("unique_frame_ids", []),
            "aligned_child_base_link": "base_link" in topics.get("fastlio_aligned_odom", {}).get("unique_child_frame_ids", []),
            "negative_header_gaps": {
                name: data.get("header_stats", {}).get("negative_gap_count", 0) for name, data in topics.items()
            },
            "axes_marker_start_error_to_raw_base_m": self.marker_start_error_to_raw_base(),
        }
        gate_pass = (
            checks["raw_odom_present"]
            and checks["aligned_odom_present"]
            and checks["gazebo_z_surrogate_present"]
            and checks["uav_axes_present"]
            and checks["raw_frame_camera_init"]
            and checks["aligned_frame_world"]
            and checks["aligned_child_base_link"]
            and all(count == 0 for count in checks["negative_header_gaps"].values())
            and checks["axes_marker_start_error_to_raw_base_m"] is not None
            and checks["axes_marker_start_error_to_raw_base_m"] <= self.args.axes_error_tolerance_m
        )
        return {
            "schema": "mosim.sunray_ros1.fastlio_state_source_goal1.v1",
            "duration_requested_s": self.args.duration_s,
            "duration_wall_s": duration_wall_s,
            "state_source_boundary": {
                "controller_state_source": "/uav1/mavros/local_position/odom",
                "fastlio_raw_odom": self.args.raw_odom_topic,
                "fastlio_aligned_odom_candidate": self.args.aligned_odom_topic,
                "z_source_first_version": "gazebo_rangefinder_surrogate",
                "gazebo_truth_control_input_allowed": False,
                "setpoint_publication_allowed": False,
            },
            "mount_transform": {
                "base_link_to_livox_xyz_m": list(self.args.mount_xyz),
                "base_link_to_livox_rpy_rad": list(self.args.mount_rpy),
            },
            "topics": topics,
            "checks": checks,
            "gate_pass": gate_pass,
        }


def parse_vec3(text: str) -> tuple[float, float, float]:
    parts = [p for p in text.replace(",", " ").split() if p]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"expected 3 floats, got {text!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-s", type=float, default=25.0)
    parser.add_argument("--out", required=True)
    parser.add_argument("--raw-odom-topic", default="/Odometry")
    parser.add_argument("--aligned-odom-topic", default="/mosim/fastlio/odom_aligned")
    parser.add_argument("--local-odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--truth-topic", default="/uav1/sunray/gazebo_pose")
    parser.add_argument("--lidar-topic", default="/uav1/livox/lidar")
    parser.add_argument("--imu-topic", default="/uav1/livox/imu")
    parser.add_argument("--laser-map-topic", default="/Laser_map")
    parser.add_argument("--axes-topic", default="/mosim/fastlio/uav_axes")
    parser.add_argument("--expected-aligned-frame", default="world")
    parser.add_argument("--mount-xyz", type=parse_vec3, default=(-0.000005, 0.032295, 0.050167))
    parser.add_argument("--mount-rpy", type=parse_vec3, default=(0.0, 0.0, 4.712389))
    parser.add_argument("--axes-error-tolerance-m", type=float, default=1e-4)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    summary = Goal1Recorder(args).run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["gate_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
