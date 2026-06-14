from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_no_packet_action_escalation_note.py"


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


def test_current_no_packet_action_escalation_note_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["no_packet_action_count"] == 3
    assert stdout["environment_dependency_count"] == 1
    assert stdout["final_artifact_creation_count"] == 1
    assert stdout["post_change_gate_rerun_count"] == 1
    assert stdout["total_referenced_target_count"] == 8
    assert stdout["missing_review_artifact_count"] == 0
    assert stdout["issue_count"] == 0
    assert stdout["reviewer_packet_created_now"] is False
    assert stdout["answers_questions_now"] is False
    assert stdout["edits_decision_artifacts_now"] is False
    assert stdout["runs_commands_now"] is False
    assert stdout["authorizes_execution_now"] is False
    assert stdout["generates_final_outputs"] is False
    assert stdout["final_acceptance"] is False

    note = json.loads(
        (tmp_path / "final_submission_no_packet_action_escalation_note.json").read_text(encoding="utf-8")
    )
    assert note["status"] == "no_packet_action_escalation_note_not_execution"
    actions = {item["action_id"]: item for item in note["no_packet_actions"]}
    assert set(actions) == {
        "A2-provide-pdf-engine",
        "A4-create-reviewed-final-artifacts",
        "A5-rerun-readiness-gates",
    }
    assert actions["A2-provide-pdf-engine"]["escalation_class"] == "environment_dependency"
    assert actions["A4-create-reviewed-final-artifacts"]["escalation_class"] == "final_artifact_creation"
    assert actions["A5-rerun-readiness-gates"]["escalation_class"] == "post_change_gate_rerun"
    for action in actions.values():
        assert action["reviewer_packet_created_now"] is False
        assert action["automated_execution_allowed"] is False
        assert action["runs_commands_now"] is False
        assert action["authorizes_execution_now"] is False
        assert action["generates_final_outputs"] is False
        assert action["final_acceptance"] is False
        assert action["referenced_target_count"] > 0
    assert "pdf_export" in actions["A2-provide-pdf-engine"]["referenced_by_execution_targets"]
    assert "final_acceptance_packet" in actions["A4-create-reviewed-final-artifacts"]["referenced_by_execution_targets"]
    assert "demo_video_recording" in actions["A5-rerun-readiness-gates"]["referenced_by_execution_targets"]
    assert "It does not create reviewer packets." in note["claim_boundary"]
    assert "It does not rerun readiness gates." in note["claim_boundary"]

    markdown = (tmp_path / "final_submission_no_packet_action_escalation_note.md").read_text(encoding="utf-8")
    assert "## No-Packet Actions" in markdown
    assert "A2-provide-pdf-engine" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_no_packet_action_escalation_note_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_no_packet_action_escalation_note_builds(temp / "current")
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
    print("[OK] final submission no-packet action escalation note tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
