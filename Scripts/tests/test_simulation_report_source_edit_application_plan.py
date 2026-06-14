from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_simulation_report_source_edit_application_plan.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_simulation_report_source_edit_application_plan", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_simulation_report_source_edit_application_plan.py")
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


def test_current_application_plan_is_blocked(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["ok"] is True
    assert stdout["status"] == "source_edit_application_plan_blocked_pending_human_review"
    assert stdout["planned_application_count"] == 0
    assert stdout["safe_to_apply_report_source_edits_now"] is False

    plan = json.loads((tmp_path / "simulation_report_source_edit_application_plan.json").read_text(encoding="utf-8"))
    assert plan["summary"]["preview_count"] == 7
    assert plan["summary"]["approved_preview_count"] == 0
    assert plan["summary"]["edits_report_source"] is False
    assert plan["summary"]["applies_report_source_edits_now"] is False
    assert plan["summary"]["generates_final_outputs"] is False
    assert plan["summary"]["final_acceptance"] is False
    assert all(step["applies_now"] is False for step in plan["application_steps"])
    assert "It does not edit Docs/simulation_report.md." in plan["claim_boundary"]


def test_ready_plan_still_does_not_apply(tmp_path: Path) -> None:
    builder = load_builder()
    tmp_path.mkdir(parents=True, exist_ok=True)
    preview_path = ROOT / "Results/static_audits/simulation_report_patch_preview_20260610/simulation_report_patch_preview.json"
    decision_path = tmp_path / "decision.json"
    decision_check_path = tmp_path / "decision_check.json"
    readiness_path = tmp_path / "readiness.json"

    decision = json.loads(
        (ROOT / "Results/static_audits/report_source_edit_decision_template_20260610/report_source_edit_decision.template.json").read_text(
            encoding="utf-8"
        )
    )
    decision["decision"] = "approved"
    decision["approved_preview_ids"] = ["renumber_l1_residual_subsection_preview"]
    decision["safe_to_apply_report_source_edits"] = True
    decision_path.write_text(json.dumps(decision), encoding="utf-8")
    decision_check_path.write_text(json.dumps({"authorizes_application": True}), encoding="utf-8")
    readiness_path.write_text(
        json.dumps({"summary": {"safe_to_apply_report_source_edits_now": True}}),
        encoding="utf-8",
    )

    plan = builder.build_plan(preview_path, decision_path, decision_check_path, readiness_path)
    assert plan["status"] == "source_edit_application_plan_ready_not_applied"
    assert plan["summary"]["planned_application_count"] == 1
    assert plan["summary"]["safe_to_apply_report_source_edits_now"] is True
    assert plan["summary"]["edits_report_source"] is False
    assert plan["summary"]["applies_report_source_edits_now"] is False
    assert all(step["applies_now"] is False for step in plan["application_steps"])


def main() -> int:
    temp = ROOT / ".tmp" / "simulation_report_source_edit_application_plan_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_application_plan_is_blocked(temp / "current")
        test_ready_plan_still_does_not_apply(temp / "ready")
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
    print("[OK] simulation report source edit application plan tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
