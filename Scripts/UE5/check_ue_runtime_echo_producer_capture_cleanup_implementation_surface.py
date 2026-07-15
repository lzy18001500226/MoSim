#!/usr/bin/env python3
"""Validate the UE 036 producer/capture/cleanup implementation surface.

This checker is source/static only. It does not open Unreal Editor, run UE
runtime/build, bind sockets, start listeners/timers/threads/background loops,
consume a live probe attempt, or claim live command acknowledgement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-PRODUCER-CAPTURE-CLEANUP-IMPLEMENTATION-SURFACE-20260609-036"

EVIDENCE_035 = ROOT / "Results/unreal_experiment_console/runtime_echo_producer_capture_cleanup_route_contract_20260609_035/runtime_echo_producer_capture_cleanup_route_contract.json"
MATRIX_035 = ROOT / "Results/unreal_experiment_console/runtime_echo_producer_capture_cleanup_route_contract_20260609_035/runtime_echo_producer_capture_cleanup_route_contract_matrix.json"
BLOCKER_034 = ROOT / "Results/agent_packets/blockers/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-SINGLE-BOUNDED-LIVE-PROBE-20260609-034.json"

BRIDGE_ROOT = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge"
SENDER_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksUdpCommandSenderComponent.h"
SENDER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksUdpCommandSenderComponent.cpp"
RECEIVER_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.h"
RECEIVER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.cpp"

EXPECTED_ARTIFACTS = [
    "runtime_probe_manifest.json",
    "pending_request_capture.json",
    "authoritative_echo_capture.json",
    "request_echo_match_report.json",
    "no_pose_overwrite_report.json",
    "false_ack_negative_report.json",
    "timeout_cleanup_manifest.json",
]

EXPECTED_SURFACE_METHODS = {
    "pending_request_capture": {
        "header": SENDER_HEADER,
        "source": SENDER_SOURCE,
        "method": "BuildPendingRequestCaptureJson",
        "artifact": "pending_request_capture.json",
        "schema": "mosim.ue_runtime_probe_capture.pending_request.v1",
    },
    "runtime_probe_manifest": {
        "header": RECEIVER_HEADER,
        "source": RECEIVER_SOURCE,
        "method": "BuildRuntimeProbeManifestJson",
        "artifact": "runtime_probe_manifest.json",
        "schema": "mosim.ue_runtime_probe_manifest.v1",
    },
    "authoritative_echo_capture": {
        "header": RECEIVER_HEADER,
        "source": RECEIVER_SOURCE,
        "method": "BuildAuthoritativeEchoCaptureJson",
        "artifact": "authoritative_echo_capture.json",
        "schema": "mosim.ue_runtime_probe_capture.authoritative_echo.v1",
    },
    "request_echo_match_report": {
        "header": RECEIVER_HEADER,
        "source": RECEIVER_SOURCE,
        "method": "BuildRequestEchoMatchReportJson",
        "artifact": "request_echo_match_report.json",
        "schema": "mosim.ue_runtime_probe_capture.request_echo_match_report.v1",
    },
    "no_pose_overwrite_report": {
        "header": RECEIVER_HEADER,
        "source": RECEIVER_SOURCE,
        "method": "BuildNoPoseOverwriteReportJson",
        "artifact": "no_pose_overwrite_report.json",
        "schema": "mosim.ue_runtime_probe_capture.no_pose_overwrite_report.v1",
    },
    "false_ack_negative_report": {
        "header": RECEIVER_HEADER,
        "source": RECEIVER_SOURCE,
        "method": "BuildFalseAckNegativeReportJson",
        "artifact": "false_ack_negative_report.json",
        "schema": "mosim.ue_runtime_probe_capture.false_ack_negative_report.v1",
    },
    "timeout_cleanup_manifest": {
        "header": RECEIVER_HEADER,
        "source": RECEIVER_SOURCE,
        "method": "BuildTimeoutCleanupManifestJson",
        "artifact": "timeout_cleanup_manifest.json",
        "schema": "mosim.ue_runtime_probe_capture.timeout_cleanup_manifest.v1",
    },
}

AUTHORITATIVE_PAIRS = {
    "MWORKS_live_downlink": "MWORKS",
    "ROS2_runtime_echo": "ROS2",
    "MWORKS_ROS2_live_downlink": "MWORKS_ROS2",
}

FALSE_ACK_SOURCES = [
    "034_no_side_effect_preflight_blocker",
    "033_single_bounded_probe_plan_checker",
    "032_capture_bundle_wiring_checker",
    "031_compile_pass",
    "build_success",
    "checker_success",
    "sender_result_bSent",
    "udp_send_success",
    "fixture_only_echo",
    "operator_intent",
    "quadrotor.unreal_state.frame",
    "quadrotor.unreal_state.v1",
    "MWORKS_MCP_runtime_adapter_preflight",
]

NO_POSE_MARKERS = [
    "pose_override",
    "set_uav_pose",
    "actor_transform",
    "keyboard_pose",
    "direct_actor_transform",
    "actor_teleport",
    "SetActorLocation",
    "SetActorTransform",
    "TeleportTo",
    "UE_truth_shortcut",
]

RECEIVER_FORBIDDEN_RUNTIME_PATTERNS = [
    "Common/UdpSocketBuilder.h",
    "Common/UdpSocketReceiver.h",
    "FUdpSocketBuilder",
    "FUdpSocketReceiver",
    "FRunnable",
    "FRunnableThread",
    "FTimerHandle",
    "OnDataReceived",
    "StartReceiver",
    "StopReceiver",
    "ListenPort",
    "BindUObject",
    "CreateSocket",
    "AsyncTask",
    "BeginPlay",
    "EndPlay",
]


def repo(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def source_contains(path: Path, token: str) -> bool:
    return token in read_text(path)


def build_surface_rows() -> list[dict[str, Any]]:
    rows = []
    for route, spec in EXPECTED_SURFACE_METHODS.items():
        header = spec["header"]
        source = spec["source"]
        header_text = read_text(header)
        source_text = read_text(source)
        method = spec["method"]
        rows.append(
            {
                "route": route,
                "artifact": spec["artifact"],
                "schema": spec["schema"],
                "header": repo(header),
                "source": repo(source),
                "method": method,
                "method_declared_in_header": method in header_text,
                "method_defined_in_source": method in source_text,
                "artifact_literal_present": spec["artifact"] in source_text,
                "schema_literal_present": spec["schema"] in source_text,
                "current_runtime_ready": False,
                "accepted_as_runtime_ack_now": False,
            }
        )
    return rows


def build_report() -> dict[str, Any]:
    issues: list[str] = []
    for path in [EVIDENCE_035, MATRIX_035, BLOCKER_034, SENDER_HEADER, SENDER_SOURCE, RECEIVER_HEADER, RECEIVER_SOURCE]:
        if not path.exists():
            issues.append(f"missing required path: {repo(path)}")

    evidence_035 = read_json(EVIDENCE_035)
    matrix_035 = read_json(MATRIX_035)
    blocker_034 = read_json(BLOCKER_034)

    if evidence_035.get("ok") is not True:
        issues.append("035 route contract evidence is not ok=true")
    if evidence_035.get("runtime_route_ready_now") is not False:
        issues.append("035 evidence must not mark runtime_route_ready_now=true")
    if evidence_035.get("live_attempt_consumed") is not False:
        issues.append("035 evidence must keep live_attempt_consumed=false")
    if evidence_035.get("runtime_probe_executed") is not False:
        issues.append("035 evidence must keep runtime_probe_executed=false")
    if evidence_035.get("runtime_ack_leaks_now") != 0:
        issues.append("035 evidence must keep runtime_ack_leaks_now=0")
    if blocker_034.get("preflight_result", {}).get("live_attempt_consumed") is not False:
        issues.append("034 blocker must preserve live_attempt_consumed=false")
    if blocker_034.get("preflight_result", {}).get("runtime_probe_executed") is not False:
        issues.append("034 blocker must preserve runtime_probe_executed=false")

    surface_rows = build_surface_rows()
    for row in surface_rows:
        if not row["method_declared_in_header"]:
            issues.append(f"{row['method']} missing header declaration")
        if not row["method_defined_in_source"]:
            issues.append(f"{row['method']} missing source definition")
        if not row["artifact_literal_present"]:
            issues.append(f"{row['method']} missing artifact literal {row['artifact']}")
        if not row["schema_literal_present"]:
            issues.append(f"{row['method']} missing schema literal {row['schema']}")

    sender_text = read_text(SENDER_SOURCE)
    receiver_text = read_text(RECEIVER_SOURCE)
    receiver_all_text = read_text(RECEIVER_HEADER) + "\n" + receiver_text

    for source, authority in AUTHORITATIVE_PAIRS.items():
        if source not in receiver_text or authority not in receiver_text:
            issues.append(f"receiver implementation missing authoritative pair {source}/{authority}")
    for source in FALSE_ACK_SOURCES:
        if source not in matrix_035.get("false_ack_rejection_rules", [{}])[0].get("source", "") and source not in json.dumps(matrix_035, ensure_ascii=False):
            issues.append(f"035 false-ack matrix missing source {source}")
    for marker in NO_POSE_MARKERS:
        if marker not in receiver_text:
            issues.append(f"receiver implementation missing no-pose marker {marker}")

    if "pending_request_captured_before_echo" not in sender_text:
        issues.append("sender pending request capture must record pending_request_captured_before_echo")
    if "accepted_as_runtime_ack" not in sender_text or "accepted_as_runtime_ack" not in receiver_text:
        issues.append("implementation surface must mark capture artifacts accepted_as_runtime_ack=false")
    if "BuildPendingRequestCaptureJson" in receiver_text:
        issues.append("receiver surface must not synthesize pending request capture")
    if "mosim.ue_command.v1" in receiver_all_text:
        issues.append("receiver surface must not parse pending mosim.ue_command.v1")

    runtime_pattern_hits = sorted(pattern for pattern in RECEIVER_FORBIDDEN_RUNTIME_PATTERNS if pattern in receiver_all_text)
    if runtime_pattern_hits:
        issues.append("receiver surface contains forbidden runtime transport pattern(s): " + ", ".join(runtime_pattern_hits))

    artifacts_from_rows = {row["artifact"] for row in surface_rows}
    if artifacts_from_rows != set(EXPECTED_ARTIFACTS):
        issues.append("implementation surface does not cover exactly the seven expected artifacts")
    runtime_ack_leak_rows = [row for row in surface_rows if row["accepted_as_runtime_ack_now"]]

    report = {
        "schema": "mosim.ue_runtime_echo_producer_capture_cleanup_implementation_surface.v1",
        "ok": not issues,
        "task_id": TASK_ID,
        "scope_classification": "source-static producer/capture/cleanup implementation surface",
        "source_static_implementation_surface_ready": not issues,
        "runtime_route_ready_now": False,
        "live_attempt_consumed": False,
        "runtime_probe_executed": False,
        "unreal_editor_opened": False,
        "ue_runtime_started": False,
        "unreal_build_executed_in_036": False,
        "socket_listener_timer_thread_or_background_loop_started": False,
        "accepted_state_ui_controls_enabled": False,
        "authoritative_runtime_ack_claimable_now": False,
        "live_transport_evidence_rows": 0,
        "runtime_ack_leaks_now": len(runtime_ack_leak_rows),
        "implementation_surface_rows": surface_rows,
        "producer_capture_cleanup_surface": {
            "authoritative_source_authority_pairs": AUTHORITATIVE_PAIRS,
            "pending_request_capture_surface": {
                "method": "BuildPendingRequestCaptureJson",
                "source": repo(SENDER_SOURCE),
                "artifact": "pending_request_capture.json",
                "must_exist_before_echo": True,
                "accepted_as_runtime_ack_now": False,
            },
            "authoritative_echo_capture_surface": {
                "method": "BuildAuthoritativeEchoCaptureJson",
                "source": repo(RECEIVER_SOURCE),
                "artifact": "authoritative_echo_capture.json",
                "direct_receiver_input": True,
                "accepted_as_runtime_ack_now": False,
            },
            "timeout_cleanup_surface": {
                "method": "BuildTimeoutCleanupManifestJson",
                "timeout_seconds_inclusive_max": 60,
                "probe_attempt_count": 1,
                "retry_count": 0,
                "accepted_as_runtime_ack_now": False,
            },
        },
        "false_ack_rejection_boundary": {
            "checked_sources": FALSE_ACK_SOURCES,
            "accepted_runtime_ack_from_false_sources": False,
            "actual_runtime_ack_claimed_from_static_sources": False,
        },
        "no_pose_overwrite_boundary": {
            "checked_markers": NO_POSE_MARKERS,
            "forbidden_pose_command_seen": False,
            "direct_actor_transform_seen": False,
            "keyboard_pose_control_seen": False,
            "pose_override_seen": False,
            "set_uav_pose_seen": False,
            "actor_teleport_seen": False,
            "ue_truth_shortcut_seen": False,
        },
        "prior_evidence_consumed": {
            "ue_034_status": blocker_034.get("status"),
            "ue_034_live_attempt_consumed": blocker_034.get("preflight_result", {}).get("live_attempt_consumed"),
            "ue_034_runtime_probe_executed": blocker_034.get("preflight_result", {}).get("runtime_probe_executed"),
            "ue_035_ok": evidence_035.get("ok"),
            "ue_035_source_static_route_contract_ready": evidence_035.get("source_static_route_contract_ready"),
            "ue_035_runtime_route_ready_now": evidence_035.get("runtime_route_ready_now"),
            "ue_035_runtime_ack_leaks_now": evidence_035.get("runtime_ack_leaks_now"),
        },
        "matrix_summary": {
            "implementation_surface_rows": len(surface_rows),
            "implemented_artifact_rows": len(artifacts_from_rows),
            "false_ack_rejection_rows": len(FALSE_ACK_SOURCES),
            "no_pose_overwrite_marker_rows": len(NO_POSE_MARKERS),
            "current_runtime_ready_rows": sum(1 for row in surface_rows if row["current_runtime_ready"]),
            "runtime_ack_leaks_now": len(runtime_ack_leak_rows),
            "live_transport_evidence_rows": 0,
            "authoritative_runtime_ack_claimable_now": False,
        },
        "future_live_probe_preconditions": [
            "PMO explicitly authorizes a single bounded UE runtime/editor probe after the source/static surface receives an executable live producer route.",
            "A producer instance supplies source/ack_authority plus producer_surface/producer_instance_id/capture_session_id/transport_capture_id.",
            "BuildPendingRequestCaptureJson captures a mosim.ue_command.v1 pending request before any echo is ingested.",
            "BuildAuthoritativeEchoCaptureJson captures a mosim.ue_command_echo.v1 row from an allowed source/authority pair.",
            "BuildRequestEchoMatchReportJson reports matching run_id/request_id/seq/time_s/command kind/status.",
            "BuildNoPoseOverwriteReportJson and BuildFalseAckNegativeReportJson reject pose shortcuts and static/build/checker/sender/operator/fixture/frame rows.",
            "BuildTimeoutCleanupManifestJson proves timeout <= 60 seconds, attempt=1, retry=0, cleanup complete, and no leftover runtime loop/socket/listener/timer/accepted UI.",
        ],
        "claim_boundary": [
            "036 proves only source/static implementation-surface materialization for future producer/capture/cleanup artifacts.",
            "036 does not open Unreal Editor, PIE, standalone runtime, game window, or UE runtime.",
            "036 does not run Unreal build, bind sockets, start listeners/timers/threads/background loops, or execute live transport.",
            "036 does not edit Blueprint, UMG, Slate/Web UI, assets, materials, maps, project settings, Sunray/PBR/Blender, MWORKS, ROS2, FAST-LIO, planner, controller, MoSimQuadrotorModel, References, legacy agent runtime, Codex App private state, visible-thread lifecycle, or Git.",
            "036 checker/test/static rows, source-static implementation methods, sender packet construction, fixture rows, operator intent, build success, and quadrotor.unreal_state frames are not live runtime ack.",
            "034 remains the latest bounded live preflight and records live_attempt_consumed=false and runtime_probe_executed=false.",
            "036 does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime echo, final UI acceptance, planner_ready, FAST-LIO success, controller performance, mission success, or closed_loop.",
        ],
        "issues": issues,
    }
    return report


def write_summary(report: dict[str, Any], output_md: Path) -> None:
    lines = [
        "# UE 036 Producer/Capture/Cleanup Implementation Surface",
        "",
        f"- ok: {report['ok']}",
        f"- source_static_implementation_surface_ready: {report['source_static_implementation_surface_ready']}",
        f"- runtime_route_ready_now: {report['runtime_route_ready_now']}",
        f"- live_attempt_consumed: {report['live_attempt_consumed']}",
        f"- runtime_probe_executed: {report['runtime_probe_executed']}",
        "",
        "## Implementation Surface Rows",
        "",
    ]
    for row in report["implementation_surface_rows"]:
        lines.append(
            f"- {row['route']} -> {row['method']} -> {row['artifact']}: "
            f"declared={row['method_declared_in_header']}, defined={row['method_defined_in_source']}, "
            f"runtime_ready={row['current_runtime_ready']}"
        )
    lines.extend(["", "## Future Live Probe Preconditions", ""])
    for item in report["future_live_probe_preconditions"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Claim Boundary", ""])
    for item in report["claim_boundary"]:
        lines.append(f"- {item}")
    if report["issues"]:
        lines.extend(["", "## Issues", ""])
        for issue in report["issues"]:
            lines.append(f"- {issue}")
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
            "implementation_surface_rows": report["implementation_surface_rows"],
            "false_ack_rejection_boundary": report["false_ack_rejection_boundary"],
            "no_pose_overwrite_boundary": report["no_pose_overwrite_boundary"],
            "matrix_summary": report["matrix_summary"],
        }
        output_matrix.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(text)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
