"""Native Codex delegation transport helpers.

Delegation envelopes describe how a task arrived. They are transport metadata,
not an authorization token and must never widen the current task scope.
"""

from __future__ import annotations

import re


DELEGATION_CONTEXT_RE = re.compile(r"<\s*codex_delegation\b", re.IGNORECASE)
DELEGATION_INPUT_RE = re.compile(
    r"<\s*(?:input|prompt|message)\b[^>]*>([\s\S]*?)</\s*(?:input|prompt|message)\s*>",
    re.IGNORECASE,
)
DELEGATION_BODY_RE = re.compile(
    r"<\s*codex_delegation\b[^>]*>([\s\S]*?)</\s*codex_delegation\s*>",
    re.IGNORECASE,
)
DELEGATION_SOURCE_FIELD_RE = re.compile(
    r"<\s*(?:source[_-]?thread[_-]?id|source[_-]?thread|thread[_-]?id|from[_-]?thread[_-]?id)\b[^>]*>"
    r"[\s\S]*?</\s*(?:source[_-]?thread[_-]?id|source[_-]?thread|thread[_-]?id|from[_-]?thread[_-]?id)\s*>",
    re.IGNORECASE,
)


def is_delegation_context(prompt: str) -> bool:
    """Return whether input contains an internal delegation envelope."""

    return bool(DELEGATION_CONTEXT_RE.search(prompt or ""))


def delegated_task_input(prompt: str) -> str:
    """Return a nested task body when the native wrapper exposes one."""

    if not is_delegation_context(prompt):
        return ""
    match = DELEGATION_INPUT_RE.search(prompt)
    if match:
        return match.group(1).strip()

    # Native delegation metadata has changed shape across Codex surfaces. If
    # no legacy input tag is present, preserve the wrapper body as the task.
    body = DELEGATION_BODY_RE.search(prompt)
    if not body:
        return ""
    return DELEGATION_SOURCE_FIELD_RE.sub("", body.group(1)).strip()
