#!/usr/bin/env python3
"""Build a static readiness inventory for final submission source outputs.

This inventory checks whether the project is ready to export final PDFs, demo
video, and final acceptance artifacts. It does not generate those outputs.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FINAL_PACKAGING_GAP = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_packaging_gap_20260610"
    / "final_packaging_gap_inventory.json"
)
DEFAULT_SOURCE_EDIT_READINESS = (
    ROOT
    / "Results"
    / "static_audits"
    / "simulation_report_source_edit_readiness_20260610"
    / "simulation_report_source_edit_readiness_gate.json"
)
DEFAULT_SOURCE_EDIT_APPLICATION_PLAN = (
    ROOT
    / "Results"
    / "static_audits"
    / "simulation_report_source_edit_application_plan_20260610"
    / "simulation_report_source_edit_application_plan.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "static_audits" / "submission_source_output_readiness_20260610"

SOURCE_DOCS = {
    "user_manual_source": "Docs/报告/用户手册_正文骨架.md",
    "simulation_report_source": "Docs/报告/仿真分析报告_正文骨架.md",
}
EXPECTED_FINAL_OUTPUTS = {
    "user_manual_pdf": "Results/submission/user_manual.pdf",
    "simulation_analysis_report_pdf": "Results/submission/simulation_analysis_report.pdf",
    "demo_video": "Results/submission/demo_video.mp4",
    "final_acceptance_packet": "Results/agent_packets/returns/PMO-FINAL-SUBMISSION-ACCEPTANCE.json",
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


def path_record(path_value: str) -> dict[str, Any]:
    path = repo_path(path_value)
    return {
        "path": path_value,
        "exists": path.exists(),
        "kind": "directory" if path.is_dir() else "file" if path.is_file() else "missing",
        "size_bytes": path.stat().st_size if path.is_file() else 0,
    }


def pandoc_record() -> dict[str, Any]:
    source = shutil.which("pandoc")
    if not source:
        return {
            "available": False,
            "source": "",
            "version": "",
            "note": "pandoc was not found on PATH",
        }
    version = ""
    try:
        completed = subprocess.run(
            ["pandoc", "--version"],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=10,
        )
        version = completed.stdout.splitlines()[0] if completed.stdout else ""
    except Exception as exc:
        version = f"version_probe_failed: {type(exc).__name__}: {exc}"
    return {
        "available": True,
        "source": source,
        "version": version,
        "note": "tool presence only; this inventory does not run PDF export",
    }


def build_readiness(
    final_packaging_gap_path: Path,
    source_edit_readiness_path: Path,
    source_edit_application_plan_path: Path,
) -> dict[str, Any]:
    final_packaging_gap = read_json(final_packaging_gap_path)
    source_edit_readiness = read_json(source_edit_readiness_path)
    source_edit_application_plan = read_json(source_edit_application_plan_path)

    source_docs = {name: path_record(path) for name, path in SOURCE_DOCS.items()}
    final_outputs = {name: path_record(path) for name, path in EXPECTED_FINAL_OUTPUTS.items()}
    missing_final_outputs = [name for name, item in final_outputs.items() if not item["exists"]]
    source_docs_ready = all(item["exists"] and item["kind"] == "file" for item in source_docs.values())
    pandoc = pandoc_record()
    source_edit_safe = (
        source_edit_readiness.get("summary", {}).get("safe_to_apply_report_source_edits_now") is True
    )
    application_plan_safe = (
        source_edit_application_plan.get("summary", {}).get("safe_to_apply_report_source_edits_now") is True
    )
    application_plan_applied = (
        source_edit_application_plan.get("summary", {}).get("applies_report_source_edits_now") is True
        or source_edit_application_plan.get("summary", {}).get("edits_report_source") is True
    )
    final_submission_ready = final_packaging_gap.get("summary", {}).get("final_submission_ready") is True

    blockers: list[dict[str, str]] = []
    if not source_docs_ready:
        blockers.append(
            {
                "blocker_id": "source_docs_missing",
                "reason": "one or more source Markdown files are missing",
                "needed_action": "restore required source docs before export",
            }
        )
    if not pandoc["available"]:
        blockers.append(
            {
                "blocker_id": "pandoc_missing",
                "reason": "Pandoc is unavailable on PATH",
                "needed_action": "install or expose Pandoc before PDF export",
            }
        )
    if not source_edit_safe:
        blockers.append(
            {
                "blocker_id": "report_source_edit_not_approved",
                "reason": "simulation report source edit readiness gate does not permit applying preview snippets",
                "needed_action": "obtain explicit human/PMO approval before applying report-source preview edits",
            }
        )
    if not application_plan_safe:
        blockers.append(
            {
                "blocker_id": "report_source_edit_application_plan_not_ready",
                "reason": "simulation report source edit application plan is not approved for application",
                "needed_action": "approve or narrow the A1 report-source edit decision before source edit application planning can proceed",
            }
        )
    if not application_plan_applied:
        blockers.append(
            {
                "blocker_id": "report_source_edit_application_not_applied",
                "reason": "no evidence shows the approved report-source application plan has been applied to Docs/报告/仿真分析报告_正文骨架.md",
                "needed_action": "apply approved report-source edits in a separate authorized step, then regenerate source-output readiness",
            }
        )
    if missing_final_outputs:
        blockers.append(
            {
                "blocker_id": "final_outputs_missing",
                "reason": "final PDFs, demo video, or PMO final acceptance packet are missing",
                "needed_action": "export reviewed PDFs, create reviewed demo video, then write PMO final acceptance packet",
            }
        )

    safe_to_export_final_pdfs_now = (
        source_docs_ready
        and pandoc["available"]
        and source_edit_safe
        and application_plan_safe
        and application_plan_applied
    )
    safe_to_record_demo_video_now = False
    safe_to_write_final_acceptance_now = final_submission_ready and not missing_final_outputs

    return {
        "inventory_id": "submission_source_output_readiness_20260610",
        "status": "static_source_output_readiness_not_final_submission",
        "inputs": {
            "final_packaging_gap_inventory": rel(final_packaging_gap_path),
            "simulation_report_source_edit_readiness_gate": rel(source_edit_readiness_path),
            "simulation_report_source_edit_application_plan": rel(source_edit_application_plan_path),
        },
        "summary": {
            "source_docs_ready": source_docs_ready,
            "pandoc_available": pandoc["available"],
            "submission_dir_exists": repo_path("Results/submission").is_dir(),
            "missing_final_output_count": len(missing_final_outputs),
            "source_edit_readiness_safe_to_apply": source_edit_safe,
            "source_edit_application_plan_safe_to_apply": application_plan_safe,
            "source_edit_application_plan_applied": application_plan_applied,
            "safe_to_export_final_pdfs_now": safe_to_export_final_pdfs_now,
            "safe_to_record_demo_video_now": safe_to_record_demo_video_now,
            "safe_to_write_final_acceptance_now": safe_to_write_final_acceptance_now,
            "final_submission_ready": final_submission_ready,
            "edits_report_source": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "tooling": {"pandoc": pandoc},
        "source_docs": source_docs,
        "final_outputs": final_outputs,
        "missing_final_outputs": missing_final_outputs,
        "blockers": blockers,
        "claim_boundary": [
            "This inventory checks source-output readiness only.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
            "It does not edit Docs/报告/仿真分析报告_正文骨架.md.",
        ],
    }


def write_markdown(readiness: dict[str, Any], path: Path) -> None:
    summary = readiness["summary"]
    lines = [
        "# Submission Source Output Readiness, 2026-06-10",
        "",
        "Status: static source-output readiness, not final submission.",
        "",
        "## Summary",
        "",
        f"- Source docs ready: `{summary['source_docs_ready']}`",
        f"- Pandoc available: `{summary['pandoc_available']}`",
        f"- Submission dir exists: `{summary['submission_dir_exists']}`",
        f"- Missing final outputs: `{summary['missing_final_output_count']}`",
        f"- Source edit readiness safe to apply: `{summary['source_edit_readiness_safe_to_apply']}`",
        f"- Source edit application plan safe to apply: `{summary['source_edit_application_plan_safe_to_apply']}`",
        f"- Source edit application plan applied: `{summary['source_edit_application_plan_applied']}`",
        f"- Safe to export final PDFs now: `{summary['safe_to_export_final_pdfs_now']}`",
        f"- Safe to record demo video now: `{summary['safe_to_record_demo_video_now']}`",
        f"- Safe to write final acceptance now: `{summary['safe_to_write_final_acceptance_now']}`",
        f"- Final submission ready: `{summary['final_submission_ready']}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in readiness["claim_boundary"]:
        lines.append(f"- {item}")

    pandoc = readiness["tooling"]["pandoc"]
    lines.extend(
        [
            "",
            "## Tooling",
            "",
            f"- Pandoc available: `{pandoc['available']}`",
            f"- Pandoc source: `{pandoc['source']}`",
            f"- Pandoc version: `{pandoc['version']}`",
            f"- Note: {pandoc['note']}",
            "",
            "## Source Docs",
            "",
            "| Item | Exists | Size | Path |",
            "|---|---|---:|---|",
        ]
    )
    for name, item in readiness["source_docs"].items():
        lines.append(f"| {name} | {item['exists']} | {item['size_bytes']} | `{item['path']}` |")

    lines.extend(["", "## Final Outputs", "", "| Item | Exists | Size | Path |", "|---|---|---:|---|"])
    for name, item in readiness["final_outputs"].items():
        lines.append(f"| {name} | {item['exists']} | {item['size_bytes']} | `{item['path']}` |")

    lines.extend(["", "## Blockers", ""])
    if readiness["blockers"]:
        for blocker in readiness["blockers"]:
            lines.append(
                f"- `{blocker['blocker_id']}`: {blocker['reason']} Needed action: {blocker['needed_action']}"
            )
    else:
        lines.append("- None.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final-packaging-gap", default=str(DEFAULT_FINAL_PACKAGING_GAP.relative_to(ROOT)))
    parser.add_argument("--source-edit-readiness", default=str(DEFAULT_SOURCE_EDIT_READINESS.relative_to(ROOT)))
    parser.add_argument(
        "--source-edit-application-plan",
        default=str(DEFAULT_SOURCE_EDIT_APPLICATION_PLAN.relative_to(ROOT)),
    )
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    readiness = build_readiness(
        repo_path(args.final_packaging_gap),
        repo_path(args.source_edit_readiness),
        repo_path(args.source_edit_application_plan),
    )
    json_path = output_dir / "submission_source_output_readiness.json"
    md_path = output_dir / "submission_source_output_readiness.md"
    json_path.write_text(json.dumps(readiness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(readiness, md_path)

    result = {
        "ok": True,
        "readiness_json": rel(json_path),
        "readiness_markdown": rel(md_path),
        "source_docs_ready": readiness["summary"]["source_docs_ready"],
        "pandoc_available": readiness["summary"]["pandoc_available"],
        "safe_to_export_final_pdfs_now": readiness["summary"]["safe_to_export_final_pdfs_now"],
        "missing_final_output_count": readiness["summary"]["missing_final_output_count"],
        "final_submission_ready": readiness["summary"]["final_submission_ready"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
