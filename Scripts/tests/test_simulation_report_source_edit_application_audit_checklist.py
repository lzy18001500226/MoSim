from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_simulation_report_source_edit_application_audit_checklist.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_simulation_report_source_edit_application_audit_checklist", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_simulation_report_source_edit_application_audit_checklist.py")
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


def test_current_audit_checklist_blocks_application(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["pre_edit_check_count"] == 7
    assert stdout["post_edit_guard_command_count"] >= 10
    assert stdout["safe_to_apply_report_source_edits_now"] is False
    assert stdout["applies_report_source_edits_now"] is False

    checklist = json.loads(
        (tmp_path / "simulation_report_source_edit_application_audit_checklist.json").read_text(encoding="utf-8")
    )
    assert checklist["status"] == "source_edit_application_audit_checklist_not_execution"
    assert checklist["summary"]["decision_authorizes_application"] is False
    assert checklist["summary"]["application_plan_safe_to_apply"] is False
    assert checklist["summary"]["creates_backup_now"] is False
    assert checklist["summary"]["edits_report_source"] is False
    assert checklist["summary"]["runs_post_edit_guards_now"] is False
    assert "It does not edit Docs/simulation_report.md." in checklist["claim_boundary"]


def test_safe_inputs_still_do_not_apply(tmp_path: Path) -> None:
    builder = load_builder()
    tmp_path.mkdir(parents=True, exist_ok=True)
    application_path = tmp_path / "application.json"
    reviewer_path = tmp_path / "reviewer.json"
    decision_path = tmp_path / "decision.json"
    application_path.write_text(
        json.dumps({"summary": {"safe_to_apply_report_source_edits_now": True}}),
        encoding="utf-8",
    )
    reviewer_path.write_text(
        json.dumps({"summary": {"manual_review_required_count": 7}}),
        encoding="utf-8",
    )
    decision_path.write_text(json.dumps({"authorizes_application": True}), encoding="utf-8")
    checklist = builder.build_checklist(application_path, reviewer_path, decision_path)
    assert checklist["summary"]["safe_to_apply_report_source_edits_now"] is True
    assert checklist["summary"]["edits_report_source"] is False
    assert checklist["summary"]["applies_report_source_edits_now"] is False
    assert checklist["summary"]["creates_backup_now"] is False
    assert checklist["summary"]["runs_post_edit_guards_now"] is False


def main() -> int:
    temp = ROOT / ".tmp" / "simulation_report_source_edit_application_audit_checklist_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_audit_checklist_blocks_application(temp / "current")
        test_safe_inputs_still_do_not_apply(temp / "safe")
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
    print("[OK] simulation report source edit application audit checklist tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
