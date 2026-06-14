from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_final_report_outline_gap_inventory.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_final_report_outline_gap_inventory", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load build_final_report_outline_gap_inventory.py")
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


def test_current_outline_gap_inventory_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["candidate_row_count"] == 13
    assert report["section_count"] >= 15
    assert report["static_update_section_count"] >= 5
    assert report["human_or_live_review_section_count"] >= 1
    assert report["unmapped_claim_family_count"] >= 3
    assert report["final_submission_ready"] is False

    inventory = json.loads((tmp_path / "final_report_outline_gap_inventory.json").read_text(encoding="utf-8"))
    assert inventory["status"] == "static_report_outline_gap_not_final_acceptance"
    assert "Candidate rows remain" in " ".join(inventory["claim_boundary"])
    families = {item["claim_family"] for item in inventory["candidate_insertion_actions"]}
    assert "multi_uav_formation" in families
    assert "fault_tolerance" in families
    assert "visual_trajectory_review" in families


def test_parse_sections_and_rules() -> None:
    builder = load_builder()
    sections = builder.parse_sections("# A\n\ntext\n\n## 官方 PID Baseline 指标\n\nbody\n")
    assert len(sections) == 2
    rule = builder.rule_for_heading("6. 官方 PID Baseline 指标")
    assert rule["claim_family"] == "official_baseline"


def main() -> int:
    temp = ROOT / ".tmp" / "final_report_outline_gap_inventory_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_outline_gap_inventory_builds(temp / "current")
        test_parse_sections_and_rules()
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
    print("[OK] final report outline gap inventory tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
