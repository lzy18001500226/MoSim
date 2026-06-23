#!/usr/bin/env python3
"""Capture Gazebo pose truth from a SerializedStepMap state topic.

Fortress may expose a model/link pose topic with a publisher but no samples for
the current assembled Sunray world. The world state topic still carries entity
pose components. This helper records a compact truth pose JSONL compatible with
the existing Gazebo truth evaluators.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import time
from pathlib import Path
from typing import Any

from record_gazebo_pose_truth import project_path, rel


POSE_COMPONENT_TYPE = "6612894081701502240"


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


def state_service_from_topic(topic: str) -> str | None:
    match = re.match(r"^(/world/[^/]+)/state$", topic)
    return match.group(1) + "/state" if match else None


def run_state_service(command: str, service: str, sample_timeout_s: float) -> tuple[str, str, int]:
    try:
        completed = subprocess.run(
            [
                command,
                "service",
                "-s",
                service,
                "--reqtype",
                "ignition.msgs.Empty",
                "--reptype",
                "ignition.msgs.SerializedStepMap",
                "--timeout",
                str(max(1, int(sample_timeout_s * 1000))),
                "--req",
                "",
            ],
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=sample_timeout_s + 1.0,
        )
        return completed.stdout, completed.stderr, int(completed.returncode)
    except subprocess.TimeoutExpired as exc:
        return exc.stdout or "", exc.stderr or "service timeout", 124


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


def iter_state_message_chunks(text: str) -> list[str]:
    chunks: list[str] = []
    buffer: list[str] = []
    for line in text.splitlines(keepends=True):
        if line.strip() == "---":
            chunk = "".join(buffer).strip()
            if chunk:
                chunks.append(chunk)
            buffer = []
            continue
        if line.startswith("stats {") and buffer:
            chunk = "".join(buffer).strip()
            if chunk:
                chunks.append(chunk)
            buffer = [line]
            continue
        buffer.append(line)
    chunk = "".join(buffer).strip()
    if chunk:
        chunks.append(chunk)
    return chunks


def number_after(label: str, text: str) -> float | None:
    match = re.search(rf"^\s*{re.escape(label)}:\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s*$", text, re.M)
    return float(match.group(1)) if match else None


def parse_sim_time(text: str) -> float | None:
    stats_match = re.search(r"stats\s*\{(?P<body>.*?)^state\s*\{", text, re.S | re.M)
    body = stats_match.group("body") if stats_match else text
    sim_match = re.search(r"sim_time\s*\{(?P<body>.*?)^\s*\}", body, re.S | re.M)
    sim = sim_match.group("body") if sim_match else ""
    sec = number_after("sec", sim) or 0.0
    nsec = number_after("nsec", sim) or 0.0
    return float(sec) + float(nsec) * 1e-9


def euler_to_quat_xyz_w(roll: float, pitch: float, yaw: float) -> list[float]:
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    return [
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    ]


def iter_entity_blocks(text: str) -> list[tuple[int | None, str]]:
    blocks: list[tuple[int | None, str]] = []
    for match in re.finditer(r"entities\s*\{", text):
        start = match.start()
        brace = text.find("{", start)
        depth = 0
        end = brace
        while end < len(text):
            if text[end] == "{":
                depth += 1
            elif text[end] == "}":
                depth -= 1
                if depth == 0:
                    block = text[start : end + 1]
                    id_match = re.search(r"^\s*id:\s*(\d+)\s*$", block, re.M)
                    entity_id = int(id_match.group(1)) if id_match else None
                    blocks.append((entity_id, block))
                    break
            end += 1
    return blocks


def pose_from_entity_block(block: str) -> list[float] | None:
    component_match = re.search(
        rf'type:\s*{POSE_COMPONENT_TYPE}.*?component:\s*"([^"]+)"',
        block,
        re.S,
    )
    if not component_match:
        return None
    values = [float(item) for item in component_match.group(1).split()]
    if len(values) != 6:
        return None
    return values


def choose_body_pose(
    candidates: list[tuple[int | None, list[float]]],
    *,
    expected_entity_id: int | None = None,
) -> tuple[int | None, list[float], dict[str, Any]] | None:
    if not candidates:
        return None

    if expected_entity_id is not None:
        for entity_id, pose in candidates:
            if entity_id == expected_entity_id:
                details = {
                    "selection_policy": "expected_entity_id",
                    "candidate_count": len(candidates),
                    "expected_entity_id": expected_entity_id,
                    "selected_entity_id": entity_id,
                    "selected_score": 0.0,
                }
                return entity_id, pose, details
        return None

    def score(item: tuple[int | None, list[float]]) -> float:
        _, pose = item
        x, y, z = pose[:3]
        # The accepted light-world UAV starts at (0, 0, 1.2). Obstacles are
        # also near z=1, so XY proximity is the primary discriminator.
        return (x * x + y * y) + 4.0 * ((z - 1.2) ** 2)

    plausible = [item for item in candidates if 0.5 <= item[1][2] <= 2.5]
    chosen = min(plausible or candidates, key=score)
    entity_id, pose = chosen
    details = {
        "selection_policy": "nearest_to_initial_uav_body_pose_xyz_0_0_1p2",
        "candidate_count": len(candidates),
        "plausible_candidate_count": len(plausible),
        "selected_entity_id": entity_id,
        "selected_score": score(chosen),
    }
    return entity_id, pose, details


def parse_samples(
    text: str,
    *,
    topic: str,
    model_name: str,
    frame_id: str,
    expected_entity_id: int | None = None,
) -> list[dict[str, Any]]:
    sim_time = parse_sim_time(text)
    candidates: list[tuple[int | None, list[float]]] = []
    for entity_id, block in iter_entity_blocks(text):
        pose = pose_from_entity_block(block)
        if pose is not None:
            candidates.append((entity_id, pose))
    chosen = choose_body_pose(candidates, expected_entity_id=expected_entity_id)
    if chosen is None:
        return []
    entity_id, pose, details = chosen
    quat = euler_to_quat_xyz_w(pose[3], pose[4], pose[5])
    return [
        {
            "schema": "mosim.gazebo_pose_truth_sample.v1",
            "seq": 0,
            "time": round(float(sim_time if sim_time is not None else 0.0), 6),
            "time_source": "state_stats_sim_time" if sim_time is not None else "synthetic_order",
            "frame_id": frame_id,
            "source_topic": topic,
            "source_kind": "gazebo_transport_serialized_step_map_state",
            "model_name": model_name,
            "source_entity_id": entity_id,
            "position_m": [round(value, 6) for value in pose[:3]],
            "orientation_xyzw": [round(value, 9) for value in quat],
            "entity_selection": details,
        }
    ]


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
        row = dict(sample)
        row["seq"] = len(unique)
        unique.append(row)
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
    parser.add_argument("--sample-timeout-seconds", type=float, default=8.0)
    parser.add_argument("--target-samples", type=int, default=20)
    parser.add_argument("--sleep-seconds", type=float, default=0.1)
    parser.add_argument("--expected-entity-id", type=int, default=None)
    parser.add_argument("--capture-mode", choices=["stream", "service", "topic", "auto"], default="auto")
    args = parser.parse_args()

    output_jsonl = project_path(args.output_jsonl)
    summary_json = project_path(args.summary_json)
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    summary_json.parent.mkdir(parents=True, exist_ok=True)

    deadline = time.monotonic() + max(args.timeout_seconds, 0.1)
    attempts: list[dict[str, Any]] = []
    samples: list[dict[str, Any]] = []
    service = state_service_from_topic(args.topic)

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
        capture_mode = args.capture_mode
        if capture_mode == "auto":
            capture_mode = "stream"
        if capture_mode == "stream":
            remaining = max(0.1, min(args.sample_timeout_seconds, deadline - time.monotonic()))
            stdout, stderr, returncode = run_stream(args.command, args.topic, remaining)
            chunks = iter_state_message_chunks(stdout)
            parsed: list[dict[str, Any]] = []
            for chunk in chunks:
                parsed.extend(
                    parse_samples(
                        chunk,
                        topic=args.topic,
                        model_name=args.model_name,
                        frame_id=args.frame_id,
                        expected_entity_id=args.expected_entity_id,
                    )
                )
        elif capture_mode == "service" and service:
            stdout, stderr, returncode = run_state_service(args.command, service, args.sample_timeout_seconds)
            parsed = parse_samples(
                stdout,
                topic=args.topic,
                model_name=args.model_name,
                frame_id=args.frame_id,
                expected_entity_id=args.expected_entity_id,
            )
        else:
            stdout, stderr, returncode = run_sample(args.command, args.topic, args.sample_timeout_seconds)
            parsed = parse_samples(
                stdout,
                topic=args.topic,
                model_name=args.model_name,
                frame_id=args.frame_id,
                expected_entity_id=args.expected_entity_id,
            )
        attempts.append(
            {
                "returncode": returncode,
                "capture_mode": capture_mode,
                "service": service if capture_mode == "service" else None,
                "stdout_bytes": len(stdout.encode("utf-8", errors="replace")),
                "stderr_tail": stderr[-500:],
                "chunk_count": len(iter_state_message_chunks(stdout)) if capture_mode == "stream" else None,
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
            row = dict(sample)
            row["seq"] = index
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    first_selection = samples[0].get("entity_selection") if samples else None
    summary = {
        "schema": "mosim.gazebo_pose_truth_recording.v1",
        "status": "recorded" if samples else "blocked_no_samples",
        "topic": args.topic,
        "model_name": args.model_name,
        "frame_id": args.frame_id,
        "count": len(samples),
        "capture_method": "bounded_ign_state_topic_n1_retry",
        "capture_mode": args.capture_mode,
        "state_service": service,
        "source_kind": "gazebo_transport_serialized_step_map_state",
        "capture_command": args.command,
        "timeout_seconds": args.timeout_seconds,
        "min_duration_seconds": args.min_duration_seconds,
        "target_samples": args.target_samples,
        "expected_entity_id": args.expected_entity_id,
        "attempt_count": len(attempts),
        "attempts_tail": attempts[-10:],
        "entity_selection": first_selection,
        "time_sources": {
            "state_stats_sim_time": len([sample for sample in samples if sample.get("time_source") == "state_stats_sim_time"]),
            "synthetic_order": len([sample for sample in samples if sample.get("time_source") == "synthetic_order"]),
        },
        "outputs": {
            "truth_pose_jsonl": rel(output_jsonl),
        },
        "claim_boundary": [
            "Gazebo SerializedStepMap state pose truth only; no FAST-LIO quality claim by itself.",
            "Entity selection is automatic and recorded for same-run pre-acceptance comparison.",
        ],
    }
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if samples else 3


if __name__ == "__main__":
    raise SystemExit(main())
