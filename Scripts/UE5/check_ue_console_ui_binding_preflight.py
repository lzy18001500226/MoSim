#!/usr/bin/env python3
"""Check the UE Experiment Console catalog-to-control UI binding preflight.

This is a source/static preflight only. It binds the 018 operator command
catalog entries to future UI/control descriptors, but it does not open Unreal,
implement UMG/Blueprint/Slate/Web UI, run live transport, or prove live command
acknowledgement.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from types import ModuleType
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "RFLY-MOSIM-UE-CONSOLE-UI-BINDING-CATALOG-TO-CONTROL-PREFLIGHT-20260607-019"
CATALOG_GATE_ID = "RFLY-MOSIM-UE-CONSOLE-OPERATOR-COMMAND-CATALOG-SOURCE-STATIC-GATE-20260607-018"
LIVE_ECHO_GATE_ID = "RFLY-MOSIM-UE-CONSOLE-LIVE-ECHO-PRODUCER-CONSUMER-GATE-20260607-017"
COMMAND_SCHEMA = "mosim.ue_command.v1"
ECHO_SCHEMA = "mosim.ue_command_echo.v1"
STATE_PENDING_METHOD = "RecordPendingCommandFromPacketJson"
STATE_ECHO_SINK = "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson"

COMMAND_SCHEMA_PATH = ROOT / "Config/schemas/mosim_ue_command_v1.schema.json"
ECHO_SCHEMA_PATH = ROOT / "Config/schemas/mosim_ue_command_echo_v1.schema.json"
PRIOR_018_RETURN_PATH = (
    ROOT
    / "Results/agent_packets/returns/"
    / "RFLY-MOSIM-UE-CONSOLE-OPERATOR-COMMAND-CATALOG-SOURCE-STATIC-GATE-20260607-018.json"
)
PRIOR_017_RETURN_PATH = (
    ROOT
    / "Results/agent_packets/returns/"
    / "RFLY-MOSIM-UE-CONSOLE-LIVE-ECHO-PRODUCER-CONSUMER-GATE-20260607-017.json"
)
OPERATOR_CATALOG_CHECKER = ROOT / "Scripts/UE5/check_ue_console_operator_command_catalog.py"
SENDER_SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksUdpCommandSenderComponent.cpp"
SENDER_HEADER = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksUdpCommandSenderComponent.h"
STATE_SOURCE = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/QuadrotorMworksExperimentConsoleStateComponent.cpp"
STATE_HEADER = ROOT / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/QuadrotorMworksExperimentConsoleStateComponent.h"
RECEIVER_SOURCE = (
    ROOT
    / "UE5/Bridge/Source/QuadrotorMworksBridge/Private/"
    / "QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.cpp"
)
RECEIVER_HEADER = (
    ROOT
    / "UE5/Bridge/Source/QuadrotorMworksBridge/Public/"
    / "QuadrotorMworksExperimentConsoleCommandEchoReceiverComponent.h"
)

MINIMUM_COMMAND_KINDS = {
    "motor_fault.inject_or_clear",
    "disturbance.wind.set_or_clear",
    "controller.switch",
    "planner.switch",
    "scene_map.switch",
    "experiment.run_control",
    "manual_review.request",
}

CONTROL_DESCRIPTOR_PROFILES: dict[str, dict[str, str]] = {
    "motor_fault.inject_or_clear": {
        "control_descriptor_id": "fault_motor_control",
        "control_group": "Fault",
        "display_intent": "Inject or clear a motor fault request.",
    },
    "disturbance.wind.set_or_clear": {
        "control_descriptor_id": "wind_disturbance_control",
        "control_group": "Disturbance",
        "display_intent": "Set or clear a wind disturbance request.",
    },
    "controller.switch": {
        "control_descriptor_id": "controller_switch_control",
        "control_group": "Controller",
        "display_intent": "Request a controller selection change.",
    },
    "planner.switch": {
        "control_descriptor_id": "planner_switch_control",
        "control_group": "Planner",
        "display_intent": "Request a ROS2 planner selection change.",
    },
    "scene_map.switch": {
        "control_descriptor_id": "scene_map_switch_control",
        "control_group": "Scenario",
        "display_intent": "Request a scene/map binding change.",
    },
    "experiment.run_control": {
        "control_descriptor_id": "experiment_run_control",
        "control_group": "Run",
        "display_intent": "Request run reset, start/goal, or recording coordination.",
    },
    "manual_review.request": {
        "control_descriptor_id": "manual_review_request_control",
        "control_group": "Evidence/Review",
        "display_intent": "Request manual evidence or review workflow.",
    },
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


def wire_kinds(entry: dict[str, Any]) -> list[str]:
    if "current_wire_kind" in entry:
        return [str(entry["current_wire_kind"])]
    return [str(kind) for kind in entry.get("current_wire_kind_options", [])]


def load_operator_catalog_checker() -> ModuleType:
    spec = importlib.util.spec_from_file_location("mosim_operator_catalog_checker", OPERATOR_CATALOG_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load operator catalog checker: {OPERATOR_CATALOG_CHECKER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_control_descriptor(entry: dict[str, Any], catalog_checker: ModuleType) -> dict[str, Any]:
    command_kind = str(entry["command_kind"])
    profile = CONTROL_DESCRIPTOR_PROFILES[command_kind]
    current_wire_kinds = wire_kinds(entry)
    required_echo_fields = list(entry["required_ack_evidence_fields"])
    required_echo_fields.extend(
        field
        for field in [
            "source/ack_authority matches domain owner",
            "control_descriptor_id matches pending UI command descriptor",
        ]
        if field not in required_echo_fields
    )
    return {
        "command_kind": command_kind,
        "control_descriptor_id": profile["control_descriptor_id"],
        "control_group": profile["control_group"],
        "display_intent": profile["display_intent"],
        "domain_owner": entry["domain_owner"],
        "current_wire_kind": current_wire_kinds[0] if len(current_wire_kinds) == 1 else None,
        "current_wire_kind_options": current_wire_kinds if len(current_wire_kinds) > 1 else None,
        "payload_contract": entry["payload_contract"],
        "default_state": "disabled_pending_authoritative_echo",
        "pending_source": f"{STATE_PENDING_METHOD} from {COMMAND_SCHEMA} UE command request",
        "accepted_state_precondition": (
            f"Control remains pending/disabled until a matching {COMMAND_SCHEMA} request "
            f"is recorded by {STATE_PENDING_METHOD} and a future authoritative {ECHO_SCHEMA} "
            f"row passes {LIVE_ECHO_GATE_ID} through {STATE_ECHO_SINK} with matching "
            "run_id/request_id/seq/command identity, time_s, source/ack_authority, "
            "status=accepted|rejected, and no_pose_overwrite_status=pass."
        ),
        "required_echo_fields": required_echo_fields,
        "required_ack_authority_values": entry["required_ack_authority_values"],
        "required_live_source_options": entry["required_live_source_options"],
        "forbidden_shortcut": sorted(set(entry["forbidden_shortcut"] + FALSE_ACK_SOURCES)),
        "claim_boundary": entry["claim_boundary"],
        "control_enabled_now": False,
        "accepted_state_allowed_now": False,
        "source_static_descriptor_only": True,
        "not_live_runtime_evidence": True,
        "runtime_binding_implemented": False,
        "ui_runtime_implemented": False,
        "operator_click_is_success": False,
        "sender_success_is_success": False,
        "build_success_is_success": False,
        "fixture_or_static_row_is_success": False,
        "accepted_state_ui_controls_enabled": False,
        "catalog_gate": CATALOG_GATE_ID,
        "live_echo_gate": LIVE_ECHO_GATE_ID,
        "current_wire_kind_allowed_by_schema": all(
            kind in catalog_checker.read_json(COMMAND_SCHEMA_PATH).get("command", {}).get("allowed_kinds", [])
            for kind in current_wire_kinds
        ),
    }


def build_control_descriptors(catalog: list[dict[str, Any]], catalog_checker: ModuleType) -> list[dict[str, Any]]:
    return [build_control_descriptor(entry, catalog_checker) for entry in catalog]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default="")
    args = parser.parse_args()

    issues: list[str] = []
    warnings = [
        "source-static UI/control descriptors only; no runtime UI binding is implemented",
        "accepted-state controls remain disabled until a future authoritative live command echo task",
    ]

    try:
        catalog_checker = load_operator_catalog_checker()
        catalog = catalog_checker.build_catalog()
    except Exception as exc:
        catalog_checker = None
        catalog = []
        issues.append(f"cannot load 018 operator catalog checker: {exc}")

    command_schema = read_json(COMMAND_SCHEMA_PATH)
    echo_schema = read_json(ECHO_SCHEMA_PATH)
    prior_017 = read_json(PRIOR_017_RETURN_PATH)
    prior_018 = read_json(PRIOR_018_RETURN_PATH)
    sender_source = read(SENDER_SOURCE)
    sender_header = read(SENDER_HEADER)
    state_source = read(STATE_SOURCE)
    state_header = read(STATE_HEADER)
    receiver_source = read(RECEIVER_SOURCE)
    receiver_header = read(RECEIVER_HEADER)
    control_descriptors = (
        build_control_descriptors(catalog, catalog_checker) if catalog_checker is not None else []
    )

    allowed_wire_kinds = set(command_schema.get("command", {}).get("allowed_kinds", []))
    forbidden_wire_kinds = set(command_schema.get("command", {}).get("forbidden_kinds", []))
    echo_authorities = set(echo_schema.get("ack_authority_values", []))
    echo_status_values = set(echo_schema.get("status_values", []))

    if command_schema.get("schema") != COMMAND_SCHEMA:
        issues.append("missing or invalid mosim.ue_command.v1 schema")
    if echo_schema.get("schema") != ECHO_SCHEMA:
        issues.append("missing or invalid mosim.ue_command_echo.v1 schema")
    if {"accepted", "rejected"} - echo_status_values:
        issues.append("echo schema must include accepted/rejected status values")
    if {"MWORKS", "ROS2", "MWORKS_ROS2"} - echo_authorities:
        issues.append("echo schema missing required authoritative ack authority values")
    if prior_017.get("request_id") != LIVE_ECHO_GATE_ID or prior_017.get("status") != "completed":
        issues.append("017 live echo gate return is missing or not completed")
    if prior_018.get("request_id") != CATALOG_GATE_ID or prior_018.get("status") != "completed":
        issues.append("018 operator command catalog return is missing or not completed")
    if prior_018.get("operator_command_catalog_summary", {}).get("checker_ok") is not True:
        issues.append("018 operator command catalog summary is not checker_ok=true")
    if not sender_source or not sender_header:
        issues.append("missing command sender source/header anchor")
    if not state_source or not state_header:
        issues.append("missing state component source/header anchor")
    if not receiver_source or not receiver_header:
        issues.append("missing command echo receiver shell source/header anchor")
    if STATE_PENDING_METHOD not in state_source + state_header:
        issues.append("state component missing pending command method")
    if "ApplyCommandEchoJson" not in state_source + state_header:
        issues.append("state component missing command echo sink method")
    if ECHO_SCHEMA not in state_source + receiver_source + receiver_header:
        issues.append("state/receiver source anchors missing echo schema guard")
    if "Result.bSent" not in sender_source:
        issues.append("sender source missing Result.bSent anchor for false-ack rejection")
    if "FUdpSocketReceiver" in receiver_source + receiver_header:
        issues.append("command echo receiver shell must not implement runtime UDP receiver in 019")

    catalog_kinds = {entry.get("command_kind") for entry in catalog}
    descriptor_kinds = {descriptor.get("command_kind") for descriptor in control_descriptors}
    descriptor_ids = [str(descriptor.get("control_descriptor_id", "")) for descriptor in control_descriptors]

    if catalog_kinds != MINIMUM_COMMAND_KINDS:
        issues.append("018 catalog command set does not match the required seven command kinds")
    if descriptor_kinds != MINIMUM_COMMAND_KINDS:
        issues.append("UI binding descriptor set does not match the required seven command kinds")
    if len(control_descriptors) != 7:
        issues.append("UI binding preflight must define exactly seven control descriptors")
    if len(descriptor_ids) != len(set(descriptor_ids)):
        issues.append("control_descriptor_id values must be unique")

    required_descriptor_fields = {
        "command_kind",
        "control_descriptor_id",
        "control_group",
        "display_intent",
        "domain_owner",
        "payload_contract",
        "default_state",
        "pending_source",
        "accepted_state_precondition",
        "required_echo_fields",
        "required_ack_authority_values",
        "forbidden_shortcut",
        "claim_boundary",
        "control_enabled_now",
        "accepted_state_allowed_now",
        "source_static_descriptor_only",
        "not_live_runtime_evidence",
    }

    runtime_claim_leaks = [key for key, value in FORBIDDEN_RUNTIME_CLAIMS.items() if value]
    if runtime_claim_leaks:
        issues.append("forbidden runtime claim flag(s) unexpectedly true: " + ", ".join(runtime_claim_leaks))

    base_required_echo_fields = [
        "schema=mosim.ue_command_echo.v1",
        "source",
        "ack_authority",
        "run_id",
        "request_id",
        "seq",
        "time_s",
        "status=accepted|rejected",
        "command.kind or command_kind",
        "matching pending request recorded from mosim.ue_command.v1",
        "no_pose_overwrite_status=pass",
    ]

    for descriptor in control_descriptors:
        command_kind = str(descriptor.get("command_kind", ""))
        missing = [
            field
            for field in sorted(required_descriptor_fields)
            if field not in descriptor or descriptor[field] in (None, "", [])
        ]
        if missing:
            issues.append(f"{command_kind} missing descriptor field(s): {', '.join(missing)}")
        if descriptor.get("default_state") != "disabled_pending_authoritative_echo":
            issues.append(f"{command_kind} must default to disabled_pending_authoritative_echo")
        if descriptor.get("control_enabled_now") is not False:
            issues.append(f"{command_kind} control must remain disabled now")
        if descriptor.get("accepted_state_allowed_now") is not False:
            issues.append(f"{command_kind} accepted state must remain disallowed now")
        if descriptor.get("source_static_descriptor_only") is not True:
            issues.append(f"{command_kind} must be source_static_descriptor_only")
        if descriptor.get("not_live_runtime_evidence") is not True:
            issues.append(f"{command_kind} must be marked not_live_runtime_evidence")
        if descriptor.get("runtime_binding_implemented") is not False:
            issues.append(f"{command_kind} runtime binding must not be implemented in 019")
        if descriptor.get("ui_runtime_implemented") is not False:
            issues.append(f"{command_kind} UI runtime must not be implemented in 019")
        if descriptor.get("accepted_state_ui_controls_enabled") is not False:
            issues.append(f"{command_kind} accepted-state UI controls must remain disabled")
        if STATE_PENDING_METHOD not in str(descriptor.get("pending_source")):
            issues.append(f"{command_kind} pending source must reference {STATE_PENDING_METHOD}")
        if COMMAND_SCHEMA not in str(descriptor.get("pending_source")):
            issues.append(f"{command_kind} pending source must reference {COMMAND_SCHEMA}")
        precondition = str(descriptor.get("accepted_state_precondition"))
        for required in [LIVE_ECHO_GATE_ID, ECHO_SCHEMA, STATE_PENDING_METHOD, "time_s", "no_pose_overwrite_status=pass"]:
            if required not in precondition:
                issues.append(f"{command_kind} accepted-state precondition missing {required}")
        for field in base_required_echo_fields:
            if field not in descriptor.get("required_echo_fields", []):
                issues.append(f"{command_kind} missing required echo field: {field}")
        for false_source in FALSE_ACK_SOURCES:
            if false_source not in descriptor.get("forbidden_shortcut", []):
                issues.append(f"{command_kind} missing false-ack rejection: {false_source}")
        if descriptor.get("operator_click_is_success") is not False:
            issues.append(f"{command_kind} operator click must not be success")
        if descriptor.get("sender_success_is_success") is not False:
            issues.append(f"{command_kind} sender success must not be success")
        if descriptor.get("build_success_is_success") is not False:
            issues.append(f"{command_kind} build success must not be success")
        if descriptor.get("fixture_or_static_row_is_success") is not False:
            issues.append(f"{command_kind} fixture/static row must not be success")
        current_wire = [
            kind
            for kind in [descriptor.get("current_wire_kind")]
            if kind
        ] + [str(kind) for kind in descriptor.get("current_wire_kind_options") or []]
        if not current_wire:
            issues.append(f"{command_kind} must map to at least one current wire kind")
        for kind in current_wire:
            if kind not in allowed_wire_kinds:
                issues.append(f"{command_kind} maps to unsupported current wire kind {kind!r}")
            if kind in forbidden_wire_kinds:
                issues.append(f"{command_kind} maps to forbidden wire kind {kind!r}")
        descriptor_blob = json.dumps(descriptor, ensure_ascii=False)
        if command_kind == "planner.switch":
            if "planner_ready" not in descriptor_blob:
                issues.append("planner.switch must explicitly reject planner_ready from UE")
            if "browser local-map review as RViz2 replacement" not in descriptor_blob:
                issues.append("planner.switch must reject browser local-map review as RViz2 replacement")
        if command_kind == "scene_map.switch":
            if "UE global truth map to planner" not in descriptor_blob:
                issues.append("scene_map.switch must reject UE global truth map to planner")
            if "visual-only level dropdown" not in descriptor_blob:
                issues.append("scene_map.switch must reject visual-only level dropdown acceptance")
        if command_kind == "experiment.run_control":
            if "does not prove controller/planner success" not in descriptor_blob:
                issues.append("experiment.run_control must not prove controller/planner success")
            if "closed_loop" not in descriptor_blob:
                issues.append("experiment.run_control must reject closed_loop implication")
        if command_kind == "manual_review.request":
            if "not automated acceptance" not in descriptor_blob:
                issues.append("manual_review.request must not imply automated/final acceptance")

    report = {
        "schema": "mosim.ue_console_ui_binding_preflight.v1",
        "ok": not issues,
        "task_id": TASK_ID,
        "scope_classification": "source-static",
        "checker_only_contract": True,
        "source_static_ui_binding_preflight": True,
        "not_live_runtime_evidence": True,
        "runtime_transport_implemented": False,
        "ui_runtime_implemented": False,
        "accepted_state_ui_controls_enabled": False,
        "catalog_to_control_gate": {
            "gate_id": TASK_ID,
            "source_catalog_gate": CATALOG_GATE_ID,
            "future_live_echo_gate": LIVE_ECHO_GATE_ID,
            "catalog_entries_required": sorted(MINIMUM_COMMAND_KINDS),
            "catalog_entries_present": sorted(str(kind) for kind in catalog_kinds),
            "control_descriptors_present": sorted(str(kind) for kind in descriptor_kinds),
            "pending_source": f"{STATE_PENDING_METHOD} from {COMMAND_SCHEMA}",
            "accepted_state_precondition_summary": (
                "Controls stay disabled/pending until a matching pending command and "
                "authoritative mosim.ue_command_echo.v1 row satisfy the 017 gate."
            ),
            "consumer_sink": STATE_ECHO_SINK,
        },
        "control_descriptors": control_descriptors,
        "descriptor_summary": {
            "total_descriptors": len(control_descriptors),
            "control_descriptor_ids": sorted(descriptor_ids),
            "control_groups": sorted({str(item.get("control_group")) for item in control_descriptors}),
            "all_default_disabled_pending_authoritative_echo": all(
                item.get("default_state") == "disabled_pending_authoritative_echo"
                for item in control_descriptors
            ),
            "all_controls_disabled_now": all(item.get("control_enabled_now") is False for item in control_descriptors),
            "all_accepted_state_disallowed_now": all(
                item.get("accepted_state_allowed_now") is False for item in control_descriptors
            ),
            "all_descriptors_source_static_only": all(
                item.get("source_static_descriptor_only") is True for item in control_descriptors
            ),
            "all_reject_operator_click_sender_build_fixture_success": all(
                item.get("operator_click_is_success") is False
                and item.get("sender_success_is_success") is False
                and item.get("build_success_is_success") is False
                and item.get("fixture_or_static_row_is_success") is False
                for item in control_descriptors
            ),
        },
        "schema_anchor_summary": {
            "command_schema": repo(COMMAND_SCHEMA_PATH),
            "echo_schema": repo(ECHO_SCHEMA_PATH),
            "current_allowed_wire_kinds": sorted(allowed_wire_kinds),
            "forbidden_wire_kinds": sorted(forbidden_wire_kinds),
            "echo_ack_authority_values": sorted(echo_authorities),
            "echo_status_values": sorted(echo_status_values),
        },
        "source_anchor_summary": {
            "operator_catalog_checker": repo(OPERATOR_CATALOG_CHECKER),
            "prior_018_return": {
                "path": repo(PRIOR_018_RETURN_PATH),
                "status": prior_018.get("status"),
                "quality_status": prior_018.get("quality_status"),
            },
            "prior_017_return": {
                "path": repo(PRIOR_017_RETURN_PATH),
                "status": prior_017.get("status"),
                "quality_status": prior_017.get("quality_status"),
            },
            "command_sender": {
                "header": repo(SENDER_HEADER),
                "source": repo(SENDER_SOURCE),
                "role": "mosim.ue_command.v1 sender only",
                "has_command_schema": COMMAND_SCHEMA in sender_source + sender_header,
                "has_send_success_anchor": "Result.bSent" in sender_source,
                "send_success_is_runtime_ack": False,
            },
            "state_component": {
                "header": repo(STATE_HEADER),
                "source": repo(STATE_SOURCE),
                "role": "pending command and command echo state reducer",
                "has_pending_method": STATE_PENDING_METHOD in state_source + state_header,
                "has_echo_sink": "ApplyCommandEchoJson" in state_source + state_header,
                "has_echo_schema_guard": ECHO_SCHEMA in state_source,
            },
            "command_echo_receiver_shell": {
                "header": repo(RECEIVER_HEADER),
                "source": repo(RECEIVER_SOURCE),
                "role": "source-static echo shell only; no runtime listener",
                "has_receiver_shell_entry": "ApplyCommandEchoJsonToState" in receiver_source + receiver_header,
                "has_echo_schema_guard": ECHO_SCHEMA in receiver_source + receiver_header,
                "runtime_udp_receiver_pattern_present": "FUdpSocketReceiver" in receiver_source + receiver_header,
            },
        },
        "false_ack_sources_rejected": FALSE_ACK_SOURCES,
        "future_live_ui_task_recommendation": {
            "recommended_next_scope": "separately authorized editor/runtime UI implementation only after live echo transport is authorized",
            "minimum_acceptance_gate": [
                "operator control emits mosim.ue_command.v1 for an allowed current wire kind",
                "state component records matching pending request by run_id/request_id/seq",
                "authoritative MWORKS/ROS2/MWORKS_ROS2 producer emits mosim.ue_command_echo.v1",
                "source and ack_authority match domain owner",
                "time_s and command identity are present",
                "status is accepted or rejected",
                "no_pose_overwrite_status=pass",
                "negative evidence rejects build/sender/fixture/static/operator-click rows as ack",
            ],
            "blocker_conditions": [
                "no authorized live echo producer/downlink surface",
                "attempt to enable accepted-state UI before authoritative echo evidence",
                "attempt to treat sender/build/pytest/checker/fixture/static/operator-click/frame rows as ack",
                "attempt to use keyboard/mouse/direct Actor transform to move UAV pose",
                "attempt to feed UE global truth map to planner or replace RViz2 with browser point-cloud review",
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
