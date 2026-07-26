#!/usr/bin/env python3
"""Build the current non-frontend requirement-to-evidence matrix.

This matrix is intentionally conservative. It reads the current authority
JSON files and records claim ceilings; it never upgrades blocked or not-run
rows to accepted and never treats a design requirement as implementation
evidence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "Results" / "control_platform" / "non_frontend_evidence_index_20260718"

AUTHORITIES = {
    "controller_matrix": "Results/control_platform/classic_controller_closeout_20260717/CLASSIC_CONTROLLER_FINAL_MATRIX.json",
    "final_ab": "Results/control_platform/final_controller_ab_20260718/FINAL_CONTROLLER_SEVEN_SCENARIO_AB.json",
    "safety": "Results/control_platform/p6_safety_runtime_20260717/P6_SAFETY_RUNTIME_MATRIX.json",
    "ftc": "Results/control_platform/p7_ftc_generated_gazebo_r3_20260717/P7_FTC_RUNTIME_CLOSEOUT.json",
    "formation": "Results/control_platform/p8_formation_mode1_gazebo_r7_20260717/PX4CTRL_SWARM_BASIC_METRICS.json",
    "learning": "Results/control_platform/p9_learning_gazebo_r4_20260717/P9_LEARNING_RUNTIME_CLOSEOUT.json",
}


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def authority_state(data: dict[str, Any]) -> str:
    if data.get("acceptance_status") == "blocked":
        return "blocked"
    if data.get("status") in {"passed", "accepted"}:
        return "verified_at_declared_tier"
    if data.get("execution_status") == "passed":
        return "executed_with_claim_boundary"
    return str(data.get("status", "unknown"))


def build_matrix() -> dict[str, Any]:
    loaded: dict[str, dict[str, Any]] = {}
    for key, raw_path in AUTHORITIES.items():
        path = ROOT / raw_path
        if not path.exists():
            raise FileNotFoundError(raw_path)
        loaded[key] = read_json(path)

    controller = loaded["controller_matrix"]
    ab = loaded["final_ab"]
    controller_counts = controller.get("counts", {})
    expected_statuses = {"accepted", "executed_blocked", "not_run"}
    if set(controller_counts) != expected_statuses:
        raise ValueError(f"controller matrix has unexpected status keys: {controller_counts}")
    if sum(int(controller_counts[key]) for key in expected_statuses) != 67:
        raise ValueError(f"controller matrix must contain 67 rows: {controller_counts}")
    observed_counts = {
        status: sum(1 for row in controller.get("rows", []) if row.get("status") == status)
        for status in expected_statuses
    }
    if observed_counts != controller_counts:
        raise ValueError(
            f"controller matrix counts do not match rows: counts={controller_counts}, rows={observed_counts}"
        )
    rows = [
        {
            "requirement_id": "REQ-MW-01/04/07/11",
            "area": "MWORKS modeling, code generation, SIL and lifecycle",
            "status": "verified_at_declared_tier",
            "evidence": [AUTHORITIES["controller_matrix"]],
            "claim_ceiling": "The matrix records implementation, MWORKS/codegen/SIL state per controller; it does not imply Gazebo acceptance for blocked rows.",
        },
        {
            "requirement_id": "REQ-CTRL-01..79",
            "area": "Controller-family coverage",
            "status": "partial",
            "evidence": [AUTHORITIES["controller_matrix"]],
            "claim_ceiling": "67 rows are visible: {accepted} accepted, {blocked} executed-blocked, {not_run} not-run; only accepted rows may be presented as selectable Gazebo controllers.".format(
                accepted=controller_counts["accepted"],
                blocked=controller_counts["executed_blocked"],
                not_run=controller_counts["not_run"],
            ),
        },
        {
            "requirement_id": "REQ-TRAJ-01..04",
            "area": "Takeoff, hover, step, figure-eight and spiral scenarios",
            "status": "partial",
            "evidence": [AUTHORITIES["controller_matrix"], AUTHORITIES["final_ab"]],
            "claim_ceiling": "Scenario evidence exists across accepted and blocked rows; the A/B matrix is an observed comparison, not a general superiority result.",
        },
        {
            "requirement_id": "REQ-ROB-01/03",
            "area": "Wind and parameter-mismatch robustness",
            "status": "partial",
            "evidence": [AUTHORITIES["final_ab"], AUTHORITIES["learning"]],
            "claim_ceiling": "Wind injection evidence passed for both A/B profiles, but performance rows remain blocked; learning routes show report-worthy wind changes without stable overall superiority.",
        },
        {
            "requirement_id": "REQ-FAULT-01/02/07/08/09",
            "area": "Motor-efficiency fault, FDI, allocation, recovery and landing",
            "status": "verified_at_declared_tier_with_scope",
            "evidence": [AUTHORITIES["ftc"], AUTHORITIES["final_ab"]],
            "claim_ceiling": "P7 verifies rotor-1 effectiveness 0.65 with generated FDI/isolation/takeover/landing; the two C3 motor-fault A/B rows are not-run and complete outage or multi-fault recovery is not claimed.",
        },
        {
            "requirement_id": "REQ-SAFE-01/04/05/06/07/08/09/10",
            "area": "Safety filter, envelopes, geofence/failsafe and lifecycle safety",
            "status": "verified_at_declared_tier",
            "evidence": [AUTHORITIES["safety"]],
            "claim_ceiling": "Only the seven declared P6 safety modes are covered; this is not a claim for every optional CBF or reference-governor variant.",
        },
        {
            "requirement_id": "REQ-SWARM-01/03/04/07/08",
            "area": "Three-UAV formation deployment and separation safety",
            "status": "verified_at_declared_tier",
            "evidence": [AUTHORITIES["formation"]],
            "claim_ceiling": "P8 covers bounded three-UAV formation modes; it does not claim autonomous exploration or every research formation algorithm.",
        },
        {
            "requirement_id": "REQ-AI-01/02/05/07/08/10/15",
            "area": "Fuzzy and learning enhancement routes",
            "status": "partial",
            "evidence": [AUTHORITIES["controller_matrix"], AUTHORITIES["learning"]],
            "claim_ceiling": "Fuzzy PID and selected learning routes are implemented/evidenced at their row ceilings; Neural Residual and RL Gain Scheduler remain selectable=false because strict performance acceptance is blocked.",
        },
        {
            "requirement_id": "REQ-EVAL-01..16",
            "area": "Run IDs, manifests, metrics, logs, figures and failure records",
            "status": "in_progress",
            "evidence": [AUTHORITIES["controller_matrix"], AUTHORITIES["final_ab"], AUTHORITIES["safety"], AUTHORITIES["ftc"], AUTHORITIES["formation"], AUTHORITIES["learning"]],
            "claim_ceiling": "Authoritative runtime evidence exists; final report figures, requirement index and submission package still require C5/C6 completion.",
        },
        {
            "requirement_id": "REQ-OSS-01..05",
            "area": "Upstream version, license and modification audit",
            "status": "pending_final_qa",
            "evidence": [],
            "claim_ceiling": "Must be checked against the exact final submission paths before publication.",
        },
        {
            "requirement_id": "REQ-EVAL-09/11/12/13/14",
            "area": "Report, reproducibility and submission package",
            "status": "pending",
            "evidence": [],
            "claim_ceiling": "C5/C6 deliverable; no final-submission-ready claim is allowed until generated and checked.",
        },
        {
            "requirement_id": "REQ-UI-01..16",
            "area": "Frontend, UE/QGC/Flight Console/Model Studio and embedding",
            "status": "excluded_by_scope",
            "evidence": [],
            "claim_ceiling": "Explicitly excluded from the current non-frontend closeout goal; existing display evidence may be cited only as supporting visualization.",
        },
    ]

    if not ab.get("counts"):
        raise ValueError("final A/B matrix has no counts")

    return {
        "schema": "mosim.non_frontend_requirement_evidence_matrix.v1",
        "date": "2026-07-18",
        "status": "in_progress",
        "scope": "all current non-frontend engineering and submission work",
        "authority_files": AUTHORITIES,
        "authority_states": {key: authority_state(value) for key, value in loaded.items()},
        "controller_matrix_counts": controller_counts,
        "final_ab_counts": ab.get("counts", {}),
        "rows": rows,
        "global_claim_boundary": [
            "This matrix is traceability evidence, not a blanket acceptance record.",
            "accepted, executed_blocked, and not_run remain distinct terminal classes.",
            "Static, MIL, SIL, screenshots, and metrics-only evidence cannot replace the declared Gazebo/runtime gate.",
            "Frontend work is excluded and must not block this closeout.",
        ],
        "next_actions": [
            "retain the two motor-fault A/B rows as not_run under the versioned infrastructure blocker",
            "generate report-ready figures and analysis from authority files",
            "refresh manual, demo storyboard, reproducibility manifest and submission package",
            "run final quality, license, secret, large-file and exact-path Git publication QA",
        ],
    }


def write_markdown(matrix: dict[str, Any], path: Path) -> None:
    lines = [
        "# Non-Frontend Requirement-Evidence Matrix",
        "",
        "更新时间：2026-07-18。此矩阵是当前收尾追踪表，不是把所有需求标记为完成的声明。",
        "",
        f"- Controller matrix: `{matrix['controller_matrix_counts']}`",
        f"- Final A/B counts: `{matrix['final_ab_counts']}`",
        "- Scope: all current non-frontend engineering and submission work",
        "",
        "| Requirement | Area | Status | Evidence | Claim ceiling |",
        "|---|---|---|---|---|",
    ]
    for row in matrix["rows"]:
        evidence = "<br>".join(f"`{item}`" for item in row["evidence"]) or "-"
        ceiling = row["claim_ceiling"].replace("|", "\\|")
        lines.append(f"| `{row['requirement_id']}` | {row['area']} | `{row['status']}` | {evidence} | {ceiling} |")
    lines.extend(["", "## Global Claim Boundary", ""])
    lines.extend(f"- {item}" for item in matrix["global_claim_boundary"])
    lines.extend(["", "## Next Actions", ""])
    lines.extend(f"{index}. {item}" for index, item in enumerate(matrix["next_actions"], 1))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()
    output_dir = ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    matrix = build_matrix()
    json_path = output_dir / "NON_FRONTEND_REQUIREMENT_EVIDENCE_MATRIX.json"
    md_path = output_dir / "NON_FRONTEND_REQUIREMENT_EVIDENCE_MATRIX.md"
    json_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    write_markdown(matrix, md_path)
    print(json.dumps({"ok": True, "json": rel(json_path), "markdown": rel(md_path), "row_count": len(matrix["rows"])}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
