#!/usr/bin/env python3
"""Static contract check for the guarded MoSim PX4 Offboard adapter."""

from __future__ import annotations

import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> int:
    package = ROOT / "Scripts" / "ros" / "mosim_px4_offboard_adapter"
    source = package / "src" / "planner_setpoint_to_px4_offboard_node.cpp"
    cmake = package / "CMakeLists.txt"
    package_xml = package / "package.xml"
    text = source.read_text(encoding="utf-8")
    cmake_text = cmake.read_text(encoding="utf-8")
    package_text = package_xml.read_text(encoding="utf-8")

    required_snippets = {
        "px4_offboard_mode_pub": "px4_msgs::msg::OffboardControlMode",
        "px4_trajectory_pub": "px4_msgs::msg::TrajectorySetpoint",
        "px4_vehicle_command_pub": "px4_msgs::msg::VehicleCommand",
        "planner_setpoint_input": "mosim_msgs::msg::PlannerSetpoint",
        "default_no_auto_arm": 'declare_parameter<bool>("auto_arm", false)',
        "default_no_auto_offboard": 'declare_parameter<bool>("auto_offboard", false)',
        "stale_guard": "stale_timeout_s_",
        "rate_guard": "publish_rate_hz_ < 5.0",
        "enu_to_ned_conversion": 'frame_mode == "enu_to_ned"',
        "local_ned_passthrough": 'frame_mode == "local_ned"',
        "position_mode_only": "message.position = true;",
        "no_direct_actuator": "message.direct_actuator = false;",
        "warmup_before_mode": "published_setpoint_count_ >= static_cast<std::uint64_t>(warmup_setpoint_count_)",
    }
    missing = [name for name, snippet in required_snippets.items() if snippet not in text]
    cmake_missing = [snippet for snippet in ["find_package(px4_msgs REQUIRED)", "planner_setpoint_to_px4_offboard_node"] if snippet not in cmake_text]
    package_missing = [snippet for snippet in ["<depend>px4_msgs</depend>", "<depend>mosim_msgs</depend>"] if snippet not in package_text]

    payload = {
        "schema": "mosim.px4_offboard_adapter_contract.v1",
        "status": "passed" if not missing and not cmake_missing and not package_missing else "failed",
        "source": rel(source),
        "cmake": rel(cmake),
        "package_xml": rel(package_xml),
        "checked_contracts": sorted(required_snippets),
        "missing_contracts": missing,
        "cmake_missing": cmake_missing,
        "package_missing": package_missing,
        "claim_boundary": [
            "Static/source contract only: no PX4 SITL, Gazebo, uXRCE-DDS agent, or vehicle was started.",
            "Default parameters do not arm or switch to Offboard; live takeover requires explicit auto_arm/auto_offboard enablement.",
            "This adapter publishes PX4 position-mode Offboard heartbeat and TrajectorySetpoint, not direct actuator commands.",
        ],
    }
    output = ROOT / "Results" / "generated_mworks" / "AWFF_FullController_Sysblock_20260620_032747" / "px4_offboard_adapter_contract.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
