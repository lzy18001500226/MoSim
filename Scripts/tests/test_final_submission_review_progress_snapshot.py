from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_review_progress_snapshot.py"


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


def test_current_review_progress_snapshot_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["review_aid_count"] == 3
    assert stdout["pending_review_action_count"] == 3
    assert stdout["blocked_artifact_count"] == 17
    assert stdout["missing_open_file_count"] == 0
    assert stdout["automated_execution_allowed"] is False

    snapshot = json.loads((tmp_path / "final_submission_review_progress_snapshot.json").read_text(encoding="utf-8"))
    assert snapshot["status"] == "review_progress_snapshot_not_execution"
    assert snapshot["summary"]["minimum_open_file_count"] == 10
    assert snapshot["summary"]["generates_final_outputs"] is False
    assert snapshot["summary"]["final_acceptance"] is False
    assert snapshot["recommended_review_order"] == [
        "A1-approve-or-reject-report-source-edits",
        "A3-review-demo-storyboard",
        "A6-review-final-output-execution-decision",
    ]
    assert [aid["aid_id"] for aid in snapshot["review_aids"]] == [
        "blocked_gate_triage_map",
        "human_decision_diff_template",
        "reviewer_quickstart",
    ]
    assert {group["decision_group_id"] for group in snapshot["decision_groups"]} == {
        "A1-report-source-edit-decision",
        "A6-final-output-execution-decision",
    }
    assert all(action["approves_or_executes_now"] is False for action in snapshot["pending_review_actions"])
    assert "It does not change gates, readiness, approval, or decision templates." in snapshot["claim_boundary"]

    markdown = (tmp_path / "final_submission_review_progress_snapshot.md").read_text(encoding="utf-8")
    assert "## Review Aids" in markdown
    assert "blocked_gate_triage_map" in markdown
    assert "A6-review-final-output-execution-decision" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_review_progress_snapshot_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_review_progress_snapshot_builds(temp / "current")
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
    print("[OK] final submission review progress snapshot tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
