#!/usr/bin/env python3
"""Build a per-step open-file bundle for final-submission manual review.

This bundle joins the manual-review shortest path with reviewer evidence files
and checksum metadata. It is a static navigation artifact only: it does not
open files, answer questions, edit decision artifacts, run commands, or
authorize final-output execution.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SHORTEST_PATH = (
    ROOT
    / "Results/static_audits/final_submission_manual_review_shortest_path_20260610"
    / "final_submission_manual_review_shortest_path_note.json"
)
DEFAULT_REVIEWER_EVIDENCE_INDEX = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_evidence_index_20260610"
    / "final_submission_reviewer_evidence_index.json"
)
DEFAULT_CHECKSUM_INDEX = (
    ROOT
    / "Results/static_audits/final_submission_reviewer_open_file_checksum_index_20260610"
    / "final_submission_reviewer_open_file_checksum_index.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_open_file_shortest_path_bundle_20260610"


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


def evidence_by_action(index: dict[str, Any]) -> dict[str, dict[str, Any]]:
    actions = index.get("review_actions", [])
    if not isinstance(actions, list):
        return {}
    return {str(action.get("action_id", "")): action for action in actions if isinstance(action, dict)}


def checksum_by_path(index: dict[str, Any]) -> dict[str, dict[str, Any]]:
    files = index.get("open_files", [])
    if not isinstance(files, list):
        return {}
    return {str(record.get("path", "")): record for record in files if isinstance(record, dict)}


def file_record(
    evidence_file: dict[str, Any],
    checksum_lookup: dict[str, dict[str, Any]],
    action_id: str,
    first_seen_by: dict[str, str],
) -> tuple[dict[str, Any], list[str]]:
    issues: list[str] = []
    path_value = Path(str(evidence_file.get("path", ""))).as_posix()
    checksum = checksum_lookup.get(path_value)
    if checksum is None:
        issues.append(f"{action_id} references file missing from checksum index: {path_value}")
        checksum = {}
    first_seen_action = first_seen_by.get(path_value, "")
    record = {
        "path": path_value,
        "source": evidence_file.get("source", ""),
        "required": bool(evidence_file.get("required", True)),
        "exists": bool(evidence_file.get("exists", False)),
        "checksum_readable": bool(checksum.get("readable", False)),
        "checksum_sha256": checksum.get("sha256", ""),
        "checksum_size_bytes": checksum.get("size_bytes"),
        "checksum_mtime_utc": checksum.get("mtime_utc", ""),
        "checksum_issue": checksum.get("issue", ""),
        "first_seen_action_id": first_seen_action,
        "is_new_open_file": not first_seen_action,
        "reused_from_prior_step": bool(first_seen_action),
    }
    if record["required"] and not record["exists"]:
        issues.append(f"{action_id} references missing required file: {path_value}")
    if record["exists"] and not record["checksum_readable"]:
        issues.append(f"{action_id} references unreadable checksum file: {path_value}")
    return record, issues


def build_bundle(
    shortest_path_path: Path,
    reviewer_evidence_index_path: Path,
    checksum_index_path: Path,
) -> dict[str, Any]:
    shortest_path = read_json(shortest_path_path)
    evidence_index = read_json(reviewer_evidence_index_path)
    checksum_index = read_json(checksum_index_path)
    shortest_summary = shortest_path.get("summary", {})
    evidence_summary = evidence_index.get("summary", {})
    checksum_summary = checksum_index.get("summary", {})
    if not isinstance(shortest_summary, dict):
        shortest_summary = {}
    if not isinstance(evidence_summary, dict):
        evidence_summary = {}
    if not isinstance(checksum_summary, dict):
        checksum_summary = {}

    issues: list[str] = []
    if shortest_path.get("status") != "manual_review_shortest_path_note_not_execution":
        issues.append("source shortest-path note status is not manual_review_shortest_path_note_not_execution")
    if evidence_index.get("status") != "reviewer_evidence_index_not_execution":
        issues.append("source reviewer evidence index status is not reviewer_evidence_index_not_execution")
    if checksum_index.get("status") != "reviewer_open_file_checksum_index_not_execution":
        issues.append("source checksum index status is not reviewer_open_file_checksum_index_not_execution")
    if int(shortest_summary.get("issue_count", 0)) != 0:
        issues.append("source shortest-path note has open issues")
    if int(evidence_summary.get("issue_count", 0)) != 0:
        issues.append("source reviewer evidence index has open issues")
    if int(checksum_summary.get("issue_count", 0)) != 0:
        issues.append("source checksum index has open issues")
    if int(checksum_summary.get("drift_from_previous_output_count", 0)) != 0:
        issues.append("source checksum index reports open-file drift")

    evidence_lookup = evidence_by_action(evidence_index)
    checksum_lookup = checksum_by_path(checksum_index)
    first_seen_by: dict[str, str] = {}
    step_records: list[dict[str, Any]] = []
    all_references = 0
    reused_references = 0

    for step in shortest_path.get("shortest_path", []):
        if not isinstance(step, dict):
            continue
        action_id = str(step.get("action_id", ""))
        evidence_action = evidence_lookup.get(action_id)
        if evidence_action is None:
            issues.append(f"shortest-path action missing from reviewer evidence index: {action_id}")
            evidence_files: list[dict[str, Any]] = []
        else:
            evidence_files = [
                item
                for item in evidence_action.get("review_evidence_files", [])
                if isinstance(item, dict)
            ]
        new_files: list[dict[str, Any]] = []
        reused_files: list[dict[str, Any]] = []
        ordered_files: list[dict[str, Any]] = []
        for evidence_file in evidence_files:
            all_references += 1
            record, record_issues = file_record(evidence_file, checksum_lookup, action_id, first_seen_by)
            issues.extend(record_issues)
            if record["is_new_open_file"]:
                first_seen_by[record["path"]] = action_id
                record["first_seen_action_id"] = action_id
                new_files.append(record)
            else:
                reused_references += 1
                reused_files.append(record)
            ordered_files.append(record)
        step_records.append(
            {
                "order": int(step.get("order", len(step_records) + 1)),
                "action_id": action_id,
                "owner": step.get("owner", ""),
                "stage_class": step.get("stage_class", ""),
                "decision_needed": step.get("decision_needed", ""),
                "prerequisite_action_ids": list(step.get("prerequisite_action_ids", [])),
                "open_file_reference_count": len(ordered_files),
                "new_open_file_count": len(new_files),
                "reused_open_file_count": len(reused_files),
                "new_open_files": new_files,
                "reused_open_files": reused_files,
                "ordered_open_files": ordered_files,
                "opens_files_now": False,
                "answers_questions_now": False,
                "fills_answers_now": False,
                "copies_answers_now": False,
                "edits_decision_artifacts_now": False,
                "runs_commands_now": False,
                "authorizes_execution_now": False,
                "generates_final_outputs": False,
                "final_acceptance": False,
            }
        )

    unique_open_file_count = len(first_seen_by)
    expected_unique = int(checksum_summary.get("unique_open_file_count", unique_open_file_count))
    expected_refs = int(checksum_summary.get("total_open_file_reference_count", all_references))
    if unique_open_file_count != expected_unique:
        issues.append(
            f"unique open-file count mismatch: bundle={unique_open_file_count} checksum_index={expected_unique}"
        )
    if all_references != expected_refs:
        issues.append(
            f"open-file reference count mismatch: bundle={all_references} checksum_index={expected_refs}"
        )

    summary = {
        "source_shortest_path_status": shortest_path.get("status", ""),
        "source_reviewer_evidence_status": evidence_index.get("status", ""),
        "source_checksum_status": checksum_index.get("status", ""),
        "path_step_count": len(step_records),
        "unique_open_file_count": unique_open_file_count,
        "total_open_file_reference_count": all_references,
        "new_open_file_count": unique_open_file_count,
        "reused_open_file_reference_count": reused_references,
        "checksum_file_count": int(checksum_summary.get("checksum_file_count", 0)),
        "missing_open_file_count": int(checksum_summary.get("missing_open_file_count", 0)),
        "unreadable_open_file_count": int(checksum_summary.get("unreadable_open_file_count", 0)),
        "drift_from_previous_output_count": int(checksum_summary.get("drift_from_previous_output_count", 0)),
        "issue_count": len(issues),
        "automated_execution_allowed": False,
        "opens_files_now": False,
        "answers_questions_now": False,
        "fills_answers_now": False,
        "copies_answers_now": False,
        "edits_decision_artifacts_now": False,
        "runs_commands_now": False,
        "authorizes_execution_now": False,
        "generates_final_outputs": False,
        "final_acceptance": False,
    }
    return {
        "bundle_id": "final_submission_open_file_shortest_path_bundle_20260610",
        "status": "open_file_shortest_path_bundle_not_execution",
        "sources": {
            "manual_review_shortest_path_note": rel(shortest_path_path),
            "reviewer_evidence_index": rel(reviewer_evidence_index_path),
            "reviewer_open_file_checksum_index": rel(checksum_index_path),
        },
        "summary": summary,
        "path_steps": step_records,
        "issues": issues,
        "claim_boundary": [
            "This open-file shortest-path bundle is a static navigation artifact only.",
            "It does not open files in an editor or UI.",
            "It does not answer review questions.",
            "It does not fill or copy answer-sheet values.",
            "It does not edit decision artifacts.",
            "It does not approve or reject decisions.",
            "It does not install PDF tooling.",
            "It does not create final artifacts.",
            "It does not rerun readiness gates.",
            "It does not run commands.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
            "It does not run live tools or visible-thread dispatch.",
        ],
    }


def write_markdown(bundle: dict[str, Any], path: Path) -> None:
    summary = bundle["summary"]
    lines = [
        "# Final Submission Open-File Shortest-Path Bundle, 2026-06-10",
        "",
        f"Status: `{bundle['status']}`",
        "",
        "## Summary",
        "",
        f"- Shortest-path status: `{summary['source_shortest_path_status']}`",
        f"- Reviewer evidence status: `{summary['source_reviewer_evidence_status']}`",
        f"- Checksum status: `{summary['source_checksum_status']}`",
        f"- Path steps: `{summary['path_step_count']}`",
        f"- Unique open files: `{summary['unique_open_file_count']}`",
        f"- Total open-file references: `{summary['total_open_file_reference_count']}`",
        f"- New open files: `{summary['new_open_file_count']}`",
        f"- Reused open-file references: `{summary['reused_open_file_reference_count']}`",
        f"- Checksum files: `{summary['checksum_file_count']}`",
        f"- Missing open files: `{summary['missing_open_file_count']}`",
        f"- Unreadable open files: `{summary['unreadable_open_file_count']}`",
        f"- Drift from previous output: `{summary['drift_from_previous_output_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- Opens files now: `{summary['opens_files_now']}`",
        f"- Runs commands now: `{summary['runs_commands_now']}`",
        f"- Authorizes execution now: `{summary['authorizes_execution_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Path Steps",
        "",
    ]
    for step in bundle["path_steps"]:
        lines.extend(
            [
                f"### {step['order']}. {step['action_id']}",
                "",
                f"- Owner: `{step['owner']}`",
                f"- Class: `{step['stage_class']}`",
                f"- Open-file references: `{step['open_file_reference_count']}`",
                f"- New open files: `{step['new_open_file_count']}`",
                f"- Reused open files: `{step['reused_open_file_count']}`",
                f"- Opens files now: `{step['opens_files_now']}`",
                "",
                "New open files:",
                "",
            ]
        )
        if step["new_open_files"]:
            for item in step["new_open_files"]:
                lines.append(f"- `{item['path']}`")
        else:
            lines.append("- None")
        lines.extend(["", "Reused open files:", ""])
        if step["reused_open_files"]:
            for item in step["reused_open_files"]:
                lines.append(f"- `{item['path']}` from `{item['first_seen_action_id']}`")
        else:
            lines.append("- None")
        lines.append("")
    lines.extend(["## Issues", ""])
    if bundle["issues"]:
        for issue in bundle["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in bundle["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shortest-path", default=str(DEFAULT_SHORTEST_PATH.relative_to(ROOT)))
    parser.add_argument("--reviewer-evidence-index", default=str(DEFAULT_REVIEWER_EVIDENCE_INDEX.relative_to(ROOT)))
    parser.add_argument("--checksum-index", default=str(DEFAULT_CHECKSUM_INDEX.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle = build_bundle(
        repo_path(args.shortest_path),
        repo_path(args.reviewer_evidence_index),
        repo_path(args.checksum_index),
    )
    json_path = output_dir / "final_submission_open_file_shortest_path_bundle.json"
    md_path = output_dir / "final_submission_open_file_shortest_path_bundle.md"
    json_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(bundle, md_path)
    print(
        json.dumps(
            {"ok": not bundle["issues"], **bundle["summary"], "json": rel(json_path), "markdown": rel(md_path)},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not bundle["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
