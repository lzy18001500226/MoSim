#!/usr/bin/env python3
"""Smoke test for transport result import closing conversation graph edges."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.dispatch import codex_transport
from CoAgent.runtime import mosim_agent_runtime as runtime
from CoAgent.transport.adapter import TransportPlan
from CoAgent.transport.adapter import TransportStart


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


class TimeoutAdapter:
    name = "timeout_fake"

    def plan(self, request):
        request.packet_path.parent.mkdir(parents=True, exist_ok=True)
        request.result_path.parent.mkdir(parents=True, exist_ok=True)
        request.packet_path.write_text(request.packet_text.rstrip() + "\n", encoding="utf-8")
        return TransportPlan(
            adapter=self.name,
            thread_id=request.thread_id,
            thread_name=request.thread_name,
            packet_path=codex_transport.rel_project_path(request.packet_path),
            result_path=codex_transport.rel_project_path(request.result_path),
            command=["codex", "exec", "resume", request.thread_id],
            command_shell="codex exec resume fake",
            metadata={
                "codex_home": "Results/tmp/fake_codex_home",
                "sqlite_home": "Results/tmp/fake_sqlite_home",
                "copied_files": [],
                "session_files": ["Results/tmp/fake_rollout.jsonl"],
            },
            dry_run=False,
        )

    def start(self, request, plan):
        stdout = ROOT / "Results" / "tmp" / f"{request.task_id}.stdout.log"
        stderr = ROOT / "Results" / "tmp" / f"{request.task_id}.stderr.log"
        stdout.write_text("", encoding="utf-8")
        stderr.write_text("fake adapter produced no result packet\n", encoding="utf-8")
        return TransportStart(
            adapter=self.name,
            pid=0,
            stdout_log=codex_transport.rel_project_path(stdout),
            stderr_log=codex_transport.rel_project_path(stderr),
            metadata=plan.metadata,
        )


def main() -> int:
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        db = tmp_root / "tasks.sqlite3"
        events = tmp_root / "events.jsonl"
        task_id = "transport_graph_smoke"
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                objective="Smoke test transport graph reconciliation",
                role="RuntimePlatformAgent",
                read_scope=["CoAgent/dispatch"],
                write_scope=["Results/tmp"],
                acceptance="result import closes edge",
                stop_condition="done",
                depends_on=[],
                metadata="",
                priority=100,
                actor="RuntimePlatformAgent",
            )
        )
        runtime.link_conversation(
            ns(
                db=db,
                events=events,
                edge_id=f"dispatch_{task_id}_RuntimePlatformAgent",
                parent_task_id=task_id,
                department="RuntimePlatformAgent",
                thread_id="019e0000-0000-7000-8000-000000000002",
                thread_name="MoSim｜Agent Runtime 平台",
                conversation_role="department_dispatch",
                metadata='{"source":"smoke"}',
                actor="CoAgentTransport",
            )
        )
        result_rel = f"Results/tmp/{tmp_root.name}/{task_id}.yaml"
        result_path = ROOT / result_rel
        result_path.write_text(
            "\n".join(
                [
                    "[MoSim Result Packet]",
                    f"task_id: {task_id}",
                    "status: done",
                    "summary: transport graph smoke complete",
                    "owner: RuntimePlatformAgent",
                    "role: RuntimePlatformAgent",
                    "read_scope: []",
                    "write_scope: []",
                    "events: []",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        meta = {
            "task_id": task_id,
            "department": "RuntimePlatformAgent",
            "thread_id": "019e0000-0000-7000-8000-000000000002",
            "thread_name": "MoSim｜Agent Runtime 平台",
            "packet_path": "",
            "result_path": "",
            "result_file": result_rel,
            "stdout_log": result_rel,
            "stderr_log": result_rel,
            "codex_home": "",
            "sqlite_home": "",
            "pid": 0,
            "started": True,
        }
        codex_transport.write_run_meta(task_id, meta)
        polled = codex_transport.poll_dispatch(ns(db=db, events=events, task_id=task_id))
        assert polled["done"] is True
        assert polled["imported_runtime_state"]["state"] == "done"
        assert polled["conversation_edge"]["status"] == "closed"
        graph = runtime.conversation_graph(
            ns(
                db=db,
                events=events,
                parent_task_id=task_id,
                department="RuntimePlatformAgent",
                status="closed",
                include_tasks=True,
            )
        )
        assert graph["count"] == 1
        assert task_id in graph["tasks"]
        # Repeated polling should stay closed and not fail.
        again = codex_transport.poll_dispatch(ns(db=db, events=events, task_id=task_id))
        assert again["done"] is True
        assert again["conversation_edge"]["status"] == "closed"
    test_timeout_dispatch_writes_imports_and_closes_edge()
    test_finalize_timeout_imports_existing_half_open_dispatch()
    test_extract_explicit_result_file_for_custom_packet()
    print("transport_graph_reconcile ok")
    return 0


def test_timeout_dispatch_writes_imports_and_closes_edge() -> None:
    old_adapter = codex_transport.ADAPTER
    codex_transport.ADAPTER = TimeoutAdapter()
    try:
        with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
            tmp_root = Path(tmp)
            db = tmp_root / "tasks.sqlite3"
            events = tmp_root / "events.jsonl"
            registry = tmp_root / "department_threads.json"
            task_id = "transport_timeout_smoke"
            registry.write_text(
                json.dumps(
                    {
                        "threads": [
                            {
                                "department": "RuntimePlatformAgent",
                                "thread_id": "019e0000-0000-7000-8000-000000000003",
                                "thread_name": "MoSim｜Agent Runtime 平台",
                                "surface": "codex_app",
                                "status": "active_visible",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            runtime.create_task(
                ns(
                    db=db,
                    events=events,
                    task_id=task_id,
                    objective="Smoke test timeout transport result import",
                    role="RuntimePlatformAgent",
                    read_scope=["CoAgent/dispatch"],
                    write_scope=["Results/tmp"],
                    acceptance="timeout import closes edge",
                    stop_condition="blocked",
                    depends_on=[],
                    metadata="",
                    priority=100,
                    actor="RuntimePlatformAgent",
                )
            )
            result = codex_transport.dispatch_run(
                ns(
                    registry=registry,
                    department="RuntimePlatformAgent",
                    task_id=task_id,
                    db=db,
                    events=events,
                    packet_file=None,
                    result_file=None,
                    timeout=0,
                    write_timeout_result=True,
                )
            )
            assert result["ok"] is True
            assert result["mode"] == "timeout_result_imported"
            assert result["timeout_result_file"].endswith(f"{task_id}.yaml")
            task = runtime.show_task(ns(db=db, events=events, task_id=task_id))
            assert task["state"] == "blocked"
            assert task["metadata"]["result_packet_imported"] is True
            assert task["metadata"]["blockers"] == ["transport_timeout_no_result_packet"]
            graph = runtime.conversation_graph(
                ns(
                    db=db,
                    events=events,
                    parent_task_id=task_id,
                    department="RuntimePlatformAgent",
                    status="closed",
                    include_tasks=True,
                )
            )
            assert graph["count"] == 1
            assert graph["edges"][0]["status"] == "closed"
    finally:
        codex_transport.ADAPTER = old_adapter


def test_finalize_timeout_imports_existing_half_open_dispatch() -> None:
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        db = tmp_root / "tasks.sqlite3"
        events = tmp_root / "events.jsonl"
        task_id = "transport_finalize_timeout_smoke"
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                objective="Smoke test timeout finalizer",
                role="RuntimePlatformAgent",
                read_scope=["CoAgent/dispatch"],
                write_scope=["Results/tmp"],
                acceptance="finalizer closes edge",
                stop_condition="blocked",
                depends_on=[],
                metadata="",
                priority=100,
                actor="RuntimePlatformAgent",
            )
        )
        runtime.link_conversation(
            ns(
                db=db,
                events=events,
                edge_id=f"dispatch_{task_id}_RuntimePlatformAgent",
                parent_task_id=task_id,
                department="RuntimePlatformAgent",
                thread_id="019e0000-0000-7000-8000-000000000004",
                thread_name="MoSim｜Agent Runtime 平台",
                conversation_role="department_dispatch",
                metadata='{"source":"half_open"}',
                actor="CoAgentTransport",
            )
        )
        result_rel = f"Results/tmp/{tmp_root.name}/{task_id}.yaml"
        stdout = ROOT / "Results" / "tmp" / tmp_root.name / f"{task_id}.stdout.log"
        stderr = ROOT / "Results" / "tmp" / tmp_root.name / f"{task_id}.stderr.log"
        stdout.parent.mkdir(parents=True, exist_ok=True)
        stdout.write_text("", encoding="utf-8")
        stderr.write_text("half-open dispatch without result packet\n", encoding="utf-8")
        codex_transport.write_run_meta(
            task_id,
            {
                "task_id": task_id,
                "department": "RuntimePlatformAgent",
                "thread_id": "019e0000-0000-7000-8000-000000000004",
                "thread_name": "MoSim｜Agent Runtime 平台",
                "packet_path": "",
                "result_path": "",
                "result_file": result_rel,
                "stdout_log": codex_transport.rel_project_path(stdout),
                "stderr_log": codex_transport.rel_project_path(stderr),
                "codex_home": "",
                "sqlite_home": "",
                "pid": 0,
                "started": True,
            },
        )
        result = codex_transport.finalize_timeout(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                summary="half-open dispatch finalized",
                next_action="rerun dispatch after transport repair",
            )
        )
        assert result["ok"] is True
        task = runtime.show_task(ns(db=db, events=events, task_id=task_id))
        assert task["state"] == "blocked"
        assert task["metadata"]["blockers"] == ["transport_no_result_packet"]
        graph = runtime.conversation_graph(
            ns(
                db=db,
                events=events,
                parent_task_id=task_id,
                department="RuntimePlatformAgent",
                status="closed",
                include_tasks=True,
            )
        )
        assert graph["count"] == 1


def test_extract_explicit_result_file_for_custom_packet() -> None:
    explicit = codex_transport.extract_result_file_rel(
        ns(
            packet_file=ROOT / "Results" / "tmp" / "custom_packet.md",
            result_file=ROOT / "Results" / "tmp" / "custom_result.json",
        )
    )
    assert explicit == "Results/tmp/custom_result.json"


if __name__ == "__main__":
    raise SystemExit(main())
