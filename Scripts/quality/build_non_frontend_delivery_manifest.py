#!/usr/bin/env python3
"""Build a current non-frontend reproducibility and demo delivery manifest.

This is a source/evidence manifest. It does not run Gazebo, export PDFs, record
video, or accept the competition submission. Runtime rows keep their declared
accepted/blocked/not-run boundaries.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "control_platform" / "non_frontend_evidence_index_20260718"

AUTHORITY = {
    "requirement_matrix": "Results/control_platform/non_frontend_evidence_index_20260718/NON_FRONTEND_REQUIREMENT_EVIDENCE_MATRIX.json",
    "report_source": "Results/control_platform/non_frontend_evidence_index_20260718/NON_FRONTEND_REPORT_SOURCE.json",
    "figure_manifest": "Results/control_platform/non_frontend_evidence_index_20260718/figures/REPORT_FIGURE_MANIFEST.json",
    "controller_matrix": "Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json",
    "final_ab": "Results/control_platform/final_controller_ab_20260718/FINAL_CONTROLLER_SEVEN_SCENARIO_AB.json",
    "safety": "Results/control_platform/p6_safety_runtime_20260717/P6_SAFETY_RUNTIME_MATRIX.json",
    "ftc": "Results/control_platform/p7_ftc_generated_gazebo_r3_20260717/P7_FTC_RUNTIME_CLOSEOUT.json",
    "formation": "Results/control_platform/p8_formation_mode1_gazebo_r7_20260717/PX4CTRL_SWARM_BASIC_METRICS.json",
    "learning": "Results/control_platform/p9_learning_gazebo_r4_20260717/P9_LEARNING_RUNTIME_CLOSEOUT.json",
    "motor_fault_blocker": "Results/control_platform/final_controller_ab_motor_fault_r2_20260718/INFRASTRUCTURE_BLOCKER.json",
}

REPRODUCTION_COMMANDS = [
    "python -m pytest Scripts/tests/test_non_frontend_requirement_evidence_matrix.py Scripts/tests/test_non_frontend_report_source.py Scripts/tests/test_non_frontend_report_figures.py Scripts/tests/test_non_frontend_delivery_manifest.py Scripts/tests/test_non_frontend_submission_package_manifest.py Scripts/tests/test_non_frontend_final_qa_audit.py Scripts/tests/test_final_controller_ab_matrix.py -q",
    "python Scripts/quality/build_non_frontend_requirement_evidence_matrix.py",
    "python Scripts/quality/build_non_frontend_report_source.py",
    "python Scripts/quality/build_non_frontend_report_figures.py",
    "python Scripts/quality/build_non_frontend_delivery_manifest.py",
    "python Scripts/quality/build_non_frontend_submission_package_manifest.py",
    "python Scripts/quality/build_non_frontend_final_qa_audit.py",
]

FORBIDDEN_CLAIMS = [
    "final_submission_ready",
    "all_controller_gazebo_acceptance",
    "gain_scheduled_pid_general_superiority",
    "neural_or_rl_performance_accepted",
    "complete_motor_outage_recovery",
    "frontend_closed_loop_authority",
]


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def load_json(relative_path: str) -> dict[str, Any]:
    path = repo_path(relative_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {relative_path}")
    return data


def file_record(relative_path: str) -> dict[str, Any]:
    path = repo_path(relative_path)
    record: dict[str, Any] = {
        "path": relative_path,
        "exists": path.is_file(),
        "size_bytes": path.stat().st_size if path.is_file() else 0,
    }
    if path.is_file():
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        record["sha256"] = digest.hexdigest()
    return record


def accepted_controller_ids(controller: dict[str, Any]) -> list[str]:
    identifiers = [
        str(row.get("controller") or row.get("controller_id") or row.get("profile") or row.get("model") or "")
        for row in controller.get("rows", [])
        if isinstance(row, dict) and row.get("status") == "accepted"
    ]
    if not identifiers or any(not value or value == "unknown" for value in identifiers):
        raise ValueError("accepted controller rows must have concrete identifiers")
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("accepted controller identifiers must be unique")
    return identifiers


def build() -> dict[str, Any]:
    matrix = load_json(AUTHORITY["requirement_matrix"])
    source = load_json(AUTHORITY["report_source"])
    controller = load_json(AUTHORITY["controller_matrix"])
    ab = load_json(AUTHORITY["final_ab"])

    controller_counts = controller.get("counts", {})
    if matrix.get("controller_matrix_counts") != controller_counts:
        raise ValueError(
            "requirement matrix and controller authority disagree: "
            f"{matrix.get('controller_matrix_counts')} != {controller_counts}"
        )
    if source.get("controller_summary", {}).get("counts") != controller_counts:
        raise ValueError(
            "report source and controller authority disagree: "
            f"{source.get('controller_summary', {}).get('counts')} != {controller_counts}"
        )
    if sum(int(value) for value in controller_counts.values()) != 67:
        raise ValueError(f"controller authority must contain 67 rows: {controller_counts}")

    figures = [
        "Results/control_platform/non_frontend_evidence_index_20260718/figures/controller_status_counts.png",
        "Results/control_platform/non_frontend_evidence_index_20260718/figures/final_pid_ab_primary_rmse.png",
        "Results/control_platform/non_frontend_evidence_index_20260718/figures/learning_control_rmse_change.png",
    ]
    evidence_files = list(AUTHORITY.values()) + figures + [
        "Docs/user_manual.md",
        "Docs/Workflows/mainline_operations_board.md",
        "PROGRESS.md",
    ]

    return {
        "schema": "mosim.non_frontend_delivery_manifest.v1",
        "date": "2026-07-18",
        "status": "delivery_manifest_not_final_submission_acceptance",
        "scope": {
            "frontend_excluded": True,
            "excluded_components": ["Flight Console", "Model Studio", "QGC", "UE", "RViz embedding"],
            "runtime_authority": "ROS1 Noetic / Sunray / Gazebo Classic / PX4 / MAVROS / px4ctrl",
        },
        "authority": AUTHORITY,
        "controller_baseline": {
            "counts": controller_counts,
            "accepted_controller_ids": accepted_controller_ids(controller),
            "final_ab_counts": ab.get("counts", {}),
            "claim_boundary": "Only accepted rows are selectable Gazebo controller evidence; blocked and not-run rows remain visible.",
        },
        "reproduction": {
            "working_directory": "C:/Users/HP/Desktop/MoSim",
            "commands": REPRODUCTION_COMMANDS,
            "runtime_note": "The commands rebuild static indices and figures. Gazebo/MWORKS runtime gates require their declared workflows and are not silently replaced by static output.",
        },
        "demo_storyboard": [
            {"order": 1, "title": "Scope and evidence boundary", "evidence": ["requirement_matrix", "report_source"], "allowed_claim": "Show the project boundary and distinguish accepted, blocked, and not-run evidence."},
            {"order": 2, "title": "Accepted controller and baseline evidence", "evidence": ["controller_matrix", "figure_manifest"], "allowed_claim": "Show accepted controller rows and saved metrics/figures without general superiority claims."},
            {"order": 3, "title": "Safety and FTC", "evidence": ["safety", "ftc"], "allowed_claim": "Show the declared safety modes and bounded rotor-effectiveness FTC recovery."},
            {"order": 4, "title": "Three-UAV formation", "evidence": ["formation"], "allowed_claim": "Show bounded formation evidence; do not claim autonomous exploration."},
            {"order": 5, "title": "Learning-control experiment", "evidence": ["learning"], "allowed_claim": "Show Neural Residual and RL experimental routes as selectable=false report evidence."},
            {"order": 6, "title": "Known limits and closeout", "evidence": ["motor_fault_blocker", "final_ab"], "allowed_claim": "Show unresolved runtime limits and the exact claim ceiling."},
        ],
        "evidence_files": [file_record(path) for path in evidence_files],
        "required_human_outputs": [
            {"path": "Results/submission/user_manual.pdf", "status": "pending_human_export_and_review"},
            {"path": "Results/submission/simulation_analysis_report.pdf", "status": "pending_human_export_and_review"},
            {"path": "Results/submission/demo_video.mp4", "status": "pending_reviewed_recording"},
            {"path": "Results/agent_packets/returns/PMO-FINAL-SUBMISSION-ACCEPTANCE.json", "status": "pending_final_review"},
        ],
        "forbidden_claims": FORBIDDEN_CLAIMS,
        "claim_boundary": [
            "This manifest proves reproducibility inputs and delivery structure, not final submission acceptance.",
            "It does not run Gazebo or MWORKS, export PDFs, record video, or write a final acceptance packet.",
            "A blocked or not-run row cannot be presented as a successful controller result.",
        ],
    }


def write_markdown(data: dict[str, Any], path: Path) -> None:
    baseline = data["controller_baseline"]
    lines = [
        "# Non-Frontend Reproducibility and Demo Delivery Manifest",
        "",
        f"Status: `{data['status']}`",
        "",
        "## Scope",
        "",
        "- Frontend excluded: `True`",
        "- Runtime authority: `ROS1 Noetic / Sunray / Gazebo Classic / PX4 / MAVROS / px4ctrl`",
        f"- Controller counts: `{baseline['counts']}`",
        f"- Final A/B counts: `{baseline['final_ab_counts']}`",
        "",
        "## Reproduction Commands",
        "",
    ]
    lines.extend(f"{index}. `{command}`" for index, command in enumerate(data["reproduction"]["commands"], 1))
    lines.extend(["", "## Demo Storyboard", "", "| # | Scene | Evidence | Allowed claim |", "|---:|---|---|---|"])
    for scene in data["demo_storyboard"]:
        lines.append(f"| {scene['order']} | {scene['title']} | {', '.join(scene['evidence'])} | {scene['allowed_claim']} |")
    lines.extend(["", "## Required Human Outputs", "", "| Path | Status |", "|---|---|"])
    for item in data["required_human_outputs"]:
        lines.append(f"| `{item['path']}` | `{item['status']}` |")
    lines.extend(["", "## Claim Boundary", ""])
    lines.extend(f"- {item}" for item in data["claim_boundary"])
    lines.extend(["", "## Forbidden Claims", ""])
    lines.extend(f"- `{item}`" for item in data["forbidden_claims"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()
    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    data = build()
    json_path = output_dir / "NON_FRONTEND_DELIVERY_MANIFEST.json"
    md_path = output_dir / "NON_FRONTEND_DELIVERY_MANIFEST.md"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    write_markdown(data, md_path)
    print(json.dumps({"ok": True, "json": rel(json_path), "markdown": rel(md_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
