#!/usr/bin/env python3
"""Audit the UE live command-echo receiver boundary.

This is a design/static audit only. It does not open Unreal Editor, start a UE
runtime receiver, call MWORKS, publish or consume ROS2 topics, or prove live
runtime acknowledgement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STATE_HEADER = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksExperimentConsoleStateComponent.h"
STATE_SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksExperimentConsoleStateComponent.cpp"
FRAME_RECEIVER_HEADER = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksUdpReceiverComponent.h"
FRAME_RECEIVER_SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpReceiverComponent.cpp"
SENDER_HEADER = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksUdpCommandSenderComponent.h"
SENDER_SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpCommandSenderComponent.cpp"
MWORKS_004_RETURN = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-MWORKS-ECHO-LIVE-DOWNLINK-PREFLIGHT-20260606-004.json"
UE_003_RETURN = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-EXPERIMENT-CONSOLE-STATE-COMPONENT-SOURCE-SMOKE-20260606-003.json"
MWORKS_PREFLIGHT_SUMMARY = ROOT / "Results/mworks_echo_producer_smoke/20260606_004_live_downlink_preflight/mworks_runtime_adapter_preflight_summary.json"
MWORKS_PREFLIGHT_REDUCER_STATES = ROOT / "Results/mworks_echo_producer_smoke/20260606_004_live_downlink_preflight/reducer_states.json"

NON_LIVE_SOURCES = {
    "offline_adapter_smoke",
    "source_level_smoke",
    "MWORKS_MCP_result_adapter_smoke",
    "MWORKS_MCP_runtime_adapter_preflight",
}
FUTURE_LIVE_SOURCE_CANDIDATES = {
    "MWORKS_live_downlink",
    "ROS2_runtime_echo",
    "MWORKS_ROS2_live_downlink",
}
FORBIDDEN_POSE_PATTERNS = {
    "SetActorLocation",
    "SetActorTransform",
    "TeleportTo",
    "AddActorWorldOffset",
    "BindAxis",
    "BindAction",
    "InputComponent",
    "EnhancedInput",
    "UInputAction",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def source_literal(source_label: str) -> str:
    return f'TEXT("{source_label}")'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default="")
    args = parser.parse_args()

    issues: list[str] = []
    blockers: list[dict[str, str]] = []
    warnings: list[str] = [
        "static receiver-boundary audit only; no live UE/MWORKS/ROS2 ack is claimed",
        "future live receiver must be a separate component or adapter and must call ApplyCommandEchoJson only after transport provenance is proven",
    ]

    state_header = read(STATE_HEADER)
    state_source = read(STATE_SOURCE)
    frame_header = read(FRAME_RECEIVER_HEADER)
    frame_source = read(FRAME_RECEIVER_SOURCE)
    sender_combined = read(SENDER_HEADER) + "\n" + read(SENDER_SOURCE)
    all_ue_source = "\n".join([state_header, state_source, frame_header, frame_source, sender_combined])
    mworks_return = read_json(MWORKS_004_RETURN) or {}
    ue_return = read_json(UE_003_RETURN) or {}
    preflight_summary = read_json(MWORKS_PREFLIGHT_SUMMARY) or {}
    reducer_states = read_json(MWORKS_PREFLIGHT_REDUCER_STATES) or []

    if "UQuadrotorMworksExperimentConsoleStateComponent" not in state_header + state_source:
        issues.append("missing UQuadrotorMworksExperimentConsoleStateComponent")
    if "ApplyCommandEchoJson" not in state_header + state_source:
        issues.append("state component lacks ApplyCommandEchoJson anchor")
    if "UQuadrotorMworksUdpReceiverComponent" not in frame_header + frame_source:
        issues.append("missing existing frame receiver for audit")
    if "quadrotor.unreal_state." not in frame_source:
        issues.append("existing UDP receiver does not clearly restrict itself to quadrotor.unreal_state.* frames")
    if "mosim.ue_command_echo.v1" in frame_source:
        blockers.append(
            {
                "id": "frame_receiver_mixes_command_echo",
                "reason": "Existing UQuadrotorMworksUdpReceiverComponent should remain a frame/status receiver and not parse command echo rows.",
            }
        )
    if "ApplyCommandEchoJson" in sender_combined:
        blockers.append(
            {
                "id": "sender_mixes_command_echo",
                "reason": "UQuadrotorMworksUdpCommandSenderComponent must remain sender-only; echo lifecycle belongs to the state component plus future receiver adapter.",
            }
        )

    missing_non_live_sources = sorted(source for source in NON_LIVE_SOURCES if source_literal(source) not in state_source)
    covered_non_live_sources = sorted(source for source in NON_LIVE_SOURCES if source_literal(source) in state_source)
    if missing_non_live_sources:
        blockers.append(
            {
                "id": "state_component_non_live_source_gap",
                "reason": "State component does not currently downgrade all known source/offline/preflight labels to smoke_only.",
                "missing_sources": ", ".join(missing_non_live_sources),
            }
        )

    if preflight_summary.get("source") != "MWORKS_MCP_runtime_adapter_preflight":
        issues.append("MWORKS 004 preflight summary source is missing or unexpected")
    if preflight_summary.get("live_downlink_status") != "blocked_no_transport_surface":
        issues.append("MWORKS 004 summary must remain blocked_no_transport_surface for this boundary audit")
    if mworks_return.get("live_downlink_status") != "blocked_no_transport_surface":
        issues.append("MWORKS 004 return does not preserve live_downlink_status=blocked_no_transport_surface")
    if ue_return.get("quality_status") != "source_level_component_static_smoke_passed":
        issues.append("UE 003 state component return is missing or not completed")

    reducer_runtime_values = {row.get("accepted_as_runtime_ack") for row in reducer_states if isinstance(row, dict)}
    if reducer_states and reducer_runtime_values != {False}:
        blockers.append(
            {
                "id": "preflight_reducer_runtime_ack_leak",
                "reason": "MWORKS 004 reducer states must keep accepted_as_runtime_ack=false for preflight rows.",
            }
        )

    for pattern in sorted(FORBIDDEN_POSE_PATTERNS):
        if pattern in state_header + state_source:
            blockers.append(
                {
                    "id": "state_component_pose_api",
                    "reason": f"State component must not expose Actor/input pose route: {pattern}",
                }
            )

    current_live_receiver_present = "mosim.ue_command_echo.v1" in frame_source or "ApplyCommandEchoJson" in frame_source
    safe_to_implement_runtime_receiver_next = not blockers and preflight_summary.get("live_downlink_status") != "blocked_no_transport_surface"

    report = {
        "schema": "mosim.ue_live_echo_receiver_boundary_static_audit.v1",
        "ok": not issues and not blockers,
        "source": "source_level_static_boundary_audit",
        "task_id": "RFLY-MOSIM-UE-LIVE-ECHO-RECEIVER-BOUNDARY-20260606-004",
        "receiver_boundary_decision": {
            "current_live_echo_receiver_present": current_live_receiver_present,
            "existing_udp_receiver_role": "quadrotor.unreal_state frame/status receiver only",
            "future_receiver_host": "new project-owned command echo receiver/adapter component, not UQuadrotorMworksUdpReceiverComponent and not UQuadrotorMworksUdpCommandSenderComponent",
            "future_receiver_input_schema": "mosim.ue_command_echo.v1",
            "future_receiver_sink": "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson",
            "safe_to_implement_runtime_receiver_next": safe_to_implement_runtime_receiver_next,
        },
        "source_labels": {
            "non_live_sources_expected": sorted(NON_LIVE_SOURCES),
            "non_live_sources_covered_by_state_component": covered_non_live_sources,
            "non_live_sources_missing_from_state_component": missing_non_live_sources,
            "non_live_source_quality_status": "smoke_only",
            "non_live_accepted_as_runtime_ack": False,
            "future_live_source_candidates": sorted(FUTURE_LIVE_SOURCE_CANDIDATES),
            "mworks_004_source": preflight_summary.get("source", ""),
            "mworks_004_live_downlink_status": preflight_summary.get("live_downlink_status", ""),
        },
        "rules": [
            "pending rows may originate only from mosim.ue_command.v1 command requests",
            "accepted/rejected rows may originate only from matching mosim.ue_command_echo.v1",
            "offline/source/preflight rows must keep quality_status=smoke_only and accepted_as_runtime_ack=false",
            "future live receiver must require schema/status/run_id/request_id/seq/kind/ack_authority/no_pose_overwrite_status matching",
            "future live receiver must reject or keep disabled stale, duplicate, orphan, mismatched, missing-authority, and no_pose_overwrite_status!=pass rows",
            "general quadrotor.unreal_state frame/status downlink cannot be used as command ack",
            "UDP send success cannot be used as command ack",
        ],
        "issues": issues,
        "blockers": blockers,
        "warnings": warnings,
        "claim_boundary": {
            "not_live_ue_runtime_ack": True,
            "not_live_mworks_downlink": True,
            "not_ros2_runtime_ack": True,
            "planner_ready": False,
            "closed_loop_ready": False,
            "controller_performance": False,
        },
    }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output_json:
        output_path = Path(args.output_json)
        if not output_path.is_absolute():
            output_path = ROOT / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
