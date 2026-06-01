"""Internal context module for grok-search (SQLite).

Features:
- thread_id + task_id context routing
- optional auto routing based on continuation cues
- persistent storage with SQLite
- context trimming with optional summarizer

Note: internal module, not exposed as standalone tool.
"""

from __future__ import annotations

import json
import re
import sqlite3
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple


DEFAULT_CONTINUATION_PATTERNS = [
    r"继续",
    r"刚才",
    r"上次",
    r"这个",
    r"那个",
    r"前面",
    r"再说",
    r"延续",
    r"\bfollow up\b",
    r"\bcontinue\b",
    r"\bprevious\b",
    r"\bthat\b",
    r"\bthis\b",
]


def estimate_tokens(text: str) -> int:
    """Rough token estimator (no external deps)."""
    if not text:
        return 0
    return max(1, len(text) // 4)


@dataclass
class ContextConfig:
    max_messages: int = 8
    max_context_tokens: int = 4000
    summary_trigger_tokens: int = 3200
    max_summary_tokens: int = 800
    ttl_seconds: int = 24 * 3600
    continuation_patterns: List[str] = field(default_factory=lambda: list(DEFAULT_CONTINUATION_PATTERNS))


@dataclass
class ContextSnapshot:
    messages: List[Dict[str, Any]]
    summary: str
    meta: Dict[str, Any]


@dataclass
class RouteDecision:
    thread_id: str
    task_id: str
    include_context: bool
    reason: str
    snapshot: Optional[ContextSnapshot]


class ContextStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS contexts (
                    thread_id TEXT NOT NULL,
                    task_id TEXT NOT NULL,
                    messages_json TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    meta_json TEXT NOT NULL,
                    created_at INTEGER NOT NULL,
                    updated_at INTEGER NOT NULL,
                    PRIMARY KEY (thread_id, task_id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS thread_state (
                    thread_id TEXT PRIMARY KEY,
                    last_task_id TEXT NOT NULL,
                    updated_at INTEGER NOT NULL
                )
                """
            )

    def get_context(self, thread_id: str, task_id: str) -> Optional[ContextSnapshot]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT messages_json, summary, meta_json FROM contexts WHERE thread_id=? AND task_id=?",
                (thread_id, task_id),
            ).fetchone()
            if not row:
                return None
            messages = json.loads(row["messages_json"])
            summary = row["summary"]
            meta = json.loads(row["meta_json"]) if row["meta_json"] else {}
            return ContextSnapshot(messages=messages, summary=summary, meta=meta)

    def upsert_context(
        self,
        thread_id: str,
        task_id: str,
        messages: List[Dict[str, Any]],
        summary: str = "",
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        now = int(time.time())
        meta_json = json.dumps(meta or {}, ensure_ascii=False)
        messages_json = json.dumps(messages, ensure_ascii=False)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO contexts (thread_id, task_id, messages_json, summary, meta_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(thread_id, task_id) DO UPDATE SET
                    messages_json=excluded.messages_json,
                    summary=excluded.summary,
                    meta_json=excluded.meta_json,
                    updated_at=excluded.updated_at
                """,
                (thread_id, task_id, messages_json, summary, meta_json, now, now),
            )

    def update_thread_state(self, thread_id: str, task_id: str) -> None:
        now = int(time.time())
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO thread_state (thread_id, last_task_id, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(thread_id) DO UPDATE SET
                    last_task_id=excluded.last_task_id,
                    updated_at=excluded.updated_at
                """,
                (thread_id, task_id, now),
            )

    def get_last_task(self, thread_id: str) -> Optional[Tuple[str, int]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT last_task_id, updated_at FROM thread_state WHERE thread_id=?",
                (thread_id,),
            ).fetchone()
            if not row:
                return None
            return row["last_task_id"], int(row["updated_at"])

    def prune_expired(self, ttl_seconds: int) -> int:
        cutoff = int(time.time()) - ttl_seconds
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM contexts WHERE updated_at < ?", (cutoff,))
            return cur.rowcount


class ContextRouter:
    def __init__(
        self,
        store: ContextStore,
        config: Optional[ContextConfig] = None,
        summarizer: Optional[Callable[[List[Dict[str, Any]], str], str]] = None,
    ) -> None:
        self.store = store
        self.config = config or ContextConfig()
        self._continuation_re = re.compile("|".join(self.config.continuation_patterns), re.IGNORECASE)
        self.summarizer = summarizer

    def _is_continuation(self, text: str) -> bool:
        if not text:
            return False
        return bool(self._continuation_re.search(text))

    def route(
        self,
        thread_id: str,
        user_text: str,
        task_id: Optional[str] = None,
        mode: str = "auto",
        need_context_hint: Optional[bool] = None,
    ) -> RouteDecision:
        """Decide task_id and whether to include context."""
        now = int(time.time())
        include_context = False
        reason = ""

        last_task = self.store.get_last_task(thread_id)
        last_task_id = last_task[0] if last_task else None
        last_seen = last_task[1] if last_task else 0
        within_ttl = (now - last_seen) <= self.config.ttl_seconds

        if task_id:
            effective_task_id = task_id
            reason = "explicit_task_id"
        else:
            is_cont = self._is_continuation(user_text)
            if mode != "stateless" and (need_context_hint or is_cont) and last_task_id and within_ttl:
                effective_task_id = last_task_id
                reason = "reuse_last_task"
            else:
                effective_task_id = uuid.uuid4().hex
                reason = "new_task"

        if mode == "always":
            include_context = True
        elif mode == "stateless":
            include_context = False
        else:
            include_context = bool(need_context_hint) or self._is_continuation(user_text)

        snapshot = self.store.get_context(thread_id, effective_task_id) if include_context else None
        self.store.update_thread_state(thread_id, effective_task_id)
        return RouteDecision(
            thread_id=thread_id,
            task_id=effective_task_id,
            include_context=include_context,
            reason=reason,
            snapshot=snapshot,
        )

    def build_context_messages(self, snapshot: Optional[ContextSnapshot]) -> List[Dict[str, Any]]:
        if not snapshot:
            return []
        messages = []
        if snapshot.summary:
            messages.append({"role": "system", "content": f"上下文摘要：{snapshot.summary}"})
        messages.extend(snapshot.messages)
        return messages

    def record_turn(
        self,
        thread_id: str,
        task_id: str,
        user_text: str,
        assistant_text: str,
        meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        snapshot = self.store.get_context(thread_id, task_id)
        messages = list(snapshot.messages) if snapshot else []
        summary = snapshot.summary if snapshot else ""
        stored_meta = snapshot.meta if snapshot else {}

        now = int(time.time())
        messages.append({"role": "user", "content": user_text, "ts": now})
        messages.append({"role": "assistant", "content": assistant_text, "ts": now})

        messages, summary = self._trim_and_summarize(messages, summary)
        if meta:
            stored_meta.update(meta)

        self.store.upsert_context(thread_id, task_id, messages, summary, stored_meta)

    def _trim_and_summarize(
        self,
        messages: List[Dict[str, Any]],
        summary: str,
    ) -> Tuple[List[Dict[str, Any]], str]:
        """Trim messages to stay within limits, optionally summarize removed messages."""
        max_messages = self.config.max_messages
        max_tokens = self.config.max_context_tokens
        summary_trigger = self.config.summary_trigger_tokens

        def current_tokens() -> int:
            total = estimate_tokens(summary)
            for m in messages:
                total += estimate_tokens(m.get("content", ""))
            return total

        # If within limits, keep as is
        if len(messages) <= max_messages and current_tokens() <= max_tokens:
            return messages, summary

        # Remove oldest messages until under limits
        removed: List[Dict[str, Any]] = []
        while messages and (len(messages) > max_messages or current_tokens() > max_tokens):
            removed.append(messages.pop(0))

        # Summarize removed messages if provided and summary size is beyond trigger
        if self.summarizer and (estimate_tokens(summary) >= summary_trigger or removed):
            try:
                summary = self.summarizer(removed, summary)
                # Hard cap summary length
                if estimate_tokens(summary) > self.config.max_summary_tokens:
                    summary = summary[: self.config.max_summary_tokens * 4]
            except Exception:
                # Fall back silently
                pass

        return messages, summary


__all__ = [
    "ContextConfig",
    "ContextStore",
    "ContextRouter",
    "ContextSnapshot",
    "RouteDecision",
    "estimate_tokens",
]
