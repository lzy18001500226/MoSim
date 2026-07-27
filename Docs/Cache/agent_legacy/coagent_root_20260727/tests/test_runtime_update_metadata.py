#!/usr/bin/env python3
"""Smoke test for safe runtime metadata patching."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.runtime import mosim_agent_runtime as runtime


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def main() -> int:
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        db = Path(tmp) / "tasks.sqlite3"
        events = Path(tmp) / "events.jsonl"
        task_id = "runtime_update_metadata_smoke"
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                objective="Patch runtime metadata for result packet evidence",
                role="VerificationAgent",
                read_scope=["CoAgent/runtime"],
                write_scope=["Results/tmp"],
                acceptance="metadata patch is reflected in result packet",
                stop_condition="test passes",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "task_class": "clear_task",
                        "canonical_task_goal": "Patch runtime metadata for result packet evidence",
                        "conversation_objective": "Update metadata and export result packet",
                        "required_evidence": ["metadata patch output"],
                        "non_goals": ["manual sqlite edits"],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=50,
                actor="MainAgent",
            )
        )
        claimed = runtime.claim_task(ns(db=db, events=events, task_id=task_id, owner="VerificationAgent", force=False))
        token = claimed["claim_token"]
        shown_after_claim = runtime.show_task(ns(db=db, events=events, task_id=task_id))
        claim_events = [event for event in shown_after_claim["events"] if event["event_type"] == "task_claimed"]
        assert claim_events, shown_after_claim
        assert "claim_token" not in claim_events[-1]["data"], claim_events[-1]
        assert claim_events[-1]["data"]["claim_token_issued"] is True

        try:
            runtime.update_metadata(
                ns(
                    db=db,
                    events=events,
                    task_id=task_id,
                    actor="VerificationAgent",
                    claim_token="bad-token",
                    summary="bad metadata patch",
                    metadata='{"evidence":["should not apply"]}',
                )
            )
        except SystemExit as exc:
            assert "claim token" in str(exc)
        else:
            raise AssertionError("metadata update accepted a bad claim token")

        patched = runtime.update_metadata(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                actor="VerificationAgent",
                claim_token=token,
                summary="metadata patch applied",
                metadata=json.dumps(
                    {
                        "commands_run": ["python3 CoAgent/tests/test_runtime_update_metadata.py"],
                        "evidence": ["CoAgent/tests/test_runtime_update_metadata.py"],
                        "next_recommended_action": "review metadata patch smoke",
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            )
        )
        assert patched["metadata"]["evidence"] == ["CoAgent/tests/test_runtime_update_metadata.py"]

        result = runtime.export_result_packet(ns(db=db, events=events, task_id=task_id))
        assert result["evidence"] == ["CoAgent/tests/test_runtime_update_metadata.py"]
        assert result["commands_run"] == ["python3 CoAgent/tests/test_runtime_update_metadata.py"]
        assert result["next_recommended_action"] == "review metadata patch smoke"

        cli_show = subprocess.run(
            [
                sys.executable,
                "CoAgent/runtime/mosim_agent_runtime.py",
                "show",
                "--db",
                str(db),
                "--events",
                str(events),
                "--task-id",
                task_id,
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
            check=False,
        )
        assert cli_show.returncode == 0, cli_show.stderr
        cli_payload = json.loads(cli_show.stdout)
        assert cli_payload["claim_token"] == "<redacted>", cli_payload

        cli_claim = subprocess.run(
            [
                sys.executable,
                "CoAgent/runtime/mosim_agent_runtime.py",
                "claim",
                "--db",
                str(db),
                "--events",
                str(events),
                "--task-id",
                task_id,
                "--owner",
                "VerificationAgent",
                "--force",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
            check=False,
        )
        assert cli_claim.returncode == 0, cli_claim.stderr
        claim_payload = json.loads(cli_claim.stdout)
        assert claim_payload["claim_token"] == "<redacted>", claim_payload

    print("runtime_update_metadata_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
