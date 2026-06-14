from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_final_submission_answer_sheet_decision_consistency.py"


def run_checker(output_json: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--output-json",
            str(output_json.relative_to(ROOT)),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_answer_sheet_decision_consistency_passes(tmp_path: Path) -> None:
    output_json = tmp_path / "answer_sheet_decision_consistency.json"
    completed = run_checker(output_json)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["status"] == "answer_sheet_decision_consistency_check_not_execution"
    assert report["summary"]["review_action_count"] == 3
    assert report["summary"]["answer_field_count"] == 38
    assert report["summary"]["unfilled_placeholder_field_count"] == 38
    assert report["summary"]["copied_field_count"] == 0
    assert report["summary"]["issue_count"] == 0
    assert report["summary"]["report_source_decision"] == "pending_review"
    assert report["summary"]["final_output_pending_action_count"] == 3
    assert report["summary"]["applies_decisions_now"] is False
    assert report["summary"]["edits_decision_templates_now"] is False
    assert report["summary"]["generates_final_outputs"] is False
    assert report["summary"]["final_acceptance"] is False
    assert all(section["copied_field_count"] == 0 for section in report["sections"])
    assert "It does not copy answer-sheet values." in report["claim_boundary"]

    persisted = json.loads(output_json.read_text(encoding="utf-8"))
    assert persisted["check_id"] == report["check_id"]


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_answer_sheet_decision_consistency_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_answer_sheet_decision_consistency_passes(temp / "current")
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
    print("[OK] final submission answer-sheet decision consistency tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
