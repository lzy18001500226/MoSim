#!/usr/bin/env python3
"""Probe whether the Unreal Editor-side MCP TCP listener is reachable.

This checks only the editor plugin socket, not the stdio MCP wrapper. It is
useful when `/mcp` lists `unreal_engine` tools but actor/Blueprint operations
timeout because the Unreal Editor plugin is not listening on the expected host
and port.
"""

from __future__ import annotations

import argparse
import json
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


def wrapper_route_host(explicit_host: str | None) -> str | None:
    """Return the exact route the WSL MCP wrapper will use by default."""

    return explicit_host or os.environ.get("UNREAL_HOST") or wsl_default_gateway()


def windows_unreal_processes() -> tuple[list[dict[str, object]], str]:
    """Return project-owned UnrealEditor processes visible from WSL."""

    command = [
        "powershell.exe",
        "-NoProfile",
        "-Command",
        (
            "$ErrorActionPreference='SilentlyContinue';"
            "$items = Get-CimInstance Win32_Process -Filter \"name = 'UnrealEditor.exe'\" | "
            "Where-Object { $_.CommandLine -like '*MoSimSceneLibrary.uproject*' } | "
            "Select-Object ProcessId,CommandLine;"
            "if ($items) { $items | ConvertTo-Json -Compress }"
        ),
    ]
    try:
        result = subprocess.run(command, text=True, capture_output=True, check=False, timeout=5.0)
    except (OSError, subprocess.SubprocessError) as exc:
        return [], f"{type(exc).__name__}: {exc}"
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        return [], detail or f"powershell exited {result.returncode}"
    text = result.stdout.strip()
    if not text:
        return [], ""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        return [], f"JSONDecodeError: {exc}: {text[:200]}"
    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        return [], f"unexpected PowerShell JSON payload: {type(payload).__name__}"
    return [item for item in payload if isinstance(item, dict)], ""


def process_mode(command_line: str) -> str:
    lowered = command_line.lower()
    if " -game" in lowered:
        return "standalone-game"
    if "mworksunrealrenderer.uproject" in lowered:
        return "editor-or-launcher"
    return "unknown"


def print_process_diagnostics() -> None:
    processes, error = windows_unreal_processes()
    if error:
        print(f"[INFO] Unable to query Windows UnrealEditor processes: {error}")
        return
    if not processes:
        print("[INFO] No project-owned UnrealEditor.exe process found for MoSimSceneLibrary.uproject.")
        return

    print("[INFO] Project-owned UnrealEditor.exe processes:")
    for item in processes:
        pid = item.get("ProcessId", "<unknown>")
        command_line = str(item.get("CommandLine", ""))
        mode = process_mode(command_line)
        preview = command_line.replace("\r", " ").replace("\n", " ")
        if len(preview) > 220:
            preview = preview[:217] + "..."
        print(f"[INFO]   pid={pid} mode={mode} cmd={preview}")
    if all(process_mode(str(item.get("CommandLine", ""))) == "standalone-game" for item in processes):
        print("[INFO] Only standalone -game process(es) were found; those do not expose the editor MCP listener.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host",
        default=None,
        help="Specific host to test. Defaults to UNREAL_HOST, WSL gateway, then 127.0.0.1.",
    )
    parser.add_argument("--port", type=int, default=55557, help="Unreal Editor plugin TCP port")
    parser.add_argument("--timeout", type=float, default=2.0, help="Connection timeout in seconds")
    parser.add_argument(
        "--wrapper-route-only",
        action="store_true",
        help="Probe only the host that Scripts/UE5/unreal_mcp_wsl_wrapper.sh will use.",
    )
    parser.add_argument(
        "--no-process-diagnostics",
        action="store_true",
        help="Do not query Windows UnrealEditor processes when the listener is unreachable.",
    )
    args = parser.parse_args()

    if args.wrapper_route_only:
        wrapper_host = wrapper_route_host(args.host)
        hosts = [wrapper_host] if wrapper_host else []
    else:
        hosts = default_hosts(args.host)

    if not hosts:
        print("[FAIL] No Unreal MCP host candidate found. Set UNREAL_HOST or ensure WSL has a default gateway.")
        return 1

    if args.wrapper_route_only:
        print(f"[INFO] Wrapper route target: {hosts[0]}:{args.port}")

    results = [probe(host, args.port, args.timeout) for host in hosts]
    for result in results:
        if result.ok:
            print(f"[OK] Unreal Editor MCP listener reachable at {result.host}:{result.port}")
            return 0

    print(f"[FAIL] Unreal Editor MCP listener not reachable on any tested host for port {args.port}")
    for result in results:
        print(f"[FAIL] {result.host}:{result.port} -> {result.error}")
    if not args.no_process_diagnostics:
        print_process_diagnostics()
    print("[INFO] `/mcp` tool inventory can still work when this probe fails.")
    print("[INFO] Open the UE project with the UnrealMCP plugin enabled, or run the MCP server where it can reach the editor listener.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
