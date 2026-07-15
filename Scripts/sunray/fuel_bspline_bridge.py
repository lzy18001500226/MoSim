#!/usr/bin/env python3
"""Bridge FUEL bspline/Bspline messages into the local traj_utils/Bspline type."""

from __future__ import annotations

import json
import time
from pathlib import Path

import rospy
from bspline.msg import Bspline as FuelBspline
from traj_utils.msg import Bspline as TrajUtilsBspline


class FuelBsplineBridge:
    def __init__(self) -> None:
        self.input_topic = rospy.get_param("~input_topic", "/planning/bspline")
        self.output_topic = rospy.get_param("~output_topic", "/mosim/fuel/planning/bspline_traj_utils")
        self.diagnostics_path = rospy.get_param("~diagnostics_path", "")
        self.honor_start_time = bool(rospy.get_param("~honor_start_time", True))

        self.input_count = 0
        self.output_count = 0
        self.delayed_count = 0
        self.pending: FuelBspline | None = None
        self.last_msg: dict | None = None
        self.pub = rospy.Publisher(self.output_topic, TrajUtilsBspline, queue_size=10, latch=True)
        rospy.Subscriber(self.input_topic, FuelBspline, self.on_msg, queue_size=10)
        rospy.Timer(rospy.Duration(0.002), self.on_timer)

    def on_msg(self, msg: FuelBspline) -> None:
        self.input_count += 1
        if self.honor_start_time and msg.start_time > rospy.Time.now():
            self.pending = msg
            self.delayed_count += 1
            return
        self.publish(msg)

    def on_timer(self, _event: rospy.timer.TimerEvent) -> None:
        if self.pending is None or rospy.Time.now() < self.pending.start_time:
            return
        msg = self.pending
        self.pending = None
        self.publish(msg)

    def publish(self, msg: FuelBspline) -> None:
        out = TrajUtilsBspline()
        out.order = msg.order
        out.traj_id = msg.traj_id
        out.start_time = msg.start_time
        out.knots = list(msg.knots)
        out.pos_pts = list(msg.pos_pts)
        out.yaw_pts = list(msg.yaw_pts)
        out.yaw_dt = msg.yaw_dt
        self.pub.publish(out)
        self.output_count += 1
        self.last_msg = {
            "wall_time": time.time(),
            "traj_id": int(msg.traj_id),
            "order": int(msg.order),
            "knots": len(msg.knots),
            "pos_pts": len(msg.pos_pts),
            "yaw_pts": len(msg.yaw_pts),
        }
        self.write_diagnostics()

    def write_diagnostics(self) -> None:
        if not self.diagnostics_path:
            return
        path = Path(self.diagnostics_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema": "mosim.sunray_ros1.fuel_bspline_bridge.v1",
            "input_topic": self.input_topic,
            "output_topic": self.output_topic,
            "honor_start_time": self.honor_start_time,
            "input_count": self.input_count,
            "output_count": self.output_count,
            "delayed_count": self.delayed_count,
            "pending": self.pending is not None,
            "last_msg": self.last_msg,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def spin(self) -> None:
        rate = rospy.Rate(1.0)
        while not rospy.is_shutdown():
            self.write_diagnostics()
            rate.sleep()


def main() -> None:
    rospy.init_node("mosim_fuel_bspline_bridge")
    FuelBsplineBridge().spin()


if __name__ == "__main__":
    main()
