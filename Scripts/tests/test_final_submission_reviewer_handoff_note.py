from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_reviewer_handoff_note.py"


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


def test_current_reviewer_handoff_note_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["handoff_step_count"] == 5
    assert stdout["bundle_artifact_count"] == 7
    assert stdout["answer_field_count"] == 38
    assert stdout["copied_field_count"] == 0
    assert stdout["automated_execution_allowed"] is False

    handoff = json.loads((tmp_path / "final_submission_reviewer_handoff_note.json").read_text(encoding="utf-8"))
    assert handoff["status"] == "reviewer_handoff_note_not_execution"
    assert handoff["summary"]["ready_bundle_artifact_count"] == 7
    assert handoff["summary"]["required_answer_field_count"] == 29
    assert handoff["summary"]["approves_or_executes_now"] is False
    assert handoff["summary"]["generates_final_outputs"] is False
    assert handoff["summary"]["final_acceptance"] is False
    assert [step["step_id"] for step in handoff["handoff_steps"]] == [
        "H1-open-reviewer-quickstart-first",
        "H2-pick-blocker-lane-from-triage-map",
        "H3-use-decision-diff-and-answer-sheet",
        "H4-confirm-answer-sheet-consistency",
        "H5-use-rerun-matrix-only-after-human-decision-edit",
    ]
    assert handoff["first_review_targets"] == [
        "A1-approve-or-reject-report-source-edits",
        "A3-review-demo-storyboard",
        "A6-review-final-output-execution-decision",
    ]
    assert "Do not edit decision templates from this handoff note." in handoff["pre_execution_guard"]
    assert "It does not run post-review commands." in handoff["claim_boundary"]

    markdown = (tmp_path / "final_submission_reviewer_handoff_note.md").read_text(encoding="utf-8")
    assert "## Handoff Steps" in markdown
    assert "H1-open-reviewer-quickstart-first" in markdown
    assert "A6-review-final-output-execution-decision" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_reviewer_handoff_note_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_reviewer_handoff_note_builds(temp / "current")
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
    print("[OK] final submission reviewer handoff note tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
