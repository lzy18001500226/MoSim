#!/usr/bin/env python3
"""Minimal durable task queue and event stream for MoSim agent work.

This is intentionally small. It does not call LLM APIs or spawn Codex
subagents. Its job is to keep task state recoverable across chat/session loss.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "Results" / "agent_runtime" / "tasks.sqlite3"
DEFAULT_EVENTS = ROOT / "Results" / "agent_runtime" / "events.jsonl"
ALLOWED_ROOT = ROOT.resolve()


TERMINAL_STATES = {"done", "done_with_concerns", "blocked", "failed", "cancelled"}
VALID_STATES = {"queued", "claimed", "running", *TERMINAL_STATES}
RUNTIME_TO_CANONICAL_STATE = {
    "queued": "ready",
    "claimed": "working",
    "running": "working",
    "done": "completed",
    "done_with_concerns": "review_required",
    "blocked": "blocked",
    "failed": "failed",
    "cancelled": "canceled",
}
CANONICAL_TO_RUNTIME_STATE = {
    "planned": "queued",
    "ready": "queued",
    "working": "running",
    "input_required": "blocked",
    "auth_required": "blocked",
    "review_required": "done_with_concerns",
    "blocked": "blocked",
    "failed": "failed",
    "completed": "done",
    "canceled": "cancelled",
    "rejected": "failed",
    "superseded": "cancelled",
}
CANONICAL_TASK_CLASSES = {
    "simple_message",
    "clear_task",
    "complicated_task",
    "complex_task",
    "chaotic_incident",
    "disordered_task",
    "long_running_task",
}
VALID_EVENTS = {
    "task_created",
    "task_claimed",
    "heartbeat",
    "checkpoint",
    "task_completed",
    "task_blocked",
    "task_failed",
    "task_cancelled",
    "conversation_linked",
    "conversation_closed",
}
VALID_EDGE_STATUSES = {"open", "closed"}
SENSITIVE_OUTPUT_KEYS = {"claim_token", "token", "access_token", "refresh_token", "api_key", "secret", "password"}
REDACTED = "<redacted>"


def canonical_state(state: str) -> str:
    return RUNTIME_TO_CANONICAL_STATE.get(state, state)


def runtime_state(state: str) -> str:
    return CANONICAL_TO_RUNTIME_STATE.get(state, state)


def metadata_string(metadata: dict[str, Any], key: str, default: str = "") -> str:
    value = metadata.get(key, default)
    if value in (None, ""):
        return default
    return str(value)


def metadata_list(metadata: dict[str, Any], key: str) -> list[str]:
    value = metadata.get(key, [])
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def task_class_for(metadata: dict[str, Any]) -> str:
    task_class = metadata_string(metadata, "task_class", "")
    if task_class in CANONICAL_TASK_CLASSES:
        return task_class
    if metadata.get("task_conversation") or metadata.get("checkpoint_plan"):
        return "long_running_task"
    return "clear_task"


def redact_for_output(value: Any, *, reveal_claim_token: bool = False) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            normalized = str(key).lower()
            if normalized == "claim_token" and reveal_claim_token:
                redacted[key] = item
            elif normalized in SENSITIVE_OUTPUT_KEYS or normalized.endswith("_token"):
                redacted[key] = REDACTED if item else item
            else:
                redacted[key] = redact_for_output(item, reveal_claim_token=reveal_claim_token)
        return redacted
    if isinstance(value, list):
        return [redact_for_output(item, reveal_claim_token=reveal_claim_token) for item in value]
    return value


def contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower()
            if normalized in SENSITIVE_OUTPUT_KEYS or normalized.endswith("_token"):
                if item not in ("", None, REDACTED):
                    return True
                continue
            if contains_sensitive_key(item):
                return True
    elif isinstance(value, list):
        return any(contains_sensitive_key(item) for item in value)
    return False


def redact_event_data(value: Any) -> Any:
    return redact_for_output(value, reveal_claim_token=False)


@dataclass(frozen=True)
class Event:
    event_id: str
    timestamp: str
    task_id: str
    event_type: str
    actor: str
    summary: str
    data: dict[str, Any]


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def parse_json_object(value: str | None, *, field: str) -> dict[str, Any]:
    if value in (None, ""):
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{field} must be valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise SystemExit(f"{field} must be a JSON object")
    return parsed


def normalize_paths(values: list[str] | None, *, field: str) -> list[str]:
    paths: list[str] = []
    for raw in values or []:
        path = Path(raw)
        candidate = path if path.is_absolute() else ROOT / path
        try:
            resolved = candidate.resolve()
        except OSError as exc:
            raise SystemExit(f"{field} contains an invalid path {raw!r}: {exc}") from exc
        if not (resolved == ALLOWED_ROOT or ALLOWED_ROOT in resolved.parents):
            raise SystemExit(f"{field} path is outside MoSim: {raw}")
        paths.append(str(resolved.relative_to(ALLOWED_ROOT)))
    return sorted(dict.fromkeys(paths))


def open_db(path: Path = DEFAULT_DB) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            objective TEXT NOT NULL,
            role TEXT NOT NULL,
            state TEXT NOT NULL,
            priority INTEGER NOT NULL DEFAULT 100,
            read_scope_json TEXT NOT NULL,
            write_scope_json TEXT NOT NULL,
            acceptance TEXT NOT NULL,
            stop_condition TEXT NOT NULL,
            dependencies_json TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            owner TEXT NOT NULL DEFAULT '',
            claim_token TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_event_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            event_type TEXT NOT NULL,
            actor TEXT NOT NULL,
            summary TEXT NOT NULL,
            data_json TEXT NOT NULL,
            FOREIGN KEY(task_id) REFERENCES tasks(task_id)
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_edges (
            edge_id TEXT PRIMARY KEY,
            parent_task_id TEXT NOT NULL,
            department TEXT NOT NULL,
            thread_id TEXT NOT NULL,
            thread_name TEXT NOT NULL DEFAULT '',
            conversation_role TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            UNIQUE(parent_task_id, thread_id),
            FOREIGN KEY(parent_task_id) REFERENCES tasks(task_id)
        )
        """
    )
    return connection


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    result = dict(row)
    for key in ["read_scope_json", "write_scope_json", "dependencies_json", "metadata_json"]:
        result[key.removesuffix("_json")] = json.loads(result.pop(key))
    return result


