#!/usr/bin/env python3
"""Smoke test for CoAgent status export bundles."""

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
from CoAgent.status_export import status_export


def ns(**kwargs):
    return argparse.Namespace(**kwargs)


def main() -> int:
    (ROOT / "Results" / "tmp").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as tmp:
        tmp_root = Path(tmp)
        db = tmp_root / "tasks.sqlite3"
        events = tmp_root / "events.jsonl"
        task_id = "coagent_status_export_smoke"
        output = tmp_root / "status.json"
        markdown = tmp_root / "status.md"
        resume_output = tmp_root / "resume.json"
        resume_markdown = tmp_root / "resume.md"
        evidence_manifest_output = tmp_root / "evidence_manifest.json"
        evidence_manifest_markdown = tmp_root / "evidence_manifest.md"
        closeout_path = tmp_root / "status_export_smoke.review_closeout.json"
        closeout_rel = str(closeout_path.relative_to(ROOT)).replace("\\", "/")
        review_package_path = tmp_root / "review_package.json"
        review_package_rel = str(review_package_path.relative_to(ROOT)).replace("\\", "/")
        review_package_path.write_text(json.dumps({"task_id": task_id, "ok": True}, sort_keys=True), encoding="utf-8")
        runtime.create_task(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                objective="Prove status export bundle",
                role="MainAgent",
                read_scope=["CoAgent/status_export"],
                write_scope=["Results/coagent_status"],
                acceptance="status export exists",
                stop_condition="bundle written",
                depends_on=[],
                metadata=json.dumps(
                    {
                        "task_class": "long_running_task",
                        "project_goal": "CoAgent transferable multi-conversation architecture",
                        "canonical_task_goal": "Prove status export bundle",
                        "conversation_objective": "Export compact status",
                        "checkpoint": "status export smoke",
                        "next_action": "inspect bundle",
                        "review_status": "accepted",
                        "human_needed": "",
                        "review_decision_by": "MainAgent",
                        "review_closeout_path": closeout_rel,
                        "review_package_path": review_package_rel,
                        "status_export_path": str(output.relative_to(ROOT)).replace("\\", "/"),
                        "status_export_markdown": str(markdown.relative_to(ROOT)).replace("\\", "/"),
                        "resume_bundle_path": str(resume_output.relative_to(ROOT)).replace("\\", "/"),
                        "resume_bundle_markdown": str(resume_markdown.relative_to(ROOT)).replace("\\", "/"),
                        "evidence_manifest_path": str(evidence_manifest_output.relative_to(ROOT)).replace("\\", "/"),
                        "evidence_manifest_markdown": str(evidence_manifest_markdown.relative_to(ROOT)).replace("\\", "/"),
                        "review_owner": "VerificationAgent",
                        "required_evidence": ["status export"],
                        "review_gates": ["status_export"],
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
                priority=20,
                actor="MainAgent",
            )
        )
        closeout_path.write_text(
            json.dumps({"task_id": task_id, "decision": "accepted"}, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
        exported = status_export.export_status(
            ns(
                db=db,
                events=events,
                task_id=task_id,
                output=output,
                markdown_output=markdown,
                resume_output=resume_output,
                resume_markdown_output=resume_markdown,
                include_bundle=True,
                include_terminal_reviews=False,
                include_superseded_reviews=False,
                include_context_quality=True,
                context_output=tmp_root / "context.md",
                event_limit=8,
                warn_chars=14000,
                fail_chars=22000,
                include_preflight_summary=True,
                include_runtime_audit=True,
                staged_file_warning_threshold=1000,
                include_task_health=True,
                include_git_handoff=True,
                include_evidence_manifest=True,
                evidence_manifest_output=evidence_manifest_output,
                evidence_manifest_markdown_output=evidence_manifest_markdown,
                stale_minutes=120,
                json=True,
            )
        )
        assert exported["ok"], exported
        assert output.exists()
        assert markdown.exists()
        assert resume_output.exists()
        assert resume_markdown.exists()
        bundle = json.loads(output.read_text(encoding="utf-8"))
        assert bundle["task_id"] == task_id
        assert bundle["doctor"]["overallStatus"] in {"ok", "warning"}
        assert bundle["context_quality"]["quality"]["ok"], bundle["context_quality"]
        assert bundle["preflight"]["enabled"], bundle["preflight"]
        assert bundle["preflight"]["runtime_output_ignore"]["ok"], bundle["preflight"]
        assert "git_workspace_state" in bundle["preflight"]
        assert bundle["runtime_audit"]["enabled"], bundle["runtime_audit"]
        assert bundle["runtime_audit"]["ok"], bundle["runtime_audit"]
        assert bundle["runtime_audit"]["db_event_count"] == bundle["runtime_audit"]["jsonl_event_count"], bundle["runtime_audit"]
        assert bundle["runtime_audit"]["sensitive_db_event_count"] == 0, bundle["runtime_audit"]
        assert bundle["runtime_audit"]["sensitive_jsonl_event_count"] == 0, bundle["runtime_audit"]
        assert bundle["task_health"]["enabled"], bundle["task_health"]
        assert bundle["task_health"]["ok"], bundle["task_health"]
        assert bundle["task_health"]["continue_allowed"] is True, bundle["task_health"]
        assert bundle["task_health"]["recommended_action"] == "continue", bundle["task_health"]
        assert bundle["task_health"]["decision"]["continue_allowed"] is True, bundle["task_health"]
        assert bundle["task_health"]["tasks"][0]["task_id"] == task_id, bundle["task_health"]
        assert bundle["task_health"]["tasks"][0]["decision"]["continue_allowed"] is True, bundle["task_health"]
        assert bundle["git_handoff"]["enabled"], bundle["git_handoff"]
        assert "totals" in bundle["git_handoff"], bundle["git_handoff"]
        assert bundle["evidence_manifest"]["enabled"], bundle["evidence_manifest"]
        assert bundle["evidence_manifest"]["ok"], bundle["evidence_manifest"]
        assert bundle["evidence_manifest"]["evidence_count"] >= 1, bundle["evidence_manifest"]
        assert "stale_count" in bundle["evidence_manifest"], bundle["evidence_manifest"]
        assert "critical_stale_count" in bundle["evidence_manifest"], bundle["evidence_manifest"]
        assert "archival_stale_count" in bundle["evidence_manifest"], bundle["evidence_manifest"]
        assert "stale" in bundle["evidence_manifest"], bundle["evidence_manifest"]
        assert "freshness_status" in bundle["evidence_manifest"], bundle["evidence_manifest"]
        assert "stale_refresh_recommended" in bundle["evidence_manifest"], bundle["evidence_manifest"]
        assert "refresh_commands" in bundle["evidence_manifest"], bundle["evidence_manifest"]
        markdown_text = markdown.read_text(encoding="utf-8")
        assert "status export smoke" in markdown_text
        assert "## Review Closeout" in markdown_text
        assert "status_export_smoke.review_closeout.json" in markdown_text
        assert "## Git And Runtime Preflight" in markdown_text
        assert "## Runtime Event Audit" in markdown_text
        assert "## Task Health" in markdown_text
        assert "## Git Handoff" in markdown_text
        assert "## Evidence Manifest" in markdown_text
        assert "stale_refresh_recommended" in markdown_text
        assert "critical_stale_count" in markdown_text
        resume = json.loads(resume_output.read_text(encoding="utf-8"))
        assert resume["schema_type"] == "coagent_resume_bundle"
        assert resume["task_id"] == task_id
        assert resume["checkpoint"] == "status export smoke"
        assert resume["continue_allowed"] is True, resume
        assert resume["recommended_action"] == "continue", resume
        assert resume["blocking_task_ids"] == [], resume
        assert resume["watch_task_ids"] == [], resume
        assert resume["human_task_ids"] == [], resume
        assert resume["review_task_ids"] == [], resume
        assert resume["safety_task_ids"] == [], resume
        assert resume["task_health"]["enabled"], resume["task_health"]
        assert resume["task_health"]["continue_allowed"] is True, resume["task_health"]
        assert resume["task_health"] == resume["health"]["task_health"], resume
        assert resume["evidence_manifest_summary"]["enabled"], resume["evidence_manifest_summary"]
        assert resume["evidence_manifest_summary"]["ok"], resume["evidence_manifest_summary"]
        assert resume["evidence_manifest_summary"]["missing_count"] == 0, resume["evidence_manifest_summary"]
        assert resume["evidence_manifest_summary"]["critical_stale_count"] == 0, resume["evidence_manifest_summary"]
        assert resume["evidence_manifest_summary"]["stale_refresh_recommended"] is False, resume["evidence_manifest_summary"]
        assert resume["evidence_manifest_summary"] == resume["health"]["evidence_manifest"], resume
        assert resume["review"]["review_status"] == "accepted"
        assert resume["review"]["review_closeout_path"].endswith("status_export_smoke.review_closeout.json")
        assert resume["review"]["review_package_path"].endswith("review_package.json")
        assert resume["health"]["runtime_audit"]["ok"], resume["health"]["runtime_audit"]
        assert resume["health"]["task_health"]["enabled"], resume["health"]["task_health"]
        assert resume["health"]["task_health"]["continue_allowed"] is True, resume["health"]["task_health"]
        assert resume["health"]["task_health"]["recommended_action"] == "continue", resume["health"]["task_health"]
        assert resume["health"]["task_health"]["decision"]["continue_allowed"] is True, resume["health"]["task_health"]
        assert resume["health"]["task_health"]["tasks"][0]["task_id"] == task_id, resume["health"]["task_health"]
        assert resume["health"]["task_health"]["tasks"][0]["decision"]["continue_allowed"] is True, resume["health"]["task_health"]
        assert resume["health"]["git_handoff"]["enabled"], resume["health"]["git_handoff"]
        assert "totals" in resume["health"]["git_handoff"], resume["health"]["git_handoff"]
        assert resume["health"]["evidence_manifest"]["enabled"], resume["health"]["evidence_manifest"]
        assert resume["health"]["evidence_manifest"]["ok"], resume["health"]["evidence_manifest"]
        assert "stale_count" in resume["health"]["evidence_manifest"], resume["health"]["evidence_manifest"]
        assert "critical_stale_count" in resume["health"]["evidence_manifest"], resume["health"]["evidence_manifest"]
        assert "archival_stale_count" in resume["health"]["evidence_manifest"], resume["health"]["evidence_manifest"]
        assert "freshness_status" in resume["health"]["evidence_manifest"], resume["health"]["evidence_manifest"]
        assert "stale_refresh_recommended" in resume["health"]["evidence_manifest"], resume["health"]["evidence_manifest"]
        assert "refresh_commands" in resume["health"]["evidence_manifest"], resume["health"]["evidence_manifest"]
        assert resume["review"]["blocker_packet_needed"] is False, resume["review"]
        assert "blocker_packet.py" in resume["review"]["blocker_packet_command"], resume["review"]
        assert "--record-metadata" in resume["review"]["blocker_packet_record_command"], resume["review"]
        assert any("task_health.py" in command for command in resume["resume_commands"])
        assert any("git_handoff_packet.py" in command for command in resume["resume_commands"])
        assert any("evidence_manifest.py" in command for command in resume["resume_commands"])
        assert any("review_package.py" in command for command in resume["resume_commands"])
        assert any("blocker_packet.py" in command for command in resume["resume_commands"])
        assert any("status_export.py" in command for command in resume["resume_commands"])
        resume_markdown_text = resume_markdown.read_text(encoding="utf-8")
        assert "## Resume Commands" in resume_markdown_text
        assert "## Task Health" in resume_markdown_text
        assert "## Git Handoff" in resume_markdown_text
        assert "## Evidence Manifest" in resume_markdown_text
        assert "blocker_packet_command" in resume_markdown_text
        assert "status export smoke" in resume_markdown_text

    print("status_export_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
