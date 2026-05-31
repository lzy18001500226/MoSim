#!/usr/bin/env python3
"""Smoke test for reusable long-task bootstrap and recovery."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.bootstrap import task_bootstrap
from CoAgent.dispatch import codex_transport
from CoAgent.runtime import mosim_agent_runtime as runtime
from CoAgent.transport.codex_exec import CodexExecResumeAdapter


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def main() -> int:
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        db = tmp_root / "tasks.sqlite3"
        events = tmp_root / "events.jsonl"
        output_root = ROOT / "Results" / "coagent_bootstrap" / "smoke"
        context_root = ROOT / "Results" / "context_packs" / "smoke"
        task_id = "task_bootstrap_smoke"
        source_home = tmp_root / "codex_source_home"
        source_home.mkdir(parents=True, exist_ok=True)
        (source_home / "config.toml").write_text("model = \"gpt-5.5\"\n", encoding="utf-8")
        registry_data = json.loads((ROOT / "CoAgent" / "dispatch" / "department_threads.json").read_text(encoding="utf-8"))
        project_thread = next(item for item in registry_data["threads"] if item["department"] == "RuntimePlatformAgent")
        session_dir = source_home / "sessions" / "RuntimePlatformAgent"
        session_dir.mkdir(parents=True, exist_ok=True)
        (session_dir / "rollout.jsonl").write_text(
            f'{{"timestamp":"2026-05-27T00:00:00Z","type":"session_meta","payload":{{"id":"{project_thread["thread_id"]}","cwd":"{ROOT}"}}}}\n',
            encoding="utf-8",
        )

        old_adapter = codex_transport.ADAPTER
        codex_transport.ADAPTER = CodexExecResumeAdapter(source_home=source_home)
        try:
            boot = task_bootstrap.bootstrap_task(
                ns(
                    db=db,
                    events=events,
                    registry=ROOT / "CoAgent" / "dispatch" / "department_threads.json",
                    department="RuntimePlatformAgent",
                    output_root=output_root,
                    context_root=context_root,
                    actor="MainAgent",
                    task_id=task_id,
                    objective="Smoke test reusable CoAgent bootstrap",
                    role="RuntimePlatformAgent",
                    read_scope=["CoAgent/bootstrap", "CoAgent/runtime"],
                    write_scope=["Results/agent_packets", "Results/coagent_bootstrap"],
                    acceptance="bootstrap handoff and recovery work",
                    stop_condition="result packet imported",
                    depends_on=[],
                    metadata="",
                    priority=30,
                    parent_goal="coagent_transferable_multi_conversation_architecture",
                    owner_conversation="MoSim｜主线总控",
                    reuse_existing=False,
                    link_edge=True,
                    event_limit=8,
                    knowledge_query=["task bootstrap recovery"],
                    decision=[],
                    blocker=[],
                    include_memory_context=False,
                    memory_policy=None,
                    memory_limit_per_query=None,
                    memory_max_hits=None,
                    memory_max_chars=None,
                    warn_chars=14000,
                    fail_chars=22000,
                    include_transport_plan=True,
                )
            )
        finally:
            codex_transport.ADAPTER = old_adapter
        assert boot["ok"], boot
        assert (ROOT / boot["context_pack"]).exists()
        assert (ROOT / boot["dispatch_packet"]).exists()
        assert (ROOT / boot["handoff"]).exists()
        assert boot["conversation_edge"]["status"] == "open"
        assert boot["result_file"] == f"Results/agent_packets/{task_id}.yaml"
        assert boot["context_metrics"]["risk"] == "ok"
        assert boot["context_metrics"]["char_count"] > 0
        assert boot["transport_plan"]["command"][:3] == ["codex", "exec", "resume"]
        assert boot["transport_plan"]["adapter"] == "codex_exec_resume"
        assert boot["transport_plan_summary"].endswith(f"{task_id}.transport-plan.json")
        transport_packet = ROOT / boot["transport_packet"]
        transport_text = transport_packet.read_text(encoding="utf-8")
        assert "[MoSim Task Handoff]" in transport_text
        assert "## Context Pack" in transport_text

        result_file = ROOT / boot["result_file"]
        result_file.parent.mkdir(parents=True, exist_ok=True)
        result_file.write_text(
            "\n".join(
                [
                    "[MoSim Result Packet]",
                    f"task_id: {task_id}",
                    "status: done",
                    "summary: task bootstrap recovery smoke complete",
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

        recovery = task_bootstrap.recover_task(
            ns(
                db=db,
                events=events,
                registry=ROOT / "CoAgent" / "dispatch" / "department_threads.json",
                department="RuntimePlatformAgent",
                output_root=output_root,
                context_root=context_root,
                actor="MainAgent",
                task_id=task_id,
                claim_token="",
                import_result=True,
                close_edge=True,
                knowledge_upsert=True,
            )
        )
        assert recovery["ok"], recovery
        assert recovery["terminal"], recovery
        assert recovery["runtime_state"] == "done"
        assert recovery["closed_edge"]["status"] == "closed"
        assert recovery["result_summary"].endswith(f"{task_id}.summary.md")
        assert recovery["recovery_summary"].endswith(f"{task_id}.recovery.json")

        status = task_bootstrap.status_task(
            ns(
                db=db,
                events=events,
                registry=ROOT / "CoAgent" / "dispatch" / "department_threads.json",
                department="RuntimePlatformAgent",
                output_root=output_root,
                context_root=context_root,
                actor="MainAgent",
                task_id=task_id,
            )
        )
        assert status["terminal"], status
        assert status["conversation_graph"]["count"] == 1
        assert status["transport_plan_summary"].endswith(f"{task_id}.transport-plan.json")
        task = runtime.show_task(ns(db=db, events=events, task_id=task_id))
        assert task["state"] == "done"

    print("task_bootstrap_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
