"""Deprecated shim: context module is now internal to grok-search.

Do not use directly. This module re-exports internal grok-search context classes
for backward compatibility.
"""

from __future__ import annotations

from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2]
sys.path.append(str(root))

from tools.grok_search.context import (  # type: ignore
    ContextConfig,
    ContextRouter,
    ContextSnapshot,
    ContextStore,
    RouteDecision,
    DEFAULT_CONTINUATION_PATTERNS,
    estimate_tokens,
)

__all__ = [
    "ContextConfig",
    "ContextRouter",
    "ContextSnapshot",
    "ContextStore",
    "RouteDecision",
    "DEFAULT_CONTINUATION_PATTERNS",
    "estimate_tokens",
]
