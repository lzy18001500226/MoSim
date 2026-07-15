#!/usr/bin/env python3
"""Convert HighStar SwarmTraj into px4ctrl-compatible PositionCommand.

This bridge intentionally does not publish MAVROS raw setpoints. It samples
HighStar's polynomial trajectory into a raw quadrotor_msgs/PositionCommand
stream, which can then be passed through MoSim's existing safety adapter before
px4ctrl sees it.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from pathlib import Path

import rospy
from geometry_msgs.msg import Point
from nav_msgs.msg import Odometry
from quadrotor_msgs.msg import PositionCommand
from swarm_exp_msgs.msg import SwarmTraj
from visualization_msgs.msg import Marker, MarkerArray


@dataclass
class Piece:
    duration: float
    coeff_p: list[list[float]]


@dataclass
class ActiveTrajectory:
    state: int
    start_wall: float
    pieces: list[Piece]
    yaw_durations: list[float]
    yaw_coeffs: list[list[float]]
    recover_pt: tuple[float, float, float] | None = None
    traj_id: int = 0

    @property
    def total_duration(self) -> float:
        return sum(piece.duration for piece in self.pieces)


class HighStarSwarmTrajPositionCmdBridge:
    def __init__(self) -> None:
        self.input_topic = rospy.get_param("~input_topic", "/Murder/Traj")
        self.output_topic = rospy.get_param("~output_topic", "/highstar/position_cmd_raw")
        self.odom_topic = rospy.get_param("~odom_topic", "/uav1/mavros/local_position/odom")
        self.marker_topic = rospy.get_param("~marker_topic", "/highstar/position_cmd_preview")
        self.rate_hz = float(rospy.get_param("~rate_hz", 50.0))
        self.max_v = float(rospy.get_param("~max_v", 1.5))
        self.max_a = float(rospy.get_param("~max_a", 1.5))
        self.max_yaw_rate = float(rospy.get_param("~max_yaw_rate", 1.5))
        self.max_yaw_acc = float(rospy.get_param("~max_yaw_acc", 1.5))
        self.retime_to_receive = bool(rospy.get_param("~retime_to_receive", True))
        self.start_delay_s = float(rospy.get_param("~start_delay_s", 0.10))
        self.end_fade_s = float(rospy.get_param("~end_fade_s", 0.25))
        self.hold_after_end_s = float(rospy.get_param("~hold_after_end_s", 2.0))
        self.recover_step_m = float(rospy.get_param("~recover_step_m", 0.3))
        self.frame_id = rospy.get_param("~frame_id", "world")
        self.diagnostics_path = rospy.get_param("~diagnostics_path", "")

        self.active: ActiveTrajectory | None = None
        self.pending: list[ActiveTrajectory] = []
        self.last_odom_xyz: tuple[float, float, float] | None = None
        self.last_odom_yaw = 0.0
        self.input_count = 0
        self.accepted_count = 0
        self.rejected_count = 0
        self.published_count = 0
        self.hold_published_count = 0
        self.last_reject_reason: str | None = None
        self.last_msg_summary: dict | None = None
        self.last_output: dict | None = None
        self.traj_id = 0

        self.pub = rospy.Publisher(self.output_topic, PositionCommand, queue_size=50)
        self.marker_pub = rospy.Publisher(self.marker_topic, MarkerArray, queue_size=2, latch=True)
        rospy.Subscriber(self.input_topic, SwarmTraj, self.on_traj, queue_size=10)
        rospy.Subscriber(self.odom_topic, Odometry, self.on_odom, queue_size=50)

    @staticmethod
    def clamp_norm(vec: tuple[float, float, float], limit: float) -> tuple[float, float, float]:
        if limit <= 0.0:
            return vec
        norm = math.sqrt(vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2])
        if norm <= limit or norm <= 1e-9:
            return vec
        scale = limit / norm
        return (vec[0] * scale, vec[1] * scale, vec[2] * scale)

    @staticmethod
    def eval_highstar_position_coeff(coeff: list[list[float]], t: float) -> tuple[float, float, float]:
        # HighStar/gcopter stores columns as [t^5, t^4, t^3, t^2, t, 1].
        out = [0.0, 0.0, 0.0]
        powers = [5, 4, 3, 2, 1, 0]
        for axis in range(3):
            out[axis] = sum(coeff[i][axis] * (t**powers[i]) for i in range(6))
        return (out[0], out[1], out[2])

    @staticmethod
    def eval_highstar_velocity_coeff(coeff: list[list[float]], t: float) -> tuple[float, float, float]:
        out = [0.0, 0.0, 0.0]
        powers = [4, 3, 2, 1, 0]
        factors = [5, 4, 3, 2, 1]
        for axis in range(3):
            out[axis] = sum(factors[i] * coeff[i][axis] * (t**powers[i]) for i in range(5))
        return (out[0], out[1], out[2])

    @staticmethod
    def eval_highstar_acc_coeff(coeff: list[list[float]], t: float) -> tuple[float, float, float]:
        out = [0.0, 0.0, 0.0]
        powers = [3, 2, 1, 0]
        factors = [20, 12, 6, 2]
        for axis in range(3):
            out[axis] = sum(factors[i] * coeff[i][axis] * (t**powers[i]) for i in range(4))
        return (out[0], out[1], out[2])

    @staticmethod
    def eval_highstar_jerk_coeff(coeff: list[list[float]], t: float) -> tuple[float, float, float]:
        out = [0.0, 0.0, 0.0]
        powers = [2, 1, 0]
        factors = [60, 24, 6]
        for axis in range(3):
            out[axis] = sum(factors[i] * coeff[i][axis] * (t**powers[i]) for i in range(3))
        return (out[0], out[1], out[2])

    @staticmethod
    def eval_yaw_coeff(coeff: list[float], t: float) -> tuple[float, float, float]:
        # HighStar yaw planner stores coefficients as [1, t, t^2, ..., t^5].
        yaw = sum(coeff[i] * (t**i) for i in range(6))
        yaw_rate = sum(i * coeff[i] * (t ** (i - 1)) for i in range(1, 6))
        yaw_acc = sum(i * (i - 1) * coeff[i] * (t ** (i - 2)) for i in range(2, 6))
        return yaw, yaw_rate, yaw_acc

    @staticmethod
    def yaw_norm(yaw: float) -> float:
        while yaw < -math.pi:
            yaw += 2.0 * math.pi
        while yaw > math.pi:
            yaw -= 2.0 * math.pi
        return yaw

    def on_odom(self, msg: Odometry) -> None:
        p = msg.pose.pose.position
        self.last_odom_xyz = (float(p.x), float(p.y), float(p.z))
        q = msg.pose.pose.orientation
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.last_odom_yaw = math.atan2(siny_cosp, cosy_cosp)

    def on_traj(self, msg: SwarmTraj) -> None:
        self.input_count += 1
        try:
            traj = self.parse_traj(msg)
        except ValueError as exc:
            self.rejected_count += 1
            self.last_reject_reason = str(exc)
            self.write_diagnostics()
            rospy.logwarn("Rejected HighStar SwarmTraj: %s", exc)
            return
        self.pending.append(traj)
        self.accepted_count += 1
        self.last_msg_summary = {
            "wall_time": time.time(),
            "state": int(msg.state),
            "start_t": float(msg.start_t),
            "piece_count": len(traj.pieces),
            "total_duration_s": traj.total_duration,
            "yaw_piece_count": len(traj.yaw_coeffs),
            "traj_id": traj.traj_id,
        }
        self.publish_preview(traj)
        self.write_diagnostics()

    def parse_traj(self, msg: SwarmTraj) -> ActiveTrajectory:
        self.traj_id += 1
        if int(msg.state) == 1:
            return ActiveTrajectory(
                state=1,
                start_wall=float(msg.start_t),
                pieces=[],
                yaw_durations=[],
                yaw_coeffs=[],
                recover_pt=(float(msg.recover_pt.x), float(msg.recover_pt.y), float(msg.recover_pt.z)),
                traj_id=self.traj_id,
            )
        if int(msg.state) != 2:
            raise ValueError(f"unsupported_state_{int(msg.state)}")
        if int(msg.order_p) != 5:
            raise ValueError(f"unsupported_position_order_{int(msg.order_p)}")
        if len(msg.coef_p) % 6 != 0:
            raise ValueError(f"position_coef_count_not_multiple_of_6:{len(msg.coef_p)}")
        piece_count = len(msg.coef_p) // 6
        if piece_count == 0:
            raise ValueError("empty_position_trajectory")
        if len(msg.t_p) < piece_count:
            raise ValueError(f"not_enough_position_durations:{len(msg.t_p)}<{piece_count}")

        pieces: list[Piece] = []
        for piece_idx in range(piece_count):
            coeff_points = msg.coef_p[piece_idx * 6 : (piece_idx + 1) * 6]
            coeff = [[float(p.x), float(p.y), float(p.z)] for p in coeff_points]
            duration = float(msg.t_p[piece_idx])
            if duration <= 0.0:
                raise ValueError(f"nonpositive_piece_duration:{duration}")
            pieces.append(Piece(duration=duration, coeff_p=coeff))

        if int(msg.order_yaw) != 5:
            raise ValueError(f"unsupported_yaw_order_{int(msg.order_yaw)}")
        if len(msg.coef_yaw) % 6 != 0:
            raise ValueError(f"yaw_coef_count_not_multiple_of_6:{len(msg.coef_yaw)}")
        yaw_piece_count = len(msg.coef_yaw) // 6
        if yaw_piece_count == 0:
            yaw_durations = [sum(float(t) for t in msg.t_p[:piece_count])]
            yaw_coeffs = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]
        else:
            if len(msg.t_yaw) < yaw_piece_count:
                raise ValueError(f"not_enough_yaw_durations:{len(msg.t_yaw)}<{yaw_piece_count}")
            yaw_durations = [float(t) for t in msg.t_yaw[:yaw_piece_count]]
            yaw_coeffs = [
                [float(x) for x in msg.coef_yaw[i * 6 : (i + 1) * 6]]
                for i in range(yaw_piece_count)
            ]
        start_wall = float(msg.start_t)
        if self.retime_to_receive:
            start_wall = time.time() + max(0.0, self.start_delay_s)
        return ActiveTrajectory(
            state=2,
            start_wall=start_wall,
            pieces=pieces,
            yaw_durations=yaw_durations,
            yaw_coeffs=yaw_coeffs,
            traj_id=self.traj_id,
        )

    def pop_ready_trajectory(self, wall_now: float) -> None:
        while self.pending and self.pending[0].start_wall <= wall_now:
            self.active = self.pending.pop(0)
            rospy.loginfo("Activated HighStar trajectory id=%d state=%d", self.active.traj_id, self.active.state)

    @staticmethod
    def locate_piece(pieces: list[Piece], t: float) -> tuple[Piece, float]:
        offset = 0.0
        for piece in pieces:
            if t <= offset + piece.duration:
                return piece, max(0.0, t - offset)
            offset += piece.duration
        return pieces[-1], max(0.0, pieces[-1].duration - 1e-4)

    @staticmethod
    def locate_yaw_piece(durations: list[float], coeffs: list[list[float]], t: float) -> tuple[list[float], float]:
        offset = 0.0
        for idx, duration in enumerate(durations):
            if t <= offset + duration:
                return coeffs[min(idx, len(coeffs) - 1)], max(0.0, t - offset)
            offset += duration
        return coeffs[-1], max(0.0, durations[-1] - 1e-4)

    def sample_active(self, wall_now: float) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], float, float] | None:
        if self.active is None:
            return None
        if self.active.state == 1:
            if self.last_odom_xyz is None or self.active.recover_pt is None:
                return None
            dx = self.active.recover_pt[0] - self.last_odom_xyz[0]
            dy = self.active.recover_pt[1] - self.last_odom_xyz[1]
            dz = self.active.recover_pt[2] - self.last_odom_xyz[2]
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            scale = min(distance, self.recover_step_m) / max(distance, 1e-9)
            pos = (
                self.last_odom_xyz[0] + dx * scale,
                self.last_odom_xyz[1] + dy * scale,
                self.last_odom_xyz[2] + dz * scale,
            )
            return pos, (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), self.last_odom_yaw, 0.0

        elapsed = wall_now - self.active.start_wall
        total = self.active.total_duration
        if elapsed > total + self.hold_after_end_s:
            return None
        eval_t = min(max(elapsed, 0.0), max(total - 1e-4, 0.0))
        piece, local_t = self.locate_piece(self.active.pieces, eval_t)
        pos = self.eval_highstar_position_coeff(piece.coeff_p, local_t)
        vel = self.eval_highstar_velocity_coeff(piece.coeff_p, local_t)
        acc = self.eval_highstar_acc_coeff(piece.coeff_p, local_t)
        jerk = self.eval_highstar_jerk_coeff(piece.coeff_p, local_t)

        if elapsed >= total:
            fade = max(0.0, min(1.0, (self.end_fade_s + total - elapsed) / max(self.end_fade_s, 1e-6)))
            vel = (vel[0] * fade, vel[1] * fade, vel[2] * fade)
            acc = (acc[0] * fade, acc[1] * fade, acc[2] * fade)
            jerk = (jerk[0] * fade, jerk[1] * fade, jerk[2] * fade)

        vel = self.clamp_norm(vel, self.max_v)
        acc = self.clamp_norm(acc, self.max_a)
        yaw_coeff, yaw_t = self.locate_yaw_piece(self.active.yaw_durations, self.active.yaw_coeffs, eval_t)
        yaw, yaw_rate, _yaw_acc = self.eval_yaw_coeff(yaw_coeff, yaw_t)
        yaw = self.yaw_norm(yaw)
        yaw_rate = max(-self.max_yaw_rate, min(self.max_yaw_rate, yaw_rate))
        return pos, vel, acc, jerk, yaw, yaw_rate

    def make_position_cmd(
        self,
        sample: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], tuple[float, float, float], float, float],
    ) -> PositionCommand:
        pos, vel, acc, jerk, yaw, yaw_rate = sample
        msg = PositionCommand()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.frame_id
        msg.trajectory_id = self.active.traj_id if self.active is not None else 0
        msg.trajectory_flag = getattr(PositionCommand, "TRAJECTORY_STATUS_READY", 1)
        msg.position.x, msg.position.y, msg.position.z = pos
        msg.velocity.x, msg.velocity.y, msg.velocity.z = vel
        msg.acceleration.x, msg.acceleration.y, msg.acceleration.z = acc
        if hasattr(msg, "jerk"):
            msg.jerk.x, msg.jerk.y, msg.jerk.z = jerk
        msg.yaw = yaw
        msg.yaw_dot = yaw_rate
        msg.kx = [0.0, 0.0, 0.0]
        msg.kv = [0.0, 0.0, 0.0]
        return msg

    def publish_preview(self, traj: ActiveTrajectory) -> None:
        if traj.state != 2:
            return
        marker = Marker()
        marker.header.stamp = rospy.Time.now()
        marker.header.frame_id = self.frame_id
        marker.ns = "highstar_swarmtraj_preview"
        marker.id = traj.traj_id
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.08
        marker.color.r = 0.1
        marker.color.g = 0.9
        marker.color.b = 0.2
        marker.color.a = 1.0
        total = traj.total_duration
        step = max(0.05, min(0.25, total / 80.0))
        t = 0.0
        while t <= total:
            piece, local_t = self.locate_piece(traj.pieces, t)
            xyz = self.eval_highstar_position_coeff(piece.coeff_p, local_t)
            pt = Point()
            pt.x, pt.y, pt.z = xyz
            marker.points.append(pt)
            t += step
        self.marker_pub.publish(MarkerArray(markers=[marker]))

    def write_diagnostics(self) -> None:
        if not self.diagnostics_path:
            return
        path = Path(self.diagnostics_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema": "mosim.sunray_ros1.highstar_swarmtraj_position_cmd_bridge.v1",
            "input_topic": self.input_topic,
            "output_topic": self.output_topic,
            "odom_topic": self.odom_topic,
            "marker_topic": self.marker_topic,
            "rate_hz": self.rate_hz,
            "retime_to_receive": self.retime_to_receive,
            "start_delay_s": self.start_delay_s,
            "input_count": self.input_count,
            "accepted_count": self.accepted_count,
            "rejected_count": self.rejected_count,
            "published_count": self.published_count,
            "hold_published_count": self.hold_published_count,
            "pending_count": len(self.pending),
            "active_traj_id": self.active.traj_id if self.active else None,
            "active_state": self.active.state if self.active else None,
            "last_reject_reason": self.last_reject_reason,
            "last_msg_summary": self.last_msg_summary,
            "last_output": self.last_output,
            "last_odom_xyz": self.last_odom_xyz,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def spin(self) -> None:
        rate = rospy.Rate(self.rate_hz)
        while not rospy.is_shutdown():
            wall_now = time.time()
            self.pop_ready_trajectory(wall_now)
            sample = self.sample_active(wall_now)
            if sample is not None:
                msg = self.make_position_cmd(sample)
                self.pub.publish(msg)
                self.published_count += 1
                if self.active is not None and self.active.state == 2:
                    elapsed = wall_now - self.active.start_wall
                    if elapsed >= self.active.total_duration:
                        self.hold_published_count += 1
                self.last_output = {
                    "wall_time": wall_now,
                    "trajectory_id": int(msg.trajectory_id),
                    "trajectory_flag": int(msg.trajectory_flag),
                    "position": [msg.position.x, msg.position.y, msg.position.z],
                    "velocity": [msg.velocity.x, msg.velocity.y, msg.velocity.z],
                    "acceleration": [msg.acceleration.x, msg.acceleration.y, msg.acceleration.z],
                    "yaw": msg.yaw,
                    "yaw_dot": msg.yaw_dot,
                }
            self.write_diagnostics()
            rate.sleep()


def main() -> None:
    rospy.init_node("mosim_highstar_swarmtraj_position_cmd_bridge", anonymous=True)
    HighStarSwarmTrajPositionCmdBridge().spin()


if __name__ == "__main__":
    main()
