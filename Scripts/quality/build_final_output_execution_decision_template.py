#!/usr/bin/env python3
"""Build a pending final-output execution decision template.

The template records the future human/PMO decision surface for PDF export,
demo-video recording, and canonical final acceptance. It never executes those
actions.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_output_execution_decision_20260610"
DEFAULT_PDF_PLAN = ROOT / "Results/static_audits/pdf_export_dry_run_plan_20260610/pdf_export_dry_run_plan.json"
DEFAULT_VIDEO_PLAN = ROOT / "Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.json"
DEFAULT_ACCEPTANCE_PREREQ = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_acceptance_packet_prereq_20260610"
    / "final_acceptance_packet_prereq_plan.json"
)
DECISION_CHECKER = ROOT / "Scripts/quality/check_final_output_execution_decision.py"
CANONICAL_DECISION_PATH = (
    "Results/static_audits/final_output_execution_decision_20260610/"
    "final_output_execution_decision.template.json"
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
    spec = importlib.util.spec_from_file_location("check_final_output_execution_decision", DECISION_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_final_output_execution_decision.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pending_action(action_id: str, description: str) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "decision": "pending_review",
        "approved": False,
        "approved_by": "<user_or_PMO>",
        "approved_at": "<ISO8601_after_review>",
        "description": description,
        "review_notes": "",
    }


def build_template(
    pdf_plan_path: Path,
    video_plan_path: Path,
    acceptance_prereq_path: Path,
) -> dict[str, Any]:
    return {
        "decision_id": "final_output_execution_decision_20260610",
        "status": "execution_decision_template_pending_review",
        "applies_to": {
            "pdf_export_dry_run_plan": rel(pdf_plan_path),
            "demo_video_storyboard_plan": rel(video_plan_path),
            "final_acceptance_packet_prereq_plan": rel(acceptance_prereq_path),
        },
        "actions": {
            "pdf_export": pending_action(
                "pdf_export",
                "Run approved Pandoc commands and create final PDF outputs.",
            ),
            "demo_video_recording": pending_action(
                "demo_video_recording",
                "Record or render the reviewed demo video artifact.",
            ),
            "final_acceptance_packet": pending_action(
                "final_acceptance_packet",
                "Write canonical PMO final submission acceptance packet.",
            ),
        },
        "execution_flags": {
            "creates_submission_dir_now": False,
            "runs_pandoc_now": False,
            "records_or_renders_video_now": False,
            "writes_canonical_acceptance_packet_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "required_boundaries": [
            "Do not create Results/submission unless final-output execution is explicitly approved and upstream gates pass.",
            "Do not run Pandoc unless pdf_export is approved and pdf_export_plan.safe_to_run_pdf_export_now=true.",
            "Do not record or render demo video unless demo_video_recording is approved and storyboard gate permits it.",
            "Do not write canonical PMO final acceptance unless final_acceptance_packet is approved and prerequisite gate permits it.",
            "Do not claim final submission ready until final artifact manifest passes and PMO accepts it.",
        ],
    }


def build_artifact(
    pdf_plan_path: Path,
    video_plan_path: Path,
    acceptance_prereq_path: Path,
) -> dict[str, Any]:
    template = build_template(pdf_plan_path, video_plan_path, acceptance_prereq_path)
    checker = load_decision_checker()
    validation = checker.validate_decision(
        template,
        read_json(pdf_plan_path),
        read_json(video_plan_path),
        read_json(acceptance_prereq_path),
        repo_path(CANONICAL_DECISION_PATH),
    )
    return {
        "artifact_id": "final_output_execution_decision_template_20260610",
        "status": "execution_decision_template_pending_review_not_execution",
        "canonical_template_path": CANONICAL_DECISION_PATH,
        "summary": {
            "action_count": len(template["actions"]),
            "pending_action_count": sum(
                1 for action in template["actions"].values() if action["decision"] == "pending_review"
            ),
            "authorizes_pdf_export": validation["summary"]["authorizes_pdf_export"],
            "authorizes_demo_video_recording": validation["summary"]["authorizes_demo_video_recording"],
            "authorizes_final_acceptance_packet": validation["summary"][
                "authorizes_final_acceptance_packet"
            ],
            "creates_submission_dir_now": False,
            "runs_pandoc_now": False,
            "records_or_renders_video_now": False,
            "writes_canonical_acceptance_packet_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "template": template,
        "validation": validation,
        "claim_boundary": [
            "This artifact is a pending decision template only.",
            "It does not create Results/submission.",
            "It does not run Pandoc.",
            "It does not record or render demo video.",
            "It does not write canonical PMO final acceptance.",
        ],
    }


def write_markdown(artifact: dict[str, Any], path: Path) -> None:
    summary = artifact["summary"]
    validation = artifact["validation"]
    lines = [
        "# Final Output Execution Decision Template, 2026-06-10",
        "",
        f"Status: `{artifact['status']}`",
        "",
        "## Summary",
        "",
        f"- Actions: `{summary['action_count']}`",
        f"- Pending actions: `{summary['pending_action_count']}`",
        f"- Authorizes PDF export: `{summary['authorizes_pdf_export']}`",
        f"- Authorizes demo video recording: `{summary['authorizes_demo_video_recording']}`",
        f"- Authorizes final acceptance packet: `{summary['authorizes_final_acceptance_packet']}`",
        f"- Creates submission dir now: `{summary['creates_submission_dir_now']}`",
        f"- Runs Pandoc now: `{summary['runs_pandoc_now']}`",
        f"- Records or renders video now: `{summary['records_or_renders_video_now']}`",
        f"- Writes canonical acceptance packet now: `{summary['writes_canonical_acceptance_packet_now']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Validation",
        "",
        f"- OK: `{validation['ok']}`",
        f"- Status: `{validation['status']}`",
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
    parser.add_argument("--pdf-plan", default=str(DEFAULT_PDF_PLAN.relative_to(ROOT)))
    parser.add_argument("--video-plan", default=str(DEFAULT_VIDEO_PLAN.relative_to(ROOT)))
    parser.add_argument("--acceptance-prereq", default=str(DEFAULT_ACCEPTANCE_PREREQ.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact = build_artifact(
        repo_path(args.pdf_plan),
        repo_path(args.video_plan),
        repo_path(args.acceptance_prereq),
    )
    json_path = output_dir / "final_output_execution_decision_template.json"
    md_path = output_dir / "final_output_execution_decision_template.md"
    template_path = output_dir / "final_output_execution_decision.template.json"
    check_path = output_dir / "final_output_execution_decision_check.json"
    json_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    template_path.write_text(json.dumps(artifact["template"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    check_path.write_text(json.dumps(artifact["validation"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(artifact, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "artifact_json": rel(json_path),
                "artifact_markdown": rel(md_path),
                "template": rel(template_path),
                "decision_check": rel(check_path),
                "authorizes_pdf_export": artifact["summary"]["authorizes_pdf_export"],
                "authorizes_demo_video_recording": artifact["summary"]["authorizes_demo_video_recording"],
                "authorizes_final_acceptance_packet": artifact["summary"][
                    "authorizes_final_acceptance_packet"
                ],
                "final_acceptance": artifact["summary"]["final_acceptance"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
