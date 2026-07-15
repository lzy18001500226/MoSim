#!/usr/bin/env python3
"""Publish RViz-only body axes for the Goal5 multi-UAV review."""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import rospy
from geometry_msgs.msg import Point
from nav_msgs.msg import Odometry
from visualization_msgs.msg import Marker, MarkerArray


@dataclass
class UavState:
    odom: Optional[Odometry] = None


Vector3 = Tuple[float, float, float]
Quaternion = Tuple[float, float, float, float]
Rgba = Tuple[float, float, float, float]


def quat_rotate(q: Quaternion, v: Vector3) -> Vector3:
    x, y, z, w = q
    vx, vy, vz = v
    tx = 2.0 * (y * vz - z * vy)
    ty = 2.0 * (z * vx - x * vz)
    tz = 2.0 * (x * vy - y * vx)
    return (
        vx + w * tx + (y * tz - z * ty),
        vy + w * ty + (z * tx - x * tz),
        vz + w * tz + (x * ty - y * tx),
    )


class SwarmBodyAxesPublisher:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.states: Dict[int, UavState] = {uid: UavState() for uid in range(1, args.uav_num + 1)}
        self.pub = rospy.Publisher(args.marker_topic, MarkerArray, queue_size=1)
        self.subs = [
            rospy.Subscriber(
                f"/uav{uid}/mavros/local_position/odom",
                Odometry,
                lambda msg, uid=uid: self.on_odom(uid, msg),
                queue_size=1,
            )
            for uid in self.states
        ]

    def on_odom(self, uid: int, msg: Odometry) -> None:
        self.states[uid].odom = msg

    def marker(
        self,
        uid: int,
        marker_id: int,
        stamp: rospy.Time,
        start: Point,
        direction: Vector3,
        color: Rgba,
        name: str,
    ) -> Marker:
        marker = Marker()
        marker.header.stamp = stamp
        marker.header.frame_id = self.args.frame_id
        marker.ns = f"uav{uid}_{name}"
        marker.id = marker_id
        marker.type = Marker.ARROW
        marker.action = Marker.ADD
        marker.points = [
            start,
            Point(
                x=start.x + direction[0] * self.args.axis_length_m,
                y=start.y + direction[1] * self.args.axis_length_m,
                z=start.z + direction[2] * self.args.axis_length_m,
            ),
        ]
        marker.scale.x = self.args.shaft_m
        marker.scale.y = self.args.head_diameter_m
        marker.scale.z = self.args.head_length_m
        marker.color.r, marker.color.g, marker.color.b, marker.color.a = color
        marker.lifetime = rospy.Duration(self.args.lifetime_s)
        return marker

    def publish(self) -> None:
        stamp = rospy.Time.now()
        out = MarkerArray()
        axes = (
            ("body_x_forward", (1.0, 0.0, 0.0), (1.0, 0.05, 0.05, 1.0)),
            ("body_y_left", (0.0, 1.0, 0.0), (0.05, 1.0, 0.05, 1.0)),
            ("body_z_up", (0.0, 0.0, 1.0), (0.1, 0.35, 1.0, 1.0)),
        )
        for uid, state in self.states.items():
            if state.odom is None:
                continue
            pose = state.odom.pose.pose
            q = pose.orientation
            quat = (q.x, q.y, q.z, q.w)
            norm = math.sqrt(sum(component * component for component in quat))
            if norm < 1e-6:
                quat = (0.0, 0.0, 0.0, 1.0)
            else:
                quat = tuple(component / norm for component in quat)
            start = Point(x=pose.position.x, y=pose.position.y, z=pose.position.z)
            for axis_index, (name, axis, color) in enumerate(axes):
                out.markers.append(
                    self.marker(
                        uid=uid,
                        marker_id=uid * 10 + axis_index,
                        stamp=stamp,
                        start=start,
                        direction=quat_rotate(quat, axis),
                        color=color,
                        name=name,
                    )
                )
        self.pub.publish(out)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--uav-num", type=int, choices=[2, 3], default=3)
    parser.add_argument("--marker-topic", default="/mosim/goal5/body_axes")
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--rate-hz", type=float, default=20.0)
    parser.add_argument("--axis-length-m", type=float, default=0.20)
    parser.add_argument("--shaft-m", type=float, default=0.015)
    parser.add_argument("--head-diameter-m", type=float, default=0.045)
    parser.add_argument("--head-length-m", type=float, default=0.060)
    parser.add_argument("--lifetime-s", type=float, default=0.25)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rospy.init_node("mosim_goal5_swarm_body_axes_marker", anonymous=False)
    publisher = SwarmBodyAxesPublisher(args)
    rate = rospy.Rate(args.rate_hz)
    while not rospy.is_shutdown():
        publisher.publish()
        rate.sleep()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
