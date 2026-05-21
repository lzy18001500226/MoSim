#!/usr/bin/env python3
"""Project-local environment and workflow doctor.

This script performs cheap checks only. It does not open GUI tools, mutate Git,
or probe personal directories outside the project.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], timeout: int = 10) -> dict:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
    except Exception as exc:  # pragma: no cover - defensive utility
        return {"ok": False, "error": str(exc)}


def path_exists(relative: str) -> dict:
    path = ROOT / relative
    return {"ok": path.exists(), "path": relative}


def git_status(full: bool) -> dict:
    lock = ROOT / ".git" / "index.lock"
    if not full:
        branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], timeout=10)
        head = run(["git", "rev-parse", "--short", "HEAD"], timeout=10)
        return {
            "ok": branch.get("ok", False) and head.get("ok", False) and not lock.exists(),
            "mode": "fast",
            "index_lock": lock.exists(),
            "branch": branch.get("stdout", ""),
            "head": head.get("stdout", ""),
        }
    result = run(["git", "status", "--short", "--branch"], timeout=60)
    return {
        "ok": result.get("ok", False) and not lock.exists(),
        "index_lock": lock.exists(),
        "status": result,
    }


def git_lfs() -> dict:
    result = run(["git", "lfs", "version"], timeout=10)
    return {
        "ok": result.get("ok", False),
        "required_for_overall": False,
        "path": shutil.which("git-lfs"),
        "result": result,
        "note": "Optional in WSL if Windows Git LFS is used for push cleanup.",
    }


def ledger() -> dict:
    path = ROOT / "workflows" / "agent_task_ledger.md"
    if not path.exists():
        return {"ok": False, "message": "missing workflows/agent_task_ledger.md"}
    text = path.read_text(encoding="utf-8", errors="replace")
    running = [line for line in text.splitlines() if "| running |" in line]
    blocked = [line for line in text.splitlines() if "| blocked |" in line]
    return {
        "ok": not blocked,
        "running_count": len(running),
        "blocked_count": len(blocked),
        "running": running,
        "blocked": blocked,
    }


def large_tracked_files(limit_mb: int, max_files: int) -> dict:
    result = run(["git", "ls-files"], timeout=30)
    if not result.get("ok"):
        return {"ok": False, "result": result}
    offenders = []
    limit = limit_mb * 1024 * 1024
    files = result["stdout"].splitlines()
    truncated = len(files) > max_files
    for line in files[:max_files]:
        path = ROOT / line
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > limit:
            offenders.append({"path": line, "size_mb": round(size / 1024 / 1024, 2)})
            if len(offenders) >= 100:
                break
    return {
        "ok": not offenders and not truncated,
        "limit_mb": limit_mb,
        "scanned_files": min(len(files), max_files),
        "tracked_files": len(files),
        "truncated": truncated,
        "offenders": offenders,
        "note": "Use --max-large-scan-files 0 for full scan." if truncated else "",
    }


def mcp_config_hint() -> dict:
    required_wrappers = [
        "scripts/sysplorer_mcp_wsl_bridge.sh",
        "scripts/sysplorer_mcp_wsl_entry.py",
        "scripts/unreal_mcp_wsl_wrapper.sh",
    ]
    return {
        "ok": all((ROOT / item).exists() for item in required_wrappers),
        "wrappers": [path_exists(item) for item in required_wrappers],
        "note": "Use Codex /mcp for live server health; this doctor avoids external config reads.",
    }


def collect(limit_mb: int, full_git: bool, max_large_scan_files: int) -> dict:
    scan_limit = 10**12 if max_large_scan_files == 0 else max_large_scan_files
    checks = {
        "project_root": {"ok": ROOT.exists(), "path": str(ROOT)},
        "git": git_status(full_git),
        "git_lfs": git_lfs(),
        "agent_ledger": ledger(),
        "large_tracked_files": large_tracked_files(limit_mb, scan_limit),
        "mcp_wrappers": mcp_config_hint(),
        "key_workflows": {
            "ok": all((ROOT / p).exists() for p in [
                "workflows/agent_task_ledger.md",
                "workflows/agent_orchestration.md",
                "workflows/audit_external_repo.md",
                "workflows/unreal_renderer.md",
            ]),
        },
    }
    checks["ok"] = all(
        value.get("ok", False)
        for name, value in checks.items()
        if isinstance(value, dict)
        and name not in {"large_tracked_files", "git_lfs"}
    ) and not checks["large_tracked_files"].get("offenders")
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--large-limit-mb", type=int, default=100)
    parser.add_argument("--full-git-status", action="store_true")
    parser.add_argument("--max-large-scan-files", type=int, default=20_000)
    args = parser.parse_args()
    data = collect(args.large_limit_mb, args.full_git_status, args.max_large_scan_files)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for name, value in data.items():
            if name == "ok":
                continue
            status = "ok" if value.get("ok") else "check"
            print(f"{status:5} {name}")
            if name == "agent_ledger":
                print(f"      running={value.get('running_count')} blocked={value.get('blocked_count')}")
            if name == "large_tracked_files" and value.get("offenders"):
                for item in value["offenders"][:10]:
                    print(f"      {item['size_mb']} MB {item['path']}")
            if name == "large_tracked_files" and value.get("truncated"):
                print(f"      scanned={value.get('scanned_files')} tracked={value.get('tracked_files')}")
        print(f"overall={'ok' if data['ok'] else 'check'}")
    return 0 if data["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
