#!/usr/bin/env python3
"""Capture Gazebo pose truth by repeatedly sampling a transport topic.

`ign topic -e` can be brittle when used as a long-running pipe in short
bounded gates: depending on startup timing, the recorder may receive no data
even when `ign topic -e -n 1` succeeds moments later. This helper uses bounded
single-sample probes and writes the same JSONL/summary shape as
`record_gazebo_pose_truth.py`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Any

from record_gazebo_pose_truth import parse_samples, project_path, rel


def run_sample(command: str, topic: str, sample_timeout_s: float) -> tuple[str, str, int]:
    try:
        completed = subprocess.run(
            [command, "topic", "-e", "-t", topic, "-n", "1"],
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=sample_timeout_s,
        )
        return completed.stdout, completed.stderr, int(completed.returncode)
    except subprocess.TimeoutExpired as exc:
        return exc.stdout or "", exc.stderr or "sample timeout", 124


def run_stream(command: str, topic: str, stream_seconds: float) -> tuple[str, str, int]:
    try:
        completed = subprocess.run(
            [command, "topic", "-e", "-t", topic],
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=max(stream_seconds, 0.1),
        )
        return completed.stdout, completed.stderr, int(completed.returncode)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return stdout, stderr, 124


def dedupe(samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    unique: list[dict[str, Any]] = []
    for sample in samples:
        key = (
            sample.get("time"),
            tuple(sample.get("position_m") or []),
            tuple(sample.get("orientation_xyzw") or []),
        )
        if key in seen:
            continue
        seen.add(key)
        sample = dict(sample)
        sample["seq"] = len(unique)
        unique.append(sample)
    return unique


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-jsonl", required=True, type=Path)
    parser.add_argument("--summary-json", required=True, type=Path)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--command", default="ign")
    parser.add_argument("--timeout-seconds", type=float, default=15.0)
    parser.add_argument("--min-duration-seconds", type=float, default=0.0)
    parser.add_argument("--sample-timeout-seconds", type=float, default=25.0)
    parser.add_argument("--target-samples", type=int, default=20)
    parser.add_argument("--sleep-seconds", type=float, default=0.1)
    parser.add_argument("--startup-delay-seconds", type=float, default=0.0)
    parser.add_argument("--capture-mode", choices=["sample", "stream"], default="sample")
    args = parser.parse_args()

    output_jsonl = project_path(args.output_jsonl)
    summary_json = project_path(args.summary_json)
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    summary_json.parent.mkdir(parents=True, exist_ok=True)

    start_monotonic = time.monotonic()
    deadline = start_monotonic + max(args.timeout_seconds, 0.1)
    attempts: list[dict[str, Any]] = []
    samples: list[dict[str, Any]] = []
    startup_delay = max(args.startup_delay_seconds, 0.0)
    if startup_delay:
        time.sleep(startup_delay)

    def observed_duration() -> float:
        if len(samples) < 2:
            return 0.0
        try:
            return float(samples[-1].get("time", 0.0)) - float(samples[0].get("time", 0.0))
        except (TypeError, ValueError):
            return 0.0

    while time.monotonic() < deadline and (
        len(samples) < args.target_samples or observed_duration() < max(args.min_duration_seconds, 0.0)
    ):
        if args.capture_mode == "stream":
            remaining = max(0.1, min(args.sample_timeout_seconds, deadline - time.monotonic()))
            stdout, stderr, returncode = run_stream(args.command, args.topic, remaining)
        else:
            stdout, stderr, returncode = run_sample(args.command, args.topic, args.sample_timeout_seconds)
        capture_elapsed_s = time.monotonic() - start_monotonic
        parsed = parse_samples(
            stdout,
            model_name=args.model_name,
            topic=args.topic,
            frame_id=args.frame_id,
        )
        for sample in parsed:
            if sample.get("time_source") == "synthetic_order":
                sample["time"] = round(capture_elapsed_s, 6)
                sample["time_source"] = "capture_elapsed"
        attempts.append(
            {
                "returncode": returncode,
                "capture_mode": args.capture_mode,
                "stdout_bytes": len(stdout.encode("utf-8", errors="replace")),
                "stderr_tail": stderr[-500:],
                "parsed_samples": len(parsed),
            }
        )
        samples.extend(parsed)
        samples = dedupe(samples)
        if len(samples) >= args.target_samples and observed_duration() >= max(args.min_duration_seconds, 0.0):
            break
        time.sleep(max(args.sleep_seconds, 0.0))

    with output_jsonl.open("w", encoding="utf-8", newline="\n") as handle:
        for index, sample in enumerate(samples):
            sample = dict(sample)
            sample["seq"] = index
            handle.write(json.dumps(sample, ensure_ascii=False, separators=(",", ":")) + "\n")

    summary = {
        "schema": "mosim.gazebo_pose_truth_recording.v1",
        "status": "recorded" if samples else "blocked_no_samples",
        "topic": args.topic,
        "model_name": args.model_name,
        "frame_id": args.frame_id,
        "count": len(samples),
        "capture_method": "bounded_ign_topic_n1_retry",
        "capture_mode": args.capture_mode,
        "capture_command": args.command,
        "timeout_seconds": args.timeout_seconds,
        "min_duration_seconds": args.min_duration_seconds,
        "target_samples": args.target_samples,
        "startup_delay_seconds": args.startup_delay_seconds,
        "attempt_count": len(attempts),
        "attempts_tail": attempts[-10:],
        "time_sources": {
            "header_stamp": len([sample for sample in samples if sample.get("time_source") == "header_stamp"]),
            "synthetic_order": len([sample for sample in samples if sample.get("time_source") == "synthetic_order"]),
            "capture_elapsed": len([sample for sample in samples if sample.get("time_source") == "capture_elapsed"]),
        },
        "outputs": {
            "truth_pose_jsonl": rel(output_jsonl),
        },
        "claim_boundary": [
            "Gazebo transport pose truth only; no FAST-LIO quality claim by itself.",
            "This file is intended for same-run comparison against estimator odometry.",
        ],
    }
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if samples else 3


if __name__ == "__main__":
    raise SystemExit(main())
