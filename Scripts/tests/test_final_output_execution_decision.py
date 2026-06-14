from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_output_execution_decision_template.py"
CHECKER = ROOT / "Scripts" / "quality" / "check_final_output_execution_decision.py"
PDF_PLAN = ROOT / "Results/static_audits/pdf_export_dry_run_plan_20260610/pdf_export_dry_run_plan.json"
VIDEO_PLAN = ROOT / "Results/static_audits/demo_video_storyboard_plan_20260610/demo_video_storyboard_plan.json"
ACCEPTANCE_PREREQ = (
    ROOT
    / "Results"
    / "static_audits"
    / "final_acceptance_packet_prereq_20260610"
    / "final_acceptance_packet_prereq_plan.json"
)
def load_builder():
    spec = importlib.util.spec_from_file_location("build_final_output_execution_decision_template", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_final_output_execution_decision_template.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_checker():
    spec = importlib.util.spec_from_file_location("check_final_output_execution_decision", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_final_output_execution_decision.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_builder(output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--output-dir",
            str(output_dir.relative_to(ROOT) if output_dir.is_relative_to(ROOT) else output_dir),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_template_is_pending_and_non_authorizing(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["authorizes_pdf_export"] is False
    assert stdout["authorizes_demo_video_recording"] is False
    assert stdout["authorizes_final_acceptance_packet"] is False
    assert stdout["final_acceptance"] is False

    artifact = json.loads((tmp_path / "final_output_execution_decision_template.json").read_text(encoding="utf-8"))
    check = json.loads((tmp_path / "final_output_execution_decision_check.json").read_text(encoding="utf-8"))
    assert artifact["status"] == "execution_decision_template_pending_review_not_execution"
    assert artifact["summary"]["pending_action_count"] == 3
    assert artifact["summary"]["runs_pandoc_now"] is False
    assert check["ok"] is True
    assert check["summary"]["authorizes_pdf_export"] is False


def test_rejects_approved_pdf_export_when_upstream_blocked() -> None:
    builder = load_builder()
    checker = load_checker()
    template = builder.build_template(PDF_PLAN, VIDEO_PLAN, ACCEPTANCE_PREREQ)
    template["actions"]["pdf_export"].update(
        {
            "decision": "approved",
            "approved": True,
            "approved_by": "PMO-static-review",
            "approved_at": "2026-06-11T03:00:00+08:00",
        }
    )
    result = checker.validate_decision(
        template,
        json.loads(PDF_PLAN.read_text(encoding="utf-8")),
        json.loads(VIDEO_PLAN.read_text(encoding="utf-8")),
        json.loads(ACCEPTANCE_PREREQ.read_text(encoding="utf-8")),
        ROOT / "decision.json",
    )
    assert result["ok"] is False
    assert result["summary"]["authorizes_pdf_export"] is False
    assert any("pdf_export is approved but its upstream readiness gate is false" in issue for issue in result["issues"])


def test_valid_pdf_approval_requires_ready_upstream() -> None:
    builder = load_builder()
    checker = load_checker()
    template = builder.build_template(PDF_PLAN, VIDEO_PLAN, ACCEPTANCE_PREREQ)
    template["actions"]["pdf_export"].update(
        {
            "decision": "approved",
            "approved": True,
            "approved_by": "PMO-static-review",
            "approved_at": "2026-06-11T03:00:00+08:00",
            "review_notes": "Approve PDF export only.",
        }
    )
    pdf_plan = json.loads(PDF_PLAN.read_text(encoding="utf-8"))
    pdf_plan["summary"]["safe_to_run_pdf_export_now"] = True
    result = checker.validate_decision(
        template,
        pdf_plan,
        json.loads(VIDEO_PLAN.read_text(encoding="utf-8")),
        json.loads(ACCEPTANCE_PREREQ.read_text(encoding="utf-8")),
        ROOT / "decision.json",
    )
    assert result["ok"] is True
    assert result["summary"]["authorizes_pdf_export"] is True
    assert result["summary"]["runs_pandoc_now"] is False
    assert result["summary"]["generates_final_outputs"] is False


def main() -> int:
    temp = ROOT / ".tmp" / "final_output_execution_decision_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_template_is_pending_and_non_authorizing(temp / "current")
        test_rejects_approved_pdf_export_when_upstream_blocked()
        test_valid_pdf_approval_requires_ready_upstream()
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
    print("[OK] final output execution decision tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
