"""Base agent class for PentestAgent."""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, AsyncIterator, List, Optional

from ..config.constants import AGENT_MAX_ITERATIONS
from ..workspaces import validation
from ..workspaces.manager import WorkspaceManager
from .state import AgentState, AgentStateManager

if TYPE_CHECKING:
    from ..llm import LLM
    from ..runtime import Runtime
    from ..tools import Tool

_TOOL_LIMIT = 128


@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""

    id: str
    name: str
    arguments: dict

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "arguments": self.arguments}

    @classmethod
    def from_dict(cls, data: dict) -> "ToolCall":
        return cls(
            id=data["id"], name=data["name"], arguments=data.get("arguments", {})
        )


@dataclass
class ToolResult:
    """Result from a tool execution."""

    tool_call_id: str
    tool_name: str
    result: Optional[str] = None
    error: Optional[str] = None
    success: bool = True
    suggested_tools: Optional[List["Tool"]] = None

    def to_dict(self) -> dict:
        return {
            "tool_call_id": self.tool_call_id,
            "tool_name": self.tool_name,
            "result": self.result,
            "error": self.error,
            "success": self.success,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ToolResult":
        return cls(
            tool_call_id=data["tool_call_id"],
            tool_name=data["tool_name"],
            result=data.get("result"),
            error=data.get("error"),
            success=data.get("success", True),
        )


@dataclass
class AgentMessage:
    """A message in the agent conversation."""

    role: str  # "user", "assistant", "tool_result", "system"
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    tool_results: Optional[List[ToolResult]] = None
    metadata: dict = field(default_factory=dict)
    usage: Optional[dict] = None  # Token usage from LLM response

    def to_llm_format(self) -> dict:
        """Convert to LLM message format."""
        import json

        msg = {"role": self.role, "content": self.content}

        if self.tool_calls:
            msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": (
                            json.dumps(tc.arguments)
                            if isinstance(tc.arguments, dict)
                            else tc.arguments
                        ),
                    },
                }
                for tc in self.tool_calls
            ]

        return msg

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "tool_calls": (
                [tc.to_dict() for tc in self.tool_calls] if self.tool_calls else None
            ),
            "tool_results": (
                [tr.to_dict() for tr in self.tool_results]
                if self.tool_results
                else None
            ),
            "metadata": self.metadata,
            "usage": self.usage,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AgentMessage":
        tool_calls = None
        if data.get("tool_calls"):
            tool_calls = [ToolCall.from_dict(tc) for tc in data["tool_calls"]]
        tool_results = None
        if data.get("tool_results"):
            tool_results = [ToolResult.from_dict(tr) for tr in data["tool_results"]]
        return cls(
            role=data["role"],
            content=data.get("content", ""),
            tool_calls=tool_calls,
            tool_results=tool_results,
            metadata=data.get("metadata", {}),
            usage=data.get("usage"),
        )


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(
        self,
        llm: "LLM",
        tools: List["Tool"],
        runtime: "Runtime",
        max_iterations: int = AGENT_MAX_ITERATIONS,
        **kwargs,
    ):
        """
        Initialize base agent state.

        Args:
            llm: LLM instance used for generation
            tools: Available tool list
            runtime: Runtime used for tool execution
            max_iterations: Safety limit for iterations
        """
        self.llm = llm
        self.tools = tools
        self.runtime = runtime
        self.max_iterations = max_iterations

        self.suggested_tools: List[Tool] = []

        # Agent runtime state
        self.state_manager = AgentStateManager()
        self.conversation_history: List[AgentMessage] = []

        # Task planning structure (used by finish tool)
        try:
            from ..tools.finish import TaskPlan

            self._task_plan = TaskPlan()
        except Exception as e:
            import logging

            logging.getLogger(__name__).exception("Failed importing TaskPlan: %s", e)
            try:
                from ..interface.notifier import notify

                notify("warning", f"Failed to import TaskPlan: {e}")
            except Exception:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about TaskPlan import failure"
                )

            # Fallback simple plan structure
            class _SimplePlan:
                def __init__(self):
                    self.steps = []
                    self.original_request = ""

                def clear(self):
                    self.steps.clear()

                def is_complete(self):
                    return True

                def has_failure(self):
                    return False

            self._task_plan = _SimplePlan()

        # Expose plan to runtime so tools like `finish` can access it
        try:
            self.runtime.plan = self._task_plan
        except Exception as e:
            import logging

            logging.getLogger(__name__).exception(
                "Failed to attach plan to runtime: %s", e
            )
            try:
                from ..interface.notifier import notify

                notify("warning", f"Failed to attach plan to runtime: {e}")
            except Exception:
                logging.getLogger(__name__).exception(
                    "Failed to notify operator about runtime plan attach failure"
                )

        # Ensure agent starts idle
        self.state_manager.transition_to(AgentState.IDLE)

    @abstractmethod
    def get_system_prompt(self, mode: str = "agent") -> str:
        """Return the system prompt for this agent.

        Args:
            mode: 'agent' for autonomous mode, 'assist' for single-shot assist mode
        """
        pass

    async def agent_loop(self, initial_message: str) -> AsyncIterator[AgentMessage]:
        """
        Main agent execution loop.

        Starts a new task session, resetting previous state and history.

        Simple control flow:
        - Tool calls: Execute tools, continue loop
        - Text response (no tools): Done
        - Max iterations reached: Force stop with warning

        Args:
            initial_message: The initial user message to process

        Yields:
            AgentMessage objects as the agent processes
        """
        # Always reset for a new agent loop task to ensure clean state
        self.reset()
        self._task_plan.clear()

        self.state_manager.transition_to(AgentState.THINKING)
        self.conversation_history.append(
            AgentMessage(role="user", content=initial_message)
        )

        async for msg in self._run_loop():
            yield msg

    async def continue_conversation(
        self, user_message: str
    ) -> AsyncIterator[AgentMessage]:
        """
        Continue the conversation with a new user message.

        Args:
            user_message: The new user message

        Yields:
            AgentMessage objects as the agent processes
        """
        self.conversation_history.append(
            AgentMessage(role="user", content=user_message)
        )
        self.state_manager.transition_to(AgentState.THINKING)

        async for msg in self._run_loop():
            yield msg

    async def wake_up(self, mode: str = "agent") -> AsyncIterator[AgentMessage]:
        """Re-enter processing to handle a pending push notification.

        The notification has already been injected into conversation_history by
        the watcher.  Dispatches to the loop matching the active TUI mode so
        the agent resumes in the same style it was using before going idle:
          - "assist"   → single LLM call + one tool round
          - "interact" → streaming chat loop until natural stop
          - "agent"    → autonomous _run_loop() (no plan reset)
        """
        self.state_manager.transition_to(AgentState.THINKING)
        if mode == "assist":
            async for msg in self._assist_loop():
                yield msg
        elif mode == "interact":
            async for msg in self._interact_loop():
                yield msg
        else:
            async for msg in self._run_loop():
                yield msg

    async def _run_loop(self) -> AsyncIterator[AgentMessage]:
        """
        Core agent loop logic - shared by agent_loop, continue_conversation and wake_up.

        Termination conditions:
        1. finish tool is called AND plan complete -> clean exit with summary
        2. max_iterations reached -> forced exit with warning
        3. error -> exit with error state

        Text responses WITHOUT tool calls are treated as "thinking out loud"
        and do NOT terminate the loop. This prevents premature stopping.

        The loop enforces plan completion before allowing finish.

        Yields:
            AgentMessage objects as the agent processes
        """
        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1
            agent_tools = [t for t in self.tools if t.enabled]

            # ITERATION 1: Force plan creation (loop-enforced, not prompt-based)
            if iteration == 1 and len(self._task_plan.steps) == 0:
                plan_msg = await self._auto_generate_plan()
                if plan_msg:
                    yield plan_msg

            response = await self.llm.generate(
                system_prompt=self.get_system_prompt(),
                messages=self._format_messages_for_llm(),
                tools=agent_tools
                + self.suggested_tools,  # Only, enabled tools + suggested tools.
            )

            # Case 1: Empty response (Error)
            if not response.tool_calls and not response.content:
                stuck_msg = AgentMessage(
                    role="assistant",
                    content="Agent returned empty response. Exiting gracefully.",
                    metadata={"empty_response": True},
                )
                self.conversation_history.append(stuck_msg)
                yield stuck_msg
                self.state_manager.transition_to(AgentState.COMPLETE)
                return

            # Case 2: Thinking / Intermediate Output (Content but no tools)
            if not response.tool_calls:
                thinking_msg = AgentMessage(
                    role="assistant",
                    content=response.content,
                    usage=response.usage,
                    metadata={"intermediate": True},
                )
                self.conversation_history.append(thinking_msg)
                yield thinking_msg
                continue

            # Case 3: Tool Execution
            # Build tool calls list
            tool_calls = [
                ToolCall(
                    id=tc.id if hasattr(tc, "id") else str(i),
                    name=(
                        tc.function.name
                        if hasattr(tc, "function")
                        else tc.get("name", "")
                    ),
                    arguments=self._parse_arguments(tc),
                )
                for i, tc in enumerate(response.tool_calls)
            ]

            # Execute tools
            self.state_manager.transition_to(AgentState.EXECUTING)

            # Yield thinking message if content exists (before execution)
            if response.content:
                thinking_msg = AgentMessage(
                    role="assistant",
                    content=response.content,
                    usage=response.usage,
                    metadata={"intermediate": True},
                )
                yield thinking_msg

            tool_results = await self._execute_tools(response.tool_calls)

            for tool_result in tool_results:
                # If there are suggested tools to inject (from RAG optimizer, inject them)
                if tool_result.suggested_tools:
                    self.suggested_tools += (
                        tool_result.suggested_tools
                    )  # The suggested tools list is overwritten everytime that the RAG optimizer is called
                    self.deduplicate_suggested_tools()  # Deduplicate

            # Purge excess suggested tools if total exceeds 128
            total_tools = len(agent_tools) + len(self.suggested_tools)
            if total_tools > _TOOL_LIMIT:
                allowed_suggested = max(0, _TOOL_LIMIT - len(agent_tools))
                self.suggested_tools = (
                    self.suggested_tools[-allowed_suggested:]
                    if allowed_suggested > 0
                    else []
                )

            # Record in history
            assistant_msg = AgentMessage(
                role="assistant",
                content=response.content or "",
                tool_calls=tool_calls,
                usage=response.usage,
            )
            self.conversation_history.append(assistant_msg)

            tool_result_msg = AgentMessage(
                role="tool_result", content="", tool_results=tool_results
            )
            self.conversation_history.append(tool_result_msg)

            # Yield results for display update immediately
            display_msg = AgentMessage(
                role="assistant",
                content="",  # Suppress content here as it was already yielded as thinking
                tool_calls=tool_calls,
                tool_results=tool_results,
                usage=response.usage,
            )
            yield display_msg

            # Check for plan failure (Tactical Replanning)
            if (
                hasattr(self._task_plan, "has_failure")
                and self._task_plan.has_failure()
            ):
                # Find the failed step
                failed_step = None
                for s in self._task_plan.steps:
                    if s.status == "fail":
                        failed_step = s
                        break

                if failed_step:
                    replan_msg = await self._replan(failed_step)
                    if replan_msg:
                        self.conversation_history.append(replan_msg)
                        yield replan_msg

                        # Check if replan indicated impossibility
                        if replan_msg.metadata.get("replan_impossible"):
                            self.state_manager.transition_to(AgentState.COMPLETE)
                            return

                        continue

            # Check if plan is now complete
            if self._task_plan.is_complete():
                # All steps done - generate final summary
                summary_response = await self.llm.generate(
                    system_prompt="You are a helpful assistant. Provide a brief, clear summary of what was accomplished.",
                    messages=self._format_messages_for_llm(),
                    tools=[
                        t for t in self.tools if t.enabled
                    ],  # Must provide tools if history contains tool calls
                )

                completion_msg = AgentMessage(
                    role="assistant",
                    content=summary_response.content or "Task complete.",
                    usage=summary_response.usage,
                    metadata={"task_complete": True},
                )
                self.conversation_history.append(completion_msg)
                yield completion_msg
                self.state_manager.transition_to(AgentState.COMPLETE)
                return

            self.state_manager.transition_to(AgentState.THINKING)

        # Max iterations reached - force stop
        warning_msg = AgentMessage(
            role="assistant",
            content=f"[!] Reached maximum iterations ({self.max_iterations}). Stopping to prevent infinite loop. You can continue the conversation if needed.",
            metadata={"max_iterations_reached": True},
        )
        self.conversation_history.append(warning_msg)
        yield warning_msg
        self.state_manager.transition_to(AgentState.COMPLETE)

    def _format_messages_for_llm(self) -> List[dict]:
        """Format conversation history for LLM."""
        messages = []

        for msg in self.conversation_history:
            if msg.role == "tool_result" and msg.tool_results:
                # Format tool results as tool response messages
                for result in msg.tool_results:
                    messages.append(
                        {
                            "role": "tool",
                            "content": (
                                result.result
                                if result.success
                                else f"Error: {result.error}"
                            ),
                            "tool_call_id": result.tool_call_id,
                        }
                    )
            else:
                messages.append(msg.to_llm_format())

        return messages

    def _parse_arguments(self, tool_call: Any) -> dict:
        """Parse tool call arguments."""
        import json

        if hasattr(tool_call, "function"):
            args = tool_call.function.arguments
        elif isinstance(tool_call, dict):
            args = tool_call.get("arguments", {})
        else:
            args = {}

        if isinstance(args, str):
            try:
                return json.loads(args)
            except json.JSONDecodeError:
                return {"raw": args}
        return args

    async def _execute_single(self, i: int, call: Any) -> ToolResult:
        """Execute a single tool call and return the result."""
        # Extract tool call id, name and arguments
        if hasattr(call, "id"):
            tool_call_id = call.id
        elif isinstance(call, dict) and "id" in call:
            tool_call_id = call["id"]
        else:
            tool_call_id = f"call_{i}"

        if hasattr(call, "function"):
            name = call.function.name
            arguments = self._parse_arguments(call)
        elif isinstance(call, dict):
            name = call.get("name", "")
            arguments = call.get("arguments", {})
        else:
            return ToolResult(
                tool_call_id=tool_call_id,
                tool_name="unknown",
                error="Malformed tool call: missing name or function attribute",
                success=False,
            )

        tool = self._find_tool(name)

        if tool:
            try:
                wm = WorkspaceManager()
                active = wm.get_active()

                candidates = validation.gather_candidate_targets(arguments)
                out_of_scope = []
                if active:
                    allowed = wm.list_targets(active)
                    for c in candidates:
                        try:
                            if not validation.is_target_in_scope(c, allowed):
                                out_of_scope.append(c)
                        except Exception as e:
                            import logging

                            logging.getLogger(__name__).exception(
                                "Error validating candidate target %s: %s", c, e
                            )
                            out_of_scope.append(c)

                if active and out_of_scope:
                    return ToolResult(
                        tool_call_id=tool_call_id,
                        tool_name=name,
                        error=(
                            f"Out-of-scope target(s): {out_of_scope} - operator confirmation required. "
                            "Set workspace targets with /target or run tool manually."
                        ),
                        success=False,
                    )
                else:
                    if tool.name == "terminal" and name != "terminal":
                        if isinstance(arguments, dict) and "command" in arguments:
                            terminal_args = arguments
                        else:
                            cmd_parts = [name]
                            if isinstance(arguments, dict):
                                for k in (
                                    "target",
                                    "host",
                                    "hosts",
                                    "hosts_list",
                                    "hosts[]",
                                ):
                                    if k in arguments:
                                        v = arguments[k]
                                        if isinstance(v, (list, tuple)):
                                            cmd_parts.extend([str(x) for x in v])
                                        else:
                                            cmd_parts.append(str(v))
                                for k, v in arguments.items():
                                    if k in (
                                        "target",
                                        "host",
                                        "hosts",
                                        "hosts_list",
                                        "hosts[]",
                                    ):
                                        continue
                                    if v is True:
                                        cmd_parts.append(f"--{k}")
                                    elif v is False or v is None:
                                        continue
                                    elif isinstance(v, (list, tuple)):
                                        cmd_parts.extend([str(x) for x in v])
                                    else:
                                        cmd_parts.append(str(v))
                            elif isinstance(arguments, (list, tuple)):
                                cmd_parts.extend([str(x) for x in arguments])
                            else:
                                cmd_parts.append(str(arguments))

                            terminal_args = {"command": " ".join(cmd_parts)}

                        result = await tool.execute(terminal_args, self.runtime)
                    else:
                        result = await tool.execute(arguments, self.runtime)

                    # Check if the called tool is a MCP RAG Optimizer to obtain the new suggested tools

                    suggested_tools = None

                    if tool.metadata.get("is_rag_optimizer", False):
                        suggested_tools = tool.metadata.get("top_k_tools", {}).get(
                            "retrieved_top_k_tools", None
                        )

                    return ToolResult(
                        tool_call_id=tool_call_id,
                        tool_name=name,
                        result=result,
                        success=True,
                        suggested_tools=suggested_tools,
                    )

            except Exception as e:
                import logging

                logging.getLogger(__name__).exception(
                    "Error executing tool %s: %s", name, e
                )
                try:
                    from ..interface.notifier import notify

                    notify("warning", f"Tool execution failed ({name}): {e}")
                except Exception:
                    logging.getLogger(__name__).exception(
                        "Failed to notify operator about tool execution failure"
                    )
                return ToolResult(
                    tool_call_id=tool_call_id,
                    tool_name=name,
                    error=str(e),
                    success=False,
                )
        else:
            return ToolResult(
                tool_call_id=tool_call_id,
                tool_name=name,
                error=f"Tool '{name}' not found",
                success=False,
            )

    async def _execute_tools(self, tool_calls: List[Any]) -> List[ToolResult]:
        """Execute tool calls concurrently and return all results."""
        tasks = [
            asyncio.ensure_future(self._execute_single(i, call))
            for i, call in enumerate(tool_calls)
        ]
        return list(await asyncio.gather(*tasks))

    def _find_tool(self, name: str) -> Optional["Tool"]:
        """
        Find a tool by name.

        Args:
            name: The tool name to find

        Returns:
            The Tool if found, None otherwise
        """
        for tool in self.tools + self.suggested_tools:
            if tool.name == name:
                return tool
        # Fallback: if tool not found, attempt to use a generic terminal tool
        # for commands. Some LLMs may emit semantic tool names (e.g. "network_scan")
        # instead of the actual registered tool name. Use the `terminal` tool
        # as a best-effort fallback when available.
        for tool in self.tools:
            if tool.name == "terminal":
                return tool
        return None

    def _can_finish(self) -> tuple[bool, str]:
        """Check if the agent can finish based on plan completion."""
        if len(self._task_plan.steps) == 0:
            return True, "No plan exists"

        pending = self._task_plan.get_pending_steps()
        if pending:
            pending_desc = ", ".join(
                f"Step {s.id}: {s.description}" for s in pending[:3]
            )
            more = f" (+{len(pending) - 3} more)" if len(pending) > 3 else ""
            return False, f"Incomplete: {pending_desc}{more}"

        return True, "All steps complete"

    async def _auto_generate_plan(self) -> Optional[AgentMessage]:
        """
        Automatically generate a plan from the user's request (loop-enforced).

        This is called on iteration 1 to force plan creation before any tool execution.
        Uses function calling for reliable structured output.

        Returns:
            AgentMessage with plan display, or None if generation fails
        """
        from ..tools.finish import PlanStep
        from ..tools.registry import Tool, ToolSchema

        # Get the user's original request (last message)
        user_request = ""
        for msg in reversed(self.conversation_history):
            if msg.role == "user":
                user_request = msg.content
                break

        if not user_request:
            return None  # No request to plan

        # Create a temporary tool for plan generation (function calling)
        plan_generator_tool = Tool(
            name="create_plan",
            description="Create a step-by-step plan for the task. Call this with the steps needed.",
            schema=ToolSchema(
                properties={
                    "steps": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of actionable steps (one tool action each)",
                    },
                },
                required=["steps"],
            ),
            execute_fn=lambda args, runtime: None,  # Dummy - we parse args directly
            category="planning",
        )

        plan_prompt = f"""Break this request into minimal, actionable steps.

Request: {user_request}

Guidelines:
- Be concise (typically 2-4 steps)
- One tool action per step
- Don't include waiting/loading (handled automatically)
- Do NOT include a "finish", "complete", or "verify" step (handled automatically)

Call the create_plan tool with your steps."""

        try:
            response = await self.llm.generate(
                system_prompt="You are a task planning assistant. Always use the create_plan tool.",
                messages=[{"role": "user", "content": plan_prompt}],
                tools=[plan_generator_tool],
            )

            # Extract steps from tool call arguments
            steps = []
            if response.tool_calls:
                for tc in response.tool_calls:
                    args = self._parse_arguments(tc)
                    if args.get("steps"):
                        steps = args["steps"]
                        break

            # Fallback: if LLM didn't provide steps, create single-step plan
            if not steps:
                steps = [user_request]

            # Create the plan
            self._task_plan.original_request = user_request
            self._task_plan.steps = [
                PlanStep(id=i + 1, description=str(step).strip())
                for i, step in enumerate(steps)
            ]

            # Add a system message showing the generated plan
            plan_display = ["Plan:"]
            for step in self._task_plan.steps:
                plan_display.append(f"  {step.id}. {step.description}")

            plan_msg = AgentMessage(
                role="assistant",
                content="\n".join(plan_display),
                metadata={"auto_plan": True},
                usage=response.usage,
            )
            self.conversation_history.append(plan_msg)
            return plan_msg

        except Exception as e:
            # Plan generation failed - create fallback single-step plan
            self._task_plan.original_request = user_request
            self._task_plan.steps = [PlanStep(id=1, description=user_request)]

            error_msg = AgentMessage(
                role="assistant",
                content=f"Plan generation failed: {str(e)}\nUsing fallback: treating request as single step.",
                metadata={"auto_plan_failed": True},
            )
            self.conversation_history.append(error_msg)
            return error_msg
            return error_msg

    async def _replan(self, failed_step: Any) -> Optional[AgentMessage]:
        """
        Handle plan failure by generating a new plan (Tactical Replanning).
        """
        from ..tools.finish import PlanStep
        from ..tools.registry import Tool, ToolSchema

        # 1. Archive current plan (log it)
        old_plan_str = "\n".join(
            [f"{s.id}. {s.description} ({s.status})" for s in self._task_plan.steps]
        )

        # 2. Generate new plan
        # Create a temporary tool for plan generation
        plan_generator_tool = Tool(
            name="create_plan",
            description="Create a NEW step-by-step plan. Call this with the steps needed.",
            schema=ToolSchema(
                properties={
                    "feasible": {
                        "type": "boolean",
                        "description": "Can the task be completed with a new plan? Set false if impossible/out-of-scope.",
                    },
                    "steps": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of actionable steps (required if feasible=true).",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the new plan OR reason why it's impossible.",
                    },
                },
                required=["feasible", "reason"],
            ),
            execute_fn=lambda args, runtime: None,
            category="planning",
        )

        replan_prompt = f"""The previous plan failed at step {failed_step.id}.

Failed Step: {failed_step.description}
Reason: {failed_step.result}

Previous Plan:
{old_plan_str}

Original Request: {self._task_plan.original_request}

Task: Generate a NEW plan (v2) that addresses this failure.
- If the failure invalidates the entire approach, try a different tactical approach.
- If the task is IMPOSSIBLE or OUT OF SCOPE (e.g., requires installing software on a remote target, physical access, or permissions you don't have), set feasible=False.
- Do NOT propose steps that violate standard pentest constraints (no installing agents/services on targets unless exploited).

Call create_plan with the new steps OR feasible=False."""

        try:
            response = await self.llm.generate(
                system_prompt="You are a tactical planning assistant. The previous plan failed. Create a new one or declare it impossible.",
                messages=[{"role": "user", "content": replan_prompt}],
                tools=[plan_generator_tool],
            )

            # Extract steps
            steps = []
            feasible = True
            reason = ""

            if response.tool_calls:
                for tc in response.tool_calls:
                    args = self._parse_arguments(tc)
                    feasible = args.get("feasible", True)
                    reason = args.get("reason", "")
                    if feasible and args.get("steps"):
                        steps = args["steps"]
                    break

            if not feasible:
                return AgentMessage(
                    role="assistant",
                    content=f"Task determined to be infeasible after failure.\nReason: {reason}",
                    metadata={"replan_impossible": True},
                )

            if not steps:
                return None

            # Update plan
            self._task_plan.steps = [
                PlanStep(id=i + 1, description=str(step).strip())
                for i, step in enumerate(steps)
            ]

            # Return message
            plan_display = [f"Plan v2 (Replanned) - {reason}:"]
            for step in self._task_plan.steps:
                plan_display.append(f"  {step.id}. {step.description}")

            return AgentMessage(
                role="assistant",
                content="\n".join(plan_display),
                metadata={"replanned": True},
            )

        except Exception as e:
            return AgentMessage(
                role="assistant",
                content=f"Replanning failed: {str(e)}",
                metadata={"replan_failed": True},
            )

    def reset(self):
        """Reset the agent state for a new conversation."""
        self.state_manager.reset()
        self.conversation_history.clear()

    def add_tools(self, tools: List["Tool"]):
        self.tools.extend(tools)

    def delete_tools(self, tools: List["Tool"]):
        """
        Remove tools from the agent by name.

        Args:
            tools: List of tool names to remove
        """
        self.tools = [
            t for t in self.tools if t.name not in [tool.name for tool in tools]
        ]

    def get_tools(self) -> List["Tool"]:
        retVal: List[Tool] = []
        for tool in self.tools:
            if tool.metadata.get(
                "is_rag_optimizer", False
            ):  # Expand tools if we are using the RAG optimizer, so all the tools are listed (although, the only exposed tool is the RAG optimizer tool)
                suggested_tools = tool.metadata.get("total_tools_indexed", [])
                retVal += suggested_tools
            else:
                retVal.append(tool)
        return retVal

    # Helper function to avoid duplicates
    def deduplicate_suggested_tools(self):
        # Deduplicate the same tools
        seen = set()
        deduped = []
        for tool in self.suggested_tools:
            if id(tool) not in seen:
                seen.add(id(tool))
                deduped.append(tool)
        self.suggested_tools = deduped

    async def _assist_loop(self) -> AsyncIterator[AgentMessage]:
        """Single LLM call + one tool round on the existing conversation history."""
        assist_tools = [t for t in self.tools if t.name != "finish" and t.enabled]

        response = await self.llm.generate(
            system_prompt=self.get_system_prompt(mode="assist"),
            messages=self._format_messages_for_llm(),
            tools=assist_tools + self.suggested_tools,
        )

        if response.tool_calls:
            tool_calls = [
                ToolCall(
                    id=tc.id if hasattr(tc, "id") else str(i),
                    name=(
                        tc.function.name
                        if hasattr(tc, "function")
                        else tc.get("name", "")
                    ),
                    arguments=self._parse_arguments(tc),
                )
                for i, tc in enumerate(response.tool_calls)
            ]

            if response.content:
                thinking_msg = AgentMessage(
                    role="assistant",
                    content=response.content,
                    metadata={"intermediate": True},
                )
                yield thinking_msg

            self.state_manager.transition_to(AgentState.EXECUTING)
            tool_results = await self._execute_tools(response.tool_calls)

            for tool_result in tool_results:
                if tool_result.suggested_tools:
                    self.suggested_tools += tool_result.suggested_tools
                    self.deduplicate_suggested_tools()

            total_tools = len(assist_tools) + len(self.suggested_tools)
            if total_tools > _TOOL_LIMIT:
                allowed_suggested = max(0, _TOOL_LIMIT - len(assist_tools))
                self.suggested_tools = (
                    self.suggested_tools[-allowed_suggested:]
                    if allowed_suggested > 0
                    else []
                )

            assistant_msg = AgentMessage(
                role="assistant", content=response.content or "", tool_calls=tool_calls
            )
            self.conversation_history.append(assistant_msg)
            self.conversation_history.append(
                AgentMessage(role="tool_result", content="", tool_results=tool_results)
            )

            yield AgentMessage(
                role="assistant",
                content="",
                tool_calls=tool_calls,
                tool_results=tool_results,
            )

            result_text = self._format_tool_results(tool_results)
            final_msg = AgentMessage(role="assistant", content=result_text)
            self.conversation_history.append(final_msg)
            yield final_msg
        else:
            assistant_msg = AgentMessage(
                role="assistant", content=response.content or ""
            )
            self.conversation_history.append(assistant_msg)
            yield assistant_msg

        self.state_manager.transition_to(AgentState.COMPLETE)

    async def assist(self, message: str) -> AsyncIterator[AgentMessage]:
        """
        Assist mode - single LLM call, single tool execution if needed.

        Simple flow: LLM responds, optionally calls one tool, returns result.
        No looping, no retries. User can follow up if needed.

        Note: 'finish' tool is excluded - assist mode doesn't need explicit
        termination since it's single-shot by design.

        Args:
            message: The user message to respond to

        Yields:
            AgentMessage objects
        """
        self.state_manager.transition_to(AgentState.THINKING)
        self.conversation_history.append(AgentMessage(role="user", content=message))
        async for msg in self._assist_loop():
            yield msg

    async def _interact_loop(self) -> AsyncIterator[AgentMessage]:
        """Streaming chat loop on the existing conversation history."""
        while True:
            interact_tools = [t for t in self.tools if t.name != "finish" and t.enabled]

            response = await self.llm.generate(
                system_prompt=self.get_system_prompt(mode="interact"),
                messages=self._format_messages_for_llm(),
                tools=interact_tools + self.suggested_tools,
            )

            if response.tool_calls:
                tool_calls = [
                    ToolCall(
                        id=tc.id if hasattr(tc, "id") else str(i),
                        name=(
                            tc.function.name
                            if hasattr(tc, "function")
                            else tc.get("name", "")
                        ),
                        arguments=self._parse_arguments(tc),
                    )
                    for i, tc in enumerate(response.tool_calls)
                ]

                assistant_msg = AgentMessage(
                    role="assistant",
                    content=response.content or "",
                    tool_calls=tool_calls,
                )
                self.conversation_history.append(assistant_msg)
                yield assistant_msg

                self.state_manager.transition_to(AgentState.EXECUTING)

                tasks = [
                    asyncio.ensure_future(self._execute_single(i, tc))
                    for i, tc in enumerate(response.tool_calls)
                ]

                all_tool_results = []
                for coro in asyncio.as_completed(tasks):
                    tool_result = await coro
                    all_tool_results.append(tool_result)

                    if tool_result.suggested_tools:
                        self.suggested_tools += tool_result.suggested_tools
                        self.deduplicate_suggested_tools()

                    yield AgentMessage(
                        role="tool_result",
                        content="",
                        tool_results=[tool_result],
                    )

                total_tools = len(interact_tools) + len(self.suggested_tools)
                if total_tools > _TOOL_LIMIT:
                    allowed_suggested = max(0, _TOOL_LIMIT - len(interact_tools))
                    self.suggested_tools = (
                        self.suggested_tools[-allowed_suggested:]
                        if allowed_suggested > 0
                        else []
                    )

                self.conversation_history.append(
                    AgentMessage(
                        role="tool_result", content="", tool_results=all_tool_results
                    )
                )

            else:
                assistant_msg = AgentMessage(
                    role="assistant", content=response.content or ""
                )
                self.conversation_history.append(assistant_msg)
                yield assistant_msg

            finish_reason = getattr(response, "finish_reason", None)
            if finish_reason in ("length", "stop"):
                break

        self.state_manager.transition_to(AgentState.COMPLETE)

    async def interact(self, message: str) -> AsyncIterator[AgentMessage]:
        """
        Interactive mode

        Args:
            message: The user message to respond to

        Yields:
            AgentMessage objects
        """
        self.state_manager.transition_to(AgentState.THINKING)
        self.conversation_history.append(AgentMessage(role="user", content=message))
        async for msg in self._interact_loop():
            yield msg

    async def run_mcp(self, task: str) -> AsyncIterator["AgentMessage"]:
        """
        MCP autonomous execution loop.

        Purpose-built for programmatic callers (MCP server, orchestrating agents).
        Differences from interact():
        - Uses pa_mcp system prompt (dense, structured, no conversational filler)
        - Never stalls waiting for human confirmation
        - Terminates cleanly on natural stop (finish_reason == 'stop' with no tools)
        - No finish/plan tool dependency — lifecycle owned by the MCP layer
        - Saves findings via notes tool; final message is the structured summary

        Yields AgentMessage objects. The MCP driver (_drive_mcp) maps these to
        AgentEntry fields for retrieval via get_agent_result().

        Args:
            task: The fully-specified task string from the MCP caller.

        Yields:
            AgentMessage objects throughout execution.
        """
        self.reset()
        self.state_manager.transition_to(AgentState.THINKING)
        self.conversation_history.append(AgentMessage(role="user", content=task))

        # Exclude finish tool — MCP layer owns lifecycle, not the agent
        mcp_tools = [t for t in self.tools if t.name != "finish" and t.enabled]

        iteration = 0

        while iteration < self.max_iterations:
            iteration += 1

            response = await self.llm.generate(
                system_prompt=self.get_system_prompt(mode="mcp"),
                messages=self._format_messages_for_llm(),
                tools=mcp_tools + self.suggested_tools,
            )

            # ── finish_reason: break early if LLM signals done or context full ──
            finish_reason = getattr(response, "finish_reason", None)
            if finish_reason == "length":
                break
            elif finish_reason == "stop" and not response.tool_calls:
                pass

            # ── Empty response ────────────────────────────────────────────────
            if not response.tool_calls and not response.content:
                empty_msg = AgentMessage(
                    role="assistant",
                    content="[mcp] Agent returned empty response. Stopping.",
                    metadata={"empty_response": True},
                )
                self.conversation_history.append(empty_msg)
                yield empty_msg
                self.state_manager.transition_to(AgentState.COMPLETE)
                return

            # ── Natural stop: text response with no tool calls ────────────────
            # Unlike interact(), we treat this as DONE — MCP tasks are
            # self-contained. The final text is the structured summary.
            if not response.tool_calls:
                final_msg = AgentMessage(
                    role="assistant",
                    content=response.content or "",
                    usage=response.usage,
                    metadata={"task_complete": True},
                )
                self.conversation_history.append(final_msg)
                yield final_msg
                self.state_manager.transition_to(AgentState.COMPLETE)
                return

            # ── Tool execution ────────────────────────────────────────────────
            self.state_manager.transition_to(AgentState.EXECUTING)

            # Yield thinking content before executing (if present)
            if response.content:
                thinking_msg = AgentMessage(
                    role="assistant",
                    content=response.content,
                    usage=response.usage,
                    metadata={"intermediate": True},
                )
                yield thinking_msg

            tool_calls = [
                ToolCall(
                    id=tc.id if hasattr(tc, "id") else str(i),
                    name=(
                        tc.function.name
                        if hasattr(tc, "function")
                        else tc.get("name", "")
                    ),
                    arguments=self._parse_arguments(tc),
                )
                for i, tc in enumerate(response.tool_calls)
            ]

            tool_results = await self._execute_tools(response.tool_calls)

            # Inject RAG-suggested tools if any tool returned them
            for tool_result in tool_results:
                if tool_result.suggested_tools:
                    self.suggested_tools += tool_result.suggested_tools
                    self.deduplicate_suggested_tools()

            # Enforce tool cap
            total_tools = len(mcp_tools) + len(self.suggested_tools)
            if total_tools > _TOOL_LIMIT:
                allowed = max(0, _TOOL_LIMIT - len(mcp_tools))
                self.suggested_tools = (
                    self.suggested_tools[-allowed:] if allowed > 0 else []
                )

            # Record in conversation history
            assistant_msg = AgentMessage(
                role="assistant",
                content=response.content or "",
                tool_calls=tool_calls,
                usage=response.usage,
            )
            self.conversation_history.append(assistant_msg)
            self.conversation_history.append(
                AgentMessage(role="tool_result", content="", tool_results=tool_results)
            )

            # Yield for the MCP driver to record
            yield AgentMessage(
                role="assistant",
                content="",
                tool_calls=tool_calls,
                tool_results=tool_results,
                usage=response.usage,
            )

            self.state_manager.transition_to(AgentState.THINKING)

        # ── Max iterations reached ────────────────────────────────────────────
        # Ask the LLM for a partial-results summary before stopping
        try:
            summary_response = await self.llm.generate(
                system_prompt=(
                    "You are a penetration testing assistant. "
                    "The task ran out of iterations before completing. "
                    "Summarize what was accomplished and what remains."
                ),
                messages=self._format_messages_for_llm(),
                tools=[],  # No tools — we need text output, not tool calls
            )
            summary_content = (
                summary_response.content
                or "Max iterations reached — no summary available."
            )
        except Exception:
            summary_content = f"[mcp] Max iterations ({self.max_iterations}) reached. Partial results in notes."

        max_iter_msg = AgentMessage(
            role="assistant",
            content=summary_content,
            metadata={"max_iterations_reached": True, "task_complete": True},
        )
        self.conversation_history.append(max_iter_msg)
        yield max_iter_msg
        self.state_manager.transition_to(AgentState.COMPLETE)

    def _format_tool_results(self, results: List[ToolResult]) -> str:
        """Format tool results as a simple response."""
        parts = []
        for r in results:
            if r.success:
                parts.append(r.result or "Done.")
            else:
                parts.append(f"Error: {r.error}")
        return "\n".join(parts)

    def get_state(self) -> AgentState:
        return self.state_manager.current_state

    def cleanup_after_cancel(self) -> None:
        """
        Clean up agent state after a cancellation.

        Removes the cancelled request and any pending tool calls from
        conversation history to prevent stale responses from contaminating
        the next conversation.
        """
        # Remove incomplete messages from the end of conversation
        while self.conversation_history:
            last_msg = self.conversation_history[-1]
            # Remove assistant message with tool calls (incomplete tool execution)
            if last_msg.role == "assistant" and last_msg.tool_calls:
                self.conversation_history.pop()
            # Remove orphaned tool_result messages
            elif last_msg.role == "tool":
                self.conversation_history.pop()
            # Remove the user message that triggered the cancelled request
            elif last_msg.role == "user":
                self.conversation_history.pop()
                break  # Stop after removing the user message
            else:
                break

        # Reset state to idle
        self.state_manager.transition_to(AgentState.IDLE)
