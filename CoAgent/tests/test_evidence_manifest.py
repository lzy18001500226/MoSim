#!/usr/bin/env python3
"""Smoke test CoAgent evidence manifest generation."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.evidence import evidence_manifest
from CoAgent.runtime import mosim_agent_runtime as runtime


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def main() -> int:
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        db = tmp_root / "tasks.sqlite3"
        events = tmp_root / "events.jsonl"
        task_id = "coagent_evidence_manifest_smoke"
        evidence_file = tmp_root / "evidence.txt"
        evidence_file.write_text("evidence", encoding="utf-8")
        rel_evidence = str(evidence_file.relative_to(ROOT)).replace("\\", "/")
        review_package_file = tmp_root / "sample.review_package.json"
        review_package_file.write_text("{}", encoding="utf-8")
        rel_review_package = str(review_package_file.relative_to(ROOT)).replace("\\", "/")
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                objective="Prove evidence manifest",
                role="VerificationAgent",
                read_scope=["CoAgent/evidence"],
                write_scope=["Results/coagent_status"],
                acceptance="manifest indexes known evidence",
                stop_condition="manifest exists",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "checkpoint": "evidence manifest smoke",
                        "next_action": "inspect manifest",
                        "evidence": [rel_evidence],
                        "review_package_path": rel_review_package,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=10,
                actor="MainAgent",
            )
        )
        output = tmp_root / "manifest.json"
        markdown = tmp_root / "manifest.md"
        result = evidence_manifest.run_manifest(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                output=output,
                markdown_output=markdown,
                include_manifest=True,
                json=True,
            )
        )
        assert result["ok"], result
        assert output.exists()
        assert markdown.exists()
        manifest = json.loads(output.read_text(encoding="utf-8"))
        assert manifest["schema_type"] == "coagent_evidence_manifest"
        assert manifest["task_id"] == task_id
        assert manifest["task_last_event_at"]
        assert manifest["evidence_count"] >= 1
        assert "stale_count" in manifest
        assert "unknown_freshness_count" in manifest
        assert any(item["path"] == rel_evidence for item in manifest["items"])
        assert any(item["path"] == rel_review_package and item["kind"] == "review_package" for item in manifest["items"])
        assert "evidence manifest smoke" in markdown.read_text(encoding="utf-8")

        stale_task_id = "coagent_evidence_manifest_stale_smoke"
        stale_file = tmp_root / "stale_status.json"
        stale_file.write_text("{}", encoding="utf-8")
        stale_rel = str(stale_file.relative_to(ROOT)).replace("\\", "/")
        old_timestamp = datetime(2000, 1, 1, tzinfo=timezone.utc).timestamp()
        os.utime(stale_file, (old_timestamp, old_timestamp))
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=stale_task_id,
                objective="Prove stale evidence manifest",
                role="VerificationAgent",
                read_scope=["CoAgent/evidence"],
                write_scope=["Results/coagent_status"],
                acceptance="manifest reports stale evidence",
                stop_condition="stale finding exists",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "checkpoint": "stale evidence manifest smoke",
                        "next_action": "refresh stale artifact",
                        "status_export_path": stale_rel,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=10,
                actor="MainAgent",
            )
        )
        stale_result = evidence_manifest.run_manifest(
            ns(
                db=db,
                events=events,
                task_id=stale_task_id,
                output=tmp_root / "stale_manifest.json",
                markdown_output=tmp_root / "stale_manifest.md",
                include_manifest=True,
                json=True,
            )
        )
        assert stale_result["ok"], stale_result
        stale_manifest = json.loads((tmp_root / "stale_manifest.json").read_text(encoding="utf-8"))
        assert stale_manifest["stale_count"] >= 1, stale_manifest
        assert stale_manifest["critical_stale_count"] >= 1, stale_manifest
        assert stale_manifest["archival_stale_count"] >= 0, stale_manifest
        assert stale_manifest["freshness_status"] == "critical_stale_warning", stale_manifest
        assert stale_manifest["stale_refresh_recommended"] is True, stale_manifest
        assert any("coagent_doctor.py --mode quick" in command for command in stale_manifest["refresh_commands"])
        assert any("coagent_doctor.py --mode full" in command for command in stale_manifest["refresh_commands"])
        assert any("status_export.py" in command for command in stale_manifest["refresh_commands"])
        assert any("evidence_manifest.py" in command for command in stale_manifest["refresh_commands"])
        stale_item = next(item for item in stale_manifest["items"] if item["path"] == stale_rel)
        assert stale_item["fresh_after_task_last_event"] is False, stale_item
        assert stale_item["kind"] == "status_export", stale_item
        assert stale_item["freshness_role"] == "recovery_current", stale_item
        stale_markdown = (tmp_root / "stale_manifest.md").read_text(encoding="utf-8")
        assert "## Refresh Commands" in stale_markdown
        assert "## Critical Stale Recovery Artifacts" in stale_markdown
        assert "status_export.py" in stale_markdown

        archival_task_id = "coagent_evidence_manifest_archival_stale_smoke"
        archival_file = tmp_root / "archival_status.json"
        archival_file.write_text("{}", encoding="utf-8")
        old_timestamp = datetime(2000, 1, 2, tzinfo=timezone.utc).timestamp()
        os.utime(archival_file, (old_timestamp, old_timestamp))
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=archival_task_id,
                objective="Prove archival stale evidence does not require refresh",
                role="VerificationAgent",
                read_scope=["CoAgent/evidence"],
                write_scope=["Results/coagent_status"],
                acceptance="manifest reports archival stale without refresh recommendation",
                stop_condition="archival stale finding exists",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "checkpoint": "archival stale smoke",
                        "next_action": "continue",
                        "evidence": [str(archival_file.relative_to(ROOT)).replace("\\", "/")],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=10,
                actor="MainAgent",
            )
        )
        archival_result = evidence_manifest.run_manifest(
            ns(
                db=db,
                events=events,
                task_id=archival_task_id,
                output=tmp_root / "archival_manifest.json",
                markdown_output=tmp_root / "archival_manifest.md",
                include_manifest=True,
                json=True,
            )
        )
        assert archival_result["ok"], archival_result
        archival_manifest = json.loads((tmp_root / "archival_manifest.json").read_text(encoding="utf-8"))
        assert archival_manifest["freshness_status"] == "archival_stale", archival_manifest
        assert archival_manifest["stale_refresh_recommended"] is False, archival_manifest
        assert archival_manifest["critical_stale_count"] == 0, archival_manifest
        assert archival_manifest["archival_stale_count"] >= 1, archival_manifest
        assert archival_manifest["refresh_commands"] == [], archival_manifest
        archival_markdown = (tmp_root / "archival_manifest.md").read_text(encoding="utf-8")
        assert "## Archival Or Supporting Stale Artifacts" in archival_markdown

        downstream_task_id = "coagent_evidence_manifest_downstream_review_smoke"
        downstream_file = tmp_root / "old_review_package.json"
        downstream_file.write_text("{}", encoding="utf-8")
        old_timestamp = datetime(2000, 1, 3, tzinfo=timezone.utc).timestamp()
        os.utime(downstream_file, (old_timestamp, old_timestamp))
        downstream_rel = str(downstream_file.relative_to(ROOT)).replace("\\", "/")
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=downstream_task_id,
                objective="Prove downstream review package does not create freshness loop",
                role="VerificationAgent",
                read_scope=["CoAgent/evidence"],
                write_scope=["Results/coagent_status"],
                acceptance="manifest excludes downstream package from stale counts",
                stop_condition="downstream package marked freshness not applicable",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "checkpoint": "downstream review package smoke",
                        "next_action": "continue",
                        "review_package_path": downstream_rel,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=10,
                actor="MainAgent",
            )
        )
        downstream_result = evidence_manifest.run_manifest(
            ns(
                db=db,
                events=events,
                task_id=downstream_task_id,
                output=tmp_root / "downstream_manifest.json",
                markdown_output=tmp_root / "downstream_manifest.md",
                include_manifest=True,
                json=True,
            )
        )
        assert downstream_result["ok"], downstream_result
        downstream_manifest = json.loads((tmp_root / "downstream_manifest.json").read_text(encoding="utf-8"))
        downstream_item = next(item for item in downstream_manifest["items"] if item["path"] == downstream_rel)
        assert downstream_item["kind"] == "review_package", downstream_item
        assert downstream_item["freshness_role"] == "downstream_package", downstream_item
        assert downstream_item["fresh_after_task_last_event"] is None, downstream_item
        assert all(item["path"] != downstream_rel for item in downstream_manifest["stale"]), downstream_manifest
        assert downstream_manifest["critical_stale_count"] == 0, downstream_manifest
        assert downstream_manifest["stale_refresh_recommended"] is False, downstream_manifest

    print("evidence_manifest_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
