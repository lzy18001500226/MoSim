#!/usr/bin/env python3
"""Static contract checks for the ROS2 dense LiDAR C++ package."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "Scripts" / "ros" / "mosim_dense_lidar_cpp"


def test_dense_lidar_cpp_contract() -> None:
    cmake = (PKG / "CMakeLists.txt").read_text(encoding="utf-8")
    publisher = (PKG / "src" / "dense_lidar_replay_node.cpp").read_text(encoding="utf-8")
    subscriber = (PKG / "src" / "dense_lidar_subscriber_probe_node.cpp").read_text(encoding="utf-8")
    imu_replay = (PKG / "src" / "mworks_state_imu_replay_node.cpp").read_text(encoding="utf-8")

    for target in ("dense_lidar_replay_node", "dense_lidar_subscriber_probe_node"):
        if target not in cmake:
            raise AssertionError(f"missing CMake target: {target}")

    for field in ("offset_time", "x", "y", "z", "intensity", "tag", "line"):
        if field not in publisher:
            raise AssertionError(f"publisher missing Livox field {field}")
        if field not in subscriber:
            raise AssertionError(f"subscriber missing Livox field {field}")

    if "msg.point_step = 22" not in publisher:
        raise AssertionError("publisher should use compact Livox-compatible PointCloud2 point_step=22")
    if "livox_ros_driver2" not in cmake:
        raise AssertionError("publisher must declare livox_ros_driver2 for CustomMsg output")
    if "livox_topic" not in publisher or "CustomMsg" not in publisher:
        raise AssertionError("publisher should optionally publish Livox CustomMsg for FAST-LIO")
    if "rclcpp::QoS(rclcpp::KeepLast(20)).reliable()" not in publisher:
        raise AssertionError("Livox CustomMsg publisher must use reliable QoS for FAST-LIO subscription compatibility")
    if "msg.header.stamp = now();" in publisher:
        raise AssertionError("dense LiDAR replay must not assign per-message header stamps from node.now()")
    for marker in (
        "replay_start_stamp_ = now();",
        "replay_stamp_for_index(index_)",
        "rclcpp::Duration::from_seconds(replay_elapsed_s)",
        "livox_msg.header.stamp = msg.header.stamp",
    ):
        if marker not in publisher:
            raise AssertionError(f"publisher missing monotonic replay-clock marker: {marker}")
    for marker in (
        'declare_parameter<bool>("loop", true)',
        'declare_parameter<bool>("exit_after_last_frame", false)',
        "finish_non_looping_replay()",
        'completed non-looping dense LiDAR replay after %zu/%zu frames',
        "frames_[loop_ ? index_ % frames_.size() : index_]",
    ):
        if marker not in publisher:
            raise AssertionError(f"publisher missing no-loopback replay marker: {marker}")
    package_xml = (PKG / "package.xml").read_text(encoding="utf-8")
    if "<depend>livox_ros_driver2</depend>" not in package_xml:
        raise AssertionError("package.xml must declare livox_ros_driver2 dependency")
    if "subscriber-side PointCloud2 contract and throughput probe; not FAST-LIO evidence" not in subscriber:
        raise AssertionError("subscriber probe must not claim FAST-LIO evidence")
    if "double second_finite_diff(" not in imu_replay:
        raise AssertionError("MWORKS IMU replay must compute linear acceleration with a second derivative")
    for axis in ("x", "y", "z"):
        if f"imu.linear_acceleration.{axis} = finite_diff" in imu_replay:
            raise AssertionError("MWORKS IMU replay must not publish velocity as linear acceleration")
    if "imu.linear_acceleration.z = second_finite_diff(rows_, index, &Row::z) + 9.81" not in imu_replay:
        raise AssertionError("MWORKS IMU replay must publish specific force with explicit gravity convention")
    if "std::min(tick_count_ / truth_stride_, rows_.size() - 1)" not in imu_replay:
        raise AssertionError("MWORKS IMU replay must hold the final row instead of looping finite rows and creating trajectory/time discontinuities")


def main() -> int:
    test_dense_lidar_cpp_contract()
    print("[OK] dense LiDAR C++ contract regression")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
