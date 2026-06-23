#!/usr/bin/env python3
"""Measure effective ROS1 topic rates for the current Sunray runtime stack."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path
from typing import Any

import rospy
import rostopic


DEFAULT_TOPICS = [
    "/clock",
    "/tf",
    "/imu",
    "/uav1/mavros/imu/data",
    "/uav1/mavros/local_position/pose",
    "/uav1/mavros/local_position/velocity_local",
    "/uav1/mavros/setpoint_raw/attitude",
    "/uav1/mavros/setpoint_raw/local",
    "/uav1/mavros/setpoint_raw/target_local",
    "/uav1/sunray/uav_state",
    "/uav1/sunray/px4_state",
    "/uav1/sunray/uav_control_cmd",
    "/uav1/livox/lidar",
    "/uav1/livox/imu",
    "/mosim/fastlio/livox/lidar",
    "/cloud_registered",
    "/cloud_registered_body",
    "/Odometry",
    "/path",
    "/mosim/sunray/truth_path",
    "/mosim/sunray/reference_path",
    "/mosim/sunray/lidar_points_map_accumulated",
]


def stamp_to_sec(stamp: Any) -> float | None:
    if stamp is None:
        return None
    try:
        return float(stamp.secs) + float(stamp.nsecs) * 1.0e-9
    except Exception:
        return None


def get_header_stamp(msg: Any) -> float | None:
    clock = getattr(msg, "clock", None)
    if clock is not None:
        return stamp_to_sec(clock)
    header = getattr(msg, "header", None)
    if header is not None:
        return stamp_to_sec(getattr(header, "stamp", None))
    return None


def finite_stats(values: list[float]) -> dict[str, Any]:
    values = [v for v in values if math.isfinite(v)]
    if not values:
        return {"count": 0}
    values_sorted = sorted(values)
    return {
        "count": len(values),
        "min": values_sorted[0],
        "p50": values_sorted[int(0.50 * (len(values_sorted) - 1))],
        "p95": values_sorted[int(0.95 * (len(values_sorted) - 1))],
        "max": values_sorted[-1],
    }


def rate_stats(times: list[float]) -> dict[str, Any]:
    if len(times) < 2:
        return {"count": len(times), "avg_hz": None}
    gaps = [b - a for a, b in zip(times, times[1:])]
    elapsed = times[-1] - times[0]
    positive_gaps = [gap for gap in gaps if gap > 0]
    return {
        "count": len(times),
        "elapsed_s": elapsed,
        "avg_hz": (len(times) - 1) / elapsed if elapsed > 0 else None,
        "gap_s": finite_stats(gaps),
        "positive_gap_s": finite_stats(positive_gaps),
        "gaps_gt_0p1s": sum(1 for gap in gaps if gap > 0.1),
        "gaps_gt_0p5s": sum(1 for gap in gaps if gap > 0.5),
        "gaps_gt_1s": sum(1 for gap in gaps if gap > 1.0),
        "backward_count": sum(1 for gap in gaps if gap < -1.0e-6),
    }


class TopicRecorder:
    def __init__(self, topic: str, msg_class: Any | None, topic_type: str | None) -> None:
        self.topic = topic
        self.msg_class = msg_class
        self.topic_type = topic_type
        self.wall_times: list[float] = []
        self.header_times: list[float] = []
        self.frames: list[str] = []
        self.widths: list[int] = []
        self.heights: list[int] = []
        self.point_nums: list[int] = []
        self.subscriber = None

    def start(self) -> None:
        if self.msg_class is None:
            return
        self.subscriber = rospy.Subscriber(self.topic, self.msg_class, self.callback, queue_size=500)

    def callback(self, msg: Any) -> None:
        self.wall_times.append(time.time())
        stamp = get_header_stamp(msg)
        if stamp is not None:
            self.header_times.append(stamp)
        header = getattr(msg, "header", None)
        if header is not None:
            frame = getattr(header, "frame_id", "")
            if frame:
                self.frames.append(frame)
        width = getattr(msg, "width", None)
        height = getattr(msg, "height", None)
        if width is not None:
            self.widths.append(int(width))
        if height is not None:
            self.heights.append(int(height))
        point_num = getattr(msg, "point_num", None)
        if point_num is not None:
            self.point_nums.append(int(point_num))

    def summary(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "topic": self.topic,
            "type": self.topic_type,
            "present_at_start": self.msg_class is not None,
            "wall_rate": rate_stats(self.wall_times),
            "header_rate": rate_stats(self.header_times),
            "unique_frames": sorted(set(self.frames))[:12],
        }
        if self.widths:
            payload["width_min_max_last"] = [min(self.widths), max(self.widths), self.widths[-1]]
        if self.heights:
            payload["height_min_max_last"] = [min(self.heights), max(self.heights), self.heights[-1]]
        if self.point_nums:
            payload["point_num_min_max_last"] = [min(self.point_nums), max(self.point_nums), self.point_nums[-1]]
        return payload


def resolve_topic(topic: str) -> tuple[Any | None, str | None]:
    try:
        msg_class, real_topic, _ = rostopic.get_topic_class(topic, blocking=False)
    except Exception:
        return None, None
    if msg_class is None:
        return None, None
    try:
        topic_type = f"{msg_class._type}"
    except Exception:
        topic_type = None
    return msg_class, topic_type


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration-s", type=float, default=90.0)
    parser.add_argument("--out", required=True)
    parser.add_argument("--topic", action="append", default=[])
    args = parser.parse_args()

    rospy.init_node("mosim_sunray_ros1_system_frequency_audit", anonymous=True, disable_signals=True)
    topics = args.topic or DEFAULT_TOPICS
    recorders = []
    for topic in topics:
        msg_class, topic_type = resolve_topic(topic)
        recorder = TopicRecorder(topic, msg_class, topic_type)
        recorder.start()
        recorders.append(recorder)

    start = time.time()
    while not rospy.is_shutdown() and time.time() - start < args.duration_s:
        time.sleep(0.05)

    summary = {
        "schema": "mosim.sunray_ros1_system_frequency_audit.v1",
        "duration_requested_s": args.duration_s,
        "duration_wall_s": time.time() - start,
        "use_sim_time": bool(rospy.get_param("/use_sim_time", False)),
        "topics": {recorder.topic: recorder.summary() for recorder in recorders},
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
