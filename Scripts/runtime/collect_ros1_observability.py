#!/usr/bin/env python3
"""Collect same-run ROS1 topic bandwidth/rates and Gazebo realtime metrics."""

from __future__ import annotations

import argparse
from collections import deque
import json
import time
from pathlib import Path
from typing import Any


DEFAULT_TOPICS = (
    "/gazebo/model_states",
    "/uav1/sunray/gazebo_pose",
    "/uav1/mavros/local_position/odom",
    "/uav1/mavros/imu/data",
    "/uav1/mavros/state",
    "/position_cmd",
    "/uav1/mavros/setpoint_raw/attitude",
    "/mosim/fastlio/laser_map_obstacles",
    "/mosim/fastlio/occupancy_object_review",
)


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


class TopicWindow:
    def __init__(self, window_s: float) -> None:
        self.window_s = window_s
        self.samples: deque[tuple[float, int]] = deque()

    def observe(self, payload_bytes: int) -> None:
        now = time.monotonic()
        self.samples.append((now, payload_bytes))
        self.trim(now)

    def trim(self, now: float) -> None:
        cutoff = now - self.window_s
        while self.samples and self.samples[0][0] < cutoff:
            self.samples.popleft()

    def snapshot(self) -> dict[str, Any]:
        now = time.monotonic()
        self.trim(now)
        if not self.samples:
            return {"state": "no_samples", "rate_hz": 0.0, "payload_bytes_per_s": 0.0, "sample_count": 0}
        elapsed_s = max(min(self.window_s, now - self.samples[0][0]), 1e-6)
        return {
            "state": "available",
            "rate_hz": len(self.samples) / elapsed_s,
            "payload_bytes_per_s": sum(size for _, size in self.samples) / elapsed_s,
            "sample_count": len(self.samples),
        }


class Ros1Collector:
    def __init__(self, args: argparse.Namespace) -> None:
        import rospy
        from gazebo_msgs.msg import PerformanceMetrics
        from rosgraph_msgs.msg import Clock

        self.rospy = rospy
        self.args = args
        self.started = time.monotonic()
        self.windows = {topic: TopicWindow(args.window_s) for topic in args.topic}
        self.clock_samples: deque[tuple[float, float]] = deque(maxlen=10000)
        self.performance: dict[str, Any] | None = None
        for topic, window in self.windows.items():
            rospy.Subscriber(topic, rospy.AnyMsg, self._topic_cb, callback_args=window, queue_size=100)
        rospy.Subscriber(args.clock_topic, Clock, self._clock_cb, queue_size=100)
        rospy.Subscriber(args.performance_topic, PerformanceMetrics, self._performance_cb, queue_size=10)

    @staticmethod
    def _topic_cb(message: Any, window: TopicWindow) -> None:
        payload = getattr(message, "_buff", b"")
        window.observe(len(payload))

    def _clock_cb(self, message: Any) -> None:
        self.clock_samples.append((time.monotonic(), message.clock.to_sec()))
        cutoff = time.monotonic() - self.args.window_s
        while self.clock_samples and self.clock_samples[0][0] < cutoff:
            self.clock_samples.popleft()

    def _performance_cb(self, message: Any) -> None:
        self.performance = {
            "real_time_factor": float(message.real_time_factor),
            "sensors": [
                {
                    "name": sensor.name,
                    "sim_update_rate_hz": float(sensor.sim_update_rate),
                    "real_update_rate_hz": float(sensor.real_update_rate),
                    "fps": float(sensor.fps),
                }
                for sensor in message.sensors
            ],
            "received_at_unix": time.time(),
        }

    def clock_rtf(self) -> float | None:
        if len(self.clock_samples) < 2:
            return None
        wall_delta = self.clock_samples[-1][0] - self.clock_samples[0][0]
        sim_delta = self.clock_samples[-1][1] - self.clock_samples[0][1]
        return None if wall_delta <= 0.0 else sim_delta / wall_delta

    def snapshot(self) -> dict[str, Any]:
        return {
            "schema": "mosim.ros1_runtime_observability.v1",
            "run_id": self.args.run_id,
            "window_s": self.args.window_s,
            "topics": {topic: window.snapshot() for topic, window in self.windows.items()},
            "gazebo": {
                "clock_derived_real_time_factor": self.clock_rtf(),
                "performance_metrics": self.performance,
            },
            "unavailable_metrics": [
                "topic_queue_drop_rate_without_ros_statistics",
                "cross_host_one_way_delay_without_clock_sync",
                "rviz_render_fps_without_viewer_instrumentation",
            ],
            "updated_at_unix": time.time(),
        }

    def run(self) -> None:
        rate = self.rospy.Rate(self.args.output_rate_hz)
        while not self.rospy.is_shutdown():
            atomic_json(self.args.output, self.snapshot())
            if self.args.duration_s > 0.0 and time.monotonic() - self.started >= self.args.duration_s:
                return
            rate.sleep()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--topic", action="append", default=[])
    parser.add_argument("--clock-topic", default="/clock")
    parser.add_argument("--performance-topic", default="/gazebo/performance_metrics")
    parser.add_argument("--window-s", type=float, default=5.0)
    parser.add_argument("--output-rate-hz", type=float, default=1.0)
    parser.add_argument("--duration-s", type=float, default=0.0)
    args = parser.parse_args()
    if not args.topic:
        args.topic = list(DEFAULT_TOPICS)
    return args


def main() -> int:
    args = parse_args()
    if args.window_s <= 0.0 or args.output_rate_hz <= 0.0 or args.duration_s < 0.0:
        raise SystemExit("invalid observability sampling configuration")
    import rospy

    rospy.init_node("mosim_runtime_observability", anonymous=False)
    Ros1Collector(args).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
