#!/usr/bin/env python3
"""Generate the bounded D3a Orchestrator contract evidence packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.orchestration import MoSimOrchestrator


PROFILE = "Config/profiles/experiments/px4ctrl_figure8_baseline_v1.json"
REQUIRED_FIELDS = {"request_id", "accepted", "reason_code", "run_id", "profile_hash", "timestamp"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "Results" / "ui_platform" / "orchestrator_d3a_gate_20260717",
    )
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    run_root = output_dir / "runs"
    orchestrator = MoSimOrchestrator(run_root=run_root)

    valid = orchestrator.validate_experiment_profile(
        request_id="valid-single", profile_path=PROFILE, controller_id="px4ctrl", vehicle_count=1
    )
    wrong_controller = orchestrator.validate_experiment_profile(
        request_id="wrong-controller", profile_path=PROFILE, controller_id="cascade_pid", vehicle_count=1
    )
    wrong_profile_scale = orchestrator.validate_experiment_profile(
        request_id="wrong-profile-scale", profile_path=PROFILE, controller_id="px4ctrl", vehicle_count=3
    )
    closed_scale = orchestrator.validate_experiment_profile(
        request_id="closed-scale", profile_path=PROFILE, controller_id="px4ctrl", vehicle_count=5
    )
    prepared = orchestrator.prepare_run(
        request_id="prepare", profile_path=PROFILE, controller_id="px4ctrl", vehicle_count=1
    )
    start = orchestrator.start_run(request_id="start", run_id=prepared.get("run_id", ""))

    responses = [valid, wrong_controller, wrong_profile_scale, closed_scale, prepared, start]
    checks = {
        "valid_single_profile": valid.get("accepted") is True,
        "controller_profile_mismatch_rejected": wrong_controller.get("reason_code")
        == "profile_controller_mismatch",
        "three_uav_profile_mismatch_rejected": wrong_profile_scale.get("reason_code")
        == "profile_vehicle_count_mismatch",
        "four_to_nine_scale_gate_closed": closed_scale.get("reason_code") == "vehicle_scale_gate_pending",
        "run_prepared_as_ready": prepared.get("manifest", {}).get("lifecycle_state") == "ready",
        "unconfigured_backend_cannot_start": start.get("reason_code") == "runtime_backend_unconfigured",
        "all_responses_match_required_shape": all(REQUIRED_FIELDS <= response.keys() for response in responses),
        "runtime_not_started": prepared.get("manifest", {}).get("runtime_started") is False,
    }
    gate = {
        "schema": "mosim.ui_platform.orchestrator_d3a_gate.v1",
        "status": "passed" if all(checks.values()) else "failed",
        "checks": checks,
        "responses": responses,
        "shared_gazebo_px4_touched": False,
        "actual_end_to_end_runtime_accepted": False,
        "claim_ceiling": (
            "Offline Orchestrator API, profile/controller/vehicle gates, lifecycle persistence, and explicit "
            "runtime-backend rejection only. This is not D3 live-runtime acceptance."
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "GATE.json").write_text(
        json.dumps(gate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps({"status": gate["status"], "checks": checks}, ensure_ascii=False, indent=2))
    return 0 if gate["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
