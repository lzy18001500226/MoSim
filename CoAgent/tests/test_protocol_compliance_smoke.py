#!/usr/bin/env python3
"""Smoke test for CoAgent protocol-compliance validation."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.context import context_pack
from CoAgent.doctor import protocol_compliance
from CoAgent.runtime import mosim_agent_runtime as runtime


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def main() -> int:
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        db = tmp_root / "tasks.sqlite3"
        events = tmp_root / "events.jsonl"
        task_id = "protocol_compliance_smoke"
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                objective="Verify CoAgent protocol compliance smoke path",
                role="ProjectOwner",
                read_scope=["CoAgent"],
                write_scope=["Results/agent_packets", "Results/context_packs"],
                acceptance="task/context/result artifacts satisfy protocol",
                stop_condition="protocol compliance passes",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "task_class": "long_running_task",
                        "project_goal": "CoAgent protocol-conformant lifecycle",
                        "phase_objective": "Protocol compliance gate",
                        "canonical_task_goal": "Verify task packet, context pack, and result packet protocol compliance",
                        "conversation_objective": "Run protocol compliance smoke and return reviewable result",
                        "accountable_owner": "ProjectOwner",
                        "definition_of_done": "protocol compliance validator returns ok",
                        "non_goals": ["transport expansion", "automation expansion"],
                        "required_evidence": ["protocol validation report"],
                        "appetite": "single protocol smoke pass",
                        "circuit_breaker": "missing required protocol field",
                        "checkpoint_plan": "one checkpoint at smoke completion",
                        "escalation_conditions": ["protocol validator fails", "context pack is missing required sections"],
                        "review_gates": ["protocol compliance smoke", "doctor"],
                        "review_owner": "Verification",
                        "human_review_points": ["accept protocol gate before transport expansion"],
                        "forbidden_actions": ["expand app-server transport", "create new permanent departments"],
                        "assumptions": ["project-owned packet flow remains the durable authority"],
                        "open_questions": ["whether result packet should later carry richer worktree closeout details"],
                        "worktree_path": "worktrees/projectowner/protocol-smoke",
                        "branch_or_base": "main",
                        "merge_owner": "GitIntegrator",
                        "close_condition": "review accepted and Git state summarized",
                        "git_status": "isolated_worktree_pending_review",
                        "next_recommended_action": "review protocol validation result",
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=40,
                actor="MainAgent",
            )
        )
        runtime.update_task(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                actor="ProjectOwner",
                claim_token="",
                summary="protocol compliance smoke ready for review",
                data="",
            ),
            state="done_with_concerns",
            event_type="task_completed",
        )

        task_packet = runtime.export_task_packet(ns(db=db, events=events, task_id=task_id))
        result_packet = runtime.export_result_packet(ns(db=db, events=events, task_id=task_id))
        context = context_pack.build_context_pack(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                output=None,
                event_limit=8,
                knowledge_query=["protocol compliance smoke"],
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
        report = protocol_compliance.validate_bundle(task_packet, context["text"], result_packet)
        assert report["ok"], report

        cli_report = protocol_compliance.check_task(ns(db=db, events=events, task_id=task_id, event_limit=8))
        assert cli_report["ok"], cli_report
        assert cli_report["task_packet"]["worktree_path"] == "worktrees/projectowner/protocol-smoke"
        assert "## Worktree Binding" in context["text"]
        assert "review_owner: Verification" in context["text"]
        assert "worktree_path: worktrees/projectowner/protocol-smoke" in context["text"]

    print("protocol_compliance_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
