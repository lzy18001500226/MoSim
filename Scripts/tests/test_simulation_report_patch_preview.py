from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_simulation_report_patch_preview.py"


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


def test_current_simulation_report_patch_preview_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["preview_count"] == 7
    assert report["edits_report_source"] is False
    assert report["deletes_content"] is False
    assert report["final_acceptance"] is False

    preview = json.loads((tmp_path / "simulation_report_patch_preview.json").read_text(encoding="utf-8"))
    assert preview["status"] == "draft_patch_preview_not_report_edit"
    assert preview["summary"]["candidate_insert_preview_count"] == 3
    assert preview["summary"]["replacement_preview_count"] == 1
    preview_ids = {item["preview_id"] for item in preview["previews"]}
    assert {
        "preserve_final_acceptance_boundary_preview",
        "rewrite_formation_next_stage_boundary_preview",
        "insert_visual_trajectory_review_candidate_subsection_preview",
        "insert_fault_tolerance_candidate_subsection_preview",
        "insert_multi_uav_formation_candidate_subsection_preview",
        "condense_smoke_and_legacy_sections_preview",
        "renumber_l1_residual_subsection_preview",
    } == preview_ids
    assert all(item["applies_patch_now"] is False for item in preview["previews"])
    items = {item["preview_id"]: item for item in preview["previews"]}
    assert "规划和编队仍保留" in items["rewrite_formation_next_stage_boundary_preview"]["original"]
    assert items["renumber_l1_residual_subsection_preview"]["original"].startswith("### 9.4 ")
    assert "does not edit Docs/simulation_report.md" in " ".join(preview["claim_boundary"])
    joined_preview = "\n".join(item["preview"] for item in preview["previews"])
    assert "ROS2/PX4/QGC" in joined_preview
    assert "UE build/runtime/editor" in joined_preview
    assert "final PMO acceptance" in " ".join(preview["claim_boundary"])


def main() -> int:
    temp = ROOT / ".tmp" / "simulation_report_patch_preview_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_simulation_report_patch_preview_builds(temp / "current")
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
    print("[OK] simulation report patch preview tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
