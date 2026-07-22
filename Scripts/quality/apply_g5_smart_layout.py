#!/usr/bin/env python3
"""Apply verified Smart Layout coordinates to Modelica diagram annotations only.

The bundled Smart Layout engine correctly computes coordinates but its current
``writeback_mo`` path appends a second annotation after an existing Modelica
statement.  That form is syntactically invalid for these controller models.
This adapter uses the engine's *layout-only* JSON and replaces only the
existing ``Placement(...)`` and ``Line(...)`` subannotations.  Equations,
parameters, component types, MWORKS metadata, and all non-visual text must
remain byte-for-byte equivalent after visual metadata is normalized.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
EQUATION_RE = re.compile(r"(?m)^\s*equation\s*$")
CONNECT_RE = re.compile(
    r"\bconnect\s*\(\s*"
    r"([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*,\s*"
    r"([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*\)",
    re.MULTILINE,
)
COMPONENT_DECL_RE = re.compile(
    r"(?m)^\s*(?:[A-Za-z_]\w*\.)+[A-Za-z_]\w*\s+([A-Za-z_]\w*)\b",
)


class LayoutApplyError(ValueError):
    """Raised when a layout cannot be applied without changing semantics."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def resolve_project_path(value: Path) -> Path:
    path = value if value.is_absolute() else ROOT / value
    path = path.resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise LayoutApplyError(f"path escapes project root: {value}") from exc
    return path


def repo_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def scan_call_end(text: str, open_paren: int) -> int:
    """Return the exclusive end of a balanced function call."""

    if open_paren >= len(text) or text[open_paren] != "(":
        raise LayoutApplyError("expected opening parenthesis")
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(open_paren, len(text)):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index + 1
            if depth < 0:
                break
    raise LayoutApplyError("unbalanced parenthesis while locating annotation")


def statement_end(text: str, start: int, limit: int | None = None) -> int:
    """Return the exclusive end of a Modelica statement ending in a semicolon."""

    end = len(text) if limit is None else limit
    depth = 0
    quote: str | None = None
    escaped = False
    for index in range(start, end):
        char = text[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char == ";" and depth == 0:
            return index + 1
    raise LayoutApplyError("unable to locate Modelica statement terminator")


def token_call_span(text: str, token: str, start: int, end: int) -> tuple[int, int] | None:
    pattern = re.compile(rf"\b{re.escape(token)}\s*\(")
    match = pattern.search(text, start, end)
    if match is None:
        return None
    open_paren = text.find("(", match.start(), end)
    call_end = scan_call_end(text, open_paren)
    if call_end > end:
        raise LayoutApplyError(f"{token}() extends beyond its Modelica statement")
    return match.start(), call_end


def all_token_call_spans(text: str, token: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    cursor = 0
    while True:
        span = token_call_span(text, token, cursor, len(text))
        if span is None:
            return spans
        spans.append(span)
        cursor = span[1]


def normalized_visual_metadata(text: str) -> str:
    """Remove only placement and line calls for a semantic-text equivalence check."""

    spans = all_token_call_spans(text, "Placement") + all_token_call_spans(text, "Line")
    for start, end in sorted(spans, reverse=True):
        text = text[:start] + "__G5_VISUAL_METADATA__" + text[end:]
    return text


def split_statements(text: str, end: int) -> list[tuple[int, int]]:
    statements: list[tuple[int, int]] = []
    cursor = 0
    while cursor < end:
        try:
            finish = statement_end(text, cursor, end)
        except LayoutApplyError:
            break
        statements.append((cursor, finish))
        cursor = finish
    return statements


def component_declarations(text: str, equation_start: int) -> dict[str, tuple[int, int, tuple[int, int]]]:
    declarations: dict[str, tuple[int, int, tuple[int, int]]] = {}
    for start, end in split_statements(text, equation_start):
        statement = text[start:end]
        # A model header has no semicolon, so the first component can share a
        # statement range with ``model <Name>``. Search physical lines rather
        # than assuming the component begins the range.
        match = COMPONENT_DECL_RE.search(statement)
        if match is None:
            continue
        placement = token_call_span(text, "Placement", start, end)
        if placement is None:
            continue
        name = match.group(1)
        if name in declarations:
            raise LayoutApplyError(f"duplicate component declaration: {name}")
        declarations[name] = (start, end, placement)
    return declarations


def number(value: Any) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)):
        raise LayoutApplyError(f"layout coordinate must be finite numeric: {value!r}")
    return float(value)


