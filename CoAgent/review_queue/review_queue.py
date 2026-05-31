#!/usr/bin/env python3
"""Read-only human-review queue for CoAgent runtime tasks."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "Results" / "agent_runtime" / "tasks.sqlite3"
REVIEW_ROOT = ROOT / "Results" / "agent_packets" / "reviews"
TERMINAL_STATES = {"done", "done_with_concerns", "blocked", "failed", "cancelled"}
REVIEW_STATUSES_OK = {"", "accepted", "not_required"}
REVIEW_DECISIONS = {"accepted", "accepted_with_concerns", "needs_rework", "rejected"}

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.runtime import mosim_agent_runtime as runtime


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


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
        for key in ["summary_path", "review_path", "notification_packet_path"]:
            if item.get(key):
                print(f"    {key}: {item[key]}")


def closeout_review(args: argparse.Namespace) -> dict[str, Any]:
    if args.decision not in REVIEW_DECISIONS:
        raise SystemExit(f"invalid decision: {args.decision}")
    db = args.db if args.db.is_absolute() else ROOT / args.db
    if not (db.resolve() == ROOT.resolve() or ROOT.resolve() in db.resolve().parents):
        raise SystemExit(f"db path is outside MoSim: {args.db}")
    task = runtime.show_task(argparse.Namespace(db=db, events=args.events, task_id=args.task_id))
    metadata = dict(task.get("metadata", {}))
    patch = {
        "review_status": args.decision,
        "review_decision_by": args.actor,
        "review_decision_reason": args.reason,
        "requires_human_review": args.decision not in {"accepted", "accepted_with_concerns"},
        "human_needed": "" if args.decision in {"accepted", "accepted_with_concerns"} else "yes",
        "next_action": args.next_action,
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
    return {
        "ok": True,
        "task_id": args.task_id,
        "decision": args.decision,
        "human_needed": patch["human_needed"],
        "next_action": args.next_action,
        "runtime_state": updated,
    }


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
    close_parser.add_argument("--actor", default="MainAgent")
    close_parser.add_argument("--claim-token", default="")
    close_parser.add_argument("--json", action="store_true")
    close_parser.set_defaults(func=closeout_review)
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
