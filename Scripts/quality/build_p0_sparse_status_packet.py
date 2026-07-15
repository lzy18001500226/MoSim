#!/usr/bin/env python3
"""Build a sparse PMO/manual-review status packet for the current P0 slice."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {value}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def exists(path: str) -> bool:
    return bool(path) and repo_path(path).exists()


def build_packet(gap: dict[str, Any]) -> dict[str, Any]:
    gates = as_mapping(gap.get("gates"))
    waiting_paths = [str(path) for path in as_list(gap.get("next_packets_to_consume"))]
    return {
        "template_type": "blocker_notification",
        "class": "manual_review_required",
        "task_id": "RFLY-MOSIM-P0-10H-20260606",
        "canonical_status": "blocked",
        "severity": "medium",
        "blocked_surface": "P0 planner/closed_loop claim remains blocked; MWORKS 016 is narrow bridge evidence and ROS2 019 restores odom/cloud input only, not planner acceptance.",
        "human_action_required": (
            "No immediate engineering approval is required. If WeChat delivery fails with ret=-2, send one normal "
            "text message in the MoSim WeChat gateway chat before PMO retries once."
        ),
        "why_now": "Sparse checkpoint after integrating MWORKS 016 display-position bridge pass and ROS2 019 odom/cloud restore readiness.",
        "dedupe_key": "rfly_mosim_p0_mworks016_bridge_ros2019_odom_cloud_restore_blocked_20260606",
        "schema_version": "mosim.pmo_sparse_status_packet.v1",
        "packet_id": "rfly_mosim_p0_sparse_status_20260606",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_thread_id": "019e9868-83ea-70f0-92c5-a3a408bd78c6",
        "origin_thread_id": "019e9868-83ea-70f0-92c5-a3a408bd78c6",
        "self_thread_id": "019e9868-83ea-70f0-92c5-a3a408bd78c6",
        "status": "progress_mworks_016_bridge_ros2_019_odom_cloud_restore_blocked",
        "quality_status": gap.get("quality_status", ""),
        "closed_loop_ready": gap.get("closed_loop_ready", False),
        "planner_ready": gap.get("planner_ready", False),
        "summary": (
            "PMO integrated MWORKS 016 display-position bridge evidence and ROS2 019 odom/cloud restore evidence. ROS2 "
            "now has a reproducible real /Odometry and /cloud_registered restore gate for a later separate planner "
            "startup probe, but runtime_disabled=false planner startup was not executed and PositionCommand recorder "
            "remains forbidden. MWORKS Iso23 restores result context for the narrow sampled/held display-position "
            "bridge, but full Factory trace consumption remains blocked. P0 remains smoke_only: no planner runtime, "
            "/position_cmd, /planning/bspline runtime evidence, Factory trace consumption, controller performance, or closed_loop claim."
        ),
        "evidence": [
            "Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json",
            "Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_BUNDLE_AUDIT.json",
            "Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_CLOSED_LOOP_GAP_MATRIX.json",
            "Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-YAW-RATE-DECOUPLING-20260606-013.json",
            "Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-RATE-FEEDBACK-ISOLATION-20260606-014.json",
            "Results/agent_packets/blockers/RFLY-MOSIM-MWORKS-CONTROL-SENSOR-BUS-RECONNECT-20260606-015.json",
            "Results/agent_packets/returns/RFLY-MOSIM-MWORKS-CONTROL-POSITION-BRIDGE-20260606-016.json",
            "Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-LAUNCH-AUDIT-20260606-015.json",
            "Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-LAUNCH-CONFIG-20260606-016.json",
            "Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-RUNTIME-DISABLED-SMOKE-20260606-017.json",
            "Results/agent_packets/blockers/RFLY-MOSIM-ROS2-RUNTIME-B1-REAL-PLANNER-INPUT-GATE-20260606-018.json",
            "Results/agent_packets/returns/RFLY-MOSIM-ROS2-RUNTIME-B1-ODOM-CLOUD-RESTORE-20260606-019.json",
            "Results/ros2_runtime/b1_odom_cloud_restore_20260606_019/odom_cloud_restore_summary.json",
        ],
        "next_recommended_action": "Open a separate bounded runtime_disabled=false planner startup probe against freshly restored /Odometry and /cloud_registered; use Iso23 as the passing MWORKS display-position bridge baseline before adding the next narrow sensor/display group.",
        "must_not_claim": as_list(gap.get("must_not_claim")),
        "current_blockers": [
            {
                "id": "mworks_same_trace_consumption",
                "status": as_mapping(gates.get("mworks_same_trace_consumption")).get("status", ""),
                "next": as_mapping(gates.get("mworks_same_trace_consumption")).get("next", ""),
            },
            {
                "id": "mworks_sensor_bus_reconnect",
                "status": as_mapping(gates.get("mworks_sensor_bus_reconnect")).get("status", ""),
                "next": as_mapping(gates.get("mworks_sensor_bus_reconnect")).get("next", ""),
            },
            {
                "id": "mworks_position_bridge",
                "status": as_mapping(gates.get("mworks_position_bridge")).get("status", ""),
                "next": as_mapping(gates.get("mworks_position_bridge")).get("next", ""),
            },
            {
                "id": "ros2_real_planner_runtime",
                "status": as_mapping(gates.get("ros2_real_planner_runtime")).get("status", ""),
                "next": as_mapping(gates.get("ros2_real_planner_runtime")).get("next", ""),
            },
            {
                "id": "ros2_real_planner_input_gate",
                "status": as_mapping(gates.get("ros2_real_planner_input_gate")).get("status", ""),
                "next": as_mapping(gates.get("ros2_real_planner_input_gate")).get("next", ""),
            },
            {
                "id": "ros2_odom_cloud_restore",
                "status": as_mapping(gates.get("ros2_odom_cloud_restore")).get("status", ""),
                "next": as_mapping(gates.get("ros2_odom_cloud_restore")).get("next", ""),
            },
            {
                "id": "ros2_planner_dependency_surfaces",
                "status": as_mapping(gates.get("ros2_planner_dependency_surfaces")).get("status", ""),
                "next": as_mapping(gates.get("ros2_planner_dependency_surfaces")).get("next", ""),
            },
            {
                "id": "ue_runtime_command_ack",
                "status": as_mapping(gates.get("ue_runtime_command_ack")).get("status", ""),
                "next": as_mapping(gates.get("ue_runtime_command_ack")).get("next", ""),
            },
        ],
        "waiting_for_packets": [
            {
                "path": path,
                "exists": exists(path),
            }
            for path in waiting_paths
        ],
        "wechat": {
            "send_attempted": False,
            "packet_shape": "blocker_notification/manual_review_required",
            "reason": "Ops restored the local API socket; previous business send reached the Weixin layer and returned ret=-2, so do not retry until the user sends one normal message in the gateway chat.",
            "minimal_user_action_if_needed": "Send one normal text message to the MoSim WeChat gateway chat, then PMO may retry once through the project gateway script if that legacy route is explicitly restored.",
            "ops_incident": "WEIXIN-GATEWAY-INCIDENT-B0-MANIFEST-20260606-0459",
        },
        "evidence_refs": {
            "gap_matrix": "Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_CLOSED_LOOP_GAP_MATRIX.json",
            "manifest": "Results/p0_runs/rfly_mosim_p0_slice_20260606/RUN_MANIFEST.json",
            "audit": "Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_BUNDLE_AUDIT.json",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--gap-matrix",
        default="Results/p0_runs/rfly_mosim_p0_slice_20260606/P0_CLOSED_LOOP_GAP_MATRIX.json",
    )
    parser.add_argument(
        "--output-json",
        default="Results/coagent_gateway/packets/rfly_mosim_p0_sparse_status_20260606.json",
    )
    args = parser.parse_args()

    gap_path = repo_path(args.gap_matrix)
    output_path = repo_path(args.output_json)
    packet = build_packet(read_json(gap_path))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"packet": rel(output_path), "status": packet["status"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
