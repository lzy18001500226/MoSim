#!/usr/bin/env python3
"""Regression checks for task-local MoSim startup context."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STARTUP_FILES = (
    "AGENTS.md",
    "Docs/Workflows/new_conversation_context.md",
    "Docs/Workflows/single_thread_operating_model.md",
)
FORBIDDEN_STARTUP_PHRASES = (
    "current P0 is always",
    "sole task authority",
    "one active coordinating Codex thread",
    "the current board selects the task",
    "use the current board for the next action",
    "current task selector is",
)
THREAD_ID = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
    re.IGNORECASE,
)


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _compact(text: str) -> str:
    without_quote_markers = re.sub(r"(?m)^\s*>\s?", "", text)
    return " ".join(without_quote_markers.split())


def test_startup_context_is_task_local() -> None:
    agents = _compact(_read("AGENTS.md"))
    context = _compact(_read("Docs/Workflows/new_conversation_context.md"))
    operating_model = _compact(_read("Docs/Workflows/single_thread_operating_model.md"))

    assert "newest direct user instruction in the current conversation" in agents
    assert "There is no global MoSim conversation mainline" in context
    assert "There is no project-wide coordinating thread" in operating_model
    assert "Do not load `Docs/Workflows/mainline_operations_board.md` during ordinary" in agents
    assert "Do not read `Docs/Workflows/mainline_operations_board.md` as part of startup" in context
    assert "Read-only inspection may run in parallel." in agents
    assert "A given path has at most one active writer" in agents
    assert "independent repository worktree and branch" in agents


def test_startup_context_cannot_embed_cross_task_routing() -> None:
    for relative in STARTUP_FILES:
        text = _read(relative)
        assert not THREAD_ID.search(text), f"startup file embeds a task/thread ID: {relative}"
        lowered = text.lower()
        for phrase in FORBIDDEN_STARTUP_PHRASES:
            assert phrase.lower() not in lowered, f"stale global routing phrase in {relative}: {phrase}"


def test_retired_board_is_explicitly_non_authoritative() -> None:
    board = _compact(_read("Docs/Workflows/mainline_operations_board.md"))
    assert "RETIRED ROUTING PATH" in board
    assert "not a task selector" in board
    assert "MoSim has no global conversation mainline" in board
    assert "newest direct user instruction is the only execution authority" in board


def test_task_local_companions_cannot_restore_board_or_owner_routing() -> None:
    progress = _compact(_read("PROGRESS.md"))
    capability_index = _compact(_read("Docs/Index/capability_index.md"))
    hook = _read("Scripts/hooks/codex_native_hook.py")
    machine_index = json.loads(
        _read("Config/capabilities/capability_index.json")
    )

    assert "not a transcript, task selector, or authorization source" in progress
    assert "only current-task selector" not in progress
    assert "current user's direct request" in capability_index
    assert "current PMO board" not in capability_index
    assert "current P0 minimum big system" not in capability_index
    assert "mainline_operations_board" not in hook
    assert machine_index["status"] == "task_local_machine_readable_index"
    serialized_index = json.dumps(machine_index, ensure_ascii=False).lower()
    assert "current_coordinating_thread" not in serialized_index
