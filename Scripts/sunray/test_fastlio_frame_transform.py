#!/usr/bin/env python3
"""Offline checks for FAST-LIO Livox-body to UAV-base frame conversion."""

from __future__ import annotations

import math

from fastlio_frame_transform import (
    Pose3,
    angle_diff,
    livox_pose_to_base_pose,
    make_alignment,
    pose_mul,
    quat_from_rpy,
    rotate,
    yaw_from_quat,
)


def assert_close(actual: float, expected: float, tol: float = 1e-9) -> None:
    if abs(actual - expected) > tol:
        raise AssertionError(f"actual={actual}, expected={expected}, tol={tol}")


def assert_vec_close(actual, expected, tol: float = 1e-9) -> None:
    for a, e in zip(actual, expected):
        assert_close(a, e, tol)


def test_mount_yaw_is_removed() -> None:
    t_base_livox = Pose3((-0.000005, 0.032295, 0.050167), quat_from_rpy(0.0, 0.0, 4.712389))
    t_ref_base_truth = Pose3((1.0, 2.0, 3.0), quat_from_rpy(0.0, 0.0, 0.0))
    t_ref_livox = pose_mul(t_ref_base_truth, t_base_livox)

    recovered = livox_pose_to_base_pose(t_ref_livox, t_base_livox)

    assert_vec_close(recovered.p, t_ref_base_truth.p)
    assert_close(angle_diff(yaw_from_quat(recovered.q), 0.0), 0.0)
    assert_close(angle_diff(yaw_from_quat(t_ref_livox.q), 4.712389), 0.0)


def test_mount_translation_rotates_with_vehicle() -> None:
    t_base_livox = Pose3((0.1, 0.0, 0.2), quat_from_rpy(0.0, 0.0, -math.pi / 2.0))
    t_ref_base_truth = Pose3((2.0, -1.0, 0.5), quat_from_rpy(0.0, 0.0, math.pi / 2.0))
    t_ref_livox = pose_mul(t_ref_base_truth, t_base_livox)

    expected_livox_position = (
        t_ref_base_truth.p[0] + rotate(t_ref_base_truth.q, t_base_livox.p)[0],
        t_ref_base_truth.p[1] + rotate(t_ref_base_truth.q, t_base_livox.p)[1],
        t_ref_base_truth.p[2] + rotate(t_ref_base_truth.q, t_base_livox.p)[2],
    )
    assert_vec_close(t_ref_livox.p, expected_livox_position)

    recovered = livox_pose_to_base_pose(t_ref_livox, t_base_livox)
    assert_vec_close(recovered.p, t_ref_base_truth.p)
    assert_close(angle_diff(yaw_from_quat(recovered.q), math.pi / 2.0), 0.0)


def test_initial_alignment_removes_world_yaw_offset() -> None:
    t_fast_base0 = Pose3((10.0, 20.0, 1.0), quat_from_rpy(0.0, 0.0, math.radians(30.0)))
    t_local_base0 = Pose3((0.0, 0.0, 1.0), quat_from_rpy(0.0, 0.0, 0.0))
    t_local_fast = make_alignment(t_local_base0, t_fast_base0)

    t_fast_base1 = Pose3((10.0, 20.0, 1.0), quat_from_rpy(0.0, 0.0, math.radians(40.0)))
    t_local_base1 = pose_mul(t_local_fast, t_fast_base1)

    assert_close(angle_diff(yaw_from_quat(t_local_base1.q), math.radians(10.0)), 0.0)


def main() -> int:
    test_mount_yaw_is_removed()
    test_mount_translation_rotates_with_vehicle()
    test_initial_alignment_removes_world_yaw_offset()
    print("fastlio_frame_transform offline checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

