#!/usr/bin/env python3
"""Measure Gazebo wall-clock pacing without changing a running ROS graph."""

from __future__ import annotations

import argparse
import json
import os
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def project_result_path(value: str) -> Path:
    path = Path(value)
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    results_root = (ROOT / "Results").resolve()
    if resolved != results_root and results_root not in resolved.parents:
        raise ValueError(f"--output must remain below {results_root}: {value}")
    return resolved


@dataclass
class CloudSnapshot:
    messages: int = 0
    nonempty_messages: int = 0
    latest_point_count: int = 0
    latest_data_bytes: int = 0
    latest_frame_id: str = ""
    latest_stamp_s: float | None = None


class MeasurementState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.clock_s: float | None = None
        self.performance: dict[str, Any] | None = None
        self.raw_cloud = CloudSnapshot()
        self.occupancy_cloud = CloudSnapshot()

    @staticmethod
    def _record_cloud(snapshot: CloudSnapshot, message: Any) -> None:
        snapshot.messages += 1
        point_count = int(message.width) * int(message.height)
        data_bytes = len(message.data)
        if point_count > 0 and data_bytes > 0:
            snapshot.nonempty_messages += 1
        snapshot.latest_point_count = point_count
        snapshot.latest_data_bytes = data_bytes
        snapshot.latest_frame_id = str(message.header.frame_id)
        snapshot.latest_stamp_s = message.header.stamp.to_sec()

    def record_clock(self, message: Any) -> None:
        with self.lock:
            self.clock_s = message.clock.to_sec()

    def record_performance(self, message: Any) -> None:
        sensors = [
            {
                "name": str(sensor.name),
                "sim_update_rate": float(sensor.sim_update_rate),
                "real_update_rate": float(sensor.real_update_rate),
                "fps": float(sensor.fps),
            }
            for sensor in message.sensors
        ]
        with self.lock:
            self.performance = {
                "header_stamp_s": message.header.stamp.to_sec(),
                "real_time_factor": float(message.real_time_factor),
                "sensors": sensors,
            }

    def record_raw_cloud(self, message: Any) -> None:
        with self.lock:
            self._record_cloud(self.raw_cloud, message)

    def record_occupancy_cloud(self, message: Any) -> None:
        with self.lock:
            self._record_cloud(self.occupancy_cloud, message)

    def snapshot(self) -> dict[str, Any]:
        with self.lock:
            return {
                "clock_s": self.clock_s,
                "performance": self.performance,
                "raw_cloud": self.raw_cloud.__dict__.copy(),
                "occupancy_cloud": self.occupancy_cloud.__dict__.copy(),
            }


def wait_for_initial_data(state: MeasurementState, timeout_s: float) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        snapshot = state.snapshot()
        if (
            snapshot["clock_s"] is not None
            and snapshot["raw_cloud"]["nonempty_messages"] > 0
            and snapshot["occupancy_cloud"]["messages"] > 0
        ):
            return True
        time.sleep(0.05)
    return False


def cloud_summary(snapshot: dict[str, Any], initial_messages: int, duration_s: float) -> dict[str, Any]:
    messages = int(snapshot["messages"])
    observed_messages = max(0, messages - initial_messages)
    return {
        "messages_before_window": initial_messages,
        "messages_in_window": observed_messages,
        "wall_rate_hz": observed_messages / duration_s if duration_s > 0 else None,
        "nonempty_messages_total": int(snapshot["nonempty_messages"]),
        "latest_point_count": int(snapshot["latest_point_count"]),
        "latest_data_bytes": int(snapshot["latest_data_bytes"]),
        "latest_frame_id": str(snapshot["latest_frame_id"]),
        "latest_stamp_s": snapshot["latest_stamp_s"],
    }


def measurement_status(
    initial_data_ready: bool,
    data_plane_retained: bool,
    clock_rtf: float | None,
    min_rtf: float,
) -> str:
    """Return the overall result for a real-time data-plane measurement."""
    if not initial_data_ready or not data_plane_retained or clock_rtf is None:
        return "blocked"
    return "passed" if clock_rtf >= min_rtf else "blocked"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="JSON result path below Results/")
    parser.add_argument("--duration-s", type=float, default=30.0)
    parser.add_argument("--initial-wait-s", type=float, default=20.0)
    parser.add_argument("--min-rtf", type=float, default=0.95)
    parser.add_argument("--clock-topic", default="/clock")
    parser.add_argument("--performance-topic", default="/gazebo/performance_metrics")
    parser.add_argument("--raw-cloud-topic", default="/uav1/livox/lidar")
    parser.add_argument(
        "--occupancy-topic",
        default="/drone_0_ego_planner_node/grid_map/occupancy_inflate",
    )
    args = parser.parse_args()
    if args.duration_s <= 0:
        parser.error("--duration-s must be positive")
    if args.initial_wait_s <= 0:
        parser.error("--initial-wait-s must be positive")
    if not 0 < args.min_rtf <= 1:
        parser.error("--min-rtf must be in (0, 1]")
    return args


