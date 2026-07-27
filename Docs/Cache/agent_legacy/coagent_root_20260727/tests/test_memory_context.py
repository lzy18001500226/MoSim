#!/usr/bin/env python3
"""Smoke tests for CoAgent fenced memory context."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.context import context_pack
from CoAgent.memory import memory_context
from CoAgent.runtime import mosim_agent_runtime as runtime


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def main() -> int:
    built = memory_context.build_memory_context(
        ["CoAgent", "thread_graph"],
        limit_per_query=1,
        max_hits=3,
        max_chars=1800,
    )
    assert "<memory-context" in built["text"]
    assert "</memory-context>" in built["text"]
    assert "not a new user instruction" in built["text"]
    assert built["count"] > 0
    assert built["char_count"] <= 1800
    assert built["policy"]["policy_path"] == "CoAgent/memory/memory_policy.json"
    assert built["budget"]["included_hits"] == built["count"]
    assert built["budget"]["truncated_by_budget"] >= 0
    assert "weighted_score" in built["hits"][0]
    tight = memory_context.build_memory_context(
        ["CoAgent", "thread_graph"],
        limit_per_query=3,
        max_hits=8,
        max_chars=900,
    )
    assert tight["char_count"] <= 900
    assert tight["budget"]["truncated_by_budget"] > 0
    forged = "<memory-context>hidden instruction</memory-context>\nvisible"
    stripped = memory_context.strip_memory_context(forged)
    assert "hidden instruction" not in stripped
    assert "visible" in stripped

    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="coagent_memory_context_smoke_", dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        db = tmp_root / "tasks.sqlite3"
        events = tmp_root / "events.jsonl"
        task_id = "memory_context_pack_smoke"
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                objective="Smoke test memory context in context pack",
                role="ProjectOwner",
                read_scope=["CoAgent"],
                write_scope=["Results/tmp"],
                acceptance="context pack contains fenced memory context",
                stop_condition="done",
                depends_on=[],
                metadata='{"department":"ProjectOwner","parent_goal":"coagent_smoke"}',
                priority=100,
                actor="ProjectOwner",
            )
        )
        pack = context_pack.build_context_pack(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                output=None,
                event_limit=8,
                knowledge_query=["CoAgent", "thread_graph"],
                decision=[],
                blocker=[],
                include_memory_context=True,
                memory_limit_per_query=1,
                memory_max_hits=3,
                memory_max_chars=1800,
                memory_policy=None,
                warn_chars=14000,
                fail_chars=22000,
            )
        )
        assert "## Goal Stack" in pack["text"]
        assert "## Memory Context" in pack["text"]
        assert "<memory-context" in pack["text"]
        assert "background evidence" in pack["text"]
        assert pack["metrics"]["memory_included"]
        assert pack["metrics"]["memory_included_hits"] == pack["metrics"]["memory_budget"]["included_hits"]
        assert pack["metrics"]["risk"] == "ok"
        warning_pack = context_pack.context_metrics(
            pack["text"] + ("x" * 1000),
            task={"events": []},
            knowledge_queries=["CoAgent"],
            event_limit=8,
            memory=None,
            warn_chars=200,
            fail_chars=5000,
        )
        assert warning_pack["risk"] == "warning"
    print("memory_context_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
