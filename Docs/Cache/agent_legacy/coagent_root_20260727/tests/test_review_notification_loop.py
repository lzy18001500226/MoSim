#!/usr/bin/env python3
"""Smoke test for the CoAgent review-notification closed loop."""

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
from CoAgent.runtime import mosim_agent_runtime as runtime


TASK_ID = "coagent_review_notification_smoke"


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def main() -> int:
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        db = tmp_root / "tasks.sqlite3"
        events = tmp_root / "events.jsonl"
        audit = tmp_root / "weixin_audit.jsonl"
        dedupe = tmp_root / "weixin_dedupe.json"

        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=TASK_ID,
                objective="Prove result review can request human action through a gated Weixin notification dry-run",
                role="VerificationAgent",
                read_scope=["CoAgent/result_router", "CoAgent/gateway"],
                write_scope=["Results/agent_packets", "Results/coagent_gateway"],
                acceptance="blocked result imports, review gate flags action, notification packet dry-runs",
                stop_condition="blocked packet is visible in status board and notification audit exists",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "task_class": "long_running_task",
                        "project_goal": "CoAgent transferable multi-conversation architecture",
                        "canonical_task_goal": "Verify human-review notification loop",
                        "conversation_objective": "Return a blocked packet that requires human action",
                        "accountable_owner": "VerificationAgent",
                        "required_evidence": [
                            "review packet",
                            "notification packet",
                            "weixin dry-run audit",
                        ],
                        "review_gates": ["result router", "cc-connect Weixin adapter dry-run"],
                        "human_review_points": ["manual_review_required"],
                        "department": "VerificationAgent",
                        "next_action": "import blocked smoke packet",
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=30,
                actor="MainAgent",
            )
        )

        packet = tmp_root / f"{TASK_ID}.json"
        packet.write_text(
            json.dumps(
                {
                    "task_id": TASK_ID,
                    "status": "blocked",
                    "canonical_status": "blocked",
                    "summary": "review notification smoke blocked on human confirmation",
                    "owner": "VerificationAgent",
                    "role": "VerificationAgent",
                    "read_scope": [],
                    "write_scope": [],
                    "blockers": ["manual confirmation required"],
                    "evidence": ["CoAgent/tests/test_review_notification_loop.py"],
                    "next_recommended_action": "Confirm the dry-run notification packet shape.",
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
                weixin_project="mosim-review-notification-smoke",
                weixin_session="",
                weixin_data_dir=tmp_root / "weixin_data",
                weixin_cc_bin=tmp_root / "missing-cc-connect",
                weixin_config=tmp_root / "weixin_config.toml",
                weixin_audit=audit,
                weixin_dedupe=dedupe,
                weixin_max_chars=1500,
                weixin_timeout=1,
                force_weixin=False,
                omit_weixin_message_in_audit=False,
            )
        )
        assert imported["ok"], imported
        assert imported["runtime_state"]["state"] == "blocked"
        assert imported["review"]["requires_human_review"]
        assert imported["notification"]["enabled"]
        assert imported["notification"]["result"]["send_result"]["reason"] == "dry_run"
        assert imported["notification"]["packet_path"].startswith("Results/agent_packets/notifications/")
        assert (ROOT / imported["review_path"]).exists()
        assert (ROOT / imported["summary_path"]).exists()
        assert (ROOT / imported["notification"]["packet_path"]).exists()
        assert audit.exists()

        notification_packet = json.loads((ROOT / imported["notification"]["packet_path"]).read_text(encoding="utf-8"))
        assert notification_packet["class"] == "incident_required"
        assert notification_packet["task_id"] == TASK_ID
        assert "Confirm the dry-run notification packet shape." in notification_packet["human_action_required"]

        board = runtime.status_board(ns(db=db, events=events, state="blocked", active_only=False))
        assert board["count"] == 1
        assert board["tasks"][0]["task_id"] == TASK_ID
        assert board["tasks"][0]["state"] == "blocked"
        assert board["tasks"][0]["human_needed"] == "yes"
        assert board["tasks"][0]["review_status"] == "needs_review"
        assert board["tasks"][0]["next_action"] == "Confirm the dry-run notification packet shape."

    print("review_notification_loop_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
