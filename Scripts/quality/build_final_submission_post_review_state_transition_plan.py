#!/usr/bin/env python3
"""Build a non-applying post-review state-transition plan for final submission."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RERUN_MATRIX = (
    ROOT
    / "Results/static_audits/final_submission_post_review_rerun_matrix_20260610"
    / "final_submission_post_review_rerun_matrix.json"
)
DEFAULT_CLOSURE_CHECKLIST = (
    ROOT
    / "Results/static_audits/final_submission_manual_review_closure_checklist_20260610"
    / "final_submission_manual_review_closure_checklist.json"
)
DEFAULT_DASHBOARD = (
    ROOT
    / "Results/static_audits/final_submission_readiness_dashboard_20260610"
    / "final_submission_readiness_dashboard.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_post_review_state_transition_plan_20260610"


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def source_record(source_id: str, path: Path, data: dict[str, Any]) -> dict[str, Any]:
    summary = data.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    return {
        "source_id": source_id,
        "path": rel(path),
        "status": data.get("status", ""),
        "summary": summary,
    }


def summarize_commands(commands: list[Any]) -> dict[str, Any]:
    values = [str(command) for command in commands]
    return {
        "rerun_command_count": len(values),
        "first_command": values[0] if values else "",
        "last_command": values[-1] if values else "",
        "commands": values,
    }


def transition_for_row(row: dict[str, Any]) -> dict[str, Any]:
    action_id = str(row.get("action_id", ""))
    expected_future_decisions = row.get("expected_future_decisions", [])
    if not isinstance(expected_future_decisions, list):
        expected_future_decisions = []
    commands = row.get("rerun_commands_after_separate_review_edit", [])
    if not isinstance(commands, list):
        commands = []
    current_decision = row.get("current_decision", "")
    if not current_decision and isinstance(row.get("current_action_decisions"), dict):
        current_decision = "pending_review"
    return {
        "transition_id": f"TRANSITION-{action_id}",
        "action_id": action_id,
        "current_state": {
            "decision": current_decision or "pending_review",
            "rerun_readiness": row.get("rerun_readiness", ""),
        },
        "eligible_future_states_after_separate_human_edit": expected_future_decisions,
        "state_transition_guard": [
            "A separate human/PMO decision edit has been made.",
            "Decision artifact checker passes after the edit.",
            "Manual-review closure checklist has been reviewed.",
            "Post-review rerun commands are still launched in a separate authorized step.",
        ],
        "rerun_command_summary": summarize_commands(commands),
        "execution_still_requires": row.get("execution_still_requires", []),
        "forbidden_actions": row.get("forbidden_actions", []),
        "applies_transition_now": False,
        "runs_rerun_commands_now": False,
        "approves_now": False,
    }


def build_transition_plan(
    rerun_matrix_path: Path,
    closure_checklist_path: Path,
    dashboard_path: Path,
) -> dict[str, Any]:
    rerun_matrix = read_json(rerun_matrix_path)
    closure_checklist = read_json(closure_checklist_path)
    dashboard = read_json(dashboard_path)
    rows = [row for row in rerun_matrix.get("rows", []) if isinstance(row, dict)]
    transitions = [transition_for_row(row) for row in rows]
    return {
        "transition_plan_id": "final_submission_post_review_state_transition_plan_20260610",
        "status": "post_review_state_transition_plan_not_execution",
        "sources": {
            "post_review_rerun_matrix": source_record("post_review_rerun_matrix", rerun_matrix_path, rerun_matrix),
            "manual_review_closure_checklist": source_record(
                "manual_review_closure_checklist", closure_checklist_path, closure_checklist
            ),
            "final_submission_readiness_dashboard": source_record(
                "final_submission_readiness_dashboard", dashboard_path, dashboard
            ),
        },
        "summary": {
            "transition_count": len(transitions),
            "blocked_pending_review_row_count": rerun_matrix.get("summary", {}).get(
                "blocked_pending_review_row_count", 0
            ),
            "closure_item_count": closure_checklist.get("summary", {}).get("closure_item_count", 0),
            "dashboard_blocking_gate_count": dashboard.get("summary", {}).get("blocking_gate_count", 0),
            "automated_execution_allowed": False,
            "applies_transitions_now": False,
            "runs_rerun_commands_now": False,
            "edits_decision_templates_now": False,
            "approves_or_executes_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "transitions": transitions,
        "global_state_transition_sequence": [
            "Human/PMO fills answer sheet in a separately authorized artifact.",
            "Human/PMO edits decision templates in a separately authorized step.",
            "Run decision-template checkers after the edit.",
            "Run only the applicable post-review rerun command chain after authorization.",
            "Regenerate dashboard and readiness chain to observe changed gate state.",
        ],
        "claim_boundary": [
            "This state-transition plan is a static planning artifact only.",
            "It does not fill answer-sheet values.",
            "It does not edit decision templates.",
            "It does not approve decisions.",
            "It does not apply state transitions.",
            "It does not run rerun commands.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(plan: dict[str, Any], path: Path) -> None:
    summary = plan["summary"]
    lines = [
        "# Final Submission Post-Review State Transition Plan, 2026-06-10",
        "",
        f"Status: `{plan['status']}`",
        "",
        "## Summary",
        "",
        f"- Transitions: `{summary['transition_count']}`",
        f"- Blocked pending-review rows: `{summary['blocked_pending_review_row_count']}`",
        f"- Closure items: `{summary['closure_item_count']}`",
        f"- Dashboard blocking gates: `{summary['dashboard_blocking_gate_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Applies transitions now: `{summary['applies_transitions_now']}`",
        f"- Runs rerun commands now: `{summary['runs_rerun_commands_now']}`",
        f"- Edits decision templates now: `{summary['edits_decision_templates_now']}`",
        f"- Approves or executes now: `{summary['approves_or_executes_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Global State Transition Sequence",
        "",
    ]
    for index, item in enumerate(plan["global_state_transition_sequence"], start=1):
        lines.append(f"{index}. {item}")
    lines.extend(["", "## Transitions", ""])
    for transition in plan["transitions"]:
        commands = transition["rerun_command_summary"]
        lines.extend(
            [
                f"### {transition['transition_id']}",
                "",
                f"- Action: `{transition['action_id']}`",
                f"- Current decision: `{transition['current_state']['decision']}`",
                f"- Rerun readiness: `{transition['current_state']['rerun_readiness']}`",
                f"- Future states: `{', '.join(map(str, transition['eligible_future_states_after_separate_human_edit']))}`",
                f"- Rerun commands: `{commands['rerun_command_count']}`",
                f"- First command: `{commands['first_command']}`",
                f"- Last command: `{commands['last_command']}`",
                f"- Applies transition now: `{transition['applies_transition_now']}`",
                f"- Runs rerun commands now: `{transition['runs_rerun_commands_now']}`",
                f"- Approves now: `{transition['approves_now']}`",
                "- State transition guard:",
            ]
        )
        for guard in transition["state_transition_guard"]:
            lines.append(f"  - {guard}")
        lines.append("")
    lines.extend(["## Claim Boundary", ""])
    for item in plan["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rerun-matrix", default=str(DEFAULT_RERUN_MATRIX.relative_to(ROOT)))
    parser.add_argument("--closure-checklist", default=str(DEFAULT_CLOSURE_CHECKLIST.relative_to(ROOT)))
    parser.add_argument("--dashboard", default=str(DEFAULT_DASHBOARD.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = build_transition_plan(
        repo_path(args.rerun_matrix),
        repo_path(args.closure_checklist),
        repo_path(args.dashboard),
    )
    json_path = output_dir / "final_submission_post_review_state_transition_plan.json"
    md_path = output_dir / "final_submission_post_review_state_transition_plan.md"
    json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(plan, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "transition_json": rel(json_path),
                "transition_markdown": rel(md_path),
                "transition_count": plan["summary"]["transition_count"],
                "dashboard_blocking_gate_count": plan["summary"]["dashboard_blocking_gate_count"],
                "applies_transitions_now": plan["summary"]["applies_transitions_now"],
                "runs_rerun_commands_now": plan["summary"]["runs_rerun_commands_now"],
                "automated_execution_allowed": plan["summary"]["automated_execution_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
