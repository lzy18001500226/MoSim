from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_post_review_reviewer_checklist.py"


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


def test_current_post_review_reviewer_checklist_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["review_action_count"] == 3
    assert stdout["actions_without_reviewer_packet_count"] == 3
    assert stdout["total_blocker_row_count"] == 9
    assert stdout["total_question_count"] == 9
    assert stdout["total_command_reference_count"] == 45
    assert stdout["shared_tail_family_count"] == 12
    assert stdout["issue_count"] == 0
    assert stdout["answers_questions_now"] is False
    assert stdout["edits_decision_artifacts_now"] is False
    assert stdout["runs_commands_now"] is False
    assert stdout["applies_transitions_now"] is False
    assert stdout["generates_final_outputs"] is False
    assert stdout["final_acceptance"] is False

    checklist = json.loads(
        (tmp_path / "final_submission_post_review_reviewer_checklist.json").read_text(encoding="utf-8")
    )
    assert checklist["status"] == "post_review_reviewer_checklist_not_execution"
    assert len(checklist["review_items"]) == 3
    assert len(checklist["actions_without_reviewer_packet"]) == 3
    for item in checklist["review_items"]:
        assert item["reviewer_packet_available"] is True
        assert item["question_count"] == 3
        assert item["shared_tail_matches_note"] is True
        assert item["answers_questions_now"] is False
        assert item["runs_commands_now"] is False
    assert "It does not answer reviewer questions." in checklist["claim_boundary"]
    assert "It does not write PMO final acceptance." in checklist["claim_boundary"]

    markdown = (tmp_path / "final_submission_post_review_reviewer_checklist.md").read_text(encoding="utf-8")
    assert "## Review Items" in markdown
    assert "## Actions Without Reviewer Packet" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_post_review_reviewer_checklist_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_post_review_reviewer_checklist_builds(temp / "current")
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
    print("[OK] final submission post-review reviewer checklist tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
