#!/usr/bin/env python3
"""Check future live UE command-echo accepted-state fixture contract.

This is a source/static fixture contract only. It does not open Unreal Editor,
bind UI assets, implement a runtime echo receiver, call MWORKS, or publish or
consume ROS2 topics.
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
REQUIRED_ACCEPTED_FIXTURE_FIELDS = [
    "schema",
    "source",
    "status",
    "run_id",
    "request_id",
    "seq",
    "time_s",
    "ack_authority",
    "no_pose_overwrite_status",
    "command.kind",
]
REQUIRED_CONTROL_KINDS = [
    "controller_select",
    "planner_select",
    "wind_profile",
    "motor_fault",
    "scene_switch",
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
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def command_kind(row: dict[str, Any]) -> str:
    command = row.get("command")
    if isinstance(command, dict):
        return str(command.get("kind") or "")
    return str(row.get("command_kind") or row.get("kind") or "")


def command_id(row: dict[str, Any]) -> str:
    return f"{row.get('run_id', '')}|{row.get('request_id', '')}|{row.get('seq', '')}|{command_kind(row)}"


def has_timestamp(row: dict[str, Any]) -> bool:
    value = row.get("time_s")
    return isinstance(value, (int, float)) and value >= 0.0


def has_command_id(row: dict[str, Any]) -> bool:
    return bool(str(row.get("run_id") or "")) and bool(str(row.get("request_id") or "")) and isinstance(
        row.get("seq"), int
    ) and bool(command_kind(row))


def missing_required_fields(row: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for field in REQUIRED_ACCEPTED_FIXTURE_FIELDS:
        if field == "command.kind":
            if not command_kind(row):
                missing.append(field)
            continue
        if field not in row or row.get(field) in ("", None):
            missing.append(field)
    if "time_s" not in missing and not has_timestamp(row):
        missing.append("time_s")
    if "seq" not in missing and not isinstance(row.get("seq"), int):
        missing.append("seq")
    return missing


def classify_echo_fixture(row: dict[str, Any]) -> dict[str, Any]:
    source = str(row.get("source") or "")
    status = str(row.get("status") or "")
    authority = str(row.get("ack_authority") or "")
    expected_authority = AUTHORITATIVE_LIVE_SOURCES.get(source, "")
    non_live = source in NON_LIVE_SOURCES
    missing = missing_required_fields(row)
    source_authoritative = bool(expected_authority) and authority == expected_authority
    schema_ok = row.get("schema") == "mosim.ue_command_echo.v1"
    status_ok = status in {"accepted", "rejected"}
    no_pose_ok = row.get("no_pose_overwrite_status") == "pass"
    valid_future_live_fixture = (
        schema_ok
        and status_ok
        and source_authoritative
        and has_command_id(row)
        and has_timestamp(row)
        and no_pose_ok
    )
    accepted_as_runtime_ack = valid_future_live_fixture and status == "accepted"
    if status == "pending":
        display_state = "disabled_pending_echo"
    elif status == "rejected":
        display_state = "disabled_rejected"
    elif accepted_as_runtime_ack:
        display_state = "enabled_after_runtime_echo"
    else:
        display_state = "disabled_smoke_or_invalid_fixture"
    return {
        "name": row.get("name", ""),
        "schema": row.get("schema", ""),
        "source": source or "unspecified_smoke_fixture",
        "status": status,
        "ack_authority": authority,
        "expected_ack_authority": expected_authority,
        "command_kind": command_kind(row),
        "command_id": command_id(row),
        "has_authoritative_source": source_authoritative,
        "has_command_id": has_command_id(row),
        "has_timestamp": has_timestamp(row),
        "has_status": status_ok,
        "missing_required_fields": missing,
        "quality_status": "runtime_echo_fixture" if valid_future_live_fixture else "smoke_only" if non_live else "invalid_fixture",
        "accepted_as_runtime_ack": accepted_as_runtime_ack,
        "control_display_state": display_state,
        "must_remain_disabled": display_state != "enabled_after_runtime_echo",
        "valid_future_live_fixture": valid_future_live_fixture,
        "no_pose_overwrite_status": row.get("no_pose_overwrite_status", ""),
    }


def live_echo(
    *,
    name: str,
    source: str,
    authority: str,
    status: str = "accepted",
    kind: str = "controller_select",
    request_id: str = "cmd_live",
    seq: int = 10,
    time_s: float = 1.0,
) -> dict[str, Any]:
    return {
        "name": name,
        "schema": "mosim.ue_command_echo.v1",
        "source": source,
        "status": status,
        "reason": "accepted_by_authoritative_fixture" if status == "accepted" else "runtime_gate_rejected",
        "run_id": "run_future_live_fixture",
        "request_id": request_id,
        "seq": seq,
        "time_s": time_s,
        "ack_authority": authority,
        "no_pose_overwrite_status": "pass",
        "command": {"kind": kind, "payload": {}},
    }


def build_fixture_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, kind in enumerate(REQUIRED_CONTROL_KINDS, start=1):
        source = "MWORKS_ROS2_live_downlink" if kind in {"planner_select", "scene_switch"} else "MWORKS_live_downlink"
        authority = AUTHORITATIVE_LIVE_SOURCES[source]
        rows.append(
            live_echo(
                name=f"valid_future_live_{kind}",
                source=source,
                authority=authority,
                kind=kind,
                request_id=f"cmd_live_{index}",
                seq=index,
                time_s=float(index) * 0.25,
            )
        )
    for source in sorted(label for label in NON_LIVE_SOURCES if label):
        rows.append(
            live_echo(
                name=f"non_live_{source}",
                source=source,
                authority="MWORKS_ROS2",
                kind="controller_select",
                request_id=f"cmd_{source}",
            )
        )
    rows.append(
        live_echo(
            name="rejected_future_live",
            source="MWORKS_ROS2_live_downlink",
            authority="MWORKS_ROS2",
            status="rejected",
            kind="planner_select",
            request_id="cmd_rejected",
        )
    )
    rows.append(
        live_echo(
            name="authority_mismatch",
            source="MWORKS_live_downlink",
            authority="ROS2",
            kind="controller_select",
            request_id="cmd_authority_mismatch",
        )
    )
    missing_time = live_echo(
        name="missing_timestamp",
        source="MWORKS_live_downlink",
        authority="MWORKS",
        kind="wind_profile",
        request_id="cmd_missing_timestamp",
    )
    missing_time.pop("time_s")
    rows.append(missing_time)
    missing_request = live_echo(
        name="missing_command_id",
        source="MWORKS_live_downlink",
        authority="MWORKS",
        kind="motor_fault",
        request_id="",
    )
    rows.append(missing_request)
    missing_status = live_echo(
        name="missing_status",
        source="MWORKS_live_downlink",
        authority="MWORKS",
        kind="scene_switch",
        request_id="cmd_missing_status",
    )
    missing_status.pop("status")
    rows.append(missing_status)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default="")
    args = parser.parse_args()

    issues: list[str] = []
    warnings = [
        "source/static future live-echo fixture contract only; no live runtime ack is claimed",
        "runtime receiver, UE UI binding, and C++ authoritative source allowlist are out of scope for this gate",
    ]

    command_schema = read_json(COMMAND_SCHEMA_PATH)
    echo_schema = read_json(ECHO_SCHEMA_PATH)
    state_source = read(STATE_SOURCE)
    allowed_kinds = set(command_schema.get("command", {}).get("allowed_kinds", []))
    status_values = set(echo_schema.get("status_values", []))
    authority_values = set(echo_schema.get("ack_authority_values", []))

    if {"accepted", "rejected"} - status_values:
        issues.append("echo schema must preserve accepted/rejected status values")
    if set(AUTHORITATIVE_LIVE_SOURCES.values()) - authority_values:
        issues.append("echo schema missing required authoritative ack_authority values")
    for kind in REQUIRED_CONTROL_KINDS:
        if kind not in allowed_kinds:
            issues.append(f"command schema missing required accepted-state fixture kind: {kind}")
    for label in sorted(label for label in NON_LIVE_SOURCES if label):
        if f'TEXT("{label}")' not in state_source:
            issues.append(f"state component missing non-live smoke source label: {label}")

    classified_rows = [classify_echo_fixture(row) for row in build_fixture_rows()]
    valid_live_rows = [row for row in classified_rows if row["valid_future_live_fixture"] and row["status"] == "accepted"]
    non_live_runtime_leaks = [
        row
        for row in classified_rows
        if row["source"] in NON_LIVE_SOURCES
        and (row["accepted_as_runtime_ack"] or row["control_display_state"] == "enabled_after_runtime_echo")
    ]
    malformed_runtime_leaks = [
        row
        for row in classified_rows
        if row["source"] not in NON_LIVE_SOURCES
        and row["status"] == "accepted"
        and not row["valid_future_live_fixture"]
        and row["accepted_as_runtime_ack"]
    ]
    rejected_runtime_leaks = [
        row for row in classified_rows if row["status"] == "rejected" and row["accepted_as_runtime_ack"]
    ]

    if len(valid_live_rows) != len(REQUIRED_CONTROL_KINDS):
        issues.append("not every required control kind has one valid future live accepted fixture")
    if non_live_runtime_leaks:
        issues.append("non-live smoke/preflight/source rows can be represented as runtime accepted")
    if malformed_runtime_leaks:
        issues.append("malformed future live fixtures can be represented as runtime accepted")
    if rejected_runtime_leaks:
        issues.append("rejected future live fixtures can be represented as runtime accepted")

    report = {
        "schema": "mosim.ue_live_echo_acceptance_fixture_contract_static.v1",
        "ok": not issues,
        "source": "source_static_fixture_contract",
        "accepted_state_fixture_contract": {
            "input_schema": "mosim.ue_command_echo.v1",
            "required_fields_for_runtime_accepted": REQUIRED_ACCEPTED_FIXTURE_FIELDS,
            "authoritative_live_sources": AUTHORITATIVE_LIVE_SOURCES,
            "accepted_status": "accepted",
            "rejected_status_display": "disabled_rejected",
            "runtime_ack_required_before_enablement": True,
            "smoke_preflight_source_display": "disabled_smoke_or_invalid_fixture",
            "non_live_accepted_as_runtime_ack": False,
        },
        "required_control_kinds": REQUIRED_CONTROL_KINDS,
        "non_live_source_labels": sorted(label for label in NON_LIVE_SOURCES if label),
        "fixture_rows": classified_rows,
        "fixture_summary": {
            "total_rows": len(classified_rows),
            "valid_future_live_accepted_rows": len(valid_live_rows),
            "non_live_runtime_leaks": len(non_live_runtime_leaks),
            "malformed_runtime_leaks": len(malformed_runtime_leaks),
            "rejected_runtime_leaks": len(rejected_runtime_leaks),
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
