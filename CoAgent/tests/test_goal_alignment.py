#!/usr/bin/env python3
"""Smoke tests for CoAgent goal-alignment validation."""

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
from CoAgent.doctor import goal_alignment
from CoAgent.runtime import mosim_agent_runtime as runtime


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def make_task(tmp_root: Path, *, task_id: str, objective: str, metadata: dict[str, object], state: str) -> tuple[Path, Path]:
    db = tmp_root / f"{task_id}.sqlite3"
    events = tmp_root / f"{task_id}.events.jsonl"
    runtime.create_task(
        ns(
            db=db,
            events=events,
            task_id=task_id,
            objective=objective,
            role="Verification",
            read_scope=["CoAgent"],
            write_scope=["Results/agent_packets"],
            acceptance="goal alignment validator returns expected decision",
            stop_condition="validator returns expected decision",
            depends_on=[],
            metadata=json.dumps(metadata, ensure_ascii=False, sort_keys=True),
            priority=30,
            actor="MainAgent",
        )
    )
    event_map = {
        "done": ("task_completed", "goal alignment task completed"),
        "done_with_concerns": ("task_completed", "goal alignment task requires review"),
        "blocked": ("task_blocked", "goal alignment task blocked"),
    }
    event_type, summary = event_map[state]
    runtime.update_task(
        ns(db=db, events=events, task_id=task_id, actor="Verification", claim_token="", summary=summary, data=""),
        state=state,
        event_type=event_type,
    )
    return db, events


def build_report(db: Path, events: Path, task_id: str) -> dict[str, object]:
    task_packet = runtime.export_task_packet(ns(db=db, events=events, task_id=task_id))
    result_packet = runtime.export_result_packet(ns(db=db, events=events, task_id=task_id))
    context = context_pack.build_context_pack(
        ns(
            db=db,
            events=events,
            task_id=task_id,
            output=None,
            event_limit=8,
            knowledge_query=[],
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
    return goal_alignment.validate_bundle(task_packet, context["text"], result_packet)


def main() -> int:
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        good_metadata = {
            "task_class": "long_running_task",
            "canonical_task_goal": "Implement and validate the CoAgent goal alignment checker",
            "conversation_objective": "Run the goal alignment checker and return a reviewable result",
            "definition_of_done": "validator accepts aligned task context and result packets",
            "required_evidence": ["goal alignment validator report"],
            "non_goals": ["create a task shell as success", "mutate Codex goals"],
            "evidence": ["goal alignment smoke report"],
            "next_recommended_action": "review validator output",
            "review_status": "accepted",
            "acceptance_state": "met",
        }
        db, events = make_task(
            tmp_root,
            task_id="goal_alignment_good",
            objective="Implement and validate the CoAgent goal alignment checker",
            metadata=good_metadata,
            state="done",
        )
        good_report = build_report(db, events, "goal_alignment_good")
        assert good_report["ok"], good_report

        weak_metadata = dict(good_metadata)
        weak_metadata["canonical_task_goal"] = "Create a 10 hour architecture task"
        weak_metadata["conversation_objective"] = "Open a conversation"
        db, events = make_task(
            tmp_root,
            task_id="goal_alignment_weak_goal",
            objective="Implement and validate the CoAgent goal alignment checker",
            metadata=weak_metadata,
            state="done",
        )
        weak_report = build_report(db, events, "goal_alignment_weak_goal")
        assert not weak_report["ok"], weak_report
        assert "GOAL_FORBIDDEN_SUBSTITUTION" in weak_report["finding_codes"], weak_report
        assert "GOAL_OBJECTIVE_AS_ACTIVITY" in weak_report["finding_codes"], weak_report

        task_packet = runtime.export_task_packet(ns(db=db, events=events, task_id="goal_alignment_weak_goal"))
        context = context_pack.build_context_pack(
            ns(
                db=db,
                events=events,
                task_id="goal_alignment_weak_goal",
                output=None,
                event_limit=8,
                knowledge_query=[],
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
        result_packet = runtime.export_result_packet(ns(db=db, events=events, task_id="goal_alignment_weak_goal"))
        result_packet["canonical_task_goal"] = "Different goal"
        mutation_report = goal_alignment.validate_bundle(task_packet, context["text"], result_packet)
        assert not mutation_report["ok"], mutation_report
        assert "GOAL_RESULT_MUTATION" in mutation_report["finding_codes"], mutation_report

    print("goal_alignment_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
