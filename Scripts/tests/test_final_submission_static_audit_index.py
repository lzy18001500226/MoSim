from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_static_audit_index.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_final_submission_static_audit_index", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_final_submission_static_audit_index.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def test_current_static_audit_index_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    summary = json.loads(completed.stdout)
    assert summary["ok"] is True
    assert summary["readme"] == (tmp_path / "README.md").relative_to(ROOT).as_posix()
    assert summary["artifact_count"] == 18
    assert summary["blocked_count"] == 17
    assert summary["final_submission_ready"] is False

    index_path = tmp_path / "final_submission_static_audit_index.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))
    assert index["status"] == "static_audit_index_not_final_submission"
    assert index["summary"]["missing_count"] == 0
    assert index["summary"]["unreadable_count"] == 0
    assert index["summary"]["ready_count"] == 1
    assert index["summary"]["generates_final_outputs"] is False
    assert index["summary"]["final_acceptance"] is False
    assert {item["artifact_id"] for item in index["artifacts"]} == {
        "report_source_edit_decision",
        "source_edit_readiness",
        "source_edit_application_plan",
        "source_edit_reviewer_summary",
        "source_edit_application_audit_checklist",
        "source_output_readiness",
        "pdf_export_plan",
        "demo_video_storyboard",
        "final_artifact_manifest",
        "final_acceptance_prereq",
        "final_output_execution_decision",
        "final_submission_dashboard",
        "final_submission_human_action_checklist",
        "final_submission_reviewer_action_map",
        "final_submission_human_review_decision_packet",
        "final_submission_human_review_guide",
        "final_submission_readiness_chain",
        "final_submission_refresh_order",
    }

    readme_text = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "## Hard Gates" in readme_text
    assert "## Review Aids" in readme_text
    assert "source_edit_application_audit_checklist" in readme_text
    assert "They do not authorize report-source edits" in readme_text
    assert "This README does not authorize PDF export" in readme_text


def test_missing_artifact_remains_not_ready() -> None:
    builder = load_builder()
    record = builder.artifact_record(
        {
            "artifact_id": "missing_example",
            "path": "Results/static_audits/does_not_exist_20260610/missing.json",
            "status_field": "status",
            "ready_path": ["summary", "ready"],
            "role": "test missing handling",
        }
    )
    assert record["exists"] is False
    assert record["ready"] is False
    assert record["status"] == "missing"


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_static_audit_index_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_static_audit_index_builds(temp / "current")
        test_missing_artifact_remains_not_ready()
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
    print("[OK] final submission static audit index tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
