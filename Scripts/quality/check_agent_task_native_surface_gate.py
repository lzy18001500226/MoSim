#!/usr/bin/env python3
"""Validate that a MoSim task packet records the native Codex surface gate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

ALLOWED_SURFACES = {
    "native_hook",
    "agents_md",
    "workflow_or_skill",
    "mcp_app_plugin",
    "browser_computer_use",
    "visible_thread",
    "subagent",
    "isolated_worktree",
    "codex_review",
    "codex_exec",
    "automation_thread_wakeup",
    "wechat_gateway",
    "agent_packet_glue",
    "local_pmo",
}

RETURN_PATH_SURFACES = {
    "visible_thread",
    "subagent",
    "codex_exec",
    "automation_thread_wakeup",
    "agent_packet_glue",
}

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
    "approval_pending_or_ui_blocked",
    "provider_gateway_or_pending_review",
    "dispatch_surface_or_agent_loop_failure",
    "context_compression_surface",
    "unknown_blocked",
}

DISPATCH_READINESS_STATES = {
    "busy_in_progress",
    "idle_needs_dispatch",
    "idle_blocked_by_open_dependency",
    "idle_no_ready_task",
    "idle_waiting_review_or_approval",
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

MWORKS_TARGET_FIELDS = [
    "target_department",
    "target_thread",
    "owner",
    "assigned_department",
]

MWORKS_TARGET_MARKERS = [
    "mworks",
    "sysplorer",
    "syslab",
    "sysblock",
    "mworks动力学",
    "mworks控制",
]

LEASE_MINIMUM_FIELDS = {
    "request_id",
    "target_thread_id",
    "nonce",
    "started_at",
    "last_checkpoint_at",
    "current_phase",
    "next_checkpoint_due_at",
}

ARTIFACT_TYPES = {
    "runtime_lease",
    "checkpoint_packet",
    "return_packet",
    "blocker_packet",
    "notes_file",
    "output_scaffold",
    "other",
}


def _project_relative(path_text: str) -> bool:
    path = Path(path_text)
    if path.is_absolute():
        try:
            resolved = path.resolve()
        except OSError:
            return False
        return resolved == ROOT.resolve() or ROOT.resolve() in resolved.parents
    return not any(part == ".." for part in path.parts)


def _as_surface_set(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value} if value else set()
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str) and item}
    return set()


def _native_gate(packet: dict[str, Any]) -> dict[str, Any] | None:
    gate = packet.get("native_surface_gate")
    if isinstance(gate, dict):
        return gate
    metadata = packet.get("metadata")
    if isinstance(metadata, dict) and isinstance(metadata.get("native_surface_gate"), dict):
        return metadata["native_surface_gate"]
    return None


def _semantic_boundary(packet: dict[str, Any]) -> dict[str, Any] | None:
    boundary = packet.get("semantic_boundary")
    if isinstance(boundary, dict):
        return boundary
    metadata = packet.get("metadata")
    if isinstance(metadata, dict) and isinstance(metadata.get("semantic_boundary"), dict):
        return metadata["semantic_boundary"]
    return None


def _is_non_empty_list(value: Any) -> bool:
    return isinstance(value, list) and any(isinstance(item, str) and item.strip() for item in value)


def _check_semantic_boundary(packet: dict[str, Any]) -> list[dict[str, str]]:
    boundary = _semantic_boundary(packet)
    if boundary is None:
        return [
            {
                "field": "semantic_boundary",
                "reason": "missing_semantic_boundary",
                "message": "Task packet must declare decision_scope, state_class, evidence_minimum, allowed_actions, forbidden_actions, stop_triggers, and next_owner.",
            }
        ]

    findings: list[dict[str, str]] = []
    for field in SEMANTIC_BOUNDARY_REQUIRED_FIELDS:
        value = boundary.get(field)
        if field in {"evidence_minimum", "allowed_actions", "forbidden_actions", "stop_triggers"}:
            if not _is_non_empty_list(value):
                findings.append(
                    {
                        "field": f"semantic_boundary.{field}",
                        "reason": f"missing_{field}",
                        "message": f"{field} must be a non-empty list of concrete strings.",
                    }
                )
        elif not isinstance(value, str) or not value.strip():
            findings.append(
                {
                    "field": f"semantic_boundary.{field}",
                    "reason": f"missing_{field}",
                    "message": f"{field} must be a non-empty string.",
                }
            )

    decision_scope = str(boundary.get("decision_scope", ""))
    state_class = str(boundary.get("state_class", ""))
    if decision_scope and decision_scope not in DECISION_SCOPES:
        findings.append(
            {
                "field": "semantic_boundary.decision_scope",
                "reason": "unknown_decision_scope",
                "message": decision_scope,
            }
        )
    if state_class.casefold() in FREE_TEXT_ONLY_STATES:
        findings.append(
            {
                "field": "semantic_boundary.state_class",
                "reason": "free_text_only_state_class",
                "message": state_class,
            }
        )
    if decision_scope == "visible_thread" and state_class and state_class not in VISIBLE_THREAD_STATES:
        findings.append(
            {
                "field": "semantic_boundary.state_class",
                "reason": "unknown_visible_thread_state_class",
                "message": state_class,
            }
        )
    readiness = packet.get("dispatch_readiness")
    if readiness is not None:
        if not isinstance(readiness, str) or not readiness.strip():
            findings.append(
                {
                    "field": "dispatch_readiness",
                    "reason": "invalid_dispatch_readiness",
                    "message": "dispatch_readiness must be a non-empty string when present",
                }
            )
        elif readiness not in DISPATCH_READINESS_STATES:
            findings.append(
                {
                    "field": "dispatch_readiness",
                    "reason": "unknown_dispatch_readiness",
                    "message": readiness,
                }
            )
    if decision_scope in {"mworks_window_patrol", "mworks_live_task"} and state_class and state_class not in MWORKS_STATES:
        findings.append(
            {
                "field": "semantic_boundary.state_class",
                "reason": "unknown_mworks_state_class",
                "message": state_class,
            }
        )
    return findings


def _looks_like_mworks_department_packet(packet: dict[str, Any]) -> bool:
    target_text = "\n".join(
        str(packet.get(field, "")) for field in MWORKS_TARGET_FIELDS if packet.get(field)
    ).casefold()
    return any(marker.casefold() in target_text for marker in MWORKS_TARGET_MARKERS)


def _check_durable_start_requirement(
    packet: dict[str, Any],
    *,
    visible_thread_dispatch: bool,
) -> list[dict[str, str]]:
    requirement = packet.get("durable_start_requirement")
    if not isinstance(requirement, dict):
        if visible_thread_dispatch:
            return [
                {
                    "field": "durable_start_requirement",
                    "reason": "missing_durable_start_requirement",
                    "message": "Visible-thread dispatch packets must declare a first durable-start artifact, or an explicit exact no-write probe exemption.",
                }
            ]
        return []

    findings: list[dict[str, str]] = []
    required = requirement.get("required")
    if not isinstance(required, bool):
        findings.append(
            {
                "field": "durable_start_requirement.required",
                "reason": "missing_durable_start_required_bool",
                "message": "durable_start_requirement.required must be true for normal visible-thread dispatch or false only for exact no-write probes.",
            }
        )
        return findings

    if required is not True:
        exempt_when = requirement.get("exempt_when")
        if visible_thread_dispatch and (not isinstance(exempt_when, str) or not exempt_when.strip()):
            findings.append(
                {
                    "field": "durable_start_requirement.exempt_when",
                    "reason": "missing_durable_start_exemption_reason",
                    "message": "Visible-thread packets that skip durable-start must explain the exact no-write probe exemption.",
                }
            )
        return findings

    artifact_type = requirement.get("artifact_type")
    if artifact_type not in ARTIFACT_TYPES:
        findings.append(
            {
                "field": "durable_start_requirement.artifact_type",
                "reason": "unknown_durable_start_artifact_type",
                "message": ", ".join(sorted(ARTIFACT_TYPES)),
            }
        )

    first_due = requirement.get("first_artifact_due_minutes")
    if not isinstance(first_due, (int, float)) or first_due <= 0 or first_due > 5:
        findings.append(
            {
                "field": "durable_start_requirement.first_artifact_due_minutes",
                "reason": "invalid_first_artifact_due_minutes",
                "message": "First durable-start artifact must be due within 5 minutes.",
            }
        )

    if requirement.get("completion_claim_allowed") is not False:
        findings.append(
            {
                "field": "durable_start_requirement.completion_claim_allowed",
                "reason": "durable_start_cannot_claim_completion",
                "message": "Durable-start proves execution began; it must not be treated as completion evidence.",
            }
        )

    minimum_content = requirement.get("minimum_content")
    if not isinstance(minimum_content, list) or not minimum_content:
        findings.append(
            {
                "field": "durable_start_requirement.minimum_content",
                "reason": "missing_durable_start_minimum_content",
                "message": "Durable-start requirement must declare minimum artifact content.",
            }
        )

    dispatch_nonce = packet.get("dispatch_nonce")
    requirement_nonce = requirement.get("nonce")
    if artifact_type == "runtime_lease":
        if not isinstance(dispatch_nonce, str) or not dispatch_nonce.strip():
            findings.append(
                {
                    "field": "dispatch_nonce",
                    "reason": "missing_dispatch_nonce",
                    "message": "Runtime-lease durable start requires a unique dispatch_nonce in the task packet.",
                }
            )
        if not isinstance(requirement_nonce, str) or not requirement_nonce.strip():
            findings.append(
                {
                    "field": "durable_start_requirement.nonce",
                    "reason": "missing_runtime_lease_nonce",
                    "message": "Runtime-lease durable start must echo the dispatch nonce.",
                }
            )
        elif isinstance(dispatch_nonce, str) and requirement_nonce != dispatch_nonce:
            findings.append(
                {
                    "field": "durable_start_requirement.nonce",
                    "reason": "runtime_lease_nonce_mismatch",
                    "message": "Runtime-lease nonce must match task packet dispatch_nonce.",
                }
            )

        target_thread_id = packet.get("target_thread_id")
        request_id = packet.get("request_id")
        expected_path = None
        if not isinstance(request_id, str) or not request_id.strip():
            findings.append(
                {
                    "field": "request_id",
                    "reason": "missing_request_id_for_runtime_lease",
                    "message": "Runtime-lease durable start requires request_id so the canonical lease path is unique.",
                }
            )
        if isinstance(target_thread_id, str) and target_thread_id and isinstance(request_id, str) and request_id:
            expected_path = (
                Path("Results")
                / "runtime_leases"
                / target_thread_id
                / f"{request_id}.json"
            )
        artifact = requirement.get("artifact_path_or_class")
        if not isinstance(artifact, str) or not artifact.strip():
            findings.append(
                {
                    "field": "durable_start_requirement.artifact_path_or_class",
                    "reason": "missing_runtime_lease_path",
                    "message": "Runtime-lease durable start requires an explicit project-local lease path.",
                }
            )
        elif not _project_relative(artifact):
            findings.append(
                {
                    "field": "durable_start_requirement.artifact_path_or_class",
                    "reason": "runtime_lease_path_outside_project",
                    "message": artifact,
                }
            )
        elif expected_path is not None and tuple(Path(artifact).parts) != tuple(expected_path.parts):
            findings.append(
                {
                    "field": "durable_start_requirement.artifact_path_or_class",
                    "reason": "runtime_lease_path_not_canonical",
                    "message": f"Expected {expected_path.as_posix()}",
                }
            )

        if isinstance(minimum_content, list):
            missing = sorted(LEASE_MINIMUM_FIELDS - {str(field) for field in minimum_content})
            if missing:
                findings.append(
                    {
                        "field": "durable_start_requirement.minimum_content",
                        "reason": "runtime_lease_minimum_content_missing_fields",
                        "message": ", ".join(missing),
                    }
                )

    return findings


def _check_mworks_department_task(packet: dict[str, Any]) -> list[dict[str, str]]:
    try:
        from check_mworks_live_gate import _check_task as check_mworks_task
    except Exception as exc:  # pragma: no cover - defensive for direct script use.
        return [
            {
                "field": "mworks_live_gate",
                "reason": "mworks_gate_checker_unavailable",
                "message": f"Could not import check_mworks_live_gate.py: {exc}",
            }
        ]

    mworks_result = check_mworks_task(packet, expect="department")
    if mworks_result.get("ok"):
        return []
    nested_findings = mworks_result.get("findings", [])
    if not isinstance(nested_findings, list):
        return [
            {
                "field": "mworks_live_gate",
                "reason": "mworks_department_gate_failed",
                "message": "MWORKS department task packet failed the activation/screenshot gate.",
            }
        ]
    findings: list[dict[str, str]] = []
    for nested in nested_findings:
        if not isinstance(nested, dict):
            continue
        findings.append(
            {
                "field": str(nested.get("field", "mworks_live_gate")),
                "reason": f"mworks_department_gate_{nested.get('reason', 'failed')}",
                "message": str(nested.get("message", "MWORKS department task packet failed the activation/screenshot gate.")),
            }
        )
    return findings


def _check_capability_resolution(packet: dict[str, Any], *, strict: bool) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    try:
        from check_capability_resolution import validate_packet as validate_capability_packet
    except Exception as exc:  # pragma: no cover - defensive for direct script use.
        return [
            {
                "field": "capability_resolution",
                "reason": "capability_resolution_checker_unavailable",
                "message": f"Could not import check_capability_resolution.py: {exc}",
            }
        ], []

    capability_result = validate_capability_packet(packet, strict=strict)
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    for finding in capability_result.get("findings", []):
        if not isinstance(finding, dict):
            continue
        mapped = {
            "field": str(finding.get("field", "capability_resolution")),
            "reason": f"capability_resolution_{finding.get('reason', 'failed')}",
            "message": str(finding.get("message", "Capability resolution failed.")),
        }
        if finding.get("severity") == "warning":
            warnings.append(mapped)
        else:
            errors.append(mapped)
    return errors, warnings


def check_packet(packet: dict[str, Any], *, strict: bool = False) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    gate = _native_gate(packet)

    if gate is None:
        findings.append(
            {
                "field": "native_surface_gate",
                "reason": "missing_native_surface_gate",
                "message": "Task packet must record the PMO native Codex surface gate before dispatch.",
            }
        )
        findings.extend(_check_semantic_boundary(packet))
        return {"ok": False, "warning_count": 0, "fail_count": len(findings), "findings": findings, "warnings": warnings}

    surfaces = _as_surface_set(gate.get("selected_native_surface"))
    findings.extend(_check_semantic_boundary(packet))
    findings.extend(
        _check_durable_start_requirement(
            packet,
            visible_thread_dispatch="visible_thread" in surfaces,
        )
    )

    if not surfaces:
        findings.append(
            {
                "field": "native_surface_gate.selected_native_surface",
                "reason": "missing_selected_native_surface",
                "message": "Use one allowed surface name or a non-empty list of surface names.",
            }
        )
    unknown = sorted(surfaces - ALLOWED_SURFACES)
    if unknown:
        findings.append(
            {
                "field": "native_surface_gate.selected_native_surface",
                "reason": "unknown_selected_native_surface",
                "message": ", ".join(unknown),
            }
        )

    reason = gate.get("surface_selection_reason")
    if not isinstance(reason, str) or not reason.strip():
        findings.append(
            {
                "field": "native_surface_gate.surface_selection_reason",
                "reason": "missing_surface_selection_reason",
                "message": "Explain why this surface is narrower than the alternatives.",
            }
        )

    if not isinstance(gate.get("worktree_required"), bool):
        findings.append(
            {
                "field": "native_surface_gate.worktree_required",
                "reason": "missing_worktree_required_bool",
                "message": "Record whether an isolated worktree is required for this task.",
            }
        )
    worktree_decision = gate.get("worktree_decision")
    if not isinstance(worktree_decision, str) or not worktree_decision.strip():
        findings.append(
            {
                "field": "native_surface_gate.worktree_decision",
                "reason": "missing_worktree_decision",
                "message": "Explain the worktree choice, even when no worktree is required.",
            }
        )

    rejected = gate.get("rejected_surfaces")
    if strict and not rejected:
        warnings.append(
            {
                "field": "native_surface_gate.rejected_surfaces",
                "reason": "missing_rejected_surfaces",
                "message": "Strict mode prefers a short record of rejected alternatives for non-trivial tasks.",
            }
        )

    needs_return_paths = bool(surfaces & RETURN_PATH_SURFACES)
    expected_return_path = packet.get("expected_return_path") or gate.get("expected_return_path")
    blocker_return_path = packet.get("blocker_return_path") or gate.get("blocker_return_path")
    if needs_return_paths:
        for field_name, value in [
            ("expected_return_path", expected_return_path),
            ("blocker_return_path", blocker_return_path),
        ]:
            if not isinstance(value, str) or not value.strip():
                findings.append(
                    {
                        "field": field_name,
                        "reason": f"missing_{field_name}",
                        "message": f"{field_name} is required for delegated or packet-return surfaces.",
                    }
                )
            elif not _project_relative(value):
                findings.append(
                    {
                        "field": field_name,
                        "reason": f"{field_name}_outside_project",
                        "message": value,
                    }
                )

    if "visible_thread" in surfaces:
        for field_name in ["target_thread", "target_thread_id"]:
            value = packet.get(field_name) or gate.get(field_name)
            if not isinstance(value, str) or not value.strip():
                findings.append(
                    {
                        "field": field_name,
                        "reason": f"missing_{field_name}",
                        "message": "Visible-thread dispatch requires concrete target thread title and id.",
                    }
                )

    if _looks_like_mworks_department_packet(packet):
        findings.extend(_check_mworks_department_task(packet))

    if strict:
        capability_findings, capability_warnings = _check_capability_resolution(packet, strict=True)
        findings.extend(capability_findings)
        warnings.extend(capability_warnings)

    return {
        "ok": not findings,
        "warning_count": len(warnings),
        "fail_count": len(findings),
        "selected_native_surfaces": sorted(surfaces),
        "findings": findings,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet", type=Path, help="Path to a JSON task packet.")
    parser.add_argument("--strict", action="store_true", help="Emit warnings for recommended but non-blocking fields.")
    args = parser.parse_args(argv)

    packet_path = args.packet if args.packet.is_absolute() else ROOT / args.packet
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    if not isinstance(packet, dict):
        raise SystemExit("packet root must be a JSON object")
    result = check_packet(packet, strict=args.strict)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
