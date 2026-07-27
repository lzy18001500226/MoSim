#!/usr/bin/env python3
"""Validate that CoAgent task, context, and result goals did not drift."""

from __future__ import annotations

import argparse
import json
import re
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
FORBIDDEN_ACTIVITY_PATTERNS = [
    r"\bcreate\b.{0,40}\btask\b",
    r"\bopen\b.{0,40}\bconversation\b",
    r"\bresume\b.{0,40}\bconversation\b",
    r"\bspend\s+time\b",
    r"建立.*任务",
    r"创建.*任务",
    r"新建.*对话",
    r"打开.*对话",
    r"花.*小时",
]


def words(value: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z0-9_\u4e00-\u9fff]+", value.lower()))


def has_activity_only_goal(value: str) -> bool:
    text = value.strip().lower()
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in FORBIDDEN_ACTIVITY_PATTERNS)


def add_finding(
    findings: list[dict[str, str]],
    *,
    code: str,
    severity: str,
    field: str,
    message: str,
    remediation: str,
) -> None:
    findings.append(
        {
            "code": code,
            "severity": severity,
            "field": field,
            "message": message,
            "remediation": remediation,
        }
    )


def validate_task_goal(task_packet: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    objective = str(task_packet.get("objective") or "").strip()
    canonical = str(task_packet.get("canonical_task_goal") or "").strip()
    conversation = str(task_packet.get("conversation_objective") or "").strip()
    required_evidence = task_packet.get("required_evidence") or []
    non_goals = task_packet.get("non_goals") or []

    if not objective:
        add_finding(
            findings,
            code="GOAL_USER_OBJECTIVE_MISSING",
            severity="error",
            field="objective",
            message="task objective is missing",
            remediation="set the user-facing task objective before dispatch",
        )
    if not canonical:
        add_finding(
            findings,
            code="GOAL_CANONICAL_MISSING",
            severity="error",
            field="canonical_task_goal",
            message="canonical task goal is missing",
            remediation="set canonical_task_goal in task metadata",
        )
    if canonical and has_activity_only_goal(canonical):
        add_finding(
            findings,
            code="GOAL_FORBIDDEN_SUBSTITUTION",
            severity="error",
            field="canonical_task_goal",
            message="canonical goal is a setup/activity substitute, not the requested outcome",
            remediation="rewrite the canonical goal to name the actual deliverable and acceptance path",
        )
    if conversation and has_activity_only_goal(conversation):
        add_finding(
            findings,
            code="GOAL_OBJECTIVE_AS_ACTIVITY",
            severity="error",
            field="conversation_objective",
            message="conversation objective is only setup activity",
            remediation="make the conversation objective describe the slice output and result path",
        )
    if objective and canonical:
        objective_words = words(objective)
        canonical_words = words(canonical)
        meaningful = {word for word in objective_words if len(word) >= 4}
        dropped = sorted(word for word in meaningful if word not in canonical_words)
        if len(dropped) >= max(3, len(meaningful) // 2):
            add_finding(
                findings,
                code="GOAL_CANONICAL_WEAKENED",
                severity="warning",
                field="canonical_task_goal",
                message="canonical goal shares little terminology with the task objective",
                remediation="review whether the canonical goal dropped required user scope",
            )
    if not required_evidence:
        add_finding(
            findings,
            code="GOAL_EVIDENCE_OUT_OF_SCOPE",
            severity="warning",
            field="required_evidence",
            message="task declares no required evidence",
            remediation="declare evidence required to close this task",
        )
    if not non_goals:
        add_finding(
            findings,
            code="GOAL_NON_SUBSTITUTION_MISSING",
            severity="warning",
            field="non_goals",
            message="task has no explicit non-goals or non-substitution summary",
            remediation="add non_goals for forbidden substitutes and gated boundaries",
        )
    return findings


def validate_result_goal(task_packet: dict[str, Any], result_packet: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    task_goal = str(task_packet.get("canonical_task_goal") or "").strip()
    result_goal = str(result_packet.get("canonical_task_goal") or "").strip()
    summary = str(result_packet.get("summary") or "").strip()
    canonical_status = str(result_packet.get("canonical_status") or "")
    evidence = result_packet.get("evidence") or []
    next_action = str(result_packet.get("next_recommended_action") or "").strip()

    if task_goal and result_goal and task_goal != result_goal:
        add_finding(
            findings,
            code="GOAL_RESULT_MUTATION",
            severity="error",
            field="result_packet.canonical_task_goal",
            message="result packet changed the canonical task goal",
            remediation="repair the result packet or re-dispatch; workers cannot mutate the canonical goal",
        )
    if summary and has_activity_only_goal(summary):
        add_finding(
            findings,
            code="GOAL_FORBIDDEN_SUBSTITUTION",
            severity="error",
            field="result_packet.summary",
            message="result summary reports setup activity as completion",
            remediation="summarize actual accepted evidence or return a blocker",
        )
    if canonical_status in TERMINAL_CANONICAL_STATUSES and not evidence:
        add_finding(
            findings,
            code="GOAL_COMPLETION_OVERCLAIM",
            severity="error",
            field="result_packet.evidence",
            message="terminal result has no evidence",
            remediation="add evidence paths or downgrade to blocker/review_required",
        )
    if canonical_status in TERMINAL_CANONICAL_STATUSES and not next_action:
        add_finding(
            findings,
            code="GOAL_COMPLETION_OVERCLAIM",
            severity="error",
            field="result_packet.next_recommended_action",
            message="terminal result has no next recommended action",
            remediation="state review, closeout, continuation, or blocker action",
        )
    return findings


def validate_context_goal(task_packet: dict[str, Any], context_text: str) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for field in ["canonical_task_goal", "conversation_objective", "result_file"]:
        value = str(task_packet.get(field) or "")
        if value and value not in context_text:
            add_finding(
                findings,
                code="GOAL_LOCAL_UNALIGNED",
                severity="error",
                field=f"context_pack.{field}",
                message=f"context pack does not contain {field}",
                remediation="rebuild the context pack from the current task packet",
            )
    return findings


def decision_for(findings: list[dict[str, str]]) -> str:
    if any(item["severity"] == "error" for item in findings):
        return "reject"
    if findings:
        return "needs_review"
    return "accept"


def validate_bundle(task_packet: dict[str, Any], context_text: str, result_packet: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    findings.extend(validate_task_goal(task_packet))
    findings.extend(validate_context_goal(task_packet, context_text))
    findings.extend(validate_result_goal(task_packet, result_packet))
    error_count = sum(1 for item in findings if item["severity"] == "error")
    warning_count = sum(1 for item in findings if item["severity"] == "warning")
    return {
        "schema_version": "coagent.validator_report.v1",
        "validator": "goal_alignment",
        "ok": error_count == 0,
        "decision": decision_for(findings),
        "finding_codes": sorted({item["code"] for item in findings}),
        "findings": findings,
        "error_count": error_count,
        "warning_count": warning_count,
        "side_effects": {
            "declared": ["read_runtime_task", "read_context_pack", "read_result_packet"],
            "forbidden": ["goal_mutation", "live_dispatch", "mcp_or_tool_call", "git_mutation"],
        },
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
    report = validate_bundle(task_packet, context["text"], result_packet)
    report.update(
        {
            "task_id": args.task_id,
            "context_metrics": context["metrics"],
            "evidence_paths": [str(args.db), str(args.events)],
        }
    )
    if args.output:
        output = Path(args.output)
        target = output if output.is_absolute() else ROOT / output
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    runtime.add_common(parser)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--event-limit", type=int, default=8)
    parser.add_argument("--output", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = check_task(args)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
