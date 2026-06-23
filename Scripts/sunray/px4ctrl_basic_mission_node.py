#!/usr/bin/env python3
"""Run basic missions through Fast-Drone-250 px4ctrl and record metrics."""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import time
from pathlib import Path

import rospy
import tf2_ros
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import Point, PoseStamped, TransformStamped
from mavros_msgs.msg import AttitudeTarget, State
from mavros_msgs.srv import CommandBool
from nav_msgs.msg import Odometry, Path as RosPath
from quadrotor_msgs.msg import PositionCommand, Px4ctrlDebug, TakeoffLand
from sensor_msgs.msg import Imu
from std_msgs.msg import Header
from visualization_msgs.msg import Marker, MarkerArray


TRAJECTORY_MISSIONS = {"figure8", "spiral", "circle", "step_x", "step_y", "step_z"}


class Px4ctrlBasicMission:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.result_dir = Path(args.result_dir)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.start_wall = time.time()
        self.phase = "init"
        self.truth_rows: list[dict] = []
        self.sunray_truth_rows: list[dict] = []
        self.local_rows: list[dict] = []
        self.control_odom_rows: list[dict] = []
        self.ref_rows: list[dict] = []
        self.debug_rows: list[dict] = []
        self.att_target_rows: list[dict] = []
        self.state_rows: list[dict] = []
        self.home: tuple[float, float, float] | None = None
        self.last_truth: dict | None = None
        self.last_sunray_truth: dict | None = None
        self.last_local: dict | None = None
        self.last_control_odom: dict | None = None
        self.last_debug: dict | None = None
        self.last_state: State | None = None
        self.control_home: tuple[float, float, float] | None = None
        self.last_record_t = {
            "truth": -1e9,
            "sunray_truth": -1e9,
            "local": -1e9,
            "control_odom": -1e9,
            "debug": -1e9,
            "att_target": -1e9,
            "state": -1e9,
        }

        self.takeoff_land_pub = rospy.Publisher("/px4ctrl/takeoff_land", TakeoffLand, queue_size=3, latch=True)
        self.cmd_pub = rospy.Publisher("/position_cmd", PositionCommand, queue_size=10)
        self.ref_path_pub = rospy.Publisher("/mosim/px4ctrl/reference_path", RosPath, queue_size=1, latch=True)
        self.truth_path_pub = rospy.Publisher("/mosim/px4ctrl/truth_path", RosPath, queue_size=1, latch=True)
        self.truth_axes_pub = rospy.Publisher("/mosim/px4ctrl/body_axes", MarkerArray, queue_size=1)
        self.reference_path = RosPath(header=Header(frame_id=args.path_frame))
        self.truth_path = RosPath(header=Header(frame_id=args.path_frame))
        self.last_truth_path_publish_t = -1e9
        self.tf_broadcaster = tf2_ros.TransformBroadcaster()
        self.disarm_attempts = 0
        self.disarm_success = False

        rospy.Subscriber("/gazebo/model_states", ModelStates, self.on_model_states, queue_size=50)
        rospy.Subscriber(args.sunray_truth_topic, Odometry, self.on_sunray_truth, queue_size=100)
        rospy.Subscriber("/uav1/mavros/local_position/odom", Odometry, self.on_local_odom, queue_size=100)
        rospy.Subscriber(args.control_odom_topic, Odometry, self.on_control_odom, queue_size=100)
        rospy.Subscriber("/uav1/mavros/state", State, self.on_state, queue_size=20)
        rospy.Subscriber("/uav1/mavros/setpoint_raw/target_attitude", AttitudeTarget, self.on_att_target, queue_size=100)
        rospy.Subscriber("/debugPx4ctrl", Px4ctrlDebug, self.on_debug, queue_size=100)
        rospy.Subscriber("/uav1/mavros/imu/data", Imu, self.on_imu, queue_size=20)

    def now(self) -> float:
        stamp = rospy.Time.now().to_sec()
        return float(stamp) if stamp > 0 else time.time() - self.start_wall

    def wall_elapsed(self) -> float:
        return time.time() - self.start_wall

    def deadline_reached(self) -> bool:
        return self.args.wall_timeout_s > 0 and self.wall_elapsed() > self.args.wall_timeout_s

    def should_record(self, key: str, t: float, hz: float) -> bool:
        if hz <= 0:
            return True
        if t - self.last_record_t[key] < 1.0 / hz:
            return False
        self.last_record_t[key] = t
        return True

    @staticmethod
    def yaw_from_quat(x: float, y: float, z: float, w: float) -> float:
        return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))

    @staticmethod
    def rpy_from_quat(x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
        roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
        pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
        yaw = Px4ctrlBasicMission.yaw_from_quat(x, y, z, w)
        return roll, pitch, yaw

    def on_state(self, msg: State) -> None:
        self.last_state = msg
        t = self.now()
        if not self.should_record("state", t, self.args.record_state_hz):
            return
        self.state_rows.append(
            {
                "t": t,
                "phase": self.phase,
                "connected": bool(msg.connected),
                "armed": bool(msg.armed),
                "guided": bool(msg.guided),
                "mode": msg.mode,
            }
        )

    def on_model_states(self, msg: ModelStates) -> None:
        try:
            idx = list(msg.name).index(self.args.truth_model_name)
        except ValueError:
            return
        pose = msg.pose[idx]
        twist = msg.twist[idx]
        q = pose.orientation
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        t = self.now()
        row = {
            "t": t,
            "phase": self.phase,
            "x": float(pose.position.x),
            "y": float(pose.position.y),
            "z": float(pose.position.z),
            "vx": float(twist.linear.x),
            "vy": float(twist.linear.y),
            "vz": float(twist.linear.z),
            "roll": roll,
            "pitch": pitch,
            "yaw": yaw,
        }
        self.last_truth = row
        self.publish_truth_tf(pose)
        self.publish_truth_axes(pose)
        if self.should_record("truth", t, self.args.record_truth_hz):
            self.truth_rows.append(row)
            self.append_truth_path(row)
        if self.home is None and len(self.truth_rows) > 5:
            self.home = (row["x"], row["y"], row["z"])

    def on_sunray_truth(self, msg: Odometry) -> None:
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        v = msg.twist.twist.linear
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        t = self.now()
        row = {
            "t": t,
            "phase": self.phase,
            "x": float(p.x),
            "y": float(p.y),
            "z": float(p.z),
            "vx": float(v.x),
            "vy": float(v.y),
            "vz": float(v.z),
            "roll": roll,
            "pitch": pitch,
            "yaw": yaw,
        }
        self.last_sunray_truth = row
        if self.should_record("sunray_truth", t, self.args.record_truth_hz):
            self.sunray_truth_rows.append(row)

    def on_local_odom(self, msg: Odometry) -> None:
        row = self.odom_msg_to_row(msg)
        self.last_local = row
        if self.should_record("local", row["t"], self.args.record_odom_hz):
            self.local_rows.append(row)

    def on_control_odom(self, msg: Odometry) -> None:
        row = self.odom_msg_to_row(msg)
        self.last_control_odom = row
        if self.should_record("control_odom", row["t"], self.args.record_odom_hz):
            self.control_odom_rows.append(row)

    def odom_msg_to_row(self, msg: Odometry) -> dict:
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        v = msg.twist.twist.linear
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        t = self.now()
        return {
            "t": t,
            "phase": self.phase,
            "x": float(p.x),
            "y": float(p.y),
            "z": float(p.z),
            "vx": float(v.x),
            "vy": float(v.y),
            "vz": float(v.z),
            "roll": roll,
            "pitch": pitch,
            "yaw": yaw,
        }

    def on_att_target(self, msg: AttitudeTarget) -> None:
        q = msg.orientation
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        t = self.now()
        if not self.should_record("att_target", t, self.args.record_attitude_hz):
            return
        self.att_target_rows.append(
            {
                "t": t,
                "phase": self.phase,
                "type_mask": int(msg.type_mask),
                "roll": roll,
                "pitch": pitch,
                "yaw": yaw,
                "body_rate_x": float(msg.body_rate.x),
                "body_rate_y": float(msg.body_rate.y),
                "body_rate_z": float(msg.body_rate.z),
                "thrust": float(msg.thrust),
            }
        )

    def on_debug(self, msg: Px4ctrlDebug) -> None:
        t = self.now()
        if not self.should_record("debug", t, self.args.record_debug_hz):
            return
        row = {
            "t": t,
            "phase": self.phase,
            "des_v_x": float(msg.des_v_x),
            "des_v_y": float(msg.des_v_y),
            "des_v_z": float(msg.des_v_z),
            "des_a_x": float(msg.des_a_x),
            "des_a_y": float(msg.des_a_y),
            "des_a_z": float(msg.des_a_z),
            "des_q_x": float(msg.des_q_x),
            "des_q_y": float(msg.des_q_y),
            "des_q_z": float(msg.des_q_z),
            "des_q_w": float(msg.des_q_w),
            "des_thr": float(msg.des_thr),
        }
        self.last_debug = row
        self.debug_rows.append(row)

    def on_imu(self, _msg: Imu) -> None:
        return

    def append_truth_path(self, row: dict) -> None:
        if len(self.truth_path.poses) >= self.args.max_path_points:
            return
        if self.truth_path.poses and row["t"] - self.truth_path.poses[-1].header.stamp.to_sec() < 0.05:
            return
        ps = PoseStamped()
        ps.header.stamp = rospy.Time.from_sec(row["t"])
        ps.header.frame_id = self.args.path_frame
        ps.pose.position.x = row["x"]
        ps.pose.position.y = row["y"]
        ps.pose.position.z = row["z"]
        self.truth_path.poses.append(ps)
        self.truth_path.header.stamp = rospy.Time.now()
        self.publish_truth_path_if_due(row["t"])

    def publish_truth_path_if_due(self, t: float, force: bool = False) -> None:
        if not self.truth_path.poses:
            return
        min_period = 1.0 / max(1e-6, self.args.path_publish_hz)
        if not force and t - self.last_truth_path_publish_t < min_period:
            return
        self.last_truth_path_publish_t = t
        self.truth_path.header.stamp = rospy.Time.now()
        self.truth_path_pub.publish(self.truth_path)

    def publish_truth_tf(self, pose) -> None:
        transform = TransformStamped()
        transform.header.stamp = rospy.Time.now()
        transform.header.frame_id = self.args.path_frame
        transform.child_frame_id = self.args.truth_child_frame
        transform.transform.translation.x = pose.position.x
        transform.transform.translation.y = pose.position.y
        transform.transform.translation.z = pose.position.z
        transform.transform.rotation = pose.orientation
        self.tf_broadcaster.sendTransform(transform)

    @staticmethod
    def quat_rotate(q: tuple[float, float, float, float], v: tuple[float, float, float]) -> tuple[float, float, float]:
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

    def publish_truth_axes(self, pose) -> None:
        pos = (float(pose.position.x), float(pose.position.y), float(pose.position.z))
        q_msg = pose.orientation
        q = (float(q_msg.x), float(q_msg.y), float(q_msg.z), float(q_msg.w))
        axes = (
            (0, "body_x_forward", (1.0, 0.0, 0.0), (1.0, 0.05, 0.05, 1.0)),
            (1, "body_y_left", (0.0, 1.0, 0.0), (0.05, 1.0, 0.05, 1.0)),
            (2, "body_z_up", (0.0, 0.0, 1.0), (0.1, 0.35, 1.0, 1.0)),
        )
        markers = MarkerArray()
        stamp = rospy.Time.now()
        for marker_id, name, axis, color in axes:
            direction = self.quat_rotate(q, axis)
            marker = Marker()
            marker.header.stamp = stamp
            marker.header.frame_id = self.args.path_frame
            marker.ns = name
            marker.id = marker_id
            marker.type = Marker.ARROW
            marker.action = Marker.ADD
            start = Point(x=pos[0], y=pos[1], z=pos[2])
            end = Point(
                x=pos[0] + direction[0] * self.args.body_axis_length_m,
                y=pos[1] + direction[1] * self.args.body_axis_length_m,
                z=pos[2] + direction[2] * self.args.body_axis_length_m,
            )
            marker.points = [start, end]
            marker.scale.x = self.args.body_axis_shaft_m
            marker.scale.y = self.args.body_axis_head_diameter_m
            marker.scale.z = self.args.body_axis_head_length_m
            marker.color.r = color[0]
            marker.color.g = color[1]
            marker.color.b = color[2]
            marker.color.a = color[3]
            marker.lifetime = rospy.Duration(self.args.body_axis_lifetime_s)
            markers.markers.append(marker)
        self.truth_axes_pub.publish(markers)

    def publish_takeoff_land(self, cmd: int, repeats: int = 8) -> None:
        msg = TakeoffLand()
        msg.takeoff_land_cmd = cmd
        for _ in range(repeats):
            self.takeoff_land_pub.publish(msg)
            rospy.sleep(0.1)

    def final_z_rel_m(self) -> float | None:
        if self.last_sunray_truth is None or self.home is None:
            return None
        return float(self.last_sunray_truth["z"] - self.home[2])

    def wait_land_and_optionally_disarm(self) -> None:
        end = time.time() + self.args.land_wait_s
        rate = rospy.Rate(10)
        while not rospy.is_shutdown() and time.time() < end:
            if self.last_state is not None and not self.last_state.armed:
                return
            rate.sleep()

        if not self.args.force_disarm_after_land:
            return
        final_z_rel = self.final_z_rel_m()
        if final_z_rel is None or final_z_rel > self.args.force_disarm_max_z_rel_m:
            return
        try:
            rospy.wait_for_service("/uav1/mavros/cmd/arming", timeout=3.0)
            arm_srv = rospy.ServiceProxy("/uav1/mavros/cmd/arming", CommandBool)
        except Exception:
            return

        end = time.time() + self.args.force_disarm_timeout_s
        while not rospy.is_shutdown() and time.time() < end:
            if self.last_state is not None and not self.last_state.armed:
                self.disarm_success = True
                return
            self.disarm_attempts += 1
            try:
                response = arm_srv(False)
                if bool(response.success):
                    self.disarm_success = True
            except Exception:
                pass
            rospy.sleep(1.0)

    def make_position_cmd(self, x: float, y: float, z: float, vx: float, vy: float, vz: float,
                          ax: float, ay: float, az: float, yaw: float, yaw_rate: float = 0.0) -> PositionCommand:
        msg = PositionCommand()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.args.path_frame
        msg.position.x = x
        msg.position.y = y
        msg.position.z = z
        msg.velocity.x = vx
        msg.velocity.y = vy
        msg.velocity.z = vz
        msg.acceleration.x = ax
        msg.acceleration.y = ay
        msg.acceleration.z = az
        msg.jerk.x = 0.0
        msg.jerk.y = 0.0
        msg.jerk.z = 0.0
        msg.yaw = yaw
        msg.yaw_dot = yaw_rate
        msg.trajectory_flag = PositionCommand.TRAJECTORY_STATUS_READY
        return msg

    def reference_at(self, mission_t: float) -> tuple[float, float, float, float, float, float, float, float, float, float]:
        if self.args.reference_frame_source == "control_odom" and self.control_home is not None:
            base_x, base_y, base_z = self.control_home
        elif self.home is None:
            base_x, base_y, base_z = 0.0, 0.0, 0.0
        else:
            base_x, base_y, base_z = self.home
        z0 = base_z + self.args.altitude_m
        if self.args.mission == "figure8":
            w = 2.0 * math.pi / self.args.figure8_period_s
            a = self.args.figure8_x_amp_m
            b = self.args.figure8_y_amp_m
            x = base_x + a * math.sin(w * mission_t)
            y = base_y + b * math.sin(2.0 * w * mission_t)
            vx = a * w * math.cos(w * mission_t)
            vy = 2.0 * b * w * math.cos(2.0 * w * mission_t)
            ax = -a * w * w * math.sin(w * mission_t)
            ay = -4.0 * b * w * w * math.sin(2.0 * w * mission_t)
            return x, y, z0, vx, vy, 0.0, ax, ay, 0.0, 0.0
        if self.args.mission == "spiral":
            w = 2.0 * math.pi / self.args.spiral_period_s
            r = self.args.spiral_radius_m
            z, vz, az = self.spiral_z_reference(mission_t, z0)
            x = base_x + r * math.cos(w * mission_t) - r
            y = base_y + r * math.sin(w * mission_t)
            vx = -r * w * math.sin(w * mission_t)
            vy = r * w * math.cos(w * mission_t)
            ax = -r * w * w * math.cos(w * mission_t)
            ay = -r * w * w * math.sin(w * mission_t)
            return x, y, z, vx, vy, vz, ax, ay, az, 0.0
        if self.args.mission == "circle":
            w = 2.0 * math.pi / self.args.circle_period_s
            r = self.args.circle_radius_m
            x = base_x + r * math.sin(w * mission_t)
            y = base_y + r * (1.0 - math.cos(w * mission_t))
            vx = r * w * math.cos(w * mission_t)
            vy = r * w * math.sin(w * mission_t)
            ax = -r * w * w * math.sin(w * mission_t)
            ay = r * w * w * math.cos(w * mission_t)
            return x, y, z0, vx, vy, 0.0, ax, ay, 0.0, 0.0
        if self.args.mission in {"step_x", "step_y", "step_z"}:
            x, y, z = base_x, base_y, z0
            if self.args.mission == "step_x":
                x += self.args.step_amplitude_m
            elif self.args.mission == "step_y":
                y += self.args.step_amplitude_m
            else:
                z += self.args.step_z_amplitude_m
            return x, y, z, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        return base_x, base_y, z0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    def trajectory_duration_s(self) -> float:
        if self.args.mission == "figure8":
            return self.args.figure8_period_s * self.args.figure8_cycles
        if self.args.mission == "spiral":
            return self.args.spiral_duration_s
        if self.args.mission == "circle":
            return self.args.circle_period_s * self.args.circle_cycles
        if self.args.mission in {"step_x", "step_y", "step_z"}:
            return self.args.step_duration_s
        return 0.0

    def spiral_z_reference(self, mission_t: float, z0: float) -> tuple[float, float, float]:
        duration = max(1e-6, self.args.spiral_duration_s)
        climb = self.args.spiral_climb_m
        if self.args.spiral_z_profile == "linear":
            ratio = min(1.0, max(0.0, mission_t / duration))
            return z0 + climb * ratio, climb / duration, 0.0
        ratio = min(1.0, max(0.0, mission_t / duration))
        smooth = ratio * ratio * (3.0 - 2.0 * ratio)
        ds_dt = 6.0 * ratio * (1.0 - ratio) / duration
        d2s_dt2 = 6.0 * (1.0 - 2.0 * ratio) / (duration * duration)
        return z0 + climb * smooth, climb * ds_dt, climb * d2s_dt2

    def hover_reference(self) -> tuple[float, float, float, float, float, float, float, float, float, float]:
        if self.args.reference_frame_source == "control_odom" and self.control_home is not None:
            base_x, base_y, base_z = self.control_home
        elif self.home is None:
            base_x, base_y, base_z = 0.0, 0.0, 0.0
        else:
            base_x, base_y, base_z = self.home
        return base_x, base_y, base_z + self.args.altitude_m, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    def eval_position_from_command(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        if self.args.reference_frame_source != "control_odom" or self.control_home is None or self.home is None:
            return x, y, z
        return (
            self.home[0] + (x - self.control_home[0]),
            self.home[1] + (y - self.control_home[1]),
            self.home[2] + (z - self.control_home[2]),
        )

    def takeoff_altitude_m(self) -> float:
        if self.args.takeoff_altitude_m > 0.0:
            return self.args.takeoff_altitude_m
        return self.args.altitude_m

    def publish_reference_path(self) -> None:
        if self.home is None:
            return
        path = RosPath(header=Header(frame_id=self.args.path_frame, stamp=rospy.Time.now()))
        duration = self.trajectory_duration_s()
        samples = max(2, int(duration * 20))
        for idx in range(samples + 1):
            t = duration * idx / samples
            x, y, z, *_ = self.reference_at(t)
            eval_x, eval_y, eval_z = self.eval_position_from_command(x, y, z)
            ps = PoseStamped()
            ps.header.stamp = rospy.Time.now()
            ps.header.frame_id = self.args.path_frame
            ps.pose.position.x = eval_x
            ps.pose.position.y = eval_y
            ps.pose.position.z = eval_z
            path.poses.append(ps)
        self.reference_path = path
        self.ref_path_pub.publish(path)

    def wait_for_truth(self, timeout_s: float) -> bool:
        end = time.time() + timeout_s
        rate = rospy.Rate(20)
        while not rospy.is_shutdown() and time.time() < end:
            if self.deadline_reached():
                return False
            if self.last_truth is not None and self.last_sunray_truth is not None and self.home is not None:
                return True
            rate.sleep()
        return False

    def wait_for_static_local_odom(self, timeout_s: float) -> bool:
        end = time.time() + timeout_s
        rate = rospy.Rate(20)
        stable_samples = 0
        while not rospy.is_shutdown() and time.time() < end:
            if self.deadline_reached():
                return False
            odom = self.last_control_odom if self.last_control_odom is not None else self.last_local
            if odom is not None:
                speed = math.sqrt(
                    odom["vx"] * odom["vx"]
                    + odom["vy"] * odom["vy"]
                    + odom["vz"] * odom["vz"]
                )
                if speed <= self.args.static_odom_speed_max_mps:
                    stable_samples += 1
                    if stable_samples >= int(self.args.static_odom_hold_s * 20):
                        return True
                else:
                    stable_samples = 0
            rate.sleep()
        return False

    def takeoff_gate_sample(self) -> tuple[dict | None, float]:
        if (
            self.args.reference_frame_source == "control_odom"
            and self.control_home is not None
            and self.last_control_odom is not None
        ):
            return self.last_control_odom, self.control_home[2] + self.takeoff_altitude_m()
        if self.last_truth is not None and self.home is not None:
            return self.last_truth, self.home[2] + self.takeoff_altitude_m()
        return None, self.takeoff_altitude_m()

    def wait_until_altitude(self, timeout_s: float) -> bool:
        end = time.time() + timeout_s
        rate = rospy.Rate(20)
        while not rospy.is_shutdown() and time.time() < end:
            if self.deadline_reached():
                return False
            sample, target_z = self.takeoff_gate_sample()
            if sample is not None:
                min_z = target_z - self.takeoff_altitude_m() * (1.0 - self.args.takeoff_reached_ratio)
                z_error = abs(sample["z"] - target_z)
                vz_abs = abs(sample.get("vz", 0.0))
                if (
                    sample["z"] >= min_z
                    and z_error <= self.args.takeoff_settle_z_error_max_m
                    and vz_abs <= self.args.takeoff_settle_vz_max_mps
                ):
                    return True
            rate.sleep()
        return False

    def publish_cmd_for_duration(self, duration_s: float) -> None:
        rate = rospy.Rate(self.args.command_rate_hz)
        t0 = self.now()
        self.publish_reference_path()
        while not rospy.is_shutdown():
            if self.deadline_reached():
                break
            mission_t = self.now() - t0
            if mission_t > duration_s:
                break
            x, y, z, vx, vy, vz, ax, ay, az, yaw = self.reference_at(mission_t)
            cmd_t = min(duration_s, max(0.0, mission_t + self.args.trajectory_time_lead_s))
            cmd_x, cmd_y, cmd_z, cmd_vx, cmd_vy, cmd_vz, cmd_ax, cmd_ay, cmd_az, cmd_yaw = self.reference_at(cmd_t)
            biased_cmd_x = cmd_x + self.args.command_x_bias_m
            biased_cmd_y = cmd_y + self.args.command_y_bias_m
            biased_cmd_z = cmd_z + self.args.command_z_bias_m
            msg = self.make_position_cmd(biased_cmd_x, biased_cmd_y, biased_cmd_z, cmd_vx, cmd_vy, cmd_vz, cmd_ax, cmd_ay, cmd_az, cmd_yaw)
            self.cmd_pub.publish(msg)
            eval_x, eval_y, eval_z = self.eval_position_from_command(x, y, z)
            self.ref_rows.append(
                {
                    "t": self.now(),
                    "phase": self.phase,
                    "x": eval_x,
                    "y": eval_y,
                    "z": eval_z,
                    "cmd_x": biased_cmd_x,
                    "cmd_y": biased_cmd_y,
                    "cmd_z": biased_cmd_z,
                    "vx": vx,
                    "vy": vy,
                    "vz": vz,
                    "ax": ax,
                    "ay": ay,
                    "az": az,
                    "yaw": yaw,
                    "cmd_vx": cmd_vx,
                    "cmd_vy": cmd_vy,
                    "cmd_vz": cmd_vz,
                    "cmd_ax": cmd_ax,
                    "cmd_ay": cmd_ay,
                    "cmd_az": cmd_az,
                    "cmd_yaw": cmd_yaw,
                    "trajectory_time_lead_s": self.args.trajectory_time_lead_s,
                }
            )
            rate.sleep()

    def publish_hold_cmd_for_duration(self, duration_s: float) -> None:
        if self.home is None:
            rospy.sleep(duration_s)
            return
        rate = rospy.Rate(self.args.command_rate_hz)
        start_t = self.now()
        end_t = start_t + duration_s
        x, y, z, vx, vy, vz, ax, ay, az, yaw = self.hover_reference()
        biased_x = x + self.args.command_x_bias_m
        biased_y = y + self.args.command_y_bias_m
        ramp_start_z = z
        if self.args.hover_ramp_s > 0.0:
            odom = self.last_control_odom if self.last_control_odom is not None else self.last_local
            if odom is not None:
                ramp_start_z = odom["z"]
        while not rospy.is_shutdown() and self.now() < end_t:
            if self.deadline_reached():
                break
            elapsed = max(0.0, self.now() - start_t)
            if self.args.hover_ramp_s > 0.0:
                ratio = min(1.0, elapsed / self.args.hover_ramp_s)
                smooth = ratio * ratio * (3.0 - 2.0 * ratio)
                cmd_z_unbiased = ramp_start_z + (z - ramp_start_z) * smooth
            else:
                cmd_z_unbiased = z
            biased_z = cmd_z_unbiased + self.args.command_z_bias_m
            msg = self.make_position_cmd(biased_x, biased_y, biased_z, vx, vy, vz, ax, ay, az, yaw)
            self.cmd_pub.publish(msg)
            eval_x, eval_y, eval_z = self.eval_position_from_command(x, y, cmd_z_unbiased)
            self.ref_rows.append(
                {
                    "t": self.now(),
                    "phase": self.phase,
                    "x": eval_x,
                    "y": eval_y,
                    "z": eval_z,
                    "cmd_x": biased_x,
                    "cmd_y": biased_y,
                    "cmd_z": biased_z,
                    "vx": vx,
                    "vy": vy,
                    "vz": vz,
                    "ax": ax,
                    "ay": ay,
                    "az": az,
                    "yaw": yaw,
                    "cmd_vx": vx,
                    "cmd_vy": vy,
                    "cmd_vz": vz,
                    "cmd_ax": ax,
                    "cmd_ay": ay,
                    "cmd_az": az,
                    "cmd_yaw": yaw,
                    "trajectory_time_lead_s": 0.0,
                }
            )
            rate.sleep()

    def run(self) -> dict:
        if not self.wait_for_truth(30.0):
            return {"status": "blocked", "reason": "no_gazebo_truth"}
        assert self.home is not None
        self.phase = "wait_static_odom"
        static_odom_ok = self.wait_for_static_local_odom(self.args.static_odom_timeout_s)
        if self.last_control_odom is not None and self.control_home is None:
            self.control_home = (
                self.last_control_odom["x"],
                self.last_control_odom["y"],
                self.last_control_odom["z"],
            )
        self.phase = "takeoff"
        if static_odom_ok:
            self.publish_takeoff_land(TakeoffLand.TAKEOFF, repeats=self.args.takeoff_cmd_repeats)
        takeoff_ok = self.wait_until_altitude(self.args.takeoff_timeout_s)
        if self.deadline_reached():
            return self.metrics(takeoff_ok, static_odom_ok, forced_reason="wall_timeout_during_takeoff")

        self.phase = "hover_before"
        if self.args.hover_hold_command_mode == "position_cmd":
            self.publish_hold_cmd_for_duration(self.args.initial_hover_s)
        else:
            rospy.sleep(self.args.initial_hover_s)
        if self.deadline_reached():
            return self.metrics(takeoff_ok, static_odom_ok, forced_reason="wall_timeout_during_hover_before")

        if self.args.mission in TRAJECTORY_MISSIONS:
            self.phase = self.args.mission
            self.publish_cmd_for_duration(self.trajectory_duration_s())
            self.phase = "hover_after"
            rospy.sleep(self.args.post_hold_s)
            if self.deadline_reached():
                return self.metrics(takeoff_ok, static_odom_ok, forced_reason="wall_timeout_during_trajectory")

        self.phase = "land"
        rospy.sleep(self.args.cmd_timeout_clear_s)
        self.publish_takeoff_land(TakeoffLand.LAND)
        self.wait_land_and_optionally_disarm()
        self.phase = "done"
        return self.metrics(takeoff_ok, static_odom_ok)

    @staticmethod
    def nearest_row(rows: list[dict], t: float, max_dt: float) -> dict | None:
        if not rows:
            return None
        best = min(rows, key=lambda row: abs(row["t"] - t))
        return best if abs(best["t"] - t) <= max_dt else None

    @staticmethod
    def correlation(a: list[float], b: list[float]) -> float | None:
        if len(a) < 3 or len(b) < 3 or len(a) != len(b):
            return None
        ma = statistics.fmean(a)
        mb = statistics.fmean(b)
        da = [x - ma for x in a]
        db = [x - mb for x in b]
        va = sum(x * x for x in da)
        vb = sum(x * x for x in db)
        if va <= 1e-12 or vb <= 1e-12:
            return None
        return sum(x * y for x, y in zip(da, db)) / math.sqrt(va * vb)

    @staticmethod
    def linear_slope(a: list[float], b: list[float]) -> float | None:
        """Least-squares slope for b ~= slope * a + offset."""
        if len(a) < 3 or len(b) < 3 or len(a) != len(b):
            return None
        ma = statistics.fmean(a)
        mb = statistics.fmean(b)
        da = [x - ma for x in a]
        denom = sum(x * x for x in da)
        if denom <= 1e-12:
            return None
        return sum(x * (y - mb) for x, y in zip(da, b)) / denom

    def truth_local_alignment_metrics(self) -> dict:
        return self.truth_local_alignment_metrics_for(self.truth_rows, self.local_rows)

    def truth_local_alignment_metrics_for(self, reference_rows: list[dict], measured_rows: list[dict]) -> dict:
        pairs = []
        for measured in measured_rows:
            truth = self.nearest_row(reference_rows, measured["t"], 0.03)
            if truth is not None:
                pairs.append((truth, measured))
        if len(pairs) < 3:
            return {"matched_samples": len(pairs)}
        truth0 = pairs[0][0]
        local0 = pairs[0][1]
        out: dict = {
            "matched_samples": len(pairs),
            "first_truth": {k: truth0[k] for k in ("x", "y", "z", "roll", "pitch", "yaw")},
            "first_local": {k: local0[k] for k in ("x", "y", "z", "roll", "pitch", "yaw")},
        }
        for axis in ("x", "y", "z", "vx", "vy", "vz", "roll", "pitch", "yaw"):
            truth_abs = [p[0][axis] for p in pairs]
            local_abs = [p[1][axis] for p in pairs]
            truth_delta = [v - truth_abs[0] for v in truth_abs]
            local_delta = [v - local_abs[0] for v in local_abs]
            out[axis] = {
                "abs_corr": self.correlation(truth_abs, local_abs),
                "delta_corr": self.correlation(truth_delta, local_delta),
                "delta_slope_local_per_truth": self.linear_slope(truth_delta, local_delta),
                "truth_delta_last": truth_delta[-1],
                "local_delta_last": local_delta[-1],
            }
        return out

    def metrics(self, takeoff_ok: bool, static_odom_ok: bool, forced_reason: str | None = None) -> dict:
        errors = []
        for ref in self.ref_rows:
            truth_source_rows = self.sunray_truth_rows if self.args.metric_truth_source == "sunray_gazebo_pose" else self.truth_rows
            actual = self.nearest_row(truth_source_rows, ref["t"], 0.08)
            if actual is None:
                continue
            ex = actual["x"] - ref["x"]
            ey = actual["y"] - ref["y"]
            ez = actual["z"] - ref["z"]
            errors.append({"t": ref["t"], "phase": ref["phase"], "ex": ex, "ey": ey, "ez": ez, "xy": math.hypot(ex, ey), "xyz": math.sqrt(ex * ex + ey * ey + ez * ez)})

        def rmse(values: list[float]) -> float | None:
            return math.sqrt(sum(v * v for v in values) / len(values)) if values else None

        def percentile(values: list[float], pct: float) -> float | None:
            if not values:
                return None
            ordered = sorted(values)
            if len(ordered) == 1:
                return ordered[0]
            rank = (len(ordered) - 1) * pct / 100.0
            lo = int(math.floor(rank))
            hi = int(math.ceil(rank))
            if lo == hi:
                return ordered[lo]
            alpha = rank - lo
            return ordered[lo] * (1.0 - alpha) + ordered[hi] * alpha

        def tracking_metrics(rows: list[dict]) -> dict:
            xy = [e["xy"] for e in rows]
            xyz = [e["xyz"] for e in rows]
            z_abs = [abs(e["ez"]) for e in rows]
            return {
                "matched_samples": len(rows),
                "xy_rmse_m": rmse(xy),
                "xy_p95_m": percentile(xy, 95.0),
                "xy_max_m": max(xy) if xy else None,
                "xyz_rmse_m": rmse(xyz),
                "xyz_p95_m": percentile(xyz, 95.0),
                "xyz_max_m": max(xyz) if xyz else None,
                "z_abs_rmse_m": rmse(z_abs),
                "z_abs_p95_m": percentile(z_abs, 95.0),
                "z_abs_max_m": max(z_abs) if z_abs else None,
            }

        def axis_metrics(rows: list[dict], axis: str) -> dict:
            values = [abs(e[axis]) for e in rows]
            return {
                "rmse_m": rmse(values),
                "p95_m": percentile(values, 95.0),
                "max_m": max(values) if values else None,
                "final_abs_m": values[-1] if values else None,
            }

        def step_response_metrics(rows: list[dict]) -> dict | None:
            if self.args.mission not in {"step_x", "step_y", "step_z"}:
                return None
            if not rows:
                return {
                    "schema": "mosim.sunray_ros1.px4ctrl_step_response_metrics.v1",
                    "status": "blocked",
                    "reason": "no_step_rows",
                    "settling_exclusion_s": self.args.step_settling_exclusion_s,
                    "settled_window": tracking_metrics([]),
                    "raw_full_step_diagnostic": tracking_metrics([]),
                }
            start_t = min(e["t"] for e in rows)
            settled_rows = [e for e in rows if e["t"] >= start_t + self.args.step_settling_exclusion_s]
            primary_axis = {"step_x": "ex", "step_y": "ey", "step_z": "ez"}[self.args.mission]
            cross_axes = [axis for axis in ("ex", "ey", "ez") if axis != primary_axis]
            return {
                "schema": "mosim.sunray_ros1.px4ctrl_step_response_metrics.v1",
                "status": "passed" if settled_rows else "blocked",
                "reason": None if settled_rows else "no_settled_step_rows",
                "settling_exclusion_s": self.args.step_settling_exclusion_s,
                "raw_full_step_diagnostic": tracking_metrics(rows),
                "settled_window": tracking_metrics(settled_rows),
                "primary_axis": primary_axis,
                "primary_axis_settled": axis_metrics(settled_rows, primary_axis),
                "cross_axis_settled": {axis: axis_metrics(settled_rows, axis) for axis in cross_axes},
                "settled_sample_count": len(settled_rows),
            }

        hover_source_rows = self.sunray_truth_rows if self.args.metric_truth_source == "sunray_gazebo_pose" else self.truth_rows
        hover_rows = [r for r in hover_source_rows if r["phase"] == "hover_before"]
        if self.home is not None:
            if self.args.reference_frame_source == "control_odom" and self.control_home is not None:
                hover_target = self.eval_position_from_command(
                    self.control_home[0],
                    self.control_home[1],
                    self.control_home[2] + self.args.altitude_m,
                )
            else:
                hover_target = (self.home[0], self.home[1], self.home[2] + self.args.altitude_m)
            hover_xy = [math.hypot(r["x"] - hover_target[0], r["y"] - hover_target[1]) for r in hover_rows]
            hover_z = [abs(r["z"] - hover_target[2]) for r in hover_rows]
        else:
            hover_xy = []
            hover_z = []
        hover_metrics = {
            "xy_rmse_m": rmse(hover_xy),
            "xy_max_m": max(hover_xy) if hover_xy else None,
            "z_abs_rmse_m": rmse(hover_z),
            "z_abs_max_m": max(hover_z) if hover_z else None,
        }
        steady_hover_rows = hover_rows
        if hover_rows and self.args.steady_hover_tail_s > 0:
            steady_start_t = hover_rows[-1]["t"] - self.args.steady_hover_tail_s
            steady_hover_rows = [r for r in hover_rows if r["t"] >= steady_start_t]
        if self.home is not None:
            steady_hover_xy = [math.hypot(r["x"] - hover_target[0], r["y"] - hover_target[1]) for r in steady_hover_rows]
            steady_hover_z = [abs(r["z"] - hover_target[2]) for r in steady_hover_rows]
        else:
            steady_hover_xy = []
            steady_hover_z = []
        steady_hover_metrics = {
            "window_s": self.args.steady_hover_tail_s,
            "sample_count": len(steady_hover_rows),
            "xy_rmse_m": rmse(steady_hover_xy),
            "xy_max_m": max(steady_hover_xy) if steady_hover_xy else None,
            "z_abs_rmse_m": rmse(steady_hover_z),
            "z_abs_max_m": max(steady_hover_z) if steady_hover_z else None,
        }
        trajectory_errors = [e for e in errors if e["phase"] == self.args.mission] if self.args.mission in TRAJECTORY_MISSIONS else []
        trajectory_metrics = tracking_metrics(trajectory_errors)
        step_metrics = step_response_metrics(trajectory_errors)
        all_reference_metrics = tracking_metrics(errors)
        if self.args.mission == "takeoff_hover_land":
            gate = self.goal1_gate(takeoff_ok, static_odom_ok, forced_reason, steady_hover_metrics)
        elif self.args.gate_mode == "g7":
            gate = self.g7_gate(takeoff_ok, static_odom_ok, forced_reason, trajectory_metrics, steady_hover_metrics)
        else:
            gate = self.goal2_gate(takeoff_ok, static_odom_ok, forced_reason, steady_hover_metrics, trajectory_metrics)
        result = {
            "schema": "mosim.sunray_ros1.px4ctrl_basic_mission.v1",
            "status": gate["status"],
            "reason": gate["reason"],
            "mission": self.args.mission,
            "active_gate": gate,
            "goal1_gate": gate if self.args.mission == "takeoff_hover_land" else None,
            "goal2_gate": gate if self.args.gate_mode != "g7" and self.args.mission in {"figure8", "spiral"} else None,
            "goal7_gate": gate if self.args.gate_mode == "g7" and self.args.mission in TRAJECTORY_MISSIONS else None,
            "static_odom_ready_before_takeoff": bool(static_odom_ok),
            "takeoff_reached_altitude": bool(takeoff_ok),
            "sample_counts": {
                "truth": len(self.truth_rows),
                "sunray_truth": len(self.sunray_truth_rows),
                "local_odom": len(self.local_rows),
                "control_odom": len(self.control_odom_rows),
                "reference": len(self.ref_rows),
                "debug": len(self.debug_rows),
                "att_target": len(self.att_target_rows),
                "state": len(self.state_rows),
            },
            "hover_before": hover_metrics,
            "steady_hover": steady_hover_metrics,
            "trajectory": trajectory_metrics,
            "step_response": step_metrics,
            "all_reference_tracking": all_reference_metrics,
            "metric_truth_source": self.args.metric_truth_source,
            "truth_local_alignment": self.truth_local_alignment_metrics(),
            "sunray_truth_local_alignment": self.truth_local_alignment_metrics_for(self.sunray_truth_rows, self.local_rows),
            "sunray_truth_control_odom_alignment": self.truth_local_alignment_metrics_for(self.sunray_truth_rows, self.control_odom_rows),
            "gazebo_model_vs_sunray_truth_alignment": self.truth_local_alignment_metrics_for(self.truth_rows, self.sunray_truth_rows),
            "last_truth": self.last_truth,
            "last_sunray_truth": self.last_sunray_truth,
            "last_local": self.last_local,
            "last_debug": self.last_debug,
            "last_state": {
                "connected": bool(self.last_state.connected),
                "armed": bool(self.last_state.armed),
                "mode": self.last_state.mode,
            }
            if self.last_state is not None
            else None,
            "landing_disarm": {
                "force_disarm_after_land": bool(self.args.force_disarm_after_land),
                "attempts": int(self.disarm_attempts),
                "success": bool(self.disarm_success),
                "final_z_rel_m": self.final_z_rel_m(),
                "max_force_disarm_z_rel_m": self.args.force_disarm_max_z_rel_m,
            },
        }
        with (self.result_dir / "trajectory_errors.csv").open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["t", "phase", "ex", "ey", "ez", "xy", "xyz"])
            writer.writeheader()
            writer.writerows(errors)
        return result

    @staticmethod
    def metric_leq(value: float | None, limit: float) -> bool:
        return value is not None and math.isfinite(value) and value <= limit

    @staticmethod
    def alignment_axis_ok(alignment: dict, axis: str, min_corr: float, min_slope: float, max_slope: float) -> bool:
        axis_payload = alignment.get(axis)
        if not isinstance(axis_payload, dict):
            return False
        corr = axis_payload.get("delta_corr")
        slope = axis_payload.get("delta_slope_local_per_truth")
        if corr is None or slope is None:
            return False
        return math.isfinite(corr) and math.isfinite(slope) and corr >= min_corr and min_slope <= slope <= max_slope

    def truth_local_delta_error_metrics(self, reference_rows: list[dict], measured_rows: list[dict]) -> dict:
        pairs = []
        for measured in measured_rows:
            truth = self.nearest_row(reference_rows, measured["t"], 0.03)
            if truth is not None:
                pairs.append((truth, measured))
        if len(pairs) < 3:
            return {"matched_samples": len(pairs)}
        truth0 = pairs[0][0]
        local0 = pairs[0][1]
        out: dict = {"matched_samples": len(pairs)}
        for axis in ("x", "y", "z"):
            values = []
            for truth, local in pairs:
                truth_delta = truth[axis] - truth0[axis]
                local_delta = local[axis] - local0[axis]
                values.append(local_delta - truth_delta)
            out[axis] = {
                "rmse_m": math.sqrt(sum(v * v for v in values) / len(values)),
                "max_abs_m": max(abs(v) for v in values),
                "last_m": values[-1],
            }
        return out

    def goal1_gate(
        self,
        takeoff_ok: bool,
        static_odom_ok: bool,
        forced_reason: str | None,
        hover_metrics: dict,
    ) -> dict:
        blockers: list[str] = []
        if forced_reason:
            blockers.append(forced_reason)
        if self.args.mission != "takeoff_hover_land":
            blockers.append(f"goal1_requires_takeoff_hover_land:not_{self.args.mission}")
        if self.args.require_position_cmd_hold and self.args.hover_hold_command_mode != "position_cmd":
            blockers.append(f"goal1_requires_position_cmd_hold:not_{self.args.hover_hold_command_mode}")
        if self.args.require_position_cmd_hold and len([r for r in self.ref_rows if r.get("phase") == "hover_before"]) < self.args.min_hold_reference_samples:
            blockers.append("hold_reference_samples_too_low")
        if self.args.require_mavros_local_control_odom and self.args.control_odom_topic != "/uav1/mavros/local_position/odom":
            blockers.append(f"formal_control_odom_topic_mismatch:{self.args.control_odom_topic}")
        if not static_odom_ok:
            blockers.append("static_odom_not_ready_before_takeoff")
        if not takeoff_ok:
            blockers.append("takeoff_not_reached_altitude")
        if not self.metric_leq(hover_metrics.get("xy_rmse_m"), self.args.max_hover_xy_rmse_m):
            blockers.append(f"hover_xy_rmse_above_max:{hover_metrics.get('xy_rmse_m')}")
        if not self.metric_leq(hover_metrics.get("xy_max_m"), self.args.max_hover_xy_max_m):
            blockers.append(f"hover_xy_max_above_max:{hover_metrics.get('xy_max_m')}")
        if not self.metric_leq(hover_metrics.get("z_abs_rmse_m"), self.args.max_hover_z_rmse_m):
            blockers.append(f"hover_z_rmse_above_max:{hover_metrics.get('z_abs_rmse_m')}")
        if not self.metric_leq(hover_metrics.get("z_abs_max_m"), self.args.max_hover_z_max_m):
            blockers.append(f"hover_z_max_above_max:{hover_metrics.get('z_abs_max_m')}")

        if self.args.require_landed_disarmed:
            if self.last_state is None:
                blockers.append("missing_final_mavros_state")
            else:
                if self.last_state.armed:
                    blockers.append("final_state_still_armed")
            if self.last_sunray_truth is None:
                blockers.append("missing_final_truth")
            elif self.home is not None:
                final_z_rel = self.last_sunray_truth["z"] - self.home[2]
                if final_z_rel > self.args.max_final_z_rel_m:
                    blockers.append(f"final_z_rel_above_max:{final_z_rel}")

        alignment = self.truth_local_alignment_metrics_for(self.sunray_truth_rows, self.local_rows)
        delta_error = self.truth_local_delta_error_metrics(self.sunray_truth_rows, self.local_rows)
        if self.args.require_truth_local_alignment:
            matched = int(delta_error.get("matched_samples", 0) or 0)
            if matched < self.args.min_alignment_samples:
                blockers.append(f"truth_local_alignment_samples_too_low:{matched}")
            for axis, limit in (
                ("x", self.args.max_truth_local_delta_xy_error_m),
                ("y", self.args.max_truth_local_delta_xy_error_m),
                ("z", self.args.max_truth_local_delta_z_error_m),
            ):
                axis_payload = delta_error.get(axis)
                max_abs = axis_payload.get("max_abs_m") if isinstance(axis_payload, dict) else None
                if not self.metric_leq(max_abs, limit):
                    blockers.append(f"truth_local_delta_error_bad_{axis}:{max_abs}")

        return {
            "schema": "mosim.sunray_ros1.px4ctrl_goal1_gate.v1",
            "status": "passed" if not blockers else "blocked",
            "reason": None if not blockers else ";".join(blockers),
            "blockers": blockers,
            "scope": "Goal 1 / G-PX4CTRL-0..1 / formal mavros local takeoff-hover-land",
            "formal_state_source": "/uav1/mavros/local_position/odom",
            "hover_hold_command_mode": self.args.hover_hold_command_mode,
            "reference_frame_source": self.args.reference_frame_source,
            "gate_metric_window": f"steady_hover_last_{self.args.steady_hover_tail_s:g}s",
            "truth_for_evaluation_only": self.args.metric_truth_source,
            "thresholds": {
                "max_hover_xy_rmse_m": self.args.max_hover_xy_rmse_m,
                "max_hover_xy_max_m": self.args.max_hover_xy_max_m,
                "max_hover_z_rmse_m": self.args.max_hover_z_rmse_m,
                "max_hover_z_max_m": self.args.max_hover_z_max_m,
                "max_final_z_rel_m": self.args.max_final_z_rel_m,
                "max_truth_local_delta_xy_error_m": self.args.max_truth_local_delta_xy_error_m,
                "max_truth_local_delta_z_error_m": self.args.max_truth_local_delta_z_error_m,
            },
            "alignment_preview": alignment,
            "delta_error_preview": delta_error,
        }

    def goal2_gate(
        self,
        takeoff_ok: bool,
        static_odom_ok: bool,
        forced_reason: str | None,
        steady_hover_metrics: dict,
        trajectory_metrics: dict,
    ) -> dict:
        blockers: list[str] = []
        if forced_reason:
            blockers.append(forced_reason)
        if self.args.mission not in {"figure8", "spiral"}:
            blockers.append(f"goal2_requires_trajectory_mission:{self.args.mission}")
        if self.args.require_position_cmd_hold and self.args.hover_hold_command_mode != "position_cmd":
            blockers.append(f"goal2_requires_position_cmd_hold:not_{self.args.hover_hold_command_mode}")
        if self.args.require_position_cmd_hold and len([r for r in self.ref_rows if r.get("phase") == "hover_before"]) < self.args.min_hold_reference_samples:
            blockers.append("hold_reference_samples_too_low")
        if self.args.require_mavros_local_control_odom and self.args.control_odom_topic != "/uav1/mavros/local_position/odom":
            blockers.append(f"formal_control_odom_topic_mismatch:{self.args.control_odom_topic}")
        if not static_odom_ok:
            blockers.append("static_odom_not_ready_before_takeoff")
        if not takeoff_ok:
            blockers.append("takeoff_not_reached_altitude")
        if not self.metric_leq(steady_hover_metrics.get("xy_rmse_m"), self.args.max_hover_xy_rmse_m):
            blockers.append(f"steady_hover_xy_rmse_above_max:{steady_hover_metrics.get('xy_rmse_m')}")
        if not self.metric_leq(steady_hover_metrics.get("xy_max_m"), self.args.max_hover_xy_max_m):
            blockers.append(f"steady_hover_xy_max_above_max:{steady_hover_metrics.get('xy_max_m')}")
        if not self.metric_leq(steady_hover_metrics.get("z_abs_rmse_m"), self.args.max_hover_z_rmse_m):
            blockers.append(f"steady_hover_z_rmse_above_max:{steady_hover_metrics.get('z_abs_rmse_m')}")
        if not self.metric_leq(steady_hover_metrics.get("z_abs_max_m"), self.args.max_hover_z_max_m):
            blockers.append(f"steady_hover_z_max_above_max:{steady_hover_metrics.get('z_abs_max_m')}")

        if int(trajectory_metrics.get("matched_samples", 0) or 0) < self.args.min_trajectory_samples:
            blockers.append(f"trajectory_samples_too_low:{trajectory_metrics.get('matched_samples')}")
        if not self.metric_leq(trajectory_metrics.get("xyz_rmse_m"), self.args.max_trajectory_xyz_rmse_m):
            blockers.append(f"trajectory_xyz_rmse_above_max:{trajectory_metrics.get('xyz_rmse_m')}")
        if not self.metric_leq(trajectory_metrics.get("xyz_p95_m"), self.args.max_trajectory_xyz_p95_m):
            blockers.append(f"trajectory_xyz_p95_above_max:{trajectory_metrics.get('xyz_p95_m')}")
        if not self.metric_leq(trajectory_metrics.get("xyz_max_m"), self.args.max_trajectory_xyz_max_m):
            blockers.append(f"trajectory_xyz_max_above_max:{trajectory_metrics.get('xyz_max_m')}")

        if self.args.require_landed_disarmed:
            if self.last_state is None:
                blockers.append("missing_final_mavros_state")
            elif self.last_state.armed:
                blockers.append("final_state_still_armed")
            if self.last_sunray_truth is None:
                blockers.append("missing_final_truth")
            elif self.home is not None:
                final_z_rel = self.last_sunray_truth["z"] - self.home[2]
                if final_z_rel > self.args.max_final_z_rel_m:
                    blockers.append(f"final_z_rel_above_max:{final_z_rel}")

        delta_error = self.truth_local_delta_error_metrics(self.sunray_truth_rows, self.local_rows)
        if self.args.require_truth_local_alignment:
            matched = int(delta_error.get("matched_samples", 0) or 0)
            if matched < self.args.min_alignment_samples:
                blockers.append(f"truth_local_alignment_samples_too_low:{matched}")
            for axis, limit in (
                ("x", self.args.max_truth_local_delta_xy_error_m),
                ("y", self.args.max_truth_local_delta_xy_error_m),
                ("z", self.args.max_truth_local_delta_z_error_m),
            ):
                axis_payload = delta_error.get(axis)
                max_abs = axis_payload.get("max_abs_m") if isinstance(axis_payload, dict) else None
                if not self.metric_leq(max_abs, limit):
                    blockers.append(f"truth_local_delta_error_bad_{axis}:{max_abs}")

        return {
            "schema": "mosim.sunray_ros1.px4ctrl_goal2_gate.v1",
            "status": "passed" if not blockers else "blocked",
            "reason": None if not blockers else ";".join(blockers),
            "blockers": blockers,
            "scope": "Goal 2 / G-PX4CTRL-2..4 / formal mavros local trajectory tracking",
            "mission": self.args.mission,
            "formal_state_source": "/uav1/mavros/local_position/odom",
            "hover_hold_command_mode": self.args.hover_hold_command_mode,
            "reference_frame_source": self.args.reference_frame_source,
            "gate_metric_window": f"trajectory_phase_{self.args.mission}",
            "truth_for_evaluation_only": self.args.metric_truth_source,
            "thresholds": {
                "max_trajectory_xyz_rmse_m": self.args.max_trajectory_xyz_rmse_m,
                "max_trajectory_xyz_p95_m": self.args.max_trajectory_xyz_p95_m,
                "max_trajectory_xyz_max_m": self.args.max_trajectory_xyz_max_m,
                "min_trajectory_samples": self.args.min_trajectory_samples,
                "max_hover_xy_rmse_m": self.args.max_hover_xy_rmse_m,
                "max_hover_xy_max_m": self.args.max_hover_xy_max_m,
                "max_hover_z_rmse_m": self.args.max_hover_z_rmse_m,
                "max_hover_z_max_m": self.args.max_hover_z_max_m,
                "max_final_z_rel_m": self.args.max_final_z_rel_m,
                "max_truth_local_delta_xy_error_m": self.args.max_truth_local_delta_xy_error_m,
                "max_truth_local_delta_z_error_m": self.args.max_truth_local_delta_z_error_m,
            },
            "trajectory_preview": trajectory_metrics,
            "steady_hover_preview": steady_hover_metrics,
            "delta_error_preview": delta_error,
        }

    def g7_gate(
        self,
        takeoff_ok: bool,
        static_odom_ok: bool,
        forced_reason: str | None,
        trajectory_metrics: dict,
        steady_hover_metrics: dict,
    ) -> dict:
        blockers: list[str] = []
        if forced_reason:
            blockers.append(forced_reason)
        if self.args.mission not in TRAJECTORY_MISSIONS:
            blockers.append(f"g7_requires_trajectory_mission:{self.args.mission}")
        if self.args.require_position_cmd_hold and self.args.hover_hold_command_mode != "position_cmd":
            blockers.append(f"g7_requires_position_cmd_hold:not_{self.args.hover_hold_command_mode}")
        if self.args.require_position_cmd_hold and len([r for r in self.ref_rows if r.get("phase") == "hover_before"]) < self.args.min_hold_reference_samples:
            blockers.append("hold_reference_samples_too_low")
        if self.args.require_mavros_local_control_odom and self.args.control_odom_topic != "/uav1/mavros/local_position/odom":
            blockers.append(f"formal_control_odom_topic_mismatch:{self.args.control_odom_topic}")
        if not static_odom_ok:
            blockers.append("static_odom_not_ready_before_takeoff")
        if not takeoff_ok:
            blockers.append("takeoff_not_reached_altitude")
        if int(trajectory_metrics.get("matched_samples", 0) or 0) < self.args.min_trajectory_samples:
            blockers.append(f"trajectory_samples_too_low:{trajectory_metrics.get('matched_samples')}")

        if self.args.require_landed_disarmed:
            if self.last_state is None:
                blockers.append("missing_final_mavros_state")
            elif self.last_state.armed:
                blockers.append("final_state_still_armed")
            if self.last_sunray_truth is None:
                blockers.append("missing_final_truth")
            elif self.home is not None:
                final_z_rel = self.last_sunray_truth["z"] - self.home[2]
                if final_z_rel > self.args.max_final_z_rel_m:
                    blockers.append(f"final_z_rel_above_max:{final_z_rel}")

        delta_error = self.truth_local_delta_error_metrics(self.sunray_truth_rows, self.local_rows)
        return {
            "schema": "mosim.sunray_ros1.px4ctrl_g7_trajectory_gate.v1",
            "status": "passed" if not blockers else "blocked",
            "reason": None if not blockers else ";".join(blockers),
            "blockers": blockers,
            "scope": "G-PX4CTRL-7 / Gazebo A/B trajectory consistency run",
            "mission": self.args.mission,
            "formal_state_source": "/uav1/mavros/local_position/odom",
            "hover_hold_command_mode": self.args.hover_hold_command_mode,
            "reference_frame_source": self.args.reference_frame_source,
            "gate_metric_window": f"trajectory_phase_{self.args.mission}",
            "truth_for_evaluation_only": self.args.metric_truth_source,
            "thresholds": {
                "min_trajectory_samples": self.args.min_trajectory_samples,
                "max_final_z_rel_m": self.args.max_final_z_rel_m,
            },
            "trajectory_preview": trajectory_metrics,
            "steady_hover_preview_diagnostic_only": steady_hover_metrics,
            "delta_error_preview_diagnostic_only": delta_error,
        }

    def write_outputs(self, metrics: dict) -> None:
        for name, rows in [
            ("truth.csv", self.truth_rows),
            ("sunray_truth.csv", self.sunray_truth_rows),
            ("local_odom.csv", self.local_rows),
            ("control_odom.csv", self.control_odom_rows),
            ("reference.csv", self.ref_rows),
            ("debug_px4ctrl.csv", self.debug_rows),
            ("target_attitude.csv", self.att_target_rows),
            ("mavros_state.csv", self.state_rows),
        ]:
            if not rows:
                continue
            with (self.result_dir / name).open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
        self.publish_truth_path_if_due(self.now(), force=True)
        self.ref_path_pub.publish(self.reference_path)
        (self.result_dir / "PX4CTRL_BASIC_MISSION_METRICS.json").write_text(
            json.dumps(metrics, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--mission", choices=["takeoff_hover_land", "figure8", "spiral", "circle", "step_x", "step_y", "step_z"], default="takeoff_hover_land")
    parser.add_argument("--gate-mode", choices=["goal2", "g7"], default="goal2")
    parser.add_argument("--truth-model-name", default="uav1")
    parser.add_argument("--sunray-truth-topic", default="/uav1/sunray/gazebo_pose")
    parser.add_argument("--control-odom-topic", default="/uav1/mavros/local_position/odom")
    parser.add_argument("--metric-truth-source", choices=["sunray_gazebo_pose", "gazebo_model_states"], default="sunray_gazebo_pose")
    parser.add_argument("--reference-frame-source", choices=["control_odom", "truth"], default="control_odom")
    parser.add_argument("--path-frame", default="map")
    parser.add_argument("--truth-child-frame", default="uav1/base_link")
    parser.add_argument("--altitude-m", type=float, default=1.0)
    parser.add_argument("--takeoff-altitude-m", type=float, default=0.0)
    parser.add_argument("--takeoff-reached-ratio", type=float, default=0.98)
    parser.add_argument("--takeoff-settle-z-error-max-m", type=float, default=0.08)
    parser.add_argument("--takeoff-settle-vz-max-mps", type=float, default=0.12)
    parser.add_argument("--takeoff-timeout-s", type=float, default=35.0)
    parser.add_argument("--static-odom-timeout-s", type=float, default=60.0)
    parser.add_argument("--static-odom-speed-max-mps", type=float, default=0.08)
    parser.add_argument("--static-odom-hold-s", type=float, default=1.0)
    parser.add_argument("--takeoff-cmd-repeats", type=int, default=20)
    parser.add_argument("--initial-hover-s", type=float, default=8.0)
    parser.add_argument("--hover-ramp-s", type=float, default=0.0)
    parser.add_argument("--steady-hover-tail-s", type=float, default=2.0)
    parser.add_argument("--post-hold-s", type=float, default=2.0)
    parser.add_argument("--cmd-timeout-clear-s", type=float, default=1.0)
    parser.add_argument("--land-wait-s", type=float, default=14.0)
    parser.add_argument("--force-disarm-after-land", action="store_true")
    parser.add_argument("--force-disarm-timeout-s", type=float, default=8.0)
    parser.add_argument("--force-disarm-max-z-rel-m", type=float, default=0.18)
    parser.add_argument("--command-rate-hz", type=float, default=50.0)
    parser.add_argument("--command-x-bias-m", type=float, default=0.0)
    parser.add_argument("--command-y-bias-m", type=float, default=0.0)
    parser.add_argument("--command-z-bias-m", type=float, default=0.0)
    parser.add_argument("--hover-hold-command-mode", choices=["position_cmd", "auto_hover"], default="position_cmd")
    parser.add_argument("--figure8-period-s", type=float, default=24.0)
    parser.add_argument("--figure8-cycles", type=float, default=2.0)
    parser.add_argument("--figure8-x-amp-m", type=float, default=0.6)
    parser.add_argument("--figure8-y-amp-m", type=float, default=0.35)
    parser.add_argument("--spiral-period-s", type=float, default=16.0)
    parser.add_argument("--spiral-duration-s", type=float, default=36.0)
    parser.add_argument("--spiral-radius-m", type=float, default=0.45)
    parser.add_argument("--spiral-climb-m", type=float, default=0.5)
    parser.add_argument("--spiral-z-profile", choices=["linear", "smoothstep"], default="linear")
    parser.add_argument("--circle-period-s", type=float, default=36.0)
    parser.add_argument("--circle-cycles", type=float, default=1.0)
    parser.add_argument("--circle-radius-m", type=float, default=0.50)
    parser.add_argument("--step-duration-s", type=float, default=18.0)
    parser.add_argument("--step-amplitude-m", type=float, default=0.30)
    parser.add_argument("--step-z-amplitude-m", type=float, default=0.20)
    parser.add_argument("--step-settling-exclusion-s", type=float, default=2.0)
    parser.add_argument("--trajectory-time-lead-s", type=float, default=0.0)
    parser.add_argument("--max-path-points", type=int, default=5000)
    parser.add_argument("--path-publish-hz", type=float, default=10.0)
    parser.add_argument("--body-axis-length-m", type=float, default=0.018)
    parser.add_argument("--body-axis-shaft-m", type=float, default=0.0014)
    parser.add_argument("--body-axis-head-diameter-m", type=float, default=0.0036)
    parser.add_argument("--body-axis-head-length-m", type=float, default=0.0048)
    parser.add_argument("--body-axis-lifetime-s", type=float, default=0.25)
    parser.add_argument("--wall-timeout-s", type=float, default=150.0)
    parser.add_argument("--record-truth-hz", type=float, default=50.0)
    parser.add_argument("--record-odom-hz", type=float, default=100.0)
    parser.add_argument("--record-debug-hz", type=float, default=50.0)
    parser.add_argument("--record-attitude-hz", type=float, default=50.0)
    parser.add_argument("--record-state-hz", type=float, default=10.0)
    parser.add_argument("--max-hover-xy-rmse-m", type=float, default=0.02)
    parser.add_argument("--max-hover-xy-max-m", type=float, default=0.05)
    parser.add_argument("--max-hover-z-rmse-m", type=float, default=0.02)
    parser.add_argument("--max-hover-z-max-m", type=float, default=0.05)
    parser.add_argument("--max-trajectory-xyz-rmse-m", type=float, default=0.05)
    parser.add_argument("--max-trajectory-xyz-p95-m", type=float, default=0.08)
    parser.add_argument("--max-trajectory-xyz-max-m", type=float, default=0.15)
    parser.add_argument("--min-trajectory-samples", type=int, default=200)
    parser.add_argument("--max-final-z-rel-m", type=float, default=0.18)
    parser.add_argument("--min-alignment-samples", type=int, default=100)
    parser.add_argument("--min-hold-reference-samples", type=int, default=100)
    parser.add_argument("--max-truth-local-delta-xy-error-m", type=float, default=0.15)
    parser.add_argument("--max-truth-local-delta-z-error-m", type=float, default=0.20)
    parser.add_argument("--require-mavros-local-control-odom", action="store_true", default=True)
    parser.add_argument("--no-require-mavros-local-control-odom", dest="require_mavros_local_control_odom", action="store_false")
    parser.add_argument("--require-truth-local-alignment", action="store_true", default=True)
    parser.add_argument("--no-require-truth-local-alignment", dest="require_truth_local_alignment", action="store_false")
    parser.add_argument("--require-landed-disarmed", action="store_true", default=True)
    parser.add_argument("--no-require-landed-disarmed", dest="require_landed_disarmed", action="store_false")
    parser.add_argument("--require-position-cmd-hold", action="store_true", default=True)
    parser.add_argument("--no-require-position-cmd-hold", dest="require_position_cmd_hold", action="store_false")
    return parser.parse_args()


def main() -> int:
    rospy.init_node("mosim_px4ctrl_basic_mission", anonymous=False)
    node = Px4ctrlBasicMission(parse_args())
    metrics = node.run()
    node.write_outputs(metrics)
    return 0 if metrics.get("status") == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
