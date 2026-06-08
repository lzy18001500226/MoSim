#!/usr/bin/env python3
"""Validate visible-department return/blocker packets for planning and evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PLANNING_FIELDS = [
    "department_local_goal",
    "critical_path_steps",
    "parallelizable_slices",
    "subagent_plan",
    "subagent_plan_reason",
    "subagents_used",
    "verification_gates",
    "manual_review_or_blocker_triggers",
]

SUBAGENT_PLAN_VALUES = {"used", "available_but_not_useful", "unavailable", "unsafe"}

SEMANTIC_BOUNDARY_REQUIRED_FIELDS = [
    "decision_scope",
    "state_class",
    "evidence_minimum",
    "allowed_actions",
    "forbidden_actions",
    "stop_triggers",
    "next_owner",
]

DECISION_SCOPES = {
    "visible_thread",
    "mworks_window_patrol",
    "mworks_live_task",
    "ros2_runtime",
    "ue_runtime",
    "asset_review",
    "other",
}

VISIBLE_THREAD_STATES = {
    "routable",
    "busy_in_progress",
    "dispatch_needed",
    "idle_blocked_by_open_dependency",
    "approval_pending_or_ui_blocked",
    "provider_gateway_or_pending_review",
    "dispatch_surface_or_agent_loop_failure",
    "context_compression_surface",
    "unknown_blocked",
}

MWORKS_STATES = {
    "window_patrol_clean",
    "helper_only_nonblocking",
    "login_or_license_blocked",
    "authorization_blocked",
    "gui_error_blocked",
    "visible_unknown_blocked",
    "live_attach_blocked",
    "unknown_blocked",
}

FREE_TEXT_ONLY_STATES = {
    "ok",
    "normal",
    "healthy",
    "looks fine",
    "still running",
    "probably blocked",
}

CONTROL_PLANE_ONLY_HINTS = {
    "json",
    "packet",
    "ledger",
    "progress",
    "progress.md",
    "task packet",
    "return packet",
    "blocker packet",
}

CONTROL_PLANE_ALLOWED_CLASSES = {
    "diagnostic_only",
    "rule_sync_only",
    "preflight_drill_only",
    "dispatch_surface_diagnostic",
    "static_inventory_only",
    "static_diagnosis",
    "static_only",
}


def _load_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - argparse handles user display
        raise SystemExit(f"failed to parse JSON: {path}: {exc}") from exc


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return bool(value)
    return True


def _get_task_class(packet: dict[str, Any]) -> str:
    for key in ("task_class", "evidence_class", "work_class", "result_class"):
        value = packet.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _control_plane_exception(packet: dict[str, Any]) -> bool:
    task_class = _get_task_class(packet)
    if task_class in CONTROL_PLANE_ALLOWED_CLASSES:
        return True
    flags = packet.get("control_plane_only_allowed")
    return flags is True


def _normalise_outputs(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, dict):
        return [f"{key}: {value[key]}" for key in value]
    return [str(value)]


def _is_non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and any(isinstance(item, str) and item.strip() for item in value)


def _semantic_boundary(packet: dict[str, Any]) -> dict[str, Any] | None:
    boundary = packet.get("semantic_boundary")
    if isinstance(boundary, dict):
        return boundary
    metadata = packet.get("metadata")
    if isinstance(metadata, dict) and isinstance(metadata.get("semantic_boundary"), dict):
        return metadata["semantic_boundary"]
    return None


def _validate_semantic_boundary(packet: dict[str, Any]) -> list[str]:
    boundary = _semantic_boundary(packet)
    if boundary is None:
        return ["missing required semantic_boundary"]

    errors: list[str] = []
    for field in SEMANTIC_BOUNDARY_REQUIRED_FIELDS:
        value = boundary.get(field)
        if field in {"evidence_minimum", "allowed_actions", "forbidden_actions", "stop_triggers"}:
            if not _is_non_empty_list(value):
                errors.append(f"semantic_boundary.{field} must be a non-empty list")
        elif not isinstance(value, str) or not value.strip():
            errors.append(f"semantic_boundary.{field} must be a non-empty string")

    decision_scope = str(boundary.get("decision_scope", ""))
    state_class = str(boundary.get("state_class", ""))
    if decision_scope and decision_scope not in DECISION_SCOPES:
        errors.append(f"semantic_boundary.decision_scope unknown: {decision_scope}")
    if state_class.casefold() in FREE_TEXT_ONLY_STATES:
        errors.append(f"semantic_boundary.state_class is free-text-only: {state_class}")
    if decision_scope == "visible_thread" and state_class and state_class not in VISIBLE_THREAD_STATES:
        errors.append(f"semantic_boundary.state_class unknown for visible_thread: {state_class}")
    if decision_scope in {"mworks_window_patrol", "mworks_live_task"} and state_class and state_class not in MWORKS_STATES:
        errors.append(f"semantic_boundary.state_class unknown for MWORKS: {state_class}")
    return errors


def validate(packet: dict[str, Any], *, strict_completed_outputs: bool) -> list[str]:
    errors: list[str] = []

    for field in PLANNING_FIELDS:
        if field == "subagents_used":
            if field not in packet:
                errors.append(f"missing required planning field: {field}")
            continue
        if not _is_present(packet.get(field)):
            errors.append(f"missing required planning field: {field}")

    subagent_plan = packet.get("subagent_plan")
    if subagent_plan and not isinstance(subagent_plan, str):
        errors.append(
            "subagent_plan must be a string enum, not "
            + type(subagent_plan).__name__
        )
    elif subagent_plan and subagent_plan not in SUBAGENT_PLAN_VALUES:
        errors.append(
            "subagent_plan must be one of "
            + ", ".join(sorted(SUBAGENT_PLAN_VALUES))
            + f"; got {subagent_plan!r}"
        )

    if packet.get("subagent_plan") != "used":
        subagents_used = packet.get("subagents_used")
        if subagents_used not in ([], None) and not isinstance(subagents_used, list):
            errors.append("subagents_used must be a list")
        if not _is_present(packet.get("subagent_plan_reason")):
            errors.append("subagent_plan_reason is required when subagent_plan is not used")

    status = str(packet.get("status", "")).lower()
    completed_like = status in {"completed", "complete", "done", "success", "succeeded"}

    outputs = _normalise_outputs(packet.get("actual_engineering_outputs"))
    if completed_like and strict_completed_outputs and not _control_plane_exception(packet):
        if not outputs:
            errors.append("completed packet missing actual_engineering_outputs")
        else:
            meaningful = []
            for item in outputs:
                lowered = item.lower()
                if not any(hint in lowered for hint in CONTROL_PLANE_ONLY_HINTS):
                    meaningful.append(item)
            if not meaningful:
                errors.append(
                    "completed packet actual_engineering_outputs appears control-plane only"
                )

    if completed_like and not _is_present(packet.get("claim_boundary")):
        errors.append("completed packet missing claim_boundary")

    if "blocker" in status or status == "blocked":
        if not (
            _is_present(packet.get("blocker_summary"))
            or _is_present(packet.get("blocker"))
            or _is_present(packet.get("summary"))
        ):
            errors.append("blocked packet missing blocker summary")

    errors.extend(_validate_semantic_boundary(packet))

    return errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path)
    parser.add_argument(
        "--allow-control-plane-only",
        action="store_true",
        help="Allow completed packets whose task_class/evidence_class is diagnostic/rule-sync/preflight/static inventory.",
    )
    parser.add_argument("--json-output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    packet = _load_json(args.packet)
    errors = validate(packet, strict_completed_outputs=not args.allow_control_plane_only)
    result = {
        "ok": not errors,
        "packet": str(args.packet),
        "errors": errors,
    }
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    if errors:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
