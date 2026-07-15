#!/usr/bin/env python3
"""Build a static source audit packet for the local FALCON reference."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FALCON_ROOT = ROOT / "References" / "Lab" / "exploration_coverage" / "FALCON-ros1-noetic"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def exists_rel(rel: str) -> bool:
    return (FALCON_ROOT / rel).exists()


def grep(pattern: str, rels: list[str]) -> list[dict[str, object]]:
    rx = re.compile(pattern)
    hits: list[dict[str, object]] = []
    for rel in rels:
        path = FALCON_ROOT / rel
        if not path.exists():
            continue
        for idx, line in enumerate(read_text(path).splitlines(), 1):
            if rx.search(line):
                hits.append({"file": rel, "line": idx, "text": line.strip()})
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="")
    args = parser.parse_args()

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.out_dir) if args.out_dir else ROOT / "Results" / "sunray_ros1" / f"falcon_d0_source_audit_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    key_files = {
        "readme": "README.md",
        "exploration_launch": "falcon_planner/exploration_manager/launch/exploration.launch",
        "exploration_manager_yaml": "falcon_planner/exploration_manager/config/exploration_manager.yaml",
        "voxel_mapping_yaml": "falcon_planner/voxel_mapping/config/voxel_mapping.yaml",
        "map_example": "falcon_planner/exploration_manager/config/map/complex_office.yaml",
        "exploration_fsm": "falcon_planner/exploration_manager/src/exploration_fsm.cpp",
        "voxel_map_server": "falcon_planner/voxel_mapping/src/map_server.cpp",
        "traj_server": "falcon_planner/fast_planner/src/traj_server.cpp",
        "trajectory_msg": "falcon_planner/trajectory/msg/Bspline.msg",
        "position_command_msg": "uav_simulator/utils/quadrotor_msgs/msg/PositionCommand.msg",
    }

    topic_files = [
        key_files["exploration_launch"],
        key_files["exploration_fsm"],
        key_files["voxel_map_server"],
        key_files["traj_server"],
    ]
    cmake_files = [str(p.relative_to(FALCON_ROOT)) for p in FALCON_ROOT.rglob("CMakeLists.txt")]

    audit = {
        "status": "passed_with_integration_risks",
        "reference_root": str(FALCON_ROOT),
        "key_files": {name: {"path": rel, "exists": exists_rel(rel)} for name, rel in key_files.items()},
        "source_findings": {
            "ros_noetic_claim": "README states setup was tested on Ubuntu 20.04 / ROS Noetic.",
            "custom_map_claim": "README states EPEE supports custom .pcd/.ply/.stl/mesh maps with map config and T_m_w transform.",
            "default_launch_mode": "exploration.launch defaults to mode=uav_simulator and starts map_render plus poscmd_2_odom.",
            "planner_inputs": [
                "/odom_world remapped from launch arg odometry_topic",
                "/transformer/sensor_pose_topic remapped from launch arg sensor_pose_topic",
                "/voxel_mapping/depth_image remapped from launch arg depth_image",
                "/voxel_mapping/pointcloud is also subscribed by voxel_mapping/map_server.cpp",
                "/voxel_mapping/global_map exists but is oracle/debug unless used only for rendering or review",
            ],
            "planner_outputs": [
                "/planning/bspline from exploration_manager/exploration_fsm.cpp",
                "/planning/replan from exploration_manager/exploration_fsm.cpp",
                "/planning/pos_cmd from fast_planner/traj_server.cpp",
                "/voxel_mapping/map_coverage from voxel_mapping/map_server.cpp",
                "occupancy/tsdf/esdf visualization point clouds from voxel_mapping/map_server.cpp",
            ],
            "finish_semantics": [
                "FSM has FINISH state.",
                "No-frontier condition can transition to FINISH.",
                "FINISH logs duration and map_coverage.",
            ],
        },
        "topic_hits": {
            "subscriptions_and_publications": grep(
                r"subscribe|advertise|/odom_world|/voxel_mapping|/planning|map_coverage|FINISH|auto_start",
                topic_files,
            )
        },
        "dependency_risks": {
            "cmake_minimum": "README requires CMake >= 3.20; local runtime must be checked in FALCON-F1.",
            "system_libs": [
                "libgoogle-glog-dev",
                "libdw-dev/libdwarf-dev",
                "libarmadillo-dev",
                "libc++-dev/libc++abi-dev",
                "NLopt 2.7.1",
                "Open3D 0.18.0 for mesh_render",
                "CUDA for pointcloud_render if that package is built",
                "LKH executable is called by exploration_manager for coverage_path TSP solving",
            ],
            "cmake_hits": grep(r"find_package|Open3D|CUDA|NLopt|glog|Armadillo|LKH", cmake_files),
        },
        "mosim_bridge_decision": {
            "primary_bridge_candidate": "online_sensor_cloud",
            "reason": "voxel_mapping subscribes /voxel_mapping/pointcloud, so MID360 world/local cloud can be bridged without forcing depth-image-only mode.",
            "required_adapter_topics": {
                "odom": "MoSim /uav1 odom -> /odom_world",
                "sensor_pose": "MoSim sensor pose or synthesized TransformStamped -> /transformer/sensor_pose_topic",
                "pointcloud": "MoSim MID360/FAST-LIO cloud -> /voxel_mapping/pointcloud",
                "bspline_or_pos_cmd": "/planning/bspline or /planning/pos_cmd -> MoSim Planner Adapter / Trajectory Server",
            },
            "forbidden_for_final_proof": [
                "Do not feed global PCD/mesh directly as planner knowledge and call it unknown exploration.",
                "Do not let FALCON poscmd_2_odom replace Gazebo/PX4/MAVROS runtime evidence.",
                "Do not publish FALCON output directly to MAVROS; keep MoSim adapter/controller boundary.",
            ],
        },
        "next_gate": {
            "name": "FALCON-F1 build/dependency preflight",
            "checks": [
                "CMake version",
                "ROS Noetic environment",
                "NLopt headers/libs",
                "Open3D availability",
                "CUDA/nvcc and compute capability handling or package exclusion strategy",
                "LKH availability",
                "roslaunch static parsing for exploration.launch after overlay setup",
            ],
        },
    }

    json_path = out_dir / "FALCON_D0_SOURCE_AUDIT.json"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = f"""# FALCON D0 Source Audit

