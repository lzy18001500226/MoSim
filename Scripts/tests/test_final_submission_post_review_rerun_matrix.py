from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_post_review_rerun_matrix.py"


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


def test_current_post_review_rerun_matrix_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["matrix_row_count"] == 3
    assert stdout["blocked_pending_review_row_count"] == 3
    assert stdout["unique_rerun_command_count"] >= 18
    assert stdout["automated_execution_allowed"] is False

    matrix = json.loads((tmp_path / "final_submission_post_review_rerun_matrix.json").read_text(encoding="utf-8"))
    assert matrix["status"] == "post_review_rerun_matrix_not_execution"
    assert matrix["summary"]["runs_rerun_commands_now"] is False
    assert matrix["summary"]["applies_decisions_now"] is False
    assert matrix["summary"]["generates_final_outputs"] is False
    assert matrix["summary"]["final_acceptance"] is False
    assert [row["action_id"] for row in matrix["rows"]] == [
        "A1-approve-or-reject-report-source-edits",
        "A3-review-demo-storyboard",
        "A6-review-final-output-execution-decision",
    ]
    assert all(row["rerun_readiness"] == "blocked_pending_human_review" for row in matrix["rows"])
    assert all(row["runs_now"] is False and row["approves_now"] is False for row in matrix["rows"])
    assert any(
        command == "python Scripts/quality/build_final_submission_review_progress_snapshot.py"
        for command in matrix["unique_rerun_commands"]
    )
    assert "It does not run any listed rerun command." in matrix["claim_boundary"]

    markdown = (tmp_path / "final_submission_post_review_rerun_matrix.md").read_text(encoding="utf-8")
    assert "## Matrix Rows" in markdown
    assert "A1-approve-or-reject-report-source-edits" in markdown
    assert "A6-review-final-output-execution-decision" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_post_review_rerun_matrix_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_post_review_rerun_matrix_builds(temp / "current")
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
    print("[OK] final submission post-review rerun matrix tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
