from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_manual_review_answer_sheet_template.py"


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


def test_current_manual_review_answer_sheet_template_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["review_action_count"] == 3
    assert stdout["answer_field_count"] == 38
    assert stdout["required_answer_field_count"] == 29
    assert stdout["automated_execution_allowed"] is False

    sheet = json.loads((tmp_path / "final_submission_manual_review_answer_sheet_template.json").read_text(encoding="utf-8"))
    assert sheet["status"] == "manual_review_answer_sheet_template_not_execution"
    assert sheet["summary"]["copies_answers_now"] is False
    assert sheet["summary"]["edits_decision_artifacts_now"] is False
    assert sheet["summary"]["approves_or_executes_now"] is False
    assert sheet["summary"]["generates_final_outputs"] is False
    assert sheet["summary"]["final_acceptance"] is False
    assert [section["action_id"] for section in sheet["sections"]] == [
        "A1-approve-or-reject-report-source-edits",
        "A3-review-demo-storyboard",
        "A6-review-final-output-execution-decision",
    ]
    assert all(
        field["proposed_value"] == "<fill_after_review>"
        for section in sheet["sections"]
        for field in section["answer_fields"]
    )
    assert all(section["approves_or_executes_now"] is False for section in sheet["sections"])
    assert any(
        command == "python Scripts/quality/build_final_submission_post_review_rerun_matrix.py"
        for section in sheet["sections"]
        for command in section["post_review_rerun_commands"]
    ) is False
    assert "It does not fill answers for the user." in sheet["claim_boundary"]

    markdown = (tmp_path / "final_submission_manual_review_answer_sheet_template.md").read_text(encoding="utf-8")
    assert "## Answer Sections" in markdown
    assert "<fill_after_review>" in markdown

    template_copy = json.loads((tmp_path / "final_submission_manual_review_answer_sheet.template.json").read_text(encoding="utf-8"))
    assert template_copy["answer_sheet_id"] == sheet["answer_sheet_id"]


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_manual_review_answer_sheet_template_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_manual_review_answer_sheet_template_builds(temp / "current")
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
    print("[OK] final submission manual-review answer sheet template tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
