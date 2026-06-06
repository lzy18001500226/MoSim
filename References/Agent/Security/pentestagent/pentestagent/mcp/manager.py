"""MCP server connection manager for PentestAgent.

Uses standard MCP configuration format:
{
    "mcpServers": {
        "server-name": {
            "command": "npx",
            "args": ["-y", "package-name"],
            "env": {"VAR": "value"}
        }
    }
}
"""

import asyncio
import json
import os
from abc import ABC
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..tools import Tool
from .transport import FifoTransport, MCPTransport, SSETransport, StdioTransport


@dataclass
class MCPServerConfig(ABC):
    """Base configuration for an MCP server."""

    type: str = field(init=False)
    name: str
    enabled: bool = True
    description: str = ""


@dataclass
class StdioServerConfig(MCPServerConfig):
    """Configuration for a stdio-based MCP server."""

    command: str = ""
    args: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.type = "stdio"


@dataclass
class FifoServerConfig(MCPServerConfig):
    """Configuration for a FIFO-based MCP server (TUI child in a new terminal)."""

    fifo_in: str = ""  # parent writes, child reads (MCP requests)
    fifo_out: str = ""  # child writes, parent reads (MCP responses)

    def __post_init__(self):
        self.type = "fifo"


@dataclass
class SSEServerConfig(MCPServerConfig):
    """Configuration for an SSE-based MCP server."""

    url: str = ""
    bearer: str = ""

    def __post_init__(self):
        self.type = "sse"

    def set_bearer(self, bearer: str) -> None:
        self.bearer = bearer


"""Configuration for an MCP server."""


@dataclass
class MCPServer:
    """Represents a connected MCP server."""

    name: str
    config: MCPServerConfig
    transport: Optional[MCPTransport]
    tools: List[dict] = field(default_factory=list)
    connected: bool = False
    # Lock for serializing all communication with this server
    # Prevents message ID collisions and transport interleaving
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    last_error: str = ""  # If something went wrong, get the last error message.

    async def disconnect(self):
        """Disconnect from the server."""
        if self.connected:
            if self.transport:
                await self.transport.disconnect()
            self.connected = False

    def is_enabled(self) -> bool:
        return self.config.enabled

    def enable(self):
        self.config.enabled = True

    def disable(self):
        self.config.enabled = False

    def get_logs(self) -> str:
        if not self.transport:
            return ""
        return self.transport.get_logs()

    def get_notification_queue(self) -> Optional[asyncio.Queue]:
        """Return the push-notification queue if the transport supports it.

        Only FifoTransport (child agents spawned via spawn_mcp_agent) exposes
        this queue.  Other transports return None.
        """
        from .transport import FifoTransport

        if isinstance(self.transport, FifoTransport):
            return self.transport.notification_queue
        return None


