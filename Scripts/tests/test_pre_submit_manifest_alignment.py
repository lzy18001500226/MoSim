from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_pre_submit_manifest_alignment.py"
DOC = ROOT / "Docs" / "Workflows" / "pre_submit_check.md"
MANIFEST = (
    ROOT
    / "Results"
    / "static_audits"
    / "submission_evidence_manifest_20260610"
    / "candidate_submission_evidence_manifest.json"
)


def load_checker():
    spec = importlib.util.spec_from_file_location("check_pre_submit_manifest_alignment", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_pre_submit_manifest_alignment.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checker(path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), str(path), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_pre_submit_workflow_passes() -> None:
    completed = run_checker(DOC)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True


def test_rejects_missing_boundary_term(tmp_path: Path) -> None:
    checker = load_checker()
    text = DOC.read_text(encoding="utf-8")
    tmp_path.mkdir(parents=True, exist_ok=True)
    broken_doc = tmp_path / "pre_submit_check.md"
    broken_doc.write_text(text.replace("closed_loop", "closed loop"), encoding="utf-8")
    report = checker.validate(broken_doc, MANIFEST)
    assert report["ok"] is False
    assert any("closed_loop" in issue for issue in report["issues"])


def test_rejects_manifest_final_acceptance_status(tmp_path: Path) -> None:
    checker = load_checker()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["status"] = "final_acceptance"
    tmp_path.mkdir(parents=True, exist_ok=True)
    broken_manifest = tmp_path / "manifest.json"
    broken_manifest.write_text(json.dumps(manifest), encoding="utf-8")
    report = checker.validate(DOC, broken_manifest)
    assert report["ok"] is False
    assert any("review_candidate_not_final_acceptance" in issue for issue in report["issues"])


def test_rejects_heading_sequence_drift(tmp_path: Path) -> None:
    checker = load_checker()
    text = DOC.read_text(encoding="utf-8")
    tmp_path.mkdir(parents=True, exist_ok=True)
    broken_doc = tmp_path / "pre_submit_check.md"
    broken_doc.write_text(text.replace("## 9. Report Check", "## 8. Report Check"), encoding="utf-8")
    report = checker.validate(broken_doc, MANIFEST)
    assert report["ok"] is False
    assert any("heading sequence mismatch" in issue for issue in report["issues"])


def main() -> int:
    temp = ROOT / ".tmp" / "pre_submit_manifest_alignment_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_pre_submit_workflow_passes()
        test_rejects_missing_boundary_term(temp / "missing_boundary")
        test_rejects_manifest_final_acceptance_status(temp / "bad_status")
        test_rejects_heading_sequence_drift(temp / "heading")
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
    print("[OK] pre-submit manifest alignment tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
