#!/usr/bin/env python3
"""Build a dry-run plan for final PDF export commands.

The plan records what commands should be used after approval. It does not run
Pandoc export, create Results/submission, write PDFs, record video, or write
PMO final acceptance.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE_OUTPUT_READINESS = (
    ROOT
    / "Results"
    / "static_audits"
    / "submission_source_output_readiness_20260610"
    / "submission_source_output_readiness.json"
)
DEFAULT_ARTIFACT_MANIFEST = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_artifacts_20260610"
    / "final_submission_artifact_manifest_check.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "static_audits" / "pdf_export_dry_run_plan_20260610"

PDF_EXPORTS = {
    "user_manual_pdf": {
        "source": "Docs/user_manual.md",
        "output": "Results/submission/user_manual.pdf",
        "title": "MoSim user manual",
    },
    "simulation_analysis_report_pdf": {
        "source": "Docs/simulation_report.md",
        "output": "Results/submission/simulation_analysis_report.pdf",
        "title": "MoSim simulation analysis report",
    },
}

PDF_ENGINES_BY_PREFERENCE = [
    "xelatex",
    "lualatex",
    "tectonic",
    "pdflatex",
    "wkhtmltopdf",
    "weasyprint",
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


def quote_arg(value: str) -> str:
    if all(ch not in value for ch in " \t'\""):
        return value
    return '"' + value.replace('"', '\\"') + '"'


def tool_record(name: str) -> dict[str, Any]:
    source = shutil.which(name)
    return {
        "name": name,
        "available": bool(source),
        "source": source or "",
    }


def choose_pdf_engine() -> tuple[str, list[dict[str, Any]]]:
    records = [tool_record(name) for name in PDF_ENGINES_BY_PREFERENCE]
    for record in records:
        if record["available"]:
            return str(record["name"]), records
    return "", records


def build_command(source: str, output: str, pdf_engine: str) -> str:
    engine_arg = f" --pdf-engine={quote_arg(pdf_engine)}" if pdf_engine else " --pdf-engine=<approved_pdf_engine>"
    return (
        "pandoc "
        + quote_arg(source)
        + " --from markdown --standalone"
        + engine_arg
        + " --output "
        + quote_arg(output)
    )


def export_record(name: str, spec: dict[str, str], pdf_engine: str, blockers: list[str]) -> dict[str, Any]:
    source_path = repo_path(spec["source"])
    output_path = repo_path(spec["output"])
    record_blockers = list(blockers)
    if not source_path.is_file():
        record_blockers.append("source_doc_missing")
    if not pdf_engine:
        record_blockers.append("pdf_engine_missing")
    return {
        "export_id": name,
        "title": spec["title"],
        "source": spec["source"],
        "output": spec["output"],
        "source_exists": source_path.is_file(),
        "output_exists_before_run": output_path.exists(),
        "dry_run_only": True,
        "runs_command_now": False,
        "creates_output_now": False,
        "command_after_approval": build_command(spec["source"], spec["output"], pdf_engine),
        "blocked_by": sorted(set(record_blockers)),
    }


def build_plan(source_output_readiness_path: Path, artifact_manifest_path: Path) -> dict[str, Any]:
    source_output_readiness = read_json(source_output_readiness_path)
    artifact_manifest = read_json(artifact_manifest_path)

    pandoc = tool_record("pandoc")
    pdf_engine, pdf_engine_records = choose_pdf_engine()
    readiness_summary = source_output_readiness.get("summary", {})
    artifact_summary = artifact_manifest.get("summary", {})

    source_docs_ready = readiness_summary.get("source_docs_ready") is True
    source_edit_approved = readiness_summary.get("safe_to_export_final_pdfs_now") is True
    final_artifacts_ready = artifact_summary.get("final_submission_artifacts_ready") is True
    pdf_engine_available = bool(pdf_engine)

    blockers: list[dict[str, str]] = []
    blocker_ids: list[str] = []
    if not source_docs_ready:
        blockers.append(
            {
                "blocker_id": "source_docs_missing",
                "reason": "one or more Markdown sources are missing",
                "needed_action": "restore source Markdown before PDF export",
            }
        )
        blocker_ids.append("source_docs_missing")
    if not pandoc["available"]:
        blockers.append(
            {
                "blocker_id": "pandoc_missing",
                "reason": "Pandoc is not available on PATH",
                "needed_action": "install or expose Pandoc before PDF export",
            }
        )
        blocker_ids.append("pandoc_missing")
    if not pdf_engine_available:
        blockers.append(
            {
                "blocker_id": "pdf_engine_missing",
                "reason": "no preferred Pandoc PDF engine is available on PATH",
                "needed_action": "install or expose xelatex, lualatex, tectonic, wkhtmltopdf, or another approved engine",
            }
        )
        blocker_ids.append("pdf_engine_missing")
    if not source_edit_approved:
        blockers.append(
            {
                "blocker_id": "report_source_edit_not_approved",
                "reason": "source-output readiness does not permit final PDF export yet",
                "needed_action": "obtain explicit human/PMO approval for report-source edits and final PDF export",
            }
        )
        blocker_ids.append("report_source_edit_not_approved")
    if not final_artifacts_ready:
        blockers.append(
            {
                "blocker_id": "final_artifacts_missing",
                "reason": "final artifact manifest still reports missing final outputs",
                "needed_action": "after approved export and video creation, rerun final artifact manifest check",
            }
        )
        blocker_ids.append("final_artifacts_missing")

    safe_to_run_pdf_export_now = (
        source_docs_ready
        and pandoc["available"]
        and pdf_engine_available
        and source_edit_approved
    )

    exports = {
        name: export_record(name, spec, pdf_engine, blocker_ids)
        for name, spec in PDF_EXPORTS.items()
    }

    return {
        "plan_id": "pdf_export_dry_run_plan_20260610",
        "status": "dry_run_pdf_export_plan_not_final_output",
        "inputs": {
            "submission_source_output_readiness": rel(source_output_readiness_path),
            "final_submission_artifact_manifest": rel(artifact_manifest_path),
        },
        "summary": {
            "source_docs_ready": source_docs_ready,
            "pandoc_available": pandoc["available"],
            "pdf_engine_available": pdf_engine_available,
            "selected_pdf_engine": pdf_engine,
            "source_edit_approved_for_export": source_edit_approved,
            "final_artifacts_ready": final_artifacts_ready,
            "safe_to_run_pdf_export_now": safe_to_run_pdf_export_now,
            "runs_pandoc_now": False,
            "creates_submission_dir_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "tooling": {
            "pandoc": pandoc,
            "pdf_engines": pdf_engine_records,
        },
        "exports": exports,
        "blockers": blockers,
        "claim_boundary": [
            "This is a dry-run export command plan only.",
            "It does not run Pandoc.",
            "It does not create Results/submission.",
            "It does not write PDF files.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
        "next_gates_after_approval": [
            "Create Results/submission only after explicit approval.",
            "Run the selected Pandoc commands after source edits and export are approved.",
            "Run check_final_submission_artifact_manifest.py without --allow-missing.",
            "Do not write PMO final acceptance until PDFs, demo video, and review evidence exist.",
        ],
    }


def write_markdown(plan: dict[str, Any], path: Path) -> None:
    summary = plan["summary"]
    lines = [
        "# PDF Export Dry-Run Plan, 2026-06-10",
        "",
        f"Status: `{plan['status']}`",
        "",
        "## Summary",
        "",
        f"- Source docs ready: `{summary['source_docs_ready']}`",
        f"- Pandoc available: `{summary['pandoc_available']}`",
        f"- PDF engine available: `{summary['pdf_engine_available']}`",
        f"- Selected PDF engine: `{summary['selected_pdf_engine']}`",
        f"- Source edit approved for export: `{summary['source_edit_approved_for_export']}`",
        f"- Final artifacts ready: `{summary['final_artifacts_ready']}`",
        f"- Safe to run PDF export now: `{summary['safe_to_run_pdf_export_now']}`",
        f"- Runs Pandoc now: `{summary['runs_pandoc_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in plan["claim_boundary"]:
        lines.append(f"- {item}")

    pandoc = plan["tooling"]["pandoc"]
    lines.extend(
        [
            "",
            "## Tooling",
            "",
            f"- Pandoc available: `{pandoc['available']}`",
            f"- Pandoc source: `{pandoc['source']}`",
            "",
            "| Engine | Available | Source |",
            "|---|---|---|",
        ]
    )
    for engine in plan["tooling"]["pdf_engines"]:
        lines.append(f"| {engine['name']} | {engine['available']} | `{engine['source']}` |")

    lines.extend(
        [
            "",
            "## Commands After Approval",
            "",
            "| Export | Source | Output | Runs Now | Blocked By | Command |",
            "|---|---|---|---|---|---|",
        ]
    )
    for name, item in plan["exports"].items():
        lines.append(
            "| "
            + name
            + f" | `{item['source']}` | `{item['output']}` | `{item['runs_command_now']}` | "
            + f"{', '.join(item['blocked_by'])} | `{item['command_after_approval']}` |"
        )

    lines.extend(["", "## Blockers", ""])
    if plan["blockers"]:
        for blocker in plan["blockers"]:
            lines.append(
                f"- `{blocker['blocker_id']}`: {blocker['reason']} Needed action: {blocker['needed_action']}"
            )
    else:
        lines.append("- None.")

    lines.extend(["", "## Next Gates After Approval", ""])
    for gate in plan["next_gates_after_approval"]:
        lines.append(f"- {gate}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-output-readiness", default=str(DEFAULT_SOURCE_OUTPUT_READINESS.relative_to(ROOT)))
    parser.add_argument("--artifact-manifest", default=str(DEFAULT_ARTIFACT_MANIFEST.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = build_plan(repo_path(args.source_output_readiness), repo_path(args.artifact_manifest))
    json_path = output_dir / "pdf_export_dry_run_plan.json"
    md_path = output_dir / "pdf_export_dry_run_plan.md"
    json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(plan, md_path)

    print(
        json.dumps(
            {
                "ok": True,
                "plan_json": rel(json_path),
                "plan_markdown": rel(md_path),
                "safe_to_run_pdf_export_now": plan["summary"]["safe_to_run_pdf_export_now"],
                "runs_pandoc_now": plan["summary"]["runs_pandoc_now"],
                "generates_final_outputs": plan["summary"]["generates_final_outputs"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
