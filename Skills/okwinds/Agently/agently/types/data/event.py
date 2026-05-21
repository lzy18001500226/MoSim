# Copyright 2023-2026 AgentEra(Agently.Tech)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time
import traceback
import uuid
from typing import Any, Awaitable, Callable, Literal, TypeAlias

from pydantic import BaseModel, Field, model_validator
from typing_extensions import TypedDict

ObservationEventLevel: TypeAlias = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
RuntimeEventLevel: TypeAlias = ObservationEventLevel

_TRIGGERFLOW_WORKFLOW_SUFFIXES = frozenset(
    {
        "definition_declared",
        "execution_started",
        "execution_completed",
        "execution_failed",
        "execution_resumed",
        "interrupt_raised",
        "stream_item_emitted",
        "result_set",
    }
)

_TRIGGERFLOW_NATIVE_SUFFIXES = frozenset(
    {
        "signal",
        "handler_dispatch",
        "annotation",
    }
)

_TRIGGERFLOW_ALL_SUFFIXES = _TRIGGERFLOW_WORKFLOW_SUFFIXES | _TRIGGERFLOW_NATIVE_SUFFIXES


def normalize_triggerflow_event_type(event_type: str | None):
    if not isinstance(event_type, str) or not event_type:
        return event_type
    if event_type.startswith("triggerflow."):
        suffix = event_type[len("triggerflow.") :]
        return event_type if suffix in _TRIGGERFLOW_ALL_SUFFIXES else event_type
    if event_type.startswith("workflow."):
        suffix = event_type[len("workflow.") :]
        if suffix in _TRIGGERFLOW_WORKFLOW_SUFFIXES:
            return f"triggerflow.{ suffix }"
        return event_type
    if event_type.startswith("trigger_flow."):
        suffix = event_type[len("trigger_flow.") :]
        if suffix in _TRIGGERFLOW_NATIVE_SUFFIXES:
            return f"triggerflow.{ suffix }"
        return event_type
    return event_type


def get_triggerflow_event_aliases(event_type: str | None):
    if not isinstance(event_type, str) or not event_type:
        return set()
    normalized = normalize_triggerflow_event_type(event_type)
    aliases = {event_type}
    if not isinstance(normalized, str) or not normalized.startswith("triggerflow."):
        return aliases
    suffix = normalized[len("triggerflow.") :]
    aliases.add(normalized)
    if suffix in _TRIGGERFLOW_WORKFLOW_SUFFIXES:
        aliases.add(f"workflow.{ suffix }")
    if suffix in _TRIGGERFLOW_NATIVE_SUFFIXES:
        aliases.add(f"trigger_flow.{ suffix }")
    return aliases


def matches_runtime_event_type(event_type: str | None, expected_event_types: set[str] | None):
    if expected_event_types is None:
        return True
    aliases = get_triggerflow_event_aliases(event_type)
    return any(expected in aliases for expected in expected_event_types)


def matches_observation_event_type(event_type: str | None, expected_event_types: set[str] | None):
    return matches_runtime_event_type(event_type, expected_event_types)

RunKind: TypeAlias = Literal[
    "agent_turn",
    "request",
    "model_request",
    "workflow_execution",
    "chunk_execution",
    "action_loop",
    "tool_loop",
    "action",
] | str


class ErrorInfoDict(TypedDict, total=False):
    type: str
    message: str
    module: str | None
    traceback: str | None
    retryable: bool | None
    fatal: bool | None
    code: str | None
    details: dict[str, Any]


class RunContextDict(TypedDict, total=False):
    run_id: str
    run_kind: RunKind
    root_run_id: str | None
    parent_run_id: str | None
    agent_id: str | None
    agent_name: str | None
    session_id: str | None
    response_id: str | None
    execution_id: str | None
    meta: dict[str, Any]


class ObservationEventDict(TypedDict, total=False):
    event_id: str
    event_type: str
    source: str
    level: ObservationEventLevel
    message: str | None
    payload: Any
    error: ErrorInfoDict | BaseException | None
    run: RunContextDict | None
    meta: dict[str, Any]
    timestamp: int


RuntimeEventDict: TypeAlias = ObservationEventDict


class ErrorInfo(BaseModel):
    type: str
    message: str
    module: str | None = None
    traceback: str | None = None
    retryable: bool | None = None
    fatal: bool | None = None
    code: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_exception(cls, error: BaseException) -> "ErrorInfo":
        return cls(
            type=error.__class__.__name__,
            message=str(error),
            module=error.__class__.__module__,
            traceback="".join(traceback.format_exception(type(error), error, error.__traceback__)),
        )


class RunContext(BaseModel):
    run_id: str
    run_kind: RunKind
    root_run_id: str | None = None
    parent_run_id: str | None = None
    agent_id: str | None = None
    agent_name: str | None = None
    session_id: str | None = None
    response_id: str | None = None
    execution_id: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _apply_lineage_defaults(self):
        if self.root_run_id is None:
            self.root_run_id = self.run_id
        return self

    @classmethod
    def create(
        cls,
        *,
        run_kind: RunKind,
        run_id: str | None = None,
        parent: "RunContext | None" = None,
        agent_id: str | None = None,
        agent_name: str | None = None,
        session_id: str | None = None,
        response_id: str | None = None,
        execution_id: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> "RunContext":
        resolved_meta = {}
        if parent is not None:
            resolved_meta.update(parent.meta)
        if meta is not None:
            resolved_meta.update(meta)
        return cls(
            run_id=run_id if run_id is not None else uuid.uuid4().hex,
            run_kind=run_kind,
            root_run_id=parent.root_run_id if parent is not None else None,
            parent_run_id=parent.run_id if parent is not None else None,
            agent_id=agent_id if agent_id is not None else (parent.agent_id if parent is not None else None),
            agent_name=agent_name if agent_name is not None else (parent.agent_name if parent is not None else None),
            session_id=session_id if session_id is not None else (parent.session_id if parent is not None else None),
            response_id=response_id if response_id is not None else (parent.response_id if parent is not None else None),
            execution_id=execution_id if execution_id is not None else (parent.execution_id if parent is not None else None),
            meta=resolved_meta,
        )

    def create_child(
        self,
        *,
        run_kind: RunKind,
        run_id: str | None = None,
        agent_id: str | None = None,
        agent_name: str | None = None,
        session_id: str | None = None,
        response_id: str | None = None,
        execution_id: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> "RunContext":
        return type(self).create(
            run_kind=run_kind,
            run_id=run_id,
            parent=self,
            agent_id=agent_id,
            agent_name=agent_name,
            session_id=session_id,
            response_id=response_id,
            execution_id=execution_id,
            meta=meta,
        )


class ObservationEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    event_type: str
    source: str = "Agently"
    level: ObservationEventLevel = "INFO"
    message: str | None = None
    payload: Any = None
    error: ErrorInfo | None = None
    run: RunContext | None = None
    meta: dict[str, Any] = Field(default_factory=dict)
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000))

    model_config = {
        "arbitrary_types_allowed": True,
    }

    @model_validator(mode="before")
    @classmethod
    def _normalize_error(cls, value: Any):
        if not isinstance(value, dict):
            return value
        error = value.get("error")
        if isinstance(error, BaseException):
            normalized = dict(value)
            normalized["error"] = ErrorInfo.from_exception(error)
            return normalized
        return value


class RuntimeEvent(ObservationEvent):
    pass


EventHook = Callable[[ObservationEvent], None | Awaitable[None]]
ObservationEventHook: TypeAlias = EventHook