def append_jsonl(path: Path, event: Event) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(event), ensure_ascii=False, sort_keys=True) + "\n")


def load_event_log(path: Path = DEFAULT_EVENTS) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError as exc:
                events.append({"_invalid": True, "line": line_number, "error": str(exc), "text": stripped[:200]})
                continue
            if isinstance(parsed, dict):
                parsed["_line"] = line_number
                events.append(parsed)
            else:
                events.append({"_invalid": True, "line": line_number, "error": "event is not an object"})
    return events


def record_event(
    connection: sqlite3.Connection,
    *,
    task_id: str,
    event_type: str,
    actor: str,
    summary: str,
    data: dict[str, Any] | None = None,
    events_path: Path = DEFAULT_EVENTS,
) -> Event:
    if event_type not in VALID_EVENTS:
        raise SystemExit(f"invalid event_type: {event_type}")
    timestamp = now_iso()
    event = Event(
        event_id=f"evt_{uuid4().hex}",
        timestamp=timestamp,
        task_id=task_id,
        event_type=event_type,
        actor=actor,
        summary=summary,
        data=data or {},
    )
    connection.execute(
        """
        INSERT INTO events(event_id, task_id, timestamp, event_type, actor, summary, data_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event.event_id,
            event.task_id,
            event.timestamp,
            event.event_type,
            event.actor,
            event.summary,
            json.dumps(event.data, ensure_ascii=False, sort_keys=True),
        ),
    )
    connection.execute("UPDATE tasks SET last_event_at = ?, updated_at = ? WHERE task_id = ?", (timestamp, timestamp, task_id))
    append_jsonl(events_path, event)
    return event


def create_task(args: argparse.Namespace) -> dict[str, Any]:
    read_scope = normalize_paths(args.read_scope, field="read_scope")
    write_scope = normalize_paths(args.write_scope, field="write_scope")
    dependencies = args.depends_on or []
    metadata = parse_json_object(args.metadata, field="metadata")
    task_id = args.task_id or f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
    timestamp = now_iso()
    with open_db(args.db) as connection:
        connection.execute(
            """
            INSERT INTO tasks(
                task_id, objective, role, state, priority, read_scope_json, write_scope_json,
                acceptance, stop_condition, dependencies_json, metadata_json,
                created_at, updated_at, last_event_at
            )
            VALUES (?, ?, ?, 'queued', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                args.objective,
                args.role,
                args.priority,
                json.dumps(read_scope, ensure_ascii=False),
                json.dumps(write_scope, ensure_ascii=False),
                args.acceptance,
                args.stop_condition,
                json.dumps(dependencies, ensure_ascii=False),
                json.dumps(metadata, ensure_ascii=False, sort_keys=True),
                timestamp,
                timestamp,
                timestamp,
            ),
        )
        record_event(
            connection,
            task_id=task_id,
            event_type="task_created",
            actor=args.actor,
            summary=args.objective,
            data={"role": args.role, "priority": args.priority},
            events_path=args.events,
        )
        connection.commit()
        row = connection.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    return row_to_dict(row)


def claim_task(args: argparse.Namespace) -> dict[str, Any]:
    with open_db(args.db) as connection:
        if args.task_id:
            row = connection.execute("SELECT * FROM tasks WHERE task_id = ?", (args.task_id,)).fetchone()
        else:
            row = connection.execute(
                """
                SELECT * FROM tasks
                WHERE state = 'queued'
                ORDER BY priority ASC, created_at ASC
                LIMIT 1
                """
            ).fetchone()
        if row is None:
            raise SystemExit("no task available")
        task = row_to_dict(row)
        if task["state"] in TERMINAL_STATES:
            raise SystemExit(f"task is terminal or unavailable: {task['state']}")
        if task["state"] != "queued" and not args.force:
            raise SystemExit(f"task is already {task['state']}; use --force to reclaim explicitly")
        token = f"claim_{uuid4().hex}"
        timestamp = now_iso()
        connection.execute(
            "UPDATE tasks SET state = 'claimed', owner = ?, claim_token = ?, updated_at = ? WHERE task_id = ?",
            (args.owner, token, timestamp, task["task_id"]),
        )
        record_event(
            connection,
            task_id=task["task_id"],
            event_type="task_claimed",
            actor=args.owner,
            summary=f"claimed by {args.owner}",
            data={
                "force": bool(args.force),
                "previous_owner": task["owner"],
                "previous_state": task["state"],
                "claim_token_issued": True,
            },
            events_path=args.events,
        )
        connection.commit()
        row = connection.execute("SELECT * FROM tasks WHERE task_id = ?", (task["task_id"],)).fetchone()
    result = row_to_dict(row)
    result["claim_token"] = token
    return result


def update_task(args: argparse.Namespace, *, state: str, event_type: str) -> dict[str, Any]:
    if state not in VALID_STATES:
        raise SystemExit(f"invalid state: {state}")
    data = parse_json_object(args.data, field="data")
    with open_db(args.db) as connection:
        row = connection.execute("SELECT * FROM tasks WHERE task_id = ?", (args.task_id,)).fetchone()
        if row is None:
            raise SystemExit(f"unknown task: {args.task_id}")
        task = row_to_dict(row)
        if task["state"] in TERMINAL_STATES and event_type not in {"checkpoint"}:
            raise SystemExit(f"task is already terminal: {task['state']}")
        if task["claim_token"] and args.claim_token != task["claim_token"]:
            raise SystemExit("claim token required or mismatch")
        timestamp = now_iso()
        connection.execute(
            "UPDATE tasks SET state = ?, updated_at = ? WHERE task_id = ?",
            (state, timestamp, args.task_id),
        )
        record_event(
            connection,
            task_id=args.task_id,
            event_type=event_type,
            actor=args.actor,
            summary=args.summary,
            data=data,
            events_path=args.events,
        )
        connection.commit()
        row = connection.execute("SELECT * FROM tasks WHERE task_id = ?", (args.task_id,)).fetchone()
    return row_to_dict(row)


