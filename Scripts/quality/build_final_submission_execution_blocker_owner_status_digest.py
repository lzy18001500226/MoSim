#!/usr/bin/env python3
"""Build an owner/status digest for final-submission execution blockers.

This digest groups the current final-submission blockers by owner, required
action, execution target, and blocker class. It is a navigation artifact only:
it does not answer review questions, edit decision artifacts, run commands, or
authorize final-output execution.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ACTION_MAP = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_reviewer_action_map_20260610"
    / "final_submission_reviewer_action_map.json"
)
DEFAULT_AUTH_BLOCKERS = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_execution_authorization_blocker_20260610"
    / "final_submission_execution_authorization_blocker_index.json"
)
DEFAULT_TRIAGE_MAP = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_blocked_gate_triage_map_20260610"
    / "final_submission_blocked_gate_triage_map.json"
)
DEFAULT_DASHBOARD = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_readiness_dashboard_20260610"
    / "final_submission_readiness_dashboard.json"
)
DEFAULT_CHECKSUM_INDEX = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_reviewer_open_file_checksum_index_20260610"
    / "final_submission_reviewer_open_file_checksum_index.json"
)
DEFAULT_OUTPUT_DIR = ROOT / "Results/static_audits/final_submission_execution_blocker_owner_status_digest_20260610"


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


def action_owner(action: dict[str, Any]) -> str:
    return str(action.get("decision_owner") or action.get("checklist_owner") or "unknown_owner")


def unique(values: list[str]) -> list[str]:
    return sorted({value for value in values if value})


def build_action_lookup(action_map: dict[str, Any]) -> dict[str, dict[str, Any]]:
    actions = action_map.get("actions", [])
    if not isinstance(actions, list):
        return {}
    return {str(action.get("action_id", "")): action for action in actions if isinstance(action, dict)}


def build_target_lookup(auth_blockers: dict[str, Any]) -> dict[str, dict[str, Any]]:
    targets = auth_blockers.get("execution_target_authorization_blockers", [])
    if not isinstance(targets, list):
        return {}
    return {str(target.get("target_id", "")): target for target in targets if isinstance(target, dict)}


def action_target_references(targets: dict[str, dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    references: dict[str, list[dict[str, Any]]] = {}
    for target in targets.values():
        target_id = str(target.get("target_id", ""))
        for action_id in target.get("required_action_ids", []):
            action_id = str(action_id)
            references.setdefault(action_id, []).append(
                {
                    "target_id": target_id,
                    "label": target.get("label", ""),
                    "ready_now": bool(target.get("ready_now", False)),
                    "blocking_reason_count": int(target.get("blocking_reason_count", 0)),
                    "blocking_reasons": list(target.get("blocking_reasons", [])),
                }
            )
    return references


def action_blocked_artifacts(
    triage_map: dict[str, Any],
    action_lookup: dict[str, dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for artifact in triage_map.get("blocked_artifacts", []):
        if not isinstance(artifact, dict):
            continue
        linked_actions = artifact.get("linked_human_actions", [])
        if not isinstance(linked_actions, list):
            linked_actions = []
        for linked in linked_actions:
            if not isinstance(linked, dict):
                continue
            action_id = str(linked.get("action_id", ""))
            if not action_id:
                continue
            grouped.setdefault(action_id, []).append(
                {
                    "artifact_id": artifact.get("artifact_id", ""),
                    "blocker_class": artifact.get("blocker_class", ""),
                    "next_human_action": artifact.get("next_human_action", ""),
                    "known_owner": action_owner(action_lookup.get(action_id, {})),
                }
            )
    return grouped


def build_digest(
    action_map_path: Path,
    auth_blockers_path: Path,
    triage_map_path: Path,
    dashboard_path: Path,
    checksum_index_path: Path,
) -> dict[str, Any]:
    action_map = read_json(action_map_path)
    auth_blockers = read_json(auth_blockers_path)
    triage_map = read_json(triage_map_path)
    dashboard = read_json(dashboard_path)
    checksum_index = read_json(checksum_index_path)

    action_lookup = build_action_lookup(action_map)
    target_lookup = build_target_lookup(auth_blockers)
    target_refs = action_target_references(target_lookup)
    artifact_refs = action_blocked_artifacts(triage_map, action_lookup)

    issues: list[str] = []
    for target in target_lookup.values():
        for action_id in target.get("required_action_ids", []):
            if str(action_id) not in action_lookup:
                issues.append(f"target {target.get('target_id')} references unknown action {action_id}")

    actions: list[dict[str, Any]] = []
    owner_groups: dict[str, dict[str, Any]] = {}
    for action_id, action in sorted(action_lookup.items(), key=lambda item: int(item[1].get("priority", 0))):
        owner = action_owner(action)
        targets = target_refs.get(action_id, [])
        artifacts = artifact_refs.get(action_id, [])
        blocker_classes = unique([str(item.get("blocker_class", "")) for item in artifacts])
        target_ids = unique([str(item.get("target_id", "")) for item in targets])
        action_record = {
            "action_id": action_id,
            "priority": int(action.get("priority", 0)),
            "owner": owner,
            "decision_needed": action.get("decision_needed", ""),
            "decision_artifact": action.get("decision_artifact", ""),
            "target_count": len(target_ids),
            "target_ids": target_ids,
            "blocked_artifact_count": len(artifacts),
            "blocker_classes": blocker_classes,
            "blocked_artifacts": artifacts,
            "target_references": targets,
            "automated_execution_allowed": False,
            "answers_questions_now": False,
            "fills_answers_now": False,
            "copies_answers_now": False,
            "edits_decision_artifacts_now": False,
            "runs_commands_now": False,
            "authorizes_execution_now": False,
            "generates_final_outputs": False,
            "final_acceptance": False,
        }
        actions.append(action_record)

        group = owner_groups.setdefault(
            owner,
            {
                "owner": owner,
                "action_ids": [],
                "target_ids": [],
                "blocker_classes": [],
                "blocked_artifact_ids": [],
                "decision_needed": [],
                "automated_execution_allowed": False,
                "answers_questions_now": False,
                "fills_answers_now": False,
                "copies_answers_now": False,
                "edits_decision_artifacts_now": False,
                "runs_commands_now": False,
                "authorizes_execution_now": False,
                "generates_final_outputs": False,
                "final_acceptance": False,
            },
        )
        group["action_ids"].append(action_id)
        group["target_ids"].extend(target_ids)
        group["blocker_classes"].extend(blocker_classes)
        group["blocked_artifact_ids"].extend(str(item.get("artifact_id", "")) for item in artifacts)
        if action.get("decision_needed"):
            group["decision_needed"].append(str(action.get("decision_needed")))

    owner_records: list[dict[str, Any]] = []
    for group in owner_groups.values():
        group["action_ids"] = unique(group["action_ids"])
        group["target_ids"] = unique(group["target_ids"])
        group["blocker_classes"] = unique(group["blocker_classes"])
        group["blocked_artifact_ids"] = unique(group["blocked_artifact_ids"])
        group["decision_needed"] = unique(group["decision_needed"])
        group["action_count"] = len(group["action_ids"])
        group["target_count"] = len(group["target_ids"])
        group["blocker_class_count"] = len(group["blocker_classes"])
        group["blocked_artifact_count"] = len(group["blocked_artifact_ids"])
        owner_records.append(group)
    owner_records.sort(key=lambda item: (min([action_lookup[a].get("priority", 999) for a in item["action_ids"]]), item["owner"]))

    auth_summary = auth_blockers.get("summary", {})
    triage_summary = triage_map.get("summary", {})
    dashboard_summary = dashboard.get("summary", {})
    checksum_summary = checksum_index.get("summary", {})
    summary = {
        "owner_count": len(owner_records),
        "action_count": len(actions),
        "execution_target_count": int(auth_summary.get("execution_target_count", len(target_lookup))),
        "blocked_execution_target_count": int(auth_summary.get("blocked_execution_target_count", 0)),
        "target_action_reference_count": int(auth_summary.get("target_action_reference_count", 0)),
        "blocked_artifact_count": int(triage_summary.get("blocked_artifact_count", 0)),
        "blocker_class_count": int(triage_summary.get("blocker_class_count", 0)),
        "dashboard_blocking_gate_count": int(dashboard_summary.get("blocking_gate_count", 0)),
        "dashboard_blocker_count": int(dashboard_summary.get("blocker_count", 0)),
        "reviewer_open_file_count": int(checksum_summary.get("unique_open_file_count", 0)),
        "reviewer_open_file_drift_count": int(checksum_summary.get("drift_from_previous_output_count", 0)),
        "issue_count": len(issues),
        "automated_execution_allowed": False,
        "answers_questions_now": False,
        "fills_answers_now": False,
        "copies_answers_now": False,
        "edits_decision_artifacts_now": False,
        "runs_commands_now": False,
        "authorizes_execution_now": False,
        "generates_final_outputs": False,
        "final_acceptance": False,
    }

    return {
        "digest_id": "final_submission_execution_blocker_owner_status_digest_20260610",
        "status": "execution_blocker_owner_status_digest_not_execution",
        "sources": {
            "reviewer_action_map": rel(action_map_path),
            "execution_authorization_blocker_index": rel(auth_blockers_path),
            "blocked_gate_triage_map": rel(triage_map_path),
            "readiness_dashboard": rel(dashboard_path),
            "reviewer_open_file_checksum_index": rel(checksum_index_path),
        },
        "summary": summary,
        "owner_groups": owner_records,
        "actions": actions,
        "execution_targets": list(target_lookup.values()),
        "issues": issues,
        "claim_boundary": [
            "This owner/status digest is a static navigation artifact only.",
            "It does not answer review questions.",
            "It does not fill or copy decision answers.",
            "It does not edit decision artifacts.",
            "It does not approve or reject any decision.",
            "It does not install PDF tooling.",
            "It does not create final artifacts.",
            "It does not run commands.",
            "It does not export PDFs.",
            "It does not record or render demo video.",
            "It does not write PMO final acceptance.",
            "It does not run MWORKS, ROS2, UE, or visible-thread dispatch tools.",
        ],
    }


def write_markdown(digest: dict[str, Any], path: Path) -> None:
    summary = digest["summary"]
    lines = [
        "# Final Submission Execution-Blocker Owner/Status Digest, 2026-06-10",
        "",
        f"Status: `{digest['status']}`",
        "",
        "## Summary",
        "",
        f"- Owners: `{summary['owner_count']}`",
        f"- Actions: `{summary['action_count']}`",
        f"- Execution targets: `{summary['execution_target_count']}`",
        f"- Blocked execution targets: `{summary['blocked_execution_target_count']}`",
        f"- Target/action references: `{summary['target_action_reference_count']}`",
        f"- Blocked artifacts: `{summary['blocked_artifact_count']}`",
        f"- Blocker classes: `{summary['blocker_class_count']}`",
        f"- Dashboard blocking gates: `{summary['dashboard_blocking_gate_count']}`",
        f"- Dashboard blockers: `{summary['dashboard_blocker_count']}`",
        f"- Reviewer open files: `{summary['reviewer_open_file_count']}`",
        f"- Reviewer open-file drift: `{summary['reviewer_open_file_drift_count']}`",
        f"- Issues: `{summary['issue_count']}`",
        f"- Runs commands now: `{summary['runs_commands_now']}`",
        f"- Authorizes execution now: `{summary['authorizes_execution_now']}`",
        f"- Generates final outputs: `{summary['generates_final_outputs']}`",
        f"- Final acceptance: `{summary['final_acceptance']}`",
        "",
        "## Owner Groups",
        "",
    ]
    for owner in digest["owner_groups"]:
        lines.extend(
            [
                f"### {owner['owner']}",
                "",
                f"- Actions: `{', '.join(owner['action_ids'])}`",
                f"- Targets: `{', '.join(owner['target_ids'])}`",
                f"- Blocker classes: `{', '.join(owner['blocker_classes'])}`",
                f"- Blocked artifacts: `{owner['blocked_artifact_count']}`",
                "",
            ]
        )
        for item in owner["decision_needed"]:
            lines.append(f"  - {item}")
        lines.append("")
    lines.extend(["## Action Status", ""])
    for action in digest["actions"]:
        lines.extend(
            [
                f"### {action['action_id']}",
                "",
                f"- Owner: `{action['owner']}`",
                f"- Priority: `{action['priority']}`",
                f"- Targets: `{', '.join(action['target_ids'])}`",
                f"- Blocker classes: `{', '.join(action['blocker_classes'])}`",
                f"- Decision needed: {action['decision_needed']}",
                "",
            ]
        )
    lines.extend(["## Issues", ""])
    if digest["issues"]:
        for item in digest["issues"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.extend(["", "## Claim Boundary", ""])
    for item in digest["claim_boundary"]:
        lines.append(f"- {item}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action-map", default=str(DEFAULT_ACTION_MAP.relative_to(ROOT)))
    parser.add_argument("--auth-blockers", default=str(DEFAULT_AUTH_BLOCKERS.relative_to(ROOT)))
    parser.add_argument("--triage-map", default=str(DEFAULT_TRIAGE_MAP.relative_to(ROOT)))
    parser.add_argument("--dashboard", default=str(DEFAULT_DASHBOARD.relative_to(ROOT)))
    parser.add_argument("--checksum-index", default=str(DEFAULT_CHECKSUM_INDEX.relative_to(ROOT)))
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR.relative_to(ROOT)))
    args = parser.parse_args()

    output_dir = repo_path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    digest = build_digest(
        repo_path(args.action_map),
        repo_path(args.auth_blockers),
        repo_path(args.triage_map),
        repo_path(args.dashboard),
        repo_path(args.checksum_index),
    )
    json_path = output_dir / "final_submission_execution_blocker_owner_status_digest.json"
    md_path = output_dir / "final_submission_execution_blocker_owner_status_digest.md"
    json_path.write_text(json.dumps(digest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(digest, md_path)
    print(
        json.dumps(
            {
                "ok": not digest["issues"],
                **digest["summary"],
                "json": rel(json_path),
                "markdown": rel(md_path),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not digest["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
