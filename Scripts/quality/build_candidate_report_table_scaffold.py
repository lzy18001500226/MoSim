#!/usr/bin/env python3
"""Build a report-table scaffold from candidate submission evidence.

The scaffold is a drafting aid. It joins the conservative candidate manifest
with the figure-readiness inventory so a report writer can see metrics and
figure paths in one place. It does not rank controllers, choose final wording,
or accept final performance claims.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = (
    ROOT
    / "Results"
    / "static_audits"
    / "submission_evidence_manifest_20260610"
    / "candidate_submission_evidence_manifest.json"
)
DEFAULT_FIGURE_INVENTORY = (
    ROOT
    / "Results"
    / "static_audits"
    / "candidate_figure_readiness_20260610"
    / "candidate_figure_readiness_inventory.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "static_audits" / "candidate_report_table_scaffold_20260610"


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


def as_float(value: Any) -> float | None:
    if value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def preferred_figure(core_figures: dict[str, Any], key: str) -> str:
    values = core_figures.get(key, [])
    if isinstance(values, list) and values:
        return str(values[0])
    return ""


def build_scaffold(manifest_path: Path, figure_inventory_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    figure_inventory = read_json(figure_inventory_path)
    figures_by_slot = {
        str(row.get("claim_slot", "")): row
        for row in figure_inventory.get("candidate_rows", [])
        if isinstance(row, dict)
    }

    rows: list[dict[str, Any]] = []
    family_counts: dict[str, int] = defaultdict(int)
    for row in manifest.get("candidate_rows", []):
        if not isinstance(row, dict):
            continue
        slot = str(row.get("claim_slot", ""))
        figure_row = figures_by_slot.get(slot, {})
        core_figures = figure_row.get("core_figures", {})
        if not isinstance(core_figures, dict):
            core_figures = {}
        family = str(row.get("claim_family", ""))
        family_counts[family] += 1
        rows.append(
            {
                "claim_slot": slot,
                "claim_family": family,
                "scene_id": row.get("scene_id", ""),
                "controller_id": row.get("controller_id", ""),
                "experiment_id": row.get("experiment_id", ""),
                "quality_status": row.get("quality_status", ""),
                "position_rmse_m": as_float(row.get("position_rmse_m")),
                "total_health_score": as_float(row.get("total_health_score")),
                "formation_score": as_float(row.get("formation_score")),
                "evidence_level": row.get("evidence_level", ""),
                "metrics_file": row.get("metrics_file", ""),
                "raw_file": row.get("raw_file", ""),
                "trajectory_figure": preferred_figure(core_figures, "trajectory_xy"),
                "position_error_figure": preferred_figure(core_figures, "position_error"),
                "metrics_summary_figure": preferred_figure(core_figures, "metrics_summary"),
                "altitude_tracking_figure": preferred_figure(core_figures, "altitude_tracking"),
                "report_figure_ready": bool(figure_row.get("report_figure_ready", False)),
                "claim_ceiling": row.get("claim_ceiling", ""),
            }
        )

    missing_figure_slots = [
        row["claim_slot"]
        for row in rows
        if not row["report_figure_ready"]
    ]
    quality_non_pass_slots = [
        row["claim_slot"]
        for row in rows
        if row["quality_status"] != "pass"
    ]
    return {
        "scaffold_id": "candidate_report_table_scaffold_20260610",
        "status": "draft_table_scaffold_not_final_report_acceptance",
        "source_manifest": rel(manifest_path),
        "source_figure_inventory": rel(figure_inventory_path),
        "summary": {
            "row_count": len(rows),
            "claim_family_counts": dict(sorted(family_counts.items())),
            "figure_ready_rows": sum(1 for row in rows if row["report_figure_ready"]),
            "missing_figure_slots": missing_figure_slots,
            "quality_non_pass_slots": quality_non_pass_slots,
        },
        "claim_boundary": [
            "This scaffold is for report table drafting only.",
            "It is not final PMO acceptance and does not select final wording.",
            "Rows must keep candidate_report_evidence_only_not_final_pmo_acceptance until PMO/report review accepts final claims.",
        ],
        "rows": rows,
    }


def format_number(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.6g}"


def write_markdown(scaffold: dict[str, Any], path: Path) -> None:
    summary = scaffold["summary"]
    lines = [
        "# Candidate Report Table Scaffold, 2026-06-10",
        "",
        "Status: draft table scaffold, not final report acceptance.",
        "",
        f"- Source manifest: `{scaffold['source_manifest']}`",
        f"- Source figure inventory: `{scaffold['source_figure_inventory']}`",
        f"- Rows: `{summary['row_count']}`",
        f"- Figure-ready rows: `{summary['figure_ready_rows']}`",
        f"- Missing figure slots: `{len(summary['missing_figure_slots'])}`",
        f"- Non-pass quality slots: `{len(summary['quality_non_pass_slots'])}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in scaffold["claim_boundary"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Candidate Claim Families", ""])
    lines.append("| Claim Family | Rows |")
    lines.append("|---|---:|")
    for family, count in summary["claim_family_counts"].items():
        lines.append(f"| {family} | {count} |")

    lines.extend(["", "## Draft Table Rows", ""])
    lines.append("| Claim Slot | Family | Scene | Controller | RMSE m | Health | Formation | Figure Ready |")
    lines.append("|---|---|---|---|---:|---:|---:|---|")
    for row in scaffold["rows"]:
        lines.append(
            "| {slot} | {family} | {scene} | {controller} | {rmse} | {health} | {formation} | {ready} |".format(
                slot=row["claim_slot"],
                family=row["claim_family"],
                scene=row["scene_id"],
                controller=row["controller_id"],
                rmse=format_number(row["position_rmse_m"]),
                health=format_number(row["total_health_score"]),
                formation=format_number(row["formation_score"]),
                ready=row["report_figure_ready"],
            )
        )

    lines.extend(["", "## Figure Pointers", ""])
    lines.append("| Claim Slot | Trajectory | Error | Metrics | Altitude |")
    lines.append("|---|---|---|---|---|")
    for row in scaffold["rows"]:
        lines.append(
            f"| {row['claim_slot']} | `{row['trajectory_figure']}` | `{row['position_error_figure']}` | `{row['metrics_summary_figure']}` | `{row['altitude_tracking_figure']}` |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST.relative_to(ROOT)))
    parser.add_argument("--figure-inventory", default=str(DEFAULT_FIGURE_INVENTORY.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    manifest_path = repo_path(args.manifest)
    figure_inventory_path = repo_path(args.figure_inventory)
    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    scaffold = build_scaffold(manifest_path, figure_inventory_path)
    json_path = output_dir / "candidate_report_table_scaffold.json"
    md_path = output_dir / "candidate_report_table_scaffold.md"
    json_path.write_text(json.dumps(scaffold, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(scaffold, md_path)

    result = {
        "ok": not scaffold["summary"]["missing_figure_slots"] and not scaffold["summary"]["quality_non_pass_slots"],
        "scaffold_json": rel(json_path),
        "scaffold_markdown": rel(md_path),
        "row_count": scaffold["summary"]["row_count"],
        "figure_ready_rows": scaffold["summary"]["figure_ready_rows"],
        "missing_figure_slot_count": len(scaffold["summary"]["missing_figure_slots"]),
        "quality_non_pass_slot_count": len(scaffold["summary"]["quality_non_pass_slots"]),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
