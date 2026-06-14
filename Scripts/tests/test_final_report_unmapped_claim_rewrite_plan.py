from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_report_unmapped_claim_rewrite_plan.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_final_report_unmapped_claim_rewrite_plan", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_final_report_unmapped_claim_rewrite_plan.py")
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


def test_current_unmapped_claim_rewrite_plan_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["family_count"] == 3
    assert report["candidate_row_count"] == 4
    assert report["missing_family_row_count"] == 0
    assert report["edits_report_source"] is False
    assert report["final_acceptance"] is False

    plan = json.loads((tmp_path / "final_report_unmapped_claim_rewrite_plan.json").read_text(encoding="utf-8"))
    assert plan["status"] == "draft_rewrite_plan_not_final_report_acceptance"
    families = {section["claim_family"] for section in plan["sections"]}
    assert families == {"fault_tolerance", "multi_uav_formation", "visual_trajectory_review"}
    assert "does not edit Docs/simulation_report.md" in " ".join(plan["claim_boundary"])


def test_family_markdown_table_contains_metrics_and_figure() -> None:
    builder = load_builder()
    rows = [
        {
            "claim_slot": "slot",
            "scene_id": "scene",
            "controller_id": "controller",
            "position_rmse_m": 1.234567,
            "total_health_score": 9,
            "formation_score": "",
            "metrics_file": "metrics.json",
            "trajectory_figure": "figure.svg",
        }
    ]
    table = "\n".join(builder.family_markdown_table(rows))
    assert "metrics.json" in table
    assert "figure.svg" in table
    assert "1.23457" in table


def main() -> int:
    temp = ROOT / ".tmp" / "final_report_unmapped_claim_rewrite_plan_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_unmapped_claim_rewrite_plan_builds(temp / "current")
        test_family_markdown_table_contains_metrics_and_figure()
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
    print("[OK] final report unmapped claim rewrite plan tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
