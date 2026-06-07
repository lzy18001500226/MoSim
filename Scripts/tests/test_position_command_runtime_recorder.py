#!/usr/bin/env python3
"""Static checks for the PositionCommand runtime recorder."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "ros" / "record_position_command_adapter_runtime.py"
REPLAY = ROOT / "Scripts" / "ros" / "publish_position_command_contract_replay.py"
ORCHESTRATOR = ROOT / "Scripts" / "ros" / "run_b0_position_command_contract_replay.py"


def test_recorder_is_passive_and_source_labeled() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for required in [
        "not publish",
        "PositionCommand messages",
        "Recorder is passive",
        "This is planner-adapter runtime evidence only when source_topic is a real planner output.",
        "Closed-loop claim still requires same-run MWORKS/controller consumption",
    ]:
        if required not in text:
            raise AssertionError(required)
    if "create_publisher(PositionCommand" in text or "pub.publish" in text:
        raise AssertionError("runtime recorder must not publish PositionCommand")


def test_recorder_artifact_contract() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for required in [
        "source_position_cmd.jsonl",
        "converted_planner_position_cmd.jsonl",
        "setpoint_trace.csv",
        "setpoint_adapter_status.jsonl",
        "topic_rates.json",
        "tf_time_gate.json",
        "planner_input_gate.json",
        "run_summary.json",
        "global_truth_used_as_input",
        "minimum_required_rate_hz",
        "source_available",
        "runtime_source_required",
        "No real planner runtime source was recorded on source_topic.",
        "--min-rate-hz",
        "--min-accepted-ratio",
    ]:
        if required not in text:
            raise AssertionError(required)


def test_recorder_defaults_do_not_create_source() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    for required in [
        'parser.add_argument("--start-converter", action="store_true")',
        'parser.add_argument("--start-adapter", action="store_true")',
        'parser.add_argument("--source-topic", default="/position_cmd")',
        'parser.add_argument("--duration-s", type=float, default=10.0)',
    ]:
        if required not in text:
            raise AssertionError(required)


def test_b0_contract_replay_is_not_planner() -> None:
    text = REPLAY.read_text(encoding="utf-8")
    for required in [
        "B0 smoke-only",
        "This is not a planner",
        "does not consume a local map",
        "PositionCommand",
        "--rate-hz",
        "--duration-s",
        "trajectory_id",
        "trajectory_flag",
        "frame_id",
    ]:
        if required not in text:
            raise AssertionError(required)
    if "PointCloud2" in text or "OccupancyGrid" in text or "create_subscription" in text:
        raise AssertionError("B0 contract replay must not consume map or odometry inputs")


def test_b0_orchestrator_claim_boundary() -> None:
    text = ORCHESTRATOR.read_text(encoding="utf-8")
    for required in [
        "B0 remains contract evidence only",
        "not planner closure",
        "smoke_only",
        "not_planner_closure",
        "/mosim/",
        "publish_position_command_contract_replay.py",
        "record_position_command_adapter_runtime.py",
    ]:
        if required not in text:
            raise AssertionError(required)


def main() -> int:
    test_recorder_is_passive_and_source_labeled()
    test_recorder_artifact_contract()
    test_recorder_defaults_do_not_create_source()
    test_b0_contract_replay_is_not_planner()
    test_b0_orchestrator_claim_boundary()
    print("[OK] PositionCommand runtime recorder static contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
