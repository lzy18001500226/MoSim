#!/usr/bin/env python3
"""Run the B0 smoke-only PositionCommand contract replay through the recorder.

This orchestrates the replay source and passive recorder without shell PID
tricks. B0 remains contract evidence only; it is not planner closure.
"""

from __future__ import annotations

import argparse
import json
import signal
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def terminate(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.send_signal(signal.SIGINT)
    try:
        process.wait(timeout=3.0)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=3.0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="positioncmd_b0_contract_replay_20260606")
    parser.add_argument("--duration-s", type=float, default=10.0)
    parser.add_argument("--source-duration-s", type=float, default=18.0)
    parser.add_argument("--source-rate-hz", type=float, default=20.0)
    parser.add_argument("--adapter-rate-hz", type=float, default=25.0)
    parser.add_argument("--stale-timeout-s", type=float, default=0.3)
    parser.add_argument("--startup-wait-s", type=float, default=2.0)
    parser.add_argument("--min-rate-hz", type=float, default=19.0)
    args = parser.parse_args()

    topic_prefix = f"/mosim/{args.run_id}"
    source_topic = f"{topic_prefix}/position_cmd"
    converted_topic = f"{topic_prefix}/planner_position_cmd"
    setpoint_topic = f"{topic_prefix}/setpoint"
    status_topic = f"{topic_prefix}/setpoint_adapter_status"
    output_dir = project_path(Path("Results") / "ros2_runtime" / args.run_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    source_log = output_dir / "b0_contract_replay_source.log"
    recorder_log = output_dir / "b0_contract_replay_recorder.log"

    with source_log.open("wb") as source_handle:
        source = subprocess.Popen(
            [
                sys.executable,
                str(ROOT / "Scripts" / "ros" / "publish_position_command_contract_replay.py"),
                "--topic",
                source_topic,
                "--duration-s",
                str(args.source_duration_s),
                "--rate-hz",
                str(args.source_rate_hz),
            ],
            stdout=source_handle,
            stderr=subprocess.STDOUT,
        )
    try:
        time.sleep(float(args.startup_wait_s))
        with recorder_log.open("wb") as recorder_handle:
            recorder = subprocess.Popen(
                [
                    sys.executable,
                    str(ROOT / "Scripts" / "ros" / "record_position_command_adapter_runtime.py"),
                    "--duration-s",
                    str(args.duration_s),
                    "--output-dir",
                    str(output_dir),
                    "--start-converter",
                    "--start-adapter",
                    "--source-topic",
                    source_topic,
                    "--converted-topic",
                    converted_topic,
                    "--setpoint-topic",
                    setpoint_topic,
                    "--status-topic",
                    status_topic,
                    "--planner-id",
                    "ego_position_cmd",
                    "--adapter-rate-hz",
                    str(args.adapter_rate_hz),
                    "--stale-timeout-s",
                    str(args.stale_timeout_s),
                    "--min-rate-hz",
                    str(args.min_rate_hz),
                    "--planner-input-notes",
                    (
                        "B0 contract replay only; no local map or odom input; "
                        "global_truth_used_as_input=false; smoke_only."
                    ),
                ],
                stdout=recorder_handle,
                stderr=subprocess.STDOUT,
            )
            recorder_code = recorder.wait()
    finally:
        terminate(source)

    summary_path = output_dir / "run_summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["b0_contract_replay"] = {
            "smoke_only": True,
            "not_planner_closure": True,
            "source_script": "Scripts/ros/publish_position_command_contract_replay.py",
            "orchestrator": "Scripts/ros/run_b0_position_command_contract_replay.py",
        }
        summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"ok": False, "error": "missing run_summary.json"}, ensure_ascii=False), file=sys.stderr)
        return 3
    return int(recorder_code)


if __name__ == "__main__":
    raise SystemExit(main())
