#!/usr/bin/env python3
"""Generate compact context packs for dedicated CoAgent task conversations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.runtime import mosim_agent_runtime as runtime
from CoAgent.memory import memory_context


DEFAULT_WARN_CHARS = 14000
DEFAULT_FAIL_CHARS = 22000
TOKEN_CHARS = 4


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def project_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    if not (resolved == ROOT.resolve() or ROOT.resolve() in resolved.parents):
        raise SystemExit(f"output path is outside MoSim: {path}")
    return resolved


def lines_for_list(values: list[str]) -> list[str]:
    if not values:
        return ["- none"]
    return [f"- `{item}`" for item in values]


def metadata_value(metadata: dict[str, Any], key: str, default: str = "") -> str:
    value = metadata.get(key, default)
    if value in (None, ""):
        return default
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def context_metrics(
    text: str,
    *,
    task: dict[str, Any],
    knowledge_queries: list[str],
    event_limit: int,
    memory: dict[str, Any] | None,
    warn_chars: int,
    fail_chars: int,
) -> dict[str, Any]:
    sections: dict[str, int] = {}
    current = "preamble"
    sections[current] = 0
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections.setdefault(current, 0)
        sections[current] += len(line) + 1
    char_count = len(text)
    estimated_tokens = (char_count + TOKEN_CHARS - 1) // TOKEN_CHARS
    if char_count > fail_chars:
        risk = "fail"
    elif char_count > warn_chars:
        risk = "warning"
    else:
        risk = "ok"
    memory_budget = memory.get("budget", {}) if memory else {}
    return {
        "char_count": char_count,
        "estimated_tokens": estimated_tokens,
        "warn_chars": warn_chars,
        "fail_chars": fail_chars,
        "risk": risk,
        "section_chars": sections,
        "event_count_total": len(task.get("events", [])),
        "event_limit": event_limit,
        "event_count_included": min(len(task.get("events", [])), event_limit),
        "knowledge_query_count": len([item for item in knowledge_queries if item]),
        "memory_included": memory is not None,
        "memory_candidate_hits": memory.get("candidate_count", 0) if memory else 0,
        "memory_included_hits": memory.get("count", 0) if memory else 0,
        "memory_truncated_by_budget": memory.get("truncated_by_budget", 0) if memory else 0,
        "memory_char_count": memory.get("char_count", 0) if memory else 0,
        "memory_budget": memory_budget,
    }


def build_context_pack(args: argparse.Namespace) -> dict[str, Any]:
    task = runtime.show_task(args)
    packet = runtime.export_task_packet(args)
    metadata = task.get("metadata", {})
    owner_department = metadata_value(metadata, "department", task["role"])
    knowledge_queries = args.knowledge_query or [
        task["task_id"],
        task["role"],
        owner_department,
        " ".join(task["objective"].split()[:8]),
    ]
    relevant_decisions = args.decision or [
        "Use project-owned runtime state, not raw chat, as the durable task boundary.",
        "Use compact context packs for dedicated long-running task conversations.",
        "Return one MoSim Result Packet to the declared result_file path.",
    ]
    blockers = args.blocker or []
    current_state = task["events"][-1]["summary"] if task["events"] else task["objective"]
    worktree_path = packet.get("worktree_path", "")
    branch_or_base = packet.get("branch_or_base", "")
    merge_owner = packet.get("merge_owner", "")
    close_condition = packet.get("close_condition", "")
    review_owner = packet.get("review_owner", "") or "PMO/main or assigned reviewer"
    review_gates = packet.get("review_gates", [])
    human_review_points = packet.get("human_review_points", [])
    forbidden_actions = packet.get("forbidden_actions", [])
    assumptions = packet.get("assumptions", [])
    open_questions = packet.get("open_questions", [])
    required_evidence = packet.get("required_evidence", [])
    escalation_conditions = packet.get("escalation_conditions", [])
    non_goals = packet.get("non_goals", [])

    lines = [
        "[MoSim Context Pack]",
        f"task_id: {task['task_id']}",
        f"task_class: {packet['task_class']}",
        f"owner_department: {owner_department}",
        f"role: {task['role']}",
        f"state: {task['state']}",
        f"owner: {task['owner']}",
        "",
        "## Task Identity",
        f"task_id: {task['task_id']}",
        f"task_class: {packet['task_class']}",
        f"owner_department: {owner_department}",
        f"role: {task['role']}",
        f"accountable_owner: {packet['accountable_owner']}",
        f"state: {task['state']}",
        "",
        "## Goal Stack",
        f"project_goal: {packet['project_goal'] or 'none recorded'}",
        f"phase_or_strategy_objective: {packet.get('phase_objective', '') or 'none recorded'}",
        f"canonical_task_goal: {packet['canonical_task_goal']}",
        f"conversation_objective: {packet['conversation_objective']}",
        f"subagent_objective: {packet.get('subagent_objective', '') or 'none'}",
        "",
        "## Objective",
        packet["objective"],
        "",
        "## Definition Of Done",
        packet["definition_of_done"],
        "",
        "## Non-Goals",
        *lines_for_list(non_goals),
        "",
        "## Read Scope",
        *lines_for_list(task["read_scope"]),
        "",
        "## Write Scope",
        *lines_for_list(task["write_scope"]),
        "",
        "## Worktree Binding",
        (
            "worktree: none; task edits run in the project main workspace"
            if not worktree_path
            else f"worktree_path: {worktree_path}"
        ),
    ]
    if worktree_path:
        lines.extend(
            [
                f"branch_or_base: {branch_or_base or 'none recorded'}",
                f"merge_owner: {merge_owner or 'none recorded'}",
                f"close_condition: {close_condition or 'none recorded'}",
                f"write_scope: {json.dumps(task['write_scope'], ensure_ascii=False)}",
            ]
        )
    lines.extend(
        [
            "",
            "## Current State",
            current_state,
            "",
            "## Required Evidence",
            *lines_for_list(required_evidence),
            "",
            "## Relevant Decisions",
            *[f"- {item}" for item in relevant_decisions],
            "",
            "## Known Blockers",
            *(["- none"] if not blockers else [f"- {item}" for item in blockers]),
            "",
            "## Risks And Assumptions",
            *lines_for_list(assumptions),
            "",
            "## Open Questions",
            *lines_for_list(open_questions),
            "",
            "## Appetite And Circuit Breaker",
            f"appetite: {packet['appetite']}",
            f"circuit_breaker: {packet['circuit_breaker']}",
            f"checkpoint_plan: {packet['checkpoint_plan']}",
            "",
            "## Escalation Conditions",
            *lines_for_list(escalation_conditions),
            "",
            "## Forbidden Actions",
            *lines_for_list(forbidden_actions),
            "",
            "## Review And Acceptance Gate",
            f"review_required: {'yes' if review_gates or human_review_points or task['state'] == 'done_with_concerns' else 'no'}",
            f"review_owner: {review_owner}",
            "acceptance_state_values: met | partially_met | not_met | unknown",
            "review_status_values: not_required | pending | accepted | needs_review | rejected",
            f"evidence_required_for_acceptance: {json.dumps(required_evidence, ensure_ascii=False)}",
            f"review_gates: {json.dumps(review_gates, ensure_ascii=False)}",
            f"known_human_review_points: {json.dumps(human_review_points, ensure_ascii=False)}",
            "",
            "## Required Tools",
            "- CoAgent runtime",
            "- CoAgent dispatch/result packet contract",
            "- CoAgent knowledge search",
            "",
            "## Acceptance",
            task["acceptance"],
            "",
            "## Stop Condition",
            task["stop_condition"],
            "",
            "## Result Packet Path",
            f"`{packet['result_file']}`",
            "",
            "## Knowledge Search Queries",
            *[f"- `{item}`" for item in knowledge_queries if item],
            "",
        ]
    )
    memory = None
    if args.include_memory_context:
        memory = memory_context.build_memory_context(
            knowledge_queries,
            limit_per_query=args.memory_limit_per_query,
            max_hits=args.memory_max_hits,
            max_chars=args.memory_max_chars,
            policy_path=args.memory_policy,
        )
        lines.extend(
            [
                "## Memory Context",
                memory["text"].rstrip(),
                "",
            ]
        )
    lines.extend(
        [
        "## Recent Events",
        ]
    )
    for event in task["events"][-args.event_limit :]:
        lines.append(f"- {event['timestamp']} `{event['event_type']}` {event['actor']}: {event['summary']}")

    lines.extend(
        [
            "",
            "## Return Contract",
            "Write exactly one MoSim Result Packet to the declared result file. If blocked, set status to `blocked`, record the blocker, and identify the next human or system action.",
        ]
    )

    text = "\n".join(lines).rstrip() + "\n"
    metrics = context_metrics(
        text,
        task=task,
        knowledge_queries=knowledge_queries,
        event_limit=args.event_limit,
        memory=memory,
        warn_chars=getattr(args, "warn_chars", DEFAULT_WARN_CHARS),
        fail_chars=getattr(args, "fail_chars", DEFAULT_FAIL_CHARS),
    )
    if args.output:
        output_path = project_path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
        output = rel(output_path)
    else:
        output = ""
    return {"task_id": task["task_id"], "output": output, "text": text, "metrics": metrics}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    runtime.add_common(parser)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--event-limit", type=int, default=8)
    parser.add_argument("--knowledge-query", action="append", default=[])
    parser.add_argument("--decision", action="append", default=[])
    parser.add_argument("--blocker", action="append", default=[])
    parser.add_argument("--include-memory-context", action="store_true")
    parser.add_argument("--memory-policy", type=Path, default=None)
    parser.add_argument("--memory-limit-per-query", type=int, default=None)
    parser.add_argument("--memory-max-hits", type=int, default=None)
    parser.add_argument("--memory-max-chars", type=int, default=None)
    parser.add_argument("--warn-chars", type=int, default=DEFAULT_WARN_CHARS)
    parser.add_argument("--fail-chars", type=int, default=DEFAULT_FAIL_CHARS)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = build_context_pack(args)
    if args.output:
        print(
            json.dumps(
                {
                    "task_id": result["task_id"],
                    "output": result["output"],
                    "metrics": result["metrics"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(result["text"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
