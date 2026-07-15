#!/usr/bin/env python3
"""Check the UE 030 source-static runtime command-echo receiver surface.

This checker validates source anchors only. It does not open Unreal Editor,
run UE runtime/build, bind sockets, start listeners/timers/background loops, or
claim live command acknowledgement.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-SOURCE-GATE-20260608-030"
COMMAND_SCHEMA_ID = "mosim.ue_command.v1"
ECHO_SCHEMA_ID = "mosim.ue_command_echo.v1"
UNREAL_STATE_SCHEMA_PREFIX = "quadrotor.unreal_state."

BRIDGE_ROOT = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge"
SURFACE_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.h"
SURFACE_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.cpp"
RECEIVER_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.h"
RECEIVER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.cpp"
STATE_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksExperimentConsoleStateComponent.h"
STATE_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksExperimentConsoleStateComponent.cpp"
FRAME_RECEIVER_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksUdpReceiverComponent.h"
FRAME_RECEIVER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksUdpReceiverComponent.cpp"
SENDER_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksUdpCommandSenderComponent.h"
SENDER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksUdpCommandSenderComponent.cpp"
BUILD_CS = BRIDGE_ROOT / "QuadrotorMworksBridge.Build.cs"

RETURN_024 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-PRODUCER-DOWNLINK-GATE-20260608-024.json"
RETURN_025 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-DOWNLINK-COMPILE-GATE-20260608-025.json"
RETURN_026 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-BOUNDARY-CHECKER-REFRESH-20260608-026.json"
RETURN_027 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-AUTHORITATIVE-ECHO-RUNTIME-READINESS-GATE-20260608-027.json"
RETURN_028 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-PROBE-HARNESS-PREP-20260608-028.json"
RETURN_029 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-PROBE-CAPTURE-BUNDLE-VALIDATOR-20260608-029.json"

SURFACE_CLASS = "UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent"
SURFACE_VALIDATE_METHOD = "ValidateAuthoritativeRuntimeCommandEchoDownlinkJson"
SURFACE_INGEST_METHOD = "IngestAuthoritativeRuntimeCommandEchoDownlinkJson"
SURFACE_BOUNDARY_METHOD = "GetSourceStaticReceiverBoundary"
RECEIVER_VALIDATE_METHOD = "IsAuthoritativeRuntimeCommandEchoPacketJson"
RECEIVER_APPLY_METHOD = "ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState"
STATE_PENDING_METHOD = "RecordPendingCommandFromPacketJson"
STATE_SINK_METHOD = "ApplyCommandEchoJson"

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
    "029_capture_bundle_validator",
    "030_source_static_receiver_surface",
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
FORBIDDEN_COMMAND_KINDS = {
    "pose_override",
    "teleport",
    "set_uav_pose",
    "actor_transform",
    "keyboard_pose",
}
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


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def repo(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def present(source: str, patterns: set[str]) -> list[str]:
    return sorted(pattern for pattern in patterns if pattern in source)


def present_cpp_code(source: str, patterns: set[str]) -> list[str]:
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r'"(?:\\.|[^"\\])*"', '""', code)
    return present(code, patterns)


def source_literal(label: str) -> str:
    return f'TEXT("{label}")'


def receiver_row(
    row_id: str,
    source: str,
    ack_authority: str,
    *,
    schema: str = ECHO_SCHEMA_ID,
    status: str = "accepted",
    has_pending_request: bool = True,
    identity_match: bool = True,
    command_kind: str = "controller_select",
    no_pose_overwrite_status: str = "pass",
    live_transport_evidence: bool = False,
) -> dict[str, Any]:
    source_authority_match = AUTHORITATIVE_LIVE_SOURCES.get(source) == ack_authority
    schema_ok = schema == ECHO_SCHEMA_ID
    status_ok = status in {"accepted", "rejected"}
    no_pose_ok = no_pose_overwrite_status == "pass"
    command_ok = command_kind not in FORBIDDEN_COMMAND_KINDS
    false_ack = source in FALSE_ACK_SOURCES or source in NON_LIVE_SOURCES or source.startswith("quadrotor.unreal_state")
    source_surface_eligible = (
        schema_ok
        and status_ok
        and source_authority_match
        and has_pending_request
        and identity_match
        and command_ok
        and no_pose_ok
        and not false_ack
    )
    return {
        "row_id": row_id,
        "schema": schema,
        "source": source,
        "ack_authority": ack_authority,
        "status": status,
        "has_pending_request": has_pending_request,
        "identity_match": identity_match,
        "command_kind": command_kind,
        "no_pose_overwrite_status": no_pose_overwrite_status,
        "source_authority_match": source_authority_match,
        "source_surface_eligible_for_future_runtime_probe": source_surface_eligible,
        "live_transport_evidence": live_transport_evidence,
        "accepted_as_runtime_ack_now": False,
        "policy": "future_runtime_handoff_candidate" if source_surface_eligible else "reject_before_state_sink",
    }


def build_fixture_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source, authority in AUTHORITATIVE_LIVE_SOURCES.items():
        rows.append(receiver_row(f"future_authoritative_accepted_{source}", source, authority))
        rows.append(receiver_row(f"future_authoritative_rejected_{source}", source, authority, status="rejected"))
    for source in sorted(NON_LIVE_SOURCES):
        rows.append(receiver_row(f"non_live_{source}", source, "MWORKS"))
    for source in sorted(FALSE_ACK_SOURCES):
        rows.append(receiver_row(f"false_ack_{source}", source, "MWORKS"))
    rows.extend(
        [
            receiver_row("missing_pending_request", "MWORKS_live_downlink", "MWORKS", has_pending_request=False),
            receiver_row("identity_mismatch", "MWORKS_live_downlink", "MWORKS", identity_match=False),
            receiver_row("wrong_schema_command_request", "MWORKS_live_downlink", "MWORKS", schema=COMMAND_SCHEMA_ID),
            receiver_row("wrong_schema_unreal_state_frame", "quadrotor.unreal_state.v1", "MWORKS", schema="quadrotor.unreal_state.v1"),
            receiver_row("wrong_authority_pair", "ROS2_runtime_echo", "MWORKS"),
            receiver_row("forbidden_pose_command", "MWORKS_live_downlink", "MWORKS", command_kind="teleport"),
            receiver_row("no_pose_overwrite_failure", "MWORKS_live_downlink", "MWORKS", no_pose_overwrite_status="fail"),
        ]
    )
    return rows


def prior_gate_status() -> dict[str, Any]:
    returns = {
        "ue_024": read_json(RETURN_024),
        "ue_025": read_json(RETURN_025),
        "ue_026": read_json(RETURN_026),
        "ue_027": read_json(RETURN_027),
        "ue_028": read_json(RETURN_028),
        "ue_029": read_json(RETURN_029),
    }
    return {
        "ue_024_completed": returns["ue_024"].get("status") == "completed",
        "ue_024_quality_status": returns["ue_024"].get("quality_status"),
        "ue_025_completed": returns["ue_025"].get("status") == "completed",
        "ue_025_quality_status": returns["ue_025"].get("quality_status"),
        "ue_025_compile_exit_code": returns["ue_025"].get("build_only_compile_summary", {}).get("exit_code"),
        "ue_026_completed": returns["ue_026"].get("status") == "completed",
        "ue_026_runtime_ack_leaks_now": returns["ue_026"].get("matrix_summary", {}).get("runtime_ack_leaks_now"),
        "ue_027_completed": returns["ue_027"].get("status") == "completed",
        "ue_027_runtime_ready_now": returns["ue_027"].get("runtime_readiness_summary", {}).get("runtime_ready_now"),
        "ue_028_completed": returns["ue_028"].get("status") == "completed",
        "ue_028_runtime_probe_executed": returns["ue_028"].get("runtime_probe_harness_summary", {}).get("runtime_probe_executed"),
        "ue_029_completed": returns["ue_029"].get("status") == "completed",
        "ue_029_source_static_validator_ready": returns["ue_029"].get("capture_bundle_validator_summary", {}).get("source_static_validator_ready"),
    }


def build_report() -> dict[str, Any]:
    issues: list[str] = []
    warnings = [
        "030 is a source-static receiver surface gate only.",
        "The new receiver surface does not start live transport or prove runtime ack.",
    ]

    surface_header = read(SURFACE_HEADER)
    surface_source = read(SURFACE_SOURCE)
    surface_combined = surface_header + "\n" + surface_source
    receiver_header = read(RECEIVER_HEADER)
    receiver_source = read(RECEIVER_SOURCE)
    receiver_combined = receiver_header + "\n" + receiver_source
    state_combined = read(STATE_HEADER) + "\n" + read(STATE_SOURCE)
    state_source = read(STATE_SOURCE)
    frame_combined = read(FRAME_RECEIVER_HEADER) + "\n" + read(FRAME_RECEIVER_SOURCE)
    sender_combined = read(SENDER_HEADER) + "\n" + read(SENDER_SOURCE)
    build_cs = read(BUILD_CS)
    prior = prior_gate_status()

    for path, label in [
        (SURFACE_HEADER, "runtime echo receiver surface header"),
        (SURFACE_SOURCE, "runtime echo receiver surface source"),
        (RECEIVER_HEADER, "command echo receiver header"),
        (RECEIVER_SOURCE, "command echo receiver source"),
        (STATE_HEADER, "state component header"),
        (STATE_SOURCE, "state component source"),
        (FRAME_RECEIVER_HEADER, "quadrotor.unreal_state receiver header"),
        (FRAME_RECEIVER_SOURCE, "quadrotor.unreal_state receiver source"),
        (SENDER_HEADER, "command sender header"),
        (SENDER_SOURCE, "command sender source"),
        (BUILD_CS, "Build.cs"),
        (RETURN_024, "UE 024 return"),
        (RETURN_025, "UE 025 return"),
        (RETURN_026, "UE 026 return"),
        (RETURN_027, "UE 027 return"),
        (RETURN_028, "UE 028 return"),
        (RETURN_029, "UE 029 return"),
    ]:
        if not path.exists():
            issues.append(f"missing {label}: {repo(path)}")

    required_surface_anchors = [
        SURFACE_CLASS,
        SURFACE_VALIDATE_METHOD,
        SURFACE_INGEST_METHOD,
        SURFACE_BOUNDARY_METHOD,
        "source_static_runtime_echo_receiver_surface",
        "mosim.ue_command_echo.v1",
        "PrimaryComponentTick.bCanEverTick = false",
        "missing_command_echo_receiver",
        "missing_state_component",
        RECEIVER_VALIDATE_METHOD,
        RECEIVER_APPLY_METHOD,
        "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent",
        "UQuadrotorMworksExperimentConsoleStateComponent",
        "FQuadrotorMworksExperimentConsoleCommandState",
    ]
    for anchor in required_surface_anchors:
        if anchor not in surface_combined:
            issues.append(f"receiver surface missing anchor: {anchor}")

    surface_runtime_patterns = present(surface_combined, FORBIDDEN_RUNTIME_PATTERNS)
    if surface_runtime_patterns:
        issues.append("receiver surface contains live runtime pattern(s): " + ", ".join(surface_runtime_patterns))
    surface_pose_patterns = present_cpp_code(surface_combined, FORBIDDEN_POSE_PATTERNS)
    if surface_pose_patterns:
        issues.append("receiver surface contains forbidden pose/input pattern(s): " + ", ".join(surface_pose_patterns))
    if COMMAND_SCHEMA_ID in surface_combined:
        issues.append("receiver surface must not parse mosim.ue_command.v1 requests")
    if UNREAL_STATE_SCHEMA_PREFIX in surface_combined:
        issues.append("receiver surface must not parse quadrotor.unreal_state frames")

    for anchor in [RECEIVER_VALIDATE_METHOD, RECEIVER_APPLY_METHOD, ECHO_SCHEMA_ID, "IsAuthoritativeLiveEchoSource"]:
        if anchor not in receiver_combined:
            issues.append(f"command echo receiver missing authoritative anchor: {anchor}")
    if STATE_PENDING_METHOD not in state_combined:
        issues.append("state component missing pending command reducer")
    if STATE_SINK_METHOD not in state_combined:
        issues.append("state component missing command echo sink")
    for label in NON_LIVE_SOURCES:
        if source_literal(label) not in state_source:
            issues.append(f"state component missing non-live smoke label: {label}")

    if ECHO_SCHEMA_ID in frame_combined:
        issues.append("quadrotor.unreal_state receiver must not parse command echo schema")
    if STATE_SINK_METHOD in frame_combined:
        issues.append("quadrotor.unreal_state receiver must not call command echo state sink")
    if ECHO_SCHEMA_ID in sender_combined:
        issues.append("command sender must not parse command echo schema")
    if STATE_SINK_METHOD in sender_combined:
        issues.append("command sender must not call command echo state sink")
    if COMMAND_SCHEMA_ID not in sender_combined:
        issues.append("command sender missing mosim.ue_command.v1 schema anchor")

    for dependency in ["Core", "CoreUObject", "Engine", "Json", "JsonUtilities"]:
        if f'"{dependency}"' not in build_cs:
            issues.append(f"Build.cs missing dependency: {dependency}")

    expected_prior = {
        "ue_024_completed": True,
        "ue_025_completed": True,
        "ue_025_compile_exit_code": 0,
        "ue_026_completed": True,
        "ue_026_runtime_ack_leaks_now": 0,
        "ue_027_completed": True,
        "ue_027_runtime_ready_now": False,
        "ue_028_completed": True,
        "ue_028_runtime_probe_executed": False,
        "ue_029_completed": True,
        "ue_029_source_static_validator_ready": True,
    }
    for key, expected in expected_prior.items():
        if prior.get(key) != expected:
            issues.append(f"prior gate state mismatch: {key}={prior.get(key)!r}, expected {expected!r}")

    matrix = build_fixture_matrix()
    eligible = [row for row in matrix if row["source_surface_eligible_for_future_runtime_probe"]]
    false_ack_rows = [row for row in matrix if row["source"] in FALSE_ACK_SOURCES or row["source"] in NON_LIVE_SOURCES]
    runtime_ack_leaks = [row for row in matrix if row["accepted_as_runtime_ack_now"]]
    live_transport_rows = [row for row in matrix if row["live_transport_evidence"]]
    if len(eligible) != len(AUTHORITATIVE_LIVE_SOURCES) * 2:
        issues.append("fixture matrix must have accepted/rejected future candidates for each authoritative source")
    if any(row["source_surface_eligible_for_future_runtime_probe"] for row in false_ack_rows):
        issues.append("false-ack or non-live row is source-surface eligible")
    if runtime_ack_leaks:
        issues.append("fixture matrix leaks runtime ack")
    if live_transport_rows:
        issues.append("fixture matrix claims live transport evidence")

    ok = not issues
    return {
        "schema": "mosim.ue_runtime_echo_receiver_source_gate.v1",
        "ok": ok,
        "task_id": TASK_ID,
        "scope_classification": "source-static receiver surface gate",
        "source_static_receiver_surface_present": SURFACE_CLASS in surface_combined,
        "runtime_receiver_surface_class": SURFACE_CLASS,
        "runtime_receiver_surface_header": repo(SURFACE_HEADER),
        "runtime_receiver_surface_source": repo(SURFACE_SOURCE),
        "runtime_probe_executed": False,
        "unreal_editor_opened": False,
        "ue_runtime_started": False,
        "unreal_build_executed_in_030": False,
        "socket_listener_timer_or_background_loop_started": False,
        "accepted_state_ui_controls_enabled": False,
        "authoritative_runtime_ack_claimable_now": False,
        "prior_gate_status": prior,
        "source_anchor_summary": {
            "receiver_surface": {
                "header": repo(SURFACE_HEADER),
                "source": repo(SURFACE_SOURCE),
                "class": SURFACE_CLASS,
                "validate_method": SURFACE_VALIDATE_METHOD,
                "ingest_method": SURFACE_INGEST_METHOD,
                "boundary_method": SURFACE_BOUNDARY_METHOD,
                "calls_authoritative_validate": RECEIVER_VALIDATE_METHOD in surface_source,
                "calls_authoritative_apply": RECEIVER_APPLY_METHOD in surface_source,
                "tick_disabled": "PrimaryComponentTick.bCanEverTick = false" in surface_source,
                "runtime_transport_patterns_present": surface_runtime_patterns,
                "forbidden_pose_patterns_present": surface_pose_patterns,
                "parses_command_request_schema": COMMAND_SCHEMA_ID in surface_combined,
                "parses_quadrotor_unreal_state": UNREAL_STATE_SCHEMA_PREFIX in surface_combined,
            },
            "command_echo_receiver": {
                "header": repo(RECEIVER_HEADER),
                "source": repo(RECEIVER_SOURCE),
                "authoritative_validate_method": RECEIVER_VALIDATE_METHOD,
                "authoritative_apply_method": RECEIVER_APPLY_METHOD,
                "echo_schema": ECHO_SCHEMA_ID,
                "role": "validates authoritative mosim.ue_command_echo.v1 and applies through state sink",
            },
            "state_component": {
                "pending_source": STATE_PENDING_METHOD,
                "echo_sink": STATE_SINK_METHOD,
                "non_live_labels_downgraded": sorted(label for label in NON_LIVE_SOURCES if source_literal(label) in state_source),
                "non_live_accepted_as_runtime_ack": False,
            },
            "frame_status_receiver_role": "quadrotor.unreal_state frame/status receiver only; not command echo receiver",
            "command_sender_role": "mosim.ue_command.v1 sender only; sender Result.bSent or UDP send success is not ack",
        },
        "receiver_surface_contract": {
            "input_schema": ECHO_SCHEMA_ID,
            "future_authoritative_source_authority_pairs": AUTHORITATIVE_LIVE_SOURCES,
            "validation_chain": [
                f"{SURFACE_CLASS}.{SURFACE_VALIDATE_METHOD}",
                "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.IsAuthoritativeRuntimeCommandEchoPacketJson",
            ],
            "handoff_chain": [
                f"{SURFACE_CLASS}.{SURFACE_INGEST_METHOD}",
                "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState",
                "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson",
            ],
            "pending_precondition": f"matching {COMMAND_SCHEMA_ID} request recorded by {STATE_PENDING_METHOD}",
            "rejected_as_ack_sources": sorted(FALSE_ACK_SOURCES | NON_LIVE_SOURCES),
            "does_not_start_transport": True,
            "does_not_bind_socket": True,
            "does_not_start_listener_timer_thread_or_background_loop": True,
            "does_not_parse_quadrotor_unreal_state": True,
            "does_not_create_pose_control": True,
        },
        "fixture_matrix": matrix,
        "matrix_summary": {
            "total_rows": len(matrix),
            "future_authoritative_handoff_candidate_rows": len(eligible),
            "false_ack_or_non_live_rows": len(false_ack_rows),
            "runtime_ack_leaks_now": len(runtime_ack_leaks),
            "live_transport_evidence_rows": len(live_transport_rows),
            "authoritative_runtime_ack_claimable_now": False,
        },
        "next_safe_runtime_gate": {
            "recommendation": "Schedule a separately authorized single bounded UE runtime/editor probe only after live producer and transport capture surfaces are available; validate its seven-artifact capture bundle with the 029 validator.",
            "minimum_acceptance_gates": [
                "explicit runtime/editor probe authorization",
                "live authoritative producer identity for MWORKS_live_downlink, ROS2_runtime_echo, or MWORKS_ROS2_live_downlink",
                "pending mosim.ue_command.v1 request capture",
                "authoritative mosim.ue_command_echo.v1 runtime capture",
                "request/echo identity match report",
                "no_pose_overwrite_status=pass proof",
                "false-ack negative report rejecting build/checker/sender/fixture/operator/frame/static rows",
                "timeout and cleanup manifest after one bounded attempt",
            ],
        },
        "claim_boundary": [
            "030 proves only a UE source-static receiver surface and checker/test evidence.",
            "030 does not open Unreal Editor, PIE, standalone runtime, or UE runtime.",
            "030 does not run Unreal build, bind sockets, start listeners/timers/background loops, or execute live transport.",
            "030 does not touch Blueprint, UMG, assets, materials, maps, project settings, Sunray/PBR/Blender, MWORKS, ROS2, FAST-LIO, planner, controller, MoSimQuadrotorModel, References, or Git.",
            "030 checker/test/static rows, 025 compile pass, 029 validator success, sender success, fixture rows, operator intent, and quadrotor.unreal_state frames are not live runtime ack.",
            "030 does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime echo, final UI acceptance, planner_ready, FAST-LIO success, controller performance, mission success, or closed_loop.",
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
        "# UE 030 Runtime Echo Receiver Source Gate",
        "",
        f"- ok: {report['ok']}",
        f"- scope: {report['scope_classification']}",
        f"- source_static_receiver_surface_present: {report['source_static_receiver_surface_present']}",
        f"- runtime_probe_executed: {report['runtime_probe_executed']}",
        f"- authoritative_runtime_ack_claimable_now: {report['authoritative_runtime_ack_claimable_now']}",
        "",
        "## Receiver Surface",
        "",
        f"- class: {report['runtime_receiver_surface_class']}",
        f"- header: {report['runtime_receiver_surface_header']}",
        f"- source: {report['runtime_receiver_surface_source']}",
        "",
        "## Fixture Matrix Summary",
        "",
    ]
    for key, value in report["matrix_summary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Claim Boundary", ""])
    for item in report["claim_boundary"]:
        lines.append(f"- {item}")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default="")
    parser.add_argument("--output-md", default="")
    parser.add_argument("--output-fixture-matrix", default="")
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
    if args.output_fixture_matrix:
        output_matrix = Path(args.output_fixture_matrix)
        if not output_matrix.is_absolute():
            output_matrix = ROOT / output_matrix
        output_matrix.parent.mkdir(parents=True, exist_ok=True)
        output_matrix.write_text(json.dumps(report["fixture_matrix"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(text)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
