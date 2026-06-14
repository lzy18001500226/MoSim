from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_manual_review_shortest_path_note.py"
DIGEST = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_execution_blocker_owner_status_digest_20260610"
    / "final_submission_execution_blocker_owner_status_digest.json"
)


def load_builder():
    spec = importlib.util.spec_from_file_location("build_final_submission_manual_review_shortest_path_note", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_final_submission_manual_review_shortest_path_note.py")
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


def test_current_shortest_path_note_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["path_step_count"] == 6
    assert stdout["human_review_action_count"] == 3
    assert stdout["no_packet_action_count"] == 3
    assert stdout["independent_start_action_count"] == 3
    assert stdout["blocked_execution_target_count"] == 4
    assert stdout["target_action_reference_count"] == 16
    assert stdout["dashboard_blocker_count"] == 16
    assert stdout["reviewer_open_file_count"] == 21
    assert stdout["reviewer_open_file_drift_count"] == 0
    assert stdout["issue_count"] == 0
    assert stdout["runs_commands_now"] is False
    assert stdout["authorizes_execution_now"] is False
    assert stdout["generates_final_outputs"] is False
    assert stdout["final_acceptance"] is False

    note = json.loads((tmp_path / "final_submission_manual_review_shortest_path_note.json").read_text(encoding="utf-8"))
    assert note["status"] == "manual_review_shortest_path_note_not_execution"
    assert [step["action_id"] for step in note["shortest_path"]] == [
        "A1-approve-or-reject-report-source-edits",
        "A3-review-demo-storyboard",
        "A2-provide-pdf-engine",
        "A6-review-final-output-execution-decision",
        "A4-create-reviewed-final-artifacts",
        "A5-rerun-readiness-gates",
    ]
    action_steps = {step["action_id"]: step for step in note["shortest_path"]}
    assert action_steps["A6-review-final-output-execution-decision"]["prerequisite_action_ids"] == [
        "A1-approve-or-reject-report-source-edits",
        "A2-provide-pdf-engine",
        "A3-review-demo-storyboard",
    ]
    assert "A6-review-final-output-execution-decision" in action_steps[
        "A4-create-reviewed-final-artifacts"
    ]["prerequisite_action_ids"]
    assert "A4-create-reviewed-final-artifacts" in action_steps["A5-rerun-readiness-gates"][
        "prerequisite_action_ids"
    ]
    assert "It does not run commands." in note["claim_boundary"]

    markdown = (tmp_path / "final_submission_manual_review_shortest_path_note.md").read_text(encoding="utf-8")
    assert "## Shortest Path" in markdown
    assert "A6-review-final-output-execution-decision" in markdown


def test_reports_missing_expected_action(tmp_path: Path) -> None:
    builder = load_builder()
    digest = json.loads(DIGEST.read_text(encoding="utf-8"))
    digest["actions"] = [
        action
        for action in digest["actions"]
        if action["action_id"] != "A6-review-final-output-execution-decision"
    ]
    digest_path = tmp_path / "missing_a6_digest.json"
    digest_path.parent.mkdir(parents=True, exist_ok=True)
    digest_path.write_text(json.dumps(digest), encoding="utf-8")
    note = builder.build_note(digest_path)
    assert note["summary"]["issue_count"] >= 1
    assert any("missing expected actions" in issue for issue in note["issues"])


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_manual_review_shortest_path_note_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_shortest_path_note_builds(temp / "current")
        test_reports_missing_expected_action(temp / "missing_action")
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
    print("[OK] final submission manual-review shortest-path note tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
