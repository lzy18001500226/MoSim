#!/usr/bin/env python3
"""Relay MoSim mission PoseStamped triggers to HighStar Empty triggers."""

from __future__ import annotations

import json
import time
from pathlib import Path

import rospy
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Empty


class HighStarPoseTriggerToEmpty:
    def __init__(self) -> None:
        self.input_topic = rospy.get_param("~input_topic", "/traj_start_trigger")
        self.output_topic = rospy.get_param("~output_topic", "/start_trigger")
        self.repeat_count = int(rospy.get_param("~repeat_count", 10))
        self.repeat_interval_s = float(rospy.get_param("~repeat_interval_s", 0.1))
        self.diagnostics_path = rospy.get_param("~diagnostics_path", "")
        self.received_count = 0
        self.published_count = 0
        self.last_trigger: dict | None = None
        self.pub = rospy.Publisher(self.output_topic, Empty, queue_size=5)
        rospy.Subscriber(self.input_topic, PoseStamped, self.on_trigger, queue_size=5)

    def on_trigger(self, msg: PoseStamped) -> None:
        self.received_count += 1
        p = msg.pose.position
        self.last_trigger = {
            "wall_time": time.time(),
            "frame_id": msg.header.frame_id,
            "x": float(p.x),
            "y": float(p.y),
            "z": float(p.z),
        }
        for _ in range(max(1, self.repeat_count)):
            self.pub.publish(Empty())
            self.published_count += 1
            if self.repeat_interval_s > 0.0:
                rospy.sleep(self.repeat_interval_s)
        self.write_diagnostics()

    def write_diagnostics(self) -> None:
        if not self.diagnostics_path:
            return
        path = Path(self.diagnostics_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "input_topic": self.input_topic,
            "output_topic": self.output_topic,
            "received_count": self.received_count,
            "published_count": self.published_count,
            "last_trigger": self.last_trigger,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def spin(self) -> None:
        rate = rospy.Rate(1.0)
        while not rospy.is_shutdown():
            self.write_diagnostics()
            rate.sleep()


def main() -> None:
    rospy.init_node("mosim_highstar_pose_trigger_to_empty")
    HighStarPoseTriggerToEmpty().spin()


if __name__ == "__main__":
    main()
