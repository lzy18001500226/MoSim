#!/usr/bin/env python3
"""Publish one timestamp-consistent FAST-LIO odometry stream to MAVROS."""

from __future__ import annotations

import argparse
import copy
import json
import math
import time
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import rospy
from nav_msgs.msg import Odometry


Vec3 = Tuple[float, float, float]
Quat = Tuple[float, float, float, float]
Matrix3 = List[List[float]]


def all_finite(values: Iterable[float]) -> bool:
    return all(math.isfinite(float(value)) for value in values)


def normalize_quaternion(quaternion: Sequence[float]) -> Quat:
    x, y, z, w = (float(value) for value in quaternion)
    norm = math.sqrt(x * x + y * y + z * z + w * w)
    if not math.isfinite(norm) or norm < 1e-9:
        raise ValueError("invalid zero or nonfinite quaternion")
    return x / norm, y / norm, z / norm, w / norm


def body_to_world_rotation(quaternion: Sequence[float]) -> Matrix3:
    x, y, z, w = normalize_quaternion(quaternion)
    return [
        [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w)],
        [2.0 * (x * y + z * w), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - x * w)],
        [2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x * x + y * y)],
    ]


def transpose(matrix: Matrix3) -> Matrix3:
    return [[matrix[col][row] for col in range(3)] for row in range(3)]


def mat_vec(matrix: Matrix3, vector: Sequence[float]) -> Vec3:
    values = [float(value) for value in vector]
    return tuple(sum(matrix[row][col] * values[col] for col in range(3)) for row in range(3))  # type: ignore[return-value]


def mat_mul(left: Matrix3, right: Matrix3) -> Matrix3:
    return [
        [sum(left[row][k] * right[k][col] for k in range(3)) for col in range(3)]
        for row in range(3)
    ]


def world_to_body_vector(quaternion: Sequence[float], vector: Sequence[float]) -> Vec3:
    return mat_vec(transpose(body_to_world_rotation(quaternion)), vector)


def covariance_block(covariance: Sequence[float], row_offset: int = 0, col_offset: int = 0) -> Matrix3:
    if len(covariance) != 36:
        return [[0.0] * 3 for _ in range(3)]
    block = []
    for row in range(3):
        block_row = []
        for col in range(3):
            value = float(covariance[(row + row_offset) * 6 + col + col_offset])
            block_row.append(value if math.isfinite(value) else 0.0)
        block.append(block_row)
    return block


def rotate_covariance_world_to_body(quaternion: Sequence[float], covariance: Matrix3) -> Matrix3:
    world_to_body = transpose(body_to_world_rotation(quaternion))
    return mat_mul(mat_mul(world_to_body, covariance), transpose(world_to_body))


def covariance_with_floors(
    source: Sequence[float],
    linear_stddev: float,
    angular_stddev: float,
    linear_rotation: Optional[Matrix3] = None,
) -> List[float]:
    result = [0.0] * 36
    linear = covariance_block(source)
    if linear_rotation is not None:
        linear = mat_mul(mat_mul(linear_rotation, linear), transpose(linear_rotation))
    for row in range(3):
        for col in range(3):
            result[row * 6 + col] = linear[row][col]
    linear_variance = linear_stddev * linear_stddev
    angular_variance = angular_stddev * angular_stddev
    for axis in range(3):
        result[axis * 6 + axis] = max(result[axis * 6 + axis], linear_variance)
        result[(axis + 3) * 6 + axis + 3] = angular_variance
    return result


