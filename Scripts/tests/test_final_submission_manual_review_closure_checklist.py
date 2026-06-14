from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_manual_review_closure_checklist.py"


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


def test_current_manual_review_closure_checklist_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["closure_item_count"] == 3
    assert stdout["answer_field_count"] == 38
    assert stdout["copied_field_count"] == 0
    assert stdout["runs_rerun_commands_now"] is False
    assert stdout["automated_execution_allowed"] is False

    checklist = json.loads(
        (tmp_path / "final_submission_manual_review_closure_checklist.json").read_text(encoding="utf-8")
    )
    assert checklist["status"] == "manual_review_closure_checklist_not_execution"
    assert checklist["summary"]["handoff_step_count"] == 5
    assert checklist["summary"]["required_answer_field_count"] == 29
    assert checklist["summary"]["rerun_matrix_row_count"] == 3
    assert checklist["summary"]["copies_answers_now"] is False
    assert checklist["summary"]["edits_decision_templates_now"] is False
    assert checklist["summary"]["approves_or_executes_now"] is False
    assert checklist["summary"]["generates_final_outputs"] is False
    assert checklist["summary"]["final_acceptance"] is False
    assert [item["action_id"] for item in checklist["closure_items"]] == [
        "A1-approve-or-reject-report-source-edits",
        "A3-review-demo-storyboard",
        "A6-review-final-output-execution-decision",
    ]
    assert all(item["runs_rerun_commands_now"] is False for item in checklist["closure_items"])
    assert "It does not run rerun commands." in checklist["claim_boundary"]

    markdown = (tmp_path / "final_submission_manual_review_closure_checklist.md").read_text(encoding="utf-8")
    assert "## Closure Items" in markdown
    assert "CLOSE-01-A1-approve-or-reject-report-source-edits" in markdown
    assert "Required After Manual Fill Checks" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_manual_review_closure_checklist_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_manual_review_closure_checklist_builds(temp / "current")
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
    print("[OK] final submission manual review closure checklist tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
