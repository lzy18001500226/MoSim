from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_reviewer_packet_index.py"


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


def test_current_reviewer_packet_index_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["packet_count"] == 3
    assert stdout["pending_packet_count"] == 3
    assert stdout["total_answer_field_count"] == 38
    assert stdout["required_answer_field_count"] == 29
    assert stdout["total_rerun_command_count"] == 45
    assert stdout["fills_answers_now"] is False
    assert stdout["copies_answers_now"] is False
    assert stdout["edits_decision_artifacts_now"] is False
    assert stdout["runs_rerun_commands_now"] is False
    assert stdout["generates_final_outputs"] is False
    assert stdout["final_acceptance"] is False

    index = json.loads((tmp_path / "final_submission_reviewer_packet_index.json").read_text(encoding="utf-8"))
    assert index["status"] == "reviewer_packet_index_not_execution"
    assert [packet["action_id"] for packet in index["review_packets"]] == [
        "A1-approve-or-reject-report-source-edits",
        "A3-review-demo-storyboard",
        "A6-review-final-output-execution-decision",
    ]
    assert index["review_packets"][0]["review_artifact_count"] >= 5
    assert index["review_packets"][0]["answer_field_count"] == 8
    assert index["review_packets"][1]["answer_field_count"] == 15
    assert index["review_packets"][2]["answer_field_count"] == 15
    assert "It does not fill answer-sheet fields." in index["claim_boundary"]
    assert "It does not run post-review rerun commands." in index["claim_boundary"]

    markdown = (tmp_path / "final_submission_reviewer_packet_index.md").read_text(encoding="utf-8")
    assert "A1-approve-or-reject-report-source-edits" in markdown
    assert "A6-review-final-output-execution-decision" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_reviewer_packet_index_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_reviewer_packet_index_builds(temp / "current")
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
    print("[OK] final submission reviewer packet index tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
