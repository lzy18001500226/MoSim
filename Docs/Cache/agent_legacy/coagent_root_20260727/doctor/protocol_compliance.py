#!/usr/bin/env python3
"""Validate protocol compliance for CoAgent task/context/result artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.context import context_pack
from CoAgent.runtime import mosim_agent_runtime as runtime


TERMINAL_CANONICAL_STATUSES = {
    "review_required",
    "blocked",
    "failed",
    "completed",
    "canceled",
    "rejected",
    "superseded",
}

REQUIRED_CONTEXT_SECTIONS = [
    "## Task Identity",
    "## Goal Stack",
    "## Definition Of Done",
    "## Non-Goals",
    "## Read Scope",
    "## Write Scope",
    "## Worktree Binding",
    "## Current State",
    "## Required Evidence",
    "## Risks And Assumptions",
    "## Open Questions",
    "## Appetite And Circuit Breaker",
    "## Escalation Conditions",
    "## Forbidden Actions",
    "## Review And Acceptance Gate",
    "## Result Packet Path",
    "## Recent Events",
    "## Return Contract",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def validate_task_packet(packet: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    required = [
        "task_id",
        "task_class",
        "role",
        "objective",
        "canonical_task_goal",
        "conversation_objective",
        "accountable_owner",
        "definition_of_done",
        "appetite",
        "circuit_breaker",
        "checkpoint_plan",
        "result_file",
    ]
    for field in required:
        if packet.get(field) in (None, "", []):
            findings.append({"severity": "fail", "field": field, "reason": "missing_required"})
    worktree_fields = ["worktree_path", "branch_or_base", "merge_owner", "close_condition"]
    if any(packet.get(field) for field in worktree_fields):
        for field in worktree_fields:
            if not packet.get(field):
                findings.append({"severity": "fail", "field": field, "reason": "partial_worktree_binding"})
    return findings


def validate_context_pack_text(text: str, task_packet: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for section in REQUIRED_CONTEXT_SECTIONS:
        if section not in text:
            findings.append({"severity": "fail", "field": "context_pack", "reason": f"missing_section:{section}"})
    required_terms = {
        "canonical_task_goal": task_packet.get("canonical_task_goal", ""),
        "conversation_objective": task_packet.get("conversation_objective", ""),
        "result_file": task_packet.get("result_file", ""),
    }
    for field, value in required_terms.items():
        if value and value not in text:
            findings.append({"severity": "fail", "field": field, "reason": "missing_from_context_pack"})
    if task_packet.get("worktree_path"):
        for field in ["worktree_path", "branch_or_base", "merge_owner", "close_condition"]:
            expected = task_packet.get(field, "")
            if expected and f"{field}: {expected}" not in text:
                findings.append({"severity": "fail", "field": field, "reason": "missing_worktree_binding"})
    elif "worktree: none; task edits run in the project main workspace" not in text:
        findings.append({"severity": "fail", "field": "worktree", "reason": "missing_none_worktree_marker"})
    if "review_owner:" not in text:
        findings.append({"severity": "fail", "field": "review_owner", "reason": "missing_review_gate"})
    return findings


def validate_result_packet(packet: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    required = ["task_id", "status", "canonical_status", "summary", "review_status", "acceptance_state"]
    for field in required:
        if packet.get(field) in (None, "", []):
            findings.append({"severity": "fail", "field": field, "reason": "missing_required"})
    canonical_status = str(packet.get("canonical_status", ""))
    if canonical_status in TERMINAL_CANONICAL_STATUSES and not packet.get("next_recommended_action"):
        findings.append({"severity": "fail", "field": "next_recommended_action", "reason": "missing_terminal_next_action"})
    if packet.get("worktree_path"):
        for field in ["worktree_path", "branch_or_base", "merge_owner", "close_condition"]:
            if not packet.get(field):
                findings.append({"severity": "fail", "field": field, "reason": "partial_worktree_binding"})
    return findings


def validate_bundle(task_packet: dict[str, Any], context_text: str, result_packet: dict[str, Any]) -> dict[str, Any]:
    findings = []
    findings.extend(validate_task_packet(task_packet))
    findings.extend(validate_context_pack_text(context_text, task_packet))
    findings.extend(validate_result_packet(result_packet))
    fail_count = sum(1 for item in findings if item["severity"] == "fail")
    warning_count = sum(1 for item in findings if item["severity"] == "warning")
    return {
        "ok": fail_count == 0,
        "fail_count": fail_count,
        "warning_count": warning_count,
        "findings": findings,
    }


def check_task(args: argparse.Namespace) -> dict[str, Any]:
    task_packet = runtime.export_task_packet(args)
    result_packet = runtime.export_result_packet(args)
    context = context_pack.build_context_pack(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            task_id=args.task_id,
            output=None,
            event_limit=args.event_limit,
            knowledge_query=[],
            decision=[],
            blocker=[],
            include_memory_context=False,
            memory_policy=None,
            memory_limit_per_query=None,
            memory_max_hits=None,
            memory_max_chars=None,
            warn_chars=context_pack.DEFAULT_WARN_CHARS,
            fail_chars=context_pack.DEFAULT_FAIL_CHARS,
        )
    )
    validation = validate_bundle(task_packet, context["text"], result_packet)
    return {
        "ok": validation["ok"],
        "task_id": args.task_id,
        "task_packet": task_packet,
        "result_packet": result_packet,
        "context_metrics": context["metrics"],
        "validation": validation,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    runtime.add_common(parser)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--event-limit", type=int, default=8)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = check_task(args)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
