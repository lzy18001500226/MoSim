#!/usr/bin/env python3
"""Build a downstream review artifact bundle index for final submission."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_review_artifact_bundle_20260610"

BUNDLE_ARTIFACTS = [
    {
        "artifact_id": "blocked_gate_triage_map",
        "json_path": "Results/static_audits/final_submission_blocked_gate_triage_map_20260610/final_submission_blocked_gate_triage_map.json",
        "markdown_path": "Results/static_audits/final_submission_blocked_gate_triage_map_20260610/final_submission_blocked_gate_triage_map.md",
        "expected_status": "blocked_gate_triage_map_not_execution",
        "purpose": "group blocked gates before human review",
    },
    {
        "artifact_id": "human_decision_diff_template",
        "json_path": "Results/static_audits/final_submission_human_decision_diff_template_20260610/final_submission_human_decision_diff_template.json",
        "markdown_path": "Results/static_audits/final_submission_human_decision_diff_template_20260610/final_submission_human_decision_diff_template.md",
        "expected_status": "human_decision_diff_template_not_execution",
        "purpose": "show editable decision fields without editing templates",
    },
    {
        "artifact_id": "reviewer_quickstart",
        "json_path": "Results/static_audits/final_submission_reviewer_quickstart_20260610/final_submission_reviewer_quickstart.json",
        "markdown_path": "Results/static_audits/final_submission_reviewer_quickstart_20260610/final_submission_reviewer_quickstart.md",
        "expected_status": "reviewer_quickstart_not_execution",
        "purpose": "order the minimum A1/A3/A6 review files",
    },
    {
        "artifact_id": "review_progress_snapshot",
        "json_path": "Results/static_audits/final_submission_review_progress_snapshot_20260610/final_submission_review_progress_snapshot.json",
        "markdown_path": "Results/static_audits/final_submission_review_progress_snapshot_20260610/final_submission_review_progress_snapshot.md",
        "expected_status": "review_progress_snapshot_not_execution",
        "purpose": "summarize downstream review progress",
    },
    {
        "artifact_id": "post_review_rerun_matrix",
        "json_path": "Results/static_audits/final_submission_post_review_rerun_matrix_20260610/final_submission_post_review_rerun_matrix.json",
        "markdown_path": "Results/static_audits/final_submission_post_review_rerun_matrix_20260610/final_submission_post_review_rerun_matrix.md",
        "expected_status": "post_review_rerun_matrix_not_execution",
        "purpose": "plan future reruns after separate human decisions",
    },
    {
        "artifact_id": "manual_review_answer_sheet",
        "json_path": "Results/static_audits/final_submission_manual_review_answer_sheet_20260610/final_submission_manual_review_answer_sheet_template.json",
        "markdown_path": "Results/static_audits/final_submission_manual_review_answer_sheet_20260610/final_submission_manual_review_answer_sheet_template.md",
        "expected_status": "manual_review_answer_sheet_template_not_execution",
        "purpose": "provide placeholders for future human answers",
    },
    {
        "artifact_id": "answer_sheet_decision_consistency",
        "json_path": "Results/static_audits/final_submission_manual_review_answer_sheet_20260610/final_submission_answer_sheet_decision_consistency_check.json",
        "markdown_path": "",
        "expected_status": "answer_sheet_decision_consistency_check_not_execution",
        "purpose": "confirm answer-sheet placeholders were not copied into decisions",
    },
]


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


def artifact_record(spec: dict[str, str]) -> dict[str, Any]:
    json_path = repo_path(spec["json_path"])
    markdown_path = repo_path(spec["markdown_path"]) if spec.get("markdown_path") else None
    issues: list[str] = []
    status = "missing"
    summary: dict[str, Any] = {}
    if not json_path.exists():
        issues.append("json artifact missing")
    else:
        data = read_json(json_path)
        status = str(data.get("status", ""))
        raw_summary = data.get("summary", {})
        summary = raw_summary if isinstance(raw_summary, dict) else {}
        if status != spec["expected_status"]:
            issues.append(f"expected status {spec['expected_status']}, got {status}")
    markdown_exists = True
    if markdown_path is not None:
        markdown_exists = markdown_path.exists()
        if not markdown_exists:
            issues.append("markdown artifact missing")
    return {
        "artifact_id": spec["artifact_id"],
        "json_path": spec["json_path"],
        "markdown_path": spec.get("markdown_path", ""),
        "json_exists": json_path.exists(),
        "markdown_exists": markdown_exists,
        "status": status,
        "expected_status": spec["expected_status"],
        "purpose": spec["purpose"],
        "summary": summary,
        "ready_for_review_bundle": not issues,
        "issues": issues,
    }


def build_bundle_index() -> dict[str, Any]:
    records = [artifact_record(spec) for spec in BUNDLE_ARTIFACTS]
    missing = [item for item in records if not item["json_exists"] or item["markdown_exists"] is False]
    mismatched = [item for item in records if item["status"] != item["expected_status"]]
    ready = [item for item in records if item["ready_for_review_bundle"]]
    return {
        "bundle_id": "final_submission_review_artifact_bundle_20260610",
        "status": "review_artifact_bundle_index_not_execution",
        "summary": {
            "bundle_artifact_count": len(records),
            "ready_bundle_artifact_count": len(ready),
            "missing_or_incomplete_count": len(missing),
            "status_mismatch_count": len(mismatched),
            "automated_execution_allowed": False,
            "included_in_static_audit_index": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "review_order": [
            "reviewer_quickstart",
            "blocked_gate_triage_map",
            "human_decision_diff_template",
            "manual_review_answer_sheet",
            "answer_sheet_decision_consistency",
            "post_review_rerun_matrix",
            "review_progress_snapshot",
        ],
        "artifacts": records,
        "claim_boundary": [
            "This bundle index summarizes downstream review artifacts only.",
            "It is intentionally not added back into final_submission_static_audit_index.json.",
            "It does not edit decision templates.",
            "It does not approve decisions.",
            "It does not run post-review checkers.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(bundle: dict[str, Any], path: Path) -> None:
    summary = bundle["summary"]
    lines = [
        "# Final Submission Review Artifact Bundle Index, 2026-06-10",
        "",
        f"Status: `{bundle['status']}`",
        "",
        "## Summary",
        "",
        f"- Bundle artifacts: `{summary['bundle_artifact_count']}`",
        f"- Ready bundle artifacts: `{summary['ready_bundle_artifact_count']}`",
        f"- Missing or incomplete: `{summary['missing_or_incomplete_count']}`",
        f"- Status mismatches: `{summary['status_mismatch_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Included in static audit index: `{summary['included_in_static_audit_index']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Review Order",
        "",
    ]
    for index, artifact_id in enumerate(bundle["review_order"], start=1):
        lines.append(f"{index}. `{artifact_id}`")
    lines.extend(["", "## Artifacts", ""])
    for item in bundle["artifacts"]:
        lines.extend(
            [
                f"### {item['artifact_id']}",
                "",
                f"- JSON: `{item['json_path']}` exists=`{item['json_exists']}`",
                f"- Markdown: `{item['markdown_path'] or 'none'}` exists=`{item['markdown_exists']}`",
                f"- Status: `{item['status']}`",
                f"- Purpose: {item['purpose']}",
                f"- Ready for bundle: `{item['ready_for_review_bundle']}`",
            ]
        )
        if item["issues"]:
            lines.append("- Issues:")
            for issue in item["issues"]:
                lines.append(f"  - {issue}")
        lines.append("")
    lines.extend(["## Claim Boundary", ""])
    for item in bundle["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle = build_bundle_index()
    json_path = output_dir / "final_submission_review_artifact_bundle_index.json"
    md_path = output_dir / "final_submission_review_artifact_bundle_index.md"
    json_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(bundle, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "bundle_json": rel(json_path),
                "bundle_markdown": rel(md_path),
                "bundle_artifact_count": bundle["summary"]["bundle_artifact_count"],
                "ready_bundle_artifact_count": bundle["summary"]["ready_bundle_artifact_count"],
                "missing_or_incomplete_count": bundle["summary"]["missing_or_incomplete_count"],
                "status_mismatch_count": bundle["summary"]["status_mismatch_count"],
                "automated_execution_allowed": bundle["summary"]["automated_execution_allowed"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
