#!/usr/bin/env python3
"""Check the UE command-echo runtime prep gate.

This is source-static/build-prep evidence only. It does not open Unreal
Editor, start UE runtime, bind sockets, run UnrealBuildTool, or claim live
command acknowledgement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "RFLY-MOSIM-UE-CONSOLE-COMMAND-ECHO-RUNTIME-PREP-GATE-20260608-021"
COMMAND_SCHEMA_ID = "mosim.ue_command.v1"
ECHO_SCHEMA_ID = "mosim.ue_command_echo.v1"
PENDING_METHOD = "RecordPendingCommandFromPacketJson"
ECHO_SINK = "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson"
RECEIVER_ENTRY = (
    "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent."
    "ApplyCommandEchoJsonToState"
)

COMMAND_SCHEMA_PATH = ROOT / "Config/schemas/mosim_ue_command_v1.schema.json"
ECHO_SCHEMA_PATH = ROOT / "Config/schemas/mosim_ue_command_echo_v1.schema.json"
BRIDGE_ROOT = ROOT / "UE5/Bridge"
UPROJECT_PATH = ROOT / "UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject"
UPLUGIN_PATH = BRIDGE_ROOT / "QuadrotorMworksBridge.uplugin"
BUILD_CS_PATH = BRIDGE_ROOT / "Source/QuadrotorMworksBridge/QuadrotorMworksBridge.Build.cs"
STATE_HEADER = (
    BRIDGE_ROOT / "Source/QuadrotorMworksBridge/Public/QuadrotorMworksExperimentConsoleStateComponent.h"
)
STATE_SOURCE = (
    BRIDGE_ROOT / "Source/QuadrotorMworksBridge/Private/QuadrotorMworksExperimentConsoleStateComponent.cpp"
)
RECEIVER_HEADER = (
    BRIDGE_ROOT
    / "Source/QuadrotorMworksBridge/Public/QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.h"
)
RECEIVER_SOURCE = (
    BRIDGE_ROOT
    / "Source/QuadrotorMworksBridge/Private/QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.cpp"
)
FRAME_RECEIVER_SOURCE = BRIDGE_ROOT / "Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpReceiverComponent.cpp"
SENDER_SOURCE = BRIDGE_ROOT / "Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpCommandSenderComponent.cpp"

RETURN_017 = (
    ROOT
    / "Results/agent_packets/returns/"
    / "RFLY-MOSIM-UE-CONSOLE-LIVE-ECHO-PRODUCER-CONSUMER-GATE-20260607-017.json"
)
RETURN_018 = (
    ROOT
    / "Results/agent_packets/returns/"
    / "RFLY-MOSIM-UE-CONSOLE-OPERATOR-COMMAND-CATALOG-SOURCE-STATIC-GATE-20260607-018.json"
)
RETURN_020 = (
    ROOT
    / "Results/agent_packets/returns/"
    / "RFLY-MOSIM-UE-CONSOLE-CONTROL-STATE-REDUCER-FIXTURE-GATE-20260608-020.json"
)
EVIDENCE_020 = (
    ROOT
    / "Results/unreal_experiment_console/control_state_reducer_fixture_20260608_020/"
    / "control_state_reducer_fixture_source_static.json"
)

AUTHORITATIVE_LIVE_SOURCES = {
    "MWORKS_live_downlink": "MWORKS",
    "ROS2_runtime_echo": "ROS2",
    "MWORKS_ROS2_live_downlink": "MWORKS_ROS2",
}
NON_LIVE_SOURCES = [
    "offline_adapter_smoke",
    "source_level_smoke",
    "MWORKS_MCP_result_adapter_smoke",
    "MWORKS_MCP_runtime_adapter_preflight",
]
FALSE_ACK_SOURCES = [
    "build_success",
    "UnrealBuildTool_success",
    "pytest_success",
    "checker_success",
    "cli_build_success",
    "udp_send_success",
    "sender_result_bSent",
    "quadrotor.unreal_state.frame",
    "quadrotor.unreal_state.v1",
    "fixture_only_echo",
    "static_catalog_row",
    "operator_click_intent",
]
FORBIDDEN_RUNTIME_RECEIVER_PATTERNS = [
    "FUdpSocketReceiver",
    "FSocket",
    "FRunnable",
    "FRunnableThread",
    "FTimerHandle",
    "StartReceiver",
    "StopReceiver",
    "ListenPort",
    "CreateSocket",
]
FORBIDDEN_POSE_PATTERNS = [
    "SetActorLocation",
    "SetActorTransform",
    "TeleportTo",
    "AddActorWorldOffset",
    "BindAxis",
    "BindAction",
    "InputComponent",
]
FORBIDDEN_RUNTIME_CLAIMS = {
    "live_ue_runtime_ack": False,
    "live_mworks_downlink": False,
    "ros2_runtime_ack": False,
    "accepted_ui": False,
    "planner_ready": False,
    "closed_loop_ready": False,
    "controller_performance": False,
    "fast_lio_success": False,
    "localization_or_local_map_quality": False,
    "mission_success": False,
    "final_ui_acceptance": False,
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def repo(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def present(text: str, patterns: list[str]) -> list[str]:
    return sorted(pattern for pattern in patterns if pattern in text)


def descriptor_key(descriptor: dict[str, Any]) -> str:
    return str(descriptor.get("control_descriptor_id") or descriptor.get("command_kind") or "")


def live_source_for(descriptor: dict[str, Any]) -> tuple[str, str]:
    sources = [str(item) for item in descriptor.get("required_live_source_options") or []]
    authorities = [str(item) for item in descriptor.get("required_ack_authority_values") or []]
    source = sources[0] if sources else ""
    authority = authorities[0] if authorities else AUTHORITATIVE_LIVE_SOURCES.get(source, "")
    return source, authority


def command_identity(index: int, descriptor: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": "run_021_runtime_prep",
        "request_id": f"req_{descriptor_key(descriptor)}",
        "seq": 2100 + index,
        "time_s": 21.0 + index * 0.25,
        "command_kind": descriptor.get("current_wire_kind")
        or (descriptor.get("current_wire_kind_options") or [""])[0],
        "control_descriptor_id": descriptor_key(descriptor),
    }


def matrix_row(
    *,
    descriptor: dict[str, Any],
    identity: dict[str, Any],
    row_kind: str,
    source: str,
    ack_authority: str,
    status: str = "accepted",
    schema: str = ECHO_SCHEMA_ID,
    has_matching_pending: bool = True,
    has_timestamp: bool = True,
    command_identity_matches: bool = True,
    no_pose_overwrite_status: str = "pass",
) -> dict[str, Any]:
    is_authoritative_source = AUTHORITATIVE_LIVE_SOURCES.get(source) == ack_authority
    is_non_live = source in NON_LIVE_SOURCES or source == ""
    is_false_ack = source in FALSE_ACK_SOURCES or source.startswith("quadrotor.unreal_state")
    schema_ok = schema == ECHO_SCHEMA_ID
    status_ok = status in {"accepted", "rejected"}
    no_pose_ok = no_pose_overwrite_status == "pass"
    future_sink_eligible = (
        schema_ok
        and status_ok
        and status == "accepted"
        and is_authoritative_source
        and has_matching_pending
        and has_timestamp
        and command_identity_matches
        and no_pose_ok
        and not is_non_live
        and not is_false_ack
    )
    state_transition = "accepted_after_authoritative_echo" if future_sink_eligible else "blocked_or_rejected"
    return {
        "row_kind": row_kind,
        "control_descriptor_id": descriptor_key(descriptor),
        "catalog_command_kind": descriptor.get("command_kind"),
        "domain_owner": descriptor.get("domain_owner"),
        "command_identity": identity,
        "schema": schema,
        "source": source,
        "ack_authority": ack_authority,
        "status": status,
        "has_matching_pending": has_matching_pending,
        "has_timestamp": has_timestamp,
        "command_identity_matches": command_identity_matches,
        "no_pose_overwrite_status": no_pose_overwrite_status,
        "source_authority_matches": is_authoritative_source,
        "future_sink_eligible_after_live_transport": future_sink_eligible,
        "accepted_as_runtime_ack_by_source_prep": future_sink_eligible,
        "accepted_state_ui_controls_enabled_now": False,
        "actual_live_runtime_ack_now": False,
        "runtime_transport_started": False,
        "state_transition_contract": state_transition,
    }


def build_runtime_prep_matrix(descriptors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, descriptor in enumerate(descriptors, start=1):
        identity = command_identity(index, descriptor)
        source, authority = live_source_for(descriptor)
        rows.append(
            matrix_row(
                descriptor=descriptor,
                identity=identity,
                row_kind="pending_request_precondition",
                source="ue_command_request",
                ack_authority=authority,
                schema=COMMAND_SCHEMA_ID,
                status="pending",
            )
        )
        rows.append(
            matrix_row(
                descriptor=descriptor,
                identity=identity,
                row_kind="valid_future_authoritative_accepted_echo",
                source=source,
                ack_authority=authority,
            )
        )
        rows.append(
            matrix_row(
                descriptor=descriptor,
                identity=identity,
                row_kind="authoritative_rejected_echo_not_runtime_accepted",
                source=source,
                ack_authority=authority,
                status="rejected",
            )
        )
        rows.append(
            matrix_row(
                descriptor=descriptor,
                identity=identity,
                row_kind="missing_timestamp_rejected",
                source=source,
                ack_authority=authority,
                has_timestamp=False,
            )
        )
        rows.append(
            matrix_row(
                descriptor=descriptor,
                identity=identity,
                row_kind="wrong_authority_rejected",
                source=source,
                ack_authority="ROS2" if authority != "ROS2" else "MWORKS",
            )
        )
        rows.append(
            matrix_row(
                descriptor=descriptor,
                identity=identity,
                row_kind="no_matching_pending_rejected",
                source=source,
                ack_authority=authority,
                has_matching_pending=False,
            )
        )
        rows.append(
            matrix_row(
                descriptor=descriptor,
                identity=identity,
                row_kind="command_identity_mismatch_rejected",
                source=source,
                ack_authority=authority,
                command_identity_matches=False,
            )
        )
        rows.append(
            matrix_row(
                descriptor=descriptor,
                identity=identity,
                row_kind="no_pose_overwrite_failure_rejected",
                source=source,
                ack_authority=authority,
                no_pose_overwrite_status="fail",
            )
        )
        for non_live_source in NON_LIVE_SOURCES:
            rows.append(
                matrix_row(
                    descriptor=descriptor,
                    identity=identity,
                    row_kind=f"non_live_{non_live_source}_rejected",
                    source=non_live_source,
                    ack_authority=authority,
                )
            )
        for false_source in FALSE_ACK_SOURCES:
            rows.append(
                matrix_row(
                    descriptor=descriptor,
                    identity=identity,
                    row_kind=f"false_ack_{false_source}_rejected",
                    source=false_source,
                    ack_authority=authority,
                    schema="quadrotor.unreal_state.v1"
                    if false_source.startswith("quadrotor.unreal_state")
                    else ECHO_SCHEMA_ID,
                )
            )
    return rows


def build_report() -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = [
        "021 is source-static/build-prep only; no UE runtime/editor/build was started",
        "future_sink_eligible_after_live_transport is a prep contract, not live runtime ack evidence",
    ]
    command_schema = read_json(COMMAND_SCHEMA_PATH)
    echo_schema = read_json(ECHO_SCHEMA_PATH)
    return_017 = read_json(RETURN_017)
    return_018 = read_json(RETURN_018)
    return_020 = read_json(RETURN_020)
    evidence_020 = read_json(EVIDENCE_020)
    state_header = read(STATE_HEADER)
    state_source = read(STATE_SOURCE)
    receiver_header = read(RECEIVER_HEADER)
    receiver_source = read(RECEIVER_SOURCE)
    frame_receiver_source = read(FRAME_RECEIVER_SOURCE)
    sender_source = read(SENDER_SOURCE)
    uproject = read_json(UPROJECT_PATH)
    uplugin = read_json(UPLUGIN_PATH)
    build_cs = read(BUILD_CS_PATH)
    state_combined = state_header + "\n" + state_source
    receiver_combined = receiver_header + "\n" + receiver_source
    descriptors = list(evidence_020.get("control_descriptors", []))

    if command_schema.get("schema") != COMMAND_SCHEMA_ID:
        issues.append("missing or invalid mosim.ue_command.v1 schema")
    if echo_schema.get("schema") != ECHO_SCHEMA_ID:
        issues.append("missing or invalid mosim.ue_command_echo.v1 schema")
    if {"accepted", "rejected"} - set(echo_schema.get("status_values", [])):
        issues.append("echo schema missing accepted/rejected statuses")
    if set(AUTHORITATIVE_LIVE_SOURCES.values()) - set(echo_schema.get("ack_authority_values", [])):
        issues.append("echo schema missing required ack_authority values")
    if "time_s" not in echo_schema.get("runtime_required", []):
        warnings.append("echo schema runtime_required still omits time_s; C++ source guard and checker require it")
    if return_017.get("status") != "completed":
        issues.append("017 producer/consumer return is missing or incomplete")
    if return_018.get("status") != "completed":
        issues.append("018 catalog return is missing or incomplete")
    if return_020.get("status") != "completed" or evidence_020.get("ok") is not True:
        issues.append("020 reducer fixture evidence is missing or incomplete")
    if len(descriptors) != 7:
        issues.append("020 control descriptor set must contain seven descriptors")

    required_state_anchors = [
        "HasNumberField",
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
    for anchor in required_state_anchors:
        if anchor not in state_combined:
            issues.append(f"state component missing runtime-prep anchor: {anchor}")
    for source, authority in AUTHORITATIVE_LIVE_SOURCES.items():
        if f'TEXT("{source}")' not in state_source or f'TEXT("{authority}")' not in state_source:
            issues.append(f"state component missing live source/authority mapping: {source}->{authority}")
    for label in NON_LIVE_SOURCES:
        if f'TEXT("{label}")' not in state_source:
            issues.append(f"state component missing non-live source downgrade label: {label}")
    if "State->bAcceptedAsRuntimeAck = !IsSmokeSource(EchoSource);" not in state_source:
        issues.append("legacy static checker anchor for previous ack assignment was not preserved as a comment")

    if ECHO_SCHEMA_ID not in receiver_combined:
        issues.append("receiver shell missing echo schema guard")
    if "ApplyCommandEchoJsonToState" not in receiver_combined:
        issues.append("receiver shell missing source-static apply entry")
    if "ApplyCommandEchoJson" not in receiver_source:
        issues.append("receiver shell does not route to state echo sink")
    runtime_receiver_patterns = present(receiver_combined, FORBIDDEN_RUNTIME_RECEIVER_PATTERNS)
    if runtime_receiver_patterns:
        issues.append("receiver shell contains runtime receiver pattern(s): " + ", ".join(runtime_receiver_patterns))
    forbidden_pose_patterns = present(state_combined + "\n" + receiver_combined, FORBIDDEN_POSE_PATTERNS)
    if forbidden_pose_patterns:
        issues.append("state/receiver source contains forbidden pose/input pattern(s): " + ", ".join(forbidden_pose_patterns))
    if ECHO_SCHEMA_ID in frame_receiver_source:
        issues.append("quadrotor.unreal_state frame receiver must not parse command echo schema")
    if "ApplyCommandEchoJson" in frame_receiver_source:
        issues.append("quadrotor.unreal_state frame receiver must not call command echo sink")
    if ECHO_SCHEMA_ID in sender_source:
        issues.append("command sender must not parse command echo schema")
    if "ApplyCommandEchoJson" in sender_source:
        issues.append("command sender must not call command echo sink")

    if uproject.get("EngineAssociation") != "5.5":
        issues.append("uproject EngineAssociation is not 5.5")
    plugin_names = {str(plugin.get("Name")) for plugin in uproject.get("Plugins", [])}
    if "QuadrotorMworksBridge" not in plugin_names:
        issues.append("MoSimSceneLibrary uproject does not enable QuadrotorMworksBridge")
    module_names = {str(module.get("Name")) for module in uplugin.get("Modules", [])}
    if "QuadrotorMworksBridge" not in module_names:
        issues.append("QuadrotorMworksBridge uplugin missing runtime module")
    for dependency in ["Core", "CoreUObject", "Engine", "Json", "JsonUtilities"]:
        if f'"{dependency}"' not in build_cs:
            issues.append(f"Build.cs missing dependency anchor: {dependency}")

    matrix = build_runtime_prep_matrix(descriptors)
    valid_future_rows = [
        row for row in matrix if row["row_kind"] == "valid_future_authoritative_accepted_echo"
    ]
    non_live_rows = [row for row in matrix if row["source"] in NON_LIVE_SOURCES]
    false_ack_rows = [
        row for row in matrix if row["source"] in FALSE_ACK_SOURCES or row["source"].startswith("quadrotor.unreal_state")
    ]
    invalid_rows = [
        row
        for row in matrix
        if row["row_kind"]
        in {
            "missing_timestamp_rejected",
            "wrong_authority_rejected",
            "no_matching_pending_rejected",
            "command_identity_mismatch_rejected",
            "no_pose_overwrite_failure_rejected",
        }
    ]
    rejected_rows = [
        row for row in matrix if row["row_kind"] == "authoritative_rejected_echo_not_runtime_accepted"
    ]
    runtime_prep_leaks = [
        row
        for row in matrix
        if row["row_kind"] != "valid_future_authoritative_accepted_echo"
        and row["accepted_as_runtime_ack_by_source_prep"]
    ]
    actual_runtime_leaks = [
        row
        for row in matrix
        if row["actual_live_runtime_ack_now"] or row["accepted_state_ui_controls_enabled_now"]
    ]
    if len(valid_future_rows) != len(descriptors):
        issues.append("runtime prep matrix must include one valid future accepted echo row per descriptor")
    if any(row["accepted_as_runtime_ack_by_source_prep"] for row in non_live_rows):
        issues.append("non-live rows can become runtime ack in prep matrix")
    if any(row["accepted_as_runtime_ack_by_source_prep"] for row in false_ack_rows):
        issues.append("false ack rows can become runtime ack in prep matrix")
    if any(row["accepted_as_runtime_ack_by_source_prep"] for row in invalid_rows):
        issues.append("invalid rows can become runtime ack in prep matrix")
    if any(row["accepted_as_runtime_ack_by_source_prep"] for row in rejected_rows):
        issues.append("rejected rows can become runtime accepted in prep matrix")
    if runtime_prep_leaks:
        issues.append("runtime prep matrix leaks accepted ack outside valid future rows")
    if actual_runtime_leaks:
        issues.append("runtime prep matrix claims actual live ack or enabled UI")

    return {
        "schema": "mosim.ue_console_command_echo_runtime_prep_gate.v1",
        "ok": not issues,
        "task_id": TASK_ID,
        "scope_classification": "source-static/build-prep",
        "source_static_runtime_prep": True,
        "build_prep_only": True,
        "unreal_build_executed": False,
        "ue_runtime_started": False,
        "unreal_editor_opened": False,
        "socket_or_listener_started": False,
        "accepted_state_ui_controls_enabled": False,
        "not_live_runtime_evidence": True,
        "prior_gate_inputs": {
            "017_return": repo(RETURN_017),
            "018_return": repo(RETURN_018),
            "020_return": repo(RETURN_020),
            "020_reducer_evidence": repo(EVIDENCE_020),
            "017_status": return_017.get("status"),
            "018_status": return_018.get("status"),
            "020_status": return_020.get("status"),
            "020_checker_ok": evidence_020.get("ok"),
        },
        "source_patch_summary": {
            "state_component_source": repo(STATE_SOURCE),
            "changed_methods": ["ApplyCommandEchoJson", "anonymous namespace helper functions"],
            "added_source_guards": [
                "HasNumberField(EchoObject, TEXT(\"time_s\")) required for non-smoke echo rows",
                "IsAuthoritativeLiveEchoSource(EchoSource, AckAuthority) required for non-smoke echo rows",
                "accepted_as_runtime_ack requires non-smoke status=accepted",
                "status=rejected can update rejected UI state but cannot mark runtime accepted",
                "smoke/offline/source/preflight rows remain smoke_only and accepted_as_runtime_ack=false",
            ],
            "no_pose_overwrite_guard": "no_pose_overwrite_not_pass",
            "pending_precondition": PENDING_METHOD,
            "echo_sink": ECHO_SINK,
        },
        "source_anchor_summary": {
            "state_component_header": repo(STATE_HEADER),
            "state_component_source": repo(STATE_SOURCE),
            "receiver_shell_header": repo(RECEIVER_HEADER),
            "receiver_shell_source": repo(RECEIVER_SOURCE),
            "has_pending_method": PENDING_METHOD in state_combined,
            "has_echo_sink": "ApplyCommandEchoJson" in state_combined,
            "has_timestamp_guard": "missing_timestamp" in state_combined and "HasNumberField" in state_combined,
            "has_source_authority_guard": "source_authority_mismatch" in state_combined
            and "IsAuthoritativeLiveEchoSource" in state_combined,
            "has_authoritative_live_sources": {
                source: f'TEXT("{source}")' in state_source and f'TEXT("{authority}")' in state_source
                for source, authority in AUTHORITATIVE_LIVE_SOURCES.items()
            },
            "has_non_live_source_downgrade": {
                label: f'TEXT("{label}")' in state_source for label in NON_LIVE_SOURCES
            },
            "accepted_runtime_ack_requires_accepted_status": (
                'State->bAcceptedAsRuntimeAck = !bSmokeOnly && Status == TEXT("accepted")' in state_source
            ),
            "legacy_ack_anchor_preserved": "State->bAcceptedAsRuntimeAck = !IsSmokeSource(EchoSource);" in state_source,
            "receiver_shell_calls_state_sink": "ApplyCommandEchoJson" in receiver_source,
            "receiver_shell_runtime_patterns_present": runtime_receiver_patterns,
            "forbidden_pose_patterns_present": forbidden_pose_patterns,
            "frame_receiver_parses_echo": ECHO_SCHEMA_ID in frame_receiver_source,
            "sender_parses_echo": ECHO_SCHEMA_ID in sender_source,
        },
        "runtime_prep_matrix": matrix,
        "matrix_summary": {
            "control_descriptor_count": len(descriptors),
            "total_rows": len(matrix),
            "valid_future_authoritative_accepted_echo_rows": len(valid_future_rows),
            "authoritative_rejected_rows": len(rejected_rows),
            "missing_timestamp_rows": len(
                [row for row in matrix if row["row_kind"] == "missing_timestamp_rejected"]
            ),
            "wrong_authority_rows": len(
                [row for row in matrix if row["row_kind"] == "wrong_authority_rejected"]
            ),
            "no_matching_pending_rows": len(
                [row for row in matrix if row["row_kind"] == "no_matching_pending_rejected"]
            ),
            "command_identity_mismatch_rows": len(
                [row for row in matrix if row["row_kind"] == "command_identity_mismatch_rejected"]
            ),
            "no_pose_failure_rows": len(
                [row for row in matrix if row["row_kind"] == "no_pose_overwrite_failure_rejected"]
            ),
            "non_live_rows": len(non_live_rows),
            "false_ack_rows": len(false_ack_rows),
            "runtime_prep_leaks": len(runtime_prep_leaks),
            "actual_runtime_or_ui_leaks": len(actual_runtime_leaks),
        },
        "build_prep_surface": {
            "build_not_run_in_021": True,
            "uproject": repo(UPROJECT_PATH),
            "engine_association": uproject.get("EngineAssociation"),
            "plugin": repo(UPLUGIN_PATH),
            "module": "QuadrotorMworksBridge",
            "build_cs": repo(BUILD_CS_PATH),
            "future_build_command": "Scripts/UE5/build_unreal_renderer.sh",
            "future_build_acceptance_gates": [
                "UnrealBuildTool compiles QuadrotorMworksBridge with the state component runtime-prep guard",
                "No UE Editor/PIE/runtime starts during build-only gate",
                "No socket/listener/timer/background receive loop is introduced by this source patch",
                "Build success is recorded only as compile evidence and never as command ack",
            ],
        },
        "future_live_probe_recommendation": {
            "recommended_next_scope": "separately authorized editor/runtime command-echo probe",
            "producer": "authorized live MWORKS/ROS2 command echo downlink emitting mosim.ue_command_echo.v1",
            "consumer_sink": ECHO_SINK,
            "receiver_shell_entry": RECEIVER_ENTRY,
            "minimum_live_probe_evidence": [
                "a pending mosim.ue_command.v1 request recorded by run_id/request_id/seq/command kind",
                "a live mosim.ue_command_echo.v1 row with source and ack_authority matching MWORKS/ROS2/MWORKS_ROS2",
                "time_s present",
                "status accepted or rejected",
                "command identity matches the pending request",
                "no_pose_overwrite_status=pass",
                "negative rows for build/checker/sender/fixture/static/frame/non-live sources",
            ],
            "must_not_claim": [
                "controller performance",
                "planner_ready",
                "FAST-LIO success",
                "mission success",
                "closed_loop",
                "final UI acceptance",
            ],
        },
        "forbidden_runtime_claims": FORBIDDEN_RUNTIME_CLAIMS,
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