class FastlioMavrosOdometryAdapter:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.publisher = rospy.Publisher(args.output_topic, Odometry, queue_size=20)
        self.started_wall = time.time()
        self.last_diagnostics_wall = 0.0
        self.last_accepted_stamp_ns = 0
        self.first_output_stamp_s = None
        self.last_input_stamp_s = None
        self.last_output_stamp_s = None
        self.last_age_s = None
        self.max_age_s = 0.0
        self.age_sum_s = 0.0
        self.last_world_velocity = None
        self.last_body_velocity = None
        self.current_stale_run = 0
        self.max_stale_run = 0
        self.first_stale_ros_time_s = None
        self.last_stale_ros_time_s = None
        self.counts = {
            "received": 0,
            "published": 0,
            "dropped_nonfinite": 0,
            "dropped_zero_stamp": 0,
            "dropped_stale": 0,
            "dropped_future": 0,
            "dropped_duplicate": 0,
            "dropped_out_of_order": 0,
            "dropped_frame_mismatch": 0,
        }
        rospy.Subscriber(args.input_topic, Odometry, self.on_odometry, queue_size=50)
        rospy.on_shutdown(lambda: self.write_diagnostics(force=True))

    @staticmethod
    def pose_values(msg: Odometry) -> Tuple[Vec3, Quat]:
        position = msg.pose.pose.position
        orientation = msg.pose.pose.orientation
        return (
            (float(position.x), float(position.y), float(position.z)),
            (float(orientation.x), float(orientation.y), float(orientation.z), float(orientation.w)),
        )

    @staticmethod
    def linear_velocity(msg: Odometry) -> Vec3:
        velocity = msg.twist.twist.linear
        return float(velocity.x), float(velocity.y), float(velocity.z)

    def record_drop_event(self, reason: str, msg: Odometry, age_s: Optional[float]) -> None:
        if not self.args.events_jsonl:
            return
        event = {
            "wall_time_s": time.time(),
            "ros_time_s": rospy.Time.now().to_sec(),
            "measurement_stamp_s": msg.header.stamp.to_sec(),
            "age_s": age_s,
            "reason": reason,
            "received": self.counts["received"],
            "published": self.counts["published"],
            "consecutive_stale": self.current_stale_run,
        }
        path = Path(self.args.events_jsonl)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, sort_keys=True) + "\n")

    def drop(self, reason: str, msg: Odometry, age_s: Optional[float] = None) -> None:
        self.counts[reason] += 1
        if reason == "dropped_stale":
            self.current_stale_run += 1
            self.max_stale_run = max(self.max_stale_run, self.current_stale_run)
            ros_time_s = rospy.Time.now().to_sec()
            if self.first_stale_ros_time_s is None:
                self.first_stale_ros_time_s = ros_time_s
            self.last_stale_ros_time_s = ros_time_s
        else:
            self.current_stale_run = 0
        self.record_drop_event(reason, msg, age_s)
        self.write_diagnostics()

    def on_odometry(self, msg: Odometry) -> None:
        self.counts["received"] += 1
        if self.args.expected_input_frame and msg.header.frame_id != self.args.expected_input_frame:
            rospy.logerr_throttle(
                5.0,
                "FAST-LIO ODOMETRY input frame mismatch: expected=%s actual=%s",
                self.args.expected_input_frame,
                msg.header.frame_id,
            )
            self.drop("dropped_frame_mismatch", msg)
            return

        stamp_ns = int(msg.header.stamp.to_nsec())
        if stamp_ns <= 0:
            self.drop("dropped_zero_stamp", msg)
            return
        if stamp_ns == self.last_accepted_stamp_ns:
            self.drop("dropped_duplicate", msg)
            return
        if stamp_ns < self.last_accepted_stamp_ns:
            self.drop("dropped_out_of_order", msg)
            return

        now = rospy.Time.now()
        age_s = now.to_sec() - msg.header.stamp.to_sec() if now.to_sec() > 0.0 else 0.0
        if age_s > self.args.max_age_s:
            self.drop("dropped_stale", msg, age_s)
            return
        if age_s < -self.args.max_future_s:
            self.drop("dropped_future", msg, age_s)
            return

        position, quaternion_raw = self.pose_values(msg)
        world_velocity = self.linear_velocity(msg)
        if not all_finite((*position, *quaternion_raw, *world_velocity)):
            self.drop("dropped_nonfinite", msg, age_s)
            return
        try:
            quaternion = normalize_quaternion(quaternion_raw)
        except ValueError:
            self.drop("dropped_nonfinite", msg, age_s)
            return

        if self.args.input_twist_frame == "world":
            body_velocity = world_to_body_vector(quaternion, world_velocity)
            velocity_rotation = transpose(body_to_world_rotation(quaternion))
        else:
            body_velocity = world_velocity
            velocity_rotation = None

        if not all_finite(body_velocity):
            self.drop("dropped_nonfinite", msg, age_s)
            return

        out = copy.deepcopy(msg)
        out.header.frame_id = self.args.output_frame
        out.child_frame_id = self.args.output_child_frame
        out.pose.pose.orientation.x = quaternion[0]
        out.pose.pose.orientation.y = quaternion[1]
        out.pose.pose.orientation.z = quaternion[2]
        out.pose.pose.orientation.w = quaternion[3]
        out.twist.twist.linear.x = body_velocity[0]
        out.twist.twist.linear.y = body_velocity[1]
        out.twist.twist.linear.z = body_velocity[2]
        out.twist.twist.angular.x = 0.0
        out.twist.twist.angular.y = 0.0
        out.twist.twist.angular.z = 0.0
        out.pose.covariance = covariance_with_floors(
            msg.pose.covariance,
            self.args.position_stddev_m,
            self.args.orientation_stddev_rad,
        )
        out.twist.covariance = covariance_with_floors(
            msg.twist.covariance,
            self.args.velocity_stddev_mps,
            self.args.angular_velocity_stddev_rps,
            linear_rotation=velocity_rotation,
        )

        self.publisher.publish(out)
        self.current_stale_run = 0
        self.last_accepted_stamp_ns = stamp_ns
        self.last_input_stamp_s = msg.header.stamp.to_sec()
        self.last_output_stamp_s = out.header.stamp.to_sec()
        if self.first_output_stamp_s is None:
            self.first_output_stamp_s = out.header.stamp.to_sec()
        self.last_age_s = age_s
        self.max_age_s = max(self.max_age_s, max(0.0, age_s))
        self.age_sum_s += max(0.0, age_s)
        self.last_world_velocity = list(world_velocity)
        self.last_body_velocity = list(body_velocity)
        self.counts["published"] += 1
        self.write_diagnostics()

    def write_diagnostics(self, force: bool = False) -> None:
        if not self.args.diagnostics_json:
            return
        now = time.time()
        if not force and now - self.last_diagnostics_wall < 1.0:
            return
        self.last_diagnostics_wall = now
        published = self.counts["published"]
        elapsed = max(1e-6, now - self.started_wall)
        data = {
            "schema": "mosim.fastlio_mavros_odometry_adapter.v1",
            "input_topic": self.args.input_topic,
            "output_topic": self.args.output_topic,
            "expected_input_frame": self.args.expected_input_frame,
            "output_frame": self.args.output_frame,
            "output_child_frame": self.args.output_child_frame,
            "input_twist_frame": self.args.input_twist_frame,
            "timestamp_policy": "preserve_measurement_stamp",
            "counts": dict(self.counts),
            "published_wall_rate_hz": published / elapsed,
            "last_input_stamp_s": self.last_input_stamp_s,
            "first_output_stamp_s": self.first_output_stamp_s,
            "last_output_stamp_s": self.last_output_stamp_s,
            "last_input_output_stamp_delta_s": (
                self.last_output_stamp_s - self.last_input_stamp_s
                if self.last_input_stamp_s is not None and self.last_output_stamp_s is not None
                else None
            ),
            "last_age_s": self.last_age_s,
            "mean_accepted_age_s": self.age_sum_s / published if published else None,
            "max_accepted_age_s": self.max_age_s if published else None,
            "stale_bursts": {
                "current_consecutive": self.current_stale_run,
                "max_consecutive": self.max_stale_run,
                "first_ros_time_s": self.first_stale_ros_time_s,
                "last_ros_time_s": self.last_stale_ros_time_s,
                "events_jsonl": self.args.events_jsonl or None,
            },
            "published_measurement_rate_hz": (
                (published - 1) / (self.last_output_stamp_s - self.first_output_stamp_s)
                if published > 1
                and self.first_output_stamp_s is not None
                and self.last_output_stamp_s is not None
                and self.last_output_stamp_s > self.first_output_stamp_s
                else None
            ),
            "last_world_velocity_mps": self.last_world_velocity,
            "last_body_velocity_mps": self.last_body_velocity,
            "covariance_stddev": {
                "position_m": self.args.position_stddev_m,
                "orientation_rad": self.args.orientation_stddev_rad,
                "velocity_mps": self.args.velocity_stddev_mps,
                "angular_velocity_rps": self.args.angular_velocity_stddev_rps,
            },
        }
        path = Path(self.args.diagnostics_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--node-name", default="mosim_fastlio_mavros_odometry_adapter")
    parser.add_argument("--input-topic", default="/mosim/fastlio/odom_aligned")
    parser.add_argument("--output-topic", default="/uav1/mavros/odometry/out")
    parser.add_argument("--expected-input-frame", default="world")
    parser.add_argument("--output-frame", default="odom")
    parser.add_argument("--output-child-frame", default="base_link")
    parser.add_argument("--input-twist-frame", choices=["world", "body"], default="world")
    parser.add_argument("--max-age-s", type=float, default=0.25)
    parser.add_argument("--max-future-s", type=float, default=0.05)
    parser.add_argument("--position-stddev-m", type=float, default=0.15)
    parser.add_argument("--orientation-stddev-rad", type=float, default=0.35)
    parser.add_argument("--velocity-stddev-mps", type=float, default=0.20)
    parser.add_argument("--angular-velocity-stddev-rps", type=float, default=1.0)
    parser.add_argument("--diagnostics-json", default="")
    parser.add_argument("--events-jsonl", default="")
    args = parser.parse_args()

    for name in (
        "max_age_s",
        "max_future_s",
        "position_stddev_m",
        "orientation_stddev_rad",
        "velocity_stddev_mps",
        "angular_velocity_stddev_rps",
    ):
        if getattr(args, name) < 0.0:
            parser.error(f"--{name.replace('_', '-')} must be nonnegative")

    rospy.init_node(args.node_name, anonymous=False)
    FastlioMavrosOdometryAdapter(args)
    rospy.spin()


if __name__ == "__main__":
    main()
