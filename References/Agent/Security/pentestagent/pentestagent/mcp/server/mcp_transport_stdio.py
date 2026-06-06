# mcp_transport_stdio.py — STDIO transport layer
import asyncio
import json
import sys

from .mcp_core import MCPRouter

# ─── Wire I/O ─────────────────────────────────────────────────────────────────


def _send(msg: dict):
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def _read() -> dict | None:
    line = sys.stdin.readline()
    return json.loads(line.strip()) if line else None


# ─── Transport ────────────────────────────────────────────────────────────────


async def run_stdio(router: MCPRouter):
    """Read JSON-RPC messages from stdin, write responses to stdout."""
    loop = asyncio.get_event_loop()
    while True:
        req = await loop.run_in_executor(None, _read)
        if req is None:
            break
        response = await router.handle(req)
        if response is not None:
            _send(response)


async def run_stdio_fifo(router: MCPRouter, fifo_in: str, fifo_out: str):
    """Read JSON-RPC from *fifo_in*, write responses to *fifo_out*.

    Used when the MCP server runs alongside a TUI in a terminal window.
    The child opens *fifo_in* for reading (MCP requests come in from the
    parent) and *fifo_out* for writing (MCP responses go out to the parent).

    Opening order is intentional to match the parent's FifoTransport which
    opens them in the opposite direction concurrently:
      child  opens fifo_in  O_RDONLY → parent thread unblocks O_WRONLY
      child  opens fifo_out O_WRONLY → parent thread unblocks O_RDONLY

    Two concurrent asyncio tasks run on the same out_file:
      _serve_requests  – handles incoming MCP requests, writes responses
      _drain_outgoing  – forwards async-task-completion notifications pushed
                         by _drive_task() via _outgoing_queue

    A single asyncio.Lock serialises all writes to out_file so that JSON
    lines from both tasks are never interleaved.
    """
    from .mcp_tools import get_outgoing_queue

    loop = asyncio.get_event_loop()

    # Sequential opens are safe here: the parent opens both ends concurrently
    # (via asyncio.gather + executor), so the child's sequential opens will
    # pair with the waiting parent threads.
    in_file = await loop.run_in_executor(None, lambda: open(fifo_in, "r", buffering=1))
    out_file = await loop.run_in_executor(
        None, lambda: open(fifo_out, "w", buffering=1)
    )

    def _read_fifo() -> dict | None:
        line = in_file.readline()
        return json.loads(line.strip()) if line else None

    _write_lock = asyncio.Lock()

    async def _send_fifo(msg: dict) -> None:
        async with _write_lock:
            await loop.run_in_executor(
                None,
                lambda m=msg: (out_file.write(json.dumps(m) + "\n"), out_file.flush()),
            )

    async def _serve_requests() -> None:
        """Normal MCP request/response loop."""
        while True:
            req = await loop.run_in_executor(None, _read_fifo)
            if req is None:
                break
            response = await router.handle(req)
            if response is not None:
                await _send_fifo(response)

    async def _drain_outgoing() -> None:
        """Forward async-task-completion notifications to the parent."""
        outgoing = get_outgoing_queue()
        while True:
            msg = await outgoing.get()
            await _send_fifo(msg)

    serve_task = asyncio.create_task(_serve_requests())
    drain_task = asyncio.create_task(_drain_outgoing())
    try:
        # Block until the input FIFO is closed (parent disconnected or despawned).
        await serve_task
    except asyncio.CancelledError:
        pass
    finally:
        drain_task.cancel()
        try:
            await drain_task
        except (asyncio.CancelledError, Exception):
            pass
        for f in (in_file, out_file):
            try:
                f.close()
            except Exception:
                pass
