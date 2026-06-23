#!/usr/bin/env python3
"""Run and record Sunray ROS1/PX4/Gazebo missions with native Sunray commands."""

from __future__ import annotations

import argparse
import csv
import json
import math
import signal
import struct
import sys
import time
from pathlib import Path

import rospy
import tf2_ros
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import PoseStamped, TransformStamped
from nav_msgs.msg import Path as RosPath
from sensor_msgs.msg import PointCloud2, PointField
from std_msgs.msg import Header
from sunray_msgs.msg import UAVControlCMD, UAVSetup, UAVState


class MissionNode:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.result_dir = Path(args.result_dir)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.uav_ns = f"/{args.uav_name}{args.uav_id}"
        self.start_wall = time.time()
        self.state = UAVState()
        self.state_seen = False
        self.state_rows: list[dict] = []
        self.truth_rows: list[dict] = []
        self.local_rows: list[dict] = []
        self.reference_rows: list[dict] = []
        self.figure8_error_rows: list[dict] = []
        self.spiral_error_rows: list[dict] = []
        self.lidar_rows: list[dict] = []
        self.phase = "init"
        self.home_xy: tuple[float, float] | None = None
        self.home_z: float | None = None
        self.control_home_xy: tuple[float, float] | None = None
        self.control_home_z: float | None = None
        self.adaptive_command_offset = [0.0, 0.0, 0.0]
        self.truth_model_name = args.truth_model_name
        self.reference_path = RosPath(header=Header(frame_id=args.path_frame))
        self.truth_path = RosPath(header=Header(frame_id=args.path_frame))
        self.tf_broadcaster = tf2_ros.TransformBroadcaster()
        self.last_truth_pose = None
        self.last_truth_path_append_t = -1.0
        self.last_truth_path_publish_t = -1.0
        self.last_reference_path_publish_t = -1.0
        self.accumulated_cloud_points: list[tuple[float, float, float, int]] = []
        self.accumulated_cloud_messages = 0
        self.accumulated_cloud_last_publish_t = -1.0
        self.accumulated_cloud_last_point_count = 0

        self.cmd_pub = rospy.Publisher(
            f"{self.uav_ns}/sunray/uav_control_cmd",
            UAVControlCMD,
            queue_size=5,
        )
        self.setup_pub = rospy.Publisher(f"{self.uav_ns}/sunray/setup", UAVSetup, queue_size=5)
        self.ref_path_pub = rospy.Publisher("/mosim/sunray/reference_path", RosPath, queue_size=1, latch=True)
        self.truth_path_pub = rospy.Publisher("/mosim/sunray/truth_path", RosPath, queue_size=1, latch=True)
        self.accumulated_cloud_pub = rospy.Publisher(
            args.accumulated_cloud_topic,
            PointCloud2,
            queue_size=1,
            latch=True,
        )

        rospy.Subscriber(f"{self.uav_ns}/sunray/uav_state", UAVState, self.on_state, queue_size=20)
        rospy.Subscriber("/gazebo/model_states", ModelStates, self.on_model_states, queue_size=20)
        rospy.Subscriber(
            f"{self.uav_ns}/mavros/local_position/pose",
            PoseStamped,
            self.on_local_pose,
            queue_size=20,
        )
        rospy.Subscriber(f"{self.uav_ns}/livox/lidar", PointCloud2, self.on_lidar, queue_size=5)

    def now(self) -> float:
        stamp = rospy.Time.now().to_sec()
        if stamp > 0:
            return stamp
        return time.time() - self.start_wall

    def on_state(self, msg: UAVState) -> None:
        self.state = msg
        self.state_seen = True
        self.state_rows.append(
            {
                "t": self.now(),
                "phase": self.phase,
                "connected": bool(msg.connected),
                "armed": bool(msg.armed),
                "mode": msg.mode,
                "control_mode": int(msg.control_mode),
                "landed_state": int(msg.landed_state),
                "x": float(msg.position[0]),
                "y": float(msg.position[1]),
                "z": float(msg.position[2]),
                "vx": float(msg.velocity[0]),
                "vy": float(msg.velocity[1]),
                "vz": float(msg.velocity[2]),
                "roll": float(msg.attitude[0]),
                "pitch": float(msg.attitude[1]),
                "yaw": float(msg.attitude[2]),
                "sp_x": float(msg.pos_setpoint[0]),
                "sp_y": float(msg.pos_setpoint[1]),
                "sp_z": float(msg.pos_setpoint[2]),
                "sp_vx": float(msg.vel_setpoint[0]),
                "sp_vy": float(msg.vel_setpoint[1]),
                "sp_vz": float(msg.vel_setpoint[2]),
            }
        )

    def on_model_states(self, msg: ModelStates) -> None:
        try:
            idx = list(msg.name).index(self.truth_model_name)
        except ValueError:
            return
        pose = msg.pose[idx]
        twist = msg.twist[idx]
        q = pose.orientation
        yaw = math.atan2(
            2.0 * (q.w * q.z + q.x * q.y),
            1.0 - 2.0 * (q.y * q.y + q.z * q.z),
        )
        row = {
            "t": self.now(),
            "phase": self.phase,
            "x": pose.position.x,
            "y": pose.position.y,
            "z": pose.position.z,
            "vx": twist.linear.x,
            "vy": twist.linear.y,
            "vz": twist.linear.z,
            "roll": math.atan2(
                2.0 * (q.w * q.x + q.y * q.z),
                1.0 - 2.0 * (q.x * q.x + q.y * q.y),
            ),
            "pitch": math.asin(max(-1.0, min(1.0, 2.0 * (q.w * q.y - q.z * q.x)))),
            "yaw": yaw,
        }
        self.truth_rows.append(row)
        self.last_truth_pose = pose
        self.maybe_publish_truth_path(pose, row["t"])
        self.publish_truth_tf(pose)

    def maybe_publish_truth_path(self, pose, now_s: float) -> None:
        append_period = 1.0 / max(self.args.path_sample_rate_hz, 0.1)
        publish_period = 1.0 / max(self.args.path_publish_rate_hz, 0.1)
        if self.last_truth_path_append_t < 0 or now_s - self.last_truth_path_append_t >= append_period:
            ps = PoseStamped()
            ps.header.stamp = rospy.Time.now()
            ps.header.frame_id = self.args.path_frame
            ps.pose = pose
            self.truth_path.header.stamp = ps.header.stamp
            self.truth_path.poses.append(ps)
            self.last_truth_path_append_t = now_s
            if self.args.max_path_points > 0 and len(self.truth_path.poses) > self.args.max_path_points:
                self.truth_path.poses = self.truth_path.poses[-self.args.max_path_points :]
        if self.last_truth_path_publish_t < 0 or now_s - self.last_truth_path_publish_t >= publish_period:
            self.truth_path_pub.publish(self.truth_path)
            self.last_truth_path_publish_t = now_s

    def publish_review_surfaces(self) -> None:
        stamp = rospy.Time.now()
        if self.truth_path.poses:
            self.truth_path.header.stamp = stamp
            self.truth_path_pub.publish(self.truth_path)
        if self.reference_path.poses:
            self.reference_path.header.stamp = stamp
            self.ref_path_pub.publish(self.reference_path)
        if self.last_truth_pose is not None:
            self.publish_truth_tf(self.last_truth_pose)
        if self.accumulated_cloud_points:
            self.publish_accumulated_cloud(force=True)

    def current_z(self) -> float:
        if self.truth_rows:
            return float(self.truth_rows[-1]["z"])
        if self.local_rows:
            return float(self.local_rows[-1]["z"])
        return float(self.state.position[2])

    def target_z(self) -> float:
        if self.home_z is not None:
            return float(self.home_z) + float(self.args.altitude_m)
        return float(self.state.home_pos[2]) + float(self.args.altitude_m)

    def command_xy(self, x_ref: float, y_ref: float) -> tuple[float, float]:
        return (
            float(x_ref) + float(self.args.command_offset_x_m) + self.adaptive_command_offset[0],
            float(y_ref) + float(self.args.command_offset_y_m) + self.adaptive_command_offset[1],
        )

    def command_z(self, z_ref: float) -> float:
        return float(z_ref) + float(self.args.command_offset_z_m) + self.adaptive_command_offset[2]

    def publish_truth_tf(self, pose) -> None:
        transform = TransformStamped()
        transform.header.stamp = rospy.Time.now()
        transform.header.frame_id = self.args.path_frame
        transform.child_frame_id = f"{self.args.uav_name}{self.args.uav_id}/base_link"
        transform.transform.translation.x = pose.position.x
        transform.transform.translation.y = pose.position.y
        transform.transform.translation.z = pose.position.z
        transform.transform.rotation = pose.orientation
        self.tf_broadcaster.sendTransform(transform)

    def on_local_pose(self, msg: PoseStamped) -> None:
        p = msg.pose.position
        self.local_rows.append({"t": self.now(), "phase": self.phase, "x": p.x, "y": p.y, "z": p.z})

    def on_lidar(self, msg: PointCloud2) -> None:
        fields = [field.name for field in msg.fields]
        self.lidar_rows.append(
            {
                "t": self.now(),
                "phase": self.phase,
                "width": int(msg.width),
                "height": int(msg.height),
                "point_step": int(msg.point_step),
                "row_step": int(msg.row_step),
                "data_len": len(msg.data),
                "point_count": int(msg.width) * int(msg.height),
                "frame_id": msg.header.frame_id,
                "fields": fields,
                "accumulated_map_points": len(self.accumulated_cloud_points),
            }
        )
        self.accumulate_lidar_cloud(msg)

    def accumulate_lidar_cloud(self, msg: PointCloud2) -> None:
        if not self.args.publish_accumulated_cloud:
            return
        if self.last_truth_pose is None:
            return
        field_offsets = {field.name: field.offset for field in msg.fields}
        if not {"x", "y", "z"}.issubset(field_offsets):
            return
        if msg.point_step < 12 or not msg.data:
            return

        pose = self.last_truth_pose
        rotation = self.quaternion_to_rotation_matrix(
            pose.orientation.x,
            pose.orientation.y,
            pose.orientation.z,
            pose.orientation.w,
        )
        tx = float(pose.position.x)
        ty = float(pose.position.y)
        tz = float(pose.position.z)

        total = int(msg.width) * int(msg.height)
        stride = max(1, int(self.args.accumulated_cloud_point_stride))
        max_points = max(1, int(self.args.accumulated_cloud_max_points))
        data = msg.data
        x_off = field_offsets["x"]
        y_off = field_offsets["y"]
        z_off = field_offsets["z"]
        endian = ">" if msg.is_bigendian else "<"

        new_points: list[tuple[float, float, float, int]] = []
        for idx in range(0, total, stride):
            base = idx * msg.point_step
            try:
                lx = struct.unpack_from(endian + "f", data, base + x_off)[0]
                ly = struct.unpack_from(endian + "f", data, base + y_off)[0]
                lz = struct.unpack_from(endian + "f", data, base + z_off)[0]
            except struct.error:
                break
            if not (math.isfinite(lx) and math.isfinite(ly) and math.isfinite(lz)):
                continue
            mx = tx + rotation[0][0] * lx + rotation[0][1] * ly + rotation[0][2] * lz
            my = ty + rotation[1][0] * lx + rotation[1][1] * ly + rotation[1][2] * lz
            mz = tz + rotation[2][0] * lx + rotation[2][1] * ly + rotation[2][2] * lz
            if self.args.accumulated_cloud_min_z_m <= mz <= self.args.accumulated_cloud_max_z_m:
                new_points.append((mx, my, mz, self.height_color_rgb(mz)))

        if not new_points:
            return
        self.accumulated_cloud_points.extend(new_points)
        if len(self.accumulated_cloud_points) > max_points:
            self.accumulated_cloud_points = self.accumulated_cloud_points[-max_points:]
        self.accumulated_cloud_last_point_count = len(self.accumulated_cloud_points)
        now_s = self.now()
        publish_period = 1.0 / max(self.args.accumulated_cloud_publish_rate_hz, 0.1)
        if (
            self.accumulated_cloud_last_publish_t < 0
            or now_s - self.accumulated_cloud_last_publish_t >= publish_period
        ):
            self.publish_accumulated_cloud()
            self.accumulated_cloud_last_publish_t = now_s

    @staticmethod
    def quaternion_to_rotation_matrix(x: float, y: float, z: float, w: float) -> list[list[float]]:
        norm = math.sqrt(x * x + y * y + z * z + w * w)
        if norm <= 0.0:
            return [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        x /= norm
        y /= norm
        z /= norm
        w /= norm
        return [
            [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w)],
            [2.0 * (x * y + z * w), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - x * w)],
            [2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x * x + y * y)],
        ]

    def height_color_rgb(self, z: float) -> int:
        lo = self.args.accumulated_cloud_color_min_z_m
        hi = self.args.accumulated_cloud_color_max_z_m
        if hi <= lo:
            t = 0.5
        else:
            t = max(0.0, min(1.0, (z - lo) / (hi - lo)))
        # Blue -> cyan -> green -> yellow -> red height palette.
        if t < 0.25:
            k = t / 0.25
            r, g, b = 0, int(255 * k), 255
        elif t < 0.5:
            k = (t - 0.25) / 0.25
            r, g, b = 0, 255, int(255 * (1.0 - k))
        elif t < 0.75:
            k = (t - 0.5) / 0.25
            r, g, b = int(255 * k), 255, 0
        else:
            k = (t - 0.75) / 0.25
            r, g, b = 255, int(255 * (1.0 - k)), 0
        return (r << 16) | (g << 8) | b

    def publish_accumulated_cloud(self, force: bool = False) -> None:
        if not self.accumulated_cloud_points:
            return
        if force:
            self.accumulated_cloud_last_publish_t = self.now()
        msg = PointCloud2()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.args.path_frame
        msg.height = 1
        msg.width = len(self.accumulated_cloud_points)
        msg.fields = [
            PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
            PointField(name="rgb", offset=12, datatype=PointField.FLOAT32, count=1),
        ]
        msg.is_bigendian = False
        msg.point_step = 16
        msg.row_step = msg.point_step * msg.width
        msg.is_dense = True
        msg.data = b"".join(
            struct.pack("<ffff", float(x), float(y), float(z), self.packed_rgb_float(int(rgb)))
            for x, y, z, rgb in self.accumulated_cloud_points
        )
        self.accumulated_cloud_pub.publish(msg)
        self.accumulated_cloud_messages += 1

    @staticmethod
    def packed_rgb_float(rgb: int) -> float:
        return struct.unpack("<f", struct.pack("<I", rgb & 0x00FFFFFF))[0]

    def cmd(self, cmd_type: int, pos=None, vel=None, acc=None, yaw: float = 0.0) -> UAVControlCMD:
        msg = UAVControlCMD()
        msg.header.stamp = rospy.Time.now()
        msg.cmd = cmd_type
        msg.desired_pos = list(pos if pos is not None else [0.0, 0.0, 0.0])
        msg.desired_vel = list(vel if vel is not None else [0.0, 0.0, 0.0])
        msg.desired_acc = list(acc if acc is not None else [0.0, 0.0, 0.0])
        msg.desired_att = [0.0, 0.0, 0.0]
        msg.desired_yaw = yaw
        msg.desired_yaw_rate = 0.0
        return msg

    def position_hold_cmd_type(self) -> int:
        if self.args.position_hold_mode == "ctrlxyzpos":
            return UAVControlCMD.CTRL_XyzPos
        return UAVControlCMD.XyzPos

    def setup(self, cmd_type: int, control_mode: str = "") -> UAVSetup:
        msg = UAVSetup()
        msg.header.stamp = rospy.Time.now()
        msg.cmd = cmd_type
        msg.control_mode = control_mode
        return msg

    def wait_until(self, predicate, timeout_s: float, rate_hz: float = 20.0) -> bool:
        deadline = time.time() + timeout_s
        rate = rospy.Rate(rate_hz)
        while not rospy.is_shutdown() and time.time() < deadline:
            if predicate():
                return True
            rate.sleep()
        return False

    def wait_for_connection(self) -> None:
        self.phase = "wait_connection"
        if not self.wait_until(lambda: self.state_seen and self.state.connected, self.args.connect_timeout_s):
            raise RuntimeError("uav_state_not_connected")
        self.home_xy = (float(self.state.position[0]), float(self.state.position[1]))
        self.home_z = float(self.state.position[2])

    def enter_cmd_control(self) -> None:
        self.phase = "cmd_control"
        rate = rospy.Rate(2)
        deadline = time.time() + self.args.mode_timeout_s
        while not rospy.is_shutdown() and time.time() < deadline:
            if self.state.control_mode == UAVSetup.CMD_CONTROL:
                return
            self.setup_pub.publish(self.setup(UAVSetup.SET_CONTROL_MODE, "CMD_CONTROL"))
            rate.sleep()
        raise RuntimeError("cmd_control_mode_timeout")

    def arm(self) -> None:
        self.phase = "arm"
        rate = rospy.Rate(2)
        deadline = time.time() + self.args.arm_timeout_s
        while not rospy.is_shutdown() and time.time() < deadline:
            if self.state.armed:
                self.sync_control_home()
                return
            self.setup_pub.publish(self.setup(UAVSetup.ARM))
            rate.sleep()
        raise RuntimeError("arm_timeout")

    def sync_control_home(self) -> None:
        deadline = time.time() + 3.0
        rate = rospy.Rate(20)
        while not rospy.is_shutdown() and time.time() < deadline:
            home = list(self.state.home_pos)
            if any(abs(float(v)) > 1e-6 for v in home):
                self.control_home_xy = (float(home[0]), float(home[1]))
                self.control_home_z = float(home[2])
                self.home_xy = self.control_home_xy
                self.home_z = self.control_home_z
                return
            rate.sleep()

    def takeoff(self) -> None:
        self.phase = "takeoff"
        rate = rospy.Rate(5)
        target = self.target_z()
        if self.home_xy is None:
            hold_x = float(self.state.position[0])
            hold_y = float(self.state.position[1])
        else:
            hold_x, hold_y = self.home_xy
        deadline = time.time() + self.args.takeoff_timeout_s
        stable_since = None
        while not rospy.is_shutdown() and time.time() < deadline:
            z_now = self.current_z()
            vz_now = float(self.state.velocity[2])
            stable = (
                abs(z_now - target) <= self.args.takeoff_z_tolerance_m
                and abs(vz_now) <= self.args.takeoff_max_abs_vz_mps
            )
            if stable:
                if stable_since is None:
                    stable_since = time.time()
                elif time.time() - stable_since >= self.args.takeoff_stable_s:
                    return
            else:
                stable_since = None
            if self.state.landed_state == 1 or z_now < self.args.takeoff_airborne_z_m:
                self.cmd_pub.publish(self.cmd(UAVControlCMD.Takeoff))
            else:
                cmd_x, cmd_y = self.command_xy(hold_x, hold_y)
                self.cmd_pub.publish(self.cmd(self.position_hold_cmd_type(), pos=[cmd_x, cmd_y, self.command_z(target)], yaw=0.0))
            rate.sleep()
        z_now = self.current_z()
        raise RuntimeError(
            "takeoff_timeout:"
            f"target_z={target:.3f},current_z={z_now:.3f},"
            f"vz={float(self.state.velocity[2]):.3f},"
            f"state_z={float(self.state.position[2]):.3f},"
            f"landed_state={self.state.landed_state},armed={self.state.armed},"
            f"control_mode={self.state.control_mode}"
        )

    def hover(self, duration_s: float, phase: str = "hover") -> None:
        self.phase = phase
        rate = rospy.Rate(10)
        end = time.time() + duration_s
        while not rospy.is_shutdown() and time.time() < end:
            self.cmd_pub.publish(self.cmd(UAVControlCMD.Hover))
            rate.sleep()

    def hold_home_position(self, duration_s: float, phase: str = "hold_home") -> None:
        self.phase = phase
        rate = rospy.Rate(20)
        end = time.time() + duration_s
        if self.home_xy is None:
            x_ref = float(self.state.position[0])
            y_ref = float(self.state.position[1])
        else:
            x_ref, y_ref = self.home_xy
        z_ref = self.target_z()
        cmd_x, cmd_y = self.command_xy(x_ref, y_ref)
        cmd_z = self.command_z(z_ref)
        while not rospy.is_shutdown() and time.time() < end:
            self.cmd_pub.publish(self.cmd(self.position_hold_cmd_type(), pos=[cmd_x, cmd_y, cmd_z], yaw=0.0))
            rate.sleep()

    def calibrate_hover_bias(self) -> None:
        if not self.args.enable_hover_bias_calibration:
            return
        self.phase = "hover_bias_calibration"
        self.hold_home_position(self.args.hover_bias_calibration_settle_s, self.phase)
        rows = self.tail_phase_rows(self.truth_rows, self.phase, self.args.hover_bias_calibration_tail_s)
        if not rows or self.home_xy is None:
            return
        mean_x = sum(float(r["x"]) for r in rows) / len(rows)
        mean_y = sum(float(r["y"]) for r in rows) / len(rows)
        mean_z = sum(float(r["z"]) for r in rows) / len(rows)
        target_x, target_y = self.home_xy
        target_z = self.target_z()
        gain = self.args.hover_bias_calibration_gain
        axes = set(self.args.hover_bias_calibration_axes.lower())
        if "x" in axes:
            self.adaptive_command_offset[0] += max(
                -self.args.hover_bias_calibration_max_step_m,
                min(self.args.hover_bias_calibration_max_step_m, gain * (target_x - mean_x)),
            )
        if "y" in axes:
            self.adaptive_command_offset[1] += max(
                -self.args.hover_bias_calibration_max_step_m,
                min(self.args.hover_bias_calibration_max_step_m, gain * (target_y - mean_y)),
            )
        if "z" in axes:
            self.adaptive_command_offset[2] += max(
                -self.args.hover_bias_calibration_max_step_m,
                min(self.args.hover_bias_calibration_max_step_m, gain * (target_z - mean_z)),
            )
        self.phase = "post_hover_bias_calibration"
        self.hold_home_position(self.args.hover_bias_calibration_verify_s, self.phase)

    def land(self) -> None:
        self.phase = "land"
        rate = rospy.Rate(2)
        deadline = time.time() + self.args.land_timeout_s
        while not rospy.is_shutdown() and time.time() < deadline:
            self.cmd_pub.publish(self.cmd(UAVControlCMD.Land))
            if self.state.landed_state == 1 and float(self.state.position[2]) <= self.args.max_landed_state_z_m:
                break
            rate.sleep()
        self.phase = "settle"
        end = time.time() + self.args.final_settle_s
        while not rospy.is_shutdown() and time.time() < end:
            self.cmd_pub.publish(self.cmd(UAVControlCMD.Land))
            self.publish_review_surfaces()
            rate.sleep()

    def publish_reference_path_point(self, x: float, y: float, z: float) -> None:
        ps = PoseStamped()
        ps.header.stamp = rospy.Time.now()
        ps.header.frame_id = self.args.path_frame
        ps.pose.position.x = x
        ps.pose.position.y = y
        ps.pose.position.z = z
        ps.pose.orientation.w = 1.0
        self.reference_path.header.stamp = ps.header.stamp
        self.reference_path.poses.append(ps)
        if self.args.max_path_points > 0 and len(self.reference_path.poses) > self.args.max_path_points:
            self.reference_path.poses = self.reference_path.poses[-self.args.max_path_points :]
        now_s = self.now()
        publish_period = 1.0 / max(self.args.path_publish_rate_hz, 0.1)
        if self.last_reference_path_publish_t < 0 or now_s - self.last_reference_path_publish_t >= publish_period:
            self.ref_path_pub.publish(self.reference_path)
            self.last_reference_path_publish_t = now_s

    def publish_traj_command(
        self,
        x_ref: float,
        y_ref: float,
        z_ref: float,
        vx_ref: float,
        vy_ref: float,
        vz_ref: float,
        ax_ref: float,
        ay_ref: float,
        az_ref: float,
    ) -> None:
        x_cmd, y_cmd = self.command_xy(x_ref, y_ref)
        z_cmd = self.command_z(z_ref)
        if self.args.control_mode == "ctrltraj":
            self.cmd_pub.publish(
                self.cmd(
                    UAVControlCMD.CTRL_Traj,
                    pos=[x_cmd, y_cmd, z_cmd],
                    vel=[vx_ref, vy_ref, vz_ref],
                    acc=[ax_ref, ay_ref, az_ref],
                    yaw=0.0,
                )
            )
        elif self.args.control_mode == "posvel":
            self.cmd_pub.publish(
                self.cmd(
                    UAVControlCMD.XyzPosVelYaw,
                    pos=[x_cmd, y_cmd, z_cmd],
                    vel=[vx_ref, vy_ref, vz_ref],
                    yaw=0.0,
                )
            )
        elif self.args.control_mode == "xyvelzpos":
            ex = x_cmd - float(self.state.position[0])
            ey = y_cmd - float(self.state.position[1])
            vx_cmd = max(-self.args.max_xy_vel_mps, min(self.args.max_xy_vel_mps, vx_ref + self.args.kp_xy * ex))
            vy_cmd = max(-self.args.max_xy_vel_mps, min(self.args.max_xy_vel_mps, vy_ref + self.args.kp_xy * ey))
            self.cmd_pub.publish(
                self.cmd(
                    UAVControlCMD.XyVelZPos,
                    pos=[0.0, 0.0, z_cmd],
                    vel=[vx_cmd, vy_cmd, vz_ref],
                )
            )
        else:
            self.cmd_pub.publish(self.cmd(UAVControlCMD.XyzPos, pos=[x_cmd, y_cmd, z_cmd]))

    def run_figure8(self) -> None:
        self.phase = "pre_figure8_hover"
        self.hold_home_position(self.args.pre_figure8_hold_s, self.phase)
        if self.home_xy is None:
            local_cx = float(self.state.position[0])
            local_cy = float(self.state.position[1])
        else:
            local_cx, local_cy = self.home_xy
        world_cx, world_cy = local_cx, local_cy
        z_ref = self.target_z()
        amp_x = self.args.figure8_amp_x_m
        amp_y = self.args.figure8_amp_y_m
        omega = 2.0 * math.pi / self.args.figure8_period_s
        target_theta = 2.0 * math.pi * self.args.figure8_laps
        ramp_s = max(0.0, min(float(self.args.figure8_speed_ramp_s), self.args.figure8_period_s))
        total = self.figure8_total_time_s(target_theta, omega, ramp_s)
        rate = rospy.Rate(self.args.command_rate_hz)
        t0 = self.now()
        self.phase = "figure8"
        while not rospy.is_shutdown():
            elapsed = self.now() - t0
            if elapsed > total:
                break
            theta_ref, theta_dot_ref, theta_ddot_ref = self.figure8_theta_profile(elapsed, omega, ramp_s, target_theta)
            theta_cmd, theta_dot_cmd, theta_ddot_cmd = self.figure8_theta_profile(
                elapsed + self.args.trajectory_time_lead_s,
                omega,
                ramp_s,
                target_theta,
            )
            theta_cmd = min(theta_cmd, target_theta)
            x_ref_local = local_cx + amp_x * math.sin(theta_ref)
            y_ref_local = local_cy + amp_y * math.sin(2.0 * theta_ref)
            x_ref_world = world_cx + amp_x * math.sin(theta_ref)
            y_ref_world = world_cy + amp_y * math.sin(2.0 * theta_ref)
            x_cmd_local = local_cx + amp_x * math.sin(theta_cmd)
            y_cmd_local = local_cy + amp_y * math.sin(2.0 * theta_cmd)
            vx_cmd = amp_x * math.cos(theta_cmd) * theta_dot_cmd
            vy_cmd = 2.0 * amp_y * math.cos(2.0 * theta_cmd) * theta_dot_cmd
            ax_cmd = amp_x * (-math.sin(theta_cmd) * theta_dot_cmd * theta_dot_cmd + math.cos(theta_cmd) * theta_ddot_cmd)
            ay_cmd = 2.0 * amp_y * (
                -2.0 * math.sin(2.0 * theta_cmd) * theta_dot_cmd * theta_dot_cmd
                + math.cos(2.0 * theta_cmd) * theta_ddot_cmd
            )
            vx_ref = amp_x * math.cos(theta_ref) * theta_dot_ref
            vy_ref = 2.0 * amp_y * math.cos(2.0 * theta_ref) * theta_dot_ref
            ax_ref = amp_x * (-math.sin(theta_ref) * theta_dot_ref * theta_dot_ref + math.cos(theta_ref) * theta_ddot_ref)
            ay_ref = 2.0 * amp_y * (
                -2.0 * math.sin(2.0 * theta_ref) * theta_dot_ref * theta_dot_ref
                + math.cos(2.0 * theta_ref) * theta_ddot_ref
            )
            row = {
                "t": self.now(),
                "phase": self.phase,
                "x": x_ref_world,
                "y": y_ref_world,
                "z": z_ref,
                "local_x": x_ref_local,
                "local_y": y_ref_local,
                "vx": vx_ref,
                "vy": vy_ref,
                "vz": 0.0,
                "ax": ax_ref,
                "ay": ay_ref,
                "az": 0.0,
            }
            self.reference_rows.append(row)
            self.publish_reference_path_point(x_ref_world, y_ref_world, z_ref)
            self.publish_traj_command(
                x_cmd_local,
                y_cmd_local,
                z_ref,
                vx_cmd,
                vy_cmd,
                0.0,
                ax_cmd,
                ay_cmd,
                0.0,
            )
            rate.sleep()
        self.hold_home_position(self.args.post_figure8_hold_s, "post_figure8_hover")

    @staticmethod
    def figure8_total_time_s(target_theta: float, omega: float, ramp_s: float) -> float:
        if ramp_s <= 0.0 or omega <= 0.0:
            return target_theta / omega if omega > 0.0 else 0.0
        theta_ramp = 0.5 * omega * ramp_s
        const_s = max(0.0, (target_theta - 2.0 * theta_ramp) / omega)
        return 2.0 * ramp_s + const_s

    @staticmethod
    def figure8_theta_profile(elapsed: float, omega: float, ramp_s: float, target_theta: float | None = None) -> tuple[float, float, float]:
        if ramp_s <= 0.0:
            return omega * elapsed, omega, 0.0
        ramp_s = max(0.0, ramp_s)
        if elapsed <= ramp_s:
            theta = 0.5 * omega * elapsed * elapsed / ramp_s
            theta_dot = omega * elapsed / ramp_s
            theta_ddot = omega / ramp_s
            return theta, theta_dot, theta_ddot
        theta_ramp = 0.5 * omega * ramp_s
        if target_theta is None:
            return omega * (elapsed - 0.5 * ramp_s), omega, 0.0
        const_s = max(0.0, (target_theta - 2.0 * theta_ramp) / omega)
        if elapsed <= ramp_s + const_s:
            return theta_ramp + omega * (elapsed - ramp_s), omega, 0.0
        dt = elapsed - ramp_s - const_s
        if dt <= ramp_s:
            theta = theta_ramp + omega * const_s + omega * dt - 0.5 * omega * dt * dt / ramp_s
            theta_dot = max(0.0, omega * (1.0 - dt / ramp_s))
            theta_ddot = -omega / ramp_s
            return theta, theta_dot, theta_ddot
        return target_theta, 0.0, 0.0

    def run_spiral_climb(self) -> None:
        self.phase = "pre_spiral_hover"
        self.hold_home_position(self.args.pre_spiral_hold_s, self.phase)
        if self.home_xy is None:
            cx = float(self.state.position[0])
            cy = float(self.state.position[1])
        else:
            cx, cy = self.home_xy
        z0 = self.target_z()
        z1 = z0 + self.args.spiral_height_m
        radius = self.args.spiral_radius_m
        omega = 2.0 * math.pi / self.args.spiral_period_s
        target_theta = 2.0 * math.pi * self.args.spiral_turns
        ramp_s = max(0.0, min(float(self.args.spiral_speed_ramp_s), self.args.spiral_period_s))
        total = self.figure8_total_time_s(target_theta, omega, ramp_s) if ramp_s > 0.0 else self.args.spiral_period_s * self.args.spiral_turns
        climb_rate = self.args.spiral_height_m / total if total > 0 else 0.0
        rate = rospy.Rate(self.args.command_rate_hz)
        z_time_lead = self.args.trajectory_time_lead_s
        if self.args.trajectory_z_time_lead_s is not None:
            z_time_lead = self.args.trajectory_z_time_lead_s
        if self.args.spiral_entry_s > 0 and radius > 0:
            self.phase = "spiral_entry"
            entry_t0 = self.now()
            while not rospy.is_shutdown():
                elapsed = self.now() - entry_t0
                if elapsed > self.args.spiral_entry_s:
                    break
                s = max(0.0, min(1.0, elapsed / self.args.spiral_entry_s))
                # Smoothstep gives zero velocity at the center and at the circle start.
                smooth = s * s * (3.0 - 2.0 * s)
                ds_dt = 6.0 * s * (1.0 - s) / self.args.spiral_entry_s
                d2s_dt2 = 6.0 * (1.0 - 2.0 * s) / (self.args.spiral_entry_s * self.args.spiral_entry_s)
                x_ref = cx + radius * smooth
                y_ref = cy
                z_ref = z0
                vx_ref = radius * ds_dt
                vy_ref = 0.0
                vz_ref = 0.0
                ax_ref = radius * d2s_dt2
                ay_ref = 0.0
                row = {
                    "t": self.now(),
                    "phase": self.phase,
                    "x": x_ref,
                    "y": y_ref,
                    "z": z_ref,
                    "local_x": x_ref,
                    "local_y": y_ref,
                    "vx": vx_ref,
                    "vy": vy_ref,
                    "vz": vz_ref,
                    "ax": ax_ref,
                    "ay": ay_ref,
                    "az": 0.0,
                }
                self.reference_rows.append(row)
                self.publish_reference_path_point(x_ref, y_ref, z_ref)
                self.publish_traj_command(x_ref, y_ref, z_ref, vx_ref, vy_ref, vz_ref, ax_ref, ay_ref, 0.0)
                rate.sleep()
            self.hold_position(cx + radius, cy, z0, self.args.spiral_entry_settle_s, "spiral_entry_settle")
        t0 = self.now()
        self.phase = "spiral_climb"
        while not rospy.is_shutdown():
            elapsed = self.now() - t0
            if elapsed > total:
                break
            theta, theta_dot, theta_ddot = self.spiral_theta_profile(elapsed, omega, ramp_s, target_theta)
            cmd_elapsed = max(0.0, min(total, elapsed + self.args.trajectory_time_lead_s))
            z_cmd_elapsed = max(0.0, min(total, elapsed + z_time_lead))
            theta_cmd, theta_dot_cmd, theta_ddot_cmd = self.spiral_theta_profile(
                cmd_elapsed,
                omega,
                ramp_s,
                target_theta,
            )
            z_ref, vz_ref, az_ref = self.spiral_z_reference(elapsed, z0, total, theta, theta_dot, theta_ddot, target_theta)
            z_cmd, vz_cmd, az_cmd = self.spiral_z_reference(
                z_cmd_elapsed,
                z0,
                total,
                theta_cmd,
                theta_dot_cmd,
                theta_ddot_cmd,
                target_theta,
            )
            x_ref = cx + radius * math.cos(theta)
            y_ref = cy + radius * math.sin(theta)
            x_cmd = cx + radius * math.cos(theta_cmd)
            y_cmd = cy + radius * math.sin(theta_cmd)
            vx_ref = -radius * math.sin(theta) * theta_dot
            vy_ref = radius * math.cos(theta) * theta_dot
            vx_cmd = -radius * math.sin(theta_cmd) * theta_dot_cmd
            vy_cmd = radius * math.cos(theta_cmd) * theta_dot_cmd
            ax_ref = -radius * (math.cos(theta) * theta_dot * theta_dot + math.sin(theta) * theta_ddot)
            ay_ref = radius * (-math.sin(theta) * theta_dot * theta_dot + math.cos(theta) * theta_ddot)
            ax_cmd = -radius * (math.cos(theta_cmd) * theta_dot_cmd * theta_dot_cmd + math.sin(theta_cmd) * theta_ddot_cmd)
            ay_cmd = radius * (-math.sin(theta_cmd) * theta_dot_cmd * theta_dot_cmd + math.cos(theta_cmd) * theta_ddot_cmd)
            row = {
                "t": self.now(),
                "phase": self.phase,
                "x": x_ref,
                "y": y_ref,
                "z": z_ref,
                "local_x": x_ref,
                "local_y": y_ref,
                "vx": vx_ref,
                "vy": vy_ref,
                "vz": vz_ref,
                "ax": ax_ref,
                "ay": ay_ref,
                "az": az_ref,
            }
            self.reference_rows.append(row)
            self.publish_reference_path_point(x_ref, y_ref, z_ref)
            self.publish_traj_command(x_cmd, y_cmd, z_cmd, vx_cmd, vy_cmd, vz_cmd, ax_cmd, ay_cmd, az_cmd)
            rate.sleep()
        self.hold_home_position(self.args.post_spiral_hold_s, "post_spiral_hover")

    @staticmethod
    def spiral_theta_profile(elapsed: float, omega: float, ramp_s: float, target_theta: float) -> tuple[float, float, float]:
        if ramp_s <= 0.0:
            theta = min(target_theta, max(0.0, omega * elapsed))
            theta_dot = omega if theta < target_theta else 0.0
            return theta, theta_dot, 0.0
        return MissionNode.figure8_theta_profile(elapsed, omega, ramp_s, target_theta)

    def spiral_z_reference(
        self,
        elapsed: float,
        z0: float,
        total: float,
        theta: float | None = None,
        theta_dot: float = 0.0,
        theta_ddot: float = 0.0,
        target_theta: float | None = None,
    ) -> tuple[float, float, float]:
        height = self.args.spiral_height_m
        if total <= 0:
            return z0, 0.0, 0.0
        if self.args.spiral_z_profile == "theta_ramp" and theta is not None and target_theta and target_theta > 0:
            scale = height / target_theta
            progress = max(0.0, min(1.0, theta / target_theta))
            return z0 + height * progress, scale * theta_dot, scale * theta_ddot
        if self.args.spiral_z_profile == "linear":
            return z0 + height * elapsed / total, height / total, 0.0
        s = max(0.0, min(1.0, elapsed / total))
        smooth = s * s * (3.0 - 2.0 * s)
        ds_dt = 6.0 * s * (1.0 - s) / total
        d2s_dt2 = 6.0 * (1.0 - 2.0 * s) / (total * total)
        return z0 + height * smooth, height * ds_dt, height * d2s_dt2

    def hold_position(self, x_ref: float, y_ref: float, z_ref: float, duration_s: float, phase: str) -> None:
        self.phase = phase
        rate = rospy.Rate(20)
        end = time.time() + duration_s
        while not rospy.is_shutdown() and time.time() < end:
            self.publish_traj_command(x_ref, y_ref, z_ref, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            rate.sleep()

    def run(self) -> dict:
        self.wait_for_connection()
        self.enter_cmd_control()
        self.arm()
        self.takeoff()
        self.calibrate_hover_bias()
        self.hold_home_position(self.args.initial_hover_s, "initial_hover")
        if self.args.mission == "figure8":
            self.run_figure8()
        elif self.args.mission == "spiral_climb":
            self.run_spiral_climb()
        self.land()
        self.review_hold()
        payload = self.evaluate()
        self.write_outputs()
        (self.result_dir / "SUNRAY_ROS1_NATIVE_MISSION_GATE.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return payload

    def review_hold(self) -> None:
        if self.args.review_hold_s <= 0:
            return
        self.phase = "review_hold"
        rate = rospy.Rate(10)
        end = time.time() + self.args.review_hold_s
        while not rospy.is_shutdown() and time.time() < end:
            self.cmd_pub.publish(self.cmd(UAVControlCMD.Land))
            self.publish_review_surfaces()
            rate.sleep()

    def write_outputs(self) -> None:
        def write_jsonl(name: str, rows: list[dict]) -> None:
            (self.result_dir / name).write_text(
                "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                encoding="utf-8",
            )

        write_jsonl("gazebo_truth_uav1.jsonl", self.truth_rows)
        write_jsonl("mavros_local_position_pose.jsonl", self.local_rows)
        write_jsonl("sunray_uav_state.jsonl", self.state_rows)
        write_jsonl("reference_trajectory.jsonl", self.reference_rows)
        write_jsonl("figure8_time_sync_errors.jsonl", self.figure8_error_rows)
        write_jsonl("spiral_time_sync_errors.jsonl", self.spiral_error_rows)
        write_jsonl("livox_lidar_samples.jsonl", self.lidar_rows)
        for name, rows in [
            ("gazebo_truth_uav1.csv", self.truth_rows),
            ("reference_trajectory.csv", self.reference_rows),
        ]:
            if rows:
                with (self.result_dir / name).open("w", newline="", encoding="utf-8") as f:
                    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                    writer.writeheader()
                    writer.writerows(rows)

    @staticmethod
    def rmse(values: list[float]) -> float | None:
        if not values:
            return None
        return math.sqrt(sum(v * v for v in values) / len(values))

    @staticmethod
    def tail_phase_rows(rows: list[dict], phase: str, tail_s: float) -> list[dict]:
        phase_rows = [r for r in rows if r.get("phase") == phase]
        if not phase_rows or tail_s <= 0:
            return phase_rows
        end_t = phase_rows[-1]["t"]
        return [r for r in phase_rows if end_t - r["t"] <= tail_s]

    def evaluate(self) -> dict:
        rows = self.truth_rows
        blockers: list[str] = []
        if not rows:
            blockers.append("no_gazebo_truth_samples")
            metrics = {}
        else:
            max_z = max(r["z"] for r in rows)
            final = rows[-1]
            hover = [r for r in rows if r["phase"] in {"initial_hover", "pre_figure8_hover"}]
            steady_hover = self.tail_phase_rows(rows, "initial_hover", self.args.steady_hover_eval_tail_s)
            landed = [r for r in rows if r["phase"] == "settle"]
            airborne = [r for r in rows if r["z"] > 0.3]
            max_tilt = max((math.hypot(r["roll"], r["pitch"]) for r in airborne), default=0.0)
            if self.home_xy is None:
                home_x = rows[0]["x"]
                home_y = rows[0]["y"]
            else:
                home_x, home_y = self.home_xy
            hover_xy = [math.hypot(r["x"] - home_x, r["y"] - home_y) for r in hover]
            z_ref = self.target_z()
            hover_z = [abs(r["z"] - z_ref) for r in hover]
            steady_hover_xy = [math.hypot(r["x"] - home_x, r["y"] - home_y) for r in steady_hover]
            steady_hover_z = [abs(r["z"] - z_ref) for r in steady_hover]
            steady_hover_sp_xy = []
            steady_hover_sp_z = []
            state_hover = [
                r for r in self.state_rows
                if r.get("phase") == "initial_hover"
                and steady_hover
                and steady_hover[0]["t"] <= r.get("t", -1.0) <= steady_hover[-1]["t"]
                and math.isfinite(float(r.get("sp_x", float("nan"))))
                and math.isfinite(float(r.get("sp_y", float("nan"))))
                and math.isfinite(float(r.get("sp_z", float("nan"))))
            ]
            if state_hover:
                sp_x = sum(float(r["sp_x"]) for r in state_hover) / len(state_hover)
                sp_y = sum(float(r["sp_y"]) for r in state_hover) / len(state_hover)
                sp_z = sum(float(r["sp_z"]) for r in state_hover) / len(state_hover)
                steady_hover_sp_xy = [math.hypot(r["x"] - sp_x, r["y"] - sp_y) for r in steady_hover]
                steady_hover_sp_z = [abs(r["z"] - sp_z) for r in steady_hover]
            else:
                sp_x = sp_y = sp_z = None
            landed_xy_span = None
            landed_yaw_delta = None
            if len(landed) >= 2:
                landed_xy_span = max(
                    math.hypot(r["x"] - landed[0]["x"], r["y"] - landed[0]["y"])
                    for r in landed
                )
                landed_yaw_delta = landed[-1]["yaw"] - landed[0]["yaw"]
            metrics = {
                "duration_s": rows[-1]["t"] - rows[0]["t"] if len(rows) >= 2 else 0.0,
                "truth_samples": len(rows),
                "local_pose_samples": len(self.local_rows),
                "lidar_samples": len(self.lidar_rows),
                "lidar_last_width": self.lidar_rows[-1]["width"] if self.lidar_rows else None,
                "lidar_last_height": self.lidar_rows[-1]["height"] if self.lidar_rows else None,
                "lidar_last_point_count": self.lidar_rows[-1]["point_count"] if self.lidar_rows else None,
                "lidar_last_data_len": self.lidar_rows[-1]["data_len"] if self.lidar_rows else None,
                "lidar_last_fields": self.lidar_rows[-1]["fields"] if self.lidar_rows else None,
                "accumulated_cloud_topic": self.args.accumulated_cloud_topic,
                "accumulated_cloud_messages": self.accumulated_cloud_messages,
                "accumulated_cloud_points": self.accumulated_cloud_last_point_count,
                "max_z_m": max_z,
                "final_position_m": {"x": final["x"], "y": final["y"], "z": final["z"]},
                "max_airborne_tilt_rad": max_tilt,
                "hover_xy_rmse_m": self.rmse(hover_xy),
                "hover_max_xy_m": max(hover_xy) if hover_xy else None,
                "hover_z_rmse_m": self.rmse(hover_z),
                "hover_max_abs_z_error_m": max(hover_z) if hover_z else None,
                "steady_hover_eval_tail_s": self.args.steady_hover_eval_tail_s,
                "steady_hover_samples": len(steady_hover),
                "steady_hover_xy_rmse_m": self.rmse(steady_hover_xy),
                "steady_hover_max_xy_m": max(steady_hover_xy) if steady_hover_xy else None,
                "steady_hover_z_rmse_m": self.rmse(steady_hover_z),
                "steady_hover_max_abs_z_error_m": max(steady_hover_z) if steady_hover_z else None,
                "steady_hover_setpoint_m": {"x": sp_x, "y": sp_y, "z": sp_z},
                "steady_hover_vs_setpoint_xy_rmse_m": self.rmse(steady_hover_sp_xy),
                "steady_hover_vs_setpoint_max_xy_m": max(steady_hover_sp_xy) if steady_hover_sp_xy else None,
                "steady_hover_vs_setpoint_z_rmse_m": self.rmse(steady_hover_sp_z),
                "steady_hover_vs_setpoint_max_abs_z_error_m": max(steady_hover_sp_z) if steady_hover_sp_z else None,
                "mission_home_m": {"x": home_x, "y": home_y, "z": self.home_z},
                "control_home_m": (
                    {"x": self.control_home_xy[0], "y": self.control_home_xy[1], "z": self.control_home_z}
                    if self.control_home_xy is not None
                    else None
                ),
                "command_offset_m": {
                    "x": self.args.command_offset_x_m,
                    "y": self.args.command_offset_y_m,
                    "z": self.args.command_offset_z_m,
                },
                "adaptive_command_offset_m": {
                    "x": self.adaptive_command_offset[0],
                    "y": self.adaptive_command_offset[1],
                    "z": self.adaptive_command_offset[2],
                },
                "landed_xy_span_m": landed_xy_span,
                "landed_yaw_delta_rad": landed_yaw_delta,
            }
            if max_z < self.args.min_takeoff_peak_z_m:
                blockers.append(f"takeoff_peak_z_below_min:{max_z:.3f}")
            if metrics["steady_hover_z_rmse_m"] is not None and metrics["steady_hover_z_rmse_m"] > self.args.max_hover_z_rmse_m:
                blockers.append(f"steady_hover_z_rmse_above_max:{metrics['steady_hover_z_rmse_m']:.3f}")
            if metrics["steady_hover_max_abs_z_error_m"] is not None and metrics["steady_hover_max_abs_z_error_m"] > self.args.max_hover_z_error_m:
                blockers.append(f"steady_hover_z_error_above_max:{metrics['steady_hover_max_abs_z_error_m']:.3f}")
            if metrics["steady_hover_xy_rmse_m"] is not None and metrics["steady_hover_xy_rmse_m"] > self.args.max_hover_xy_rmse_m:
                blockers.append(f"steady_hover_xy_rmse_above_max:{metrics['steady_hover_xy_rmse_m']:.3f}")
            if metrics["steady_hover_max_xy_m"] is not None and metrics["steady_hover_max_xy_m"] > self.args.max_hover_xy_m:
                blockers.append(f"steady_hover_xy_above_max:{metrics['steady_hover_max_xy_m']:.3f}")
            if final["z"] > self.args.max_final_z_m:
                blockers.append(f"final_z_above_max:{final['z']:.3f}")
            if landed_xy_span is not None and landed_xy_span > self.args.max_landed_xy_span_m:
                blockers.append(f"landed_xy_slide_above_max:{landed_xy_span:.3f}")
            if self.args.require_nonempty_lidar:
                nonempty_lidar = [
                    r for r in self.lidar_rows
                    if int(r.get("data_len", 0)) > 0 and int(r.get("point_count", 0)) > 0
                ]
                metrics["lidar_nonempty_samples"] = len(nonempty_lidar)
                if not nonempty_lidar:
                    blockers.append("lidar_pointcloud_empty")
            if self.args.require_accumulated_cloud and self.accumulated_cloud_last_point_count <= 0:
                blockers.append("accumulated_cloud_empty")

        figure8_metrics = self.evaluate_figure8()
        if figure8_metrics:
            metrics["figure8"] = figure8_metrics
            if figure8_metrics.get("rmse_xy_m") is not None and figure8_metrics["rmse_xy_m"] > self.args.max_figure8_rmse_xy_m:
                blockers.append(f"figure8_rmse_xy_above_max:{figure8_metrics['rmse_xy_m']:.3f}")
            if figure8_metrics.get("p95_xy_error_m") is not None and figure8_metrics["p95_xy_error_m"] > self.args.max_figure8_p95_xy_error_m:
                blockers.append(f"figure8_p95_xy_error_above_max:{figure8_metrics['p95_xy_error_m']:.3f}")
            if figure8_metrics.get("max_xy_error_m") is not None and figure8_metrics["max_xy_error_m"] > self.args.max_figure8_max_xy_error_m:
                blockers.append(f"figure8_max_xy_error_above_max:{figure8_metrics['max_xy_error_m']:.3f}")
            if figure8_metrics.get("time_sync_rmse_xy_m") is not None and figure8_metrics["time_sync_rmse_xy_m"] > self.args.max_figure8_time_sync_rmse_xy_m:
                blockers.append(f"figure8_time_sync_rmse_xy_above_max:{figure8_metrics['time_sync_rmse_xy_m']:.3f}")
            if figure8_metrics.get("time_sync_p95_xy_error_m") is not None and figure8_metrics["time_sync_p95_xy_error_m"] > self.args.max_figure8_time_sync_p95_xy_error_m:
                blockers.append(f"figure8_time_sync_p95_xy_error_above_max:{figure8_metrics['time_sync_p95_xy_error_m']:.3f}")
            if figure8_metrics.get("time_sync_max_xy_error_m") is not None and figure8_metrics["time_sync_max_xy_error_m"] > self.args.max_figure8_time_sync_max_xy_error_m:
                blockers.append(f"figure8_time_sync_max_xy_error_above_max:{figure8_metrics['time_sync_max_xy_error_m']:.3f}")
            if figure8_metrics.get("center_crossings") is not None and figure8_metrics["center_crossings"] < 2:
                blockers.append(f"figure8_center_crossings_below_min:{figure8_metrics['center_crossings']}")

        spiral_metrics = self.evaluate_named_trajectory("spiral_climb", self.spiral_error_rows)
        if spiral_metrics:
            metrics["spiral_climb"] = spiral_metrics
            if spiral_metrics.get("time_sync_rmse_xyz_m") is not None and spiral_metrics["time_sync_rmse_xyz_m"] > self.args.max_spiral_rmse_xyz_m:
                blockers.append(f"spiral_rmse_xyz_above_max:{spiral_metrics['time_sync_rmse_xyz_m']:.3f}")
            if spiral_metrics.get("time_sync_p95_xyz_error_m") is not None and spiral_metrics["time_sync_p95_xyz_error_m"] > self.args.max_spiral_p95_xyz_error_m:
                blockers.append(f"spiral_p95_xyz_error_above_max:{spiral_metrics['time_sync_p95_xyz_error_m']:.3f}")
            if spiral_metrics.get("time_sync_max_xyz_error_m") is not None and spiral_metrics["time_sync_max_xyz_error_m"] > self.args.max_spiral_max_xyz_error_m:
                blockers.append(f"spiral_max_xyz_error_above_max:{spiral_metrics['time_sync_max_xyz_error_m']:.3f}")

        payload = {
            "schema": "mosim.sunray_ros1_native_mission_gate.v1",
            "status": "passed" if not blockers else "blocked",
            "mission": self.args.mission,
            "control_interface": f"{self.uav_ns}/sunray/uav_control_cmd",
            "control_backend": "Sunray native control node -> PX4 SITL -> Gazebo Classic plant",
            "command_modes": {
                "position_hold_mode": self.args.position_hold_mode,
                "figure8_control_mode": self.args.control_mode,
            },
            "acceptance_thresholds": {
                "hover_xy_rmse_m": self.args.max_hover_xy_rmse_m,
                "hover_xy_max_m": self.args.max_hover_xy_m,
                "hover_z_rmse_m": self.args.max_hover_z_rmse_m,
                "hover_z_max_m": self.args.max_hover_z_error_m,
                "hover_gate_uses": "steady_hover_tail",
                "steady_hover_eval_tail_s": self.args.steady_hover_eval_tail_s,
                "figure8_xy_rmse_m": self.args.max_figure8_rmse_xy_m,
                "figure8_xy_p95_m": self.args.max_figure8_p95_xy_error_m,
                "figure8_xy_max_m": self.args.max_figure8_max_xy_error_m,
                "spiral_xyz_rmse_m": self.args.max_spiral_rmse_xyz_m,
                "spiral_xyz_p95_m": self.args.max_spiral_p95_xyz_error_m,
                "spiral_xyz_max_m": self.args.max_spiral_max_xyz_error_m,
            },
            "control_feedback_source": {
                "current_default": "Sunray uav_control consumes /uav1/sunray/px4_state from external_fusion_node.",
                "px4_state_fields": "external_fusion_node fills position/velocity/attitude from MAVROS local_position/velocity_local/imu topics.",
                "flight_controller_imu": "/imu -> PX4 SITL estimator -> /uav1/mavros/imu/data",
                "mid360_imu": "/uav1/livox/imu",
                "fastlio_feedback_into_control": (
                    "requires external_fusion/PX4 fusion proof; FAST-LIO running alone is localization/review evidence only"
                ),
                "external_fusion_source": self.args.external_fusion_source,
                "external_fusion_position_topic": self.args.external_fusion_position_topic,
                "external_fusion_use_vision_pose": self.args.external_fusion_use_vision_pose,
                "fastlio_enabled": self.args.fastlio_enabled,
            },
            "result_dir": str(self.result_dir),
            "metrics": metrics,
            "blockers": blockers,
            "artifacts": {
                "truth_jsonl": str(self.result_dir / "gazebo_truth_uav1.jsonl"),
                "truth_csv": str(self.result_dir / "gazebo_truth_uav1.csv"),
                "uav_state_jsonl": str(self.result_dir / "sunray_uav_state.jsonl"),
                "reference_jsonl": str(self.result_dir / "reference_trajectory.jsonl"),
                "reference_csv": str(self.result_dir / "reference_trajectory.csv"),
                "figure8_time_sync_errors_jsonl": str(self.result_dir / "figure8_time_sync_errors.jsonl"),
                "spiral_time_sync_errors_jsonl": str(self.result_dir / "spiral_time_sync_errors.jsonl"),
                "lidar_jsonl": str(self.result_dir / "livox_lidar_samples.jsonl"),
            },
            "claim_boundary": [
                "This is a ROS1/Sunray native-command Gazebo Classic mission gate using the assembled Sunray150+MID360 model.",
                "Unless external_fusion/PX4 fusion of FAST-LIO odometry is separately proven, controller feedback is PX4/MAVROS state, not MID360/FAST-LIO state.",
                "It does not prove MWORKS generated C/C++ deployment or multi-UAV readiness.",
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return payload

    def evaluate_figure8(self) -> dict:
        if not self.reference_rows:
            return {}
        fig_truth = [r for r in self.truth_rows if r["phase"] == "figure8"]
        refs = self.reference_rows
        if not fig_truth:
            return {"sample_count": 0}
        errors = []
        self.figure8_error_rows = []
        ref_idx = 0
        for row in fig_truth:
            while ref_idx + 1 < len(refs) and refs[ref_idx + 1]["t"] <= row["t"]:
                ref_idx += 1
            ref, ref_dt = self.interpolate_reference_at(refs, row["t"], ref_idx)
            ex = row["x"] - ref["x"]
            ey = row["y"] - ref["y"]
            ez = row["z"] - ref["z"]
            e_xy = math.hypot(ex, ey)
            errors.append(e_xy)
            self.figure8_error_rows.append(
                {
                    "t": row["t"],
                    "truth_x": row["x"],
                    "truth_y": row["y"],
                    "truth_z": row["z"],
                    "ref_x": ref["x"],
                    "ref_y": ref["y"],
                    "ref_z": ref["z"],
                    "error_x_m": ex,
                    "error_y_m": ey,
                    "error_z_m": ez,
                    "error_xy_m": e_xy,
                    "ref_time_delta_s": ref_dt,
                    "reference_interpolation": "linear_time",
                }
            )
        ref_stride = max(1, len(refs) // 240)
        ref_for_distance = refs[::ref_stride]
        nearest_path_errors = [
            min(math.hypot(row["x"] - ref["x"], row["y"] - ref["y"]) for ref in ref_for_distance)
            for row in fig_truth
        ]
        xs = [r["x"] for r in fig_truth]
        ys = [r["y"] for r in fig_truth]
        cx = refs[0]["x"]
        center_crossings = 0
        prev = None
        for r in fig_truth:
            val = r["x"] - cx
            if prev is not None and prev * val < 0:
                center_crossings += 1
            if abs(val) > 0.03:
                prev = val
        return {
            "sample_count": len(fig_truth),
            "reference_samples": len(refs),
            "time_sync_rmse_xy_m": self.rmse(errors),
            "time_sync_max_xy_error_m": max(errors) if errors else None,
            "time_sync_p95_xy_error_m": self.percentile(errors, 95.0),
            "time_sync_p99_xy_error_m": self.percentile(errors, 99.0),
            "rmse_xy_m": self.rmse(nearest_path_errors),
            "max_xy_error_m": max(nearest_path_errors) if nearest_path_errors else None,
            "p95_xy_error_m": self.percentile(nearest_path_errors, 95.0),
            "p99_xy_error_m": self.percentile(nearest_path_errors, 99.0),
            "span_x_m": max(xs) - min(xs),
            "span_y_m": max(ys) - min(ys),
            "center_crossings": center_crossings,
            "metric_note": "rmse_xy_m/max_xy_error_m are nearest-reference-path shape errors; time_sync_* uses linear interpolation of the sampled reference trajectory at each truth timestamp.",
        }

    def evaluate_named_trajectory(self, phase: str, error_sink: list[dict]) -> dict:
        refs = [r for r in self.reference_rows if r.get("phase") == phase]
        truth = [r for r in self.truth_rows if r.get("phase") == phase]
        if not refs:
            return {}
        if not truth:
            return {"sample_count": 0, "reference_samples": len(refs)}
        error_sink.clear()
        xy_errors = []
        z_errors = []
        xyz_errors = []
        ref_idx = 0
        for row in truth:
            while ref_idx + 1 < len(refs) and refs[ref_idx + 1]["t"] <= row["t"]:
                ref_idx += 1
            ref, ref_dt = self.interpolate_reference_at(refs, row["t"], ref_idx)
            ex = row["x"] - ref["x"]
            ey = row["y"] - ref["y"]
            ez = row["z"] - ref["z"]
            e_xy = math.hypot(ex, ey)
            e_xyz = math.sqrt(ex * ex + ey * ey + ez * ez)
            xy_errors.append(e_xy)
            z_errors.append(abs(ez))
            xyz_errors.append(e_xyz)
            error_sink.append(
                {
                    "t": row["t"],
                    "truth_x": row["x"],
                    "truth_y": row["y"],
                    "truth_z": row["z"],
                    "ref_x": ref["x"],
                    "ref_y": ref["y"],
                    "ref_z": ref["z"],
                    "error_x_m": ex,
                    "error_y_m": ey,
                    "error_z_m": ez,
                    "error_xy_m": e_xy,
                    "error_xyz_m": e_xyz,
                    "ref_time_delta_s": ref_dt,
                    "reference_interpolation": "linear_time",
                }
            )
        xs = [r["x"] for r in truth]
        ys = [r["y"] for r in truth]
        zs = [r["z"] for r in truth]
        return {
            "sample_count": len(truth),
            "reference_samples": len(refs),
            "time_sync_rmse_xy_m": self.rmse(xy_errors),
            "time_sync_p95_xy_error_m": self.percentile(xy_errors, 95.0),
            "time_sync_max_xy_error_m": max(xy_errors) if xy_errors else None,
            "time_sync_rmse_z_m": self.rmse(z_errors),
            "time_sync_p95_z_error_m": self.percentile(z_errors, 95.0),
            "time_sync_max_z_error_m": max(z_errors) if z_errors else None,
            "time_sync_rmse_xyz_m": self.rmse(xyz_errors),
            "time_sync_p95_xyz_error_m": self.percentile(xyz_errors, 95.0),
            "time_sync_p99_xyz_error_m": self.percentile(xyz_errors, 99.0),
            "time_sync_max_xyz_error_m": max(xyz_errors) if xyz_errors else None,
            "span_x_m": max(xs) - min(xs),
            "span_y_m": max(ys) - min(ys),
            "span_z_m": max(zs) - min(zs),
            "metric_note": "Spiral metrics are strict time-synchronized XYZ tracking errors against the commanded helix using linear interpolation of sampled reference rows.",
        }

    @staticmethod
    def interpolate_reference_at(refs: list[dict], t: float, lower_idx: int) -> tuple[dict, float]:
        if not refs:
            return {}, 0.0
        if lower_idx < 0:
            lower_idx = 0
        if lower_idx >= len(refs) - 1:
            ref = refs[-1]
            return ref, float(t) - float(ref["t"])
        lo = refs[lower_idx]
        hi = refs[lower_idx + 1]
        lo_t = float(lo["t"])
        hi_t = float(hi["t"])
        if hi_t <= lo_t:
            return lo, float(t) - lo_t
        alpha = max(0.0, min(1.0, (float(t) - lo_t) / (hi_t - lo_t)))
        out = dict(lo)
        for key in ("x", "y", "z", "vx", "vy", "vz", "ax", "ay", "az", "local_x", "local_y"):
            if key in lo and key in hi:
                out[key] = float(lo[key]) + alpha * (float(hi[key]) - float(lo[key]))
        out["t"] = float(t)
        return out, min(abs(float(t) - lo_t), abs(hi_t - float(t)))

    @staticmethod
    def percentile(values: list[float], pct: float) -> float | None:
        if not values:
            return None
        ordered = sorted(values)
        idx = int(max(0, min(len(ordered) - 1, round((pct / 100.0) * (len(ordered) - 1)))))
        return ordered[idx]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--mission", choices=["takeoff_hover_land", "figure8", "spiral_climb"], default="takeoff_hover_land")
    parser.add_argument("--uav-id", type=int, default=1)
    parser.add_argument("--uav-name", default="uav")
    parser.add_argument("--truth-model-name", default="uav1")
    parser.add_argument("--path-frame", default="map")
    parser.add_argument("--altitude-m", type=float, default=1.0)
    parser.add_argument("--command-offset-x-m", type=float, default=0.0)
    parser.add_argument("--command-offset-y-m", type=float, default=0.0)
    parser.add_argument("--command-offset-z-m", type=float, default=0.0)
    parser.add_argument("--initial-hover-s", type=float, default=6.0)
    parser.add_argument("--enable-hover-bias-calibration", action="store_true")
    parser.add_argument("--hover-bias-calibration-settle-s", type=float, default=8.0)
    parser.add_argument("--hover-bias-calibration-tail-s", type=float, default=4.0)
    parser.add_argument("--hover-bias-calibration-verify-s", type=float, default=3.0)
    parser.add_argument("--hover-bias-calibration-gain", type=float, default=0.6)
    parser.add_argument("--hover-bias-calibration-max-step-m", type=float, default=0.04)
    parser.add_argument("--hover-bias-calibration-axes", choices=["x", "y", "z", "xy", "xz", "yz", "xyz"], default="xyz")
    parser.add_argument("--pre-figure8-hold-s", type=float, default=2.0)
    parser.add_argument("--post-figure8-hold-s", type=float, default=2.0)
    parser.add_argument("--final-settle-s", type=float, default=5.0)
    parser.add_argument("--review-hold-s", type=float, default=0.0)
    parser.add_argument("--steady-hover-eval-tail-s", type=float, default=8.0)
    parser.add_argument("--figure8-laps", type=float, default=2.0)
    parser.add_argument("--figure8-period-s", type=float, default=16.0)
    parser.add_argument("--figure8-amp-x-m", type=float, default=1.2)
    parser.add_argument("--figure8-amp-y-m", type=float, default=0.7)
    parser.add_argument("--figure8-speed-ramp-s", type=float, default=0.0)
    parser.add_argument("--pre-spiral-hold-s", type=float, default=2.0)
    parser.add_argument("--post-spiral-hold-s", type=float, default=2.0)
    parser.add_argument("--spiral-turns", type=float, default=2.0)
    parser.add_argument("--spiral-period-s", type=float, default=18.0)
    parser.add_argument("--spiral-radius-m", type=float, default=0.6)
    parser.add_argument("--spiral-height-m", type=float, default=0.6)
    parser.add_argument("--spiral-z-profile", choices=["linear", "smoothstep", "theta_ramp"], default="linear")
    parser.add_argument("--spiral-entry-s", type=float, default=6.0)
    parser.add_argument("--spiral-entry-settle-s", type=float, default=1.0)
    parser.add_argument("--spiral-speed-ramp-s", type=float, default=0.0)
    parser.add_argument("--command-rate-hz", type=float, default=20.0)
    parser.add_argument("--trajectory-time-lead-s", type=float, default=0.0)
    parser.add_argument("--trajectory-z-time-lead-s", type=float, default=None)
    parser.add_argument("--control-mode", choices=["xyvelzpos", "xyzpos", "posvel", "ctrltraj"], default="ctrltraj")
    parser.add_argument("--position-hold-mode", choices=["ctrlxyzpos", "px4xyzpos"], default="ctrlxyzpos")
    parser.add_argument("--kp-xy", type=float, default=0.9)
    parser.add_argument("--max-xy-vel-mps", type=float, default=1.2)
    parser.add_argument("--connect-timeout-s", type=float, default=45.0)
    parser.add_argument("--mode-timeout-s", type=float, default=25.0)
    parser.add_argument("--arm-timeout-s", type=float, default=25.0)
    parser.add_argument("--takeoff-timeout-s", type=float, default=35.0)
    parser.add_argument("--land-timeout-s", type=float, default=35.0)
    parser.add_argument("--takeoff-z-tolerance-m", type=float, default=0.22)
    parser.add_argument("--takeoff-max-abs-vz-mps", type=float, default=0.08)
    parser.add_argument("--takeoff-stable-s", type=float, default=1.0)
    parser.add_argument("--takeoff-airborne-z-m", type=float, default=0.25)
    parser.add_argument("--max-laned-state-z-m", dest="max_landed_state_z_m", type=float, default=0.4)
    parser.add_argument("--min-takeoff-peak-z-m", type=float, default=0.75)
    parser.add_argument("--max-hover-z-error-m", type=float, default=0.05)
    parser.add_argument("--max-hover-z-rmse-m", type=float, default=0.02)
    parser.add_argument("--max-hover-xy-m", type=float, default=0.05)
    parser.add_argument("--max-hover-xy-rmse-m", type=float, default=0.02)
    parser.add_argument("--max-final-z-m", type=float, default=0.35)
    parser.add_argument("--max-landed-xy-span-m", type=float, default=0.20)
    parser.add_argument("--max-figure8-rmse-xy-m", type=float, default=0.05)
    parser.add_argument("--max-figure8-p95-xy-error-m", type=float, default=0.05)
    parser.add_argument("--max-figure8-max-xy-error-m", type=float, default=0.05)
    parser.add_argument("--max-figure8-time-sync-rmse-xy-m", type=float, default=0.05)
    parser.add_argument("--max-figure8-time-sync-p95-xy-error-m", type=float, default=0.05)
    parser.add_argument("--max-figure8-time-sync-max-xy-error-m", type=float, default=0.05)
    parser.add_argument("--max-spiral-rmse-xyz-m", type=float, default=0.05)
    parser.add_argument("--max-spiral-p95-xyz-error-m", type=float, default=0.05)
    parser.add_argument("--max-spiral-max-xyz-error-m", type=float, default=0.05)
    parser.add_argument("--require-nonempty-lidar", action="store_true")
    parser.add_argument("--require-accumulated-cloud", action="store_true")
    parser.add_argument("--external-fusion-source", default="2")
    parser.add_argument("--external-fusion-position-topic", default="/uav1/mavros/local_position/pose")
    parser.add_argument("--external-fusion-use-vision-pose", default="true")
    parser.add_argument("--fastlio-enabled", default="false")
    parser.add_argument("--path-sample-rate-hz", type=float, default=20.0)
    parser.add_argument("--path-publish-rate-hz", type=float, default=5.0)
    parser.add_argument(
        "--max-path-points",
        type=int,
        default=0,
        help="Maximum poses retained in published RViz paths. 0 keeps the full mission path for review.",
    )
    parser.add_argument("--publish-accumulated-cloud", dest="publish_accumulated_cloud", action="store_true", default=True)
    parser.add_argument("--no-publish-accumulated-cloud", dest="publish_accumulated_cloud", action="store_false")
    parser.add_argument("--accumulated-cloud-topic", default="/mosim/sunray/lidar_points_map_accumulated")
    parser.add_argument("--accumulated-cloud-max-points", type=int, default=300000)
    parser.add_argument("--accumulated-cloud-point-stride", type=int, default=2)
    parser.add_argument("--accumulated-cloud-publish-rate-hz", type=float, default=2.0)
    parser.add_argument("--accumulated-cloud-min-z-m", type=float, default=-2.0)
    parser.add_argument("--accumulated-cloud-max-z-m", type=float, default=8.0)
    parser.add_argument("--accumulated-cloud-color-min-z-m", type=float, default=0.0)
    parser.add_argument("--accumulated-cloud-color-max-z-m", type=float, default=4.0)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    rospy.init_node("mosim_sunray_ros1_native_mission_node", anonymous=True)

    def handle_sigint(_sig, _frame):
        rospy.signal_shutdown("SIGINT")
        sys.exit(130)

    signal.signal(signal.SIGINT, handle_sigint)
    node = MissionNode(args)
    try:
        payload = node.run()
        return 0 if payload.get("status") == "passed" else 2
    except Exception as exc:
        node.write_outputs()
        payload = {
            "schema": "mosim.sunray_ros1_native_mission_gate.v1",
            "status": "blocked",
            "mission": args.mission,
            "reason": str(exc),
            "result_dir": str(node.result_dir),
            "control_feedback_source": {
                "current_default": "Sunray uav_control consumes /uav1/sunray/px4_state from external_fusion_node.",
                "px4_state_fields": "external_fusion_node fills position/velocity/attitude from MAVROS local_position/velocity_local/imu topics.",
                "flight_controller_imu": "/imu -> PX4 SITL estimator -> /uav1/mavros/imu/data",
                "mid360_imu": "/uav1/livox/imu",
                "external_fusion_source": args.external_fusion_source,
                "external_fusion_position_topic": args.external_fusion_position_topic,
                "external_fusion_use_vision_pose": args.external_fusion_use_vision_pose,
                "fastlio_enabled": args.fastlio_enabled,
            },
            "truth_samples": len(node.truth_rows),
            "local_pose_samples": len(node.local_rows),
            "lidar_samples": len(node.lidar_rows),
        }
        (node.result_dir / "SUNRAY_ROS1_NATIVE_MISSION_GATE.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
