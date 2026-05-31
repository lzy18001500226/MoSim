#!/usr/bin/env python3
"""Diagnose and repair local Codex department session records.

The default mode is read-only. `restore --apply` writes to a selected Codex home
after backing up the affected index/database files.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "CoAgent" / "dispatch" / "department_threads.json"
DEFAULT_CODEX_HOME = Path("/home/linux/.codex")
DEFAULT_BACKUP_ROOT = DEFAULT_CODEX_HOME / "backups" / "deleted_department_rollouts_20260526_193424"
DEFAULT_WINDOWS_CODEX_HOME = Path("/mnt/c/Users/HP/.codex")


def load_registry(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8")).get("threads", [])


def selected_threads(args: argparse.Namespace) -> list[dict[str, Any]]:
    threads = load_registry(args.registry)
    wanted = set(args.department or [])
    if wanted:
        threads = [item for item in threads if item.get("department") in wanted]
    if not threads:
        raise SystemExit("no matching department entries")
    return threads


def parse_iso_seconds(value: str | None) -> int:
    if not value:
        return 0
    try:
        return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return 0


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def rollout_metadata(path: Path, thread: dict[str, Any]) -> dict[str, Any]:
    records = read_jsonl(path)
    meta = next((item.get("payload", {}) for item in records if item.get("type") == "session_meta"), {})
    user_message = ""
    assistant_message = ""
    latest_ts = meta.get("timestamp") or ""
    for item in records:
        timestamp = item.get("timestamp") or ""
        if timestamp:
            latest_ts = timestamp
        payload = item.get("payload", {})
        if item.get("type") == "event_msg" and payload.get("type") == "user_message" and not user_message:
            user_message = payload.get("message", "")
        if item.get("type") == "event_msg" and payload.get("type") == "agent_message":
            assistant_message = payload.get("message", assistant_message)
    thread_name = thread.get("thread_name") or thread.get("department") or meta.get("id")
    created_at = parse_iso_seconds(meta.get("timestamp")) or parse_iso_seconds(latest_ts)
    updated_at = parse_iso_seconds(latest_ts) or created_at
    git = meta.get("git") if isinstance(meta.get("git"), dict) else {}
    return {
        "id": thread.get("thread_id") or meta.get("id"),
        "thread_name": thread_name,
        "cwd": meta.get("cwd") or str(ROOT),
        "created_at": created_at,
        "updated_at": updated_at,
        "created_at_ms": created_at * 1000 if created_at else None,
        "updated_at_ms": updated_at * 1000 if updated_at else None,
        "model_provider": meta.get("model_provider") or "OpenAI",
        "cli_version": meta.get("cli_version") or "",
        "source": "vscode",
        "thread_source": "vscode",
        "model": meta.get("model") or "gpt-5.5",
        "reasoning_effort": meta.get("reasoning_effort") or "high",
        "sandbox_policy": json.dumps({"type": "danger-full-access"}, separators=(",", ":")),
        "approval_mode": "never",
        "first_user_message": user_message or thread_name,
        "preview": assistant_message or f"{thread_name}：部门线程已建立，等待任务单。",
        "git_sha": git.get("commit_hash"),
        "git_branch": git.get("branch"),
        "git_origin_url": git.get("repository_url"),
    }


def find_live_rollout(codex_home: Path, thread_id: str) -> Path | None:
    sessions = codex_home / "sessions"
    if not sessions.exists():
        return None
    matches = sorted(sessions.rglob(f"*{thread_id}*.jsonl"))
    return matches[0] if matches else None


def find_backup_rollout(backup_roots: list[Path], thread_id: str) -> Path | None:
    for root in backup_roots:
        if not root.exists():
            continue
        matches = sorted(root.rglob(f"rollout-*{thread_id}.jsonl"))
        if matches:
            return matches[0]
    return None


def rollout_destination(codex_home: Path, rollout: Path) -> Path:
    match = re.match(r"rollout-(\d{4})-(\d{2})-(\d{2})T", rollout.name)
    if not match:
        return codex_home / "sessions" / rollout.name
    year, month, day = match.groups()
    return codex_home / "sessions" / year / month / day / rollout.name


def backup_existing(codex_home: Path, paths: list[Path]) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = codex_home / "backups" / f"coagent-session-restore-{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    for path in paths:
        if path.exists():
            target = backup_dir / path.relative_to(codex_home).as_posix().replace("/", "__")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
    return backup_dir


def upsert_session_index(index_path: Path, thread_id: str, thread_name: str, updated_at: str) -> None:
    entry = {"id": thread_id, "thread_name": thread_name, "updated_at": updated_at}
    lines = []
    replaced = False
    if index_path.exists():
        for line in index_path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                lines.append(line)
                continue
            if item.get("id") == thread_id:
                lines.append(json.dumps(entry, ensure_ascii=False, separators=(",", ":")))
                replaced = True
            else:
                lines.append(line)
    if not replaced:
        lines.append(json.dumps(entry, ensure_ascii=False, separators=(",", ":")))
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def db_candidates(codex_home: Path) -> list[Path]:
    return [codex_home / "state_5.sqlite", codex_home / "sqlite" / "state_5.sqlite"]


def sqlite_state_paths(db_path: Path) -> list[Path]:
    return [db_path, Path(str(db_path) + "-wal"), Path(str(db_path) + "-shm")]


def codex_backup_paths(codex_home: Path, rollout_path: Path | None = None) -> list[Path]:
    paths = [codex_home / "session_index.jsonl"]
    for db_path in db_candidates(codex_home):
        paths.extend(sqlite_state_paths(db_path))
    if rollout_path is not None:
        paths.append(rollout_path)
    return paths


def db_rollout_path_value(path: Path) -> str:
    parts = path.parts
    if len(parts) >= 4 and parts[1] == "mnt" and len(parts[2]) == 1:
        drive = f"{parts[2].upper()}:/"
        return str(PureWindowsPath(drive, *parts[3:]))
    return str(path)


def read_thread_db_row(codex_home: Path, thread_id: str) -> dict[str, Any] | None:
    for db_path in db_candidates(codex_home):
        if not db_path.exists():
            continue
        con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            columns = [row[1] for row in con.execute("pragma table_info(threads)")]
            if not columns:
                continue
            row = con.execute(f"select {','.join(columns)} from threads where id=?", (thread_id,)).fetchone()
            if row:
                return dict(zip(columns, row))
        finally:
            con.close()
    return None


def upsert_thread_db(db_path: Path, meta: dict[str, Any], rollout_path: Path | str) -> bool:
    if not db_path.exists():
        return False
    values = {
        "id": meta["id"],
        "rollout_path": str(rollout_path),
        "created_at": meta["created_at"],
        "updated_at": meta["updated_at"],
        "source": meta["source"],
        "model_provider": meta["model_provider"],
        "cwd": meta["cwd"],
        "title": meta["thread_name"],
        "sandbox_policy": meta["sandbox_policy"],
        "approval_mode": meta["approval_mode"],
        "tokens_used": 0,
        "has_user_event": 1,
        "archived": 0,
        "archived_at": None,
        "git_sha": meta.get("git_sha"),
        "git_branch": meta.get("git_branch"),
        "git_origin_url": meta.get("git_origin_url"),
        "cli_version": meta["cli_version"],
        "first_user_message": meta["first_user_message"],
        "agent_nickname": None,
        "agent_role": None,
        "memory_mode": "enabled",
        "model": meta["model"],
        "reasoning_effort": meta["reasoning_effort"],
        "agent_path": None,
        "created_at_ms": meta["created_at_ms"],
        "updated_at_ms": meta["updated_at_ms"],
        "thread_source": meta["thread_source"],
        "preview": meta["preview"],
    }
    con = sqlite3.connect(str(db_path))
    try:
        columns = [row[1] for row in con.execute("pragma table_info(threads)")]
        insert_cols = [column for column in columns if column in values]
        update_cols = [column for column in insert_cols if column != "id"]
        update_sql = ",".join(f"{column}=?" for column in update_cols)
        cursor = con.execute(
            f"update threads set {update_sql} where id=?",
            [values[column] for column in update_cols] + [values["id"]],
        )
        if cursor.rowcount:
            con.commit()
            return True
        placeholders = ",".join("?" for _ in insert_cols)
        sql = f"insert into threads ({','.join(insert_cols)}) values ({placeholders})"
        con.execute(sql, [values[column] for column in insert_cols])
        con.commit()
    finally:
        con.close()
    return True


def sync_visible_metadata(
    *,
    source_rollout: Path,
    source_row: dict[str, Any] | None,
    thread_id: str,
    thread_name: str,
    preview: str | None,
    cwd: str | None = None,
) -> dict[str, Any]:
    meta = rollout_metadata(source_rollout, {"thread_id": thread_id, "thread_name": thread_name})
    now = int(datetime.now(timezone.utc).timestamp())
    source_row = source_row or {}
    meta.update(
        {
            "id": thread_id,
            "thread_name": thread_name,
            "cwd": cwd or source_row.get("cwd") or meta["cwd"],
            "created_at": source_row.get("created_at") or meta["created_at"] or now,
            "updated_at": now,
            "created_at_ms": source_row.get("created_at_ms") or meta["created_at_ms"] or now * 1000,
            "updated_at_ms": now * 1000,
            "model_provider": source_row.get("model_provider") or meta["model_provider"],
            "cli_version": source_row.get("cli_version") or meta["cli_version"],
            "source": "vscode",
            "thread_source": "vscode",
            "model": source_row.get("model") or meta["model"],
            "reasoning_effort": source_row.get("reasoning_effort") or meta["reasoning_effort"],
            "first_user_message": thread_name,
            "preview": preview or thread_name,
            "git_sha": source_row.get("git_sha") or meta.get("git_sha"),
            "git_branch": source_row.get("git_branch") or meta.get("git_branch"),
            "git_origin_url": source_row.get("git_origin_url") or meta.get("git_origin_url"),
        }
    )
    return meta


def sync_visible_plan(args: argparse.Namespace) -> dict[str, Any]:
    source_rollout = find_live_rollout(args.source_codex_home, args.thread_id)
    if source_rollout is None:
        raise SystemExit(f"missing source rollout for {args.thread_id} under {args.source_codex_home}")
    source_row = read_thread_db_row(args.source_codex_home, args.thread_id)
    targets = args.target_codex_home or [args.source_codex_home]
    meta = sync_visible_metadata(
        source_rollout=source_rollout,
        source_row=source_row,
        thread_id=args.thread_id,
        thread_name=args.thread_name,
        preview=args.preview,
        cwd=args.cwd,
    )
    items = []
    for target_home in targets:
        target_rollout = rollout_destination(target_home, source_rollout)
        existing_row = read_thread_db_row(target_home, args.thread_id)
        items.append(
            {
                "target_codex_home": str(target_home),
                "target_rollout": str(target_rollout),
                "db_rollout_path": db_rollout_path_value(target_rollout),
                "session_index": str(target_home / "session_index.jsonl"),
                "state_dbs": [str(path) for path in db_candidates(target_home) if path.exists()],
                "existing_title": existing_row.get("title") if existing_row else "",
                "existing_source": existing_row.get("source") if existing_row else "",
                "existing_thread_source": existing_row.get("thread_source") if existing_row else "",
                "existing_has_user_event": existing_row.get("has_user_event") if existing_row else None,
                "action": "sync_visible_metadata",
            }
        )
    return {
        "thread_id": args.thread_id,
        "thread_name": args.thread_name,
        "source_codex_home": str(args.source_codex_home),
        "source_rollout": str(source_rollout),
        "source_row_found": bool(source_row),
        "targets": items,
        "metadata": {
            "title": meta["thread_name"],
            "source": meta["source"],
            "thread_source": meta["thread_source"],
            "has_user_event": 1,
            "archived": 0,
            "preview": meta["preview"],
            "cwd": meta["cwd"],
        },
    }


def cmd_sync_visible(args: argparse.Namespace) -> int:
    plan = sync_visible_plan(args)
    if not args.apply:
        plan["dry_run"] = True
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    source_rollout = Path(plan["source_rollout"])
    source_row = read_thread_db_row(args.source_codex_home, args.thread_id)
    meta = sync_visible_metadata(
        source_rollout=source_rollout,
        source_row=source_row,
        thread_id=args.thread_id,
        thread_name=args.thread_name,
        preview=args.preview,
        cwd=args.cwd,
    )
    updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    applied = []
    for item in plan["targets"]:
        target_home = Path(item["target_codex_home"])
        target_rollout = Path(item["target_rollout"])
        backup_dir = backup_existing(target_home, codex_backup_paths(target_home, target_rollout))
        target_rollout.parent.mkdir(parents=True, exist_ok=True)
        if source_rollout.resolve() != target_rollout.resolve():
            shutil.copy2(source_rollout, target_rollout)
        upsert_session_index(target_home / "session_index.jsonl", meta["id"], meta["thread_name"], updated_at)
        updated_dbs = []
        rollout_value = db_rollout_path_value(target_rollout)
        for db_path in db_candidates(target_home):
            if upsert_thread_db(db_path, meta, rollout_value):
                updated_dbs.append(str(db_path))
        applied.append(
            {
                "target_codex_home": str(target_home),
                "backup_dir": str(backup_dir),
                "target_rollout": str(target_rollout),
                "db_rollout_path": rollout_value,
                "updated_dbs": updated_dbs,
            }
        )
    print(json.dumps({"ok": True, "thread_id": args.thread_id, "thread_name": args.thread_name, "applied": applied}, ensure_ascii=False, indent=2))
    return 0


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    codex_home = args.codex_home
    backup_roots = args.backup_root or [DEFAULT_BACKUP_ROOT]
    items = []
    for thread in selected_threads(args):
        thread_id = thread.get("thread_id", "")
        live = find_live_rollout(codex_home, thread_id) if thread_id else None
        backup = find_backup_rollout(backup_roots, thread_id) if thread_id else None
        items.append(
            {
                "department": thread.get("department"),
                "thread_name": thread.get("thread_name"),
                "thread_id": thread_id,
                "live_rollout": str(live) if live else "",
                "backup_rollout": str(backup) if backup else "",
                "action": "ok" if live else "restore_rollout" if backup else "missing_backup",
            }
        )
    return {"codex_home": str(codex_home), "backup_roots": [str(path) for path in backup_roots], "items": items}


def cmd_diagnose(args: argparse.Namespace) -> int:
    print(json.dumps(build_plan(args), ensure_ascii=False, indent=2))
    return 0


def cmd_restore(args: argparse.Namespace) -> int:
    plan = build_plan(args)
    if not args.apply:
        plan["dry_run"] = True
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    codex_home = args.codex_home
    backup_paths = [codex_home / "session_index.jsonl", codex_home / "state_5.sqlite", codex_home / "sqlite" / "state_5.sqlite"]
    backup_dir = backup_existing(codex_home, backup_paths)
    restored = []
    now = datetime.now().astimezone().isoformat()
    threads_by_id = {item.get("thread_id"): item for item in selected_threads(args)}
    for item in plan["items"]:
        if item["action"] == "ok":
            continue
        if item["action"] != "restore_rollout":
            continue
        thread = threads_by_id[item["thread_id"]]
        source = Path(item["backup_rollout"])
        destination = rollout_destination(codex_home, source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        meta = rollout_metadata(destination, thread)
        upsert_session_index(codex_home / "session_index.jsonl", meta["id"], meta["thread_name"], now)
        updated_dbs = []
        for db_path in [codex_home / "state_5.sqlite", codex_home / "sqlite" / "state_5.sqlite"]:
            if upsert_thread_db(db_path, meta, destination):
                updated_dbs.append(str(db_path))
        restored.append(
            {
                "department": item["department"],
                "thread_id": item["thread_id"],
                "source": str(source),
                "destination": str(destination),
                "updated_dbs": updated_dbs,
            }
        )
    print(json.dumps({"ok": True, "backup_dir": str(backup_dir), "restored": restored}, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--codex-home", type=Path, default=DEFAULT_CODEX_HOME)
    parser.add_argument("--backup-root", type=Path, action="append")
    parser.add_argument("--department", action="append")
    sub = parser.add_subparsers(dest="command", required=True)
    diagnose = sub.add_parser("diagnose")
    diagnose.set_defaults(func=cmd_diagnose)
    restore = sub.add_parser("restore")
    restore.add_argument("--apply", action="store_true")
    restore.set_defaults(func=cmd_restore)
    sync = sub.add_parser("sync-visible")
    sync.add_argument("--thread-id", required=True)
    sync.add_argument("--thread-name", required=True)
    sync.add_argument("--preview")
    sync.add_argument("--cwd")
    sync.add_argument("--source-codex-home", type=Path, default=DEFAULT_CODEX_HOME)
    sync.add_argument("--target-codex-home", type=Path, action="append")
    sync.add_argument("--apply", action="store_true")
    sync.set_defaults(func=cmd_sync_visible)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
