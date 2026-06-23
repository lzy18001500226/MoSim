#!/usr/bin/env python3
"""Static contract checks for the ROS2 planner setpoint adapter package."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MSGS = ROOT / "Scripts" / "ros" / "mosim_msgs"
ADAPTER = ROOT / "Scripts" / "ros" / "mosim_setpoint_adapter"


def test_mosim_msgs_contract_fields() -> None:
    position = (MSGS / "msg" / "PositionCommand.msg").read_text(encoding="utf-8")
    for text in [
        "std_msgs/Header header",
        "geometry_msgs/Point position",
        "geometry_msgs/Vector3 velocity",
        "geometry_msgs/Vector3 acceleration",
        "float64 yaw",
        "float64 yaw_dot",
        "uint32 trajectory_id",
        "uint8 trajectory_flag",
    ]:
        if text not in position:
            raise AssertionError(text)

    planner = (MSGS / "msg" / "PlannerSetpoint.msg").read_text(encoding="utf-8")
    for text in [
        "std_msgs/Header header",
        "uint32 sequence",
        "string frame_id",
        "float64[3] position_m",
        "float64[3] velocity_mps",
        "float64[3] acceleration_mps2",
        "float64 yaw_rad",
        "float64 yaw_rate_radps",
        "uint8 trajectory_status",
        "string planner_id",
    ]:
        if text not in planner:
            raise AssertionError(text)
    status = (MSGS / "msg" / "SetpointAdapterStatus.msg").read_text(encoding="utf-8")
    for text in [
        "uint32 last_sequence",
        "bool accepted",
        "string reject_reason",
        "string mode",
        "bool stale",
        "float64 age_s",
        "string planner_id",
    ]:
        if text not in status:
            raise AssertionError(text)


def test_ros2_package_metadata_and_topics() -> None:
    msg_package = (MSGS / "package.xml").read_text(encoding="utf-8")
    if "<member_of_group>rosidl_interface_packages</member_of_group>" not in msg_package:
        raise AssertionError("mosim_msgs must be a rosidl interface package")
    if "rosidl_generate_interfaces" not in (MSGS / "CMakeLists.txt").read_text(encoding="utf-8"):
        raise AssertionError("mosim_msgs must generate interfaces")
    if "<depend>geometry_msgs</depend>" not in msg_package:
        raise AssertionError("mosim_msgs must depend on geometry_msgs for PositionCommand")

    adapter_package = (ADAPTER / "package.xml").read_text(encoding="utf-8")
    if "<depend>mosim_msgs</depend>" not in adapter_package:
        raise AssertionError("adapter package must depend on mosim_msgs")
    cmake = (ADAPTER / "CMakeLists.txt").read_text(encoding="utf-8")
    if "add_executable(planner_setpoint_adapter_node" not in cmake:
        raise AssertionError("adapter executable missing")
    if "add_executable(position_command_to_planner_setpoint_node" not in cmake:
        raise AssertionError("PositionCommand converter executable missing")

    source = (ADAPTER / "src" / "planner_setpoint_adapter_node.cpp").read_text(encoding="utf-8")
    for text in [
        "/mosim/planner/position_cmd",
        "/mosim/planner/setpoint",
        "/mosim/planner/setpoint_adapter_status",
        "frame_id_mismatch",
        "non_finite_setpoint",
        "non_monotonic_stamp",
        "non_monotonic_sequence",
        "stale_command",
        "no_command",
        "stale_timeout_s",
        "rate_hz",
    ]:
        if text not in source:
            raise AssertionError(text)

    converter = (ADAPTER / "src" / "position_command_to_planner_setpoint_node.cpp").read_text(encoding="utf-8")
    for text in [
        "/position_cmd",
        "/mosim/planner/position_cmd",
        "ego_position_cmd",
        "trajectory_id",
        "trajectory_flag",
        "yaw_dot",
        "source_frame_alias",
        "min_position_z_m",
    ]:
        if text not in converter:
            raise AssertionError(text)


def main() -> int:
    test_mosim_msgs_contract_fields()
    test_ros2_package_metadata_and_topics()
    print("[OK] ROS2 planner setpoint adapter static contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
