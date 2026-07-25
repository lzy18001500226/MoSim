#!/usr/bin/env python3
"""Validate the synthetic Gazebo-step synchronization gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-dir", type=Path, required=True)
    args = parser.parse_args()

    responder = load_json(args.result_dir / "synthetic_responder.json")
    status = load_json(args.result_dir / "RT1_STATUS.json")
    events = [
        json.loads(line)
        for line in (args.result_dir / "rt1_trace.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    ]
    sync = status["synchronization"]
    stall_start = responder.get("stall_started_monotonic_ns")
    stall_end = responder.get("stall_finished_monotonic_ns")
    step_events = [
        event
        for event in events
        if event.get("event") in {"step_requested", "step_completed"}
    ]
    steps_during_stall = [
        event
        for event in step_events
        if stall_start is not None
        and stall_end is not None
        and stall_start <= event.get("monotonic_ns", -1) <= stall_end
    ]
    accepted_after_stall = [
        event
        for event in events
        if event.get("event") == "command_decision"
        and event.get("accepted") is True
        and stall_end is not None
        and event.get("received_ns", -1) > stall_end
    ]
    bootstrap_step_completion_count = sync.get("bootstrap_step_completion_count", 0)
    expected_sim_time_ns = (
        (sync["step_completion_count"] + bootstrap_step_completion_count)
        * sync["gazebo_steps_per_command"]
        * sync["gazebo_step_size_ns"]
    )
    checks = {
        "synthetic_source_labeled": responder.get("execution_source")
        == "python_synthetic_protocol_test_only",
        "stall_injected": responder.get("stall_injected") is True,
        "step_requests_completed": sync["step_request_count"]
        == sync["step_completion_count"]
        and sync["step_completion_count"] > 0,
        "bootstrap_steps_completed": sync.get("bootstrap_complete") is True
        and sync.get("bootstrap_step_request_count", 0)
        == bootstrap_step_completion_count
        and bootstrap_step_completion_count > 0,
        "accepted_command_drives_exactly_one_step_request": status[
            "accepted_command_count"
        ]
        == sync["step_request_count"],
        "simulation_time_matches_completed_steps": sync["sim_time_ns"]
        == expected_sim_time_ns,
        "no_physics_step_during_solver_stall": not steps_during_stall,
        "stale_stall_output_rejected": status["rejection_counts"]["output_stale"]
        > 0,
        "fresh_command_accepted_after_stall": bool(accepted_after_stall),
    }
    accepted = all(checks.values())
    result = {
        "schema": "mosim.mworks_live.gazebo_step_synthetic_gate.v1",
        "accepted": accepted,
        "evidence_scope": "synthetic_protocol_test_only_not_mworks_runtime_evidence",
        "checks": checks,
        "metrics": {
            "stall_duration_s": responder.get("stall_duration_s"),
            "steps_during_stall": len(steps_during_stall),
            "step_request_count": sync["step_request_count"],
            "step_completion_count": sync["step_completion_count"],
            "bootstrap_step_request_count": sync.get(
                "bootstrap_step_request_count", 0
            ),
            "bootstrap_step_completion_count": bootstrap_step_completion_count,
            "sim_time_ns": sync["sim_time_ns"],
            "output_stale_count": status["rejection_counts"]["output_stale"],
            "accepted_after_stall_count": len(accepted_after_stall),
        },
    }
    output = args.result_dir / "GAZEBO_STEP_SYNTHETIC_GATE.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if accepted else 2


if __name__ == "__main__":
    raise SystemExit(main())