def update_metadata(args: argparse.Namespace) -> dict[str, Any]:
    patch = parse_json_object(args.metadata, field="metadata")
    if not patch:
        raise SystemExit("metadata patch must not be empty")
    with open_db(args.db) as connection:
        row = connection.execute("SELECT * FROM tasks WHERE task_id = ?", (args.task_id,)).fetchone()
        if row is None:
            raise SystemExit(f"unknown task: {args.task_id}")
        task = row_to_dict(row)
        if task["claim_token"] and args.claim_token != task["claim_token"]:
            raise SystemExit("claim token required or mismatch")
        metadata = dict(task["metadata"])
        metadata.update(patch)
        timestamp = now_iso()
        connection.execute(
            "UPDATE tasks SET metadata_json = ?, updated_at = ? WHERE task_id = ?",
            (json.dumps(metadata, ensure_ascii=False, sort_keys=True), timestamp, args.task_id),
        )
        record_event(
            connection,
            task_id=args.task_id,
            event_type="checkpoint",
            actor=args.actor,
            summary=args.summary,
            data={"metadata_patch_keys": sorted(patch)},
            events_path=args.events,
        )
        connection.commit()
        row = connection.execute("SELECT * FROM tasks WHERE task_id = ?", (args.task_id,)).fetchone()
    return row_to_dict(row)


def list_tasks(args: argparse.Namespace) -> dict[str, Any]:
    with open_db(args.db) as connection:
        params: list[Any] = []
        where = []
        if args.state:
            where.append("state = ?")
            params.append(args.state)
        sql = "SELECT * FROM tasks"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY priority ASC, created_at ASC"
        rows = connection.execute(sql, params).fetchall()
    return {"tasks": [row_to_dict(row) for row in rows], "count": len(rows)}


def show_task(args: argparse.Namespace) -> dict[str, Any]:
    with open_db(args.db) as connection:
        row = connection.execute("SELECT * FROM tasks WHERE task_id = ?", (args.task_id,)).fetchone()
        if row is None:
            raise SystemExit(f"unknown task: {args.task_id}")
        events = connection.execute(
            "SELECT * FROM events WHERE task_id = ? ORDER BY timestamp ASC",
            (args.task_id,),
        ).fetchall()
    task = row_to_dict(row)
    task["events"] = [
        {
            "event_id": item["event_id"],
            "task_id": item["task_id"],
            "timestamp": item["timestamp"],
            "event_type": item["event_type"],
            "actor": item["actor"],
            "summary": item["summary"],
            "data": json.loads(item["data_json"]),
        }
        for item in events
    ]
    return task


def export_task_packet(args: argparse.Namespace) -> dict[str, Any]:
    with open_db(args.db) as connection:
        row = connection.execute("SELECT * FROM tasks WHERE task_id = ?", (args.task_id,)).fetchone()
        if row is None:
            raise SystemExit(f"unknown task: {args.task_id}")
    task = row_to_dict(row)
    metadata = task["metadata"]
    result_file = f"Results/agent_packets/{task['task_id']}.yaml"
    return {
        "task_id": task["task_id"],
        "task_class": task_class_for(metadata),
        "role": task["role"],
        "objective": task["objective"],
        "project_goal": metadata_string(metadata, "project_goal", metadata_string(metadata, "parent_goal", "")),
        "phase_objective": metadata_string(metadata, "phase_objective", metadata_string(metadata, "parent_goal", "")),
        "canonical_task_goal": metadata_string(metadata, "canonical_task_goal", task["objective"]),
        "conversation_objective": metadata_string(metadata, "conversation_objective", task["objective"]),
        "subagent_objective": metadata_string(metadata, "subagent_objective", ""),
        "accountable_owner": metadata_string(metadata, "accountable_owner", task["role"]),
        "supporting_departments": metadata_list(metadata, "supporting_departments"),
        "read_scope": task["read_scope"],
        "write_scope": task["write_scope"],
        "acceptance": task["acceptance"],
        "definition_of_done": metadata_string(metadata, "definition_of_done", task["acceptance"]),
        "non_goals": metadata_list(metadata, "non_goals"),
        "required_evidence": metadata_list(metadata, "required_evidence"),
        "stop_condition": task["stop_condition"],
        "appetite": metadata_string(metadata, "appetite", "bounded to declared task scope"),
        "circuit_breaker": metadata_string(metadata, "circuit_breaker", task["stop_condition"]),
        "checkpoint_plan": metadata_string(metadata, "checkpoint_plan", "checkpoint on blocker, scope change, or completion"),
        "escalation_conditions": metadata_list(metadata, "escalation_conditions"),
        "review_gates": metadata_list(metadata, "review_gates"),
        "risk_level": metadata_string(metadata, "risk_level", "medium"),
        "dependencies": task["dependencies"],
        "allowed_actions": metadata_list(metadata, "allowed_actions"),
        "forbidden_actions": metadata_list(metadata, "forbidden_actions"),
        "required_checks": metadata_list(metadata, "required_checks"),
        "assumptions": metadata_list(metadata, "assumptions"),
        "open_questions": metadata_list(metadata, "open_questions"),
        "worktree_path": metadata_string(metadata, "worktree_path", ""),
        "branch_or_base": metadata_string(metadata, "branch_or_base", ""),
        "merge_owner": metadata_string(metadata, "merge_owner", ""),
        "close_condition": metadata_string(metadata, "close_condition", ""),
        "review_owner": metadata_string(metadata, "review_owner", ""),
        "human_review_points": metadata_list(metadata, "human_review_points"),
        "git_status": metadata_string(metadata, "git_status", ""),
        "metadata": task["metadata"],
        "result_file": result_file,
    }


