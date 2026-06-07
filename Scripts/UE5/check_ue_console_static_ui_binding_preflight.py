#!/usr/bin/env python3
"""Check UE Experiment Console static UI-binding preflight contract.

This is a source/static preflight only. It does not open Unreal Editor, bind
Blueprint/UMG/Slate assets, implement a runtime receiver, call MWORKS/ROS2/UE
runtime, or prove live acknowledgement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
COMMAND_SCHEMA_PATH = ROOT / "Config/schemas/mosim_ue_command_v1.schema.json"
ECHO_SCHEMA_PATH = ROOT / "Config/schemas/mosim_ue_command_echo_v1.schema.json"
STATE_SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksExperimentConsoleStateComponent.cpp"
STATE_HEADER = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksExperimentConsoleStateComponent.h"
RECEIVER_010_CONTRACT = (
    ROOT
    / "Results/unreal_experiment_console/source_static_receiver_shell_contract_20260607_010/receiver_shell_contract_design.json"
)

NON_LIVE_SOURCES = {
    "",
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
CONTROL_CATEGORIES = [
    {
        "category": "controller",
        "control_group": "controller switch",
        "command_kind": "controller_select",
        "required_ack_authority": "MWORKS",
        "live_source": "MWORKS_live_downlink",
    },
    {
        "category": "planner",
        "control_group": "planner switch",
        "command_kind": "planner_select",
        "required_ack_authority": "ROS2",
        "live_source": "ROS2_runtime_echo",
    },
    {
        "category": "wind",
        "control_group": "wind disturbance",
        "command_kind": "wind_profile",
        "required_ack_authority": "MWORKS",
        "live_source": "MWORKS_live_downlink",
    },
    {
        "category": "fault",
        "control_group": "fault injection",
        "command_kind": "motor_fault",
        "required_ack_authority": "MWORKS",
        "live_source": "MWORKS_live_downlink",
    },
    {
        "category": "map_scene",
        "control_group": "map/scene switch",
        "command_kind": "scene_switch",
        "required_ack_authority": "MWORKS_ROS2",
        "live_source": "MWORKS_ROS2_live_downlink",
    },
    {
        "category": "reset",
        "control_group": "scenario reset",
        "command_kind": "scenario_reset",
        "required_ack_authority": "MWORKS",
        "live_source": "MWORKS_live_downlink",
    },
    {
        "category": "recording",
        "control_group": "recording",
        "command_kind": "recording",
        "required_ack_authority": "MWORKS",
        "live_source": "MWORKS_live_downlink",
    },
]
FORBIDDEN_ACK_SOURCES = {
    "udp_send_success",
    "sender_result_bSent",
    "quadrotor.unreal_state.v1",
    "quadrotor.unreal_state.frame",
    "fixture_only_007",
    "fixture_only_008",
    "fixture_only_010",
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


def source_literal(label: str) -> str:
    return "Source.IsEmpty()" if label == "" else f'TEXT("{label}")'


def ui_binding_row(
    *,
    category: dict[str, str],
    row_name: str,
    source: str,
    status: str,
    schema: str = "mosim.ue_command_echo.v1",
    has_matching_pending: bool = True,
    has_timestamp: bool = True,
    command_id_matches: bool = True,
    no_pose_overwrite_status: str = "pass",
) -> dict[str, Any]:
    expected_authority = category["required_ack_authority"]
    authoritative_source = AUTHORITATIVE_LIVE_SOURCES.get(source) == expected_authority
    is_pending = row_name == "pending_request"
    is_non_live = source in NON_LIVE_SOURCES
    is_forbidden_source = source in FORBIDDEN_ACK_SOURCES
    schema_ok = schema == "mosim.ue_command_echo.v1"
    status_ok = status in {"accepted", "rejected"}
    no_pose_ok = no_pose_overwrite_status == "pass"
    complete_future_live_echo = (
        schema_ok
        and status_ok
        and status == "accepted"
        and authoritative_source
        and has_matching_pending
        and has_timestamp
        and command_id_matches
        and no_pose_ok
        and not is_non_live
        and not is_forbidden_source
    )
    accepted_as_runtime_ack = complete_future_live_echo
    if is_pending:
        ui_binding_preflight_state = "pending_disabled"
        display_policy = "must_remain_disabled_until_echo"
    elif status == "rejected" and schema_ok and authoritative_source and no_pose_ok:
        ui_binding_preflight_state = "rejected_disabled"
        display_policy = "must_remain_disabled_after_rejection"
    elif complete_future_live_echo:
        ui_binding_preflight_state = "eligible_after_future_live_echo"
        display_policy = "eligible_only_not_implemented_or_enabled"
    else:
        ui_binding_preflight_state = "disabled_non_authoritative_or_invalid"
        display_policy = "must_remain_disabled"
    return {
        "row_name": row_name,
        "category": category["category"],
        "control_group": category["control_group"],
        "command_kind": category["command_kind"],
        "schema": schema,
        "source": source or "unspecified_pending_or_smoke",
        "status": status or "pending",
        "expected_ack_authority": expected_authority,
        "authoritative_source": authoritative_source,
        "has_matching_pending_request": has_matching_pending,
        "has_timestamp": has_timestamp,
        "command_id_matches": command_id_matches,
        "no_pose_overwrite_status": no_pose_overwrite_status,
        "accepted_as_runtime_ack": accepted_as_runtime_ack,
        "ui_binding_preflight_state": ui_binding_preflight_state,
        "display_policy": display_policy,
        "must_remain_pending_or_disabled": ui_binding_preflight_state != "eligible_after_future_live_echo",
        "actual_ui_binding_implemented": False,
        "actual_accepted_state_control_enabled": False,
    }


def build_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for category in CONTROL_CATEGORIES:
        rows.append(
            ui_binding_row(
                category=category,
                row_name="pending_request",
                source="",
                status="",
                has_matching_pending=True,
            )
        )
        for source in sorted(source for source in NON_LIVE_SOURCES if source):
            rows.append(
                ui_binding_row(
                    category=category,
                    row_name=f"non_live_{source}",
                    source=source,
                    status="accepted",
                )
            )
        for source in sorted(FORBIDDEN_ACK_SOURCES):
            rows.append(
                ui_binding_row(
                    category=category,
                    row_name=f"forbidden_ack_source_{source}",
                    source=source,
                    status="accepted",
                )
            )
        rows.append(
            ui_binding_row(
                category=category,
                row_name="no_pose_overwrite_failure",
                source=category["live_source"],
                status="accepted",
                no_pose_overwrite_status="fail",
            )
        )
        rows.append(
            ui_binding_row(
                category=category,
                row_name="missing_timestamp",
                source=category["live_source"],
                status="accepted",
                has_timestamp=False,
            )
        )
        rows.append(
            ui_binding_row(
                category=category,
                row_name="command_id_mismatch",
                source=category["live_source"],
                status="accepted",
                command_id_matches=False,
            )
        )
        rows.append(
            ui_binding_row(
                category=category,
                row_name="no_matching_pending",
                source=category["live_source"],
                status="accepted",
                has_matching_pending=False,
            )
        )
        rows.append(
            ui_binding_row(
                category=category,
                row_name="authoritative_rejected",
                source=category["live_source"],
                status="rejected",
            )
        )
        rows.append(
            ui_binding_row(
                category=category,
                row_name="valid_future_authoritative_live_echo",
                source=category["live_source"],
                status="accepted",
            )
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default="")
    args = parser.parse_args()

    issues: list[str] = []
    warnings = [
        "source/static UI-binding preflight only; no Blueprint/UMG/Slate binding is implemented",
        "eligible_after_future_live_echo is a contract eligibility state, not actual live UI enablement",
    ]

    command_schema = read_json(COMMAND_SCHEMA_PATH)
    echo_schema = read_json(ECHO_SCHEMA_PATH)
    receiver_contract = read_json(RECEIVER_010_CONTRACT)
    state_source = read(STATE_SOURCE)
    state_header = read(STATE_HEADER)
    combined_state = state_header + "\n" + state_source
    allowed_kinds = set(command_schema.get("command", {}).get("allowed_kinds", []))
    echo_status_values = set(echo_schema.get("status_values", []))
    ack_authority_values = set(echo_schema.get("ack_authority_values", []))

    if not command_schema:
        issues.append("missing mosim_ue_command_v1 schema")
    if not echo_schema:
        issues.append("missing mosim_ue_command_echo_v1 schema")
    if not receiver_contract:
        issues.append("missing UE 010 receiver shell contract evidence")
    if "ApplyCommandEchoJson" not in combined_state:
        issues.append("state component lacks ApplyCommandEchoJson sink")
    if "RecordPendingCommandFromPacketJson" not in combined_state:
        issues.append("state component lacks RecordPendingCommandFromPacketJson pending anchor")
    if "mosim.ue_command_echo.v1" not in combined_state:
        issues.append("state component lacks mosim.ue_command_echo.v1 guard")
    for source in sorted(NON_LIVE_SOURCES):
        literal = source_literal(source)
        if literal not in state_source:
            issues.append(f"state component no longer classifies non-live source as smoke-only: {source or '<empty>'}")
    for category in CONTROL_CATEGORIES:
        kind = category["command_kind"]
        if kind not in allowed_kinds:
            issues.append(f"command schema missing UI preflight command kind: {kind}")
        if f'TEXT("{kind}")' not in state_source:
            issues.append(f"state component missing UI preflight command kind allowlist: {kind}")
    if {"accepted", "rejected"} - echo_status_values:
        issues.append("echo schema must include accepted and rejected status values")
    if set(AUTHORITATIVE_LIVE_SOURCES.values()) - ack_authority_values:
        issues.append("echo schema missing required ack_authority values")

    receiver_summary = receiver_contract.get("future_receiver_shell_contract", {})
    input_contract = receiver_summary.get("input_contract", {}) if isinstance(receiver_summary, dict) else {}
    forbidden_inputs = set(input_contract.get("forbidden_inputs_as_ack", [])) if isinstance(input_contract, dict) else set()
    if "quadrotor.unreal_state.* frame/status downlink" not in forbidden_inputs:
        issues.append("010 contract does not forbid quadrotor.unreal_state frame/status downlink as ack")
    if "UDP send success" not in forbidden_inputs:
        issues.append("010 contract does not forbid UDP send success as ack")

    matrix = build_matrix()
    pending_rows = [row for row in matrix if row["row_name"] == "pending_request"]
    non_live_rows = [row for row in matrix if row["source"] in NON_LIVE_SOURCES]
    forbidden_source_rows = [row for row in matrix if row["source"] in FORBIDDEN_ACK_SOURCES]
    invalid_live_rows = [
        row
        for row in matrix
        if row["row_name"] in {"no_pose_overwrite_failure", "missing_timestamp", "command_id_mismatch", "no_matching_pending"}
    ]
    rejected_rows = [row for row in matrix if row["row_name"] == "authoritative_rejected"]
    eligible_rows = [row for row in matrix if row["ui_binding_preflight_state"] == "eligible_after_future_live_echo"]
    actual_enabled_rows = [
        row
        for row in matrix
        if row["actual_ui_binding_implemented"] or row["actual_accepted_state_control_enabled"]
    ]
    disabled_leaks = [
        row
        for row in matrix
        if row["row_name"] != "valid_future_authoritative_live_echo" and not row["must_remain_pending_or_disabled"]
    ]
    runtime_ack_leaks = [
        row
        for row in matrix
        if row["row_name"] != "valid_future_authoritative_live_echo" and row["accepted_as_runtime_ack"]
    ]

    if len(pending_rows) != len(CONTROL_CATEGORIES):
        issues.append("not every UI control category has a pending disabled row")
    if any(row["ui_binding_preflight_state"] != "pending_disabled" for row in pending_rows):
        issues.append("pending request rows are not pending_disabled")
    if any(row["accepted_as_runtime_ack"] for row in non_live_rows):
        issues.append("non-live smoke/source/preflight rows can become runtime ack")
    if any(row["accepted_as_runtime_ack"] for row in forbidden_source_rows):
        issues.append("forbidden ack sources can become runtime ack")
    if any(row["accepted_as_runtime_ack"] for row in invalid_live_rows):
        issues.append("invalid live rows can become runtime ack")
    if any(row["accepted_as_runtime_ack"] for row in rejected_rows):
        issues.append("rejected authoritative rows can become runtime ack")
    if len(eligible_rows) != len(CONTROL_CATEGORIES):
        issues.append("not every UI control category has exactly one future authoritative live echo eligibility row")
    if actual_enabled_rows:
        issues.append("static UI preflight must not mark actual UI binding or controls as enabled")
    if disabled_leaks:
        issues.append("non-authoritative/non-live/pending/rejected rows can escape pending/disabled policy")
    if runtime_ack_leaks:
        issues.append("non-authoritative/non-live/pending/rejected rows can leak accepted_as_runtime_ack")

    report = {
        "schema": "mosim.ue_console_static_ui_binding_preflight.v1",
        "ok": not issues,
        "source": "source_static_ui_binding_preflight",
        "ui_binding_implemented": False,
        "accepted_state_controls_enabled": False,
        "runtime_receiver_implemented": False,
        "not_runtime_ue_console": True,
        "ui_preflight_contract": {
            "purpose": "Keep controller/planner/wind/fault/scene/reset/recording controls pending or disabled until a future authoritative mosim.ue_command_echo.v1 accepted row exists.",
            "pending_policy": "pending_disabled",
            "non_live_policy": "disabled_non_authoritative_or_invalid",
            "forbidden_ack_source_policy": "disabled_non_authoritative_or_invalid",
            "rejected_policy": "rejected_disabled",
            "future_live_eligibility_policy": "eligible_after_future_live_echo",
            "eligibility_is_not_actual_ui_enablement": True,
        },
        "control_categories": CONTROL_CATEGORIES,
        "authoritative_live_sources": AUTHORITATIVE_LIVE_SOURCES,
        "non_live_source_labels": sorted(source for source in NON_LIVE_SOURCES if source),
        "forbidden_ack_sources": sorted(FORBIDDEN_ACK_SOURCES),
        "fixture_matrix": matrix,
        "matrix_summary": {
            "total_rows": len(matrix),
            "control_categories": len(CONTROL_CATEGORIES),
            "pending_disabled_rows": sum(1 for row in matrix if row["ui_binding_preflight_state"] == "pending_disabled"),
            "non_live_rows": len(non_live_rows),
            "forbidden_ack_source_rows": len(forbidden_source_rows),
            "invalid_live_rows": len(invalid_live_rows),
            "rejected_disabled_rows": len(rejected_rows),
            "future_authoritative_live_eligible_rows": len(eligible_rows),
            "actual_enabled_rows": len(actual_enabled_rows),
            "disabled_leaks": len(disabled_leaks),
            "runtime_ack_leaks": len(runtime_ack_leaks),
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
