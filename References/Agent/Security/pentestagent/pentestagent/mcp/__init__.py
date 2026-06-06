"""MCP (Model Context Protocol) integration for PentestAgent."""

from .manager import (
    MCPManager,
    MCPServer,
    MCPServerConfig,
    SSEServerConfig,
    StdioServerConfig,
)
from .tools import create_mcp_tool
from .transport import MCPTransport, SSETransport, StdioTransport

__all__ = [
    "MCPManager",
    "MCPServerConfig",
    "StdioServerConfig",
    "SSEServerConfig",
    "MCPServer",
    "MCPTransport",
    "StdioTransport",
    "SSETransport",
    "create_mcp_tool",
]
