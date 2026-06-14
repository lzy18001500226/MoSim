from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_post_review_state_transition_plan.py"


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


def test_current_post_review_state_transition_plan_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["transition_count"] == 3
    assert stdout["dashboard_blocking_gate_count"] == 7
    assert stdout["applies_transitions_now"] is False
    assert stdout["runs_rerun_commands_now"] is False
    assert stdout["automated_execution_allowed"] is False

    plan = json.loads(
        (tmp_path / "final_submission_post_review_state_transition_plan.json").read_text(encoding="utf-8")
    )
    assert plan["status"] == "post_review_state_transition_plan_not_execution"
    assert plan["summary"]["blocked_pending_review_row_count"] == 3
    assert plan["summary"]["closure_item_count"] == 3
    assert plan["summary"]["edits_decision_templates_now"] is False
    assert plan["summary"]["approves_or_executes_now"] is False
    assert plan["summary"]["generates_final_outputs"] is False
    assert plan["summary"]["final_acceptance"] is False
    assert [transition["action_id"] for transition in plan["transitions"]] == [
        "A1-approve-or-reject-report-source-edits",
        "A3-review-demo-storyboard",
        "A6-review-final-output-execution-decision",
    ]
    assert all(transition["applies_transition_now"] is False for transition in plan["transitions"])
    assert all(transition["runs_rerun_commands_now"] is False for transition in plan["transitions"])
    assert "It does not apply state transitions." in plan["claim_boundary"]

    markdown = (tmp_path / "final_submission_post_review_state_transition_plan.md").read_text(encoding="utf-8")
    assert "## Global State Transition Sequence" in markdown
    assert "TRANSITION-A1-approve-or-reject-report-source-edits" in markdown
    assert "A6-review-final-output-execution-decision" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_post_review_state_transition_plan_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_post_review_state_transition_plan_builds(temp / "current")
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
    print("[OK] final submission post-review state transition plan tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
