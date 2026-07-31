#!/usr/bin/env python3
"""Guard the three-UAV OpenBlocks display trajectory binding shape."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODEL = ROOT / "Models" / "MoSimQuadrotorModel" / "Guidance" / "Planning" / "ThreeUavOpenBlocksReconfigurableFormationLinearMPC.mo"


def component_body(source: str, component_name: str) -> str:
    match = re.search(rf"(?s)\b{re.escape(component_name)}\s*\((.*?)\)\s*annotation", source)
    if not match:
        raise AssertionError(f"Missing component declaration: {component_name}")
    return match.group(1)


def literal_vector(body: str, field_name: str) -> list[str]:
    match = re.search(rf"\b{re.escape(field_name)}\s*=\s*\{{", body)
    if not match:
        raise AssertionError(f"Missing vector binding: {field_name}")
    start = match.end()
    depth = 1
    cursor = start
    while cursor < len(body) and depth:
        if body[cursor] == "{":
            depth += 1
        elif body[cursor] == "}":
            depth -= 1
        cursor += 1
    if depth:
        raise AssertionError(f"Unclosed vector binding: {field_name}")
    return re.findall(r"(?<![A-Za-z_])[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?", body[start : cursor - 1])


def main() -> int:
    source = MODEL.read_text(encoding="utf-8")
    reference = component_body(source, "reference1")
    display = component_body(source, "navigationDisplay")
    expected_lengths = {"p_x": 91, "p_y": 91, "p_z": 91, "segment_duration": 90}
    for field_name, expected_length in expected_lengths.items():
        reference_values = literal_vector(reference, field_name)
        display_values = literal_vector(display, field_name)
        assert len(reference_values) == expected_length, (field_name, len(reference_values), expected_length)
        assert len(display_values) == expected_length, (field_name, len(display_values), expected_length)
        assert display_values == reference_values, f"navigationDisplay.{field_name} differs from reference1.{field_name}"
    print("[OK] Three-UAV OpenBlocks display/reference trajectory contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
