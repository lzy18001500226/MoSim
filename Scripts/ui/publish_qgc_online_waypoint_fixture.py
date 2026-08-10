#!/usr/bin/env python3
"""Publish a controlled, read-only ROS1 stream for QGC waypoint-display review."""

from __future__ import annotations

import argparse
import math

import rospy
from geometry_msgs.msg import Point, PoseStamped
from mavros_msgs.msg import State
from nav_msgs.msg import Odometry, Path
from visualization_msgs.msg import Marker


def _point(x: float, y: float, z: float = 1.5) -> Point:
    point = Point()
    point.x = x
    point.y = y
    point.z = z
    return point


def _expected_points() -> list[Point]:
    return [
        _point(-46.0, -18.0),
        _point(-30.0, -4.0),
        _point(-8.0, 6.0),
        _point(18.0, -5.0),
        _point(42.0, 8.0),
    ]


def _future_points(elapsed_s: float) -> list[Point]:
    points: list[Point] = []
    for index in range(25):
        phase = elapsed_s * 0.7 + index * 0.22
        points.append(_point(-4.0 + index * 2.1, -15.0 + 8.0 * math.sin(phase), 1.5))
    return points


def _publish_path(publisher: rospy.Publisher, frame_id: str, stamp: rospy.Time) -> None:
    path = Path()
    path.header.stamp = stamp
    path.header.frame_id = frame_id
    for point in _expected_points():
        pose = PoseStamped()
        pose.header = path.header
        pose.pose.position = point
        pose.pose.orientation.w = 1.0
        path.poses.append(pose)
    publisher.publish(path)


def _publish_future(publisher: rospy.Publisher, frame_id: str, stamp: rospy.Time, elapsed_s: float) -> None:
    marker = Marker()
    marker.header.stamp = stamp
    marker.header.frame_id = frame_id
    marker.ns = "B-Spline"
    marker.id = 1
    marker.type = Marker.LINE_STRIP
    marker.action = Marker.ADD
    marker.scale.x = 0.1
    marker.color.a = 1.0
    marker.color.r = 0.29
    marker.color.g = 0.64
    marker.color.b = 1.0
    marker.points = _future_points(elapsed_s)
    publisher.publish(marker)


def _publish_vehicle(
    state_publisher: rospy.Publisher,
    odom_publisher: rospy.Publisher,
    frame_id: str,
    stamp: rospy.Time,
    elapsed_s: float,
) -> None:
    state = State()
    state.connected = True
    state.armed = False
    state.mode = "FIXTURE_READ_ONLY"
    state_publisher.publish(state)

    odometry = Odometry()
    odometry.header.stamp = stamp
    odometry.header.frame_id = frame_id
    odometry.child_frame_id = frame_id
    odometry.pose.pose.position.x = -38.0 + 9.0 * math.cos(elapsed_s * 0.35)
    odometry.pose.pose.position.y = -12.0 + 5.0 * math.sin(elapsed_s * 0.35)
    odometry.pose.pose.position.z = 1.5
    odometry.pose.pose.orientation.w = 1.0
    odometry.twist.twist.linear.x = -3.15 * math.sin(elapsed_s * 0.35)
    odometry.twist.twist.linear.y = 1.75 * math.cos(elapsed_s * 0.35)
    odom_publisher.publish(odometry)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frame-id", default="mworks_world")
    parser.add_argument("--rate-hz", type=float, default=2.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.rate_hz <= 0.0:
        raise SystemExit("rate must be positive")
    rospy.init_node("mosim_qgc_online_waypoint_fixture", anonymous=False)
    state_publisher = rospy.Publisher("/uav1/mavros/state", State, queue_size=10)
    odom_publisher = rospy.Publisher("/uav1/mavros/local_position/odom", Odometry, queue_size=10)
    expected_publisher = rospy.Publisher("/mosim/qgc_audit/expected_path", Path, queue_size=1, latch=True)
    future_publisher = rospy.Publisher("/mosim/qgc_audit/future_path", Marker, queue_size=10)
    started_at = rospy.get_time()
    rate = rospy.Rate(args.rate_hz)
    while not rospy.is_shutdown():
        stamp = rospy.Time.now()
        elapsed_s = rospy.get_time() - started_at
        _publish_vehicle(state_publisher, odom_publisher, args.frame_id, stamp, elapsed_s)
        _publish_path(expected_publisher, args.frame_id, stamp)
        _publish_future(future_publisher, args.frame_id, stamp, elapsed_s)
        rate.sleep()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
