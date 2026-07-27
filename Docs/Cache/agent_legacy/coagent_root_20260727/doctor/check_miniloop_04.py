#!/usr/bin/env python3
"""Validate COAGENT-MINILOOP-04 as a visible but non-dispatchable test loop."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "Results" / "coagent_miniloop" / "COAGENT-MINILOOP-04"
THREAD_ID = "019e7373-37f4-75e1-9780-e1519a489715"
THREAD_NAME = "MoSim｜候选测试闭环"
REAL_TUI_THREAD_ID = "019e73e5-d97d-75a3-ba72-b52e19d755b3"
REAL_TUI_THREAD_NAME = "MoSim｜可见对话测试"
CANONICAL_CWD = "/mnt/c/Users/HP/Desktop/MoSim"

REQUIRED_FILES = [
    "scoped_task_packet.md",
    "repair_packet.md",
    "worker_result_packet.json",
    "visibility_review.md",
]


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise AssertionError(f"{path} must contain a JSON object")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def require_index(path: Path, thread_id: str, thread_name: str) -> None:
    require(path.exists(), f"missing session index: {path}")
    matches = [
        line
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
        if thread_id in line and thread_name in line
    ]
    require(matches, f"thread missing from session index: {path}")


def require_db(path: Path, thread_id: str, thread_name: str) -> None:
    import sqlite3

    require(path.exists(), f"missing Codex state DB: {path}")
    con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        row = con.execute(
            """
            select title, source, thread_source, has_user_event, archived, cwd
            from threads
            where id=?
            """,
            (thread_id,),
        ).fetchone()
    finally:
        con.close()
    require(row is not None, f"thread missing from Codex state DB: {path}")
    title, source, thread_source, has_user_event, archived, cwd = row
    require(title == thread_name, f"unexpected title in {path}: {title}")
    require(source == "vscode", f"unexpected source in {path}: {source}")
    require(thread_source == "vscode", f"unexpected thread_source in {path}: {thread_source}")
    require(has_user_event == 1, f"has_user_event not set in {path}")
    require(archived == 0, f"thread archived in {path}")
    require(cwd == CANONICAL_CWD, f"unexpected cwd in {path}: {cwd}")


def check() -> dict[str, Any]:
    missing = [name for name in REQUIRED_FILES if not (BUNDLE / name).exists()]
    require(not missing, f"missing files: {missing}")

    result = load_json(BUNDLE / "worker_result_packet.json")
    require(result.get("task_id") == "COAGENT-MINILOOP-04", "worker result task_id mismatch")
    require(result.get("status") == "done", "worker result status mismatch")
    require(result.get("summary"), "worker result missing summary")
    require(result.get("visible_confirmation_required") is True, "visible confirmation gate missing")
    forbidden = result.get("forbidden_actions_observed", {})
    for key in ["git_used", "mcp_used", "outside_project_write"]:
        require(forbidden.get(key) is False, f"forbidden action observed: {key}")

    summary = ROOT / "Results" / "agent_packets" / "summaries" / "COAGENT-MINILOOP-04.summary.md"
    review = ROOT / "Results" / "agent_packets" / "reviews" / "COAGENT-MINILOOP-04.review.json"
    require(summary.exists(), "missing result router summary")
    require(review.exists(), "missing result router review")
    summary_text = summary.read_text(encoding="utf-8")
    require("review_status: `accepted`" in summary_text, "router summary does not show accepted")
    require("runtime_state: `done`" in summary_text, "router summary does not show runtime done")

    visibility = (BUNDLE / "visibility_review.md").read_text(encoding="utf-8")
    require(
        "real_tui_thread_synced_awaiting_user_confirmation" in visibility,
        "visibility review must record real TUI synced awaiting confirmation state",
    )
    require("visibility-repair-20260529T125333Z" in visibility, "visibility repair backup missing")
    require("coagent-session-restore-20260529-210054" in visibility, "CoAgent sync backup missing")
    require("codex_session_repair.py sync-visible" in visibility, "sync-visible command missing")
    require("source: vscode" in visibility, "visibility repair source field missing")
    require("has_user_event: 1" in visibility, "visibility repair user-event field missing")
    require("real_tui_backup_windows" in visibility, "real TUI sync backup missing")
    require(REAL_TUI_THREAD_ID in visibility, "real TUI thread id missing")
    require(REAL_TUI_THREAD_NAME in visibility, "real TUI thread name missing")
    require("must not be registered as `active_visible` unless" in visibility, "active-visible gate missing")
    require("user must confirm" in visibility, "user visibility confirmation gate missing")
    require(THREAD_ID in visibility, "candidate thread id missing from visibility review")

    for index_path in [
        Path("/home/linux/.codex/session_index.jsonl"),
        Path("/mnt/c/Users/HP/.codex/session_index.jsonl"),
    ]:
        require_index(index_path, THREAD_ID, THREAD_NAME)
        require_index(index_path, REAL_TUI_THREAD_ID, REAL_TUI_THREAD_NAME)
    for db_path in [
        Path("/home/linux/.codex/state_5.sqlite"),
        Path("/home/linux/.codex/sqlite/state_5.sqlite"),
        Path("/mnt/c/Users/HP/.codex/state_5.sqlite"),
    ]:
        require_db(db_path, THREAD_ID, THREAD_NAME)
        require_db(db_path, REAL_TUI_THREAD_ID, REAL_TUI_THREAD_NAME)

    registry = load_json(ROOT / "CoAgent" / "dispatch" / "department_threads.json")
    active_ids = [item.get("thread_id") for item in registry["threads"] if item.get("status") == "active_visible"]
    require(THREAD_ID not in active_ids, "candidate thread must not be active_visible before user confirmation")
    require(REAL_TUI_THREAD_ID not in active_ids, "real TUI test thread must not be active_visible before user confirmation")

    return {
        "ok": True,
        "task_id": "COAGENT-MINILOOP-04",
        "state": "real_tui_thread_synced_awaiting_user_confirmation",
        "thread_id": THREAD_ID,
        "real_tui_thread_id": REAL_TUI_THREAD_ID,
        "files_checked": len(REQUIRED_FILES),
        "limitation": "The candidate conversation produced and repaired a valid result packet. A real WSL Codex TUI test thread has been created and synced to WSL/Windows visibility metadata. Both remain non-dispatchable until the user confirms the thread is visible and openable in VSCode Codex/Codex App.",
    }


def main() -> int:
    print(json.dumps(check(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
