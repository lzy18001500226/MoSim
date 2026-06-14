from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_reviewer_evidence_index.py"
ACTION_MAP = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_reviewer_action_map_20260610"
    / "final_submission_reviewer_action_map.json"
)


def load_builder():
    spec = importlib.util.spec_from_file_location("build_final_submission_reviewer_evidence_index", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_final_submission_reviewer_evidence_index.py")
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


def test_current_reviewer_evidence_index_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["action_count"] == 6
    assert stdout["reviewer_packet_action_count"] == 3
    assert stdout["no_packet_action_count"] == 3
    assert stdout["unique_review_evidence_file_count"] == 21
    assert stdout["missing_review_evidence_file_count"] == 0
    assert stdout["issue_count"] == 0
    assert stdout["pdf_export_still_forbidden"] is True
    assert stdout["demo_recording_still_forbidden"] is True
    assert stdout["final_acceptance_still_forbidden"] is True
    assert stdout["live_tools_still_forbidden"] is True
    assert stdout["visible_thread_dispatch_still_forbidden"] is True
    assert stdout["fills_answers_now"] is False
    assert stdout["edits_decision_artifacts_now"] is False
    assert stdout["runs_commands_now"] is False
    assert stdout["authorizes_execution_now"] is False
    assert stdout["generates_final_outputs"] is False
    assert stdout["final_acceptance"] is False

    index = json.loads((tmp_path / "final_submission_reviewer_evidence_index.json").read_text(encoding="utf-8"))
    actions = {row["action_id"]: row for row in index["review_actions"]}
    assert set(actions) == {
        "A1-approve-or-reject-report-source-edits",
        "A2-provide-pdf-engine",
        "A3-review-demo-storyboard",
        "A4-create-reviewed-final-artifacts",
        "A5-rerun-readiness-gates",
        "A6-review-final-output-execution-decision",
    }
    assert actions["A1-approve-or-reject-report-source-edits"]["packet_class"] == "reviewer_packet"
    assert actions["A3-review-demo-storyboard"]["packet_class"] == "reviewer_packet"
    assert actions["A6-review-final-output-execution-decision"]["packet_class"] == "reviewer_packet"
    assert actions["A2-provide-pdf-engine"]["packet_class"] == "no_packet_escalation"
    assert actions["A4-create-reviewed-final-artifacts"]["packet_class"] == "no_packet_escalation"
    assert actions["A5-rerun-readiness-gates"]["packet_class"] == "no_packet_escalation"
    assert actions["A2-provide-pdf-engine"]["escalation_class"] == "environment_dependency"
    assert actions["A4-create-reviewed-final-artifacts"]["escalation_class"] == "final_artifact_creation"
    assert actions["A5-rerun-readiness-gates"]["escalation_class"] == "post_change_gate_rerun"
    for action in actions.values():
        assert action["missing_review_evidence_file_count"] == 0
        assert action["fills_answers_now"] is False
        assert action["edits_decision_artifacts_now"] is False
        assert action["runs_commands_now"] is False
        assert action["authorizes_execution_now"] is False
        assert action["generates_final_outputs"] is False
        assert action["final_acceptance"] is False
    assert "It does not run commands." in index["claim_boundary"]

    markdown = (tmp_path / "final_submission_reviewer_evidence_index.md").read_text(encoding="utf-8")
    assert "## Review Actions" in markdown
    assert "A2-provide-pdf-engine" in markdown


def test_rejects_missing_review_evidence_file(tmp_path: Path) -> None:
    builder = load_builder()
    broken_action_map = tmp_path / "broken_action_map.json"
    action_map = json.loads(ACTION_MAP.read_text(encoding="utf-8"))
    action_map["actions"][0]["review_artifacts"][0]["path"] = "Results/static_audits/missing-review-file.md"
    broken_action_map.parent.mkdir(parents=True, exist_ok=True)
    broken_action_map.write_text(json.dumps(action_map), encoding="utf-8")
    index = builder.build_index(
        broken_action_map,
        builder.DEFAULT_QUICKSTART,
        builder.DEFAULT_PACKET_INDEX,
        builder.DEFAULT_NO_PACKET_NOTE,
        builder.DEFAULT_FORBIDDEN_GUARD,
    )
    assert index["summary"]["issue_count"] == 1
    assert any("missing required evidence files" in issue for issue in index["issues"])


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_reviewer_evidence_index_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_reviewer_evidence_index_builds(temp / "current")
        test_rejects_missing_review_evidence_file(temp / "missing_file")
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
    print("[OK] final submission reviewer evidence index tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
