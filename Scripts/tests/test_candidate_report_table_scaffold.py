from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_candidate_report_table_scaffold.py"
MANIFEST = (
    ROOT
    / "Results"
    / "static_audits"
    / "submission_evidence_manifest_20260610"
    / "candidate_submission_evidence_manifest.json"
)
FIGURE_INVENTORY = (
    ROOT
    / "Results"
    / "static_audits"
    / "candidate_figure_readiness_20260610"
    / "candidate_figure_readiness_inventory.json"
)


def load_builder():
    spec = importlib.util.spec_from_file_location("build_candidate_report_table_scaffold", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_candidate_report_table_scaffold.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_builder(output_dir: Path, manifest: Path = MANIFEST, figure_inventory: Path = FIGURE_INVENTORY) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--manifest",
            str(manifest.relative_to(ROOT) if manifest.is_relative_to(ROOT) else manifest),
            "--figure-inventory",
            str(figure_inventory.relative_to(ROOT) if figure_inventory.is_relative_to(ROOT) else figure_inventory),
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


def test_current_report_table_scaffold_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["row_count"] == 13
    assert report["figure_ready_rows"] == 13
    assert report["missing_figure_slot_count"] == 0
    assert report["quality_non_pass_slot_count"] == 0

    scaffold = json.loads((tmp_path / "candidate_report_table_scaffold.json").read_text(encoding="utf-8"))
    assert scaffold["status"] == "draft_table_scaffold_not_final_report_acceptance"
    assert "not final PMO acceptance" in " ".join(scaffold["claim_boundary"])
    assert scaffold["summary"]["claim_family_counts"]["official_baseline"] == 3


def test_rejects_missing_figure_readiness(tmp_path: Path) -> None:
    builder = load_builder()
    tmp_path.mkdir(parents=True, exist_ok=True)
    figure_inventory = json.loads(FIGURE_INVENTORY.read_text(encoding="utf-8"))
    figure_inventory["candidate_rows"][0]["report_figure_ready"] = False
    bad_figures = tmp_path / "bad_figures.json"
    bad_figures.write_text(json.dumps(figure_inventory), encoding="utf-8")
    scaffold = builder.build_scaffold(MANIFEST, bad_figures)
    assert scaffold["summary"]["missing_figure_slots"] == ["C0-baseline-step-example1"]


def test_rejects_non_pass_quality(tmp_path: Path) -> None:
    builder = load_builder()
    tmp_path.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["candidate_rows"][0]["quality_status"] = "needs_iteration"
    bad_manifest = tmp_path / "bad_manifest.json"
    bad_manifest.write_text(json.dumps(manifest), encoding="utf-8")
    scaffold = builder.build_scaffold(bad_manifest, FIGURE_INVENTORY)
    assert scaffold["summary"]["quality_non_pass_slots"] == ["C0-baseline-step-example1"]


def main() -> int:
    temp = ROOT / ".tmp" / "candidate_report_table_scaffold_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_report_table_scaffold_builds(temp / "current")
        test_rejects_missing_figure_readiness(temp / "missing_figure")
        test_rejects_non_pass_quality(temp / "non_pass")
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
    print("[OK] candidate report table scaffold tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
