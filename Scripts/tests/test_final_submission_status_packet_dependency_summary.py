from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_status_packet_dependency_summary.py"
STATUS_SKELETON = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_submission_human_review_status_packet_skeleton_20260610"
    / "final_submission_human_review_status_packet_skeleton.json"
)


def load_builder():
    spec = importlib.util.spec_from_file_location("build_final_submission_status_packet_dependency_summary", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_final_submission_status_packet_dependency_summary.py")
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


def test_current_status_packet_dependency_summary_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["dashboard_blocker_count"] == 16
    assert stdout["prerequisite_class_count"] >= 5
    assert stdout["mapped_action_count"] == 6
    assert stdout["execution_target_count"] == 4
    assert stdout["blocked_execution_target_count"] == 4
    assert stdout["satisfies_dependencies_now"] is False
    assert stdout["runs_commands_now"] is False
    assert stdout["authorizes_execution_now"] is False
    assert stdout["generates_final_outputs"] is False
    assert stdout["final_acceptance"] is False

    summary = json.loads((tmp_path / "final_submission_status_packet_dependency_summary.json").read_text(encoding="utf-8"))
    assert summary["status"] == "status_packet_dependency_summary_not_execution"
    classes = {item["prerequisite_class"] for item in summary["prerequisite_classes"]}
    assert "report_source_review" in classes
    assert "pdf_engine" in classes
    assert "demo_storyboard_and_video" in classes
    assert "final_artifact_creation" in classes
    assert "final_output_execution_decision" in classes
    assert summary["action_to_prerequisite_classes"]["A1-approve-or-reject-report-source-edits"]
    assert summary["action_to_prerequisite_classes"]["A2-provide-pdf-engine"]
    assert summary["action_to_prerequisite_classes"]["A3-review-demo-storyboard"]
    assert summary["action_to_prerequisite_classes"]["A4-create-reviewed-final-artifacts"]
    assert summary["action_to_prerequisite_classes"]["A5-rerun-readiness-gates"]
    assert summary["action_to_prerequisite_classes"]["A6-review-final-output-execution-decision"]
    assert len(summary["blocker_rows"]) == 16
    assert "It does not satisfy prerequisites." in summary["claim_boundary"]
    assert "It does not run post-review commands." in summary["claim_boundary"]

    markdown = (tmp_path / "final_submission_status_packet_dependency_summary.md").read_text(encoding="utf-8")
    assert "## Prerequisite Classes" in markdown
    assert "report_source_review" in markdown


def test_reports_bad_status_skeleton_status(tmp_path: Path) -> None:
    builder = load_builder()
    skeleton = json.loads(STATUS_SKELETON.read_text(encoding="utf-8"))
    skeleton["status"] = "unexpected_status"
    skeleton_path = tmp_path / "bad_status_skeleton.json"
    skeleton_path.parent.mkdir(parents=True, exist_ok=True)
    skeleton_path.write_text(json.dumps(skeleton), encoding="utf-8")
    summary = builder.build_summary(
        skeleton_path,
        builder.DEFAULT_AUTHORIZATION_BLOCKERS,
        builder.DEFAULT_SHORTEST_PATH,
    )
    assert summary["summary"]["issue_count"] >= 1
    assert any("status skeleton status" in issue for issue in summary["issues"])


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_status_packet_dependency_summary_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_status_packet_dependency_summary_builds(temp / "current")
        test_reports_bad_status_skeleton_status(temp / "bad_status")
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
    print("[OK] final submission status-packet dependency summary tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
