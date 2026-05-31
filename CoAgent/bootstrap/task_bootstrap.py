#!/usr/bin/env python3
"""Create and recover dedicated long-running CoAgent task conversations.

This is the project-owned bootstrap layer between a durable runtime task and a
visible department or dedicated task conversation. It does not create Codex App
threads and does not read Codex private state. Transport remains a separate
layer under `CoAgent/dispatch` and `CoAgent/transport`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "Results" / "coagent_bootstrap"
DEFAULT_CONTEXT_ROOT = ROOT / "Results" / "context_packs"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.context import context_pack
from CoAgent.dispatch import codex_transport
from CoAgent.dispatch import dispatch_helper
from CoAgent.dispatch.conversation_registry import THREADS_JSON, get_thread_by_department
from CoAgent.knowledge import knowledge_indexer
from CoAgent.result_router import result_router
from CoAgent.runtime import mosim_agent_runtime as runtime


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


def project_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    if not (resolved == ROOT.resolve() or ROOT.resolve() in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def write_json(path: Path, payload: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return rel(path)


def read_task_or_none(db: Path, events: Path, task_id: str) -> dict[str, Any] | None:
    try:
        return runtime.show_task(argparse.Namespace(db=db, events=events, task_id=task_id))
    except SystemExit:
        return None


def result_summary_path(task_id: str) -> Path:
    return ROOT / "Results" / "agent_packets" / "summaries" / f"{task_id}.summary.md"


def create_or_reuse_task(args: argparse.Namespace, target: dict[str, str]) -> dict[str, Any]:
    existing = read_task_or_none(args.db, args.events, args.task_id)
    if existing is not None:
        if not args.reuse_existing:
            raise SystemExit(f"task already exists: {args.task_id}; pass --reuse-existing to refresh bootstrap artifacts")
        return existing
    metadata = {
        "department": args.department,
        "parent_goal": args.parent_goal,
        "owner_conversation": args.owner_conversation,
        "task_conversation": target["thread_name"],
        "task_conversation_thread_id": target["thread_id"],
        "next_action": "send generated handoff text to the visible task conversation",
        "bootstrap_state": "created",
    }
    if args.metadata:
        try:
            metadata.update(json.loads(args.metadata))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"metadata must be valid JSON object: {exc}") from exc
    role = args.role or args.department
    runtime.create_task(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            task_id=args.task_id,
            objective=args.objective,
            role=role,
            read_scope=args.read_scope,
            write_scope=args.write_scope,
            acceptance=args.acceptance,
            stop_condition=args.stop_condition,
            depends_on=args.depends_on,
            metadata=json.dumps(metadata, ensure_ascii=False, sort_keys=True),
            priority=args.priority,
            actor=args.actor,
        )
    )
    return runtime.show_task(argparse.Namespace(db=args.db, events=args.events, task_id=args.task_id))


def build_artifact_paths(task_id: str, output_root: Path, context_root: Path) -> dict[str, Path]:
    output_root = project_path(output_root)
    context_root = project_path(context_root)
    return {
        "context": context_root / f"{task_id}.context.md",
        "dispatch": output_root / f"{task_id}.dispatch.txt",
        "handoff": output_root / f"{task_id}.handoff.txt",
        "bootstrap": output_root / f"{task_id}.bootstrap.json",
        "recovery": output_root / f"{task_id}.recovery.json",
        "transport_plan": output_root / f"{task_id}.transport-plan.json",
    }


def write_handoff(context_text: str, dispatch_text: str, context_path: Path, dispatch_path: Path, handoff_path: Path) -> str:
    lines = [
        "[MoSim Task Handoff]",
        f"context_pack: {rel(context_path)}",
        f"dispatch_packet: {rel(dispatch_path)}",
        "",
        "## Context Pack",
        context_text.rstrip(),
        "",
        "## Dispatch Packet",
        dispatch_text.rstrip(),
        "",
    ]
    handoff_path.parent.mkdir(parents=True, exist_ok=True)
    handoff_path.write_text("\n".join(lines), encoding="utf-8")
    return rel(handoff_path)


def bootstrap_task(args: argparse.Namespace) -> dict[str, Any]:
    target = get_thread_by_department(args.department, args.registry)
    task = create_or_reuse_task(args, target)
    paths = build_artifact_paths(args.task_id, args.output_root, args.context_root)
    context = context_pack.build_context_pack(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            task_id=args.task_id,
            output=paths["context"],
            event_limit=args.event_limit,
            knowledge_query=args.knowledge_query,
            decision=args.decision,
            blocker=args.blocker,
            include_memory_context=args.include_memory_context,
            memory_policy=args.memory_policy,
            memory_limit_per_query=args.memory_limit_per_query,
            memory_max_hits=args.memory_max_hits,
            memory_max_chars=args.memory_max_chars,
            warn_chars=args.warn_chars,
            fail_chars=args.fail_chars,
        )
    )
    dispatch = dispatch_helper.build_department_task_text(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            registry=args.registry,
            department=args.department,
            task_id=args.task_id,
        )
    )
    paths["dispatch"].parent.mkdir(parents=True, exist_ok=True)
    paths["dispatch"].write_text(dispatch["text"].rstrip() + "\n", encoding="utf-8")
    handoff_rel = write_handoff(context["text"], dispatch["text"], paths["context"], paths["dispatch"], paths["handoff"])
    packet = runtime.export_task_packet(argparse.Namespace(db=args.db, events=args.events, task_id=args.task_id))
    edge = None
    if args.link_edge:
        edge = runtime.link_conversation(
            argparse.Namespace(
                db=args.db,
                events=args.events,
                edge_id=f"dispatch_{args.task_id}_{args.department}",
                parent_task_id=args.task_id,
                department=args.department,
                thread_id=target["thread_id"],
                thread_name=target["thread_name"],
                conversation_role="dedicated_task_bootstrap",
                metadata=json.dumps(
                    {
                        "bootstrap_state": "handoff_ready",
                        "context_pack": context["output"],
                        "dispatch_packet": rel(paths["dispatch"]),
                        "handoff": handoff_rel,
                        "result_file": packet["result_file"],
                        "surface": target["surface"],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                actor=args.actor,
            )
        )
    payload = {
        "ok": True,
        "task_id": args.task_id,
        "department": args.department,
        "thread_id": target["thread_id"],
        "thread_name": target["thread_name"],
        "task_state": task["state"],
        "context_pack": context["output"],
        "context_metrics": context["metrics"],
        "dispatch_packet": rel(paths["dispatch"]),
        "handoff": handoff_rel,
        "result_file": packet["result_file"],
        "conversation_edge": edge,
        "next_action": "send the handoff file content to the target visible conversation, then run recover-task after it writes the result packet",
    }
    if getattr(args, "include_transport_plan", False):
        transport_plan = codex_transport.dispatch_plan(
            argparse.Namespace(
                db=args.db,
                events=args.events,
                registry=args.registry,
                department=args.department,
                task_id=args.task_id,
                packet_file=paths["handoff"],
            )
        )
        payload["transport_plan"] = transport_plan
        payload["transport_packet"] = transport_plan["packet_path"]
        payload["transport_result"] = transport_plan["result_path"]
        payload["transport_plan_summary"] = write_json(paths["transport_plan"], transport_plan)
        payload["next_action"] = (
            "review transport_plan.command_shell; if approved, run codex_transport.py start-dispatch "
            "with --packet-file set to the generated handoff, then run recover-task after result packet appears"
        )
    payload["bootstrap_summary"] = write_json(paths["bootstrap"], payload)
    return payload


def recover_task(args: argparse.Namespace) -> dict[str, Any]:
    task = runtime.show_task(argparse.Namespace(db=args.db, events=args.events, task_id=args.task_id))
    packet = runtime.export_task_packet(argparse.Namespace(db=args.db, events=args.events, task_id=args.task_id))
    result_file = project_path(Path(packet["result_file"]))
    imported = None
    if args.import_result and result_file.exists() and task["state"] not in runtime.TERMINAL_STATES:
        imported = result_router.import_packet(
            argparse.Namespace(
                db=args.db,
                events=args.events,
                packet=result_file,
                claim_token=args.claim_token or "",
                archive=True,
                archive_invalid=True,
            )
        )
        task = runtime.show_task(argparse.Namespace(db=args.db, events=args.events, task_id=args.task_id))
    summary_path = result_summary_path(args.task_id)
    upserted = []
    if args.knowledge_upsert and summary_path.exists():
        upserted.append(
            knowledge_indexer.upsert_file(
                summary_path,
                source_id="result_packet_summaries",
                category="runtime_evidence",
                priority=7,
            )
        )
    closed_edge = None
    if args.close_edge and task["state"] in runtime.TERMINAL_STATES:
        try:
            closed_edge = runtime.close_conversation(
                argparse.Namespace(
                    db=args.db,
                    events=args.events,
                    edge_id=f"dispatch_{args.task_id}_{args.department}",
                    parent_task_id="",
                    thread_id="",
                    summary=f"bootstrap recovery observed terminal state: {task['state']}",
                    metadata=json.dumps(
                        {
                            "result_file": packet["result_file"],
                            "result_file_exists": result_file.exists(),
                            "runtime_state": task["state"],
                            "summary_path": rel(summary_path) if summary_path.exists() else "",
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    actor=args.actor,
                )
            )
        except SystemExit:
            closed_edge = None
    paths = build_artifact_paths(args.task_id, args.output_root, args.context_root)
    next_action = "task is terminal; review result summary and close any remaining review work"
    if task["state"] not in runtime.TERMINAL_STATES and not result_file.exists():
        next_action = "result packet is missing; send or resend the handoff to the visible task conversation"
    elif task["state"] not in runtime.TERMINAL_STATES:
        next_action = "result packet exists but task is not terminal; inspect router validation output"
    payload = {
        "ok": True,
        "task_id": args.task_id,
        "department": args.department,
        "runtime_state": task["state"],
        "terminal": task["state"] in runtime.TERMINAL_STATES,
        "result_file": packet["result_file"],
        "result_file_exists": result_file.exists(),
        "imported": imported,
        "closed_edge": closed_edge,
        "result_summary": rel(summary_path) if summary_path.exists() else "",
        "knowledge_upserts": upserted,
        "next_action": next_action,
    }
    recovery_rel = write_json(paths["recovery"], payload)
    payload["recovery_summary"] = recovery_rel
    if args.knowledge_upsert:
        upserted.append(
            knowledge_indexer.upsert_file(
                ROOT / recovery_rel,
                source_id="bootstrap_recovery",
                category="runtime_evidence",
                priority=7,
            )
        )
    return payload


def status_task(args: argparse.Namespace) -> dict[str, Any]:
    task = runtime.show_task(argparse.Namespace(db=args.db, events=args.events, task_id=args.task_id))
    packet = runtime.export_task_packet(argparse.Namespace(db=args.db, events=args.events, task_id=args.task_id))
    result_file = project_path(Path(packet["result_file"]))
    graph = runtime.conversation_graph(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            parent_task_id=args.task_id,
            department=args.department or "",
            status="",
            include_tasks=True,
        )
    )
    paths = build_artifact_paths(args.task_id, args.output_root, args.context_root)
    return {
        "task_id": args.task_id,
        "runtime_state": task["state"],
        "terminal": task["state"] in runtime.TERMINAL_STATES,
        "result_file": packet["result_file"],
        "result_file_exists": result_file.exists(),
        "context_pack": rel(paths["context"]) if paths["context"].exists() else "",
        "handoff": rel(paths["handoff"]) if paths["handoff"].exists() else "",
        "bootstrap_summary": rel(paths["bootstrap"]) if paths["bootstrap"].exists() else "",
        "recovery_summary": rel(paths["recovery"]) if paths["recovery"].exists() else "",
        "transport_plan_summary": rel(paths["transport_plan"]) if paths["transport_plan"].exists() else "",
        "conversation_graph": graph,
    }


def add_common(parser: argparse.ArgumentParser) -> None:
    runtime.add_common(parser)
    parser.add_argument("--registry", type=Path, default=THREADS_JSON)
    parser.add_argument("--department", required=True)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--context-root", type=Path, default=DEFAULT_CONTEXT_ROOT)
    parser.add_argument("--actor", default="MainAgent")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap = subparsers.add_parser("bootstrap-task")
    add_common(bootstrap)
    bootstrap.add_argument("--task-id", required=True)
    bootstrap.add_argument("--objective", required=True)
    bootstrap.add_argument("--role", default="")
    bootstrap.add_argument("--read-scope", action="append", default=[])
    bootstrap.add_argument("--write-scope", action="append", default=[])
    bootstrap.add_argument("--acceptance", required=True)
    bootstrap.add_argument("--stop-condition", required=True)
    bootstrap.add_argument("--depends-on", action="append", default=[])
    bootstrap.add_argument("--metadata", default="")
    bootstrap.add_argument("--priority", type=int, default=100)
    bootstrap.add_argument("--parent-goal", default="active_thread_goal")
    bootstrap.add_argument("--owner-conversation", default="MoSim｜主线总控")
    bootstrap.add_argument("--reuse-existing", action="store_true")
    bootstrap.add_argument("--no-link-edge", dest="link_edge", action="store_false")
    bootstrap.add_argument("--event-limit", type=int, default=8)
    bootstrap.add_argument("--knowledge-query", action="append", default=[])
    bootstrap.add_argument("--decision", action="append", default=[])
    bootstrap.add_argument("--blocker", action="append", default=[])
    bootstrap.add_argument("--include-memory-context", action="store_true")
    bootstrap.add_argument("--memory-policy", type=Path, default=None)
    bootstrap.add_argument("--memory-limit-per-query", type=int, default=None)
    bootstrap.add_argument("--memory-max-hits", type=int, default=None)
    bootstrap.add_argument("--memory-max-chars", type=int, default=None)
    bootstrap.add_argument("--warn-chars", type=int, default=context_pack.DEFAULT_WARN_CHARS)
    bootstrap.add_argument("--fail-chars", type=int, default=context_pack.DEFAULT_FAIL_CHARS)
    bootstrap.add_argument("--include-transport-plan", action="store_true")
    bootstrap.set_defaults(func=bootstrap_task, link_edge=True)

    recover = subparsers.add_parser("recover-task")
    add_common(recover)
    recover.add_argument("--task-id", required=True)
    recover.add_argument("--claim-token", default="")
    recover.add_argument("--no-import-result", dest="import_result", action="store_false")
    recover.add_argument("--no-close-edge", dest="close_edge", action="store_false")
    recover.add_argument("--no-knowledge-upsert", dest="knowledge_upsert", action="store_false")
    recover.set_defaults(func=recover_task, import_result=True, close_edge=True, knowledge_upsert=True)

    status = subparsers.add_parser("status-task")
    add_common(status)
    status.add_argument("--task-id", required=True)
    status.set_defaults(func=status_task)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
