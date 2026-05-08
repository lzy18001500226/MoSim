#!/usr/bin/env python3
"""
Basic project QA check for the A8 quadrotor control project.

Usage:
    python scripts/qa_check.py

This script checks the project entry points, key documents, converted MWORKS
knowledge base, official quadrotor case, and MCP wrapper scripts. It does not
validate MWORKS models.
"""

from __future__ import annotations

from pathlib import Path
import os
import subprocess
import sys


REQUIRED_DIRS = [
    "scripts",
    "docs",
    "docs/index",
    "docs/mworks/converted",
    "QuadrotorModel",
    "workflows",
]

RECOMMENDED_DIRS = [
    "controllers",
    "planners",
    "scenarios",
    "tests",
    "results",
]

OPTIONAL_NONEMPTY_DIRS = [
    "controllers",
    "planners",
    "scenarios",
    "tests",
    "results",
]

REQUIRED_DOCS = [
    "README.md",
    "AGENTS.md",
]

RECOMMENDED_DOCS = [
    "docs/user_manual.md",
    "docs/simulation_report.md",
    "docs/index/doc_index.md",
    "docs/index/api_index.md",
    "docs/index/workflow_index.md",
    "workflows/run_simulation.md",
    "workflows/calc_metrics.md",
    "workflows/pre_submit_check.md",
]

OFFICIAL_MODELS = [
    "QuadrotorModel.Examples.Example1",
    "QuadrotorModel.Examples.Example2",
    "QuadrotorModel.Examples.Example3",
]

OFFICIAL_SCENARIOS = [
    "scenarios/official/example1_pid_baseline.yaml",
    "scenarios/official/example2_pid_baseline.yaml",
    "scenarios/official/example3_pid_baseline.yaml",
]

OFFICIAL_REFERENCE_OUTPUTS = [
    "results/raw/reference_official_example1.csv",
    "results/raw/reference_official_example2.csv",
    "results/raw/reference_official_example3.csv",
    "results/replay/reference_official_example1.json",
    "results/replay/reference_official_example2.json",
    "results/replay/reference_official_example3.json",
    "results/replay_html/reference_official_example1.html",
    "results/replay_html/reference_official_example2.html",
    "results/replay_html/reference_official_example3.html",
]

WRAPPER_SCRIPTS = {
    "syslab_mcp.sh": [
        "~/mcp-wrappers/syslab_mcp.sh",
        "/home/linux/mcp-wrappers/syslab_mcp.sh",
    ],
    "sysplorer_mcp.sh": [
        "~/mcp-wrappers/sysplorer_mcp.sh",
        "/home/linux/mcp-wrappers/sysplorer_mcp.sh",
    ],
    "filesystem_mcp.sh": [
        "~/mcp-wrappers/filesystem_mcp.sh",
        "/home/linux/mcp-wrappers/filesystem_mcp.sh",
    ],
}


def check_path(path: Path, required: bool = True) -> bool:
    if path.exists():
        print(f"[OK] {path}")
        return True

    label = "FAIL" if required else "WARN"
    print(f"[{label}] Missing: {path}")
    return not required


def has_real_content(path: Path) -> bool:
    if not path.exists() or not path.is_dir():
        return False
    for item in path.rglob("*"):
        if item.is_file() and item.name != ".gitkeep":
            return True
    return False


def is_windows() -> bool:
    return os.name == "nt"


def check_wsl_file(path: str) -> tuple[bool, bool]:
    """Return (exists, executable) for a WSL path when running from Windows."""
    if not is_windows() or not path.startswith("/"):
        return False, False

    try:
        exists = subprocess.run(
            ["wsl.exe", "test", "-f", path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode == 0
        executable = subprocess.run(
            ["wsl.exe", "test", "-x", path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode == 0
    except FileNotFoundError:
        return False, False

    return exists, executable


def check_dirs(root: Path) -> bool:
    print("\n== Required directories ==")
    ok = True
    for item in REQUIRED_DIRS:
        ok = check_path(root / item, required=True) and ok

    print("\n== Recommended directories ==")
    for item in RECOMMENDED_DIRS:
        ok = check_path(root / item, required=False) and ok

    print("\n== Optional implementation directories ==")
    for item in OPTIONAL_NONEMPTY_DIRS:
        path = root / item
        if not path.exists():
            print(f"[OK] Optional absent until used: {path}")
        elif has_real_content(path):
            print(f"[OK] Has content: {path}")
        else:
            print(f"[WARN] Empty placeholder directory: {path}")

    return ok


def check_docs(root: Path) -> bool:
    print("\n== Required documents ==")
    ok = True
    for item in REQUIRED_DOCS:
        ok = check_path(root / item, required=True) and ok

    print("\n== Recommended documents ==")
    for item in RECOMMENDED_DOCS:
        ok = check_path(root / item, required=False) and ok

    return ok


def check_wrappers() -> bool:
    print("\n== MCP wrapper scripts ==")
    ok = True
    for name, candidates in WRAPPER_SCRIPTS.items():
        found = False
        for item in candidates:
            exists_wsl, executable_wsl = check_wsl_file(item)
            if exists_wsl:
                found = True
                if executable_wsl:
                    print(f"[OK] {name}: WSL:{item}")
                else:
                    print(f"[WARN] {name} found but not executable: WSL:{item}")
                    ok = False
                break

            path = Path(item).expanduser()
            if not path.exists() or not path.is_file():
                continue
            found = True
            if not path.stat().st_mode & 0o111:
                print(f"[WARN] {name} found but not executable: {path}")
                ok = False
            else:
                print(f"[OK] {name}: {path}")
            break

        if not found:
            print(f"[WARN] Missing wrapper: {name}")
            for item in candidates:
                print(f"       checked: {Path(item).expanduser()}")
            ok = False
    return ok


def check_official_case(root: Path) -> bool:
    print("\n== Official quadrotor case ==")
    ok = True
    package_path = root / "QuadrotorModel" / "package.mo"
    if not package_path.exists():
        print(f"[FAIL] Missing official package: {package_path}")
        return False

    package_text = package_path.read_text(encoding="utf-8-sig", errors="replace")
    for model_name in OFFICIAL_MODELS:
        short_name = model_name.rsplit(".", 1)[-1]
        if f"model {short_name} " in package_text:
            print(f"[OK] Official model present: {model_name}")
        else:
            print(f"[FAIL] Official model missing: {model_name}")
            ok = False

    for item in OFFICIAL_SCENARIOS:
        ok = check_path(root / item, required=True) and ok

    for item in OFFICIAL_REFERENCE_OUTPUTS:
        ok = check_path(root / item, required=True) and ok

    return ok


def main() -> int:
    root = Path.cwd()
    print(f"Project root: {root}")

    ok = True
    ok = check_dirs(root) and ok
    ok = check_docs(root) and ok
    ok = check_official_case(root) and ok
    wrappers_ok = check_wrappers()

    print("\n== Summary ==")
    if ok:
        print("[OK] Required project structure passed.")
    else:
        print("[FAIL] Required project structure has missing items.")

    if wrappers_ok:
        print("[OK] MCP wrapper scripts found.")
    else:
        print("[WARN] MCP wrapper scripts need attention.")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
