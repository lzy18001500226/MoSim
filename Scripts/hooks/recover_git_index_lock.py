#!/usr/bin/env python3
"""Safely inspect and, with explicit confirmation, remove a stale Git index lock."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[2]
LOCK_PATH = (ROOT / ".git" / "index.lock").resolve()
DEFAULT_MIN_AGE_SECONDS = 10 * 60
ProcessProbe = Callable[[], tuple[list[str], str | None]]
ERROR_SHARING_VIOLATION = 32
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
FILE_ATTRIBUTE_NORMAL = 0x80


READ_ONLY_GIT_COMMANDS = (
    " status",
    " ls-files",
    " diff",
    " check-ignore",
    " rev-parse",
    " log",
    " show",
    " cat-file",
    " for-each-ref",
)
WRITE_GIT_COMMANDS = (
    " add",
    " commit",
    " merge",
    " rebase",
    " update-index",
    " checkout",
    " switch",
    " reset",
    " cherry-pick",
    " revert",
    " am",
    " apply",
    " worktree",
    " gc",
    " prune",
    " pack-refs",
)


def classify_git_command(command_line: str) -> str:
    """Classify a Git process conservatively from its command line."""
    normalized = " " + re.sub(r"\s+", " ", command_line.lower()).strip() + " "
    if any(marker in normalized for marker in WRITE_GIT_COMMANDS):
        return "writer"
    if any(marker in normalized for marker in READ_ONLY_GIT_COMMANDS):
        return "read-only"
    return "unknown"


def probe_git_writers() -> tuple[list[str], str | None]:
    """Return active Git writers without starting another Git process."""
    try:
        if os.name == "nt":
            powershell = shutil.which("pwsh") or shutil.which("powershell")
            if not powershell:
                return [], "PowerShell is required to inspect Git command lines"
            query = (
                "Get-CimInstance Win32_Process -Filter \"Name='git.exe'\" | "
                "Select-Object ProcessId,ParentProcessId,CommandLine | ConvertTo-Json -Compress"
            )
            completed = subprocess.run(
                [powershell, "-NoProfile", "-NonInteractive", "-Command", query],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                check=False,
            )
            if completed.returncode != 0:
                return [], completed.stderr.strip() or "PowerShell process query failed"
            if not completed.stdout.strip() or completed.stdout.strip() == "null":
                return [], None
            data = json.loads(completed.stdout)
            rows = data if isinstance(data, list) else [data]
            states: dict[str, str] = {}
            parents: dict[str, str] = {}
            direct: dict[str, str | None] = {}
            for row in rows:
                pid = str(row.get("ProcessId", "?"))
                parents[pid] = str(row.get("ParentProcessId", ""))
                command_line = str(row.get("CommandLine") or "")
                direct[pid] = classify_git_command(command_line) if command_line else None
                states[pid] = direct[pid] or "unknown"

            # Git helper children can expose no command line. Inherit the
            # classification from a known parent, but keep unknown roots blocked.
            for _ in range(len(rows)):
                changed = False
                for pid, classification in direct.items():
                    if classification is not None:
                        continue
                    parent_state = states.get(parents.get(pid, ""))
                    if parent_state in {"read-only", "writer"} and states[pid] != parent_state:
                        states[pid] = parent_state
                        changed = True
                if not changed:
                    break

            writers: list[str] = []
            for row in rows:
                pid = str(row.get("ProcessId", "?"))
                classification = states[pid]
                if classification != "read-only":
                    writers.append(f"{pid}:{classification}")
            return writers, None

        completed = subprocess.run(
            ["ps", "-eo", "pid=,args="],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            check=False,
        )
        if completed.returncode != 0:
            return [], completed.stderr.strip() or "ps failed"
        writers = []
        for line in completed.stdout.splitlines():
            match = re.match(r"\s*(\d+)\s+(.*)", line)
            if not match or not re.search(r"(?:^|/)git(?:\s|$)", match.group(2)):
                continue
            classification = classify_git_command(match.group(2))
            if classification != "read-only":
                writers.append(f"{match.group(1)}:{classification}")
        return writers, None
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        return [], str(exc)


def probe_lock_holder(lock_path: Path) -> tuple[bool | None, str | None]:
    """Check whether Windows can open the lock with an exclusive share mode."""
    if os.name != "nt":
        return None, "exclusive lock probing is only implemented on Windows"

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    create_file = kernel32.CreateFileW
    create_file.argtypes = [
        ctypes.c_wchar_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_void_p,
    ]
    create_file.restype = ctypes.c_void_p
    close_handle = kernel32.CloseHandle
    close_handle.argtypes = [ctypes.c_void_p]
    close_handle.restype = ctypes.c_int

    handle = create_file(
        str(lock_path),
        GENERIC_READ | GENERIC_WRITE,
        0,
        None,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        None,
    )
    if handle == ctypes.c_void_p(-1).value:
        error = ctypes.get_last_error()
        if error == ERROR_SHARING_VIOLATION:
            return True, "the lock file is held by another process"
        return None, f"CreateFileW failed with error {error}"
    close_handle(handle)
    return False, None


def inspect_lock(
    lock_path: Path = LOCK_PATH,
    *,
    min_age_seconds: int = DEFAULT_MIN_AGE_SECONDS,
    confirm: bool = False,
    now: float | None = None,
    process_probe: ProcessProbe = probe_git_writers,
) -> dict:
    """Inspect the exact repository lock and optionally remove it."""
    resolved = lock_path.resolve()
    if resolved != LOCK_PATH:
        return {
            "status": "rejected_path",
            "ok": False,
            "lock_path": str(resolved),
            "reason": "only the repository .git/index.lock may be handled",
        }

    if not resolved.exists():
        return {"status": "absent", "ok": True, "lock_path": str(resolved)}
    if resolved.is_symlink():
        return {
            "status": "rejected_link",
            "ok": False,
            "lock_path": str(resolved),
            "reason": "the lock path must be a regular file",
        }

    try:
        stat = resolved.stat()
    except OSError as exc:
        return {
            "status": "stat_failed",
            "ok": False,
            "lock_path": str(resolved),
            "reason": str(exc),
        }

    current_time = time.time() if now is None else now
    age_seconds = max(0.0, current_time - stat.st_mtime)
    result = {
        "status": "inspection",
        "ok": False,
        "lock_path": str(resolved),
        "size": stat.st_size,
        "age_seconds": round(age_seconds, 3),
        "min_age_seconds": min_age_seconds,
        "confirmed": confirm,
    }

    if age_seconds < min_age_seconds:
        result.update({"status": "too_recent", "reason": "lock is newer than the safety threshold"})
        return result

    processes, probe_error = process_probe()
    result["git_processes"] = processes
    if probe_error:
        result.update({"status": "process_probe_failed", "reason": probe_error})
        return result

    known_writers = [item for item in processes if not item.endswith(":unknown")]
    result["git_writers"] = known_writers
    result["unclassified_git_processes"] = [item for item in processes if item.endswith(":unknown")]
    if processes:
        reason = "a repository writer or unclassified repository process is still running"
        result.update({"status": "git_process_active", "reason": reason})
        return result

    lock_held, lock_probe_error = probe_lock_holder(resolved)
    result["lock_exclusive_holder"] = lock_held
    if lock_probe_error:
        result.update({"status": "lock_probe_failed", "reason": lock_probe_error})
        return result
    if lock_held:
        result.update({"status": "lock_in_use", "reason": "the lock file is still held by another process"})
        return result
    if not confirm:
        result.update({"status": "confirmation_required", "reason": "pass --confirm-stale to remove the verified stale lock"})
        return result

    try:
        resolved.unlink()
    except OSError as exc:
        result.update({"status": "remove_failed", "reason": str(exc)})
        return result
    result.update({"status": "removed", "ok": True})
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-stale", action="store_true", help="remove only after all safety checks pass")
    parser.add_argument("--min-age-seconds", type=int, default=DEFAULT_MIN_AGE_SECONDS)
    parser.add_argument("--json", action="store_true", help="emit one JSON result")
    args = parser.parse_args()
    if args.min_age_seconds < 0:
        parser.error("--min-age-seconds must be non-negative")

    result = inspect_lock(
        min_age_seconds=args.min_age_seconds,
        confirm=args.confirm_stale,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
    else:
        print(f"status={result['status']} lock_path={result['lock_path']}")
        if result.get("reason"):
            print(f"reason={result['reason']}")
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
