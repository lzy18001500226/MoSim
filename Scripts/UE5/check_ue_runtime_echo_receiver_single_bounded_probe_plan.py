#!/usr/bin/env python3
"""Build the UE 033 single bounded runtime probe plan/readiness contract.

This is a source-static checker. It does not open Unreal Editor, run UE
runtime/build, bind sockets, start listeners/timers/threads/background loops,
or claim live command acknowledgement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-SINGLE-BOUNDED-PROBE-PLAN-20260609-033"

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
    "033_single_bounded_probe_plan_checker",
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

FORBIDDEN_POSE_SHORTCUTS = [
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

FORBIDDEN_SOURCE_POSE_PATTERNS = {
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

EVIDENCE_032_DIR = ROOT / "Results/unreal_experiment_console/runtime_echo_receiver_capture_bundle_wiring_20260608_032"
WIRING_032_JSON = EVIDENCE_032_DIR / "runtime_echo_receiver_capture_bundle_wiring.json"
WIRING_032_MATRIX = EVIDENCE_032_DIR / "runtime_echo_receiver_capture_bundle_wiring_matrix.json"
VALIDATOR_029_SCRIPT = ROOT / "Scripts/UE5/check_ue_runtime_probe_capture_bundle_validator.py"
WIRING_032_SCRIPT = ROOT / "Scripts/UE5/check_ue_runtime_echo_receiver_capture_bundle_wiring.py"

RETURN_029 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-PROBE-CAPTURE-BUNDLE-VALIDATOR-20260608-029.json"
RETURN_030 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-SOURCE-GATE-20260608-030.json"
RETURN_031 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-COMPILE-GATE-20260608-031.json"
RETURN_032 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-CAPTURE-BUNDLE-WIRING-20260608-032.json"

BRIDGE_ROOT = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge"
SURFACE_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.h"
SURFACE_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.cpp"
SURFACE_CLASS = "UQuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent"
SURFACE_VALIDATE_METHOD = "ValidateAuthoritativeRuntimeCommandEchoDownlinkJson"
SURFACE_INGEST_METHOD = "IngestAuthoritativeRuntimeCommandEchoDownlinkJson"
SURFACE_BOUNDARY_METHOD = "GetSourceStaticReceiverBoundary"


def repo(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path) -> Any:
    if not path.exists():
        return {} if path.suffix == ".json" else None
    return json.loads(path.read_text(encoding="utf-8"))


def present(source: str, patterns: set[str]) -> list[str]:
    return sorted(pattern for pattern in patterns if pattern in source)


def build_capture_precondition_rows() -> list[dict[str, Any]]:
    return [
        {
            "artifact": "runtime_probe_manifest.json",
            "precondition": "Future PMO packet explicitly authorizes exactly one bounded UE runtime/editor probe and records producer identity.",
            "required_fields": [
                "probe_id",
                "run_id",
                "request_id",
                "capture_session_id",
                "transport_capture_id",
                "producer_identity.source",
                "producer_identity.ack_authority",
                "bounded_probe=true",
                "probe_attempt_count=1",
            ],
            "direct_receiver_input": False,
            "current_runtime_evidence": False,
            "accepted_as_runtime_ack_now": False,
        },
        {
            "artifact": "pending_request_capture.json",
            "precondition": "Capture the matching mosim.ue_command.v1 request before any echo is accepted or rejected.",
            "required_fields": [
                "schema",
                "run_id",
                "request_id",
                "seq",
                "time_s",
                "command.kind",
                "command.payload",
            ],
            "direct_receiver_input": False,
            "current_runtime_evidence": False,
            "accepted_as_runtime_ack_now": False,
        },
        {
            "artifact": "authoritative_echo_capture.json",
            "precondition": "Capture mosim.ue_command_echo.v1 from an authoritative live source and feed it through the receiver surface Validate/Ingest methods.",
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
                "no_pose_overwrite_status=pass",
            ],
            "direct_receiver_input": True,
            "current_runtime_evidence": False,
            "accepted_as_runtime_ack_now": False,
        },
        {
            "artifact": "request_echo_match_report.json",
            "precondition": "Prove pending request identity matches the authoritative echo identity.",
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
            "current_runtime_evidence": False,
            "accepted_as_runtime_ack_now": False,
        },
        {
            "artifact": "no_pose_overwrite_report.json",
            "precondition": "Prove the probe did not use keyboard pose, direct Actor transform, teleport, pose_override, set_uav_pose, or UE truth shortcuts.",
            "required_fields": [
                "no_pose_overwrite_status=pass",
                "forbidden_pose_command_seen=false",
                "direct_actor_transform_seen=false",
                "keyboard_pose_control_seen=false",
                "pose_override_seen=false",
                "set_uav_pose_seen=false",
                "actor_teleport_seen=false",
            ],
            "direct_receiver_input": False,
            "current_runtime_evidence": False,
            "accepted_as_runtime_ack_now": False,
        },
        {
            "artifact": "false_ack_negative_report.json",
            "precondition": "Prove build/checker/sender/fixture/operator/static/frame rows were rejected as live command ack.",
            "required_fields": [
                "false_ack_negative_status=pass",
                "checked_sources",
                "false_ack_rows_accepted_as_runtime_ack=0",
                "accepted_runtime_ack_from_false_sources=false",
            ],
            "direct_receiver_input": False,
            "current_runtime_evidence": False,
            "accepted_as_runtime_ack_now": False,
        },
        {
            "artifact": "timeout_cleanup_manifest.json",
            "precondition": "Prove the single attempt stayed within timeout and left no listener, timer, background loop, socket, or accepted-state UI running.",
            "required_fields": [
                "timeout_seconds in (0, 60]",
                "probe_attempt_count=1",
                "cleanup_status=pass",
                "cleanup_completed=true",
                "listener_left_running=false",
                "timer_left_running=false",
                "background_loop_left_running=false",
                "socket_left_bound=false",
                "accepted_ui_controls_enabled=false",
            ],
            "direct_receiver_input": False,
            "current_runtime_evidence": False,
            "accepted_as_runtime_ack_now": False,
        },
    ]


def build_false_ack_rules() -> list[dict[str, Any]]:
    return [
        {
            "source": source,
            "future_probe_expected_result": "reject_as_runtime_ack",
            "accepted_as_runtime_ack_now": False,
            "reason": "Only matching authoritative mosim.ue_command_echo.v1 from an approved live producer can accept or reject a pending command.",
        }
        for source in sorted(FALSE_ACK_OR_NON_LIVE_SOURCES)
    ]


def build_no_pose_checks() -> list[dict[str, Any]]:
    return [
        {
            "check": shortcut,
            "required_result": "absent_or_false",
            "accepted_as_runtime_ack_now": False,
        }
        for shortcut in FORBIDDEN_POSE_SHORTCUTS
    ]


def build_report() -> dict[str, Any]:
    issues: list[str] = []

    required_paths = [
        WIRING_032_JSON,
        WIRING_032_MATRIX,
        VALIDATOR_029_SCRIPT,
        WIRING_032_SCRIPT,
        RETURN_029,
        RETURN_030,
        RETURN_031,
        RETURN_032,
        SURFACE_HEADER,
        SURFACE_SOURCE,
    ]
    for path in required_paths:
        if not path.exists():
            issues.append(f"missing required path: {repo(path)}")

    wiring_032 = read_json(WIRING_032_JSON)
    wiring_032_matrix = read_json(WIRING_032_MATRIX)
    return_029 = read_json(RETURN_029)
    return_030 = read_json(RETURN_030)
    return_031 = read_json(RETURN_031)
    return_032 = read_json(RETURN_032)
    validator_source = read_text(VALIDATOR_029_SCRIPT)
    wiring_source = read_text(WIRING_032_SCRIPT)
    surface_source = read_text(SURFACE_SOURCE)
    surface_header = read_text(SURFACE_HEADER)
    surface_combined = surface_header + "\n" + surface_source

    if not isinstance(wiring_032_matrix, list):
        issues.append("032 wiring matrix is not a JSON list")
        wiring_032_matrix = []

    if wiring_032.get("ok") is not True:
        issues.append("032 wiring evidence is not ok=true")
    if wiring_032.get("source_static_wiring_ready") is not True:
        issues.append("032 wiring evidence does not mark source_static_wiring_ready=true")
    if wiring_032.get("runtime_probe_executed") is not False:
        issues.append("032 wiring evidence must not have executed runtime probe")
    if wiring_032.get("authoritative_runtime_ack_claimable_now") is not False:
        issues.append("032 wiring evidence must not claim authoritative runtime ack")
    if wiring_032.get("runtime_ack_leaks_now") != 0:
        issues.append("032 wiring evidence reports runtime ack leaks")
    if wiring_032.get("live_transport_evidence_rows") != 0:
        issues.append("032 wiring evidence reports live transport rows")

    matrix_artifacts = {row.get("artifact") for row in wiring_032_matrix if isinstance(row, dict)}
    if matrix_artifacts != set(EXPECTED_CAPTURE_ARTIFACTS):
        issues.append("032 wiring matrix does not cover exactly the seven expected capture artifacts")
    direct_inputs = [
        row for row in wiring_032_matrix
        if isinstance(row, dict) and row.get("direct_receiver_input") is True
    ]
    if len(direct_inputs) != 1 or direct_inputs[0].get("artifact") != "authoritative_echo_capture.json":
        issues.append("032 wiring matrix must have only authoritative_echo_capture.json as direct receiver input")
    if any(row.get("accepted_as_runtime_ack_now") is True for row in wiring_032_matrix if isinstance(row, dict)):
        issues.append("032 wiring matrix contains a current runtime ack row")

    for artifact in EXPECTED_CAPTURE_ARTIFACTS:
        if artifact not in validator_source:
            issues.append(f"029 validator missing artifact anchor: {artifact}")
        if artifact not in wiring_source:
            issues.append(f"032 wiring checker missing artifact anchor: {artifact}")
    for source, authority in AUTHORITATIVE_LIVE_SOURCES.items():
        if source not in validator_source or authority not in validator_source:
            issues.append(f"029 validator missing authoritative source/authority anchor: {source}/{authority}")

    for anchor in [
        SURFACE_CLASS,
        SURFACE_VALIDATE_METHOD,
        SURFACE_INGEST_METHOD,
        SURFACE_BOUNDARY_METHOD,
        "source_static_runtime_echo_receiver_surface",
        ECHO_SCHEMA_ID,
        "PrimaryComponentTick.bCanEverTick = false",
        "IsAuthoritativeRuntimeCommandEchoPacketJson",
        "ApplyAuthoritativeRuntimeCommandEchoDownlinkJsonToState",
    ]:
        if anchor not in surface_combined:
            issues.append(f"receiver surface missing anchor: {anchor}")

    runtime_patterns = present(surface_combined, FORBIDDEN_RUNTIME_PATTERNS)
    pose_patterns = present(surface_combined, FORBIDDEN_SOURCE_POSE_PATTERNS)
    if runtime_patterns:
        issues.append("receiver surface contains runtime transport pattern(s): " + ", ".join(runtime_patterns))
    if pose_patterns:
        issues.append("receiver surface contains forbidden pose/input pattern(s): " + ", ".join(pose_patterns))
    if COMMAND_SCHEMA_ID in surface_combined:
        issues.append("receiver surface must not parse mosim.ue_command.v1 pending requests")

    for name, packet in [
        ("029", return_029),
        ("030", return_030),
        ("031", return_031),
        ("032", return_032),
    ]:
        if packet.get("status") != "completed":
            issues.append(f"{name} return is not completed")
    if return_031.get("build_only_compile_summary", {}).get("exit_code") != 0:
        issues.append("031 return does not report compile exit_code=0")

    capture_rows = build_capture_precondition_rows()
    false_ack_rules = build_false_ack_rules()
    no_pose_checks = build_no_pose_checks()
    runtime_ack_leaks_now = sum(
        1
        for row in capture_rows + false_ack_rules + no_pose_checks
        if row.get("accepted_as_runtime_ack_now") is True
    )
    if runtime_ack_leaks_now:
        issues.append("033 plan rows contain current runtime ack claims")

    return {
        "schema": "mosim.ue_runtime_echo_receiver_single_bounded_probe_plan.v1",
        "ok": not issues,
        "task_id": TASK_ID,
        "scope_classification": "source-static single-bounded-probe plan/readiness",
        "source_static_plan_ready": not issues,
        "runtime_probe_executed": False,
        "unreal_editor_opened": False,
        "ue_runtime_started": False,
        "unreal_build_executed_in_033": False,
        "socket_listener_timer_thread_or_background_loop_started": False,
        "accepted_state_ui_controls_enabled": False,
        "authoritative_runtime_ack_claimable_now": False,
        "live_transport_evidence_rows": 0,
        "runtime_ack_leaks_now": runtime_ack_leaks_now,
        "single_bounded_probe_plan": {
            "future_pmo_runtime_authorization_required": True,
            "future_probe_attempt_count": 1,
            "future_probe_retry_budget": 0,
            "timeout_seconds_range": {
                "exclusive_min": 0,
                "inclusive_max": 60,
                "recommended_default": 60,
            },
            "future_probe_must_stop_after_first_attempt": True,
            "future_runtime_surface": "bounded UE runtime/editor command-echo probe only when a later PMO packet explicitly authorizes runtime scope",
            "authoritative_producer_identity": {
                "allowed_source_authority_pairs": AUTHORITATIVE_LIVE_SOURCES,
                "required_fields": [
                    "producer_surface",
                    "producer_instance_id",
                    "source",
                    "ack_authority",
                    "capture_session_id",
                    "transport_capture_id",
                ],
            },
            "pending_request_capture": {
                "schema": COMMAND_SCHEMA_ID,
                "source": "UE command request path only",
                "must_exist_before_echo": True,
                "receiver_surface_must_not_synthesize_pending": True,
            },
            "authoritative_echo_capture": {
                "schema": ECHO_SCHEMA_ID,
                "direct_receiver_input": "authoritative_echo_capture.json",
                "receiver_surface_class": SURFACE_CLASS,
                "receiver_surface_validate_method": SURFACE_VALIDATE_METHOD,
                "receiver_surface_ingest_method": SURFACE_INGEST_METHOD,
                "status_values": ["accepted", "rejected"],
            },
            "request_echo_identity_match_fields": [
                "run_id",
                "request_id",
                "seq",
                "time_s",
                "command.kind or command_kind",
                "status",
            ],
            "seven_capture_bundle_artifacts": EXPECTED_CAPTURE_ARTIFACTS,
            "timeout_cleanup_required": True,
            "false_ack_negative_report_required": True,
            "no_pose_overwrite_report_required": True,
        },
        "capture_bundle_precondition_matrix": capture_rows,
        "false_ack_negative_rules": false_ack_rules,
        "no_pose_overwrite_checks": no_pose_checks,
        "source_static_evidence_consumed": {
            "ue_029_return_status": return_029.get("status"),
            "ue_030_return_status": return_030.get("status"),
            "ue_031_return_status": return_031.get("status"),
            "ue_031_compile_exit_code": return_031.get("build_only_compile_summary", {}).get("exit_code"),
            "ue_032_return_status": return_032.get("status"),
            "ue_032_source_static_wiring_ready": wiring_032.get("source_static_wiring_ready"),
            "ue_032_runtime_ack_leaks_now": wiring_032.get("runtime_ack_leaks_now"),
            "ue_032_live_transport_evidence_rows": wiring_032.get("live_transport_evidence_rows"),
        },
        "receiver_surface_source_scan": {
            "header": repo(SURFACE_HEADER),
            "source": repo(SURFACE_SOURCE),
            "validate_method_present": SURFACE_VALIDATE_METHOD in surface_combined,
            "ingest_method_present": SURFACE_INGEST_METHOD in surface_combined,
            "boundary_method_present": SURFACE_BOUNDARY_METHOD in surface_combined,
            "runtime_transport_patterns_present": runtime_patterns,
            "forbidden_pose_patterns_present": pose_patterns,
            "parses_pending_command_request_schema": COMMAND_SCHEMA_ID in surface_combined,
        },
        "future_single_probe_stop_triggers": [
            "More than one live probe attempt would be required.",
            "Timeout would exceed 60 seconds or no cleanup manifest can be produced.",
            "Authoritative producer identity or source/authority pair is missing.",
            "Pending mosim.ue_command.v1 request capture is missing or mismatched.",
            "Authoritative mosim.ue_command_echo.v1 capture does not pass through the receiver surface.",
            "Request/echo identity fields do not match.",
            "No-pose-overwrite report fails or any forbidden pose shortcut appears.",
            "False-ack negative report accepts build/checker/sender/fixture/operator/static/frame rows.",
            "UE runtime/editor, MWORKS, ROS2, planner, controller, or manual review needs exceed the future packet authorization.",
        ],
        "matrix_summary": {
            "capture_bundle_precondition_rows": len(capture_rows),
            "false_ack_negative_rows": len(false_ack_rules),
            "no_pose_overwrite_check_rows": len(no_pose_checks),
            "future_probe_attempt_count": 1,
            "max_timeout_seconds": 60,
            "runtime_ack_leaks_now": runtime_ack_leaks_now,
            "live_transport_evidence_rows": 0,
            "authoritative_runtime_ack_claimable_now": False,
        },
        "claim_boundary": [
            "033 proves only a source-static plan/readiness contract for one future bounded UE runtime command-echo probe.",
            "033 does not open Unreal Editor, PIE, standalone runtime, game window, or UE runtime.",
            "033 does not run Unreal build, bind sockets, start listeners/timers/threads/background loops, or execute live transport.",
            "033 does not edit UE C++ source, Blueprint, UMG, Slate/Web UI, assets, materials, maps, project settings, Sunray/PBR/Blender, MWORKS, ROS2, FAST-LIO, planner, controller, MoSimQuadrotorModel, References, CoAgent runtime, or Git.",
            "033 checker/test/static rows, 032 wiring, 031 compile success, 030 source surface, 029 validator success, sender success, fixture rows, operator intent, and quadrotor.unreal_state frames are not live runtime ack.",
            "A later live probe requires a separate PMO task packet with explicit runtime authorization, one-attempt budget, timeout, cleanup, capture bundle, false-ack negative report, and no-pose-overwrite proof.",
            "033 does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime echo, final UI acceptance, planner_ready, FAST-LIO success, controller performance, mission success, or closed_loop.",
        ],
        "issues": issues,
    }


def write_summary(report: dict[str, Any], output_md: Path) -> None:
    lines = [
        "# UE 033 Single Bounded Runtime Probe Plan",
        "",
        f"- ok: {report['ok']}",
        f"- scope: {report['scope_classification']}",
        f"- source_static_plan_ready: {report['source_static_plan_ready']}",
        f"- runtime_probe_executed: {report['runtime_probe_executed']}",
        f"- authoritative_runtime_ack_claimable_now: {report['authoritative_runtime_ack_claimable_now']}",
        f"- future_probe_attempt_count: {report['single_bounded_probe_plan']['future_probe_attempt_count']}",
        f"- max_timeout_seconds: {report['single_bounded_probe_plan']['timeout_seconds_range']['inclusive_max']}",
        "",
        "## Seven Capture Bundle Preconditions",
        "",
    ]
    for row in report["capture_bundle_precondition_matrix"]:
        lines.append(f"- {row['artifact']}: {row['precondition']}")
    lines.extend(["", "## Stop Triggers", ""])
    for trigger in report["future_single_probe_stop_triggers"]:
        lines.append(f"- {trigger}")
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
            "capture_bundle_precondition_matrix": report["capture_bundle_precondition_matrix"],
            "false_ack_negative_rules": report["false_ack_negative_rules"],
            "no_pose_overwrite_checks": report["no_pose_overwrite_checks"],
            "matrix_summary": report["matrix_summary"],
        }
        output_matrix.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(text)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
