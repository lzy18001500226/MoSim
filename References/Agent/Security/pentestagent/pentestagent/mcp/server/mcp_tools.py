from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Optional, Type

from .mcp_core import ToolRegistry

if TYPE_CHECKING:
    from pentestagent.agents.pa_agent import PentestAgentAgent
    from pentestagent.llm import LLM
    from pentestagent.runtime.runtime import Runtime

# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------

_primary_agent: Optional[PentestAgentAgent] = None
_LLMClass: Optional[Type[LLM]] = None
_RuntimeClass: Optional[Type[Runtime]] = None
_llm_kwargs: dict[str, Any] = {}
_runtime_kwargs: dict[str, Any] = {}

# Optional UI hook: called with (event_type: str, data: dict) for each
# significant event during task execution.  Registered by the TUI when
# running in MCP observation mode.
_ui_hook: Optional[Callable[[str, dict], None]] = None


def set_ui_hook(hook: Optional[Callable[[str, dict], None]]) -> None:
    """Register (or clear) the UI event hook.  Thread-safe write."""
    global _ui_hook
    _ui_hook = hook


def _emit(event: str, data: dict) -> None:
    """Deliver a UI event if a hook is registered, swallowing any errors."""
    if _ui_hook is not None:
        try:
            _ui_hook(event, data)
        except Exception:
            pass


_tasks: dict[str, TaskEntry] = {}
_memory: dict[str, dict[str, str]] = {}
_logs: list[dict[str, str]] = []
_LOG_MAX = 500

# Outgoing JSON-RPC notification queue.
# _drive_task() puts a "notifications/task_completed" message here when an
# async task finishes.  The FIFO transport (run_stdio_fifo) drains this queue
# concurrently and forwards every message to the parent agent.
_outgoing_queue: asyncio.Queue = asyncio.Queue()


def get_outgoing_queue() -> asyncio.Queue:
    """Return the module-level outgoing notification queue."""
    return _outgoing_queue


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------


def bootstrap(
    primary_agent: "PentestAgentAgent",
    llm_class: Type["LLM"],
    runtime_class: Type["Runtime"],
    llm_kwargs: Optional[dict[str, Any]] = None,
    runtime_kwargs: Optional[dict[str, Any]] = None,
) -> None:
    """
    Called once from server.py after _initialize() has built every component.
    The primary_agent is used ONLY as a configuration source — never to execute tasks.
    """
    global _primary_agent, _LLMClass, _RuntimeClass, _llm_kwargs, _runtime_kwargs
    _primary_agent = primary_agent
    _LLMClass = llm_class
    _RuntimeClass = runtime_class
    _llm_kwargs = llm_kwargs or {}
    _runtime_kwargs = runtime_kwargs or {}
    _log("info", "mcp_tools bootstrapped.")


# ---------------------------------------------------------------------------
# TaskEntry
# ---------------------------------------------------------------------------


@dataclass
class TaskEntry:
    id: str
    task: str
    status: str  # pending | running | done | error | cancelled
    created_at: str
    agent: "PentestAgentAgent"
    target: Optional[str] = None
    scope: list[str] = field(default_factory=list)
    finished_at: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None
    thinking: list[str] = field(default_factory=list)
    tool_calls: list[dict[str, object]] = field(default_factory=list)
    tool_results: list[dict[str, object]] = field(default_factory=list)
    notes_snapshot: Optional[str] = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _log(level: str, message: str) -> None:
    _logs.append(
        {"ts": datetime.utcnow().isoformat(), "level": level, "message": message}
    )
    if len(_logs) > _LOG_MAX:
        _logs.pop(0)


async def _make_agent(target: Optional[str], scope: list[str]) -> "PentestAgentAgent":
    """Construct a fresh agent for each task — no shared mutable state between runs."""
    from pentestagent.agents.pa_agent import PentestAgentAgent

    if _LLMClass is None or _RuntimeClass is None:
        raise RuntimeError("bootstrap() must be called before running tasks.")

    runtime = _RuntimeClass(**_runtime_kwargs)
    await runtime.start()

    return PentestAgentAgent(
        llm=_LLMClass(**_llm_kwargs),
        tools=list(_primary_agent.get_tools()) if _primary_agent else [],
        runtime=runtime,
        target=target,
        scope=scope,
        max_iterations=getattr(_primary_agent, "max_iterations", 30),
    )


