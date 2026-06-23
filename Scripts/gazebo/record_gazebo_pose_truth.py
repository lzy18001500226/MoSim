#!/usr/bin/env python3
"""Record a Gazebo transport pose stream as compact JSONL.

This helper reads `ign topic -e`/`gz topic -e` protobuf-text output from stdin
and extracts one named model pose into `gazebo_truth_pose.jsonl`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def number_after(label: str, text: str) -> float | None:
    match = re.search(rf"^\s*{re.escape(label)}:\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s*$", text, re.M)
    return float(match.group(1)) if match else None


def string_after(label: str, text: str) -> str | None:
    match = re.search(rf'^\s*{re.escape(label)}:\s*"([^"]+)"\s*$', text, re.M)
    return match.group(1) if match else None


def first_balanced_block(text: str, label: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(label)}\s*\{{", text)
    if not match:
        return None
    brace = text.find("{", match.start())
    depth = 0
    for index in range(brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[brace + 1 : index]
    return None


def parse_header_time(block: str) -> float | None:
    header = first_balanced_block(block, "header")
    if header is None:
        return None
    stamp = first_balanced_block(header, "stamp") or header
    sec = number_after("sec", stamp)
    nsec = number_after("nsec", stamp)
    if nsec is None:
        nsec = number_after("nanosec", stamp)
    if sec is None:
        return None
    return float(sec) + float(nsec or 0.0) * 1e-9


def iter_pose_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    index = 0
    while True:
        start = text.find("pose {", index)
        if start < 0:
            break
        brace = text.find("{", start)
        depth = 0
        end = brace
        while end < len(text):
            if text[end] == "{":
                depth += 1
            elif text[end] == "}":
                depth -= 1
                if depth == 0:
                    blocks.append(text[start : end + 1])
                    index = end + 1
                    break
            end += 1
        else:
            break
    return blocks


def xyz_from_section(block: str, section: str) -> list[float]:
    match = re.search(rf"{re.escape(section)}\s*\{{(?P<body>.*?)^\s*\}}", block, re.S | re.M)
    body = match.group("body") if match else ""
    return [
        float(number_after("x", body) or 0.0),
        float(number_after("y", body) or 0.0),
        float(number_after("z", body) or 0.0),
    ]


def xyzw_from_orientation(block: str) -> list[float]:
    match = re.search(r"orientation\s*\{(?P<body>.*?)^\s*\}", block, re.S | re.M)
    body = match.group("body") if match else ""
    return [
        float(number_after("x", body) or 0.0),
        float(number_after("y", body) or 0.0),
        float(number_after("z", body) or 0.0),
        float(number_after("w", body) if number_after("w", body) is not None else 1.0),
    ]


def iter_message_chunks(text: str) -> list[str]:
    explicit_chunks = [chunk for chunk in re.split(r"(?m)^---\s*$", text) if chunk.strip()]
    chunks: list[str] = []
    for chunk in explicit_chunks:
        starts = [match.start() for match in re.finditer(r"(?m)^header\s*\{", chunk)]
        if len(starts) <= 1:
            chunks.append(chunk)
            continue
        starts.append(len(chunk))
        for index in range(len(starts) - 1):
            message = chunk[starts[index] : starts[index + 1]].strip()
            if message:
                chunks.append(message)
    return chunks


def parse_samples(text: str, *, model_name: str, topic: str, frame_id: str) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for chunk in iter_message_chunks(text):
        time_s = parse_header_time(chunk)
        pose_blocks = iter_pose_blocks(chunk)
        if not pose_blocks and re.search(r"(?m)^position\s*\{", chunk):
            pose_blocks = [chunk]
        for pose_block in pose_blocks:
            actual_name = string_after("name", pose_block)
            if actual_name != model_name and not (actual_name or "").endswith(f"::{model_name}"):
                continue
            time_source = "header_stamp" if time_s is not None else "synthetic_order"
            samples.append(
                {
                    "schema": "mosim.gazebo_pose_truth_sample.v1",
                    "seq": len(samples),
                    "time": round(float(time_s if time_s is not None else len(samples) * 1e-6), 6),
                    "time_source": time_source,
                    "frame_id": frame_id,
                    "source_topic": topic,
                    "model_name": model_name,
                    "source_entity_name": actual_name,
                    "position_m": [round(value, 6) for value in xyz_from_section(pose_block, "position")],
                    "orientation_xyzw": [round(value, 9) for value in xyzw_from_orientation(pose_block)],
                }
            )
    return samples


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-jsonl", required=True, type=Path)
    parser.add_argument("--summary-json", required=True, type=Path)
    parser.add_argument("--topic", default="/world/mosim_factory_minimal/dynamic_pose/info")
    parser.add_argument("--model-name", default="sunray150")
    parser.add_argument("--frame-id", default="world")
    args = parser.parse_args()

    output_jsonl = project_path(args.output_jsonl)
    summary_json = project_path(args.summary_json)
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    summary_json.parent.mkdir(parents=True, exist_ok=True)

    raw = sys.stdin.read()
    samples = parse_samples(raw, model_name=args.model_name, topic=args.topic, frame_id=args.frame_id)
    with output_jsonl.open("w", encoding="utf-8", newline="\n") as handle:
        for sample in samples:
            handle.write(json.dumps(sample, ensure_ascii=False, separators=(",", ":")) + "\n")

    summary = {
        "schema": "mosim.gazebo_pose_truth_recording.v1",
        "status": "recorded" if samples else "blocked_no_samples",
        "topic": args.topic,
        "model_name": args.model_name,
        "frame_id": args.frame_id,
        "count": len(samples),
        "time_sources": {
            "header_stamp": len([sample for sample in samples if sample.get("time_source") == "header_stamp"]),
            "synthetic_order": len([sample for sample in samples if sample.get("time_source") == "synthetic_order"]),
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
