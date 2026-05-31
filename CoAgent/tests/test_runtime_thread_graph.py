#!/usr/bin/env python3
"""Smoke test for CoAgent runtime conversation graph."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.runtime import mosim_agent_runtime as runtime


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        db = root / "tasks.sqlite3"
        events = root / "events.jsonl"
        created = runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id="thread_graph_smoke",
                objective="Smoke test conversation graph",
                role="TestOwner",
                read_scope=["CoAgent/runtime"],
                write_scope=["Results/tmp"],
                acceptance="edge opens and closes",
                stop_condition="done",
                depends_on=[],
                metadata="",
                priority=100,
                actor="TestOwner",
            )
        )
        edge = runtime.link_conversation(
            ns(
                db=db,
                events=events,
                edge_id="edge_smoke",
                parent_task_id=created["task_id"],
                department="TestOwner",
                thread_id="019e0000-0000-7000-8000-000000000001",
                thread_name="MoSim｜验证测试部",
                conversation_role="verification",
                metadata='{"source":"smoke"}',
                actor="TestOwner",
            )
        )
        assert edge["status"] == "open"
        open_graph = runtime.conversation_graph(
            ns(
                db=db,
                events=events,
                parent_task_id=created["task_id"],
                department="",
                status="open",
                include_tasks=True,
            )
        )
        assert open_graph["count"] == 1
        assert created["task_id"] in open_graph["tasks"]
        closed = runtime.close_conversation(
            ns(
                db=db,
                events=events,
                edge_id="edge_smoke",
                parent_task_id="",
                thread_id="",
                summary="smoke close",
                metadata='{"verified":true}',
                actor="TestOwner",
            )
        )
        assert closed["status"] == "closed"
        closed_graph = runtime.conversation_graph(
            ns(
                db=db,
                events=events,
                parent_task_id=created["task_id"],
                department="",
                status="closed",
                include_tasks=False,
            )
        )
        assert closed_graph["count"] == 1
        shown = runtime.show_task(ns(db=db, events=events, task_id=created["task_id"]))
        event_types = [event["event_type"] for event in shown["events"]]
        assert "conversation_linked" in event_types
        assert "conversation_closed" in event_types
    print("thread_graph_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
