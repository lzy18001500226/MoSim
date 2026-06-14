#!/usr/bin/env python3
"""Build a static final-submission readiness dashboard.

The dashboard aggregates current static gates. It does not generate final
artifacts and does not approve final submission.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUTS = {
    "final_packaging_gap": ROOT / "Results/static_audits/final_packaging_gap_20260610/final_packaging_gap_inventory.json",
    "source_output_readiness": ROOT / "Results/static_audits/submission_source_output_readiness_20260610/submission_source_output_readiness.json",
    "final_artifact_manifest": ROOT / "Results/static_audits/final_submission_artifacts_20260610/final_submission_artifact_manifest_check.json",
    "pdf_export_plan": ROOT / "Results/static_audits/pdf_export_dry_run_plan_20260610/pdf_export_dry_run_plan.json",
    "demo_video_storyboard": ROOT / "Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.json",
    "final_acceptance_prereq": ROOT / "Results/static_audits/final_acceptance_packet_prereq_20260610/final_acceptance_packet_prereq_plan.json",
    "final_output_execution_decision": ROOT / "Results/static_audits/final_output_execution_decision_20260610/final_output_execution_decision_check.json",
}
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_readiness_dashboard_20260610"


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


def gate_record(gate_id: str, path: Path, data: dict[str, Any], ready_key: str, ready_value: bool = True) -> dict[str, Any]:
    summary = data.get("summary", {})
    ready = summary.get(ready_key) is ready_value
    return {
        "gate_id": gate_id,
        "path": rel(path),
        "status": data.get("status", ""),
        "ready_key": ready_key,
        "ready": ready,
        "summary": summary,
    }


def collect_blockers(gate_id: str, data: dict[str, Any]) -> list[dict[str, str]]:
    blockers: list[dict[str, str]] = []
    for blocker in data.get("blockers", []):
        if isinstance(blocker, dict):
            blockers.append(
                {
                    "gate_id": gate_id,
                    "blocker_id": str(blocker.get("blocker_id", "")),
                    "reason": str(blocker.get("reason", "")),
                    "needed_action": str(blocker.get("needed_action", "")),
                }
            )
    return blockers


def execution_decision_blockers(gate_id: str, data: dict[str, Any]) -> list[dict[str, str]]:
    summary = data.get("summary", {})
    blockers: list[dict[str, str]] = []
    decisions = [
        ("authorizes_pdf_export", "PDF export execution is not authorized"),
        ("authorizes_demo_video_recording", "demo video recording/rendering is not authorized"),
        ("authorizes_final_acceptance_packet", "canonical final acceptance packet writing is not authorized"),
    ]
    for key, reason in decisions:
        if summary.get(key) is not True:
            blockers.append(
                {
                    "gate_id": gate_id,
                    "blocker_id": key,
                    "reason": reason,
                    "needed_action": "review final output execution decision template and satisfy upstream readiness gates",
                }
            )
    return blockers


def build_dashboard(inputs: dict[str, Path]) -> dict[str, Any]:
    data = {name: read_json(path) for name, path in inputs.items()}
    gates = {
        "final_packaging_gap": gate_record(
            "final_packaging_gap",
            inputs["final_packaging_gap"],
            data["final_packaging_gap"],
            "final_submission_ready",
        ),
        "source_output_readiness": gate_record(
            "source_output_readiness",
            inputs["source_output_readiness"],
            data["source_output_readiness"],
            "safe_to_export_final_pdfs_now",
        ),
        "final_artifact_manifest": gate_record(
            "final_artifact_manifest",
            inputs["final_artifact_manifest"],
            data["final_artifact_manifest"],
            "final_submission_artifacts_ready",
        ),
        "pdf_export_plan": gate_record(
            "pdf_export_plan",
            inputs["pdf_export_plan"],
            data["pdf_export_plan"],
            "safe_to_run_pdf_export_now",
        ),
        "demo_video_storyboard": gate_record(
            "demo_video_storyboard",
            inputs["demo_video_storyboard"],
            data["demo_video_storyboard"],
            "safe_to_record_demo_video_now",
        ),
        "final_acceptance_prereq": gate_record(
            "final_acceptance_prereq",
            inputs["final_acceptance_prereq"],
            data["final_acceptance_prereq"],
            "safe_to_write_final_acceptance_packet_now",
        ),
        "final_output_execution_decision": {
            **gate_record(
                "final_output_execution_decision",
                inputs["final_output_execution_decision"],
                data["final_output_execution_decision"],
                "all_execution_decisions_authorized",
            ),
            "ready": (
                data["final_output_execution_decision"].get("summary", {}).get("authorizes_pdf_export") is True
                and data["final_output_execution_decision"].get("summary", {}).get(
                    "authorizes_demo_video_recording"
                ) is True
                and data["final_output_execution_decision"].get("summary", {}).get(
                    "authorizes_final_acceptance_packet"
                ) is True
            ),
        },
    }
    blockers: list[dict[str, str]] = []
    for gate_id, gate_data in data.items():
        blockers.extend(collect_blockers(gate_id, gate_data))
    blockers.extend(execution_decision_blockers("final_output_execution_decision", data["final_output_execution_decision"]))

    blocking_gate_ids = [gate_id for gate_id, gate in gates.items() if not gate["ready"]]
    final_submission_ready = not blocking_gate_ids

    return {
        "dashboard_id": "final_submission_readiness_dashboard_20260610",
        "status": "static_dashboard_not_final_submission_acceptance",
        "summary": {
            "gate_count": len(gates),
            "ready_gate_count": len(gates) - len(blocking_gate_ids),
            "blocking_gate_count": len(blocking_gate_ids),
            "blocker_count": len(blockers),
            "final_submission_ready": final_submission_ready,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "gates": gates,
        "blocking_gate_ids": blocking_gate_ids,
        "blockers": blockers,
        "claim_boundary": [
            "This dashboard aggregates static readiness gates only.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
            "It does not replace manual/PMO review.",
        ],
    }


def write_markdown(dashboard: dict[str, Any], path: Path) -> None:
    summary = dashboard["summary"]
    lines = [
        "# Final Submission Readiness Dashboard, 2026-06-10",
        "",
        f"Status: `{dashboard['status']}`",
        "",
        "## Summary",
        "",
        f"- Gates: `{summary['gate_count']}`",
        f"- Ready gates: `{summary['ready_gate_count']}`",
        f"- Blocking gates: `{summary['blocking_gate_count']}`",
        f"- Blockers: `{summary['blocker_count']}`",
        f"- Final submission ready: `{summary['final_submission_ready']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Claim Boundary",
        "",
    ]
    for item in dashboard["claim_boundary"]:
        lines.append(f"- {item}")

    lines.extend(["", "## Gates", "", "| Gate | Ready | Status | Ready Key | Path |", "|---|---|---|---|---|"])
    for gate_id, gate in dashboard["gates"].items():
        lines.append(
            f"| {gate_id} | {gate['ready']} | `{gate['status']}` | `{gate['ready_key']}` | `{gate['path']}` |"
        )

    lines.extend(["", "## Blockers", ""])
    if dashboard["blockers"]:
        for blocker in dashboard["blockers"]:
            lines.append(
                f"- `{blocker['gate_id']}/{blocker['blocker_id']}`: {blocker['reason']} Needed action: {blocker['needed_action']}"
            )
    else:
        lines.append("- None.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    for name, path in DEFAULT_INPUTS.items():
        parser.add_argument(f"--{name.replace('_', '-')}", default=str(path.relative_to(ROOT)))
    args = parser.parse_args()

    inputs = {
        name: repo_path(getattr(args, name))
        for name in DEFAULT_INPUTS
    }
    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    dashboard = build_dashboard(inputs)
    json_path = output_dir / "final_submission_readiness_dashboard.json"
    md_path = output_dir / "final_submission_readiness_dashboard.md"
    json_path.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(dashboard, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "dashboard_json": rel(json_path),
                "dashboard_markdown": rel(md_path),
                "blocking_gate_count": dashboard["summary"]["blocking_gate_count"],
                "final_submission_ready": dashboard["summary"]["final_submission_ready"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
