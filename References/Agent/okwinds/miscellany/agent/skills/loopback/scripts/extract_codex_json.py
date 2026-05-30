#!/usr/bin/env python3
"""
Extract human-readable assistant text and the thread id from Codex CLI `--json` output.

Input: JSONL from stdin (mixed with possible non-JSON lines)
Output:
  - Writes assistant text (agent_message) to stdout
  - Writes the thread id to a file if provided

This is intentionally tolerant of unknown event shapes so it keeps working as Codex evolves.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _write_thread_id(path: str | None, thread_id: str) -> None:
    if not path:
        return
    try:
        Path(path).write_text(thread_id)
    except Exception:
        # Best-effort: never fail the pipeline due to metadata write.
        pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--thread-id-file", default=None)
    args = parser.parse_args()

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except Exception:
            continue

        event_type = event.get("type")
        if event_type == "thread.started":
            thread_id = event.get("thread_id")
            if isinstance(thread_id, str) and thread_id:
                _write_thread_id(args.thread_id_file, thread_id)
            continue

        # Most important: completed agent messages.
        if event_type == "item.completed":
            item = event.get("item") or {}
            if isinstance(item, dict) and item.get("type") == "agent_message":
                text = item.get("text")
                if isinstance(text, str) and text:
                    sys.stdout.write(text)
                    if not text.endswith("\n"):
                        sys.stdout.write("\n")
                    sys.stdout.flush()
            continue

        # Fallback: some builds may use slightly different shapes.
        text = event.get("text")
        if isinstance(text, str) and text:
            sys.stdout.write(text)
            if not text.endswith("\n"):
                sys.stdout.write("\n")
            sys.stdout.flush()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

