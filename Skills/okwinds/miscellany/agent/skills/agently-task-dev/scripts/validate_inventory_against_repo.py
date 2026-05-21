#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_SYMBOLS: list[str] = [
    # Core entrypoints / configuration
    "AgentlyMain",
    "create_agent",
    "create_request",
    "set_settings",
    "OpenAICompatible",
    # Prompt & output control
    "load_yaml_prompt",
    "load_json_prompt",
    "get_yaml_prompt",
    "get_json_prompt",
    "ensure_keys",
    # Streaming
    "get_generator",
    "get_async_generator",
    "streaming_parse",
    "instant",
    "specific",
    # Tools & MCP
    "ToolExtension",
    "tool_func",
    "use_tools",
    "Search",
    "Browse",
    "use_mcp",
    "async_use_mcp",
    # Orchestration
    "TriggerFlow",
    "TriggerFlowEventData",
    "get_runtime_stream",
    "put_into_stream",
    "stop_stream",
    # KB / RAG
    "ChromaCollection",
    # Optional extensions
    "AutoFuncExtension",
    "auto_func",
    "KeyWaiterExtension",
    "when_key",
    "start_waiter",
    "ChatSessionExtension",
    "activate_chat_session",
    # Multimodal
    "attachment",
    "rich_content",
]


def _iter_py_files(root: Path) -> list[Path]:
    return [
        p
        for p in root.rglob("*.py")
        if "__pycache__" not in p.parts and p.is_file()
    ]


def _file_contains(path: Path, token: str) -> bool:
    try:
        return token in path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False


def _repo_contains_any(repo_root: Path, token: str) -> bool:
    agently_root = repo_root / "agently"
    if not agently_root.exists():
        return False
    for p in _iter_py_files(agently_root):
        if _file_contains(p, token):
            return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate that capability-inventory.md keeps up with the upstream Agently repo features.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[4],
        help="Path to the Agently repository root (default: ../../../../ from this script).",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "references" / "capability-inventory.md",
        help="Path to capability inventory markdown.",
    )
    args = parser.parse_args()

    repo_root: Path = args.repo_root
    inventory_path: Path = args.inventory

    if not inventory_path.exists():
        print(f"[FAIL] inventory file not found: {inventory_path}", file=sys.stderr)
        return 2

    inventory_text = inventory_path.read_text(encoding="utf-8", errors="ignore")

    missing: list[str] = []
    skipped: list[str] = []

    for token in REPO_SYMBOLS:
        if not _repo_contains_any(repo_root, token):
            skipped.append(token)
            continue
        if token not in inventory_text:
            missing.append(token)

    if missing:
        print("[FAIL] capability-inventory.md is missing repo symbols:", file=sys.stderr)
        for token in missing:
            print(f"- {token}", file=sys.stderr)
        print("\nHint: add the missing capability rows into references/capability-inventory.md", file=sys.stderr)
        return 1

    print("[OK] capability-inventory.md covers all detected repo symbols.")
    if skipped:
        print(f"[INFO] skipped {len(skipped)} tokens not found in repo (probably renamed/removed).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

