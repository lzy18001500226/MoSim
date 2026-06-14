from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_final_submission_readiness_chain.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_final_submission_readiness_chain", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_final_submission_readiness_chain.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checker(output_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--output-json",
            str((output_dir / "chain.json").relative_to(ROOT)),
            "--output-md",
            str((output_dir / "chain.md").relative_to(ROOT)),
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def copy_artifacts(tmp_path: Path, checker) -> dict[str, str]:
    paths: dict[str, str] = {}
    for artifact_id, rel_path in checker.PATHS.items():
        source = ROOT / rel_path
        target = tmp_path / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        paths[artifact_id] = str(target.relative_to(ROOT))
    return paths


def test_current_final_submission_readiness_chain_passes(tmp_path: Path) -> None:
    completed = run_checker(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True
    assert report["summary"]["dashboard_blocking_gate_count"] == 7
    assert report["summary"]["artifact_count"] == 13
    assert report["summary"]["dashboard_blocker_count"] == 16
    assert report["summary"]["reviewer_action_count"] == 6
    assert report["summary"]["human_review_decision_count"] == 3
    assert report["summary"]["final_submission_ready"] is False
    assert report["summary"]["generates_final_outputs"] is False
    assert report["summary"]["final_acceptance"] is False


def test_rejects_dashboard_gate_path_drift(tmp_path: Path) -> None:
    checker = load_checker()
    paths = copy_artifacts(tmp_path, checker)
    dashboard_path = ROOT / paths["dashboard"]
    dashboard = json.loads(dashboard_path.read_text(encoding="utf-8"))
    dashboard["gates"]["pdf_export_plan"]["path"] = "Results/static_audits/wrong.json"
    dashboard_path.write_text(json.dumps(dashboard), encoding="utf-8")
    report = checker.validate_chain(paths)
    assert report["ok"] is False
    assert any("dashboard gate pdf_export_plan path" in issue for issue in report["issues"])


def test_rejects_unblocked_pdf_export_flag(tmp_path: Path) -> None:
    checker = load_checker()
    paths = copy_artifacts(tmp_path, checker)
    pdf_path = ROOT / paths["pdf_export_plan"]
    pdf_plan = json.loads(pdf_path.read_text(encoding="utf-8"))
    pdf_plan["summary"]["runs_pandoc_now"] = True
    pdf_path.write_text(json.dumps(pdf_plan), encoding="utf-8")
    report = checker.validate_chain(paths)
    assert report["ok"] is False
    assert any("pdf_export_plan.runs_pandoc_now" in issue for issue in report["issues"])


def main() -> int:
    temp = ROOT / ".tmp" / "final_submission_readiness_chain_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_final_submission_readiness_chain_passes(temp / "current")
        test_rejects_dashboard_gate_path_drift(temp / "path_drift")
        test_rejects_unblocked_pdf_export_flag(temp / "unblocked_flag")
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
    print("[OK] final submission readiness chain tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
