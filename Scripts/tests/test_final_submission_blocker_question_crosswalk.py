from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_blocker_question_crosswalk.py"


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


def test_current_blocker_question_crosswalk_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["dashboard_blocker_count"] == 16
    assert stdout["crosswalk_row_count"] == 16
    assert stdout["reviewer_packet_action_count"] == 3
    assert stdout["actions_without_reviewer_packet_count"] == 3
    assert stdout["unmapped_dashboard_blocker_count"] == 0
    assert stdout["question_backed_row_count"] == 9
    assert stdout["answers_questions_now"] is False
    assert stdout["edits_decision_artifacts_now"] is False
    assert stdout["runs_rerun_commands_now"] is False
    assert stdout["generates_final_outputs"] is False
    assert stdout["final_acceptance"] is False

    crosswalk = json.loads((tmp_path / "final_submission_blocker_question_crosswalk.json").read_text(encoding="utf-8"))
    assert crosswalk["status"] == "blocker_question_crosswalk_not_execution"
    assert crosswalk["actions_without_reviewer_packet"] == [
        "A2-provide-pdf-engine",
        "A4-create-reviewed-final-artifacts",
        "A5-rerun-readiness-gates",
    ]
    assert any(
        row["action_id"] == "A1-approve-or-reject-report-source-edits"
        and row["review_question_count"] == 3
        for row in crosswalk["rows"]
    )
    assert any(
        row["action_id"] == "A6-review-final-output-execution-decision"
        and row["review_question_count"] == 3
        for row in crosswalk["rows"]
    )
    assert "It does not answer review questions." in crosswalk["claim_boundary"]
    assert "It does not run rerun commands." in crosswalk["claim_boundary"]

    markdown = (tmp_path / "final_submission_blocker_question_crosswalk.md").read_text(encoding="utf-8")
    assert "source_output_readiness:report_source_edit_not_approved" in markdown
    assert "A2-provide-pdf-engine" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_blocker_question_crosswalk_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_blocker_question_crosswalk_builds(temp / "current")
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
    print("[OK] final submission blocker question crosswalk tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
