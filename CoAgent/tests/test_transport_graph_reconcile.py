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


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


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
    print("transport_graph_reconcile ok")
    return 0


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
