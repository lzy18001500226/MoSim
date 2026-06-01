"""Internal shim for grok-search context module.

This module re-exports the canonical context implementation from tools.grok_search.
"""

from __future__ import annotations

from pathlib import Path
import sys

root = Path(__file__).resolve().parents[3]
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
