#!/usr/bin/env python3
"""Probe whether the Unreal Editor-side MCP TCP listener is reachable.

This checks only the editor plugin socket, not the stdio MCP wrapper. It is
useful when `/mcp` lists `unreal_engine` tools but actor/Blueprint operations
timeout because the Unreal Editor plugin is not listening on the expected host
and port.
"""

from __future__ import annotations

import argparse
import socket
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class ProbeResult:
    host: str
    port: int
    ok: bool
    error: str = ""


def probe(host: str, port: int, timeout_seconds: float) -> ProbeResult:
    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return ProbeResult(host=host, port=port, ok=True)
    except OSError as exc:
        return ProbeResult(host=host, port=port, ok=False, error=f"{type(exc).__name__}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Host used by the Unreal MCP Python server")
    parser.add_argument("--port", type=int, default=55557, help="Unreal Editor plugin TCP port")
    parser.add_argument("--timeout", type=float, default=2.0, help="Connection timeout in seconds")
    args = parser.parse_args()

    result = probe(args.host, args.port, args.timeout)
    if result.ok:
        print(f"[OK] Unreal Editor MCP listener reachable at {result.host}:{result.port}")
        return 0

    print(f"[FAIL] Unreal Editor MCP listener not reachable at {result.host}:{result.port}")
    print(f"[FAIL] {result.error}")
    print("[INFO] `/mcp` tool inventory can still work when this probe fails.")
    print("[INFO] Open the UE project with the UnrealMCP plugin enabled, or run the MCP server where it can reach the editor listener.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