def _resolve_target_scope(args: dict[str, object]) -> tuple[Optional[str], list[str]]:
    target = (
        str(args["target"])
        if "target" in args
        else getattr(_primary_agent, "target", None)
    )
    scope = list(args["scope"]) if "scope" in args else list(getattr(_primary_agent, "scope", []))  # type: ignore[arg-type]
    return target, scope


async def _capture_notes_snapshot(agent: "PentestAgentAgent") -> Optional[str]:
    try:
        notes_tool = next((t for t in agent.tools if t.name == "notes"), None)
        if notes_tool is None:
            return None
        result = await notes_tool.execute({"action": "list"}, agent.runtime)
        return result if isinstance(result, str) else None
    except Exception as exc:
        _log("warning", f"notes snapshot failed: {exc}")
        return None


async def _drive_task(entry: TaskEntry) -> None:
    """Run the agent loop, recording all output into the TaskEntry."""
    entry.status = "running"
    output_parts: list[str] = []

    _emit(
        "task_start",
        {
            "task_id": entry.id,
            "task": entry.task,
            "target": entry.target,
        },
    )

    try:
        async for response in entry.agent.run_mcp(entry.task):

            if entry.status == "cancelled":
                entry.agent.cleanup_after_cancel()
                break

            if response.content and response.tool_calls:
                entry.thinking.append(response.content.strip())
                _emit(
                    "thinking",
                    {"content": response.content.strip(), "task_id": entry.id},
                )
            elif response.content:
                output_parts.append(response.content.strip())
                _emit(
                    "content",
                    {"content": response.content.strip(), "task_id": entry.id},
                )

            for call in response.tool_calls or []:
                entry.tool_calls.append(
                    {
                        "id": call.id,
                        "name": call.name,
                        "arguments": call.arguments,
                    }
                )
                _emit(
                    "tool_call",
                    {
                        "task_id": entry.id,
                        "id": call.id,
                        "name": call.name,
                        "arguments": call.arguments,
                    },
                )

            for result in response.tool_results or []:
                entry.tool_results.append(
                    {
                        "tool_call_id": result.tool_call_id,
                        "tool_name": result.tool_name,
                        "success": result.success,
                        "result": result.result if result.success else None,
                        "error": result.error if not result.success else None,
                    }
                )
                _emit(
                    "tool_result",
                    {
                        "task_id": entry.id,
                        "tool_call_id": result.tool_call_id,
                        "tool_name": result.tool_name,
                        "success": result.success,
                        "result": result.result if result.success else result.error,
                    },
                )

        if entry.status != "cancelled":
            entry.result = "\n".join(output_parts) or "Done (no text output)."
            entry.status = "done"
            entry.notes_snapshot = await _capture_notes_snapshot(entry.agent)

    except asyncio.CancelledError:
        entry.status = "cancelled"
        entry.agent.cleanup_after_cancel()
        _log("info", f"Task {entry.id} cancelled.")

    except Exception as exc:
        entry.status = "error"
        entry.error = str(exc)
        _log("error", f"Task {entry.id} error: {exc}")

    finally:
        entry.finished_at = datetime.utcnow().isoformat()
        _log("info", f"Task {entry.id} finished — status={entry.status}")
        _emit(
            "task_done",
            {
                "task_id": entry.id,
                "status": entry.status,
                "result": entry.result,
                "error": entry.error,
            },
        )
        # Push a JSON-RPC notification to the parent agent.
        # The FIFO transport picks this up and routes it to the parent's
        # notification_queue, which wakes the parent agent loop.
        try:
            _outgoing_queue.put_nowait(
                {
                    "jsonrpc": "2.0",
                    "method": "notifications/task_completed",
                    "params": {
                        "task_id": entry.id,
                        "status": entry.status,
                        "task": entry.task[:120],
                    },
                }
            )
        except Exception:
            pass


def _create_task(
    task: str, agent: "PentestAgentAgent", target: Optional[str], scope: list[str]
) -> TaskEntry:
    entry = TaskEntry(
        id=str(uuid.uuid4())[:8],
        task=task,
        status="pending",
        created_at=datetime.utcnow().isoformat(),
        agent=agent,
        target=target,
        scope=scope,
    )
    _tasks[entry.id] = entry
    return entry


