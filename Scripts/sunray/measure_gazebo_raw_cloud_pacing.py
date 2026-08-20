#!/usr/bin/env python3
"""Measure Gazebo pacing while retaining a raw PointCloud2 observation."""

from __future__ import annotations

import argparse
import json
import math
import os
import struct
import threading
import time
from dataclasses import dataclass, field
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
    latest_point_step: int = 0
    latest_row_step: int = 0
    latest_is_bigendian: bool = False
    latest_fields: list[dict[str, int | str]] | None = None
    latest_xyz_summary: dict[str, Any] | None = None
    observations: list[dict[str, float | bool]] = field(default_factory=list)


class MeasurementState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.clock_s: float | None = None
        self.performance: dict[str, Any] | None = None
        self.raw_cloud = CloudSnapshot()

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
        arrival_monotonic_s = time.monotonic()
        point_count = int(message.width) * int(message.height)
        data_bytes = len(message.data)
        header_stamp_s = message.header.stamp.to_sec()
        nonempty = point_count > 0 and data_bytes > 0
        fields = [
            {
                "name": str(field.name),
                "offset": int(field.offset),
                "datatype": int(field.datatype),
                "count": int(field.count),
            }
            for field in message.fields
        ]
        xyz_summary = pointcloud_xyz_summary(
            bytes(message.data),
            point_count,
            int(message.point_step),
            fields,
            bool(message.is_bigendian),
        )
        with self.lock:
            self.raw_cloud.messages += 1
            if nonempty:
                self.raw_cloud.nonempty_messages += 1
            self.raw_cloud.latest_point_count = point_count
            self.raw_cloud.latest_data_bytes = data_bytes
            self.raw_cloud.latest_frame_id = str(message.header.frame_id)
            self.raw_cloud.latest_stamp_s = header_stamp_s
            self.raw_cloud.latest_point_step = int(message.point_step)
            self.raw_cloud.latest_row_step = int(message.row_step)
            self.raw_cloud.latest_is_bigendian = bool(message.is_bigendian)
            self.raw_cloud.latest_fields = fields
            self.raw_cloud.latest_xyz_summary = xyz_summary
            self.raw_cloud.observations.append(
                {
                    "arrival_monotonic_s": arrival_monotonic_s,
                    "header_stamp_s": header_stamp_s,
                    "nonempty": nonempty,
                }
            )

    def snapshot(self) -> dict[str, Any]:
        with self.lock:
            raw_cloud = self.raw_cloud.__dict__.copy()
            raw_cloud["latest_fields"] = list(self.raw_cloud.latest_fields or [])
            raw_cloud["latest_xyz_summary"] = dict(self.raw_cloud.latest_xyz_summary or {})
            raw_cloud["observations"] = list(self.raw_cloud.observations)
            return {
                "clock_s": self.clock_s,
                "performance": self.performance,
                "raw_cloud": raw_cloud,
            }


def wait_for_initial_data(state: MeasurementState, timeout_s: float) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        snapshot = state.snapshot()
        if (
            snapshot["clock_s"] is not None
            and snapshot["raw_cloud"]["nonempty_messages"] > 0
        ):
            return True
        time.sleep(0.05)
    return False


def continuity_summary(
    observations: list[dict[str, float | bool]],
    window_start_monotonic_s: float,
    window_end_monotonic_s: float,
) -> dict[str, float | int | None]:
    nonempty = [observation for observation in observations if bool(observation["nonempty"])]
    in_window = [
        observation
        for observation in nonempty
        if window_start_monotonic_s <= float(observation["arrival_monotonic_s"]) <= window_end_monotonic_s
    ]
    before_window = [
        observation
        for observation in nonempty
        if float(observation["arrival_monotonic_s"]) < window_start_monotonic_s
    ]

    wall_gaps: list[float] = []
    header_gaps: list[float] = []
    previous = before_window[-1] if before_window else None
    for observation in in_window:
        if previous is not None:
            wall_gaps.append(
                float(observation["arrival_monotonic_s"])
                - float(previous["arrival_monotonic_s"])
            )
            header_gap_s = float(observation["header_stamp_s"]) - float(previous["header_stamp_s"])
            if header_gap_s >= 0.0:
                header_gaps.append(header_gap_s)
        else:
            wall_gaps.append(float(observation["arrival_monotonic_s"]) - window_start_monotonic_s)
        previous = observation

    if in_window:
        wall_gaps.append(window_end_monotonic_s - float(in_window[-1]["arrival_monotonic_s"]))

    return {
        "nonempty_observations_in_window": len(in_window),
        "first_nonempty_arrival_offset_s": (
            float(in_window[0]["arrival_monotonic_s"]) - window_start_monotonic_s if in_window else None
        ),
        "last_nonempty_arrival_offset_s": (
            float(in_window[-1]["arrival_monotonic_s"]) - window_start_monotonic_s if in_window else None
        ),
        "max_nonempty_wall_gap_s": max(wall_gaps) if wall_gaps else None,
        "max_nonempty_header_gap_s": max(header_gaps) if header_gaps else None,
    }


