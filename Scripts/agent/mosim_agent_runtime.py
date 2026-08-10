#!/usr/bin/env python3
"""Retired compatibility entrypoint for the old durable agent runtime."""

from __future__ import annotations


def main() -> int:
    print(
        "The old durable agent runtime is retired for current task-local "
        "MoSim work. Use the current project workflows under Docs/Workflows/."
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
