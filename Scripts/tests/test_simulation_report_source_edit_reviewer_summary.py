from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_simulation_report_source_edit_reviewer_summary.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_simulation_report_source_edit_reviewer_summary", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_simulation_report_source_edit_reviewer_summary.py")
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


def test_current_reviewer_summary_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["preview_count"] == 7
    assert stdout["high_impact_count"] == 2
    assert stdout["candidate_insert_count"] == 3
    assert stdout["automated_execution_allowed"] is False

    summary = json.loads((tmp_path / "simulation_report_source_edit_reviewer_summary.json").read_text(encoding="utf-8"))
    assert summary["status"] == "source_edit_reviewer_summary_not_execution"
    assert summary["summary"]["missing_sequence_action_count"] == 0
    assert summary["summary"]["manual_review_required_count"] == 7
    assert summary["summary"]["edits_report_source"] is False
    assert summary["summary"]["applies_report_source_edits_now"] is False
    assert summary["summary"]["final_acceptance"] is False
    assert all(item["applies_now"] is False for item in summary["review_items"])
    assert "It does not edit Docs/报告/仿真分析报告_正文骨架.md." in summary["claim_boundary"]


def test_missing_sequence_action_is_reported() -> None:
    builder = load_builder()
    preview = {
        "previews": [
            {
                "preview_id": "unknown_preview",
                "source_action_id": "unknown_action",
                "operation": "manual",
                "target": "target",
                "safety_boundary": "boundary",
            }
        ]
    }
    sequence = {"actions": []}
    application_plan = {"application_steps": []}
    preview_path = ROOT / ".tmp" / "source_edit_reviewer_summary_missing_preview.json"
    sequence_path = ROOT / ".tmp" / "source_edit_reviewer_summary_missing_sequence.json"
    application_path = ROOT / ".tmp" / "source_edit_reviewer_summary_missing_application.json"
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        preview_path.write_text(json.dumps(preview), encoding="utf-8")
        sequence_path.write_text(json.dumps(sequence), encoding="utf-8")
        application_path.write_text(json.dumps(application_plan), encoding="utf-8")
        summary = builder.build_summary(preview_path, sequence_path, application_path)
        assert summary["summary"]["missing_sequence_action_count"] == 1
        assert summary["missing_sequence_actions"] == ["unknown_action"]
    finally:
        for path in [preview_path, sequence_path, application_path]:
            if path.exists():
                path.unlink()
        tmp_root = ROOT / ".tmp"
        if tmp_root.exists() and not any(tmp_root.iterdir()):
            tmp_root.rmdir()


def main() -> int:
    temp = ROOT / ".tmp" / "simulation_report_source_edit_reviewer_summary_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_reviewer_summary_builds(temp / "current")
        test_missing_sequence_action_is_reported()
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
    print("[OK] simulation report source edit reviewer summary tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
