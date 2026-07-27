#!/usr/bin/env python3
"""Smoke test for CoAgent task-surface and review/merge design docs."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def assert_contains(path: Path, required: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for item in required:
        assert item in text, (path, item)


def main() -> int:
    task_surface = ROOT / "CoAgent" / "docs" / "architecture" / "coagent_task_surface_model.md"
    review_merge = ROOT / "CoAgent" / "docs" / "architecture" / "coagent_review_merge_protocol.md"

    assert_contains(
        task_surface,
        [
            "Task Surface Classes",
            "File Surface Classes",
            "Review surface",
            "Integration Worktree",
            "Binding Rules",
            "Closeout Rules",
            "Anti-Patterns",
        ],
    )
    assert_contains(
        review_merge,
        [
            "Four Distinct Roles",
            "review_owner",
            "merge_owner",
            "close_owner",
            "Merge Outcome States",
            "Worktree Closeout Contract",
            "Anti-Patterns",
        ],
    )
    print("design_surface_docs ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
