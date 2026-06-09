#!/usr/bin/env python3
"""Build the UE 035 producer/capture/cleanup route contract.

This is a source-static checker. It does not open Unreal Editor, run UE
runtime/build, bind sockets, start listeners/timers/threads/background loops,
consume a live probe attempt, or claim live command acknowledgement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-PRODUCER-CAPTURE-CLEANUP-ROUTE-CONTRACT-20260609-035"

COMMAND_SCHEMA_ID = "mosim.ue_command.v1"
ECHO_SCHEMA_ID = "mosim.ue_command_echo.v1"

EXPECTED_CAPTURE_ARTIFACTS = [
    "runtime_probe_manifest.json",
    "pending_request_capture.json",
    "authoritative_echo_capture.json",
    "request_echo_match_report.json",
    "no_pose_overwrite_report.json",
    "false_ack_negative_report.json",
    "timeout_cleanup_manifest.json",
]

AUTHORITATIVE_SOURCE_AUTHORITY_PAIRS = {
    "MWORKS_live_downlink": "MWORKS",
    "ROS2_runtime_echo": "ROS2",
    "MWORKS_ROS2_live_downlink": "MWORKS_ROS2",
}

FALSE_ACK_OR_NON_LIVE_SOURCES = {
    "024_source_static_handoff",
    "025_compile_pass",
    "026_checker_success",
    "027_runtime_readiness_checker",
    "028_harness_prep_checker",
    "029_capture_bundle_validator",
    "030_source_static_receiver_surface",
    "031_compile_pass",
    "032_capture_bundle_wiring_checker",
    "033_single_bounded_probe_plan_checker",
    "034_no_side_effect_preflight_blocker",
    "MWORKS_MCP_result_adapter_smoke",
    "MWORKS_MCP_runtime_adapter_preflight",
    "UnrealBuildTool_success",
    "build_success",
    "checker_success",
    "cli_build_success",
    "compile_pass_warning_only",
    "fixture_only_echo",
    "offline_adapter_smoke",
    "operator_intent",
    "pytest_success",
    "quadrotor.unreal_state.frame",
    "quadrotor.unreal_state.v1",
    "sender_result_bSent",
    "source_level_smoke",
    "static_fixture_row",
    "udp_send_success",
}

NO_POSE_OVERWRITE_CHECKS = [
    "keyboard_pose",
    "direct_actor_transform",
    "actor_teleport",
    "pose_override",
    "set_uav_pose",
    "SetActorLocation",
    "SetActorTransform",
    "TeleportTo",
    "UE_truth_shortcut",
]

FORBIDDEN_RUNTIME_PATTERNS = {
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
    "BeginPlay",
    "EndPlay",
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
    "pose_override",
    "set_uav_pose",
    "actor_transform",
    "keyboard_pose",
}

RETURN_029 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-PROBE-CAPTURE-BUNDLE-VALIDATOR-20260608-029.json"
RETURN_030 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-SOURCE-GATE-20260608-030.json"
RETURN_031 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-COMPILE-GATE-20260608-031.json"
RETURN_032 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-CAPTURE-BUNDLE-WIRING-20260608-032.json"
RETURN_033 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-SINGLE-BOUNDED-PROBE-PLAN-20260609-033.json"
BLOCKER_034 = ROOT / "Results/agent_packets/blockers/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-SINGLE-BOUNDED-LIVE-PROBE-20260609-034.json"

EVIDENCE_032 = ROOT / "Results/unreal_experiment_console/runtime_echo_receiver_capture_bundle_wiring_20260608_032/runtime_echo_receiver_capture_bundle_wiring.json"
EVIDENCE_033 = ROOT / "Results/unreal_experiment_console/runtime_echo_receiver_single_bounded_probe_plan_20260609_033/runtime_echo_receiver_single_bounded_probe_plan.json"
PREFLIGHT_034 = ROOT / "Results/unreal_experiment_console/runtime_echo_receiver_single_bounded_live_probe_20260609_034/preflight_live_probe_034.json"

VALIDATOR_029_SCRIPT = ROOT / "Scripts/UE5/check_ue_runtime_probe_capture_bundle_validator.py"
WIRING_032_SCRIPT = ROOT / "Scripts/UE5/check_ue_runtime_echo_receiver_capture_bundle_wiring.py"
PLAN_033_SCRIPT = ROOT / "Scripts/UE5/check_ue_runtime_echo_receiver_single_bounded_probe_plan.py"

BRIDGE_ROOT = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge"
SURFACE_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.h"
SURFACE_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.cpp"
RECEIVER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.cpp"
STATE_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksExperimentConsoleStateComponent.cpp"

SURFACE_CLASS = "UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent"
SURFACE_VALIDATE_METHOD = "ValidateAuthoritativeRuntimeCommandEchoDownlinkJson"
SURFACE_INGEST_METHOD = "IngestAuthoritativeRuntimeCommandEchoDownlinkJson"
SURFACE_BOUNDARY_METHOD = "GetSourceStaticReceiverBoundary"
RECEIVER_VALIDATE_METHOD = "IsAuthoritativeRuntimeCommandEchoPacketJson"
RECEIVER_APPLY_METHOD = "ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState"
STATE_PENDING_METHOD = "RecordPendingCommandFromPacketJson"
STATE_SINK_METHOD = "ApplyCommandEchoJson"


def repo(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def present(source: str, patterns: set[str]) -> list[str]:
    return sorted(pattern for pattern in patterns if pattern in source)


def artifact_contracts() -> list[dict[str, Any]]:
    return [
        {
            "artifact": "runtime_probe_manifest.json",
            "route": "authoritative_producer_identity",
            "required_fields": [
                "probe_id",
                "run_id",
                "request_id",
                "capture_session_id",
                "transport_capture_id",
                "producer_identity.source",
                "producer_identity.ack_authority",
                "producer_identity.producer_surface",
                "producer_identity.producer_instance_id",
                "bounded_probe=true",
                "probe_attempt_count=1",
                "retry_count=0",
            ],
            "direct_receiver_input": False,
            "current_runtime_ready": False,
            "accepted_as_runtime_ack_now": False,
        },
        {
            "artifact": "pending_request_capture.json",
            "route": "pending_request_capture",
            "required_fields": [
                "schema=mosim.ue_command.v1",
                "run_id",
                "request_id",
                "seq",
                "time_s",
                "command.kind",
                "command.payload",
                "requested_by=ue_experiment_console",
            ],
            "direct_receiver_input": False,
            "current_runtime_ready": False,
            "accepted_as_runtime_ack_now": False,
        },
        {
            "artifact": "authoritative_echo_capture.json",
            "route": "authoritative_echo_capture",
            "required_fields": [
                "schema=mosim.ue_command_echo.v1",
                "source",
                "ack_authority",
                "run_id",
                "request_id",
                "seq",
                "time_s",
                "status",
                "command.kind or command_kind",
                "no_pose_overwrite_status=pass",
            ],
            "direct_receiver_input": True,
            "current_runtime_ready": False,
            "accepted_as_runtime_ack_now": False,
        },
        {
            "artifact": "request_echo_match_report.json",
            "route": "request_echo_identity_match",
            "required_fields": [
                "match_status=pass",
                "run_id_match=true",
                "request_id_match=true",
                "seq_match=true",
                "time_s_match=true",
                "command_kind_match=true",
                "status_match=true",
            ],
            "direct_receiver_input": False,
            "current_runtime_ready": False,
            "accepted_as_runtime_ack_now": False,
        },
        {
            "artifact": "no_pose_overwrite_report.json",
            "route": "no_pose_overwrite_proof",
            "required_fields": [
                "no_pose_overwrite_status=pass",
                "forbidden_pose_command_seen=false",
                "direct_actor_transform_seen=false",
                "keyboard_pose_control_seen=false",
                "pose_override_seen=false",
                "set_uav_pose_seen=false",
                "actor_teleport_seen=false",
                "ue_truth_shortcut_seen=false",
            ],
            "direct_receiver_input": False,
            "current_runtime_ready": False,
            "accepted_as_runtime_ack_now": False,
        },
        {
            "artifact": "false_ack_negative_report.json",
            "route": "false_ack_negative_proof",
            "required_fields": [
                "false_ack_negative_status=pass",
                "checked_sources",
                "false_ack_rows_accepted_as_runtime_ack=0",
                "accepted_runtime_ack_from_false_sources=false",
                "actual_runtime_ack_claimed_from_static_sources=false",
            ],
            "direct_receiver_input": False,
            "current_runtime_ready": False,
            "accepted_as_runtime_ack_now": False,
        },
        {
            "artifact": "timeout_cleanup_manifest.json",
            "route": "timeout_cleanup_proof",
            "required_fields": [
                "timeout_seconds in (0, 60]",
                "probe_attempt_count=1",
                "retry_count=0",
                "cleanup_status=pass",
                "cleanup_completed=true",
                "listener_left_running=false",
                "timer_left_running=false",
                "background_loop_left_running=false",
                "socket_left_bound=false",
                "accepted_ui_controls_enabled=false",
            ],
            "direct_receiver_input": False,
            "current_runtime_ready": False,
            "accepted_as_runtime_ack_now": False,
        },
    ]


def route_readiness_matrix() -> list[dict[str, Any]]:
    rows = []
    for contract in artifact_contracts():
        rows.append(
            {
                "route": contract["route"],
                "artifact": contract["artifact"],
                "contract_defined_now": True,
                "source_static_evidence_now": True,
                "current_runtime_ready": False,
                "blocks_live_probe_until_implemented": True,
                "accepted_as_runtime_ack_now": False,
                "reason": "035 defines the required source/static contract only; live producer/capture/cleanup execution is a later PMO-authorized task.",
            }
        )
    return rows


def false_ack_rejection_rules() -> list[dict[str, Any]]:
    return [
        {
            "source": source,
            "expected_result": "reject_as_live_runtime_ack",
            "accepted_as_runtime_ack_now": False,
            "reason": "Only matching authoritative mosim.ue_command_echo.v1 from an approved live producer can accept or reject a pending command.",
        }
        for source in sorted(FALSE_ACK_OR_NON_LIVE_SOURCES)
    ]


def no_pose_rules() -> list[dict[str, Any]]:
    return [
        {
            "check": check,
            "required_result": "absent_or_false",
            "accepted_as_runtime_ack_now": False,
        }
        for check in NO_POSE_OVERWRITE_CHECKS
    ]


def build_report() -> dict[str, Any]:
    issues: list[str] = []

    required_paths = [
        RETURN_029,
        RETURN_030,
        RETURN_031,
        RETURN_032,
        RETURN_033,
        BLOCKER_034,
        EVIDENCE_032,
        EVIDENCE_033,
        PREFLIGHT_034,
        VALIDATOR_029_SCRIPT,
        WIRING_032_SCRIPT,
        PLAN_033_SCRIPT,
        SURFACE_HEADER,
        SURFACE_SOURCE,
        RECEIVER_SOURCE,
        STATE_SOURCE,
    ]
    for path in required_paths:
        if not path.exists():
            issues.append(f"missing required path: {repo(path)}")

    return_029 = read_json(RETURN_029)
    return_030 = read_json(RETURN_030)
    return_031 = read_json(RETURN_031)
    return_032 = read_json(RETURN_032)
    return_033 = read_json(RETURN_033)
    blocker_034 = read_json(BLOCKER_034)
    evidence_032 = read_json(EVIDENCE_032)
    evidence_033 = read_json(EVIDENCE_033)
    preflight_034 = read_json(PREFLIGHT_034)
    validator_source = read_text(VALIDATOR_029_SCRIPT)
    plan_033_source = read_text(PLAN_033_SCRIPT)
    surface_combined = read_text(SURFACE_HEADER) + "\n" + read_text(SURFACE_SOURCE)
    receiver_source = read_text(RECEIVER_SOURCE)
    state_source = read_text(STATE_SOURCE)

    for label, packet in [
        ("029", return_029),
        ("030", return_030),
        ("031", return_031),
        ("032", return_032),
        ("033", return_033),
    ]:
        if packet.get("status") != "completed":
            issues.append(f"{label} return is not completed")

    if blocker_034.get("status") != "blocked":
        issues.append("034 packet is not a blocked packet")
    if preflight_034.get("preflight_ok_to_consume_live_attempt") is not False:
        issues.append("034 preflight must keep preflight_ok_to_consume_live_attempt=false")
    if preflight_034.get("live_attempt_consumed") is not False:
        issues.append("034 preflight must keep live_attempt_consumed=false")
    if preflight_034.get("runtime_probe_executed") is not False:
        issues.append("034 preflight must keep runtime_probe_executed=false")
    if blocker_034.get("preflight_result", {}).get("live_attempt_consumed") is not False:
        issues.append("034 blocker must keep live_attempt_consumed=false")
    if blocker_034.get("preflight_result", {}).get("runtime_probe_executed") is not False:
        issues.append("034 blocker must keep runtime_probe_executed=false")

    if evidence_032.get("source_static_wiring_ready") is not True:
        issues.append("032 evidence must keep source_static_wiring_ready=true")
    if evidence_032.get("runtime_probe_executed") is not False:
        issues.append("032 evidence must not execute a runtime probe")
    if evidence_032.get("live_transport_evidence_rows") != 0:
        issues.append("032 evidence must keep live_transport_evidence_rows=0")
    if evidence_032.get("runtime_ack_leaks_now") != 0:
        issues.append("032 evidence must keep runtime_ack_leaks_now=0")

    if evidence_033.get("source_static_plan_ready") is not True:
        issues.append("033 evidence must keep source_static_plan_ready=true")
    if evidence_033.get("runtime_probe_executed") is not False:
        issues.append("033 evidence must not execute a runtime probe")
    if evidence_033.get("live_transport_evidence_rows") != 0:
        issues.append("033 evidence must keep live_transport_evidence_rows=0")
    if evidence_033.get("runtime_ack_leaks_now") != 0:
        issues.append("033 evidence must keep runtime_ack_leaks_now=0")
    if evidence_033.get("single_bounded_probe_plan", {}).get("future_probe_attempt_count") != 1:
        issues.append("033 evidence must preserve future_probe_attempt_count=1")
    if evidence_033.get("single_bounded_probe_plan", {}).get("future_probe_retry_budget") != 0:
        issues.append("033 evidence must preserve future_probe_retry_budget=0")

    for artifact in EXPECTED_CAPTURE_ARTIFACTS:
        if artifact not in validator_source:
            issues.append(f"029 validator missing artifact contract: {artifact}")
        if artifact not in plan_033_source:
            issues.append(f"033 plan checker missing artifact contract: {artifact}")
    for source, authority in AUTHORITATIVE_SOURCE_AUTHORITY_PAIRS.items():
        if source not in validator_source or authority not in validator_source:
            issues.append(f"029 validator missing authoritative pair: {source}/{authority}")

    for anchor in [
        SURFACE_CLASS,
        SURFACE_VALIDATE_METHOD,
        SURFACE_INGEST_METHOD,
        SURFACE_BOUNDARY_METHOD,
        "source_static_runtime_echo_receiver_surface",
        ECHO_SCHEMA_ID,
        "PrimaryComponentTick.bCanEverTick = false",
    ]:
        if anchor not in surface_combined:
            issues.append(f"receiver surface missing anchor: {anchor}")
    if RECEIVER_VALIDATE_METHOD not in receiver_source:
        issues.append(f"receiver source missing validate anchor: {RECEIVER_VALIDATE_METHOD}")
    if RECEIVER_APPLY_METHOD not in receiver_source:
        issues.append(f"receiver source missing apply anchor: {RECEIVER_APPLY_METHOD}")
    if STATE_PENDING_METHOD not in state_source:
        issues.append(f"state source missing pending anchor: {STATE_PENDING_METHOD}")
    if STATE_SINK_METHOD not in state_source:
        issues.append(f"state source missing echo sink anchor: {STATE_SINK_METHOD}")

    runtime_patterns = present(surface_combined, FORBIDDEN_RUNTIME_PATTERNS)
    pose_patterns = present(surface_combined, FORBIDDEN_POSE_PATTERNS)
    if runtime_patterns:
        issues.append("receiver surface contains runtime transport pattern(s): " + ", ".join(runtime_patterns))
    if pose_patterns:
        issues.append("receiver surface contains forbidden pose/input pattern(s): " + ", ".join(pose_patterns))
    if COMMAND_SCHEMA_ID in surface_combined:
        issues.append("receiver surface must not synthesize or parse pending mosim.ue_command.v1")

    artifact_rows = artifact_contracts()
    route_rows = route_readiness_matrix()
    false_ack_rows = false_ack_rejection_rules()
    no_pose_rows = no_pose_rules()
    direct_inputs = [row for row in artifact_rows if row["direct_receiver_input"]]
    runtime_ack_leaks = [
        row
        for row in artifact_rows + route_rows + false_ack_rows + no_pose_rows
        if row.get("accepted_as_runtime_ack_now") is True
    ]
    if {row["artifact"] for row in artifact_rows} != set(EXPECTED_CAPTURE_ARTIFACTS):
        issues.append("artifact contracts do not cover exactly the seven expected artifacts")
    if len(direct_inputs) != 1 or direct_inputs[0]["artifact"] != "authoritative_echo_capture.json":
        issues.append("only authoritative_echo_capture.json may be a direct receiver input")
    if runtime_ack_leaks:
        issues.append("source/static route contract contains runtime ack leak rows")

    return {
        "schema": "mosim.ue_runtime_echo_producer_capture_cleanup_route_contract.v1",
        "ok": not issues,
        "task_id": TASK_ID,
        "scope_classification": "source-static producer/capture/cleanup route contract",
        "source_static_route_contract_ready": not issues,
        "runtime_route_ready_now": False,
        "live_attempt_consumed": False,
        "runtime_probe_executed": False,
        "unreal_editor_opened": False,
        "ue_runtime_started": False,
        "unreal_build_executed_in_035": False,
        "socket_listener_timer_thread_or_background_loop_started": False,
        "accepted_state_ui_controls_enabled": False,
        "authoritative_runtime_ack_claimable_now": False,
        "live_transport_evidence_rows": 0,
        "runtime_ack_leaks_now": len(runtime_ack_leaks),
        "producer_capture_cleanup_route_contract": {
            "authoritative_source_authority_pairs": AUTHORITATIVE_SOURCE_AUTHORITY_PAIRS,
            "authoritative_producer_identity": {
                "status_now": "contract_defined_missing_live_producer_instance",
                "required_fields": [
                    "producer_surface",
                    "producer_instance_id",
                    "source",
                    "ack_authority",
                    "capture_session_id",
                    "transport_capture_id",
                ],
                "allowed_sources": sorted(AUTHORITATIVE_SOURCE_AUTHORITY_PAIRS),
            },
            "pending_request_capture": {
                "status_now": "contract_defined_missing_live_capture_route",
                "schema": COMMAND_SCHEMA_ID,
                "artifact": "pending_request_capture.json",
                "must_exist_before_echo": True,
                "receiver_surface_must_not_synthesize_pending": True,
                "state_anchor": STATE_PENDING_METHOD,
            },
            "authoritative_echo_capture": {
                "status_now": "contract_defined_missing_live_capture_route",
                "schema": ECHO_SCHEMA_ID,
                "artifact": "authoritative_echo_capture.json",
                "direct_receiver_input": True,
                "receiver_surface_class": SURFACE_CLASS,
                "receiver_surface_validate_method": SURFACE_VALIDATE_METHOD,
                "receiver_surface_ingest_method": SURFACE_INGEST_METHOD,
            },
            "timeout_cleanup": {
                "status_now": "contract_defined_missing_live_cleanup_route",
                "artifact": "timeout_cleanup_manifest.json",
                "timeout_seconds_exclusive_min": 0,
                "timeout_seconds_inclusive_max": 60,
                "probe_attempt_count": 1,
                "retry_count": 0,
            },
            "seven_artifact_generation": {
                "status_now": "contract_defined_missing_live_generation_route",
                "artifacts": EXPECTED_CAPTURE_ARTIFACTS,
            },
        },
        "field_level_capture_contract": artifact_rows,
        "route_readiness_matrix": route_rows,
        "false_ack_rejection_rules": false_ack_rows,
        "no_pose_overwrite_rules": no_pose_rows,
        "source_static_receiver_boundary": {
            "header": repo(SURFACE_HEADER),
            "source": repo(SURFACE_SOURCE),
            "validate_method_present": SURFACE_VALIDATE_METHOD in surface_combined,
            "ingest_method_present": SURFACE_INGEST_METHOD in surface_combined,
            "boundary_method_present": SURFACE_BOUNDARY_METHOD in surface_combined,
            "runtime_transport_patterns_present": runtime_patterns,
            "forbidden_pose_patterns_present": pose_patterns,
            "parses_pending_command_request_schema": COMMAND_SCHEMA_ID in surface_combined,
        },
        "prior_evidence_consumed": {
            "ue_029_status": return_029.get("status"),
            "ue_030_status": return_030.get("status"),
            "ue_031_status": return_031.get("status"),
            "ue_032_status": return_032.get("status"),
            "ue_033_status": return_033.get("status"),
            "ue_034_status": blocker_034.get("status"),
            "ue_032_source_static_wiring_ready": evidence_032.get("source_static_wiring_ready"),
            "ue_033_source_static_plan_ready": evidence_033.get("source_static_plan_ready"),
            "ue_034_live_attempt_consumed": preflight_034.get("live_attempt_consumed"),
            "ue_034_runtime_probe_executed": preflight_034.get("runtime_probe_executed"),
        },
        "future_live_probe_preconditions": [
            "PMO explicitly authorizes a single bounded UE runtime/editor probe after this contract is implemented as live routes.",
            "A producer route supplies source/ack_authority plus producer_surface/producer_instance_id/capture_session_id/transport_capture_id.",
            "A pending mosim.ue_command.v1 request is captured before any echo is ingested.",
            "A runtime mosim.ue_command_echo.v1 row from an allowed source/authority pair is captured and fed through the receiver surface.",
            "Request/echo identity match passes for run_id/request_id/seq/time_s/command kind/status.",
            "No-pose-overwrite proof passes and no forbidden pose shortcut is observed.",
            "False-ack negative report rejects static/build/checker/sender/operator/fixture/frame rows.",
            "Timeout cleanup manifest proves one attempt, timeout <= 60 seconds, retry_count=0, and no leftover socket/listener/timer/thread/background loop/accepted UI.",
        ],
        "matrix_summary": {
            "field_level_capture_contract_rows": len(artifact_rows),
            "route_readiness_rows": len(route_rows),
            "false_ack_rejection_rows": len(false_ack_rows),
            "no_pose_overwrite_rows": len(no_pose_rows),
            "direct_receiver_input_rows": len(direct_inputs),
            "current_runtime_ready_rows": sum(1 for row in route_rows if row["current_runtime_ready"]),
            "runtime_ack_leaks_now": len(runtime_ack_leaks),
            "live_transport_evidence_rows": 0,
            "authoritative_runtime_ack_claimable_now": False,
        },
        "claim_boundary": [
            "035 proves only a source/static producer/capture/cleanup route contract for a future bounded UE runtime command-echo probe.",
            "035 does not open Unreal Editor, PIE, standalone runtime, game window, or UE runtime.",
            "035 does not run Unreal build, bind sockets, start listeners/timers/threads/background loops, or execute live transport.",
            "035 does not edit UE C++ source, Blueprint, UMG, Slate/Web UI, assets, materials, maps, project settings, Sunray/PBR/Blender, MWORKS, ROS2, FAST-LIO, planner, controller, MoSimQuadrotorModel, References, CoAgent runtime, or Git.",
            "035 checker/test/static rows, 034 preflight blocker, 033 readiness, 032 wiring, 031 compile success, 030 source surface, 029 validator success, sender success, fixture rows, operator intent, and quadrotor.unreal_state frames are not live runtime ack.",
            "034 remains the latest bounded live preflight and records live_attempt_consumed=false and runtime_probe_executed=false.",
            "035 does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime echo, final UI acceptance, planner_ready, FAST-LIO success, controller performance, mission success, or closed_loop.",
        ],
        "issues": issues,
    }


def write_summary(report: dict[str, Any], output_md: Path) -> None:
    lines = [
        "# UE 035 Producer/Capture/Cleanup Route Contract",
        "",
        f"- ok: {report['ok']}",
        f"- scope: {report['scope_classification']}",
        f"- source_static_route_contract_ready: {report['source_static_route_contract_ready']}",
        f"- runtime_route_ready_now: {report['runtime_route_ready_now']}",
        f"- live_attempt_consumed: {report['live_attempt_consumed']}",
        f"- runtime_probe_executed: {report['runtime_probe_executed']}",
        "",
        "## Route Readiness Matrix",
        "",
    ]
    for row in report["route_readiness_matrix"]:
        lines.append(
            f"- {row['route']} -> {row['artifact']}: "
            f"contract_defined_now={row['contract_defined_now']}, "
            f"current_runtime_ready={row['current_runtime_ready']}"
        )
    lines.extend(["", "## Future Preconditions", ""])
    for item in report["future_live_probe_preconditions"]:
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
    parser.add_argument("--output-matrix", default="")
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
    if args.output_matrix:
        output_matrix = Path(args.output_matrix)
        if not output_matrix.is_absolute():
            output_matrix = ROOT / output_matrix
        output_matrix.parent.mkdir(parents=True, exist_ok=True)
        matrix = {
            "field_level_capture_contract": report["field_level_capture_contract"],
            "route_readiness_matrix": report["route_readiness_matrix"],
            "false_ack_rejection_rules": report["false_ack_rejection_rules"],
            "no_pose_overwrite_rules": report["no_pose_overwrite_rules"],
            "matrix_summary": report["matrix_summary"],
        }
        output_matrix.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(text)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
