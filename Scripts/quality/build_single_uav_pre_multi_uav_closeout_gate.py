#!/usr/bin/env python3
"""Build the single-UAV closeout gate before multi-UAV work.

This read-only artifact combines current batch acceptance, rotor1-loss
diagnostics, candidate selection, and MWORKS GUI blocker state. It does not run
MWORKS, Sysplorer, MCP, check_model, SimulateModel, ROS2, UE, or GUI tools.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "Results" / "mworks_model_hygiene" / "20260612_single_uav_pre_multi_uav_closeout_gate"
DEFAULT_ACCEPTANCE = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260611_single_uav_control_batch_result_acceptance"
    / "single_uav_control_batch_result_acceptance.json"
)
DEFAULT_ERROR_PROFILE = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260611_rotor1_loss15_error_profile"
    / "rotor1_loss15_error_profile.json"
)
DEFAULT_CANDIDATE_MATRIX = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260611_rotor1_loss15_candidate_matrix"
    / "rotor1_loss15_candidate_matrix.json"
)
PREFERRED_SENTINEL = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260612_post_simulation_preflight"
    / "current_gui_sentinel.json"
)


def rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def repo_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        return parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def find_latest_sentinel() -> Path:
    if PREFERRED_SENTINEL.exists():
        return PREFERRED_SENTINEL
    candidates = sorted(
        (ROOT / "Results" / "mworks_model_hygiene").glob("**/current_gui_sentinel*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if candidates:
        return candidates[0]
    return PREFERRED_SENTINEL


def live_gate(sentinel_path: Path) -> dict[str, Any]:
    if not sentinel_path.exists():
        return {
            "state": "unknown_no_current_sentinel",
            "sentinel": rel(sentinel_path),
            "live_mworks_allowed": False,
        }
    sentinel = read_json(sentinel_path)
    blocked = (
        sentinel.get("status") == "incident_detected"
        or sentinel.get("error_kind") == "gui_blocked"
        or sentinel.get("license_state_hint") == "upgrade_model_surface_blocked"
        or int(sentinel.get("blocking_mworks_window_count", 0) or 0) > 0
    )
    return {
        "state": "blocked_by_mworks_gui" if blocked else "clean_preflight_available",
        "sentinel": rel(sentinel_path),
        "live_mworks_allowed": not blocked,
        "created_at": sentinel.get("created_at"),
        "status": sentinel.get("status"),
        "error_kind": sentinel.get("error_kind"),
        "license_state_hint": sentinel.get("license_state_hint"),
        "blocking_mworks_window_count": sentinel.get("blocking_mworks_window_count"),
        "upgrade_model_window_count": sentinel.get("upgrade_model_window_count"),
    }


def current_candidate_evidence(best: dict[str, Any], live: dict[str, Any]) -> dict[str, Any]:
    metrics_ref = best.get("metrics_file")
    metrics_path = repo_path(Path(str(metrics_ref))) if metrics_ref else Path()
    if not best:
        return {
            "state": "missing_candidate",
            "accepted_current_rerun": False,
            "metrics_file": None,
            "reasons": ["no accepted rotor-loss candidate is available"],
        }
    if not metrics_path.exists():
        return {
            "state": "missing_metrics",
            "accepted_current_rerun": False,
            "metrics_file": rel(metrics_path),
            "reasons": ["best candidate metrics file is missing"],
        }

    metrics = read_json(metrics_path)
    raw_path = repo_path(Path(str(metrics.get("raw_file", "")))) if metrics.get("raw_file") else Path()
    metrics_checked_at = parse_time(metrics.get("quality_checked_at") or metrics.get("generated_at"))
    sentinel_created_at = parse_time(live.get("created_at"))

    checks = {
        "quality_status_pass": metrics.get("quality_status") == "pass",
        "quality_pass_true": metrics.get("quality_pass") is True,
        "source_mworks_mcp": metrics.get("source") == "MWORKS_MCP",
        "row_count_full_run": int(metrics.get("row_count", 0) or 0) >= 10000,
        "duration_full_run": float(metrics.get("duration_s", 0.0) or 0.0) >= 45.0,
        "raw_file_present": raw_path.exists(),
        "metrics_after_clean_sentinel": (
            metrics_checked_at is not None
            and sentinel_created_at is not None
            and metrics_checked_at >= sentinel_created_at
        ),
    }
    reasons = [name for name, passed in checks.items() if not passed]
    accepted = not reasons
    return {
        "state": "current_rerun_accepted" if accepted else "candidate_needs_fresh_rerun_or_audit",
        "accepted_current_rerun": accepted,
        "metrics_file": rel(metrics_path),
        "raw_file": rel(raw_path) if str(raw_path) else None,
        "quality_checked_at": metrics.get("quality_checked_at"),
        "generated_at": metrics.get("generated_at"),
        "source": metrics.get("source"),
        "row_count": metrics.get("row_count"),
        "duration_s": metrics.get("duration_s"),
        "position_rmse_m": metrics.get("position_rmse_m"),
        "steady_state_error_m": metrics.get("steady_state_error_m"),
        "disturbance_recovery_time_s": metrics.get("disturbance_recovery_time_s"),
        "total_health_score": metrics.get("total_health_score"),
        "quality_rmse_improvement_pct": metrics.get("quality_rmse_improvement_pct"),
        "checks": checks,
        "reasons": reasons,
    }


def build_gate(
    acceptance_path: Path,
    error_profile_path: Path,
    candidate_matrix_path: Path,
    sentinel_path: Path,
) -> dict[str, Any]:
    acceptance = read_json(acceptance_path)
    error_profile = read_json(error_profile_path)
    matrix = read_json(candidate_matrix_path)
    live = live_gate(sentinel_path)

    accepted_count = int(acceptance.get("accepted_result_count", 0) or 0)
    needs_iteration_count = int(acceptance.get("needs_iteration_count", 0) or 0)
    candidate_count = int(matrix.get("accepted_candidate_count", 0) or 0)
    best = matrix.get("best_rmse_candidate") if isinstance(matrix.get("best_rmse_candidate"), dict) else {}
    live_allowed = bool(live.get("live_mworks_allowed"))
    current_candidate = current_candidate_evidence(best, live)

    if not live_allowed:
        status = "blocked_by_live_mworks_gate"
        decision = "do_not_enter_multi_uav_yet"
    elif candidate_count and current_candidate.get("accepted_current_rerun"):
        status = "single_uav_gate_ready_for_ue_prep"
        decision = "prepare_ue_replay_inputs_directly_when_user_authorized"
    elif needs_iteration_count and candidate_count:
        status = "ready_for_fresh_single_uav_rerun_before_multi_uav"
        decision = "rerun_selected_single_uav_gates_before_multi_uav"
    elif needs_iteration_count:
        status = "needs_single_uav_iteration"
        decision = "continue_single_uav_iteration"
    else:
        status = "single_uav_gate_ready_for_pmo_review"
        decision = "pmo_review_before_multi_uav"

    if candidate_count and current_candidate.get("accepted_current_rerun"):
        required_before_multi_uav = [
            "If the user has authorized this thread to continue, proceed to UE replay/render input preparation without waiting for PMO idleness.",
            "Prepare a UE replay/render input bundle from the accepted raw CSV, metrics JSON, replay JSON, and scene/map contract.",
            "Do not open UE editor/runtime/build or claim UE runtime success until the UE workflow gate authorizes that scope.",
            "Keep final report acceptance separate from engineering continuation; terminal report wording still needs its own final acceptance gate.",
            "If report wording needs current baseline comparison, rerun the two plain PID/AWFF rotor1_loss15 scenarios and acceptance checker.",
            "Keep the remaining needs-iteration rotor1_loss15 rows visible as negative or iteration evidence.",
        ]
    elif candidate_count:
        required_before_multi_uav = [
            "Use the latest clean MWORKS GUI sentinel before new live MWORKS or UE transition work.",
            "If report wording needs current baseline comparison, rerun the two plain PID/AWFF rotor1_loss15 scenarios and acceptance checker.",
            "Rerun the selected accepted rotor-loss candidate under the current clean MWORKS preflight before UE replay or multi-UAV transition.",
            "Refresh the rotor1_loss15 candidate matrix and this closeout gate after the rerun.",
            "Do not wait for PMO idleness after the fresh rerun if the user has already authorized this thread to continue and no hard blocker appears.",
        ]
    else:
        required_before_multi_uav = [
            "Use the latest clean MWORKS GUI sentinel before any new live MWORKS work.",
            "Continue single-UAV controller/model iteration for rotor1_loss15; no current accepted rotor-loss candidate is available.",
            "Do not enter UE replay/rendering or multi-UAV formation transition from this gate.",
            "After an engineering change, rerun the relevant rotor1_loss15 scenario(s), refresh acceptance, refresh the candidate matrix, and rebuild this closeout gate.",
            "PMO/report review may only discuss needs-iteration evidence and next engineering focus, not accepted robustness performance.",
        ]

    return {
        "schema": "mosim.mworks.single_uav_pre_multi_uav_closeout_gate.v1",
        "status": status,
        "decision": decision,
        "static_read_only": True,
        "live_mworks_touched": False,
        "scope": "single_uav_closeout_before_multi_uav",
        "input_artifacts": {
            "batch_acceptance": rel(acceptance_path),
            "rotor1_error_profile": rel(error_profile_path),
            "rotor1_candidate_matrix": rel(candidate_matrix_path),
            "mworks_gui_sentinel": rel(sentinel_path),
        },
        "live_gate": live,
        "batch_acceptance_summary": {
            "status": acceptance.get("status"),
            "scenario_count": acceptance.get("scenario_count"),
            "accepted_result_count": accepted_count,
            "needs_iteration_count": needs_iteration_count,
            "iteration_targets": acceptance.get("iteration_targets", []),
        },
        "rotor1_diagnostic_summary": {
            "status": error_profile.get("status"),
            "comparison": error_profile.get("comparison", {}),
            "next_engineering_focus": error_profile.get("next_engineering_focus", []),
        },
        "rotor1_candidate_summary": {
            "status": matrix.get("status"),
            "scenario_count": matrix.get("scenario_count"),
            "accepted_candidate_count": candidate_count,
            "needs_iteration_or_unverified_count": matrix.get("needs_iteration_or_unverified_count"),
            "best_rmse_candidate": best,
        },
        "current_candidate_rerun_evidence": current_candidate,
        "required_before_multi_uav": required_before_multi_uav,
        "claim_boundary": [
            "This closeout gate is read-only and does not run MWORKS itself.",
            "Current-rerun readiness is inferred only from metrics/raw artifacts, source labels, quality gates, and clean-sentinel timing.",
            "It may prepare UE replay inputs, but it does not authorize UE editor/runtime/build work.",
            "It does not start or authorize multi-UAV formation work.",
            "It does not grant final report acceptance.",
        ],
    }


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def write_markdown(path: Path, gate: dict[str, Any]) -> None:
    best = gate["rotor1_candidate_summary"].get("best_rmse_candidate") or {}
    lines = [
        "# Single-UAV Pre Multi-UAV Closeout Gate",
        "",
        f"Status: `{gate['status']}`",
        f"Decision: `{gate['decision']}`",
        "",
        "Read-only gate. It does not run MWORKS and does not authorize formation work.",
        "",
        "## Current State",
        "",
        f"- Batch acceptance: `{gate['batch_acceptance_summary']['status']}`; "
        f"{gate['batch_acceptance_summary']['accepted_result_count']} accepted, "
        f"{gate['batch_acceptance_summary']['needs_iteration_count']} need iteration.",
        f"- Live MWORKS gate: `{gate['live_gate']['state']}`.",
        f"- Rotor1 accepted candidates: `{gate['rotor1_candidate_summary']['accepted_candidate_count']}`.",
    ]
    if best:
        lines.append(
            f"- Best rotor1 candidate: `{best.get('controller_id')}` "
            f"rmse=`{float(best.get('position_rmse_m')):.6f}`, "
            f"health=`{float(best.get('total_health_score')):.6f}`."
        )
    current = gate.get("current_candidate_rerun_evidence", {})
    if current:
        lines.append(
            f"- Current candidate rerun evidence: `{current.get('state')}`; "
            f"metrics=`{current.get('metrics_file')}`."
        )
    lines.extend(["", "## Required Before Multi-UAV", ""])
    lines.extend(f"- {item}" for item in gate["required_before_multi_uav"])
    lines.extend(["", "## Claim Boundary", ""])
    lines.extend(f"- {item}" for item in gate["claim_boundary"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acceptance", type=Path, default=DEFAULT_ACCEPTANCE)
    parser.add_argument("--error-profile", type=Path, default=DEFAULT_ERROR_PROFILE)
    parser.add_argument("--candidate-matrix", type=Path, default=DEFAULT_CANDIDATE_MATRIX)
    parser.add_argument("--sentinel", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    gate = build_gate(
        repo_path(args.acceptance),
        repo_path(args.error_profile),
        repo_path(args.candidate_matrix),
        repo_path(args.sentinel) if args.sentinel else find_latest_sentinel(),
    )
    output_dir = repo_path(args.output_dir)
    write_json(output_dir / "single_uav_pre_multi_uav_closeout_gate.json", gate)
    write_markdown(output_dir / "single_uav_pre_multi_uav_closeout_gate.md", gate)
    print(json.dumps(gate, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
