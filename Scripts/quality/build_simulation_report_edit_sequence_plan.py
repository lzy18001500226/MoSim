#!/usr/bin/env python3
"""Build a safe edit-sequence plan for the simulation report source.

This combines the outline gap inventory, unmapped-claim rewrite plan, and
source-hygiene plan into a reviewable sequence. It does not edit the report.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
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
DEFAULT_HYGIENE_PLAN = (
    ROOT
    / "Results"
    / "static_audits"
    / "simulation_report_source_hygiene_20260610"
    / "simulation_report_source_hygiene_plan.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "static_audits" / "simulation_report_edit_sequence_20260610"


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


def rewrite_sections_by_family(rewrite_plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for section in rewrite_plan.get("sections", []):
        if isinstance(section, dict):
            family = str(section.get("claim_family") or "")
            if family:
                result[family] = section
    return result


def hygiene_findings_by_id(hygiene_plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for finding in hygiene_plan.get("findings", []):
        if isinstance(finding, dict):
            finding_id = str(finding.get("finding_id") or "")
            if finding_id:
                result[finding_id] = finding
    return result


def first_evidence_line(finding: dict[str, Any] | None) -> int | None:
    if not finding:
        return None
    evidence = finding.get("evidence", [])
    if not evidence or not isinstance(evidence, list):
        return None
    first = evidence[0] if isinstance(evidence[0], dict) else {}
    line = first.get("line")
    return int(line) if isinstance(line, int) else None


def action(
    action_id: str,
    order: int,
    kind: str,
    target_section: str,
    rationale: str,
    inputs: list[str],
    source_finding_id: str = "",
    claim_family: str = "",
    report_line_hint: int | None = None,
    proposed_change: str = "",
    safety_boundary: str = "",
) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "order": order,
        "kind": kind,
        "target_section": target_section,
        "claim_family": claim_family,
        "source_finding_id": source_finding_id,
        "report_line_hint": report_line_hint,
        "rationale": rationale,
        "inputs": inputs,
        "proposed_change": proposed_change,
        "safety_boundary": safety_boundary,
        "edits_now": False,
        "requires_human_review_before_apply": True,
    }


def build_plan(outline_gap_path: Path, rewrite_plan_path: Path, hygiene_plan_path: Path) -> dict[str, Any]:
    outline_gap = read_json(outline_gap_path)
    rewrite_plan = read_json(rewrite_plan_path)
    hygiene_plan = read_json(hygiene_plan_path)
    families = rewrite_sections_by_family(rewrite_plan)
    findings = hygiene_findings_by_id(hygiene_plan)

    actions: list[dict[str, Any]] = []
    actions.append(
        action(
            "preserve_final_acceptance_boundary",
            1,
            "boundary_guard",
            "1. 报告范围",
            "Final PDF, demo video, and final PMO acceptance packet are still missing.",
            [rel(hygiene_plan_path), rel(outline_gap_path)],
            source_finding_id="final_artifact_missing_boundary",
            report_line_hint=first_evidence_line(findings.get("final_artifact_missing_boundary")),
            proposed_change="Keep the current not-final paragraph near the front matter before any source rewrite.",
            safety_boundary="Do not convert static candidate readiness into final acceptance.",
        )
    )
    actions.append(
        action(
            "rewrite_formation_next_stage_boundary",
            2,
            "targeted_sentence_rewrite",
            "12. 扩展场景状态",
            "The current sentence says planning and formation are next-stage goals, but a formation candidate row now exists.",
            [rel(hygiene_plan_path), rel(rewrite_plan_path)],
            source_finding_id="formation_next_stage_statement_conflict",
            claim_family="multi_uav_formation",
            report_line_hint=first_evidence_line(findings.get("formation_next_stage_statement_conflict")),
            proposed_change=(
                "Rewrite the sentence to separate static MWORKS/Sysplorer formation candidate evidence "
                "from unproven ROS2/PX4/QGC online formation claims."
            ),
            safety_boundary="Do not claim ROS2/PX4/QGC online formation or final formation acceptance.",
        )
    )

    insertion_order = [
        ("visual_trajectory_review", "insert_visual_trajectory_review_candidate_subsection", "11. 当前图表"),
        ("fault_tolerance", "insert_fault_tolerance_candidate_subsection", "13. Linear MPC-style 外环闭环结果"),
        ("multi_uav_formation", "insert_multi_uav_formation_candidate_subsection", "13. Linear MPC-style 外环闭环结果"),
    ]
    order = 3
    for family, action_id, target in insertion_order:
        section = families.get(family, {})
        actions.append(
            action(
                action_id,
                order,
                "candidate_subsection_insert",
                target,
                f"Candidate family `{family}` is not yet represented as a dedicated final-report subsection.",
                [rel(rewrite_plan_path), rel(outline_gap_path)],
                claim_family=family,
                proposed_change=str(section.get("draft_paragraph") or ""),
                safety_boundary=str(section.get("boundary") or "Keep candidate evidence below final acceptance."),
            )
        )
        order += 1

    actions.append(
        action(
            "condense_smoke_and_legacy_sections",
            order,
            "condense_without_delete",
            "5-9 legacy/smoke sections",
            "Smoke/staged and legacy comparison sections are useful provenance but should not dominate the final candidate narrative.",
            [rel(hygiene_plan_path), rel(outline_gap_path)],
            source_finding_id="smoke_and_staged_prominence;legacy_controller_comparison_sections",
            report_line_hint=first_evidence_line(findings.get("smoke_and_staged_prominence")),
            proposed_change="Condense these sections into a short history/background block or appendix pointer after final table review.",
            safety_boundary="Do not delete provenance or use smoke/staged rows as full performance conclusions.",
        )
    )
    order += 1

    actions.append(
        action(
            "renumber_l1_residual_subsection",
            order,
            "structure_cleanup",
            "9.4 L1-inspired 残差补偿控制器首轮消融",
            "The numbered subsection appears under a later report flow and can confuse navigation.",
            [rel(hygiene_plan_path)],
            source_finding_id="heading_number_mismatch",
            report_line_hint=first_evidence_line(findings.get("heading_number_mismatch")),
            proposed_change="Renumber or remove explicit subsection numbering after content placement is approved.",
            safety_boundary="Structure cleanup only; do not change technical claims.",
        )
    )

    family_count = len(families)
    return {
        "plan_id": "simulation_report_edit_sequence_20260610",
        "status": "draft_edit_sequence_not_report_edit",
        "inputs": {
            "final_report_outline_gap_inventory": rel(outline_gap_path),
            "final_report_unmapped_claim_rewrite_plan": rel(rewrite_plan_path),
            "simulation_report_source_hygiene_plan": rel(hygiene_plan_path),
        },
        "summary": {
            "action_count": len(actions),
            "candidate_family_count": family_count,
            "hygiene_finding_count": hygiene_plan.get("summary", {}).get("finding_count"),
            "edits_report_source": False,
            "deletes_content": False,
            "final_acceptance": False,
        },
        "actions": actions,
        "apply_prerequisites": [
            "Human/PMO review approves which candidate families enter the report body.",
            "Historical evidence retention policy is confirmed before condensing legacy sections.",
            "Final acceptance boundary remains in the first report scope section.",
        ],
        "claim_boundary": [
            "This plan sequences report-source edits only.",
            "It does not edit Docs/simulation_report.md.",
            "It does not delete historical evidence.",
            "It does not generate PDFs/video or PMO final acceptance.",
        ],
    }


def write_markdown(plan: dict[str, Any], path: Path) -> None:
    summary = plan["summary"]
    lines = [
        "# Simulation Report Edit Sequence Plan, 2026-06-10",
        "",
        "Status: draft edit sequence, not a report edit.",
        "",
        "## Summary",
        "",
        f"- Actions: `{summary['action_count']}`",
        f"- Candidate families: `{summary['candidate_family_count']}`",
        f"- Hygiene findings: `{summary['hygiene_finding_count']}`",
        f"- Edits report source: `{summary['edits_report_source']}`",
        f"- Deletes content: `{summary['deletes_content']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in plan["claim_boundary"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Actions", ""])
    for item in plan["actions"]:
        lines.extend(
            [
                f"### {item['order']}. {item['action_id']}",
                "",
                f"- Kind: `{item['kind']}`",
                f"- Target section: {item['target_section']}",
                f"- Claim family: `{item['claim_family']}`",
                f"- Source finding: `{item['source_finding_id']}`",
                f"- Report line hint: `{item['report_line_hint']}`",
                f"- Rationale: {item['rationale']}",
                f"- Proposed change: {item['proposed_change']}",
                f"- Safety boundary: {item['safety_boundary']}",
                "",
            ]
        )
    lines.extend(["## Apply Prerequisites", ""])
    for item in plan["apply_prerequisites"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outline-gap", default=str(DEFAULT_OUTLINE_GAP.relative_to(ROOT)))
    parser.add_argument("--rewrite-plan", default=str(DEFAULT_REWRITE_PLAN.relative_to(ROOT)))
    parser.add_argument("--hygiene-plan", default=str(DEFAULT_HYGIENE_PLAN.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = build_plan(repo_path(args.outline_gap), repo_path(args.rewrite_plan), repo_path(args.hygiene_plan))
    json_path = output_dir / "simulation_report_edit_sequence_plan.json"
    md_path = output_dir / "simulation_report_edit_sequence_plan.md"
    json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(plan, md_path)

    result = {
        "ok": True,
        "plan_json": rel(json_path),
        "plan_markdown": rel(md_path),
        "action_count": plan["summary"]["action_count"],
        "candidate_family_count": plan["summary"]["candidate_family_count"],
        "edits_report_source": plan["summary"]["edits_report_source"],
        "deletes_content": plan["summary"]["deletes_content"],
        "final_acceptance": plan["summary"]["final_acceptance"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
