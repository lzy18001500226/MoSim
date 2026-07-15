#!/usr/bin/env python3
"""Audit ROS1 time and TF monotonicity for Sunray/Gazebo/RViz runs."""

from __future__ import annotations

import argparse
import glob
import json
import re
import signal
import time
from pathlib import Path
from typing import Any

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry, Path as RosPath
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import Imu, PointCloud2
from tf2_msgs.msg import TFMessage

try:
    from livox_ros_driver.msg import CustomMsg
except Exception:  # pragma: no cover - depends on sourced catkin workspace.
    CustomMsg = None


def stamp_to_sec(stamp: Any) -> float | None:
    try:
        return float(stamp.secs) + float(stamp.nsecs) * 1e-9
    except Exception:
        return None


def monotonic_stats(values: list[float], tolerance_s: float = 1.0e-6) -> dict[str, Any]:
    if not values:
        return {"count": 0}
    backward = []
    gaps = []
    for idx, (prev, cur) in enumerate(zip(values, values[1:]), start=1):
        delta = cur - prev
        gaps.append(delta)
        if delta < -tolerance_s:
            backward.append({"index": idx, "previous": prev, "current": cur, "delta_s": delta})
    elapsed = values[-1] - values[0]
    positive_gaps = [gap for gap in gaps if gap >= 0]
    return {
        "count": len(values),
        "first": values[0],
        "last": values[-1],
        "elapsed_s": elapsed,
        "avg_hz": (len(values) - 1) / elapsed if elapsed > 0 and len(values) > 1 else None,
        "min_delta_s": min(gaps) if gaps else None,
        "max_delta_s": max(gaps) if gaps else None,
        "max_positive_gap_s": max(positive_gaps) if positive_gaps else None,
        "backward_count": len(backward),
        "backward_examples": backward[:10],
    }


