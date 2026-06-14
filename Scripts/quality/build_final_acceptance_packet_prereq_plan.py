#!/usr/bin/env python3
"""Build a blocked final-acceptance packet prerequisite plan.

This script creates a reviewable draft template and prerequisite report for the
future PMO final submission acceptance packet. It never writes the canonical
final acceptance packet.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT_MANIFEST = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_artifacts_20260610"
    / "final_submission_artifact_manifest_check.json"
)
DEFAULT_SOURCE_OUTPUT_READINESS = (
    ROOT
    / "Results"
    / "static_audits"
    / "submission_source_output_readiness_20260610"
    / "submission_source_output_readiness.json"
)
DEFAULT_PDF_PLAN = (
    ROOT
    / "Results"
    / "static_audits"
    / "pdf_export_dry_run_plan_20260610"
    / "pdf_export_dry_run_plan.json"
)
DEFAULT_VIDEO_PLAN = (
    ROOT
    / "Results"
    / "static_audits"
    / "demo_video_storyboard_plan_20260610"
    / "demo_video_storyboard_plan.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "static_audits" / "final_acceptance_packet_prereq_20260610"
CANONICAL_ACCEPTANCE_PACKET = "Results/agent_packets/returns/PMO-FINAL-SUBMISSION-ACCEPTANCE.json"

REQUIRED_ARTIFACTS = [
    "user_manual_pdf",
    "simulation_analysis_report_pdf",
    "demo_video",
    "final_acceptance_packet",
]

REQUIRED_ACCEPTANCE_FIELDS = [
    "packet_type",
    "request_id",
    "status",
    "accepted_by",
    "accepted_at",
    "final_submission",
    "accepted_artifacts",
    "evidence_inputs",
    "claim_boundaries_checked",
    "manual_review_notes",
    "remaining_risks",
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


def build_template(
    artifact_manifest_path: Path,
    source_output_readiness_path: Path,
    pdf_plan_path: Path,
    video_plan_path: Path,
) -> dict[str, Any]:
    return {
        "packet_type": "return",
        "request_id": "PMO-FINAL-SUBMISSION-ACCEPTANCE",
        "status": "draft_template_not_final_acceptance",
        "accepted_by": "<PMO_or_user_after_manual_review>",
        "accepted_at": "<ISO8601_after_manual_review>",
        "final_submission": {
            "accepted": False,
            "canonical_packet_path": CANONICAL_ACCEPTANCE_PACKET,
            "must_not_write_until_prereqs_pass": True,
        },
        "accepted_artifacts": {
            "user_manual_pdf": "Results/submission/user_manual.pdf",
            "simulation_analysis_report_pdf": "Results/submission/simulation_analysis_report.pdf",
            "demo_video": "Results/submission/demo_video.mp4",
        },
        "evidence_inputs": {
            "final_submission_artifact_manifest": rel(artifact_manifest_path),
            "submission_source_output_readiness": rel(source_output_readiness_path),
            "pdf_export_dry_run_plan": rel(pdf_plan_path),
            "demo_video_storyboard_plan": rel(video_plan_path),
        },
        "claim_boundaries_checked": [
            "No final PMO acceptance before PDFs, demo video, and review evidence exist.",
            "No planner_ready or closed_loop claim without separate ROS2/runtime evidence.",
            "No UE build/runtime/editor success claim without separate UE evidence.",
            "No native Syslab complete report generation claim without separate evidence.",
        ],
        "manual_review_notes": [
            "<confirm final PDFs match reviewed source>",
            "<confirm demo video follows reviewed storyboard and avoids forbidden claims>",
            "<confirm final artifact manifest passes without --allow-missing>",
        ],
        "remaining_risks": [],
    }


def build_plan(
    artifact_manifest_path: Path,
    source_output_readiness_path: Path,
    pdf_plan_path: Path,
    video_plan_path: Path,
) -> dict[str, Any]:
    artifact_manifest = read_json(artifact_manifest_path)
    source_output_readiness = read_json(source_output_readiness_path)
    pdf_plan = read_json(pdf_plan_path)
    video_plan = read_json(video_plan_path)

    artifacts = artifact_manifest.get("artifacts", {})
    missing = [
        name
        for name in REQUIRED_ARTIFACTS
        if not isinstance(artifacts.get(name), dict) or not artifacts[name].get("ok")
    ]
    safe_to_write_source = (
        source_output_readiness.get("summary", {}).get("safe_to_write_final_acceptance_now") is True
    )
    pdf_export_ready = pdf_plan.get("summary", {}).get("safe_to_run_pdf_export_now") is True
    video_record_ready = video_plan.get("summary", {}).get("safe_to_record_demo_video_now") is True
    final_artifacts_ready = artifact_manifest.get("summary", {}).get("final_submission_artifacts_ready") is True
    canonical_packet_exists = repo_path(CANONICAL_ACCEPTANCE_PACKET).exists()

    blockers: list[dict[str, str]] = []
    if missing:
        blockers.append(
            {
                "blocker_id": "final_artifacts_not_ready",
                "reason": "one or more final artifacts are missing or failing",
                "needed_action": "create reviewed final PDFs and demo video, then rerun artifact manifest without --allow-missing",
            }
        )
    if not pdf_export_ready:
        blockers.append(
            {
                "blocker_id": "pdf_export_not_ready",
                "reason": "PDF export dry-run plan does not permit final PDF export yet",
                "needed_action": "satisfy PDF engine, report-source approval, and final export gates",
            }
        )
    if not video_record_ready:
        blockers.append(
            {
                "blocker_id": "demo_video_recording_not_approved",
                "reason": "storyboard plan does not permit video recording yet",
                "needed_action": "manually review storyboard and authorize recording or rendering",
            }
        )
    if not safe_to_write_source:
        blockers.append(
            {
                "blocker_id": "source_output_readiness_blocks_acceptance",
                "reason": "source-output readiness does not permit writing final acceptance",
                "needed_action": "complete final artifacts and source-output readiness gates first",
            }
        )

    safe_to_write_final_acceptance_packet_now = (
        final_artifacts_ready
        and safe_to_write_source
        and canonical_packet_exists
    )

    template = build_template(
        artifact_manifest_path,
        source_output_readiness_path,
        pdf_plan_path,
        video_plan_path,
    )

    return {
        "plan_id": "final_acceptance_packet_prereq_plan_20260610",
        "status": "blocked_template_not_final_acceptance",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "canonical_acceptance_packet_path": CANONICAL_ACCEPTANCE_PACKET,
        "inputs": {
            "final_submission_artifact_manifest": rel(artifact_manifest_path),
            "submission_source_output_readiness": rel(source_output_readiness_path),
            "pdf_export_dry_run_plan": rel(pdf_plan_path),
            "demo_video_storyboard_plan": rel(video_plan_path),
        },
        "summary": {
            "required_field_count": len(REQUIRED_ACCEPTANCE_FIELDS),
            "missing_or_failing_final_artifact_count": len(missing),
            "final_artifacts_ready": final_artifacts_ready,
            "pdf_export_ready": pdf_export_ready,
            "demo_video_recording_ready": video_record_ready,
            "source_output_allows_final_acceptance": safe_to_write_source,
            "canonical_acceptance_packet_exists": canonical_packet_exists,
            "safe_to_write_final_acceptance_packet_now": safe_to_write_final_acceptance_packet_now,
            "writes_canonical_acceptance_packet_now": False,
            "final_acceptance": False,
        },
        "required_fields": REQUIRED_ACCEPTANCE_FIELDS,
        "missing_or_failing_final_artifacts": missing,
        "draft_template": template,
        "blockers": blockers,
        "claim_boundary": [
            "This artifact is a prerequisite plan and draft template only.",
            "It does not write the canonical PMO final acceptance packet.",
            "It does not accept final submission.",
            "It does not create PDFs or demo video.",
        ],
    }


def write_markdown(plan: dict[str, Any], path: Path) -> None:
    summary = plan["summary"]
    lines = [
        "# Final Acceptance Packet Prerequisite Plan, 2026-06-10",
        "",
        f"Status: `{plan['status']}`",
        "",
        "## Summary",
        "",
        f"- Required fields: `{summary['required_field_count']}`",
        f"- Missing or failing final artifacts: `{summary['missing_or_failing_final_artifact_count']}`",
        f"- Final artifacts ready: `{summary['final_artifacts_ready']}`",
        f"- PDF export ready: `{summary['pdf_export_ready']}`",
        f"- Demo video recording ready: `{summary['demo_video_recording_ready']}`",
        f"- Source output allows final acceptance: `{summary['source_output_allows_final_acceptance']}`",
        f"- Canonical acceptance packet exists: `{summary['canonical_acceptance_packet_exists']}`",
        f"- Safe to write final acceptance packet now: `{summary['safe_to_write_final_acceptance_packet_now']}`",
        f"- Writes canonical acceptance packet now: `{summary['writes_canonical_acceptance_packet_now']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in plan["claim_boundary"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Required Fields", ""])
    for field in plan["required_fields"]:
        lines.append(f"- `{field}`")

    lines.extend(["", "## Missing Or Failing Final Artifacts", ""])
    if plan["missing_or_failing_final_artifacts"]:
        for item in plan["missing_or_failing_final_artifacts"]:
            lines.append(f"- `{item}`")
    else:
        lines.append("- None.")

    lines.extend(["", "## Blockers", ""])
    if plan["blockers"]:
        for blocker in plan["blockers"]:
            lines.append(
                f"- `{blocker['blocker_id']}`: {blocker['reason']} Needed action: {blocker['needed_action']}"
            )
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Draft Template",
            "",
            "```json",
            json.dumps(plan["draft_template"], ensure_ascii=False, indent=2),
            "```",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-manifest", default=str(DEFAULT_ARTIFACT_MANIFEST.relative_to(ROOT)))
    parser.add_argument("--source-output-readiness", default=str(DEFAULT_SOURCE_OUTPUT_READINESS.relative_to(ROOT)))
    parser.add_argument("--pdf-plan", default=str(DEFAULT_PDF_PLAN.relative_to(ROOT)))
    parser.add_argument("--video-plan", default=str(DEFAULT_VIDEO_PLAN.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    plan = build_plan(
        repo_path(args.artifact_manifest),
        repo_path(args.source_output_readiness),
        repo_path(args.pdf_plan),
        repo_path(args.video_plan),
    )
    json_path = output_dir / "final_acceptance_packet_prereq_plan.json"
    md_path = output_dir / "final_acceptance_packet_prereq_plan.md"
    template_path = output_dir / "PMO-FINAL-SUBMISSION-ACCEPTANCE.draft-template.json"
    json_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(plan, md_path)
    template_path.write_text(json.dumps(plan["draft_template"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "ok": True,
                "plan_json": rel(json_path),
                "plan_markdown": rel(md_path),
                "draft_template": rel(template_path),
                "safe_to_write_final_acceptance_packet_now": plan["summary"]["safe_to_write_final_acceptance_packet_now"],
                "writes_canonical_acceptance_packet_now": plan["summary"]["writes_canonical_acceptance_packet_now"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
