#!/usr/bin/env python3
"""Smoke test CoAgent human-review package generation."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.review_package import review_package
from CoAgent.runtime import mosim_agent_runtime as runtime


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def main() -> int:
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        db = tmp_root / "tasks.sqlite3"
        events = tmp_root / "events.jsonl"
        task_id = "coagent_review_package_smoke"
        status_path = tmp_root / "status.json"
        status_path.write_text(
            json.dumps(
                {
                    "task_id": task_id,
                    "state": "running",
                    "checkpoint": "review package smoke",
                    "next_action": "inspect review package",
                },
                ensure_ascii=False,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        doctor_path = tmp_root / "doctor.json"
        doctor_path.write_text(
            json.dumps({"overallStatus": "ok", "counts": {"ok": 1, "warning": 0, "fail": 0}}, sort_keys=True),
            encoding="utf-8",
        )
        evidence_path = tmp_root / "evidence_manifest.json"
        evidence_path.write_text(
            json.dumps(
                {
                    "schema_type": "coagent_evidence_manifest",
                    "task_id": task_id,
                    "ok": True,
                    "evidence_count": 1,
                    "missing_count": 0,
                    "stale_count": 2,
                    "critical_stale_count": 1,
                    "archival_stale_count": 1,
                    "freshness_status": "critical_stale_warning",
                    "stale_refresh_recommended": True,
                    "refresh_commands": [
                        "python3 CoAgent/doctor/coagent_doctor.py --mode quick --json --output Results/coagent_doctor/latest_gateway_quick.json",
                        "python3 CoAgent/status_export/status_export.py --task-id coagent_review_package_smoke --output Results/coagent_status/coagent_review_package_smoke.status.json",
                        "python3 CoAgent/evidence/evidence_manifest.py --task-id coagent_review_package_smoke --output Results/coagent_status/coagent_review_package_smoke.evidence_manifest.json",
                    ],
                    "by_kind": {"status_export": 1},
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
                task_id=task_id,
                objective="Prove review package",
                role="MainAgent",
                read_scope=["CoAgent/review_package"],
                write_scope=["Results/coagent_status"],
                acceptance="review package indexes review artifacts",
                stop_condition="package exists",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "checkpoint": "review package smoke",
                        "next_action": "inspect review package",
                        "review_status": "not_required",
                        "human_needed": "",
                        "status_export_path": str(status_path.relative_to(ROOT)).replace("\\", "/"),
                        "doctor_full_path": str(doctor_path.relative_to(ROOT)).replace("\\", "/"),
                        "evidence_manifest_path": str(evidence_path.relative_to(ROOT)).replace("\\", "/"),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=10,
                actor="MainAgent",
            )
        )
        output = tmp_root / "review_package.json"
        markdown = tmp_root / "review_package.md"
        result = review_package.run_package(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                output=output,
                markdown_output=markdown,
                include_terminal_reviews=False,
                include_superseded_reviews=False,
                staged_file_warning_threshold=1000,
                include_package=True,
                json=True,
            )
        )
        assert result["ok"], result
        assert output.exists()
        assert markdown.exists()
        package = json.loads(output.read_text(encoding="utf-8"))
        assert package["schema_type"] == "coagent_human_review_package"
        assert package["task_id"] == task_id
        assert package["human_required"] is False
        assert package["artifacts"]["status_export_path"]["exists"]
        assert package["artifacts"]["doctor_full_path"]["overallStatus"] == "ok"
        assert package["artifacts"]["evidence_manifest_path"]["evidence_count"] == 1
        assert package["evidence_refresh"]["recommended"] is True, package["evidence_refresh"]
        assert package["evidence_refresh"]["stale_count"] == 2, package["evidence_refresh"]
        assert package["evidence_refresh"]["critical_stale_count"] == 1, package["evidence_refresh"]
        assert package["evidence_refresh"]["archival_stale_count"] == 1, package["evidence_refresh"]
        assert any("coagent_doctor.py --mode quick" in command for command in package["evidence_refresh"]["commands"])
        assert any("status_export.py" in command for command in package["evidence_refresh"]["commands"])
        assert package["task_health"]["ok"], package["task_health"]
        assert package["task_health"]["continue_allowed"] is True, package["task_health"]
        assert package["task_health"]["recommended_action"] == "continue", package["task_health"]
        assert package["task_health"]["decision"]["continue_allowed"] is True, package["task_health"]
        assert package["task_health"]["tasks"][0]["decision"]["continue_allowed"] is True, package["task_health"]
        assert package["closeout_verification"]["ok"], package["closeout_verification"]
        assert package["closeout_verification"]["closeout_required"] is False, package["closeout_verification"]
        assert package["closeout_verification"]["effect"]["review_unblocked"] is True, package["closeout_verification"]
        assert package["blocker_packet_needed"] is False, package
        assert "blocker_packet.py" in package["blocker_packet_command"], package
        assert "--record-metadata" in package["blocker_packet_record_command"], package
        assert any("blocker_packet.py" in command for command in package["resume_commands"])
        assert package["runtime_audit"]["ok"], package["runtime_audit"]
        text = markdown.read_text(encoding="utf-8")
        assert "CoAgent Human Review Package" in text
        assert "review package smoke" in text
        assert "task_continue_allowed" in text
        assert "## Blocker Packet" in text
        assert "## Task Health" in text
        assert "## Evidence Freshness" in text
        assert "status_export.py" in text
        assert "## Review Closeout Verification" in text
        assert "progress_review" in text

        missing_closeout_task_id = "coagent_review_package_missing_closeout_smoke"
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=missing_closeout_task_id,
                objective="Prove review package flags broken closeout",
                role="MainAgent",
                read_scope=["CoAgent/review_package"],
                write_scope=["Results/coagent_status"],
                acceptance="review package requires human when closeout evidence is broken",
                stop_condition="package flags closeout failure",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "checkpoint": "missing closeout smoke",
                        "next_action": "repair closeout",
                        "review_status": "accepted",
                        "human_needed": "",
                        "review_closeout_path": str((tmp_root / "missing_closeout.json").relative_to(ROOT)).replace("\\", "/"),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=10,
                actor="MainAgent",
            )
        )
        missing_result = review_package.run_package(
            ns(
                db=db,
                events=events,
                task_id=missing_closeout_task_id,
                output=tmp_root / "missing_closeout_review_package.json",
                markdown_output=tmp_root / "missing_closeout_review_package.md",
                include_terminal_reviews=False,
                include_superseded_reviews=False,
                staged_file_warning_threshold=1000,
                include_package=True,
                json=True,
            )
        )
        assert missing_result["ok"], missing_result
        missing_package = json.loads((tmp_root / "missing_closeout_review_package.json").read_text(encoding="utf-8"))
        assert missing_package["human_required"] is True, missing_package
        assert missing_package["closeout_verification"]["ok"] is False, missing_package["closeout_verification"]
        assert any(
            item["reason"] == "missing_review_closeout_artifact"
            for item in missing_package["closeout_verification"]["findings"]
        )

    print("review_package_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
