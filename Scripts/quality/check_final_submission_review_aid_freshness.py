#!/usr/bin/env python3
"""Check downstream final-submission review-aid freshness without regenerating artifacts."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REFRESH_ORDER = (
    ROOT
    / "Results/static_audits/final_submission_refresh_order_20260610"
    / "final_submission_refresh_order_check.json"
)
DEFAULT_OUTPUT_JSON = (
    ROOT
    / "Results/static_audits/final_submission_review_aid_freshness_20260610"
    / "final_submission_review_aid_freshness_check.json"
)
DEFAULT_OUTPUT_MD = (
    ROOT
    / "Results/static_audits/final_submission_review_aid_freshness_20260610"
    / "final_submission_review_aid_freshness_check.md"
)
DEFAULT_GRACE_SECONDS = 1.0

REVIEW_NODE_IDS = (
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
    "final_submission_review_artifact_dependency_graph",
)

EXPECTED_STATUSES = {
    "final_submission_blocked_gate_triage_map": "blocked_gate_triage_map_not_execution",
    "final_submission_human_decision_diff_template": "human_decision_diff_template_not_execution",
    "final_submission_reviewer_quickstart": "reviewer_quickstart_not_execution",
    "final_submission_review_progress_snapshot": "review_progress_snapshot_not_execution",
    "final_submission_post_review_rerun_matrix": "post_review_rerun_matrix_not_execution",
    "final_submission_manual_review_answer_sheet": "manual_review_answer_sheet_template_not_execution",
    "final_submission_answer_sheet_decision_consistency": "answer_sheet_decision_consistency_check_not_execution",
    "final_submission_review_artifact_bundle_index": "review_artifact_bundle_index_not_execution",
    "final_submission_reviewer_handoff_note": "reviewer_handoff_note_not_execution",
    "final_submission_manual_review_closure_checklist": "manual_review_closure_checklist_not_execution",
    "final_submission_post_review_state_transition_plan": "post_review_state_transition_plan_not_execution",
    "final_submission_post_review_command_plan_coverage": "post_review_command_plan_coverage_check_not_execution",
    "final_submission_review_artifact_dependency_graph": "review_artifact_dependency_graph_not_execution",
}


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


def mtime_iso(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="milliseconds")


def node_record(node: dict[str, Any]) -> dict[str, Any]:
    node_id = str(node.get("node_id", ""))
    outputs = [str(output) for output in node.get("outputs", []) if output]
    primary_output = outputs[0] if outputs else ""
    output_path = repo_path(primary_output) if primary_output else ROOT / "__missing_output__"
    expected_status = EXPECTED_STATUSES.get(node_id, "")
    actual_status = ""
    read_error = ""
    mtime_epoch: float | None = None

    if primary_output and output_path.exists():
        mtime_epoch = output_path.stat().st_mtime
        try:
            actual_status = str(read_json(output_path).get("status", ""))
        except Exception as exc:  # pragma: no cover - kept for corrupt local artifact diagnosis.
            read_error = str(exc)

    return {
        "node_id": node_id,
        "command": str(node.get("command", "")),
        "primary_output": primary_output,
        "output_exists": bool(primary_output and output_path.exists()),
        "output_mtime": mtime_iso(output_path) if primary_output and output_path.exists() else "",
        "output_mtime_epoch": mtime_epoch,
        "expected_status": expected_status,
        "actual_status": actual_status,
        "status_matches": bool(expected_status and actual_status == expected_status),
        "read_error": read_error,
        "after": [str(item) for item in node.get("after", [])],
        "runs_now": False,
    }


def dependency_edges(records: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    known = set(records)
    for node_id, record in records.items():
        for dep in record["after"]:
            if dep in known:
                edges.append({"from": dep, "to": node_id, "type": "after"})
    return edges


def detect_stale_dependencies(
    records: dict[str, dict[str, Any]],
    edges: list[dict[str, str]],
    grace_seconds: float,
) -> list[dict[str, Any]]:
    stale: list[dict[str, Any]] = []
    for edge in edges:
        upstream = records[edge["from"]]
        downstream = records[edge["to"]]
        upstream_time = upstream.get("output_mtime_epoch")
        downstream_time = downstream.get("output_mtime_epoch")
        if not isinstance(upstream_time, float) or not isinstance(downstream_time, float):
            continue
        lag_seconds = upstream_time - downstream_time
        if lag_seconds > grace_seconds:
            stale.append(
                {
                    "from": edge["from"],
                    "to": edge["to"],
                    "lag_seconds": round(lag_seconds, 3),
                    "upstream_mtime": upstream["output_mtime"],
                    "downstream_mtime": downstream["output_mtime"],
                }
            )
    return stale


def build_freshness_check(refresh_order_path: Path, grace_seconds: float) -> dict[str, Any]:
    refresh_order = read_json(refresh_order_path)
    refresh_nodes = [node for node in refresh_order.get("nodes", []) if isinstance(node, dict)]
    refresh_node_by_id = {str(node.get("node_id", "")): node for node in refresh_nodes}
    issues: list[str] = []
    warnings: list[str] = []
    missing_node_ids = [node_id for node_id in REVIEW_NODE_IDS if node_id not in refresh_node_by_id]
    for node_id in missing_node_ids:
        issues.append(f"missing refresh-order node: {node_id}")

    records = {
        node_id: node_record(refresh_node_by_id[node_id])
        for node_id in REVIEW_NODE_IDS
        if node_id in refresh_node_by_id
    }
    edges = dependency_edges(records)
    stale = detect_stale_dependencies(records, edges, grace_seconds)
    missing_outputs = [
        record["node_id"]
        for record in records.values()
        if not record["output_exists"]
    ]
    status_mismatches = [
        {
            "node_id": record["node_id"],
            "expected_status": record["expected_status"],
            "actual_status": record["actual_status"],
            "read_error": record["read_error"],
        }
        for record in records.values()
        if not record["status_matches"]
    ]
    for node_id in missing_outputs:
        issues.append(f"missing output for review-aid node: {node_id}")
    for mismatch in status_mismatches:
        issues.append(
            f"status mismatch for {mismatch['node_id']}: "
            f"expected {mismatch['expected_status']}, got {mismatch['actual_status']}"
        )
    for edge in stale:
        issues.append(
            f"stale dependency: {edge['to']} is older than {edge['from']} by {edge['lag_seconds']} seconds"
        )

    return {
        "ok": not issues,
        "check_id": "final_submission_review_aid_freshness_20260610",
        "status": "review_aid_freshness_check_not_execution",
        "source_refresh_order": rel(refresh_order_path),
        "summary": {
            "review_node_count": len(records),
            "dependency_edge_count": len(edges),
            "missing_output_count": len(missing_outputs),
            "status_mismatch_count": len(status_mismatches),
            "stale_dependency_count": len(stale),
            "issue_count": len(issues),
            "warning_count": len(warnings),
            "freshness_grace_seconds": grace_seconds,
            "automated_execution_allowed": False,
            "refreshes_artifacts_now": False,
            "runs_commands_now": False,
            "updates_static_audit_index": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        },
        "nodes": list(records.values()),
        "edges": edges,
        "stale_dependencies": stale,
        "missing_outputs": missing_outputs,
        "status_mismatches": status_mismatches,
        "issues": issues,
        "warnings": warnings,
        "claim_boundary": [
            "This checker reads downstream review-aid artifacts only.",
            "It does not regenerate or refresh artifacts.",
            "It does not run listed commands.",
            "It does not update final_submission_static_audit_index.json.",
            "It does not edit decision templates.",
            "It does not approve decisions.",
            "It does not apply report-source edits.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
        ],
    }


def write_markdown(result: dict[str, Any], path: Path) -> None:
    summary = result["summary"]
    lines = [
        "# Final Submission Review-Aid Freshness Check, 2026-06-10",
        "",
        f"Status: `{result['status']}`",
        "",
        "## Summary",
        "",
        f"- OK: `{result['ok']}`",
        f"- Review nodes: `{summary['review_node_count']}`",
        f"- Dependency edges: `{summary['dependency_edge_count']}`",
        f"- Missing outputs: `{summary['missing_output_count']}`",
        f"- Status mismatches: `{summary['status_mismatch_count']}`",
        f"- Stale dependencies: `{summary['stale_dependency_count']}`",
        f"- Freshness grace seconds: `{summary['freshness_grace_seconds']}`",
        f"- Automated execution allowed: `{summary['automated_execution_allowed']}`",
        f"- Refreshes artifacts now: `{summary['refreshes_artifacts_now']}`",
        f"- Runs commands now: `{summary['runs_commands_now']}`",
        f"- Updates static audit index: `{summary['updates_static_audit_index']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Stale Dependencies",
        "",
    ]
    if result["stale_dependencies"]:
        for edge in result["stale_dependencies"]:
            lines.append(f"- `{edge['to']}` is older than `{edge['from']}` by `{edge['lag_seconds']}` seconds")
    else:
        lines.append("- None")
    lines.extend(["", "## Nodes", ""])
    for node in result["nodes"]:
        lines.extend(
            [
                f"### {node['node_id']}",
                "",
                f"- Output: `{node['primary_output']}`",
                f"- Exists: `{node['output_exists']}`",
                f"- MTime: `{node['output_mtime']}`",
                f"- Status: `{node['actual_status']}`",
                f"- Expected status: `{node['expected_status']}`",
                f"- Status matches: `{node['status_matches']}`",
                f"- Runs now: `{node['runs_now']}`",
                "",
            ]
        )
    lines.extend(["## Issues", ""])
    if result["issues"]:
        for issue in result["issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in result["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-order", default=str(DEFAULT_REFRESH_ORDER.relative_to(ROOT)))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON.relative_to(ROOT)))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD.relative_to(ROOT)))
    parser.add_argument("--grace-seconds", type=float, default=DEFAULT_GRACE_SECONDS)
    args = parser.parse_args()

    result = build_freshness_check(repo_path(args.refresh_order), args.grace_seconds)
    output_json = repo_path(args.output_json)
    output_md = repo_path(args.output_md)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(result, output_md)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
