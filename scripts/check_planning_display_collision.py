#!/usr/bin/env python3
"""Check a Sysplorer planning display trajectory against rendered pillar obstacles."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path


def parse_real_array(text: str, name: str) -> list[float]:
    match = re.search(rf"{re.escape(name)}\s*=\s*\{{([^}}]*)\}}", text)
    if not match:
        raise ValueError(f"Missing array parameter: {name}")
    return [float(item.strip()) for item in match.group(1).split(",") if item.strip()]


def parse_pillar_centers(text: str) -> list[tuple[float, float]]:
    match = re.search(r"pillar_center\s*=\s*\{(.*?)\}\s*,\s*pillar_width", text, re.S)
    if not match:
        raise ValueError("Missing pillar_center parameter before pillar_width")
    centers: list[tuple[float, float]] = []
    for pair in re.findall(r"\{([^{}]+)\}", match.group(1)):
        values = [float(item.strip()) for item in pair.split(",") if item.strip()]
        if len(values) == 2:
            centers.append((values[0], values[1]))
    return centers


def parse_int_parameter(text: str, name: str, default: int) -> int:
    match = re.search(rf"{re.escape(name)}\s*=\s*(\d+)", text)
    return int(match.group(1)) if match else default


def segment_min_distance(
    a: tuple[float, float],
    b: tuple[float, float],
    centers: list[tuple[float, float]],
    sample_step_m: float,
) -> tuple[float, int]:
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    steps = max(1, math.ceil(length / sample_step_m))
    best_distance = float("inf")
    best_index = -1
    for step in range(steps + 1):
        ratio = step / steps
        x = a[0] + (b[0] - a[0]) * ratio
        y = a[1] + (b[1] - a[1]) * ratio
        for index, center in enumerate(centers, start=1):
            distance = math.hypot(x - center[0], y - center[1])
            if distance < best_distance:
                best_distance = distance
                best_index = index
    return best_distance, best_index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", type=Path)
    parser.add_argument("--required-clearance-m", type=float, default=0.35)
    parser.add_argument("--sample-step-m", type=float, default=0.01)
    args = parser.parse_args()

    text = args.model.read_text(encoding="utf-8")
    n_segments_match = re.search(r"n_segments\s*=\s*(\d+)", text)
    if not n_segments_match:
        raise ValueError("Missing n_segments parameter")
    n_segments = int(n_segments_match.group(1))
    p_x = parse_real_array(text, "p_x")
    p_y = parse_real_array(text, "p_y")
    centers = parse_pillar_centers(text)
    pillar_count = parse_int_parameter(text, "pillar_count", len(centers))
    active_centers = centers[:pillar_count]

    points = list(zip(p_x, p_y))[: n_segments + 1]
    if len(points) < n_segments + 1:
        raise ValueError(f"Expected at least {n_segments + 1} trajectory points, got {len(points)}")

    print(f"model: {args.model}")
    print(f"n_segments: {n_segments}")
    print(f"required_clearance_m: {args.required_clearance_m:.3f}")
    ok = True
    for index, (a, b) in enumerate(zip(points, points[1:]), start=1):
        distance, pillar_index = segment_min_distance(a, b, active_centers, args.sample_step_m)
        status = "OK" if distance >= args.required_clearance_m else "COLLISION_RISK"
        print(
            f"segment {index}: {a} -> {b}, "
            f"min_center_distance_m={distance:.3f}, nearest_pillar={pillar_index}, {status}"
        )
        if distance < args.required_clearance_m:
            ok = False
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
