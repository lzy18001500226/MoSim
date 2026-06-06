# mcp_core.py — Tool registry & request router (transport-agnostic)
from dataclasses import dataclass
from typing import Awaitable, Callable

# ─── Types ────────────────────────────────────────────────────────────────────

Handler = Callable[[dict], Awaitable[str]]


@dataclass
class Tool:
    name: str
    description: str
    schema: dict  # JSON Schema for the input arguments
    handler: Handler


# ─── Registry ─────────────────────────────────────────────────────────────────


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, schema: dict):
        """
        Decorator — annotate an async function to expose it as an MCP tool.

        Usage:
            @registry.register(
                name="port_scan",
                description="Scan open TCP ports on a target host.",
                schema={
                    "type": "object",
                    "properties": {
                        "target": {"type": "string"},
                        "ports":  {"type": "string"},
                    },
                    "required": ["target"],
                },
            )
            async def port_scan(args: dict) -> str:
                ...
        """

        def decorator(fn: Handler) -> Handler:
            self._tools[name] = Tool(
                name=name, description=description, schema=schema, handler=fn
            )
            return fn

        return decorator

    def to_list(self) -> list[dict]:
        """Serialise all tools to the MCP wire format."""
        return [
            {"name": t.name, "description": t.description, "inputSchema": t.schema}
            for t in self._tools.values()
        ]

    async def call(self, name: str, args: dict) -> dict:
        """Execute a tool and return a JSON-RPC-ready result block."""
        tool = self._tools.get(name)
        if tool is None:
            return {"error": {"code": -32601, "message": f"Unknown tool: {name}"}}
        try:
            text = await tool.handler(args)
            return {"result": {"content": [{"type": "text", "text": text}]}}
        except Exception as e:
            return {"error": {"code": -32000, "message": str(e)}}


# ─── Shared Request Router ────────────────────────────────────────────────────


class MCPRouter:
    """
    Stateless JSON-RPC router.
    Both transports hand every incoming message to `handle()` and send
    whatever it returns (None = notification, no reply needed).
    """

    SERVER_NAME = "pentest-mcp"
    SERVER_VERSION = "1.0.0"

    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    async def handle(self, req: dict) -> dict | None:
        method = req.get("method")
        id_ = req.get("id")

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": id_,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": self.SERVER_NAME,
                        "version": self.SERVER_VERSION,
                    },
                    "capabilities": {"tools": {}},
                },
            }

        if method == "notifications/initialized":
            return None  # fire-and-forget, no reply

        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": id_,
                "result": {"tools": self.registry.to_list()},
            }

        if method == "tools/call":
            name = req["params"]["name"]
            args = req["params"].get("arguments", {})
            body = await self.registry.call(name, args)
            return {"jsonrpc": "2.0", "id": id_, **body}

        return {
            "jsonrpc": "2.0",
            "id": id_,
            "error": {"code": -32601, "message": f"Method not found: {method}"},
        }
