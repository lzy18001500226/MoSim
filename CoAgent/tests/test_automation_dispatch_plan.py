#!/usr/bin/env python3
"""Smoke test automation dry-run dispatch planning."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.automation import automation_runner
from CoAgent.dispatch import codex_transport
from CoAgent.transport.codex_exec import CodexExecResumeAdapter


def main() -> int:
    source_home = ROOT / "Results" / "tmp" / "automation_plan_source_home"
    source_home.mkdir(parents=True, exist_ok=True)
    (source_home / "config.toml").write_text("model = \"gpt-5.5\"\n", encoding="utf-8")
    registry = json.loads((ROOT / "CoAgent" / "dispatch" / "department_threads.json").read_text(encoding="utf-8"))
    for thread in registry["threads"]:
        thread_id = thread.get("thread_id")
        if not thread_id:
            continue
        session_dir = source_home / "sessions" / thread["department"]
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "rollout.jsonl").write_text(
            f'{{"timestamp":"2026-05-27T00:00:00Z","type":"session_meta","payload":{{"id":"{thread_id}","cwd":"{ROOT}"}}}}\n',
            encoding="utf-8",
        )

    old_adapter = codex_transport.ADAPTER
    codex_transport.ADAPTER = CodexExecResumeAdapter(source_home=source_home)
    try:
        result = automation_runner.plan_due_dispatch(
            argparse.Namespace(
                registry=ROOT / "CoAgent" / "automation" / "automation_tasks.json",
                thread_registry=ROOT / "CoAgent" / "dispatch" / "department_threads.json",
                cadence="daily",
                priority=120,
                actor="AutomationRunner",
            )
        )
    finally:
        codex_transport.ADAPTER = old_adapter

    assert result["ok"] if "ok" in result else True
    assert result["count"] >= 1
    for item in result["plans"]:
        dispatch = item["dispatch_plan"]
        guard = item["task_preview"]["guardrail"]
        assert guard["ok"], guard
        assert dispatch["adapter"] == "codex_exec_resume"
        assert dispatch["command"][:3] == ["codex", "exec", "resume"]
        assert dispatch["packet_path"].endswith("_packet.txt")
        assert dispatch["result_path"].endswith("_result.txt")

    print("automation_dispatch_plan_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
