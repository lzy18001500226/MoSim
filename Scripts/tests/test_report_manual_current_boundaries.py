from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "Scripts" / "quality" / "check_report_manual_current_boundaries.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_report_manual_current_boundaries", CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load check_report_manual_current_boundaries.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_checker(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_current_report_and_manual_pass() -> None:
    completed = run_checker()
    assert completed.returncode == 0, completed.stdout + completed.stderr
    report = json.loads(completed.stdout)
    assert report["ok"] is True


def test_rejects_obsolete_wsl_manual_term(tmp_path: Path) -> None:
    checker = load_checker()
    report_path = ROOT / "Docs" / "simulation_report.md"
    manual_path = tmp_path / "user_manual.md"
    tmp_path.mkdir(parents=True, exist_ok=True)
    manual_text = (ROOT / "Docs" / "user_manual.md").read_text(encoding="utf-8")
    manual_text += "\n当前 WSL 自动化优先使用 Python 脚本。\n"
    manual_path.write_text(manual_text, encoding="utf-8")
    result = checker.validate(report_path, manual_path)
    assert result["ok"] is False
    assert any("当前 WSL 自动化优先" in issue for issue in result["issues"])


def test_rejects_missing_report_boundary(tmp_path: Path) -> None:
    checker = load_checker()
    report_path = tmp_path / "simulation_report.md"
    manual_path = ROOT / "Docs" / "user_manual.md"
    tmp_path.mkdir(parents=True, exist_ok=True)
    report_text = (ROOT / "Docs" / "simulation_report.md").read_text(encoding="utf-8")
    report_path.write_text(report_text.replace("planner_ready", "planner ready"), encoding="utf-8")
    result = checker.validate(report_path, manual_path)
    assert result["ok"] is False
    assert any("planner_ready" in issue for issue in result["issues"])


def main() -> int:
    temp = ROOT / ".tmp" / "report_manual_current_boundaries_test"
    temp.mkdir(parents=True, exist_ok=True)
    try:
        test_current_report_and_manual_pass()
        test_rejects_obsolete_wsl_manual_term(temp / "wsl")
        test_rejects_missing_report_boundary(temp / "missing_report")
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
    print("[OK] report/manual current boundary tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