def export_result_packet(args: argparse.Namespace) -> dict[str, Any]:
    task = show_task(args)
    metadata = task["metadata"]
    summary = task["events"][-1]["summary"] if task["events"] else task["objective"]
    return {
        "task_id": task["task_id"],
        "status": task["state"],
        "canonical_status": canonical_state(task["state"]),
        "task_class": task_class_for(metadata),
        "summary": summary,
        "project_goal": metadata_string(metadata, "project_goal", metadata_string(metadata, "parent_goal", "")),
        "phase_objective": metadata_string(metadata, "phase_objective", metadata_string(metadata, "parent_goal", "")),
        "canonical_task_goal": metadata_string(metadata, "canonical_task_goal", task["objective"]),
        "conversation_objective": metadata_string(metadata, "conversation_objective", task["objective"]),
        "owner": task["owner"],
        "role": task["role"],
        "read_scope": task["read_scope"],
        "write_scope": task["write_scope"],
        "files_changed": metadata_list(metadata, "files_changed"),
        "commands_run": metadata_list(metadata, "commands_run"),
        "evidence": metadata_list(metadata, "evidence"),
        "risks": metadata_list(metadata, "risks"),
        "blockers": metadata_list(metadata, "blockers"),
        "review_status": metadata_string(metadata, "review_status", "pending" if task["state"] == "done_with_concerns" else "not_required"),
        "acceptance_state": metadata_string(metadata, "acceptance_state", "met" if task["state"] == "done" else "unknown"),
        "checkpoint": metadata_string(metadata, "checkpoint", summary),
        "continue_or_stop": metadata_string(metadata, "continue_or_stop", "stop" if task["state"] in TERMINAL_STATES else "continue"),
        "escalation": metadata_string(metadata, "escalation", ""),
        "residual_risk": metadata_list(metadata, "residual_risk"),
        "known_exclusions": metadata_list(metadata, "known_exclusions"),
        "next_recommended_action": metadata_string(metadata, "next_recommended_action", metadata_string(metadata, "next_action", "review result packet")),
        "worktree_path": metadata_string(metadata, "worktree_path", ""),
        "branch_or_base": metadata_string(metadata, "branch_or_base", ""),
        "merge_owner": metadata_string(metadata, "merge_owner", ""),
        "close_condition": metadata_string(metadata, "close_condition", ""),
        "git_status": metadata_string(metadata, "git_status", ""),
        "review_owner": metadata_string(metadata, "review_owner", ""),
        "events": task["events"],
    }


def edge_row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    result = dict(row)
    result["metadata"] = json.loads(result.pop("metadata_json"))
    return result


def link_conversation(args: argparse.Namespace) -> dict[str, Any]:
    metadata = parse_json_object(args.metadata, field="metadata")
    timestamp = now_iso()
    with open_db(args.db) as connection:
        task = connection.execute("SELECT * FROM tasks WHERE task_id = ?", (args.parent_task_id,)).fetchone()
        if task is None:
            raise SystemExit(f"unknown parent task: {args.parent_task_id}")
        edge_id = args.edge_id or f"edge_{uuid4().hex}"
        connection.execute(
            """
            INSERT INTO conversation_edges(
                edge_id, parent_task_id, department, thread_id, thread_name,
                conversation_role, status, created_at, updated_at, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?, ?)
            ON CONFLICT(parent_task_id, thread_id) DO UPDATE SET
                department = excluded.department,
                thread_name = excluded.thread_name,
                conversation_role = excluded.conversation_role,
                status = 'open',
                updated_at = excluded.updated_at,
                metadata_json = excluded.metadata_json
            """,
            (
                edge_id,
                args.parent_task_id,
                args.department,
                args.thread_id,
                args.thread_name,
                args.conversation_role,
                timestamp,
                timestamp,
                json.dumps(metadata, ensure_ascii=False, sort_keys=True),
            ),
        )
        record_event(
            connection,
            task_id=args.parent_task_id,
            event_type="conversation_linked",
            actor=args.actor,
            summary=f"linked {args.department} conversation {args.thread_id}",
            data={
                "edge_id": edge_id,
                "department": args.department,
                "thread_id": args.thread_id,
                "thread_name": args.thread_name,
                "conversation_role": args.conversation_role,
                "metadata": metadata,
            },
            events_path=args.events,
        )
        connection.commit()
        row = connection.execute(
            "SELECT * FROM conversation_edges WHERE parent_task_id = ? AND thread_id = ?",
            (args.parent_task_id, args.thread_id),
        ).fetchone()
    return edge_row_to_dict(row)


def close_conversation(args: argparse.Namespace) -> dict[str, Any]:
    metadata = parse_json_object(args.metadata, field="metadata")
    with open_db(args.db) as connection:
        if args.edge_id:
            row = connection.execute("SELECT * FROM conversation_edges WHERE edge_id = ?", (args.edge_id,)).fetchone()
        else:
            row = connection.execute(
                "SELECT * FROM conversation_edges WHERE parent_task_id = ? AND thread_id = ?",
                (args.parent_task_id, args.thread_id),
            ).fetchone()
        if row is None:
            raise SystemExit("conversation edge not found")
        edge = edge_row_to_dict(row)
        if edge["status"] == "closed":
            return edge
        timestamp = now_iso()
        current_metadata = dict(edge["metadata"])
        current_metadata.update(metadata)
        if args.summary:
            current_metadata["close_summary"] = args.summary
        connection.execute(
            """
            UPDATE conversation_edges
            SET status = 'closed', updated_at = ?, metadata_json = ?
            WHERE edge_id = ?
            """,
            (timestamp, json.dumps(current_metadata, ensure_ascii=False, sort_keys=True), edge["edge_id"]),
        )
        record_event(
            connection,
            task_id=edge["parent_task_id"],
            event_type="conversation_closed",
            actor=args.actor,
            summary=args.summary or f"closed conversation {edge['thread_id']}",
            data={
                "edge_id": edge["edge_id"],
                "department": edge["department"],
                "thread_id": edge["thread_id"],
                "metadata": current_metadata,
            },
            events_path=args.events,
        )
        connection.commit()
        row = connection.execute("SELECT * FROM conversation_edges WHERE edge_id = ?", (edge["edge_id"],)).fetchone()
    return edge_row_to_dict(row)


