from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_human_review_status_packet_skeleton.py"
ANSWER_SHEET = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_manual_review_answer_sheet_20260610"
    / "final_submission_manual_review_answer_sheet.template.json"
)


def load_builder():
    spec = importlib.util.spec_from_file_location("build_final_submission_human_review_status_packet_skeleton", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_final_submission_human_review_status_packet_skeleton.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_builder(output_dir: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--output-dir",
            str(output_dir.relative_to(ROOT)),
            *extra_args,
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_human_review_status_packet_skeleton_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["review_action_count"] == 3
    assert stdout["reviewer_packet_action_count"] == 3
    assert stdout["no_packet_action_count"] == 3
    assert stdout["pending_field_count"] == 38
    assert stdout["required_pending_field_count"] == 29
    assert stdout["review_question_count"] == 9
    assert stdout["blocked_execution_target_count"] == 4
    assert stdout["dashboard_blocking_gate_count"] == 7
    assert stdout["dashboard_blocker_count"] == 16
    assert stdout["fills_answers_now"] is False
    assert stdout["edits_decision_artifacts_now"] is False
    assert stdout["runs_commands_now"] is False
    assert stdout["authorizes_execution_now"] is False
    assert stdout["generates_final_outputs"] is False
    assert stdout["final_acceptance"] is False

    skeleton = json.loads((tmp_path / "final_submission_human_review_status_packet_skeleton.json").read_text(encoding="utf-8"))
    assert skeleton["status"] == "human_review_status_packet_skeleton_not_execution"
    assert [action["action_id"] for action in skeleton["review_actions"]] == [
        "A1-approve-or-reject-report-source-edits",
        "A3-review-demo-storyboard",
        "A6-review-final-output-execution-decision",
    ]
    assert skeleton["summary"]["minimum_open_file_count"] == 10
    assert skeleton["summary"]["unique_open_file_count"] == 21
    assert skeleton["no_packet_actions"] == [
        "A2-provide-pdf-engine",
        "A4-create-reviewed-final-artifacts",
        "A5-rerun-readiness-gates",
    ]
    assert "It intentionally leaves human-review fields blank." in skeleton["claim_boundary"]
    assert "It does not edit report-source or final-output decision templates." in skeleton["claim_boundary"]

    markdown = (tmp_path / "final_submission_human_review_status_packet_skeleton.md").read_text(encoding="utf-8")
    assert "## Review Actions" in markdown
    assert "## Upstream Change Requirements" in markdown
    assert "A1-approve-or-reject-report-source-edits" in markdown


def test_reports_bad_source_status(tmp_path: Path) -> None:
    builder = load_builder()
    answer_sheet = json.loads(ANSWER_SHEET.read_text(encoding="utf-8"))
    answer_sheet["status"] = "unexpected_status"
    answer_path = tmp_path / "bad_answer_sheet.json"
    answer_path.parent.mkdir(parents=True, exist_ok=True)
    answer_path.write_text(json.dumps(answer_sheet), encoding="utf-8")
    skeleton = builder.build_skeleton(
        answer_path,
        builder.DEFAULT_EXECUTION_GATE,
        builder.DEFAULT_AUTHORIZATION_BLOCKERS,
        builder.DEFAULT_DASHBOARD,
        builder.DEFAULT_OPEN_FILE_BUNDLE,
    )
    assert skeleton["summary"]["issue_count"] >= 1
    assert any("answer_sheet status" in issue for issue in skeleton["issues"])


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_human_review_status_packet_skeleton_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_human_review_status_packet_skeleton_builds(temp / "current")
        test_reports_bad_source_status(temp / "bad_source_status")
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
    print("[OK] final submission human-review status packet skeleton tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
