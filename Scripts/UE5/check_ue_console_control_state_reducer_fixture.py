#!/usr/bin/env python3
"""Check UE Experiment Console control-state reducer fixture contract.

Source/static only. This checker defines the reducer matrix future UI code must
obey; it does not open or build Unreal, implement UI, bind transport, or claim
live command acknowledgement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "RFLY-MOSIM-UE-CONSOLE-CONTROL-STATE-REDUCER-FIXTURE-GATE-20260608-020"
UI_BINDING_GATE_ID = "RFLY-MOSIM-UE-CONSOLE-UI-BINDING-CATALOG-TO-CONTROL-PREFLIGHT-20260607-019"
LIVE_ECHO_GATE_ID = "RFLY-MOSIM-UE-CONSOLE-LIVE-ECHO-PRODUCER-CONSUMER-GATE-20260607-017"
COMMAND_SCHEMA_ID = "mosim.ue_command.v1"
ECHO_SCHEMA_ID = "mosim.ue_command_echo.v1"
STATE_PENDING_METHOD = "RecordPendingCommandFromPacketJson"
STATE_ECHO_SINK = "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson"

UI_BINDING_EVIDENCE = (
    ROOT
    / "Results/unreal_experiment_console/ui_binding_catalog_to_control_20260607_019/"
    / "ui_binding_preflight_source_static.json"
)
UI_BINDING_RETURN = (
    ROOT
    / "Results/agent_packets/returns/"
    / "RFLY-MOSIM-UE-CONSOLE-UI-BINDING-CATALOG-TO-CONTROL-PREFLIGHT-20260607-019.json"
)
COMMAND_SCHEMA_PATH = ROOT / "Config/schemas/mosim_ue_command_v1.schema.json"
ECHO_SCHEMA_PATH = ROOT / "Config/schemas/mosim_ue_command_echo_v1.schema.json"
BRIDGE_SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge"
STATE_HEADER = BRIDGE_SOURCE / "Public/QuadrotorMworksExperimentConsoleStateComponent.h"
STATE_SOURCE = (
    BRIDGE_SOURCE
    / ("Pri" + "vate")
    / "QuadrotorMworksExperimentConsoleStateComponent.cpp"
)

REQUIRED_CATALOG_KINDS = {
    "motor_fault.inject_or_clear",
    "disturbance.wind.set_or_clear",
    "controller.switch",
    "planner.switch",
    "scene_map.switch",
    "experiment.run_control",
    "manual_review.request",
}
REQUIRED_ROW_KINDS = {
    "initial_disabled",
    "pending_from_matching_command",
    "accepted_from_authoritative_echo",
    "rejected_from_authoritative_echo",
    "stale_echo_rejected",
    "mismatched_echo_rejected",
    "false_ack_rejected",
}
FALSE_ACK_SOURCES = [
    "build_success",
    "UnrealBuildTool_success",
    "pytest_success",
    "checker_success",
    "udp_send_success",
    "sender_result_bSent",
    "quadrotor.unreal_state.frame",
    "quadrotor.unreal_state.v1",
    "fixture_only_echo",
    "static_catalog_row",
    "operator_click_intent",
    "offline_adapter_smoke",
    "source_level_smoke",
    "MWORKS_MCP_result_adapter_smoke",
    "MWORKS_MCP_runtime_adapter_preflight",
]
AUTH_SOURCE_BY_AUTHORITY = {
    "MWORKS": "MWORKS_live_downlink",
    "ROS2": "ROS2_runtime_echo",
    "MWORKS_ROS2": "MWORKS_ROS2_live_downlink",
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


def repo(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_019_descriptors() -> list[dict[str, Any]]:
    return list(read_json(UI_BINDING_EVIDENCE).get("control_descriptors", []))


def descriptor_wire_kinds(descriptor: dict[str, Any]) -> list[str]:
    current = descriptor.get("current_wire_kind")
    if current:
        return [str(current)]
    return [str(item) for item in descriptor.get("current_wire_kind_options") or []]


def first_authority(descriptor: dict[str, Any]) -> str:
    values = descriptor.get("required_ack_authority_values") or []
    return str(values[0]) if values else ""


def authoritative_source(descriptor: dict[str, Any]) -> str:
    values = descriptor.get("required_live_source_options") or []
    if values:
        return str(values[0])
    return AUTH_SOURCE_BY_AUTHORITY.get(first_authority(descriptor), "")


def identity_for(index: int, descriptor: dict[str, Any]) -> dict[str, Any]:
    wire_kinds = descriptor_wire_kinds(descriptor)
    return {
        "run_id": "run_020_control_reducer_fixture",
        "request_id": f"req_{descriptor['control_descriptor_id']}",
        "seq": 2000 + index,
        "time_s": 20.0 + index * 0.25,
        "catalog_command_kind": descriptor["command_kind"],
        "control_descriptor_id": descriptor["control_descriptor_id"],
        "command_wire_kind": wire_kinds[0] if wire_kinds else "",
        "allowed_command_wire_kinds": wire_kinds,
    }


def common_row(
    *,
    row_kind: str,
    descriptor: dict[str, Any],
    identity: dict[str, Any],
    state_after: str,
    transition_applied: bool,
    reject_reason: str = "",
) -> dict[str, Any]:
    return {
        "row_kind": row_kind,
        "catalog_command_kind": identity["catalog_command_kind"],
        "control_descriptor_id": identity["control_descriptor_id"],
        "domain_owner": descriptor["domain_owner"],
        "required_ack_authority": first_authority(descriptor),
        "command_identity": {
            "run_id": identity["run_id"],
            "request_id": identity["request_id"],
            "seq": identity["seq"],
            "time_s": identity["time_s"],
            "command_wire_kind": identity["command_wire_kind"],
            "allowed_command_wire_kinds": identity["allowed_command_wire_kinds"],
            "control_descriptor_id": identity["control_descriptor_id"],
        },
        "state_after": state_after,
        "transition_applied": transition_applied,
        "reject_reason": reject_reason,
        "quality_status": "source_static_reducer_fixture",
        "actual_live_runtime_ack": False,
        "accepted_as_live_runtime_ack_now": False,
        "accepted_state_ui_controls_enabled_now": False,
        "not_live_runtime_evidence": True,
        "control_enabled_now": False,
    }


def build_rows_for_descriptor(index: int, descriptor: dict[str, Any]) -> list[dict[str, Any]]:
    identity = identity_for(index, descriptor)
    authority = first_authority(descriptor)
    source = authoritative_source(descriptor)
    initial = common_row(
        row_kind="initial_disabled",
        descriptor=descriptor,
        identity=identity,
        state_after="disabled",
        transition_applied=False,
    )
    initial.update({"input_schema": "", "input_provenance": "none", "pending_created": False})
    pending = common_row(
        row_kind="pending_from_matching_command",
        descriptor=descriptor,
        identity=identity,
        state_after="pending",
        transition_applied=True,
    )
    pending.update(
        {
            "input_schema": COMMAND_SCHEMA_ID,
            "input_provenance": "UE command request",
            "requested_by": "ue_experiment_console",
            "pending_source_method": STATE_PENDING_METHOD,
            "pending_created": True,
            "request_matches_descriptor": True,
            "request_matches_command_identity": True,
            "quality_status": "pending_no_runtime_echo",
        }
    )
    accepted = common_row(
        row_kind="accepted_from_authoritative_echo",
        descriptor=descriptor,
        identity=identity,
        state_after="accepted",
        transition_applied=True,
    )
    accepted.update(
        {
            "input_schema": ECHO_SCHEMA_ID,
            "input_provenance": "authoritative command echo fixture",
            "echo_source": source,
            "ack_authority": authority,
            "status": "accepted",
            "source_authoritative_for_required_ack": True,
            "matches_pending_request": True,
            "matches_command_identity": True,
            "stale_or_mismatched": False,
            "no_pose_overwrite_status": "pass",
            "echo_sink": STATE_ECHO_SINK,
            "future_authoritative_echo_state": "accepted",
            "future_ui_state_if_live_task_authorized": "accepted_after_authoritative_echo",
            "future_accepted_state_eligible": True,
        }
    )
    rejected = common_row(
        row_kind="rejected_from_authoritative_echo",
        descriptor=descriptor,
        identity=identity,
        state_after="rejected",
        transition_applied=True,
    )
    rejected.update(
        {
            "input_schema": ECHO_SCHEMA_ID,
            "input_provenance": "authoritative command echo fixture",
            "echo_source": source,
            "ack_authority": authority,
            "status": "rejected",
            "source_authoritative_for_required_ack": True,
            "matches_pending_request": True,
            "matches_command_identity": True,
            "stale_or_mismatched": False,
            "no_pose_overwrite_status": "pass",
            "echo_sink": STATE_ECHO_SINK,
            "future_authoritative_echo_state": "rejected",
            "future_accepted_state_eligible": False,
        }
    )
    stale = common_row(
        row_kind="stale_echo_rejected",
        descriptor=descriptor,
        identity=identity,
        state_after="pending",
        transition_applied=False,
        reject_reason="stale_or_seq_mismatch",
    )
    stale.update(
        {
            "input_schema": ECHO_SCHEMA_ID,
            "input_provenance": "authoritative but stale command echo fixture",
            "echo_source": source,
            "ack_authority": authority,
            "status": "accepted",
            "source_authoritative_for_required_ack": True,
            "matches_pending_request": True,
            "matches_command_identity": False,
            "stale_or_mismatched": True,
            "echo_seq": identity["seq"] - 1,
            "pending_seq": identity["seq"],
            "echo_time_s": identity["time_s"] - 5.0,
            "pending_time_s": identity["time_s"],
            "no_pose_overwrite_status": "pass",
            "future_authoritative_echo_state": "rejected_by_reducer",
            "future_accepted_state_eligible": False,
        }
    )
    mismatch = common_row(
        row_kind="mismatched_echo_rejected",
        descriptor=descriptor,
        identity=identity,
        state_after="pending",
        transition_applied=False,
        reject_reason="request_id_or_command_identity_mismatch",
    )
    mismatch.update(
        {
            "input_schema": ECHO_SCHEMA_ID,
            "input_provenance": "authoritative but mismatched command echo fixture",
            "echo_source": source,
            "ack_authority": authority,
            "status": "accepted",
            "source_authoritative_for_required_ack": True,
            "matches_pending_request": False,
            "matches_command_identity": False,
            "stale_or_mismatched": True,
            "echo_request_id": f"{identity['request_id']}_other",
            "pending_request_id": identity["request_id"],
            "echo_control_descriptor_id": f"{identity['control_descriptor_id']}_other",
            "pending_control_descriptor_id": identity["control_descriptor_id"],
            "echo_command_wire_kind": "sensor_mode"
            if identity["command_wire_kind"] != "sensor_mode"
            else "recording",
            "pending_command_wire_kind": identity["command_wire_kind"],
            "no_pose_overwrite_status": "pass",
            "future_authoritative_echo_state": "rejected_by_reducer",
            "future_accepted_state_eligible": False,
        }
    )
    false_ack = common_row(
        row_kind="false_ack_rejected",
        descriptor=descriptor,
        identity=identity,
        state_after="disabled_or_pending",
        transition_applied=False,
        reject_reason="false_ack_source_not_authoritative_command_echo",
    )
    false_ack.update(
        {
            "input_schema": "mixed_false_ack_sources",
            "input_provenance": "non-authoritative false ack sources",
            "false_ack_sources": [
                {
                    "source": source_name,
                    "is_authoritative_echo": False,
                    "can_create_pending": False,
                    "can_accept_or_reject": False,
                    "accepted_as_live_runtime_ack_now": False,
                    "accepted_state_ui_controls_enabled_now": False,
                }
                for source_name in FALSE_ACK_SOURCES
            ],
            "future_authoritative_echo_state": "rejected_by_reducer",
            "future_accepted_state_eligible": False,
        }
    )
    return [initial, pending, accepted, rejected, stale, mismatch, false_ack]


def build_fixture_matrix(descriptors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matrix: list[dict[str, Any]] = []
    for index, descriptor in enumerate(descriptors, start=1):
        matrix.extend(build_rows_for_descriptor(index, descriptor))
    return matrix


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default="")
    args = parser.parse_args()
    issues: list[str] = []
    warnings = [
        "source-static reducer fixture only; no UE runtime ack or accepted UI is claimed",
        "future UI implementation must still be authorized separately and consume real live echo evidence",
    ]
    descriptors = load_019_descriptors()
    command_schema = read_json(COMMAND_SCHEMA_PATH)
    echo_schema = read_json(ECHO_SCHEMA_PATH)
    ui_binding_evidence = read_json(UI_BINDING_EVIDENCE)
    ui_binding_return = read_json(UI_BINDING_RETURN)
    state_text = read(STATE_HEADER) + "\n" + read(STATE_SOURCE)
    matrix = build_fixture_matrix(descriptors)
    descriptor_kinds = {str(item.get("command_kind")) for item in descriptors}
    descriptor_ids = [str(item.get("control_descriptor_id")) for item in descriptors]
    allowed_wire_kinds = set(command_schema.get("command", {}).get("allowed_kinds", []))
    forbidden_wire_kinds = set(command_schema.get("command", {}).get("forbidden_kinds", []))
    echo_status_values = set(echo_schema.get("status_values", []))
    echo_authorities = set(echo_schema.get("ack_authority_values", []))

    if command_schema.get("schema") != COMMAND_SCHEMA_ID:
        issues.append("missing or invalid mosim.ue_command.v1 schema")
    if echo_schema.get("schema") != ECHO_SCHEMA_ID:
        issues.append("missing or invalid mosim.ue_command_echo.v1 schema")
    if {"accepted", "rejected"} - echo_status_values:
        issues.append("echo schema missing accepted/rejected statuses")
    if {"MWORKS", "ROS2", "MWORKS_ROS2"} - echo_authorities:
        issues.append("echo schema missing required ack authority values")
    if ui_binding_evidence.get("ok") is not True:
        issues.append("019 UI binding evidence is missing or not ok=true")
    if ui_binding_return.get("status") != "completed":
        issues.append("019 UI binding return is missing or not completed")
    if descriptor_kinds != REQUIRED_CATALOG_KINDS:
        issues.append("019 descriptors do not cover the required seven control kinds")
    if len(descriptors) != 7:
        issues.append("020 requires exactly seven control descriptors")
    if len(descriptor_ids) != len(set(descriptor_ids)):
        issues.append("control_descriptor_id values must be unique")

    for required_text in [
        STATE_PENDING_METHOD,
        "ApplyCommandEchoJson",
        COMMAND_SCHEMA_ID,
        ECHO_SCHEMA_ID,
        "unsupported_echo_schema",
        "unsupported_echo_status",
        "no_pose_overwrite_not_pass",
        "no_matching_command_request",
        "seq_mismatch",
        "command_kind_mismatch",
        "pending_no_runtime_echo",
        "smoke_only",
    ]:
        if required_text not in state_text:
            issues.append(f"state component missing source anchor: {required_text}")

    for descriptor in descriptors:
        kind = str(descriptor.get("command_kind"))
        if descriptor.get("default_state") != "disabled_pending_authoritative_echo":
            issues.append(f"{kind} must keep disabled_pending_authoritative_echo default")
        if descriptor.get("control_enabled_now") is not False:
            issues.append(f"{kind} control_enabled_now must be false")
        if descriptor.get("accepted_state_allowed_now") is not False:
            issues.append(f"{kind} accepted_state_allowed_now must be false")
        if descriptor.get("source_static_descriptor_only") is not True:
            issues.append(f"{kind} must remain source_static_descriptor_only")
        if descriptor.get("not_live_runtime_evidence") is not True:
            issues.append(f"{kind} must remain not_live_runtime_evidence")
        if not first_authority(descriptor):
            issues.append(f"{kind} missing required ack authority")
        if not authoritative_source(descriptor):
            issues.append(f"{kind} missing authoritative source option")
        for wire_kind in descriptor_wire_kinds(descriptor):
            if wire_kind not in allowed_wire_kinds:
                issues.append(f"{kind} maps to unsupported command wire kind {wire_kind}")
            if wire_kind in forbidden_wire_kinds:
                issues.append(f"{kind} maps to forbidden command wire kind {wire_kind}")

    rows_by_descriptor: dict[str, list[dict[str, Any]]] = {}
    for row in matrix:
        rows_by_descriptor.setdefault(str(row["control_descriptor_id"]), []).append(row)
    if set(rows_by_descriptor) != set(descriptor_ids):
        issues.append("fixture matrix does not cover every control descriptor id")
    future_accepted_rows = [row for row in matrix if row["row_kind"] == "accepted_from_authoritative_echo"]
    future_rejected_rows = [row for row in matrix if row["row_kind"] == "rejected_from_authoritative_echo"]
    stale_rows = [row for row in matrix if row["row_kind"] == "stale_echo_rejected"]
    mismatch_rows = [row for row in matrix if row["row_kind"] == "mismatched_echo_rejected"]
    false_ack_rows = [row for row in matrix if row["row_kind"] == "false_ack_rejected"]
    runtime_ack_now_leaks = [
        row
        for row in matrix
        if row.get("accepted_as_live_runtime_ack_now") is not False
        or row.get("actual_live_runtime_ack") is not False
        or row.get("accepted_state_ui_controls_enabled_now") is not False
    ]
    for descriptor_id, rows in rows_by_descriptor.items():
        row_kinds = {str(row.get("row_kind")) for row in rows}
        if row_kinds != REQUIRED_ROW_KINDS:
            issues.append(f"{descriptor_id} missing row kind coverage")
        pending_rows = [row for row in rows if row["row_kind"] == "pending_from_matching_command"]
        if len(pending_rows) != 1 or pending_rows[0].get("input_schema") != COMMAND_SCHEMA_ID:
            issues.append(f"{descriptor_id} pending must come from matching mosim.ue_command.v1 request")
        for row in rows:
            if row["row_kind"] in {"accepted_from_authoritative_echo", "rejected_from_authoritative_echo"}:
                if row.get("input_schema") != ECHO_SCHEMA_ID:
                    issues.append(f"{descriptor_id} accepted/rejected row must use mosim.ue_command_echo.v1")
                if row.get("source_authoritative_for_required_ack") is not True:
                    issues.append(f"{descriptor_id} accepted/rejected row must use authoritative source")
                if row.get("matches_pending_request") is not True:
                    issues.append(f"{descriptor_id} accepted/rejected row must match pending request")
                if row.get("matches_command_identity") is not True:
                    issues.append(f"{descriptor_id} accepted/rejected row must match command identity")
                if row.get("no_pose_overwrite_status") != "pass":
                    issues.append(f"{descriptor_id} accepted/rejected row must preserve no_pose_overwrite_status=pass")
            if row["row_kind"] == "stale_echo_rejected":
                if row.get("transition_applied") is not False or row.get("state_after") != "pending":
                    issues.append(f"{descriptor_id} stale echo must be rejected and remain pending")
            if row["row_kind"] == "mismatched_echo_rejected":
                if row.get("transition_applied") is not False or row.get("matches_pending_request") is not False:
                    issues.append(f"{descriptor_id} mismatched echo must be rejected")
            if row["row_kind"] == "false_ack_rejected":
                sources = {case["source"] for case in row.get("false_ack_sources", [])}
                if set(FALSE_ACK_SOURCES) - sources:
                    issues.append(f"{descriptor_id} false-ack row missing required false sources")
                leaks = [
                    case
                    for case in row.get("false_ack_sources", [])
                    if case.get("can_create_pending")
                    or case.get("can_accept_or_reject")
                    or case.get("accepted_as_live_runtime_ack_now")
                    or case.get("accepted_state_ui_controls_enabled_now")
                ]
                if leaks:
                    issues.append(f"{descriptor_id} false-ack source can drive reducer state")
    if len(future_accepted_rows) != 7:
        issues.append("matrix must include one accepted authoritative echo row per descriptor")
    if len(future_rejected_rows) != 7:
        issues.append("matrix must include one rejected authoritative echo row per descriptor")
    if len(stale_rows) != 7 or len(mismatch_rows) != 7:
        issues.append("matrix must include stale and mismatched rejection rows for every descriptor")
    if len(false_ack_rows) != 7:
        issues.append("matrix must include false-ack rejection rows for every descriptor")
    if runtime_ack_now_leaks:
        issues.append("source-static matrix leaked live runtime ack or accepted UI state")

    report = {
        "schema": "mosim.ue_console_control_state_reducer_fixture.v1",
        "ok": not issues,
        "task_id": TASK_ID,
        "scope_classification": "source-static",
        "checker_only_contract": True,
        "source_static_reducer_fixture_gate": True,
        "not_live_runtime_evidence": True,
        "runtime_transport_implemented": False,
        "ui_runtime_implemented": False,
        "accepted_state_ui_controls_enabled": False,
        "gate_summary": {
            "source_ui_binding_gate": UI_BINDING_GATE_ID,
            "future_live_echo_gate": LIVE_ECHO_GATE_ID,
            "pending_only_from": COMMAND_SCHEMA_ID,
            "pending_method": STATE_PENDING_METHOD,
            "accepted_rejected_only_from": ECHO_SCHEMA_ID,
            "consumer_sink": STATE_ECHO_SINK,
            "false_ack_sources_rejected": FALSE_ACK_SOURCES,
            "actual_live_runtime_ack_claimed": False,
        },
        "control_descriptors": descriptors,
        "reducer_fixture_matrix": matrix,
        "matrix_summary": {
            "descriptor_count": len(descriptors),
            "total_rows": len(matrix),
            "required_row_kinds": sorted(REQUIRED_ROW_KINDS),
            "rows_per_descriptor": {
                descriptor_id: sorted(row["row_kind"] for row in rows)
                for descriptor_id, rows in sorted(rows_by_descriptor.items())
            },
            "pending_rows": len([row for row in matrix if row["row_kind"] == "pending_from_matching_command"]),
            "future_authoritative_accepted_rows": len(future_accepted_rows),
            "future_authoritative_rejected_rows": len(future_rejected_rows),
            "stale_echo_rejected_rows": len(stale_rows),
            "mismatched_echo_rejected_rows": len(mismatch_rows),
            "false_ack_rejected_rows": len(false_ack_rows),
            "runtime_ack_now_leaks": len(runtime_ack_now_leaks),
            "all_controls_disabled_now": all(row.get("control_enabled_now") is False for row in matrix),
            "all_rows_not_live_runtime_evidence": all(row.get("not_live_runtime_evidence") is True for row in matrix),
        },
        "schema_anchor_summary": {
            "command_schema": repo(COMMAND_SCHEMA_PATH),
            "echo_schema": repo(ECHO_SCHEMA_PATH),
            "command_schema_allowed_wire_kinds": sorted(allowed_wire_kinds),
            "command_schema_forbidden_wire_kinds": sorted(forbidden_wire_kinds),
            "echo_status_values": sorted(echo_status_values),
            "echo_ack_authority_values": sorted(echo_authorities),
        },
        "source_anchor_summary": {
            "ui_binding_evidence": repo(UI_BINDING_EVIDENCE),
            "ui_binding_return": repo(UI_BINDING_RETURN),
            "state_component_header": repo(STATE_HEADER),
            "state_component_source": repo(STATE_SOURCE),
            "has_pending_method": STATE_PENDING_METHOD in state_text,
            "has_echo_sink": "ApplyCommandEchoJson" in state_text,
            "has_command_schema_guard": COMMAND_SCHEMA_ID in state_text,
            "has_echo_schema_guard": ECHO_SCHEMA_ID in state_text,
            "has_no_pose_overwrite_guard": "no_pose_overwrite_not_pass" in state_text,
            "has_matching_pending_request_guard": "no_matching_command_request" in state_text,
            "has_seq_mismatch_guard": "seq_mismatch" in state_text,
            "has_command_kind_mismatch_guard": "command_kind_mismatch" in state_text,
            "has_smoke_source_downgrade": "smoke_only" in state_text and "IsSmokeSource" in state_text,
        },
        "future_ui_implementation_recommendation": {
            "recommended_next_scope": "separately authorized UI/runtime implementation after live echo transport exists",
            "minimum_reducer_acceptance_gate": [
                "UI creates pending state only after a matching mosim.ue_command.v1 request is recorded",
                "UI displays accepted/rejected only after a matching authoritative mosim.ue_command_echo.v1 row",
                "matching identity includes run_id, request_id, seq, command wire kind, control_descriptor_id, and time_s",
                "stale seq/time echoes remain rejected and do not clear pending state",
                "mismatched request_id, command kind, or control descriptor echoes remain rejected",
                "false ack sources, build success, sender success, fixture rows, and quadrotor.unreal_state never enable accepted controls",
                "no_pose_overwrite_status must remain pass",
            ],
            "blocker_conditions": [
                "future task needs UE Editor, runtime, build, UMG, Blueprint, Slate, Web UI, sockets, listeners, timers, or background loops without PMO authorization",
                "future task treats build, pytest, checker, sender, fixture, static, operator-click, or quadrotor.unreal_state rows as live ack",
                "future task enables accepted-state controls before authoritative live echo evidence",
                "future task claims planner_ready, controller performance, FAST-LIO success, mission success, closed_loop, or final UI acceptance from this fixture",
            ],
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
