#!/usr/bin/env python3
"""Check UE Experiment Console disabled-state source/fixture contract.

This is a source/static fixture smoke only. It does not open Unreal Editor,
bind UMG/Blueprint controls, implement a live echo receiver, call MWORKS, or
publish/consume ROS2 topics.
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

NON_LIVE_SOURCES = {
    "",
    "offline_adapter_smoke",
    "source_level_smoke",
    "MWORKS_MCP_result_adapter_smoke",
    "MWORKS_MCP_runtime_adapter_preflight",
}
FUTURE_LIVE_SOURCE = "MWORKS_ROS2_live_downlink"
REQUIRED_CONTROL_CATEGORIES = [
    {
        "category": "controller",
        "command_kind": "controller_select",
        "control_group": "controller switch",
        "required_ack_authority": "MWORKS",
    },
    {
        "category": "planner",
        "command_kind": "planner_select",
        "control_group": "planner switch",
        "required_ack_authority": "ROS2",
    },
    {
        "category": "wind",
        "command_kind": "wind_profile",
        "control_group": "wind disturbance",
        "required_ack_authority": "MWORKS",
    },
    {
        "category": "fault",
        "command_kind": "motor_fault",
        "control_group": "fault injection",
        "required_ack_authority": "MWORKS",
    },
    {
        "category": "map_scene",
        "command_kind": "scene_switch",
        "control_group": "map/scene switch",
        "required_ack_authority": "MWORKS_ROS2",
    },
]
FORBIDDEN_RUNTIME_CLAIMS = {
    "live_ue_runtime_ack": False,
    "live_mworks_downlink": False,
    "ros2_runtime_ack": False,
    "planner_ready": False,
    "closed_loop_ready": False,
    "controller_performance": False,
    "fast_lio_success": False,
    "mission_success": False,
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def source_literal(label: str) -> str:
    return 'Source.IsEmpty()' if label == "" else f'TEXT("{label}")'


def fixture_state(
    *,
    category: dict[str, str],
    ui_state: str,
    echo_source: str,
    status: str = "",
) -> dict[str, Any]:
    is_pending = ui_state == "pending"
    is_rejected = ui_state == "rejected" or status == "rejected"
    is_non_live = echo_source in NON_LIVE_SOURCES
    accepted_as_runtime_ack = ui_state == "accepted" and not is_non_live and status != "rejected"
    quality_status = (
        "pending_no_runtime_echo"
        if is_pending
        else "smoke_only"
        if is_non_live
        else "runtime_echo_fixture"
    )
    display_state = (
        "disabled_pending_echo"
        if is_pending
        else "disabled_rejected"
        if is_rejected
        else "disabled_smoke_or_preflight"
        if is_non_live
        else "enabled_after_runtime_echo"
    )
    return {
        "category": category["category"],
        "control_group": category["control_group"],
        "command_kind": category["command_kind"],
        "required_ack_authority": category["required_ack_authority"],
        "ui_state": ui_state,
        "echo_source": echo_source or "unspecified_smoke_fixture",
        "quality_status": quality_status,
        "accepted_as_runtime_ack": accepted_as_runtime_ack,
        "control_display_state": display_state,
        "must_remain_disabled": display_state != "enabled_after_runtime_echo",
        "no_pose_overwrite_status": "pass",
    }


def build_fixture_matrix() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for category in REQUIRED_CONTROL_CATEGORIES:
        rows.append(fixture_state(category=category, ui_state="pending", echo_source=""))
        for source in sorted(label for label in NON_LIVE_SOURCES if label):
            rows.append(fixture_state(category=category, ui_state="accepted", echo_source=source, status="accepted"))
        rows.append(
            fixture_state(
                category=category,
                ui_state="rejected",
                echo_source=FUTURE_LIVE_SOURCE,
                status="rejected",
            )
        )
        rows.append(
            fixture_state(
                category=category,
                ui_state="accepted",
                echo_source=FUTURE_LIVE_SOURCE,
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
        "source/static disabled-state fixture only; no live runtime ack is claimed",
        "future UI binding must consume this as a disabled-state contract, not as implemented UMG evidence",
    ]

    command_schema = read_json(COMMAND_SCHEMA_PATH) if COMMAND_SCHEMA_PATH.exists() else {}
    echo_schema = read_json(ECHO_SCHEMA_PATH) if ECHO_SCHEMA_PATH.exists() else {}
    state_source = read(STATE_SOURCE)
    state_header = read(STATE_HEADER)
    combined_state_source = state_header + "\n" + state_source
    allowed_kinds = set(command_schema.get("command", {}).get("allowed_kinds", []))
    echo_status_values = set(echo_schema.get("status_values", []))
    command_schema_runtime_ack = str(command_schema.get("runtime_ack", ""))

    if not command_schema:
        issues.append("missing command schema")
    if not echo_schema:
        issues.append("missing command echo schema")
    for category in REQUIRED_CONTROL_CATEGORIES:
        kind = category["command_kind"]
        if kind not in allowed_kinds:
            issues.append(f"required disabled-state command kind missing from schema: {kind}")
        if f'TEXT("{kind}")' not in state_source:
            issues.append(f"required disabled-state command kind missing from state component allowlist: {kind}")
    if {"accepted", "rejected"} - echo_status_values:
        issues.append("echo schema must include accepted and rejected status values")
    if "mosim.ue_command_echo.v1" not in command_schema_runtime_ack:
        issues.append("command schema must require mosim.ue_command_echo.v1 before accepted state")
    for source in sorted(NON_LIVE_SOURCES):
        literal = source_literal(source)
        if literal not in state_source:
            issues.append(f"non-live source label missing from IsSmokeSource: {source or '<empty>'}")
    for required in [
        "pending_no_runtime_echo",
        "smoke_only",
        "runtime_echo_fixture",
        "bAcceptedAsRuntimeAck = false",
        "State->bAcceptedAsRuntimeAck = !IsSmokeSource(EchoSource);",
        "no_pose_overwrite_not_pass",
        "no_matching_command_request",
        "seq_mismatch",
        "command_kind_mismatch",
    ]:
        if required not in combined_state_source:
            issues.append(f"missing source-level state transition guard: {required}")

    matrix = build_fixture_matrix()
    non_live_runtime_leaks = [
        row
        for row in matrix
        if row["echo_source"] != FUTURE_LIVE_SOURCE
        and (row["accepted_as_runtime_ack"] or row["control_display_state"] == "enabled_after_runtime_echo")
    ]
    pending_not_disabled = [
        row
        for row in matrix
        if row["ui_state"] == "pending" and row["control_display_state"] != "disabled_pending_echo"
    ]
    rejected_not_disabled = [
        row
        for row in matrix
        if row["ui_state"] == "rejected" and row["control_display_state"] != "disabled_rejected"
    ]
    future_live_enabled = [
        row
        for row in matrix
        if row["echo_source"] == FUTURE_LIVE_SOURCE
        and row["ui_state"] == "accepted"
        and row["control_display_state"] == "enabled_after_runtime_echo"
        and row["accepted_as_runtime_ack"] is True
    ]

    if non_live_runtime_leaks:
        issues.append("non-live smoke/preflight/source rows can enable accepted runtime controls")
    if pending_not_disabled:
        issues.append("pending rows are not disabled_pending_echo")
    if rejected_not_disabled:
        issues.append("rejected rows are not disabled_rejected")
    if len(future_live_enabled) != len(REQUIRED_CONTROL_CATEGORIES):
        issues.append("future live fixture cannot represent accepted/enabled state for every required control category")

    report = {
        "schema": "mosim.ue_console_disabled_state_contract_static_smoke.v1",
        "ok": not issues,
        "source": "source_level_static_fixture_contract",
        "required_control_categories": REQUIRED_CONTROL_CATEGORIES,
        "disabled_state_contract": {
            "pending_source": "mosim.ue_command.v1 request only",
            "accepted_rejected_source": "matching mosim.ue_command_echo.v1 only",
            "runtime_ack_required_before_enablement": True,
            "pending_display_state": "disabled_pending_echo",
            "non_live_echo_display_state": "disabled_smoke_or_preflight",
            "rejected_display_state": "disabled_rejected",
            "future_live_accepted_display_state": "enabled_after_runtime_echo",
            "known_non_live_sources_quality_status": "smoke_only",
            "known_non_live_sources_accepted_as_runtime_ack": False,
        },
        "non_live_source_labels": sorted(label for label in NON_LIVE_SOURCES if label),
        "future_live_source_fixture": FUTURE_LIVE_SOURCE,
        "fixture_matrix": matrix,
        "matrix_summary": {
            "total_rows": len(matrix),
            "pending_rows": sum(1 for row in matrix if row["ui_state"] == "pending"),
            "non_live_rows": sum(
                1 for row in matrix if row["echo_source"] != FUTURE_LIVE_SOURCE and row["ui_state"] != "pending"
            ),
            "rejected_rows": sum(1 for row in matrix if row["ui_state"] == "rejected"),
            "future_live_enabled_rows": len(future_live_enabled),
            "non_live_runtime_leaks": len(non_live_runtime_leaks),
        },
        "ui_asset_binding_implemented": False,
        "runtime_receiver_implemented": False,
        "not_runtime_ue_console": True,
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
