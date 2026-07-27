#!/usr/bin/env python3
"""Smoke test runtime DB/JSONL event-stream audit."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.runtime import mosim_agent_runtime as runtime


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def create_smoke_task(db: Path, events: Path) -> str:
    task_id = "runtime_event_audit_smoke"
    created = runtime.create_task(
        ns(
            db=db,
            events=events,
            task_id=task_id,
            objective="Audit runtime event stream",
            role="RuntimePlatformAgent",
            read_scope=["CoAgent/runtime"],
            write_scope=["Results/tmp"],
            acceptance="event audit passes",
            stop_condition="audit done",
            depends_on=[],
            metadata=json.dumps({"task_class": "clear_task"}, sort_keys=True),
            priority=50,
            actor="RuntimePlatformAgent",
        )
    )
    runtime.update_task(
        ns(
            db=db,
            events=events,
            task_id=created["task_id"],
            actor="RuntimePlatformAgent",
            claim_token="",
            summary="audit checkpoint",
            data="",
        ),
        state="running",
        event_type="checkpoint",
    )
    return task_id


def main() -> int:
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        root = Path(tmp)
        db = root / "tasks.sqlite3"
        events = root / "events.jsonl"
        task_id = create_smoke_task(db, events)
        audit = runtime.audit_event_stream(ns(db=db, events=events))
        assert audit["ok"], audit
        assert audit["task_count"] == 1, audit
        assert audit["db_event_count"] == 2, audit
        assert audit["jsonl_event_count"] == 2, audit

        events.write_text(events.read_text(encoding="utf-8") + "{bad json\n", encoding="utf-8")
        broken = runtime.audit_event_stream(ns(db=db, events=events))
        assert not broken["ok"], broken
        assert broken["invalid_jsonl_count"] == 1, broken
        assert any(item["reason"] == "invalid_jsonl_event" for item in broken["findings"]), broken

        clean_events = root / "clean_events.jsonl"
        create_smoke_task(root / "other.sqlite3", clean_events)
        with sqlite3.connect(root / "other.sqlite3") as connection:
            connection.execute("UPDATE tasks SET last_event_at = '2000-01-01T00:00:00+00:00' WHERE task_id = ?", (task_id,))
            connection.commit()
        drift = runtime.audit_event_stream(ns(db=root / "other.sqlite3", events=clean_events))
        assert drift["ok"], drift
        assert drift["warning_count"] >= 1, drift
        assert any(item["reason"] == "last_event_at_mismatch" for item in drift["findings"]), drift

        sensitive_db = root / "sensitive.sqlite3"
        sensitive_events = root / "sensitive_events.jsonl"
        create_smoke_task(sensitive_db, sensitive_events)
        with sqlite3.connect(sensitive_db) as connection:
            row = connection.execute("SELECT event_id, data_json FROM events WHERE event_type = 'checkpoint' LIMIT 1").fetchone()
            data = json.loads(row[1])
            data["claim_token"] = "claim_should_not_persist"
            connection.execute(
                "UPDATE events SET data_json = ? WHERE event_id = ?",
                (json.dumps(data, sort_keys=True), row[0]),
            )
            connection.commit()
        events_payload = [
            json.loads(line)
            for line in sensitive_events.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        events_payload[-1]["data"]["claim_token"] = "claim_should_not_persist"
        sensitive_events.write_text("\n".join(json.dumps(item, sort_keys=True) for item in events_payload) + "\n", encoding="utf-8")
        sensitive = runtime.audit_event_stream(ns(db=sensitive_db, events=sensitive_events))
        assert not sensitive["ok"], sensitive
        assert sensitive["sensitive_db_event_count"] == 1, sensitive
        assert sensitive["sensitive_jsonl_event_count"] == 1, sensitive
        dry = runtime.scrub_sensitive_events(ns(db=sensitive_db, events=sensitive_events, dry_run=True))
        assert dry["db_scrubbed_count"] == 1, dry
        assert dry["jsonl_scrubbed_count"] == 1, dry
        applied = runtime.scrub_sensitive_events(ns(db=sensitive_db, events=sensitive_events, dry_run=False))
        assert applied["db_scrubbed_count"] == 1, applied
        assert applied["jsonl_scrubbed_count"] == 1, applied
        cleaned = runtime.audit_event_stream(ns(db=sensitive_db, events=sensitive_events))
        assert cleaned["ok"], cleaned
        assert cleaned["sensitive_db_event_count"] == 0, cleaned
        assert cleaned["sensitive_jsonl_event_count"] == 0, cleaned

    print("runtime_event_audit_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
