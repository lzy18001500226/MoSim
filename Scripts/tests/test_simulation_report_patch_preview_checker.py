from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_simulation_report_patch_preview.py"
PREVIEW = (
    ROOT
    / "Results"
    / "static_audits"
    / "simulation_report_patch_preview_20260610"
    / "simulation_report_patch_preview.json"
)


def load_checker():
    spec = importlib.util.spec_from_file_location("check_simulation_report_patch_preview", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_simulation_report_patch_preview.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checker(preview_path: Path, output_path: Path | None = None) -> subprocess.CompletedProcess[str]:
    cmd = [
        sys.executable,
        str(CHECKER),
        "--preview",
        str(preview_path.relative_to(ROOT) if preview_path.is_relative_to(ROOT) else preview_path),
    ]
    if output_path is not None:
        cmd.extend(["--output-json", str(output_path.relative_to(ROOT) if output_path.is_relative_to(ROOT) else output_path)])
    return subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_simulation_report_patch_preview_validates(tmp_path: Path) -> None:
    completed = run_checker(PREVIEW, tmp_path / "check.json")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["ok"] is True
    assert result["preview_count"] == 7
    written = json.loads((tmp_path / "check.json").read_text(encoding="utf-8"))
    assert written["ok"] is True


def test_checker_rejects_applying_preview(tmp_path: Path) -> None:
    checker = load_checker()
    tmp_path.mkdir(parents=True, exist_ok=True)
    bad = json.loads(PREVIEW.read_text(encoding="utf-8"))
    bad["previews"][0]["applies_patch_now"] = True
    bad_path = tmp_path / "bad_preview.json"
    bad_path.write_text(json.dumps(bad, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = checker.validate(ROOT / "Docs" / "simulation_report.md", bad_path)
    assert result["ok"] is False
    assert any("applies_patch_now=false" in issue for issue in result["issues"])


def main() -> int:
    temp = ROOT / ".tmp" / "simulation_report_patch_preview_checker_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_simulation_report_patch_preview_validates(temp / "current")
        test_checker_rejects_applying_preview(temp / "bad")
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
    print("[OK] simulation report patch preview checker tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
