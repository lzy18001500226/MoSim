#!/usr/bin/env python3
"""Smoke tests for CoAgent transport adapter planning."""

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
from CoAgent.transport.codex_exec import CodexExecResumeAdapter


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def main() -> int:
    source_home = ROOT / "Results" / "tmp" / "codex_adapter_source_home"
    source_home.mkdir(parents=True, exist_ok=True)
    (source_home / "config.toml").write_text("model = \"gpt-5.5\"\n", encoding="utf-8")
    registry = json.loads((ROOT / "CoAgent" / "dispatch" / "department_threads.json").read_text(encoding="utf-8"))
    project_thread = next(item for item in registry["threads"] if item["department"] == "RuntimePlatformAgent")
    thread_id = project_thread["thread_id"]
    session_dir = source_home / "sessions" / "2026" / "05" / "27"
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "rollout.jsonl").write_text(
        f'{{"timestamp":"2026-05-27T00:00:00Z","type":"session_meta","payload":{{"id":"{thread_id}","cwd":"{ROOT}"}}}}\n',
        encoding="utf-8",
    )
    (session_dir / "unrelated.jsonl").write_text(
        f'{{"timestamp":"2026-05-27T00:00:00Z","type":"response_item","payload":{{"text":"mentions {thread_id} but is not the target session"}}}}\n',
        encoding="utf-8",
    )

    adapter = CodexExecResumeAdapter(source_home=source_home)
    old_adapter = codex_transport.ADAPTER
    codex_transport.ADAPTER = adapter
    try:
        with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
            tmp_root = Path(tmp)
            db = tmp_root / "tasks.sqlite3"
            events = tmp_root / "events.jsonl"
            task_id = "transport_adapter_smoke"
            runtime.create_task(
                ns(
                    db=db,
                    events=events,
                    task_id=task_id,
                    objective="Smoke test transport adapter plan",
                    role="RuntimePlatformAgent",
                    read_scope=["CoAgent/transport"],
                    write_scope=["Results/tmp"],
                    acceptance="adapter plan preserves command contract",
                    stop_condition="done",
                    depends_on=[],
                    metadata="",
                    priority=100,
                    actor="RuntimePlatformAgent",
                )
            )
            plan = codex_transport.dispatch_plan(
                ns(
                    registry=ROOT / "CoAgent" / "dispatch" / "department_threads.json",
                    department="RuntimePlatformAgent",
                    task_id=task_id,
                    db=db,
                    events=events,
                )
            )
            assert plan["adapter"] == "codex_exec_resume"
            assert plan["command"][:3] == ["codex", "exec", "resume"]
            assert plan["thread_id"]
            assert plan["packet_path"].endswith(f"{task_id}_packet.txt")
            assert plan["result_path"].endswith(f"{task_id}_result.txt")
            assert "sqlite_home" in plan and plan["sqlite_home"]
            assert "codex_home" in plan and plan["codex_home"]
            assert plan["copied_files"]
            copied = "\n".join(plan["copied_files"])
            assert "rollout.jsonl" in copied
            assert "unrelated.jsonl" not in copied
            assert "sessions/sessions" not in copied
            assert plan["adapter_metadata"]["session_files"]
            assert (ROOT / plan["packet_path"]).exists()
    finally:
        codex_transport.ADAPTER = old_adapter

    print("transport_adapter_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
