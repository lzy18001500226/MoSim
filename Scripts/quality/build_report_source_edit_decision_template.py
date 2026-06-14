#!/usr/bin/env python3
"""Build a report-source edit decision template and validate its blocked state.

This creates a reviewable decision template only. It does not approve edits and
does not modify Docs/simulation_report.md.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATCH_PREVIEW = (
    ROOT
    / "Results"
    / "static_audits"
    / "simulation_report_patch_preview_20260610"
    / "simulation_report_patch_preview.json"
)
DEFAULT_SOURCE_EDIT_READINESS = (
    ROOT
    / "Results"
    / "static_audits"
    / "simulation_report_source_edit_readiness_20260610"
    / "simulation_report_source_edit_readiness_gate.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/report_source_edit_decision_template_20260610"
DECISION_CHECKER = ROOT / "Scripts" / "quality" / "check_report_source_edit_decision.py"

VALID_DECISIONS = ["pending_review", "approved", "rejected", "narrowed"]
CANONICAL_DECISION_PATH = (
    "Results/static_audits/report_source_edit_decision_template_20260610/"
    "report_source_edit_decision.template.json"
)


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


def load_decision_checker():
    spec = importlib.util.spec_from_file_location("check_report_source_edit_decision", DECISION_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_report_source_edit_decision.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_template(patch_preview_path: Path, readiness_path: Path) -> dict[str, Any]:
    patch_preview = read_json(patch_preview_path)
    previews = patch_preview.get("previews", [])
    preview_ids = [
        str(item.get("preview_id", ""))
        for item in previews
        if isinstance(item, dict) and item.get("preview_id")
    ]
    return {
        "decision_id": "report_source_edit_decision_20260610",
        "status": "decision_template_pending_review",
        "decision": "pending_review",
        "valid_decisions": VALID_DECISIONS,
        "decision_owner": "<user_or_PMO>",
        "decided_at": "<ISO8601_after_review>",
        "applies_to": {
            "simulation_report": "Docs/simulation_report.md",
            "patch_preview": rel(patch_preview_path),
            "source_edit_readiness_gate": rel(readiness_path),
        },
        "approved_preview_ids": [],
        "rejected_preview_ids": [],
        "narrowed_scope_notes": "",
        "review_notes": "",
        "required_boundaries": [
            "Do not claim final PMO acceptance.",
            "Do not claim final submission ready.",
            "Do not claim planner_ready or closed_loop.",
            "Do not claim UE build/runtime/editor success.",
            "Do not delete historical evidence without explicit approval.",
        ],
        "available_preview_ids": preview_ids,
        "safe_to_apply_report_source_edits": False,
    }


def validate_template(template: dict[str, Any], patch_preview_path: Path) -> dict[str, Any]:
    patch_preview = read_json(patch_preview_path)
    checker = load_decision_checker()
    return checker.validate_decision_template(
        template,
        patch_preview,
        repo_path(CANONICAL_DECISION_PATH),
        patch_preview_path,
    )


def build_artifacts(patch_preview_path: Path, readiness_path: Path) -> dict[str, Any]:
    template = build_template(patch_preview_path, readiness_path)
    validation = validate_template(template, patch_preview_path)
    return {
        "artifact_id": "report_source_edit_decision_template_20260610",
        "status": "decision_template_pending_review_not_approval",
        "canonical_template_path": CANONICAL_DECISION_PATH,
        "summary": {
            "available_preview_count": len(template["available_preview_ids"]),
            "approved_preview_count": len(template["approved_preview_ids"]),
            "decision_pending": template["decision"] == "pending_review",
            "safe_to_apply_report_source_edits": False,
            "edits_report_source": False,
            "final_acceptance": False,
        },
        "template": template,
        "validation": validation,
        "claim_boundary": [
            "This artifact is a decision template only.",
            "It does not approve report-source edits.",
            "It does not edit Docs/simulation_report.md.",
            "It does not generate final PDFs/video or PMO final acceptance.",
        ],
    }


def write_markdown(artifact: dict[str, Any], path: Path) -> None:
    summary = artifact["summary"]
    validation = artifact["validation"]
    lines = [
        "# Report Source Edit Decision Template, 2026-06-10",
        "",
        f"Status: `{artifact['status']}`",
        "",
        "## Summary",
        "",
        f"- Available previews: `{summary['available_preview_count']}`",
        f"- Approved previews: `{summary['approved_preview_count']}`",
        f"- Decision pending: `{summary['decision_pending']}`",
        f"- Safe to apply report source edits: `{summary['safe_to_apply_report_source_edits']}`",
        f"- Edits report source: `{summary['edits_report_source']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Validation",
        "",
        f"- OK: `{validation['ok']}`",
        f"- Decision: `{validation['decision']}`",
        f"- Issues: `{len(validation['issues'])}`",
        f"- Warnings: `{len(validation['warnings'])}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in artifact["claim_boundary"]:
        lines.append(f"- {item}")
    lines.extend(["", "## Template", "", "```json", json.dumps(artifact["template"], ensure_ascii=False, indent=2), "```"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--patch-preview", default=str(DEFAULT_PATCH_PREVIEW.relative_to(ROOT)))
    parser.add_argument("--source-edit-readiness", default=str(DEFAULT_SOURCE_EDIT_READINESS.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = build_artifacts(repo_path(args.patch_preview), repo_path(args.source_edit_readiness))
    json_path = output_dir / "report_source_edit_decision_template.json"
    md_path = output_dir / "report_source_edit_decision_template.md"
    template_path = output_dir / "report_source_edit_decision.template.json"
    json_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    template_path.write_text(json.dumps(artifact["template"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(artifact, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "artifact_json": rel(json_path),
                "artifact_markdown": rel(md_path),
                "template": rel(template_path),
                "decision": artifact["template"]["decision"],
                "safe_to_apply_report_source_edits": artifact["summary"]["safe_to_apply_report_source_edits"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