class TimeTfAudit:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.wall_times: list[float] = []
        self.ros_now: list[float] = []
        self.clock: list[float] = []
        self.header_times: dict[str, list[float]] = {}
        self.frames: dict[str, list[str]] = {}
        self.tf_times_by_child: dict[str, list[float]] = {}
        self.tf_count = 0
        self.tf_static_count = 0
        self.subscribers = []
        self.stop_requested = False

    def request_stop(self, _signum, _frame) -> None:
        self.stop_requested = True

    def _record_header(self, topic: str, msg: Any) -> None:
        header = getattr(msg, "header", None)
        stamp = stamp_to_sec(header.stamp) if header is not None else None
        if stamp is not None:
            self.header_times.setdefault(topic, []).append(stamp)
        frame = getattr(header, "frame_id", "") if header is not None else ""
        self.frames.setdefault(topic, []).append(frame)

    def _clock_cb(self, msg: Clock) -> None:
        stamp = stamp_to_sec(msg.clock)
        if stamp is not None:
            self.clock.append(stamp)

    def _tf_cb(self, msg: TFMessage) -> None:
        self.tf_count += len(msg.transforms)
        for transform in msg.transforms:
            child = transform.child_frame_id or "<empty_child>"
            stamp = stamp_to_sec(transform.header.stamp)
            if stamp is not None:
                self.tf_times_by_child.setdefault(child, []).append(stamp)

    def _tf_static_cb(self, msg: TFMessage) -> None:
        self.tf_static_count += len(msg.transforms)

    def run(self) -> dict[str, Any]:
        signal.signal(signal.SIGTERM, self.request_stop)
        signal.signal(signal.SIGINT, self.request_stop)
        rospy.init_node("mosim_sunray_ros1_time_tf_audit", anonymous=True, disable_signals=True)
        self.subscribers.append(rospy.Subscriber("/clock", Clock, self._clock_cb, queue_size=200))
        self.subscribers.append(rospy.Subscriber("/tf", TFMessage, self._tf_cb, queue_size=500))
        self.subscribers.append(rospy.Subscriber("/tf_static", TFMessage, self._tf_static_cb, queue_size=50))

        topic_types: list[tuple[str, Any]] = [
            ("/uav1/livox/lidar", PointCloud2),
            ("/uav1/livox/imu", Imu),
            ("/uav1/mavros/local_position/pose", PoseStamped),
            ("/cloud_registered", PointCloud2),
            ("/Odometry", Odometry),
            ("/path", RosPath),
            ("/mosim/sunray/truth_path", RosPath),
            ("/mosim/sunray/reference_path", RosPath),
            ("/mosim/sunray/lidar_points_map_accumulated", PointCloud2),
        ]
        if CustomMsg is not None:
            topic_types.insert(2, ("/mosim/fastlio/livox/lidar", CustomMsg))
        for topic, msg_type in topic_types:
            self.subscribers.append(rospy.Subscriber(topic, msg_type, lambda msg, t=topic: self._record_header(t, msg), queue_size=200))

        start_wall = time.time()
        while not rospy.is_shutdown() and not self.stop_requested and time.time() - start_wall < self.args.duration_s:
            self.wall_times.append(time.time())
            now = rospy.Time.now().to_sec()
            if now > 0:
                self.ros_now.append(now)
            time.sleep(max(self.args.sample_period_s, 0.005))

        summary = self.summary(time.time() - start_wall)
        summary["interrupted"] = bool(self.stop_requested)
        return summary

    def summary(self, duration_wall_s: float) -> dict[str, Any]:
        tf_child_stats = {
            child: monotonic_stats(values)
            for child, values in sorted(self.tf_times_by_child.items())
            if values
        }
        tf_backwards = {
            child: stats
            for child, stats in tf_child_stats.items()
            if stats.get("backward_count", 0) > 0
        }
        header_stats = {
            topic: {
                "stamp_stats": monotonic_stats(values),
                "unique_frames": sorted({frame for frame in self.frames.get(topic, []) if frame})[:20],
            }
            for topic, values in sorted(self.header_times.items())
        }
        return {
            "schema": "mosim.sunray_ros1_time_tf_audit.v1",
            "duration_requested_s": self.args.duration_s,
            "duration_wall_s": duration_wall_s,
            "use_sim_time": bool(rospy.get_param("/use_sim_time", False)),
            "wall_time_stats": monotonic_stats(self.wall_times),
            "rospy_time_now_stats": monotonic_stats(self.ros_now),
            "clock_topic_stats": monotonic_stats(self.clock),
            "header_topics": header_stats,
            "tf": {
                "transform_count": self.tf_count,
                "static_transform_count": self.tf_static_count,
                "child_frame_count": len(self.tf_times_by_child),
                "children_with_backward_time": tf_backwards,
            },
            "log_scan": scan_logs(self.args.log_globs),
        }


def scan_logs(patterns: list[str]) -> dict[str, Any]:
    regexes = {
        "tf_jump_back": re.compile(r"Detected jump back in time.*Clearing TF buffer"),
        "timesync_time_jump": re.compile(r"timesync time jump detected", re.IGNORECASE),
        "simulator_mavlink_poll_timeout": re.compile(r"simulator_mavlink.*poll timeout", re.IGNORECASE),
        "imu_lidar_not_synced": re.compile(r"IMU and LiDAR not Synced", re.IGNORECASE),
    }
    counts = {name: 0 for name in regexes}
    examples: dict[str, list[str]] = {name: [] for name in regexes}
    files = []
    for pattern in patterns:
        for raw_path in sorted(glob.glob(pattern)):
            path = Path(raw_path)
            if not path.is_file():
                continue
            files.append(str(path))
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            for line in text.splitlines():
                for name, regex in regexes.items():
                    if regex.search(line):
                        counts[name] += 1
                        if len(examples[name]) < 10:
                            examples[name].append(f"{path}: {line}")
    return {"files_scanned": files, "counts": counts, "examples": examples}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-s", type=float, default=120.0)
    parser.add_argument("--sample-period-s", type=float, default=0.05)
    parser.add_argument("--out", required=True)
    parser.add_argument("--log-glob", dest="log_globs", action="append", default=[])
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not args.log_globs:
        args.log_globs = ["*.log", "*.txt"]
    summary = TimeTfAudit(args).run()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