# ---------------------------------------------------------------------------
# ToolRegistry
# ---------------------------------------------------------------------------

mcp_tool_registry = ToolRegistry()


# ===========================================================================
# GROUP: SERVER STATUS & CONFIG
# ===========================================================================


@mcp_tool_registry.register(
    name="get_server_status",
    description=(
        "Return the live status of the MCP server: readiness, task counts by state, "
        "primary target/scope, and memory store size."
    ),
    schema={"type": "object", "properties": {}, "required": []},
)
async def get_server_status(args: dict[str, object]) -> str:
    by_status = {s: [] for s in ("pending", "running", "done", "error", "cancelled")}
    for e in _tasks.values():
        by_status.get(e.status, []).append(e.id)

    lines: list[str] = [
        f"ready:      {_primary_agent is not None}",
        f"active:     {len(by_status['pending']) + len(by_status['running'])}",
        f"done:       {len(by_status['done'])}",
        f"error:      {len(by_status['error'])}",
        f"cancelled:  {len(by_status['cancelled'])}",
        f"memory_keys:{len(_memory)}",
    ]
    if _primary_agent:
        lines += [
            f"primary_target: {getattr(_primary_agent, 'target', 'none')}",
            f"primary_scope:  {getattr(_primary_agent, 'scope', [])}",
            f"max_iterations: {_primary_agent.max_iterations}",
        ]
    active_ids = by_status["pending"] + by_status["running"]
    if active_ids:
        lines.append("active_ids: " + ", ".join(active_ids))
    return "\n".join(lines)


@mcp_tool_registry.register(
    name="get_config",
    description="Return the primary agent configuration: target, scope, max_iterations, and tool list.",
    schema={"type": "object", "properties": {}, "required": []},
)
async def get_config(args: dict[str, object]) -> str:
    if not _primary_agent:
        return "[error] Primary agent not initialised."
    tools = [t.name for t in _primary_agent.get_tools()]
    return "\n".join(
        [
            f"target:         {getattr(_primary_agent, 'target', 'none')}",
            f"scope:          {getattr(_primary_agent, 'scope', [])}",
            f"max_iterations: {_primary_agent.max_iterations}",
            f"tools ({len(tools)}): {', '.join(tools)}",
        ]
    )


@mcp_tool_registry.register(
    name="update_config",
    description="Update the primary agent configuration. Changes apply to all subsequent tasks.",
    schema={
        "type": "object",
        "properties": {
            "target": {"type": "string"},
            "scope": {"type": "array", "items": {"type": "string"}},
            "max_iterations": {"type": "integer"},
        },
        "required": [],
    },
)
async def update_config(args: dict[str, object]) -> str:
    if not _primary_agent:
        return "[error] Primary agent not initialised."
    updated: list[str] = []
    if "target" in args:
        _primary_agent.target = str(args["target"])
        updated.append(f"target → {args['target']}")
    if "scope" in args:
        _primary_agent.scope = list(args["scope"])  # type: ignore[arg-type]
        updated.append(f"scope → {args['scope']}")
    if "max_iterations" in args:
        _primary_agent.max_iterations = int(args["max_iterations"])  # type: ignore[arg-type]
        updated.append(f"max_iterations → {args['max_iterations']}")
    return (
        "Updated:\n" + "\n".join(updated)
        if updated
        else "No recognised fields provided."
    )


# ===========================================================================
# GROUP: TASK EXECUTION
# ===========================================================================


@mcp_tool_registry.register(
    name="run_task",
    description=(
        "Submit a task and BLOCK until it completes. "
        "Use for short tasks where the result is needed immediately."
    ),
    schema={
        "type": "object",
        "properties": {
            "task": {"type": "string", "description": "Fully-specified task prompt"},
            "target": {
                "type": "string",
                "description": "Override primary target for this task",
            },
            "scope": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Override scope for this task",
            },
        },
        "required": ["task"],
    },
)
async def run_task(args: dict[str, object]) -> str:
    if not _primary_agent:
        return "[error] Primary agent not initialised."

    target, scope = _resolve_target_scope(args)
    try:
        agent = await _make_agent(target, scope)
    except Exception as exc:
        return f"[error] Failed to create agent: {exc}"

    entry = _create_task(str(args["task"]), agent, target, scope)
    _log("info", f"run_task [{entry.id}]: {entry.task[:80]}")
    await _drive_task(entry)

    if entry.status == "error":
        return f"[error] {entry.error}"

    lines = [f"[result]\n{entry.result}"]
    if entry.tool_calls:
        lines.append(
            "[tools_used] " + ", ".join(str(c["name"]) for c in entry.tool_calls)
        )
    if entry.notes_snapshot:
        lines.append(f"[notes_snapshot]\n{entry.notes_snapshot}")
    return "\n".join(lines)


