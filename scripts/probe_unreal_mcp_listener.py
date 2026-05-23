#!/usr/bin/env python3
"""Probe whether the Unreal Editor-side MCP TCP listener is reachable.

This checks only the editor plugin socket, not the stdio MCP wrapper. It is
useful when `/mcp` lists `unreal_engine` tools but actor/Blueprint operations
timeout because the Unreal Editor plugin is not listening on the expected host
and port.
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
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


def wsl_default_gateway() -> str | None:
    try:
        result = subprocess.run(
            ["ip", "route"],
            text=True,
            capture_output=True,
            check=False,
            timeout=2.0,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[0] == "default" and parts[1] == "via":
            return parts[2]
    return None


def default_hosts(explicit_host: str | None) -> list[str]:
    hosts: list[str] = []
    for candidate in [explicit_host, os.environ.get("UNREAL_HOST"), wsl_default_gateway(), "127.0.0.1"]:
        if candidate and candidate not in hosts:
            hosts.append(candidate)
    return hosts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host",
        default=None,
        help="Specific host to test. Defaults to UNREAL_HOST, WSL gateway, then 127.0.0.1.",
    )
    parser.add_argument("--port", type=int, default=55557, help="Unreal Editor plugin TCP port")
    parser.add_argument("--timeout", type=float, default=2.0, help="Connection timeout in seconds")
    args = parser.parse_args()

    results = [probe(host, args.port, args.timeout) for host in default_hosts(args.host)]
    for result in results:
        if result.ok:
            print(f"[OK] Unreal Editor MCP listener reachable at {result.host}:{result.port}")
            return 0

    print(f"[FAIL] Unreal Editor MCP listener not reachable on any tested host for port {args.port}")
    for result in results:
        print(f"[FAIL] {result.host}:{result.port} -> {result.error}")
    print("[INFO] `/mcp` tool inventory can still work when this probe fails.")
    print("[INFO] Open the UE project with the UnrealMCP plugin enabled, or run the MCP server where it can reach the editor listener.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
