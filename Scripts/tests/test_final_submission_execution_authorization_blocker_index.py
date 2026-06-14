from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_execution_authorization_blocker_index.py"


def run_builder(output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--output-dir",
            str(output_dir.relative_to(ROOT)),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_execution_authorization_blocker_index_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["execution_target_count"] == 4
    assert stdout["blocked_execution_target_count"] == 4
    assert stdout["unique_reviewer_packet_action_count"] == 3
    assert stdout["unique_no_packet_action_count"] == 3
    assert stdout["target_action_reference_count"] == 16
    assert stdout["target_without_no_packet_action_count"] == 1
    assert stdout["issue_count"] == 0
    assert stdout["automated_execution_allowed"] is False
    assert stdout["answers_questions_now"] is False
    assert stdout["fills_answers_now"] is False
    assert stdout["edits_decision_artifacts_now"] is False
    assert stdout["runs_commands_now"] is False
    assert stdout["authorizes_execution_now"] is False
    assert stdout["generates_final_outputs"] is False
    assert stdout["final_acceptance"] is False

    index = json.loads(
        (tmp_path / "final_submission_execution_authorization_blocker_index.json").read_text(encoding="utf-8")
    )
    assert index["status"] == "execution_authorization_blocker_index_not_execution"
    assert index["unique_reviewer_packet_actions"] == [
        "A1-approve-or-reject-report-source-edits",
        "A3-review-demo-storyboard",
        "A6-review-final-output-execution-decision",
    ]
    assert index["unique_no_packet_actions"] == [
        "A2-provide-pdf-engine",
        "A4-create-reviewed-final-artifacts",
        "A5-rerun-readiness-gates",
    ]
    targets = {item["target_id"]: item for item in index["execution_target_authorization_blockers"]}
    assert set(targets) == {
        "report_source_edit",
        "pdf_export",
        "demo_video_recording",
        "final_acceptance_packet",
    }
    assert targets["report_source_edit"]["no_packet_action_count"] == 0
    assert targets["pdf_export"]["no_packet_action_count"] == 3
    assert targets["demo_video_recording"]["no_packet_action_count"] == 2
    assert targets["final_acceptance_packet"]["no_packet_action_count"] == 3
    for target in targets.values():
        assert target["ready_now"] is False
        assert target["requires_separate_authorization"] is True
        assert target["authorizes_execution_now"] is False
        assert target["executes_now"] is False
    assert "pdf_export" in targets["pdf_export"]["future_command_families"]
    assert "demo_video" in targets["demo_video_recording"]["future_command_families"]
    assert "final_acceptance_prereq" in targets["final_acceptance_packet"]["future_command_families"]
    assert "final_artifact_manifest" in targets["final_acceptance_packet"]["future_command_families"]
    for action in targets["pdf_export"]["no_packet_actions"]:
        assert action["reviewer_packet_available"] is False
        assert action["reason"] == "no_current_reviewer_packet"
    assert "It does not approve execution." in index["claim_boundary"]
    assert "It does not run commands." in index["claim_boundary"]

    markdown = (tmp_path / "final_submission_execution_authorization_blocker_index.md").read_text(
        encoding="utf-8"
    )
    assert "## Execution Targets" in markdown
    assert "## No-Packet Actions" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_execution_authorization_blocker_index_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_execution_authorization_blocker_index_builds(temp / "current")
    finally:
        if temp.exists():
            for item in sorted(temp.glob("**/*"), key=lambda path: len(path.parts), reverse=True):
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    item.rmdir()
            temp.rmdir()
        tmp_root = ROOT / ".tmp"
        if tmp_root.exists() and not any(tmp_root.iterdir()):
            tmp_root.rmdir()
    print("[OK] final submission execution authorization blocker index tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