def conversation_graph(args: argparse.Namespace) -> dict[str, Any]:
    with open_db(args.db) as connection:
        params: list[Any] = []
        where = []
        if args.parent_task_id:
            where.append("parent_task_id = ?")
            params.append(args.parent_task_id)
        if args.department:
            where.append("department = ?")
            params.append(args.department)
        if args.status:
            where.append("status = ?")
            params.append(args.status)
        sql = "SELECT * FROM conversation_edges"
        if where:
            sql += " WHERE " + " AND ".join(where)
        sql += " ORDER BY parent_task_id ASC, created_at ASC, thread_id ASC"
        rows = connection.execute(sql, params).fetchall()
        task_rows = {
            row["task_id"]: row_to_dict(row)
            for row in connection.execute("SELECT * FROM tasks").fetchall()
        }
    edges = [edge_row_to_dict(row) for row in rows]
    if args.include_tasks:
        tasks = {
            task_id: {
                "task_id": task["task_id"],
                "objective": task["objective"],
                "state": task["state"],
                "role": task["role"],
                "owner": task["owner"],
            }
            for task_id, task in task_rows.items()
            if any(edge["parent_task_id"] == task_id for edge in edges)
        }
    else:
        tasks = {}
    return {"count": len(edges), "edges": edges, "tasks": tasks}


def status_board(args: argparse.Namespace) -> dict[str, Any]:
    listing = list_tasks(args)
    board = []
    for task in listing["tasks"]:
        if getattr(args, "active_only", False) and task["state"] in TERMINAL_STATES:
            continue
        metadata = task.get("metadata", {})
        board.append(
            {
                "task_id": task["task_id"],
                "state": task["state"],
                "role": task["role"],
                "owner": task["owner"],
                "priority": task["priority"],
                "read_scope": task["read_scope"],
                "write_scope": task["write_scope"],
                "last_event_at": task["last_event_at"],
                "department": metadata.get("department", ""),
                "parent_goal": metadata.get("parent_goal", ""),
                "owner_conversation": metadata.get("owner_conversation", ""),
                "task_conversation": metadata.get("task_conversation", ""),
                "next_action": metadata.get("next_action", ""),
                "human_needed": metadata.get("human_needed", ""),
                "review_status": metadata.get("review_status", ""),
                "git_status": metadata.get("git_status", ""),
            }
        )
    return {"count": len(board), "tasks": board}


def audit_event_stream(args: argparse.Namespace) -> dict[str, Any]:
    with open_db(args.db) as connection:
        task_rows = connection.execute("SELECT * FROM tasks ORDER BY task_id ASC").fetchall()
        event_rows = connection.execute("SELECT * FROM events ORDER BY timestamp ASC").fetchall()
    tasks = {row["task_id"]: row_to_dict(row) for row in task_rows}
    db_events = [
        {
            "event_id": row["event_id"],
            "task_id": row["task_id"],
            "timestamp": row["timestamp"],
            "event_type": row["event_type"],
            "actor": row["actor"],
            "summary": row["summary"],
            "data": json.loads(row["data_json"]),
        }
        for row in event_rows
    ]
    jsonl_events = load_event_log(args.events)
    findings: list[dict[str, Any]] = []
    invalid_jsonl = [event for event in jsonl_events if event.get("_invalid")]
    for event in invalid_jsonl[:20]:
        findings.append({"severity": "fail", "reason": "invalid_jsonl_event", "line": event.get("line"), "error": event.get("error")})

    db_event_ids = {event["event_id"] for event in db_events}
    jsonl_event_ids = {event.get("event_id") for event in jsonl_events if not event.get("_invalid") and event.get("event_id")}
    missing_in_jsonl = sorted(db_event_ids - jsonl_event_ids)
    missing_in_db = sorted(jsonl_event_ids - db_event_ids)
    if missing_in_jsonl:
        findings.append({"severity": "warning", "reason": "events_missing_in_jsonl", "count": len(missing_in_jsonl), "event_ids": missing_in_jsonl[:20]})
    if missing_in_db:
        findings.append({"severity": "warning", "reason": "events_missing_in_db", "count": len(missing_in_db), "event_ids": missing_in_db[:20]})

    sensitive_db_events = [
        event["event_id"]
        for event in db_events
        if contains_sensitive_key(event.get("data", {}))
    ]
    sensitive_jsonl_events = [
        str(event.get("event_id") or f"line:{event.get('_line')}")
        for event in jsonl_events
        if not event.get("_invalid") and contains_sensitive_key(event.get("data", {}))
    ]
    if sensitive_db_events:
        findings.append(
            {
                "severity": "fail",
                "reason": "sensitive_event_data_in_db",
                "count": len(sensitive_db_events),
                "event_ids": sensitive_db_events[:20],
            }
        )
    if sensitive_jsonl_events:
        findings.append(
            {
                "severity": "fail",
                "reason": "sensitive_event_data_in_jsonl",
                "count": len(sensitive_jsonl_events),
                "event_ids": sensitive_jsonl_events[:20],
            }
        )

    unknown_task_events = sorted({event["task_id"] for event in db_events if event["task_id"] not in tasks})
    if unknown_task_events:
        findings.append({"severity": "fail", "reason": "db_events_reference_unknown_task", "task_ids": unknown_task_events[:20]})

    events_by_task: dict[str, list[dict[str, Any]]] = {task_id: [] for task_id in tasks}
    for event in db_events:
        events_by_task.setdefault(event["task_id"], []).append(event)
    for task_id, task in tasks.items():
        task_events = events_by_task.get(task_id, [])
        if not task_events:
            findings.append({"severity": "fail", "reason": "task_has_no_events", "task_id": task_id})
            continue
        created_count = sum(1 for event in task_events if event["event_type"] == "task_created")
        if created_count != 1:
            findings.append({"severity": "warning", "reason": "task_created_event_count_not_one", "task_id": task_id, "count": created_count})
        latest_timestamp = max(event["timestamp"] for event in task_events)
        if task["last_event_at"] != latest_timestamp:
            findings.append(
                {
                    "severity": "warning",
                    "reason": "last_event_at_mismatch",
                    "task_id": task_id,
                    "task_last_event_at": task["last_event_at"],
                    "latest_event_at": latest_timestamp,
                }
            )
    fail_count = sum(1 for item in findings if item["severity"] == "fail")
    warning_count = sum(1 for item in findings if item["severity"] == "warning")
    return {
        "ok": fail_count == 0,
        "task_count": len(tasks),
        "db_event_count": len(db_events),
        "jsonl_event_count": len([event for event in jsonl_events if not event.get("_invalid")]),
        "invalid_jsonl_count": len(invalid_jsonl),
        "missing_in_jsonl_count": len(missing_in_jsonl),
        "missing_in_db_count": len(missing_in_db),
        "sensitive_db_event_count": len(sensitive_db_events),
        "sensitive_jsonl_event_count": len(sensitive_jsonl_events),
        "warning_count": warning_count,
        "fail_count": fail_count,
        "findings": findings,
    }


