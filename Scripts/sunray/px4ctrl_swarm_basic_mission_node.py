#!/usr/bin/env python3
"""Multi-UAV takeoff-hover-land gate for original px4ctrl on Sunray/PX4/Gazebo."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path

import rospy
from gazebo_msgs.msg import ModelStates
from mavros_msgs.msg import AttitudeTarget, State
from nav_msgs.msg import Odometry
from quadrotor_msgs.msg import PositionCommand, Px4ctrlDebug, TakeoffLand
from sensor_msgs.msg import PointCloud2


@dataclass
class Uav:
    uid: int
    start_xy: tuple[float, float]
    takeoff_land_pub: rospy.Publisher
    cmd_pub: rospy.Publisher
    state: State | None = None
    truth: dict | None = None
    odom: dict | None = None
    home_truth_xy: tuple[float, float] | None = None
    home_truth_z: float | None = None
    home_odom_xy: tuple[float, float] | None = None
    home_odom_z: float | None = None
    raw_lidar_count: int = 0
    raw_lidar_points: int = 0
    target_attitude_count: int = 0
    debug_count: int = 0
    truth_rows: list[dict] = field(default_factory=list)
    odom_rows: list[dict] = field(default_factory=list)
    att_rows: list[dict] = field(default_factory=list)
    debug_rows: list[dict] = field(default_factory=list)
    last_record_t: dict[str, float] = field(default_factory=lambda: {"truth": -1e9, "odom": -1e9, "att": -1e9, "debug": -1e9})


class SwarmBasicMission:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.result_dir = Path(args.result_dir)
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.start_wall = time.time()
        self.phase = "init"
        self.uavs: dict[int, Uav] = {}
        self.min_inter_uav_distance = float("inf")
        self.min_inter_uav_pair: tuple[int, int] | None = None
        self.separation_rows: list[dict] = []
        self.last_sep_record_t = -1e9

        for uid in range(1, args.uav_num + 1):
            uav = Uav(
                uid=uid,
                start_xy=self.start_xy_for(uid),
                takeoff_land_pub=rospy.Publisher(f"/uav{uid}/px4ctrl/takeoff_land", TakeoffLand, queue_size=3, latch=True),
                cmd_pub=rospy.Publisher(f"/uav{uid}/position_cmd", PositionCommand, queue_size=10),
            )
            self.uavs[uid] = uav
            rospy.Subscriber(f"/uav{uid}/mavros/state", State, lambda msg, uid=uid: self.on_state(uid, msg), queue_size=20)
            rospy.Subscriber(f"/uav{uid}/mavros/local_position/odom", Odometry, lambda msg, uid=uid: self.on_odom(uid, msg), queue_size=100)
            rospy.Subscriber(f"/uav{uid}/mavros/setpoint_raw/target_attitude", AttitudeTarget, lambda msg, uid=uid: self.on_att(uid, msg), queue_size=100)
            rospy.Subscriber(f"/uav{uid}/debugPx4ctrl", Px4ctrlDebug, lambda msg, uid=uid: self.on_debug(uid, msg), queue_size=100)
            rospy.Subscriber(f"/uav{uid}/livox/lidar", PointCloud2, lambda msg, uid=uid: self.on_raw_lidar(uid, msg), queue_size=20)
        rospy.Subscriber("/gazebo/model_states", ModelStates, self.on_model_states, queue_size=30)

    def start_xy_for(self, uid: int) -> tuple[float, float]:
        return (getattr(self.args, f"start{uid}_x"), getattr(self.args, f"start{uid}_y"))

    def now(self) -> float:
        stamp = rospy.Time.now().to_sec()
        return float(stamp) if stamp > 0 else time.time() - self.start_wall

    def should_record(self, uav: Uav, key: str, t: float, hz: float) -> bool:
        if hz <= 0:
            return True
        if t - uav.last_record_t[key] < 1.0 / hz:
            return False
        uav.last_record_t[key] = t
        return True

    @staticmethod
    def rpy_from_quat(x: float, y: float, z: float, w: float) -> tuple[float, float, float]:
        roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
        pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
        yaw = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
        return roll, pitch, yaw

    def on_state(self, uid: int, msg: State) -> None:
        self.uavs[uid].state = msg

    def on_model_states(self, msg: ModelStates) -> None:
        names = list(msg.name)
        t = self.now()
        for uid, uav in self.uavs.items():
            try:
                idx = names.index(f"uav{uid}")
            except ValueError:
                continue
            pose = msg.pose[idx]
            twist = msg.twist[idx]
            q = pose.orientation
            roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
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
            uav.truth = row
            if self.should_record(uav, "truth", t, self.args.record_hz):
                uav.truth_rows.append(row)
        self.update_separation(t)

    def on_odom(self, uid: int, msg: Odometry) -> None:
        uav = self.uavs[uid]
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        v = msg.twist.twist.linear
        roll, pitch, yaw = self.rpy_from_quat(q.x, q.y, q.z, q.w)
        row = {
            "t": self.now(),
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
        uav.odom = row
        if self.should_record(uav, "odom", row["t"], self.args.record_hz):
            uav.odom_rows.append(row)

    def on_att(self, uid: int, msg: AttitudeTarget) -> None:
        uav = self.uavs[uid]
        uav.target_attitude_count += 1
        t = self.now()
        if self.should_record(uav, "att", t, self.args.record_cmd_hz):
            uav.att_rows.append({"t": t, "phase": self.phase, "thrust": float(msg.thrust)})

    def on_debug(self, uid: int, msg: Px4ctrlDebug) -> None:
        uav = self.uavs[uid]
        uav.debug_count += 1
        t = self.now()
        if self.should_record(uav, "debug", t, self.args.record_cmd_hz):
            uav.debug_rows.append({"t": t, "phase": self.phase, "des_thr": float(msg.des_thr), "des_a_z": float(msg.des_a_z)})

    def on_raw_lidar(self, uid: int, msg: PointCloud2) -> None:
        uav = self.uavs[uid]
        uav.raw_lidar_count += 1
        uav.raw_lidar_points = int(msg.width * msg.height)

    def update_separation(self, t: float) -> None:
        ids = sorted(self.uavs)
        current_min = float("inf")
        current_pair = None
        for i, uid_a in enumerate(ids):
            a = self.uavs[uid_a].truth
            if not a:
                continue
            for uid_b in ids[i + 1:]:
                b = self.uavs[uid_b].truth
                if not b:
                    continue
                dist = math.dist((a["x"], a["y"], a["z"]), (b["x"], b["y"], b["z"]))
                if dist < current_min:
                    current_min = dist
                    current_pair = (uid_a, uid_b)
                if dist < self.min_inter_uav_distance:
                    self.min_inter_uav_distance = dist
                    self.min_inter_uav_pair = (uid_a, uid_b)
        if current_pair and t - self.last_sep_record_t >= 1.0 / self.args.record_hz:
            self.separation_rows.append({"t": t, "phase": self.phase, "uav_a": current_pair[0], "uav_b": current_pair[1], "distance_m": current_min})
            self.last_sep_record_t = t

    def make_hover_cmd(self, uav: Uav) -> PositionCommand:
        cmd_xy = uav.home_odom_xy if uav.home_odom_xy is not None else uav.start_xy
        msg = PositionCommand()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.args.path_frame
        msg.trajectory_flag = PositionCommand.TRAJECTORY_STATUS_READY
        msg.position.x = cmd_xy[0]
        msg.position.y = cmd_xy[1]
        msg.position.z = self.takeoff_target_z(uav)
        msg.yaw = self.args.yaw
        return msg

    def takeoff_target_z(self, uav: Uav) -> float:
        return (uav.home_odom_z or 0.0) + self.args.takeoff_height

    def publish_hover_cmds(self) -> None:
        for uav in self.uavs.values():
            uav.cmd_pub.publish(self.make_hover_cmd(uav))

    def publish_takeoff_land(self, cmd: int, repeats: int) -> None:
        msg = TakeoffLand()
        msg.takeoff_land_cmd = cmd
        for _ in range(repeats):
            for uav in self.uavs.values():
                uav.takeoff_land_pub.publish(msg)
            rospy.sleep(0.1)

    def all_ready(self) -> bool:
        return all(uav.state and uav.state.connected and uav.odom and uav.truth for uav in self.uavs.values())

    @staticmethod
    def rmse(values: list[float]) -> float | None:
        if not values:
            return None
        return math.sqrt(sum(v * v for v in values) / len(values))

    @staticmethod
    def pose_delta(a: dict | None, b: dict | None) -> dict | None:
        if not a or not b:
            return None
        dx = float(a["x"] - b["x"])
        dy = float(a["y"] - b["y"])
        dz = float(a["z"] - b["z"])
        return {
            "dx_m": dx,
            "dy_m": dy,
            "dz_m": dz,
            "dxy_m": math.hypot(dx, dy),
            "dxyz_m": math.sqrt(dx * dx + dy * dy + dz * dz),
        }

    def frame_alignment_summary(self, uav: Uav) -> dict:
        home_delta = None
        if uav.home_truth_xy is not None and uav.home_odom_xy is not None:
            dx = uav.home_odom_xy[0] - uav.home_truth_xy[0]
            dy = uav.home_odom_xy[1] - uav.home_truth_xy[1]
            home_delta = {
                "odom_minus_truth_dx_m": dx,
                "odom_minus_truth_dy_m": dy,
                "odom_minus_truth_dxy_m": math.hypot(dx, dy),
            }
        return {
            "home_truth_xy": None if uav.home_truth_xy is None else {"x": uav.home_truth_xy[0], "y": uav.home_truth_xy[1]},
            "home_odom_xy": None if uav.home_odom_xy is None else {"x": uav.home_odom_xy[0], "y": uav.home_odom_xy[1]},
            "home_odom_minus_truth": home_delta,
            "final_odom_minus_truth": self.pose_delta(uav.odom, uav.truth),
            "note": (
                "px4ctrl commands are generated in the MAVROS/PX4 local frame. "
                "Gazebo truth is evaluation-only; a large home odom-vs-truth "
                "offset means world-frame planner/evaluation targets must not "
                "be mixed with local-frame controller setpoints without a "
                "documented transform or PX4 EKF external-position alignment."
            ),
        }

    def run(self) -> int:
        rate = rospy.Rate(self.args.command_hz)
        ready_deadline = time.time() + self.args.ready_timeout_s
        while not rospy.is_shutdown() and time.time() < ready_deadline:
            if self.all_ready():
                break
            rate.sleep()
        if not self.all_ready():
            self.write_outputs("blocked", ["ready_timeout"])
            return 10
        for uav in self.uavs.values():
            if uav.truth:
                uav.home_truth_xy = (float(uav.truth["x"]), float(uav.truth["y"]))
                uav.home_truth_z = float(uav.truth["z"])
            if uav.odom:
                uav.home_odom_xy = (float(uav.odom["x"]), float(uav.odom["y"]))
                uav.home_odom_z = float(uav.odom["z"])

        self.phase = "takeoff"
        self.publish_takeoff_land(TakeoffLand.TAKEOFF, self.args.takeoff_cmd_repeats)
        reached_since: float | None = None
        takeoff_deadline = time.time() + self.args.takeoff_timeout_s
        while not rospy.is_shutdown() and time.time() < takeoff_deadline:
            self.publish_hover_cmds()
            if all(uav.odom and abs(uav.odom["z"] - self.takeoff_target_z(uav)) <= self.args.takeoff_z_tol for uav in self.uavs.values()):
                reached_since = reached_since or time.time()
                if time.time() - reached_since >= self.args.takeoff_hold_s:
                    break
            else:
                reached_since = None
            rate.sleep()
        if reached_since is None:
            self.write_outputs("blocked", ["takeoff_height_not_reached"])
            return 11

        self.phase = "hover"
        hover_start = self.now()
        while not rospy.is_shutdown() and self.now() - hover_start < self.args.hover_s:
            self.publish_hover_cmds()
            rate.sleep()

        self.phase = "land"
        rospy.sleep(self.args.pre_land_command_silence_s)
        self.publish_takeoff_land(TakeoffLand.LAND, self.args.land_cmd_repeats)
        land_deadline = time.time() + self.args.land_timeout_s
        while not rospy.is_shutdown() and time.time() < land_deadline:
            all_landed = all(
                uav.truth and uav.truth["z"] <= self.args.landed_z_max
                for uav in self.uavs.values()
            )
            all_disarmed = all(uav.state and not uav.state.armed for uav in self.uavs.values())
            if all_landed and (not self.args.require_disarmed or all_disarmed):
                break
            rate.sleep()

        blockers = self.acceptance_blockers()
        self.write_outputs("passed" if not blockers else "blocked", blockers)
        return 0 if not blockers else 12

    def hover_metrics(self, uav: Uav) -> dict:
        rows = [r for r in uav.truth_rows if r["phase"] == "hover"]
        if rows and self.args.steady_hover_tail_s > 0:
            t0 = rows[-1]["t"] - self.args.steady_hover_tail_s
            rows = [r for r in rows if r["t"] >= t0]
        home_truth_xy = uav.home_truth_xy if uav.home_truth_xy is not None else uav.start_xy
        xy = [math.hypot(r["x"] - home_truth_xy[0], r["y"] - home_truth_xy[1]) for r in rows]
        target_truth_z = (uav.home_truth_z or 0.0) + self.args.takeoff_height
        z = [abs(r["z"] - target_truth_z) for r in rows]
        return {
            "sample_count": len(rows),
            "xy_rmse_m": self.rmse(xy),
            "xy_max_m": max(xy) if xy else None,
            "z_abs_rmse_m": self.rmse(z),
            "z_abs_max_m": max(z) if z else None,
        }

    def acceptance_blockers(self) -> list[str]:
        blockers: list[str] = []
        if self.min_inter_uav_distance < self.args.min_inter_uav_distance:
            blockers.append("inter_uav_distance_below_gate")
        for uid, uav in self.uavs.items():
            prefix = f"uav{uid}_"
            metrics = self.hover_metrics(uav)
            if metrics["sample_count"] < self.args.min_hover_samples:
                blockers.append(prefix + "hover_samples_below_gate")
            for key, limit, label in (
                ("xy_rmse_m", self.args.max_hover_xy_rmse_m, "hover_xy_rmse_above_max"),
                ("xy_max_m", self.args.max_hover_xy_max_m, "hover_xy_max_above_max"),
                ("z_abs_rmse_m", self.args.max_hover_z_rmse_m, "hover_z_rmse_above_max"),
                ("z_abs_max_m", self.args.max_hover_z_max_m, "hover_z_max_above_max"),
            ):
                value = metrics.get(key)
                if value is None or value > limit:
                    blockers.append(f"{prefix}{label}:{value}")
            if not uav.truth or uav.truth["z"] > self.args.landed_z_max:
                blockers.append(prefix + "not_landed")
            if uav.state and uav.state.armed and self.args.require_disarmed:
                blockers.append(prefix + "final_state_still_armed")
            if uav.target_attitude_count < self.args.min_target_attitude_count:
                blockers.append(prefix + "target_attitude_count_below_gate")
            if uav.debug_count < self.args.min_debug_count:
                blockers.append(prefix + "debug_count_below_gate")
            if uav.raw_lidar_count < self.args.min_raw_lidar_count:
                blockers.append(prefix + "raw_lidar_count_below_gate")
            if uav.raw_lidar_points < self.args.min_raw_lidar_points:
                blockers.append(prefix + "raw_lidar_points_below_gate")
        return blockers

    @staticmethod
    def write_csv(path: Path, rows: list[dict]) -> None:
        if not rows:
            path.write_text("", encoding="utf-8")
            return
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    def write_outputs(self, status: str, blockers: list[str]) -> None:
        per_uav = {}
        for uid, uav in self.uavs.items():
            self.write_csv(self.result_dir / f"uav{uid}_truth.csv", uav.truth_rows)
            self.write_csv(self.result_dir / f"uav{uid}_odom.csv", uav.odom_rows)
            self.write_csv(self.result_dir / f"uav{uid}_target_attitude.csv", uav.att_rows)
            self.write_csv(self.result_dir / f"uav{uid}_debug_px4ctrl.csv", uav.debug_rows)
            per_uav[str(uid)] = {
                "start_xy": {"x": uav.start_xy[0], "y": uav.start_xy[1]},
                "home_truth_xy": None if uav.home_truth_xy is None else {"x": uav.home_truth_xy[0], "y": uav.home_truth_xy[1]},
                "home_truth_z": uav.home_truth_z,
                "home_odom_xy": None if uav.home_odom_xy is None else {"x": uav.home_odom_xy[0], "y": uav.home_odom_xy[1]},
                "home_odom_z": uav.home_odom_z,
                "takeoff_target_odom_z": self.takeoff_target_z(uav),
                "frame_alignment": self.frame_alignment_summary(uav),
                "final_truth": uav.truth,
                "final_odom": uav.odom,
                "final_state": None if uav.state is None else {"connected": uav.state.connected, "armed": uav.state.armed, "mode": uav.state.mode},
                "hover_metrics": self.hover_metrics(uav),
                "counts": {
                    "truth_rows": len(uav.truth_rows),
                    "odom_rows": len(uav.odom_rows),
                    "target_attitude": uav.target_attitude_count,
                    "debug_px4ctrl": uav.debug_count,
                    "raw_lidar": uav.raw_lidar_count,
                },
                "last_point_counts": {"raw_lidar": uav.raw_lidar_points},
            }
        self.write_csv(self.result_dir / "inter_uav_separation.csv", self.separation_rows)
        summary = {
            "schema": "mosim.sunray_ros1.px4ctrl_swarm_basic_metrics.v1",
            "status": status,
            "blockers": blockers,
            "uav_num": self.args.uav_num,
            "per_uav": per_uav,
            "min_inter_uav_distance_m": None if math.isinf(self.min_inter_uav_distance) else self.min_inter_uav_distance,
            "min_inter_uav_pair": self.min_inter_uav_pair,
            "claim_boundary": "Multi-UAV original px4ctrl/PX4/Gazebo takeoff-hover-land baseline only; no EGO-Swarm planning success claim.",
        }
        (self.result_dir / "PX4CTRL_SWARM_BASIC_METRICS.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--uav-num", type=int, choices=[2, 3], default=2)
    for uid, defaults in {1: (0.0, -1.0), 2: (0.0, 1.0), 3: (-1.5, 0.0)}.items():
        sx, sy = defaults
        parser.add_argument(f"--start{uid}-x", dest=f"start{uid}_x", type=float, default=sx)
        parser.add_argument(f"--start{uid}-y", dest=f"start{uid}_y", type=float, default=sy)
    parser.add_argument("--path-frame", default="world")
    parser.add_argument("--takeoff-height", type=float, default=1.0)
    parser.add_argument("--yaw", type=float, default=0.0)
    parser.add_argument("--ready-timeout-s", type=float, default=60.0)
    parser.add_argument("--takeoff-timeout-s", type=float, default=45.0)
    parser.add_argument("--takeoff-hold-s", type=float, default=2.0)
    parser.add_argument("--hover-s", type=float, default=10.0)
    parser.add_argument("--steady-hover-tail-s", type=float, default=6.0)
    parser.add_argument("--land-timeout-s", type=float, default=35.0)
    parser.add_argument("--pre-land-command-silence-s", type=float, default=0.8)
    parser.add_argument("--takeoff-z-tol", type=float, default=0.15)
    parser.add_argument("--landed-z-max", type=float, default=0.25)
    parser.add_argument("--command-hz", type=float, default=50.0)
    parser.add_argument("--record-hz", type=float, default=30.0)
    parser.add_argument("--record-cmd-hz", type=float, default=50.0)
    parser.add_argument("--min-hover-samples", type=int, default=30)
    parser.add_argument("--max-hover-xy-rmse-m", type=float, default=0.08)
    parser.add_argument("--max-hover-xy-max-m", type=float, default=0.15)
    parser.add_argument("--max-hover-z-rmse-m", type=float, default=0.08)
    parser.add_argument("--max-hover-z-max-m", type=float, default=0.15)
    parser.add_argument("--min-inter-uav-distance", type=float, default=0.45)
    parser.add_argument("--min-target-attitude-count", type=int, default=20)
    parser.add_argument("--min-debug-count", type=int, default=20)
    parser.add_argument("--min-raw-lidar-count", type=int, default=5)
    parser.add_argument("--min-raw-lidar-points", type=int, default=1)
    parser.add_argument("--takeoff-cmd-repeats", type=int, default=8)
    parser.add_argument("--land-cmd-repeats", type=int, default=8)
    parser.add_argument("--require-disarmed", action="store_true", default=False)
    return parser.parse_args()


def main() -> None:
    rospy.init_node("mosim_px4ctrl_swarm_basic_mission")
    raise SystemExit(SwarmBasicMission(parse_args()).run())


if __name__ == "__main__":
    main()
