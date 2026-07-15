#!/usr/bin/env python3
"""Bridge MoSim Goal4 trigger poses into FUEL's trigger Path topic."""

from __future__ import annotations

import json
import time
from pathlib import Path

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Path as RosPath


class FuelTriggerPathAdapter:
    def __init__(self) -> None:
        self.input_topic = rospy.get_param("~input_topic", "/traj_start_trigger")
        self.output_topic = rospy.get_param("~output_topic", "/waypoint_generator/waypoints")
        self.frame_id = rospy.get_param("~frame_id", "world")
        self.min_z = float(rospy.get_param("~min_z", 0.0))
        self.offset_x = float(rospy.get_param("~offset_x", 0.0))
        self.offset_y = float(rospy.get_param("~offset_y", 0.0))
        self.offset_z = float(rospy.get_param("~offset_z", 0.0))
        self.apply_input_offset = bool(rospy.get_param("~apply_input_offset", False))
        self.repeat_count = max(1, int(rospy.get_param("~repeat_count", 3)))
        self.repeat_interval_s = max(0.0, float(rospy.get_param("~repeat_interval_s", 0.10)))
        self.diagnostics_path = rospy.get_param("~diagnostics_path", "")

        self.trigger_count = 0
        self.publish_count = 0
        self.last_trigger: dict | None = None
        self.last_publish_wall: float | None = None

        self.pub = rospy.Publisher(self.output_topic, RosPath, queue_size=3, latch=True)
        rospy.Subscriber(self.input_topic, PoseStamped, self.on_trigger, queue_size=10)

    def on_trigger(self, msg: PoseStamped) -> None:
        self.trigger_count += 1
        path = RosPath()
        path.header.stamp = rospy.Time.now()
        path.header.frame_id = msg.header.frame_id or self.frame_id

        pose = PoseStamped()
        pose.header = path.header
        pose.pose = msg.pose
        input_xyz = [pose.pose.position.x, pose.pose.position.y, pose.pose.position.z]
        if self.apply_input_offset:
            pose.pose.position.x -= self.offset_x
            pose.pose.position.y -= self.offset_y
            pose.pose.position.z -= self.offset_z
        if pose.pose.position.z < self.min_z:
            pose.pose.position.z = self.min_z
        path.poses.append(pose)

        self.last_trigger = {
            "wall_time": time.time(),
            "input_frame": msg.header.frame_id,
            "output_frame": path.header.frame_id,
            "input_xyz": input_xyz,
            "xyz": [pose.pose.position.x, pose.pose.position.y, pose.pose.position.z],
            "repeat_count": self.repeat_count,
        }
        for _ in range(self.repeat_count):
            path.header.stamp = rospy.Time.now()
            path.poses[0].header = path.header
            self.pub.publish(path)
            self.publish_count += 1
            self.last_publish_wall = time.time()
            self.write_diagnostics()
            if self.repeat_interval_s > 0.0:
                rospy.sleep(self.repeat_interval_s)

    def write_diagnostics(self) -> None:
        if not self.diagnostics_path:
            return
        path = Path(self.diagnostics_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema": "mosim.sunray_ros1.fuel_trigger_path_adapter.v1",
            "input_topic": self.input_topic,
            "output_topic": self.output_topic,
            "frame_id": self.frame_id,
            "min_z": self.min_z,
            "apply_input_offset": self.apply_input_offset,
            "offset_xyz": [self.offset_x, self.offset_y, self.offset_z],
            "repeat_count": self.repeat_count,
            "repeat_interval_s": self.repeat_interval_s,
            "trigger_count": self.trigger_count,
            "publish_count": self.publish_count,
            "last_trigger": self.last_trigger,
            "last_publish_wall": self.last_publish_wall,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def spin(self) -> None:
        rate = rospy.Rate(1.0)
        while not rospy.is_shutdown():
            self.write_diagnostics()
            rate.sleep()


def main() -> None:
    rospy.init_node("mosim_fuel_trigger_path_adapter")
    FuelTriggerPathAdapter().spin()


if __name__ == "__main__":
    main()
