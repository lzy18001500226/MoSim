#!/usr/bin/env python3
"""Build conservative report-source tables from current authority JSON files."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "control_platform" / "non_frontend_evidence_index_20260718"
AUTH = {
    "controller": "Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json",
    "ab": "Results/control_platform/final_controller_ab_20260718/FINAL_CONTROLLER_SEVEN_SCENARIO_AB.json",
    "safety": "Results/control_platform/p6_safety_runtime_20260717/P6_SAFETY_RUNTIME_MATRIX.json",
    "ftc": "Results/control_platform/p7_ftc_generated_gazebo_r3_20260717/P7_FTC_RUNTIME_CLOSEOUT.json",
    "formation": "Results/control_platform/p8_formation_mode1_gazebo_r7_20260717/PX4CTRL_SWARM_BASIC_METRICS.json",
    "learning": "Results/control_platform/p9_learning_gazebo_r4_20260717/P9_LEARNING_RUNTIME_CLOSEOUT.json",
}


def load(name: str) -> dict[str, Any]:
    return json.loads((ROOT / AUTH[name]).read_text(encoding="utf-8"))


def build() -> dict[str, Any]:
    controller = load("controller")
    ab = load("ab")
    rows = controller.get("rows", [])
    by_cohort: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        by_cohort[str(row.get("cohort", "unknown"))][str(row.get("status", "unknown"))] += 1

    ab_rows = []
    for row in ab.get("rows", []):
        ab_rows.append({
            "profile": row.get("profile", ""),
            "scenario": row.get("scenario", ""),
            "status": row.get("status", ""),
            "primary_rmse_m": row.get("primary_rmse_m"),
            "hover_xy_rmse_m": row.get("hover_xy_rmse_m"),
            "hover_z_rmse_m": row.get("hover_z_rmse_m"),
            "injection_status": row.get("injection_status", ""),
            "landing_disarm": row.get("landing_disarm"),
            "mission_reason": row.get("mission_reason"),
            "run_dir": row.get("run_dir", ""),
        })

    return {
        "schema": "mosim.non_frontend_report_source.v1",
        "date": "2026-07-18",
        "status": "report_source_not_final_report_acceptance",
        "claim_boundary": [
            "Tables are generated from current authority JSON only.",
            "Rows retain accepted, executed_blocked and not_run status.",
            "A/B is an observed same-run comparison and does not establish general superiority.",
            "This source does not render figures, record video, or approve final submission wording.",
        ],
        "sources": AUTH,
        "controller_summary": {
            "counts": controller.get("counts", {}),
            "by_cohort": {cohort: dict(sorted(counts.items())) for cohort, counts in sorted(by_cohort.items())},
        },
        "final_ab_summary": {
            "counts": ab.get("counts", {}),
            "scenarios": sorted({str(row.get("scenario", "")) for row in ab_rows}),
            "rows": ab_rows,
        },
        "specialized_summary": {
            "safety_status": load("safety").get("status"),
            "ftc_status": load("ftc").get("status"),
            "formation_status": load("formation").get("status"),
            "learning_status": load("learning").get("status"),
            "learning_claim_boundary": load("learning").get("claim_boundary", ""),
        },
    }


def write_markdown(data: dict[str, Any], path: Path) -> None:
    counts = data["controller_summary"]["counts"]
    lines = [
        "# Non-Frontend Report Source Tables",
        "",
        "更新时间：2026-07-18。本文是报告数据源，不是最终报告，也不是最终验收。",
        "",
        "## Controller Family Summary",
        "",
        f"- accepted: `{counts.get('accepted')}`",
        f"- executed_blocked: `{counts.get('executed_blocked')}`",
        f"- not_run: `{counts.get('not_run')}`",
        "",
        "| Cohort | Accepted | Executed blocked | Not run |",
        "|---|---:|---:|---:|",
    ]
    for cohort, values in data["controller_summary"]["by_cohort"].items():
        lines.append(f"| {cohort} | {values.get('accepted', 0)} | {values.get('executed_blocked', 0)} | {values.get('not_run', 0)} |")

    lines.extend(["", "## Official PID vs Gain-Scheduled PID", "", "| Profile | Scenario | Status | Primary RMSE (m) | Wind/Fault injection | Landing/disarm | Reason |", "|---|---|---|---:|---|---|---|"])
    for row in data["final_ab_summary"]["rows"]:
        reason = str(row.get("mission_reason") or "").replace("|", "\\|")
        lines.append(f"| {row['profile']} | {row['scenario']} | {row['status']} | {row['primary_rmse_m'] if row['primary_rmse_m'] is not None else ''} | {row['injection_status']} | {row['landing_disarm']} | {reason} |")

    lines.extend(["", "## Specialized Evidence", "", "| Area | Authority status |", "|---|---|"])
    special = data["specialized_summary"]
    for label, key in (("Safety", "safety_status"), ("FTC", "ftc_status"), ("Formation", "formation_status"), ("Learning", "learning_status")):
        lines.append(f"| {label} | `{special[key]}` |")
    lines.extend(["", "## Writing Boundary", ""])
    lines.extend(f"- {item}" for item in data["claim_boundary"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    data = build()
    json_path = output_dir / "NON_FRONTEND_REPORT_SOURCE.json"
    md_path = output_dir / "NON_FRONTEND_REPORT_SOURCE.md"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    write_markdown(data, md_path)
    print(json.dumps({"ok": True, "json": str(json_path.relative_to(ROOT)).replace("\\", "/"), "markdown": str(md_path.relative_to(ROOT)).replace("\\", "/"), "ab_rows": len(data["final_ab_summary"]["rows"])}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
