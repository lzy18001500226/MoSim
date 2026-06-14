from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_human_review_guide.py"


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


def test_current_human_review_guide_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["review_step_count"] == 3
    assert stdout["pending_decision_count"] == 3
    assert stdout["automated_execution_allowed"] is False

    guide = json.loads((tmp_path / "final_submission_human_review_guide.json").read_text(encoding="utf-8"))
    assert guide["status"] == "human_review_guide_not_execution"
    assert guide["summary"]["generates_final_outputs"] is False
    assert guide["summary"]["final_acceptance"] is False
    assert [step["action_id"] for step in guide["review_steps"]] == [
        "A1-approve-or-reject-report-source-edits",
        "A3-review-demo-storyboard",
        "A6-review-final-output-execution-decision",
    ]
    assert all(step["current_decision"] == "pending_review" for step in guide["review_steps"])
    assert all(step["approved"] is False for step in guide["review_steps"])
    assert "It does not execute rerun commands." in guide["claim_boundary"]


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_human_review_guide_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_human_review_guide_builds(temp / "current")
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
    print("[OK] final submission human review guide tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