@mcp_tool_registry.register(
    name="run_task_async",
    description=(
        "Submit a task and return IMMEDIATELY with a task_id. "
        "Use get_task_status to poll, or await_tasks to block until done."
    ),
    schema={
        "type": "object",
        "properties": {
            "task": {"type": "string", "description": "Fully-specified task prompt"},
            "target": {
                "type": "string",
                "description": "Override primary target for this task",
            },
            "scope": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Override scope for this task",
            },
        },
        "required": ["task"],
    },
)
async def run_task_async(args: dict[str, object]) -> str:
    if not _primary_agent:
        return "[error] Primary agent not initialised."

    target, scope = _resolve_target_scope(args)
    try:
        agent = await _make_agent(target, scope)
    except Exception as exc:
        return f"[error] Failed to create agent: {exc}"

    entry = _create_task(str(args["task"]), agent, target, scope)
    asyncio.create_task(_drive_task(entry))
    _log("info", f"run_task_async [{entry.id}]: {entry.task[:80]}")
    return f"task_id: {entry.id}\nstatus: pending\ntask: {entry.task}"


# ===========================================================================
# GROUP: TASK INSPECTION
# ===========================================================================


@mcp_tool_registry.register(
    name="list_tasks",
    description="List all tasks with their status, target, and task summary.",
    schema={
        "type": "object",
        "properties": {
            "status": {
                "type": "string",
                "description": "Filter: pending | running | done | error | cancelled",
            },
            "limit": {
                "type": "integer",
                "description": "Max entries, most recent first (default 20)",
            },
        },
        "required": [],
    },
)
async def list_tasks(args: dict[str, object]) -> str:
    entries = sorted(_tasks.values(), key=lambda e: e.created_at, reverse=True)
    if "status" in args:
        entries = [e for e in entries if e.status == str(args["status"])]
    entries = entries[: int(args.get("limit") or 20)]  # type: ignore[arg-type]
    if not entries:
        return "No tasks found."
    lines: list[str] = []
    for e in entries:
        summary = e.task[:55] + ("…" if len(e.task) > 55 else "")
        target = f" target={e.target}" if e.target else ""
        lines.append(f"[{e.id}] {e.status:10s}{target} | {e.created_at} | {summary}")
    return "\n".join(lines)


@mcp_tool_registry.register(
    name="get_task_status",
    description="Poll the current status and result preview of a task by task_id.",
    schema={
        "type": "object",
        "properties": {"task_id": {"type": "string"}},
        "required": ["task_id"],
    },
)
async def get_task_status(args: dict[str, object]) -> str:
    entry = _tasks.get(str(args["task_id"]))
    if not entry:
        return f"[error] No task with id '{args['task_id']}'"
    lines: list[str] = [
        f"task_id:    {entry.id}",
        f"status:     {entry.status}",
        f"task:       {entry.task}",
        f"target:     {entry.target or 'none'}",
        f"created_at: {entry.created_at}",
    ]
    if entry.finished_at:
        lines.append(f"finished_at: {entry.finished_at}")
    if entry.status == "done" and entry.result:
        lines.append(f"result (preview):\n{entry.result[:300]}")
    if entry.status == "error":
        lines.append(f"error: {entry.error}")
    if entry.tool_calls:
        lines.append(
            "tools_used: " + ", ".join(str(c["name"]) for c in entry.tool_calls)
        )
    return "\n".join(lines)


