#!/usr/bin/env python3
"""Frame math for converting FAST-LIO Livox-body odometry to UAV base odometry."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple


Vec3 = Tuple[float, float, float]
Quat = Tuple[float, float, float, float]  # x, y, z, w


@dataclass(frozen=True)
class Pose3:
    p: Vec3
    q: Quat


def vec_add(a: Vec3, b: Vec3) -> Vec3:
    return a[0] + b[0], a[1] + b[1], a[2] + b[2]


def vec_sub(a: Vec3, b: Vec3) -> Vec3:
    return a[0] - b[0], a[1] - b[1], a[2] - b[2]


def quat_norm(q: Quat) -> Quat:
    x, y, z, w = q
    n = math.sqrt(x * x + y * y + z * z + w * w)
    if n <= 0.0:
        return 0.0, 0.0, 0.0, 1.0
    return x / n, y / n, z / n, w / n


def quat_mul(a: Quat, b: Quat) -> Quat:
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return quat_norm(
        (
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw,
            aw * bw - ax * bx - ay * by - az * bz,
        )
    )


def quat_inv(q: Quat) -> Quat:
    x, y, z, w = quat_norm(q)
    return -x, -y, -z, w


def rotate(q: Quat, v: Vec3) -> Vec3:
    x, y, z, w = quat_norm(q)
    vx, vy, vz = v
    tx = 2.0 * (y * vz - z * vy)
    ty = 2.0 * (z * vx - x * vz)
    tz = 2.0 * (x * vy - y * vx)
    return (
        vx + w * tx + (y * tz - z * ty),
        vy + w * ty + (z * tx - x * tz),
        vz + w * tz + (x * ty - y * tx),
    )


def quat_from_rpy(roll: float, pitch: float, yaw: float) -> Quat:
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    return quat_norm(
        (
            sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy,
            cr * cp * sy - sr * sp * cy,
            cr * cp * cy + sr * sp * sy,
        )
    )


def yaw_from_quat(q: Quat) -> float:
    x, y, z, w = quat_norm(q)
    return math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))


def pose_inv(t_ab: Pose3) -> Pose3:
    q_ba = quat_inv(t_ab.q)
    p_ba = rotate(q_ba, (-t_ab.p[0], -t_ab.p[1], -t_ab.p[2]))
    return Pose3(p_ba, q_ba)


def pose_mul(t_ab: Pose3, t_bc: Pose3) -> Pose3:
    return Pose3(
        vec_add(t_ab.p, rotate(t_ab.q, t_bc.p)),
        quat_mul(t_ab.q, t_bc.q),
    )


def livox_pose_to_base_pose(t_ref_livox: Pose3, t_base_livox: Pose3) -> Pose3:
    """Return T_ref_base from T_ref_livox and fixed T_base_livox."""

    return pose_mul(t_ref_livox, pose_inv(t_base_livox))


def make_alignment(t_local_base0: Pose3, t_fast_base0: Pose3) -> Pose3:
    """Return fixed T_local_fast so T_local_base = T_local_fast * T_fast_base."""

    return pose_mul(t_local_base0, pose_inv(t_fast_base0))


def transform_velocity(q_local_fast: Quat, v_fast: Vec3) -> Vec3:
    return rotate(q_local_fast, v_fast)


def angle_diff(a: float, b: float) -> float:
    d = (a - b + math.pi) % (2.0 * math.pi) - math.pi
    return d
