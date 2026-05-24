"""
Helper MCP server for 10-actions-03_mcp.py.
Exposes two unit-conversion tools via the Model Context Protocol.
Run directly to verify: python _10_mcp_server.py   (stdio mode, exits after one session)
"""
import asyncio
import os

from fastmcp import FastMCP

app = FastMCP("unit-converter")


@app.tool
def km_to_miles(km: float) -> float:
    """Convert a distance in kilometres to miles, rounded to 4 decimal places."""
    return round(km * 0.621371, 4)


@app.tool
def kg_to_lb(kg: float) -> float:
    """Convert a weight in kilograms to pounds, rounded to 4 decimal places."""
    return round(kg * 2.20462, 4)


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

# Helper MCP server — spawned as a subprocess by 10-actions-03_mcp.py (stdio mode).
# Exposes two tools: km_to_miles(km) and kg_to_lb(kg).
# Agently manages the subprocess lifecycle; it is killed after the request completes.
