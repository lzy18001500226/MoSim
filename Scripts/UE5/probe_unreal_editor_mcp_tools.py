#!/usr/bin/env python3
"""Run a reversible live-editor round trip against the UnrealMCP socket.

The stdio MCP inventory only proves that the Python wrapper starts.  This
probe talks to the same Unreal Editor listener used by the MCP server and
verifies the editor can read actors, create an actor, modify its transform,
and delete it again without saving the map.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any


DEFAULT_PORT = 55557
BUFFER_SIZE = 8192


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


def default_host(explicit_host: str | None) -> str:
    host = explicit_host or os.environ.get("UNREAL_HOST") or wsl_default_gateway()
    if not host:
        raise RuntimeError("No Unreal host found. Set --host or UNREAL_HOST.")
    return host


def receive_json(sock: socket.socket, timeout_seconds: float) -> dict[str, Any]:
    sock.settimeout(timeout_seconds)
    chunks: list[bytes] = []
    deadline = time.monotonic() + timeout_seconds

    while True:
        if time.monotonic() > deadline:
            raise TimeoutError("Timed out waiting for complete JSON response from Unreal")
        chunk = sock.recv(BUFFER_SIZE)
        if not chunk:
            if not chunks:
                raise ConnectionError("Unreal closed the socket before returning data")
            break
        chunks.append(chunk)
        data = b"".join(chunks)
        try:
            return json.loads(data.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue

    data = b"".join(chunks)
    return json.loads(data.decode("utf-8"))


def send_command(
    host: str,
    port: int,
    command: str,
    params: dict[str, Any] | None = None,
    timeout_seconds: float = 30.0,
) -> dict[str, Any]:
    payload = json.dumps({"type": command, "params": params or {}}).encode("utf-8")
    with socket.create_connection((host, port), timeout=timeout_seconds) as sock:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.settimeout(timeout_seconds)
        sock.sendall(payload)
        response = receive_json(sock, timeout_seconds)
    if response.get("status") == "error":
        raise RuntimeError(f"{command} failed: {response.get('error') or response}")
    return response


def response_result(response: dict[str, Any]) -> dict[str, Any]:
    result = response.get("result")
    if isinstance(result, dict):
        return result
    return response


def actor_count(response: dict[str, Any]) -> int:
    result = response_result(response)
    actors = result.get("actors")
    return len(actors) if isinstance(actors, list) else 0


def find_count(host: str, port: int, pattern: str, timeout_seconds: float) -> int:
    return actor_count(send_command(host, port, "find_actors_by_name", {"pattern": pattern}, timeout_seconds))


def unique_actor_name(prefix: str) -> str:
    """Return a UE-safe probe name that avoids same-session FName reuse traps."""

    cleaned = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in prefix).strip("_")
    if not cleaned:
        cleaned = "MoSimMcpProbe"
    return f"{cleaned}_{uuid.uuid4().hex[:12]}"


def run_probe(host: str, port: int, actor_name: str, timeout_seconds: float) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "host": host,
        "port": port,
        "actor_name": actor_name,
        "steps": [],
    }

    def record(step: str, command: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = send_command(host, port, command, params, timeout_seconds)
        result = response_result(response)
        evidence["steps"].append(
            {
                "step": step,
                "command": command,
                "status": response.get("status", "unknown"),
                "actor_count": len(result.get("actors", [])) if isinstance(result.get("actors"), list) else None,
                "keys": sorted(result.keys()),
            }
        )
        return response

    cleanup_errors: list[str] = []
    try:
        before = record("read actors before probe", "get_actors_in_level")
        evidence["initial_actor_count"] = actor_count(before)

        preexisting = find_count(host, port, actor_name, timeout_seconds)
        if preexisting:
            raise RuntimeError(
                f"Probe actor name '{actor_name}' already exists. "
                "Use the default unique name or pass a fresh --actor-name."
            )

        spawn_params = {
            "name": actor_name,
            "type": "StaticMeshActor",
            "location": [120.0, -80.0, 60.0],
            "rotation": [0.0, 15.0, 0.0],
            "scale": [0.3, 0.3, 0.3],
            "static_mesh": "/Engine/BasicShapes/Cube.Cube",
        }
        spawn_response = record("spawn probe actor", "spawn_actor", spawn_params)
        spawn_result = response_result(spawn_response)
        evidence["spawned_actor"] = {
            "name": spawn_result.get("name"),
            "type": spawn_result.get("type"),
        }

        after_spawn = find_count(host, port, actor_name, timeout_seconds)
        if after_spawn != 1:
            raise RuntimeError(f"Expected one spawned probe actor, found {after_spawn}")

        set_params = {
            "name": actor_name,
            "location": [180.0, -40.0, 90.0],
            "rotation": [5.0, 30.0, 10.0],
            "scale": [0.45, 0.25, 0.2],
        }
        transform_response = record("modify probe transform", "set_actor_transform", set_params)
        transform_result = response_result(transform_response)
        evidence["modified_actor"] = {
            "name": transform_result.get("name"),
            "location": transform_result.get("location"),
            "rotation": transform_result.get("rotation"),
            "scale": transform_result.get("scale"),
        }

        record("delete probe actor", "delete_actor", {"name": actor_name})
        after_delete = find_count(host, port, actor_name, timeout_seconds)
        if after_delete:
            raise RuntimeError(f"Probe actor cleanup failed; {after_delete} matching actor(s) remain")

        after = record("read actors after cleanup", "get_actors_in_level")
        evidence["final_actor_count"] = actor_count(after)
        evidence["ok"] = True
        return evidence
    finally:
        try:
            if find_count(host, port, actor_name, timeout_seconds):
                record("final cleanup probe actor", "delete_actor", {"name": actor_name})
        except Exception as exc:  # pragma: no cover - best-effort cleanup path.
            cleanup_errors.append(str(exc))
        if cleanup_errors:
            evidence["cleanup_errors"] = cleanup_errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=None, help="Unreal Editor MCP host. Defaults to UNREAL_HOST or WSL gateway.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Unreal Editor MCP TCP port.")
    parser.add_argument("--timeout", type=float, default=30.0, help="Per-command timeout in seconds.")
    parser.add_argument(
        "--actor-name",
        default=None,
        help="Temporary actor name to create and remove. Defaults to a unique MoSimMcpProbe_DoNotSave_* name.",
    )
    parser.add_argument("--json-output", type=Path, default=None, help="Optional evidence JSON output path.")
    args = parser.parse_args()

    try:
        host = default_host(args.host)
        actor_name = args.actor_name or unique_actor_name("MoSimMcpProbe_DoNotSave")
        evidence = run_probe(host, args.port, actor_name, args.timeout)
    except Exception as exc:
        print(f"[FAIL] Unreal MCP editor round trip failed: {type(exc).__name__}: {exc}")
        return 1

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        "[OK] Unreal MCP editor round trip passed: "
        f"read {evidence.get('initial_actor_count')} actor(s), spawned/moved/deleted {evidence.get('actor_name')}"
    )
    if args.json_output:
        print(f"[OK] Evidence: {args.json_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
