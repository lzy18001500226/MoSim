"""Minimal MCP adapter scaffold for PentestAgent.

This module provides a small example adapter and a base interface that
adapter implementers can follow. Adapters are expected to provide a
lightweight set of methods so the `MCPManager` or external tools can
manage adapter lifecycle and issue tool calls. This scaffold intentionally
does not auto-start external processes; it's a development aid only.

Implemented surface (example):
 - `BaseAdapter` (abstract interface)
 - `ExampleAdapter` (in-process mock adapter for testing)

Usage:
 - Use `ExampleAdapter` as a working reference when implementing real
   adapters under `third_party/` or when wiring an adapter into
   `mcp_servers.json`.
"""

from __future__ import annotations

from typing import Any, Dict, List


class BaseAdapter:
    """Minimal adapter interface.

    Implementers should provide at least these methods. Real adapters may
    expose additional methods such as `stop_sync` or an underlying
    `_process` attribute that the manager may inspect when cleaning up.
    """

    name: str = "base"

    async def start(self) -> None:  # pragma: no cover - interface
        raise NotImplementedError()

    async def stop(self) -> None:  # pragma: no cover - interface
        raise NotImplementedError()

    def stop_sync(self) -> None:  # pragma: no cover - optional
        raise NotImplementedError()

    async def list_tools(self) -> List[Dict[str, Any]]:  # pragma: no cover - interface
        raise NotImplementedError()

    async def call_tool(
        self, name: str, arguments: Dict[str, Any]
    ) -> Any:  # pragma: no cover - interface
        raise NotImplementedError()


class ExampleAdapter(BaseAdapter):
    """A trivial in-process adapter useful for tests and development.

    - `list_tools()` returns a single example tool definition.
    - `call_tool()` returns a simple echo response.
    """

    name = "example"

    def __init__(self):
        self._running = False

    async def start(self) -> None:
        self._running = True

    async def stop(self) -> None:
        self._running = False

    def stop_sync(self) -> None:
        # Synchronous stop helper for manager cleanup code paths
        self._running = False

    async def list_tools(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "ping",
                "description": "Return a ping response",
                "inputSchema": {"type": "object", "properties": {}},
            }
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        if name == "ping":
            return [{"type": "text", "text": "pong"}]
        raise ValueError(f"Unknown tool: {name}")
