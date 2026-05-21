import asyncio
import os

from fastmcp import FastMCP


app = FastMCP("calculator")


@app.tool
def add(first_number: float, second_number: float) -> float:
    """Add two numbers and round to two decimals."""
    return round(first_number + second_number, 2)


@app.tool
def multiply(first_number: float, second_number: float) -> float:
    """Multiply two numbers and round to four decimals."""
    return round(first_number * second_number, 4)


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio").strip().lower()
    try:
        if transport == "http":
            port = int(os.getenv("MCP_PORT", "8080"))
            app.run(show_banner=False, transport="http", port=port)
        else:
            app.run(show_banner=False, transport="stdio")
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass

# Helper MCP server — runs as a subprocess, no standalone terminal output when imported.
# Spawned by 2_1_mcp_stdio_action_deepseek.py (stdio mode) and
# 2_2_mcp_http_action_deepseek.py (HTTP mode, env MCP_TRANSPORT=http MCP_PORT=<port>).
#
# How it works:
# When MCP_TRANSPORT == "http", the server starts an HTTP MCP server on MCP_PORT.
# Otherwise it starts in stdio mode, reading JSON-RPC from stdin and writing to stdout.
# Exposes two MCP tools: add(a, b) and multiply(a, b) as calculator actions.
# The server exits after the parent process kills it or closes the stdio pipe.
