"""MCP transport implementations for PentestAgent."""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class MCPTransport(ABC):
    """Abstract base class for MCP transports."""

    @abstractmethod
    async def connect(self):
        """Establish the connection."""
        pass

    @abstractmethod
    async def send(self, message: dict, timeout: float = 15.0) -> dict:
        """Send a message and receive a response."""
        pass

    @abstractmethod
    async def disconnect(self):
        """Close the connection."""
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the transport is connected."""
        pass

    @abstractmethod
    def get_logs(self) -> str:
        pass


class StdioTransport(MCPTransport):
    """MCP transport over stdio (for npx/uvx commands)."""

    def __init__(self, command: str, args: list[str], env: Dict[str, str]):
        """
        Initialize stdio transport.

        Args:
            command: The command to run (e.g., 'npx', 'uvx')
            args: Command arguments
            env: Additional environment variables
        """
        self.command = command
        self.args = args
        self.env = env
        self.process: Optional[asyncio.subprocess.Process] = None
        self._lock = asyncio.Lock()
        self.logstask = None
        self.logs = ""

    def get_logs(self) -> str:
        return self.logs

    @property
    def is_connected(self) -> bool:
        """Check if the process is running."""
        return self.process is not None and self.process.returncode is None

    async def _read_stderr_loop(self):
        try:
            while True:
                line = await self.process.stderr.readline()
                if not line:
                    break
                self.logs += line.decode().rstrip() + "\n"
        except asyncio.CancelledError:
            # Optional: do any cleanup here
            pass

    async def connect(self):
        """Start the MCP server process."""
        import shutil

        # Merge environment variables
        full_env = {**os.environ, **self.env}

        # On Windows, resolve commands like npx, uvx that may be .cmd/.ps1 wrappers
        if os.name == "nt":
            # Check for .cmd version first (more compatible)
            cmd_path = shutil.which(f"{self.command}.cmd")
            if cmd_path:
                resolved_command = cmd_path
            else:
                # Fall back to regular which
                resolved_command = shutil.which(self.command) or self.command
        else:
            resolved_command = self.command

        self.process = await asyncio.create_subprocess_exec(
            resolved_command,
            *self.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=full_env,
            limit=1024 * 1024,  # 1MB buffer limit for large MCP responses
        )

        self.logstask = asyncio.create_task(self._read_stderr_loop())

    async def send(self, message: dict, timeout: float = 15.0) -> dict:
        """
        Send a JSON-RPC message and wait for response.

        Args:
            message: The JSON-RPC message to send
            timeout: Timeout in seconds for response (default 15s)

        Returns:
            The JSON-RPC response
        """
        if not self.process or not self.process.stdin or not self.process.stdout:
            raise RuntimeError("Transport not connected")

        async with self._lock:
            # Send JSON-RPC message with newline
            msg_bytes = (json.dumps(message) + "\n").encode()
            self.process.stdin.write(msg_bytes)
            await self.process.stdin.drain()

            # Notifications don't have responses
            if "id" not in message:
                return {}

            # Read response line
            try:
                response_line = await asyncio.wait_for(
                    self.process.stdout.readline(), timeout=timeout
                )

                if not response_line:
                    raise RuntimeError("Server closed connection")

                return json.loads(response_line.decode())

            except asyncio.TimeoutError as e:
                raise RuntimeError("Timeout waiting for MCP response") from e
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Invalid JSON response: {e}") from e

    async def disconnect(self):
        """Terminate the MCP server process cleanly."""
        if not self.process:
            return

        if self.logstask:

            self.logstask.cancel()

            try:
                await self.logstask
            except asyncio.CancelledError:
                pass  # Task was successfully cancelled

        proc = self.process
        self.process = None

        # Close all pipes first to prevent "unclosed transport" warnings
        for pipe in (proc.stdin, proc.stdout, proc.stderr):
            if pipe:
                try:
                    pipe.close()
                except Exception:
                    pass

        # Wait for pipe transports to close
        if proc.stdin:
            try:
                await proc.stdin.wait_closed()
            except Exception:
                pass

        # Terminate the process
        try:
            proc.terminate()
            await asyncio.wait_for(proc.wait(), timeout=2.0)
        except asyncio.TimeoutError:
            proc.kill()
            try:
                await proc.wait()
            except Exception:
                pass
        except Exception:
            pass


class SSETransport(MCPTransport):
    """MCP transport over Server-Sent Events (HTTP)."""

    def __init__(self, url: str, bearer: str = ""):
        """
        Initialize SSE transport.

        Args:
            url: The HTTP endpoint URL
        """
        self.url = url
        self.session: Optional[Any] = None  # aiohttp.ClientSession
        self._connected = False
        self._logs = ""
        self._bearer = bearer

    @property
    def is_connected(self) -> bool:
        """Check if the session is active."""
        return self._connected and self.session is not None

    def get_logs(self) -> str:
        return self._logs

    async def connect(self):
        """Connect to the SSE endpoint."""
        try:
            import aiohttp

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            }

            if self._bearer:
                headers["Authorization"] = f"Bearer {self._bearer}"

            self.session = aiohttp.ClientSession(headers=headers)
            self._connected = True
        except ImportError as e:
            raise RuntimeError(
                "aiohttp is required for SSE transport. Install with: pip install aiohttp"
            ) from e

    async def send(self, message: dict, timeout: float = 15.0) -> dict:
        """
        Send a message via HTTP POST.

        Args:
            message: The JSON-RPC message to send

        Returns:
            The JSON-RPC response
        """
        if not self.session:
            raise RuntimeError("Transport not connected")

        try:
            import aiohttp

            headers_str = "\n".join(
                f"{k}: {v}" for k, v in self.session.headers.items()
            )
            self._logs += f"Request headers: {headers_str}" + "\n"

            async with self.session.post(
                self.url, json=message, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status != 200 and response.status != 202:
                    raise RuntimeError(f"HTTP error: {response.status}")

                # https://modelcontextprotocol.io/specification/2025-11-25/basic/transports#session-management
                mcp_session_id = response.headers.get("mcp-session-id")

                if mcp_session_id:
                    self.session.headers.update({"mcp-session-id": mcp_session_id})

                content_type = response.headers.get("Content-Type", "")

                headers_str = "\n".join(
                    f"{k}: {v}" for k, v in response.headers.items()
                )
                self._logs += f"Response headers: {headers_str}\nResponse status: {response.status}\n"

                if "application/json" in content_type:
                    return await response.json()
                elif "text/event-stream" in content_type:
                    text = await response.text()
                    # Parse SSE format: "data: {json}\n"
                    for line in text.split("\n"):
                        if line.startswith("data:"):
                            try:
                                return json.loads(line[len("data:") :].strip())
                            except json.JSONDecodeError:
                                pass
                    raise RuntimeError("No valid data field in SSE response")
                return {}
        except ImportError as e:
            raise RuntimeError(
                "aiohttp is required for SSE transport. Install with: pip install aiohttp"
            ) from e
        except Exception as e:
            raise RuntimeError(f"SSE request failed: {e}") from e

    async def disconnect(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
            self._connected = False


class FifoTransport(MCPTransport):
    """MCP transport over a pair of named FIFOs.

    Used when the child MCP server runs in a separate terminal window with a TUI.
    The parent writes MCP requests to ``fifo_in`` and reads responses from
    ``fifo_out``.  The child does the opposite: reads from ``fifo_in``, writes
    to ``fifo_out``.

    FIFO open(2) calls block until the other end is also opened, so the two
    opens are issued concurrently (via asyncio gather + executor threads) to
    avoid deadlock.  The parent waits up to *connect_timeout* seconds for the
    child process to start and open its end.

    A background asyncio task (_background_reader) continuously reads from
    fifo_out and dispatches each line:
      • Lines that carry an "id" field → delivered to the matching Future
        that send() is awaiting, so the MCP request/response cycle works as
        before but without holding a lock during the read.
      • Lines without an "id" field (JSON-RPC notifications) → placed in
        notification_queue so the parent agent can drain them between LLM
        iterations and inject high-priority wake-up messages.
    """

    def __init__(self, fifo_in: str, fifo_out: str, connect_timeout: float = 30.0):
        self.fifo_in = fifo_in  # parent writes, child reads
        self.fifo_out = fifo_out  # child writes, parent reads
        self._writer = None
        self._reader = None
        self._connected = False
        self._connect_timeout = connect_timeout
        self.logs = ""
        # Write-side serialisation (reads handled by background task).
        self._writer_lock: asyncio.Lock = asyncio.Lock()
        # Pending response futures keyed by JSON-RPC message id.
        self._pending: dict[int, asyncio.Future] = {}
        # Push-notification queue: child → parent (no "id" in JSON-RPC message).
        self.notification_queue: asyncio.Queue = asyncio.Queue()
        self._reader_task: Optional[asyncio.Task] = None

    def get_logs(self) -> str:
        return self.logs

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def _background_reader(self) -> None:
        """Continuously read fifo_out, dispatch responses and queue notifications."""
        loop = asyncio.get_running_loop()
        try:
            while self._connected:
                line = await loop.run_in_executor(None, self._reader.readline)
                if not line:
                    # EOF – child closed its end (despawned or crashed).
                    break
                try:
                    msg = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
                msg_id = msg.get("id")
                if msg_id is not None:
                    # MCP response – wake the waiting send() call.
                    fut = self._pending.get(msg_id)
                    if fut is not None and not fut.done():
                        fut.set_result(msg)
                else:
                    # JSON-RPC notification (no id) – push to notification queue.
                    await self.notification_queue.put(msg)
        except asyncio.CancelledError:
            pass
        except Exception:
            pass
        finally:
            # Fail any pending futures so send() callers don't hang.
            for fut in list(self._pending.values()):
                if not fut.done():
                    fut.cancel()
            self._pending.clear()

    async def connect(self):
        """Open both FIFOs concurrently.  Blocks until the child opens its ends."""
        loop = asyncio.get_running_loop()

        async def _open_write():
            fd = await loop.run_in_executor(
                None, lambda: os.open(self.fifo_in, os.O_WRONLY)
            )
            return os.fdopen(fd, "w", buffering=1)

        async def _open_read():
            fd = await loop.run_in_executor(
                None, lambda: os.open(self.fifo_out, os.O_RDONLY)
            )
            return os.fdopen(fd, "r", buffering=1)

        try:
            self._writer, self._reader = await asyncio.wait_for(
                asyncio.gather(_open_write(), _open_read()),
                timeout=self._connect_timeout,
            )
            self._connected = True
            # Start the background reader *after* both files are open.
            self._reader_task = asyncio.create_task(self._background_reader())
        except asyncio.TimeoutError as err:
            raise RuntimeError(
                f"Timeout ({self._connect_timeout}s) waiting for child agent "
                "to open FIFOs — child may have failed to start"
            ) from err

    async def send(self, message: dict, timeout: float = 15.0) -> dict:
        if not self._writer or not self._reader:
            raise RuntimeError("FifoTransport not connected")

        loop = asyncio.get_running_loop()
        msg_str = json.dumps(message) + "\n"

        if "id" not in message:
            # Fire-and-forget notification: just write, no response expected.
            async with self._writer_lock:
                await loop.run_in_executor(
                    None,
                    lambda: (self._writer.write(msg_str), self._writer.flush()),
                )
            return {}

        msg_id = message["id"]
        # Register the future *before* writing so the background reader can
        # always find it, even if the child responds before we reach the await.
        fut: asyncio.Future = loop.create_future()
        self._pending[msg_id] = fut
        try:
            async with self._writer_lock:
                await loop.run_in_executor(
                    None,
                    lambda: (self._writer.write(msg_str), self._writer.flush()),
                )
            return await asyncio.wait_for(fut, timeout=timeout)
        except asyncio.TimeoutError as err:
            raise RuntimeError("Timeout waiting for MCP response via FIFO") from err
        finally:
            self._pending.pop(msg_id, None)

    async def disconnect(self):
        self._connected = False
        # Close the reader first so any blocking readline() in the background
        # task returns immediately (EOF), letting the task finish cleanly.
        if self._reader is not None:
            try:
                self._reader.close()
            except Exception:
                pass
            self._reader = None
        if self._reader_task is not None:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
            self._reader_task = None
        if self._writer is not None:
            try:
                self._writer.close()
            except Exception:
                pass
            self._writer = None


class WebSocketTransport(MCPTransport):
    """MCP transport over WebSocket."""

    def __init__(self, url: str):
        """
        Initialize WebSocket transport.

        Args:
            url: The WebSocket endpoint URL
        """
        self.url = url
        self.ws: Optional[Any] = None
        self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if the WebSocket is connected."""
        return self._connected and self.ws is not None

    async def connect(self):
        """Connect to the WebSocket endpoint."""
        try:
            import aiohttp

            self._session = aiohttp.ClientSession()
            self.ws = await self._session.ws_connect(self.url)
            self._connected = True
        except ImportError as e:
            raise RuntimeError("aiohttp is required for WebSocket transport") from e

    async def send(self, message: dict, timeout: float = 15.0) -> dict:
        """
        Send a message via WebSocket.

        Args:
            message: The JSON-RPC message to send

        Returns:
            The JSON-RPC response
        """
        if not self.ws:
            raise RuntimeError("Transport not connected")

        await self.ws.send_json(message)

        # Notifications don't have responses
        if "id" not in message:
            return {}

        response = await self.ws.receive_json()
        return response

    async def disconnect(self):
        """Close the WebSocket connection."""
        if self.ws:
            await self.ws.close()
            self.ws = None
        if hasattr(self, "_session") and self._session:
            await self._session.close()
            self._session = None
        self._connected = False
