#!/usr/bin/env python3
"""Transfer only G5 diagram metadata between isomorphic Modelica models.

The donor and target must have the same component names and ordered connect()
topology.  The transfer is limited to existing Placement and Line annotations;
controller declarations, parameters, equations, and connection endpoints stay
byte-identical after visual metadata is normalized.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from apply_g5_smart_layout import (
    CONNECT_RE,
    EQUATION_RE,
    LayoutApplyError,
    component_declarations,
    endpoint_component,
    normalized_visual_metadata,
    repo_path,
    resolve_project_path,
    statement_end,
    token_call_span,
)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_utf8(path: Path) -> str:
    """Preserve source line endings so reported hashes bind on-disk bytes."""

    return path.read_bytes().decode("utf-8")


def write_utf8(path: Path, text: str) -> None:
    path.write_bytes(text.encode("utf-8"))


def visual_spans(text: str) -> tuple[list[str], dict[str, tuple[int, int]], list[tuple[tuple[str, str], tuple[int, int]]]]:
    equation_match = EQUATION_RE.search(text)
    if equation_match is None:
        raise LayoutApplyError("source has no equation section")
    declarations = component_declarations(text, equation_match.start())
    if not declarations:
        raise LayoutApplyError("source has no placed component declarations")
    placements = {name: item[2] for name, item in declarations.items()}
    lines: list[tuple[tuple[str, str], tuple[int, int]]] = []
    for match in CONNECT_RE.finditer(text, equation_match.start()):
        statement_finish = statement_end(text, match.start())
        line_span = token_call_span(text, "Line", match.start(), statement_finish)
        if line_span is None:
            raise LayoutApplyError("every connect() statement must have a Line annotation")
        endpoints = (endpoint_component(match.group(1)), endpoint_component(match.group(2)))
        lines.append((endpoints, line_span))
    if not lines:
        raise LayoutApplyError("source has no connect() topology")
    return list(declarations), placements, lines


def transfer_visual_layout(donor: str, target: str) -> tuple[str, dict[str, int]]:
    donor_names, donor_placements, donor_lines = visual_spans(donor)
    target_names, target_placements, target_lines = visual_spans(target)
    if donor_names != target_names:
        raise LayoutApplyError("donor and target component order differ")
    donor_endpoints = [item[0] for item in donor_lines]
    target_endpoints = [item[0] for item in target_lines]
    if donor_endpoints != target_endpoints:
        raise LayoutApplyError("donor and target ordered connect() topology differ")

    replacements: list[tuple[int, int, str]] = []
    for name in donor_names:
        donor_start, donor_end = donor_placements[name]
        target_start, target_end = target_placements[name]
        replacements.append((target_start, target_end, donor[donor_start:donor_end]))
    for (_, donor_span), (_, target_span) in zip(donor_lines, target_lines, strict=True):
        donor_start, donor_end = donor_span
        target_start, target_end = target_span
        replacements.append((target_start, target_end, donor[donor_start:donor_end]))

    updated = target
    previous_start = len(target) + 1
    for start, end, replacement in sorted(replacements, reverse=True):
        if end > previous_start:
            raise LayoutApplyError("overlapping visual metadata replacement")
        updated = updated[:start] + replacement + updated[end:]
        previous_start = start
    if normalized_visual_metadata(target) != normalized_visual_metadata(updated):
        raise LayoutApplyError("visual-layout transfer changed non-visual Modelica text")
    return updated, {"component_placement_count": len(donor_names), "connection_line_count": len(donor_lines)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--donor", required=True, type=Path, help="project-relative relaid-out donor .mo")
    parser.add_argument("--source", required=True, type=Path, help="project-relative target source .mo")
    parser.add_argument("--output", required=True, type=Path, help="project-relative output .mo")
    parser.add_argument("--summary-output", type=Path, help="optional project-relative provenance JSON")
    parser.add_argument("--allow-in-place", action="store_true", help="required when output equals source")
    parser.add_argument("--check", action="store_true", help="fail if output differs from deterministic transfer")
    args = parser.parse_args(argv)

    try:
        donor_path = resolve_project_path(args.donor)
        source_path = resolve_project_path(args.source)
        output_path = resolve_project_path(args.output)
        if not donor_path.is_file() or not source_path.is_file():
            raise LayoutApplyError("donor and source must exist")
        if source_path == output_path and not args.allow_in_place:
            raise LayoutApplyError("in-place transfer requires --allow-in-place")
        donor = read_utf8(donor_path)
        source = read_utf8(source_path)
        updated, counts = transfer_visual_layout(donor, source)
        summary = {
            "schema": "mosim.g5_visual_layout_transfer.v1",
            "claim_boundary": "Visual metadata transfer only. This record does not claim MWORKS check_model, simulation, controller behavior, code generation, runtime, or report acceptance.",
            "donor_model": repo_path(donor_path),
            "donor_sha256": sha256_text(donor),
            "source_model": repo_path(source_path),
            # For a non-in-place transfer this is the immutable formal source
            # hash.  In-place staging writes use the resulting bytes so the
            # summary remains checkable on a later invocation.
            "source_sha256": sha256_text(updated if source_path == output_path else source),
            "output_model": repo_path(output_path),
            "output_sha256": sha256_text(updated),
            **counts,
            "non_visual_text_equivalent": True,
        }
        errors: list[str] = []
        if args.check:
            if not output_path.is_file():
                errors.append(f"layout output is missing: {repo_path(output_path)}")
            elif read_utf8(output_path) != updated:
                errors.append("existing output differs from deterministic visual transfer")
            if args.summary_output:
                summary_path = resolve_project_path(args.summary_output)
                if not summary_path.is_file():
                    errors.append(f"summary output is missing: {repo_path(summary_path)}")
                elif json.loads(summary_path.read_text(encoding="utf-8")) != summary:
                    errors.append("layout summary differs from deterministic visual transfer")
        elif not errors:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            write_utf8(output_path, updated)
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
