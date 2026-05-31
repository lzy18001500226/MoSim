#!/usr/bin/env python3
"""Smoke test for the read-only CoAgent human-review queue."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.result_router import result_router
from CoAgent.review_queue import review_queue
from CoAgent.runtime import mosim_agent_runtime as runtime


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def create_task(db: Path, events: Path, task_id: str) -> None:
    runtime.create_task(
        ns(
            db=db,
            events=events,
            task_id=task_id,
            objective=f"Review queue smoke {task_id}",
            role="VerificationAgent",
            read_scope=["CoAgent/review_queue"],
            write_scope=["Results/agent_packets"],
            acceptance="review queue records blocked task",
            stop_condition="queue item exists",
            depends_on=[],
            metadata="{}",
            priority=10,
            actor="MainAgent",
        )
    )


def create_cancelled_parent_with_blocked_child(db: Path, events: Path) -> None:
    parent_id = "coagent_review_queue_cancelled_parent"
    child_id = "coagent_review_queue_suppressed_child"
    runtime.create_task(
        ns(
            db=db,
            events=events,
            task_id=parent_id,
            objective="Cancelled parent for review queue suppression",
            role="DispatchAgent",
            read_scope=[],
            write_scope=[],
            acceptance="cancelled parent exists",
            stop_condition="cancelled",
            depends_on=[],
            metadata="{}",
            priority=20,
            actor="MainAgent",
        )
    )
    runtime.update_task(
        ns(db=db, events=events, task_id=parent_id, actor="MainAgent", claim_token="", summary="cancel parent", data="{}"),
        state="cancelled",
        event_type="task_cancelled",
    )
    runtime.create_task(
        ns(
            db=db,
            events=events,
            task_id=child_id,
            objective="Suppressed blocked child",
            role="RuntimePlatformAgent",
            read_scope=[],
            write_scope=[],
            acceptance="child blocked",
            stop_condition="blocked",
            depends_on=[],
            metadata=json.dumps({"parent_task_id": parent_id, "human_needed": "yes"}, sort_keys=True),
            priority=20,
            actor="MainAgent",
        )
    )
    runtime.update_task(
        ns(db=db, events=events, task_id=child_id, actor="MainAgent", claim_token="", summary="block child", data="{}"),
        state="blocked",
        event_type="task_blocked",
    )


def main() -> int:
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        db = tmp_root / "tasks.sqlite3"
        events = tmp_root / "events.jsonl"
        task_id = "coagent_review_queue_smoke"
        create_task(db, events, task_id)
        create_cancelled_parent_with_blocked_child(db, events)

        packet = tmp_root / f"{task_id}.json"
        packet.write_text(
            json.dumps(
                {
                    "task_id": task_id,
                    "status": "blocked",
                    "canonical_status": "blocked",
                    "summary": "review queue smoke blocked",
                    "owner": "VerificationAgent",
                    "role": "VerificationAgent",
                    "read_scope": [],
                    "write_scope": [],
                    "blockers": ["needs human review"],
                    "evidence": ["CoAgent/tests/test_review_queue.py"],
                    "next_recommended_action": "Inspect review queue item.",
                    "events": [],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        imported = result_router.import_packet(
            ns(
                db=db,
                events=events,
                packet=packet,
                claim_token="",
                archive=True,
                archive_invalid=True,
                notify_weixin=True,
                send_weixin=False,
                weixin_project="mosim-review-queue-smoke",
                weixin_session="",
                weixin_data_dir=tmp_root / "weixin_data",
                weixin_cc_bin=tmp_root / "missing-cc-connect",
                weixin_config=tmp_root / "weixin_config.toml",
                weixin_audit=tmp_root / "weixin_audit.jsonl",
                weixin_dedupe=tmp_root / "weixin_dedupe.json",
                weixin_max_chars=1500,
                weixin_timeout=1,
                force_weixin=False,
                omit_weixin_message_in_audit=False,
            )
        )
        assert imported["ok"], imported

        queue = review_queue.build_queue(ns(db=db, include_terminal=False, include_superseded=False, json=True))
        assert queue["count"] == 1, queue
        assert queue["suppressed_count"] == 1, queue
        item = queue["items"][0]
        assert item["task_id"] == task_id
        assert item["state"] == "blocked"
        assert item["human_needed"] == "yes"
        assert item["review_status"] == "needs_review"
        assert item["next_action"] == "Inspect review queue item."
        assert item["summary_path"].startswith("Results/agent_packets/summaries/")
        assert item["review_path"].startswith("Results/agent_packets/reviews/")
        assert item["notification_packet_path"].startswith("Results/agent_packets/notifications/")
        assert "human_needed=yes" in item["reasons"]

        with_superseded = review_queue.build_queue(ns(db=db, include_terminal=False, include_superseded=True, json=True))
        assert with_superseded["count"] == 2, with_superseded

        closeout = review_queue.closeout_review(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                decision="accepted",
                reason="smoke accepted",
                next_action="none",
                evidence=["CoAgent/tests/test_review_queue.py"],
                actor="MainAgent",
                claim_token="",
                json=True,
            )
        )
        assert closeout["ok"], closeout
        assert closeout["human_needed"] == ""
        closed_queue = review_queue.build_queue(ns(db=db, include_terminal=False, include_superseded=False, json=True))
        assert closed_queue["count"] == 0, closed_queue

    print("review_queue_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
