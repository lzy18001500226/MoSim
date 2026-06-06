"""Conversation persistence for PentestAgent.

Saves/loads agent conversation history as JSON files under:
    {loot_base}/conversations/

Index file: conversations/index.json — list of {id, title, created_at, message_count}, newest first.
Each conversation: conversations/{id}.json — {id, title, created_at, messages: [...]}

Keeps at most MAX_CONVERSATIONS entries; older ones are pruned (file deleted).
"""

import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

log = logging.getLogger(__name__)


@dataclass
class ConversationMeta:
    id: str
    title: str
    created_at: str
    message_count: int


class ConversationStore:
    MAX_CONVERSATIONS = 20

    def __init__(self, base_path: Path) -> None:
        self._base = Path(base_path)

    def save(self, messages: list, conv_id: Optional[str] = None) -> Optional[str]:
        """Serialize messages to disk and update the index.

        If conv_id is given and already exists in the index, the file is
        overwritten and the index entry is updated in-place (no new entry).
        Otherwise a new conversation is created.

        Returns the conversation id, or None on failure.
        """
        from ..agents.base_agent import AgentMessage

        if not messages:
            return None
        try:
            entries = self._read_index()
            existing_idx = next(
                (i for i, e in enumerate(entries) if e.get("id") == conv_id), None
            )

            if conv_id is None or existing_idx is None:
                # New conversation
                conv_id = uuid.uuid4().hex
                created_at = datetime.now(timezone.utc).isoformat()
                is_new = True
            else:
                created_at = entries[existing_idx].get(
                    "created_at", datetime.now(timezone.utc).isoformat()
                )
                is_new = False

            title = ""
            for m in messages:
                if isinstance(m, AgentMessage) and m.role == "user" and m.content:
                    title = m.content[:80].replace("\n", " ").strip()
                    break
            if not title:
                title = f"Conversation {created_at[:10]}"

            serialized = [m.to_dict() for m in messages]
            conv_path = self._get_dir() / f"{conv_id}.json"
            conv_path.write_text(
                json.dumps(
                    {
                        "id": conv_id,
                        "title": title,
                        "created_at": created_at,
                        "messages": serialized,
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            entry = {
                "id": conv_id,
                "title": title,
                "created_at": created_at,
                "message_count": len(messages),
            }
            if is_new:
                entries.insert(0, entry)
                entries = self._prune(entries)
            else:
                entries[existing_idx] = entry
            self._write_index(entries)
            return conv_id
        except Exception as e:
            log.exception("ConversationStore.save failed: %s", e)
            return None

    def load(self, conv_id: str) -> list:
        """Load and deserialize a saved conversation. Returns [] on error."""
        from ..agents.base_agent import AgentMessage

        try:
            conv_path = self._get_dir() / f"{conv_id}.json"
            if not conv_path.exists():
                log.warning("Conversation not found: %s", conv_id)
                return []
            data = json.loads(conv_path.read_text(encoding="utf-8"))
            return [AgentMessage.from_dict(m) for m in data.get("messages", [])]
        except Exception as e:
            log.exception("ConversationStore.load failed for %s: %s", conv_id, e)
            return []

    def list_conversations(self) -> List[ConversationMeta]:
        """Return all saved conversations, newest first."""
        entries = self._read_index()
        return [
            ConversationMeta(
                id=e["id"],
                title=e.get("title", ""),
                created_at=e.get("created_at", ""),
                message_count=e.get("message_count", 0),
            )
            for e in entries
        ]

    def _get_dir(self) -> Path:
        self._base.mkdir(parents=True, exist_ok=True)
        return self._base

    def _read_index(self) -> list:
        index_path = self._get_dir() / "index.json"
        if not index_path.exists():
            return []
        try:
            return json.loads(index_path.read_text(encoding="utf-8"))
        except Exception as e:
            log.exception("Failed to read conversations index: %s", e)
            return []

    def _write_index(self, entries: list) -> None:
        index_path = self._get_dir() / "index.json"
        try:
            index_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")
        except Exception as e:
            log.exception("Failed to write conversations index: %s", e)

    def _prune(self, entries: list) -> list:
        """Remove files for entries beyond MAX_CONVERSATIONS."""
        if len(entries) <= self.MAX_CONVERSATIONS:
            return entries
        for e in entries[self.MAX_CONVERSATIONS :]:
            try:
                p = self._get_dir() / f"{e['id']}.json"
                if p.exists():
                    p.unlink()
            except Exception as ex:
                log.warning("Failed to prune conversation %s: %s", e.get("id"), ex)
        return entries[: self.MAX_CONVERSATIONS]
