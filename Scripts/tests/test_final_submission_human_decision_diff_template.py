from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_human_decision_diff_template.py"


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


def test_current_human_decision_diff_template_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["report_source_field_count"] == 8
    assert stdout["final_output_action_count"] == 3
    assert stdout["final_output_field_count"] == 15
    assert stdout["applies_decisions_now"] is False

    template = json.loads((tmp_path / "final_submission_human_decision_diff_template.json").read_text(encoding="utf-8"))
    assert template["status"] == "human_decision_diff_template_not_execution"
    assert template["summary"]["edits_decision_templates_now"] is False
    assert template["summary"]["generates_final_outputs"] is False
    assert template["summary"]["final_acceptance"] is False
    group_ids = [group["decision_group_id"] for group in template["decision_groups"]]
    assert group_ids == [
        "A1-report-source-edit-decision",
        "A6-final-output-execution-decision",
    ]

    report_fields = {
        field["field_path"]
        for field in template["decision_groups"][0]["field_changes"]
    }
    assert "decision" in report_fields
    assert "approved_preview_ids" in report_fields
    assert "safe_to_apply_report_source_edits" in report_fields

    execution_fields = {
        field["field_path"]
        for field in template["decision_groups"][1]["field_changes"]
    }
    assert "actions.pdf_export.decision" in execution_fields
    assert "actions.demo_video_recording.approved" in execution_fields
    assert "actions.final_acceptance_packet.approved_at" in execution_fields
    assert "It does not approve pending decisions." in template["claim_boundary"]

    markdown = (tmp_path / "final_submission_human_decision_diff_template.md").read_text(encoding="utf-8")
    assert "A1-report-source-edit-decision" in markdown
    assert "A6-final-output-execution-decision" in markdown
    assert "safe_to_apply_report_source_edits" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_human_decision_diff_template_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_human_decision_diff_template_builds(temp / "current")
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
    print("[OK] final submission human decision diff template tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
