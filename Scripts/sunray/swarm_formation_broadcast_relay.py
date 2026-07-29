#!/usr/bin/env python3
"""Relay Swarm-Formation PolyTraj broadcasts on one ROS master.

The polynomial coefficients are relative to ``start_time``. Changing that
timestamp without translating the polynomial changes the planned phase, so the
same-master relay is deliberately transparent and only records delivery
diagnostics. Receiver-side validity is checked against the original trajectory
duration by the planner.
"""

from __future__ import annotations

import json
import math
import os
import time
from pathlib import Path

import rospy
from traj_utils.msg import PolyTraj


class SwarmFormationBroadcastRelay:
    def __init__(self) -> None:
        self.input_topic = rospy.get_param("~input_topic", "/broadcast_traj_from_planner")
        self.output_topic = rospy.get_param("~output_topic", "/broadcast_traj_to_planner")
        self.future_s = float(rospy.get_param("~retime_future_s", 0.0))
        if not math.isfinite(self.future_s) or not math.isclose(self.future_s, 0.0, abs_tol=1.0e-12):
            raise ValueError(
                "~retime_future_s must be exactly zero: PolyTraj coefficients are relative to start_time"
            )
        self.diagnostics_path = Path(rospy.get_param("~diagnostics_path", "/tmp/mosim_swarm_formation_broadcast_relay.json"))
        self.write_period_s = float(rospy.get_param("~write_period_s", 1.0))
        self.count = 0
        self.transparent_count = 0
        self.retime_count = 0
        self.per_drone: dict[str, int] = {}
        self.last_summary: dict = {}
        self.start_wall = time.time()
        self.last_write_wall = 0.0
        self.pub = rospy.Publisher(self.output_topic, PolyTraj, queue_size=100)
        rospy.Subscriber(self.input_topic, PolyTraj, self.on_polytraj, queue_size=100)

    @staticmethod
    def clone(msg: PolyTraj) -> PolyTraj:
        relayed = PolyTraj()
        relayed.drone_id = msg.drone_id
        relayed.traj_id = msg.traj_id
        relayed.start_time = msg.start_time
        relayed.order = msg.order
        relayed.coef_x = list(msg.coef_x)
        relayed.coef_y = list(msg.coef_y)
        relayed.coef_z = list(msg.coef_z)
        relayed.duration = list(msg.duration)
        return relayed

    def on_polytraj(self, msg: PolyTraj) -> None:
        relayed = self.clone(msg)
        original_start = msg.start_time.to_sec()
        self.pub.publish(relayed)

        self.count += 1
        self.transparent_count += 1
        drone_key = str(int(msg.drone_id))
        self.per_drone[drone_key] = self.per_drone.get(drone_key, 0) + 1
        self.last_summary = {
            "drone_id": int(msg.drone_id),
            "traj_id": int(msg.traj_id),
            "order": int(msg.order),
            "duration_count": len(msg.duration),
            "duration_sum_s": float(sum(msg.duration)) if msg.duration else 0.0,
            "original_start_time_s": original_start,
            "forwarded_start_time_s": relayed.start_time.to_sec(),
            "start_time_delta_s": 0.0,
            "relay_wall_elapsed_s": time.time() - self.start_wall,
        }
        self.maybe_write()

    def maybe_write(self) -> None:
        now = time.time()
        if now - self.last_write_wall >= self.write_period_s:
            self.write()
            self.last_write_wall = now

    def write(self) -> None:
        data = {
            "schema": "mosim.sunray_ros1.swarm_formation_broadcast_relay.v1",
            "mode": "transparent_single_ros_master",
            "input_topic": self.input_topic,
            "output_topic": self.output_topic,
            "retime_future_s": self.future_s,
            "count": self.count,
            "transparent_count": self.transparent_count,
            "retime_count": self.retime_count,
            "per_drone": self.per_drone,
            "last_summary": self.last_summary,
            "wall_elapsed_s": time.time() - self.start_wall,
        }
        os.makedirs(self.diagnostics_path.parent, exist_ok=True)
        self.diagnostics_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")

    def spin(self) -> None:
        rate = rospy.Rate(2.0)
        while not rospy.is_shutdown():
            self.maybe_write()
            rate.sleep()
        self.write()


def main() -> None:
    rospy.init_node("mosim_swarm_formation_broadcast_relay", anonymous=False)
    SwarmFormationBroadcastRelay().spin()


if __name__ == "__main__":
    main()
