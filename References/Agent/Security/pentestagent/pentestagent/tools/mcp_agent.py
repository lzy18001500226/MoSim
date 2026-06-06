import asyncio
import os
import struct
import sys
import tempfile
from typing import TYPE_CHECKING

# fcntl and termios are Unix-only. Import them lazily so the module loads on
# Windows: spawn_mcp_agent will return a clear error if called there.
try:
    import fcntl
    import termios

    _UNIX_PTY_AVAILABLE = True
except ImportError:
    fcntl = None  # type: ignore[assignment]
    termios = None  # type: ignore[assignment]
    _UNIX_PTY_AVAILABLE = False

from .registry import Tool, ToolSchema

if TYPE_CHECKING:
    from ..agents.base_agent import BaseAgent
    from ..mcp.manager import MCPManager
    from ..runtime import Runtime


async def _watch_child_notifications(
    agent: "BaseAgent",
    server_name: str,
    notification_queue: "asyncio.Queue",
) -> None:
    """Background task: relay child async-task completion events to the parent.

    When a child agent finishes an async task it pushes a
    ``notifications/task_completed`` JSON-RPC notification.  FifoTransport
    routes it here.  We inject a high-priority user message directly into the
    parent agent's conversation_history so the *next* LLM iteration
    immediately sees it — effectively "waking up" the agent to process the
    result before continuing other work.

    Async tasks are prioritised over sync work because the message is injected
    at the *start* of the next iteration (before the LLM call), regardless of
    whatever the agent was doing before.
    """
    from ..agents.base_agent import AgentMessage

    try:
        while True:
            notif = await notification_queue.get()

            if notif.get("method") != "notifications/task_completed":
                continue  # ignore unrecognised notifications

            params = notif.get("params", {})
            task_id = params.get("task_id", "?")
            status = params.get("status", "unknown")
            task_desc = params.get("task", "")[:100]

            wake_content = (
                f"[ASYNC TASK COMPLETED — HIGH PRIORITY]\n"
                f"Child agent '{server_name}' finished task '{task_id}' "
                f"(status: {status}).\n"
                f"Task: {task_desc!r}\n"
                f"→ Call mcp_{server_name}_get_task_result(task_id='{task_id}') "
                f"to retrieve the full result.\n"
                f"Process this result immediately — prioritise it over any other "
                f"pending work."
            )
            agent.conversation_history.append(
                AgentMessage(
                    role="user",
                    content=wake_content,
                    metadata={
                        "child_notification": True,
                        "server": server_name,
                        "task_id": task_id,
                        "priority": "high",
                    },
                )
            )

            # Operator-visible notification in the TUI status bar / log.
            try:
                from ..interface.notifier import notify

                notify(
                    "info",
                    f"[{server_name}] async task '{task_id}' completed "
                    f"(status: {status})",
                )
            except Exception:
                pass

            # If the agent loop finished while waiting for the child, wake it up.
            # The TUI callback starts _run_wake_up_mode(), which calls
            # agent.wake_up() → _run_loop() and routes output to the chat panel.
            try:
                from ..agents.state import AgentState
                from ..interface.notifier import agent_wake_up

                # IDLE: agent_loop reset; COMPLETE: assist/interact finished
                if agent.state_manager.current_state in (
                    AgentState.IDLE,
                    AgentState.COMPLETE,
                ):
                    agent_wake_up()
            except Exception:
                pass

    except asyncio.CancelledError:
        pass


