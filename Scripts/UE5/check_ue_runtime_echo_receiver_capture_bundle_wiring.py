#!/usr/bin/env python3
"""Check UE 032 runtime echo receiver to capture-bundle wiring.

This is a source-static checker. It connects the compiled UE 030 receiver
surface to the UE 029 future runtime-probe capture-bundle validator contract.
It does not open Unreal Editor, run UE runtime/build, bind sockets, start
listeners/timers/background loops, or claim live command acknowledgement.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-CAPTURE-BUNDLE-WIRING-20260608-032"

COMMAND_SCHEMA_ID = "mosim.ue_command.v1"
ECHO_SCHEMA_ID = "mosim.ue_command_echo.v1"
UNREAL_STATE_SCHEMA_PREFIX = "quadrotor.unreal_state."

EXPECTED_CAPTURE_ARTIFACTS = [
    "runtime_probe_manifest.json",
    "pending_request_capture.json",
    "authoritative_echo_capture.json",
    "request_echo_match_report.json",
    "no_pose_overwrite_report.json",
    "false_ack_negative_report.json",
    "timeout_cleanup_manifest.json",
]

AUTHORITATIVE_LIVE_SOURCES = {
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

VALIDATOR_SCRIPT = ROOT / "Scripts/UE5/check_ue_runtime_probe_capture_bundle_validator.py"
RETURN_029 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-PROBE-CAPTURE-BUNDLE-VALIDATOR-20260608-029.json"
RETURN_030 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-SOURCE-GATE-20260608-030.json"
RETURN_031 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-COMPILE-GATE-20260608-031.json"
COMPILE_SUMMARY_031 = ROOT / "Results/unreal_experiment_console/runtime_echo_receiver_compile_gate_20260608_031/runtime_echo_receiver_compile_summary.json"

SURFACE_CLASS = "UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent"
SURFACE_VALIDATE_METHOD = "ValidateAuthoritativeRuntimeCommandEchoDownlinkJson"
SURFACE_INGEST_METHOD = "IngestAuthoritativeRuntimeCommandEchoDownlinkJson"
SURFACE_BOUNDARY_METHOD = "GetSourceStaticReceiverBoundary"
RECEIVER_VALIDATE_METHOD = "IsAuthoritativeRuntimeCommandEchoPacketJson"
RECEIVER_APPLY_METHOD = "ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState"
STATE_PENDING_METHOD = "RecordPendingCommandFromPacketJson"
STATE_SINK_METHOD = "ApplyCommandEchoJson"

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


def present_cpp_code(source: str, patterns: set[str]) -> list[str]:
    code = re.sub(r"/\*.*?\*/", "", source, flags=re.DOTALL)
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r'"(?:\\.|[^"\\])*"', '""', code)
    return present(code, patterns)


def source_literal(label: str) -> str:
    return f'TEXT("{label}")'


def build_wiring_row(
    artifact: str,
    required_for_future_bundle: bool,
    receiver_surface_role: str,
    validator_role: str,
    state_or_boundary: str,
    *,
    direct_receiver_input: bool = False,
    runtime_ack_now: bool = False,
    future_live_probe_required: bool = True,
) -> dict[str, Any]:
    return {
        "artifact": artifact,
        "required_for_future_bundle": required_for_future_bundle,
        "receiver_surface_role": receiver_surface_role,
        "validator_role": validator_role,
        "state_or_boundary": state_or_boundary,
        "direct_receiver_input": direct_receiver_input,
        "future_live_probe_required": future_live_probe_required,
        "live_transport_evidence_now": False,
        "accepted_as_runtime_ack_now": runtime_ack_now,
    }


def build_wiring_matrix() -> list[dict[str, Any]]:
    return [
        build_wiring_row(
            "runtime_probe_manifest.json",
            True,
            "future probe identity and source/authority metadata; not ingested by the receiver component",
            "requires bounded probe metadata and authoritative producer identity",
            "source-static receiver boundary must remain no-transport/no-ack",
        ),
        build_wiring_row(
            "pending_request_capture.json",
            True,
            "precondition only; receiver surface must not synthesize or parse pending mosim.ue_command.v1 requests",
            "requires captured pending mosim.ue_command.v1 request before echo",
            "pending reducer remains UQuadrotorMworksExperimentConsoleStateComponent.RecordPendingCommandFromPacketJson",
        ),
        build_wiring_row(
            "authoritative_echo_capture.json",
            True,
            "future authoritative mosim.ue_command_echo.v1 payload enters through Validate/Ingest receiver methods",
            "requires source/ack_authority/run_id/request_id/seq/time_s/status/command/no_pose fields",
            "sink chain reaches UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson",
            direct_receiver_input=True,
        ),
        build_wiring_row(
            "request_echo_match_report.json",
            True,
            "receiver sink path is not enough by itself; future bundle must prove pending/echo identity match",
            "requires run_id/request_id/seq/time_s/command_kind/status match report",
            "accepted/rejected state remains gated by matching pending request",
        ),
        build_wiring_row(
            "no_pose_overwrite_report.json",
            True,
            "receiver surface must contain no pose shortcuts and future echo must include no_pose_overwrite_status=pass",
            "requires no forbidden pose command or direct actor transform evidence",
            "static source scan plus future live capture proof",
        ),
        build_wiring_row(
            "false_ack_negative_report.json",
            True,
            "receiver wiring must reject build/checker/sender/fixture/operator/frame/static rows as live ack",
            "requires false-ack negative report covering non-live/static sources",
            "state rows from source/static/preflight quality remain smoke-only until live authoritative echo",
        ),
        build_wiring_row(
            "timeout_cleanup_manifest.json",
            True,
            "source-static receiver has no listener/timer/socket cleanup burden; future probe still must prove cleanup",
            "requires one bounded attempt, timeout, cleanup pass, and no leftover listener/timer/background loop/socket",
            "future runtime probe cleanup gate",
        ),
    ]


def build_false_ack_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in sorted(FALSE_ACK_OR_NON_LIVE_SOURCES):
        rows.append(
            {
                "source": source,
                "accepted_as_runtime_ack_now": False,
                "eligible_for_future_authoritative_echo": False,
                "reason": "static/build/checker/sender/operator/frame/preflight rows cannot satisfy authoritative live command echo",
            }
        )
    return rows


def build_report() -> dict[str, Any]:
    issues: list[str] = []

    required_paths = [
        SURFACE_HEADER,
        SURFACE_SOURCE,
        RECEIVER_HEADER,
        RECEIVER_SOURCE,
        STATE_HEADER,
        STATE_SOURCE,
        FRAME_RECEIVER_HEADER,
        FRAME_RECEIVER_SOURCE,
        SENDER_HEADER,
        SENDER_SOURCE,
        VALIDATOR_SCRIPT,
        RETURN_029,
        RETURN_030,
        RETURN_031,
        COMPILE_SUMMARY_031,
    ]
    for path in required_paths:
        if not path.exists():
            issues.append(f"missing required path: {repo(path)}")

    surface_header = read_text(SURFACE_HEADER)
    surface_source = read_text(SURFACE_SOURCE)
    surface_combined = surface_header + "\n" + surface_source
    receiver_combined = read_text(RECEIVER_HEADER) + "\n" + read_text(RECEIVER_SOURCE)
    state_source = read_text(STATE_SOURCE)
    state_combined = read_text(STATE_HEADER) + "\n" + state_source
    frame_combined = read_text(FRAME_RECEIVER_HEADER) + "\n" + read_text(FRAME_RECEIVER_SOURCE)
    sender_combined = read_text(SENDER_HEADER) + "\n" + read_text(SENDER_SOURCE)
    validator_source = read_text(VALIDATOR_SCRIPT)
    return_029 = read_json(RETURN_029)
    return_030 = read_json(RETURN_030)
    return_031 = read_json(RETURN_031)
    compile_summary = read_json(COMPILE_SUMMARY_031)

    for anchor in [
        SURFACE_CLASS,
        SURFACE_VALIDATE_METHOD,
        SURFACE_INGEST_METHOD,
        SURFACE_BOUNDARY_METHOD,
        "source_static_runtime_echo_receiver_surface",
        ECHO_SCHEMA_ID,
        "PrimaryComponentTick.bCanEverTick = false",
        RECEIVER_VALIDATE_METHOD,
        RECEIVER_APPLY_METHOD,
        "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent",
        "UQuadrotorMworksExperimentConsoleStateComponent",
    ]:
        if anchor not in surface_combined:
            issues.append(f"receiver surface missing anchor: {anchor}")

    runtime_patterns = present(surface_combined, FORBIDDEN_RUNTIME_PATTERNS)
    pose_patterns = present_cpp_code(surface_combined, FORBIDDEN_POSE_PATTERNS)
    if runtime_patterns:
        issues.append("receiver surface contains runtime transport pattern(s): " + ", ".join(runtime_patterns))
    if pose_patterns:
        issues.append("receiver surface contains forbidden pose/input pattern(s): " + ", ".join(pose_patterns))
    if COMMAND_SCHEMA_ID in surface_combined:
        issues.append("receiver surface must not parse mosim.ue_command.v1 pending requests")
    if UNREAL_STATE_SCHEMA_PREFIX in surface_combined:
        issues.append("receiver surface must not parse quadrotor.unreal_state frames")

    for anchor in [RECEIVER_VALIDATE_METHOD, RECEIVER_APPLY_METHOD, ECHO_SCHEMA_ID, "IsAuthoritativeLiveEchoSource"]:
        if anchor not in receiver_combined:
            issues.append(f"command echo receiver missing anchor: {anchor}")
    for anchor in [STATE_PENDING_METHOD, STATE_SINK_METHOD]:
        if anchor not in state_combined:
            issues.append(f"state component missing reducer anchor: {anchor}")
    for source in ["offline_adapter_smoke", "source_level_smoke", "MWORKS_MCP_result_adapter_smoke", "MWORKS_MCP_runtime_adapter_preflight"]:
        if source_literal(source) not in state_source:
            issues.append(f"state component missing smoke-only label guard: {source}")
    if ECHO_SCHEMA_ID in frame_combined or STATE_SINK_METHOD in frame_combined:
        issues.append("quadrotor.unreal_state receiver must not be wired as command echo sink")
    if ECHO_SCHEMA_ID in sender_combined or STATE_SINK_METHOD in sender_combined:
        issues.append("command sender must not be wired as command echo sink")

    for artifact in EXPECTED_CAPTURE_ARTIFACTS:
        if artifact not in validator_source:
            issues.append(f"029 validator missing required artifact anchor: {artifact}")
    for source, authority in AUTHORITATIVE_LIVE_SOURCES.items():
        if source not in validator_source or authority not in validator_source:
            issues.append(f"029 validator missing authoritative source/authority anchor: {source}/{authority}")
    for source in ["build_success", "sender_result_bSent", "quadrotor.unreal_state.v1", "fixture_only_echo"]:
        if source not in validator_source:
            issues.append(f"029 validator missing false-ack rejection anchor: {source}")

    compile_actions = compile_summary.get("compiled_or_linked_actions", [])
    compile_actions_text = "\n".join(str(item) for item in compile_actions)
    compile_surface = "QuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.cpp" in compile_actions_text
    if compile_summary.get("exit_code") != 0:
        issues.append(f"031 compile summary exit_code is not 0: {compile_summary.get('exit_code')!r}")
    if not compile_surface:
        issues.append("031 compile summary does not mention receiver surface .cpp")

    if return_029.get("status") != "completed":
        issues.append("029 return is not completed")
    if return_029.get("capture_bundle_validator_summary", {}).get("source_static_validator_ready") is not True:
        issues.append("029 return does not mark source_static_validator_ready=true")
    if return_030.get("status") != "completed":
        issues.append("030 return is not completed")
    if return_030.get("source_static_receiver_surface_summary", {}).get("does_not_start_transport") is not True:
        issues.append("030 return does not preserve no-transport boundary")
    if return_031.get("status") != "completed":
        issues.append("031 return is not completed")
    if return_031.get("build_only_compile_summary", {}).get("exit_code") != 0:
        issues.append("031 return does not report compile exit_code=0")

    wiring_matrix = build_wiring_matrix()
    false_ack_matrix = build_false_ack_matrix()
    runtime_ack_leaks = [
        row for row in wiring_matrix + false_ack_matrix
        if row.get("accepted_as_runtime_ack_now") is True
    ]
    direct_inputs = [row for row in wiring_matrix if row["direct_receiver_input"]]
    if len(wiring_matrix) != len(EXPECTED_CAPTURE_ARTIFACTS):
        issues.append("wiring matrix does not cover all seven expected capture artifacts")
    if len(direct_inputs) != 1 or direct_inputs[0]["artifact"] != "authoritative_echo_capture.json":
        issues.append("only authoritative_echo_capture.json should be a direct receiver input")

    return {
        "schema": "mosim.ue_runtime_echo_receiver_capture_bundle_wiring.v1",
        "ok": not issues,
        "task_id": TASK_ID,
        "scope_classification": "source-static wiring/checker",
        "source_static_wiring_ready": not issues,
        "runtime_probe_executed": False,
        "unreal_editor_opened": False,
        "ue_runtime_started": False,
        "unreal_build_executed_in_032": False,
        "socket_listener_timer_or_background_loop_started": False,
        "accepted_state_ui_controls_enabled": False,
        "authoritative_runtime_ack_claimable_now": False,
        "live_transport_evidence_rows": 0,
        "runtime_ack_leaks_now": len(runtime_ack_leaks),
        "receiver_surface_anchor": {
            "class": SURFACE_CLASS,
            "header": repo(SURFACE_HEADER),
            "source": repo(SURFACE_SOURCE),
            "validate_method": SURFACE_VALIDATE_METHOD,
            "ingest_method": SURFACE_INGEST_METHOD,
            "boundary_method": SURFACE_BOUNDARY_METHOD,
            "calls_authoritative_validate": RECEIVER_VALIDATE_METHOD in surface_source,
            "calls_authoritative_apply": RECEIVER_APPLY_METHOD in surface_source,
            "tick_disabled": "PrimaryComponentTick.bCanEverTick = false" in surface_source,
            "runtime_transport_patterns_present": runtime_patterns,
            "forbidden_pose_patterns_present": pose_patterns,
            "parses_pending_command_request_schema": COMMAND_SCHEMA_ID in surface_combined,
            "parses_quadrotor_unreal_state": UNREAL_STATE_SCHEMA_PREFIX in surface_combined,
        },
        "capture_bundle_contract_anchor": {
            "validator_script": repo(VALIDATOR_SCRIPT),
            "expected_artifacts": EXPECTED_CAPTURE_ARTIFACTS,
            "authoritative_source_authority_pairs": AUTHORITATIVE_LIVE_SOURCES,
            "false_ack_or_non_live_sources_rejected": sorted(FALSE_ACK_OR_NON_LIVE_SOURCES),
        },
        "source_static_handoff_chain": [
            f"{SURFACE_CLASS}.{SURFACE_VALIDATE_METHOD}",
            "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.IsAuthoritativeRuntimeCommandEchoPacketJson",
            f"{SURFACE_CLASS}.{SURFACE_INGEST_METHOD}",
            "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState",
            "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson",
        ],
        "pending_request_precondition": {
            "schema": COMMAND_SCHEMA_ID,
            "source": "UE command request path only",
            "state_anchor": STATE_PENDING_METHOD,
            "receiver_surface_must_not_synthesize_pending": True,
        },
        "wiring_matrix": wiring_matrix,
        "false_ack_negative_matrix": false_ack_matrix,
        "matrix_summary": {
            "capture_artifact_rows": len(wiring_matrix),
            "false_ack_negative_rows": len(false_ack_matrix),
            "direct_receiver_input_rows": len(direct_inputs),
            "runtime_ack_leaks_now": len(runtime_ack_leaks),
            "live_transport_evidence_rows": 0,
            "authoritative_runtime_ack_claimable_now": False,
        },
        "prior_evidence_consumed": {
            "ue_029_status": return_029.get("status"),
            "ue_029_source_static_validator_ready": return_029.get("capture_bundle_validator_summary", {}).get("source_static_validator_ready"),
            "ue_030_status": return_030.get("status"),
            "ue_030_receiver_does_not_start_transport": return_030.get("source_static_receiver_surface_summary", {}).get("does_not_start_transport"),
            "ue_031_status": return_031.get("status"),
            "ue_031_compile_exit_code": return_031.get("build_only_compile_summary", {}).get("exit_code"),
            "ue_031_compiled_receiver_surface_cpp": compile_surface,
        },
        "future_live_probe_acceptance_gates": [
            "PMO explicitly authorizes a single bounded Unreal runtime/editor probe",
            "runtime_probe_manifest.json identifies authoritative producer source and authority",
            "pending_request_capture.json captures matching mosim.ue_command.v1 request before echo",
            "authoritative_echo_capture.json captures runtime mosim.ue_command_echo.v1 through the receiver surface",
            "request_echo_match_report.json proves run_id/request_id/seq/time_s/command/status match",
            "no_pose_overwrite_report.json proves no pose overwrite or direct Actor transform",
            "false_ack_negative_report.json rejects build/checker/sender/fixture/operator/frame/static rows",
            "timeout_cleanup_manifest.json proves bounded timeout and cleanup",
        ],
        "claim_boundary": [
            "032 proves only source-static wiring between the compiled UE receiver surface and the 029 capture-bundle validator contract.",
            "032 does not open Unreal Editor, PIE, standalone runtime, or UE runtime.",
            "032 does not run Unreal build, bind sockets, start listeners/timers/background loops, or execute live transport.",
            "032 does not edit UE C++ source, Blueprint, UMG, assets, materials, maps, project settings, Sunray/PBR/Blender, MWORKS, ROS2, FAST-LIO, planner, controller, MoSimQuadrotorModel, References, legacy agent runtime, or Git.",
            "032 checker/test/static rows, 031 compile success, 030 source surface, 029 validator success, sender success, fixture rows, operator intent, and quadrotor.unreal_state frames are not live runtime ack.",
            "032 does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime echo, final UI acceptance, planner_ready, FAST-LIO success, controller performance, mission success, or closed_loop.",
        ],
        "issues": issues,
    }


def write_summary(report: dict[str, Any], output_md: Path) -> None:
    lines = [
        "# UE 032 Runtime Echo Receiver Capture Bundle Wiring",
        "",
        f"- ok: {report['ok']}",
        f"- scope: {report['scope_classification']}",
        f"- source_static_wiring_ready: {report['source_static_wiring_ready']}",
        f"- runtime_probe_executed: {report['runtime_probe_executed']}",
        f"- authoritative_runtime_ack_claimable_now: {report['authoritative_runtime_ack_claimable_now']}",
        "",
        "## Wiring Matrix",
        "",
    ]
    for row in report["wiring_matrix"]:
        lines.append(f"- {row['artifact']}: {row['receiver_surface_role']}")
    lines.extend(["", "## Matrix Summary", ""])
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
        output_matrix.write_text(json.dumps(report["wiring_matrix"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(text)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