@mcp_tool_registry.register(
    name="get_task_result",
    description=(
        "Retrieve the full result of a completed task: final summary, "
        "thinking steps, tool calls and results, and notes snapshot."
    ),
    schema={
        "type": "object",
        "properties": {"task_id": {"type": "string"}},
        "required": ["task_id"],
    },
)
async def get_task_result(args: dict[str, object]) -> str:
    entry = _tasks.get(str(args["task_id"]))
    if not entry:
        return f"[error] No task with id '{args['task_id']}'"
    if entry.status in ("pending", "running"):
        return f"[info] Task {entry.id} is still {entry.status}."

    lines: list[str] = [
        f"task_id:     {entry.id}",
        f"status:      {entry.status}",
        f"task:        {entry.task}",
        f"target:      {entry.target or 'none'}",
        f"scope:       {entry.scope}",
        f"created_at:  {entry.created_at}",
        f"finished_at: {entry.finished_at}",
    ]
    if entry.thinking:
        lines.append("\n[thinking]")
        lines.extend(f"  {t}" for t in entry.thinking)
    if entry.tool_calls:
        lines.append("\n[tool_calls]")
        for c in entry.tool_calls:
            lines.append(f"  {c['name']}({c['arguments']})")
    if entry.tool_results:
        lines.append("\n[tool_results]")
        for r in entry.tool_results:
            if r["success"]:
                lines.append(f"  ✓ {r['tool_name']}: {str(r['result'] or '')[:200]}")
            else:
                lines.append(f"  ✗ {r['tool_name']} [FAILED]: {r['error']}")
    if entry.result:
        lines.append(f"\n[result]\n{entry.result}")
    if entry.notes_snapshot:
        lines.append(f"\n[notes_snapshot]\n{entry.notes_snapshot}")
    if entry.error:
        lines.append(f"\n[error]\n{entry.error}")
    return "\n".join(lines)


@mcp_tool_registry.register(
    name="await_tasks",
    description=(
        "Block until ALL given task_ids have finished (done / error / cancelled). "
        "Polls every 500 ms; returns a one-line summary per task."
    ),
    schema={
        "type": "object",
        "properties": {
            "task_ids": {"type": "array", "items": {"type": "string"}},
            "timeout_seconds": {
                "type": "number",
                "description": "Max wait (default 120)",
            },
        },
        "required": ["task_ids"],
    },
)
async def await_tasks(args: dict[str, object]) -> str:
    task_ids = [str(tid) for tid in args["task_ids"]]  # type: ignore[union-attr]
    timeout = float(args.get("timeout_seconds") or 120)  # type: ignore[arg-type]
    elapsed = 0.0

    while elapsed < timeout:
        if all(
            tid in _tasks and _tasks[tid].status not in ("pending", "running")
            for tid in task_ids
        ):
            break
        await asyncio.sleep(0.5)
        elapsed += 0.5

    lines: list[str] = []
    for tid in task_ids:
        entry = _tasks.get(tid)
        if not entry:
            lines.append(f"[{tid}] NOT FOUND")
        elif entry.status == "done":
            lines.append(
                f"[{tid}] done      | {(entry.result or '')[:120].replace(chr(10), ' ')}"
            )
        elif entry.status == "error":
            lines.append(f"[{tid}] error     | {entry.error}")
        elif entry.status == "cancelled":
            lines.append(f"[{tid}] cancelled")
        else:
            lines.append(f"[{tid}] {entry.status} (timed out after {timeout}s)")
    return "\n".join(lines)


# ===========================================================================
# GROUP: TASK CONTROL
# ===========================================================================


@mcp_tool_registry.register(
    name="cancel_task",
    description="Cancel a running or pending task.",
    schema={
        "type": "object",
        "properties": {"task_id": {"type": "string"}},
        "required": ["task_id"],
    },
)
async def cancel_task(args: dict[str, object]) -> str:
    entry = _tasks.get(str(args["task_id"]))
    if not entry:
        return f"[error] No task with id '{args['task_id']}'"
    if entry.status not in ("pending", "running"):
        return f"[info] Task {entry.id} is already '{entry.status}', cannot cancel."
    entry.status = "cancelled"
    entry.finished_at = datetime.utcnow().isoformat()
    _log("info", f"cancel_task [{entry.id}]")
    return f"[ok] Task {entry.id} marked for cancellation."


# ===========================================================================
# GROUP: TOOL MANAGEMENT
# ===========================================================================


