"""
Task Classification — Unified Verification Check (Step 10)
===========================================================

Standalone module for classifying tasks before execution.  The unified
:func:`classify_task` function replaces the former two-step approach
(Step 10a: ambiguous, Step 10b: impossible) with a single LLM call that
evaluates **two axes** drawn from the error taxonomy:

  1. **Task Ambiguity** (Category 7)  — underspecified, ambiguous, unsafe
  2. **Invalid Task**   (Category 8)  — impossible, illegal, NSFW, RAI

Only the task description, starting URL/app, and current date are
required — no screenshots, action history, or rubric context.

Usage
-----
Via :class:`TaskAgent` (recommended)::

    from webeval.rubric_agent.task_classification import (
        TaskAgent, TaskAgentConfig,
    )

    agent = TaskAgent(TaskAgentConfig(client=my_llm_client))
    # Standalone (no DataPoint):
    result = await agent.classify("Book a flight", "https://...", apps=["Google Flights"])
    # With a DataPoint via RunContext:
    results = await agent.run(run_context)

Via bare function::

    from webeval.rubric_agent.task_classification import classify_task
    result = await classify_task("Book a flight", "https://...", client)

"""

import json
import logging
from datetime import datetime, timezone
from string import Template
from typing import Any, Dict, List, Optional

from pydantic import ConfigDict

from .base import AgentConfig, RunContext, VerifierAgent
from .data_point import DataPoint, TaskAgentResult
from .prompts import CHECK_VALID_TASK_PROMPT

# webeval's native ChatCompletionClient interface.
from webeval.oai_clients import (
    ChatCompletionClient,  # noqa: F401 — re-exported for type hints only
)

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_MESSAGES: List[Dict[str, str]] = [
    {"role": "system", "content": "You are a helpful AI assistant."}
]

MAX_LLM_RETRIES = 5

# Required top-level fields and their expected types in the verification JSON.
# This module validates only axes 1 (ambiguity) and 2 (invalid task), which
# are the outputs produced by classify_task / CHECK_VALID_TASK_PROMPT.
_REQUIRED_FIELDS: Dict[str, type] = {
    "reasoning_is_ambiguous": str,
    "is_ambiguous": bool,
    "ambiguity_codes": list,
    "reasoning_is_invalid": str,
    "is_invalid": bool,
    "invalid_task_codes": list,
}


# ---------------------------------------------------------------------------
# DataPoint helpers
# ---------------------------------------------------------------------------
def _extract_start_url_from_environment_config(data_point: DataPoint) -> str:
    """Extract the configured starting URL/page from task.environment_config."""
    env_cfg = data_point.task.environment_config or {}
    for key in ("init_url", "start_page", "start_url"):
        url = env_cfg.get(key)
        if url:
            return str(url)
    return ""


def extract_initial_url(data_point: DataPoint) -> str:
    """Extract the starting URL, preferring task config over solver log events."""
    configured_url = _extract_start_url_from_environment_config(data_point)
    if configured_url:
        return configured_url
    for event in data_point.solver_log.events:
        url = getattr(event, "url", "") or ""
        if url:
            return url
    return "N/A"


def extract_apps(data_point: DataPoint) -> List[str]:
    """Extract the application name(s) from environment_config.apps.

    Returns a list of application names.  Falls back to ``["Edge"]``
    (Microsoft Edge) when there is a URL but no explicit app list, or
    ``["N/A"]`` when there is neither.
    """
    env_cfg = data_point.task.environment_config or {}
    apps = env_cfg.get("apps")
    if apps:
        if isinstance(apps, list):
            return [str(a) for a in apps]
        return [str(apps)]
    # No explicit apps — default to Edge if there is a URL
    url = extract_initial_url(data_point)
    if url and url != "N/A":
        return ["Edge"]
    return ["N/A"]


def extract_app(data_point: DataPoint) -> str:
    """Extract the application name(s) as a comma-separated string.

    .. deprecated:: Use :func:`extract_apps` instead.
    """
    return ", ".join(extract_apps(data_point))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
async def _call_llm(
    messages: list[dict],
    client: Any,
    json_output: bool = False,
) -> str:
    """Call a :class:`ChatCompletionClient` and return the response text.

    ``messages`` is a list of OpenAI-chat-completion dicts that the
    wrappers in :mod:`webeval.oai_clients.wrapper` accept directly.
    """
    supports_json = True
    fn = getattr(client, "supports_json", None)
    if callable(fn):
        try:
            supports_json = bool(fn())
        except TypeError:
            supports_json = bool(fn)
    result = await client.create(
        messages=messages,
        json_output=json_output if supports_json else False,
    )
    content = result.content
    if hasattr(content, "content"):
        content = content.content
    assert isinstance(content, str), (
        f"Expected str content from client, got {type(content).__name__}: {content!r}"
    )
    return content


def _validate_verification_result(result: dict) -> None:
    """Raise ``ValueError`` if *result* is missing or mis-typed fields."""
    for field, expected_type in _REQUIRED_FIELDS.items():
        if field not in result:
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(result[field], expected_type):
            raise ValueError(
                f"{field} must be {expected_type.__name__}, "
                f"got {type(result[field]).__name__}"
            )
    # Reasoning fields must be non-empty strings.
    for rf in ("reasoning_is_ambiguous", "reasoning_is_invalid"):
        if not result[rf]:
            raise ValueError(f"{rf} must be a non-empty string")


