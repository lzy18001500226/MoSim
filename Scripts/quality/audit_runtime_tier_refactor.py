#!/usr/bin/env python3
"""Audit runtime-code tiers for the Sunray ROS1 refactor.

This is a static inventory, not a runtime gate.  It keeps the current baseline
intact while making the C++/generated-code migration debt explicit.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def exists(path: str) -> bool:
    return (ROOT / path).exists()


def classify(entry: dict[str, Any]) -> str:
    current_exists = exists(entry["current_path"]) if entry.get("current_path") else False
    target_exists = exists(entry["target_path"]) if entry.get("target_path") else False

    if entry["target_state"] in {"cpp_ready", "generated_c_ready"}:
        return "ready" if target_exists else "missing_target"

    if entry["target_state"] == "upstream_cpp_reuse":
        return "ready" if current_exists else "missing_current"

    if entry["target_state"] == "must_port_to_cpp":
        if target_exists:
            return "cpp_candidate_present"
        if current_exists:
            return "prototype_only_must_port"
        return "missing_current"

    if entry["target_state"] == "tooling_python_ok":
        return "tooling_ok" if current_exists else "missing_current"

    return "unknown"


def build_inventory() -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = [
        {
            "id": "px4ctrl_core_cpp",
            "priority": "P0",
            "tier": "T0",
            "role": "controller_core",
            "current_path": "Scripts/sunray/px4ctrl_golden_slice/px4ctrl_core.cpp",
            "target_path": "Scripts/sunray/px4ctrl_golden_slice/px4ctrl_core.cpp",
            "target_state": "cpp_ready",
            "reason": "Extracted px4ctrl core must remain ROS-free and compile-testable.",
        },
        {
            "id": "px4ctrl_core_c_abi",
            "priority": "P0",
            "tier": "T0",
            "role": "controller_core_c_abi",
            "current_path": "Scripts/sunray/px4ctrl_golden_slice/px4ctrl_core_c.c",
            "target_path": "Scripts/sunray/px4ctrl_golden_slice/px4ctrl_core_c.c",
            "target_state": "generated_c_ready",
            "reason": "C ABI is the bridge shape for MWORKS/generated-code consistency.",
        },
        {
            "id": "fastlio_odom_alignment_adapter",
            "priority": "P0",
            "tier": "T1",
            "role": "state_source_alignment",
            "current_path": "Scripts/sunray/fastlio_odom_alignment_adapter.py",
            "target_path": "Scripts/sunray/cpp/mosim_sunray_runtime_adapters/src/fastlio_odom_alignment_adapter_node.cpp",
            "target_state": "must_port_to_cpp",
            "reason": "This node transforms localization into the flight-control body frame; a frame bug can directly destabilize control.",
        },
        {
            "id": "fastlio_frame_transform_cpp_math",
            "priority": "P0",
            "tier": "T1",
            "role": "state_source_alignment_math",
            "current_path": "Scripts/sunray/cpp/mosim_sunray_runtime_adapters/include/mosim_sunray_runtime_adapters/fastlio_frame_transform.hpp",
            "target_path": "Scripts/sunray/cpp/mosim_sunray_runtime_adapters/include/mosim_sunray_runtime_adapters/fastlio_frame_transform.hpp",
            "target_state": "cpp_ready",
            "reason": "Pure C++ FAST-LIO frame math is the first non-ROS building block for the compiled alignment adapter.",
        },
        {
            "id": "px4_external_odometry_publisher",
            "priority": "P0",
            "tier": "T1",
            "role": "px4_ekf_external_odometry",
            "current_path": "References/Sunray/General_Module/sunray_uav_control/externalFusion/externalFusion.cpp",
            "target_path": "References/Sunray/General_Module/sunray_uav_control/externalFusion/externalFusion.cpp",
            "target_state": "upstream_cpp_reuse",
            "reason": "Sunray external_fusion is C++ and should stay the baseline EKF input surface until a MoSim replacement is justified.",
        },
        {
            "id": "trajectory_reference_server",
            "priority": "P1",
            "tier": "T1",
            "role": "trajectory_evaluation",
            "current_path": "Scripts/sunray/px4ctrl_basic_mission_node.py",
            "target_path": "Scripts/sunray/cpp/mosim_sunray_runtime_adapters/src/trajectory_reference_server_node.cpp",
            "target_state": "must_port_to_cpp",
            "reason": "Online trajectory evaluation affects phase lag and tracking error; Python remains acceptable only as a prototype/runner.",
        },
        {
            "id": "controller_adapter_attitude_thrust",
            "priority": "P1",
            "tier": "T1",
            "role": "attitude_thrust_adapter",
            "current_path": "Scripts/ros/mosim_px4_offboard_adapter/src/position_outer_loop_to_px4_attitude_node.cpp",
            "target_path": "Scripts/ros/mosim_px4_offboard_adapter/src/position_outer_loop_to_px4_attitude_node.cpp",
            "target_state": "cpp_ready",
            "reason": "Adapter-level thrust and attitude semantics should live in a compiled component.",
        },
        {
            "id": "pointcloud_to_world_bridge",
            "priority": "P1",
            "tier": "T1",
            "role": "planner_pointcloud_transform",
            "current_path": "Scripts/sunray/goal4_pointcloud_to_world_node.py",
            "target_path": "Scripts/sunray/cpp/mosim_sunray_runtime_adapters/src/pointcloud_to_world_node.cpp",
            "target_state": "must_port_to_cpp",
            "reason": "Planner obstacle input depends on pose/frame transforms; keep Python as review/prototype until C++/PCL path exists.",
        },
        {
            "id": "position_cmd_safety_adapter",
            "priority": "P1",
            "tier": "T1",
            "role": "planner_command_guard",
            "current_path": "Scripts/sunray/goal4_position_cmd_safety_adapter.py",
            "target_path": "Scripts/sunray/cpp/mosim_sunray_runtime_adapters/src/position_cmd_safety_adapter_node.cpp",
            "target_state": "must_port_to_cpp",
            "reason": "Command guards are safety-relevant once planner output is accepted as online input.",
        },
        {
            "id": "metrics_and_review_recorders",
            "priority": "P2",
            "tier": "T3",
            "role": "evidence_tooling",
            "current_path": "Scripts/sunray/record_sunray_ros1_control_diagnostics.py",
            "target_path": "",
            "target_state": "tooling_python_ok",
            "reason": "Recording, metrics, review-pack generation, and plotting can remain Python tooling.",
        },
    ]
    for entry in inventory:
        entry["current_exists"] = exists(entry["current_path"]) if entry.get("current_path") else False
        entry["target_exists"] = exists(entry["target_path"]) if entry.get("target_path") else False
        entry["status"] = classify(entry)
    return inventory


def write_markdown(payload: dict[str, Any], path: Path) -> None:
    lines = [
        "# Runtime Tier Refactor Audit",
        "",
        f"Status: `{payload['status']}`",
        "",
        "This is a static refactor inventory. It does not start ROS, Gazebo, PX4, RViz, or MWORKS.",
        "",
        "| ID | Priority | Tier | Status | Current | Target |",
        "|---|---|---|---|---|---|",
    ]
    for item in payload["inventory"]:
        lines.append(
            "| {id} | {priority} | {tier} | {status} | `{current}` | `{target}` |".format(
                id=item["id"],
                priority=item["priority"],
                tier=item["tier"],
                status=item["status"],
                current=item.get("current_path", ""),
                target=item.get("target_path", ""),
            )
        )
    lines.extend(
        [
            "",
            "## Required Next Refactor",
            "",
            "P0/P1 entries with `prototype_only_must_port` must not be claimed as flight-like deployable runtime.",
            "They remain valid only as baseline-preserving prototypes until a compiled replacement is added and A/B checked.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    inventory = build_inventory()
    prototype_debt = [item["id"] for item in inventory if item["status"] == "prototype_only_must_port"]
    missing_current = [item["id"] for item in inventory if item["status"] == "missing_current"]
    payload = {
        "schema": "mosim.runtime_tier_refactor_audit.v1",
        "status": "attention_required" if prototype_debt or missing_current else "passed",
        "inventory": inventory,
        "prototype_debt": prototype_debt,
        "missing_current": missing_current,
        "claim_boundary": [
            "Static inventory only: no ROS, Gazebo, PX4, RViz, MWORKS, or controller mission was started.",
            "prototype_only_must_port entries may support review/prototype runs, but not flight-like deployable claims.",
            "Compiled candidates still require source contract checks and runtime A/B validation before replacing the baseline.",
        ],
    }
    output_dir = ROOT / "Results" / "refactor" / "runtime_tiers"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "runtime_tier_refactor_audit.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_markdown(payload, output_dir / "runtime_tier_refactor_audit.md")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
