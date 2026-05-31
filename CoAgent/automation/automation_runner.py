#!/usr/bin/env python3
"""Minimal CoAgent automation runner."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
AUTOMATION_JSON = ROOT / "CoAgent" / "automation" / "automation_tasks.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.runtime import mosim_agent_runtime as runtime
from CoAgent.dispatch import codex_transport
from CoAgent.dispatch.conversation_registry import get_thread_by_department
from CoAgent.automation import guardrails
from CoAgent.transport.adapter import TransportRequest


def load_definitions(path: Path = AUTOMATION_JSON) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def list_tasks(args: argparse.Namespace) -> dict[str, Any]:
    return load_definitions(args.registry)


def is_due(task: dict[str, Any], cadence: str) -> bool:
    return task.get("cadence") == cadence


def due_task_list(data: dict[str, Any], cadence: str) -> list[dict[str, Any]]:
    return [task for task in data["tasks"] if is_due(task, cadence)]


def due_tasks(args: argparse.Namespace) -> dict[str, Any]:
    data = load_definitions(args.registry)
    tasks = due_task_list(data, args.cadence)
    return {"cadence": args.cadence, "count": len(tasks), "tasks": tasks}


def guard_due(args: argparse.Namespace) -> dict[str, Any]:
    data = load_definitions(args.registry)
    tasks = due_task_list(data, args.cadence)
    checked = guardrails.check_registry(tasks, acquire=args.acquire_locks, run_id=args.run_id, reviewed=args.reviewed)
    return {"cadence": args.cadence, **checked}


def worker_status(args: argparse.Namespace) -> dict[str, Any]:
    return guardrails.worker_status(args.worker_policy)


def enqueue_due(args: argparse.Namespace) -> dict[str, Any]:
    data = load_definitions(args.registry)
    created = []
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
    for task in due_task_list(data, args.cadence):
        metadata = {
            "department": task.get("department", ""),
            "automation_id": task["automation_id"],
            "cadence": task["cadence"],
            "parent_goal": "coagent_automation"
        }
        namespace = argparse.Namespace(
            db=args.db,
            events=args.events,
            task_id=f"auto_{task['automation_id']}_{stamp}",
            objective=task["objective"],
            role=task["role"],
            read_scope=task.get("read_scope", []),
            write_scope=task.get("write_scope", []),
            acceptance=task["acceptance"],
            stop_condition=task["stop_condition"],
            depends_on=[],
            metadata=json.dumps(metadata, ensure_ascii=False),
            priority=args.priority,
            actor=args.actor,
        )
        created.append(runtime.create_task(namespace))
    return {"cadence": args.cadence, "count": len(created), "tasks": created}


def plan_due_dispatch(args: argparse.Namespace) -> dict[str, Any]:
    data = load_definitions(args.registry)
    plans = []
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
    for task in due_task_list(data, args.cadence):
        guard = guardrails.check_task(task)
        metadata = {
            "department": task.get("department", ""),
            "automation_id": task["automation_id"],
            "cadence": task["cadence"],
            "parent_goal": "coagent_automation"
        }
        task_id = f"auto_{task['automation_id']}_{stamp}"
        thread = get_thread_by_department(task.get("department", ""), args.thread_registry)
        result_file = f"Results/agent_packets/{task_id}.yaml"
        packet_path = ROOT / "Results" / "coagent_transport" / f"{task_id}_packet.txt"
        result_path = ROOT / "Results" / "coagent_transport" / f"{task_id}_result.txt"
        packet_text = "\n".join(
            [
                "[MoSim Task Packet]",
                f"task_id: {task_id}",
                f"role: {task['role']}",
                f"objective: {task['objective']}",
                f"read_scope: {json.dumps(task.get('read_scope', []), ensure_ascii=False)}",
                f"write_scope: {json.dumps(task.get('write_scope', []), ensure_ascii=False)}",
                f"acceptance: {task['acceptance']}",
                f"stop_condition: {task['stop_condition']}",
                "dependencies: []",
                f"metadata: {json.dumps(metadata, ensure_ascii=False, sort_keys=True)}",
                f"result_file: {result_file}",
            ]
        )
        transport_plan = codex_transport.ADAPTER.plan(
            TransportRequest(
                task_id=task_id,
                department=task.get("department", ""),
                thread_id=thread["thread_id"],
                thread_name=thread["thread_name"],
                packet_path=packet_path,
                result_path=result_path,
                packet_text=packet_text,
            )
        )
        plans.append(
            {
                "task_preview": {
                    "task_id": task_id,
                    "objective": task["objective"],
                    "role": task["role"],
                    "department": task.get("department", ""),
                    "read_scope": task.get("read_scope", []),
                    "write_scope": task.get("write_scope", []),
                    "acceptance": task["acceptance"],
                    "stop_condition": task["stop_condition"],
                "metadata": metadata,
                "result_file": result_file,
                "guardrail": guard.to_dict(),
            },
                "dispatch_plan": {
                    "department": task.get("department", ""),
                    "thread_name": thread["thread_name"],
                    "thread_id": thread["thread_id"],
                    "packet_text": packet_text,
                    "adapter": transport_plan.adapter,
                    "packet_path": transport_plan.packet_path,
                    "result_path": transport_plan.result_path,
                    "command": transport_plan.command,
                    "command_shell": transport_plan.command_shell,
                    "adapter_metadata": transport_plan.metadata,
                    "dry_run": True,
                },
            }
        )
    return {"cadence": args.cadence, "count": len(plans), "plans": plans}


def enqueue_and_plan_due(args: argparse.Namespace) -> dict[str, Any]:
    data = load_definitions(args.registry)
    plans = []
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
    for task in due_task_list(data, args.cadence):
        metadata = {
            "department": task.get("department", ""),
            "automation_id": task["automation_id"],
            "cadence": task["cadence"],
            "parent_goal": "coagent_automation"
        }
        namespace = argparse.Namespace(
            db=args.db,
            events=args.events,
            task_id=f"auto_{task['automation_id']}_{stamp}",
            objective=task["objective"],
            role=task["role"],
            read_scope=task.get("read_scope", []),
            write_scope=task.get("write_scope", []),
            acceptance=task["acceptance"],
            stop_condition=task["stop_condition"],
            depends_on=[],
            metadata=json.dumps(metadata, ensure_ascii=False),
            priority=args.priority,
            actor=args.actor,
        )
        created = runtime.create_task(namespace)
        dispatch_args = argparse.Namespace(
            registry=args.thread_registry,
            department=task.get("department", ""),
            task_id=created["task_id"],
            db=args.db,
            events=args.events,
        )
        plan = codex_transport.dispatch_plan(dispatch_args)
        plans.append({"task": created, "dispatch_plan": plan})
    return {"cadence": args.cadence, "count": len(plans), "plans": plans}


def start_due_dispatch(args: argparse.Namespace) -> dict[str, Any]:
    data = load_definitions(args.registry)
    runs = []
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d_%H%M%S")
    for task in due_task_list(data, args.cadence):
        run_id = f"{task['automation_id']}_{stamp}"
        guard = guardrails.check_task(task, acquire=True, run_id=run_id, reviewed=args.reviewed)
        if not guard.ok:
            runs.append({"automation_id": task["automation_id"], "guardrail": guard.to_dict(), "skipped": True})
            continue
        metadata = {
            "department": task.get("department", ""),
            "automation_id": task["automation_id"],
            "cadence": task["cadence"],
            "parent_goal": "coagent_automation"
        }
        namespace = argparse.Namespace(
            db=args.db,
            events=args.events,
            task_id=f"auto_{task['automation_id']}_{stamp}",
            objective=task["objective"],
            role=task["role"],
            read_scope=task.get("read_scope", []),
            write_scope=task.get("write_scope", []),
            acceptance=task["acceptance"],
            stop_condition=task["stop_condition"],
            depends_on=[],
            metadata=json.dumps(metadata, ensure_ascii=False),
            priority=args.priority,
            actor=args.actor,
        )
        created = runtime.create_task(namespace)
        dispatch_args = argparse.Namespace(
            registry=args.thread_registry,
            department=task.get("department", ""),
            task_id=created["task_id"],
            db=args.db,
            events=args.events,
        )
        try:
            started = codex_transport.start_dispatch(dispatch_args)
        except Exception:
            guardrails.release_lock(guard.lock_id)
            raise
        runs.append({"task": created, "guardrail": guard.to_dict(), "dispatch_started": started})
    return {"cadence": args.cadence, "count": len(runs), "runs": runs}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--registry", type=Path, default=AUTOMATION_JSON)
    list_parser.set_defaults(func=list_tasks)

    due_parser = subparsers.add_parser("due")
    due_parser.add_argument("--registry", type=Path, default=AUTOMATION_JSON)
    due_parser.add_argument("--cadence", choices=["daily", "weekly"], default="daily")
    due_parser.set_defaults(func=due_tasks)

    guard_parser = subparsers.add_parser("guard-due")
    guard_parser.add_argument("--registry", type=Path, default=AUTOMATION_JSON)
    guard_parser.add_argument("--cadence", choices=["daily", "weekly"], default="daily")
    guard_parser.add_argument("--acquire-locks", action="store_true")
    guard_parser.add_argument("--run-id", default="")
    guard_parser.add_argument("--reviewed", action="store_true")
    guard_parser.set_defaults(func=guard_due)

    worker_parser = subparsers.add_parser("worker-status")
    worker_parser.add_argument("--worker-policy", type=Path, default=ROOT / "CoAgent" / "automation" / "worker_policy.json")
    worker_parser.set_defaults(func=worker_status)

    enqueue_parser = subparsers.add_parser("enqueue-due")
    runtime.add_common(enqueue_parser)
    enqueue_parser.add_argument("--registry", type=Path, default=AUTOMATION_JSON)
    enqueue_parser.add_argument("--cadence", choices=["daily", "weekly"], default="daily")
    enqueue_parser.add_argument("--priority", type=int, default=120)
    enqueue_parser.add_argument("--actor", default="AutomationRunner")
    enqueue_parser.set_defaults(func=enqueue_due)

    dispatch_plan_parser = subparsers.add_parser("plan-due-dispatch")
    runtime.add_common(dispatch_plan_parser)
    dispatch_plan_parser.add_argument("--registry", type=Path, default=AUTOMATION_JSON)
    dispatch_plan_parser.add_argument("--thread-registry", type=Path, default=ROOT / "CoAgent" / "dispatch" / "department_threads.json")
    dispatch_plan_parser.add_argument("--cadence", choices=["daily", "weekly"], default="daily")
    dispatch_plan_parser.add_argument("--priority", type=int, default=120)
    dispatch_plan_parser.add_argument("--actor", default="AutomationRunner")
    dispatch_plan_parser.set_defaults(func=plan_due_dispatch)

    enqueue_dispatch_parser = subparsers.add_parser("enqueue-and-plan-due")
    runtime.add_common(enqueue_dispatch_parser)
    enqueue_dispatch_parser.add_argument("--registry", type=Path, default=AUTOMATION_JSON)
    enqueue_dispatch_parser.add_argument("--thread-registry", type=Path, default=ROOT / "CoAgent" / "dispatch" / "department_threads.json")
    enqueue_dispatch_parser.add_argument("--cadence", choices=["daily", "weekly"], default="daily")
    enqueue_dispatch_parser.add_argument("--priority", type=int, default=120)
    enqueue_dispatch_parser.add_argument("--actor", default="AutomationRunner")
    enqueue_dispatch_parser.set_defaults(func=enqueue_and_plan_due)

    start_dispatch_parser = subparsers.add_parser("start-due-dispatch")
    runtime.add_common(start_dispatch_parser)
    start_dispatch_parser.add_argument("--registry", type=Path, default=AUTOMATION_JSON)
    start_dispatch_parser.add_argument("--thread-registry", type=Path, default=ROOT / "CoAgent" / "dispatch" / "department_threads.json")
    start_dispatch_parser.add_argument("--cadence", choices=["daily", "weekly"], default="daily")
    start_dispatch_parser.add_argument("--priority", type=int, default=120)
    start_dispatch_parser.add_argument("--actor", default="AutomationRunner")
    start_dispatch_parser.add_argument("--reviewed", action="store_true")
    start_dispatch_parser.set_defaults(func=start_due_dispatch)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = args.func(args)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
