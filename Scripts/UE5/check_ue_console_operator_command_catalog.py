#!/usr/bin/env python3
"""Check the UE Experiment Console operator command catalog contract.

This is a source/static checker only. It defines the RflySim-like operator
command catalog for future UI/runtime work, but it does not open Unreal,
implement UI, bind ports, run live transport, or prove live command ack.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
COMMAND_SCHEMA_PATH = ROOT / "Config/schemas/mosim_ue_command_v1.schema.json"
ECHO_SCHEMA_PATH = ROOT / "Config/schemas/mosim_ue_command_echo_v1.schema.json"
PRIOR_017_RETURN_PATH = (
    ROOT
    / "Results/agent_packets/returns/"
    / "RFLY-MOSIM-UE-CONSOLE-LIVE-ECHO-PRODUCER-CONSUMER-GATE-20260607-017.json"
)
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

TASK_ID = "RFLY-MOSIM-UE-CONSOLE-OPERATOR-COMMAND-CATALOG-SOURCE-STATIC-GATE-20260607-018"
LIVE_GATE_ID = "RFLY-MOSIM-UE-CONSOLE-LIVE-ECHO-PRODUCER-CONSUMER-GATE-20260607-017"
COMMAND_SCHEMA = "mosim.ue_command.v1"
ECHO_SCHEMA = "mosim.ue_command_echo.v1"
STATE_PENDING_METHOD = "RecordPendingCommandFromPacketJson"
STATE_ECHO_SINK = "UQuadrotorMworksExperimentConsoleStateComponent.ApplyCommandEchoJson"
RECEIVER_SHELL_ENTRY = (
    "UQuadrotorMworksExperimentConsoleCommandEchoReceiverComponent."
    "ApplyCommandEchoJsonToState"
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
DOMAIN_OWNERS = {"MWORKS", "ROS2", "UE", "PMO"}
AUTHORITATIVE_LIVE_SOURCES = {
    "MWORKS_live_downlink": "MWORKS",
    "ROS2_runtime_echo": "ROS2",
    "MWORKS_ROS2_live_downlink": "MWORKS_ROS2",
}
BASE_REQUIRED_ACK_EVIDENCE_FIELDS = [
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
GLOBAL_FORBIDDEN_SHORTCUTS = [
    "keyboard_pose",
    "mouse_pose",
    "actor_transform",
    "SetActorLocation",
    "SetActorTransform",
    "TeleportTo",
    "set_uav_pose",
    "pose_override",
    "fake_point_cloud",
    "fake_grid_map",
    "browser_point_cloud_review",
    "UE_truth_map_to_planner",
    "build_success",
    "UnrealBuildTool_success",
    "pytest_success",
    "checker_success",
    "udp_send_success",
    "sender_result_bSent",
    "quadrotor.unreal_state.frame",
    "fixture_only_echo",
    "offline_source_preflight_smoke_row",
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


def present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value)
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def build_ack_fields(*extra: str) -> list[str]:
    fields = list(BASE_REQUIRED_ACK_EVIDENCE_FIELDS)
    fields.extend(extra)
    return fields


def accepted_precondition(command_kind: str) -> str:
    return (
        f"{command_kind} remains pending/disabled until {STATE_PENDING_METHOD} records "
        f"a matching {COMMAND_SCHEMA} request and a future authoritative {ECHO_SCHEMA} "
        f"row passes {LIVE_GATE_ID} with source/ack_authority, identity, time_s, "
        "accepted|rejected status, and no_pose_overwrite_status=pass."
    )


def catalog_entry(
    *,
    command_kind: str,
    domain_owner: str,
    current_wire_kind: str | None = None,
    current_wire_kind_options: list[str] | None = None,
    payload_contract: list[str],
    ack_authorities: list[str],
    live_sources: list[str],
    requires_mworks_ack: bool,
    requires_ros2_ack: bool,
    claim_boundary: str,
    domain_ack_fields: list[str],
    extra_forbidden_shortcuts: list[str] | None = None,
    source_static_note: str = "",
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "command_kind": command_kind,
        "operator_catalog_label": command_kind,
        "command_kind_status": "source_static_operator_catalog_label",
        "domain_owner": domain_owner,
        "payload_contract": payload_contract,
        "required_ack_evidence_fields": build_ack_fields(*domain_ack_fields),
        "required_ack_authority_values": ack_authorities,
        "required_live_source_options": live_sources,
        "forbidden_shortcut": sorted(set(GLOBAL_FORBIDDEN_SHORTCUTS + (extra_forbidden_shortcuts or []))),
        "accepted_state_precondition": accepted_precondition(command_kind),
        "claim_boundary": claim_boundary,
        "guard_contract": {
            "require_mworks_ack": requires_mworks_ack,
            "require_ros2_ack": requires_ros2_ack,
            "reject_if_gate_open": [LIVE_GATE_ID, "manual_review_gate_open_when_required"],
        },
        "requires_mworks_ack": requires_mworks_ack,
        "requires_ros2_ack": requires_ros2_ack,
        "accepted_state_allowed_now": False,
        "ui_control_enabled_now": False,
        "source_static_catalog_only": True,
        "not_live_runtime_ack": True,
        "source_static_note": source_static_note,
    }
    if current_wire_kind is not None:
        entry["current_wire_kind"] = current_wire_kind
    if current_wire_kind_options is not None:
        entry["current_wire_kind_options"] = current_wire_kind_options
    return entry


def build_catalog() -> list[dict[str, Any]]:
    return [
        catalog_entry(
            command_kind="motor_fault.inject_or_clear",
            domain_owner="MWORKS",
            current_wire_kind="motor_fault",
            payload_contract=[
                "motor_id or rotor_index",
                "fault_mode",
                "severity",
                "start_time_s",
                "duration_s or clear flag",
            ],
            ack_authorities=["MWORKS"],
            live_sources=["MWORKS_live_downlink"],
            requires_mworks_ack=True,
            requires_ros2_ack=False,
            claim_boundary=(
                "UE may request and display the command state, but MWORKS decides "
                "dynamics/control effect and metrics."
            ),
            domain_ack_fields=[
                "MWORKS fault wrapper echo",
                "fault command accepted/rejected reason",
                "MWORKS event log or metrics bundle reference for later effect review",
            ],
            extra_forbidden_shortcuts=["UE-side rotor visual disable as fault evidence"],
        ),
        catalog_entry(
            command_kind="disturbance.wind.set_or_clear",
            domain_owner="MWORKS",
            current_wire_kind="wind_profile",
            payload_contract=[
                "wind_vector or profile_id",
                "frame",
                "start_time_s",
                "duration_s",
            ],
            ack_authorities=["MWORKS"],
            live_sources=["MWORKS_live_downlink"],
            requires_mworks_ack=True,
            requires_ros2_ack=False,
            claim_boundary=(
                "UE may visualize wind intent; MWORKS owns physics truth and controller effect."
            ),
            domain_ack_fields=[
                "MWORKS wind/disturbance adapter echo",
                "wind command accepted/rejected reason",
                "MWORKS run/event evidence for later disturbance effect review",
            ],
            extra_forbidden_shortcuts=["UE visual wind arrow as physics truth"],
        ),
        catalog_entry(
            command_kind="controller.switch",
            domain_owner="MWORKS",
            current_wire_kind="controller_select",
            payload_contract=[
                "controller_id",
                "switch_time_s",
                "safe_transition_policy",
            ],
            ack_authorities=["MWORKS"],
            live_sources=["MWORKS_live_downlink"],
            requires_mworks_ack=True,
            requires_ros2_ack=False,
            claim_boundary=(
                "UE may expose operator choice; MWORKS owns controller execution and performance evidence."
            ),
            domain_ack_fields=[
                "MWORKS controller adapter echo",
                "controller switch accepted/rejected reason",
                "MWORKS controller mode/event evidence for later performance review",
            ],
            extra_forbidden_shortcuts=["UE label-only controller mode as active controller"],
        ),
        catalog_entry(
            command_kind="planner.switch",
            domain_owner="ROS2",
            current_wire_kind="planner_select",
            payload_contract=[
                "planner_id",
                "switch_time_s",
                "review_mode",
            ],
            ack_authorities=["ROS2"],
            live_sources=["ROS2_runtime_echo"],
            requires_mworks_ack=True,
            requires_ros2_ack=True,
            claim_boundary=(
                "UE may expose operator choice; ROS2/RViz2 owns planner topic/runtime evidence. "
                "No planner_ready claim from UE."
            ),
            domain_ack_fields=[
                "ROS2 planner adapter echo",
                "planner switch accepted/rejected reason",
                "ROS2 topic/review evidence reference for later planner review",
            ],
            extra_forbidden_shortcuts=[
                "UE label-only planner mode as planner_ready",
                "browser local-map review as RViz2 replacement",
            ],
        ),
        catalog_entry(
            command_kind="scene_map.switch",
            domain_owner="UE",
            current_wire_kind="scene_switch",
            payload_contract=[
                "scene_id or map_id",
                "loading_policy",
                "review_gate",
            ],
            ack_authorities=["MWORKS_ROS2"],
            live_sources=["MWORKS_ROS2_live_downlink"],
            requires_mworks_ack=True,
            requires_ros2_ack=True,
            claim_boundary=(
                "UE owns rendering scene/map selection and sensor-oracle context; it must not "
                "feed global truth map to planner."
            ),
            domain_ack_fields=[
                "UE scene/map load state",
                "MWORKS scenario binding echo",
                "ROS2 topic/scene contract echo when planner or perception is touched",
            ],
            extra_forbidden_shortcuts=[
                "visual-only level dropdown as simulation scene acceptance",
                "UE global truth map to planner",
            ],
        ),
        catalog_entry(
            command_kind="experiment.run_control",
            domain_owner="PMO",
            current_wire_kind_options=["scenario_reset", "start_goal_update", "recording"],
            payload_contract=[
                "run_id",
                "action",
                "target_domain",
                "evidence_policy",
            ],
            ack_authorities=["MWORKS_ROS2"],
            live_sources=["MWORKS_ROS2_live_downlink"],
            requires_mworks_ack=True,
            requires_ros2_ack=True,
            claim_boundary=(
                "Run control coordinates surfaces; it does not prove controller/planner success."
            ),
            domain_ack_fields=[
                "PMO run packet or evidence bundle reference",
                "MWORKS run-state echo when dynamics/control is touched",
                "ROS2 run-state echo when planner/perception is touched",
            ],
            extra_forbidden_shortcuts=[
                "start button as closed_loop evidence",
                "recording started as mission success",
            ],
        ),
        catalog_entry(
            command_kind="manual_review.request",
            domain_owner="PMO",
            current_wire_kind="recording",
            payload_contract=[
                "review_target",
                "artifact_type",
                "blocking_policy",
            ],
            ack_authorities=["MWORKS_ROS2"],
            live_sources=["MWORKS_ROS2_live_downlink"],
            requires_mworks_ack=True,
            requires_ros2_ack=True,
            claim_boundary="Manual review opens or reports evidence; it is not automated acceptance.",
            domain_ack_fields=[
                "manual review packet path or display request id",
                "review target and artifact type",
                "human review verdict required when blocking_policy requires it",
            ],
            extra_forbidden_shortcuts=[
                "manual review request as final UI acceptance",
                "screenshot path alone as visual acceptance",
            ],
            source_static_note=(
                "Current wire kind uses recording/evidence request shape only; final manual-review "
                "UI binding remains a future task."
            ),
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default="")
    args = parser.parse_args()

    issues: list[str] = []
    warnings = [
        "operator catalog command_kind labels are source-static contract labels, not current UI controls",
        "dotted catalog labels map to current base mosim.ue_command.v1 wire kinds where possible",
        "accepted-state UI remains disabled until a future authoritative live echo task passes 017",
    ]

    command_schema = read_json(COMMAND_SCHEMA_PATH)
    echo_schema = read_json(ECHO_SCHEMA_PATH)
    prior_017 = read_json(PRIOR_017_RETURN_PATH)
    sender_source = read(SENDER_SOURCE)
    sender_header = read(SENDER_HEADER)
    state_source = read(STATE_SOURCE)
    state_header = read(STATE_HEADER)
    receiver_source = read(RECEIVER_SOURCE)
    receiver_header = read(RECEIVER_HEADER)
    catalog = build_catalog()

    allowed_wire_kinds = set(command_schema.get("command", {}).get("allowed_kinds", []))
    forbidden_wire_kinds = set(command_schema.get("command", {}).get("forbidden_kinds", []))
    echo_authorities = set(echo_schema.get("ack_authority_values", []))
    echo_status_values = set(echo_schema.get("status_values", []))

    if command_schema.get("schema") != COMMAND_SCHEMA:
        issues.append("missing or invalid mosim.ue_command.v1 schema")
    if echo_schema.get("schema") != ECHO_SCHEMA:
        issues.append("missing or invalid mosim.ue_command_echo.v1 schema")
    if not {"accepted", "rejected"} <= echo_status_values:
        issues.append("echo schema must include accepted and rejected status values")
    if not {"MWORKS", "ROS2", "MWORKS_ROS2"} <= echo_authorities:
        issues.append("echo schema missing required authoritative ack authority values")
    if prior_017.get("request_id") != LIVE_GATE_ID or prior_017.get("status") != "completed":
        issues.append("017 live echo producer/consumer return packet is missing or not completed")
    if ECHO_SCHEMA not in json.dumps(prior_017, ensure_ascii=False):
        issues.append("017 return does not reference mosim.ue_command_echo.v1")
    if STATE_ECHO_SINK not in json.dumps(prior_017, ensure_ascii=False):
        issues.append("017 return does not fix the state component echo sink")
    for field in BASE_REQUIRED_ACK_EVIDENCE_FIELDS:
        if field not in json.dumps(prior_017, ensure_ascii=False):
            issues.append(f"017 return missing required future live evidence field: {field}")

    if not sender_source or not sender_header:
        issues.append("missing command sender source/header anchor")
    if not state_source or not state_header:
        issues.append("missing state component source/header anchor")
    if not receiver_source or not receiver_header:
        issues.append("missing command echo receiver shell source/header anchor")
    for kind in sorted(allowed_wire_kinds):
        if f'TEXT("{kind}")' not in sender_source:
            issues.append(f"command sender source missing current base wire kind: {kind}")
    if ECHO_SCHEMA not in state_source:
        issues.append("state component source missing mosim.ue_command_echo.v1 guard")
    if STATE_PENDING_METHOD not in state_source + state_header:
        issues.append("state component missing pending command method")
    if "ApplyCommandEchoJson" not in state_source + state_header:
        issues.append("state component missing command echo sink method")
    if ECHO_SCHEMA not in receiver_source + receiver_header:
        issues.append("receiver shell source missing mosim.ue_command_echo.v1 guard")

    catalog_kinds = {entry["command_kind"] for entry in catalog}
    if catalog_kinds != MINIMUM_COMMAND_KINDS:
        issues.append(
            "catalog command kind set does not match the 018 minimum: "
            + ", ".join(sorted(MINIMUM_COMMAND_KINDS - catalog_kinds))
        )

    required_entry_fields = {
        "command_kind",
        "domain_owner",
        "payload_contract",
        "required_ack_evidence_fields",
        "forbidden_shortcut",
        "accepted_state_precondition",
        "claim_boundary",
        "accepted_state_allowed_now",
        "requires_mworks_ack",
        "requires_ros2_ack",
    }
    runtime_claim_leaks = [key for key, value in FORBIDDEN_RUNTIME_CLAIMS.items() if value]
    if runtime_claim_leaks:
        issues.append("forbidden runtime claim flag(s) unexpectedly true: " + ", ".join(runtime_claim_leaks))

    entries_with_current_wire_support: list[str] = []
    catalog_only_labels: list[str] = []
    for entry in catalog:
        missing_fields = [
            field
            for field in sorted(required_entry_fields)
            if field not in entry or not present(entry[field])
        ]
        if missing_fields:
            issues.append(f"{entry.get('command_kind', '<unknown>')} missing field(s): {', '.join(missing_fields)}")
        command_kind = str(entry["command_kind"])
        domain_owner = str(entry["domain_owner"])
        if domain_owner not in DOMAIN_OWNERS:
            issues.append(f"{command_kind} has invalid domain_owner {domain_owner!r}")
        if command_kind in forbidden_wire_kinds or any(blocked in command_kind for blocked in forbidden_wire_kinds):
            issues.append(f"{command_kind} overlaps forbidden command kind")
        for kind in wire_kinds(entry):
            if kind not in allowed_wire_kinds:
                issues.append(f"{command_kind} maps to unsupported current wire kind {kind!r}")
            else:
                entries_with_current_wire_support.append(command_kind)
        if command_kind not in allowed_wire_kinds:
            catalog_only_labels.append(command_kind)
        if entry["accepted_state_allowed_now"] is not False:
            issues.append(f"{command_kind} may allow accepted state now")
        if entry.get("ui_control_enabled_now") is not False:
            issues.append(f"{command_kind} UI control must remain disabled now")
        if entry.get("not_live_runtime_ack") is not True:
            issues.append(f"{command_kind} must be marked not_live_runtime_ack")
        if LIVE_GATE_ID not in entry["accepted_state_precondition"]:
            issues.append(f"{command_kind} accepted-state precondition must reference 017 gate")
        if ECHO_SCHEMA not in entry["accepted_state_precondition"]:
            issues.append(f"{command_kind} accepted-state precondition must reference echo schema")
        if STATE_PENDING_METHOD not in entry["accepted_state_precondition"]:
            issues.append(f"{command_kind} accepted-state precondition must require pending command source")
        for evidence_field in BASE_REQUIRED_ACK_EVIDENCE_FIELDS:
            if evidence_field not in entry["required_ack_evidence_fields"]:
                issues.append(f"{command_kind} missing ack/evidence field: {evidence_field}")
        for shortcut in GLOBAL_FORBIDDEN_SHORTCUTS:
            if shortcut not in entry["forbidden_shortcut"]:
                issues.append(f"{command_kind} missing forbidden shortcut: {shortcut}")
        if domain_owner == "MWORKS":
            if "MWORKS" not in entry["required_ack_authority_values"]:
                issues.append(f"{command_kind} must require MWORKS ack authority")
            if entry["requires_mworks_ack"] is not True:
                issues.append(f"{command_kind} must require MWORKS ack")
        if domain_owner == "ROS2":
            if "ROS2" not in entry["required_ack_authority_values"]:
                issues.append(f"{command_kind} must require ROS2 ack authority")
            if entry["requires_ros2_ack"] is not True:
                issues.append(f"{command_kind} must require ROS2 ack")
        if command_kind == "scene_map.switch":
            joined = json.dumps(entry, ensure_ascii=False)
            if "UE global truth map to planner" not in joined and "global truth map to planner" not in joined:
                issues.append("scene_map.switch must forbid feeding UE truth map to planner")
            if "sensor-oracle context" not in joined:
                issues.append("scene_map.switch must keep UE claim boundary to scene/sensor oracle context")
        if command_kind == "planner.switch" and "planner_ready" not in json.dumps(entry, ensure_ascii=False):
            issues.append("planner.switch must explicitly reject planner_ready claim from UE")
        if command_kind == "manual_review.request" and "not automated acceptance" not in entry["claim_boundary"]:
            issues.append("manual_review.request must not be automated acceptance")

    report = {
        "schema": "mosim.ue_console_operator_command_catalog.v1",
        "ok": not issues,
        "task_id": TASK_ID,
        "scope_classification": "source-static",
        "checker_only_contract": True,
        "not_live_runtime_evidence": True,
        "accepted_state_ui_controls_enabled": False,
        "runtime_transport_implemented": False,
        "umg_blueprint_slate_or_web_ui_implemented": False,
        "operator_catalog_gate": {
            "gate_id": TASK_ID,
            "prior_live_echo_gate": LIVE_GATE_ID,
            "accepted_state_precondition_summary": (
                f"Every catalog command remains pending/disabled until a matching {COMMAND_SCHEMA} "
                f"pending request and a future authoritative {ECHO_SCHEMA} row pass 017."
            ),
            "consumer_sink": STATE_ECHO_SINK,
            "receiver_shell_entry": RECEIVER_SHELL_ENTRY,
            "catalog_entries_required": sorted(MINIMUM_COMMAND_KINDS),
            "catalog_entries_present": sorted(catalog_kinds),
        },
        "catalog_entries": catalog,
        "catalog_summary": {
            "total_entries": len(catalog),
            "domain_owner_counts": {
                owner: sum(1 for entry in catalog if entry["domain_owner"] == owner)
                for owner in sorted(DOMAIN_OWNERS)
            },
            "entries_with_current_wire_support": sorted(set(entries_with_current_wire_support)),
            "catalog_only_operator_labels": sorted(catalog_only_labels),
            "current_wire_kinds_used": sorted({kind for entry in catalog for kind in wire_kinds(entry)}),
            "current_wire_kind_options_only": [
                entry["command_kind"] for entry in catalog if "current_wire_kind_options" in entry
            ],
            "all_entries_disable_accepted_state_now": all(
                entry["accepted_state_allowed_now"] is False for entry in catalog
            ),
            "all_entries_require_017_gate": all(
                LIVE_GATE_ID in entry["accepted_state_precondition"] for entry in catalog
            ),
            "all_entries_reject_global_shortcuts": all(
                set(GLOBAL_FORBIDDEN_SHORTCUTS) <= set(entry["forbidden_shortcut"])
                for entry in catalog
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
            "command_sender": {
                "header": repo(SENDER_HEADER),
                "source": repo(SENDER_SOURCE),
                "role": "current mosim.ue_command.v1 sender only",
                "has_component": "UQuadrotorMworksUdpCommandSenderComponent" in sender_source + sender_header,
                "supported_wire_kinds_present": sorted(
                    kind for kind in allowed_wire_kinds if f'TEXT("{kind}")' in sender_source
                ),
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
            },
            "prior_017_return": {
                "path": repo(PRIOR_017_RETURN_PATH),
                "status": prior_017.get("status"),
                "gate_status": prior_017.get("live_echo_producer_consumer_gate_summary", {}).get("gate_status"),
            },
        },
        "future_live_ui_task_recommendation": {
            "recommended_next_scope": "source-static UI binding catalog-to-control checker, then separately authorized editor/runtime UI work",
            "minimum_future_live_acceptance_gate": [
                "operator action emits mosim.ue_command.v1 with a catalog entry mapped to an allowed base wire kind",
                "state component records matching pending request by run_id/request_id/seq",
                "authorized MWORKS/ROS2/MWORKS_ROS2 producer emits mosim.ue_command_echo.v1",
                "source matches ack_authority and domain owner",
                "time_s and command identity are present",
                "status is accepted or rejected",
                "no_pose_overwrite_status=pass",
                "negative evidence rejects build, sender, fixture, frame, source, and preflight rows as ack",
            ],
            "blocker_conditions": [
                "future work needs Unreal Editor/runtime without explicit PMO runtime authorization",
                "future work tries to enable accepted-state UI before authoritative echo evidence",
                "future work treats sender success, UBT/build success, pytest/checker success, fixture rows, or quadrotor.unreal_state frames as ack",
                "future work uses keyboard/mouse/direct Actor transform to move UAV pose",
                "future work feeds UE global truth map to planner or uses browser point-cloud review as RViz2 replacement",
            ],
        },
        "forbidden_shortcuts_global": GLOBAL_FORBIDDEN_SHORTCUTS,
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