def pointcloud_xyz_summary(
    data: bytes,
    point_count: int,
    point_step: int,
    fields: list[dict[str, int | str]],
    is_bigendian: bool,
) -> dict[str, Any]:
    field_offsets = {
        str(field["name"]): int(field["offset"])
        for field in fields
        if int(field["datatype"]) == 7 and int(field["count"]) == 1
    }
    if point_count <= 0 or point_step <= 0 or not {"x", "y", "z"}.issubset(field_offsets):
        return {"status": "unavailable"}
    if any(offset + 4 > point_step for offset in field_offsets.values()):
        return {"status": "invalid_field_layout"}
    if len(data) < point_count * point_step:
        return {"status": "truncated_data"}

    unpack = struct.Struct((">" if is_bigendian else "<") + "f").unpack_from
    finite_points = 0
    minimum = [float("inf")] * 3
    maximum = [float("-inf")] * 3
    sums = [0.0] * 3
    sums_squared = [0.0] * 3
    for point_index in range(point_count):
        base = point_index * point_step
        xyz = [unpack(data, base + field_offsets[axis])[0] for axis in ("x", "y", "z")]
        if not all(math.isfinite(value) for value in xyz):
            continue
        finite_points += 1
        for index, value in enumerate(xyz):
            minimum[index] = min(minimum[index], value)
            maximum[index] = max(maximum[index], value)
            sums[index] += value
            sums_squared[index] += value * value
    if finite_points == 0:
        return {"status": "no_finite_xyz", "point_count": point_count}
    return {
        "status": "available",
        "point_count": point_count,
        "finite_point_count": finite_points,
        "min_xyz": minimum,
        "max_xyz": maximum,
        "sum_xyz": sums,
        "sum_squared_xyz": sums_squared,
    }


def cloud_stream_continuous(
    raw_cloud_retained: bool,
    max_gap_s: float | int | None,
    nominal_max_gap_s: float,
    scheduling_tolerance_s: float,
) -> bool:
    if not raw_cloud_retained or max_gap_s is None:
        return False
    return float(max_gap_s) <= nominal_max_gap_s + scheduling_tolerance_s


