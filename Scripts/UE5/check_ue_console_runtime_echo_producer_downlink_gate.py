#!/usr/bin/env python3
"""Check the UE runtime echo producer/downlink source-static/build-prep gate.

This checker verifies the source-level handoff that a future authorized live
transport may use to feed authoritative mosim.ue_command_echo.v1 rows into the
experiment-console state reducer. It does not open Unreal Editor, start UE
runtime, bind ports, implement sockets/listeners/timers, or claim live ack.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-PRODUCER-DOWNLINK-GATE-20260608-024"
COMMAND_SCHEMA_ID = "mosim.ue_command.v1"
ECHO_SCHEMA_ID = "mosim.ue_command_echo.v1"
DOWNLINK_VALIDATE_METHOD = "IsAuthoritativeRuntimeCommandEchoPacketJson"
DOWNLINK_APPLY_METHOD = "ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState"
SOURCE_STATIC_APPLY_METHOD = "ApplyCommandEchoJsonToState"
STATE_SINK_METHOD = "ApplyCommandEchoJson"
PENDING_METHOD = "RecordPendingCommandFromPacketJson"
STATE_SINK = "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson"

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
UPROJECT_PATH = ROOT / "UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject"
UPLUGIN_PATH = ROOT / "UE5/Bridge/QuadrotorMworksBridge.uplugin"
BUILD_CS_PATH = BRIDGE_ROOT / "QuadrotorMworksBridge.Build.cs"

RETURN_021 = (
    ROOT
    / "Results/agent_packets/returns/"
    / "RFLY-MOSIM-UE-CONSOLE-COMMAND-ECHO-RUNTIME-PREP-GATE-20260608-021.json"
)
RETURN_022 = (
    ROOT
    / "Results/agent_packets/returns/"
    / "RFLY-MOSIM-UE-CONSOLE-BUILD-ONLY-COMPILE-GATE-20260608-022.json"
)
BLOCKER_023 = (
    ROOT
    / "Results/agent_packets/blockers/"
    / "RFLY-MOSIM-UE-CONSOLE-RUNTIME-COMMAND-ECHO-PROBE-GATE-20260608-023.json"
)

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
    "015_build_gate_passed",
    "022_build_only_compile_pass",
    "UnrealBuildTool_success",
    "build_success",
    "cli_build_success",
    "pytest_success",
    "checker_success",
    "udp_send_success",
    "sender_result_bSent",
    "quadrotor.unreal_state.v1",
    "quadrotor.unreal_state.frame",
    "fixture_only_echo",
    "static_catalog_row",
    "operator_click_intent",
    "023_runtime_probe_blocker",
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


def matrix_row(
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
    is_non_live = source in NON_LIVE_SOURCES
    is_false_ack = source in FALSE_ACK_SOURCES or source.startswith("quadrotor.unreal_state")
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
    accepted_by_downlink_gate = (
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
    accepted_as_runtime_ack = accepted_by_downlink_gate and status == "accepted"
    if accepted_by_downlink_gate:
        downlink_policy = "source_static_handoff_eligible_future_runtime_row"
    else:
        downlink_policy = "reject_before_state_sink"
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
        "downlink_handoff_eligible": accepted_by_downlink_gate,
        "accepted_as_runtime_ack": accepted_as_runtime_ack,
        "downlink_policy": downlink_policy,
        "actual_runtime_transport_evidence": False,
    }


def build_downlink_fixture_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source, authority in AUTHORITATIVE_LIVE_SOURCES.items():
        rows.append(
            matrix_row(
                row_name=f"valid_future_{source}",
                source=source,
                ack_authority=authority,
            )
        )
        rows.append(
            matrix_row(
                row_name=f"valid_future_rejected_{source}",
                source=source,
                ack_authority=authority,
                status="rejected",
            )
        )

    for source in sorted(NON_LIVE_SOURCES):
        rows.append(matrix_row(row_name=f"non_live_{source}", source=source, ack_authority="MWORKS"))
    for source in sorted(FALSE_ACK_SOURCES):
        rows.append(matrix_row(row_name=f"false_ack_{source}", source=source, ack_authority="MWORKS"))

    rows.extend(
        [
            matrix_row(row_name="missing_run_id", source="MWORKS_live_downlink", ack_authority="MWORKS", has_run_id=False),
            matrix_row(row_name="missing_request_id", source="MWORKS_live_downlink", ack_authority="MWORKS", has_request_id=False),
            matrix_row(row_name="missing_seq", source="MWORKS_live_downlink", ack_authority="MWORKS", has_seq=False),
            matrix_row(row_name="missing_time_s", source="MWORKS_live_downlink", ack_authority="MWORKS", has_time_s=False),
            matrix_row(row_name="missing_command_kind", source="MWORKS_live_downlink", ack_authority="MWORKS", has_command_kind=False),
            matrix_row(row_name="wrong_authority_for_source", source="ROS2_runtime_echo", ack_authority="MWORKS"),
            matrix_row(row_name="no_pose_overwrite_failure", source="MWORKS_live_downlink", ack_authority="MWORKS", no_pose_overwrite_status="fail"),
            matrix_row(row_name="forbidden_pose_command", source="MWORKS_live_downlink", ack_authority="MWORKS", command_kind="teleport"),
            matrix_row(row_name="frame_schema_not_echo", source="quadrotor.unreal_state.v1", ack_authority="MWORKS", schema="quadrotor.unreal_state.v1"),
        ]
    )
    return rows


def build_report() -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = [
        "024 source-static/build-prep adds a handoff entry only; no live transport, port binding, or runtime probe is implemented.",
        "source_static_handoff_eligible_future_runtime_row is contract eligibility, not runtime ack evidence.",
    ]

    command_schema = read_json(COMMAND_SCHEMA_PATH)
    echo_schema = read_json(ECHO_SCHEMA_PATH)
    return_021 = read_json(RETURN_021)
    return_022 = read_json(RETURN_022)
    blocker_023 = read_json(BLOCKER_023)
    uproject = read_json(UPROJECT_PATH)
    uplugin = read_json(UPLUGIN_PATH)
    build_cs = read(BUILD_CS_PATH)

    receiver_header = read(RECEIVER_HEADER)
    receiver_source = read(RECEIVER_SOURCE)
    receiver_combined = receiver_header + "\n" + receiver_source
    state_header = read(STATE_HEADER)
    state_source = read(STATE_SOURCE)
    state_combined = state_header + "\n" + state_source
    frame_receiver_combined = read(FRAME_RECEIVER_HEADER) + "\n" + read(FRAME_RECEIVER_SOURCE)
    sender_combined = read(SENDER_HEADER) + "\n" + read(SENDER_SOURCE)

    if command_schema.get("schema") != COMMAND_SCHEMA_ID:
        issues.append("missing or invalid mosim.ue_command.v1 schema")
    if echo_schema.get("schema") != ECHO_SCHEMA_ID:
        issues.append("missing or invalid mosim.ue_command_echo.v1 schema")
    if "time_s" not in echo_schema.get("runtime_required", []):
        warnings.append("echo schema runtime_required still omits time_s; 024 downlink handoff requires it before state sink")
    if return_021.get("status") != "completed":
        issues.append("021 runtime-prep return is missing or incomplete")
    if return_022.get("status") != "completed":
        issues.append("022 build-only return is missing or incomplete")
    if blocker_023.get("status") != "blocked":
        issues.append("023 runtime probe blocker is missing")
    if blocker_023.get("blocker_summary", {}).get("blocker_code") != "blocked_no_authoritative_runtime_echo_probe_surface":
        issues.append("023 blocker code is not the expected no-authoritative-echo-surface state")

    for path, label in [
        (RECEIVER_HEADER, "receiver shell header"),
        (RECEIVER_SOURCE, "receiver shell source"),
        (STATE_HEADER, "state component header"),
        (STATE_SOURCE, "state component source"),
        (FRAME_RECEIVER_HEADER, "frame receiver header"),
        (FRAME_RECEIVER_SOURCE, "frame receiver source"),
        (SENDER_HEADER, "command sender header"),
        (SENDER_SOURCE, "command sender source"),
    ]:
        if not path.exists():
            issues.append(f"missing {label}: {repo(path)}")

    receiver_required_anchors = [
        DOWNLINK_VALIDATE_METHOD,
        DOWNLINK_APPLY_METHOD,
        SOURCE_STATIC_APPLY_METHOD,
        STATE_SINK_METHOD,
        "missing_timestamp",
        "missing_seq",
        "missing_command_kind",
        "source_authority_mismatch",
        "no_pose_overwrite_not_pass",
        "forbidden_pose_command",
        "IsAuthoritativeLiveEchoSource",
        "MWORKS_live_downlink",
        "ROS2_runtime_echo",
        "MWORKS_ROS2_live_downlink",
        ECHO_SCHEMA_ID,
    ]
    for anchor in receiver_required_anchors:
        if anchor not in receiver_combined:
            issues.append(f"receiver shell missing 024 downlink anchor: {anchor}")
    if PENDING_METHOD in receiver_source:
        issues.append("receiver downlink shell must not record pending requests")
    if COMMAND_SCHEMA_ID in receiver_combined:
        issues.append("receiver downlink shell must not parse mosim.ue_command.v1 command requests")
    if "quadrotor.unreal_state." in receiver_combined:
        issues.append("receiver downlink shell must not parse quadrotor.unreal_state frames")
    runtime_patterns = present(receiver_combined, FORBIDDEN_RUNTIME_RECEIVER_PATTERNS)
    if runtime_patterns:
        issues.append("receiver downlink shell contains runtime transport pattern(s): " + ", ".join(runtime_patterns))
    forbidden_pose_patterns = present(receiver_combined, FORBIDDEN_POSE_PATTERNS)
    if forbidden_pose_patterns:
        issues.append("receiver downlink shell contains forbidden pose/input pattern(s): " + ", ".join(forbidden_pose_patterns))

    state_required_anchors = [
        PENDING_METHOD,
        STATE_SINK_METHOD,
        "IsAuthoritativeLiveEchoSource",
        "missing_timestamp",
        "source_authority_mismatch",
        "State->bAcceptedAsRuntimeAck = !bSmokeOnly && Status == TEXT(\"accepted\")",
        "State->QualityStatus = bSmokeOnly ? TEXT(\"smoke_only\") : TEXT(\"runtime_echo_fixture\")",
        "no_pose_overwrite_not_pass",
        "seq_mismatch",
        "command_kind_mismatch",
        COMMAND_SCHEMA_ID,
        ECHO_SCHEMA_ID,
    ]
    for anchor in state_required_anchors:
        if anchor not in state_combined:
            issues.append(f"state component missing required echo reducer anchor: {anchor}")
    for label in NON_LIVE_SOURCES:
        if f'TEXT("{label}")' not in state_source:
            issues.append(f"state component does not downgrade non-live label: {label}")

    if ECHO_SCHEMA_ID in frame_receiver_combined:
        issues.append("quadrotor.unreal_state frame receiver must not parse command echo schema")
    if STATE_SINK_METHOD in frame_receiver_combined:
        issues.append("quadrotor.unreal_state frame receiver must not call command echo sink")
    if "quadrotor.unreal_state." not in frame_receiver_combined:
        issues.append("frame receiver missing quadrotor.unreal_state schema guard anchor")
    if ECHO_SCHEMA_ID in sender_combined:
        issues.append("command sender must not parse command echo schema")
    if STATE_SINK_METHOD in sender_combined:
        issues.append("command sender must not call command echo sink")
    if COMMAND_SCHEMA_ID not in sender_combined:
        issues.append("command sender missing command schema anchor")
    if "Result.bSent" not in sender_combined:
        issues.append("command sender missing sender-success negative ack anchor")

    if uproject.get("EngineAssociation") != "5.5":
        issues.append("uproject EngineAssociation is not 5.5")
    plugin_names = {str(plugin.get("Name")) for plugin in uproject.get("Plugins", [])}
    if "QuadrotorMworksBridge" not in plugin_names:
        issues.append("MoSimSceneLibrary uproject does not enable QuadrotorMworksBridge")
    module_names = {str(module.get("Name")) for module in uplugin.get("Modules", [])}
    if "QuadrotorMworksBridge" not in module_names:
        issues.append("QuadrotorMworksBridge uplugin missing module")
    for dependency in ["Core", "CoreUObject", "Engine", "Json", "JsonUtilities"]:
        if f'"{dependency}"' not in build_cs:
            issues.append(f"Build.cs missing dependency anchor: {dependency}")

    matrix = build_downlink_fixture_matrix()
    eligible_accepted = [
        row
        for row in matrix
        if row["downlink_handoff_eligible"] and row["status"] == "accepted"
    ]
    eligible_rejected = [
        row
        for row in matrix
        if row["downlink_handoff_eligible"] and row["status"] == "rejected"
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
    runtime_ack_leaks = [
        row
        for row in matrix
        if not row["row_name"].startswith("valid_future_") and row["accepted_as_runtime_ack"]
    ]
    actual_runtime_claims = [
        row for row in matrix if row["actual_runtime_transport_evidence"]
    ]
    if len(eligible_accepted) != len(AUTHORITATIVE_LIVE_SOURCES):
        issues.append("downlink matrix must contain one accepted eligible row per authoritative source")
    if len(eligible_rejected) != len(AUTHORITATIVE_LIVE_SOURCES):
        issues.append("downlink matrix must contain one rejected handoff-eligible row per authoritative source")
    if any(row["downlink_handoff_eligible"] for row in non_live_rows):
        issues.append("non-live rows can pass downlink handoff gate")
    if any(row["downlink_handoff_eligible"] for row in false_ack_rows):
        issues.append("false ack rows can pass downlink handoff gate")
    if any(row["downlink_handoff_eligible"] for row in invalid_rows):
        issues.append("invalid rows can pass downlink handoff gate")
    if runtime_ack_leaks:
        issues.append("runtime ack leaks outside accepted authoritative future rows")
    if actual_runtime_claims:
        issues.append("matrix claims actual runtime transport evidence")

    return {
        "schema": "mosim.ue_console_runtime_echo_producer_downlink_gate.v1",
        "ok": not issues,
        "task_id": TASK_ID,
        "scope_classification": "source-static/build-prep",
        "source_static_build_prep": True,
        "runtime_probe_executed": False,
        "ue_runtime_started": False,
        "unreal_editor_opened": False,
        "unreal_build_executed": False,
        "socket_or_listener_started": False,
        "runtime_socket_udp_tcp_receiver_implemented": False,
        "accepted_state_ui_controls_enabled": False,
        "not_live_runtime_evidence": True,
        "prior_gate_inputs": {
            "021_return": repo(RETURN_021),
            "022_return": repo(RETURN_022),
            "023_blocker": repo(BLOCKER_023),
            "021_status": return_021.get("status"),
            "022_status": return_022.get("status"),
            "023_status": blocker_023.get("status"),
            "023_blocker_code": blocker_023.get("blocker_summary", {}).get("blocker_code"),
        },
        "source_patch_summary": {
            "receiver_shell_header": repo(RECEIVER_HEADER),
            "receiver_shell_source": repo(RECEIVER_SOURCE),
            "added_source_static_methods": [
                DOWNLINK_VALIDATE_METHOD,
                DOWNLINK_APPLY_METHOD,
            ],
            "unchanged_source_static_method": SOURCE_STATIC_APPLY_METHOD,
            "single_state_sink": STATE_SINK,
            "guards_before_sink": [
                "schema=mosim.ue_command_echo.v1",
                "status accepted|rejected",
                "run_id and request_id present",
                "seq present",
                "time_s present",
                "command.kind or command_kind present",
                "forbidden pose command kinds rejected",
                "no_pose_overwrite_status=pass",
                "source/ack_authority is MWORKS_live_downlink/MWORKS, ROS2_runtime_echo/ROS2, or MWORKS_ROS2_live_downlink/MWORKS_ROS2",
            ],
            "does_not_record_pending_request": PENDING_METHOD not in receiver_source,
            "does_not_parse_command_request_schema": COMMAND_SCHEMA_ID not in receiver_combined,
            "does_not_parse_quadrotor_unreal_state": "quadrotor.unreal_state." not in receiver_combined,
            "runtime_transport_patterns_present": runtime_patterns,
            "forbidden_pose_patterns_present": forbidden_pose_patterns,
        },
        "source_anchor_summary": {
            "receiver_shell": {
                "header": repo(RECEIVER_HEADER),
                "source": repo(RECEIVER_SOURCE),
                "role": "source-static authoritative command echo downlink handoff only",
                "has_authoritative_validate_method": DOWNLINK_VALIDATE_METHOD in receiver_combined,
                "has_authoritative_apply_method": DOWNLINK_APPLY_METHOD in receiver_combined,
                "has_existing_source_static_apply_method": SOURCE_STATIC_APPLY_METHOD in receiver_combined,
                "calls_state_sink": STATE_SINK_METHOD in receiver_source,
                "runtime_transport_patterns_present": runtime_patterns,
                "forbidden_pose_patterns_present": forbidden_pose_patterns,
            },
            "state_component": {
                "header": repo(STATE_HEADER),
                "source": repo(STATE_SOURCE),
                "pending_source": PENDING_METHOD,
                "echo_sink": STATE_SINK_METHOD,
                "has_timestamp_guard": "missing_timestamp" in state_source,
                "has_source_authority_guard": "source_authority_mismatch" in state_source,
                "non_live_labels_downgraded": sorted(
                    label for label in NON_LIVE_SOURCES if f'TEXT("{label}")' in state_source
                ),
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
        "downlink_contract": {
            "producer_role": "future authorized MWORKS/ROS2 live command echo producer/downlink",
            "consumer_handoff": (
                "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent."
                "ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState"
            ),
            "consumer_sink": STATE_SINK,
            "pending_precondition": f"matching {COMMAND_SCHEMA_ID} request recorded by {PENDING_METHOD}",
            "authoritative_source_authority_pairs": AUTHORITATIVE_LIVE_SOURCES,
            "required_fields_before_state_sink": [
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
            "negative_sources_rejected_before_state_sink": {
                "non_live_sources": sorted(NON_LIVE_SOURCES),
                "false_ack_sources": sorted(FALSE_ACK_SOURCES),
            },
            "future_probe_acceptance_gates": [
                "record pending mosim.ue_command.v1 request identity",
                "capture actual live transport receipt of mosim.ue_command_echo.v1",
                "verify source/ack_authority pair and timestamp",
                "verify seq/request/run/command kind match pending request",
                "verify no_pose_overwrite_status=pass",
                "capture negative evidence that build/send/frame/fixture/static rows cannot satisfy ack",
                "do not claim controller/planner success from UE echo state",
            ],
        },
        "downlink_fixture_matrix": matrix,
        "matrix_summary": {
            "total_rows": len(matrix),
            "future_authoritative_accepted_rows": len(eligible_accepted),
            "future_authoritative_rejected_rows": len(eligible_rejected),
            "non_live_rows": len(non_live_rows),
            "false_ack_rows": len(false_ack_rows),
            "invalid_rows": len(invalid_rows),
            "runtime_ack_leaks": len(runtime_ack_leaks),
            "actual_runtime_claim_rows": len(actual_runtime_claims),
        },
        "build_prep_surface": {
            "build_not_run_in_024": True,
            "reason": "024 is source-static/build-prep and allowed_write_scope does not authorize generated Unreal build outputs; 022 remains prior compile evidence and a later compile gate should validate this C++ patch.",
            "future_build_command": "Scripts/UE5/build_unreal_renderer.sh",
            "uproject": repo(UPROJECT_PATH),
            "engine_association": uproject.get("EngineAssociation"),
            "plugin": repo(UPLUGIN_PATH),
            "module": "QuadrotorMworksBridge",
            "build_cs": repo(BUILD_CS_PATH),
            "prior_compile_evidence": repo(RETURN_022),
        },
        "claim_boundary": [
            "024 proves only source-static/build-prep for the UE authoritative command echo producer/downlink handoff.",
            "024 does not run a live UE runtime/editor command-echo probe.",
            "024 does not implement a socket/UDP/TCP listener, timer, background loop, or port binding.",
            "024 does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime ack, accepted UI, planner_ready, controller performance, mission success, or closed_loop.",
        ],
        "forbidden_runtime_claims": {
            "live_ue_runtime_ack": False,
            "live_mworks_downlink": False,
            "ros2_runtime_ack": False,
            "accepted_ui": False,
            "planner_ready": False,
            "closed_loop": False,
            "controller_performance": False,
            "fast_lio_success": False,
            "localization_or_local_map_quality": False,
            "mission_success": False,
            "final_ui_acceptance": False,
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
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