def format_number(value: float) -> str:
    rounded = round(value)
    if abs(value - rounded) < 1e-9:
        return str(int(rounded))
    return f"{value:.6f}".rstrip("0").rstrip(".")


def point_text(point: dict[str, Any]) -> str:
    return "{" + ",".join((format_number(number(point.get("x"))), format_number(number(point.get("y"))))) + "}"


def placement_text(node: dict[str, Any]) -> str:
    x = number(node.get("x"))
    y = number(node.get("y"))
    width = number(node.get("width"))
    height = number(node.get("height"))
    if width <= 0 or height <= 0:
        raise LayoutApplyError(f"layout node has non-positive size: {node.get('id')}")
    lower = "{" + format_number(x) + "," + format_number(y) + "}"
    upper = "{" + format_number(x + width) + "," + format_number(y + height) + "}"
    return f"Placement(transformation(extent = {{{lower}, {upper}}}))"


def line_text(edge: dict[str, Any]) -> str:
    sections = edge.get("sections")
    if not isinstance(sections, list) or not sections:
        raise LayoutApplyError(f"layout edge has no sections: {edge.get('id')}")
    section = sections[0]
    if not isinstance(section, dict):
        raise LayoutApplyError(f"layout edge section is invalid: {edge.get('id')}")
    start = section.get("startPoint")
    finish = section.get("endPoint")
    bends = section.get("bendPoints", [])
    if not isinstance(start, dict) or not isinstance(finish, dict) or not isinstance(bends, list):
        raise LayoutApplyError(f"layout edge points are invalid: {edge.get('id')}")
    points = [start, *bends, finish]
    if any(not isinstance(point, dict) for point in points):
        raise LayoutApplyError(f"layout edge point is invalid: {edge.get('id')}")
    color = edge.get("_color", [0, 0, 127])
    if not isinstance(color, list) or len(color) != 3 or any(not isinstance(value, (int, float)) for value in color):
        raise LayoutApplyError(f"layout edge color is invalid: {edge.get('id')}")
    points_text = "{" + ",".join(point_text(point) for point in points) + "}"
    color_text = "{" + ",".join(format_number(float(value)) for value in color) + "}"
    return f"Line(points = {points_text}, color = {color_text})"


def layout_root(layout: dict[str, Any]) -> dict[str, Any]:
    for key in ("_layout", "layout"):
        candidate = layout.get(key)
        if isinstance(candidate, dict) and isinstance(candidate.get("children"), list):
            return candidate
    if isinstance(layout.get("children"), list):
        return layout
    raise LayoutApplyError("layout JSON contains no root children list")


def endpoint_component(endpoint: str) -> str:
    return endpoint.split(".", 1)[0]


def apply_layout_to_text(source: str, layout: dict[str, Any]) -> tuple[str, dict[str, int]]:
    equation_match = EQUATION_RE.search(source)
    if equation_match is None:
        raise LayoutApplyError("source has no equation section")
    equation_start = equation_match.start()
    root = layout_root(layout)
    nodes = root.get("children")
    edges = root.get("edges")
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise LayoutApplyError("layout root must contain children and edges")

    node_by_id: dict[str, dict[str, Any]] = {}
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get("id"), str) or not node["id"]:
            raise LayoutApplyError("layout contains a node without an id")
        node_id = node["id"]
        if node_id in node_by_id:
            raise LayoutApplyError(f"duplicate layout node id: {node_id}")
        node_by_id[node_id] = node
    declarations = component_declarations(source, equation_start)
    if not set(node_by_id).issubset(declarations):
        missing = sorted(set(node_by_id) - set(declarations))
        raise LayoutApplyError(f"layout/component mismatch; missing declarations={missing}")

    replacements: list[tuple[int, int, str]] = []
    for node_id, node in node_by_id.items():
        _, _, span = declarations[node_id]
        replacements.append((span[0], span[1], placement_text(node)))

    expected_edges: dict[str, dict[str, Any]] = {}
    for edge in edges:
        if not isinstance(edge, dict) or not isinstance(edge.get("id"), str):
            raise LayoutApplyError("layout contains an edge without an id")
        edge_id = edge["id"]
        if edge_id in expected_edges:
            raise LayoutApplyError(f"duplicate layout edge id: {edge_id}")
        expected_edges[edge_id] = edge

    source_connections = list(CONNECT_RE.finditer(source, equation_start))
    if len(source_connections) != len(expected_edges):
        raise LayoutApplyError(
            f"layout/source connection count mismatch: layout={len(expected_edges)}, source={len(source_connections)}"
        )
    for index, match in enumerate(source_connections, start=1):
        source_name = endpoint_component(match.group(1))
        target_name = endpoint_component(match.group(2))
        edge_id = f"edge_{index:03d}_{source_name}_to_{target_name}"
        edge = expected_edges.get(edge_id)
        if edge is None:
            raise LayoutApplyError(f"layout edge is missing: {edge_id}")
        end = statement_end(source, match.start())
        span = token_call_span(source, "Line", match.start(), end)
        if span is None:
            raise LayoutApplyError(f"connection has no existing Line annotation: {edge_id}")
        replacements.append((span[0], span[1], line_text(edge)))

    ordered = sorted(replacements, reverse=True)
    previous_start = len(source) + 1
    updated = source
    for start, end, replacement in ordered:
        if end > previous_start:
            raise LayoutApplyError("overlapping visual annotation replacements")
        updated = updated[:start] + replacement + updated[end:]
        previous_start = start
    if normalized_visual_metadata(source) != normalized_visual_metadata(updated):
        raise LayoutApplyError("non-visual Modelica text changed during layout application")
    return updated, {"component_count": len(node_by_id), "connect_count": len(source_connections)}


