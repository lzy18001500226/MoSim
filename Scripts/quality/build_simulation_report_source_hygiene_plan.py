#!/usr/bin/env python3
"""Build a safe hygiene plan for the simulation report source.

The plan identifies stale or confusing report-source areas without deleting or
rewriting content. It is a review aid for the next report-editing pass.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / "Docs" / "simulation_report.md"
DEFAULT_OUTLINE_GAP = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_report_outline_gap_20260610"
    / "final_report_outline_gap_inventory.json"
)
DEFAULT_REWRITE_PLAN = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_report_unmapped_claim_rewrite_20260610"
    / "final_report_unmapped_claim_rewrite_plan.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "static_audits" / "simulation_report_source_hygiene_20260610"


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


def numbered_lines(text: str) -> list[tuple[int, str]]:
    return [(index + 1, line) for index, line in enumerate(text.splitlines())]


def find_line_matches(text: str, pattern: str) -> list[dict[str, Any]]:
    regex = re.compile(pattern, re.IGNORECASE)
    return [
        {"line": line_no, "text": line.strip()}
        for line_no, line in numbered_lines(text)
        if regex.search(line)
    ]


def outline_sections(outline_gap: dict[str, Any]) -> list[dict[str, Any]]:
    sections = outline_gap.get("sections", [])
    return [section for section in sections if isinstance(section, dict)]


def rewrite_families(rewrite_plan: dict[str, Any]) -> set[str]:
    return {
        str(section.get("claim_family", ""))
        for section in rewrite_plan.get("sections", [])
        if isinstance(section, dict)
    }


def add_finding(
    findings: list[dict[str, Any]],
    finding_id: str,
    severity: str,
    category: str,
    evidence: list[dict[str, Any]],
    risk: str,
    recommendation: str,
    proposed_action: str,
) -> None:
    if not evidence:
        return
    findings.append(
        {
            "finding_id": finding_id,
            "severity": severity,
            "category": category,
            "evidence": evidence,
            "risk": risk,
            "recommendation": recommendation,
            "proposed_action": proposed_action,
        }
    )


def build_plan(report_path: Path, outline_gap_path: Path, rewrite_plan_path: Path) -> dict[str, Any]:
    report_text = report_path.read_text(encoding="utf-8")
    outline_gap = read_json(outline_gap_path)
    rewrite_plan = read_json(rewrite_plan_path)
    sections = outline_sections(outline_gap)
    families = rewrite_families(rewrite_plan)
    findings: list[dict[str, Any]] = []

    add_finding(
        findings,
        "old_airframe_snapshot_warnings",
        "medium",
        "old_stage_context",
        find_line_matches(report_text, r"历史表格是旧机体证据快照|旧轻量机架|旧控制器速度输出"),
        "Old-airframe or old-controller notes are useful history, but they can distract from the final candidate evidence set.",
        "Move or condense old-stage context into a history/appendix block during the next report rewrite.",
        "condense_keep_boundary",
    )

    add_finding(
        findings,
        "smoke_and_staged_prominence",
        "medium",
        "smoke_context",
        find_line_matches(report_text, r"smoke|0-1 s|staged"),
        "Smoke/staged rows are valid pipeline evidence but should not dominate the final performance narrative.",
        "Keep the smoke boundary, but move detailed smoke/staged tables out of the main final-results path.",
        "move_to_appendix_or_summary",
    )

    legacy_sections = [
        {
            "line": section.get("line"),
            "text": str(section.get("heading", "")),
        }
        for section in sections
        if section.get("role") == "legacy_comparison"
    ]
    add_finding(
        findings,
        "legacy_controller_comparison_sections",
        "medium",
        "legacy_comparison",
        legacy_sections,
        "Legacy Improved PID / Enhanced PID / AWFF sections are useful provenance but may compete with the current candidate LinearMPC report path.",
        "Compress these sections after the final candidate table is accepted; preserve evidence references until review completes.",
        "compress_after_candidate_table_review",
    )

    add_finding(
        findings,
        "heading_number_mismatch",
        "low",
        "report_structure",
        find_line_matches(report_text, r"^### 9\.4 "),
        "A 9.4 subsection appears under the later report flow and can confuse navigation.",
        "Renumber or remove explicit subsection numbering during the final report rewrite.",
        "renumber_in_report_rewrite",
    )

    planning_matches = find_line_matches(report_text, r"规划和编队仍保留.*下一阶段")
    if "multi_uav_formation" in families:
        add_finding(
            findings,
            "formation_next_stage_statement_conflict",
            "high",
            "candidate_mismatch",
            planning_matches,
            "The report says planning and formation remain next-stage goals, while the static candidate set now includes a multi-UAV formation candidate row.",
            "Rewrite this sentence to distinguish final acceptance from available candidate formation evidence.",
            "rewrite_with_candidate_boundary",
        )

    add_finding(
        findings,
        "final_artifact_missing_boundary",
        "high",
        "final_acceptance_boundary",
        find_line_matches(report_text, r"最终 PDF|演示视频|最终验收 packet|最终 PMO 验收"),
        "The report correctly states final packaging is not complete; any source rewrite must keep this boundary.",
        "Keep the not-final boundary until final PDFs, demo video, and PMO acceptance packet exist.",
        "preserve_boundary",
    )

    severity_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    for finding in findings:
        severity_counts[finding["severity"]] = severity_counts.get(finding["severity"], 0) + 1
        category_counts[finding["category"]] = category_counts.get(finding["category"], 0) + 1

    return {
        "plan_id": "simulation_report_source_hygiene_20260610",
        "status": "draft_hygiene_plan_not_report_edit",
        "inputs": {
            "simulation_report": rel(report_path),
            "final_report_outline_gap_inventory": rel(outline_gap_path),
            "final_report_unmapped_claim_rewrite_plan": rel(rewrite_plan_path),
        },
        "summary": {
            "finding_count": len(findings),
            "severity_counts": dict(sorted(severity_counts.items())),
            "category_counts": dict(sorted(category_counts.items())),
            "edits_report_source": False,
            "deletes_content": False,
            "final_acceptance": False,
        },
        "findings": findings,
        "recommended_order": [
            "Preserve current not-final and no-live-runtime boundaries.",
            "Rewrite the formation/planning next-stage sentence with candidate-evidence boundaries.",
            "Move smoke/staged details and legacy comparisons toward summary/appendix form.",
            "Renumber report sections after content placement is approved.",
        ],
        "claim_boundary": [
            "This plan is a review aid only.",
            "It does not edit Docs/simulation_report.md.",
            "It does not delete report content.",
            "It does not change final PMO acceptance or live-runtime status.",
        ],
    }


def write_markdown(plan: dict[str, Any], path: Path) -> None:
    summary = plan["summary"]
    lines = [
        "# Simulation Report Source Hygiene Plan, 2026-06-10",
        "",
        "Status: draft hygiene plan, not a report edit.",
        "",
        "## Summary",
        "",
        f"- Findings: `{summary['finding_count']}`",
        f"- Edits report source: `{summary['edits_report_source']}`",
        f"- Deletes content: `{summary['deletes_content']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "Severity counts:",
        "",
    ]
    for severity, count in summary["severity_counts"].items():
        lines.append(f"- `{severity}`: `{count}`")
    lines.extend(["", "## Claim Boundary", ""])
    for item in plan["claim_boundary"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Findings", ""])
    for finding in plan["findings"]:
        lines.extend(
            [
                f"### {finding['finding_id']}",
                "",
                f"- Severity: `{finding['severity']}`",
                f"- Category: `{finding['category']}`",
                f"- Risk: {finding['risk']}",
                f"- Recommendation: {finding['recommendation']}",
                f"- Proposed action: `{finding['proposed_action']}`",
                "",
                "Evidence:",
            ]
        )
        for item in finding["evidence"][:8]:
            lines.append(f"- line {item.get('line')}: {item.get('text')}")
        if len(finding["evidence"]) > 8:
            lines.append(f"- ... {len(finding['evidence']) - 8} more matches")
        lines.append("")

    lines.extend(["## Recommended Order", ""])
    for index, item in enumerate(plan["recommended_order"], start=1):
        lines.append(f"{index}. {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default=str(DEFAULT_REPORT.relative_to(ROOT)))
    parser.add_argument("--outline-gap", default=str(DEFAULT_OUTLINE_GAP.relative_to(ROOT)))
    parser.add_argument("--rewrite-plan", default=str(DEFAULT_REWRITE_PLAN.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = build_plan(repo_path(args.report), repo_path(args.outline_gap), repo_path(args.rewrite_plan))
    json_path = output_dir / "simulation_report_source_hygiene_plan.json"
    md_path = output_dir / "simulation_report_source_hygiene_plan.md"
    json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(plan, md_path)

    result = {
        "ok": True,
        "plan_json": rel(json_path),
        "plan_markdown": rel(md_path),
        "finding_count": plan["summary"]["finding_count"],
        "severity_counts": plan["summary"]["severity_counts"],
        "edits_report_source": plan["summary"]["edits_report_source"],
        "deletes_content": plan["summary"]["deletes_content"],
        "final_acceptance": plan["summary"]["final_acceptance"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
