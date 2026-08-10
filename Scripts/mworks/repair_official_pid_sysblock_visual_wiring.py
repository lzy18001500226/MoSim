#!/usr/bin/env python3
"""Repair missing or degenerate graphical Line metadata without changing topology."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
IDENTIFIER = r"[A-Za-z_]\w*"
INDEX = r"(?:\s*\[[^\[\]]+\])*"
ENDPOINT = rf"{IDENTIFIER}{INDEX}(?:\s*\.\s*{IDENTIFIER}{INDEX})*"
CONNECT_RE = re.compile(
    r"\bconnect\s*\(\s*"
    rf"(?P<source>{ENDPOINT})\s*,\s*"
    rf"(?P<target>{ENDPOINT})\s*\)",
    re.MULTILINE,
)
EQUATION_RE = re.compile(r"(?m)^\s*equation\s*$")
COMPONENT_DECL_RE = re.compile(
    rf"(?m)^\s*(?:(?:final|inner|outer|replaceable|parameter|constant|discrete|"
    rf"input|output|flow|stream|each)\s+)*(?:{IDENTIFIER}\.)*{IDENTIFIER}\s+"
    rf"(?P<name>{IDENTIFIER})\b"
)
EXTENT_RE = re.compile(
    rf"\bextent\s*=\s*\{{\{{\s*(?P<x1>{NUMBER})\s*,\s*(?P<y1>{NUMBER})\s*\}}\s*,\s*"
    rf"\{{\s*(?P<x2>{NUMBER})\s*,\s*(?P<y2>{NUMBER})\s*\}}\s*\}}"
)
ORIGIN_RE = re.compile(
    rf"\borigin\s*=\s*\{{\s*(?P<x>{NUMBER})\s*,\s*(?P<y>{NUMBER})\s*\}}"
)
POINT_RE = re.compile(rf"\{{\s*({NUMBER})\s*,\s*({NUMBER})\s*\}}")


class VisualWiringError(ValueError):
    """Raised when visual metadata cannot be repaired safely."""


@dataclass(frozen=True)
class Box:
    left: float
    bottom: float
    right: float
    top: float

    @property
    def center_x(self) -> float:
        return (self.left + self.right) / 2

    @property
    def center_y(self) -> float:
        return (self.bottom + self.top) / 2


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def resolve_project_path(value: Path) -> Path:
    path = value if value.is_absolute() else ROOT / value
    path = path.resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as error:
        raise VisualWiringError(f"path escapes project root: {value}") from error
    return path


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def scan_call_end(text: str, open_paren: int) -> int:
    if open_paren >= len(text) or text[open_paren] != "(":
        raise VisualWiringError("expected opening parenthesis")
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(open_paren, len(text)):
        character = text[index]
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in {"'", '"'}:
            quote = character
        elif character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                return index + 1
            if depth < 0:
                break
    raise VisualWiringError("unbalanced parenthesis")


def statement_end(text: str, start: int, limit: int | None = None) -> int:
    end = len(text) if limit is None else limit
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(start, end):
        character = text[index]
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in {"'", '"'}:
            quote = character
        elif character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
        elif character == ";" and depth == 0:
            return index + 1
    raise VisualWiringError("unable to locate Modelica statement terminator")


def token_call_span(text: str, token: str, start: int, end: int) -> tuple[int, int] | None:
    match = re.compile(rf"\b{re.escape(token)}\s*\(").search(text, start, end)
    if match is None:
        return None
    open_paren = text.find("(", match.start(), end)
    finish = scan_call_end(text, open_paren)
    if finish > end:
        raise VisualWiringError(f"{token}() extends beyond its statement")
    return match.start(), finish


def split_statements(text: str, end: int) -> list[tuple[int, int]]:
    statements: list[tuple[int, int]] = []
    cursor = 0
    while cursor < end:
        try:
            finish = statement_end(text, cursor, end)
        except VisualWiringError:
            break
        statements.append((cursor, finish))
        cursor = finish
    return statements


def parse_box(placement: str) -> Box:
    extent = EXTENT_RE.search(placement)
    if extent is None:
        raise VisualWiringError("Placement has no rectangular extent")
    origin = ORIGIN_RE.search(placement)
    origin_x = float(origin.group("x")) if origin else 0.0
    origin_y = float(origin.group("y")) if origin else 0.0
    x1 = origin_x + float(extent.group("x1"))
    y1 = origin_y + float(extent.group("y1"))
    x2 = origin_x + float(extent.group("x2"))
    y2 = origin_y + float(extent.group("y2"))
    return Box(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))


def parenthesis_depths(text: str, end: int) -> list[int]:
    depths = [0] * end
    depth = 0
    quote: str | None = None
    escaped = False
    for index, character in enumerate(text[:end]):
        depths[index] = depth
        if quote:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
            continue
        if character in {"'", '"'}:
            quote = character
        elif character == "(":
            depth += 1
        elif character == ")":
            depth = max(0, depth - 1)
    return depths


def component_declarations(text: str, equation_start: int) -> list[tuple[str, int, int]]:
    ignored_starts = {
        "algorithm",
        "annotation",
        "end",
        "equation",
        "extends",
        "if",
        "import",
        "protected",
        "public",
        "within",
    }
    depths = parenthesis_depths(text, equation_start)
    declarations: list[tuple[str, int, int]] = []
    for declaration in COMPONENT_DECL_RE.finditer(text, 0, equation_start):
        if depths[declaration.start()] != 0:
            continue
        first = re.match(IDENTIFIER, text[declaration.start() :].lstrip())
        if first is not None and first.group(0) in ignored_starts:
            continue
        start = declaration.start()
        end = statement_end(text, start, equation_start)
        declarations.append((declaration.group("name"), start, end))
    return declarations


def component_boxes(text: str, equation_start: int) -> dict[str, Box]:
    boxes: dict[str, Box] = {}
    for name, start, end in component_declarations(text, equation_start):
        placement_span = token_call_span(text, "Placement", start, end)
        if placement_span is None:
            continue
        if name in boxes:
            raise VisualWiringError(f"duplicate component declaration: {name}")
        boxes[name] = parse_box(text[placement_span[0] : placement_span[1]])
    return boxes


def endpoint_component(endpoint: str) -> str:
    match = re.match(IDENTIFIER, endpoint.lstrip())
    if match is None:
        raise VisualWiringError(f"invalid connector endpoint: {endpoint}")
    return match.group(0)


def line_points(line: str) -> list[tuple[float, float]]:
    points_start = re.search(r"\bpoints\s*=", line)
    if points_start is None:
        return []
    return [
        (float(x), float(y))
        for x, y in POINT_RE.findall(line[points_start.start() :])
    ]


def valid_line(line: str) -> bool:
    points = line_points(line)
    return len(points) >= 2 and any(point != points[0] for point in points[1:])


def format_number(value: float) -> str:
    if not math.isfinite(value):
        raise VisualWiringError(f"non-finite route coordinate: {value}")
    rounded = round(value)
    if abs(value - rounded) < 1e-9:
        return str(int(rounded))
    return f"{value:.6f}".rstrip("0").rstrip(".")


def route_points(source: Box, target: Box) -> list[tuple[float, float]]:
    dx = target.center_x - source.center_x
    dy = target.center_y - source.center_y
    if abs(dx) >= abs(dy):
        forward = dx >= 0
        start = (source.right if forward else source.left, source.center_y)
        finish = (target.left if forward else target.right, target.center_y)
        if start[1] == finish[1]:
            return [start, finish]
        middle_x = (start[0] + finish[0]) / 2
        return [start, (middle_x, start[1]), (middle_x, finish[1]), finish]
    upward = dy >= 0
    start = (source.center_x, source.top if upward else source.bottom)
    finish = (target.center_x, target.bottom if upward else target.top)
    if start[0] == finish[0]:
        return [start, finish]
    middle_y = (start[1] + finish[1]) / 2
    return [start, (start[0], middle_y), (finish[0], middle_y), finish]


def line_text(points: list[tuple[float, float]]) -> str:
    rendered = ", ".join(
        "{" + format_number(x) + ", " + format_number(y) + "}"
        for x, y in points
    )
    return f"Line(points = {{{rendered}}}, color = {{0, 0, 127}})"


def connection_signature(text: str, equation_start: int) -> list[tuple[str, str]]:
    return [
        (match.group("source"), match.group("target"))
        for match in CONNECT_RE.finditer(text, equation_start)
    ]


def placement_signature(text: str, equation_start: int) -> dict[str, str]:
    signature: dict[str, str] = {}
    for name, start, end in component_declarations(text, equation_start):
        placement_span = token_call_span(text, "Placement", start, end)
        if placement_span:
            signature[name] = text[placement_span[0] : placement_span[1]]
    return signature


def audit_text(text: str) -> dict[str, Any]:
    equation = EQUATION_RE.search(text)
    if equation is None:
        raise VisualWiringError("source has no equation section")
    missing_lines: list[str] = []
    degenerate_lines: list[str] = []
    unplaced_endpoints: list[str] = []
    boundary_endpoints: list[str] = []
    boxes = component_boxes(text, equation.start())
    declared_components = {name for name, _, _ in component_declarations(text, equation.start())}
    connections = list(CONNECT_RE.finditer(text, equation.start()))
    for index, connection in enumerate(connections, start=1):
        source = connection.group("source")
        target = connection.group("target")
        source_component = endpoint_component(source)
        target_component = endpoint_component(target)
        label = f"{index}:{source}->{target}"
        for component in (source_component, target_component):
            if component in boxes:
                continue
            if component in declared_components:
                unplaced_endpoints.append(f"{label}:{component}")
            else:
                boundary_endpoints.append(f"{label}:{component}")
        finish = statement_end(text, connection.start())
        line_span = token_call_span(text, "Line", connection.start(), finish)
        if line_span is None:
            missing_lines.append(label)
        elif not valid_line(text[line_span[0] : line_span[1]]):
            degenerate_lines.append(label)
    return {
        "connect_count": len(connections),
        "missing_line_count": len(missing_lines),
        "degenerate_line_count": len(degenerate_lines),
        "unplaced_endpoint_count": len(unplaced_endpoints),
        "boundary_endpoint_count": len(boundary_endpoints),
        "missing_lines": missing_lines,
        "degenerate_lines": degenerate_lines,
        "unplaced_endpoints": unplaced_endpoints,
        "boundary_endpoints": boundary_endpoints,
        "ok": not missing_lines and not degenerate_lines and not unplaced_endpoints,
    }


def repair_text(source: str) -> tuple[str, dict[str, Any]]:
    equation = EQUATION_RE.search(source)
    if equation is None:
        raise VisualWiringError("source has no equation section")
    equation_start = equation.start()
    boxes = component_boxes(source, equation_start)
    declared_components = {name for name, _, _ in component_declarations(source, equation_start)}
    before_connections = connection_signature(source, equation_start)
    before_placements = placement_signature(source, equation_start)
    replacements: list[tuple[int, int, str]] = []
    added = 0
    repaired = 0
    retained = 0
    for connection in CONNECT_RE.finditer(source, equation_start):
        source_name = endpoint_component(connection.group("source"))
        target_name = endpoint_component(connection.group("target"))
        finish = statement_end(source, connection.start())
        span = token_call_span(source, "Line", connection.start(), finish)
        if span is not None and valid_line(source[span[0] : span[1]]):
            retained += 1
            continue
        if source_name not in boxes or target_name not in boxes:
            # Inherited boundary ports have no local Placement; do not invent their routes.
            boundary = [
                name for name in (source_name, target_name)
                if name not in boxes and name not in declared_components
            ]
            detail = "boundary" if boundary else "unplaced"
            raise VisualWiringError(
                f"{detail} connection endpoint has no safe route: "
                f"{connection.group('source')} -> {connection.group('target')}"
            )
        replacement = line_text(route_points(boxes[source_name], boxes[target_name]))
        if span is not None:
            replacements.append((span[0], span[1], replacement))
            repaired += 1
            continue
        line_start = source.rfind("\n", 0, connection.start()) + 1
        indent = re.match(r"[ \t]*", source[line_start : connection.start()]).group(0)
        replacements.append((finish - 1, finish - 1, f"\n{indent}  annotation({replacement})"))
        added += 1

    updated = source
    for start, end, replacement in sorted(replacements, reverse=True):
        updated = updated[:start] + replacement + updated[end:]
    updated_equation = EQUATION_RE.search(updated)
    if updated_equation is None:
        raise VisualWiringError("visual repair removed equation section")
    if before_connections != connection_signature(updated, updated_equation.start()):
        raise VisualWiringError("visual repair changed connect() topology")
    if before_placements != placement_signature(updated, updated_equation.start()):
        raise VisualWiringError("visual repair changed component Placement metadata")
    audit = audit_text(updated)
    if not audit["ok"]:
        raise VisualWiringError(f"visual repair did not close audit: {audit}")
    return updated, {
        **audit,
        "added_line_count": added,
        "repaired_line_count": repaired,
        "retained_line_count": retained,
        "placement_unchanged": True,
        "connect_topology_unchanged": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="project-relative Modelica source")
    parser.add_argument("--output", type=Path, help="target source; defaults to audit-only")
    parser.add_argument("--summary-output", type=Path, help="optional JSON provenance output")
    parser.add_argument("--allow-in-place", action="store_true", help="required for in-place writes")
    args = parser.parse_args(argv)

    try:
        source_path = resolve_project_path(args.source)
        if not source_path.is_file():
            raise VisualWiringError(f"source is missing: {repo_path(source_path)}")
        source = source_path.read_bytes().decode("utf-8")
        before = audit_text(source)
        summary: dict[str, Any] = {
            "schema": "mosim.official_pid_visual_wiring_repair.v1",
            "claim_boundary": "Visual Line metadata only; no component Placement, parameter, port, or connect() topology changes.",
            "source_model": repo_path(source_path),
            "before_sha256": sha256_text(source),
            "before": before,
        }
        if args.output is not None:
            output_path = resolve_project_path(args.output)
            if output_path == source_path and not args.allow_in_place:
                raise VisualWiringError("in-place write requires --allow-in-place")
            updated, repair = repair_text(source)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(updated.encode("utf-8"))
            summary.update(
                {
                    "output_model": repo_path(output_path),
                    "after_sha256": sha256_text(updated),
                    "repair": repair,
                }
            )
        if args.summary_output:
            summary_path = resolve_project_path(args.summary_output)
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            summary_path.write_text(canonical_json(summary), encoding="utf-8")
        print(canonical_json({"ok": True, "summary": summary}).rstrip())
    except Exception as error:
        print(canonical_json({"ok": False, "error": str(error)}).rstrip())
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
