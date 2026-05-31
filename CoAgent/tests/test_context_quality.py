#!/usr/bin/env python3
"""Smoke tests for CoAgent context pack quality checks."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.context import context_pack, context_quality
from CoAgent.runtime import mosim_agent_runtime as runtime


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def main() -> int:
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        db = tmp_root / "tasks.sqlite3"
        events = tmp_root / "events.jsonl"
        task_id = "coagent_context_quality_smoke"
        output = tmp_root / "context.md"
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                objective="Prove context pack quality gate",
                role="ContextMemoryAgent",
                read_scope=["CoAgent/context"],
                write_scope=["Results/context_packs"],
                acceptance="context quality passes",
                stop_condition="context pack is valid",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "task_class": "long_running_task",
                        "project_goal": "CoAgent transferable multi-conversation architecture",
                        "canonical_task_goal": "Prove context pack quality gate",
                        "conversation_objective": "Generate and validate a compact context pack",
                        "definition_of_done": "context quality passes",
                        "review_owner": "VerificationAgent",
                        "required_evidence": ["context quality report"],
                        "review_gates": ["context_quality"],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=20,
                actor="MainAgent",
            )
        )
        built = context_pack.build_context_pack(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                output=output,
                event_limit=8,
                knowledge_query=["context pack quality"],
                decision=[],
                blocker=[],
                include_memory_context=False,
                memory_policy=None,
                memory_limit_per_query=None,
                memory_max_hits=None,
                memory_max_chars=None,
                warn_chars=14000,
                fail_chars=22000,
            )
        )
        assert built["metrics"]["risk"] == "ok"
        quality = context_quality.check_file(ns(path=output, warn_chars=14000, fail_chars=22000, json=True))
        assert quality["ok"], quality
        assert quality["fail_count"] == 0
        assert quality["path"].endswith("context.md")

        bad = tmp_root / "bad.md"
        bad.write_text("## Goal Stack\nproject_goal: missing much\n", encoding="utf-8")
        bad_quality = context_quality.check_file(ns(path=bad, warn_chars=14000, fail_chars=22000, json=True))
        assert not bad_quality["ok"]
        assert any(item["reason"] == "missing_required_section" for item in bad_quality["findings"])

    print("context_quality_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
