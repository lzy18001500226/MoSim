"""Structured log events emitted by the websurfer system.

The :class:`webeval.utils.LogHandler` checks ``isinstance(record.msg, …)``
against these dataclasses to format ``web_surfer.log`` entries. Three are
in use:

* :class:`OrchestrationEvent` — orchestrator-side bookkeeping.
* :class:`AgentEvent` — generic agent lifecycle messages.
* :class:`WebSurferEvent` — per-action trace from the FaraAgent loop
  (also recognised by ``post_eval_analysis.py`` when counting actions).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class OrchestrationEvent:
    source: str
    message: str


@dataclass
class AgentEvent:
    source: str
    message: str


@dataclass
class WebSurferEvent:
    source: str
    message: str
    url: str
    action: str | None = None
    arguments: Dict[str, Any] | None = None