class MCPManager:
    """Manages MCP server connections and exposes tools to agents."""

    DEFAULT_CONFIG_PATHS = [
        Path.cwd() / "mcp_servers.json",
        Path.cwd() / "mcp.json",
        Path(__file__).parent / "mcp_servers.json",
        Path.home() / ".pentestagent" / "mcp_servers.json",
    ]

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or self._find_config()
        self.servers: Dict[str, MCPServer] = {}
        self._message_id = 0

    def _find_config(self) -> Path:
        for path in self.DEFAULT_CONFIG_PATHS:
            if path.exists():
                return path
        return self.DEFAULT_CONFIG_PATHS[0]

    def _get_next_id(self) -> int:
        self._message_id += 1
        return self._message_id

    def _load_config(self) -> Dict[str, MCPServerConfig]:
        if not self.config_path.exists():
            return {}
        try:
            raw = json.loads(self.config_path.read_text(encoding="utf-8"))
            servers = {}
            mcp_servers = raw.get("mcpServers", {})

            for name, config in mcp_servers.items():

                if config.get("type") and config["type"] == "sse":
                    if not config.get("url"):
                        continue  # Improper configuration

                    servers[name] = SSEServerConfig(
                        name=name,
                        url=config.get("url", ""),
                        enabled=config.get("enabled", True),
                        description=config.get("description", ""),
                    )

                    if config.get("bearer"):
                        servers[name].set_bearer(config["bearer"])

                else:

                    if not config.get("command"):
                        continue

                    servers[name] = StdioServerConfig(
                        name=name,
                        command=config.get("command", ""),
                        args=config.get("args", []),
                        env=config.get("env", {}),
                        enabled=config.get("enabled", True),
                        description=config.get("description", ""),
                    )

            return servers

        except json.JSONDecodeError as e:
            print(f"[MCP] Error loading config: {e}")
            return {}

    def _save_config(self, servers: Dict[str, MCPServerConfig]):
        config = {"mcpServers": {}}
        for name, server in servers.items():

            server_config: dict[str, Any] = {"type": server.type}
            if server.description:
                server_config["description"] = server.description
            if not server.enabled:
                server_config["enabled"] = False

            if isinstance(server, SSEServerConfig):
                server_config["url"] = server.url
                if server.bearer:
                    server_config["bearer"] = server.bearer

            elif isinstance(server, StdioServerConfig):
                server_config["command"] = server.command
                server_config["args"] = server.args
                if server.env:
                    server_config["env"] = server.env

            config["mcpServers"][name] = server_config
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

    def add_stdio_server(
        self,
        name: str,
        command: str,
        args: List[str] = None,
        env: Dict[str, str] = None,
        description: str = "",
    ):
        servers = self._load_config()
        servers[name] = StdioServerConfig(
            name=name,
            command=command or "",
            args=args or [],
            env=env or {},
            description=description,
        )
        self._save_config(servers)
        print(f"[MCP] Added server: {name}, stdio type")

    def add_sse_server(
        self,
        name: str,
        url: str,
        description: str = "",
    ):
        servers = self._load_config()
        servers[name] = SSEServerConfig(
            name=name,
            url=url or "",
            description=description,
        )
        self._save_config(servers)
        print(f"[MCP] Added server: {name}, sse type")

    def remove_server(self, name: str) -> bool:
        servers = self._load_config()
        if name in servers:
            del servers[name]
            self._save_config(servers)
            return True
        return False

    def list_configured_servers(self) -> List[dict]:
        servers = self._load_config()
        return [
            {
                "name": n,
                "type": s.type,
                "command": getattr(s, "command", None),
                "url": getattr(s, "url", None),
                "args": getattr(s, "args", None),
                "env": getattr(s, "env", None),
                "enabled": s.enabled,
                "description": s.description,
                "connected": n in self.servers and self.servers[n].connected,
            }
            for n, s in servers.items()
        ]

    def create_mcp_tools_from_server(
        self,
        server: MCPServer,
        embedding_model: str = "text-embedding-3-small",
        rag_top_k: int = 20,
    ) -> List["Tool"]:
        from .mcp_rag_optimizer import _TOOL_LIMIT, create_mcp_rag_optimizer
        from .tools import create_mcp_tool

        all_tools = [
            create_mcp_tool(tool_def, server, self) for tool_def in server.tools
        ]

        if len(all_tools) <= _TOOL_LIMIT:
            return all_tools  # under the limit — expose everything directly

        rag_tool = create_mcp_rag_optimizer(
            all_tools,
            server,
            embedding_model=embedding_model,
            top_k=rag_top_k,
        )
        return [rag_tool]

    async def connect_all(self) -> List["Tool"]:
        servers_config = self._load_config()
        all_tools = []
        for name, config in servers_config.items():
            if not config.enabled:
                continue
            server = await self._connect_server(config)
            if server:
                self.servers[name] = server
                tools = self.create_mcp_tools_from_server(server)
                all_tools.extend(tools)
                print(f"[MCP] Connected to {name} with {len(server.tools)} tools")
        return all_tools

    async def connect_server(self, name: str) -> Optional[MCPServer]:
        servers_config = self._load_config()
        if name not in servers_config:
            return None
        config = servers_config[name]
        server = await self._connect_server(config)
        if server:
            self.servers[name] = server
        return server

    async def _connect_server(self, config: MCPServerConfig) -> Optional[MCPServer]:
        transport = None
        try:

            if isinstance(config, SSEServerConfig):
                transport = SSETransport(url=config.url, bearer=config.bearer)
            elif isinstance(config, FifoServerConfig):
                transport = FifoTransport(
                    fifo_in=config.fifo_in, fifo_out=config.fifo_out
                )
            elif isinstance(config, StdioServerConfig):
                env = {**os.environ, **config.env}
                transport = StdioTransport(
                    command=config.command, args=config.args, env=env
                )

            if transport is None:
                raise RuntimeError("Failed to create transport")

            await transport.connect()

            await transport.send(
                {
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-11-25",
                        "capabilities": {},
                        "clientInfo": {"name": "pentestagent", "version": "0.2.0"},
                    },
                    "id": self._get_next_id(),
                }
            )
            await transport.send(
                {"jsonrpc": "2.0", "method": "notifications/initialized"}
            )

            tools_response = await transport.send(
                {"jsonrpc": "2.0", "method": "tools/list", "id": self._get_next_id()}
            )
            tools = tools_response.get("result", {}).get("tools", [])

            return MCPServer(
                name=config.name,
                config=config,
                transport=transport,
                tools=tools,
                connected=True,
            )
        except Exception as e:
            # Clean up transport on failure
            if transport:
                try:
                    await transport.disconnect()
                except Exception:
                    pass
            print(f"[MCP] Failed to connect to {config.name}: {e}")
            return MCPServer(
                name=config.name,
                config=config,
                transport=None,
                tools=[],
                connected=False,
                last_error=str(e),
            )

    async def call_tool(self, server_name: str, tool_name: str, arguments: dict) -> Any:
        server = self.servers.get(server_name)
        if not server or not server.connected:
            raise ValueError(f"Server '{server_name}' not connected")

        # Serialize all communication with this server to prevent:
        # - Message ID collisions
        # - Transport write interleaving
        # - Response routing issues
        async with server._lock:
            # Use 5 minute timeout for tool calls (scans can take a while)
            response = await server.transport.send(
                {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {"name": tool_name, "arguments": arguments},
                    "id": self._get_next_id(),
                },
                timeout=300.0,
            )
        if "error" in response:
            raise RuntimeError(f"MCP error: {response['error'].get('message')}")
        return response.get("result", {}).get("content", [])

    async def disconnect_server(self, name: str):
        server = self.servers.get(name)
        if server:
            await server.disconnect()
            del self.servers[name]

    async def disconnect_all(self):
        for server in list(self.servers.values()):
            await server.disconnect()
        self.servers.clear()

    async def reconnect_all(self) -> List[Any]:
        """Disconnect all servers and reconnect them.

        Useful after cancellation leaves servers in a bad state.
        """
        # Disconnect all
        await self.disconnect_all()

        # Reconnect all configured servers
        return await self.connect_all()

    def get_server(self, name: str) -> Optional[MCPServer]:
        return self.servers.get(name)

    def get_all_servers(self) -> List[MCPServer]:
        return list(self.servers.values())

    def is_connected(self, name: str) -> bool:
        server = self.servers.get(name)
        return server is not None and server.connected

    async def enable(self, name: str):
        server = self.servers.get(name)
        if not server:
            return
        server.enable()
        server = await self._connect_server(server.config)
        if server:  # Do a shadow copy.
            self.servers[name].name = server.name
            self.servers[name].config = server.config
            self.servers[name].connected = server.connected
            self.servers[name].last_error = server.last_error
            self.servers[name].tools = server.tools
            self.servers[name].transport = server.transport

    async def disable(self, name: str):
        server = self.servers.get(name)
        if not server:
            return
        await server.disconnect()
        server.disable()