def build_summary(source_path: Path, layout_path: Path, source: str, updated: str, counts: dict[str, int]) -> dict[str, Any]:
    return {
        "schema": "mosim.g5_layout_metadata_writeback.v1",
        "claim_boundary": "Visual metadata repair only. This record does not claim MWORKS check_model, simulation, controller behavior, code generation, runtime, or report acceptance.",
        "source_model": repo_path(source_path),
        "layout_json": repo_path(layout_path),
        "before_sha256": sha256_text(source),
        "after_sha256": sha256_text(updated),
        "component_placement_count": counts["component_count"],
        "connection_line_count": counts["connect_count"],
        "non_visual_text_equivalent": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path, help="project-relative Modelica .mo source")
    parser.add_argument("--layout", required=True, type=Path, help="layout-only JSON from Smart Layout")
    parser.add_argument("--output", required=True, type=Path, help="target Modelica .mo path")
    parser.add_argument("--summary-output", type=Path, help="optional provenance summary JSON")
    parser.add_argument("--allow-in-place", action="store_true", help="required when --output equals --source")
    parser.add_argument("--check", action="store_true", help="fail if existing output differs from deterministic visual rewrite")
    args = parser.parse_args(argv)

    try:
        source_path = resolve_project_path(args.source)
        layout_path = resolve_project_path(args.layout)
        output_path = resolve_project_path(args.output)
        if not source_path.is_file() or not layout_path.is_file():
            raise LayoutApplyError("source and layout inputs must exist")
        if source_path == output_path and not args.allow_in_place:
            raise LayoutApplyError("in-place write requires --allow-in-place")
        source = source_path.read_text(encoding="utf-8")
        layout = json.loads(layout_path.read_text(encoding="utf-8"))
        if not isinstance(layout, dict):
            raise LayoutApplyError("layout JSON object required")
        updated, counts = apply_layout_to_text(source, layout)
        summary = build_summary(source_path, layout_path, source, updated, counts)
        errors: list[str] = []
        if args.check:
            if not output_path.is_file():
                errors.append(f"layout output is missing: {repo_path(output_path)}")
            elif output_path.read_text(encoding="utf-8") != updated:
                errors.append("existing layout output differs from deterministic visual rewrite")
            if args.summary_output:
                summary_path = resolve_project_path(args.summary_output)
                if not summary_path.is_file():
                    errors.append(f"layout summary is missing: {repo_path(summary_path)}")
                elif json.loads(summary_path.read_text(encoding="utf-8")) != summary:
                    errors.append("layout summary differs from deterministic visual rewrite")
        else:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(updated, encoding="utf-8")
            if args.summary_output:
                summary_path = resolve_project_path(args.summary_output)
                summary_path.parent.mkdir(parents=True, exist_ok=True)
                summary_path.write_text(canonical_json(summary), encoding="utf-8")
    except Exception as exc:
        errors = [str(exc)]
        summary = None

    print(canonical_json({"ok": not errors, "summary": summary, "errors": errors}).rstrip())
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
