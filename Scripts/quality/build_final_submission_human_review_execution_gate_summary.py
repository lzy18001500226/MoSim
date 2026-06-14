#!/usr/bin/env python3
"""Build a static execution-gate summary after human-review navigation aids."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REVIEWER_CHECKLIST = (
    ROOT
    / "Results/static_audits/final_submission_post_review_reviewer_checklist_20260610"
    / "final_submission_post_review_reviewer_checklist.json"
)
DEFAULT_DASHBOARD = (
    ROOT
    / "Results/static_audits/final_submission_readiness_dashboard_20260610"
    / "final_submission_readiness_dashboard.json"
)
DEFAULT_SOURCE_OUTPUT = (
    ROOT
    / "Results/static_audits/submission_source_output_readiness_20260610"
    / "submission_source_output_readiness.json"
)
DEFAULT_PDF_PLAN = ROOT / "Results/static_audits/pdf_export_dry_run_plan_20260610/pdf_export_dry_run_plan.json"
DEFAULT_DEMO_PLAN = (
    ROOT / "Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.json"
)
DEFAULT_FINAL_DECISION = (
    ROOT
    / "Results/static_audits/final_output_execution_decision_20260610"
    / "final_output_execution_decision_check.json"
)
DEFAULT_FINAL_ACCEPTANCE = (
    ROOT
    / "Results/static_audits/final_acceptance_packet_prereq_20260610"
    / "final_acceptance_packet_prereq_plan.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_human_review_execution_gate_20260610"


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


def blockers(data: dict[str, Any]) -> list[dict[str, Any]]:
    values = data.get("blockers", [])
    return [item for item in values if isinstance(item, dict)]


def source_record(path: Path, data: dict[str, Any]) -> dict[str, Any]:
    summary = data.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    return {
        "path": rel(path),
        "status": data.get("status", ""),
        "summary": summary,
    }


def target(
    target_id: str,
    label: str,
    gate_sources: list[str],
    blocking_reasons: list[str],
    readiness_flags: dict[str, Any],
) -> dict[str, Any]:
    return {
        "target_id": target_id,
        "label": label,
        "gate_sources": gate_sources,
        "ready_now": False,
        "blocking_reason_count": len(blocking_reasons),
        "blocking_reasons": blocking_reasons,
        "readiness_flags": readiness_flags,
        "requires_separate_authorization": True,
        "executes_now": False,
    }


def build_summary(
    reviewer_checklist_path: Path,
    dashboard_path: Path,
    source_output_path: Path,
    pdf_plan_path: Path,
    demo_plan_path: Path,
    final_decision_path: Path,
    final_acceptance_path: Path,
) -> dict[str, Any]:
    reviewer_checklist = read_json(reviewer_checklist_path)
    dashboard = read_json(dashboard_path)
    source_output = read_json(source_output_path)
    pdf_plan = read_json(pdf_plan_path)
    demo_plan = read_json(demo_plan_path)
    final_decision = read_json(final_decision_path)
    final_acceptance = read_json(final_acceptance_path)

    source_summary = source_output.get("summary", {})
    pdf_summary = pdf_plan.get("summary", {})
    demo_summary = demo_plan.get("summary", {})
    decision_summary = final_decision.get("summary", {})
    acceptance_summary = final_acceptance.get("summary", {})
    checklist_summary = reviewer_checklist.get("summary", {})

    targets = [
        target(
            "report_source_edit",
            "Report-source edit application",
            [rel(reviewer_checklist_path), rel(source_output_path)],
            [
                "review questions are not answered",
                "decision artifacts are not edited",
                "source edit readiness safe_to_apply remains false",
                "source edit application plan is not applied",
            ],
            {
                "review_action_count": checklist_summary.get("review_action_count", 0),
                "answers_questions_now": checklist_summary.get("answers_questions_now", False),
                "edits_decision_artifacts_now": checklist_summary.get("edits_decision_artifacts_now", False),
                "source_edit_readiness_safe_to_apply": source_summary.get("source_edit_readiness_safe_to_apply", False),
                "source_edit_application_plan_applied": source_summary.get("source_edit_application_plan_applied", False),
            },
        ),
        target(
            "pdf_export",
            "Final PDF export",
            [rel(pdf_plan_path), rel(final_decision_path), rel(source_output_path)],
            [
                "PDF engine is missing",
                "report-source edit is not approved for export",
                "final artifacts are not ready",
                "final-output execution decision does not authorize PDF export",
            ],
            {
                "pdf_engine_available": pdf_summary.get("pdf_engine_available", False),
                "source_edit_approved_for_export": pdf_summary.get("source_edit_approved_for_export", False),
                "safe_to_run_pdf_export_now": pdf_summary.get("safe_to_run_pdf_export_now", False),
                "authorizes_pdf_export": decision_summary.get("authorizes_pdf_export", False),
                "runs_pandoc_now": decision_summary.get("runs_pandoc_now", False),
            },
        ),
        target(
            "demo_video_recording",
            "Demo video recording/rendering",
            [rel(demo_plan_path), rel(final_decision_path)],
            [
                "storyboard still requires manual review before recording",
                "demo video artifact does not exist",
                "final-output execution decision does not authorize demo video recording",
            ],
            {
                "storyboard_ready_for_review": demo_summary.get("storyboard_ready_for_review", False),
                "demo_video_exists": demo_summary.get("demo_video_exists", False),
                "safe_to_record_demo_video_now": demo_summary.get("safe_to_record_demo_video_now", False),
                "authorizes_demo_video_recording": decision_summary.get("authorizes_demo_video_recording", False),
                "records_or_renders_video_now": decision_summary.get("records_or_renders_video_now", False),
            },
        ),
        target(
            "final_acceptance_packet",
            "Canonical PMO final acceptance packet",
            [rel(final_acceptance_path), rel(final_decision_path), rel(dashboard_path)],
            [
                "final artifacts are missing or failing",
                "PDF export is not ready",
                "demo video recording is not approved",
                "source-output readiness blocks acceptance",
                "final-output execution decision does not authorize final acceptance packet writing",
            ],
            {
                "final_artifacts_ready": acceptance_summary.get("final_artifacts_ready", False),
                "pdf_export_ready": acceptance_summary.get("pdf_export_ready", False),
                "demo_video_recording_ready": acceptance_summary.get("demo_video_recording_ready", False),
                "safe_to_write_final_acceptance_packet_now": acceptance_summary.get(
                    "safe_to_write_final_acceptance_packet_now", False
                ),
                "authorizes_final_acceptance_packet": decision_summary.get("authorizes_final_acceptance_packet", False),
                "writes_canonical_acceptance_packet_now": decision_summary.get(
                    "writes_canonical_acceptance_packet_now", False
                ),
            },
        ),
    ]
    return {
        "summary_id": "final_submission_human_review_execution_gate_20260610",
        "status": "human_review_execution_gate_summary_not_execution",
        "sources": {
            "reviewer_checklist": source_record(reviewer_checklist_path, reviewer_checklist),
            "readiness_dashboard": source_record(dashboard_path, dashboard),
            "source_output_readiness": source_record(source_output_path, source_output),
            "pdf_export_dry_run_plan": source_record(pdf_plan_path, pdf_plan),
            "demo_video_storyboard_plan": source_record(demo_plan_path, demo_plan),
            "final_output_execution_decision": source_record(final_decision_path, final_decision),
            "final_acceptance_prereq": source_record(final_acceptance_path, final_acceptance),
        },
        "summary": {
            "execution_target_count": len(targets),
            "blocked_execution_target_count": sum(1 for item in targets if not item["ready_now"]),
            "dashboard_blocking_gate_count": dashboard.get("summary", {}).get("blocking_gate_count", 0),
            "dashboard_blocker_count": dashboard.get("summary", {}).get("blocker_count", 0),
            "review_action_count": checklist_summary.get("review_action_count", 0),
            "total_question_count": checklist_summary.get("total_question_count", 0),
            "automated_execution_allowed": False,
            "answers_questions_now": False,
            "edits_decision_artifacts_now": False,
            "runs_commands_now": False,
            "creates_submission_dir_now": False,
            "runs_pandoc_now": False,
            "records_or_renders_video_now": False,
            "writes_canonical_acceptance_packet_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "execution_targets": targets,
        "dashboard_blockers": blockers(dashboard),
        "claim_boundary": [
            "This execution-gate summary is a static review artifact only.",
            "It does not answer reviewer questions.",
            "It does not fill answer-sheet values.",
            "It does not edit decision artifacts.",
            "It does not apply report-source edits.",
            "It does not create Results/submission.",
            "It does not run Pandoc.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write canonical PMO final acceptance.",
        ],
    }


def write_markdown(result: dict[str, Any], path: Path) -> None:
    summary = result["summary"]
    lines = [
        "# Final Submission Human-Review Execution Gate Summary, 2026-06-10",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Summary",
        "",
        f"- Execution targets: `{summary['execution_target_count']}`",
        f"- Blocked execution targets: `{summary['blocked_execution_target_count']}`",
        f"- Dashboard blocking gates: `{summary['dashboard_blocking_gate_count']}`",
        f"- Dashboard blockers: `{summary['dashboard_blocker_count']}`",
        f"- Review actions: `{summary['review_action_count']}`",
        f"- Review questions: `{summary['total_question_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Answers questions now: `{summary['answers_questions_now']}`",
        f"- Edits decision artifacts now: `{summary['edits_decision_artifacts_now']}`",
        f"- Runs commands now: `{summary['runs_commands_now']}`",
        f"- Creates submission dir now: `{summary['creates_submission_dir_now']}`",
        f"- Runs Pandoc now: `{summary['runs_pandoc_now']}`",
        f"- Records or renders video now: `{summary['records_or_renders_video_now']}`",
        f"- Writes canonical acceptance packet now: `{summary['writes_canonical_acceptance_packet_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Execution Targets",
        "",
    ]
    for target_record in result["execution_targets"]:
        lines.extend(
            [
                f"### {target_record['target_id']}",
                "",
                f"- Label: {target_record['label']}",
                f"- Ready now: `{target_record['ready_now']}`",
                f"- Blocking reasons: `{target_record['blocking_reason_count']}`",
                f"- Requires separate authorization: `{target_record['requires_separate_authorization']}`",
                f"- Executes now: `{target_record['executes_now']}`",
                "",
            ]
        )
    lines.extend(["## Claim Boundary", ""])
    for item in result["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reviewer-checklist", default=str(DEFAULT_REVIEWER_CHECKLIST.relative_to(ROOT)))
    parser.add_argument("--dashboard", default=str(DEFAULT_DASHBOARD.relative_to(ROOT)))
    parser.add_argument("--source-output", default=str(DEFAULT_SOURCE_OUTPUT.relative_to(ROOT)))
    parser.add_argument("--pdf-plan", default=str(DEFAULT_PDF_PLAN.relative_to(ROOT)))
    parser.add_argument("--demo-plan", default=str(DEFAULT_DEMO_PLAN.relative_to(ROOT)))
    parser.add_argument("--final-decision", default=str(DEFAULT_FINAL_DECISION.relative_to(ROOT)))
    parser.add_argument("--final-acceptance", default=str(DEFAULT_FINAL_ACCEPTANCE.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = build_summary(
        repo_path(args.reviewer_checklist),
        repo_path(args.dashboard),
        repo_path(args.source_output),
        repo_path(args.pdf_plan),
        repo_path(args.demo_plan),
        repo_path(args.final_decision),
        repo_path(args.final_acceptance),
    )
    json_path = output_dir / "final_submission_human_review_execution_gate_summary.json"
    md_path = output_dir / "final_submission_human_review_execution_gate_summary.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(result, md_path)
    print(
        json.dumps(
            {"ok": True, **result["summary"], "json": rel(json_path), "markdown": rel(md_path)},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
