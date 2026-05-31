#!/usr/bin/env python3
"""Transport-aware Codex dispatch helpers.

This module deliberately defaults to dry-run command planning.
It does not assume the current environment should directly mutate Codex session
stores or silently resume visible conversations.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
TMP_DIR = ROOT / "Results" / "coagent_transport"
RUNS_DIR = ROOT / "Results" / "coagent_transport" / "runs"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.dispatch.conversation_registry import get_thread_by_department
from CoAgent.dispatch.dispatch_helper import build_department_task_text
from CoAgent.result_router import result_router
from CoAgent.runtime import mosim_agent_runtime as runtime
from CoAgent.transport.adapter import TransportRequest
from CoAgent.transport.codex_exec import CodexExecResumeAdapter


ADAPTER = CodexExecResumeAdapter()


def ensure_tmp() -> None:
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)


def project_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    if not (resolved == ROOT.resolve() or ROOT.resolve() in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel_project_path(path: Path) -> str:
    return str(project_path(path).relative_to(ROOT.resolve())).replace("\\", "/")


def read_packet_text(args: argparse.Namespace) -> str:
    packet_file = getattr(args, "packet_file", None)
    if not packet_file:
        return build_department_task_text(args)["text"]
    packet_path = project_path(Path(packet_file))
    if not packet_path.exists():
        raise SystemExit(f"packet file not found: {packet_file}")
    return packet_path.read_text(encoding="utf-8")


def build_transport_request(args: argparse.Namespace) -> TransportRequest:
    thread = get_thread_by_department(args.department, args.registry)
    if thread.get("status") != "active_visible":
        raise SystemExit(
            f"department {args.department} is not active_visible; current status={thread.get('status', '')}. "
            "Do not resume historical rollout files as department conversations."
        )
    packet_text = read_packet_text(args)
    ensure_tmp()
    packet_path = TMP_DIR / f"{args.task_id}_packet.txt"
    result_path = TMP_DIR / f"{args.task_id}_result.txt"
    return TransportRequest(
        task_id=args.task_id,
        department=args.department,
        thread_id=thread["thread_id"],
        thread_name=thread["thread_name"],
        packet_path=packet_path,
        result_path=result_path,
        packet_text=packet_text,
    )


def dispatch_plan(args: argparse.Namespace) -> dict[str, Any]:
    request = build_transport_request(args)
    plan = ADAPTER.plan(request)
    return {
        "department": args.department,
        "thread_name": request.thread_name,
        "thread_id": request.thread_id,
        "packet_path": plan.packet_path,
        "result_path": plan.result_path,
        "sqlite_home": plan.metadata.get("sqlite_home", ""),
        "codex_home": plan.metadata.get("codex_home", ""),
        "copied_files": plan.metadata.get("copied_files", []),
        "adapter": plan.adapter,
        "adapter_metadata": plan.metadata,
        "command": plan.command,
        "command_shell": plan.command_shell,
        "dry_run": True,
    }


def extract_result_file_rel(args: argparse.Namespace) -> str:
    explicit_result_file = getattr(args, "result_file", None)
    if explicit_result_file:
        return rel_project_path(Path(explicit_result_file))

    packet_file = getattr(args, "packet_file", None)
    text = read_packet_text(args) if packet_file else build_department_task_text(args)["text"]
    for line in text.splitlines():
        if line.startswith("result_file: "):
            return rel_project_path(Path(line.split(": ", 1)[1]))
    if packet_file:
        raise SystemExit("custom packet file must declare result_file or use --result-file")
    raise SystemExit("task packet missing result_file")


def run_meta_path(task_id: str) -> Path:
    return RUNS_DIR / f"{task_id}.json"


def write_run_meta(task_id: str, data: dict[str, Any]) -> None:
    path = run_meta_path(task_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_run_meta(task_id: str) -> dict[str, Any]:
    path = run_meta_path(task_id)
    if not path.exists():
        raise SystemExit(f"unknown dispatch run: {task_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def maybe_import_result(task_id: str, db: Path, events: Path, result_file_rel: str) -> dict[str, Any] | None:
    result_file_path = ROOT / result_file_rel
    if not result_file_path.exists():
        return None
    task = runtime.show_task(argparse.Namespace(db=db, events=events, task_id=task_id))
    if task["state"] in runtime.TERMINAL_STATES:
        return task
    namespace = argparse.Namespace(
        db=db,
        events=events,
        packet=str(result_file_path),
        claim_token="",
        archive=True,
        archive_invalid=True,
    )
    imported = result_router.import_packet(namespace)
    if not imported.get("ok"):
        return imported
    return imported.get("runtime_state", imported)


def summary_path(task_id: str) -> Path:
    return RUNS_DIR / f"{task_id}.summary.md"


def write_run_summary(task_id: str, payload: dict[str, Any]) -> str:
    started = payload.get("started") if isinstance(payload.get("started"), dict) else {}
    poll = payload.get("poll") if isinstance(payload.get("poll"), dict) else {}
    lines = [
        f"# Dispatch Run Summary: {task_id}",
        "",
        f"- task_id: `{task_id}`",
        f"- mode: `{payload.get('mode', '')}`",
        f"- timed_out: `{payload.get('timed_out', False)}`",
        f"- department: `{payload.get('department', started.get('department', ''))}`",
        f"- thread_id: `{payload.get('thread_id', started.get('thread_id', ''))}`",
        f"- result_file: `{payload.get('result_file', poll.get('result_file', ''))}`",
        f"- done: `{payload.get('done', poll.get('done', False))}`",
        "",
        "## Details",
        "",
        "```json",
        json.dumps(payload, ensure_ascii=False, indent=2),
        "```",
    ]
    path = summary_path(task_id)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(path.relative_to(ROOT)).replace("\\", "/")


def dispatch_run(args: argparse.Namespace) -> dict[str, Any]:
    start = start_dispatch(args)
    deadline = time.monotonic() + args.timeout
    last = None
    while time.monotonic() < deadline:
        last = poll_dispatch(args)
        if last["done"]:
            result = {
                "ok": True,
                "mode": "completed_via_result_file",
                "started": start,
                "poll": last,
                "timed_out": False,
            }
            result["summary_path"] = write_run_summary(args.task_id, result)
            return result
        time.sleep(1.0)
    last = poll_dispatch(args)
    result = {
        "ok": bool(last and last["done"]),
        "mode": "background_running" if last and last["alive"] else "no_result_yet",
        "started": start,
        "poll": last,
        "timed_out": True,
    }
    result["summary_path"] = write_run_summary(args.task_id, result)
    return result


def validate_transport(args: argparse.Namespace) -> dict[str, Any]:
    plan = dispatch_plan(args)
    command = plan["command"]
    if len(command) < 3 or command[:3] != ["codex", "exec", "resume"]:
        raise SystemExit("unexpected command shape")
    session_files = plan.get("adapter_metadata", {}).get("session_files", [])
    ok = bool(plan["thread_id"] and session_files)
    return {
        "ok": ok,
        "department": plan["department"],
        "thread_name": plan["thread_name"],
        "thread_id": plan["thread_id"],
        "adapter": plan["adapter"],
        "packet_path": plan["packet_path"],
        "result_path": plan["result_path"],
        "sqlite_home": plan["sqlite_home"],
        "codex_home": plan["codex_home"],
        "session_files": session_files,
        "command_shell": plan["command_shell"],
        "message": "transport ready" if ok else "missing matching local Codex session file",
    }


def start_dispatch(args: argparse.Namespace) -> dict[str, Any]:
    request = build_transport_request(args)
    plan_obj = ADAPTER.plan(request)
    plan = {
        "department": args.department,
        "thread_name": request.thread_name,
        "thread_id": request.thread_id,
        **plan_obj.to_dict(),
    }
    if not request.thread_id:
        raise SystemExit(f"department {args.department} has no thread_id configured")

    result_path = ROOT / plan["result_path"]
    result_file_rel = extract_result_file_rel(args)
    result_file_path = ROOT / result_file_rel

    if result_path.exists():
        result_path.unlink()
    if result_file_path.exists():
        result_file_path.unlink()

    started = ADAPTER.start(request, plan_obj)

    meta = {
        "task_id": args.task_id,
        "department": args.department,
        "thread_id": request.thread_id,
        "thread_name": request.thread_name,
        "packet_path": plan["packet_path"],
        "result_path": plan["result_path"],
        "result_file": result_file_rel,
        "stdout_log": started.stdout_log,
        "stderr_log": started.stderr_log,
        "codex_home": plan_obj.metadata.get("codex_home", ""),
        "sqlite_home": plan_obj.metadata.get("sqlite_home", ""),
        "pid": started.pid,
        "adapter": started.adapter,
        "adapter_metadata": started.metadata,
        "started": True,
    }
    edge = runtime.link_conversation(
        argparse.Namespace(
            db=args.db,
            events=args.events,
            edge_id=f"dispatch_{args.task_id}_{args.department}",
            parent_task_id=args.task_id,
            department=args.department,
            thread_id=plan["thread_id"],
            thread_name=plan["thread_name"],
            conversation_role="department_dispatch",
            metadata=json.dumps(
                {
                    "packet_path": plan["packet_path"],
                    "result_path": plan["result_path"],
                    "result_file": result_file_rel,
                    "pid": started.pid,
                    "transport": started.adapter,
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            actor="CoAgentTransport",
        )
    )
    meta["conversation_edge"] = edge
    write_run_meta(args.task_id, meta)
    meta["summary_path"] = write_run_summary(args.task_id, meta)
    return meta


def poll_dispatch(args: argparse.Namespace) -> dict[str, Any]:
    meta = read_run_meta(args.task_id)
    alive = process_alive(meta["pid"])
    imported = maybe_import_result(args.task_id, args.db, args.events, meta["result_file"])
    closed_edge = None
    if imported and imported.get("state") in runtime.TERMINAL_STATES:
        try:
            closed_edge = runtime.close_conversation(
                argparse.Namespace(
                    db=args.db,
                    events=args.events,
                    edge_id=f"dispatch_{args.task_id}_{meta['department']}",
                    parent_task_id="",
                    thread_id="",
                    summary=f"dispatch result imported: {imported.get('state')}",
                    metadata=json.dumps(
                        {
                            "result_file": meta["result_file"],
                            "imported_state": imported.get("state"),
                            "summary_path": summary_path(args.task_id).relative_to(ROOT).as_posix(),
                        },
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    actor="CoAgentTransport",
                )
            )
        except SystemExit:
            closed_edge = None
    result_file_path = ROOT / meta["result_file"]
    result = {
        "task_id": args.task_id,
        "pid": meta["pid"],
        "alive": alive,
        "result_file": meta["result_file"],
        "result_file_exists": result_file_path.exists(),
        "stdout_log": meta["stdout_log"],
        "stderr_log": meta["stderr_log"],
        "imported_runtime_state": imported,
        "conversation_edge": closed_edge,
        "done": bool(imported and imported.get("state") in runtime.TERMINAL_STATES),
    }
    result["summary_path"] = write_run_summary(args.task_id, result)
    return result


def reconcile_result(args: argparse.Namespace) -> dict[str, Any]:
    dummy = argparse.Namespace(
        registry=args.registry,
        department=args.department,
        task_id=args.task_id,
        db=args.db,
        events=args.events,
        packet_file=None,
        result_file=getattr(args, "result_file", None),
    )
    plan = dispatch_plan(dummy)
    result_file_rel = extract_result_file_rel(dummy)
    result_file_path = ROOT / result_file_rel
    if not result_file_path.exists():
        return {
            "ok": False,
            "task_id": args.task_id,
            "result_file": result_file_rel,
            "message": "result file not found",
        }
    namespace = argparse.Namespace(
        db=args.db,
        events=args.events,
        packet=str(result_file_path),
        claim_token="",
        archive=True,
        archive_invalid=True,
    )
    routed = result_router.import_packet(namespace)
    if not routed.get("ok"):
        return {
            "ok": False,
            "task_id": args.task_id,
            "result_file": result_file_rel,
            "router": routed,
            "message": "result packet import failed",
        }
    imported = routed.get("runtime_state", routed)
    closed_edge = None
    try:
        closed_edge = runtime.close_conversation(
            argparse.Namespace(
                db=args.db,
                events=args.events,
                edge_id=f"dispatch_{args.task_id}_{args.department}",
                parent_task_id="",
                thread_id="",
                summary=f"reconciled result imported: {imported.get('state')}",
                metadata=json.dumps(
                    {
                        "result_file": result_file_rel,
                        "imported_state": imported.get("state"),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                actor="CoAgentTransport",
            )
        )
    except SystemExit:
        closed_edge = None
    result = {
        "ok": True,
        "task_id": args.task_id,
        "result_file": result_file_rel,
        "router": routed,
        "imported_runtime_state": imported,
        "conversation_edge": closed_edge,
    }
    result["summary_path"] = write_run_summary(args.task_id, result)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan-dispatch")
    plan_parser.add_argument("--registry", type=Path, default=ROOT / "CoAgent" / "dispatch" / "department_threads.json")
    plan_parser.add_argument("--department", required=True)
    plan_parser.add_argument("--task-id", required=True)
    plan_parser.add_argument("--db", type=Path, default=ROOT / "Results" / "agent_runtime" / "tasks.sqlite3")
    plan_parser.add_argument("--events", type=Path, default=ROOT / "Results" / "agent_runtime" / "events.jsonl")
    plan_parser.add_argument("--packet-file", type=Path, default=None)
    plan_parser.set_defaults(func=dispatch_plan)

    run_parser = subparsers.add_parser("run-dispatch")
    run_parser.add_argument("--registry", type=Path, default=ROOT / "CoAgent" / "dispatch" / "department_threads.json")
    run_parser.add_argument("--department", required=True)
    run_parser.add_argument("--task-id", required=True)
    run_parser.add_argument("--db", type=Path, default=ROOT / "Results" / "agent_runtime" / "tasks.sqlite3")
    run_parser.add_argument("--events", type=Path, default=ROOT / "Results" / "agent_runtime" / "events.jsonl")
    run_parser.add_argument("--timeout", type=int, default=60)
    run_parser.add_argument("--packet-file", type=Path, default=None)
    run_parser.add_argument("--result-file", type=Path, default=None)
    run_parser.set_defaults(func=dispatch_run)

    start_parser = subparsers.add_parser("start-dispatch")
    start_parser.add_argument("--registry", type=Path, default=ROOT / "CoAgent" / "dispatch" / "department_threads.json")
    start_parser.add_argument("--department", required=True)
    start_parser.add_argument("--task-id", required=True)
    start_parser.add_argument("--db", type=Path, default=ROOT / "Results" / "agent_runtime" / "tasks.sqlite3")
    start_parser.add_argument("--events", type=Path, default=ROOT / "Results" / "agent_runtime" / "events.jsonl")
    start_parser.add_argument("--packet-file", type=Path, default=None)
    start_parser.add_argument("--result-file", type=Path, default=None)
    start_parser.set_defaults(func=start_dispatch)

    validate_parser = subparsers.add_parser("validate-transport")
    validate_parser.add_argument("--registry", type=Path, default=ROOT / "CoAgent" / "dispatch" / "department_threads.json")
    validate_parser.add_argument("--department", required=True)
    validate_parser.add_argument("--task-id", required=True)
    validate_parser.add_argument("--db", type=Path, default=ROOT / "Results" / "agent_runtime" / "tasks.sqlite3")
    validate_parser.add_argument("--events", type=Path, default=ROOT / "Results" / "agent_runtime" / "events.jsonl")
    validate_parser.add_argument("--packet-file", type=Path, default=None)
    validate_parser.set_defaults(func=validate_transport)

    reconcile_parser = subparsers.add_parser("reconcile-result")
    reconcile_parser.add_argument("--registry", type=Path, default=ROOT / "CoAgent" / "dispatch" / "department_threads.json")
    reconcile_parser.add_argument("--department", required=True)
    reconcile_parser.add_argument("--task-id", required=True)
    reconcile_parser.add_argument("--db", type=Path, default=ROOT / "Results" / "agent_runtime" / "tasks.sqlite3")
    reconcile_parser.add_argument("--events", type=Path, default=ROOT / "Results" / "agent_runtime" / "events.jsonl")
    reconcile_parser.add_argument("--result-file", type=Path, default=None)
    reconcile_parser.set_defaults(func=reconcile_result)

    poll_parser = subparsers.add_parser("poll-dispatch")
    poll_parser.add_argument("--db", type=Path, default=ROOT / "Results" / "agent_runtime" / "tasks.sqlite3")
    poll_parser.add_argument("--events", type=Path, default=ROOT / "Results" / "agent_runtime" / "events.jsonl")
    poll_parser.add_argument("--task-id", required=True)
    poll_parser.set_defaults(func=poll_dispatch)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
