#!/usr/bin/env python3
"""Check the UE Experiment Console receiver-shell static contract.

This is a source/static checker only. It does not require or implement a live
socket/UDP/TCP receiver, open Unreal Editor, build Unreal, bind ports, call
MWORKS/ROS2/UE runtime, or prove live command acknowledgement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
COMMAND_SCHEMA_PATH = ROOT / "Config/schemas/mosim_ue_command_v1.schema.json"
ECHO_SCHEMA_PATH = ROOT / "Config/schemas/mosim_ue_command_echo_v1.schema.json"
CONTRACT_010_PATH = (
    ROOT
    / "Results/unreal_experiment_console/source_static_receiver_shell_contract_20260607_010/receiver_shell_contract_design.json"
)
STATE_HEADER = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksExperimentConsoleStateComponent.h"
STATE_SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksExperimentConsoleStateComponent.cpp"
FRAME_RECEIVER_HEADER = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksUdpReceiverComponent.h"
FRAME_RECEIVER_SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpReceiverComponent.cpp"
SENDER_HEADER = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksUdpCommandSenderComponent.h"
SENDER_SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpCommandSenderComponent.cpp"

EXPECTED_COMPONENT_NAME = "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent"
ECHO_SCHEMA = "mosim.ue_command_echo.v1"
COMMAND_SCHEMA = "mosim.ue_command.v1"
STATE_SINK = "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson"
STATE_SINK_METHOD = "ApplyCommandEchoJson"
PENDING_METHOD = "RecordPendingCommandFromPacketJson"
FRAME_SCHEMA_PREFIX = "quadrotor.unreal_state."
NON_LIVE_SOURCES = {
    "offline_adapter_smoke",
    "source_level_smoke",
    "MWORKS_MCP_result_adapter_smoke",
    "MWORKS_MCP_runtime_adapter_preflight",
}
AUTHORITATIVE_LIVE_SOURCES = {
    "MWORKS_live_downlink": "MWORKS",
    "ROS2_runtime_echo": "ROS2",
    "MWORKS_ROS2_live_downlink": "MWORKS_ROS2",
}
FORBIDDEN_ACK_SOURCES = {
    "udp_send_success",
    "sender_result_bSent",
    "quadrotor.unreal_state.v1",
    "quadrotor.unreal_state.frame",
    "fixture_only_007",
    "fixture_only_008",
    "fixture_only_010",
    "fixture_only_011",
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
FORBIDDEN_RUNTIME_CLAIMS = {
    "live_ue_runtime_ack": False,
    "live_mworks_downlink": False,
    "ros2_runtime_ack": False,
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


def source_literal(source_label: str) -> str:
    return f'TEXT("{source_label}")'


def is_future_receiver_implemented(*source_blobs: str) -> bool:
    combined = "\n".join(source_blobs)
    return EXPECTED_COMPONENT_NAME in combined


def matrix_row(
    *,
    row_name: str,
    source: str,
    status: str,
    schema: str = ECHO_SCHEMA,
    ack_authority: str = "MWORKS",
    has_command_id: bool = True,
    has_timestamp: bool = True,
    has_matching_pending: bool = True,
    command_id_matches: bool = True,
    no_pose_overwrite_status: str = "pass",
) -> dict[str, Any]:
    authoritative_source = AUTHORITATIVE_LIVE_SOURCES.get(source) == ack_authority
    is_non_live = source in NON_LIVE_SOURCES
    is_forbidden_source = source in FORBIDDEN_ACK_SOURCES or source.startswith("quadrotor.unreal_state")
    schema_ok = schema == ECHO_SCHEMA
    status_ok = status in {"accepted", "rejected"}
    no_pose_ok = no_pose_overwrite_status == "pass"
    eligible_for_future_receiver_sink = (
        schema_ok
        and status_ok
        and status == "accepted"
        and authoritative_source
        and has_command_id
        and has_timestamp
        and has_matching_pending
        and command_id_matches
        and no_pose_ok
        and not is_non_live
        and not is_forbidden_source
    )
    accepted_as_runtime_ack = eligible_for_future_receiver_sink
    if eligible_for_future_receiver_sink:
        receiver_shell_policy = "future_sink_eligible_after_runtime_receiver_exists"
    elif status == "rejected" and schema_ok and authoritative_source and no_pose_ok:
        receiver_shell_policy = "do_not_mark_runtime_accepted_rejected_echo"
    else:
        receiver_shell_policy = "do_not_sink_as_live_ack"
    return {
        "row_name": row_name,
        "schema": schema,
        "source": source,
        "status": status,
        "ack_authority": ack_authority,
        "authoritative_source": authoritative_source,
        "has_command_id": has_command_id,
        "has_timestamp": has_timestamp,
        "has_matching_pending": has_matching_pending,
        "command_id_matches": command_id_matches,
        "no_pose_overwrite_status": no_pose_overwrite_status,
        "eligible_for_future_receiver_sink": eligible_for_future_receiver_sink,
        "accepted_as_runtime_ack": accepted_as_runtime_ack,
        "receiver_shell_policy": receiver_shell_policy,
        "actual_runtime_receiver_implemented": False,
        "actual_sink_called_by_receiver": False,
    }


def build_fixture_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.append(
        matrix_row(
            row_name="valid_future_mworks_live_echo",
            source="MWORKS_live_downlink",
            status="accepted",
            ack_authority="MWORKS",
        )
    )
    rows.append(
        matrix_row(
            row_name="valid_future_ros2_live_echo",
            source="ROS2_runtime_echo",
            status="accepted",
            ack_authority="ROS2",
        )
    )
    rows.append(
        matrix_row(
            row_name="valid_future_joint_live_echo",
            source="MWORKS_ROS2_live_downlink",
            status="accepted",
            ack_authority="MWORKS_ROS2",
        )
    )
    for source in sorted(NON_LIVE_SOURCES):
        rows.append(matrix_row(row_name=f"non_live_{source}", source=source, status="accepted"))
    for source in sorted(FORBIDDEN_ACK_SOURCES):
        rows.append(matrix_row(row_name=f"forbidden_ack_source_{source}", source=source, status="accepted"))
    rows.extend(
        [
            matrix_row(
                row_name="sender_only_success",
                source="sender_result_bSent",
                status="accepted",
            ),
            matrix_row(
                row_name="quadrotor_unreal_state_frame",
                source="quadrotor.unreal_state.v1",
                status="accepted",
                schema="quadrotor.unreal_state.v1",
            ),
            matrix_row(
                row_name="missing_command_id",
                source="MWORKS_live_downlink",
                status="accepted",
                has_command_id=False,
            ),
            matrix_row(
                row_name="missing_timestamp",
                source="MWORKS_live_downlink",
                status="accepted",
                has_timestamp=False,
            ),
            matrix_row(
                row_name="no_matching_pending",
                source="MWORKS_live_downlink",
                status="accepted",
                has_matching_pending=False,
            ),
            matrix_row(
                row_name="command_id_mismatch",
                source="MWORKS_live_downlink",
                status="accepted",
                command_id_matches=False,
            ),
            matrix_row(
                row_name="no_pose_overwrite_failure",
                source="MWORKS_live_downlink",
                status="accepted",
                no_pose_overwrite_status="fail",
            ),
            matrix_row(
                row_name="authoritative_rejected",
                source="MWORKS_live_downlink",
                status="rejected",
            ),
            matrix_row(
                row_name="wrong_authority_for_source",
                source="ROS2_runtime_echo",
                status="accepted",
                ack_authority="MWORKS",
            ),
        ]
    )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default="")
    args = parser.parse_args()

    issues: list[str] = []
    warnings = [
        "source/static receiver-shell checker only; runtime receiver source is intentionally not implemented",
        "future_sink_eligible_after_runtime_receiver_exists is contract eligibility, not live runtime evidence",
    ]

    command_schema = read_json(COMMAND_SCHEMA_PATH)
    echo_schema = read_json(ECHO_SCHEMA_PATH)
    contract_010 = read_json(CONTRACT_010_PATH)
    state_header = read(STATE_HEADER)
    state_source = read(STATE_SOURCE)
    frame_header = read(FRAME_RECEIVER_HEADER)
    frame_source = read(FRAME_RECEIVER_SOURCE)
    sender_header = read(SENDER_HEADER)
    sender_source = read(SENDER_SOURCE)
    state_combined = state_header + "\n" + state_source
    frame_combined = frame_header + "\n" + frame_source
    sender_combined = sender_header + "\n" + sender_source

    receiver_shell_cpp_implemented = is_future_receiver_implemented(
        state_combined,
        frame_combined,
        sender_combined,
    )
    runtime_receiver_implemented = receiver_shell_cpp_implemented

    if not command_schema:
        issues.append("missing mosim_ue_command_v1 schema")
    elif command_schema.get("runtime_ack") != "Accepted state must be shown only after a mosim.ue_command_echo.v1 row from MWORKS, ROS2, or MWORKS_ROS2 authority.":
        issues.append("command schema runtime_ack boundary changed unexpectedly")
    if not echo_schema:
        issues.append("missing mosim_ue_command_echo_v1 schema")
    else:
        if echo_schema.get("schema") != ECHO_SCHEMA:
            issues.append("echo schema is not mosim.ue_command_echo.v1")
        if "time_s" not in echo_schema.get("runtime_required", []):
            warnings.append("echo schema runtime_required does not explicitly list time_s; 012 fixture still requires timestamp before future receiver sink")
        if {"accepted", "rejected"} - set(echo_schema.get("status_values", [])):
            issues.append("echo schema must include accepted and rejected status values")
        if set(AUTHORITATIVE_LIVE_SOURCES.values()) - set(echo_schema.get("ack_authority_values", [])):
            issues.append("echo schema missing required ack_authority values")
    if not contract_010:
        issues.append("missing 010 receiver shell contract design evidence")

    future_contract = contract_010.get("future_receiver_shell_contract", {})
    if contract_010.get("future_receiver_shell_contract", {}).get("recommended_component_name") != EXPECTED_COMPONENT_NAME:
        # Older 010 evidence stores the recommended component at the return packet level in
        # some fields; accept the JSON if the component name appears anywhere.
        if EXPECTED_COMPONENT_NAME not in json.dumps(contract_010, ensure_ascii=False):
            issues.append("010 contract missing expected future receiver component name")
    if ECHO_SCHEMA not in json.dumps(future_contract, ensure_ascii=False):
        issues.append("010 contract missing mosim.ue_command_echo.v1 future input schema")
    if STATE_SINK_METHOD not in json.dumps(future_contract, ensure_ascii=False):
        issues.append("010 contract missing ApplyCommandEchoJson sink")
    for forbidden in [
        "quadrotor.unreal_state.* frame/status downlink",
        "UDP send success",
        "007 disabled-state fixture rows",
        "008 future-live fixture rows",
        "offline/source/preflight smoke rows",
    ]:
        if forbidden not in json.dumps(future_contract, ensure_ascii=False):
            issues.append(f"010 contract missing forbidden ack source: {forbidden}")
    for source in sorted(NON_LIVE_SOURCES):
        if source not in json.dumps(future_contract, ensure_ascii=False):
            issues.append(f"010 contract missing non-live source label: {source}")
        if source_literal(source) not in state_source:
            issues.append(f"state component no longer downgrades non-live source label: {source}")
    for source, authority in AUTHORITATIVE_LIVE_SOURCES.items():
        if source not in json.dumps(future_contract, ensure_ascii=False) or authority not in json.dumps(future_contract, ensure_ascii=False):
            issues.append(f"010 contract missing authoritative live source mapping: {source}->{authority}")

    if STATE_SINK_METHOD not in state_combined:
        issues.append("state component missing ApplyCommandEchoJson sink")
    if PENDING_METHOD not in state_combined:
        issues.append("state component missing RecordPendingCommandFromPacketJson pending source")
    if ECHO_SCHEMA not in state_combined:
        issues.append("state component missing mosim.ue_command_echo.v1 schema guard")
    if COMMAND_SCHEMA not in state_combined:
        issues.append("state component missing mosim.ue_command.v1 pending schema guard")
    if FRAME_SCHEMA_PREFIX not in frame_source:
        issues.append("existing UDP receiver no longer has quadrotor.unreal_state.* frame guard")
    if "FUdpSocketReceiver" not in frame_combined:
        issues.append("existing UDP receiver source anchor no longer uses FUdpSocketReceiver")
    if ECHO_SCHEMA in frame_combined:
        issues.append("frame/status UDP receiver must not parse mosim.ue_command_echo.v1")
    if STATE_SINK_METHOD in frame_combined:
        issues.append("frame/status UDP receiver must not call ApplyCommandEchoJson")
    if COMMAND_SCHEMA not in sender_combined:
        issues.append("command sender missing mosim.ue_command.v1 source anchor")
    if ECHO_SCHEMA in sender_combined:
        issues.append("command sender must not parse mosim.ue_command_echo.v1")
    if STATE_SINK_METHOD in sender_combined:
        issues.append("command sender must not call ApplyCommandEchoJson")
    if "Result.bSent" not in sender_source:
        issues.append("command sender source no longer exposes Result.bSent send-success anchor for negative ack check")
    for pattern in sorted(FORBIDDEN_POSE_PATTERNS):
        if pattern in state_combined:
            issues.append(f"state component must not expose Actor/input pose route: {pattern}")

    matrix = build_fixture_matrix()
    eligible_rows = [row for row in matrix if row["eligible_for_future_receiver_sink"]]
    non_live_rows = [row for row in matrix if row["source"] in NON_LIVE_SOURCES]
    forbidden_rows = [
        row
        for row in matrix
        if row["source"] in FORBIDDEN_ACK_SOURCES or str(row["source"]).startswith("quadrotor.unreal_state")
    ]
    invalid_rows = [
        row
        for row in matrix
        if row["row_name"]
        in {
            "missing_command_id",
            "missing_timestamp",
            "no_matching_pending",
            "command_id_mismatch",
            "no_pose_overwrite_failure",
            "wrong_authority_for_source",
        }
    ]
    rejected_rows = [row for row in matrix if row["status"] == "rejected"]
    runtime_ack_leaks = [
        row
        for row in matrix
        if not row["row_name"].startswith("valid_future_") and row["accepted_as_runtime_ack"]
    ]
    actual_receiver_sink_leaks = [
        row
        for row in matrix
        if row["actual_runtime_receiver_implemented"] or row["actual_sink_called_by_receiver"]
    ]

    if len(eligible_rows) != len(AUTHORITATIVE_LIVE_SOURCES):
        issues.append("fixture matrix must have exactly one future eligible row per authoritative live source")
    if any(row["accepted_as_runtime_ack"] for row in non_live_rows):
        issues.append("non-live source rows can become runtime ack")
    if any(row["accepted_as_runtime_ack"] for row in forbidden_rows):
        issues.append("forbidden ack source rows can become runtime ack")
    if any(row["accepted_as_runtime_ack"] for row in invalid_rows):
        issues.append("invalid future live rows can become runtime ack")
    if any(row["accepted_as_runtime_ack"] for row in rejected_rows):
        issues.append("rejected authoritative rows can become runtime ack")
    if runtime_ack_leaks:
        issues.append("fixture matrix leaks runtime ack outside valid future rows")
    if actual_receiver_sink_leaks:
        issues.append("012 checker must not report actual runtime receiver or sink invocation")
    if receiver_shell_cpp_implemented:
        issues.append("future receiver C++ shell appears implemented, but 012 is checker-only and must not validate live receiver implementation")

    report = {
        "schema": "mosim.ue_console_receiver_shell_static_contract.v1",
        "ok": not issues,
        "checker_only_contract": True,
        "receiver_shell_cpp_implemented": receiver_shell_cpp_implemented,
        "runtime_receiver_implemented": runtime_receiver_implemented,
        "safe_to_implement_runtime_receiver_next": False,
        "ui_accepted_state_controls_enabled": False,
        "not_live_runtime_evidence": True,
        "future_receiver_shell_contract": {
            "recommended_component_name": EXPECTED_COMPONENT_NAME,
            "input_schema": ECHO_SCHEMA,
            "single_state_sink": STATE_SINK,
            "pending_precondition": f"matching request recorded by {PENDING_METHOD}",
            "must_remain_separate_from": [
                "UQuadrotorMworksUdpReceiverComponent",
                "UQuadrotorMworksUdpCommandSenderComponent",
                "Blueprint/UMG-only logic",
            ],
            "authoritative_live_sources_for_future_sink": AUTHORITATIVE_LIVE_SOURCES,
            "non_live_source_labels": sorted(NON_LIVE_SOURCES),
            "forbidden_ack_sources": sorted(FORBIDDEN_ACK_SOURCES),
            "non_live_policy": "quality_status=smoke_only and accepted_as_runtime_ack=false",
        },
        "source_anchor_summary": {
            "state_component": {
                "header": STATE_HEADER.relative_to(ROOT).as_posix(),
                "source": STATE_SOURCE.relative_to(ROOT).as_posix(),
                "has_pending_method": PENDING_METHOD in state_combined,
                "has_echo_sink": STATE_SINK_METHOD in state_combined,
                "has_echo_schema_guard": ECHO_SCHEMA in state_combined,
                "has_command_schema_guard": COMMAND_SCHEMA in state_combined,
                "non_live_source_labels_covered": sorted(
                    source for source in NON_LIVE_SOURCES if source_literal(source) in state_source
                ),
                "forbidden_pose_patterns_present": sorted(pattern for pattern in FORBIDDEN_POSE_PATTERNS if pattern in state_combined),
            },
            "frame_status_receiver": {
                "header": FRAME_RECEIVER_HEADER.relative_to(ROOT).as_posix(),
                "source": FRAME_RECEIVER_SOURCE.relative_to(ROOT).as_posix(),
                "role": "quadrotor.unreal_state frame/status receiver only",
                "has_frame_schema_guard": FRAME_SCHEMA_PREFIX in frame_source,
                "uses_fudp_socket_receiver": "FUdpSocketReceiver" in frame_combined,
                "parses_command_echo_schema": ECHO_SCHEMA in frame_combined,
                "calls_echo_sink": STATE_SINK_METHOD in frame_combined,
            },
            "command_sender": {
                "header": SENDER_HEADER.relative_to(ROOT).as_posix(),
                "source": SENDER_SOURCE.relative_to(ROOT).as_posix(),
                "role": "mosim.ue_command.v1 sender only",
                "has_command_schema": COMMAND_SCHEMA in sender_combined,
                "has_send_success_anchor": "Result.bSent" in sender_source,
                "send_success_is_ack": False,
                "parses_command_echo_schema": ECHO_SCHEMA in sender_combined,
                "calls_echo_sink": STATE_SINK_METHOD in sender_combined,
            },
        },
        "fixture_matrix": matrix,
        "matrix_summary": {
            "total_rows": len(matrix),
            "future_authoritative_live_eligible_rows": len(eligible_rows),
            "non_live_rows": len(non_live_rows),
            "forbidden_ack_source_rows": len(forbidden_rows),
            "invalid_live_rows": len(invalid_rows),
            "rejected_rows": len(rejected_rows),
            "runtime_ack_leaks": len(runtime_ack_leaks),
            "actual_receiver_sink_leaks": len(actual_receiver_sink_leaks),
        },
        "forbidden_runtime_claims": FORBIDDEN_RUNTIME_CLAIMS,
        "issues": issues,
        "warnings": warnings,
    }

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
