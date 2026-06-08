#!/usr/bin/env python3
"""Prepare the UE authoritative command-echo runtime probe harness contract.

This is a source-static/runtime-probe harness-prep checker only. It defines the
minimum evidence a future single bounded live UE runtime probe must capture,
while preserving that no live runtime command ack is claimable from this task.
It does not open Unreal Editor, run UE runtime/build, bind sockets, start
listeners/timers/background loops, or touch MWORKS/ROS2/planner surfaces.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "RFLY-MOSIM-UE-CONSOLE-RUNTIME-PROBE-HARNESS-PREP-20260608-028"
COMMAND_SCHEMA_ID = "mosim.ue_command.v1"
ECHO_SCHEMA_ID = "mosim.ue_command_echo.v1"
UNREAL_STATE_SCHEMA_PREFIX = "quadrotor.unreal_state."

COMMAND_SCHEMA_PATH = ROOT / "Config/schemas/mosim_ue_command_v1.schema.json"
ECHO_SCHEMA_PATH = ROOT / "Config/schemas/mosim_ue_command_echo_v1.schema.json"
BRIDGE_ROOT = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge"
RECEIVER_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.h"
RECEIVER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.cpp"
STATE_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksExperimentConsoleStateComponent.h"
STATE_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksExperimentConsoleStateComponent.cpp"
FRAME_RECEIVER_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksUdpReceiverComponent.h"
FRAME_RECEIVER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksUdpReceiverComponent.cpp"
SENDER_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksUdpCommandSenderComponent.h"
SENDER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksUdpCommandSenderComponent.cpp"

RETURN_027 = (
    ROOT
    / "Results/agent_packets/returns/"
    / "RFLY-MOSIM-UE-CONSOLE-AUTHORITATIVE-ECHO-RUNTIME-READINESS-GATE-20260608-027.json"
)
EVIDENCE_027 = (
    ROOT
    / "Results/unreal_experiment_console/authoritative_echo_runtime_readiness_gate_20260608_027/"
    / "authoritative_echo_runtime_readiness_gate.json"
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
    "027_runtime_readiness_checker",
    "028_harness_prep_checker",
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
FORBIDDEN_COMMAND_KINDS = {
    "pose_override",
    "teleport",
    "set_uav_pose",
    "actor_transform",
    "keyboard_pose",
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


def future_probe_row(
    *,
    row_name: str,
    source: str,
    ack_authority: str,
    status: str = "accepted",
    schema: str = ECHO_SCHEMA_ID,
    has_run_id: bool = True,
    has_request_id: bool = True,
    has_seq: bool = True,
    has_time_s: bool = True,
    has_command_kind: bool = True,
    command_kind: str = "controller_select",
    no_pose_overwrite_status: str = "pass",
    producer_identity_captured: bool = True,
    pending_request_captured: bool = True,
    echo_capture_present: bool = True,
    cleanup_plan_present: bool = True,
) -> dict[str, Any]:
    source_authority_matches = AUTHORITATIVE_LIVE_SOURCES.get(source) == ack_authority
    schema_ok = schema == ECHO_SCHEMA_ID
    status_ok = status in {"accepted", "rejected"}
    identity_ok = has_run_id and has_request_id and has_seq and has_time_s and has_command_kind
    no_pose_ok = no_pose_overwrite_status == "pass"
    command_kind_ok = command_kind not in FORBIDDEN_COMMAND_KINDS
    is_non_live = source in NON_LIVE_SOURCES
    is_false_ack = source in FALSE_ACK_SOURCES or source.startswith("quadrotor.unreal_state")
    source_static_contract_eligible = (
        schema_ok
        and status_ok
        and source_authority_matches
        and identity_ok
        and no_pose_ok
        and command_kind_ok
        and producer_identity_captured
        and pending_request_captured
        and echo_capture_present
        and cleanup_plan_present
        and not is_non_live
        and not is_false_ack
    )
    return {
        "row_name": row_name,
        "schema": schema,
        "source": source,
        "ack_authority": ack_authority,
        "status": status,
        "has_run_id": has_run_id,
        "has_request_id": has_request_id,
        "has_seq": has_seq,
        "has_time_s": has_time_s,
        "has_command_kind": has_command_kind,
        "command_kind": command_kind,
        "no_pose_overwrite_status": no_pose_overwrite_status,
        "producer_identity_captured": producer_identity_captured,
        "pending_request_captured": pending_request_captured,
        "echo_capture_present": echo_capture_present,
        "cleanup_plan_present": cleanup_plan_present,
        "source_authority_matches": source_authority_matches,
        "source_static_contract_eligible_for_future_probe": source_static_contract_eligible,
        "would_be_runtime_ack_if_future_live_transport_verified": (
            source_static_contract_eligible and status == "accepted"
        ),
        "accepted_as_runtime_ack_now": False,
        "actual_runtime_transport_evidence": False,
        "policy": (
            "future_live_probe_contract_eligible"
            if source_static_contract_eligible
            else "reject_before_runtime_ack_claim"
        ),
    }


def build_future_probe_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source, authority in AUTHORITATIVE_LIVE_SOURCES.items():
        rows.append(
            future_probe_row(
                row_name=f"future_authoritative_accepted_{source}",
                source=source,
                ack_authority=authority,
            )
        )
        rows.append(
            future_probe_row(
                row_name=f"future_authoritative_rejected_{source}",
                source=source,
                ack_authority=authority,
                status="rejected",
            )
        )

    for source in sorted(NON_LIVE_SOURCES):
        rows.append(future_probe_row(row_name=f"non_live_{source}", source=source, ack_authority="MWORKS"))
    for source in sorted(FALSE_ACK_SOURCES):
        rows.append(future_probe_row(row_name=f"false_ack_{source}", source=source, ack_authority="MWORKS"))

    rows.extend(
        [
            future_probe_row(row_name="missing_producer_identity", source="MWORKS_live_downlink", ack_authority="MWORKS", producer_identity_captured=False),
            future_probe_row(row_name="missing_pending_request_capture", source="MWORKS_live_downlink", ack_authority="MWORKS", pending_request_captured=False),
            future_probe_row(row_name="missing_echo_capture", source="MWORKS_live_downlink", ack_authority="MWORKS", echo_capture_present=False),
            future_probe_row(row_name="missing_cleanup_plan", source="MWORKS_live_downlink", ack_authority="MWORKS", cleanup_plan_present=False),
            future_probe_row(row_name="missing_run_id", source="MWORKS_live_downlink", ack_authority="MWORKS", has_run_id=False),
            future_probe_row(row_name="missing_request_id", source="MWORKS_live_downlink", ack_authority="MWORKS", has_request_id=False),
            future_probe_row(row_name="missing_seq", source="MWORKS_live_downlink", ack_authority="MWORKS", has_seq=False),
            future_probe_row(row_name="missing_time_s", source="MWORKS_live_downlink", ack_authority="MWORKS", has_time_s=False),
            future_probe_row(row_name="missing_command_kind", source="MWORKS_live_downlink", ack_authority="MWORKS", has_command_kind=False),
            future_probe_row(row_name="wrong_authority_for_source", source="ROS2_runtime_echo", ack_authority="MWORKS"),
            future_probe_row(row_name="no_pose_overwrite_failure", source="MWORKS_live_downlink", ack_authority="MWORKS", no_pose_overwrite_status="fail"),
            future_probe_row(row_name="forbidden_pose_command", source="MWORKS_live_downlink", ack_authority="MWORKS", command_kind="teleport"),
            future_probe_row(row_name="frame_schema_not_echo", source="quadrotor.unreal_state.v1", ack_authority="MWORKS", schema="quadrotor.unreal_state.v1"),
        ]
    )
    return rows


def harness_readiness_row(
    row_id: str,
    available_now: bool,
    evidence: str,
    required_for_future_live_probe: bool,
    missing_reason: str = "",
) -> dict[str, Any]:
    return {
        "row_id": row_id,
        "available_now": available_now,
        "required_for_future_live_probe": required_for_future_live_probe,
        "accepted_as_runtime_ack_now": False,
        "evidence": evidence,
        "missing_reason": missing_reason,
    }


def build_report() -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = [
        "028 is source-static/runtime-probe harness prep only.",
        "The generated harness contract is not live UE runtime ack evidence.",
    ]

    command_schema = read_json(COMMAND_SCHEMA_PATH)
    echo_schema = read_json(ECHO_SCHEMA_PATH)
    return_027 = read_json(RETURN_027)
    evidence_027 = read_json(EVIDENCE_027)
    receiver_header = read(RECEIVER_HEADER)
    receiver_source = read(RECEIVER_SOURCE)
    receiver_combined = receiver_header + "\n" + receiver_source
    state_header = read(STATE_HEADER)
    state_source = read(STATE_SOURCE)
    state_combined = state_header + "\n" + state_source
    frame_receiver_combined = read(FRAME_RECEIVER_HEADER) + "\n" + read(FRAME_RECEIVER_SOURCE)
    sender_combined = read(SENDER_HEADER) + "\n" + read(SENDER_SOURCE)

    for path, label in [
        (COMMAND_SCHEMA_PATH, "mosim.ue_command.v1 schema"),
        (ECHO_SCHEMA_PATH, "mosim.ue_command_echo.v1 schema"),
        (RETURN_027, "UE 027 return packet"),
        (EVIDENCE_027, "UE 027 readiness evidence"),
        (RECEIVER_HEADER, "command echo receiver header"),
        (RECEIVER_SOURCE, "command echo receiver source"),
        (STATE_HEADER, "experiment console state header"),
        (STATE_SOURCE, "experiment console state source"),
        (FRAME_RECEIVER_HEADER, "quadrotor.unreal_state receiver header"),
        (FRAME_RECEIVER_SOURCE, "quadrotor.unreal_state receiver source"),
        (SENDER_HEADER, "command sender header"),
        (SENDER_SOURCE, "command sender source"),
    ]:
        if not path.exists():
            issues.append(f"missing {label}: {repo(path)}")

    if command_schema.get("schema") != COMMAND_SCHEMA_ID:
        issues.append("mosim.ue_command.v1 schema missing or invalid")
    if echo_schema.get("schema") != ECHO_SCHEMA_ID:
        issues.append("mosim.ue_command_echo.v1 schema missing or invalid")
    for field in ["schema", "type", "run_id", "request_id", "seq", "time_s", "requested_by", "command", "guard"]:
        if field not in command_schema.get("required", []):
            issues.append(f"command schema missing required field: {field}")
    for field in ["schema", "status", "run_id", "request_id", "ack_authority", "no_pose_overwrite_status"]:
        if field not in echo_schema.get("runtime_required", []):
            issues.append(f"echo schema missing runtime_required field: {field}")
    for field in ["source", "seq", "time_s", "command.kind or command_kind"]:
        if field not in echo_schema.get("runtime_required", []):
            warnings.append(f"future probe contract requires {field} even though echo schema runtime_required does not list it")

    if return_027.get("status") != "completed":
        issues.append("UE 027 return is missing or not completed")
    if return_027.get("quality_status") != "authoritative_echo_runtime_readiness_source_static_passed":
        issues.append("UE 027 quality_status is not the expected source-static readiness pass")
    if evidence_027.get("ok") is not True:
        issues.append("UE 027 readiness evidence is not ok=true")
    if evidence_027.get("runtime_ready_now") is not False:
        issues.append("UE 027 evidence must preserve runtime_ready_now=false")
    if evidence_027.get("authoritative_runtime_ack_claimable_now") is not False:
        issues.append("UE 027 evidence must preserve authoritative_runtime_ack_claimable_now=false")
    if evidence_027.get("matrix_summary", {}).get("false_ack_runtime_leaks_now") != 0:
        issues.append("UE 027 evidence has false ack runtime leaks")

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
            issues.append(f"command echo receiver missing future probe anchor: {anchor}")
    if PENDING_METHOD in receiver_source:
        issues.append("command echo receiver must not record pending requests")
    if COMMAND_SCHEMA_ID in receiver_combined:
        issues.append("command echo receiver must not parse command request schema")
    if UNREAL_STATE_SCHEMA_PREFIX in receiver_combined:
        issues.append("command echo receiver must not parse quadrotor.unreal_state frames")

    receiver_runtime_patterns = present(receiver_combined, FORBIDDEN_RUNTIME_RECEIVER_PATTERNS)
    if receiver_runtime_patterns:
        issues.append("command echo receiver contains runtime transport pattern(s): " + ", ".join(receiver_runtime_patterns))
    receiver_pose_patterns = present(receiver_combined, FORBIDDEN_POSE_PATTERNS)
    if receiver_pose_patterns:
        issues.append("command echo receiver contains forbidden pose/input pattern(s): " + ", ".join(receiver_pose_patterns))

    state_required_anchors = [
        PENDING_METHOD,
        STATE_SINK_METHOD,
        COMMAND_SCHEMA_ID,
        ECHO_SCHEMA_ID,
        "seq_mismatch",
        "command_kind_mismatch",
        "no_pose_overwrite_not_pass",
    ]
    for anchor in state_required_anchors:
        if anchor not in state_combined:
            issues.append(f"state component missing future probe reducer anchor: {anchor}")
    missing_non_live_labels = sorted(label for label in NON_LIVE_SOURCES if source_literal(label) not in state_source)
    if missing_non_live_labels:
        issues.append("state component missing non-live source labels: " + ", ".join(missing_non_live_labels))
    state_pose_patterns = present(state_combined, FORBIDDEN_POSE_PATTERNS)
    if state_pose_patterns:
        issues.append("state component contains forbidden pose/input pattern(s): " + ", ".join(state_pose_patterns))

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
        issues.append("command sender missing command request schema anchor")

    source_static_receiver_ready = (
        DOWNLINK_VALIDATE_METHOD in receiver_combined
        and DOWNLINK_APPLY_METHOD in receiver_combined
        and STATE_SINK_METHOD in receiver_source
        and not receiver_runtime_patterns
        and not receiver_pose_patterns
    )
    pending_reducer_ready = PENDING_METHOD in state_combined
    echo_sink_ready = STATE_SINK_METHOD in state_combined
    readiness_matrix = [
        harness_readiness_row("prior_027_source_static_readiness", evidence_027.get("ok") is True, repo(EVIDENCE_027), True),
        harness_readiness_row("command_request_schema_identity", command_schema.get("schema") == COMMAND_SCHEMA_ID, repo(COMMAND_SCHEMA_PATH), True),
        harness_readiness_row("command_echo_schema_boundary", echo_schema.get("schema") == ECHO_SCHEMA_ID, repo(ECHO_SCHEMA_PATH), True),
        harness_readiness_row("source_static_authoritative_echo_receiver", source_static_receiver_ready, f"{repo(RECEIVER_HEADER)}; {repo(RECEIVER_SOURCE)}", True),
        harness_readiness_row("pending_request_capture_sink", pending_reducer_ready, f"{repo(STATE_HEADER)}; {repo(STATE_SOURCE)}", True),
        harness_readiness_row("authoritative_echo_state_sink", echo_sink_ready, f"{repo(STATE_HEADER)}; {repo(STATE_SOURCE)}", True),
        harness_readiness_row("no_diff_harness_plan", True, "generated by this checker", True),
        harness_readiness_row("future_live_authoritative_echo_producer", False, "not present in 028 source-static scope", True, "future PMO-authorized live producer/downlink required"),
        harness_readiness_row("future_live_transport_capture", False, "not present in 028 source-static scope", True, "future bounded runtime transport capture required"),
        harness_readiness_row("future_runtime_no_pose_overwrite_capture", False, "not present in 028 source-static scope", True, "future live probe must capture no_pose_overwrite_status=pass"),
        harness_readiness_row("future_runtime_false_ack_negative_capture", False, "not present in 028 source-static scope", True, "future live probe must capture negative false-ack evidence"),
        harness_readiness_row("future_cleanup_manifest", False, "not present in 028 source-static scope", True, "future live probe must capture timeout and cleanup manifest"),
    ]

    future_probe_matrix = build_future_probe_matrix()
    future_eligible_rows = [
        row for row in future_probe_matrix if row["source_static_contract_eligible_for_future_probe"]
    ]
    future_eligible_accepted = [row for row in future_eligible_rows if row["status"] == "accepted"]
    future_eligible_rejected = [row for row in future_eligible_rows if row["status"] == "rejected"]
    negative_rows = [
        row
        for row in future_probe_matrix
        if row["source"] in NON_LIVE_SOURCES
        or row["source"] in FALSE_ACK_SOURCES
        or row["row_name"].startswith("missing_")
        or row["row_name"] in {"wrong_authority_for_source", "no_pose_overwrite_failure", "forbidden_pose_command", "frame_schema_not_echo"}
    ]
    false_ack_runtime_leaks = [row for row in future_probe_matrix if row["accepted_as_runtime_ack_now"]]
    actual_runtime_claim_rows = [row for row in future_probe_matrix if row["actual_runtime_transport_evidence"]]
    if len(future_eligible_accepted) != len(AUTHORITATIVE_LIVE_SOURCES):
        issues.append("future probe matrix lacks one accepted eligible row per authoritative source")
    if len(future_eligible_rejected) != len(AUTHORITATIVE_LIVE_SOURCES):
        issues.append("future probe matrix lacks one rejected eligible row per authoritative source")
    if any(row["source_static_contract_eligible_for_future_probe"] for row in negative_rows):
        issues.append("negative/false-ack rows are future-probe eligible")
    if false_ack_runtime_leaks:
        issues.append("future probe matrix leaks accepted_as_runtime_ack_now=true")
    if actual_runtime_claim_rows:
        issues.append("future probe matrix claims actual runtime transport evidence")

    return {
        "schema": "mosim.ue_runtime_probe_harness_prep.v1",
        "ok": not issues,
        "task_id": TASK_ID,
        "scope_classification": "source-static/runtime-probe-harness-prep",
        "source_diff_required_for_028": False,
        "cxx_edits_performed_by_028": False,
        "runtime_probe_executed": False,
        "unreal_editor_opened": False,
        "ue_runtime_started": False,
        "unreal_build_executed_in_028": False,
        "socket_listener_timer_or_background_loop_started": False,
        "accepted_state_ui_controls_enabled": False,
        "authoritative_runtime_ack_claimable_now": False,
        "no_diff_harness_plan": {
            "plan_type": "precise_no_diff_harness_plan",
            "existing_source_anchors_sufficient": source_static_receiver_ready and pending_reducer_ready and echo_sink_ready,
            "reason": "Existing project-owned receiver/state anchors can consume a future authoritative echo after a pending request; 028 only needs the future live probe capture contract and static tests.",
            "next_code_surface": "No UE C++ diff is required before the next PMO-authorized single bounded live runtime probe unless that task adds a transport/capture adapter.",
        },
        "prior_gate_inputs": {
            "ue_027_return": repo(RETURN_027),
            "ue_027_evidence": repo(EVIDENCE_027),
            "ue_027_status": return_027.get("status"),
            "ue_027_quality_status": return_027.get("quality_status"),
            "ue_027_runtime_ready_now": evidence_027.get("runtime_ready_now"),
            "ue_027_authoritative_runtime_ack_claimable_now": evidence_027.get("authoritative_runtime_ack_claimable_now"),
            "ue_027_false_ack_runtime_leaks_now": evidence_027.get("matrix_summary", {}).get("false_ack_runtime_leaks_now"),
        },
        "source_anchor_summary": {
            "command_echo_receiver": {
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
                "non_live_labels_downgraded": sorted(label for label in NON_LIVE_SOURCES if source_literal(label) in state_source),
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
        },
        "runtime_probe_harness_contract": {
            "future_probe_scope": "single bounded PMO-authorized UE runtime/editor probe only",
            "producer_identity_required": [
                "producer_surface",
                "producer_instance_id",
                "source",
                "ack_authority",
                "capture_session_id",
                "transport_capture_id",
            ],
            "authoritative_source_authority_pairs": AUTHORITATIVE_LIVE_SOURCES,
            "pending_request_capture": {
                "schema": COMMAND_SCHEMA_ID,
                "required_fields": [
                    "schema",
                    "type",
                    "run_id",
                    "request_id",
                    "seq",
                    "time_s",
                    "requested_by",
                    "command.kind",
                    "guard.require_mworks_ack",
                    "guard.require_ros2_ack",
                ],
                "source": "UE command request path only",
            },
            "echo_capture": {
                "schema": ECHO_SCHEMA_ID,
                "required_fields": [
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
                "status_values": ["accepted", "rejected"],
            },
            "matching_identity_fields": [
                "run_id",
                "request_id",
                "seq",
                "time_s",
                "command.kind or command_kind",
                "status",
            ],
            "no_pose_overwrite_proof": {
                "required_value": "no_pose_overwrite_status=pass",
                "forbidden_command_kinds": sorted(FORBIDDEN_COMMAND_KINDS),
                "forbidden_shortcuts": [
                    "keyboard pose control",
                    "direct Actor teleport",
                    "pose_override",
                    "fake command echo",
                    "UE truth shortcut",
                ],
            },
            "negative_false_ack_proof": {
                "must_reject_sources": sorted(FALSE_ACK_SOURCES | NON_LIVE_SOURCES),
                "must_reject_frame_topics": ["quadrotor.unreal_state.frame", "quadrotor.unreal_state.v1"],
                "must_reject_sender_success": ["sender_result_bSent", "udp_send_success"],
            },
            "timeout_and_cleanup": {
                "bounded_probe_required": True,
                "default_timeout_seconds": 60,
                "cleanup_manifest_required": True,
                "cleanup_assertions": [
                    "probe exits after one bounded attempt",
                    "no listener/timer/background loop remains",
                    "no accepted UI state is enabled by cleanup",
                    "runtime windows/process state is recorded by the future task",
                ],
            },
            "future_capture_artifacts": [
                "runtime_probe_manifest.json",
                "pending_request_capture.json",
                "authoritative_echo_capture.json",
                "request_echo_match_report.json",
                "no_pose_overwrite_report.json",
                "false_ack_negative_report.json",
                "timeout_cleanup_manifest.json",
            ],
        },
        "harness_readiness_matrix": readiness_matrix,
        "future_probe_fixture_matrix": future_probe_matrix,
        "matrix_summary": {
            "harness_rows": len(readiness_matrix),
            "source_static_rows_available_now": sum(1 for row in readiness_matrix if row["available_now"]),
            "future_runtime_rows_missing_now": sum(1 for row in readiness_matrix if row["required_for_future_live_probe"] and not row["available_now"]),
            "future_probe_fixture_rows": len(future_probe_matrix),
            "future_contract_eligible_accepted_rows": len(future_eligible_accepted),
            "future_contract_eligible_rejected_rows": len(future_eligible_rejected),
            "negative_or_false_ack_rows": len(negative_rows),
            "false_ack_runtime_leaks_now": len(false_ack_runtime_leaks),
            "actual_runtime_claim_rows": len(actual_runtime_claim_rows),
            "authoritative_runtime_ack_claimable_now": False,
        },
        "next_safe_runtime_gate": {
            "recommendation": "Schedule a separate PMO-authorized single bounded live UE runtime command-echo probe only after an authoritative MWORKS/ROS2 producer and capture surface are available.",
            "minimum_acceptance_gates": [
                "runtime/editor probe explicitly authorized by PMO",
                "producer identity captured for MWORKS_live_downlink, ROS2_runtime_echo, or MWORKS_ROS2_live_downlink",
                "pending mosim.ue_command.v1 request captured before echo",
                "authoritative mosim.ue_command_echo.v1 echo captured from live transport",
                "run_id/request_id/seq/time_s/command kind/status match policy evaluated",
                "no_pose_overwrite_status=pass captured",
                "false-ack negative report rejects build/checker/sender/fixture/operator/frame rows",
                "timeout and cleanup manifest captured after one bounded attempt",
            ],
            "blocked_now_reason": "028 does not authorize UE runtime/editor launch, live transport, socket/listener/timer/background loop, MWORKS/ROS2 producer execution, or runtime capture.",
        },
        "claim_boundary": [
            "028 proves only source-static/runtime-probe harness preparation.",
            "028 does not open Unreal Editor, PIE, standalone runtime, or UE runtime.",
            "028 does not run Unreal build or bind sockets/listeners/timers/background loops.",
            "028 does not edit UE C++ source, Blueprint/UMG/Slate/Web UI, assets/materials/maps/project settings, Sunray/PBR, MWORKS, ROS2, FAST-LIO, planner, controller, References, or Git.",
            "028 checker/test/source-static rows are not live runtime ack.",
            "024 source handoff, 025 compile pass, 026 checker success, 027 readiness, sender success, fixture rows, operator intent, pytest/checker success, or quadrotor.unreal_state frames are not live runtime ack.",
            "028 does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime echo, final UI acceptance, planner_ready, FAST-LIO success, controller performance, mission success, or closed_loop.",
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
        "# UE 028 Runtime Probe Harness Prep",
        "",
        f"- ok: {report['ok']}",
        f"- scope: {report['scope_classification']}",
        f"- source_diff_required_for_028: {report['source_diff_required_for_028']}",
        f"- runtime_probe_executed: {report['runtime_probe_executed']}",
        f"- authoritative_runtime_ack_claimable_now: {report['authoritative_runtime_ack_claimable_now']}",
        "",
        "## Harness Readiness Matrix",
        "",
        "| row_id | available_now | accepted_as_runtime_ack_now |",
        "|---|---:|---:|",
    ]
    for row in report["harness_readiness_matrix"]:
        lines.append(f"| {row['row_id']} | {row['available_now']} | {row['accepted_as_runtime_ack_now']} |")
    lines.extend(["", "## Future Capture Artifacts", ""])
    for item in report["runtime_probe_harness_contract"]["future_capture_artifacts"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Claim Boundary", ""])
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
