#!/usr/bin/env python3
"""Validate UE 037 source/static build-readiness for runtime echo surfaces.

This checker is source/static only. It does not run UnrealBuildTool, open
Unreal Editor, start UE runtime, bind sockets, start listeners/timers/threads,
consume a live probe attempt, or claim live command acknowledgement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "PMO-UE-R2-RUNTIME-ECHO-BUILD-READINESS-SOURCE-STATIC-20260609-037"

TASK_PACKET = ROOT / "Results/agent_packets/tasks/ue/PMO-UE-R2-RUNTIME-ECHO-BUILD-READINESS-SOURCE-STATIC-20260609-037.json"
BLOCKER_034 = ROOT / "Results/agent_packets/blockers/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-RECEIVER-SINGLE-BOUNDED-LIVE-PROBE-20260609-034.json"
RETURN_036 = ROOT / "Results/agent_packets/returns/RFLY-MOSIM-UE-CONSOLE-RUNTIME-ECHO-PRODUCER-CAPTURE-CLEANUP-IMPLEMENTATION-SURFACE-20260609-036.json"
EVIDENCE_036 = ROOT / "Results/unreal_experiment_console/runtime_echo_producer_capture_cleanup_implementation_surface_20260609_036/runtime_echo_producer_capture_cleanup_implementation_surface.json"
COMMAND_SCHEMA = ROOT / "Config/schemas/mosim_ue_command_v1.schema.json"
ECHO_SCHEMA = ROOT / "Config/schemas/mosim_ue_command_echo_v1.schema.json"

BRIDGE_ROOT = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge"
BUILD_CS = BRIDGE_ROOT / "QuadrotorMworksBridge.Build.cs"
SENDER_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksUdpCommandSenderComponent.h"
SENDER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksUdpCommandSenderComponent.cpp"
RECEIVER_HEADER = BRIDGE_ROOT / "Public/QuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.h"
RECEIVER_SOURCE = BRIDGE_ROOT / "Private/QuadrotorMworksExperimentConsoleRuntimeEchoReceiverSurfaceComponent.cpp"

REQUIRED_MODULE_DEPENDENCIES = {
    "Core",
    "CoreUObject",
    "Engine",
    "Json",
    "JsonUtilities",
    "Networking",
    "Sockets",
}

REQUIRED_BUILD_READY_SYMBOLS = {
    "BuildPendingRequestCaptureJson": {
        "header": SENDER_HEADER,
        "source": SENDER_SOURCE,
        "owner": "sender",
        "artifact": "pending_request_capture.json",
        "schema": "mosim.ue_runtime_probe_capture.pending_request.v1",
    },
    "BuildRuntimeProbeManifestJson": {
        "header": RECEIVER_HEADER,
        "source": RECEIVER_SOURCE,
        "owner": "receiver",
        "artifact": "runtime_probe_manifest.json",
        "schema": "mosim.ue_runtime_probe_manifest.v1",
    },
    "BuildAuthoritativeEchoCaptureJson": {
        "header": RECEIVER_HEADER,
        "source": RECEIVER_SOURCE,
        "owner": "receiver",
        "artifact": "authoritative_echo_capture.json",
        "schema": "mosim.ue_runtime_probe_capture.authoritative_echo.v1",
    },
    "BuildRequestEchoMatchReportJson": {
        "header": RECEIVER_HEADER,
        "source": RECEIVER_SOURCE,
        "owner": "receiver",
        "artifact": "request_echo_match_report.json",
        "schema": "mosim.ue_runtime_probe_capture.request_echo_match_report.v1",
    },
    "BuildNoPoseOverwriteReportJson": {
        "header": RECEIVER_HEADER,
        "source": RECEIVER_SOURCE,
        "owner": "receiver",
        "artifact": "no_pose_overwrite_report.json",
        "schema": "mosim.ue_runtime_probe_capture.no_pose_overwrite_report.v1",
    },
    "BuildFalseAckNegativeReportJson": {
        "header": RECEIVER_HEADER,
        "source": RECEIVER_SOURCE,
        "owner": "receiver",
        "artifact": "false_ack_negative_report.json",
        "schema": "mosim.ue_runtime_probe_capture.false_ack_negative_report.v1",
    },
    "BuildTimeoutCleanupManifestJson": {
        "header": RECEIVER_HEADER,
        "source": RECEIVER_SOURCE,
        "owner": "receiver",
        "artifact": "timeout_cleanup_manifest.json",
        "schema": "mosim.ue_runtime_probe_capture.timeout_cleanup_manifest.v1",
    },
}

REQUIRED_SCHEMA_ANCHORS = {
    "command_schema": {
        "path": COMMAND_SCHEMA,
        "schema": "mosim.ue_command.v1",
        "required_runtime_ack_note": "mosim.ue_command_echo.v1",
    },
    "echo_schema": {
        "path": ECHO_SCHEMA,
        "schema": "mosim.ue_command_echo.v1",
        "ack_authorities": ["MWORKS", "ROS2", "MWORKS_ROS2"],
        "forbidden_kinds": ["pose_override", "teleport", "set_uav_pose", "actor_transform", "keyboard_pose"],
    },
}

FALSE_ACK_STATIC_SOURCES = [
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

FORBIDDEN_RUNTIME_START_TOKENS_IN_RECEIVER = [
    "Common/UdpSocketBuilder.h",
    "Common/UdpSocketReceiver.h",
    "FUdpSocketBuilder",
    "FUdpSocketReceiver",
    "FRunnable",
    "FRunnableThread",
    "FTimerHandle",
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


def build_module_dependency_rows() -> list[dict[str, Any]]:
    text = read_text(BUILD_CS)
    rows = []
    for dep in sorted(REQUIRED_MODULE_DEPENDENCIES):
        rows.append(
            {
                "dependency": dep,
                "declared_in_build_cs": f'"{dep}"' in text,
                "required_for_static_surface": dep in {"Json", "JsonUtilities", "Networking", "Sockets", "Core", "CoreUObject", "Engine"},
            }
        )
    return rows


def collect_symbol_rows() -> list[dict[str, Any]]:
    rows = []
    for symbol, spec in REQUIRED_BUILD_READY_SYMBOLS.items():
        header_text = read_text(spec["header"])
        source_text = read_text(spec["source"])
        rows.append(
            {
                "symbol": symbol,
                "owner": spec["owner"],
                "header": repo(spec["header"]),
                "source": repo(spec["source"]),
                "declared_in_header": symbol in header_text,
                "blueprint_callable_header_surface": symbol in header_text and "UFUNCTION(BlueprintCallable" in header_text,
                "defined_in_source": symbol in source_text,
                "artifact_literal_present": spec["artifact"] in source_text,
                "schema_literal_present": spec["schema"] in source_text,
                "accepted_as_runtime_ack_literal_present": "accepted_as_runtime_ack" in source_text,
                "build_only_gate_ready_static_symbol": True,
                "runtime_ready_now": False,
                "accepted_as_runtime_ack_now": False,
            }
        )
    return rows


def build_schema_rows() -> list[dict[str, Any]]:
    rows = []
    for name, spec in REQUIRED_SCHEMA_ANCHORS.items():
        data = read_json(spec["path"])
        row: dict[str, Any] = {
            "name": name,
            "path": repo(spec["path"]),
            "exists": spec["path"].exists(),
            "schema_matches": data.get("schema") == spec["schema"],
            "runtime_ack_is_required_for_acceptance": False,
        }
        if name == "command_schema":
            row["runtime_ack_is_required_for_acceptance"] = spec["required_runtime_ack_note"] in str(data.get("runtime_ack", ""))
        if name == "echo_schema":
            row["ack_authorities_present"] = all(authority in data.get("ack_authority_values", []) for authority in spec["ack_authorities"])
            row["forbidden_pose_kinds_present"] = all(kind in data.get("forbidden_kinds", []) for kind in spec["forbidden_kinds"])
        rows.append(row)
    return rows


def build_report() -> dict[str, Any]:
    issues: list[str] = []
    required_paths = [
        TASK_PACKET,
        BLOCKER_034,
        RETURN_036,
        EVIDENCE_036,
        COMMAND_SCHEMA,
        ECHO_SCHEMA,
        BUILD_CS,
        SENDER_HEADER,
        SENDER_SOURCE,
        RECEIVER_HEADER,
        RECEIVER_SOURCE,
    ]
    for path in required_paths:
        if not path.exists():
            issues.append(f"missing required path: {repo(path)}")

    task_packet = read_json(TASK_PACKET)
    blocker_034 = read_json(BLOCKER_034)
    return_036 = read_json(RETURN_036)
    evidence_036 = read_json(EVIDENCE_036)

    if task_packet.get("task_class") != "source_static":
        issues.append("037 task packet must remain task_class=source_static")
    if blocker_034.get("preflight_result", {}).get("live_attempt_consumed") is not False:
        issues.append("034 blocker must preserve live_attempt_consumed=false")
    if blocker_034.get("preflight_result", {}).get("runtime_probe_executed") is not False:
        issues.append("034 blocker must preserve runtime_probe_executed=false")
    if return_036.get("status") != "completed":
        issues.append("036 return must be completed before 037 build-readiness classification")
    if return_036.get("implementation_surface_summary", {}).get("runtime_route_ready_now") is not False:
        issues.append("036 return must keep runtime_route_ready_now=false")
    if return_036.get("implementation_surface_summary", {}).get("runtime_ack_leaks_now") != 0:
        issues.append("036 return must keep runtime_ack_leaks_now=0")
    if evidence_036.get("ok") is not True:
        issues.append("036 evidence must be ok=true")
    if evidence_036.get("source_static_implementation_surface_ready") is not True:
        issues.append("036 evidence must mark source_static_implementation_surface_ready=true")
    if evidence_036.get("runtime_route_ready_now") is not False:
        issues.append("036 evidence must keep runtime_route_ready_now=false")
    if evidence_036.get("runtime_ack_leaks_now") != 0:
        issues.append("036 evidence must keep runtime_ack_leaks_now=0")

    module_dependency_rows = build_module_dependency_rows()
    for row in module_dependency_rows:
        if not row["declared_in_build_cs"]:
            issues.append(f"missing Build.cs dependency: {row['dependency']}")

    symbol_rows = collect_symbol_rows()
    for row in symbol_rows:
        if not row["declared_in_header"]:
            issues.append(f"{row['symbol']} missing header declaration")
        if not row["defined_in_source"]:
            issues.append(f"{row['symbol']} missing source definition")
        if not row["artifact_literal_present"]:
            issues.append(f"{row['symbol']} missing artifact literal")
        if not row["schema_literal_present"]:
            issues.append(f"{row['symbol']} missing schema literal")
        if not row["accepted_as_runtime_ack_literal_present"]:
            issues.append(f"{row['symbol']} missing accepted_as_runtime_ack=false boundary")

    schema_rows = build_schema_rows()
    for row in schema_rows:
        if not row["exists"]:
            issues.append(f"missing schema file: {row['path']}")
        if not row["schema_matches"]:
            issues.append(f"schema mismatch: {row['path']}")
        if row["name"] == "command_schema" and not row["runtime_ack_is_required_for_acceptance"]:
            issues.append("command schema must require mosim.ue_command_echo.v1 for accepted state")
        if row["name"] == "echo_schema":
            if not row.get("ack_authorities_present"):
                issues.append("echo schema missing MWORKS/ROS2/MWORKS_ROS2 ack authorities")
            if not row.get("forbidden_pose_kinds_present"):
                issues.append("echo schema missing forbidden pose kinds")

    receiver_text = read_text(RECEIVER_HEADER) + "\n" + read_text(RECEIVER_SOURCE)
    receiver_runtime_hits = sorted(token for token in FORBIDDEN_RUNTIME_START_TOKENS_IN_RECEIVER if token in receiver_text)
    if receiver_runtime_hits:
        issues.append("receiver source-static surface contains runtime-start token(s): " + ", ".join(receiver_runtime_hits))

    if "BuildPendingRequestCaptureJson" in read_text(RECEIVER_SOURCE):
        issues.append("receiver must not synthesize pending request capture")
    if "mosim.ue_command.v1" in receiver_text:
        issues.append("receiver must not parse pending mosim.ue_command.v1")

    source_static_ready = not issues
    next_gate_classification = "build_only_gate_ready" if source_static_ready else "source_static_fix_needed"

    return {
        "schema": "mosim.ue_runtime_echo_build_readiness_surface.v1",
        "ok": source_static_ready,
        "task_id": TASK_ID,
        "scope_classification": "source-static build-readiness checker",
        "next_gate_classification": next_gate_classification,
        "build_only_gate_ready": next_gate_classification == "build_only_gate_ready",
        "source_static_fix_needed": next_gate_classification == "source_static_fix_needed",
        "blocked": False,
        "source_static_build_readiness_ready": source_static_ready,
        "unreal_build_executed": False,
        "unreal_editor_opened": False,
        "ue_runtime_started": False,
        "socket_listener_timer_thread_or_background_loop_started": False,
        "live_command_echo_probe_executed": False,
        "live_attempt_consumed": False,
        "runtime_route_ready_now": False,
        "authoritative_runtime_ack_claimable_now": False,
        "runtime_ack_leaks_now": 0,
        "module_dependency_rows": module_dependency_rows,
        "build_symbol_rows": symbol_rows,
        "schema_anchor_rows": schema_rows,
        "no_live_ack_boundary": {
            "static_sources_rejected_as_runtime_ack": FALSE_ACK_STATIC_SOURCES,
            "build_success_is_not_runtime_ack": True,
            "checker_success_is_not_runtime_ack": True,
            "sender_success_is_not_runtime_ack": True,
            "fixture_echo_is_not_runtime_ack": True,
            "operator_intent_is_not_runtime_ack": True,
            "quadrotor_unreal_state_frame_is_not_runtime_ack": True,
            "accepted_as_runtime_ack_from_static_rows": False,
        },
        "prior_evidence_consumed": {
            "ue_034_status": blocker_034.get("status"),
            "ue_034_live_attempt_consumed": blocker_034.get("preflight_result", {}).get("live_attempt_consumed"),
            "ue_034_runtime_probe_executed": blocker_034.get("preflight_result", {}).get("runtime_probe_executed"),
            "ue_036_status": return_036.get("status"),
            "ue_036_source_static_ready": evidence_036.get("source_static_implementation_surface_ready"),
            "ue_036_runtime_route_ready_now": evidence_036.get("runtime_route_ready_now"),
            "ue_036_runtime_ack_leaks_now": evidence_036.get("runtime_ack_leaks_now"),
        },
        "next_gate_requires": [
            "PMO issues a separate build-only task packet.",
            "The build-only task runs UnrealBuildTool or the project build script only within its own authorization.",
            "Build output is classified as build evidence only, not runtime ack.",
            "A later bounded live probe still requires PMO authorization, authoritative producer identity, pending request capture, authoritative echo capture, match report, no-pose report, false-ack report, and timeout cleanup evidence.",
        ],
        "claim_boundary": [
            "037 proves only source/static UE build-readiness classification for the 036 runtime echo implementation surface.",
            "037 does not run Unreal build, Unreal Editor, PIE, standalone runtime, game window, sockets, listeners, timers, threads, background loops, accepted-state UI, or a live command-echo probe.",
            "037 does not edit UE source, Blueprint, UMG, assets, materials, maps, scene registry, project settings, visual/PBR assets, MWORKS, ROS2, FAST-LIO, planner, controller, Sunray/PBR, Blender, References, CoAgent runtime, Git, Codex App private state, or visible-thread lifecycle.",
            "037 build_only_gate_ready means the next safe UE step may be a separately authorized build-only gate; it is not build success.",
            "037 checker/test/static rows, 036 implementation methods, sender packet construction, fixture rows, operator intent, build success, and quadrotor.unreal_state frames are not live runtime ack.",
            "034 remains the latest bounded live preflight and records live_attempt_consumed=false and runtime_probe_executed=false.",
            "037 does not prove live UE runtime ack, live MWORKS downlink, ROS2 runtime echo, final UI acceptance, planner_ready, controller performance, mission success, or closed_loop.",
        ],
        "issues": issues,
    }


def write_summary(report: dict[str, Any], output_md: Path) -> None:
    lines = [
        "# UE 037 Runtime Echo Build-Readiness Source/Static Gate",
        "",
        f"- ok: {report['ok']}",
        f"- next_gate_classification: {report['next_gate_classification']}",
        f"- source_static_build_readiness_ready: {report['source_static_build_readiness_ready']}",
        f"- unreal_build_executed: {report['unreal_build_executed']}",
        f"- runtime_route_ready_now: {report['runtime_route_ready_now']}",
        f"- live_attempt_consumed: {report['live_attempt_consumed']}",
        "",
        "## Static Symbol Rows",
        "",
    ]
    for row in report["build_symbol_rows"]:
        lines.append(
            f"- {row['symbol']}: declared={row['declared_in_header']}, "
            f"defined={row['defined_in_source']}, artifact={row['artifact_literal_present']}, "
            f"schema={row['schema_literal_present']}"
        )
    lines.extend(["", "## Module Dependencies", ""])
    for row in report["module_dependency_rows"]:
        lines.append(f"- {row['dependency']}: declared={row['declared_in_build_cs']}")
    lines.extend(["", "## Next Gate Requires", ""])
    for item in report["next_gate_requires"]:
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
            "next_gate_classification": report["next_gate_classification"],
            "module_dependency_rows": report["module_dependency_rows"],
            "build_symbol_rows": report["build_symbol_rows"],
            "schema_anchor_rows": report["schema_anchor_rows"],
            "no_live_ack_boundary": report["no_live_ack_boundary"],
        }
        output_matrix.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(text)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
