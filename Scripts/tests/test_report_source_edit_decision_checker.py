from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_report_source_edit_decision.py"
TEMPLATE = (
    ROOT
    / "Results"
    / "static_audits"
    / "report_source_edit_decision_template_20260610"
    / "report_source_edit_decision.template.json"
)
PATCH_PREVIEW = (
    ROOT
    / "Results"
    / "static_audits"
    / "simulation_report_patch_preview_20260610"
    / "simulation_report_patch_preview.json"
)


def load_checker():
    spec = importlib.util.spec_from_file_location("check_report_source_edit_decision", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_report_source_edit_decision.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checker(output_json: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--output-json",
            str(output_json.relative_to(ROOT) if output_json.is_relative_to(ROOT) else output_json),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_pending_decision_is_valid_but_non_authorizing(tmp_path: Path) -> None:
    completed = run_checker(tmp_path / "decision_check.json")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["decision"] == "pending_review"
    assert report["authorizes_application"] is False
    assert report["safe_to_apply_report_source_edits"] is False
    assert report["approved_preview_count"] == 0


def test_rejects_invalid_approval_without_review_fields() -> None:
    checker = load_checker()
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    patch_preview = json.loads(PATCH_PREVIEW.read_text(encoding="utf-8"))
    template["decision"] = "approved"
    template["safe_to_apply_report_source_edits"] = True
    report = checker.validate_decision_template(template, patch_preview, TEMPLATE, PATCH_PREVIEW)
    assert report["ok"] is False
    assert report["authorizes_application"] is False
    assert any("approved/narrowed decision must name approved_preview_ids" in issue for issue in report["issues"])
    assert any("decision_owner" in issue for issue in report["issues"])
    assert any("decided_at" in issue for issue in report["issues"])


def test_valid_narrowed_decision_authorizes_application() -> None:
    checker = load_checker()
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    patch_preview = json.loads(PATCH_PREVIEW.read_text(encoding="utf-8"))
    approved_id = template["available_preview_ids"][0]
    template.update(
        {
            "decision": "narrowed",
            "decision_owner": "PMO-static-review",
            "decided_at": "2026-06-11T02:40:00+08:00",
            "approved_preview_ids": [approved_id],
            "safe_to_apply_report_source_edits": True,
            "review_notes": "Approve one reviewed preview only.",
        }
    )
    report = checker.validate_decision_template(template, patch_preview, TEMPLATE, PATCH_PREVIEW)
    assert report["ok"] is True
    assert report["authorizes_application"] is True
    assert report["approved_preview_count"] == 1


def main() -> int:
    temp = ROOT / ".tmp" / "report_source_edit_decision_checker_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_pending_decision_is_valid_but_non_authorizing(temp / "current")
        test_rejects_invalid_approval_without_review_fields()
        test_valid_narrowed_decision_authorizes_application()
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
    print("[OK] report source edit decision checker tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
