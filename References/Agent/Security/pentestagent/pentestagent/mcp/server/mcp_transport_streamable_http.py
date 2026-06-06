# mcp_transport_streamable_http.py — Streamable HTTP transport (spec 2025-03-26 / 2025-11-25)


import asyncio
import json
import uuid

from aiohttp import web

from .mcp_core import MCPRouter

# ── helpers ───────────────────────────────────────────────────────────────────


def _is_notification(msg: dict) -> bool:
    """JSON-RPC notifications have no 'id' field."""
    return "id" not in msg


def _session_id() -> str:
    return str(uuid.uuid4())


# ── transport ─────────────────────────────────────────────────────────────────


def create_streamable_http_app(router: MCPRouter) -> web.Application:
    """
    Build and return the aiohttp app.
    Call  web.run_app(create_streamable_http_app(router))  to start.

    Single endpoint: /mcp
      POST   — client sends JSON-RPC messages
      GET    — client opens a persistent SSE channel for server-initiated pushes
      DELETE — client terminates its session
    """

    # session_id -> asyncio.Queue  (used only when client has an open GET /mcp stream)
    sse_queues: dict[str, asyncio.Queue] = {}

    # ── POST /mcp ─────────────────────────────────────────────────────────────
    async def mcp_post(request: web.Request) -> web.StreamResponse:
        # ── parse body ────────────────────────────────────────────────────────
        try:
            body = await request.json()
        except Exception:
            return web.Response(
                status=400,
                content_type="application/json",
                text=json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": "Parse error"},
                    }
                ),
            )

        # ── session handling ──────────────────────────────────────────────────
        session_id: str | None = request.headers.get("Mcp-Session-Id")
        is_init = isinstance(body, dict) and body.get("method") == "initialize"

        # Non-init requests without a session ID → 400
        if not is_init and session_id is None:
            return web.Response(status=400, text="Mcp-Session-Id header required")

        # ── notifications / responses (no id) → 202, no body ─────────────────
        if isinstance(body, dict) and _is_notification(body):
            await router.handle(body)  # fire-and-forget side-effects
            return web.Response(status=202)

        # ── normal request → get response from router ─────────────────────────
        response = await router.handle(body)

        # Decide whether to respond with plain JSON or SSE.
        # We use SSE only when the client explicitly listed text/event-stream in
        # Accept AND there is a streaming result to send.  For simplicity this
        # implementation always replies with plain JSON (the most compatible mode).
        # Swap the block below for an SSE StreamResponse if you need true streaming.

        accept = request.headers.get("Accept", "")
        use_sse = "text/event-stream" in accept and response is None
        # (extend this condition when your router supports streaming generators)

        if use_sse:
            # Server has nothing to send right now; open an empty SSE stream
            # so the client knows it should keep listening.
            resp = web.StreamResponse(
                status=200,
                headers={
                    "Content-Type": "text/event-stream",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )
            await resp.prepare(request)
            return resp

        # Plain JSON response (most common path)
        resp_headers = {}
        if is_init and response is not None:
            # Assign a new session ID and return it in the response header
            new_sid = _session_id()
            sse_queues.setdefault(new_sid, asyncio.Queue())
            resp_headers["Mcp-Session-Id"] = new_sid

        return web.Response(
            status=200,
            content_type="application/json",
            headers=resp_headers,
            text=json.dumps(response) if response is not None else "",
        )

    # ── GET /mcp ──────────────────────────────────────────────────────────────
    async def mcp_get(request: web.Request) -> web.StreamResponse:
        """
        Optional persistent SSE channel for server → client pushes
        (notifications, progress, sampling requests, etc.).
        The client must include Mcp-Session-Id.
        """
        session_id = request.headers.get("Mcp-Session-Id")
        if session_id is None:
            return web.Response(status=400, text="Mcp-Session-Id header required")

        queue = sse_queues.get(session_id)
        if queue is None:
            # Create queue on demand (client may open GET before or after POST init)
            queue = asyncio.Queue()
            sse_queues[session_id] = queue

        resp = web.StreamResponse(
            status=200,
            headers={
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
        await resp.prepare(request)

        try:
            while True:
                msg = await queue.get()
                await resp.write(
                    f"event: message\ndata: {json.dumps(msg)}\n\n".encode()
                )
        except (asyncio.CancelledError, ConnectionResetError):
            pass
        finally:
            # Only remove the queue if no other coroutine will need it
            sse_queues.pop(session_id, None)

        return resp

    # ── DELETE /mcp ───────────────────────────────────────────────────────────
    async def mcp_delete(request: web.Request) -> web.Response:
        """Client signals it is done with the session."""
        session_id = request.headers.get("Mcp-Session-Id")
        if session_id is None:
            return web.Response(status=400, text="Mcp-Session-Id header required")

        queue = sse_queues.pop(session_id, None)
        if queue is not None:
            await queue.put(None)  # unblock any waiting GET handler

        return web.Response(status=200, text="Session terminated")

    # ── wire up routes ────────────────────────────────────────────────────────
    app = web.Application()
    app.router.add_post("/mcp", mcp_post)
    app.router.add_get("/mcp", mcp_get)
    app.router.add_delete("/mcp", mcp_delete)
    return app
