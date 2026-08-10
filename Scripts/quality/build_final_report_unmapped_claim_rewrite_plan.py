#!/usr/bin/env python3
"""Build patch-ready wording for currently unmapped report claim families.

The output is a report-editing aid for the three candidate families identified
by the outline gap inventory. It does not modify the report and does not
promote candidate evidence to final PMO acceptance.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCAFFOLD = (
    ROOT
    / "Results"
    / "static_audits"
    / "candidate_report_table_scaffold_20260610"
    / "candidate_report_table_scaffold.json"
)
DEFAULT_OUTLINE_GAP = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_report_outline_gap_20260610"
    / "final_report_outline_gap_inventory.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "static_audits" / "final_report_unmapped_claim_rewrite_20260610"

FAMILY_CONFIG = {
    "fault_tolerance": {
        "proposed_heading": "执行器退化与复合扰动容错候选证据",
        "insert_after": "13. Linear MPC-style 外环闭环结果",
        "safe_claim": "当前候选证据可用于报告草稿说明：在 rotor1 85% 效率退化叠加横向阵风场景中，加入在线效率估计与控制分配的 LinearMPC Sysblock 候选行通过质量门。",
        "boundary": "不支撑瞬态故障切换、多旋翼同时故障、真实飞控容错或最终 PMO 验收声明。",
    },
    "multi_uav_formation": {
        "proposed_heading": "多无人机编队控制候选证据",
        "insert_after": "13. Linear MPC-style 外环闭环结果",
        "safe_claim": "当前候选证据可用于报告草稿说明：triangle figure-8 编队场景已有一条 MWORKS/Sysplorer 候选行，记录了位置 RMSE、健康分和 formation_score。",
        "boundary": "不支撑 ROS2/PX4/QGC 在线编队、真实多机通信链路或最终编队验收声明。",
    },
    "visual_trajectory_review": {
        "proposed_heading": "原生轨迹留痕与视觉审查候选证据",
        "insert_after": "11. 当前图表",
        "safe_claim": "当前候选证据可用于报告草稿说明：平面 8 字和螺旋上升 8 字留痕审查模型已有 native GUI 候选行与图表路径。",
        "boundary": "不支撑 UE build/runtime/editor 成功、最终演示视频完成或最终视觉验收声明。",
    },
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


def format_number(value: Any) -> str:
    if value in ("", None):
        return ""
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return str(value)


def rows_by_family(scaffold: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in scaffold.get("rows", []):
        if isinstance(row, dict):
            grouped[str(row.get("claim_family", ""))].append(row)
    return dict(grouped)


def family_markdown_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| Claim Slot | Scene | Controller | RMSE m | Health | Formation | Metrics | Main Figure |",
        "|---|---|---|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {slot} | {scene} | {controller} | {rmse} | {health} | {formation} | `{metrics}` | `{figure}` |".format(
                slot=row.get("claim_slot", ""),
                scene=row.get("scene_id", ""),
                controller=row.get("controller_id", ""),
                rmse=format_number(row.get("position_rmse_m")),
                health=format_number(row.get("total_health_score")),
                formation=format_number(row.get("formation_score")),
                metrics=row.get("metrics_file", ""),
                figure=row.get("trajectory_figure", ""),
            )
        )
    return lines


def draft_paragraph(family: str, rows: list[dict[str, Any]]) -> str:
    config = FAMILY_CONFIG[family]
    if family == "fault_tolerance":
        row = rows[0]
        return (
            f"{config['safe_claim']} 候选实验 `{row['experiment_id']}` 的 "
            f"position_rmse_m={format_number(row.get('position_rmse_m'))}，"
            f"total_health_score={format_number(row.get('total_health_score'))}，"
            f"证据路径包括 metrics、raw CSV 和核心 SVG 图表。"
            f"{config['boundary']}"
        )
    if family == "multi_uav_formation":
        row = rows[0]
        return (
            f"{config['safe_claim']} 候选实验 `{row['experiment_id']}` 的 "
            f"position_rmse_m={format_number(row.get('position_rmse_m'))}，"
            f"formation_score={format_number(row.get('formation_score'))}，"
            f"total_health_score={format_number(row.get('total_health_score'))}。"
            f"{config['boundary']}"
        )
    joined = "、".join(f"`{row['experiment_id']}`" for row in rows)
    rmse_values = "、".join(format_number(row.get("position_rmse_m")) for row in rows)
    return (
        f"{config['safe_claim']} 候选实验包括 {joined}，"
        f"position_rmse_m 分别为 {rmse_values}。"
        f"{config['boundary']}"
    )


def build_plan(scaffold_path: Path, outline_gap_path: Path) -> dict[str, Any]:
    scaffold = read_json(scaffold_path)
    outline_gap = read_json(outline_gap_path)
    grouped = rows_by_family(scaffold)
    requested_families = [
        str(item.get("claim_family", ""))
        for item in outline_gap.get("candidate_insertion_actions", [])
        if isinstance(item, dict)
    ]
    families = [family for family in requested_families if family in FAMILY_CONFIG]

    sections: list[dict[str, Any]] = []
    for family in families:
        rows = grouped.get(family, [])
        config = FAMILY_CONFIG[family]
        sections.append(
            {
                "claim_family": family,
                "proposed_heading": config["proposed_heading"],
                "insert_after": config["insert_after"],
                "candidate_row_count": len(rows),
                "safe_claim": config["safe_claim"],
                "boundary": config["boundary"],
                "draft_paragraph": draft_paragraph(family, rows) if rows else "",
                "rows": rows,
            }
        )

    missing_rows = [family for family in families if not grouped.get(family)]
    return {
        "plan_id": "final_report_unmapped_claim_rewrite_20260610",
        "status": "draft_rewrite_plan_not_final_report_acceptance",
        "inputs": {
            "candidate_report_table_scaffold": rel(scaffold_path),
            "final_report_outline_gap_inventory": rel(outline_gap_path),
        },
        "summary": {
            "family_count": len(sections),
            "candidate_row_count": sum(section["candidate_row_count"] for section in sections),
            "missing_family_rows": missing_rows,
            "edits_report_source": False,
            "final_acceptance": False,
        },
        "sections": sections,
        "claim_boundary": [
            "This plan provides patch-ready wording only.",
            "It does not edit Docs/报告/仿真分析报告_正文骨架.md.",
            "It does not generate final PDFs/video or PMO final acceptance.",
            "All wording keeps candidate_report_evidence_only_not_final_pmo_acceptance boundaries.",
        ],
    }


def write_markdown(plan: dict[str, Any], path: Path) -> None:
    summary = plan["summary"]
    lines = [
        "# Final Report Unmapped Claim Rewrite Plan, 2026-06-10",
        "",
        "Status: draft rewrite plan, not final report acceptance.",
        "",
        "## Summary",
        "",
        f"- Families: `{summary['family_count']}`",
        f"- Candidate rows: `{summary['candidate_row_count']}`",
        f"- Missing family rows: `{len(summary['missing_family_rows'])}`",
        f"- Edits report source: `{summary['edits_report_source']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in plan["claim_boundary"]:
        lines.append(f"- {item}")

    for section in plan["sections"]:
        lines.extend(
            [
                "",
                f"## {section['proposed_heading']}",
                "",
                f"- Claim family: `{section['claim_family']}`",
                f"- Insert after: `{section['insert_after']}`",
                f"- Candidate rows: `{section['candidate_row_count']}`",
                "",
                "Suggested paragraph:",
                "",
                section["draft_paragraph"],
                "",
                "Suggested table:",
                "",
            ]
        )
        lines.extend(family_markdown_table(section["rows"]))

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scaffold", default=str(DEFAULT_SCAFFOLD.relative_to(ROOT)))
    parser.add_argument("--outline-gap", default=str(DEFAULT_OUTLINE_GAP.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = build_plan(repo_path(args.scaffold), repo_path(args.outline_gap))
    json_path = output_dir / "final_report_unmapped_claim_rewrite_plan.json"
    md_path = output_dir / "final_report_unmapped_claim_rewrite_plan.md"
    json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(plan, md_path)

    result = {
        "ok": not plan["summary"]["missing_family_rows"],
        "plan_json": rel(json_path),
        "plan_markdown": rel(md_path),
        "family_count": plan["summary"]["family_count"],
        "candidate_row_count": plan["summary"]["candidate_row_count"],
        "missing_family_row_count": len(plan["summary"]["missing_family_rows"]),
        "edits_report_source": plan["summary"]["edits_report_source"],
        "final_acceptance": plan["summary"]["final_acceptance"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
