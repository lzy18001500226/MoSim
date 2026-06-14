from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_submission_human_review_decision_packet_template.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_final_submission_human_review_decision_packet_template", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_final_submission_human_review_decision_packet_template.py")
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


def test_current_human_review_decision_packet_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["decision_count"] == 3
    assert stdout["pending_decision_count"] == 3
    assert stdout["automated_execution_allowed"] is False

    artifact = json.loads(
        (tmp_path / "final_submission_human_review_decision_packet_template.json").read_text(encoding="utf-8")
    )
    assert artifact["status"] == "human_review_decision_packet_pending_review_not_execution"
    assert artifact["summary"]["generates_final_outputs"] is False
    assert artifact["summary"]["final_acceptance"] is False
    decisions = artifact["template"]["decisions"]
    assert set(decisions) == {
        "A1-approve-or-reject-report-source-edits",
        "A3-review-demo-storyboard",
        "A6-review-final-output-execution-decision",
    }
    assert all(item["decision"] == "pending_review" for item in decisions.values())
    assert all(item["approved"] is False for item in decisions.values())
    assert "It does not create final outputs or PMO final acceptance." in artifact["claim_boundary"]


def test_rejects_approved_pending_decision() -> None:
    builder = load_builder()
    template = builder.build_template(
        ROOT
        / "Results/static_audits/final_submission_reviewer_action_map_20260610"
        / "final_submission_reviewer_action_map.json"
    )
    first = template["decisions"]["A1-approve-or-reject-report-source-edits"]
    first["decision"] = "pending_review"
    first["approved"] = True
    result = builder.validate_template(template)
    assert result["ok"] is False
    assert any("pending_review must keep approved=false" in issue for issue in result["issues"])


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_human_review_decision_packet_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_human_review_decision_packet_builds(temp / "current")
        test_rejects_approved_pending_decision()
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
    print("[OK] final submission human review decision packet tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
