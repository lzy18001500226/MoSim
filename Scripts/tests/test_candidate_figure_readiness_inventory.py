from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_candidate_figure_readiness_inventory.py"
MANIFEST = (
    ROOT
    / "Results"
    / "static_audits"
    / "submission_evidence_manifest_20260610"
    / "candidate_submission_evidence_manifest.json"
)


def load_builder():
    spec = importlib.util.spec_from_file_location("build_candidate_figure_readiness_inventory", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_candidate_figure_readiness_inventory.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_builder(output_dir: Path, manifest: Path = MANIFEST) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(BUILDER),
            "--manifest",
            str(manifest.relative_to(ROOT) if manifest.is_relative_to(ROOT) else manifest),
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


def test_current_candidate_figures_are_ready(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["candidate_row_count"] == 13
    assert report["not_ready_count"] == 0
    assert report["report_figure_ready_count"] == 13

    inventory = json.loads(
        (tmp_path / "candidate_figure_readiness_inventory.json").read_text(encoding="utf-8")
    )
    assert inventory["status"] == "static_figure_inventory_not_final_report_acceptance"
    assert "not final PMO acceptance" in " ".join(inventory["claim_boundary"])
    assert all(row["report_figure_ready"] for row in inventory["candidate_rows"])


def test_missing_core_figure_is_not_ready(tmp_path: Path) -> None:
    builder = load_builder()
    exp_root = tmp_path / "experiment"
    (exp_root / "metrics").mkdir(parents=True)
    (exp_root / "raw").mkdir(parents=True)
    (exp_root / "figures").mkdir(parents=True)
    metrics = exp_root / "metrics" / "x.json"
    raw = exp_root / "raw" / "x.csv"
    metrics.write_text("{}", encoding="utf-8")
    raw.write_text("t,x\n0,0\n", encoding="utf-8")
    for name in ["trajectory_xy.svg", "position_error.svg", "metrics_summary.svg", "figure_manifest.md"]:
        (exp_root / "figures" / name).write_text("placeholder", encoding="utf-8")

    row = {
        "claim_slot": "missing-altitude",
        "experiment_id": "x",
        "claim_family": "unit",
        "quality_status": "pass",
        "claim_ceiling": "candidate_report_evidence_only_not_final_pmo_acceptance",
        "metrics_file": str(metrics),
        "raw_file": str(raw),
    }
    result = builder.row_inventory(row)
    assert result["report_figure_ready"] is False
    assert result["missing_core_figures"] == ["altitude_tracking"]


def test_missing_replay_log_are_review_notes_only() -> None:
    builder = load_builder()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    first = builder.row_inventory(manifest["candidate_rows"][0])
    assert first["report_figure_ready"] is True
    assert isinstance(first["review_notes"], list)


def main() -> int:
    temp = ROOT / ".tmp" / "candidate_figure_readiness_inventory_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_candidate_figures_are_ready(temp / "current")
        test_missing_core_figure_is_not_ready(temp / "missing")
        test_missing_replay_log_are_review_notes_only()
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
    print("[OK] candidate figure readiness inventory tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
