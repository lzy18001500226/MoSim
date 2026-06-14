#!/usr/bin/env python3
"""Build a static dependency graph for downstream final-submission review aids."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REFRESH_ORDER = (
    ROOT
    / "Results/static_audits/final_submission_refresh_order_20260610"
    / "final_submission_refresh_order_check.json"
)
DEFAULT_BUNDLE = (
    ROOT
    / "Results/static_audits/final_submission_review_artifact_bundle_20260610"
    / "final_submission_review_artifact_bundle_index.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_review_artifact_dependency_graph_20260610"

REVIEW_NODE_PREFIXES = (
    "final_submission_blocked_gate_triage_map",
    "final_submission_human_decision_diff_template",
    "final_submission_reviewer_quickstart",
    "final_submission_review_progress_snapshot",
    "final_submission_post_review_rerun_matrix",
    "final_submission_manual_review_answer_sheet",
    "final_submission_answer_sheet_decision_consistency",
    "final_submission_review_artifact_bundle_index",
    "final_submission_reviewer_handoff_note",
    "final_submission_manual_review_closure_checklist",
    "final_submission_post_review_state_transition_plan",
    "final_submission_post_review_command_plan_coverage",
)


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return data


def is_review_node(node_id: str) -> bool:
    return node_id.startswith(REVIEW_NODE_PREFIXES)


def graph_node(node: dict[str, Any]) -> dict[str, Any]:
    outputs = [str(item) for item in node.get("outputs", []) if item]
    return {
        "node_id": node.get("node_id", ""),
        "command": node.get("command", ""),
        "outputs": outputs,
        "output_exists_count": sum(1 for output in outputs if repo_path(output).exists()),
        "after": [str(item) for item in node.get("after", [])],
        "runs_now": False,
    }


def dependency_edges(nodes: list[dict[str, Any]], known_review_ids: set[str]) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    for node in nodes:
        node_id = str(node.get("node_id", ""))
        for dep in node.get("after", []):
            dep = str(dep)
            if dep in known_review_ids:
                edges.append({"from": dep, "to": node_id, "type": "after"})
    return edges


def bundle_links(bundle: dict[str, Any]) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    artifacts = bundle.get("artifacts", [])
    if not isinstance(artifacts, list):
        return links
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        links.append(
            {
                "bundle_artifact_id": str(artifact.get("artifact_id", "")),
                "json_path": str(artifact.get("json_path", "")),
                "markdown_path": str(artifact.get("markdown_path", "")),
                "status": str(artifact.get("status", "")),
            }
        )
    return links


def build_dependency_graph(refresh_order_path: Path, bundle_path: Path) -> dict[str, Any]:
    refresh_order = read_json(refresh_order_path)
    bundle = read_json(bundle_path)
    refresh_nodes = [node for node in refresh_order.get("nodes", []) if isinstance(node, dict)]
    review_nodes = [graph_node(node) for node in refresh_nodes if is_review_node(str(node.get("node_id", "")))]
    known_review_ids = {str(node["node_id"]) for node in review_nodes}
    edges = dependency_edges(review_nodes, known_review_ids)
    missing_outputs = [
        output
        for node in review_nodes
        for output in node["outputs"]
        if not repo_path(output).exists()
    ]
    return {
        "graph_id": "final_submission_review_artifact_dependency_graph_20260610",
        "status": "review_artifact_dependency_graph_not_execution",
        "sources": {
            "refresh_order": rel(refresh_order_path),
            "review_artifact_bundle": rel(bundle_path),
        },
        "summary": {
            "review_node_count": len(review_nodes),
            "dependency_edge_count": len(edges),
            "bundle_artifact_count": bundle.get("summary", {}).get("bundle_artifact_count", 0),
            "missing_output_count": len(missing_outputs),
            "automated_execution_allowed": False,
            "updates_static_audit_index": False,
            "runs_commands_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "nodes": review_nodes,
        "edges": edges,
        "bundle_artifact_links": bundle_links(bundle),
        "missing_outputs": missing_outputs,
        "claim_boundary": [
            "This dependency graph is a static navigation artifact only.",
            "It does not change final_submission_static_audit_index.json.",
            "It does not run generators or checkers.",
            "It does not edit decision templates.",
            "It does not approve decisions.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(graph: dict[str, Any], path: Path) -> None:
    summary = graph["summary"]
    lines = [
        "# Final Submission Review Artifact Dependency Graph, 2026-06-10",
        "",
        f"Status: `{graph['status']}`",
        "",
        "## Summary",
        "",
        f"- Review nodes: `{summary['review_node_count']}`",
        f"- Dependency edges: `{summary['dependency_edge_count']}`",
        f"- Bundle artifacts: `{summary['bundle_artifact_count']}`",
        f"- Missing outputs: `{summary['missing_output_count']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Updates static audit index: `{summary['updates_static_audit_index']}`",
        f"- Runs commands now: `{summary['runs_commands_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Edges",
        "",
    ]
    for edge in graph["edges"]:
        lines.append(f"- `{edge['from']}` -> `{edge['to']}` ({edge['type']})")
    lines.extend(["", "## Nodes", ""])
    for node in graph["nodes"]:
        lines.extend(
            [
                f"### {node['node_id']}",
                "",
                f"- Command: `{node['command']}`",
                f"- Outputs: `{len(node['outputs'])}`",
                f"- Existing outputs: `{node['output_exists_count']}`",
                f"- Runs now: `{node['runs_now']}`",
                "",
            ]
        )
    lines.extend(["## Claim Boundary", ""])
    for item in graph["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-order", default=str(DEFAULT_REFRESH_ORDER.relative_to(ROOT)))
    parser.add_argument("--bundle", default=str(DEFAULT_BUNDLE.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    graph = build_dependency_graph(repo_path(args.refresh_order), repo_path(args.bundle))
    json_path = output_dir / "final_submission_review_artifact_dependency_graph.json"
    md_path = output_dir / "final_submission_review_artifact_dependency_graph.md"
    json_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(graph, md_path)
    print(
        json.dumps(
            {
                "ok": True,
                "dependency_graph_json": rel(json_path),
                "dependency_graph_markdown": rel(md_path),
                "review_node_count": graph["summary"]["review_node_count"],
                "dependency_edge_count": graph["summary"]["dependency_edge_count"],
                "bundle_artifact_count": graph["summary"]["bundle_artifact_count"],
                "missing_output_count": graph["summary"]["missing_output_count"],
                "updates_static_audit_index": graph["summary"]["updates_static_audit_index"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
