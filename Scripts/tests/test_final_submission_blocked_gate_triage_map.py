from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_blocked_gate_triage_map.py"


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


def test_current_blocked_gate_triage_map_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["blocked_artifact_count"] == 17
    assert stdout["dashboard_blocker_count"] == 16
    assert stdout["automated_execution_allowed"] is False

    triage_map = json.loads((tmp_path / "final_submission_blocked_gate_triage_map.json").read_text(encoding="utf-8"))
    assert triage_map["status"] == "blocked_gate_triage_map_not_execution"
    assert triage_map["summary"]["blocked_artifact_count"] == 17
    assert triage_map["summary"]["generates_final_outputs"] is False
    assert triage_map["summary"]["final_acceptance"] is False
    assert "human_report_source_decision" in triage_map["blocker_classes"]
    assert "review_aid_not_execution" in triage_map["blocker_classes"]

    by_artifact = {item["artifact_id"]: item for item in triage_map["blocked_artifacts"]}
    assert "final_submission_refresh_order" not in by_artifact
    assert by_artifact["source_edit_readiness"]["blocker_class"] == "human_report_source_decision"
    assert by_artifact["source_edit_readiness"]["linked_human_actions"][0]["action_id"] == (
        "A1-approve-or-reject-report-source-edits"
    )
    assert "python Scripts/quality/build_pdf_export_dry_run_plan.py" in by_artifact["pdf_export_plan"][
        "safe_rerun_commands"
    ]
    assert by_artifact["source_edit_reviewer_summary"]["blocker_class"] == "review_aid_not_execution"
    assert "It does not execute safe rerun commands." in triage_map["claim_boundary"]

    markdown = (tmp_path / "final_submission_blocked_gate_triage_map.md").read_text(encoding="utf-8")
    assert "## Blocker Classes" in markdown
    assert "## Blocked Artifacts" in markdown
    assert "human_report_source_decision" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_blocked_gate_triage_map_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_blocked_gate_triage_map_builds(temp / "current")
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
    print("[OK] final submission blocked gate triage map tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