# ---------------------------------------------------------------------------
# TaskAgent — agent wrapper
# ---------------------------------------------------------------------------
class TaskAgentConfig(AgentConfig):
    """Configuration for the task verification classification agent."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)

    name: str = "task_agent"
    client: Any = None  # ChatCompletionClient


class TaskAgent(VerifierAgent):
    """Agent that performs task verification classification.

    Evaluates a task along two axes (ambiguity, validity)
    and returns a :class:`TaskAgentResult`.

    Two usage patterns:

    1. **Via RunContext** (``run``): Reads the task from a DataPoint,
       extracts the URL from solver_log events, classifies, and returns
       the result.
    2. **Standalone** (``classify``): Takes raw task text + URL and
       returns a result without needing a DataPoint.
    """

    config: TaskAgentConfig

    @classmethod
    def _get_config_class(cls) -> type[AgentConfig]:
        return TaskAgentConfig

    async def run(
        self, run_context: RunContext, input: Any = None
    ) -> list[TaskAgentResult]:
        """Classify the task in the DataPoint.

        Returns a single-element list containing the
        :class:`TaskAgentResult`.
        """
        dp = run_context.data_point
        task_desc = dp.task.instruction
        url = extract_initial_url(dp)
        apps = extract_apps(dp)
        result = await classify_task(
            task_desc,
            url,
            self.config.client,
            apps=apps,
        )
        return [result]

    async def classify(
        self,
        task: str,
        url: str,
        *,
        apps: List[str] | None = None,
        date: str | None = None,
    ) -> TaskAgentResult:
        """Classify a task without a DataPoint / RunContext."""
        return await classify_task(
            task,
            url,
            self.config.client,
            apps=apps,
            date=date,
        )


# ---------------------------------------------------------------------------
# Step 10: Unified task verification classification (bare function)
# ---------------------------------------------------------------------------
async def classify_task(
    task: str,
    url: str,
    client: ChatCompletionClient,
    *,
    apps: List[str] | None = None,
    date: str | None = None,
    system_messages: Optional[List[Dict[str, str]]] = None,
) -> TaskAgentResult:
    """Unified task verification classification across ambiguity
    and validity axes.

    Parameters
    ----------
    task : str
        The task description the agent was asked to complete.
    url : str
        The starting URL (or ``"N/A"`` / empty string).
    client : ChatCompletionClient
        LLM client to use for the classification call.
    apps : list[str], optional
        The application(s) available to the agent (e.g.
        ``["Google Flights", "Edge"]``).  Defaults to ``["N/A"]``.
    date : str, optional
        ISO-formatted date string (e.g. ``"2026-04-07"``).
        Defaults to today's UTC date.
    system_messages : list[dict], optional
        Override the default system messages.

    Returns
    -------
    TaskAgentResult
        Structured result matching the ``CHECK_VALID_TASK_PROMPT`` schema.
        On repeated LLM failures, boolean fields are set to ``None``.
    """
    if apps is None:
        apps = ["N/A"]
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    apps_str = ", ".join(apps) if apps else "N/A"

    sys_msgs = (
        system_messages if system_messages is not None else DEFAULT_SYSTEM_MESSAGES
    )
    prompt = Template(CHECK_VALID_TASK_PROMPT).substitute(
        task_definition=task,
        url=url or "N/A",
        apps=apps_str,
        date=date,
    )
    messages = list(sys_msgs) + [{"role": "user", "content": prompt}]

    retries_left = MAX_LLM_RETRIES
    last_error = None
    while retries_left > 0:
        try:
            response_text = await _call_llm(messages, client, json_output=True)
            result = json.loads(response_text)
            _validate_verification_result(result)
            is_flagged = result.get("is_ambiguous") or result.get("is_invalid")
            logger.info(
                "Task verification result: is_ambiguous=%s, is_invalid=%s",
                result["is_ambiguous"],
                result["is_invalid"],
            )
            return TaskAgentResult(
                verifier_name="task_verification",
                score=0.0 if is_flagged else 1.0,
                reasoning="FLAGGED" if is_flagged else "OK",
                **result,
            )
        except Exception as e:
            last_error = str(e)
            attempt = MAX_LLM_RETRIES - retries_left + 1
            logger.error(
                f"Error in task verification classification (attempt {attempt}): {e}"
            )
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"Error: {e}. Please ensure your output follows the exact "
                        "JSON format specified with all required fields."
                    ),
                }
            )
            retries_left -= 1

    logger.warning(
        "Failed task verification classification after %d attempts. Last error: %s",
        MAX_LLM_RETRIES,
        last_error,
    )
    error_msg = f"Failed after {MAX_LLM_RETRIES} attempts. Last error: {last_error}"
    return TaskAgentResult(
        verifier_name="task_verification",
        score=None,
        reasoning=error_msg,
        reasoning_is_ambiguous=error_msg,
        is_ambiguous=None,
        reasoning_is_invalid=error_msg,
        is_invalid=None,
    )
