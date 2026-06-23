#!/usr/bin/env python3
"""Safety/hold adapter for planner PositionCommand streams.

This node is intentionally narrow: it keeps the planner output observable on a
raw topic, then publishes the px4ctrl-facing command with a bounded altitude
envelope and a continuous final hold. It is used for Diff-Planner integration,
whose traj_server stops publishing at trajectory end and can produce low-Z
transients in the current Sunray150 pillar map.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import rospy
from quadrotor_msgs.msg import PositionCommand
from std_msgs.msg import Bool


class PositionCmdSafetyAdapter:
    def __init__(self) -> None:
        self.input_topic = rospy.get_param("~input_topic", "/diff_planner/position_cmd_raw")
        self.output_topic = rospy.get_param("~output_topic", "/position_cmd")
        self.rate_hz = float(rospy.get_param("~rate_hz", 100.0))
        self.min_z = float(rospy.get_param("~min_z", 0.85))
        self.max_z = float(rospy.get_param("~max_z", 1.35))
        self.input_timeout_s = float(rospy.get_param("~input_timeout_s", 0.30))
        self.enable_topic = rospy.get_param("~enable_topic", "/mosim/goal4/position_cmd_adapter_enable")
        self.enabled = bool(rospy.get_param("~initial_enabled", True))
        self.diagnostics_path = rospy.get_param("~diagnostics_path", "")

        self.last_raw: PositionCommand | None = None
        self.last_raw_wall = 0.0
        self.last_publish_wall = 0.0
        self.raw_count = 0
        self.published_count = 0
        self.clamped_low_count = 0
        self.clamped_high_count = 0
        self.hold_publish_count = 0
        self.first_raw_wall: float | None = None
        self.last_raw_z: float | None = None
        self.min_raw_z: float | None = None
        self.min_published_z: float | None = None
        self.max_published_z: float | None = None
        self.enable_update_count = 0
        self.disabled_publish_skip_count = 0
        self.last_enable_wall: float | None = None

        self.pub = rospy.Publisher(self.output_topic, PositionCommand, queue_size=20)
        rospy.Subscriber(self.input_topic, PositionCommand, self.on_raw, queue_size=50)
        rospy.Subscriber(self.enable_topic, Bool, self.on_enable, queue_size=5)

    def on_raw(self, msg: PositionCommand) -> None:
        self.raw_count += 1
        now = time.time()
        if self.first_raw_wall is None:
            self.first_raw_wall = now
        self.last_raw_wall = now
        self.last_raw = msg
        self.last_raw_z = float(msg.position.z)
        self.min_raw_z = self.last_raw_z if self.min_raw_z is None else min(self.min_raw_z, self.last_raw_z)

    def on_enable(self, msg: Bool) -> None:
        self.enabled = bool(msg.data)
        self.enable_update_count += 1
        self.last_enable_wall = time.time()
        self.write_diagnostics()

    def adapted_msg(self, now_wall: float) -> PositionCommand | None:
        if self.last_raw is None:
            return None

        msg = PositionCommand()
        msg.header = self.last_raw.header
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.last_raw.header.frame_id or "world"
        msg.trajectory_flag = self.last_raw.trajectory_flag
        msg.trajectory_id = self.last_raw.trajectory_id
        msg.position.x = self.last_raw.position.x
        msg.position.y = self.last_raw.position.y
        msg.position.z = self.last_raw.position.z
        msg.velocity.x = self.last_raw.velocity.x
        msg.velocity.y = self.last_raw.velocity.y
        msg.velocity.z = self.last_raw.velocity.z
        msg.acceleration.x = self.last_raw.acceleration.x
        msg.acceleration.y = self.last_raw.acceleration.y
        msg.acceleration.z = self.last_raw.acceleration.z
        msg.jerk.x = self.last_raw.jerk.x
        msg.jerk.y = self.last_raw.jerk.y
        msg.jerk.z = self.last_raw.jerk.z
        msg.yaw = self.last_raw.yaw
        msg.yaw_dot = self.last_raw.yaw_dot
        msg.kx = list(self.last_raw.kx)
        msg.kv = list(self.last_raw.kv)

        stale = now_wall - self.last_raw_wall > self.input_timeout_s
        if stale:
            msg.velocity.x = 0.0
            msg.velocity.y = 0.0
            msg.velocity.z = 0.0
            msg.acceleration.x = 0.0
            msg.acceleration.y = 0.0
            msg.acceleration.z = 0.0
            msg.jerk.x = 0.0
            msg.jerk.y = 0.0
            msg.jerk.z = 0.0
            msg.yaw_dot = 0.0
            self.hold_publish_count += 1

        if msg.position.z < self.min_z:
            msg.position.z = self.min_z
            msg.velocity.z = max(0.0, msg.velocity.z)
            msg.acceleration.z = max(0.0, msg.acceleration.z)
            self.clamped_low_count += 1
        elif msg.position.z > self.max_z:
            msg.position.z = self.max_z
            msg.velocity.z = min(0.0, msg.velocity.z)
            msg.acceleration.z = min(0.0, msg.acceleration.z)
            self.clamped_high_count += 1

        self.min_published_z = msg.position.z if self.min_published_z is None else min(self.min_published_z, msg.position.z)
        self.max_published_z = msg.position.z if self.max_published_z is None else max(self.max_published_z, msg.position.z)
        return msg

    def write_diagnostics(self) -> None:
        if not self.diagnostics_path:
            return
        path = Path(self.diagnostics_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema": "mosim.sunray_ros1.position_cmd_safety_adapter.v1",
            "input_topic": self.input_topic,
            "output_topic": self.output_topic,
            "enable_topic": self.enable_topic,
            "enabled": self.enabled,
            "rate_hz": self.rate_hz,
            "min_z": self.min_z,
            "max_z": self.max_z,
            "input_timeout_s": self.input_timeout_s,
            "raw_count": self.raw_count,
            "published_count": self.published_count,
            "clamped_low_count": self.clamped_low_count,
            "clamped_high_count": self.clamped_high_count,
            "hold_publish_count": self.hold_publish_count,
            "enable_update_count": self.enable_update_count,
            "disabled_publish_skip_count": self.disabled_publish_skip_count,
            "last_enable_wall": self.last_enable_wall,
            "first_raw_wall": self.first_raw_wall,
            "last_raw_z": self.last_raw_z,
            "min_raw_z": self.min_raw_z,
            "min_published_z": self.min_published_z,
            "max_published_z": self.max_published_z,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def spin(self) -> None:
        rate = rospy.Rate(self.rate_hz)
        while not rospy.is_shutdown():
            now = time.time()
            if self.enabled:
                msg = self.adapted_msg(now)
                if msg is not None:
                    self.pub.publish(msg)
                    self.published_count += 1
            else:
                self.disabled_publish_skip_count += 1
            if self.diagnostics_path and now - self.last_publish_wall > 1.0:
                self.write_diagnostics()
                self.last_publish_wall = now
            rate.sleep()
        self.write_diagnostics()


def main() -> None:
    rospy.init_node("mosim_goal4_position_cmd_safety_adapter")
    PositionCmdSafetyAdapter().spin()


if __name__ == "__main__":
    main()
