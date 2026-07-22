#!/usr/bin/env python3
"""Build a deterministic Smart Layout graph from a Modelica controller core.

The G5 graphical review may repair only diagram metadata after a source model
has been found to contain real control logic but unreadable routing.  This
tool reads the existing ``connect(...)`` topology without changing the source
model, then emits the compact node/edge JSON accepted by the Sysplorer Smart
Layout tool.  It intentionally does not infer controller behavior or produce
an MWORKS acceptance claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONNECT_RE = re.compile(
    r"\bconnect\s*\(\s*"
    r"([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*,\s*"
    r"([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*\)",
    re.MULTILINE,
)


class RelayoutGraphError(ValueError):
    """Raised when a requested source cannot form a safe layout graph."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def repo_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise RelayoutGraphError(f"path escapes project root: {path}") from exc


def resolve_project_path(value: Path) -> Path:
    path = value if value.is_absolute() else ROOT / value
    path = path.resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise RelayoutGraphError(f"path escapes project root: {value}") from exc
    return path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def endpoint_component(endpoint: str) -> str:
    return endpoint.split(".", 1)[0]


def build_graph(model_path: Path) -> dict[str, Any]:
    """Return the topology-only JSON accepted by ``smart_layout``.

    Nodes intentionally retain original component names so a post-writeback
    review can compare the visual layout with the actual Modelica source.
    """

    path = resolve_project_path(model_path)
    if path.suffix.lower() != ".mo":
        raise RelayoutGraphError(f"Modelica .mo file required: {repo_path(path)}")
    if not path.is_file():
        raise RelayoutGraphError(f"model file is missing: {repo_path(path)}")

    text = path.read_text(encoding="utf-8")
    matches = list(CONNECT_RE.finditer(text))
    if not matches:
        raise RelayoutGraphError(f"no connect() topology found: {repo_path(path)}")

    ordered_nodes: list[str] = []
    seen_nodes: set[str] = set()
    edges: list[dict[str, str]] = []
    for index, match in enumerate(matches, start=1):
        source = endpoint_component(match.group(1))
        target = endpoint_component(match.group(2))
        for node_id in (source, target):
            if node_id not in seen_nodes:
                seen_nodes.add(node_id)
                ordered_nodes.append(node_id)
        edges.append(
            {
                "id": f"edge_{index:03d}_{source}_to_{target}",
                "source": source,
                "target": target,
            }
        )

    return {
        "id": path.stem,
        "nodes": [
            {"id": node_id, "label": node_id, "width": 32.0, "height": 22.0}
            for node_id in ordered_nodes
        ],
        "edges": edges,
    }


def graph_summary(model_path: Path, graph: dict[str, Any]) -> dict[str, Any]:
    path = resolve_project_path(model_path)
    return {
        "schema": "mosim.g5_relayout_graph_summary.v1",
        "claim_boundary": "Topology-only Smart Layout input. It does not prove a readable GUI layout, check_model, simulation, controller behavior, code generation, or runtime result.",
        "source_model": repo_path(path),
        "source_sha256": sha256_file(path),
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
    }


def validate_graph(graph: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not nodes:
        return ["graph must contain non-empty nodes"]
    if not isinstance(edges, list) or not edges:
        return ["graph must contain non-empty edges"]
    node_ids = [item.get("id") for item in nodes if isinstance(item, dict)]
    if len(node_ids) != len(nodes) or any(not isinstance(value, str) or not value for value in node_ids):
        errors.append("every node must have a non-empty id")
    if len(node_ids) != len(set(node_ids)):
        errors.append("node IDs must be unique")
    known_nodes = set(node_ids)
    edge_ids: list[str] = []
    for edge in edges:
        if not isinstance(edge, dict):
            errors.append("every edge must be an object")
            continue
        edge_id = edge.get("id")
        if not isinstance(edge_id, str) or not edge_id:
            errors.append("every edge must have a non-empty id")
        else:
            edge_ids.append(edge_id)
        for endpoint in ("source", "target"):
            if edge.get(endpoint) not in known_nodes:
                errors.append(f"edge {edge_id!r} has an unknown {endpoint}")
    if len(edge_ids) != len(set(edge_ids)):
        errors.append("edge IDs must be unique")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, type=Path, help="project-relative .mo source")
    parser.add_argument("--output", required=True, type=Path, help="project-relative graph JSON")
    parser.add_argument(
        "--summary-output",
        type=Path,
        help="optional project-relative provenance summary JSON",
    )
    parser.add_argument("--check", action="store_true", help="fail if output differs from deterministic graph")
    args = parser.parse_args(argv)

    try:
        model_path = resolve_project_path(args.model)
        output_path = resolve_project_path(args.output)
        graph = build_graph(model_path)
        errors = validate_graph(graph)
        summary = graph_summary(model_path, graph)
        if args.check:
            if not output_path.is_file():
                errors.append(f"graph output is missing: {repo_path(output_path)}")
            elif json.loads(output_path.read_text(encoding="utf-8")) != graph:
                errors.append("on-disk graph differs from deterministic source topology")
            if args.summary_output:
                summary_path = resolve_project_path(args.summary_output)
                if not summary_path.is_file():
                    errors.append(f"summary output is missing: {repo_path(summary_path)}")
                elif json.loads(summary_path.read_text(encoding="utf-8")) != summary:
                    errors.append("on-disk summary differs from deterministic source topology")
        elif not errors:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(canonical_json(graph), encoding="utf-8")
            if args.summary_output:
                summary_path = resolve_project_path(args.summary_output)
                summary_path.parent.mkdir(parents=True, exist_ok=True)
                summary_path.write_text(canonical_json(summary), encoding="utf-8")
    except Exception as exc:
        errors = [str(exc)]

    report = {
        "ok": not errors,
        "model": str(args.model),
        "output": str(args.output),
        "errors": errors,
    }
    print(canonical_json(report).rstrip())
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
