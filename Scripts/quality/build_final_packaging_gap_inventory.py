#!/usr/bin/env python3
"""Build a static final-packaging gap inventory.

This inventory separates report-drafting readiness from final submission
readiness. It records whether final PDFs, demo video, and PMO final acceptance
packet exist, and points to the static evidence inventories that are already
available. It does not generate PDFs, videos, or acceptance packets.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "static_audits" / "final_packaging_gap_20260610"

SOURCE_INPUTS = {
    "user_manual_source": "Docs/user_manual.md",
    "simulation_report_source": "Docs/simulation_report.md",
    "candidate_manifest": "Results/static_audits/submission_evidence_manifest_20260610/candidate_submission_evidence_manifest.json",
    "candidate_figure_readiness": "Results/static_audits/candidate_figure_readiness_20260610/candidate_figure_readiness_inventory.json",
    "pre_submit_readiness": "Results/static_audits/pre_submit_readiness_inventory_20260610/pre_submit_readiness_inventory.json",
}

FINAL_ARTIFACTS = {
    "user_manual_pdf": {
        "path": "Results/submission/user_manual.pdf",
        "owner": "report_packaging_or_human_export",
        "needed_action": "export reviewed user manual source to PDF",
    },
    "simulation_analysis_report_pdf": {
        "path": "Results/submission/simulation_analysis_report.pdf",
        "owner": "report_packaging_or_human_export",
        "needed_action": "export reviewed simulation analysis report source to PDF",
    },
    "demo_video": {
        "path": "Results/submission/demo_video.mp4",
        "owner": "manual_review_or_video_packaging",
        "needed_action": "record or render demo video using implemented features only",
    },
    "final_acceptance_packet": {
        "path": "Results/agent_packets/returns/PMO-FINAL-SUBMISSION-ACCEPTANCE.json",
        "owner": "PMO_or_user",
        "needed_action": "write final acceptance packet after final artifacts and claim boundaries are reviewed",
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


def read_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def path_record(path_value: str) -> dict[str, Any]:
    path = repo_path(path_value)
    return {
        "path": path_value,
        "exists": path.exists(),
        "kind": "directory" if path.is_dir() else "file" if path.is_file() else "missing",
        "size_bytes": path.stat().st_size if path.is_file() else 0,
    }


def build_inventory() -> dict[str, Any]:
    source_inputs = {name: path_record(path) for name, path in SOURCE_INPUTS.items()}
    final_artifacts = {
        name: {**path_record(str(spec["path"])), "owner": spec["owner"], "needed_action": spec["needed_action"]}
        for name, spec in FINAL_ARTIFACTS.items()
    }
    missing_final_artifacts = [
        name for name, item in final_artifacts.items() if not item["exists"]
    ]

    figure_inventory = read_json_if_exists(repo_path(SOURCE_INPUTS["candidate_figure_readiness"]))
    pre_submit_inventory = read_json_if_exists(repo_path(SOURCE_INPUTS["pre_submit_readiness"]))

    readiness_signals = {
        "candidate_figure_not_ready_count": figure_inventory.get("summary", {}).get("not_ready_count"),
        "candidate_figure_ready_count": figure_inventory.get("summary", {}).get("report_figure_ready_count"),
        "candidate_row_count": figure_inventory.get("summary", {}).get("candidate_row_count"),
        "pre_submit_final_review_missing_count": pre_submit_inventory.get("summary", {}).get("final_review_missing_count"),
        "pre_submit_live_claim_blocker_count": pre_submit_inventory.get("summary", {}).get("live_claim_blocker_count"),
    }

    source_inputs_ready = all(item["exists"] for item in source_inputs.values())
    final_submission_ready = not missing_final_artifacts and source_inputs_ready

    return {
        "inventory_id": "final_packaging_gap_20260610",
        "status": "final_packaging_gap_inventory_not_final_acceptance",
        "summary": {
            "source_inputs_ready": source_inputs_ready,
            "missing_final_artifact_count": len(missing_final_artifacts),
            "final_submission_ready": final_submission_ready,
        },
        "source_inputs": source_inputs,
        "readiness_signals": readiness_signals,
        "final_artifacts": final_artifacts,
        "missing_final_artifacts": missing_final_artifacts,
        "claim_boundary": [
            "This inventory lists packaging gaps only.",
            "It does not generate final PDFs, demo video, or PMO final acceptance.",
            "Static evidence readiness must not be treated as final submission readiness.",
        ],
    }


def write_markdown(inventory: dict[str, Any], path: Path) -> None:
    summary = inventory["summary"]
    lines = [
        "# Final Packaging Gap Inventory, 2026-06-10",
        "",
        "Status: final packaging gap inventory, not final acceptance.",
        "",
        f"- Source inputs ready: `{summary['source_inputs_ready']}`",
        f"- Missing final artifacts: `{summary['missing_final_artifact_count']}`",
        f"- Final submission ready: `{summary['final_submission_ready']}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in inventory["claim_boundary"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Readiness Signals", ""])
    lines.append("| Signal | Value |")
    lines.append("|---|---:|")
    for name, value in inventory["readiness_signals"].items():
        lines.append(f"| {name} | {value} |")

    lines.extend(["", "## Source Inputs", ""])
    lines.append("| Item | Exists | Path |")
    lines.append("|---|---|---|")
    for name, item in inventory["source_inputs"].items():
        lines.append(f"| {name} | {item['exists']} | `{item['path']}` |")

    lines.extend(["", "## Final Artifacts", ""])
    lines.append("| Artifact | Exists | Owner | Needed Action | Path |")
    lines.append("|---|---|---|---|---|")
    for name, item in inventory["final_artifacts"].items():
        lines.append(
            f"| {name} | {item['exists']} | {item['owner']} | {item['needed_action']} | `{item['path']}` |"
        )

    lines.extend(["", "## Missing Final Artifacts", ""])
    if inventory["missing_final_artifacts"]:
        for name in inventory["missing_final_artifacts"]:
            item = inventory["final_artifacts"][name]
            lines.append(f"- `{name}`: `{item['path']}`")
    else:
        lines.append("- None.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory = build_inventory()

    json_path = output_dir / "final_packaging_gap_inventory.json"
    md_path = output_dir / "final_packaging_gap_inventory.md"
    json_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(inventory, md_path)

    result = {
        "ok": True,
        "inventory_json": rel(json_path),
        "inventory_markdown": rel(md_path),
        "source_inputs_ready": inventory["summary"]["source_inputs_ready"],
        "missing_final_artifact_count": inventory["summary"]["missing_final_artifact_count"],
        "final_submission_ready": inventory["summary"]["final_submission_ready"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
