#!/usr/bin/env python3
"""Build a static final-report outline gap inventory.

This inventory compares the current simulation report source with the
candidate report-table scaffold and final packaging gap inventory. It tells a
report writer which sections can be refreshed from static evidence and which
sections still need human/live/final-acceptance review.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / "Docs" / "simulation_report.md"
DEFAULT_SCAFFOLD = (
    ROOT
    / "Results"
    / "static_audits"
    / "candidate_report_table_scaffold_20260610"
    / "candidate_report_table_scaffold.json"
)
DEFAULT_PRE_SUBMIT = (
    ROOT
    / "Results"
    / "static_audits"
    / "pre_submit_readiness_inventory_20260610"
    / "pre_submit_readiness_inventory.json"
)
DEFAULT_FINAL_GAP = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_packaging_gap_20260610"
    / "final_packaging_gap_inventory.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "static_audits" / "final_report_outline_gap_20260610"

SECTION_RULES = [
    {
        "heading_contains": "报告范围",
        "role": "scope_boundary",
        "static_update": "current manifest and packaging boundary paragraph can stay near the front matter",
    },
    {
        "heading_contains": "当前机体模型迁移状态",
        "role": "platform_context",
        "static_update": "keep as context; do not use as current final performance ranking",
    },
    {
        "heading_contains": "模型与场景",
        "role": "scenario_catalog",
        "static_update": "refresh scenario catalog from candidate rows before final report freeze",
    },
    {
        "heading_contains": "数据链路",
        "role": "pipeline_and_evidence",
        "static_update": "keep reproducible pipeline and evidence boundary",
    },
    {
        "heading_contains": "当前正式基线指标",
        "role": "historical_smoke_boundary",
        "static_update": "retain as smoke/background only unless final report chooses to remove it",
    },
    {
        "heading_contains": "官方 PID Baseline 指标",
        "role": "candidate_family:official_baseline",
        "claim_family": "official_baseline",
        "static_update": "can refresh with three candidate baseline rows and their figures",
    },
    {
        "heading_contains": "改进 PID 对比",
        "role": "legacy_comparison",
        "static_update": "legacy comparison; should not compete with current candidate LinearMPC table unless explicitly retained",
    },
    {
        "heading_contains": "Enhanced PID",
        "role": "legacy_comparison",
        "static_update": "legacy comparison; can be shortened after final candidate table is accepted",
    },
    {
        "heading_contains": "AWFF",
        "role": "legacy_comparison",
        "static_update": "legacy comparison and Sysblock implementation history; separate from final candidate ranking",
    },
    {
        "heading_contains": "鲁棒",
        "role": "candidate_family:robustness",
        "claim_family": "robustness",
        "static_update": "can refresh with mass and wind robustness candidate rows",
    },
    {
        "heading_contains": "图表",
        "role": "figure_inventory",
        "static_update": "can replace broad directory list with candidate figure pointers",
    },
    {
        "heading_contains": "扩展场景状态",
        "role": "known_mismatch_review",
        "static_update": "needs review because candidate scaffold now includes formation and visual-review rows",
    },
    {
        "heading_contains": "Linear MPC",
        "role": "candidate_family:optimized_controller",
        "claim_family": "optimized_controller",
        "static_update": "can refresh with optimized controller candidate rows",
    },
    {
        "heading_contains": "Safety Filter",
        "role": "candidate_family:safety_filter",
        "claim_family": "safety_filter",
        "static_update": "can refresh with safety return/land candidate row",
    },
    {
        "heading_contains": "结论约束",
        "role": "final_boundary",
        "static_update": "must keep not-final boundaries until PDF/video/final acceptance exist",
    },
]

UNMAPPED_CLAIM_FAMILY_GUIDANCE = {
    "fault_tolerance": "add or refresh a final fault-tolerance subsection from the rotor-loss wind candidate row",
    "multi_uav_formation": "add or refresh a formation subsection from the triangle figure-8 candidate row",
    "visual_trajectory_review": "add or refresh a visual trajectory review subsection from helical/planar figure-8 rows",
}


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


def parse_sections(report_text: str) -> list[dict[str, Any]]:
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
    matches = list(heading_pattern.finditer(report_text))
    sections: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(report_text)
        content = report_text[start:end].strip()
        sections.append(
            {
                "heading": match.group(2).strip(),
                "level": len(match.group(1)),
                "line": report_text[: match.start()].count("\n") + 1,
                "content_chars": len(content),
            }
        )
    return sections


def rule_for_heading(heading: str) -> dict[str, Any]:
    for rule in SECTION_RULES:
        if str(rule["heading_contains"]).lower() in heading.lower():
            return rule
    return {
        "role": "unclassified",
        "static_update": "manual review needed before editing this section",
    }


def section_requires_human(section: dict[str, Any], rule: dict[str, Any], packaging_ready: bool) -> bool:
    if not packaging_ready and str(rule.get("role")) in {"final_boundary", "scope_boundary"}:
        return True
    return str(rule.get("role")) in {"known_mismatch_review", "unclassified"}


def build_inventory(
    report_path: Path,
    scaffold_path: Path,
    pre_submit_path: Path,
    final_gap_path: Path,
) -> dict[str, Any]:
    report_text = report_path.read_text(encoding="utf-8")
    scaffold = read_json(scaffold_path)
    pre_submit = read_json(pre_submit_path)
    final_gap = read_json(final_gap_path)

    family_counts = scaffold.get("summary", {}).get("claim_family_counts", {})
    if not isinstance(family_counts, dict):
        family_counts = {}
    sections = parse_sections(report_text)

    mapped_families: set[str] = set()
    section_rows: list[dict[str, Any]] = []
    packaging_ready = bool(final_gap.get("summary", {}).get("final_submission_ready", False))
    for section in sections:
        rule = rule_for_heading(str(section["heading"]))
        family = str(rule.get("claim_family", ""))
        if family:
            mapped_families.add(family)
        needs_human = section_requires_human(section, rule, packaging_ready)
        section_rows.append(
            {
                "heading": section["heading"],
                "line": section["line"],
                "level": section["level"],
                "role": rule.get("role", "unclassified"),
                "claim_family": family,
                "candidate_row_count": int(family_counts.get(family, 0)) if family else 0,
                "can_update_from_static_evidence": bool(family or rule.get("role") in {"figure_inventory", "scenario_catalog", "pipeline_and_evidence"}),
                "needs_human_or_live_acceptance": needs_human,
                "editing_guidance": rule.get("static_update", ""),
            }
        )

    unmapped_families = {
        str(family): int(count)
        for family, count in family_counts.items()
        if str(family) not in mapped_families and int(count) > 0
    }
    insertion_candidates = [
        {
            "claim_family": family,
            "candidate_row_count": count,
            "suggested_action": UNMAPPED_CLAIM_FAMILY_GUIDANCE.get(
                family,
                "add a dedicated final-report subsection or map this family to an existing section",
            ),
        }
        for family, count in sorted(unmapped_families.items())
    ]

    static_update_sections = [
        row["heading"]
        for row in section_rows
        if row["can_update_from_static_evidence"] and not row["needs_human_or_live_acceptance"]
    ]
    human_review_sections = [
        row["heading"]
        for row in section_rows
        if row["needs_human_or_live_acceptance"]
    ]
    final_missing = final_gap.get("missing_final_artifacts", [])
    live_blockers = pre_submit.get("live_claim_blockers", [])
    claim_family_row_counts = dict(sorted((str(k), int(v)) for k, v in family_counts.items()))
    return {
        "inventory_id": "final_report_outline_gap_20260610",
        "status": "static_report_outline_gap_not_final_acceptance",
        "inputs": {
            "simulation_report": rel(report_path),
            "candidate_report_table_scaffold": rel(scaffold_path),
            "pre_submit_readiness_inventory": rel(pre_submit_path),
            "final_packaging_gap_inventory": rel(final_gap_path),
        },
        "summary": {
            "section_count": len(section_rows),
            "candidate_row_count": int(scaffold.get("summary", {}).get("row_count", 0)),
            "claim_family_row_counts": claim_family_row_counts,
            "static_update_section_count": len(static_update_sections),
            "human_or_live_review_section_count": len(human_review_sections),
            "unmapped_claim_family_count": len(insertion_candidates),
            "missing_final_artifact_count": len(final_missing) if isinstance(final_missing, list) else 0,
            "live_claim_blocker_count": len(live_blockers) if isinstance(live_blockers, list) else 0,
            "final_submission_ready": packaging_ready,
        },
        "sections": section_rows,
        "static_update_sections": static_update_sections,
        "human_or_live_review_sections": human_review_sections,
        "candidate_insertion_actions": insertion_candidates,
        "missing_final_artifacts": final_missing if isinstance(final_missing, list) else [],
        "live_claim_blockers": live_blockers if isinstance(live_blockers, list) else [],
        "claim_boundary": [
            "This is an outline/editing inventory only.",
            "It does not edit the report, generate final PDFs or video, or write PMO final acceptance.",
            "Candidate rows remain candidate_report_evidence_only_not_final_pmo_acceptance until final PMO/report review.",
        ],
    }


def write_markdown(inventory: dict[str, Any], path: Path) -> None:
    summary = inventory["summary"]
    lines = [
        "# Final Report Outline Gap Inventory, 2026-06-10",
        "",
        "Status: static report outline gap, not final acceptance.",
        "",
        "## Summary",
        "",
        f"- Sections scanned: `{summary['section_count']}`",
        f"- Candidate rows: `{summary['candidate_row_count']}`",
        f"- Static-update sections: `{summary['static_update_section_count']}`",
        f"- Human/live-review sections: `{summary['human_or_live_review_section_count']}`",
        f"- Unmapped claim families: `{summary['unmapped_claim_family_count']}`",
        f"- Missing final artifacts: `{summary['missing_final_artifact_count']}`",
        f"- Live claim blockers: `{summary['live_claim_blocker_count']}`",
        f"- Final submission ready: `{summary['final_submission_ready']}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in inventory["claim_boundary"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Candidate Claim Families", ""])
    lines.append("| Claim Family | Rows |")
    lines.append("|---|---:|")
    for family, count in summary["claim_family_row_counts"].items():
        lines.append(f"| {family} | {count} |")

    lines.extend(["", "## Section Editing Plan", ""])
    lines.append("| Line | Section | Role | Candidate Rows | Static Update | Needs Human/Live Review |")
    lines.append("|---:|---|---|---:|---|---|")
    for row in inventory["sections"]:
        lines.append(
            "| {line} | {heading} | {role} | {rows} | {static} | {human} |".format(
                line=row["line"],
                heading=row["heading"],
                role=row["role"],
                rows=row["candidate_row_count"],
                static=row["can_update_from_static_evidence"],
                human=row["needs_human_or_live_acceptance"],
            )
        )

    lines.extend(["", "## Candidate Insertion Actions", ""])
    if inventory["candidate_insertion_actions"]:
        lines.append("| Claim Family | Rows | Suggested Action |")
        lines.append("|---|---:|---|")
        for item in inventory["candidate_insertion_actions"]:
            lines.append(
                f"| {item['claim_family']} | {item['candidate_row_count']} | {item['suggested_action']} |"
            )
    else:
        lines.append("No unmapped candidate claim family.")

    lines.extend(["", "## Final Acceptance Blockers", ""])
    if inventory["missing_final_artifacts"]:
        lines.append("Missing final artifacts:")
        for item in inventory["missing_final_artifacts"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("No missing final artifact listed.")
    if inventory["live_claim_blockers"]:
        lines.append("")
        lines.append("Live/final claim blockers:")
        for item in inventory["live_claim_blockers"]:
            claim = item.get("claim", "")
            needed = item.get("needed_evidence", "")
            lines.append(f"- {claim}: {needed}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default=str(DEFAULT_REPORT.relative_to(ROOT)))
    parser.add_argument("--scaffold", default=str(DEFAULT_SCAFFOLD.relative_to(ROOT)))
    parser.add_argument("--pre-submit", default=str(DEFAULT_PRE_SUBMIT.relative_to(ROOT)))
    parser.add_argument("--final-gap", default=str(DEFAULT_FINAL_GAP.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory(
        repo_path(args.report),
        repo_path(args.scaffold),
        repo_path(args.pre_submit),
        repo_path(args.final_gap),
    )
    json_path = output_dir / "final_report_outline_gap_inventory.json"
    md_path = output_dir / "final_report_outline_gap_inventory.md"
    json_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(inventory, md_path)

    result = {
        "ok": True,
        "inventory_json": rel(json_path),
        "inventory_markdown": rel(md_path),
        "section_count": inventory["summary"]["section_count"],
        "candidate_row_count": inventory["summary"]["candidate_row_count"],
        "static_update_section_count": inventory["summary"]["static_update_section_count"],
        "human_or_live_review_section_count": inventory["summary"]["human_or_live_review_section_count"],
        "unmapped_claim_family_count": inventory["summary"]["unmapped_claim_family_count"],
        "final_submission_ready": inventory["summary"]["final_submission_ready"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