def scrub_sensitive_events(args: argparse.Namespace) -> dict[str, Any]:
    db = args.db if args.db.is_absolute() else ROOT / args.db
    events_path = args.events if args.events.is_absolute() else ROOT / args.events
    if not (db.resolve() == ROOT.resolve() or ROOT.resolve() in db.resolve().parents):
        raise SystemExit(f"db path is outside MoSim: {args.db}")
    if not (events_path.resolve() == ROOT.resolve() or ROOT.resolve() in events_path.resolve().parents):
        raise SystemExit(f"events path is outside MoSim: {args.events}")

    db_scrubbed: list[str] = []
    with open_db(db) as connection:
        rows = connection.execute("SELECT event_id, data_json FROM events ORDER BY timestamp ASC").fetchall()
        for row in rows:
            try:
                data = json.loads(row["data_json"])
            except json.JSONDecodeError:
                continue
            if contains_sensitive_key(data):
                cleaned = redact_event_data(data)
                db_scrubbed.append(row["event_id"])
                if not args.dry_run:
                    connection.execute(
                        "UPDATE events SET data_json = ? WHERE event_id = ?",
                        (json.dumps(cleaned, ensure_ascii=False, sort_keys=True), row["event_id"]),
                    )
        if not args.dry_run:
            connection.commit()

    jsonl_scrubbed: list[str] = []
    if events_path.exists():
        original_lines = events_path.read_text(encoding="utf-8").splitlines()
        new_lines: list[str] = []
        for line_number, line in enumerate(original_lines, start=1):
            stripped = line.strip()
            if not stripped:
                new_lines.append(line)
                continue
            try:
                event = json.loads(stripped)
            except json.JSONDecodeError:
                new_lines.append(line)
                continue
            if isinstance(event, dict) and contains_sensitive_key(event.get("data", {})):
                event["data"] = redact_event_data(event.get("data", {}))
                jsonl_scrubbed.append(str(event.get("event_id") or f"line:{line_number}"))
                new_lines.append(json.dumps(event, ensure_ascii=False, sort_keys=True))
            else:
                new_lines.append(line)
        if jsonl_scrubbed and not args.dry_run:
            events_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "dry_run": bool(args.dry_run),
        "db_scrubbed_count": len(db_scrubbed),
        "jsonl_scrubbed_count": len(jsonl_scrubbed),
        "db_event_ids": db_scrubbed[:20],
        "jsonl_event_ids": jsonl_scrubbed[:20],
    }


