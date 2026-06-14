from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_demo_video_storyboard_plan.py"


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


def test_current_storyboard_maps_candidate_evidence_without_recording(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    stdout = json.loads(completed.stdout)
    assert stdout["storyboard_ready_for_review"] is True
    assert stdout["safe_to_record_demo_video_now"] is False
    assert stdout["records_or_renders_video_now"] is False

    plan = json.loads((tmp_path / "demo_video_storyboard_plan.json").read_text(encoding="utf-8"))
    assert plan["status"] == "storyboard_plan_not_demo_video_acceptance"
    assert plan["summary"]["candidate_row_count"] == 13
    assert plan["summary"]["scene_count"] == 7
    assert plan["summary"]["records_or_renders_video_now"] is False
    assert plan["summary"]["generates_final_outputs"] is False
    assert plan["summary"]["final_acceptance"] is False
    scene_ids = {scene["scene_id"] for scene in plan["scenes"]}
    assert "S4-formation-control" in scene_ids
    assert "S5-visual-trajectory-review" in scene_ids
    assert "closed_loop" in plan["forbidden_video_claims"]
    assert "UE build/runtime/editor success" in plan["forbidden_video_claims"]
    blocker_ids = {blocker["blocker_id"] for blocker in plan["blockers"]}
    assert "demo_video_not_recorded" in blocker_ids
    assert "manual_storyboard_review_required" in blocker_ids


def main() -> int:
    temp = ROOT / ".tmp" / "demo_video_storyboard_plan_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_storyboard_maps_candidate_evidence_without_recording(temp / "current")
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
    print("[OK] demo video storyboard plan tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
