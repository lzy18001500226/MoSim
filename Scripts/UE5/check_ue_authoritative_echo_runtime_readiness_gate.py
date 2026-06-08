#!/usr/bin/env python3
"""Check UE authoritative command-echo runtime readiness after UE 024/025/026.

This is a source-static/build-prep/runtime-readiness checker only. It records
which parts of the future authoritative mosim.ue_command_echo.v1 path are
present and which live-runtime preconditions are still missing. It does not
open Unreal Editor, run UE runtime, run Unreal build, bind sockets, or claim
live command ack.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "RFLY-MOSIM-UE-CONSOLE-AUTHORITATIVE-ECHO-RUNTIME-READINESS-GATE-20260608-027"
COMMAND_SCHEMA_ID = "mosim.ue_command.v1"
ECHO_SCHEMA_ID = "mosim.ue_command_echo.v1"
UNREAL_STATE_SCHEMA_PREFIX = "quadrotor.unreal_state."

BRIDGE_ROOT = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge"
RECEIVER_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.h"
RECEIVER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.cpp"
STATE_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksExperimentConsoleStateComponent.h"
STATE_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksExperimentConsoleStateComponent.cpp"
FRAME_RECEIVER_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksUdpReceiverComponent.h"
FRAME_RECEIVER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksUdpReceiverComponent.cpp"
SENDER_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksUdpCommandSenderComponent.h"
SENDER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksUdpCommandSenderComponent.cpp"
UPROJECT_PATH = ROOT / "UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject"
UPLUGIN_PATH = ROOT / "UE5/Bridge/QuadrotorMworksBridge.uplugin"
BUILD_CS_PATH = BRIDGE_ROOT / "QuadrotorMworksBridge.Build.cs"

RETURN_024 = (
    ROOT
    / "Results/agent_packets/returns/"
    / "RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-PRODUCER-DOWNLINK-GATE-20260608-024.json"
)
RETURN_025 = (
    ROOT
    / "Results/agent_packets/returns/"
    / "RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-DOWNLINK-COMPILE-GATE-20260608-025.json"
)
RETURN_026 = (
    ROOT
    / "Results/agent_packets/returns/"
    / "RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-BOUNDARY-CHECKER-REFRESH-20260608-026.json"
)

PENDING_METHOD = "RecordPendingCommandFromPacketJson"
STATE_SINK_METHOD = "ApplyCommandEchoJson"
DOWNLINK_VALIDATE_METHOD = "IsAuthoritativeRuntimeCommandEchoPacketJson"
DOWNLINK_APPLY_METHOD = "ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState"
STATE_SINK = "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson"

AUTHORITATIVE_LIVE_SOURCES = {
    "MWORKS_live_downlink": "MWORKS",
    "ROS2_runtime_echo": "ROS2",
    "MWORKS_ROS2_live_downlink": "MWORKS_ROS2",
}
NON_LIVE_SOURCES = {
    "offline_adapter_smoke",
    "source_level_smoke",
    "MWORKS_MCP_result_adapter_smoke",
    "MWORKS_MCP_runtime_adapter_preflight",
}
FALSE_ACK_SOURCES = {
    "024_source_static_handoff",
    "025_compile_pass",
    "026_checker_success",
    "UnrealBuildTool_success",
    "build_success",
    "checker_success",
    "cli_build_success",
    "compile_pass_warning_only",
    "fixture_only_echo",
    "operator_intent",
    "pytest_success",
    "quadrotor.unreal_state.frame",
    "quadrotor.unreal_state.v1",
    "sender_result_bSent",
    "static_fixture_row",
    "udp_send_success",
}
FORBIDDEN_RUNTIME_RECEIVER_PATTERNS = {
    "Common/UdpSocketBuilder.h",
    "Common/UdpSocketReceiver.h",
    "FSocket",
    "FUdpSocketBuilder",
    "FUdpSocketReceiver",
    "FIPv4Endpoint",
    "FRunnable",
    "FRunnableThread",
    "FTimerHandle",
    "OnDataReceived",
    "StartReceiver",
    "StopReceiver",
    "ListenPort",
    "RemotePort",
    "BindUObject",
    "CreateSocket",
    "SocketSubsystem",
    "Sockets.h",
    "AsyncTask",
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


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def repo(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def present(source: str, patterns: set[str]) -> list[str]:
    return sorted(pattern for pattern in patterns if pattern in source)


def source_literal(label: str) -> str:
    return f'TEXT("{label}")'


def readiness_row(
    *,
    row_id: str,
    layer: str,
    description: str,
    available_now: bool,
    evidence: str,
    required_for_live_ack: bool,
    accepted_as_runtime_ack_now: bool = False,
    missing_reason: str = "",
) -> dict[str, Any]:
    return {
        "row_id": row_id,
        "layer": layer,
        "description": description,
        "available_now": available_now,
        "required_for_live_ack": required_for_live_ack,
        "accepted_as_runtime_ack_now": accepted_as_runtime_ack_now,
        "evidence": evidence,
        "missing_reason": missing_reason,
    }


def false_ack_row(source: str) -> dict[str, Any]:
    return {
        "source": source,
        "accepted_as_runtime_ack_now": False,
        "runtime_transport_evidence": False,
        "policy": "reject_as_false_ack",
        "reason": "not an authoritative live mosim.ue_command_echo.v1 transport capture matching a pending mosim.ue_command.v1 request",
    }


def build_report() -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = [
        "027 is source-static/build-prep/runtime-readiness classification only.",
        "024 source handoff, 025 compile pass, and 026 checker success remain engineering readiness evidence, not live runtime ack.",
    ]

    receiver_header = read(RECEIVER_HEADER)
    receiver_source = read(RECEIVER_SOURCE)
    receiver_combined = receiver_header + "\n" + receiver_source
    state_header = read(STATE_HEADER)
    state_source = read(STATE_SOURCE)
    state_combined = state_header + "\n" + state_source
    frame_receiver_combined = read(FRAME_RECEIVER_HEADER) + "\n" + read(FRAME_RECEIVER_SOURCE)
    sender_combined = read(SENDER_HEADER) + "\n" + read(SENDER_SOURCE)
    uproject = read_json(UPROJECT_PATH)
    uplugin = read_json(UPLUGIN_PATH)
    build_cs = read(BUILD_CS_PATH)
    return_024 = read_json(RETURN_024)
    return_025 = read_json(RETURN_025)
    return_026 = read_json(RETURN_026)

    for path, label in [
        (RECEIVER_HEADER, "command echo receiver header"),
        (RECEIVER_SOURCE, "command echo receiver source"),
        (STATE_HEADER, "experiment console state header"),
        (STATE_SOURCE, "experiment console state source"),
        (FRAME_RECEIVER_HEADER, "quadrotor.unreal_state receiver header"),
        (FRAME_RECEIVER_SOURCE, "quadrotor.unreal_state receiver source"),
        (SENDER_HEADER, "command sender header"),
        (SENDER_SOURCE, "command sender source"),
        (UPROJECT_PATH, "MoSimSceneLibrary uproject"),
        (UPLUGIN_PATH, "QuadrotorMworksBridge uplugin"),
        (BUILD_CS_PATH, "QuadrotorMworksBridge Build.cs"),
        (RETURN_024, "UE 024 return packet"),
        (RETURN_025, "UE 025 return packet"),
        (RETURN_026, "UE 026 return packet"),
    ]:
        if not path.exists():
            issues.append(f"missing {label}: {repo(path)}")

    if return_024.get("status") != "completed":
        issues.append("UE 024 return is missing or not completed")
    if return_024.get("quality_status") != "runtime_echo_producer_downlink_source_static_build_prep_passed":
        issues.append("UE 024 quality_status is not the expected source-static/build-prep pass")
    if return_025.get("status") != "completed":
        issues.append("UE 025 return is missing or not completed")
    if return_025.get("quality_status") != "runtime_echo_downlink_compile_gate_passed":
        issues.append("UE 025 quality_status is not the expected compile-only pass")
    compile_summary = return_025.get("build_only_compile_summary", {})
    if compile_summary.get("exit_code") != 0:
        issues.append("UE 025 compile evidence does not record exit_code=0")
    if return_026.get("status") != "completed":
        issues.append("UE 026 return is missing or not completed")
    if return_026.get("quality_status") != "runtime_echo_boundary_checker_refresh_source_static_passed":
        issues.append("UE 026 quality_status is not the expected source-static checker pass")
    matrix_026 = return_026.get("matrix_summary", {})
    if matrix_026.get("runtime_ack_leaks_now") != 0:
        issues.append("UE 026 matrix does not preserve runtime_ack_leaks_now=0")
    if matrix_026.get("actual_runtime_claim_rows") != 0:
        issues.append("UE 026 matrix claims actual runtime rows")

    receiver_required_anchors = [
        DOWNLINK_VALIDATE_METHOD,
        DOWNLINK_APPLY_METHOD,
        STATE_SINK_METHOD,
        ECHO_SCHEMA_ID,
        "IsAuthoritativeLiveEchoSource",
        "MWORKS_live_downlink",
        "ROS2_runtime_echo",
        "MWORKS_ROS2_live_downlink",
        "missing_timestamp",
        "missing_seq",
        "missing_command_kind",
        "source_authority_mismatch",
        "no_pose_overwrite_not_pass",
        "forbidden_pose_command",
    ]
    for anchor in receiver_required_anchors:
        if anchor not in receiver_combined:
            issues.append(f"receiver shell missing authoritative echo anchor: {anchor}")
    if PENDING_METHOD in receiver_source:
        issues.append("receiver shell must not record pending requests")
    if COMMAND_SCHEMA_ID in receiver_combined:
        issues.append("receiver shell must not parse command request schema")
    if UNREAL_STATE_SCHEMA_PREFIX in receiver_combined:
        issues.append("receiver shell must not parse quadrotor.unreal_state frames")

    receiver_runtime_patterns = present(receiver_combined, FORBIDDEN_RUNTIME_RECEIVER_PATTERNS)
    if receiver_runtime_patterns:
        issues.append(
            "receiver shell contains runtime transport pattern(s): "
            + ", ".join(receiver_runtime_patterns)
        )
    receiver_pose_patterns = present(receiver_combined, FORBIDDEN_POSE_PATTERNS)
    if receiver_pose_patterns:
        issues.append(
            "receiver shell contains forbidden pose/input pattern(s): "
            + ", ".join(receiver_pose_patterns)
        )

    state_required_anchors = [
        PENDING_METHOD,
        STATE_SINK_METHOD,
        "IsAuthoritativeLiveEchoSource",
        "missing_timestamp",
        "source_authority_mismatch",
        "seq_mismatch",
        "command_kind_mismatch",
        "no_pose_overwrite_not_pass",
        COMMAND_SCHEMA_ID,
        ECHO_SCHEMA_ID,
    ]
    for anchor in state_required_anchors:
        if anchor not in state_combined:
            issues.append(f"state component missing reducer anchor: {anchor}")
    missing_non_live_labels = sorted(
        label for label in NON_LIVE_SOURCES if source_literal(label) not in state_source
    )
    if missing_non_live_labels:
        issues.append("state component missing non-live smoke labels: " + ", ".join(missing_non_live_labels))

    if UNREAL_STATE_SCHEMA_PREFIX not in frame_receiver_combined:
        issues.append("frame receiver missing quadrotor.unreal_state schema anchor")
    if ECHO_SCHEMA_ID in frame_receiver_combined:
        issues.append("frame receiver must not parse command echo schema")
    if STATE_SINK_METHOD in frame_receiver_combined:
        issues.append("frame receiver must not call command echo state sink")
    if ECHO_SCHEMA_ID in sender_combined:
        issues.append("command sender must not parse command echo schema")
    if STATE_SINK_METHOD in sender_combined:
        issues.append("command sender must not call command echo state sink")
    if COMMAND_SCHEMA_ID not in sender_combined:
        issues.append("command sender missing command schema anchor")

    if uproject.get("EngineAssociation") != "5.5":
        issues.append("MoSimSceneLibrary uproject EngineAssociation is not 5.5")
    plugin_names = {str(plugin.get("Name")) for plugin in uproject.get("Plugins", [])}
    if "QuadrotorMworksBridge" not in plugin_names:
        issues.append("MoSimSceneLibrary uproject does not enable QuadrotorMworksBridge")
    module_names = {str(module.get("Name")) for module in uplugin.get("Modules", [])}
    if "QuadrotorMworksBridge" not in module_names:
        issues.append("QuadrotorMworksBridge uplugin missing module")
    for dependency in ["Core", "CoreUObject", "Engine", "Json", "JsonUtilities"]:
        if f'"{dependency}"' not in build_cs:
            issues.append(f"Build.cs missing dependency anchor: {dependency}")

    source_handoff_present = (
        DOWNLINK_VALIDATE_METHOD in receiver_combined
        and DOWNLINK_APPLY_METHOD in receiver_combined
        and STATE_SINK_METHOD in receiver_source
        and not receiver_runtime_patterns
        and not receiver_pose_patterns
    )
    compile_only_pass_present = (
        return_025.get("status") == "completed"
        and compile_summary.get("exit_code") == 0
        and return_025.get("quality_status") == "runtime_echo_downlink_compile_gate_passed"
    )
    boundary_checker_pass_present = (
        return_026.get("status") == "completed"
        and matrix_026.get("runtime_ack_leaks_now") == 0
        and matrix_026.get("actual_runtime_claim_rows") == 0
    )
    pending_reducer_present = PENDING_METHOD in state_combined
    state_echo_sink_present = STATE_SINK_METHOD in state_combined

    readiness_matrix = [
        readiness_row(
            row_id="source_static_authoritative_downlink_handoff",
            layer="UE C++ source anchor",
            description="Future authoritative echo handoff validates mosim.ue_command_echo.v1 before the state sink.",
            available_now=source_handoff_present,
            evidence=f"{repo(RECEIVER_HEADER)}; {repo(RECEIVER_SOURCE)}",
            required_for_live_ack=True,
        ),
        readiness_row(
            row_id="compile_only_evidence_for_handoff",
            layer="build-prep evidence",
            description="024 C++ handoff compiled once through the project renderer build script in UE 025.",
            available_now=compile_only_pass_present,
            evidence=repo(RETURN_025),
            required_for_live_ack=True,
        ),
        readiness_row(
            row_id="boundary_checker_false_ack_rejection",
            layer="source-static checker evidence",
            description="UE 026 refreshed the live-echo boundary checker and preserved zero current runtime-ack leaks.",
            available_now=boundary_checker_pass_present,
            evidence=repo(RETURN_026),
            required_for_live_ack=True,
        ),
        readiness_row(
            row_id="pending_command_request_reducer",
            layer="state reducer source anchor",
            description="Pending state can be recorded only from mosim.ue_command.v1 request identity.",
            available_now=pending_reducer_present,
            evidence=f"{repo(STATE_HEADER)}; {repo(STATE_SOURCE)}",
            required_for_live_ack=True,
        ),
        readiness_row(
            row_id="command_echo_state_sink",
            layer="state reducer source anchor",
            description="Accepted/rejected state sink exists for authoritative echo rows after validation.",
            available_now=state_echo_sink_present,
            evidence=f"{repo(STATE_HEADER)}; {repo(STATE_SOURCE)}",
            required_for_live_ack=True,
        ),
        readiness_row(
            row_id="live_authoritative_echo_producer",
            layer="runtime producer",
            description="A live MWORKS/ROS2 producer emits mosim.ue_command_echo.v1 rows.",
            available_now=False,
            evidence="not present in 027 source-static scope",
            required_for_live_ack=True,
            missing_reason="No MWORKS/ROS2 live downlink producer evidence is available or authorized in 027.",
        ),
        readiness_row(
            row_id="live_transport_capture_surface",
            layer="runtime transport",
            description="A bounded transport capture proves the echo row was received from a live producer.",
            available_now=False,
            evidence="not present in 027 source-static scope",
            required_for_live_ack=True,
            missing_reason="027 forbids sockets/listeners/runtime transport and does not run UE runtime.",
        ),
        readiness_row(
            row_id="bounded_ue_runtime_probe_authorization",
            layer="editor/runtime probe",
            description="PMO-authorized single bounded UE runtime/editor probe with capture and cleanup.",
            available_now=False,
            evidence="not authorized by 027",
            required_for_live_ack=True,
            missing_reason="027 explicitly forbids opening Unreal Editor, PIE, standalone runtime, or live sockets.",
        ),
        readiness_row(
            row_id="matching_pending_request_and_echo_capture",
            layer="runtime evidence",
            description="Captured echo matches a pending mosim.ue_command.v1 by run_id/request_id/seq/command kind/time_s/status.",
            available_now=False,
            evidence="not present in 027 source-static scope",
            required_for_live_ack=True,
            missing_reason="No live command/echo pair was produced or captured in 027.",
        ),
        readiness_row(
            row_id="runtime_no_pose_overwrite_proof",
            layer="runtime negative evidence",
            description="Runtime capture proves no_pose_overwrite_status=pass and no direct UAV pose override path was used.",
            available_now=False,
            evidence="source-static guards only",
            required_for_live_ack=True,
            missing_reason="027 proves source guards but not runtime no-pose behavior.",
        ),
        readiness_row(
            row_id="runtime_negative_false_ack_proof",
            layer="runtime negative evidence",
            description="Runtime evidence rejects build/checker/sender/fixture/operator/frame rows as accepted state.",
            available_now=False,
            evidence="static false-ack matrix only",
            required_for_live_ack=True,
            missing_reason="027 can only provide static false-ack rejection, not runtime negative capture.",
        ),
        readiness_row(
            row_id="final_operator_ui_acceptance",
            layer="UI/manual review",
            description="Final UI displays accepted/rejected state only after authoritative echo evidence.",
            available_now=False,
            evidence="not present in 027 source-static scope",
            required_for_live_ack=False,
            missing_reason="027 does not implement or review final UI controls.",
        ),
    ]

    false_ack_matrix = [
        false_ack_row(source) for source in sorted(FALSE_ACK_SOURCES | NON_LIVE_SOURCES)
    ]
    false_ack_runtime_leaks = [
        row for row in false_ack_matrix if row["accepted_as_runtime_ack_now"]
    ]
    if false_ack_runtime_leaks:
        issues.append("false-ack matrix leaks accepted runtime ack")

    available_required = [
        row for row in readiness_matrix if row["required_for_live_ack"] and row["available_now"]
    ]
    missing_required = [
        row for row in readiness_matrix if row["required_for_live_ack"] and not row["available_now"]
    ]
    runtime_ready_now = len(missing_required) == 0
    if runtime_ready_now:
        issues.append("027 must not classify current state as runtime-ready for live ack")

    return {
        "schema": "mosim.ue_authoritative_echo_runtime_readiness_gate.v1",
        "ok": not issues,
        "task_id": TASK_ID,
        "scope_classification": "source-static/build-prep/runtime-readiness",
        "runtime_readiness_classification": "source_static_ready_live_runtime_probe_blocked_by_missing_authoritative_producer_transport_capture",
        "source_static_readiness_ok": not issues,
        "runtime_ready_now": False,
        "authoritative_runtime_ack_claimable_now": False,
        "unreal_editor_opened": False,
        "ue_runtime_started": False,
        "unreal_build_executed_in_027": False,
        "live_socket_listener_or_transport_started": False,
        "ue_cpp_source_edited_by_027": False,
        "accepted_state_ui_controls_enabled": False,
        "prior_gate_inputs": {
            "ue_024_return": repo(RETURN_024),
            "ue_024_status": return_024.get("status"),
            "ue_024_quality_status": return_024.get("quality_status"),
            "ue_025_return": repo(RETURN_025),
            "ue_025_status": return_025.get("status"),
            "ue_025_quality_status": return_025.get("quality_status"),
            "ue_025_compile_exit_code": compile_summary.get("exit_code"),
            "ue_025_compile_classification": compile_summary.get("classification"),
            "ue_026_return": repo(RETURN_026),
            "ue_026_status": return_026.get("status"),
            "ue_026_quality_status": return_026.get("quality_status"),
            "ue_026_runtime_ack_leaks_now": matrix_026.get("runtime_ack_leaks_now"),
            "ue_026_actual_runtime_claim_rows": matrix_026.get("actual_runtime_claim_rows"),
        },
        "source_anchor_summary": {
            "command_echo_receiver_shell": {
                "header": repo(RECEIVER_HEADER),
                "source": repo(RECEIVER_SOURCE),
                "has_authoritative_validate_method": DOWNLINK_VALIDATE_METHOD in receiver_combined,
                "has_authoritative_apply_method": DOWNLINK_APPLY_METHOD in receiver_combined,
                "calls_state_sink": STATE_SINK_METHOD in receiver_source,
                "runtime_transport_patterns_present": receiver_runtime_patterns,
                "forbidden_pose_patterns_present": receiver_pose_patterns,
                "records_pending_requests": PENDING_METHOD in receiver_source,
                "parses_command_request_schema": COMMAND_SCHEMA_ID in receiver_combined,
                "parses_quadrotor_unreal_state": UNREAL_STATE_SCHEMA_PREFIX in receiver_combined,
            },
            "state_component": {
                "header": repo(STATE_HEADER),
                "source": repo(STATE_SOURCE),
                "pending_source": PENDING_METHOD,
                "echo_sink": STATE_SINK_METHOD,
                "non_live_labels_downgraded": sorted(
                    label for label in NON_LIVE_SOURCES if source_literal(label) in state_source
                ),
                "non_live_source_quality_status": "smoke_only",
                "non_live_accepted_as_runtime_ack": False,
            },
            "frame_status_receiver": {
                "header": repo(FRAME_RECEIVER_HEADER),
                "source": repo(FRAME_RECEIVER_SOURCE),
                "role": "quadrotor.unreal_state frame/status receiver only",
                "parses_command_echo_schema": ECHO_SCHEMA_ID in frame_receiver_combined,
                "calls_echo_sink": STATE_SINK_METHOD in frame_receiver_combined,
            },
            "command_sender": {
                "header": repo(SENDER_HEADER),
                "source": repo(SENDER_SOURCE),
                "role": "mosim.ue_command.v1 sender only",
                "parses_command_echo_schema": ECHO_SCHEMA_ID in sender_combined,
                "calls_echo_sink": STATE_SINK_METHOD in sender_combined,
                "send_success_is_ack": False,
            },
            "build_surface": {
                "uproject": repo(UPROJECT_PATH),
                "engine_association": uproject.get("EngineAssociation"),
                "plugin": repo(UPLUGIN_PATH),
                "module": "QuadrotorMworksBridge",
                "build_cs": repo(BUILD_CS_PATH),
                "build_command_for_future_gate": "Scripts/UE5/build_unreal_renderer.sh",
            },
        },
        "authoritative_echo_acceptance_contract": {
            "pending_precondition": f"matching {COMMAND_SCHEMA_ID} request recorded by {PENDING_METHOD}",
            "echo_schema": ECHO_SCHEMA_ID,
            "consumer_handoff": (
                "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent."
                "ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState"
            ),
            "consumer_sink": STATE_SINK,
            "authoritative_source_authority_pairs": AUTHORITATIVE_LIVE_SOURCES,
            "required_echo_fields": [
                "schema",
                "source",
                "ack_authority",
                "run_id",
                "request_id",
                "seq",
                "time_s",
                "status",
                "command.kind or command_kind",
                "no_pose_overwrite_status",
            ],
            "required_runtime_evidence": [
                "live producer identity",
                "transport capture/log",
                "pending request capture",
                "matching request/echo identity",
                "no_pose_overwrite_status=pass",
                "negative false-ack rejection evidence",
                "bounded probe exit/cleanup evidence",
            ],
        },
        "source_static_readiness_matrix": readiness_matrix,
        "false_ack_rejection_matrix": false_ack_matrix,
        "matrix_summary": {
            "total_readiness_rows": len(readiness_matrix),
            "required_rows_available_now": len(available_required),
            "required_rows_missing_now": len(missing_required),
            "false_ack_rows": len(false_ack_matrix),
            "false_ack_runtime_leaks_now": len(false_ack_runtime_leaks),
            "runtime_ready_now": False,
            "authoritative_runtime_ack_claimable_now": False,
        },
        "next_safe_runtime_gate": {
            "recommendation": "Do not run a live UE runtime probe from 027. Schedule a separate PMO-authorized editor/runtime command-echo probe only after a live MWORKS/ROS2 echo producer/downlink and capture route are available.",
            "minimum_preconditions": [
                "explicit runtime/editor probe authorization",
                "single bounded probe budget and cleanup plan",
                "live authoritative producer for mosim.ue_command_echo.v1",
                "transport capture route from producer to UE command echo receiver",
                "pending mosim.ue_command.v1 request capture",
                "matching run_id/request_id/seq/time_s/command kind/status",
                "no_pose_overwrite_status=pass",
                "negative proof that build/checker/sender/fixture/operator/frame rows cannot satisfy ack",
            ],
            "blocked_now_reason": "No live authoritative producer/downlink transport or runtime capture is available or authorized in 027.",
        },
        "claim_boundary": [
            "027 proves only source-static/build-prep/runtime-readiness classification after UE 024/025/026.",
            "027 does not run Unreal Editor, PIE, standalone runtime, UE runtime, Unreal build, sockets/listeners/timers/background loops, or live transport.",
            "027 does not edit UE C++ source, Blueprint/UMG/Slate/Web UI, assets/materials/maps/project settings, Sunray/PBR, MWORKS, ROS2, FAST-LIO, planner, controller, References, or Git.",
            "024 source handoff, 025 compile pass, 026 checker success, static fixtures, operator intent, sender success, or quadrotor.unreal_state frames are not live runtime ack.",
            "027 does not prove authoritative runtime ack, live MWORKS downlink, ROS2 runtime echo, final UI acceptance, planner_ready, controller performance, mission success, or closed_loop.",
        ],
        "forbidden_runtime_claims": {
            "authoritative_runtime_ack": False,
            "live_ue_runtime_ack": False,
            "live_mworks_downlink": False,
            "ros2_runtime_ack": False,
            "final_ui_acceptance": False,
            "planner_ready": False,
            "closed_loop": False,
            "controller_performance": False,
            "fast_lio_success": False,
            "mission_success": False,
        },
        "issues": issues,
        "warnings": warnings,
    }


def write_summary(report: dict[str, Any], output_md: Path) -> None:
    lines = [
        "# UE 027 Authoritative Echo Runtime Readiness Gate",
        "",
        f"- ok: {report['ok']}",
        f"- scope: {report['scope_classification']}",
        f"- classification: {report['runtime_readiness_classification']}",
        f"- runtime_ready_now: {report['runtime_ready_now']}",
        f"- authoritative_runtime_ack_claimable_now: {report['authoritative_runtime_ack_claimable_now']}",
        "",
        "## Source-Static Readiness Matrix",
        "",
        "| row_id | available_now | required_for_live_ack | accepted_as_runtime_ack_now |",
        "|---|---:|---:|---:|",
    ]
    for row in report["source_static_readiness_matrix"]:
        lines.append(
            f"| {row['row_id']} | {row['available_now']} | "
            f"{row['required_for_live_ack']} | {row['accepted_as_runtime_ack_now']} |"
        )
    lines.extend(
        [
            "",
            "## Next Safe Runtime Gate",
            "",
            report["next_safe_runtime_gate"]["recommendation"],
            "",
            "## Claim Boundary",
            "",
        ]
    )
    for item in report["claim_boundary"]:
        lines.append(f"- {item}")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default="")
    parser.add_argument("--output-md", default="")
    args = parser.parse_args()

    report = build_report()
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output_json:
        output_json = Path(args.output_json)
        if not output_json.is_absolute():
            output_json = ROOT / output_json
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(text + "\n", encoding="utf-8")
    if args.output_md:
        output_md = Path(args.output_md)
        if not output_md.is_absolute():
            output_md = ROOT / output_md
        write_summary(report, output_md)
    print(text)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