def format_task_packet_text(args: argparse.Namespace) -> dict[str, Any]:
    packet = export_task_packet(args)
    result_template = [
        "[MoSim Result Packet]",
        f"task_id: {packet['task_id']}",
        "status: completed",
        "canonical_status: completed",
        f"task_class: {packet['task_class']}",
        f"canonical_task_goal: {packet['canonical_task_goal']}",
        f"conversation_objective: {packet['conversation_objective']}",
        "summary: one-line outcome summary",
        f"owner: {packet['accountable_owner']}",
        f"role: {packet['role']}",
        f"read_scope: {json.dumps(packet['read_scope'], ensure_ascii=False)}",
        f"write_scope: {json.dumps(packet['write_scope'], ensure_ascii=False)}",
        "files_changed: []",
        "commands_run: []",
        "evidence: []",
        "risks: []",
        "blockers: []",
        "review_status: accepted",
        f"review_owner: {packet['review_owner']}",
        f"worktree_path: {packet['worktree_path']}",
        f"branch_or_base: {packet['branch_or_base']}",
        f"merge_owner: {packet['merge_owner']}",
        f"close_condition: {packet['close_condition']}",
        "git_status: not_checked",
        "continue_or_stop: stop",
        "next_recommended_action: none",
        "events: []",
    ]
    lines = [
        "[MoSim Task Packet]",
        f"task_id: {packet['task_id']}",
        f"task_class: {packet['task_class']}",
        f"role: {packet['role']}",
        f"objective: {packet['objective']}",
        f"project_goal: {packet['project_goal']}",
        f"phase_objective: {packet['phase_objective']}",
        f"canonical_task_goal: {packet['canonical_task_goal']}",
        f"conversation_objective: {packet['conversation_objective']}",
        f"accountable_owner: {packet['accountable_owner']}",
        f"supporting_departments: {json.dumps(packet['supporting_departments'], ensure_ascii=False)}",
        f"read_scope: {json.dumps(packet['read_scope'], ensure_ascii=False)}",
        f"write_scope: {json.dumps(packet['write_scope'], ensure_ascii=False)}",
        f"acceptance: {packet['acceptance']}",
        f"definition_of_done: {packet['definition_of_done']}",
        f"non_goals: {json.dumps(packet['non_goals'], ensure_ascii=False)}",
        f"required_evidence: {json.dumps(packet['required_evidence'], ensure_ascii=False)}",
        f"stop_condition: {packet['stop_condition']}",
        f"appetite: {packet['appetite']}",
        f"circuit_breaker: {packet['circuit_breaker']}",
        f"checkpoint_plan: {packet['checkpoint_plan']}",
        f"escalation_conditions: {json.dumps(packet['escalation_conditions'], ensure_ascii=False)}",
        f"review_gates: {json.dumps(packet['review_gates'], ensure_ascii=False)}",
        f"dependencies: {json.dumps(packet['dependencies'], ensure_ascii=False)}",
        f"allowed_actions: {json.dumps(packet['allowed_actions'], ensure_ascii=False)}",
        f"forbidden_actions: {json.dumps(packet['forbidden_actions'], ensure_ascii=False)}",
        f"required_checks: {json.dumps(packet['required_checks'], ensure_ascii=False)}",
        f"assumptions: {json.dumps(packet['assumptions'], ensure_ascii=False)}",
        f"open_questions: {json.dumps(packet['open_questions'], ensure_ascii=False)}",
        f"worktree_path: {packet['worktree_path']}",
        f"branch_or_base: {packet['branch_or_base']}",
        f"merge_owner: {packet['merge_owner']}",
        f"close_condition: {packet['close_condition']}",
        f"review_owner: {packet['review_owner']}",
        f"human_review_points: {json.dumps(packet['human_review_points'], ensure_ascii=False)}",
        f"git_status: {packet['git_status']}",
        f"metadata: {json.dumps(packet['metadata'], ensure_ascii=False, sort_keys=True)}",
        f"result_file: {packet['result_file']}",
        "",
        "[Required Result Packet Format]",
        "Write exactly this flat key-value packet shape to result_file. Do not return nested YAML as the only result packet; nested details must be summarized into JSON arrays on evidence, risks, blockers, commands_run, files_changed, or events.",
        *result_template,
    ]
    return {"task_id": packet["task_id"], "text": "\n".join(lines)}