async def spawn_child_agent(
    agent: "BaseAgent",
    runtime: "Runtime",
    arguments: dict,
) -> str:
    """Spawn a child PentestAgent MCP server and wire it into *agent*.

    This is the shared implementation used by both the ``spawn_mcp_agent`` tool
    (called by the LLM) and the ``/spawn`` TUI command (called by the operator).
    """
    if not _UNIX_PTY_AVAILABLE:
        return (
            "[error] spawn_mcp_agent is not supported on Windows. "
            "Child agent spawning requires a Unix PTY (fcntl/termios). "
            "Run PentestAgent inside WSL or Docker to use this feature."
        )

    from ..mcp.manager import FifoServerConfig, MCPManager

    target = arguments.get("target", "")
    scope: list = arguments.get("scope", [])
    model = arguments.get("model", "")
    no_rag = bool(arguments.get("no_rag", False))
    no_mcp = bool(arguments.get("no_mcp", True))

    manager: MCPManager = _get_or_create_manager(runtime)
    child_index = (
        sum(1 for name in manager.servers if name.startswith("child_agent_")) + 1
    )
    server_name = f"child_agent_{child_index}"
    while server_name in manager.servers:
        child_index += 1
        server_name = f"child_agent_{child_index}"

    cmd_args = ["mcp_server", "--type", "stdio"]
    if target:
        cmd_args += ["--target", target]
    if scope:
        cmd_args += ["--scope"] + list(scope)
    if model:
        cmd_args += ["--model", model]
    if no_rag:
        cmd_args.append("--no-rag")
    if no_mcp:
        cmd_args.append("--no-mcp")

    from ..interface.notifier import spawn_terminal

    tmp_dir = tempfile.mkdtemp(prefix="pa_mcp_")
    fifo_in = os.path.join(tmp_dir, "mcp_in.fifo")
    fifo_out = os.path.join(tmp_dir, "mcp_out.fifo")
    os.mkfifo(fifo_in)
    os.mkfifo(fifo_out)

    master_fd, slave_fd = os.openpty()
    fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))

    tui_cmd_args = (
        ["-m", "pentestagent"]
        + cmd_args
        + [
            "--tui",
            "--mcp-fifo-in",
            fifo_in,
            "--mcp-fifo-out",
            fifo_out,
        ]
    )
    child_env = {**os.environ, "TERM": "xterm-256color", "COLORTERM": "truecolor"}

    def _child_pty_setup() -> None:
        os.setsid()
        fcntl.ioctl(0, termios.TIOCSCTTY, 0)

    try:
        child_proc = await asyncio.create_subprocess_exec(
            sys.executable,
            *tui_cmd_args,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            env=child_env,
            preexec_fn=_child_pty_setup,
        )
    except Exception as exc:
        os.close(slave_fd)
        os.close(master_fd)
        for p in (fifo_in, fifo_out):
            try:
                os.unlink(p)
            except OSError:
                pass
        try:
            os.rmdir(tmp_dir)
        except OSError:
            pass
        return f"[error] Failed to launch child: {exc}"

    os.close(slave_fd)

    if not hasattr(manager, "_child_processes"):
        manager._child_processes = {}  # type: ignore[attr-defined]
    manager._child_processes[server_name] = child_proc  # type: ignore[attr-defined]

    tui_accepted = spawn_terminal(master_fd, server_name)
    if not tui_accepted:
        os.close(master_fd)

    config = FifoServerConfig(
        name=server_name,
        fifo_in=fifo_in,
        fifo_out=fifo_out,
        description=f"Child PentestAgent TUI (target={target or 'none'})",
    )

    server = await manager._connect_server(config)
    if not server or not server.connected:
        err = server.last_error if server else "unknown error"
        return f"[error] Failed to connect child MCP server '{server_name}': {err}"

    manager.servers[server_name] = server

    _BLOCKED_SUFFIXES = ("_run_task", "_await_tasks")
    all_child_tools = manager.create_mcp_tools_from_server(server)
    child_tools = [
        t
        for t in all_child_tools
        if not any(t.name.endswith(suffix) for suffix in _BLOCKED_SUFFIXES)
    ]
    agent.add_tools(child_tools)

    _notif_queue = server.get_notification_queue()
    if _notif_queue is not None:
        if not hasattr(manager, "_notification_watchers"):
            manager._notification_watchers = {}  # type: ignore[attr-defined]
        manager._notification_watchers[server_name] = asyncio.create_task(  # type: ignore[attr-defined]
            _watch_child_notifications(agent, server_name, _notif_queue)
        )

    tool_names = [t.name for t in child_tools]
    lines = [
        "[ok] Child MCP agent spawned.",
        f"server_name: {server_name}",
        f"target:      {target or 'none'}",
        f"scope:       {scope or []}",
        f"tools ({len(tool_names)}): {', '.join(tool_names)}",
        "",
        "Async-only mode: use run_task_async to submit tasks.",
        "A push notification is delivered when each task completes.",
    ]
    return "\n".join(lines)


