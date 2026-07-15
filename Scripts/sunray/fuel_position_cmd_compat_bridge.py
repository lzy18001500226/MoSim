#!/usr/bin/env python3
"""Bridge older FUEL/RACER PositionCommand wire format to MoSim px4ctrl."""

from __future__ import annotations

import json
import struct
import time
from pathlib import Path

import rospy
from rospy.msg import AnyMsg
from quadrotor_msgs.msg import PositionCommand


class LegacyPositionCommandCompatBridge:
    def __init__(self) -> None:
        self.input_topic = rospy.get_param("~input_topic", "/fuel/position_cmd_fuel_raw")
        self.output_topic = rospy.get_param("~output_topic", "/fuel/position_cmd_raw")
        self.gate_bspline_topic = rospy.get_param("~gate_bspline_topic", "/planning/bspline")
        self.forward_before_first_bspline = bool(rospy.get_param("~forward_before_first_bspline", False))
        self.output_offset_x = float(rospy.get_param("~output_offset_x", 0.0))
        self.output_offset_y = float(rospy.get_param("~output_offset_y", 0.0))
        self.output_offset_z = float(rospy.get_param("~output_offset_z", 0.0))
        self.diagnostics_path = rospy.get_param("~diagnostics_path", "")

        self.raw_count = 0
        self.forwarded_count = 0
        self.ignored_before_gate_count = 0
        self.decode_error_count = 0
        self.first_bspline_seen = False
        self.first_bspline_wall: float | None = None
        self.last_decode_error: str | None = None
        self.last_msg: dict | None = None
        self.last_diagnostics_wall = 0.0
        self.diagnostics_interval_s = float(rospy.get_param("~diagnostics_interval_s", 1.0))

        self.pub = rospy.Publisher(self.output_topic, PositionCommand, queue_size=50)
        # Position commands are a latest-state stream. Processing queued stale
        # commands after planner load creates artificial trajectory jumps.
        rospy.Subscriber(self.input_topic, AnyMsg, self.on_raw, queue_size=1)
        rospy.Subscriber(self.gate_bspline_topic, AnyMsg, self.on_bspline, queue_size=10)

    @staticmethod
    def read_u32(buf: bytes, offset: int) -> tuple[int, int]:
        return struct.unpack_from("<I", buf, offset)[0], offset + 4

    @staticmethod
    def read_u8(buf: bytes, offset: int) -> tuple[int, int]:
        return struct.unpack_from("<B", buf, offset)[0], offset + 1

    @staticmethod
    def read_f64(buf: bytes, offset: int) -> tuple[float, int]:
        return struct.unpack_from("<d", buf, offset)[0], offset + 8

    @classmethod
    def read_vec3(cls, buf: bytes, offset: int) -> tuple[list[float], int]:
        values = []
        for _ in range(3):
            value, offset = cls.read_f64(buf, offset)
            values.append(value)
        return values, offset

    @classmethod
    def decode_legacy_position_command(cls, buf: bytes) -> PositionCommand:
        msg = PositionCommand()
        offset = 0
        seq, offset = cls.read_u32(buf, offset)
        secs, offset = cls.read_u32(buf, offset)
        nsecs, offset = cls.read_u32(buf, offset)
        frame_len, offset = cls.read_u32(buf, offset)
        frame_bytes = buf[offset : offset + frame_len]
        offset += frame_len

        position, offset = cls.read_vec3(buf, offset)
        velocity, offset = cls.read_vec3(buf, offset)
        acceleration, offset = cls.read_vec3(buf, offset)
        yaw, offset = cls.read_f64(buf, offset)
        yaw_dot, offset = cls.read_f64(buf, offset)
        kx, offset = cls.read_vec3(buf, offset)
        kv, offset = cls.read_vec3(buf, offset)
        trajectory_id, offset = cls.read_u32(buf, offset)
        trajectory_flag, offset = cls.read_u8(buf, offset)

        msg.header.seq = seq
        msg.header.stamp = rospy.Time(secs, nsecs)
        msg.header.frame_id = frame_bytes.decode("utf-8", errors="replace") or "world"
        msg.position.x, msg.position.y, msg.position.z = position
        msg.velocity.x, msg.velocity.y, msg.velocity.z = velocity
        msg.acceleration.x, msg.acceleration.y, msg.acceleration.z = acceleration
        msg.jerk.x = 0.0
        msg.jerk.y = 0.0
        msg.jerk.z = 0.0
        msg.yaw = yaw
        msg.yaw_dot = yaw_dot
        msg.kx = kx
        msg.kv = kv
        msg.trajectory_id = trajectory_id
        msg.trajectory_flag = trajectory_flag
        return msg

    def on_bspline(self, _msg: AnyMsg) -> None:
        if not self.first_bspline_seen:
            self.first_bspline_seen = True
            self.first_bspline_wall = time.time()
            self.write_diagnostics(force=True)

    def on_raw(self, raw: AnyMsg) -> None:
        self.raw_count += 1
        if not self.first_bspline_seen and not self.forward_before_first_bspline:
            self.ignored_before_gate_count += 1
            self.write_diagnostics()
            return
        try:
            msg = self.decode_legacy_position_command(raw._buff)
        except Exception as exc:  # noqa: BLE001 - diagnostics bridge must preserve malformed samples.
            self.decode_error_count += 1
            self.last_decode_error = repr(exc)
            self.write_diagnostics(force=True)
            return

        msg.header.stamp = rospy.Time.now()
        if not msg.header.frame_id:
            msg.header.frame_id = "world"
        msg.position.x += self.output_offset_x
        msg.position.y += self.output_offset_y
        msg.position.z += self.output_offset_z
        self.pub.publish(msg)
        self.forwarded_count += 1
        self.last_msg = {
            "wall_time": time.time(),
            "trajectory_id": int(msg.trajectory_id),
            "trajectory_flag": int(msg.trajectory_flag),
            "position": [msg.position.x, msg.position.y, msg.position.z],
            "velocity": [msg.velocity.x, msg.velocity.y, msg.velocity.z],
            "acceleration": [msg.acceleration.x, msg.acceleration.y, msg.acceleration.z],
            "yaw": msg.yaw,
            "yaw_dot": msg.yaw_dot,
        }
        self.write_diagnostics()

    def write_diagnostics(self, *, force: bool = False) -> None:
        if not self.diagnostics_path:
            return
        now = time.time()
        if not force and now - self.last_diagnostics_wall < self.diagnostics_interval_s:
            return
        self.last_diagnostics_wall = now
        path = Path(self.diagnostics_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema": "mosim.sunray_ros1.legacy_position_cmd_compat_bridge.v1",
            "input_topic": self.input_topic,
            "output_topic": self.output_topic,
            "gate_bspline_topic": self.gate_bspline_topic,
            "forward_before_first_bspline": self.forward_before_first_bspline,
            "output_offset_xyz": [self.output_offset_x, self.output_offset_y, self.output_offset_z],
            "first_bspline_seen": self.first_bspline_seen,
            "first_bspline_wall": self.first_bspline_wall,
            "raw_count": self.raw_count,
            "forwarded_count": self.forwarded_count,
            "ignored_before_gate_count": self.ignored_before_gate_count,
            "decode_error_count": self.decode_error_count,
            "last_decode_error": self.last_decode_error,
            "last_msg": self.last_msg,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def spin(self) -> None:
        rate = rospy.Rate(1.0)
        while not rospy.is_shutdown():
            self.write_diagnostics(force=True)
            rate.sleep()
        self.write_diagnostics(force=True)


def main() -> None:
    rospy.init_node("mosim_legacy_position_cmd_compat_bridge", anonymous=True)
    LegacyPositionCommandCompatBridge().spin()


if __name__ == "__main__":
    main()
