#!/usr/bin/env python3
"""Build a non-applying patch preview for the simulation report source.

The preview gives reviewers concrete before/after snippets and insertion
points, but it never edits `Docs/simulation_report.md`.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT = ROOT / "Docs" / "simulation_report.md"
DEFAULT_EDIT_SEQUENCE = (
    ROOT
    / "Results"
    / "static_audits"
    / "simulation_report_edit_sequence_20260610"
    / "simulation_report_edit_sequence_plan.json"
)
DEFAULT_REWRITE_PLAN = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_report_unmapped_claim_rewrite_20260610"
    / "final_report_unmapped_claim_rewrite_plan.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "static_audits" / "simulation_report_patch_preview_20260610"


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


def line_at(text: str, line_no: int | None) -> str:
    if line_no is None:
        return ""
    lines = text.splitlines()
    if 1 <= line_no <= len(lines):
        return lines[line_no - 1]
    return ""


def find_line(text: str, pattern: str) -> tuple[int | None, str]:
    regex = re.compile(pattern)
    for index, line in enumerate(text.splitlines(), start=1):
        if regex.search(line):
            return index, line
    return None, ""


def rewrite_by_family(rewrite_plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sections: dict[str, dict[str, Any]] = {}
    for section in rewrite_plan.get("sections", []):
        if isinstance(section, dict):
            family = str(section.get("claim_family") or "")
            if family:
                sections[family] = section
    return sections


def make_candidate_block(section: dict[str, Any]) -> str:
    heading = str(section.get("proposed_heading") or "候选证据")
    paragraph = str(section.get("draft_paragraph") or "")
    rows = section.get("rows", [])
    lines = [
        f"### {heading}",
        "",
        paragraph,
        "",
        "| claim_slot | scene_id | controller_id | position_rmse_m | total_health_score | figure |",
        "|---|---|---|---:|---:|---|",
    ]
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            lines.append(
                "| {claim_slot} | {scene_id} | {controller_id} | {rmse} | {score} | {figure} |".format(
                    claim_slot=row.get("claim_slot", ""),
                    scene_id=row.get("scene_id", ""),
                    controller_id=row.get("controller_id", ""),
                    rmse=row.get("position_rmse_m", ""),
                    score=row.get("total_health_score", ""),
                    figure=row.get("trajectory_figure", ""),
                )
            )
    return "\n".join(lines)


def build_preview(report_path: Path, edit_sequence_path: Path, rewrite_plan_path: Path) -> dict[str, Any]:
    report_text = report_path.read_text(encoding="utf-8")
    edit_sequence = read_json(edit_sequence_path)
    rewrite_plan = read_json(rewrite_plan_path)
    sections = rewrite_by_family(rewrite_plan)
    previews: list[dict[str, Any]] = []

    actions = [
        action
        for action in edit_sequence.get("actions", [])
        if isinstance(action, dict)
    ]
    action_by_id = {str(action.get("action_id")): action for action in actions}

    boundary_action = action_by_id.get("preserve_final_acceptance_boundary", {})
    boundary_line_no, boundary_line = find_line(report_text, r"不是最终 PMO 验收")
    if boundary_line_no is None:
        boundary_line_no = boundary_action.get("report_line_hint")
        boundary_line = line_at(report_text, boundary_line_no)
    previews.append(
        {
            "preview_id": "preserve_final_acceptance_boundary_preview",
            "source_action_id": "preserve_final_acceptance_boundary",
            "operation": "verify_keep_existing_text",
            "target": boundary_action.get("target_section", "1. 报告范围"),
            "line_hint": boundary_line_no,
            "original": boundary_line,
            "preview": "Keep this boundary near the front matter before any report-source rewrite.",
            "safety_boundary": boundary_action.get("safety_boundary", ""),
            "applies_patch_now": False,
        }
    )

    formation_action = action_by_id.get("rewrite_formation_next_stage_boundary", {})
    formation_line_no, formation_line = find_line(report_text, r"规划和编队仍保留")
    if formation_line_no is None:
        formation_line_no = formation_action.get("report_line_hint")
        formation_line = line_at(report_text, formation_line_no)
    previews.append(
        {
            "preview_id": "rewrite_formation_next_stage_boundary_preview",
            "source_action_id": "rewrite_formation_next_stage_boundary",
            "operation": "replace_single_sentence_after_review",
            "target": formation_action.get("target_section", "12. 扩展场景状态"),
            "line_hint": formation_line_no,
            "original": formation_line,
            "preview": (
                "质量 +20% 参数摄动、15-19 s 横向阵风扰动、1 号旋翼 85% 效率退化、"
                "Example1 AWFF 独立控制器替换、Example1/2/3 AWFF Sysblock 官方场景、"
                "L1 residual Sysblock 消融、已知效率退化控制分配补偿，以及 triangle figure-8 "
                "编队候选行均已有静态候选证据或真实 MWORKS/Sysplorer 证据；其中编队候选证据只"
                "支撑报告草稿中的 MWORKS/Sysplorer 编队验证描述，不支撑 ROS2/PX4/QGC 在线编队、"
                "真实多机通信链路或最终编队验收声明。"
            ),
            "safety_boundary": formation_action.get("safety_boundary", ""),
            "applies_patch_now": False,
        }
    )

    for family, action_id in [
        ("visual_trajectory_review", "insert_visual_trajectory_review_candidate_subsection"),
        ("fault_tolerance", "insert_fault_tolerance_candidate_subsection"),
        ("multi_uav_formation", "insert_multi_uav_formation_candidate_subsection"),
    ]:
        action = action_by_id.get(action_id, {})
        previews.append(
            {
                "preview_id": f"{action_id}_preview",
                "source_action_id": action_id,
                "operation": "insert_candidate_subsection_after_review",
                "target": action.get("target_section", ""),
                "line_hint": action.get("report_line_hint"),
                "original": "",
                "preview": make_candidate_block(sections.get(family, {})),
                "safety_boundary": action.get("safety_boundary", ""),
                "applies_patch_now": False,
            }
        )

    condense_action = action_by_id.get("condense_smoke_and_legacy_sections", {})
    previews.append(
        {
            "preview_id": "condense_smoke_and_legacy_sections_preview",
            "source_action_id": "condense_smoke_and_legacy_sections",
            "operation": "manual_condense_no_delete",
            "target": condense_action.get("target_section", "5-9 legacy/smoke sections"),
            "line_hint": condense_action.get("report_line_hint"),
            "original": "smoke/staged and legacy comparison sections remain in source until reviewer approves condensation",
            "preview": (
                "Move detailed smoke/staged and legacy-comparison tables toward a history or appendix "
                "summary only after the final candidate table is reviewed."
            ),
            "safety_boundary": condense_action.get("safety_boundary", ""),
            "applies_patch_now": False,
        }
    )

    renumber_action = action_by_id.get("renumber_l1_residual_subsection", {})
    renumber_line_no, renumber_line = find_line(report_text, r"^### 9\.4 ")
    if renumber_line_no is None:
        renumber_line_no = renumber_action.get("report_line_hint")
        renumber_line = line_at(report_text, renumber_line_no)
    previews.append(
        {
            "preview_id": "renumber_l1_residual_subsection_preview",
            "source_action_id": "renumber_l1_residual_subsection",
            "operation": "rename_heading_after_review",
            "target": renumber_action.get("target_section", ""),
            "line_hint": renumber_line_no,
            "original": renumber_line,
            "preview": "### L1-inspired 残差补偿控制器首轮消融",
            "safety_boundary": renumber_action.get("safety_boundary", ""),
            "applies_patch_now": False,
        }
    )

    return {
        "preview_id": "simulation_report_patch_preview_20260610",
        "status": "draft_patch_preview_not_report_edit",
        "inputs": {
            "simulation_report": rel(report_path),
            "simulation_report_edit_sequence_plan": rel(edit_sequence_path),
            "final_report_unmapped_claim_rewrite_plan": rel(rewrite_plan_path),
        },
        "summary": {
            "preview_count": len(previews),
            "candidate_insert_preview_count": sum(
                1 for item in previews if item["operation"] == "insert_candidate_subsection_after_review"
            ),
            "replacement_preview_count": sum(
                1 for item in previews if item["operation"] == "replace_single_sentence_after_review"
            ),
            "edits_report_source": False,
            "deletes_content": False,
            "final_acceptance": False,
        },
        "previews": previews,
        "claim_boundary": [
            "This artifact previews possible report-source edits only.",
            "It does not edit Docs/simulation_report.md.",
            "It does not delete historical evidence.",
            "It does not generate a patch to apply automatically.",
            "It does not change final PMO acceptance.",
        ],
    }


def write_markdown(preview: dict[str, Any], path: Path) -> None:
    summary = preview["summary"]
    lines = [
        "# Simulation Report Patch Preview, 2026-06-10",
        "",
        "Status: draft patch preview, not a report edit.",
        "",
        "## Summary",
        "",
        f"- Previews: `{summary['preview_count']}`",
        f"- Candidate insert previews: `{summary['candidate_insert_preview_count']}`",
        f"- Replacement previews: `{summary['replacement_preview_count']}`",
        f"- Edits report source: `{summary['edits_report_source']}`",
        f"- Deletes content: `{summary['deletes_content']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in preview["claim_boundary"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Preview Items", ""])
    for item in preview["previews"]:
        lines.extend(
            [
                f"### {item['preview_id']}",
                "",
                f"- Operation: `{item['operation']}`",
                f"- Source action: `{item['source_action_id']}`",
                f"- Target: {item['target']}",
                f"- Line hint: `{item['line_hint']}`",
                f"- Applies patch now: `{item['applies_patch_now']}`",
                f"- Safety boundary: {item['safety_boundary']}",
                "",
                "Original:",
                "",
                "```text",
                str(item["original"]),
                "```",
                "",
                "Preview:",
                "",
                "```text",
                str(item["preview"]),
                "```",
                "",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", default=str(DEFAULT_REPORT.relative_to(ROOT)))
    parser.add_argument("--edit-sequence", default=str(DEFAULT_EDIT_SEQUENCE.relative_to(ROOT)))
    parser.add_argument("--rewrite-plan", default=str(DEFAULT_REWRITE_PLAN.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    preview = build_preview(repo_path(args.report), repo_path(args.edit_sequence), repo_path(args.rewrite_plan))
    json_path = output_dir / "simulation_report_patch_preview.json"
    md_path = output_dir / "simulation_report_patch_preview.md"
    json_path.write_text(json.dumps(preview, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(preview, md_path)

    result = {
        "ok": True,
        "preview_json": rel(json_path),
        "preview_markdown": rel(md_path),
        "preview_count": preview["summary"]["preview_count"],
        "edits_report_source": preview["summary"]["edits_report_source"],
        "deletes_content": preview["summary"]["deletes_content"],
        "final_acceptance": preview["summary"]["final_acceptance"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