async def despawn_child_agent(
    agent: "BaseAgent",
    runtime: "Runtime",
    server_name: str,
) -> str:
    """Terminate a child MCP agent and free all associated resources.

    Shared implementation used by both the ``despawn_mcp_agent`` tool and
    the ``/despawn`` TUI command.
    """
    from ..mcp.manager import FifoServerConfig

    server_name = server_name.strip()
    if not server_name:
        return "[error] server_name is required."

    manager = _get_or_create_manager(runtime)
    server = manager.servers.get(server_name)
    if server is None:
        return f"[error] No child agent named '{server_name}' is connected."

    fifo_paths: list[str] = []
    tmp_dir: str = ""
    if isinstance(server.config, FifoServerConfig):
        fifo_paths = [server.config.fifo_in, server.config.fifo_out]
        if fifo_paths:
            tmp_dir = os.path.dirname(fifo_paths[0])

    prefix = f"mcp_{server_name}_"
    tools_to_remove = [t for t in agent.tools if t.name.startswith(prefix)]
    agent.delete_tools(tools_to_remove)
    removed_names = [t.name for t in tools_to_remove]

    child_proc = None
    child_processes: dict = getattr(manager, "_child_processes", {})
    if server_name in child_processes:
        child_proc = child_processes.pop(server_name)
        try:
            child_proc.terminate()
            try:
                await asyncio.wait_for(child_proc.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                child_proc.kill()
                await child_proc.wait()
        except (ProcessLookupError, OSError):
            pass

    _watchers: dict = getattr(manager, "_notification_watchers", {})
    if server_name in _watchers:
        watcher_task = _watchers.pop(server_name)
        watcher_task.cancel()
        try:
            await watcher_task
        except asyncio.CancelledError:
            pass

    await manager.disconnect_server(server_name)

    for path in fifo_paths:
        try:
            os.unlink(path)
        except OSError:
            pass
    if tmp_dir:
        try:
            os.rmdir(tmp_dir)
        except OSError:
            pass

    try:
        from ..interface.notifier import despawn_terminal

        despawn_terminal(server_name)
    except Exception:
        pass

    lines = [
        f"[ok] Child agent '{server_name}' despawned.",
        f"process terminated: {'yes' if child_proc is not None else 'n/a'}",
        f"tools removed ({len(removed_names)}): {', '.join(removed_names) or 'none'}",
    ]
    return "\n".join(lines)


def create_spawn_mcp_agent_tool(agent: "BaseAgent") -> Tool:
    """
    Build and return the spawn_mcp_agent Tool with the agent captured in closure.

    Args:
        agent: The parent PentestAgentAgent instance. Captured by reference so
               add_tools() calls on it are reflected immediately.

    Returns:
        A fully configured Tool ready to be passed to agent.add_tools().
    """

    async def _spawn_mcp_agent(arguments: dict, runtime: "Runtime") -> str:
        return await spawn_child_agent(agent, runtime, arguments)

    return Tool(
        name="spawn_mcp_agent",
        description=(
            "Spawn a child PentestAgent process as a subordinate MCP server and "
            "register its tools into your current tool set. "
            "The child is always launched with an embedded terminal panel inside the "
            "parent TUI so an operator can observe it; MCP communication is routed "
            "through named FIFOs while the child's TUI output is captured via PTY "
            "and rendered in a side panel. "
            "After this tool returns, the child's tools will be available to you in "
            "the NEXT tool call — they are not usable within the same turn. "
            "ASYNC-ONLY: the child exposes only non-blocking task execution. "
            "Use mcp_<name>_run_task_async to submit work; a push notification "
            "(notifications/task_completed) is delivered automatically when the task "
            "finishes — call mcp_<name>_get_task_result then. "
            "run_task (sync) and await_tasks are not available on child agents."
        ),
        schema=ToolSchema(
            properties={
                "target": {
                    "type": "string",
                    "description": "Pentest target to pass to the child agent.",
                },
                "scope": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "In-scope targets/CIDRs to pass to the child agent.",
                },
                "model": {
                    "type": "string",
                    "description": (
                        "Model identifier for the child agent "
                        "(overrides PENTESTAGENT_MODEL env var on the child)."
                    ),
                },
                "no_rag": {
                    "type": "boolean",
                    "description": "Skip RAG engine initialisation on the child.",
                },
                "no_mcp": {
                    "type": "boolean",
                    "description": (
                        "Skip external MCP server connections on the child "
                        "(default: true — children don't chain MCP servers unless asked)."
                    ),
                },
            },
            required=[],
        ),
        execute_fn=_spawn_mcp_agent,
        category="agents",
    )


def create_despawn_mcp_agent_tool(agent: "BaseAgent") -> Tool:
    """
    Build and return the despawn_mcp_agent Tool with the agent captured in closure.

    Args:
        agent: The parent PentestAgentAgent instance whose tool list will be pruned.

    Returns:
        A fully configured Tool ready to be passed to agent.add_tools().
    """

    async def _despawn_mcp_agent(arguments: dict, runtime: "Runtime") -> str:
        return await despawn_child_agent(
            agent, runtime, arguments.get("server_name", "")
        )

    return Tool(
        name="despawn_mcp_agent",
        description=(
            "Terminate a child MCP agent that was previously spawned with "
            "spawn_mcp_agent and free all associated resources. "
            "This will: (1) send SIGTERM (then SIGKILL if needed) to the child "
            "process; (2) close the MCP transport connection; (3) remove all tools "
            "that the child injected into your tool set; (4) delete any FIFO files "
            "and temporary directories created for TUI mode. "
            "Use this when a subtask is complete and you no longer need the child "
            "agent, or when you want to reclaim resources. "
            "Pass the server_name that was returned by spawn_mcp_agent."
        ),
        schema=ToolSchema(
            properties={
                "server_name": {
                    "type": "string",
                    "description": (
                        "The server name of the child agent to despawn "
                        "(e.g. 'child_agent_1'). This is the 'server_name' field "
                        "returned by spawn_mcp_agent."
                    ),
                },
            },
            required=["server_name"],
        ),
        execute_fn=_despawn_mcp_agent,
        category="agents",
    )


def _get_or_create_manager(runtime: "Runtime") -> "MCPManager":
    from ..mcp.manager import MCPManager

    manager = getattr(runtime, "mcp_manager", None)
    if manager is None:
        manager = MCPManager()
        runtime.mcp_manager = manager  # type: ignore[attr-defined]
    return manager