@mcp_tool_registry.register(
    name="list_tools",
    description="List all tools available to tasks, expanding any RAG optimizer.",
    schema={"type": "object", "properties": {}, "required": []},
)
async def list_tools(args: dict[str, object]) -> str:
    if not _primary_agent:
        return "[error] Primary agent not initialised."
    tools = _primary_agent.get_tools()
    if not tools:
        return "No tools registered."
    lines = [f"{t.name}: {getattr(t, 'description', '')}" for t in tools]
    return f"Total tools: {len(lines)}\n" + "\n".join(lines)


@mcp_tool_registry.register(
    name="enable_tool",
    description="Enable a tool on the primary agent by name.",
    schema={
        "type": "object",
        "properties": {"tool_name": {"type": "string"}},
        "required": ["tool_name"],
    },
)
async def enable_tool(args: dict[str, object]) -> str:
    if not _primary_agent:
        return "[error] Primary agent not initialised."
    name = str(args["tool_name"])
    for tool in _primary_agent.tools:
        if tool.name == name:
            tool.enabled = True
            _log("info", f"enable_tool: {name}")
            return f"[ok] Tool '{name}' enabled."
    return f"[error] Tool '{name}' not found."


@mcp_tool_registry.register(
    name="disable_tool",
    description="Disable a tool on the primary agent by name.",
    schema={
        "type": "object",
        "properties": {"tool_name": {"type": "string"}},
        "required": ["tool_name"],
    },
)
async def disable_tool(args: dict[str, object]) -> str:
    if not _primary_agent:
        return "[error] Primary agent not initialised."
    name = str(args["tool_name"])
    for tool in _primary_agent.tools:
        if tool.name == name:
            tool.enabled = False
            _log("info", f"disable_tool: {name}")
            return f"[ok] Tool '{name}' disabled."
    return f"[error] Tool '{name}' not found."


# ===========================================================================
# GROUP: CONVERSATION HISTORY
# ===========================================================================


@mcp_tool_registry.register(
    name="get_conversation_history",
    description=(
        "Return the conversation history of a task by task_id, "
        "or the primary agent if omitted."
    ),
    schema={
        "type": "object",
        "properties": {
            "task_id": {"type": "string", "description": "Omit for primary agent"},
            "limit": {
                "type": "integer",
                "description": "Max messages, most recent first (default 20)",
            },
        },
        "required": [],
    },
)
async def get_conversation_history(args: dict[str, object]) -> str:
    if "task_id" in args:
        entry = _tasks.get(str(args["task_id"]))
        if not entry:
            return f"[error] No task with id '{args['task_id']}'"
        agent = entry.agent
    else:
        if not _primary_agent:
            return "[error] Primary agent not initialised."
        agent = _primary_agent

    history = agent.conversation_history[-int(args.get("limit") or 20) :]  # type: ignore[arg-type]
    if not history:
        return "No conversation history."

    lines: list[str] = []
    for msg in history:
        role = msg.role.upper()
        content = (msg.content or "").strip()[:200]
        if msg.tool_calls:
            lines.append(
                f"[{role}] (tool_calls: {', '.join(c.name for c in msg.tool_calls)}) {content}"
            )
        elif msg.tool_results:
            lines.append(
                f"[{role}] (tool_results: {', '.join(r.tool_name for r in msg.tool_results)})"
            )
        else:
            lines.append(f"[{role}] {content}")
    return "\n".join(lines)


@mcp_tool_registry.register(
    name="reset_conversation",
    description="Reset the conversation history of a task, or the primary agent if omitted.",
    schema={
        "type": "object",
        "properties": {
            "task_id": {"type": "string", "description": "Omit for primary agent"},
        },
        "required": [],
    },
)
async def reset_conversation(args: dict[str, object]) -> str:
    if "task_id" in args:
        entry = _tasks.get(str(args["task_id"]))
        if not entry:
            return f"[error] No task with id '{args['task_id']}'"
        entry.agent.reset()
        _log("info", f"reset_conversation [{args['task_id']}]")
        return f"[ok] Task {args['task_id']} conversation reset."
    if not _primary_agent:
        return "[error] Primary agent not initialised."
    _primary_agent.reset()
    _log("info", "reset_conversation [primary]")
    return "[ok] Primary agent conversation reset."


# ===========================================================================
# GROUP: MEMORY
# ===========================================================================


