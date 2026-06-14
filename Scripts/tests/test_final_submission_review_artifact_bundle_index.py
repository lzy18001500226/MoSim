from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_review_artifact_bundle_index.py"


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


def test_current_review_artifact_bundle_index_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["bundle_artifact_count"] == 7
    assert stdout["ready_bundle_artifact_count"] == 7
    assert stdout["missing_or_incomplete_count"] == 0
    assert stdout["status_mismatch_count"] == 0
    assert stdout["automated_execution_allowed"] is False

    bundle = json.loads((tmp_path / "final_submission_review_artifact_bundle_index.json").read_text(encoding="utf-8"))
    assert bundle["status"] == "review_artifact_bundle_index_not_execution"
    assert bundle["summary"]["included_in_static_audit_index"] is False
    assert bundle["summary"]["generates_final_outputs"] is False
    assert bundle["summary"]["final_acceptance"] is False
    assert [item["artifact_id"] for item in bundle["artifacts"]] == [
        "blocked_gate_triage_map",
        "human_decision_diff_template",
        "reviewer_quickstart",
        "review_progress_snapshot",
        "post_review_rerun_matrix",
        "manual_review_answer_sheet",
        "answer_sheet_decision_consistency",
    ]
    assert all(item["ready_for_review_bundle"] is True for item in bundle["artifacts"])
    assert "It is intentionally not added back into final_submission_static_audit_index.json." in bundle[
        "claim_boundary"
    ]

    markdown = (tmp_path / "final_submission_review_artifact_bundle_index.md").read_text(encoding="utf-8")
    assert "## Review Order" in markdown
    assert "manual_review_answer_sheet" in markdown


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_review_artifact_bundle_index_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_review_artifact_bundle_index_builds(temp / "current")
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
    print("[OK] final submission review artifact bundle index tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
