#!/usr/bin/env python3
"""Regression checks for the explicit stale Git index-lock recovery route."""

from __future__ import annotations

import importlib.util
import os
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "Scripts" / "hooks" / "recover_git_index_lock.py"


def load_recovery_module():
    spec = importlib.util.spec_from_file_location("recover_git_index_lock", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load stale-lock recovery module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_lock(path: Path, timestamp: float) -> None:
    path.touch()
    os.utime(path, (timestamp, timestamp))


def main() -> int:
    recovery = load_recovery_module()
    assert recovery.classify_git_command("git.exe diff --numstat") == "read-only"
    assert recovery.classify_git_command("git.exe add AGENTS.md") == "writer"
    assert recovery.classify_git_command("git.exe") == "unknown"
    with tempfile.TemporaryDirectory(dir=ROOT / "Results" / "tmp") as temp:
        temp_root = Path(temp)
        lock = temp_root / ".git" / "index.lock"
        lock.parent.mkdir()
        now = time.time()
        original_lock_path = recovery.LOCK_PATH
        recovery.LOCK_PATH = lock.resolve()

        try:
            make_lock(lock, now - 30)
            fresh = recovery.inspect_lock(
                lock,
                min_age_seconds=600,
                confirm=True,
                now=now,
                process_probe=lambda: ([], None),
            )
            assert fresh["status"] == "too_recent", fresh
            assert lock.exists()

            make_lock(lock, now - 3600)
            if recovery.os.name == "nt":
                lock_held, lock_probe_error = recovery.probe_lock_holder(lock)
                assert lock_held is False, lock_probe_error
            unconfirmed = recovery.inspect_lock(
                lock,
                min_age_seconds=600,
                confirm=False,
                now=now,
                process_probe=lambda: ([], None),
            )
            assert unconfirmed["status"] == "confirmation_required", unconfirmed
            assert lock.exists()

            active = recovery.inspect_lock(
                lock,
                min_age_seconds=600,
                confirm=True,
                now=now,
                process_probe=lambda: (["git.exe"], None),
            )
            assert active["status"] == "git_process_active", active
            assert lock.exists()

            unclassified = recovery.inspect_lock(
                lock,
                min_age_seconds=600,
                confirm=True,
                now=now,
                process_probe=lambda: (["123:unknown"], None),
            )
            assert unclassified["status"] == "git_process_active", unclassified
            assert lock.exists()

            removed = recovery.inspect_lock(
                lock,
                min_age_seconds=600,
                confirm=True,
                now=now,
                process_probe=lambda: ([], None),
            )
            assert removed["status"] == "removed", removed
            assert not lock.exists()
        finally:
            recovery.LOCK_PATH = original_lock_path

    print("git_index_lock_recovery smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
