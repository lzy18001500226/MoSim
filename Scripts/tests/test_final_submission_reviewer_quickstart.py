from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_reviewer_quickstart.py"


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


def test_current_reviewer_quickstart_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["review_action_count"] == 3
    assert stdout["minimum_open_file_count"] == 10
    assert stdout["missing_open_file_count"] == 0
    assert stdout["automated_execution_allowed"] is False

    quickstart = json.loads((tmp_path / "final_submission_reviewer_quickstart.json").read_text(encoding="utf-8"))
    assert quickstart["status"] == "reviewer_quickstart_not_execution"
    assert quickstart["summary"]["generates_final_outputs"] is False
    assert quickstart["summary"]["final_acceptance"] is False
    assert quickstart["review_order"] == [
        "A1-approve-or-reject-report-source-edits",
        "A3-review-demo-storyboard",
        "A6-review-final-output-execution-decision",
    ]
    by_action = {section["action_id"]: section for section in quickstart["sections"]}
    assert by_action["A1-approve-or-reject-report-source-edits"]["decision_diff_group"] == (
        "A1-report-source-edit-decision"
    )
    assert by_action["A6-review-final-output-execution-decision"]["decision_diff_group"] == (
        "A6-final-output-execution-decision"
    )
    assert all(
        item["exists"] is True
        for section in quickstart["sections"]
        for item in section["minimum_open_files"]
    )
    assert "It does not approve decisions." in quickstart["claim_boundary"]

    markdown = (tmp_path / "final_submission_reviewer_quickstart.md").read_text(encoding="utf-8")
    assert "## Review Order" in markdown
    assert "A1-approve-or-reject-report-source-edits" in markdown
    assert "A6-review-final-output-execution-decision" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_reviewer_quickstart_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_reviewer_quickstart_builds(temp / "current")
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
    print("[OK] final submission reviewer quickstart tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
