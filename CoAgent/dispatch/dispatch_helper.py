#!/usr/bin/env python3
"""CoAgent dispatch helpers for department-thread routing and packet exchange."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.runtime import mosim_agent_runtime as runtime
from CoAgent.dispatch.conversation_registry import THREADS_JSON, get_thread_by_department, load_registry, save_registry
from CoAgent.result_router import result_router


def list_departments(args: argparse.Namespace) -> dict[str, Any]:
    return load_registry(args.registry)


def set_thread(args: argparse.Namespace) -> dict[str, Any]:
    data = load_registry(args.registry)
    found = False
    for item in data["threads"]:
        if item["department"] == args.department:
            item["thread_id"] = args.thread_id
            item["surface"] = args.surface
            item["status"] = args.status
            found = True
            break
    if not found:
        raise SystemExit(f"unknown department: {args.department}")
    save_registry(data, args.registry)
    return data


def build_dispatch_envelope(args: argparse.Namespace) -> dict[str, Any]:
    task = runtime.export_task_packet(args)
    task_text = runtime.format_task_packet_text(args)["text"]
    target = get_thread_by_department(args.department, args.registry)
    return {
        "target_department": args.department,
        "thread_name": target["thread_name"],
        "thread_id": target["thread_id"],
        "surface": target["surface"],
        "status": target["status"],
        "task_packet": task,
        "task_packet_text": task_text,
    }


def build_department_task_text(args: argparse.Namespace) -> dict[str, Any]:
    envelope = build_dispatch_envelope(args)
    lines = [
        "[MoSim Department Dispatch]",
        f"target_department: {envelope['target_department']}",
        f"thread_name: {envelope['thread_name']}",
        f"thread_id: {envelope['thread_id']}",
        f"surface: {envelope['surface']}",
        f"dispatch_status: {envelope['status']}",
        "",
        envelope["task_packet_text"],
        "",
        "[Execution Contract]",
        "1. Stay inside the declared read/write scope.",
        "2. Do not expand scope without returning a blocker.",
        "3. Write one MoSim Result Packet to the declared result_file path.",
        "4. If blocked, report blocker and next recommended action.",
    ]
    return {
        "task_id": envelope["task_packet"]["task_id"],
        "department": envelope["target_department"],
        "text": "\n".join(lines),
    }


def import_result_packet(args: argparse.Namespace) -> dict[str, Any]:
    return result_router.import_packet(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            packet=Path(args.packet),
            claim_token=args.claim_token or "",
            archive=True,
            archive_invalid=True,
        )
    )


def import_result_text(args: argparse.Namespace) -> dict[str, Any]:
    return result_router.import_packet(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            packet=Path(args.packet),
            claim_token=args.claim_token or "",
            archive=True,
            archive_invalid=True,
        )
    )


def build_review_brief(args: argparse.Namespace) -> dict[str, Any]:
    packet = runtime.export_result_packet(args)
    lines = [
        "[MoSim Review Brief]",
        f"task_id: {packet['task_id']}",
        f"status: {packet['status']}",
        f"owner: {packet['owner']}",
        f"role: {packet['role']}",
        f"summary: {packet['summary']}",
        f"read_scope: {json.dumps(packet['read_scope'], ensure_ascii=False)}",
        f"write_scope: {json.dumps(packet['write_scope'], ensure_ascii=False)}",
        "review_checklist:",
        "- verify the task stayed inside scope",
        "- verify evidence is sufficient",
        "- verify next action or blocker is coherent",
        "- return approval or follow-up",
    ]
    return {"task_id": packet["task_id"], "text": "\n".join(lines)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--registry", type=Path, default=THREADS_JSON)
    list_parser.set_defaults(func=list_departments)

    set_parser = subparsers.add_parser("set-thread")
    set_parser.add_argument("--registry", type=Path, default=THREADS_JSON)
    set_parser.add_argument("--department", required=True)
    set_parser.add_argument("--thread-id", required=True)
    set_parser.add_argument("--surface", default="codex_app_or_vscode")
    set_parser.add_argument("--status", default="ready")
    set_parser.set_defaults(func=set_thread)

    dispatch_parser = subparsers.add_parser("dispatch-envelope")
    runtime.add_common(dispatch_parser)
    dispatch_parser.add_argument("--registry", type=Path, default=THREADS_JSON)
    dispatch_parser.add_argument("--department", required=True)
    dispatch_parser.add_argument("--task-id", required=True)
    dispatch_parser.set_defaults(func=build_dispatch_envelope)

    dispatch_text_parser = subparsers.add_parser("department-task-text")
    runtime.add_common(dispatch_text_parser)
    dispatch_text_parser.add_argument("--registry", type=Path, default=THREADS_JSON)
    dispatch_text_parser.add_argument("--department", required=True)
    dispatch_text_parser.add_argument("--task-id", required=True)
    dispatch_text_parser.set_defaults(func=build_department_task_text)

    import_parser = subparsers.add_parser("import-result")
    runtime.add_common(import_parser)
    import_parser.add_argument("--packet", required=True)
    import_parser.add_argument("--claim-token", default="")
    import_parser.set_defaults(func=import_result_packet)

    import_text_parser = subparsers.add_parser("import-result-text")
    runtime.add_common(import_text_parser)
    import_text_parser.add_argument("--packet", required=True)
    import_text_parser.add_argument("--claim-token", default="")
    import_text_parser.set_defaults(func=import_result_text)

    review_parser = subparsers.add_parser("review-brief")
    runtime.add_common(review_parser)
    review_parser.add_argument("--task-id", required=True)
    review_parser.set_defaults(func=build_review_brief)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = args.func(args)
    if args.command in {"department-task-text", "review-brief"}:
        print(result["text"])
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
