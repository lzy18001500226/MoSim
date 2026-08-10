#!/usr/bin/env python3
"""Build a blocked application plan for simulation-report source edits.

The plan consumes the non-applying patch preview and the A1 decision artifact.
It never edits Docs/报告/仿真分析报告_正文骨架.md.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PREVIEW = (
    ROOT
    / "Results/static_audits/simulation_report_patch_preview_20260610"
    / "simulation_report_patch_preview.json"
)
DEFAULT_DECISION = (
    ROOT
    / "Results/static_audits/report_source_edit_decision_template_20260610"
    / "report_source_edit_decision.template.json"
)
DEFAULT_DECISION_CHECK = (
    ROOT
    / "Results/static_audits/report_source_edit_decision_template_20260610"
    / "report_source_edit_decision_check.json"
)
DEFAULT_READINESS = (
    ROOT
    / "Results/static_audits/simulation_report_source_edit_readiness_20260610"
    / "simulation_report_source_edit_readiness_gate.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/simulation_report_source_edit_application_plan_20260610"


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


def build_step(preview: dict[str, Any], approved_ids: set[str], rejected_ids: set[str]) -> dict[str, Any]:
    preview_id = str(preview.get("preview_id", ""))
    approved = preview_id in approved_ids
    rejected = preview_id in rejected_ids
    return {
        "preview_id": preview_id,
        "source_action_id": preview.get("source_action_id", ""),
        "operation": preview.get("operation", ""),
        "target": preview.get("target", ""),
        "line_hint": preview.get("line_hint"),
        "approved": approved,
        "rejected": rejected,
        "planned_for_application": approved and not rejected,
        "applies_now": False,
        "safety_boundary": preview.get("safety_boundary", ""),
    }


def build_plan(preview_path: Path, decision_path: Path, decision_check_path: Path, readiness_path: Path) -> dict[str, Any]:
    preview = read_json(preview_path)
    decision = read_json(decision_path)
    decision_check = read_json(decision_check_path)
    readiness = read_json(readiness_path)
    approved_ids = {str(item) for item in decision.get("approved_preview_ids", [])}
    rejected_ids = {str(item) for item in decision.get("rejected_preview_ids", [])}
    steps = [build_step(item, approved_ids, rejected_ids) for item in preview.get("previews", []) if isinstance(item, dict)]
    planned_count = sum(1 for step in steps if step["planned_for_application"])
    safe_to_apply = (
        decision.get("decision") in {"approved", "narrowed"}
        and decision.get("safe_to_apply_report_source_edits") is True
        and decision_check.get("authorizes_application") is True
        and readiness.get("summary", {}).get("safe_to_apply_report_source_edits_now") is True
        and planned_count > 0
    )
    return {
        "plan_id": "simulation_report_source_edit_application_plan_20260610",
        "status": (
            "source_edit_application_plan_ready_not_applied"
            if safe_to_apply
            else "source_edit_application_plan_blocked_pending_human_review"
        ),
        "inputs": {
            "simulation_report": "Docs/报告/仿真分析报告_正文骨架.md",
            "patch_preview": rel(preview_path),
            "report_source_edit_decision": rel(decision_path),
            "report_source_edit_decision_check": rel(decision_check_path),
            "source_edit_readiness_gate": rel(readiness_path),
        },
        "summary": {
            "preview_count": len(steps),
            "approved_preview_count": len(approved_ids),
            "rejected_preview_count": len(rejected_ids),
            "planned_application_count": planned_count,
            "decision": decision.get("decision", ""),
            "decision_authorizes_application": decision_check.get("authorizes_application") is True,
            "readiness_safe_to_apply": readiness.get("summary", {}).get("safe_to_apply_report_source_edits_now") is True,
            "safe_to_apply_report_source_edits_now": safe_to_apply,
            "edits_report_source": False,
            "applies_report_source_edits_now": False,
            "deletes_content": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "application_steps": steps,
        "blocked_reason": ""
        if safe_to_apply
        else "A1 report-source edit decision is not approved or readiness gate is still blocked.",
        "claim_boundary": [
            "This plan is a non-applying source-edit application plan.",
            "It does not edit Docs/报告/仿真分析报告_正文骨架.md.",
            "It does not delete content.",
            "It does not run a patch command.",
            "It does not export PDFs/video or write PMO final acceptance.",
        ],
    }


def write_markdown(plan: dict[str, Any], path: Path) -> None:
    summary = plan["summary"]
    lines = [
        "# Simulation Report Source Edit Application Plan, 2026-06-10",
        "",
        f"Status: `{plan['status']}`",
        "",
        "## Summary",
        "",
        f"- Preview count: `{summary['preview_count']}`",
        f"- Approved previews: `{summary['approved_preview_count']}`",
        f"- Rejected previews: `{summary['rejected_preview_count']}`",
        f"- Planned applications: `{summary['planned_application_count']}`",
        f"- Decision: `{summary['decision']}`",
        f"- Decision authorizes application: `{summary['decision_authorizes_application']}`",
        f"- Readiness safe to apply: `{summary['readiness_safe_to_apply']}`",
        f"- Safe to apply now: `{summary['safe_to_apply_report_source_edits_now']}`",
        f"- Edits report source: `{summary['edits_report_source']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Blocked Reason",
        "",
        plan["blocked_reason"] or "None",
        "",
        "## Application Steps",
        "",
        "| Preview | Operation | Target | Approved | Planned | Applies Now |",
        "|---|---|---|---|---|---|",
    ]
    for step in plan["application_steps"]:
        lines.append(
            f"| {step['preview_id']} | `{step['operation']}` | {step['target']} | {step['approved']} | {step['planned_for_application']} | {step['applies_now']} |"
        )
    lines.extend(["", "## Claim Boundary", ""])
    for item in plan["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preview", default=str(DEFAULT_PREVIEW.relative_to(ROOT)))
    parser.add_argument("--decision", default=str(DEFAULT_DECISION.relative_to(ROOT)))
    parser.add_argument("--decision-check", default=str(DEFAULT_DECISION_CHECK.relative_to(ROOT)))
    parser.add_argument("--readiness", default=str(DEFAULT_READINESS.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = build_plan(
        repo_path(args.preview),
        repo_path(args.decision),
        repo_path(args.decision_check),
        repo_path(args.readiness),
    )
    json_path = output_dir / "simulation_report_source_edit_application_plan.json"
    md_path = output_dir / "simulation_report_source_edit_application_plan.md"
    json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(plan, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "plan_json": rel(json_path),
                "plan_markdown": rel(md_path),
                "status": plan["status"],
                "planned_application_count": plan["summary"]["planned_application_count"],
                "safe_to_apply_report_source_edits_now": plan["summary"]["safe_to_apply_report_source_edits_now"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