def main() -> int:
    args = parse_args()
    output_path = project_result_path(args.output)

    import rospy
    from gazebo_msgs.msg import PerformanceMetrics
    from rosgraph_msgs.msg import Clock
    from sensor_msgs.msg import PointCloud2

    state = MeasurementState()
    rospy.init_node("mosim_realtime_data_plane_measurement", anonymous=True, disable_signals=True)
    rospy.Subscriber(args.clock_topic, Clock, state.record_clock, queue_size=10)
    rospy.Subscriber(args.performance_topic, PerformanceMetrics, state.record_performance, queue_size=2)
    rospy.Subscriber(args.raw_cloud_topic, PointCloud2, state.record_raw_cloud, queue_size=10)
    rospy.Subscriber(args.occupancy_topic, PointCloud2, state.record_occupancy_cloud, queue_size=10)

    initial_ready = wait_for_initial_data(state, args.initial_wait_s)
    start = state.snapshot()
    wall_start = time.monotonic()
    deadline = wall_start + args.duration_s
    while not rospy.is_shutdown() and time.monotonic() < deadline:
        time.sleep(0.05)
    wall_end = time.monotonic()
    end = state.snapshot()
    wall_span_s = wall_end - wall_start

    start_clock_s = start["clock_s"]
    end_clock_s = end["clock_s"]
    sim_span_s = None
    clock_rtf = None
    if start_clock_s is not None and end_clock_s is not None:
        sim_span_s = float(end_clock_s) - float(start_clock_s)
        clock_rtf = sim_span_s / wall_span_s

    raw_cloud = cloud_summary(end["raw_cloud"], int(start["raw_cloud"]["messages"]), wall_span_s)
    occupancy_cloud = cloud_summary(
        end["occupancy_cloud"], int(start["occupancy_cloud"]["messages"]), wall_span_s
    )
    # The planner may correctly publish an empty obstacle cloud when no occupied
    # cells are inside its local window. Preserve liveness and content as separate
    # observations instead of treating an empty local window as a broken grid.
    data_plane_retained = (
        raw_cloud["messages_in_window"] > 0
        and occupancy_cloud["messages_in_window"] > 0
        and raw_cloud["latest_point_count"] > 0
    )
    realtime_restored = clock_rtf is not None and clock_rtf >= args.min_rtf
    status = measurement_status(initial_ready, data_plane_retained, clock_rtf, args.min_rtf)

    payload = {
        "schema": "mosim.gazebo_realtime_data_plane_measurement.v1",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "configuration": {
            "duration_s_requested": args.duration_s,
            "initial_wait_s": args.initial_wait_s,
            "min_rtf": args.min_rtf,
            "clock_topic": args.clock_topic,
            "performance_topic": args.performance_topic,
            "raw_cloud_topic": args.raw_cloud_topic,
            "occupancy_topic": args.occupancy_topic,
        },
        "wall_clock_measurement": {
            "window_s": wall_span_s,
            "sim_start_s": start_clock_s,
            "sim_end_s": end_clock_s,
            "sim_span_s": sim_span_s,
            "clock_real_time_factor": clock_rtf,
        },
        "gazebo_performance_metrics": end["performance"],
        "data_plane": {
            "raw_cloud": raw_cloud,
            "occupancy": occupancy_cloud,
            "retained": data_plane_retained,
            "occupancy_payload_nonempty": occupancy_cloud["latest_point_count"] > 0,
        },
        "conclusion": {
            "realtime_restored": realtime_restored,
            "initial_data_ready": initial_ready,
            "data_plane_retained": data_plane_retained,
            "claim_boundary": (
                "This is a read-only live ROS observation. It measures pacing and topic continuity; "
                "it does not prove visual review, planner success, controller performance, or flight acceptance."
            ),
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = output_path.with_suffix(output_path.suffix + ".tmp")
    temporary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary_path, output_path)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
