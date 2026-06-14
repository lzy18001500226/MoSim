#!/usr/bin/env python3
"""Build a readiness gate for applying simulation-report source edits.

This gate answers whether the current non-applying patch preview may be applied
to `Docs/simulation_report.md`. It does not edit the report.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PATCH_PREVIEW_CHECK = (
    ROOT
    / "Results"
    / "static_audits"
    / "simulation_report_patch_preview_20260610"
    / "simulation_report_patch_preview_check.json"
)
DEFAULT_PATCH_PREVIEW = (
    ROOT
    / "Results"
    / "static_audits"
    / "simulation_report_patch_preview_20260610"
    / "simulation_report_patch_preview.json"
)
DEFAULT_FINAL_PACKAGING_GAP = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_packaging_gap_20260610"
    / "final_packaging_gap_inventory.json"
)
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
DEFAULT_DECISION_TEMPLATE = (
    ROOT
    / "Results"
    / "static_audits"
    / "report_source_edit_decision_template_20260610"
    / "report_source_edit_decision.template.json"
)
DEFAULT_DECISION_CHECK = (
    ROOT
    / "Results"
    / "static_audits"
    / "report_source_edit_decision_template_20260610"
    / "report_source_edit_decision_check.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "static_audits" / "simulation_report_source_edit_readiness_20260610"
DECISION_CHECKER = ROOT / "Scripts" / "quality" / "check_report_source_edit_decision.py"


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


def gate(
    gate_id: str,
    ok: bool,
    evidence: str,
    blocking_reason: str = "",
    needed_action: str = "",
) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "ok": ok,
        "evidence": evidence,
        "blocking_reason": blocking_reason,
        "needed_action": needed_action,
    }


def build_gate(
    patch_preview_check_path: Path,
    patch_preview_path: Path,
    final_packaging_gap_path: Path,
    outline_gap_path: Path,
    rewrite_plan_path: Path,
    decision_template_path: Path,
    decision_check_path: Path,
) -> dict[str, Any]:
    patch_preview_check = read_json(patch_preview_check_path)
    patch_preview = read_json(patch_preview_path)
    final_packaging_gap = read_json(final_packaging_gap_path)
    outline_gap = read_json(outline_gap_path)
    rewrite_plan = read_json(rewrite_plan_path)
    decision_template = read_json(decision_template_path)
    decision_checker = load_decision_checker()
    decision_check = decision_checker.validate_decision_template(
        decision_template,
        patch_preview,
        decision_template_path,
        patch_preview_path,
    )

    decision = str(decision_check.get("decision", "missing"))
    approved_preview_count = int(decision_check.get("approved_preview_count", 0))
    decision_allows_application = decision_check.get("authorizes_application") is True
    decision_blocking_reason = (
        ""
        if decision_allows_application
        else (
            "report source edit application needs human/PMO approval and a valid decision check; "
            f"current decision={decision}"
        )
    )

    gates: list[dict[str, Any]] = []
    gates.append(
        gate(
            "patch_preview_checker_ok",
            bool(patch_preview_check.get("ok") is True),
            rel(patch_preview_check_path),
            "" if patch_preview_check.get("ok") is True else "patch preview checker has issues",
            "fix patch preview anchors/non-applying boundaries",
        )
    )
    gates.append(
        gate(
            "patch_preview_is_non_applying",
            patch_preview.get("status") == "draft_patch_preview_not_report_edit"
            and patch_preview.get("summary", {}).get("edits_report_source") is False,
            rel(patch_preview_path),
            "" if patch_preview.get("status") == "draft_patch_preview_not_report_edit" else "patch preview status drifted",
            "regenerate patch preview and keep applies_patch_now=false",
        )
    )
    gates.append(
        gate(
            "human_pmo_apply_approval_present",
            decision_allows_application,
            rel(decision_check_path),
            decision_blocking_reason,
            "obtain explicit approval before applying preview snippets to Docs/simulation_report.md",
        )
    )
    gates.append(
        gate(
            "report_source_edit_decision_check_ok",
            decision_check.get("ok") is True,
            rel(decision_check_path),
            "" if decision_check.get("ok") is True else "; ".join(decision_check.get("issues", [])),
            "fix report-source decision artifact before using it for source edits",
        )
    )
    gates.append(
        gate(
            "final_packaging_still_not_ready_boundary",
            final_packaging_gap.get("summary", {}).get("final_submission_ready") is False,
            rel(final_packaging_gap_path),
            "",
            "keep final submission readiness blocked until final PDF/video/acceptance artifacts exist",
        )
    )
    gates.append(
        gate(
            "outline_gap_requires_review_boundary",
            outline_gap.get("summary", {}).get("human_or_live_review_section_count", 0) > 0,
            rel(outline_gap_path),
            "",
            "review human/live sections before final report freeze",
        )
    )
    gates.append(
        gate(
            "rewrite_plan_is_draft_only",
            rewrite_plan.get("status") == "draft_rewrite_plan_not_final_report_acceptance",
            rel(rewrite_plan_path),
            "" if rewrite_plan.get("status") == "draft_rewrite_plan_not_final_report_acceptance" else "rewrite plan status drifted",
            "keep rewrite plan draft-only until accepted by report reviewer",
        )
    )

    blocking_gates = [
        item
        for item in gates
        if not item["ok"] or item["gate_id"] in {"human_pmo_apply_approval_present"}
    ]
    safe_to_apply_now = not blocking_gates
    return {
        "gate_id": "simulation_report_source_edit_readiness_20260610",
        "status": "source_edit_application_blocked_pending_human_review",
        "inputs": {
            "simulation_report_patch_preview_check": rel(patch_preview_check_path),
            "simulation_report_patch_preview": rel(patch_preview_path),
            "final_packaging_gap_inventory": rel(final_packaging_gap_path),
            "final_report_outline_gap_inventory": rel(outline_gap_path),
            "final_report_unmapped_claim_rewrite_plan": rel(rewrite_plan_path),
            "report_source_edit_decision_template": rel(decision_template_path),
            "report_source_edit_decision_check": rel(decision_check_path),
        },
        "summary": {
            "gate_count": len(gates),
            "blocking_gate_count": len(blocking_gates),
            "safe_to_apply_report_source_edits_now": safe_to_apply_now,
            "decision": decision,
            "approved_preview_count": approved_preview_count,
            "decision_check_ok": decision_check.get("ok") is True,
            "decision_authorizes_application": decision_allows_application,
            "edits_report_source": False,
            "deletes_content": False,
            "final_acceptance": False,
        },
        "gates": gates,
        "blocking_gates": blocking_gates,
        "decision_check": decision_check,
        "decision": (
            "Do not apply preview snippets to Docs/simulation_report.md in this run. "
            "The preview is valid as a review artifact, but source-edit application still needs explicit human/PMO approval."
        ),
        "claim_boundary": [
            "This gate does not edit Docs/simulation_report.md.",
            "It does not authorize automatic patch application.",
            "It does not generate final PDFs/video or PMO final acceptance.",
            "It keeps final submission readiness blocked while final artifacts are missing.",
        ],
    }


def write_markdown(readiness: dict[str, Any], path: Path) -> None:
    summary = readiness["summary"]
    lines = [
        "# Simulation Report Source Edit Readiness Gate, 2026-06-10",
        "",
        f"Status: `{readiness['status']}`",
        "",
        "## Summary",
        "",
        f"- Gates: `{summary['gate_count']}`",
        f"- Blocking gates: `{summary['blocking_gate_count']}`",
        f"- Safe to apply report source edits now: `{summary['safe_to_apply_report_source_edits_now']}`",
        f"- Decision: `{summary['decision']}`",
        f"- Approved preview count: `{summary['approved_preview_count']}`",
        f"- Decision check OK: `{summary['decision_check_ok']}`",
        f"- Decision authorizes application: `{summary['decision_authorizes_application']}`",
        f"- Edits report source: `{summary['edits_report_source']}`",
        f"- Deletes content: `{summary['deletes_content']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Decision",
        "",
        readiness["decision"],
        "",
        "## Gates",
        "",
    ]
    for item in readiness["gates"]:
        lines.extend(
            [
                f"### {item['gate_id']}",
                "",
                f"- OK: `{item['ok']}`",
                f"- Evidence: {item['evidence']}",
                f"- Blocking reason: {item['blocking_reason']}",
                f"- Needed action: {item['needed_action']}",
                "",
            ]
        )
    lines.extend(["## Claim Boundary", ""])
    for item in readiness["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--patch-preview-check", default=str(DEFAULT_PATCH_PREVIEW_CHECK.relative_to(ROOT)))
    parser.add_argument("--patch-preview", default=str(DEFAULT_PATCH_PREVIEW.relative_to(ROOT)))
    parser.add_argument("--final-packaging-gap", default=str(DEFAULT_FINAL_PACKAGING_GAP.relative_to(ROOT)))
    parser.add_argument("--outline-gap", default=str(DEFAULT_OUTLINE_GAP.relative_to(ROOT)))
    parser.add_argument("--rewrite-plan", default=str(DEFAULT_REWRITE_PLAN.relative_to(ROOT)))
    parser.add_argument("--decision-template", default=str(DEFAULT_DECISION_TEMPLATE.relative_to(ROOT)))
    parser.add_argument("--decision-check", default=str(DEFAULT_DECISION_CHECK.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    readiness = build_gate(
        repo_path(args.patch_preview_check),
        repo_path(args.patch_preview),
        repo_path(args.final_packaging_gap),
        repo_path(args.outline_gap),
        repo_path(args.rewrite_plan),
        repo_path(args.decision_template),
        repo_path(args.decision_check),
    )
    decision_check_path = repo_path(args.decision_check)
    decision_check_path.parent.mkdir(parents=True, exist_ok=True)
    decision_check_path.write_text(
        json.dumps(readiness["decision_check"], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    json_path = output_dir / "simulation_report_source_edit_readiness_gate.json"
    md_path = output_dir / "simulation_report_source_edit_readiness_gate.md"
    json_path.write_text(json.dumps(readiness, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(readiness, md_path)

    result = {
        "ok": True,
        "readiness_json": rel(json_path),
        "readiness_markdown": rel(md_path),
        "safe_to_apply_report_source_edits_now": readiness["summary"]["safe_to_apply_report_source_edits_now"],
        "blocking_gate_count": readiness["summary"]["blocking_gate_count"],
        "decision": readiness["summary"]["decision"],
        "approved_preview_count": readiness["summary"]["approved_preview_count"],
        "decision_check_ok": readiness["summary"]["decision_check_ok"],
        "decision_authorizes_application": readiness["summary"]["decision_authorizes_application"],
        "edits_report_source": readiness["summary"]["edits_report_source"],
        "final_acceptance": readiness["summary"]["final_acceptance"],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
