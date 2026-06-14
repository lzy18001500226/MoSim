from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_reviewer_action_map.py"


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


def test_current_reviewer_action_map_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["action_count"] == 6
    assert stdout["missing_review_artifact_count"] == 0
    assert stdout["automated_execution_allowed"] is False

    action_map = json.loads((tmp_path / "final_submission_reviewer_action_map.json").read_text(encoding="utf-8"))
    assert action_map["status"] == "reviewer_action_map_not_execution"
    assert action_map["summary"]["action_count"] == 6
    assert action_map["summary"]["generates_final_outputs"] is False
    assert action_map["summary"]["final_acceptance"] is False
    assert action_map["missing_review_artifacts"] == []
    assert action_map["human_review_decision_packet_template"].endswith(
        "final_submission_human_review_decision_packet.template.json"
    )
    action_ids = [item["action_id"] for item in action_map["actions"]]
    assert action_ids == [
        "A1-approve-or-reject-report-source-edits",
        "A2-provide-pdf-engine",
        "A3-review-demo-storyboard",
        "A4-create-reviewed-final-artifacts",
        "A5-rerun-readiness-gates",
        "A6-review-final-output-execution-decision",
    ]
    assert action_map["actions"][0]["decision_owner"] == "user_or_PMO"
    assert action_map["actions"][0]["decision_artifact"].endswith("report_source_edit_decision.template.json")
    assert any(
        item["path"].endswith("simulation_report_source_edit_application_plan.md")
        for item in action_map["actions"][0]["review_artifacts"]
    )
    assert "python Scripts/quality/build_simulation_report_source_edit_application_plan.py" in action_map["actions"][0][
        "rerun_after_decision"
    ]
    assert "It does not write PMO final acceptance." in action_map["claim_boundary"]


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_reviewer_action_map_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_reviewer_action_map_builds(temp / "current")
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
    print("[OK] final submission reviewer action map tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
