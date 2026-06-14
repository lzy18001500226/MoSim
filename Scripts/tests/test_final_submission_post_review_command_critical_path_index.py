from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_post_review_command_critical_path_index.py"


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


def test_current_post_review_command_critical_path_index_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["action_count"] == 3
    assert stdout["critical_path_count"] == 3
    assert stdout["family_count"] == 18
    assert stdout["unique_command_count"] == 20
    assert stdout["total_command_reference_count"] == 45
    assert stdout["issue_count"] == 0
    assert stdout["runs_commands_now"] is False
    assert stdout["applies_transitions_now"] is False
    assert stdout["edits_decision_artifacts_now"] is False
    assert stdout["generates_final_outputs"] is False
    assert stdout["final_acceptance"] is False

    index = json.loads(
        (tmp_path / "final_submission_post_review_command_critical_path_index.json").read_text(encoding="utf-8")
    )
    assert index["status"] == "post_review_command_critical_path_index_not_execution"
    assert len(index["critical_paths"]) == 3
    assert "final_submission_dashboard" in index["shared_tail_families"]
    assert "It does not run post-review rerun commands." in index["claim_boundary"]
    assert "It does not write PMO final acceptance." in index["claim_boundary"]
    for critical_path in index["critical_paths"]:
        assert critical_path["runs_rerun_commands_now"] is False
        assert critical_path["applies_transition_now"] is False
        assert critical_path["family_step_count"] >= len(critical_path["shared_tail_families"])
        assert critical_path["family_steps"][0]["phase"] == "action_specific_prefix"

    markdown = (tmp_path / "final_submission_post_review_command_critical_path_index.md").read_text(
        encoding="utf-8"
    )
    assert "## Shared Tail" in markdown
    assert "## Critical Paths" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_post_review_command_critical_path_index_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_post_review_command_critical_path_index_builds(temp / "current")
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
    print("[OK] final submission post-review command critical-path index tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
