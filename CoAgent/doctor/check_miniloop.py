#!/usr/bin/env python3
"""Validate the CoAgent minimum closed-loop proof bundle.

This check is intentionally static. It validates a file-level proof bundle
without creating conversations, worktrees, transport calls, emails, hooks, or
MCP/tool changes.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUNDLE = ROOT / "Results" / "coagent_miniloop" / "COAGENT-MINILOOP-01"

REQUIRED_FILES = [
    "task_charter.yaml",
    "shared_task_board.yaml",
    "team_mailbox.yaml",
    "context_pack.yaml",
    "scoped_conversation_packet.yaml",
    "result_packet.json",
    "review_packet.yaml",
    "context_delta.yaml",
    "worktree_binding.yaml",
    "integration_plan.yaml",
    "team_trace_eval.yaml",
    "workflow_graph.yaml",
    "closeout_summary.md",
    "retrospective.md",
]

REQUIRED_TEMPLATES = [
    "shared_task_board.yaml",
    "team_mailbox.yaml",
    "dynamic_team_policy.yaml",
    "conversation_fork_policy.yaml",
    "context_shard_policy.yaml",
    "worktree_binding.yaml",
    "integration_plan.yaml",
    "team_trace_eval.yaml",
]


def load_structured(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise AssertionError(f"{path} must contain a mapping/object")
    return data


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_bundle(bundle: Path) -> dict[str, Any]:
    bundle = bundle.resolve()
    require(ROOT.resolve() in bundle.parents, f"bundle is outside project: {bundle}")

    missing = [name for name in REQUIRED_FILES if not (bundle / name).exists()]
    require(not missing, f"missing miniloop files: {missing}")

    template_root = ROOT / "CoAgent" / "protocol" / "templates"
    missing_templates = [name for name in REQUIRED_TEMPLATES if not (template_root / name).exists()]
    require(not missing_templates, f"missing V2 templates: {missing_templates}")

    task = load_structured(bundle / "task_charter.yaml")
    board = load_structured(bundle / "shared_task_board.yaml")
    mailbox = load_structured(bundle / "team_mailbox.yaml")
    context_pack = load_structured(bundle / "context_pack.yaml")
    scoped = load_structured(bundle / "scoped_conversation_packet.yaml")
    result = load_structured(bundle / "result_packet.json")
    review = load_structured(bundle / "review_packet.yaml")
    context_delta = load_structured(bundle / "context_delta.yaml")
    worktree = load_structured(bundle / "worktree_binding.yaml")
    integration = load_structured(bundle / "integration_plan.yaml")
    trace_eval = load_structured(bundle / "team_trace_eval.yaml")
    workflow = load_structured(bundle / "workflow_graph.yaml")

    task_id = "COAGENT-MINILOOP-01"
    packets = {
        "task_charter.yaml": task,
        "shared_task_board.yaml": board,
        "team_mailbox.yaml": mailbox,
        "context_pack.yaml": context_pack,
        "scoped_conversation_packet.yaml": scoped,
        "result_packet.json": result,
        "review_packet.yaml": review,
        "context_delta.yaml": context_delta,
        "worktree_binding.yaml": worktree,
        "integration_plan.yaml": integration,
        "team_trace_eval.yaml": trace_eval,
        "workflow_graph.yaml": workflow,
    }
    for name, packet in packets.items():
        require(packet.get("task_id") == task_id, f"{name} has inconsistent task_id")

    require(board.get("current_phase") in {"completed", "review_required"}, "board must be terminal or review_required")
    require(not board.get("open_blockers"), "board must not have open blockers")
    require(board.get("review_gates"), "board must name review gates")

    for message in mailbox.get("messages", []):
        if message.get("requires_response"):
            require(message.get("state") == "closed", f"required mailbox message is not closed: {message.get('message_id')}")

    quality_gate = context_pack.get("quality_gate", {})
    for field in ["relevance_ok", "freshness_ok", "sufficiency_ok", "boundedness_ok"]:
        require(quality_gate.get(field) is True, f"context quality gate failed: {field}")

    require(scoped.get("result_packet_required") is True, "scoped packet must require result packet")
    require(worktree.get("worktree_required") is False, "miniloop proof must not require a worktree")
    require(worktree.get("automatic_worktree_creation_approved") is False, "automatic worktree creation must remain disabled")

    require(result.get("canonical_status") == "completed", "result packet must be terminal completed")
    require(result.get("evidence"), "result packet must include evidence")
    require(result.get("review_status") == "pending", "result packet must remain pending human/project review")

    require(review.get("decision") in {"accepted", "accepted_with_concerns"}, "review packet must accept artifact proof")
    require(review.get("integration_permission", {}).get("can_close_task") is False, "human review must remain required")

    require(context_delta.get("review", {}).get("status") == "needs_review", "context delta must wait for review")
    require(integration.get("can_close_task") is False, "integration plan must not close before human review")
    require(trace_eval.get("decision") in {"accepted", "accepted_with_concerns"}, "trace eval must have review disposition")
    require(workflow.get("review", {}).get("acceptance_state") == "needs_review", "workflow must wait for human review")

    closeout = (bundle / "closeout_summary.md").read_text(encoding="utf-8")
    for needle in ["What This Proves", "What This Does Not Prove", "Recommended Human Decision"]:
        require(needle in closeout, f"closeout summary missing section: {needle}")

    retrospective = (bundle / "retrospective.md").read_text(encoding="utf-8")
    for needle in ["What Worked", "What Did Not Get Proven", "Process Risks", "Improvement For Next Loop"]:
        require(needle in retrospective, f"retrospective missing section: {needle}")

    human_review = ROOT / "CoAgent" / "docs" / "decisions" / "coagent_miniloop_01_human_review.md"
    require(human_review.exists(), "missing human-review decision packet")
    review_text = human_review.read_text(encoding="utf-8")
    if "Status: needs user review" in review_text:
        for needle in ["approved:", "approved_with_edits:", "revision_required:"]:
            require(needle in review_text, f"human-review packet missing option: {needle}")
        human_review_state = "needs_user_review"
    else:
        for needle in [
            "Status: approved_with_next_gate",
            "multi_conversation_communication: allowed",
            "default_artifact_chain: full chain by default",
            "COAGENT-MINILOOP-02",
        ]:
            require(needle in review_text, f"human-review packet missing approved gate text: {needle}")
        human_review_state = "approved_with_next_gate"

    return {
        "ok": True,
        "task_id": task_id,
        "bundle": rel(bundle),
        "files_checked": len(REQUIRED_FILES),
        "templates_checked": len(REQUIRED_TEMPLATES),
        "human_review": rel(human_review),
        "state": human_review_state,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", default=str(DEFAULT_BUNDLE))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = check_bundle(Path(args.bundle))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("miniloop ok")
        print(f"task_id={result['task_id']}")
        print(f"state={result['state']}")
        print(f"human_review={result['human_review']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
