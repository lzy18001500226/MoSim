from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_human_review_execution_gate_summary.py"


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


def test_current_execution_gate_summary_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["execution_target_count"] == 4
    assert stdout["blocked_execution_target_count"] == 4
    assert stdout["dashboard_blocking_gate_count"] == 7
    assert stdout["dashboard_blocker_count"] == 16
    assert stdout["review_action_count"] == 3
    assert stdout["total_question_count"] == 9
    assert stdout["answers_questions_now"] is False
    assert stdout["edits_decision_artifacts_now"] is False
    assert stdout["runs_commands_now"] is False
    assert stdout["creates_submission_dir_now"] is False
    assert stdout["runs_pandoc_now"] is False
    assert stdout["records_or_renders_video_now"] is False
    assert stdout["writes_canonical_acceptance_packet_now"] is False
    assert stdout["generates_final_outputs"] is False
    assert stdout["final_acceptance"] is False

    result = json.loads(
        (tmp_path / "final_submission_human_review_execution_gate_summary.json").read_text(encoding="utf-8")
    )
    assert result["status"] == "human_review_execution_gate_summary_not_execution"
    targets = {item["target_id"]: item for item in result["execution_targets"]}
    assert set(targets) == {
        "report_source_edit",
        "pdf_export",
        "demo_video_recording",
        "final_acceptance_packet",
    }
    assert all(item["ready_now"] is False for item in targets.values())
    assert targets["pdf_export"]["readiness_flags"]["safe_to_run_pdf_export_now"] is False
    assert targets["final_acceptance_packet"]["readiness_flags"]["safe_to_write_final_acceptance_packet_now"] is False
    assert "It does not run Pandoc." in result["claim_boundary"]
    assert "It does not write canonical PMO final acceptance." in result["claim_boundary"]

    markdown = (tmp_path / "final_submission_human_review_execution_gate_summary.md").read_text(encoding="utf-8")
    assert "## Execution Targets" in markdown
    assert "pdf_export" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_human_review_execution_gate_summary_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_execution_gate_summary_builds(temp / "current")
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
    print("[OK] final submission human-review execution gate summary tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