@mcp_tool_registry.register(
    name="store_memory",
    description="Persist a key-value pair to the in-memory store.",
    schema={
        "type": "object",
        "properties": {
            "key": {"type": "string"},
            "value": {"type": "string"},
        },
        "required": ["key", "value"],
    },
)
async def store_memory(args: dict[str, object]) -> str:
    key = str(args["key"])
    _memory[key] = {
        "value": str(args["value"]),
        "stored_at": datetime.utcnow().isoformat(),
    }
    return f"[ok] Stored key '{key}'"


@mcp_tool_registry.register(
    name="retrieve_memory",
    description=(
        "Retrieve a value by exact key, search by substring, "
        "or list all keys (omit both arguments)."
    ),
    schema={
        "type": "object",
        "properties": {
            "key": {"type": "string"},
            "search": {"type": "string"},
        },
        "required": [],
    },
)
async def retrieve_memory(args: dict[str, object]) -> str:
    if "key" in args:
        mem = _memory.get(str(args["key"]))
        if not mem:
            return f"[error] Key '{args['key']}' not found"
        return (
            f"key: {args['key']}\nvalue: {mem['value']}\nstored_at: {mem['stored_at']}"
        )
    if "search" in args:
        matches = {
            k: v for k, v in _memory.items() if str(args["search"]).lower() in k.lower()
        }
        return (
            "\n".join(f"{k}: {v['value'][:80]}" for k, v in matches.items())
            or f"No keys matching '{args['search']}'"
        )
    return (
        "\n".join(f"{k}: {v['value'][:80]}" for k, v in _memory.items())
        or "Memory is empty."
    )


@mcp_tool_registry.register(
    name="clear_memory",
    description="Delete a specific memory key, or wipe all memory with scope='all'.",
    schema={
        "type": "object",
        "properties": {
            "key": {"type": "string"},
            "scope": {
                "type": "string",
                "description": "Pass 'all' to clear everything",
            },
        },
        "required": [],
    },
)
async def clear_memory(args: dict[str, object]) -> str:
    if "key" in args:
        key = str(args["key"])
        if key not in _memory:
            return f"[error] Key '{key}' not found"
        del _memory[key]
        return f"[ok] Deleted '{key}'"
    if args.get("scope") == "all":
        count = len(_memory)
        _memory.clear()
        return f"[ok] Cleared {count} entries"
    return "[error] Provide 'key' or scope='all'."


# ===========================================================================
# GROUP: OBSERVABILITY
# ===========================================================================


@mcp_tool_registry.register(
    name="get_logs",
    description="Return recent execution logs. Optionally filter by level: info | warning | error.",
    schema={
        "type": "object",
        "properties": {
            "level": {"type": "string"},
            "limit": {"type": "integer", "description": "Max lines (default 50)"},
        },
        "required": [],
    },
)
async def get_logs(args: dict[str, object]) -> str:
    entries = list(reversed(_logs))
    if "level" in args:
        entries = [e for e in entries if e["level"] == str(args["level"])]
    entries = entries[: int(args.get("limit") or 50)]  # type: ignore[arg-type]
    if not entries:
        return "No log entries found."
    return "\n".join(
        f"[{e['ts']}] [{e['level'].upper():7s}] {e['message']}" for e in entries
    )


@mcp_tool_registry.register(
    name="get_metrics",
    description="Return runtime metrics: task counts, success rate, total tool calls, memory and log sizes.",
    schema={"type": "object", "properties": {}, "required": []},
)
async def get_metrics(args: dict[str, object]) -> str:
    total = len(_tasks)
    done = sum(1 for e in _tasks.values() if e.status == "done")
    errors = sum(1 for e in _tasks.values() if e.status == "error")
    canc = sum(1 for e in _tasks.values() if e.status == "cancelled")
    active = sum(1 for e in _tasks.values() if e.status in ("pending", "running"))
    return "\n".join(
        [
            f"total_tasks:      {total}",
            f"active:           {active}",
            f"completed:        {done}",
            f"errors:           {errors}",
            f"cancelled:        {canc}",
            f"success_rate:     {f'{done / total * 100:.1f}%' if total else 'n/a'}",
            f"total_tool_calls: {sum(len(e.tool_calls) for e in _tasks.values())}",
            f"memory_keys:      {len(_memory)}",
            f"log_entries:      {len(_logs)}",
        ]
    )
