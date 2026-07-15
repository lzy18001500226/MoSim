#!/usr/bin/env python3
"""Forward aligned FAST-LIO world-frame velocity to MAVROS vision_speed."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import rospy
from geometry_msgs.msg import TwistWithCovarianceStamped
from nav_msgs.msg import Odometry


class VisionSpeedAdapter:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.output_path = Path(args.diagnostics_json) if args.diagnostics_json else None
        self.publisher = rospy.Publisher(
            args.output_topic,
            TwistWithCovarianceStamped,
            queue_size=20,
        )
        self.received = 0
        self.published = 0
        self.dropped_nonfinite = 0
        self.dropped_stale = 0
        self.dropped_frame = 0
        self.dropped_duplicate = 0
        self.out_of_order = 0
        self.last_stamp_ns: int | None = None
        self.last_velocity: list[float] | None = None
        self.age_samples: list[float] = []
        self.max_speed_mps = 0.0
        rospy.Subscriber(args.input_topic, Odometry, self.on_odom, queue_size=20)
        rospy.on_shutdown(self.write_diagnostics)

    @staticmethod
    def finite_velocity(msg: Odometry) -> tuple[float, float, float] | None:
        linear = msg.twist.twist.linear
        velocity = (float(linear.x), float(linear.y), float(linear.z))
        return velocity if all(math.isfinite(value) for value in velocity) else None

    @staticmethod
    def stamp_ns(msg: Odometry) -> int:
        return int(msg.header.stamp.secs) * 1_000_000_000 + int(msg.header.stamp.nsecs)

    def on_odom(self, msg: Odometry) -> None:
        self.received += 1
        stamp_ns = self.stamp_ns(msg)
        if stamp_ns <= 0:
            self.dropped_stale += 1
            rospy.logwarn_throttle(5.0, "Aligned FAST-LIO odom has a zero timestamp")
            return
        if self.last_stamp_ns is not None:
            if stamp_ns == self.last_stamp_ns:
                self.dropped_duplicate += 1
                return
            if stamp_ns < self.last_stamp_ns:
                self.out_of_order += 1
                rospy.logwarn_throttle(5.0, "Aligned FAST-LIO odom timestamp moved backwards")
                return
        if self.args.expected_frame and msg.header.frame_id != self.args.expected_frame:
            self.dropped_frame += 1
            rospy.logerr_throttle(
                5.0,
                "Refusing FAST-LIO velocity frame %s; expected local ENU frame %s",
                msg.header.frame_id,
                self.args.expected_frame,
            )
            return

        velocity = self.finite_velocity(msg)
        if velocity is None:
            self.dropped_nonfinite += 1
            return
        now = rospy.Time.now()
        age_s = now.to_sec() - msg.header.stamp.to_sec()
        if age_s > self.args.max_age_s:
            self.dropped_stale += 1
            rospy.logwarn_throttle(
                5.0,
                "Dropping stale FAST-LIO velocity: age=%.3f s limit=%.3f s",
                age_s,
                self.args.max_age_s,
            )
            return

        output = TwistWithCovarianceStamped()
        output.header = msg.header
        output.twist.twist.linear.x = velocity[0]
        output.twist.twist.linear.y = velocity[1]
        output.twist.twist.linear.z = velocity[2]
        variance = self.args.velocity_stddev_mps * self.args.velocity_stddev_mps
        output.twist.covariance = [0.0] * 36
        output.twist.covariance[0] = variance
        output.twist.covariance[7] = variance
        output.twist.covariance[14] = variance
        self.publisher.publish(output)

        self.last_stamp_ns = stamp_ns
        self.last_velocity = list(velocity)
        self.age_samples.append(age_s)
        self.max_speed_mps = max(self.max_speed_mps, math.sqrt(sum(v * v for v in velocity)))
        self.published += 1

    @staticmethod
    def percentile(values: list[float], fraction: float) -> float | None:
        if not values:
            return None
        ordered = sorted(values)
        index = min(len(ordered) - 1, max(0, math.ceil(fraction * len(ordered)) - 1))
        return ordered[index]

    def diagnostics(self) -> dict[str, Any]:
        return {
            "schema": "mosim.fastlio_mavros_vision_speed.v1",
            "input_topic": self.args.input_topic,
            "output_topic": self.args.output_topic,
            "input_semantics": "world/local ENU linear velocity",
            "mavros_semantics": "vision_speed converts local ENU to FCU local NED",
            "timestamp_policy": "preserve aligned FAST-LIO measurement timestamp",
            "expected_frame": self.args.expected_frame,
            "velocity_stddev_mps": self.args.velocity_stddev_mps,
            "max_age_s": self.args.max_age_s,
            "received": self.received,
            "published": self.published,
            "dropped_nonfinite": self.dropped_nonfinite,
            "dropped_stale": self.dropped_stale,
            "dropped_frame": self.dropped_frame,
            "dropped_duplicate": self.dropped_duplicate,
            "out_of_order": self.out_of_order,
            "age_s": {
                "mean": sum(self.age_samples) / len(self.age_samples) if self.age_samples else None,
                "p95": self.percentile(self.age_samples, 0.95),
                "max": max(self.age_samples) if self.age_samples else None,
            },
            "max_speed_mps": self.max_speed_mps if self.published else None,
            "last_velocity_enu_mps": self.last_velocity,
        }

    def write_diagnostics(self) -> None:
        data = self.diagnostics()
        if self.output_path is not None:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        rospy.loginfo("FAST-LIO vision-speed adapter summary: %s", json.dumps(data, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node-name", default="mosim_fastlio_vision_speed_adapter")
    parser.add_argument("--input-topic", default="/mosim/fastlio/odom_aligned")
    parser.add_argument("--output-topic", default="/uav1/mavros/vision_speed/speed_twist_cov")
    parser.add_argument("--expected-frame", default="world")
    parser.add_argument("--velocity-stddev-mps", type=float, default=0.20)
    parser.add_argument("--max-age-s", type=float, default=0.25)
    parser.add_argument("--diagnostics-json", default="")
    args = parser.parse_args()
    if args.velocity_stddev_mps <= 0:
        raise SystemExit("velocity-stddev-mps must be positive")
    if args.max_age_s <= 0:
        raise SystemExit("max-age-s must be positive")

    rospy.init_node(args.node_name, anonymous=False)
    VisionSpeedAdapter(args)
    rospy.spin()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
