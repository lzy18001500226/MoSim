#!/usr/bin/env python3
"""Smoke test for blocker-notification packet generation."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.blocker_packet import blocker_packet
from CoAgent.gateway import cc_connect_weixin
from CoAgent.runtime import mosim_agent_runtime as runtime


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def main() -> int:
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        db = tmp_root / "tasks.sqlite3"
        events = tmp_root / "events.jsonl"
        task_id = "coagent_blocker_packet_smoke"
        resume = tmp_root / "resume.md"
        resume.write_text("# resume\n", encoding="utf-8")
        resume_rel = str(resume.relative_to(ROOT)).replace("\\", "/")
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                objective="Prove blocker packet generation",
                role="VerificationAgent",
                read_scope=["CoAgent/blocker_packet"],
                write_scope=["Results/agent_packets/blockers"],
                acceptance="task health blocker produces notification packet",
                stop_condition="packet dry-runs through gateway adapter",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "checkpoint": "blocker packet smoke",
                        "next_action": "ask the user to review this smoke blocker",
                        "review_status": "needs_review",
                        "human_needed": "yes",
                        "resume_bundle_markdown": resume_rel,
                        "status_export_path": "Results/tmp/status.json",
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=10,
                actor="MainAgent",
            )
        )
        output = tmp_root / "blocker.json"
        markdown = tmp_root / "blocker.md"
        result = blocker_packet.run_packet(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                stale_minutes=120,
                staged_file_warning_threshold=1000,
                skip_preflight=True,
                skip_runtime_audit=True,
                output=output,
                markdown_output=markdown,
                write_when_clear=False,
                include_snapshot=True,
                include_packet=True,
                json=True,
            )
        )
        assert result["ok"], result
        assert result["needed"] is True, result
        assert output.exists()
        assert markdown.exists()
        packet = json.loads(output.read_text(encoding="utf-8"))
        assert packet["template_type"] == "blocker_notification"
        assert packet["task_id"] == task_id
        assert packet["class"] in {"approval_required", "manual_review_required"}
        assert packet["safe_to_continue_without_user"] is False
        assert packet["task_health_decision"]["required_human_action"] is True
        assert "ask" in packet["human_action_required"]
        assert result["metadata_recorded"] is False

        plan = cc_connect_weixin.build_plan(output)
        assert plan.ok, plan
        assert plan.packet_type == "blocker_notification"
        assert task_id in plan.message

        clear_task = "coagent_blocker_packet_clear_smoke"
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=clear_task,
                objective="Prove no blocker packet when clear",
                role="VerificationAgent",
                read_scope=["CoAgent/blocker_packet"],
                write_scope=["Results/agent_packets/blockers"],
                acceptance="clear task does not write packet",
                stop_condition="needed false",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "checkpoint": "clear blocker smoke",
                        "next_action": "continue",
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
        clear_output = tmp_root / "clear_blocker.json"
        clear = blocker_packet.run_packet(
            ns(
                db=db,
                events=events,
                task_id=clear_task,
                stale_minutes=120,
                staged_file_warning_threshold=1000,
                skip_preflight=True,
                skip_runtime_audit=True,
                output=clear_output,
                markdown_output=None,
                write_when_clear=False,
                include_snapshot=True,
                include_packet=True,
                json=True,
            )
        )
        assert clear["ok"], clear
        assert clear["needed"] is False, clear
        assert not clear_output.exists()

        claimed = runtime.claim_task(ns(db=db, events=events, task_id=task_id, owner="MainAgent", force=True))
        recorded_output = tmp_root / "recorded_blocker.json"
        recorded_markdown = tmp_root / "recorded_blocker.md"
        recorded = blocker_packet.run_packet(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                stale_minutes=120,
                staged_file_warning_threshold=1000,
                skip_preflight=True,
                skip_runtime_audit=True,
                output=recorded_output,
                markdown_output=recorded_markdown,
                write_when_clear=False,
                record_metadata=True,
                claim_token=claimed["claim_token"],
                actor="MainAgent",
                summary="record blocker packet smoke metadata",
                include_snapshot=True,
                include_packet=False,
                json=True,
            )
        )
        assert recorded["ok"], recorded
        assert recorded["needed"] is True, recorded
        assert recorded["metadata_recorded"] is True, recorded
        updated = runtime.show_task(ns(db=db, events=events, task_id=task_id))
        assert updated["metadata"]["blocker_packet_needed"] is True
        assert updated["metadata"]["blocker_packet_path"].endswith("recorded_blocker.json")
        assert updated["metadata"]["blocker_packet_markdown"].endswith("recorded_blocker.md")
        assert updated["metadata"]["blocker_packet_decision"]["continue_allowed"] is False

    print("blocker_packet_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
