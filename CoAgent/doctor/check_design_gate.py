#!/usr/bin/env python3
"""Validate the current CoAgent design approval gate wiring.

This check is intentionally read-only and import-free. It verifies that the
durable approval record, user review surfaces, frozen backlog, and project
entry points agree on whether CoAgent implementation may resume.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Union


ROOT = Path(__file__).resolve().parents[2]
REVIEW_ENTRY = "CoAgent/docs/decisions/coagent_design_review_brief.zh.md"
DECISION_RECORD = "CoAgent/docs/decisions/coagent_design_decision_record.md"
FIRST_ALLOWED_TASK = "COAGENT-IMPL-01"
DECISION_TEMPLATES = {
    "approved": (
        "CoAgent design approved.\n"
        "Decision date: YYYY-MM-DD\n"
        "Approved defaults: all\n"
        "Notes: <optional>"
    ),
    "approved_with_edits": (
        "CoAgent design approved with edits.\n"
        "Decision date: YYYY-MM-DD\n"
        "Accepted defaults: <list>\n"
        "Rejected or changed defaults: <list>\n"
        "Required doc updates before implementation: <list>\n"
        "Notes: <optional>"
    ),
    "revision_required": (
        "CoAgent design revision required.\n"
        "Decision date: YYYY-MM-DD\n"
        "Rejected defaults: <list>\n"
        "Required changes: <list>\n"
        "Do not implement until revised packet is reviewed: yes"
    ),
}


def read_rel(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def detect_decision_status(record: str) -> str:
    in_decision_state = False
    for line in record.splitlines():
        stripped = line.strip()
        if stripped == "## Decision State":
            in_decision_state = True
            continue
        if in_decision_state and stripped.startswith("## "):
            break
        if in_decision_state and stripped.startswith("status:"):
            return stripped.split(":", 1)[1].strip()
    return "unknown"


BASE_CHECKS = {
    "CoAgent/docs/decisions/coagent_design_decision_record.md": [
        "decision_id: COAGENT-DESIGN-20260527",
        "next_implementation_task_if_accepted: COAGENT-IMPL-01",
        "CoAgent/docs/decisions/coagent_design_review_brief.zh.md",
        "CoAgent/docs/decisions/coagent_post_approval_backlog.md",
        "CoAgent/learning/audits/2026-05-27_official_protocol_convergence_round11.md",
        "input_required",
        "auth_required",
    ],
    "CoAgent/docs/decisions/coagent_design_review_brief.zh.md": [
        "CoAgent/docs/decisions/coagent_design_decision_record.md",
        "COAGENT-IMPL-01",
        "CoAgent design approved.",
        "CoAgent design approved with edits.",
        "CoAgent design revision required.",
        "input_required",
        "auth_required",
        "artifact",
        "30 秒确认摘要",
        "COAGENT-IMPL-01",
    ],
    "CoAgent/docs/decisions/coagent_post_approval_backlog.md": [
        "COAGENT-IMPL-01",
        "Non-Execution Rule",
        ("pending_user_decision", "approved checkpoint"),
        "approved_with_edits",
        "artifact/evidence",
        "input_required",
        "auth_required",
    ],
    "CoAgent/docs/decisions/coagent_design_discussion_packet.md": [
        "simple message",
        "durable task",
        "artifact/evidence",
        "input_required",
        "auth_required",
        "terminal states",
    ],
    "CoAgent/docs/decisions/coagent_goal_readiness_audit.md": [
        "CoAgent/docs/decisions/coagent_design_decision_record.md",
        "CoAgent/docs/decisions/coagent_design_review_brief.zh.md",
        "COAGENT-IMPL-01",
        "input_required",
        "auth_required",
    ],
    "CoAgent/STATUS.md": [
        "CoAgent/docs/decisions/coagent_design_decision_record.md",
        "CoAgent/docs/decisions/coagent_design_review_brief.zh.md",
        "CoAgent/docs/decisions/coagent_goal_readiness_audit.md",
        "COAGENT-IMPL-01",
        "decision_status:",
        "implementation_allowed:",
        "review_entry: CoAgent/docs/decisions/coagent_design_review_brief.zh.md",
    ],
    "AGENTS.md": [
        "CoAgent/STATUS.md",
        "COAGENT-IMPL-01",
        "remain gated",
    ],
    "PROGRESS.md": [
        "CoAgent design gate",
        "CoAgent/docs/decisions/coagent_design_decision_record.md",
        "CoAgent/docs/decisions/coagent_design_review_brief.zh.md",
        "CoAgent/docs/decisions/coagent_post_approval_backlog.md",
    ],
    "Docs/Index/workflow_index.md": [
        "COAGENT-IMPL-01",
        "CoAgent/docs/decisions/coagent_design_decision_record.md",
        "CoAgent/STATUS.md",
    ],
    "CoAgent/README.md": [
        "Current Gate",
        "STATUS.md",
        "CoAgent/docs/decisions/coagent_design_decision_record.md",
        "CoAgent/docs/decisions/coagent_design_review_brief.zh.md",
        "implementation_allowed:",
        "first_allowed_task: COAGENT-IMPL-01",
    ],
    "CoAgent/docs/architecture/ARCHITECTURE.md": [
        "Current Approval Gate",
        "CoAgent/STATUS.md",
        "COAGENT-IMPL-01",
        "approved",
    ],
    "CoAgent/docs/status/MIGRATION_STATUS.md": [
        "Current Gate",
        "CoAgent/STATUS.md",
        "COAGENT-IMPL-01",
        "gates implementation",
    ],
    "CoAgent/docs/architecture/COMPONENT_MAP.md": [
        "Current implementation gate",
        "CoAgent/docs/decisions/coagent_design_decision_record.md",
        "CoAgent/docs/decisions/coagent_design_review_brief.zh.md",
        "CoAgent/docs/decisions/coagent_post_approval_backlog.md",
    ],
    "CoAgent/learning/README.md": [
        "coagent_design_decision_record.md",
        "approved",
        "coagent_design_review_brief.zh.md",
        "coagent_post_approval_backlog.md",
    ],
}


PENDING_CHECKS = {
    "CoAgent/STATUS.md": [
        "Status: pending_user_decision",
        "Implementation is frozen.",
    ],
    "CoAgent/docs/decisions/coagent_design_decision_record.md": [
        "status: pending_user_decision",
    ],
    "CoAgent/docs/decisions/coagent_goal_readiness_audit.md": [
        "Status: ready for user design confirmation, not complete.",
        "Not allowed yet",
        "Do not mark the active goal complete yet.",
    ],
    "CoAgent/docs/decisions/coagent_post_approval_backlog.md": [
        "frozen until user design approval",
        "Do not execute these tasks until",
    ],
}


APPROVED_CHECKS = {
    "CoAgent/STATUS.md": [
        ("Status: ready_for_implementation", "Status: implementation_checkpoint_complete"),
        "decision_status: approved",
        "implementation_allowed: true",
        "COAGENT-IMPL-01",
    ],
    "CoAgent/docs/decisions/coagent_design_decision_record.md": [
        "Status: approved",
        "status: approved",
        "decision_date: 2026-05-28",
        "approved_defaults: all",
        "next_state_if_accepted: ready_for_implementation",
        "next_implementation_task_if_accepted: COAGENT-IMPL-01",
    ],
    "CoAgent/docs/decisions/coagent_goal_readiness_audit.md": [
        "Status: COAGENT-IMPL-01 and COAGENT-IMPL-02 complete.",
        "status: approved",
        "implementation_allowed: true",
    ],
    "Docs/Workflows/agent_task_ledger.md": [
        "COAGENT-IMPL-01",
        "done",
        "running",
    ],
    "CoAgent/docs/decisions/coagent_post_approval_backlog.md": [
        "COAGENT-IMPL-01",
        "Minimum Verification Before Each Task Closes",
    ],
}


REVISION_CHECKS = {
    "CoAgent/docs/decisions/coagent_design_decision_record.md": [
        "next_state_if_rejected: design_revision_required",
    ],
    "CoAgent/docs/decisions/coagent_goal_readiness_audit.md": [
        "design_revision_required",
    ],
}


Needle = Union[str, tuple[str, ...]]


def collect_missing(checks: dict[str, list[Needle]]) -> list[dict[str, str]]:
    missing: list[dict[str, str]] = []
    for path, needles in checks.items():
        try:
            text = read_rel(path)
        except FileNotFoundError:
            missing.append({"file": path, "missing": "<file>"})
            continue
        for needle in needles:
            if isinstance(needle, tuple):
                if not any(option in text for option in needle):
                    missing.append({"file": path, "missing": " OR ".join(needle)})
            elif needle not in text:
                missing.append({"file": path, "missing": needle})
    return missing


def next_action_for(decision_status: str, ok: bool) -> str:
    if not ok:
        return "fix gate consistency before asking for approval or implementing"
    if decision_status == "pending_user_decision":
        return (
            "请用户审阅 CoAgent/docs/decisions/coagent_design_review_brief.zh.md，"
            "并复制 decision_templates 中的 approved / approved_with_edits / "
            "revision_required 之一作为决策回复"
        )
    if decision_status in {"approved", "approved_with_edits"}:
        return (
            "continue from CoAgent/docs/decisions/coagent_post_approval_backlog.md; "
            "select the next approved incomplete backlog task or add a new "
            "explicit backlog item instead of expanding runtime scope opportunistically"
        )
    if decision_status == "revision_required":
        return (
            "revise the discussion packet and review briefs before any implementation"
        )
    return "repair CoAgent/docs/decisions/coagent_design_decision_record.md decision status"


def main() -> int:
    record_path = "CoAgent/docs/decisions/coagent_design_decision_record.md"
    try:
        record = read_rel(record_path)
    except FileNotFoundError:
        print(
            json.dumps(
                {
                    "ok": False,
                    "decision_status": "unknown",
                    "missing": [{"file": record_path, "missing": "<file>"}],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    decision_status = detect_decision_status(record)
    missing = collect_missing(BASE_CHECKS)

    if decision_status == "pending_user_decision":
        missing.extend(collect_missing(PENDING_CHECKS))
    elif decision_status in {"approved", "approved_with_edits"}:
        missing.extend(collect_missing(APPROVED_CHECKS))
    elif decision_status == "revision_required":
        missing.extend(collect_missing(REVISION_CHECKS))
    else:
        missing.append({"file": record_path, "missing": "known decision status"})

    checked_files = sorted(
        {
            *BASE_CHECKS.keys(),
            *(
                PENDING_CHECKS
                if decision_status == "pending_user_decision"
                else APPROVED_CHECKS
                if decision_status in {"approved", "approved_with_edits"}
                else REVISION_CHECKS
                if decision_status == "revision_required"
                else {}
            ).keys(),
        }
    )
    payload = {
        "ok": not missing,
        "decision_status": decision_status,
        "implementation_allowed": (not missing)
        and decision_status in {"approved", "approved_with_edits"},
        "review_entry": REVIEW_ENTRY,
        "decision_record": DECISION_RECORD,
        "first_allowed_task": FIRST_ALLOWED_TASK,
        "decision_templates": DECISION_TEMPLATES,
        "next_action": next_action_for(decision_status, not missing),
        "checked_files": len(checked_files),
        "missing": missing,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
