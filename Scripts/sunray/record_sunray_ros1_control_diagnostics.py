#!/usr/bin/env python3
"""Record Sunray ROS1/PX4/Gazebo control diagnostics for one bounded run."""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import rospy
from gazebo_msgs.msg import ModelStates
from geometry_msgs.msg import PoseStamped, TwistStamped
from mavros_msgs.msg import Altitude, ExtendedState, PositionTarget
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu
from sunray_msgs.msg import UAVState


class ControlDiagnostics:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.out_dir = Path(args.out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.start_wall = time.time()
        self.last_truth_pose: dict | None = None
        self.last_local_pose: dict | None = None
        self.last_gazebo_pose: dict | None = None
        self.last_vision_pose: dict | None = None
        self.last_state: dict | None = None
        self.last_sp_local: dict | None = None
        self.last_target_local: dict | None = None
        self.last_velocity: dict | None = None
        self.last_imu: dict | None = None
        self.last_altitude: dict | None = None
        self.last_extended_state: dict | None = None
        self.last_fastlio_odom: dict | None = None
        self.last_fastlio_aligned_odom: dict | None = None

        self.counts = {
            "truth": 0,
            "gazebo_pose": 0,
            "vision_pose": 0,
            "local_pose": 0,
            "local_velocity": 0,
            "uav_state": 0,
            "setpoint_raw_local": 0,
            "target_local": 0,
            "imu": 0,
            "altitude": 0,
            "extended_state": 0,
            "fastlio_odom": 0,
            "fastlio_aligned_odom": 0,
            "samples": 0,
        }
        self.rows: list[dict] = []

        rospy.Subscriber("/gazebo/model_states", ModelStates, self.on_model_states, queue_size=100)
        rospy.Subscriber(f"{args.uav_ns}/sunray/gazebo_pose", Odometry, self.on_gazebo_pose, queue_size=100)
        rospy.Subscriber(f"{args.uav_ns}/mavros/vision_pose/pose", PoseStamped, self.on_vision_pose, queue_size=100)
        rospy.Subscriber(f"{args.uav_ns}/mavros/local_position/pose", PoseStamped, self.on_local_pose, queue_size=100)
        rospy.Subscriber(
            f"{args.uav_ns}/mavros/local_position/velocity_local",
            TwistStamped,
            self.on_local_velocity,
            queue_size=100,
        )
        rospy.Subscriber(f"{args.uav_ns}/sunray/uav_state", UAVState, self.on_uav_state, queue_size=100)
        rospy.Subscriber(f"{args.uav_ns}/mavros/setpoint_raw/local", PositionTarget, self.on_sp_local, queue_size=100)
        rospy.Subscriber(
            f"{args.uav_ns}/mavros/setpoint_raw/target_local",
            PositionTarget,
            self.on_target_local,
            queue_size=100,
        )
        rospy.Subscriber(f"{args.uav_ns}/mavros/imu/data", Imu, self.on_imu, queue_size=100)
        rospy.Subscriber(f"{args.uav_ns}/mavros/altitude", Altitude, self.on_altitude, queue_size=100)
        rospy.Subscriber(f"{args.uav_ns}/mavros/extended_state", ExtendedState, self.on_extended_state, queue_size=100)
        if args.fastlio_odom_topic:
            rospy.Subscriber(args.fastlio_odom_topic, Odometry, self.on_fastlio_odom, queue_size=100)
        if args.fastlio_aligned_odom_topic:
            rospy.Subscriber(args.fastlio_aligned_odom_topic, Odometry, self.on_fastlio_aligned_odom, queue_size=100)

    def now(self) -> float:
        stamp = rospy.Time.now().to_sec()
        if stamp > 0:
            return float(stamp)
        return time.time() - self.start_wall

    @staticmethod
    def yaw_from_quat(x: float, y: float, z: float, w: float) -> float:
        return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))

    @staticmethod
    def rpy_from_quat(x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
        roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
        pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
        yaw = ControlDiagnostics.yaw_from_quat(x, y, z, w)
        return roll, pitch, yaw

    @staticmethod
    def position_target_dict(msg: PositionTarget, t: float) -> dict:
        return {
            "t": t,
            "frame": int(msg.coordinate_frame),
            "type_mask": int(msg.type_mask),
            "x": float(msg.position.x),
            "y": float(msg.position.y),
            "z": float(msg.position.z),
            "vx": float(msg.velocity.x),
            "vy": float(msg.velocity.y),
            "vz": float(msg.velocity.z),
            "afx": float(msg.acceleration_or_force.x),
            "afy": float(msg.acceleration_or_force.y),
            "afz": float(msg.acceleration_or_force.z),
            "yaw": float(msg.yaw),
            "yaw_rate": float(msg.yaw_rate),
        }

    def on_model_states(self, msg: ModelStates) -> None:
        try:
            idx = list(msg.name).index(self.args.truth_model_name)
        except ValueError:
            return
        pose = msg.pose[idx]
        twist = msg.twist[idx]
        q = pose.orientation
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        self.last_truth_pose = {
            "t": self.now(),
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
        self.counts["truth"] += 1

    def on_local_pose(self, msg: PoseStamped) -> None:
        p = msg.pose.position
        q = msg.pose.orientation
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        self.last_local_pose = {
            "t": self.now(),
            "x": float(p.x),
            "y": float(p.y),
            "z": float(p.z),
            "roll": roll,
            "pitch": pitch,
            "yaw": yaw,
        }
        self.counts["local_pose"] += 1

    def on_gazebo_pose(self, msg: Odometry) -> None:
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        v = msg.twist.twist.linear
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        self.last_gazebo_pose = {
            "t": self.now(),
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
        self.counts["gazebo_pose"] += 1

    def on_vision_pose(self, msg: PoseStamped) -> None:
        p = msg.pose.position
        q = msg.pose.orientation
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        self.last_vision_pose = {
            "t": self.now(),
            "x": float(p.x),
            "y": float(p.y),
            "z": float(p.z),
            "roll": roll,
            "pitch": pitch,
            "yaw": yaw,
        }
        self.counts["vision_pose"] += 1

    def on_local_velocity(self, msg: TwistStamped) -> None:
        v = msg.twist.linear
        self.last_velocity = {"t": self.now(), "vx": float(v.x), "vy": float(v.y), "vz": float(v.z)}
        self.counts["local_velocity"] += 1

    def on_uav_state(self, msg: UAVState) -> None:
        self.last_state = {
            "t": self.now(),
            "armed": bool(msg.armed),
            "mode": msg.mode,
            "control_mode": int(msg.control_mode),
            "move_mode": int(msg.move_mode),
            "landed_state": int(msg.landed_state),
            "x": float(msg.position[0]),
            "y": float(msg.position[1]),
            "z": float(msg.position[2]),
            "vx": float(msg.velocity[0]),
            "vy": float(msg.velocity[1]),
            "vz": float(msg.velocity[2]),
            "sp_x": float(msg.pos_setpoint[0]),
            "sp_y": float(msg.pos_setpoint[1]),
            "sp_z": float(msg.pos_setpoint[2]),
            "home_x": float(msg.home_pos[0]),
            "home_y": float(msg.home_pos[1]),
            "home_z": float(msg.home_pos[2]),
            "hover_x": float(msg.hover_pos[0]),
            "hover_y": float(msg.hover_pos[1]),
            "hover_z": float(msg.hover_pos[2]),
        }
        self.counts["uav_state"] += 1

    def on_sp_local(self, msg: PositionTarget) -> None:
        self.last_sp_local = self.position_target_dict(msg, self.now())
        self.counts["setpoint_raw_local"] += 1

    def on_target_local(self, msg: PositionTarget) -> None:
        self.last_target_local = self.position_target_dict(msg, self.now())
        self.counts["target_local"] += 1

    def on_imu(self, msg: Imu) -> None:
        q = msg.orientation
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        self.last_imu = {"t": self.now(), "roll": roll, "pitch": pitch, "yaw": yaw}
        self.counts["imu"] += 1

    def on_altitude(self, msg: Altitude) -> None:
        self.last_altitude = {
            "t": self.now(),
            "monotonic": float(msg.monotonic),
            "amsl": float(msg.amsl),
            "local": float(msg.local),
            "relative": float(msg.relative),
            "terrain": float(msg.terrain),
            "bottom_clearance": float(msg.bottom_clearance),
        }
        self.counts["altitude"] += 1

    def on_extended_state(self, msg: ExtendedState) -> None:
        self.last_extended_state = {
            "t": self.now(),
            "vtol_state": int(msg.vtol_state),
            "landed_state": int(msg.landed_state),
        }
        self.counts["extended_state"] += 1

    def odom_dict(self, msg: Odometry) -> dict:
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        v = msg.twist.twist.linear
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        return {
            "t": self.now(),
            "frame_id": msg.header.frame_id,
            "child_frame_id": msg.child_frame_id,
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

    def on_fastlio_odom(self, msg: Odometry) -> None:
        self.last_fastlio_odom = self.odom_dict(msg)
        self.counts["fastlio_odom"] += 1

    def on_fastlio_aligned_odom(self, msg: Odometry) -> None:
        self.last_fastlio_aligned_odom = self.odom_dict(msg)
        self.counts["fastlio_aligned_odom"] += 1

    def snapshot(self) -> None:
        row = {
            "t": self.now(),
            "truth": self.last_truth_pose,
            "gazebo_pose": self.last_gazebo_pose,
            "vision_pose": self.last_vision_pose,
            "local_pose": self.last_local_pose,
            "local_velocity": self.last_velocity,
            "uav_state": self.last_state,
            "setpoint_raw_local": self.last_sp_local,
            "target_local": self.last_target_local,
            "imu": self.last_imu,
            "altitude": self.last_altitude,
            "extended_state": self.last_extended_state,
            "fastlio_odom": self.last_fastlio_odom,
            "fastlio_aligned_odom": self.last_fastlio_aligned_odom,
        }
        if self.last_truth_pose and self.last_target_local:
            row["truth_minus_target"] = {
                "x": self.last_truth_pose["x"] - self.last_target_local["x"],
                "y": self.last_truth_pose["y"] - self.last_target_local["y"],
                "z": self.last_truth_pose["z"] - self.last_target_local["z"],
            }
            row["truth_target_xy_error"] = math.hypot(
                row["truth_minus_target"]["x"],
                row["truth_minus_target"]["y"],
            )
        if self.last_local_pose and self.last_target_local:
            row["local_minus_target"] = {
                "x": self.last_local_pose["x"] - self.last_target_local["x"],
                "y": self.last_local_pose["y"] - self.last_target_local["y"],
                "z": self.last_local_pose["z"] - self.last_target_local["z"],
            }
            row["local_target_xy_error"] = math.hypot(
                row["local_minus_target"]["x"],
                row["local_minus_target"]["y"],
            )
        if self.last_truth_pose and self.last_local_pose:
            row["truth_minus_local"] = {
                "x": self.last_truth_pose["x"] - self.last_local_pose["x"],
                "y": self.last_truth_pose["y"] - self.last_local_pose["y"],
                "z": self.last_truth_pose["z"] - self.last_local_pose["z"],
            }
        if self.last_gazebo_pose and self.last_vision_pose:
            row["gazebo_minus_vision"] = {
                "x": self.last_gazebo_pose["x"] - self.last_vision_pose["x"],
                "y": self.last_gazebo_pose["y"] - self.last_vision_pose["y"],
                "z": self.last_gazebo_pose["z"] - self.last_vision_pose["z"],
            }
        if self.last_gazebo_pose and self.last_local_pose:
            row["gazebo_minus_local"] = {
                "x": self.last_gazebo_pose["x"] - self.last_local_pose["x"],
                "y": self.last_gazebo_pose["y"] - self.last_local_pose["y"],
                "z": self.last_gazebo_pose["z"] - self.last_local_pose["z"],
            }
        if self.last_vision_pose and self.last_local_pose:
            row["vision_minus_local"] = {
                "x": self.last_vision_pose["x"] - self.last_local_pose["x"],
                "y": self.last_vision_pose["y"] - self.last_local_pose["y"],
                "z": self.last_vision_pose["z"] - self.last_local_pose["z"],
            }
        if self.last_gazebo_pose and self.last_fastlio_aligned_odom:
            row["gazebo_minus_fastlio_aligned"] = {
                "x": self.last_gazebo_pose["x"] - self.last_fastlio_aligned_odom["x"],
                "y": self.last_gazebo_pose["y"] - self.last_fastlio_aligned_odom["y"],
                "z": self.last_gazebo_pose["z"] - self.last_fastlio_aligned_odom["z"],
            }
        if self.last_gazebo_pose and self.last_fastlio_odom:
            row["gazebo_minus_fastlio_raw"] = {
                "x": self.last_gazebo_pose["x"] - self.last_fastlio_odom["x"],
                "y": self.last_gazebo_pose["y"] - self.last_fastlio_odom["y"],
                "z": self.last_gazebo_pose["z"] - self.last_fastlio_odom["z"],
            }
        self.rows.append(row)
        self.counts["samples"] += 1

    @staticmethod
    def rmse(values: list[float]) -> float | None:
        if not values:
            return None
        return math.sqrt(sum(v * v for v in values) / len(values))

    @staticmethod
    def mean(values: list[float]) -> float | None:
        if not values:
            return None
        return sum(values) / len(values)

    def summarize(self) -> dict:
        active = [
            row
            for row in self.rows
            if row.get("uav_state")
            and row["uav_state"].get("armed")
            and row["uav_state"].get("landed_state") != 1
            and row.get("target_local")
        ]
        hover_like = [
            row
            for row in active
            if row["target_local"]
            and row["truth"]
            and abs(row["target_local"]["vx"]) < 0.02
            and abs(row["target_local"]["vy"]) < 0.02
            and abs(row["target_local"]["vz"]) < 0.02
            and row["target_local"]["z"] > 0.5
        ]
        truth_target_xy = [float(row["truth_target_xy_error"]) for row in hover_like if "truth_target_xy_error" in row]
        local_target_xy = [float(row["local_target_xy_error"]) for row in hover_like if "local_target_xy_error" in row]
        truth_target_z = [
            float(abs(row["truth_minus_target"]["z"]))
            for row in hover_like
            if "truth_minus_target" in row
        ]
        local_target_z = [
            float(abs(row["local_minus_target"]["z"]))
            for row in hover_like
            if "local_minus_target" in row
        ]
        truth_local_z = [
            float(abs(row["truth_minus_local"]["z"]))
            for row in hover_like
            if "truth_minus_local" in row
        ]
        gazebo_vision_z = [
            float(abs(row["gazebo_minus_vision"]["z"]))
            for row in self.rows
            if "gazebo_minus_vision" in row
        ]
        gazebo_local_z = [
            float(abs(row["gazebo_minus_local"]["z"]))
            for row in self.rows
            if "gazebo_minus_local" in row
        ]
        vision_local_z = [
            float(abs(row["vision_minus_local"]["z"]))
            for row in self.rows
            if "vision_minus_local" in row
        ]
        fastlio_aligned_xyz = [
            math.sqrt(
                float(row["gazebo_minus_fastlio_aligned"]["x"]) ** 2
                + float(row["gazebo_minus_fastlio_aligned"]["y"]) ** 2
                + float(row["gazebo_minus_fastlio_aligned"]["z"]) ** 2
            )
            for row in self.rows
            if "gazebo_minus_fastlio_aligned" in row
        ]
        fastlio_aligned_z = [
            float(abs(row["gazebo_minus_fastlio_aligned"]["z"]))
            for row in self.rows
            if "gazebo_minus_fastlio_aligned" in row
        ]
        fastlio_aligned_xy = [
            math.sqrt(
                float(row["gazebo_minus_fastlio_aligned"]["x"]) ** 2
                + float(row["gazebo_minus_fastlio_aligned"]["y"]) ** 2
            )
            for row in self.rows
            if "gazebo_minus_fastlio_aligned" in row
        ]
        fastlio_aligned_z_signed = [
            float(row["gazebo_minus_fastlio_aligned"]["z"])
            for row in self.rows
            if "gazebo_minus_fastlio_aligned" in row
        ]
        fastlio_aligned_z_delta = []
        if fastlio_aligned_z_signed:
            first_z_offset = fastlio_aligned_z_signed[0]
            fastlio_aligned_z_delta = [
                abs(z_offset - first_z_offset) for z_offset in fastlio_aligned_z_signed
            ]
        fastlio_raw_xyz = [
            math.sqrt(
                float(row["gazebo_minus_fastlio_raw"]["x"]) ** 2
                + float(row["gazebo_minus_fastlio_raw"]["y"]) ** 2
                + float(row["gazebo_minus_fastlio_raw"]["z"]) ** 2
            )
            for row in self.rows
            if "gazebo_minus_fastlio_raw" in row
        ]
        return {
            "schema": "mosim.sunray_ros1_control_diagnostics.v1",
            "status": "recorded",
            "duration_s": self.args.duration_s,
            "uav_ns": self.args.uav_ns,
            "truth_model_name": self.args.truth_model_name,
            "counts": self.counts,
            "hover_like_samples": len(hover_like),
            "hover_like_truth_target_xy_rmse_m": self.rmse(truth_target_xy),
            "hover_like_truth_target_xy_max_m": max(truth_target_xy) if truth_target_xy else None,
            "hover_like_local_target_xy_rmse_m": self.rmse(local_target_xy),
            "hover_like_truth_target_z_rmse_m": self.rmse(truth_target_z),
            "hover_like_truth_target_z_mean_abs_m": self.mean(truth_target_z),
            "hover_like_truth_target_z_max_abs_m": max(truth_target_z) if truth_target_z else None,
            "hover_like_local_target_z_rmse_m": self.rmse(local_target_z),
            "hover_like_truth_local_z_rmse_m": self.rmse(truth_local_z),
            "gazebo_vision_z_rmse_m": self.rmse(gazebo_vision_z),
            "gazebo_vision_z_max_abs_m": max(gazebo_vision_z) if gazebo_vision_z else None,
            "gazebo_local_z_rmse_m": self.rmse(gazebo_local_z),
            "gazebo_local_z_max_abs_m": max(gazebo_local_z) if gazebo_local_z else None,
            "vision_local_z_rmse_m": self.rmse(vision_local_z),
            "vision_local_z_max_abs_m": max(vision_local_z) if vision_local_z else None,
            "gazebo_fastlio_aligned_xyz_rmse_m": self.rmse(fastlio_aligned_xyz),
            "gazebo_fastlio_aligned_xyz_max_m": max(fastlio_aligned_xyz) if fastlio_aligned_xyz else None,
            "gazebo_fastlio_aligned_xy_rmse_m": self.rmse(fastlio_aligned_xy),
            "gazebo_fastlio_aligned_xy_max_m": max(fastlio_aligned_xy) if fastlio_aligned_xy else None,
            "gazebo_fastlio_aligned_z_rmse_m": self.rmse(fastlio_aligned_z),
            "gazebo_fastlio_aligned_z_max_abs_m": max(fastlio_aligned_z) if fastlio_aligned_z else None,
            "gazebo_fastlio_aligned_z_first_offset_m": fastlio_aligned_z_signed[0] if fastlio_aligned_z_signed else None,
            "gazebo_fastlio_aligned_z_delta_rmse_m": self.rmse(fastlio_aligned_z_delta),
            "gazebo_fastlio_aligned_z_delta_max_abs_m": max(fastlio_aligned_z_delta) if fastlio_aligned_z_delta else None,
            "gazebo_fastlio_aligned_metric_note": "xyz/z are absolute and offset-sensitive; xy and z_delta separate horizontal error from initial-frame height offset.",
            "gazebo_fastlio_raw_xyz_rmse_m": self.rmse(fastlio_raw_xyz),
            "gazebo_fastlio_raw_xyz_max_m": max(fastlio_raw_xyz) if fastlio_raw_xyz else None,
            "first_row": self.rows[0] if self.rows else None,
            "last_row": self.rows[-1] if self.rows else None,
        }

    def run(self) -> None:
        rate = rospy.Rate(self.args.sample_rate_hz)
        deadline = time.time() + self.args.duration_s
        while not rospy.is_shutdown() and time.time() < deadline:
            self.snapshot()
            rate.sleep()
        rows_path = self.out_dir / "control_diagnostics_samples.jsonl"
        rows_path.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in self.rows),
            encoding="utf-8",
        )
        summary = self.summarize()
        summary["samples_jsonl"] = str(rows_path)
        (self.out_dir / "control_diagnostics_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--duration-s", type=float, default=80.0)
    parser.add_argument("--sample-rate-hz", type=float, default=20.0)
    parser.add_argument("--uav-ns", default="/uav1")
    parser.add_argument("--truth-model-name", default="uav1")
    parser.add_argument("--fastlio-odom-topic", default="/Odometry")
    parser.add_argument("--fastlio-aligned-odom-topic", default="/mosim/fastlio/odom_aligned")
    args = parser.parse_args()
    rospy.init_node("mosim_sunray_ros1_control_diagnostics", anonymous=True, disable_signals=True)
    ControlDiagnostics(args).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
