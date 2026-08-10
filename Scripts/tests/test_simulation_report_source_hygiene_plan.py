from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER = ROOT / "Scripts" / "quality" / "build_simulation_report_source_hygiene_plan.py"


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


def test_current_simulation_report_source_hygiene_plan_builds(tmp_path: Path) -> None:
    completed = run_builder(tmp_path)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["finding_count"] == 2
    assert report["edits_report_source"] is False
    assert report["deletes_content"] is False
    assert report["final_acceptance"] is False

    plan = json.loads((tmp_path / "simulation_report_source_hygiene_plan.json").read_text(encoding="utf-8"))
    assert plan["status"] == "draft_hygiene_plan_not_report_edit"
    assert plan["summary"]["edits_report_source"] is False
    assert plan["summary"]["deletes_content"] is False
    assert plan["summary"]["final_acceptance"] is False
    finding_ids = {finding["finding_id"] for finding in plan["findings"]}
    assert finding_ids == {
        "smoke_and_staged_prominence",
        "legacy_controller_comparison_sections",
    }
    assert "does not edit Docs/报告/仿真分析报告_正文骨架.md" in " ".join(plan["claim_boundary"])


def main() -> int:
    temp = ROOT / ".tmp" / "simulation_report_source_hygiene_plan_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_simulation_report_source_hygiene_plan_builds(temp / "current")
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
    print("[OK] simulation report source hygiene plan tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
