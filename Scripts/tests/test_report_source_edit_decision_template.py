from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_report_source_edit_decision_template.py"
PATCH_PREVIEW = (
    ROOT
    / "Results"
    / "static_audits"
    / "simulation_report_patch_preview_20260610"
    / "simulation_report_patch_preview.json"
)


def load_builder():
    spec = importlib.util.spec_from_file_location("build_report_source_edit_decision_template", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_report_source_edit_decision_template.py")
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


def test_current_decision_template_is_pending_and_non_applying(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["decision"] == "pending_review"
    assert stdout["safe_to_apply_report_source_edits"] is False

    artifact = json.loads((tmp_path / "report_source_edit_decision_template.json").read_text(encoding="utf-8"))
    template = json.loads((tmp_path / "report_source_edit_decision.template.json").read_text(encoding="utf-8"))
    assert artifact["status"] == "decision_template_pending_review_not_approval"
    assert artifact["summary"]["available_preview_count"] == 7
    assert artifact["summary"]["approved_preview_count"] == 0
    assert artifact["summary"]["safe_to_apply_report_source_edits"] is False
    assert artifact["summary"]["edits_report_source"] is False
    assert artifact["summary"]["final_acceptance"] is False
    assert template["status"] == "decision_template_pending_review"
    assert template["decision"] == "pending_review"
    assert template["safe_to_apply_report_source_edits"] is False


def test_rejects_approved_decision_without_preview_ids() -> None:
    module = load_builder()
    template = module.build_template(PATCH_PREVIEW, ROOT / "missing-readiness.json")
    template["decision"] = "approved"
    result = module.validate_template(template, PATCH_PREVIEW)
    assert result["ok"] is False
    assert any("approved/narrowed" in issue for issue in result["issues"])


def main() -> int:
    temp = ROOT / ".tmp" / "report_source_edit_decision_template_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_decision_template_is_pending_and_non_applying(temp / "current")
        test_rejects_approved_decision_without_preview_ids()
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
    print("[OK] report source edit decision template tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
