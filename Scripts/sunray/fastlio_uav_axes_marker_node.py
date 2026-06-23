#!/usr/bin/env python3
"""Publish RViz UAV body axes and path from FAST-LIO odometry."""

from __future__ import annotations

import argparse
import math
from pathlib import Path as FsPath
import sys

import rospy
import tf2_ros
from geometry_msgs.msg import Point, PoseStamped, TransformStamped
from nav_msgs.msg import Odometry, Path
from std_msgs.msg import Header
from visualization_msgs.msg import Marker, MarkerArray

SCRIPT_DIR = FsPath(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from fastlio_frame_transform import Pose3, livox_pose_to_base_pose, quat_from_rpy  # noqa: E402


def quat_rotate(q: tuple[float, float, float, float], v: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z, w = q
    vx, vy, vz = v
    # Rotate vector by q * v * q^-1 without depending on tf.transformations.
    tx = 2.0 * (y * vz - z * vy)
    ty = 2.0 * (z * vx - x * vz)
    tz = 2.0 * (x * vy - y * vx)
    return (
        vx + w * tx + (y * tz - z * ty),
        vy + w * ty + (z * tx - x * tz),
        vz + w * tz + (x * ty - y * tx),
    )


class FastlioUavAxesMarkerNode:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.path = Path(header=Header(frame_id=args.frame_id or "camera_init"))
        self.last_path_point: tuple[float, float, float] | None = None
        self.mount_pose = Pose3(args.mount_xyz, quat_from_rpy(*args.mount_rpy))
        self.marker_pub = rospy.Publisher(args.marker_topic, MarkerArray, queue_size=1)
        self.path_pub = rospy.Publisher(args.path_topic, Path, queue_size=1, latch=True)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster()
        rospy.Subscriber(args.odom_topic, Odometry, self.on_odom, queue_size=20)

    def on_odom(self, msg: Odometry) -> None:
        frame_id = self.args.frame_id or msg.header.frame_id or "camera_init"
        stamp = msg.header.stamp if msg.header.stamp.to_sec() > 0 else rospy.Time.now()
        pos, q = self.body_pose(msg)

        self.publish_tf(stamp, frame_id, pos, q)
        self.append_path(stamp, frame_id, pos, q)
        self.publish_axes(stamp, frame_id, pos, q)

    def body_pose(self, msg: Odometry) -> tuple[tuple[float, float, float], tuple[float, float, float, float]]:
        p = msg.pose.pose.position
        q_msg = msg.pose.pose.orientation
        pose = Pose3(
            (float(p.x), float(p.y), float(p.z)),
            (float(q_msg.x), float(q_msg.y), float(q_msg.z), float(q_msg.w)),
        )
        if self.args.input_pose_frame == "livox":
            pose = livox_pose_to_base_pose(pose, self.mount_pose)
        return pose.p, pose.q

    def publish_tf(self, stamp: rospy.Time, frame_id: str, pos: tuple[float, float, float], q: tuple[float, float, float, float]) -> None:
        transform = TransformStamped()
        transform.header.stamp = stamp
        transform.header.frame_id = frame_id
        transform.child_frame_id = self.args.child_frame_id
        transform.transform.translation.x = pos[0]
        transform.transform.translation.y = pos[1]
        transform.transform.translation.z = pos[2]
        transform.transform.rotation.x = q[0]
        transform.transform.rotation.y = q[1]
        transform.transform.rotation.z = q[2]
        transform.transform.rotation.w = q[3]
        self.tf_broadcaster.sendTransform(transform)

    def append_path(self, stamp: rospy.Time, frame_id: str, pos: tuple[float, float, float], q: tuple[float, float, float, float]) -> None:
        if self.last_path_point is not None:
            d = math.sqrt(sum((pos[i] - self.last_path_point[i]) ** 2 for i in range(3)))
            if d < self.args.min_path_step_m:
                return
        pose = PoseStamped()
        pose.header.stamp = stamp
        pose.header.frame_id = frame_id
        pose.pose.position.x = pos[0]
        pose.pose.position.y = pos[1]
        pose.pose.position.z = pos[2]
        pose.pose.orientation.x = q[0]
        pose.pose.orientation.y = q[1]
        pose.pose.orientation.z = q[2]
        pose.pose.orientation.w = q[3]
        self.path.header.stamp = stamp
        self.path.header.frame_id = frame_id
        self.path.poses.append(pose)
        if self.args.max_path_points > 0 and len(self.path.poses) > self.args.max_path_points:
            self.path.poses = self.path.poses[-self.args.max_path_points :]
        self.last_path_point = pos
        self.path_pub.publish(self.path)

    def publish_axes(self, stamp: rospy.Time, frame_id: str, pos: tuple[float, float, float], q: tuple[float, float, float, float]) -> None:
        axes = (
            (0, "body_x_forward", (1.0, 0.0, 0.0), (1.0, 0.05, 0.05, 1.0)),
            (1, "body_y_left", (0.0, 1.0, 0.0), (0.05, 1.0, 0.05, 1.0)),
            (2, "body_z_up", (0.0, 0.0, 1.0), (0.1, 0.35, 1.0, 1.0)),
        )
        markers = MarkerArray()
        for marker_id, name, axis, color in axes:
            direction = quat_rotate(q, axis)
            end = (
                pos[0] + direction[0] * self.args.axis_length_m,
                pos[1] + direction[1] * self.args.axis_length_m,
                pos[2] + direction[2] * self.args.axis_length_m,
            )
            marker = Marker()
            marker.header.stamp = stamp
            marker.header.frame_id = frame_id
            marker.ns = name
            marker.id = marker_id
            marker.type = Marker.ARROW
            marker.action = Marker.ADD
            start_point = Point()
            start_point.x = pos[0]
            start_point.y = pos[1]
            start_point.z = pos[2]
            end_point = Point()
            end_point.x = end[0]
            end_point.y = end[1]
            end_point.z = end[2]
            marker.points = [start_point, end_point]
            marker.scale.x = self.args.shaft_diameter_m
            marker.scale.y = self.args.head_diameter_m
            marker.scale.z = self.args.head_length_m
            marker.color.r = color[0]
            marker.color.g = color[1]
            marker.color.b = color[2]
            marker.color.a = color[3]
            marker.lifetime = rospy.Duration(self.args.marker_lifetime_s)
            markers.markers.append(marker)
        self.marker_pub.publish(markers)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--odom-topic", default="/Odometry")
    parser.add_argument("--marker-topic", default="/mosim/fastlio/uav_axes")
    parser.add_argument("--path-topic", default="/mosim/fastlio/uav_path")
    parser.add_argument("--frame-id", default="")
    parser.add_argument("--child-frame-id", default="mosim_fastlio_uav_body")
    parser.add_argument("--input-pose-frame", choices=["livox", "base"], default="base")
    parser.add_argument("--mount-xyz", type=parse_vec3, default=(-0.000005, 0.032295, 0.050167))
    parser.add_argument("--mount-rpy", type=parse_vec3, default=(0.0, 0.0, 4.712389))
    parser.add_argument("--axis-length-m", type=float, default=0.018)
    parser.add_argument("--shaft-diameter-m", type=float, default=0.0014)
    parser.add_argument("--head-diameter-m", type=float, default=0.0036)
    parser.add_argument("--head-length-m", type=float, default=0.0048)
    parser.add_argument("--marker-lifetime-s", type=float, default=0.25)
    parser.add_argument("--min-path-step-m", type=float, default=0.01)
    parser.add_argument("--max-path-points", type=int, default=20000)
    return parser.parse_args()


def parse_vec3(text: str) -> tuple[float, float, float]:
    if isinstance(text, tuple):
        return text
    parts = [p for p in text.replace(",", " ").split() if p]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"expected 3 values, got {text!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


def main() -> int:
    rospy.init_node("fastlio_uav_axes_marker_node", anonymous=False)
    FastlioUavAxesMarkerNode(parse_args())
    rospy.spin()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
