#!/usr/bin/env python3
"""Check static final-submission readiness artifact chain integrity.

This verifies that downstream readiness artifacts consume the expected upstream
artifact paths and preserve blocked/not-final boundaries. It does not generate
or approve final outputs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_JSON = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_readiness_chain_20260610"
    / "final_submission_readiness_chain_check.json"
)
DEFAULT_OUTPUT_MD = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_readiness_chain_20260610"
    / "final_submission_readiness_chain_check.md"
)

PATHS = {
    "final_packaging_gap": "Results/static_audits/final_packaging_gap_20260610/final_packaging_gap_inventory.json",
    "source_edit_readiness": "Results/static_audits/simulation_report_source_edit_readiness_20260610/simulation_report_source_edit_readiness_gate.json",
    "source_edit_application_plan": "Results/static_audits/simulation_report_source_edit_application_plan_20260610/simulation_report_source_edit_application_plan.json",
    "source_output_readiness": "Results/static_audits/submission_source_output_readiness_20260610/submission_source_output_readiness.json",
    "final_artifact_manifest": "Results/static_audits/final_submission_artifacts_20260610/final_submission_artifact_manifest_check.json",
    "pdf_export_plan": "Results/static_audits/pdf_export_dry_run_plan_20260610/pdf_export_dry_run_plan.json",
    "demo_video_storyboard": "Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.json",
    "final_acceptance_prereq": "Results/static_audits/final_acceptance_packet_prereq_20260610/final_acceptance_packet_prereq_plan.json",
    "final_output_execution_decision": "Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision_check.json",
    "dashboard": "Results/static_audits/final_submission_readiness_dashboard_20260610/final_submission_readiness_dashboard.json",
    "human_action_checklist": "Results/static_audits/final_submission_human_action_checklist_20260610/final_submission_human_action_checklist.json",
    "reviewer_action_map": "Results/static_audits/final_submission_reviewer_action_map_20260610/final_submission_reviewer_action_map.json",
    "human_review_decision_packet": "Results/static_audits/final_submission_human_review_decision_packet_20260610/final_submission_human_review_decision_packet_check.json",
}

EXPECTED_STATUSES = {
    "source_edit_readiness": "source_edit_application_blocked_pending_human_review",
    "source_edit_application_plan": "source_edit_application_plan_blocked_pending_human_review",
    "source_output_readiness": "static_source_output_readiness_not_final_submission",
    "final_artifact_manifest": "final_artifacts_missing_not_final_submission",
    "pdf_export_plan": "dry_run_pdf_export_plan_not_final_output",
    "demo_video_storyboard": "storyboard_plan_not_demo_video_acceptance",
    "final_acceptance_prereq": "blocked_template_not_final_acceptance",
    "final_output_execution_decision": "execution_decision_check_not_execution",
    "dashboard": "static_dashboard_not_final_submission_acceptance",
    "human_action_checklist": "human_action_checklist_not_execution",
    "reviewer_action_map": "reviewer_action_map_not_execution",
    "human_review_decision_packet": "human_review_decision_packet_check_not_execution",
}

EXPECTED_DASHBOARD_GATES = {
    "final_packaging_gap",
    "source_output_readiness",
    "final_artifact_manifest",
    "pdf_export_plan",
    "demo_video_storyboard",
    "final_acceptance_prereq",
    "final_output_execution_decision",
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


def get_summary(data: dict[str, Any]) -> dict[str, Any]:
    summary = data.get("summary", {})
    return summary if isinstance(summary, dict) else {}


def require(condition: bool, issues: list[str], message: str) -> None:
    if not condition:
        issues.append(message)


def validate_chain(paths: dict[str, str] = PATHS) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    artifacts: dict[str, dict[str, Any]] = {}

    for artifact_id, path_value in paths.items():
        path = repo_path(path_value)
        if not path.exists():
            issues.append(f"missing artifact {artifact_id}: {path_value}")
            artifacts[artifact_id] = {}
            continue
        try:
            artifacts[artifact_id] = read_json(path)
        except Exception as exc:
            issues.append(f"cannot read artifact {artifact_id}: {exc}")
            artifacts[artifact_id] = {}

    for artifact_id, expected_status in EXPECTED_STATUSES.items():
        actual = artifacts.get(artifact_id, {}).get("status")
        require(
            actual == expected_status,
            issues,
            f"{artifact_id} status must be {expected_status}, got {actual}",
        )

    source_output = artifacts.get("source_output_readiness", {})
    source_output_inputs = source_output.get("inputs", {})
    require(
        isinstance(source_output_inputs, dict)
        and source_output_inputs.get("final_packaging_gap_inventory") == paths["final_packaging_gap"],
        issues,
        "source_output_readiness must consume final_packaging_gap_inventory",
    )
    require(
        isinstance(source_output_inputs, dict)
        and source_output_inputs.get("simulation_report_source_edit_readiness_gate") == paths["source_edit_readiness"],
        issues,
        "source_output_readiness must consume simulation_report_source_edit_readiness_gate",
    )
    require(
        isinstance(source_output_inputs, dict)
        and source_output_inputs.get("simulation_report_source_edit_application_plan")
        == paths["source_edit_application_plan"],
        issues,
        "source_output_readiness must consume simulation_report_source_edit_application_plan",
    )

    pdf_plan = artifacts.get("pdf_export_plan", {})
    pdf_inputs = pdf_plan.get("inputs", {})
    require(
        isinstance(pdf_inputs, dict)
        and pdf_inputs.get("submission_source_output_readiness") == paths["source_output_readiness"],
        issues,
        "pdf_export_plan must consume submission_source_output_readiness",
    )
    require(
        isinstance(pdf_inputs, dict)
        and pdf_inputs.get("final_submission_artifact_manifest") == paths["final_artifact_manifest"],
        issues,
        "pdf_export_plan must consume final_submission_artifact_manifest",
    )

    dashboard = artifacts.get("dashboard", {})
    gates = dashboard.get("gates", {})
    require(isinstance(gates, dict), issues, "dashboard.gates must be an object")
    if isinstance(gates, dict):
        require(
            set(gates) == EXPECTED_DASHBOARD_GATES,
            issues,
            "dashboard gate set mismatch: " + ", ".join(sorted(set(gates))),
        )
        expected_gate_paths = {
            "final_packaging_gap": paths["final_packaging_gap"],
            "source_output_readiness": paths["source_output_readiness"],
            "final_artifact_manifest": paths["final_artifact_manifest"],
            "pdf_export_plan": paths["pdf_export_plan"],
            "demo_video_storyboard": paths["demo_video_storyboard"],
            "final_acceptance_prereq": paths["final_acceptance_prereq"],
            "final_output_execution_decision": paths["final_output_execution_decision"],
        }
        for gate_id, expected_path in expected_gate_paths.items():
            gate = gates.get(gate_id, {})
            require(
                isinstance(gate, dict) and gate.get("path") == expected_path,
                issues,
                f"dashboard gate {gate_id} path must be {expected_path}",
            )
            require(
                isinstance(gate, dict) and gate.get("ready") is False,
                issues,
                f"dashboard gate {gate_id} must remain ready=false in current static state",
            )

    checklist = artifacts.get("human_action_checklist", {})
    require(
        checklist.get("source_dashboard") == paths["dashboard"],
        issues,
        "human_action_checklist must consume final_submission_readiness_dashboard",
    )
    reviewer_action_map = artifacts.get("reviewer_action_map", {})
    require(
        reviewer_action_map.get("source_checklist") == paths["human_action_checklist"],
        issues,
        "reviewer_action_map must consume final_submission_human_action_checklist",
    )
    human_review_decision_packet = artifacts.get("human_review_decision_packet", {})
    require(
        get_summary(human_review_decision_packet).get("decision_count") == 3,
        issues,
        "human_review_decision_packet must include three review decisions",
    )
    require(
        get_summary(human_review_decision_packet).get("pending_decision_count") == 3,
        issues,
        "human_review_decision_packet must keep all three decisions pending",
    )

    blocked_flags = {
        "source_edit_readiness.safe_to_apply_report_source_edits_now": get_summary(
            artifacts.get("source_edit_readiness", {})
        ).get("safe_to_apply_report_source_edits_now"),
        "source_edit_application_plan.safe_to_apply_report_source_edits_now": get_summary(
            artifacts.get("source_edit_application_plan", {})
        ).get("safe_to_apply_report_source_edits_now"),
        "source_edit_application_plan.edits_report_source": get_summary(
            artifacts.get("source_edit_application_plan", {})
        ).get("edits_report_source"),
        "source_output_readiness.source_edit_application_plan_applied": get_summary(source_output).get(
            "source_edit_application_plan_applied"
        ),
        "source_output_readiness.safe_to_export_final_pdfs_now": get_summary(
            source_output
        ).get("safe_to_export_final_pdfs_now"),
        "source_output_readiness.generates_final_outputs": get_summary(source_output).get(
            "generates_final_outputs"
        ),
        "pdf_export_plan.safe_to_run_pdf_export_now": get_summary(pdf_plan).get("safe_to_run_pdf_export_now"),
        "pdf_export_plan.runs_pandoc_now": get_summary(pdf_plan).get("runs_pandoc_now"),
        "pdf_export_plan.generates_final_outputs": get_summary(pdf_plan).get("generates_final_outputs"),
        "dashboard.final_submission_ready": get_summary(dashboard).get("final_submission_ready"),
        "dashboard.final_acceptance": get_summary(dashboard).get("final_acceptance"),
        "human_action_checklist.automated_execution_allowed": get_summary(checklist).get(
            "automated_execution_allowed"
        ),
        "human_action_checklist.final_acceptance": get_summary(checklist).get("final_acceptance"),
        "reviewer_action_map.automated_execution_allowed": get_summary(reviewer_action_map).get(
            "automated_execution_allowed"
        ),
        "reviewer_action_map.generates_final_outputs": get_summary(reviewer_action_map).get("generates_final_outputs"),
        "reviewer_action_map.final_acceptance": get_summary(reviewer_action_map).get("final_acceptance"),
        "human_review_decision_packet.automated_execution_allowed": get_summary(human_review_decision_packet).get(
            "automated_execution_allowed"
        ),
        "human_review_decision_packet.generates_final_outputs": get_summary(human_review_decision_packet).get(
            "generates_final_outputs"
        ),
        "human_review_decision_packet.final_acceptance": get_summary(human_review_decision_packet).get(
            "final_acceptance"
        ),
    }
    for flag_name, actual in blocked_flags.items():
        require(actual is False, issues, f"{flag_name} must be false, got {actual}")

    dashboard_summary = get_summary(dashboard)
    checklist_summary = get_summary(checklist)
    require(
        dashboard_summary.get("blocking_gate_count") == 7,
        issues,
        "dashboard blocking_gate_count must remain 7 in current static state",
    )
    require(
        checklist_summary.get("source_blocker_count") == dashboard_summary.get("blocker_count"),
        issues,
        "human checklist source_blocker_count must match dashboard blocker_count",
    )

    return {
        "ok": not issues,
        "check_id": "final_submission_readiness_chain_20260610",
        "status": "static_chain_check_not_final_submission",
        "artifacts": paths,
        "summary": {
            "artifact_count": len(paths),
            "issue_count": len(issues),
            "warning_count": len(warnings),
            "dashboard_blocking_gate_count": dashboard_summary.get("blocking_gate_count"),
            "dashboard_blocker_count": dashboard_summary.get("blocker_count"),
            "human_action_count": checklist_summary.get("action_count"),
            "reviewer_action_count": get_summary(reviewer_action_map).get("action_count"),
            "human_review_decision_count": get_summary(human_review_decision_packet).get("decision_count"),
            "final_submission_ready": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "issues": issues,
        "warnings": warnings,
        "claim_boundary": [
            "This checker validates static readiness artifact chaining only.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
            "It does not edit report or manual source documents.",
        ],
    }


def write_markdown(result: dict[str, Any], path: Path) -> None:
    summary = result["summary"]
    lines = [
        "# Final Submission Readiness Chain Check, 2026-06-10",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Summary",
        "",
        f"- OK: `{result['ok']}`",
        f"- Artifacts: `{summary['artifact_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- Warnings: `{summary['warning_count']}`",
        f"- Dashboard blocking gates: `{summary['dashboard_blocking_gate_count']}`",
        f"- Dashboard blockers: `{summary['dashboard_blocker_count']}`",
        f"- Human actions: `{summary['human_action_count']}`",
        f"- Final submission ready: `{summary['final_submission_ready']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Artifacts",
        "",
    ]
    for artifact_id, path_value in result["artifacts"].items():
        lines.append(f"- `{artifact_id}`: `{path_value}`")
    lines.extend(["", "## Issues", ""])
    if result["issues"]:
        for item in result["issues"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in result["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON.relative_to(ROOT)))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD.relative_to(ROOT)))
    args = parser.parse_args()

    result = validate_chain()
    output_json = repo_path(args.output_json)
    output_md = repo_path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(result, output_md)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
