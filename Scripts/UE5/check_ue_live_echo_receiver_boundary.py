#!/usr/bin/env python3
"""Refresh the UE command-echo runtime boundary checker after UE 024/025.

This is a source-static checker only. It records that the project now has a
source-level future authoritative command-echo downlink handoff and compile-only
evidence for that source, while still rejecting any claim of live UE runtime
ack, MWORKS downlink, ROS2 runtime echo, final UI acceptance, planner/controller
success, or closed loop.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-BOUNDARY-CHECKER-REFRESH-20260608-026"
PRIOR_HANDOFF_TASK_ID = "RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-PRODUCER-DOWNLINK-GATE-20260608-024"
PRIOR_COMPILE_TASK_ID = "RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-DOWNLINK-COMPILE-GATE-20260608-025"
COMMAND_SCHEMA_ID = "mosim.ue_command.v1"
ECHO_SCHEMA_ID = "mosim.ue_command_echo.v1"
UNREAL_STATE_SCHEMA_PREFIX = "quadrotor.unreal_state."

BRIDGE_ROOT = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge"
STATE_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksExperimentConsoleStateComponent.h"
STATE_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksExperimentConsoleStateComponent.cpp"
COMMAND_ECHO_RECEIVER_HEADER = (
    BRIDGE_ROOT / "Public/QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.h"
)
COMMAND_ECHO_RECEIVER_SOURCE = (
    BRIDGE_ROOT / "Private/QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.cpp"
)
FRAME_RECEIVER_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksUdpReceiverComponent.h"
FRAME_RECEIVER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksUdpReceiverComponent.cpp"
SENDER_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksUdpCommandSenderComponent.h"
SENDER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksUdpCommandSenderComponent.cpp"

UE_024_RETURN = (
    ROOT
    / "Results/agent_packets/returns/"
    / "RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-PRODUCER-DOWNLINK-GATE-20260608-024.json"
)
UE_024_SUMMARY = (
    ROOT
    / "Results/unreal_experiment_console/runtime_echo_producer_downlink_gate_20260608_024/"
    / "runtime_echo_producer_downlink_gate_summary.md"
)
UE_025_RETURN = (
    ROOT
    / "Results/agent_packets/returns/"
    / "RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-DOWNLINK-COMPILE-GATE-20260608-025.json"
)

PENDING_METHOD = "RecordPendingCommandFromPacketJson"
STATE_SINK_METHOD = "ApplyCommandEchoJson"
SOURCE_STATIC_APPLY_METHOD = "ApplyCommandEchoJsonToState"
DOWNLINK_VALIDATE_METHOD = "IsAuthoritativeRuntimeCommandEchoPacketJson"
DOWNLINK_APPLY_METHOD = "ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState"

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
    "static_catalog_row",
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


def source_literal(source_label: str) -> str:
    return f'TEXT("{source_label}")'


def boundary_row(
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
) -> dict[str, Any]:
    source_authority_matches = AUTHORITATIVE_LIVE_SOURCES.get(source) == ack_authority
    schema_ok = schema == ECHO_SCHEMA_ID
    status_ok = status in {"accepted", "rejected"}
    identity_ok = has_run_id and has_request_id and has_seq and has_command_kind
    timestamp_ok = has_time_s
    no_pose_ok = no_pose_overwrite_status == "pass"
    command_kind_ok = command_kind not in {
        "pose_override",
        "teleport",
        "set_uav_pose",
        "actor_transform",
        "keyboard_pose",
    }
    is_non_live = source in NON_LIVE_SOURCES
    is_false_ack = source in FALSE_ACK_SOURCES or source.startswith("quadrotor.unreal_state")
    handoff_eligible = (
        schema_ok
        and status_ok
        and source_authority_matches
        and identity_ok
        and timestamp_ok
        and no_pose_ok
        and command_kind_ok
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
        "source_authority_matches": source_authority_matches,
        "source_static_handoff_eligible_for_future_live_probe": handoff_eligible,
        "would_be_runtime_ack_if_live_transport_verified": handoff_eligible and status == "accepted",
        "accepted_as_runtime_ack_now": False,
        "actual_runtime_transport_evidence": False,
        "downlink_policy": (
            "source_static_handoff_eligible_future_live_probe"
            if handoff_eligible
            else "reject_before_state_sink"
        ),
    }


def build_boundary_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source, authority in AUTHORITATIVE_LIVE_SOURCES.items():
        rows.append(row := boundary_row(row_name=f"future_authoritative_accepted_{source}", source=source, ack_authority=authority))
        rows.append(
            boundary_row(
                row_name=f"future_authoritative_rejected_{source}",
                source=source,
                ack_authority=authority,
                status="rejected",
            )
        )

    for source in sorted(NON_LIVE_SOURCES):
        rows.append(boundary_row(row_name=f"non_live_{source}", source=source, ack_authority="MWORKS"))
    for source in sorted(FALSE_ACK_SOURCES):
        rows.append(boundary_row(row_name=f"false_ack_{source}", source=source, ack_authority="MWORKS"))

    rows.extend(
        [
            boundary_row(row_name="missing_run_id", source="MWORKS_live_downlink", ack_authority="MWORKS", has_run_id=False),
            boundary_row(row_name="missing_request_id", source="MWORKS_live_downlink", ack_authority="MWORKS", has_request_id=False),
            boundary_row(row_name="missing_seq", source="MWORKS_live_downlink", ack_authority="MWORKS", has_seq=False),
            boundary_row(row_name="missing_time_s", source="MWORKS_live_downlink", ack_authority="MWORKS", has_time_s=False),
            boundary_row(row_name="missing_command_kind", source="MWORKS_live_downlink", ack_authority="MWORKS", has_command_kind=False),
            boundary_row(row_name="wrong_authority_for_source", source="ROS2_runtime_echo", ack_authority="MWORKS"),
            boundary_row(
                row_name="no_pose_overwrite_failure",
                source="MWORKS_live_downlink",
                ack_authority="MWORKS",
                no_pose_overwrite_status="fail",
            ),
            boundary_row(
                row_name="forbidden_pose_command",
                source="MWORKS_live_downlink",
                ack_authority="MWORKS",
                command_kind="teleport",
            ),
            boundary_row(
                row_name="frame_schema_not_echo",
                source="quadrotor.unreal_state.v1",
                ack_authority="MWORKS",
                schema="quadrotor.unreal_state.v1",
            ),
        ]
    )
    # Keep linters quiet while making it visually clear that the first row is intentional.
    assert row
    return rows


def build_report() -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = [
        "source-static checker refresh only; no live UE/MWORKS/ROS2 command echo is claimed",
        "024 source-level handoff and 025 compile pass remain engineering evidence, not live runtime ack",
    ]

    state_header = read(STATE_HEADER)
    state_source = read(STATE_SOURCE)
    state_combined = state_header + "\n" + state_source
    receiver_header = read(COMMAND_ECHO_RECEIVER_HEADER)
    receiver_source = read(COMMAND_ECHO_RECEIVER_SOURCE)
    receiver_combined = receiver_header + "\n" + receiver_source
    frame_receiver_combined = read(FRAME_RECEIVER_HEADER) + "\n" + read(FRAME_RECEIVER_SOURCE)
    sender_combined = read(SENDER_HEADER) + "\n" + read(SENDER_SOURCE)
    ue_024_return = read_json(UE_024_RETURN)
    ue_024_summary = read(UE_024_SUMMARY)
    ue_025_return = read_json(UE_025_RETURN)

    for path, label in [
        (STATE_HEADER, "state component header"),
        (STATE_SOURCE, "state component source"),
        (COMMAND_ECHO_RECEIVER_HEADER, "command echo receiver header"),
        (COMMAND_ECHO_RECEIVER_SOURCE, "command echo receiver source"),
        (FRAME_RECEIVER_HEADER, "frame/status receiver header"),
        (FRAME_RECEIVER_SOURCE, "frame/status receiver source"),
        (SENDER_HEADER, "command sender header"),
        (SENDER_SOURCE, "command sender source"),
        (UE_024_RETURN, "UE 024 return packet"),
        (UE_024_SUMMARY, "UE 024 summary"),
        (UE_025_RETURN, "UE 025 return packet"),
    ]:
        if not path.exists():
            issues.append(f"missing {label}: {repo(path)}")

    if ue_024_return.get("status") != "completed":
        issues.append("UE 024 return is missing or not completed")
    if ue_024_return.get("quality_status") != "runtime_echo_producer_downlink_source_static_build_prep_passed":
        issues.append("UE 024 quality_status is not the expected source-static/build-prep pass")
    if "runtime_ack_leaks=0" not in ue_024_summary:
        issues.append("UE 024 summary does not preserve runtime_ack_leaks=0")
    if "does not prove live UE runtime ack" not in ue_024_summary:
        issues.append("UE 024 summary does not preserve the no-live-ack boundary")

    if ue_025_return.get("status") != "completed":
        issues.append("UE 025 return is missing or not completed")
    if ue_025_return.get("quality_status") != "runtime_echo_downlink_compile_gate_passed":
        issues.append("UE 025 quality_status is not the expected compile-only pass")
    compile_summary = ue_025_return.get("build_only_compile_summary", {})
    if compile_summary.get("exit_code") != 0:
        issues.append("UE 025 compile summary does not record exit_code=0")
    if compile_summary.get("classification") != "compile_pass_warning_only":
        issues.append("UE 025 compile summary classification is not compile_pass_warning_only")

    receiver_required_anchors = [
        "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent",
        DOWNLINK_VALIDATE_METHOD,
        DOWNLINK_APPLY_METHOD,
        SOURCE_STATIC_APPLY_METHOD,
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
            issues.append(f"command echo receiver shell missing anchor: {anchor}")
    if PENDING_METHOD in receiver_source:
        issues.append("command echo receiver shell must not record pending requests")
    if COMMAND_SCHEMA_ID in receiver_combined:
        issues.append("command echo receiver shell must not parse mosim.ue_command.v1 command requests")
    if UNREAL_STATE_SCHEMA_PREFIX in receiver_combined:
        issues.append("command echo receiver shell must not parse quadrotor.unreal_state frames")

    receiver_runtime_patterns = present(receiver_combined, FORBIDDEN_RUNTIME_RECEIVER_PATTERNS)
    if receiver_runtime_patterns:
        issues.append(
            "command echo receiver shell contains runtime transport pattern(s): "
            + ", ".join(receiver_runtime_patterns)
        )
    receiver_pose_patterns = present(receiver_combined, FORBIDDEN_POSE_PATTERNS)
    if receiver_pose_patterns:
        issues.append(
            "command echo receiver shell contains direct pose/input pattern(s): "
            + ", ".join(receiver_pose_patterns)
        )

    if "UQuadrotorMworksExperimentConsoleStateComponent" not in state_combined:
        issues.append("missing UQuadrotorMworksExperimentConsoleStateComponent anchor")
    if PENDING_METHOD not in state_combined:
        issues.append("state component lacks pending command request reducer")
    if STATE_SINK_METHOD not in state_combined:
        issues.append("state component lacks command echo sink")
    for label in NON_LIVE_SOURCES:
        if source_literal(label) not in state_source:
            issues.append(f"state component does not downgrade non-live source label: {label}")
    for pattern in sorted(FORBIDDEN_POSE_PATTERNS):
        if pattern in state_combined:
            issues.append(f"state component exposes forbidden Actor/input pose route: {pattern}")

    if UNREAL_STATE_SCHEMA_PREFIX not in frame_receiver_combined:
        issues.append("frame/status receiver missing quadrotor.unreal_state schema guard")
    if ECHO_SCHEMA_ID in frame_receiver_combined:
        issues.append("frame/status receiver must not parse mosim.ue_command_echo.v1")
    if STATE_SINK_METHOD in frame_receiver_combined:
        issues.append("frame/status receiver must not call command echo state sink")
    if ECHO_SCHEMA_ID in sender_combined:
        issues.append("command sender must not parse mosim.ue_command_echo.v1")
    if STATE_SINK_METHOD in sender_combined:
        issues.append("command sender must not call command echo state sink")
    if COMMAND_SCHEMA_ID not in sender_combined:
        issues.append("command sender missing mosim.ue_command.v1 anchor")
    if "Result.bSent" not in sender_combined:
        issues.append("command sender missing sender-success negative-ack anchor")

    matrix = build_boundary_matrix()
    handoff_eligible_rows = [
        row for row in matrix if row["source_static_handoff_eligible_for_future_live_probe"]
    ]
    future_accepted_rows = [
        row for row in handoff_eligible_rows if row["status"] == "accepted"
    ]
    future_rejected_rows = [
        row for row in handoff_eligible_rows if row["status"] == "rejected"
    ]
    non_live_rows = [row for row in matrix if row["source"] in NON_LIVE_SOURCES]
    false_ack_rows = [row for row in matrix if row["source"] in FALSE_ACK_SOURCES]
    invalid_rows = [
        row
        for row in matrix
        if row["row_name"]
        in {
            "missing_run_id",
            "missing_request_id",
            "missing_seq",
            "missing_time_s",
            "missing_command_kind",
            "wrong_authority_for_source",
            "no_pose_overwrite_failure",
            "forbidden_pose_command",
            "frame_schema_not_echo",
        }
    ]
    runtime_ack_leaks = [row for row in matrix if row["accepted_as_runtime_ack_now"]]
    actual_runtime_claim_rows = [row for row in matrix if row["actual_runtime_transport_evidence"]]

    if len(future_accepted_rows) != len(AUTHORITATIVE_LIVE_SOURCES):
        issues.append("matrix lacks one future accepted handoff-eligible row per authoritative source")
    if len(future_rejected_rows) != len(AUTHORITATIVE_LIVE_SOURCES):
        issues.append("matrix lacks one future rejected handoff-eligible row per authoritative source")
    if any(row["source_static_handoff_eligible_for_future_live_probe"] for row in non_live_rows):
        issues.append("non-live rows are handoff-eligible")
    if any(row["source_static_handoff_eligible_for_future_live_probe"] for row in false_ack_rows):
        issues.append("false-ack rows are handoff-eligible")
    if any(row["source_static_handoff_eligible_for_future_live_probe"] for row in invalid_rows):
        issues.append("invalid rows are handoff-eligible")
    if runtime_ack_leaks:
        issues.append("source-static checker leaks accepted_as_runtime_ack_now=true")
    if actual_runtime_claim_rows:
        issues.append("source-static checker claims actual runtime transport evidence")

    source_static_handoff_present = (
        DOWNLINK_VALIDATE_METHOD in receiver_combined
        and DOWNLINK_APPLY_METHOD in receiver_combined
        and not receiver_runtime_patterns
    )
    compile_only_evidence_present = (
        ue_025_return.get("status") == "completed"
        and compile_summary.get("exit_code") == 0
        and compile_summary.get("classification") == "compile_pass_warning_only"
    )

    return {
        "schema": "mosim.ue_runtime_echo_boundary_checker_refresh_static_gate.v1",
        "ok": not issues,
        "task_id": TASK_ID,
        "prior_source_handoff_task_id": PRIOR_HANDOFF_TASK_ID,
        "prior_compile_task_id": PRIOR_COMPILE_TASK_ID,
        "scope_classification": "source-static checker/test/evidence refresh",
        "source_static_authoritative_downlink_handoff_present": source_static_handoff_present,
        "compile_only_evidence_present": compile_only_evidence_present,
        "runtime_probe_executed": False,
        "ue_runtime_started": False,
        "unreal_editor_opened": False,
        "unreal_build_executed_in_026": False,
        "live_transport_bound_or_started": False,
        "accepted_state_ui_controls_enabled": False,
        "receiver_boundary_decision": {
            "source_static_echo_receiver_shell_present": source_static_handoff_present,
            "runtime_transport_receiver_present": False,
            "current_live_echo_receiver_present": False,
            "existing_udp_receiver_role": "quadrotor.unreal_state frame/status receiver only",
            "command_sender_role": "mosim.ue_command.v1 sender only",
            "future_receiver_input_schema": ECHO_SCHEMA_ID,
            "future_receiver_handoff": (
                "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent."
                "ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState"
            ),
            "future_receiver_sink": (
                "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson"
            ),
            "future_live_runtime_ack_gate": (
                "requires actual live transport receipt of mosim.ue_command_echo.v1 "
                "matching a pending mosim.ue_command.v1 request"
            ),
        },
        "prior_gate_inputs": {
            "ue_024_return": repo(UE_024_RETURN),
            "ue_024_summary": repo(UE_024_SUMMARY),
            "ue_025_return": repo(UE_025_RETURN),
            "ue_024_status": ue_024_return.get("status"),
            "ue_024_quality_status": ue_024_return.get("quality_status"),
            "ue_025_status": ue_025_return.get("status"),
            "ue_025_quality_status": ue_025_return.get("quality_status"),
            "ue_025_compile_classification": compile_summary.get("classification"),
            "ue_025_compile_exit_code": compile_summary.get("exit_code"),
        },
        "source_anchor_summary": {
            "command_echo_receiver_shell": {
                "header": repo(COMMAND_ECHO_RECEIVER_HEADER),
                "source": repo(COMMAND_ECHO_RECEIVER_SOURCE),
                "role": "source-static future authoritative command echo downlink handoff only",
                "has_authoritative_validate_method": DOWNLINK_VALIDATE_METHOD in receiver_combined,
                "has_authoritative_apply_method": DOWNLINK_APPLY_METHOD in receiver_combined,
                "has_source_static_apply_method": SOURCE_STATIC_APPLY_METHOD in receiver_combined,
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
        },
        "source_labels": {
            "non_live_sources_expected": sorted(NON_LIVE_SOURCES),
            "non_live_sources_covered_by_state_component": sorted(
                label for label in NON_LIVE_SOURCES if source_literal(label) in state_source
            ),
            "non_live_sources_missing_from_state_component": sorted(
                label for label in NON_LIVE_SOURCES if source_literal(label) not in state_source
            ),
            "non_live_source_quality_status": "smoke_only",
            "non_live_accepted_as_runtime_ack": False,
            "future_authoritative_source_candidates": AUTHORITATIVE_LIVE_SOURCES,
            "false_ack_sources_rejected_now": sorted(FALSE_ACK_SOURCES),
        },
        "boundary_fixture_matrix": matrix,
        "matrix_summary": {
            "total_rows": len(matrix),
            "future_authoritative_handoff_eligible_rows": len(handoff_eligible_rows),
            "future_authoritative_accepted_rows": len(future_accepted_rows),
            "future_authoritative_rejected_rows": len(future_rejected_rows),
            "non_live_rows": len(non_live_rows),
            "false_ack_rows": len(false_ack_rows),
            "invalid_rows": len(invalid_rows),
            "runtime_ack_leaks_now": len(runtime_ack_leaks),
            "actual_runtime_claim_rows": len(actual_runtime_claim_rows),
        },
        "rules": [
            "pending rows may originate only from matching mosim.ue_command.v1 command requests",
            "accepted/rejected rows may originate only from authoritative mosim.ue_command_echo.v1",
            "source-static handoff eligibility is not live runtime ack evidence",
            "024 source-static handoff and 025 compile pass cannot satisfy runtime ack",
            "offline/source/preflight/build/sender/frame/fixture/operator-intent rows must keep accepted_as_runtime_ack_now=false",
            "quadrotor.unreal_state frame/status downlink cannot be used as command ack",
            "UDP send success cannot be used as command ack",
        ],
        "claim_boundary": {
            "not_live_ue_runtime_ack": True,
            "not_live_mworks_downlink": True,
            "not_ros2_runtime_ack": True,
            "not_final_ui_acceptance": True,
            "planner_ready": False,
            "closed_loop_ready": False,
            "controller_performance": False,
            "fast_lio_success": False,
            "mission_success": False,
        },
        "forbidden_runtime_claims": {
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default="")
    args = parser.parse_args()

    report = build_report()
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
