#!/usr/bin/env python3
"""Human-review queue and closeout verification for CoAgent runtime tasks."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "Results" / "agent_runtime" / "tasks.sqlite3"
REVIEW_ROOT = ROOT / "Results" / "agent_packets" / "reviews"
NOTIFICATION_ROOT = ROOT / "Results" / "agent_packets" / "notifications"
CLOSEOUT_ROOT = ROOT / "Results" / "agent_packets" / "closeouts"
TERMINAL_STATES = {"done", "done_with_concerns", "blocked", "failed", "cancelled"}
REVIEW_STATUSES_OK = {"", "accepted", "not_required"}
REVIEW_DECISIONS = {"accepted", "accepted_with_concerns", "needs_rework", "rejected"}

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.runtime import mosim_agent_runtime as runtime
from CoAgent.gateway import cc_connect_weixin
from CoAgent.hooks import preflight


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def project_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def now_stamp() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def review_file_for(task_id: str) -> tuple[str, dict[str, Any]]:
    path = REVIEW_ROOT / f"{task_id}.review.json"
    if path.exists():
        return rel(path), read_json(path)
    return "", {}


def review_reason(task: dict[str, Any], metadata: dict[str, Any], review: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    review_status = str(metadata.get("review_status") or review.get("status") or "")
    if review_status in {"accepted", "accepted_with_concerns"} and metadata.get("human_needed", "") != "yes":
        return []
    if metadata.get("human_needed") == "yes":
        reasons.append("human_needed=yes")
    metadata_requires_review = metadata.get("requires_human_review")
    if metadata_requires_review is not False and (metadata_requires_review is True or review.get("requires_human_review") is True):
        reasons.append("requires_human_review=true")
    if review_status not in REVIEW_STATUSES_OK:
        reasons.append(f"review_status={review_status}")
    if task["state"] in {"blocked", "failed", "done_with_concerns"}:
        reasons.append(f"state={task['state']}")
    return sorted(dict.fromkeys(reasons))


def priority_for(task: dict[str, Any], metadata: dict[str, Any], reasons: list[str]) -> int:
    if task["state"] == "failed":
        return 10
    if task["state"] == "blocked":
        return 20
    if task["state"] == "done_with_concerns":
        return 30
    if metadata.get("human_needed") == "yes":
        return 40
    if reasons:
        return 50
    return 100


def load_tasks(db: Path) -> list[dict[str, Any]]:
    if not db.exists():
        return []
    with runtime.open_db(db) as connection:
        rows = connection.execute("SELECT * FROM tasks ORDER BY priority ASC, updated_at DESC").fetchall()
    return [runtime.row_to_dict(row) for row in rows]


def task_by_id(tasks: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {task["task_id"]: task for task in tasks}


def superseded_parent_reason(task: dict[str, Any], tasks_by_id: dict[str, dict[str, Any]]) -> str:
    parent_task_id = str(task.get("metadata", {}).get("parent_task_id") or "")
    if not parent_task_id:
        return ""
    parent = tasks_by_id.get(parent_task_id)
    if not parent:
        return ""
    if parent["state"] in {"cancelled", "done", "failed"}:
        return f"parent_task_{parent['state']}:{parent_task_id}"
    return ""


def build_queue(args: argparse.Namespace) -> dict[str, Any]:
    db = args.db if args.db.is_absolute() else ROOT / args.db
    if not (db.resolve() == ROOT.resolve() or ROOT.resolve() in db.resolve().parents):
        raise SystemExit(f"db path is outside MoSim: {args.db}")
    tasks = load_tasks(db)
    tasks_by_id = task_by_id(tasks)
    items: list[dict[str, Any]] = []
    suppressed: list[dict[str, str]] = []
    for task in tasks:
        metadata = task.get("metadata", {})
        superseded_reason = superseded_parent_reason(task, tasks_by_id)
        if superseded_reason and not args.include_superseded:
            suppressed.append({"task_id": task["task_id"], "reason": superseded_reason})
            continue
        review_path, review = review_file_for(task["task_id"])
        reasons = review_reason(task, metadata, review)
        if not reasons:
            continue
        if task["state"] in TERMINAL_STATES and not args.include_terminal and task["state"] not in {"blocked", "failed", "done_with_concerns"}:
            continue
        items.append(
            {
                "task_id": task["task_id"],
                "state": task["state"],
                "priority": priority_for(task, metadata, reasons),
                "owner": task["owner"],
                "role": task["role"],
                "updated_at": task["updated_at"],
                "last_event_at": task["last_event_at"],
                "review_status": metadata.get("review_status") or review.get("status", ""),
                "human_needed": metadata.get("human_needed", ""),
                "next_action": metadata.get("next_action", ""),
                "summary_path": metadata.get("summary_path", ""),
                "review_path": metadata.get("review_path", review_path),
                "review_closeout_path": metadata.get("review_closeout_path", ""),
                "notification_packet_path": metadata.get("notification_packet_path", ""),
                "archive_path": metadata.get("archive_path", ""),
                "reasons": reasons,
            }
        )
    items.sort(key=lambda item: (item["priority"], item["updated_at"], item["task_id"]))
    return {"count": len(items), "items": items, "suppressed_count": len(suppressed), "suppressed": suppressed}


def print_text(queue: dict[str, Any]) -> None:
    if not queue["items"]:
        print("review_queue empty")
        return
    for item in queue["items"]:
        print(
            f"{item['priority']:03d} {item['state']:18s} {item['task_id']} "
            f"review={item['review_status']} human={item['human_needed']} next={item['next_action']}"
        )
        for key in ["summary_path", "review_path", "review_closeout_path", "notification_packet_path"]:
            if item.get(key):
                print(f"    {key}: {item[key]}")


def notification_class_for(task: dict[str, Any], item: dict[str, Any]) -> str:
    metadata = task.get("metadata", {})
    canonical_status = str(metadata.get("canonical_status") or "")
    review_status = str(item.get("review_status") or "")
    if canonical_status == "auth_required":
        return "auth_required"
    if task["state"] == "failed" or review_status in {"rejected", "needs_rework"}:
        return "incident_required"
    if task["state"] == "blocked" and canonical_status not in {"review_required", "done_with_concerns"}:
        return "incident_required"
    return "manual_review_required"


def severity_for(task: dict[str, Any], item: dict[str, Any]) -> str:
    metadata = task.get("metadata", {})
    if metadata.get("canonical_status") == "auth_required":
        return "high"
    if task["state"] == "failed" or item.get("review_status") in {"rejected", "needs_rework"}:
        return "high"
    if task["state"] == "blocked":
        return "medium"
    return "low"


def evidence_paths_for(task: dict[str, Any], item: dict[str, Any]) -> list[str]:
    metadata = task.get("metadata", {})
    evidence: list[str] = []
    for value in metadata.get("evidence", []):
        evidence.append(str(value))
    for key in ["summary_path", "review_path", "archive_path", "status_export_path", "status_export_markdown"]:
        value = item.get(key) or metadata.get(key)
        if value:
            evidence.append(str(value))
    return list(dict.fromkeys(evidence))[:8]


def build_notification_packet(task: dict[str, Any], item: dict[str, Any]) -> dict[str, Any]:
    metadata = task.get("metadata", {})
    task_id = task["task_id"]
    next_action = (
        item.get("next_action")
        or metadata.get("next_recommended_action")
        or metadata.get("human_action_required")
        or "请审核该 CoAgent 任务并确认下一步。"
    )
    blocked_surface = metadata.get("checkpoint") or task.get("objective") or task.get("role") or "CoAgent review queue"
    return {
        "template_type": "blocker_notification",
        "task_id": task_id,
        "severity": severity_for(task, item),
        "class": notification_class_for(task, item),
        "dedupe_key": f"review-queue:{task_id}:{task['state']}:{item.get('review_status', '')}",
        "blocked_surface": blocked_surface,
        "human_action_required": next_action,
        "why_now": "; ".join(item.get("reasons", [])),
        "evidence_paths": evidence_paths_for(task, item),
        "resume_packet_path": item.get("summary_path") or metadata.get("status_export_markdown", ""),
        "review_status": item.get("review_status", ""),
        "canonical_status": metadata.get("canonical_status", ""),
    }


def task_for_notify(db: Path, task_id: str) -> dict[str, Any]:
    return runtime.show_task(argparse.Namespace(db=db, events=runtime.DEFAULT_EVENTS, task_id=task_id))


def notify_task(args: argparse.Namespace) -> dict[str, Any]:
    db = args.db if args.db.is_absolute() else ROOT / args.db
    if not (db.resolve() == ROOT.resolve() or ROOT.resolve() in db.resolve().parents):
        raise SystemExit(f"db path is outside MoSim: {args.db}")
    queue = build_queue(
        argparse.Namespace(
            db=db,
            include_terminal=args.include_terminal,
            include_superseded=args.include_superseded,
            json=True,
        )
    )
    item = next((entry for entry in queue["items"] if entry["task_id"] == args.task_id), None)
    if item is None:
        raise SystemExit(f"task is not currently in the review queue: {args.task_id}")
    task = task_for_notify(db, args.task_id)
    packet = build_notification_packet(task, item)
    packet_output = args.packet_output or (NOTIFICATION_ROOT / f"{args.task_id}.review_queue.{now_stamp()}.weixin_notification.json")
    packet_path = project_path(packet_output)
    packet_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    notification = cc_connect_weixin.notify(
        argparse.Namespace(
            packet=packet_path,
            project=args.weixin_project,
            session=args.weixin_session,
            data_dir=args.weixin_data_dir,
            cc_bin=args.weixin_cc_bin,
            config=args.weixin_config,
            audit=args.weixin_audit,
            dedupe=args.weixin_dedupe,
            max_chars=args.weixin_max_chars,
            timeout=args.weixin_timeout,
            send=args.send_weixin,
            force=args.force_weixin,
            omit_message_in_audit=args.omit_weixin_message_in_audit,
        )
    )
    metadata_state: dict[str, Any] | None = None
    metadata_error = ""
    if not args.no_metadata_update:
        patch = {
            "notification_packet_path": rel(packet_path),
            "notification_enabled": True,
            "notification_source": "review_queue",
            "notification_send_reason": str(notification.get("send_result", {}).get("reason", "")),
        }
        try:
            metadata_state = runtime.update_metadata(
                argparse.Namespace(
                    db=db,
                    events=args.events,
                    task_id=args.task_id,
                    actor=args.actor,
                    claim_token=args.claim_token,
                    summary="review queue notification packet generated",
                    metadata=json.dumps(patch, ensure_ascii=False, sort_keys=True),
                )
            )
        except SystemExit as exc:
            metadata_error = str(exc)
    return {
        "ok": bool(notification.get("ok")),
        "task_id": args.task_id,
        "packet_path": rel(packet_path),
        "notification": notification,
        "metadata_updated": metadata_state is not None,
        "metadata_error": metadata_error,
    }


def closeout_artifact_path(args: argparse.Namespace) -> Path:
    output = getattr(args, "closeout_output", None)
    if output:
        return project_path(output)
    return CLOSEOUT_ROOT / f"{args.task_id}.review_closeout.{now_stamp()}.json"


def closeout_review(args: argparse.Namespace) -> dict[str, Any]:
    if args.decision not in REVIEW_DECISIONS:
        raise SystemExit(f"invalid decision: {args.decision}")
    db = args.db if args.db.is_absolute() else ROOT / args.db
    if not (db.resolve() == ROOT.resolve() or ROOT.resolve() in db.resolve().parents):
        raise SystemExit(f"db path is outside MoSim: {args.db}")
    task = runtime.show_task(argparse.Namespace(db=db, events=args.events, task_id=args.task_id))
    metadata = dict(task.get("metadata", {}))
    closeout_path = closeout_artifact_path(args)
    closeout_path.parent.mkdir(parents=True, exist_ok=True)
    previous_review_state = {
        "task_state": task.get("state", ""),
        "review_status": metadata.get("review_status", ""),
        "human_needed": metadata.get("human_needed", ""),
        "requires_human_review": metadata.get("requires_human_review", ""),
        "next_action": metadata.get("next_action", ""),
        "review_path": metadata.get("review_path", ""),
        "notification_packet_path": metadata.get("notification_packet_path", ""),
        "review_closeout_path": metadata.get("review_closeout_path", ""),
    }
    patch = {
        "review_status": args.decision,
        "review_decision_by": args.actor,
        "review_decision_reason": args.reason,
        "requires_human_review": args.decision not in {"accepted", "accepted_with_concerns"},
        "human_needed": "" if args.decision in {"accepted", "accepted_with_concerns"} else "yes",
        "next_action": args.next_action,
        "review_closeout_path": rel(closeout_path),
    }
    if args.evidence:
        existing = metadata.get("review_evidence", [])
        if not isinstance(existing, list):
            existing = [str(existing)]
        patch["review_evidence"] = [*existing, *args.evidence]
    updated = runtime.update_metadata(
        argparse.Namespace(
            db=db,
            events=args.events,
            task_id=args.task_id,
            actor=args.actor,
            claim_token=args.claim_token,
            summary=f"human review closeout: {args.decision}",
            metadata=json.dumps(patch, ensure_ascii=False, sort_keys=True),
        )
    )
    resulting_metadata = updated.get("metadata", {})
    closeout_payload = {
        "schema_type": "coagent_review_closeout",
        "schema_version": 1,
        "task_id": args.task_id,
        "actor": args.actor,
        "timestamp": runtime.now_iso(),
        "decision": args.decision,
        "reason": args.reason,
        "next_action": args.next_action,
        "evidence": args.evidence,
        "previous_review_state": previous_review_state,
        "resulting_metadata": {
            "review_status": resulting_metadata.get("review_status", ""),
            "human_needed": resulting_metadata.get("human_needed", ""),
            "requires_human_review": resulting_metadata.get("requires_human_review", ""),
            "next_action": resulting_metadata.get("next_action", ""),
            "review_evidence": resulting_metadata.get("review_evidence", []),
            "review_closeout_path": resulting_metadata.get("review_closeout_path", ""),
        },
        "runtime": {
            "state": updated.get("state", ""),
            "owner": updated.get("owner", ""),
            "role": updated.get("role", ""),
            "updated_at": updated.get("updated_at", ""),
            "last_event_at": updated.get("last_event_at", ""),
        },
    }
    closeout_path.write_text(json.dumps(closeout_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "task_id": args.task_id,
        "decision": args.decision,
        "human_needed": patch["human_needed"],
        "next_action": args.next_action,
        "closeout_path": rel(closeout_path),
        "runtime_state": updated,
    }


def closeout_review_command(task_id: str) -> str:
    return (
        "python3 CoAgent/review_queue/review_queue.py closeout "
        f"--task-id {task_id} "
        "--decision <accepted|accepted_with_concerns|needs_rework|rejected> "
        "--reason \"<manual review reason>\" "
        "--next-action \"<next action>\" "
        "--claim-token <claim-token>"
    )


def closeout_artifact_for(metadata: dict[str, Any]) -> dict[str, Any]:
    path = str(metadata.get("review_closeout_path") or "")
    if not path:
        return {"exists": False, "path": "", "valid": False}
    resolved = project_path(Path(path))
    if not resolved.exists():
        return {"exists": False, "path": path, "valid": False}
    try:
        data = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"exists": True, "path": rel(resolved), "valid": False, "error": str(exc)}
    if not isinstance(data, dict):
        return {"exists": True, "path": rel(resolved), "valid": False, "error": "closeout JSON is not an object"}
    return {
        "exists": True,
        "path": rel(resolved),
        "valid": True,
        "data": data,
        "decision": data.get("decision", ""),
        "reason": data.get("reason", ""),
        "next_action": data.get("next_action", ""),
        "actor": data.get("actor", ""),
    }


def task_health_for_closeout(args: argparse.Namespace, db: Path) -> dict[str, Any]:
    from CoAgent.task_health import task_health

    snapshot = task_health.build_snapshot(
        argparse.Namespace(
            db=db,
            events=args.events,
            task_id=args.task_id,
            state="",
            active_only=True,
            stale_minutes=args.stale_minutes,
            staged_file_warning_threshold=getattr(args, "staged_file_warning_threshold", preflight.STAGED_BROAD_THRESHOLD),
            skip_preflight=getattr(args, "skip_preflight", False),
            skip_runtime_audit=False,
        )
    )
    task_item = next((item for item in snapshot.get("tasks", []) if item.get("task_id") == args.task_id), {})
    return {
        "ok": snapshot.get("ok"),
        "decision": snapshot.get("decision", {}),
        "task": task_item,
        "warning_count": snapshot.get("warning_count", 0),
        "fail_count": snapshot.get("fail_count", 0),
    }


def closeout_verification_effect(
    *,
    task: dict[str, Any],
    metadata: dict[str, Any],
    decision: str,
    queue_item: dict[str, Any] | None,
    health: dict[str, Any],
) -> dict[str, Any]:
    task_decision = health.get("task", {}).get("decision", {})
    continue_allowed = bool(task_decision.get("continue_allowed"))
    runtime_state = str(task.get("state", ""))
    terminal_runtime = runtime_state in runtime.TERMINAL_STATES
    queue_present = queue_item is not None
    review_unblocked = not queue_present and str(metadata.get("human_needed") or "") != "yes"
    if decision in {"accepted", "accepted_with_concerns"}:
        if terminal_runtime:
            runtime_continuation = "terminal_close_ready"
            expected_effect_ok = review_unblocked
            next_action = "close the terminal task or create a follow-up task; closeout does not automatically resume terminal runtime state"
        elif continue_allowed:
            runtime_continuation = "continue_allowed"
            expected_effect_ok = review_unblocked
            next_action = "continue approved work; carry any accepted-with-concerns watch item into the next checkpoint"
        else:
            runtime_continuation = "blocked_after_closeout"
            expected_effect_ok = False
            next_action = str(task_decision.get("next_intervention") or "inspect task health before continuing")
    elif decision in {"needs_rework", "rejected"}:
        runtime_continuation = "blocked_by_review_decision"
        expected_effect_ok = not continue_allowed
        next_action = str(task_decision.get("next_intervention") or "rework or reject the current implementation path before continuing")
    else:
        runtime_continuation = "not_applicable"
        expected_effect_ok = review_unblocked
        next_action = "no review closeout is currently required" if expected_effect_ok else "record a review closeout or clear the review queue item"
    return {
        "expected_effect_ok": expected_effect_ok,
        "review_unblocked": review_unblocked,
        "review_queue_item_present": queue_present,
        "runtime_state": runtime_state,
        "runtime_continuation": runtime_continuation,
        "task_health_continue_allowed": continue_allowed,
        "task_health_recommended_action": task_decision.get("recommended_action", ""),
        "next_action": next_action,
    }


def verify_closeout(args: argparse.Namespace) -> dict[str, Any]:
    db = args.db if args.db.is_absolute() else ROOT / args.db
    if not (db.resolve() == ROOT.resolve() or ROOT.resolve() in db.resolve().parents):
        raise SystemExit(f"db path is outside MoSim: {args.db}")
    task = runtime.show_task(argparse.Namespace(db=db, events=args.events, task_id=args.task_id))
    metadata = dict(task.get("metadata", {}))
    review_status = str(metadata.get("review_status") or "")
    decision = review_status if review_status in REVIEW_DECISIONS else ""
    closeout_required = decision != ""
    artifact = closeout_artifact_for(metadata)
    queue = build_queue(
        argparse.Namespace(
            db=db,
            include_terminal=True,
            include_superseded=args.include_superseded,
            json=True,
        )
    )
    queue_item = next((item for item in queue.get("items", []) if item.get("task_id") == args.task_id), None)
    health = task_health_for_closeout(args, db)
    findings: list[dict[str, Any]] = []

    artifact_ok = True
    if closeout_required:
        artifact_ok = bool(artifact.get("valid"))
        if not artifact.get("exists"):
            findings.append(
                {
                    "severity": "fail",
                    "reason": "missing_review_closeout_artifact",
                    "evidence": str(metadata.get("review_closeout_path") or "runtime metadata"),
                    "next_action": closeout_review_command(args.task_id),
                }
            )
        elif not artifact.get("valid"):
            findings.append(
                {
                    "severity": "fail",
                    "reason": "invalid_review_closeout_artifact",
                    "evidence": str(artifact.get("path", "")),
                    "next_action": "repair or regenerate the review closeout artifact",
                    "error": artifact.get("error", ""),
                }
            )
        else:
            payload = artifact.get("data", {})
            if str(payload.get("task_id") or "") != args.task_id:
                artifact_ok = False
                findings.append(
                    {
                        "severity": "fail",
                        "reason": "review_closeout_task_mismatch",
                        "evidence": str(artifact.get("path", "")),
                        "next_action": "inspect runtime metadata and closeout artifact before relying on this decision",
                        "artifact_task_id": payload.get("task_id", ""),
                    }
                )
            if str(payload.get("decision") or "") != decision:
                artifact_ok = False
                findings.append(
                    {
                        "severity": "fail",
                        "reason": "review_closeout_decision_mismatch",
                        "evidence": str(artifact.get("path", "")),
                        "next_action": "inspect runtime metadata and closeout artifact before relying on this decision",
                        "metadata_decision": decision,
                        "artifact_decision": payload.get("decision", ""),
                    }
                )
            resulting = payload.get("resulting_metadata", {}) if isinstance(payload.get("resulting_metadata"), dict) else {}
            if resulting and str(resulting.get("review_status") or "") != decision:
                artifact_ok = False
                findings.append(
                    {
                        "severity": "fail",
                        "reason": "review_closeout_result_metadata_mismatch",
                        "evidence": str(artifact.get("path", "")),
                        "next_action": "regenerate closeout or repair runtime metadata",
                        "metadata_decision": decision,
                        "artifact_resulting_review_status": resulting.get("review_status", ""),
                    }
                )
    elif queue_item or metadata.get("human_needed") == "yes":
        artifact_ok = False
        findings.append(
            {
                "severity": "fail",
                "reason": "review_item_without_closeout_decision",
                "evidence": queue_item.get("review_path", "runtime metadata") if queue_item else "runtime metadata",
                "next_action": closeout_review_command(args.task_id),
            }
        )

    effect = closeout_verification_effect(
        task=task,
        metadata=metadata,
        decision=decision,
        queue_item=queue_item,
        health=health,
    )
    if not effect["expected_effect_ok"]:
        findings.append(
            {
                "severity": "fail",
                "reason": "review_closeout_effect_mismatch",
                "evidence": "review queue + task health",
                "next_action": effect["next_action"],
                "runtime_continuation": effect["runtime_continuation"],
            }
        )
    if decision == "accepted_with_concerns":
        findings.append(
            {
                "severity": "info",
                "reason": "accepted_with_concerns_watch",
                "evidence": str(artifact.get("path", metadata.get("review_closeout_path", ""))),
                "next_action": "carry the concern into the next checkpoint and review package",
            }
        )
    if effect["runtime_continuation"] == "terminal_close_ready":
        findings.append(
            {
                "severity": "info",
                "reason": "terminal_runtime_after_closeout",
                "evidence": f"state={task.get('state', '')}",
                "next_action": effect["next_action"],
            }
        )

    result = {
        "schema_type": "coagent_review_closeout_verification",
        "schema_version": 1,
        "task_id": args.task_id,
        "ok": bool(artifact_ok and effect["expected_effect_ok"]),
        "closeout_required": closeout_required,
        "decision": decision,
        "review_status": review_status,
        "human_needed": metadata.get("human_needed", ""),
        "requires_human_review": metadata.get("requires_human_review", ""),
        "artifact": {
            key: value
            for key, value in artifact.items()
            if key not in {"data"}
        },
        "effect": effect,
        "review_queue_item": queue_item or {},
        "task_health": health,
        "closeout_command": closeout_review_command(args.task_id),
        "findings": findings,
    }
    outputs: dict[str, str] = {}
    if args.output:
        output = project_path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        outputs["json"] = rel(output)
    if args.markdown_output:
        outputs["markdown"] = write_closeout_verification_markdown(project_path(args.markdown_output), result)
    result["outputs"] = outputs
    return result


def write_closeout_verification_markdown(path: Path, result: dict[str, Any]) -> str:
    effect = result.get("effect", {})
    artifact = result.get("artifact", {})
    lines = [
        "# CoAgent Review Closeout Verification",
        "",
        f"- task_id: `{result['task_id']}`",
        f"- ok: `{result['ok']}`",
        f"- closeout_required: `{result['closeout_required']}`",
        f"- decision: `{result.get('decision', '')}`",
        f"- review_status: `{result.get('review_status', '')}`",
        f"- human_needed: `{result.get('human_needed', '')}`",
        f"- artifact_exists: `{artifact.get('exists', '')}`",
        f"- artifact_valid: `{artifact.get('valid', '')}`",
        f"- artifact_path: `{artifact.get('path', '')}`",
        f"- review_unblocked: `{effect.get('review_unblocked', '')}`",
        f"- runtime_continuation: `{effect.get('runtime_continuation', '')}`",
        f"- task_health_continue_allowed: `{effect.get('task_health_continue_allowed', '')}`",
        f"- next_action: {effect.get('next_action', '')}",
        "",
        "## Findings",
        "",
    ]
    findings = result.get("findings", [])
    if not findings:
        lines.append("- none")
    for item in findings:
        lines.append(f"- `{item.get('severity', '')}` `{item.get('reason', '')}` -> {item.get('next_action', '')}")
    lines.extend(["", "## Closeout Command", "", f"`{result.get('closeout_command', '')}`"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rel(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    list_parser.add_argument("--include-terminal", action="store_true")
    list_parser.add_argument("--include-superseded", action="store_true")
    list_parser.add_argument("--json", action="store_true")
    list_parser.set_defaults(func=build_queue)

    close_parser = subparsers.add_parser("closeout")
    close_parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    close_parser.add_argument("--events", type=Path, default=runtime.DEFAULT_EVENTS)
    close_parser.add_argument("--task-id", required=True)
    close_parser.add_argument("--decision", required=True, choices=sorted(REVIEW_DECISIONS))
    close_parser.add_argument("--reason", required=True)
    close_parser.add_argument("--next-action", default="")
    close_parser.add_argument("--evidence", action="append", default=[])
    close_parser.add_argument("--closeout-output", type=Path)
    close_parser.add_argument("--actor", default="MainAgent")
    close_parser.add_argument("--claim-token", default="")
    close_parser.add_argument("--json", action="store_true")
    close_parser.set_defaults(func=closeout_review)

    notify_parser = subparsers.add_parser("notify")
    notify_parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    notify_parser.add_argument("--events", type=Path, default=runtime.DEFAULT_EVENTS)
    notify_parser.add_argument("--task-id", required=True)
    notify_parser.add_argument("--packet-output", type=Path)
    notify_parser.add_argument("--include-terminal", action="store_true")
    notify_parser.add_argument("--include-superseded", action="store_true")
    notify_parser.add_argument("--actor", default="MainAgent")
    notify_parser.add_argument("--claim-token", default="")
    notify_parser.add_argument("--no-metadata-update", action="store_true")
    notify_parser.add_argument("--send-weixin", action="store_true")
    notify_parser.add_argument("--weixin-session", default="")
    notify_parser.add_argument("--weixin-project", default=cc_connect_weixin.DEFAULT_PROJECT)
    notify_parser.add_argument("--weixin-data-dir", type=Path, default=cc_connect_weixin.DEFAULT_DATA_DIR)
    notify_parser.add_argument("--weixin-cc-bin", type=Path, default=cc_connect_weixin.DEFAULT_BIN)
    notify_parser.add_argument("--weixin-config", type=Path, default=cc_connect_weixin.DEFAULT_CONFIG)
    notify_parser.add_argument("--weixin-audit", type=Path, default=cc_connect_weixin.DEFAULT_AUDIT)
    notify_parser.add_argument("--weixin-dedupe", type=Path, default=cc_connect_weixin.DEFAULT_DEDUPE)
    notify_parser.add_argument("--weixin-max-chars", type=int, default=1500)
    notify_parser.add_argument("--weixin-timeout", type=int, default=60)
    notify_parser.add_argument("--force-weixin", action="store_true")
    notify_parser.add_argument("--omit-weixin-message-in-audit", action="store_true")
    notify_parser.add_argument("--json", action="store_true")
    notify_parser.set_defaults(func=notify_task)

    verify_parser = subparsers.add_parser("verify-closeout")
    verify_parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    verify_parser.add_argument("--events", type=Path, default=runtime.DEFAULT_EVENTS)
    verify_parser.add_argument("--task-id", required=True)
    verify_parser.add_argument("--include-superseded", action="store_true")
    verify_parser.add_argument("--stale-minutes", type=int, default=120)
    verify_parser.add_argument("--skip-preflight", action="store_true")
    verify_parser.add_argument("--staged-file-warning-threshold", type=int, default=preflight.STAGED_BROAD_THRESHOLD)
    verify_parser.add_argument("--output", type=Path)
    verify_parser.add_argument("--markdown-output", type=Path)
    verify_parser.add_argument("--json", action="store_true")
    verify_parser.set_defaults(func=verify_closeout)
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0].startswith("-"):
        argv = ["list", *argv]
    args = build_parser().parse_args(argv)
    if not args.command:
        args.command = "list"
        args.func = build_queue
        args.db = DEFAULT_DB
        args.include_terminal = False
        args.include_superseded = False
        args.json = False
    result = args.func(args)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    elif args.command == "closeout":
        print(f"review_closeout ok task_id={result['task_id']} decision={result['decision']}")
    else:
        print_text(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
