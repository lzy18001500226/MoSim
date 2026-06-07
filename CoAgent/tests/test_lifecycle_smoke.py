#!/usr/bin/env python3
"""End-to-end smoke test for the CoAgent task lifecycle.

This proves the project-owned communication contract without launching a real
Codex conversation. It exercises the same durable artifacts the visible
conversation transport uses: runtime task state, context pack, dispatch text,
conversation edge, result packet router, packet summary, and knowledge search.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.context import context_pack
from CoAgent.dispatch import dispatch_helper
from CoAgent.knowledge import knowledge_indexer
from CoAgent.result_router import result_router
from CoAgent.runtime import mosim_agent_runtime as runtime


TASK_ID = "coagent_lifecycle_smoke"
DEPARTMENT = "RuntimePlatformAgent"
THREAD_ID = "019e74d1-72fa-7d33-8783-90584035ae92"
THREAD_NAME = "MoSim｜Agent Runtime 平台"


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def extract_result_file(packet_text: str) -> str:
    match = re.search(r"^result_file: (.+)$", packet_text, flags=re.MULTILINE)
    if not match:
        raise AssertionError("dispatch packet did not declare result_file")
    return match.group(1).strip()


def main() -> int:
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        db = tmp_root / "tasks.sqlite3"
        events = tmp_root / "events.jsonl"
        context_path = tmp_root / "context_pack.md"

        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=TASK_ID,
                objective="Prove CoAgent lifecycle from task creation to searchable result summary",
                role=DEPARTMENT,
                read_scope=["CoAgent", "Docs/Workflows/agent_task_ledger.md", "PROGRESS.md"],
                write_scope=["Results/agent_packets", "Results/context_packs", "Results/coagent_knowledge"],
                acceptance="context pack, dispatch edge, routed result, closed edge, and knowledge hit exist",
                stop_condition="runtime task is terminal and result summary is searchable",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "task_class": "long_running_task",
                        "project_goal": "CoAgent transferable multi-conversation architecture",
                        "canonical_task_goal": "Prove CoAgent lifecycle from task creation to searchable result summary",
                        "conversation_objective": "Run lifecycle smoke and return result packet",
                        "accountable_owner": DEPARTMENT,
                        "definition_of_done": "context pack, dispatch edge, routed result, closed edge, and knowledge hit exist",
                        "appetite": "single smoke lifecycle",
                        "circuit_breaker": "missing lifecycle artifact",
                        "checkpoint_plan": "checkpoint on each lifecycle artifact",
                        "required_evidence": ["result summary", "closed conversation edge", "knowledge hit"],
                        "review_gates": ["result router", "knowledge search"],
                        "department": DEPARTMENT,
                        "parent_goal": "coagent_transferable_multi_conversation_architecture",
                        "owner_conversation": "MoSim｜主线总控",
                        "task_conversation": THREAD_NAME,
                        "next_action": "run lifecycle smoke",
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=20,
                actor="MainAgent",
            )
        )

        context = context_pack.build_context_pack(
            ns(
                db=db,
                events=events,
                task_id=TASK_ID,
                output=context_path,
                event_limit=8,
                knowledge_query=["CoAgent lifecycle result router", "visible conversation context pack"],
                decision=["Dedicated task conversations start from runtime context packs, not raw chat history."],
                blocker=[],
                include_memory_context=False,
                memory_policy=None,
                memory_limit_per_query=1,
                memory_max_hits=2,
                memory_max_chars=1600,
            )
        )
        assert context["output"].endswith("context_pack.md")
        assert "[MoSim Context Pack]" in context["text"]
        assert "## Goal Stack" in context["text"]
        assert "## Review And Acceptance Gate" in context["text"]
        assert "## Result Packet Path" in context["text"]

        dispatch = dispatch_helper.build_department_task_text(
            ns(
                db=db,
                events=events,
                registry=ROOT / "CoAgent" / "dispatch" / "department_threads.json",
                department=DEPARTMENT,
                task_id=TASK_ID,
            )
        )
        assert "task_class: long_running_task" in dispatch["text"]
        assert "canonical_task_goal: Prove CoAgent lifecycle" in dispatch["text"]
        assert "definition_of_done:" in dispatch["text"]
        assert "appetite: single smoke lifecycle" in dispatch["text"]
        assert "Department Local Planning And Subagent Decision Contract" in dispatch["text"]
        assert "not a requirement to use at least one sub-agent" in dispatch["text"]
        assert "subagent_plan_reason" in dispatch["text"]
        result_file_rel = extract_result_file(dispatch["text"])
        assert result_file_rel == f"Results/agent_packets/{TASK_ID}.yaml"

        edge = runtime.link_conversation(
            ns(
                db=db,
                events=events,
                edge_id=f"dispatch_{TASK_ID}_{DEPARTMENT}",
                parent_task_id=TASK_ID,
                department=DEPARTMENT,
                thread_id=THREAD_ID,
                thread_name=THREAD_NAME,
                conversation_role="department_dispatch_smoke",
                metadata=json.dumps(
                    {
                        "context_pack": str(context_path.relative_to(ROOT)).replace("\\", "/"),
                        "result_file": result_file_rel,
                        "transport": "lifecycle_smoke",
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                actor="CoAgentLifecycleSmoke",
            )
        )
        assert edge["status"] == "open"

        result_file = ROOT / result_file_rel
        result_file.parent.mkdir(parents=True, exist_ok=True)
        result_file.write_text(
            "\n".join(
                [
                    "[MoSim Result Packet]",
                    f"task_id: {TASK_ID}",
                    "status: done",
                    "canonical_status: completed",
                    "task_class: long_running_task",
                    "canonical_task_goal: Prove CoAgent lifecycle from task creation to searchable result summary",
                    "conversation_objective: Run lifecycle smoke and return result packet",
                    "summary: lifecycle smoke complete: context dispatch result router knowledge closed edge",
                    "owner: RuntimePlatformAgent",
                    "role: RuntimePlatformAgent",
                    "read_scope: []",
                    "write_scope: []",
                    "events: []",
                    "evidence: [\"lifecycle smoke result summary\"]",
                    "next_recommended_action: none",
                    "",
                ]
            ),
            encoding="utf-8",
        )

        routed = result_router.import_packet(
            ns(db=db, events=events, packet=result_file, claim_token="", archive=True, archive_invalid=True)
        )
        assert routed["ok"], routed
        assert routed["runtime_state"]["state"] == "done"
        assert routed["summary_path"] == f"Results/agent_packets/summaries/{TASK_ID}.summary.md"
        summary_path = ROOT / routed["summary_path"]
        assert summary_path.exists()
        assert "lifecycle smoke complete" in summary_path.read_text(encoding="utf-8")

        closed = runtime.close_conversation(
            ns(
                db=db,
                events=events,
                edge_id=f"dispatch_{TASK_ID}_{DEPARTMENT}",
                parent_task_id="",
                thread_id="",
                summary="lifecycle smoke result imported and summarized",
                metadata=json.dumps(
                    {
                        "imported_state": routed["runtime_state"]["state"],
                        "summary_path": routed["summary_path"],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                actor="CoAgentLifecycleSmoke",
            )
        )
        assert closed["status"] == "closed"

        graph = runtime.conversation_graph(
            ns(
                db=db,
                events=events,
                parent_task_id=TASK_ID,
                department=DEPARTMENT,
                status="closed",
                include_tasks=True,
            )
        )
        assert graph["count"] == 1
        assert graph["tasks"][TASK_ID]["state"] == "done"

        knowledge_indexer.upsert_file(
            summary_path,
            source_id="result_packet_summaries",
            category="runtime_evidence",
            priority=7,
        )
        search = knowledge_indexer.search_index("lifecycle smoke complete result router knowledge", limit=10)
        hit_paths = {hit["path"] for hit in search["hits"]}
        assert routed["summary_path"] in hit_paths, search

    print("lifecycle_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