Status: `{audit["status"]}`

Reference root: `{FALCON_ROOT}`

## Decision

FALCON is a valid single-UAV full-coverage exploration candidate for the next
gate, but only after a dependency/build preflight. The source is not
depth-image-only: `voxel_mapping` subscribes both `/voxel_mapping/depth_image`
and `/voxel_mapping/pointcloud`, so the first MoSim bridge should try the
online MID360/FAST-LIO cloud route before using rendered depth.

## MoSim Bridge Contract

- odom: MoSim `/uav1` odometry -> `/odom_world`
- sensor pose: MoSim sensor pose or synthesized `TransformStamped` ->
  `/transformer/sensor_pose_topic`
- cloud: MoSim MID360/FAST-LIO cloud -> `/voxel_mapping/pointcloud`
- planner output: `/planning/bspline` or `/planning/pos_cmd` -> MoSim adapter /
  trajectory server; never direct MAVROS publication.

## Main Risks For FALCON-F1

- CMake >= 3.20 requirement.
- NLopt and LKH are likely mandatory for trajectory optimization / coverage
  TSP solving.
- Open3D is required if the mesh renderer path is built.
- CUDA flags in `pointcloud_render` are hardware-specific; avoid building that
  path unless needed for the selected bridge.
- Global map/PCD renderer paths are allowed only as renderer/debug support, not
  as final unknown-exploration proof.

## Evidence

Machine-readable audit: `FALCON_D0_SOURCE_AUDIT.json`
"""
    (out_dir / "SUMMARY.md").write_text(summary, encoding="utf-8")
    print(json.dumps({"status": audit["status"], "out_dir": str(out_dir)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
