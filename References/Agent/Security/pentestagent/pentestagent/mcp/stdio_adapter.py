#!/usr/bin/env python3
"""Generic stdio JSON-RPC adapter bridge to an HTTP API.

Configure via environment variables:
- `STDIO_TARGET` (default: "http://127.0.0.1:8888")
- `STDIO_TOOLS` (JSON list of tool descriptors, default: `[{"name":"http_api","description":"Generic HTTP proxy"}]`)

The adapter implements the minimal MCP/stdio surface required by
`pentestagent`'s `StdioTransport`:
- handle `initialize` and `notifications/initialized`
- respond to `tools/list`
- handle `tools/call` and forward to HTTP endpoints

`tools/call` arguments format (generic):
  {"path": "/api/foo", "method": "POST", "params": {...}, "body": {...} }

This file is intentionally small and dependency-light; it uses `requests`
when available and returns response JSON or text.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List

try:
    import requests
except Exception:
    requests = None


TARGET = os.environ.get("STDIO_TARGET", "http://127.0.0.1:8888").rstrip("/")
_tools_env = os.environ.get("STDIO_TOOLS")


def _default_tools() -> List[Dict[str, str]]:
    return [{"name": "http_api", "description": "Generic HTTP proxy"}]


def _discover_tools_from_target(target: str) -> List[Dict[str, str]]:
    """Attempt to discover tools from the HTTP API at <target>/api/tools.

    The HexStrike server exposes blueprints under `/api/tools` and many
    installations provide an index at `/api/tools` returning a JSON list.
    If discovery fails, return the default tool list.
    """
    if requests is None:
        return _default_tools()
    try:
        url = target.rstrip("/") + "/api/tools"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return _default_tools()
        data = r.json()
        # Expecting either a list of tools or an object with `tools` key
        tools = []
        if (
            isinstance(data, dict)
            and "tools" in data
            and isinstance(data["tools"], list)
        ):
            src = data["tools"]
        elif isinstance(data, list):
            src = data
        else:
            return _default_tools()

        for t in src:
            # t may be a string or object with name/description
            if isinstance(t, str):
                tools.append({"name": t, "description": "Remote tool"})
            elif isinstance(t, dict):
                name = t.get("name") or t.get("id") or t.get("tool")
                desc = t.get("description") or t.get("desc") or "Remote tool"
                if name:
                    tools.append({"name": name, "description": desc})
        if tools:
            return tools
    except Exception:
        pass
    return _default_tools()


if _tools_env:
    try:
        TOOLS: List[Dict[str, str]] = json.loads(_tools_env)
    except Exception:
        TOOLS = _default_tools()
else:
    TOOLS = _discover_tools_from_target(TARGET)


def _send(resp: Dict[str, Any]) -> None:
    print(json.dumps(resp, separators=(",", ":")), flush=True)


def send_response(req_id: Any, result: Any = None, error: Any = None) -> None:
    resp: Dict[str, Any] = {"jsonrpc": "2.0", "id": req_id}
    if error is not None:
        resp["error"] = {"code": -32000, "message": str(error)}
    else:
        resp["result"] = result if result is not None else {}
    _send(resp)


def handle_tools_list(req_id: Any) -> None:
    send_response(req_id, {"tools": TOOLS})


def _http_forward(
    path: str,
    method: str = "POST",
    params: Dict[str, Any] | None = None,
    body: Any | None = None,
) -> Any:
    if requests is None:
        raise RuntimeError("`requests` not installed in adapter process")
    url = (
        path
        if path.startswith("http")
        else TARGET + (path if path.startswith("/") else "/" + path)
    )
    method = (method or "POST").upper()
    if method == "GET":
        r = requests.get(url, params=params or {}, timeout=60)
    else:
        r = requests.request(
            method, url, json=body or {}, params=params or {}, timeout=300
        )
    try:
        return r.json()
    except Exception:
        return r.text


def handle_tools_call(req: Dict[str, Any]) -> None:
    req_id = req.get("id")
    params = req.get("params", {}) or {}
    name = params.get("name")
    arguments = params.get("arguments") or {}

    # Validate tool
    if not any(t.get("name") == name for t in TOOLS):
        send_response(req_id, error=f"unknown tool '{name}'")
        return

    path = arguments.get("path")
    if not path:
        send_response(req_id, error="missing 'path' in arguments")
        return

    method = arguments.get("method", "POST")
    body = arguments.get("body")
    qparams = arguments.get("params")

    try:
        content = _http_forward(path, method=method, params=qparams, body=body)
        send_response(req_id, {"content": content})
    except Exception as e:
        send_response(req_id, error=str(e))


def main() -> None:
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue

        method = req.get("method")
        req_id = req.get("id")

        if method == "initialize":
            send_response(req_id, {"capabilities": {}})
        elif method == "notifications/initialized":
            # ignore notification
            continue
        elif method == "tools/list":
            handle_tools_list(req_id)
        elif method == "tools/call":
            handle_tools_call(req)
        else:
            if req_id is not None:
                send_response(req_id, error=f"unsupported method '{method}'")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
