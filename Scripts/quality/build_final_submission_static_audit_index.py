#!/usr/bin/env python3
"""Build an index for final-submission static audit artifacts.

The index makes the current non-executing final-submission gate chain easy to
review. It does not generate final outputs or modify source reports.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_static_audit_index_20260610"

ARTIFACTS = [
    {
        "artifact_id": "report_source_edit_decision",
        "path": "Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision_check.json",
        "status_field": "ok",
        "ready_path": ["authorizes_application"],
        "role": "validates report-source edit decision before source edits",
    },
    {
        "artifact_id": "source_edit_readiness",
        "path": "Results/static_audits/simulation_report_source_edit_readiness_20260610/simulation_report_source_edit_readiness_gate.json",
        "status_field": "status",
        "ready_path": ["summary", "safe_to_apply_report_source_edits_now"],
        "role": "blocks applying report-source preview snippets until approved",
    },
    {
        "artifact_id": "source_edit_application_plan",
        "path": "Results/static_audits/simulation_report_source_edit_application_plan_20260610/simulation_report_source_edit_application_plan.json",
        "status_field": "status",
        "ready_path": ["summary", "safe_to_apply_report_source_edits_now"],
        "role": "turns approved report-source previews into non-applying application steps",
    },
    {
        "artifact_id": "source_edit_reviewer_summary",
        "path": "Results/static_audits/simulation_report_source_edit_reviewer_summary_20260610/simulation_report_source_edit_reviewer_summary.json",
        "status_field": "status",
        "ready_path": ["summary", "automated_execution_allowed"],
        "role": "summarizes preview impact and A1 review questions without executing",
    },
    {
        "artifact_id": "source_edit_application_audit_checklist",
        "path": "Results/static_audits/simulation_report_source_edit_application_audit_checklist_20260610/simulation_report_source_edit_application_audit_checklist.json",
        "status_field": "status",
        "ready_path": ["summary", "safe_to_apply_report_source_edits_now"],
        "role": "lists backup, diff, revert, and post-edit guard requirements before future source edits",
    },
    {
        "artifact_id": "source_output_readiness",
        "path": "Results/static_audits/submission_source_output_readiness_20260610/submission_source_output_readiness.json",
        "status_field": "status",
        "ready_path": ["summary", "safe_to_export_final_pdfs_now"],
        "role": "checks source docs/tooling before final PDF export",
    },
    {
        "artifact_id": "pdf_export_plan",
        "path": "Results/static_audits/pdf_export_dry_run_plan_20260610/pdf_export_dry_run_plan.json",
        "status_field": "status",
        "ready_path": ["summary", "safe_to_run_pdf_export_now"],
        "role": "records future PDF commands without running them",
    },
    {
        "artifact_id": "demo_video_storyboard",
        "path": "Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.json",
        "status_field": "status",
        "ready_path": ["summary", "safe_to_record_demo_video_now"],
        "role": "maps evidence to demo scenes before video recording",
    },
    {
        "artifact_id": "final_artifact_manifest",
        "path": "Results/static_audits/final_submission_artifacts_20260610/final_submission_artifact_manifest_check.json",
        "status_field": "status",
        "ready_path": ["summary", "final_submission_artifacts_ready"],
        "role": "checks final PDFs, demo video, and acceptance packet presence",
    },
    {
        "artifact_id": "final_acceptance_prereq",
        "path": "Results/static_audits/final_acceptance_packet_prereq_20260610/final_acceptance_packet_prereq_plan.json",
        "status_field": "status",
        "ready_path": ["summary", "safe_to_write_final_acceptance_packet_now"],
        "role": "blocks canonical final acceptance packet until prerequisites pass",
    },
    {
        "artifact_id": "final_output_execution_decision",
        "path": "Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision_check.json",
        "status_field": "status",
        "ready_path": ["summary", "authorizes_final_acceptance_packet"],
        "role": "records human/PMO execution decision without executing",
    },
    {
        "artifact_id": "final_submission_dashboard",
        "path": "Results/static_audits/final_submission_readiness_dashboard_20260610/final_submission_readiness_dashboard.json",
        "status_field": "status",
        "ready_path": ["summary", "final_submission_ready"],
        "role": "aggregates static readiness gates",
    },
    {
        "artifact_id": "final_submission_human_action_checklist",
        "path": "Results/static_audits/final_submission_human_action_checklist_20260610/final_submission_human_action_checklist.json",
        "status_field": "status",
        "ready_path": ["summary", "automated_execution_allowed"],
        "role": "groups human actions but does not execute them",
    },
    {
        "artifact_id": "final_submission_reviewer_action_map",
        "path": "Results/static_audits/final_submission_reviewer_action_map_20260610/final_submission_reviewer_action_map.json",
        "status_field": "status",
        "ready_path": ["summary", "automated_execution_allowed"],
        "role": "maps human actions to reviewer decisions and evidence",
    },
    {
        "artifact_id": "final_submission_human_review_decision_packet",
        "path": "Results/static_audits/final_submission_human_review_decision_packet_20260610/final_submission_human_review_decision_packet_check.json",
        "status_field": "status",
        "ready_path": ["summary", "automated_execution_allowed"],
        "role": "validates pending A1/A3/A6 human review decisions",
    },
    {
        "artifact_id": "final_submission_human_review_guide",
        "path": "Results/static_audits/final_submission_human_review_guide_20260610/final_submission_human_review_guide.json",
        "status_field": "status",
        "ready_path": ["summary", "automated_execution_allowed"],
        "role": "explains how to review A1/A3/A6 without executing",
    },
    {
        "artifact_id": "final_submission_readiness_chain",
        "path": "Results/static_audits/final_submission_readiness_chain_20260610/final_submission_readiness_chain_check.json",
        "status_field": "status",
        "ready_path": ["summary", "final_submission_ready"],
        "role": "checks static artifact chain integrity",
    },
    {
        "artifact_id": "final_submission_refresh_order",
        "path": "Results/static_audits/final_submission_refresh_order_20260610/final_submission_refresh_order_check.json",
        "status_field": "status",
        "ready_path": ["ok"],
        "role": "checks static audit refresh order and serial barriers",
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


def nested_get(data: dict[str, Any], path: list[str]) -> Any:
    value: Any = data
    for key in path:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def artifact_record(spec: dict[str, Any]) -> dict[str, Any]:
    path_value = str(spec["path"])
    path = repo_path(path_value)
    if not path.exists():
        return {
            "artifact_id": spec["artifact_id"],
            "path": path_value,
            "exists": False,
            "status": "missing",
            "ready": False,
            "role": spec["role"],
            "issue": "artifact missing",
        }
    try:
        data = read_json(path)
    except Exception as exc:
        return {
            "artifact_id": spec["artifact_id"],
            "path": path_value,
            "exists": True,
            "status": "unreadable",
            "ready": False,
            "role": spec["role"],
            "issue": str(exc),
        }
    status_field = str(spec["status_field"])
    status = data.get(status_field)
    if status_field == "ok":
        status = f"ok={data.get('ok')}"
    ready = nested_get(data, list(spec["ready_path"])) is True
    return {
        "artifact_id": spec["artifact_id"],
        "path": path_value,
        "exists": True,
        "status": status,
        "ready": ready,
        "role": spec["role"],
        "issue": "",
    }


def build_index() -> dict[str, Any]:
    records = [artifact_record(spec) for spec in ARTIFACTS]
    missing = [item for item in records if not item["exists"]]
    unreadable = [item for item in records if item["status"] == "unreadable"]
    ready = [item for item in records if item["ready"]]
    blocked = [item for item in records if item["exists"] and not item["ready"]]
    return {
        "index_id": "final_submission_static_audit_index_20260610",
        "status": "static_audit_index_not_final_submission",
        "summary": {
            "artifact_count": len(records),
            "missing_count": len(missing),
            "unreadable_count": len(unreadable),
            "ready_count": len(ready),
            "blocked_count": len(blocked),
            "final_submission_ready": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "artifacts": records,
        "claim_boundary": [
            "This index summarizes static audit artifacts only.",
            "It does not run generators.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(index: dict[str, Any], path: Path) -> None:
    summary = index["summary"]
    lines = [
        "# Final Submission Static Audit Index, 2026-06-10",
        "",
        f"Status: `{index['status']}`",
        "",
        "## Summary",
        "",
        f"- Artifacts: `{summary['artifact_count']}`",
        f"- Missing: `{summary['missing_count']}`",
        f"- Unreadable: `{summary['unreadable_count']}`",
        f"- Ready: `{summary['ready_count']}`",
        f"- Blocked: `{summary['blocked_count']}`",
        f"- Final submission ready: `{summary['final_submission_ready']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Artifacts",
        "",
        "| Artifact | Ready | Status | Path | Role |",
        "|---|---|---|---|---|",
    ]
    for item in index["artifacts"]:
        lines.append(
            f"| {item['artifact_id']} | {item['ready']} | `{item['status']}` | `{item['path']}` | {item['role']} |"
        )
    lines.extend(["", "## Claim Boundary", ""])
    for item in index["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def classification_for_artifact(artifact_id: str) -> str:
    hard_gate_ids = {
        "report_source_edit_decision",
        "source_edit_readiness",
        "source_edit_application_plan",
        "source_output_readiness",
        "pdf_export_plan",
        "demo_video_storyboard",
        "final_artifact_manifest",
        "final_acceptance_prereq",
        "final_output_execution_decision",
        "final_submission_dashboard",
        "final_submission_readiness_chain",
        "final_submission_refresh_order",
    }
    if artifact_id in hard_gate_ids:
        return "hard_gate"
    return "review_aid"


def write_readme(index: dict[str, Any], path: Path) -> None:
    hard_gates = [
        item
        for item in index["artifacts"]
        if classification_for_artifact(str(item["artifact_id"])) == "hard_gate"
    ]
    review_aids = [
        item
        for item in index["artifacts"]
        if classification_for_artifact(str(item["artifact_id"])) == "review_aid"
    ]
    summary = index["summary"]
    lines = [
        "# Final Submission Static Audit README",
        "",
        "This directory summarizes static audit outputs for human review. It is not a final submission package.",
        "",
        "## Current Status",
        "",
        f"- Index status: `{index['status']}`",
        f"- Artifact count: `{summary['artifact_count']}`",
        f"- Ready count: `{summary['ready_count']}`",
        f"- Blocked count: `{summary['blocked_count']}`",
        f"- Final submission ready: `{summary['final_submission_ready']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Hard Gates",
        "",
        "Hard gates can block source edits, final output export, final acceptance, or refresh ordering.",
        "A hard gate marked ready means only that the specific static condition passed; it does not override other blocked gates.",
        "",
        "| Artifact | Ready | Status | Role |",
        "|---|---:|---|---|",
    ]
    for item in hard_gates:
        lines.append(
            f"| {item['artifact_id']} | {item['ready']} | `{item['status']}` | {item['role']} |"
        )
    lines.extend(
        [
            "",
            "## Review Aids",
            "",
            "Review aids organize human decisions, checklist steps, or explanatory context.",
            "They do not authorize report-source edits, PDF export, video recording, or PMO final acceptance.",
            "",
            "| Artifact | Ready | Status | Role |",
            "|---|---:|---|---|",
        ]
    )
    for item in review_aids:
        lines.append(
            f"| {item['artifact_id']} | {item['ready']} | `{item['status']}` | {item['role']} |"
        )
    lines.extend(
        [
            "",
            "## Reviewer Use",
            "",
            "1. Start with `final_submission_static_audit_index.json` for machine-readable status.",
            "2. Use `final_submission_static_audit_index.md` for the full artifact table.",
            "3. Use this README to separate blocking gates from non-authorizing review aids.",
            "4. Treat all blocked hard gates as unresolved until their source artifacts are updated by an authorized workflow.",
            "",
            "## Claim Boundary",
            "",
        ]
    )
    for item in index["claim_boundary"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "- This README does not authorize applying report-source edits.",
            "- This README does not authorize PDF export, demo-video recording, or PMO final acceptance.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    index = build_index()
    json_path = output_dir / "final_submission_static_audit_index.json"
    md_path = output_dir / "final_submission_static_audit_index.md"
    readme_path = output_dir / "README.md"
    json_path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(index, md_path)
    write_readme(index, readme_path)
    print(
        json.dumps(
            {
                "ok": True,
                "index_json": rel(json_path),
                "index_markdown": rel(md_path),
                "readme": rel(readme_path),
                "artifact_count": index["summary"]["artifact_count"],
                "blocked_count": index["summary"]["blocked_count"],
                "final_submission_ready": index["summary"]["final_submission_ready"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
