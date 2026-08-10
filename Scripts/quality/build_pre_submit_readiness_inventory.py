#!/usr/bin/env python3
"""Build a static pre-submit readiness inventory.

The output is a planning inventory, not final submission acceptance. It checks
whether current project files and candidate evidence paths exist, then records
which final-review or live/runtime claims still need separate evidence.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
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
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "static_audits" / "pre_submit_readiness_inventory_20260610"

CORE_PATHS = {
    "design_docs": "Docs/Design",
    "workflow_docs": "Docs/Workflows",
    "capability_index": "Docs/Index/capability_index.md",
    "machine_capability_index": "Config/capabilities/capability_index.json",
    "models": "Models",
    "controller_config": "Config/controllers",
    "scenario_config": "Config/scenarios",
    "quality_scripts": "Scripts/quality",
    "tests": "Scripts/tests",
    "candidate_manifest": "Results/static_audits/submission_evidence_manifest_20260610/candidate_submission_evidence_manifest.json",
    "evidence_map": "Results/static_audits/mworks_control_evidence_map_20260610/evidence_map.json",
}

FINAL_REVIEW_ARTIFACTS = {
    "user_manual_source": "Docs/报告/用户手册_正文骨架.md",
    "simulation_report_source": "Docs/报告/仿真分析报告_正文骨架.md",
    "user_manual_pdf": "Results/submission/user_manual.pdf",
    "simulation_report_pdf": "Results/submission/simulation_analysis_report.pdf",
    "demo_video": "Results/submission/demo_video.mp4",
    "final_acceptance_packet": "Results/agent_packets/returns/PMO-FINAL-SUBMISSION-ACCEPTANCE.json",
}

LIVE_CLAIM_BLOCKERS = [
    {
        "claim": "native Syslab final report generation",
        "status": "not_proven_by_static_manifest",
        "needed_evidence": "Syslab run output or equivalent reviewed metric/report-generation packet",
    },
    {
        "claim": "live MWORKS no-start attach success",
        "status": "blocked_open_dependency",
        "needed_evidence": "authorized live MWORKS/Sysplorer gate with terminal return packet",
    },
    {
        "claim": "ROS2 planner_ready, controller handoff, or closed_loop",
        "status": "blocked_absent_live_grounding",
        "needed_evidence": "same-run ROS2 TF/map/world grounding and planner/controller handoff evidence",
    },
    {
        "claim": "UE build/runtime/editor success or live command echo",
        "status": "source_static_only",
        "needed_evidence": "separately authorized UE build/runtime/echo gate and return packet",
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


def path_status(path_value: str) -> dict[str, Any]:
    path = repo_path(path_value)
    return {
        "path": path_value,
        "exists": path.exists(),
        "kind": "directory" if path.is_dir() else "file" if path.is_file() else "missing",
    }


def candidate_status(row: dict[str, Any]) -> dict[str, Any]:
    metrics_path = str(row.get("metrics_file", ""))
    raw_path = str(row.get("raw_file", ""))
    return {
        "claim_slot": row.get("claim_slot", ""),
        "experiment_id": row.get("experiment_id", ""),
        "claim_family": row.get("claim_family", ""),
        "quality_status": row.get("quality_status", ""),
        "claim_ceiling": row.get("claim_ceiling", ""),
        "metrics_file": metrics_path,
        "metrics_exists": repo_path(metrics_path).exists() if metrics_path else False,
        "raw_file": raw_path,
        "raw_exists": repo_path(raw_path).exists() if raw_path else False,
    }


def build_inventory(manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    rows = [row for row in manifest.get("candidate_rows", []) if isinstance(row, dict)]
    candidate_rows = [candidate_status(row) for row in rows]
    missing_candidate_files = [
        row
        for row in candidate_rows
        if not row["metrics_exists"] or not row["raw_exists"]
    ]
    family_counts = Counter(str(row.get("claim_family", "")) for row in rows)
    core_status = {
        name: path_status(path_value)
        for name, path_value in CORE_PATHS.items()
    }
    final_review_status = {
        name: path_status(path_value)
        for name, path_value in FINAL_REVIEW_ARTIFACTS.items()
    }

    ready_static_inputs = all(item["exists"] for item in core_status.values())
    candidate_paths_ready = not missing_candidate_files
    final_review_missing = [
        name
        for name, item in final_review_status.items()
        if not item["exists"]
    ]

    return {
        "inventory_id": "pre_submit_readiness_inventory_20260610",
        "status": "static_inventory_not_final_submission_acceptance",
        "source_manifest": rel(manifest_path),
        "source_manifest_status": manifest.get("status"),
        "summary": {
            "ready_static_inputs": ready_static_inputs,
            "candidate_paths_ready": candidate_paths_ready,
            "candidate_row_count": len(candidate_rows),
            "claim_family_counts": dict(sorted(family_counts.items())),
            "final_review_missing_count": len(final_review_missing),
            "live_claim_blocker_count": len(LIVE_CLAIM_BLOCKERS),
        },
        "core_paths": core_status,
        "candidate_rows": candidate_rows,
        "missing_candidate_files": missing_candidate_files,
        "final_review_artifacts": final_review_status,
        "final_review_missing": final_review_missing,
        "live_claim_blockers": LIVE_CLAIM_BLOCKERS,
        "claim_boundary": [
            "This inventory supports planning and report-drafting readiness only.",
            "It is not final PMO acceptance.",
            "It does not prove native Syslab completion, live MWORKS attach, ROS2 planner_ready/closed_loop, or UE build/runtime/editor success.",
        ],
    }


def write_markdown(inventory: dict[str, Any], path: Path) -> None:
    summary = inventory["summary"]
    lines = [
        "# Pre-Submit Readiness Inventory, 2026-06-10",
        "",
        "Status: static inventory, not final submission acceptance.",
        "",
        f"- Source manifest: `{inventory['source_manifest']}`",
        f"- Source manifest status: `{inventory['source_manifest_status']}`",
        f"- Candidate rows: `{summary['candidate_row_count']}`",
        f"- Candidate metrics/raw paths ready: `{summary['candidate_paths_ready']}`",
        f"- Final-review missing artifacts: `{summary['final_review_missing_count']}`",
        f"- Live/runtime claim blockers: `{summary['live_claim_blocker_count']}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in inventory["claim_boundary"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Candidate Claim Families", ""])
    lines.append("| Claim Family | Rows |")
    lines.append("|---|---:|")
    for family, count in inventory["summary"]["claim_family_counts"].items():
        lines.append(f"| {family} | {count} |")

    lines.extend(["", "## Core Static Paths", ""])
    lines.append("| Item | Exists | Path |")
    lines.append("|---|---|---|")
    for name, item in inventory["core_paths"].items():
        lines.append(f"| {name} | {item['exists']} | `{item['path']}` |")

    lines.extend(["", "## Missing Final-Review Artifacts", ""])
    if inventory["final_review_missing"]:
        for name in inventory["final_review_missing"]:
            item = inventory["final_review_artifacts"][name]
            lines.append(f"- `{name}`: `{item['path']}`")
    else:
        lines.append("- None.")

    lines.extend(["", "## Live Claim Blockers", ""])
    lines.append("| Claim | Status | Needed Evidence |")
    lines.append("|---|---|---|")
    for blocker in inventory["live_claim_blockers"]:
        lines.append(
            f"| {blocker['claim']} | {blocker['status']} | {blocker['needed_evidence']} |"
        )

    lines.extend(["", "## Missing Candidate Files", ""])
    if inventory["missing_candidate_files"]:
        lines.append("| Claim Slot | Metrics Exists | Raw Exists |")
        lines.append("|---|---|---|")
        for row in inventory["missing_candidate_files"]:
            lines.append(
                f"| {row['claim_slot']} | {row['metrics_exists']} | {row['raw_exists']} |"
            )
    else:
        lines.append("- None. Candidate metrics/raw file paths resolve.")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    manifest_path = repo_path(args.manifest)
    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory(manifest_path)

    json_path = output_dir / "pre_submit_readiness_inventory.json"
    md_path = output_dir / "pre_submit_readiness_inventory.md"
    json_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(inventory, md_path)

    result = {
        "ok": not inventory["missing_candidate_files"],
        "inventory_json": rel(json_path),
        "inventory_markdown": rel(md_path),
        "candidate_paths_ready": inventory["summary"]["candidate_paths_ready"],
        "final_review_missing_count": inventory["summary"]["final_review_missing_count"],
        "live_claim_blocker_count": inventory["summary"]["live_claim_blocker_count"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
