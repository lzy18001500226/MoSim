#!/usr/bin/env python3
"""Audit the current Sunray ROS1 control-feedback and IMU source wiring.

This is a source/config audit only. It does not prove runtime topic rates or
PX4 estimator fusion; runtime gates must still record ROS topics in a run dir.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def find_text(path: Path, pattern: str) -> bool:
    return re.search(pattern, read_text(path), re.MULTILINE) is not None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--out")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    sunray_model = root / "References/Sunray/simulation/sunray_simulator/models/drone_models/sunray150_with_mid360/sunray150_with_mid360.sdf"
    mid360_model = root / "References/Sunray/simulation/sunray_simulator/models/sensor_models/livox_mid360/livox_mid360.sdf"
    external_fusion = root / "References/Sunray/General_Module/sunray_uav_control/externalFusion/externalFusion.cpp"
    external_position = root / "References/Sunray/General_Module/sunray_uav_control/externalFusion/ExternalPosition.h"
    uav_control = root / "References/Sunray/General_Module/sunray_uav_control/uav_control/UAVControl.cpp"
    mission = root / "Scripts/sunray/sunray_ros1_mission_node.py"
    fastlio_config = root / "References/Lab/FAST_LIO/config/mosim_sunray_livox_custom.yaml"

    paths = {
        "sunray_model": sunray_model,
        "mid360_model": mid360_model,
        "external_fusion": external_fusion,
        "external_position": external_position,
        "uav_control": uav_control,
        "mission": mission,
        "fastlio_config": fastlio_config,
    }
    missing = [name for name, path in paths.items() if not path.exists()]

    audit = {
        "schema": "mosim.sunray_ros1_feedback_source_audit.v1",
        "status": "blocked" if missing else "audited",
        "project_root": str(root),
        "missing": missing,
        "control_chain": {
            "mission_command_topic": "/uav1/sunray/uav_control_cmd",
            "sunray_control_feedback_topic": "/uav1/sunray/px4_state",
            "px4_setpoint_topic": "/uav1/mavros/setpoint_raw/local",
            "current_feedback_source": "PX4/MAVROS state unless external_fusion/PX4 fusion of FAST-LIO odometry is separately proven",
        },
        "imu_sources": {
            "flight_controller_imu": {
                "gazebo_topic": "/imu",
                "px4_input": "mavlink imuSubTopic /imu",
                "mavros_output": "/uav1/mavros/imu/data",
                "used_for_current_control_feedback": True,
            },
            "mid360_internal_imu": {
                "gazebo_topic": "/uav1/livox/imu",
                "fastlio_config_topic": "/uav1/livox/imu",
                "used_for_fastlio": True,
                "used_for_current_control_feedback": False,
            },
        },
        "source_checks": {},
        "claim_boundary": [
            "This audit is source/config evidence only.",
            "Current default Gazebo mission control feedback is PX4/MAVROS state, not direct MID360 IMU or FAST-LIO odometry.",
            "FAST-LIO becomes controller feedback only after external_fusion/PX4 fusion is launched and runtime-proven.",
        ],
    }

    if not missing:
        audit["source_checks"] = {
            "sdf_mavlink_imu_subtopic_is_imu": find_text(sunray_model, r"<imuSubTopic>/imu</imuSubTopic>"),
            "sdf_body_imu_topic_is_imu": find_text(sunray_model, r"<imuTopic>/imu</imuTopic>"),
            "mid360_imu_topic_is_livox_imu": find_text(mid360_model, r"<topicName>livox/imu</topicName>"),
            "external_fusion_reads_mavros_pose": find_text(external_fusion, r"/mavros/local_position/pose"),
            "external_fusion_reads_mavros_velocity": find_text(external_fusion, r"/mavros/local_position/velocity_local"),
            "external_fusion_reads_mavros_imu": find_text(external_fusion, r"/mavros/imu/data"),
            "external_position_can_publish_vision_pose": find_text(external_position, r"/mavros/vision_pose/pose"),
            "uav_control_consumes_px4_state": find_text(uav_control, r"px4_state_sub.*sunray/px4_state"),
            "mission_records_mavros_pose": find_text(mission, r"mavros/local_position/pose"),
            "fastlio_config_uses_livox_imu": find_text(fastlio_config, r'imu_topic:\s*"/uav1/livox/imu"'),
        }

    output = json.dumps(audit, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output, encoding="utf-8")
    print(output, end="")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
