#!/usr/bin/env python3
"""Smoke test for read-only CoAgent task-health snapshots."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.runtime import mosim_agent_runtime as runtime
from CoAgent.task_health import task_health


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def main() -> int:
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        db = tmp_root / "tasks.sqlite3"
        events = tmp_root / "events.jsonl"
        task_id = "coagent_task_health_smoke"
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                objective="Prove task health snapshot",
                role="VerificationAgent",
                read_scope=["CoAgent/task_health"],
                write_scope=["Results/coagent_status"],
                acceptance="task health snapshot reports stale active task",
                stop_condition="health finding exists",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "department": "VerificationAgent",
                        "checkpoint": "task health smoke",
                        "next_action": "inspect health finding",
                        "review_status": "not_required",
                        "human_needed": "",
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=10,
                actor="MainAgent",
            )
        )
        with runtime.open_db(db) as connection:
            connection.execute(
                "UPDATE tasks SET state = 'running', last_event_at = '2000-01-01T00:00:00+00:00', updated_at = '2000-01-01T00:00:00+00:00' WHERE task_id = ?",
                (task_id,),
            )
            connection.commit()
        output = tmp_root / "task_health.json"
        markdown = tmp_root / "task_health.md"
        result = task_health.run_snapshot(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                state="",
                active_only=True,
                stale_minutes=1,
                staged_file_warning_threshold=1000,
                skip_preflight=True,
                skip_runtime_audit=True,
                output=output,
                markdown_output=markdown,
                include_snapshot=True,
                json=True,
            )
        )
        assert result["ok"], result
        assert output.exists()
        assert markdown.exists()
        snapshot = json.loads(output.read_text(encoding="utf-8"))
        assert snapshot["schema_type"] == "coagent_task_health_snapshot"
        assert snapshot["task_count"] == 1
        item = snapshot["tasks"][0]
        assert item["task_id"] == task_id
        assert item["health_state"] == "continue_with_watch"
        assert item["decision"]["continue_allowed"] is True
        assert item["decision"]["recommended_action"] == "continue_with_watch"
        assert snapshot["decision"]["continue_allowed"] is True
        assert snapshot["continue_allowed"] is True
        assert snapshot["recommended_action"] == "continue_with_watch"
        assert snapshot["watch_task_ids"] == [task_id]
        assert snapshot["decision"]["recommended_action"] == "continue_with_watch"
        assert snapshot["decision"]["watch_task_ids"] == [task_id]
        assert any(finding["reason"] == "stale_active_task" for finding in item["findings"])
        assert "inspect health finding" in markdown.read_text(encoding="utf-8")

        closeout_task_id = "coagent_task_health_closeout_smoke"
        closeout_file = tmp_root / "closeout.review_closeout.json"
        closeout_rel = str(closeout_file.relative_to(ROOT)).replace("\\", "/")
        closeout_file.write_text(
            json.dumps(
                {
                    "schema_type": "coagent_review_closeout",
                    "task_id": closeout_task_id,
                    "decision": "accepted_with_concerns",
                    "reason": "watch the concern",
                    "next_action": "continue with watch",
                    "actor": "MainAgent",
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=closeout_task_id,
                objective="Prove closeout-aware task health",
                role="VerificationAgent",
                read_scope=["CoAgent/task_health"],
                write_scope=["Results/coagent_status"],
                acceptance="task health reports accepted-with-concerns watch",
                stop_condition="health finding exists",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "department": "VerificationAgent",
                        "checkpoint": "closeout health smoke",
                        "next_action": "continue with watch",
                        "review_status": "accepted_with_concerns",
                        "human_needed": "",
                        "review_closeout_path": closeout_rel,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=10,
                actor="MainAgent",
            )
        )
        closeout_output = tmp_root / "task_health_closeout.json"
        closeout_result = task_health.run_snapshot(
            ns(
                db=db,
                events=events,
                task_id=closeout_task_id,
                state="",
                active_only=True,
                stale_minutes=120,
                staged_file_warning_threshold=1000,
                skip_preflight=True,
                skip_runtime_audit=True,
                output=closeout_output,
                markdown_output=tmp_root / "task_health_closeout.md",
                include_snapshot=True,
                json=True,
            )
        )
        assert closeout_result["ok"], closeout_result
        closeout_snapshot = json.loads(closeout_output.read_text(encoding="utf-8"))
        closeout_item = closeout_snapshot["tasks"][0]
        assert closeout_item["health_state"] == "continue_with_watch"
        assert closeout_item["decision"]["continue_allowed"] is True
        assert closeout_item["decision"]["recommended_action"] == "continue_with_watch"
        assert closeout_snapshot["recommended_action"] == "continue_with_watch"
        assert closeout_snapshot["watch_task_ids"] == [closeout_task_id]
        assert closeout_item["review_closeout"]["decision"] == "accepted_with_concerns"
        assert any(finding["reason"] == "accepted_with_concerns_watch" for finding in closeout_item["findings"])

        rework_task_id = "coagent_task_health_rework_smoke"
        rework_file = tmp_root / "rework.review_closeout.json"
        rework_rel = str(rework_file.relative_to(ROOT)).replace("\\", "/")
        rework_file.write_text(
            json.dumps(
                {
                    "schema_type": "coagent_review_closeout",
                    "task_id": rework_task_id,
                    "decision": "needs_rework",
                    "reason": "not accepted",
                    "next_action": "fix the rejected slice",
                    "actor": "MainAgent",
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=rework_task_id,
                objective="Prove rework blocks continuation",
                role="VerificationAgent",
                read_scope=["CoAgent/task_health"],
                write_scope=["Results/coagent_status"],
                acceptance="task health blocks needs_rework decision",
                stop_condition="health state rejects completion",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "department": "VerificationAgent",
                        "checkpoint": "rework health smoke",
                        "next_action": "must rework",
                        "review_status": "needs_rework",
                        "human_needed": "",
                        "review_closeout_path": rework_rel,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=10,
                actor="MainAgent",
            )
        )
        rework_output = tmp_root / "task_health_rework.json"
        rework_result = task_health.run_snapshot(
            ns(
                db=db,
                events=events,
                task_id=rework_task_id,
                state="",
                active_only=True,
                stale_minutes=120,
                staged_file_warning_threshold=1000,
                skip_preflight=True,
                skip_runtime_audit=True,
                output=rework_output,
                markdown_output=tmp_root / "task_health_rework.md",
                include_snapshot=True,
                json=True,
            )
        )
        assert rework_result["ok"], rework_result
        rework_snapshot = json.loads(rework_output.read_text(encoding="utf-8"))
        assert rework_snapshot["decision"]["continue_allowed"] is False
        assert rework_snapshot["continue_allowed"] is False
        assert rework_snapshot["decision"]["recommended_action"] == "rework_or_reject_completion"
        assert rework_snapshot["recommended_action"] == "rework_or_reject_completion"
        assert rework_snapshot["blocking_task_ids"] == [rework_task_id]
        rework_item = rework_snapshot["tasks"][0]
        assert rework_item["health_state"] == "reject_completion"
        assert rework_item["decision"]["continue_allowed"] is False
        assert rework_item["decision"]["stop_reason"] == "review_decision_blocks_progress"
        assert any(finding["reason"] == "review_decision_blocks_progress" for finding in rework_item["findings"])

    print("task_health_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