def format_result_packet_text(args: argparse.Namespace) -> dict[str, Any]:
    packet = export_result_packet(args)
    lines = [
        "[MoSim Result Packet]",
        f"task_id: {packet['task_id']}",
        f"status: {packet['status']}",
        f"canonical_status: {packet['canonical_status']}",
        f"task_class: {packet['task_class']}",
        f"project_goal: {packet['project_goal']}",
        f"phase_objective: {packet['phase_objective']}",
        f"canonical_task_goal: {packet['canonical_task_goal']}",
        f"conversation_objective: {packet['conversation_objective']}",
        f"summary: {packet['summary']}",
        f"owner: {packet['owner']}",
        f"role: {packet['role']}",
        f"read_scope: {json.dumps(packet['read_scope'], ensure_ascii=False)}",
        f"write_scope: {json.dumps(packet['write_scope'], ensure_ascii=False)}",
        f"files_changed: {json.dumps(packet['files_changed'], ensure_ascii=False)}",
        f"commands_run: {json.dumps(packet['commands_run'], ensure_ascii=False)}",
        f"evidence: {json.dumps(packet['evidence'], ensure_ascii=False)}",
        f"risks: {json.dumps(packet['risks'], ensure_ascii=False)}",
        f"blockers: {json.dumps(packet['blockers'], ensure_ascii=False)}",
        f"review_status: {packet['review_status']}",
        f"acceptance_state: {packet['acceptance_state']}",
        f"review_owner: {packet['review_owner']}",
        f"worktree_path: {packet['worktree_path']}",
        f"branch_or_base: {packet['branch_or_base']}",
        f"merge_owner: {packet['merge_owner']}",
        f"close_condition: {packet['close_condition']}",
        f"git_status: {packet['git_status']}",
        f"continue_or_stop: {packet['continue_or_stop']}",
        f"next_recommended_action: {packet['next_recommended_action']}",
        f"events: {json.dumps(packet['events'], ensure_ascii=False)}",
    ]
    return {"task_id": packet["task_id"], "text": "\n".join(lines)}


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create")
    add_common(create)
    create.add_argument("--task-id", default="")
    create.add_argument("--objective", required=True)
    create.add_argument("--role", required=True)
    create.add_argument("--read-scope", action="append", default=[])
    create.add_argument("--write-scope", action="append", default=[])
    create.add_argument("--acceptance", required=True)
    create.add_argument("--stop-condition", required=True)
    create.add_argument("--depends-on", action="append", default=[])
    create.add_argument("--metadata", default="")
    create.add_argument("--priority", type=int, default=100)
    create.add_argument("--actor", default="MainAgent")
    create.set_defaults(func=create_task)

    claim = subparsers.add_parser("claim")
    add_common(claim)
    claim.add_argument("--task-id", default="")
    claim.add_argument("--owner", required=True)
    claim.add_argument("--force", action="store_true", help="explicitly reclaim a claimed/running task")
    claim.add_argument("--show-claim-token", action="store_true", help="print the claim token in CLI output for immediate manual capture")
    claim.set_defaults(func=claim_task)

    heartbeat = subparsers.add_parser("heartbeat")
    add_common(heartbeat)
    heartbeat.add_argument("--task-id", required=True)
    heartbeat.add_argument("--actor", required=True)
    heartbeat.add_argument("--claim-token", default="")
    heartbeat.add_argument("--summary", default="heartbeat")
    heartbeat.add_argument("--data", default="")
    heartbeat.set_defaults(func=lambda args: update_task(args, state="running", event_type="heartbeat"))

    checkpoint = subparsers.add_parser("checkpoint")
    add_common(checkpoint)
    checkpoint.add_argument("--task-id", required=True)
    checkpoint.add_argument("--actor", required=True)
    checkpoint.add_argument("--claim-token", default="")
    checkpoint.add_argument("--summary", required=True)
    checkpoint.add_argument("--data", default="")
    checkpoint.set_defaults(func=lambda args: update_task(args, state="running", event_type="checkpoint"))

    metadata = subparsers.add_parser("update-metadata")
    add_common(metadata)
    metadata.add_argument("--task-id", required=True)
    metadata.add_argument("--actor", required=True)
    metadata.add_argument("--claim-token", default="")
    metadata.add_argument("--summary", required=True)
    metadata.add_argument("--metadata", required=True)
    metadata.set_defaults(func=update_metadata)

    complete = subparsers.add_parser("complete")
    add_common(complete)
    complete.add_argument("--task-id", required=True)
    complete.add_argument("--actor", required=True)
    complete.add_argument("--claim-token", default="")
    complete.add_argument("--summary", required=True)
    complete.add_argument("--data", default="")
    complete.set_defaults(func=lambda args: update_task(args, state="done", event_type="task_completed"))

    block = subparsers.add_parser("block")
    add_common(block)
    block.add_argument("--task-id", required=True)
    block.add_argument("--actor", required=True)
    block.add_argument("--claim-token", default="")
    block.add_argument("--summary", required=True)
    block.add_argument("--data", default="")
    block.set_defaults(func=lambda args: update_task(args, state="blocked", event_type="task_blocked"))

    fail = subparsers.add_parser("fail")
    add_common(fail)
    fail.add_argument("--task-id", required=True)
    fail.add_argument("--actor", required=True)
    fail.add_argument("--claim-token", default="")
    fail.add_argument("--summary", required=True)
    fail.add_argument("--data", default="")
    fail.set_defaults(func=lambda args: update_task(args, state="failed", event_type="task_failed"))

    cancel = subparsers.add_parser("cancel")
    add_common(cancel)
    cancel.add_argument("--task-id", required=True)
    cancel.add_argument("--actor", required=True)
    cancel.add_argument("--claim-token", default="")
    cancel.add_argument("--summary", required=True)
    cancel.add_argument("--data", default="")
    cancel.set_defaults(func=lambda args: update_task(args, state="cancelled", event_type="task_cancelled"))

    list_parser = subparsers.add_parser("list")
    add_common(list_parser)
    list_parser.add_argument("--state", choices=sorted(VALID_STATES), default="")
    list_parser.set_defaults(func=list_tasks)

    show = subparsers.add_parser("show")
    add_common(show)
    show.add_argument("--task-id", required=True)
    show.set_defaults(func=show_task)

    packet = subparsers.add_parser("task-packet")
    add_common(packet)
    packet.add_argument("--task-id", required=True)
    packet.set_defaults(func=export_task_packet)

    result = subparsers.add_parser("result-packet")
    add_common(result)
    result.add_argument("--task-id", required=True)
    result.set_defaults(func=export_result_packet)

    board = subparsers.add_parser("status-board")
    add_common(board)
    board.add_argument("--state", choices=sorted(VALID_STATES), default="")
    board.add_argument("--active-only", action="store_true")
    board.set_defaults(func=status_board)

    audit = subparsers.add_parser("audit-events")
    add_common(audit)
    audit.set_defaults(func=audit_event_stream)

    scrub = subparsers.add_parser("scrub-sensitive-events")
    add_common(scrub)
    scrub.add_argument("--dry-run", action="store_true")
    scrub.set_defaults(func=scrub_sensitive_events)

    packet_text = subparsers.add_parser("task-packet-text")
    add_common(packet_text)
    packet_text.add_argument("--task-id", required=True)
    packet_text.set_defaults(func=format_task_packet_text)

    result_text = subparsers.add_parser("result-packet-text")
    add_common(result_text)
    result_text.add_argument("--task-id", required=True)
    result_text.set_defaults(func=format_result_packet_text)

    link = subparsers.add_parser("link-conversation")
    add_common(link)
    link.add_argument("--edge-id", default="")
    link.add_argument("--parent-task-id", required=True)
    link.add_argument("--department", required=True)
    link.add_argument("--thread-id", required=True)
    link.add_argument("--thread-name", default="")
    link.add_argument("--conversation-role", default="")
    link.add_argument("--metadata", default="")
    link.add_argument("--actor", default="MainAgent")
    link.set_defaults(func=link_conversation)

    close_edge = subparsers.add_parser("close-conversation")
    add_common(close_edge)
    close_edge.add_argument("--edge-id", default="")
    close_edge.add_argument("--parent-task-id", default="")
    close_edge.add_argument("--thread-id", default="")
    close_edge.add_argument("--summary", default="")
    close_edge.add_argument("--metadata", default="")
    close_edge.add_argument("--actor", default="MainAgent")
    close_edge.set_defaults(func=close_conversation)

    graph = subparsers.add_parser("conversation-graph")
    add_common(graph)
    graph.add_argument("--parent-task-id", default="")
    graph.add_argument("--department", default="")
    graph.add_argument("--status", choices=sorted(VALID_EDGE_STATUSES), default="")
    graph.add_argument("--include-tasks", action="store_true")
    graph.set_defaults(func=conversation_graph)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = args.func(args)
    if args.command in {"task-packet-text", "result-packet-text"}:
        print(result["text"])
    else:
        print(json.dumps(redact_for_output(result, reveal_claim_token=getattr(args, "show_claim_token", False)), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
