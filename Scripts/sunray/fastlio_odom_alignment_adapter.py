#!/usr/bin/env python3
"""Align FAST-LIO Livox-body odometry to the PX4/MAVROS UAV-base frame."""

from __future__ import annotations

import argparse
import copy
import math
import time
from pathlib import Path
import sys
from typing import Optional, Tuple

import rospy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry, Path as RosPath
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float64
import tf2_ros

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from fastlio_frame_transform import (  # noqa: E402
    Pose3,
    livox_pose_to_base_pose,
    make_alignment,
    pose_mul,
    quat_from_rpy,
    transform_velocity,
    yaw_from_quat,
)


class FastlioOdomAlignmentAdapter:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.fastlio_odom: Optional[Odometry] = None
        self.local_odom: Optional[Odometry] = None
        self.fastlio_base0: Optional[Pose3] = None
        self.local_base0: Optional[Pose3] = None
        self.truth_odom: Optional[Odometry] = None
        self.truth_base0_z: Optional[float] = None
        self.local_from_fast: Optional[Pose3] = None
        self.last_aligned_pos: Optional[Tuple[float, float, float]] = None
        self.last_aligned_time: Optional[float] = None
        self.last_published_fastlio_key: Optional[Tuple[int, int, int]] = None
        self.aligned_path = RosPath()
        self.aligned_path.header.frame_id = args.output_frame
        self.mount_pose = Pose3(args.mount_xyz, quat_from_rpy(*args.mount_rpy))

        self.pub = rospy.Publisher(args.output_topic, Odometry, queue_size=20)
        self.path_pub = rospy.Publisher(args.path_topic, RosPath, queue_size=1, latch=True)
        self.delay_pub = rospy.Publisher(args.delay_topic, Float64, queue_size=20)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster()

        rospy.Subscriber(args.fastlio_topic, Odometry, self.on_fastlio_odom, queue_size=20)
        rospy.Subscriber(args.local_topic, Odometry, self.on_local_odom, queue_size=20)
        if args.z_source in ("truth", "truth_delta"):
            rospy.Subscriber(args.truth_topic, Odometry, self.on_truth_odom, queue_size=20)

    @staticmethod
    def pose(msg: Odometry) -> Pose3:
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        return Pose3(
            (float(p.x), float(p.y), float(p.z)),
            (float(q.x), float(q.y), float(q.z), float(q.w)),
        )

    @staticmethod
    def pos(msg: Odometry) -> Tuple[float, float, float]:
        return FastlioOdomAlignmentAdapter.pose(msg).p

    @staticmethod
    def set_pose(msg: Odometry, pose: Pose3) -> None:
        msg.pose.pose.position.x = pose.p[0]
        msg.pose.pose.position.y = pose.p[1]
        msg.pose.pose.position.z = pose.p[2]
        msg.pose.pose.orientation.x = pose.q[0]
        msg.pose.pose.orientation.y = pose.q[1]
        msg.pose.pose.orientation.z = pose.q[2]
        msg.pose.pose.orientation.w = pose.q[3]

    @staticmethod
    def vec(msg: Odometry) -> Tuple[float, float, float]:
        v = msg.twist.twist.linear
        return float(v.x), float(v.y), float(v.z)

    def on_fastlio_odom(self, msg: Odometry) -> None:
        self.fastlio_odom = msg
        if self.fastlio_base0 is None:
            self.fastlio_base0 = self.fastlio_base_pose(msg)
            self.try_make_alignment()

    def on_local_odom(self, msg: Odometry) -> None:
        self.local_odom = msg
        if self.local_base0 is None:
            self.local_base0 = self.pose(msg)
            self.try_make_alignment()

    def on_truth_odom(self, msg: Odometry) -> None:
        self.truth_odom = msg
        if self.truth_base0_z is None:
            self.truth_base0_z = float(msg.pose.pose.position.z)

    def try_make_alignment(self) -> None:
        if self.local_from_fast is None and self.local_base0 is not None and self.fastlio_base0 is not None:
            self.local_from_fast = make_alignment(self.local_base0, self.fastlio_base0)

    def ready(self) -> bool:
        return (
            self.fastlio_odom is not None
            and self.local_odom is not None
            and self.fastlio_base0 is not None
            and self.local_base0 is not None
            and self.local_from_fast is not None
            and (
                self.args.z_source not in ("truth", "truth_delta")
                or (self.truth_odom is not None and self.truth_base0_z is not None)
            )
        )

    def fastlio_base_pose(self, msg: Odometry) -> Pose3:
        pose = self.pose(msg)
        if self.args.input_pose_frame == "livox":
            return livox_pose_to_base_pose(pose, self.mount_pose)
        return pose

    def aligned_pose(self, msg: Odometry) -> Pose3:
        if self.local_from_fast is None:
            raise RuntimeError("alignment transform not initialized")
        return pose_mul(self.local_from_fast, self.fastlio_base_pose(msg))

    def fastlio_key(self, msg: Odometry) -> Tuple[int, int, int]:
        return int(msg.header.seq), int(msg.header.stamp.secs), int(msg.header.stamp.nsecs)

    def output_stamp(self, msg: Odometry, now: rospy.Time) -> rospy.Time:
        if self.args.stamp_source == "now":
            return now
        if msg.header.stamp.to_sec() > 0:
            return msg.header.stamp
        rospy.logwarn_throttle(5.0, "FAST-LIO odom stamp is zero; falling back to rospy.Time.now()")
        return now

    def publish_once(self) -> None:
        if not self.ready() or self.fastlio_odom is None:
            return

        now = rospy.Time.now()
        fastlio_key = self.fastlio_key(self.fastlio_odom)
        if not self.args.republish_latest and fastlio_key == self.last_published_fastlio_key:
            return

        out = copy.deepcopy(self.fastlio_odom)
        out.header.stamp = self.output_stamp(self.fastlio_odom, now)
        out.header.frame_id = self.args.output_frame
        out.child_frame_id = self.args.child_frame

        aligned = self.aligned_pose(self.fastlio_odom)
        self.set_pose(out, aligned)
        x, y, z = aligned.p
        if self.args.z_source == "truth":
            z = self.truth_z()
            out.pose.pose.position.z = z
        elif self.args.z_source == "truth_delta":
            z = self.truth_delta_z()
            out.pose.pose.position.z = z

        if self.args.use_fastlio_twist and self.local_from_fast is not None:
            vx, vy, vz = transform_velocity(self.local_from_fast.q, self.vec(self.fastlio_odom))
            out.twist.twist.linear.x = vx
            out.twist.twist.linear.y = vy
            out.twist.twist.linear.z = vz
            if self.args.z_source in ("truth", "truth_delta") and self.truth_odom is not None:
                out.twist.twist.linear.z = float(self.truth_odom.twist.twist.linear.z)

        t = out.header.stamp.to_sec()
        if not self.args.use_fastlio_twist and self.last_aligned_pos is not None and self.last_aligned_time is not None:
            dt = max(1e-3, t - self.last_aligned_time)
            px, py, pz = self.last_aligned_pos
            out.twist.twist.linear.x = (x - px) / dt
            out.twist.twist.linear.y = (y - py) / dt
            out.twist.twist.linear.z = (z - pz) / dt

        self.pub.publish(out)
        self.delay_pub.publish(Float64(data=max(0.0, now.to_sec() - out.header.stamp.to_sec())))
        self.publish_path_point(out)
        self.publish_tf(out)

        self.last_aligned_pos = (x, y, z)
        self.last_aligned_time = t
        self.last_published_fastlio_key = fastlio_key

    def truth_delta_z(self) -> float:
        if self.local_base0 is None or self.truth_odom is None or self.truth_base0_z is None:
            raise RuntimeError("truth_delta z source is not ready")
        truth_z = float(self.truth_odom.pose.pose.position.z)
        return self.local_base0.p[2] + (truth_z - self.truth_base0_z)

    def truth_z(self) -> float:
        if self.truth_odom is None:
            raise RuntimeError("truth z source is not ready")
        return float(self.truth_odom.pose.pose.position.z)

    def publish_path_point(self, msg: Odometry) -> None:
        if self.aligned_path.poses:
            last = self.aligned_path.poses[-1].pose.position
            p = msg.pose.pose.position
            dist = math.sqrt((p.x - last.x) ** 2 + (p.y - last.y) ** 2 + (p.z - last.z) ** 2)
            if dist < self.args.path_min_step_m:
                return
        if len(self.aligned_path.poses) >= self.args.max_path_points:
            self.aligned_path.poses.pop(0)

        pose = PoseStamped()
        pose.header = msg.header
        pose.pose = msg.pose.pose
        self.aligned_path.header.stamp = msg.header.stamp
        self.aligned_path.poses.append(pose)
        self.path_pub.publish(self.aligned_path)

    def publish_tf(self, msg: Odometry) -> None:
        tf = TransformStamped()
        tf.header = msg.header
        tf.child_frame_id = self.args.child_frame
        tf.transform.translation.x = msg.pose.pose.position.x
        tf.transform.translation.y = msg.pose.pose.position.y
        tf.transform.translation.z = msg.pose.pose.position.z
        tf.transform.rotation = msg.pose.pose.orientation
        self.tf_broadcaster.sendTransform(tf)

    def spin(self) -> None:
        deadline = time.time() + self.args.ready_timeout_s
        wait_rate = rospy.Rate(20)
        try:
            while not rospy.is_shutdown() and not self.ready() and time.time() < deadline:
                wait_rate.sleep()
        except rospy.ROSInterruptException:
            return
        if not self.ready():
            rospy.logerr("FAST-LIO alignment adapter did not receive both odom sources before timeout")
            return

        rospy.loginfo(
            "FAST-LIO odom aligned: fastlio_base0=%s local_base0=%s local_from_fast_yaw=%.6f output=%s",
            self.fastlio_base0,
            self.local_base0,
            yaw_from_quat(self.local_from_fast.q) if self.local_from_fast else float("nan"),
            self.args.output_topic,
        )
        rate = rospy.Rate(self.args.publish_rate_hz)
        try:
            while not rospy.is_shutdown():
                self.publish_once()
                rate.sleep()
        except rospy.ROSInterruptException:
            return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fastlio-topic", default="/Odometry")
    parser.add_argument("--local-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--output-topic", default="/mosim/fastlio/odom_aligned")
    parser.add_argument("--path-topic", default="/mosim/fastlio/odom_aligned_path")
    parser.add_argument("--delay-topic", default="/mosim/fastlio/odom_aligned_delay")
    parser.add_argument("--z-source", choices=["fastlio", "truth", "truth_delta"], default="fastlio")
    parser.add_argument("--truth-topic", default="/uav1/sunray/gazebo_pose")
    parser.add_argument("--output-frame", default="world")
    parser.add_argument("--child-frame", default="base_link")
    parser.add_argument(
        "--stamp-source",
        choices=["measurement", "now"],
        default="measurement",
        help="Use FAST-LIO measurement stamps by default; 'now' is only for legacy smoke tests.",
    )
    parser.add_argument(
        "--republish-latest",
        action="store_true",
        help="Republish the latest FAST-LIO frame at publish-rate-hz. Default publishes each measured odom once.",
    )
    parser.add_argument(
        "--input-pose-frame",
        choices=["base", "livox"],
        default="base",
        help="Semantic frame of FAST-LIO /Odometry pose. FAST-LIO publishes camera_init->body, so base is the safe default.",
    )
    parser.add_argument(
        "--mount-xyz",
        type=parse_vec3,
        default=(-0.000005, 0.032295, 0.050167),
        help="Fixed UAV base_link -> MID360/Livox body translation in meters.",
    )
    parser.add_argument(
        "--mount-rpy",
        type=parse_vec3,
        default=(0.0, 0.0, 4.712389),
        help="Fixed UAV base_link -> MID360/Livox body roll,pitch,yaw in radians.",
    )
    parser.add_argument(
        "--use-fastlio-twist",
        action="store_true",
        help="Rotate FAST-LIO twist into the aligned frame instead of differentiating aligned pose.",
    )
    parser.add_argument("--publish-rate-hz", type=float, default=100.0)
    parser.add_argument("--ready-timeout-s", type=float, default=20.0)
    parser.add_argument("--path-min-step-m", type=float, default=0.01)
    parser.add_argument("--max-path-points", type=int, default=20000)
    args = parser.parse_args()

    rospy.init_node("mosim_fastlio_odom_alignment_adapter", anonymous=False)
    FastlioOdomAlignmentAdapter(args).spin()


def parse_vec3(text: str) -> Tuple[float, float, float]:
    parts = [p for p in text.replace(",", " ").split() if p]
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f"expected 3 floats, got {text!r}")
    return float(parts[0]), float(parts[1]), float(parts[2])


if __name__ == "__main__":
    main()
