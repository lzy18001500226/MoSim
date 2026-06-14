from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_post_review_shared_tail_deduplication_note.py"


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


def test_current_shared_tail_deduplication_note_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["action_count"] == 3
    assert stdout["shared_tail_family_count"] == 12
    assert stdout["shared_tail_action_coverage_issue_count"] == 0
    assert stdout["action_specific_prefix_group_count"] == 3
    assert stdout["runs_commands_now"] is False
    assert stdout["applies_transitions_now"] is False
    assert stdout["edits_decision_artifacts_now"] is False
    assert stdout["generates_final_outputs"] is False
    assert stdout["final_acceptance"] is False

    note = json.loads(
        (tmp_path / "final_submission_post_review_shared_tail_deduplication_note.json").read_text(encoding="utf-8")
    )
    assert note["status"] == "post_review_shared_tail_deduplication_note_not_execution"
    assert len(note["shared_tail_families"]) == 12
    assert all(record["action_count"] == 3 for record in note["shared_tail_families"])
    assert any(record["family"] == "final_submission_dashboard" for record in note["shared_tail_families"])
    assert len(note["action_specific_prefixes_not_deduped"]) == 3
    assert "It does not deduplicate executed work now." in note["claim_boundary"]
    assert "It does not write PMO final acceptance." in note["claim_boundary"]

    markdown = (tmp_path / "final_submission_post_review_shared_tail_deduplication_note.md").read_text(
        encoding="utf-8"
    )
    assert "## Deduplication Rules" in markdown
    assert "## Shared-Tail Families" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_post_review_shared_tail_deduplication_note_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_shared_tail_deduplication_note_builds(temp / "current")
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
    print("[OK] final submission post-review shared-tail deduplication note tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
