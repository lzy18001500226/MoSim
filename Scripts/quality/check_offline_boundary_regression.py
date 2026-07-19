#!/usr/bin/env python3
"""Audit the current offline MWORKS evidence for all four output boundaries."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = (
    ROOT
    / "Results"
    / "control_platform"
    / "offline_expansion_goal_20260719"
    / "P2_FOUR_BOUNDARY_REGRESSION.json"
)

REQUIRED_ACCEPTANCE = (
    "model_loaded",
    "check_model",
    "simulate_model",
    "raw_result_valid",
    "native_result_present",
    "result_window_opened",
    "plot_window_opened",
    "model_window_opened",
    "animation_window_opened",
    "bounded_closed_loop",
)
ACCEPTED_RECORD_STATUSES = {"accepted", "accepted_current_worktree"}

BOUNDARY_CASES: tuple[dict[str, str], ...] = (
    {
        "output_variant": "ATTITUDE_THRUST",
        "record": "Results/mworks_generated_profiles/goal-p2-attitude-thrust-fixture-20260719-v8/CERTIFICATION.json",
        "evidence_kind": "current_platform_fixture",
    },
    {
        "output_variant": "BODY_RATE_THRUST",
        "record": "Results/control_platform/offline_expansion_goal_20260719/P2_BODY_RATE_THRUST_LIVE_ACCEPTANCE.json",
        "evidence_kind": "current_platform_fixture",
    },
    {
        "output_variant": "WRENCH",
        "record": "Results/control_platform/offline_expansion_goal_20260719/P2_WRENCH_LIVE_ACCEPTANCE.json",
        "evidence_kind": "current_platform_fixture",
    },
    {
        "output_variant": "ROTOR_COMMAND",
        "record": "Results/mworks_generated_profiles/cert-official-pid-20260719-v2/CERTIFICATION.json",
        "evidence_kind": "certified_single_uav_profile",
    },
)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"json_object_required:{path}")
    return value


def artifact_path(root: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    path = Path(value)
    return path if path.is_absolute() else root / path


def audit_record(root: Path, case: dict[str, str]) -> dict[str, Any]:
    record_path = root / case["record"]
    result: dict[str, Any] = {
        "output_variant": case["output_variant"],
        "record": case["record"],
        "evidence_kind": case["evidence_kind"],
        "status": "blocked",
        "reasons": [],
    }
    if not record_path.is_file():
        result["reasons"].append("record_missing")
        return result

    try:
        record = read_json(record_path)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        result["reasons"].append(f"record_invalid:{type(error).__name__}")
        return result

    result["run_id"] = record.get("run_id")
    result["record_status"] = record.get("status")
    if record.get("output_variant") != case["output_variant"]:
        result["reasons"].append("output_variant_mismatch")

    acceptance = record.get("acceptance")
    if not isinstance(acceptance, dict):
        result["reasons"].append("acceptance_missing")
    else:
        result["acceptance"] = {
            key: acceptance.get(key) for key in REQUIRED_ACCEPTANCE
        }
        for key in REQUIRED_ACCEPTANCE:
            if acceptance.get(key) is not True:
                result["reasons"].append(f"acceptance_not_true:{key}")

    artifacts = record.get("artifacts")
    missing_artifacts: list[str] = []
    if not isinstance(artifacts, dict):
        result["reasons"].append("artifacts_missing")
    else:
        for key in ("raw_csv", "metrics_json", "native_result"):
            path = artifact_path(root, artifacts.get(key))
            if path is None or not path.is_file():
                missing_artifacts.append(key)
        if missing_artifacts:
            result["reasons"].append(
                "artifact_missing:" + ",".join(missing_artifacts)
            )

    cleanup = record.get("session_cleanup")
    cleanup_ok = False
    if isinstance(cleanup, dict):
        cleanup_ok = cleanup.get("shutdown_recorded") is True or (
            cleanup.get("task_owned_session_status") == "passed"
        )
    result["session_cleanup"] = "passed" if cleanup_ok else "blocked"
    if not cleanup_ok:
        result["reasons"].append("task_owned_session_cleanup_missing")

    if not result["reasons"] and record.get("status") in ACCEPTED_RECORD_STATUSES:
        result["status"] = "accepted"
    elif not result["reasons"]:
        result["reasons"].append("record_not_accepted")
    return result


def build_report(root: Path = ROOT) -> dict[str, Any]:
    boundaries = [audit_record(root, case) for case in BOUNDARY_CASES]
    accepted = all(item["status"] == "accepted" for item in boundaries)
    return {
        "schema": "mosim.offline_boundary_regression.v1",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "status": "accepted" if accepted else "blocked",
        "boundaries": boundaries,
        "claim_boundary": (
            "Current offline MWORKS evidence audit only; this report does not claim "
            "competition-controller performance, code generation, PX4, Gazebo, "
            "ROS1, online co-simulation, or flight acceptance."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    report = build_report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if args.strict and report["status"] != "accepted" else 0


if __name__ == "__main__":
    raise SystemExit(main())
