#!/usr/bin/env python3
"""Validate CoAgent permanent department conversation visibility metadata."""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path, PureWindowsPath
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "CoAgent" / "dispatch" / "department_threads.json"
INDEXES = [
    Path("/home/linux/.codex/session_index.jsonl"),
    Path("/mnt/c/Users/HP/.codex/session_index.jsonl"),
]
STATE_DBS = [
    Path("/home/linux/.codex/state_5.sqlite"),
    Path("/home/linux/.codex/sqlite/state_5.sqlite"),
    Path("/mnt/c/Users/HP/.codex/state_5.sqlite"),
]
CANONICAL_CWD = "/mnt/c/Users/HP/Desktop/MoSim"
VISIBLE_STATUSES = {"active_visible", "visible_pending_user_confirmation"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_registry() -> list[dict[str, Any]]:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    threads = data.get("threads")
    require(isinstance(threads, list), "registry threads must be a list")
    return threads


def index_contains(path: Path, thread_id: str, thread_name: str) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return thread_id in text and thread_name in text


def rollout_exists(raw_path: str | None) -> bool:
    if not raw_path:
        return False
    path = Path(raw_path)
    if path.exists():
        return True
    match = re.match(r"^([A-Za-z]):\\(.*)$", raw_path)
    if not match:
        return False
    drive = match.group(1).lower()
    rest = match.group(2).replace("\\", "/")
    wsl_path = Path("/mnt") / drive / PureWindowsPath(rest).as_posix()
    return wsl_path.exists()


def db_row_ok(path: Path, thread_id: str, thread_name: str, *, strict_cwd: bool) -> bool:
    if not path.exists():
        return False
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        row = con.execute(
            """
            select title, source, thread_source, has_user_event, archived, rollout_path, cwd
            from threads
            where id=?
            """,
            (thread_id,),
        ).fetchone()
    finally:
        con.close()
    if not row:
        return False
    rollout_path = row[5]
    return bool(
        row[0] == thread_name
        and row[1] == "vscode"
        and row[2] == "vscode"
        and row[3] == 1
        and row[4] == 0
        and ((row[6] == CANONICAL_CWD) if strict_cwd else bool(row[6]))
        and rollout_path
        and rollout_exists(rollout_path)
    )


def legacy_main_db_row_ok(path: Path, thread_id: str) -> bool:
    if not path.exists():
        return False
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        row = con.execute(
            """
            select source, has_user_event, archived, rollout_path, cwd
            from threads
            where id=?
            """,
            (thread_id,),
        ).fetchone()
    finally:
        con.close()
    if not row:
        return False
    cwd = str(row[4] or "")
    return bool(
        row[0] == "vscode"
        and row[1] == 1
        and row[2] == 0
        and row[3]
        and rollout_exists(row[3])
        and cwd.lower() == CANONICAL_CWD.lower()
    )


def check() -> dict[str, Any]:
    threads = load_registry()
    rows = []
    require(threads, "registry has no department threads")
    for item in threads:
        department = str(item["department"])
        thread_id = str(item["thread_id"])
        thread_name = str(item["thread_name"])
        status = str(item["status"])
        require(thread_id, f"{department} missing thread_id")
        require(thread_name.startswith("MoSim｜"), f"{department} has unexpected title: {thread_name}")
        require(status in VISIBLE_STATUSES, f"{department} has non-visible status {status}")
        if department == "MainAgent":
            require(status == "active_visible", "MainAgent must remain active_visible")
        index_ok = [index_contains(path, thread_id, thread_name) for path in INDEXES]
        if department == "MainAgent":
            db_ok = [legacy_main_db_row_ok(path, thread_id) for path in STATE_DBS]
        else:
            db_ok = [db_row_ok(path, thread_id, thread_name, strict_cwd=True) for path in STATE_DBS]
        require(all(index_ok), f"{department} missing index entry")
        require(all(db_ok), f"{department} missing valid state DB row or rollout file")
        rows.append(
            {
                "department": department,
                "thread_name": thread_name,
                "thread_id": thread_id,
                "status": status,
                "index_ok": index_ok,
                "db_ok": db_ok,
            }
        )
    return {
        "ok": True,
        "state": "registry_visibility_metadata_ok",
        "department_count": len(rows),
        "active_visible": [row["department"] for row in rows if row["status"] == "active_visible"],
        "pending_user_confirmation": [
            row["department"] for row in rows if row["status"] == "visible_pending_user_confirmation"
        ],
        "rows": rows,
    }


def main() -> int:
    print(json.dumps(check(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
