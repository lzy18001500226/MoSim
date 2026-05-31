#!/usr/bin/env python3
"""Smoke tests for CoAgent result packet router."""

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


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def create_runtime_task(db: Path, events: Path, task_id: str) -> None:
    runtime.create_task(
        ns(
            db=db,
            events=events,
            task_id=task_id,
            objective=f"Smoke test result router {task_id}",
            role="ProjectOwner",
            read_scope=["CoAgent/result_router"],
            write_scope=["Results/tmp"],
            acceptance="result router imports packet",
            stop_condition="done",
            depends_on=[],
            metadata="",
            priority=100,
            actor="ProjectOwner",
        )
    )


def create_runtime_task_with_metadata(db: Path, events: Path, task_id: str, metadata: dict) -> None:
    runtime.create_task(
        ns(
            db=db,
            events=events,
            task_id=task_id,
            objective=f"Smoke test result router {task_id}",
            role="ProjectOwner",
            read_scope=["CoAgent/result_router"],
            write_scope=["Results/tmp"],
            acceptance="result router imports packet",
            stop_condition="done",
            depends_on=[],
            metadata=json.dumps(metadata, ensure_ascii=False, sort_keys=True),
            priority=100,
            actor="ProjectOwner",
        )
    )


def main() -> int:
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        db = tmp_root / "tasks.sqlite3"
        events = tmp_root / "events.jsonl"

        text_task = "result_router_text_smoke"
        create_runtime_task(db, events, text_task)
        text_packet = tmp_root / f"{text_task}.txt"
        text_packet.write_text(
            "\n".join(
                [
                    "[MoSim Result Packet]",
                    f"task_id: {text_task}",
                    "status: done",
                    "summary: text packet imported",
                    "owner: ProjectOwner",
                    "role: ProjectOwner",
                    "read_scope: []",
                    "write_scope: []",
                    "evidence: [\"test_result_router.py\"]",
                    "next_recommended_action: none",
                    "events: []",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        text_imported = result_router.import_packet(
            ns(db=db, events=events, packet=text_packet, claim_token="", archive=True, archive_invalid=True)
        )
        assert text_imported["ok"], text_imported
        assert text_imported["runtime_state"]["state"] == "done"
        assert text_imported["review"]["status"] == "accepted"
        assert text_imported["review_path"].startswith("Results/agent_packets/reviews/")
        assert text_imported["archive"]["archive_path"].startswith("Results/agent_packets/archive/")
        assert text_imported["summary_path"].startswith("Results/agent_packets/summaries/")

        json_task = "result_router_json_smoke"
        create_runtime_task(db, events, json_task)
        json_packet = tmp_root / f"{json_task}.json"
        json_packet.write_text(
            json.dumps(
                {
                    "task_id": json_task,
                    "status": "blocked",
                    "summary": "json packet blocked",
                    "owner": "ProjectOwner",
                    "role": "ProjectOwner",
                    "read_scope": [],
                    "write_scope": [],
                    "blockers": ["json smoke blocker"],
                    "next_recommended_action": "inspect blocker",
                    "events": [],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        json_imported = result_router.import_packet(
            ns(
                db=db,
                events=events,
                packet=json_packet,
                claim_token="",
                archive=True,
                archive_invalid=True,
                notify_weixin=True,
                send_weixin=False,
                weixin_project="mosim-result-router-smoke",
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
        assert json_imported["ok"], json_imported
        assert json_imported["runtime_state"]["state"] == "blocked"
        assert json_imported["review"]["status"] == "needs_review"
        assert any(item["field"] == "evidence" for item in json_imported["review"]["findings"])
        assert json_imported["notification"]["enabled"], json_imported
        assert json_imported["notification"]["packet_path"].startswith("Results/agent_packets/notifications/")
        assert json_imported["notification"]["result"]["send_result"]["reason"] == "dry_run"
        assert (ROOT / json_imported["notification"]["packet_path"]).exists()

        invalid_packet = tmp_root / "invalid.txt"
        invalid_packet.write_text("status: done\nsummary: missing task id\n", encoding="utf-8")
        invalid = result_router.validate_command(ns(packet=invalid_packet))
        assert not invalid["ok"], invalid
        assert any(item["field"] == "task_id" for item in invalid["validation"]["findings"])
        assert invalid["review"]["status"] == "rejected"
        invalid_import = result_router.import_packet(
            ns(db=db, events=events, packet=invalid_packet, claim_token="", archive=True, archive_invalid=True)
        )
        assert not invalid_import["ok"], invalid_import
        assert invalid_import["archive"]["archive_path"].startswith("Results/agent_packets/archive/invalid/")

        canonical_task = "result_router_canonical_smoke"
        create_runtime_task_with_metadata(
            db,
            events,
            canonical_task,
            {
                "task_class": "long_running_task",
                "project_goal": "CoAgent protocol alignment",
                "canonical_task_goal": "Align result packet canonical state handling",
                "conversation_objective": "Return a canonical completed packet",
                "accountable_owner": "Verification",
                "definition_of_done": "canonical packet imported",
                "appetite": "one smoke test",
                "circuit_breaker": "schema mismatch",
                "checkpoint_plan": "single checkpoint",
                "required_evidence": ["test_result_router.py"],
                "review_gates": ["pytest"],
            },
        )
        task_packet = runtime.export_task_packet(ns(db=db, events=events, task_id=canonical_task))
        assert task_packet["task_class"] == "long_running_task"
        assert task_packet["canonical_task_goal"] == "Align result packet canonical state handling"
        assert task_packet["definition_of_done"] == "canonical packet imported"
        assert task_packet["appetite"] == "one smoke test"

        canonical_packet = tmp_root / f"{canonical_task}.json"
        canonical_packet.write_text(
            json.dumps(
                {
                    "task_id": canonical_task,
                    "status": "completed",
                    "canonical_status": "completed",
                    "task_class": "long_running_task",
                    "canonical_task_goal": "Align result packet canonical state handling",
                    "conversation_objective": "Return a canonical completed packet",
                    "summary": "canonical packet imported",
                    "owner": "Verification",
                    "role": "ProjectOwner",
                    "read_scope": [],
                    "write_scope": [],
                    "files_changed": [],
                    "commands_run": ["pytest CoAgent/tests/test_result_router.py"],
                    "evidence": ["test_result_router.py"],
                    "risks": [],
                    "blockers": [],
                    "review_status": "not_required",
                    "acceptance_state": "met",
                    "continue_or_stop": "stop",
                    "next_recommended_action": "none",
                    "events": [],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        canonical_imported = result_router.import_packet(
            ns(
                db=db,
                events=events,
                packet=canonical_packet,
                claim_token="",
                archive=True,
                archive_invalid=True,
                notify_weixin=True,
                send_weixin=False,
                weixin_project="mosim-result-router-smoke",
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
        assert canonical_imported["ok"], canonical_imported
        assert canonical_imported["runtime_state"]["state"] == "done"
        assert canonical_imported["review"]["canonical_status"] == "completed"
        assert canonical_imported["review"]["status"] == "accepted"
        assert canonical_imported["notification"]["skipped"]
        assert canonical_imported["notification"]["reason"] == "human_review_not_required"

    print("result_router_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
