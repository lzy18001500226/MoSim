#!/usr/bin/env python3
"""Smoke tests for CoAgent knowledge search."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.knowledge import knowledge_indexer


def main() -> int:
    knowledge_indexer.build_index()
    result = knowledge_indexer.search_index("worker policy stale lock concurrency", limit=10)
    assert result["count"] > 0, result
    assert any("CoAgent/automation" in hit["path"] for hit in result["hits"]), result
    assert any(hit["matched_terms"] for hit in result["hits"]), result
    print("knowledge_search_smoke ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