def raw_cloud_summary(
    snapshot: dict[str, Any],
    initial_messages: int,
    initial_nonempty_messages: int,
    duration_s: float,
    window_start_monotonic_s: float,
    window_end_monotonic_s: float,
) -> dict[str, Any]:
    observed_messages = max(0, int(snapshot["messages"]) - initial_messages)
    observed_nonempty_messages = max(0, int(snapshot["nonempty_messages"]) - initial_nonempty_messages)
    return {
        "messages_before_window": initial_messages,
        "messages_in_window": observed_messages,
        "wall_rate_hz": observed_messages / duration_s if duration_s > 0 else None,
        "nonempty_messages_total": int(snapshot["nonempty_messages"]),
        "nonempty_messages_in_window": observed_nonempty_messages,
        "latest_point_count": int(snapshot["latest_point_count"]),
        "latest_data_bytes": int(snapshot["latest_data_bytes"]),
        "latest_frame_id": str(snapshot["latest_frame_id"]),
        "latest_stamp_s": snapshot["latest_stamp_s"],
        "latest_point_step": int(snapshot["latest_point_step"]),
        "latest_row_step": int(snapshot["latest_row_step"]),
        "latest_is_bigendian": bool(snapshot["latest_is_bigendian"]),
        "latest_fields": snapshot["latest_fields"] or [],
        "latest_xyz_summary": snapshot["latest_xyz_summary"] or {},
        "continuity": continuity_summary(
            list(snapshot.get("observations") or []),
            window_start_monotonic_s,
            window_end_monotonic_s,
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="JSON result path below Results/")
    parser.add_argument("--duration-s", type=float, default=30.0)
    parser.add_argument("--initial-wait-s", type=float, default=180.0)
    parser.add_argument("--min-rtf", type=float, default=0.95)
    parser.add_argument("--clock-topic", default="/clock")
    parser.add_argument("--performance-topic", default="/gazebo/performance_metrics")
    parser.add_argument("--raw-cloud-topic", default="/uav1/livox/lidar")
    parser.add_argument(
        "--max-cloud-wall-gap-s",
        type=float,
        default=0.25,
        help="Maximum accepted nonempty PointCloud2 wall-clock gap during the measurement window.",
    )
    parser.add_argument(
        "--cloud-gap-scheduling-tolerance-s",
        type=float,
        default=0.005,
        help="Additional bounded scheduling tolerance for the PointCloud2 wall-gap check.",
    )
    args = parser.parse_args()
    if args.duration_s <= 0 or args.initial_wait_s <= 0:
        parser.error("--duration-s and --initial-wait-s must be positive")
    if not 0 < args.min_rtf <= 1:
        parser.error("--min-rtf must be in (0, 1]")
    if args.max_cloud_wall_gap_s <= 0:
        parser.error("--max-cloud-wall-gap-s must be positive")
    if args.cloud_gap_scheduling_tolerance_s < 0:
        parser.error("--cloud-gap-scheduling-tolerance-s must be non-negative")
    return args


def write_payload(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary_path, path)


def main() -> int:
    args = parse_args()
    output_path = project_result_path(args.output)

    import rospy
    from gazebo_msgs.msg import PerformanceMetrics
    from rosgraph_msgs.msg import Clock
    from sensor_msgs.msg import PointCloud2

    state = MeasurementState()
    rospy.init_node("mosim_gazebo_raw_cloud_pacing", anonymous=True, disable_signals=True)
    rospy.Subscriber(args.clock_topic, Clock, state.record_clock, queue_size=10)
    rospy.Subscriber(args.performance_topic, PerformanceMetrics, state.record_performance, queue_size=2)
    rospy.Subscriber(args.raw_cloud_topic, PointCloud2, state.record_raw_cloud, queue_size=10)

    initial_data_ready = wait_for_initial_data(state, args.initial_wait_s)
    wall_start = time.monotonic()
    start = state.snapshot()
    if initial_data_ready:
        deadline = wall_start + args.duration_s
        while not rospy.is_shutdown() and time.monotonic() < deadline:
            time.sleep(0.05)
    wall_end = time.monotonic()
    wall_span_s = wall_end - wall_start
    end = state.snapshot()

    start_clock_s = start["clock_s"] if initial_data_ready else None
    end_clock_s = end["clock_s"] if initial_data_ready else None
    sim_span_s = None
    clock_rtf = None
    if start_clock_s is not None and end_clock_s is not None:
        sim_span_s = float(end_clock_s) - float(start_clock_s)
        clock_rtf = sim_span_s / wall_span_s

    initial_raw_messages = int(start["raw_cloud"]["messages"]) if initial_data_ready else 0
    initial_nonempty_messages = int(start["raw_cloud"]["nonempty_messages"]) if initial_data_ready else 0
    raw_cloud = raw_cloud_summary(
        end["raw_cloud"],
        initial_raw_messages,
        initial_nonempty_messages,
        wall_span_s,
        wall_start,
        wall_end,
    )
    raw_cloud_retained = (
        initial_data_ready
        and raw_cloud["messages_in_window"] > 0
        and raw_cloud["nonempty_messages_in_window"] > 0
        and raw_cloud["latest_point_count"] > 0
        and raw_cloud["latest_data_bytes"] > 0
    )
    max_cloud_gap_s = raw_cloud["continuity"]["max_nonempty_wall_gap_s"]
    raw_cloud_continuous = cloud_stream_continuous(
        raw_cloud_retained,
        max_cloud_gap_s,
        args.max_cloud_wall_gap_s,
        args.cloud_gap_scheduling_tolerance_s,
    )
    observation_valid = initial_data_ready and raw_cloud_continuous
    realtime_restored = observation_valid and clock_rtf is not None and clock_rtf >= args.min_rtf

    payload = {
        "schema": "mosim.gazebo_raw_cloud_pacing_measurement.v1",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if realtime_restored else "blocked",
        "configuration": {
            "duration_s_requested": args.duration_s,
            "initial_wait_s": args.initial_wait_s,
            "min_rtf": args.min_rtf,
            "clock_topic": args.clock_topic,
            "performance_topic": args.performance_topic,
            "raw_cloud_topic": args.raw_cloud_topic,
            "max_cloud_wall_gap_s": args.max_cloud_wall_gap_s,
            "cloud_gap_scheduling_tolerance_s": args.cloud_gap_scheduling_tolerance_s,
        },
        "wall_clock_measurement": {
            "window_s": wall_span_s,
            "sim_start_s": start_clock_s,
            "sim_end_s": end_clock_s,
            "sim_span_s": sim_span_s,
            "clock_real_time_factor": clock_rtf,
        },
        "gazebo_performance_metrics": end["performance"],
        "raw_cloud": raw_cloud,
        "conclusion": {
            "observation_valid": observation_valid,
            "initial_data_ready": initial_data_ready,
            "raw_cloud_retained": raw_cloud_retained,
            "raw_cloud_continuous": raw_cloud_continuous,
            "raw_cloud_continuity_effective_limit_s": (
                args.max_cloud_wall_gap_s + args.cloud_gap_scheduling_tolerance_s
            ),
            "gazebo_performance_metrics_available": end["performance"] is not None,
            "realtime_restored": realtime_restored,
            "claim_boundary": (
                "This is a read-only Gazebo and raw PointCloud2 observation. It measures pacing and "
                "raw-cloud continuity only; it does not prove planner, controller, PX4, or flight acceptance."
            ),
        },
    }
    write_payload(output_path, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if realtime_restored else 1


if __name__ == "__main__":
    raise SystemExit(main())
