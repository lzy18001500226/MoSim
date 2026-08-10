#!/usr/bin/env python3
"""Validate the non-applying simulation-report patch preview."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / "Docs" / "报告" / "仿真分析报告_正文骨架.md"
DEFAULT_PREVIEW = (
    ROOT
    / "Results"
    / "static_audits"
    / "simulation_report_patch_preview_20260610"
    / "simulation_report_patch_preview.json"
)

REQUIRED_PREVIEW_IDS = {
    "preserve_final_acceptance_boundary_preview",
    "rewrite_formation_next_stage_boundary_preview",
    "insert_visual_trajectory_review_candidate_subsection_preview",
    "insert_fault_tolerance_candidate_subsection_preview",
    "insert_multi_uav_formation_candidate_subsection_preview",
    "condense_smoke_and_legacy_sections_preview",
    "renumber_l1_residual_subsection_preview",
}

REQUIRED_BOUNDARY_TERMS = [
    "does not edit Docs/报告/仿真分析报告_正文骨架.md",
    "does not delete historical evidence",
    "does not generate a patch to apply automatically",
    "does not change final PMO acceptance",
]

REQUIRED_BLOCKING_TERMS = [
    "不支撑 ROS2/PX4/QGC 在线编队",
    "不支撑 UE build/runtime/editor 成功",
    "不支撑瞬态故障切换",
]

FORBIDDEN_FINAL_CLAIMS = [
    "最终 PMO 验收已完成",
    "final acceptance complete",
    "final_submission_ready=true",
    "closed_loop success",
    "planner_ready=true",
    "UE runtime success",
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


def validate(report_path: Path, preview_path: Path) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    report_text = report_path.read_text(encoding="utf-8") if report_path.exists() else ""
    if not report_text:
        issues.append(f"missing report source: {rel(report_path)}")

    try:
        preview = read_json(preview_path)
    except Exception as exc:
        return {
            "ok": False,
            "report": rel(report_path),
            "preview": rel(preview_path),
            "issues": [str(exc)],
            "warnings": [],
        }

    if preview.get("status") != "draft_patch_preview_not_report_edit":
        issues.append("preview status must remain draft_patch_preview_not_report_edit")

    summary = preview.get("summary", {})
    for key in ("edits_report_source", "deletes_content", "final_acceptance"):
        if summary.get(key) is not False:
            issues.append(f"preview summary {key} must be false")

    claim_boundary = " ".join(str(item) for item in preview.get("claim_boundary", []))
    for term in REQUIRED_BOUNDARY_TERMS:
        if term not in claim_boundary:
            issues.append(f"preview claim boundary missing term: {term}")

    items = preview.get("previews", [])
    if not isinstance(items, list):
        issues.append("preview previews field must be a list")
        items = []
    item_ids = {str(item.get("preview_id")) for item in items if isinstance(item, dict)}
    missing_ids = sorted(REQUIRED_PREVIEW_IDS - item_ids)
    if missing_ids:
        issues.append("missing preview ids: " + ", ".join(missing_ids))

    for item in items:
        if not isinstance(item, dict):
            issues.append("preview item must be object")
            continue
        if item.get("applies_patch_now") is not False:
            issues.append(f"{item.get('preview_id')} must have applies_patch_now=false")
        original = str(item.get("original") or "")
        if item.get("operation") in {
            "verify_keep_existing_text",
            "replace_single_sentence_after_review",
            "rename_heading_after_review",
        }:
            if item.get("anchor_found") is True and not original:
                issues.append(f"{item.get('preview_id')} marks anchor_found=true but original is empty")
            if item.get("anchor_found") is True and original not in report_text:
                issues.append(f"{item.get('preview_id')} original anchor no longer appears in report source")
            if item.get("anchor_found") is False:
                warnings.append(
                    f"{item.get('preview_id')} source anchor was not found; "
                    "historical line hints are not treated as current evidence"
                )

    joined_preview = "\n".join(
        str(item.get("preview") or "") + "\n" + str(item.get("safety_boundary") or "")
        for item in items
        if isinstance(item, dict)
    )
    for term in REQUIRED_BLOCKING_TERMS:
        if term not in joined_preview:
            issues.append(f"preview missing required blocking term: {term}")
    for term in FORBIDDEN_FINAL_CLAIMS:
        if term in joined_preview or term in claim_boundary:
            issues.append(f"preview contains forbidden final/runtime claim: {term}")

    if summary.get("preview_count") != len(items):
        issues.append("summary preview_count does not match previews length")
    if summary.get("candidate_insert_preview_count") != sum(
        1 for item in items if isinstance(item, dict) and item.get("operation") == "insert_candidate_subsection_after_review"
    ):
        issues.append("summary candidate_insert_preview_count mismatch")

    return {
        "ok": not issues,
        "report": rel(report_path),
        "preview": rel(preview_path),
        "issues": issues,
        "warnings": warnings,
        "preview_count": len(items),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default=str(DEFAULT_REPORT.relative_to(ROOT)))
    parser.add_argument("--preview", default=str(DEFAULT_PREVIEW.relative_to(ROOT)))
    parser.add_argument("--output-json", help="Optional validation report path")
    args = parser.parse_args()

    result = validate(repo_path(args.report), repo_path(args.preview))
    if args.output_json:
        output = repo_path(args.output_json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
