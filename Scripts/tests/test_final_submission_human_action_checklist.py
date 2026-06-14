from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_human_action_checklist.py"


def run_builder(output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--output-dir",
            str(output_dir.relative_to(ROOT) if output_dir.is_relative_to(ROOT) else output_dir),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_human_action_checklist_groups_blockers(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["action_count"] == 6
    assert stdout["automated_execution_allowed"] is False

    checklist = json.loads((tmp_path / "final_submission_human_action_checklist.json").read_text(encoding="utf-8"))
    assert checklist["status"] == "human_action_checklist_not_execution"
    assert checklist["summary"]["source_blocker_count"] == 16
    assert checklist["summary"]["action_count"] == 6
    assert checklist["summary"]["generates_final_outputs"] is False
    assert checklist["summary"]["final_acceptance"] is False
    action_ids = [action["action_id"] for action in checklist["actions"]]
    assert action_ids == [
        "A1-approve-or-reject-report-source-edits",
        "A2-provide-pdf-engine",
        "A3-review-demo-storyboard",
        "A4-create-reviewed-final-artifacts",
        "A5-rerun-readiness-gates",
        "A6-review-final-output-execution-decision",
    ]
    assert "It does not write PMO final acceptance." in checklist["claim_boundary"]


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_human_action_checklist_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_human_action_checklist_groups_blockers(temp / "current")
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
    print("[OK] final submission human action checklist tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
