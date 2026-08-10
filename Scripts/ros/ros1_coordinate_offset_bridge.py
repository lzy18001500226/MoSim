#!/usr/bin/env python3
"""Translate ROS1 pose, odom, cloud, and visualization messages by XYZ offset."""

from __future__ import annotations

import copy
import json
import math
import time
from pathlib import Path
from typing import Any

import rospy
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2
from visualization_msgs.msg import Marker, MarkerArray

try:
    from quadrotor_msgs.msg import PositionCommand
except ImportError:  # pragma: no cover - only relevant outside a planner ROS overlay.
    PositionCommand = None


class CoordinateOffsetBridge:
    def __init__(self) -> None:
        self.input_topic = rospy.get_param("~input_topic")
        self.output_topic = rospy.get_param("~output_topic")
        self.message_type = rospy.get_param("~message_type", "cloud")
        self.direction = rospy.get_param("~direction", "world_to_local")
        self.offset_x = float(rospy.get_param("~offset_x", 0.0))
        self.offset_y = float(rospy.get_param("~offset_y", 0.0))
        self.offset_z = float(rospy.get_param("~offset_z", 0.0))
        self.output_frame_id = rospy.get_param("~output_frame_id", "")
        self.output_child_frame_id = rospy.get_param("~output_child_frame_id", "")
        self.latch_input_origin = bool(rospy.get_param("~latch_input_origin", False))
        self.origin_latch_samples = max(1, int(rospy.get_param("~origin_latch_samples", 1)))
        self.target_origin = (
            float(rospy.get_param("~target_origin_x", 0.0)),
            float(rospy.get_param("~target_origin_y", 0.0)),
            float(rospy.get_param("~target_origin_z", 0.0)),
        )
        self.origin_sum = [0.0, 0.0, 0.0]
        self.origin_sample_count = 0
        self.latched_input_origin: tuple[float, float, float] | None = None
        self.rotate_odom_twist_body_to_world = bool(
            rospy.get_param("~rotate_odom_twist_body_to_world", False)
        )
        self.diagnostics_path = rospy.get_param("~diagnostics_path", "")

        if self.direction == "world_to_local":
            self.sign = -1.0
        elif self.direction == "local_to_world":
            self.sign = 1.0
        else:
            raise ValueError("~direction must be world_to_local or local_to_world")

        self.count = 0
        self.last_msg: dict[str, Any] | None = None

        if self.message_type == "pose":
            self.pub = rospy.Publisher(self.output_topic, PoseStamped, queue_size=50)
            rospy.Subscriber(self.input_topic, PoseStamped, self.on_pose, queue_size=50)
        elif self.message_type == "odom":
            self.pub = rospy.Publisher(self.output_topic, Odometry, queue_size=50)
            rospy.Subscriber(self.input_topic, Odometry, self.on_odom, queue_size=50)
        elif self.message_type == "cloud":
            self.pub = rospy.Publisher(self.output_topic, PointCloud2, queue_size=10)
            rospy.Subscriber(self.input_topic, PointCloud2, self.on_cloud, queue_size=10)
        elif self.message_type == "position_cmd":
            if PositionCommand is None:
                raise ImportError("quadrotor_msgs.msg.PositionCommand is required for position_cmd mode")
            self.pub = rospy.Publisher(self.output_topic, PositionCommand, queue_size=50)
            rospy.Subscriber(self.input_topic, PositionCommand, self.on_position_cmd, queue_size=50)
        elif self.message_type == "marker":
            self.pub = rospy.Publisher(self.output_topic, Marker, queue_size=100)
            rospy.Subscriber(self.input_topic, Marker, self.on_marker, queue_size=100)
        elif self.message_type == "marker_array":
            self.pub = rospy.Publisher(self.output_topic, MarkerArray, queue_size=20)
            rospy.Subscriber(self.input_topic, MarkerArray, self.on_marker_array, queue_size=20)
        else:
            raise ValueError("~message_type must be pose, odom, cloud, position_cmd, marker, or marker_array")
        if self.latch_input_origin and self.message_type not in ("pose", "odom"):
            raise ValueError("~latch_input_origin is supported only for pose or odom messages")

    def observe_origin(self, x: float, y: float, z: float) -> bool:
        if not self.latch_input_origin or self.latched_input_origin is not None:
            return True
        self.origin_sum[0] += x
        self.origin_sum[1] += y
        self.origin_sum[2] += z
        self.origin_sample_count += 1
        if self.origin_sample_count < self.origin_latch_samples:
            return False
        self.latched_input_origin = tuple(
            value / self.origin_sample_count for value in self.origin_sum
        )
        rospy.loginfo(
            "Latched input origin %s from %d samples; target origin %s",
            self.latched_input_origin,
            self.origin_sample_count,
            self.target_origin,
        )
        return True

    def shifted(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        if self.latch_input_origin:
            if self.latched_input_origin is None:
                raise RuntimeError("input origin has not been latched")
            return (
                x - self.latched_input_origin[0] + self.target_origin[0],
                y - self.latched_input_origin[1] + self.target_origin[1],
                z - self.latched_input_origin[2] + self.target_origin[2],
            )
        return (
            x + self.sign * self.offset_x,
            y + self.sign * self.offset_y,
            z + self.sign * self.offset_z,
        )

    def update_header(self, msg: Any) -> None:
        if self.output_frame_id:
            msg.header.frame_id = self.output_frame_id

    @staticmethod
    def rotate_vector_by_quaternion(
        x: float, y: float, z: float, qx: float, qy: float, qz: float, qw: float
    ) -> tuple[float, float, float]:
        norm = math.sqrt(qx * qx + qy * qy + qz * qz + qw * qw)
        if norm < 1e-9:
            raise ValueError("cannot rotate odometry twist with a zero quaternion")
        qx, qy, qz, qw = qx / norm, qy / norm, qz / norm, qw / norm
        # R(q) maps a vector from the odometry child/body frame to its parent/world frame.
        return (
            (1.0 - 2.0 * (qy * qy + qz * qz)) * x
            + 2.0 * (qx * qy - qz * qw) * y
            + 2.0 * (qx * qz + qy * qw) * z,
            2.0 * (qx * qy + qz * qw) * x
            + (1.0 - 2.0 * (qx * qx + qz * qz)) * y
            + 2.0 * (qy * qz - qx * qw) * z,
            2.0 * (qx * qz - qy * qw) * x
            + 2.0 * (qy * qz + qx * qw) * y
            + (1.0 - 2.0 * (qx * qx + qy * qy)) * z,
        )

    def header_diag(self, in_msg: Any, out_msg: Any) -> dict[str, Any]:
        def stamp_to_dict(stamp: Any) -> dict[str, Any]:
            sec = int(getattr(stamp, "secs", 0))
            nsec = int(getattr(stamp, "nsecs", 0))
            return {
                "secs": sec,
                "nsecs": nsec,
                "float": float(sec) + float(nsec) * 1e-9,
            }

        in_header = getattr(in_msg, "header", None)
        out_header = getattr(out_msg, "header", None)
        return {
            "input_frame_id": getattr(in_header, "frame_id", "") if in_header else "",
            "output_frame_id": getattr(out_header, "frame_id", "") if out_header else "",
            "input_stamp": stamp_to_dict(in_header.stamp) if in_header else None,
            "output_stamp": stamp_to_dict(out_header.stamp) if out_header else None,
        }

    def on_pose(self, msg: PoseStamped) -> None:
        if not self.observe_origin(msg.pose.position.x, msg.pose.position.y, msg.pose.position.z):
            return
        out = copy.deepcopy(msg)
        out.pose.position.x, out.pose.position.y, out.pose.position.z = self.shifted(
            msg.pose.position.x, msg.pose.position.y, msg.pose.position.z
        )
        self.update_header(out)
        self.pub.publish(out)
        self.note([out.pose.position.x, out.pose.position.y, out.pose.position.z], None, self.header_diag(msg, out))

    def on_odom(self, msg: Odometry) -> None:
        if not self.observe_origin(
            msg.pose.pose.position.x, msg.pose.pose.position.y, msg.pose.pose.position.z
        ):
            return
        out = copy.deepcopy(msg)
        out.pose.pose.position.x, out.pose.pose.position.y, out.pose.pose.position.z = self.shifted(
            msg.pose.pose.position.x, msg.pose.pose.position.y, msg.pose.pose.position.z
        )
        if self.rotate_odom_twist_body_to_world:
            q = msg.pose.pose.orientation
            linear = out.twist.twist.linear
            linear.x, linear.y, linear.z = self.rotate_vector_by_quaternion(
                linear.x, linear.y, linear.z, q.x, q.y, q.z, q.w
            )
            angular = out.twist.twist.angular
            angular.x, angular.y, angular.z = self.rotate_vector_by_quaternion(
                angular.x, angular.y, angular.z, q.x, q.y, q.z, q.w
            )
        if self.output_child_frame_id:
            out.child_frame_id = self.output_child_frame_id
        self.update_header(out)
        self.pub.publish(out)
        self.note(
            [out.pose.pose.position.x, out.pose.pose.position.y, out.pose.pose.position.z],
            None,
            self.header_diag(msg, out),
        )

    def on_cloud(self, msg: PointCloud2) -> None:
        field_names = [field.name for field in msg.fields]
        try:
            ix = field_names.index("x")
            iy = field_names.index("y")
            iz = field_names.index("z")
        except ValueError:
            rospy.logwarn_throttle(2.0, "PointCloud2 has no x/y/z fields: %s", self.input_topic)
            return

        points = []
        count = 0
        sample = None
        for point in point_cloud2.read_points(msg, field_names=field_names, skip_nans=False):
            values = list(point)
            values[ix], values[iy], values[iz] = self.shifted(
                float(values[ix]), float(values[iy]), float(values[iz])
            )
            if sample is None:
                sample = [values[ix], values[iy], values[iz]]
            points.append(values)
            count += 1

        header = copy.deepcopy(msg.header)
        if self.output_frame_id:
            header.frame_id = self.output_frame_id
        out = point_cloud2.create_cloud(header, msg.fields, points)
        out.is_dense = msg.is_dense
        self.pub.publish(out)
        self.note(sample, count, self.header_diag(msg, out))

    def on_position_cmd(self, msg: PositionCommand) -> None:
        out = copy.deepcopy(msg)
        out.position.x, out.position.y, out.position.z = self.shifted(
            msg.position.x, msg.position.y, msg.position.z
        )
        self.update_header(out)
        self.pub.publish(out)
        self.note(
            [out.position.x, out.position.y, out.position.z],
            None,
            self.header_diag(msg, out),
        )

    def shift_marker_pose(self, marker: Marker) -> None:
        marker.pose.position.x, marker.pose.position.y, marker.pose.position.z = self.shifted(
            marker.pose.position.x, marker.pose.position.y, marker.pose.position.z
        )
        self.update_header(marker)

    def on_marker(self, msg: Marker) -> None:
        out = copy.deepcopy(msg)
        self.shift_marker_pose(out)
        self.pub.publish(out)
        self.note(
            [out.pose.position.x, out.pose.position.y, out.pose.position.z],
            len(out.points),
            self.header_diag(msg, out),
        )

    def on_marker_array(self, msg: MarkerArray) -> None:
        out = copy.deepcopy(msg)
        for marker in out.markers:
            self.shift_marker_pose(marker)
        self.pub.publish(out)
        sample = None
        header = None
        if out.markers:
            marker = out.markers[0]
            sample = [marker.pose.position.x, marker.pose.position.y, marker.pose.position.z]
            header = self.header_diag(msg.markers[0], marker)
        self.note(sample, len(out.markers), header)

    def note(
        self,
        sample_xyz: list[float] | None,
        point_count: int | None,
        header: dict[str, Any] | None,
    ) -> None:
        self.count += 1
        self.last_msg = {
            "wall_time": time.time(),
            "sample_xyz": sample_xyz,
            "point_count": point_count,
            "header": header,
        }
        self.write_diagnostics()

    def write_diagnostics(self) -> None:
        if not self.diagnostics_path:
            return
        path = Path(self.diagnostics_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema": "mosim.ros1_coordinate_offset_bridge.v1",
            "input_topic": self.input_topic,
            "output_topic": self.output_topic,
            "message_type": self.message_type,
            "direction": self.direction,
            "offset_xyz": [self.offset_x, self.offset_y, self.offset_z],
            "output_frame_id": self.output_frame_id,
            "output_child_frame_id": self.output_child_frame_id,
            "latch_input_origin": self.latch_input_origin,
            "origin_latch_samples": self.origin_latch_samples,
            "origin_sample_count": self.origin_sample_count,
            "latched_input_origin_xyz": self.latched_input_origin,
            "target_origin_xyz": self.target_origin,
            "rotate_odom_twist_body_to_world": self.rotate_odom_twist_body_to_world,
            "count": self.count,
            "last_msg": self.last_msg,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def spin(self) -> None:
        rate = rospy.Rate(1.0)
        while not rospy.is_shutdown():
            self.write_diagnostics()
            rate.sleep()


def main() -> None:
    rospy.init_node("mosim_coordinate_offset_bridge", anonymous=True)
    CoordinateOffsetBridge().spin()


if __name__ == "__main__":
    main()
