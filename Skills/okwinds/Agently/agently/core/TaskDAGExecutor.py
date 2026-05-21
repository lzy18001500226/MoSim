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

from __future__ import annotations

import asyncio
import re
import uuid
from collections import deque
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from typing import Any, Literal, TYPE_CHECKING

from agently.types.trigger_flow import TriggerFlowRuntimeData
from agently.utils import FunctionShifter

if TYPE_CHECKING:
    from .TriggerFlow import TriggerFlow
    from .TriggerFlow.Execution import TriggerFlowExecution


_TASK_ID_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
_GRAPH_SCHEMA_VERSION = "task_dag/v1"
_DYNAMIC_CACHE_ATTR = "_task_dag_executor_cache"
_RESERVED_RESOLVER_KEYS = frozenset(
    {
        "model",
        "action",
        "skill",
        "validate",
        "approval",
        "artifact",
        "emit",
    }
)


@dataclass(frozen=True)
class TaskDAGNode:
    id: str
    kind: str = "task"
    title: str | None = None
    purpose: str | None = None
    depends_on: tuple[str, ...] = field(default_factory=tuple)
    inputs: Any = field(default_factory=dict)
    binding: Any = None
    produces: tuple[Any, ...] = field(default_factory=tuple)
    side_effect_policy: Mapping[str, Any] = field(default_factory=dict)
    fallback: Any = None
    approval: Any = None

    @classmethod
    def from_value(cls, value: "TaskDAGNode | Mapping[str, Any]") -> "TaskDAGNode":
        if isinstance(value, TaskDAGNode):
            return value
        if not isinstance(value, Mapping):
            raise TypeError(f"Dynamic task must be a mapping or TaskDAGNode, got: { type(value) }.")
        task_id = value.get("id")
        if task_id is None:
            raise ValueError("Dynamic task requires non-empty 'id'.")
        depends_on = value.get("depends_on", ())
        if depends_on is None:
            depends_on = ()
        if isinstance(depends_on, str):
            depends_on = (depends_on,)
        produces = value.get("produces", ())
        if produces is None:
            produces = ()
        if isinstance(produces, (str, Mapping)):
            produces = (produces,)
        return cls(
            id=str(task_id).strip(),
            kind=str(value.get("kind", "task")).strip() or "task",
            title=str(value["title"]) if value.get("title") is not None else None,
            purpose=str(value["purpose"]) if value.get("purpose") is not None else None,
            depends_on=tuple(str(item).strip() for item in depends_on),
            inputs=value.get("inputs", {}),
            binding=value.get("binding"),
            produces=tuple(produces),
            side_effect_policy=(
                dict(value.get("side_effect_policy") or {})
                if isinstance(value.get("side_effect_policy") or {}, Mapping)
                else {"value": value.get("side_effect_policy")}
            ),
            fallback=value.get("fallback"),
            approval=value.get("approval"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "title": self.title,
            "purpose": self.purpose,
            "depends_on": list(self.depends_on),
            "inputs": self.inputs,
            "binding": self.binding,
            "produces": list(self.produces),
            "side_effect_policy": dict(self.side_effect_policy),
            "fallback": self.fallback,
            "approval": self.approval,
        }


@dataclass(frozen=True)
class TaskDAG:
    graph_id: str
    tasks: tuple[TaskDAGNode, ...]
    task_schema_version: str = _GRAPH_SCHEMA_VERSION
    semantic_outputs: Any = field(default_factory=dict)
    policies: Mapping[str, Any] = field(default_factory=dict)
    diagnostics: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)

    @classmethod
    def from_value(cls, value: "TaskDAG | Mapping[str, Any]") -> "TaskDAG":
        if isinstance(value, TaskDAG):
            return value
        if not isinstance(value, Mapping):
            raise TypeError(f"Task DAG must be a mapping or TaskDAG, got: { type(value) }.")
        raw_tasks = value.get("tasks")
        if raw_tasks is None:
            raise ValueError("Task DAG requires 'tasks'.")
        if not isinstance(raw_tasks, list | tuple):
            raise TypeError(f"Task DAG 'tasks' must be a list/tuple, got: { type(raw_tasks) }.")
        graph_id = str(value.get("graph_id") or f"graph-{ uuid.uuid4().hex[:12] }").strip()
        if not graph_id:
            raise ValueError("Task DAG requires non-empty 'graph_id'.")
        diagnostics = value.get("diagnostics", ())
        if isinstance(diagnostics, Mapping):
            diagnostics = (diagnostics,)
        return cls(
            graph_id=graph_id,
            task_schema_version=str(value.get("task_schema_version") or _GRAPH_SCHEMA_VERSION),
            tasks=tuple(TaskDAGNode.from_value(task) for task in raw_tasks),
            semantic_outputs=value.get("semantic_outputs", {}),
            policies=dict(value.get("policies") or {}),
            diagnostics=tuple(
                dict(item) if isinstance(item, Mapping) else {"message": str(item)}
                for item in (diagnostics or ())
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "graph_id": self.graph_id,
            "task_schema_version": self.task_schema_version,
            "tasks": [task.to_dict() for task in self.tasks],
            "semantic_outputs": self.semantic_outputs,
            "policies": dict(self.policies),
            "diagnostics": [dict(item) for item in self.diagnostics],
        }


@dataclass(frozen=True)
class DynamicTaskContext:
    graph: TaskDAG
    task: TaskDAGNode
    task_input: Mapping[str, Any]
    graph_input: Any
    dependency_results: Mapping[str, Any]
    dependency_payload: Any
    resources: Mapping[str, Any]
    runtime_data: TriggerFlowRuntimeData

    @property
    def execution(self) -> "TriggerFlowExecution":
        return self.runtime_data.execution


DynamicTaskHandler = Callable[[DynamicTaskContext], Any]


class DynamicTaskResolver:
    def __init__(self, entries: Mapping[str, Any] | None = None):
        self._entries: dict[str, Any] = {}
        self.register("validate", _default_validate_task)
        self.register("emit", _default_emit_task)
        if entries:
            for key, value in entries.items():
                self.register(str(key), value)

    def register(self, key: str, value: Any):
        normalized_key = str(key).strip()
        if not normalized_key:
            raise ValueError("DynamicTaskResolver.register() requires a non-empty key.")
        if not _TASK_ID_PATTERN.fullmatch(normalized_key):
            raise ValueError(
                f"Dynamic task resolver key '{ normalized_key }' is invalid. "
                "Use letters, digits, underscore, dot, or dash."
            )
        self._entries[normalized_key] = value
        return self

    def has(self, key: str):
        return str(key) in self._entries

    def keys(self):
        return tuple(self._entries.keys())

    def to_mapping(self):
        return dict(self._entries)

    def resolve(self, task: TaskDAGNode):
        if task.binding is not None and callable(task.binding):
            return task.binding
        if isinstance(task.binding, str):
            if task.binding in self._entries:
                return self._resolve_registered(self._entries[task.binding], task)
            if task.kind in {"model", "action", "skill"} and task.kind in self._entries:
                return self._resolve_registered(self._entries[task.kind], task)
            return None
        if task.id in self._entries:
            return self._resolve_registered(self._entries[task.id], task)
        if task.kind in self._entries:
            return self._resolve_registered(self._entries[task.kind], task)
        return None

    @staticmethod
    def _resolve_registered(value: Any, task: TaskDAGNode):
        return value(task) if _is_task_resolver_factory(value) else value


@dataclass(frozen=True)
class TaskDAGValidation:
    graph: TaskDAG
    task_ids: tuple[str, ...]
    root_task_ids: tuple[str, ...]
    topological_task_ids: tuple[str, ...]
    diagnostics: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)


@dataclass
class CompiledTaskDAG:
    graph: TaskDAG
    flow: "TriggerFlow"
    validation: TaskDAGValidation

    def create_execution(self, **kwargs: Any) -> "TriggerFlowExecution":
        return self.flow.create_execution(**kwargs)

    async def async_run(
        self,
        graph_input: Any = None,
        *,
        timeout: float | None = None,
        concurrency: int | None = None,
        runtime_resources: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        execution = self.create_execution(
            auto_close=False,
            concurrency=concurrency,
            runtime_resources=runtime_resources,
        )
        await execution.async_start(graph_input)
        return await execution.async_close(timeout=timeout)


class TaskDAGValidator:
    def __init__(
        self,
        resolver: DynamicTaskResolver | Mapping[str, Any] | None = None,
        *,
        schema_version: str = _GRAPH_SCHEMA_VERSION,
    ):
        self.resolver = _coerce_resolver(resolver)
        self.schema_version = schema_version

    def validate(
        self,
        graph: TaskDAG | Mapping[str, Any],
        *,
        resolver: DynamicTaskResolver | Mapping[str, Any] | None = None,
        strict_schema_version: bool = False,
    ) -> TaskDAGValidation:
        validation = validate_task_dag(
            graph,
            resolver=self._merge_resolver(resolver),
        )
        if strict_schema_version and validation.graph.task_schema_version != self.schema_version:
            raise ValueError(
                f"Task DAG schema version must be '{ self.schema_version }', "
                f"got '{ validation.graph.task_schema_version }'."
            )
        return validation

    def validate_planner_output(
        self,
        result: Mapping[str, Any],
        context: Any = None,
        *,
        resolver: DynamicTaskResolver | Mapping[str, Any] | None = None,
    ):
        return validate_task_dag_planner_output(
            result,
            resolver=self._merge_resolver(resolver),
            schema_version=self.schema_version,
        )

    def _merge_resolver(self, resolver: DynamicTaskResolver | Mapping[str, Any] | None):
        if resolver is None:
            return self.resolver
        merged = DynamicTaskResolver(self.resolver.to_mapping())
        for key, value in _coerce_resolver(resolver).to_mapping().items():
            merged.register(key, value)
        return merged


class TaskDAGExecutor:
    def __init__(
        self,
        resolver: DynamicTaskResolver | Mapping[str, Any] | None = None,
        *,
        flow: "TriggerFlow | None" = None,
        name: str | None = None,
        validator: TaskDAGValidator | None = None,
    ):
        self.resolver = _coerce_resolver(resolver)
        self.flow = flow
        self.name = name
        self.validator = validator if validator is not None else TaskDAGValidator(resolver=self.resolver)

    def compile(
        self,
        graph: TaskDAG | Mapping[str, Any],
        *,
        resolver: DynamicTaskResolver | Mapping[str, Any] | None = None,
        flow: "TriggerFlow | None" = None,
        name: str | None = None,
    ) -> CompiledTaskDAG:
        merged_resolver = self._merge_resolver(resolver)
        validation = self.validator.validate(graph, resolver=merged_resolver)
        compiled = compile_task_dag(
            validation.graph,
            resolver=merged_resolver,
            flow=flow if flow is not None else self.flow,
            name=name if name is not None else self.name,
        )
        if self.flow is None:
            self.flow = compiled.flow
        return compiled

    async def async_run(
        self,
        graph: TaskDAG | Mapping[str, Any],
        graph_input: Any = None,
        *,
        resolver: DynamicTaskResolver | Mapping[str, Any] | None = None,
        timeout: float | None = None,
        concurrency: int | None = None,
        runtime_resources: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        compiled = self.compile(graph, resolver=resolver)
        return await compiled.async_run(
            graph_input,
            timeout=timeout,
            concurrency=concurrency,
            runtime_resources=runtime_resources,
        )

    def _merge_resolver(self, resolver: DynamicTaskResolver | Mapping[str, Any] | None):
        if resolver is None:
            return self.resolver
        merged = DynamicTaskResolver(self.resolver.to_mapping())
        for key, value in _coerce_resolver(resolver).to_mapping().items():
            merged.register(key, value)
        return merged

    @staticmethod
    def resolver_factory(func: Callable[[TaskDAGNode], Any]):
        return dynamic_task_resolver_factory(func)


def validate_task_dag(
    graph: TaskDAG | Mapping[str, Any],
    *,
    resolver: DynamicTaskResolver | Mapping[str, Any] | None = None,
) -> TaskDAGValidation:
    normalized = TaskDAG.from_value(graph)
    resolved_resolver = _coerce_resolver(resolver)
    tasks = list(normalized.tasks)
    if not tasks:
        raise ValueError("Task DAG must contain at least one task.")

    task_by_id: dict[str, TaskDAGNode] = {}
    duplicates: list[str] = []
    for task in tasks:
        if not task.id:
            raise ValueError("Dynamic task id must be non-empty.")
        if not _TASK_ID_PATTERN.fullmatch(task.id):
            raise ValueError(
                f"Dynamic task id '{ task.id }' is invalid. Use letters, digits, underscore, dot, or dash."
            )
        if task.id in task_by_id:
            duplicates.append(task.id)
        task_by_id[task.id] = task
    if duplicates:
        raise ValueError(f"Duplicate dynamic task id(s): { ', '.join(sorted(set(duplicates))) }.")

    for task in tasks:
        for dependency in task.depends_on:
            if dependency not in task_by_id:
                raise ValueError(
                    f"Dynamic task '{ task.id }' depends on missing task '{ dependency }'."
                )

    adjacency: dict[str, list[str]] = {task.id: [] for task in tasks}
    indegree: dict[str, int] = {task.id: 0 for task in tasks}
    for task in tasks:
        for dependency in task.depends_on:
            adjacency[dependency].append(task.id)
            indegree[task.id] += 1

    roots = tuple(task.id for task in tasks if not task.depends_on)
    if not roots:
        raise ValueError("Task DAG must contain at least one root task.")

    queue = deque(task_id for task_id in roots)
    ordered: list[str] = []
    while queue:
        task_id = queue.popleft()
        ordered.append(task_id)
        for child_id in adjacency[task_id]:
            indegree[child_id] -= 1
            if indegree[child_id] == 0:
                queue.append(child_id)
    if len(ordered) != len(tasks):
        cycle_ids = sorted(task_id for task_id, count in indegree.items() if count > 0)
        raise ValueError(f"Task DAG contains a dependency cycle: { ', '.join(cycle_ids) }.")

    normalized, tasks, task_by_id, roots, ordered_ids = _prune_unresolved_optional_tasks(
        normalized,
        tasks,
        task_by_id,
        roots,
        tuple(ordered),
        resolved_resolver,
    )

    for task in tasks:
        if _is_approval_task(task):
            continue
        if resolved_resolver.resolve(task) is None:
            raise ValueError(
                f"Dynamic task '{ task.id }' kind '{ task.kind }' has no executor resolver entry."
            )

    _validate_semantic_outputs(normalized, task_by_id)
    _validate_side_effects(normalized)

    return TaskDAGValidation(
        graph=normalized,
        task_ids=tuple(task.id for task in tasks),
        root_task_ids=roots,
        topological_task_ids=ordered_ids,
        diagnostics=normalized.diagnostics,
    )


def task_dag_planner_output_schema() -> dict[str, Any]:
    return {
        "graph_id": (
            str,
            "Stable graph id using lowercase words, digits, dash, or underscore.",
            True,
        ),
        "task_schema_version": (
            str,
            f"Task graph schema version. Use '{ _GRAPH_SCHEMA_VERSION }'.",
            True,
        ),
        "tasks": [
            {
                "id": (
                    str,
                    "Unique stable task id. Use letters, digits, underscore, dot, or dash. Do not renumber on retry.",
                    True,
                ),
                "kind": (
                    str,
                    "Task kind such as model, action, local, artifact, approval, emit, or validate.",
                    True,
                ),
                "title": (str, "Short human-readable task title."),
                "purpose": (str, "Why this task exists in the graph."),
                "depends_on": (
                    ["str"],
                    "List of upstream task ids. Use an empty list for root tasks.",
                    True,
                ),
                "inputs": (
                    dict,
                    "Task-local static inputs. Do not include dependency results here.",
                ),
                "binding": (
                    str,
                    "Optional resolver entry name such as risk_check_handler when kind alone is not specific enough.",
                ),
                "produces": [
                    {
                        "role": (str, "Semantic output or artifact role produced by this task.", True),
                        "type": (str, "Result type such as text, json, artifact_ref, table, or list."),
                    }
                ],
                "side_effect_policy": (
                    dict,
                    "Side-effect declaration such as network, local_write, external_write, or credential_usage.",
                ),
                "fallback": (
                    dict,
                    "Fallback policy such as {'on_error': 'skip'} or {'on_error': 'fail'}.",
                ),
                "approval": (
                    dict,
                    "Approval policy. Use {'required': true, 'type': 'human_approval'} when a task must pause.",
                ),
            }
        ],
        "semantic_outputs": (
            dict,
            "Map final deliverable role to source task id or {'task_id': '<id>'}.",
            True,
        ),
        "policies": (
            dict,
            "Graph-level policy for concurrency, fallback, retry, approval, and side effects.",
        ),
        "diagnostics": [
            {
                "level": (str, "info, warning, or repaired."),
                "message": (str, "Planner normalization note."),
            }
        ],
    }


def task_dag_planner_ensure_keys() -> list[str]:
    return [
        "graph_id",
        "task_schema_version",
        "tasks[*].id",
        "tasks[*].kind",
        "tasks[*].depends_on",
        "semantic_outputs",
    ]


def validate_task_dag_planner_output(
    result: Mapping[str, Any],
    *,
    resolver: DynamicTaskResolver | Mapping[str, Any] | None = None,
    schema_version: str = _GRAPH_SCHEMA_VERSION,
):
    try:
        validation = validate_task_dag(result, resolver=resolver)
    except Exception as error:
        return {
            "ok": False,
            "reason": str(error),
            "validator_name": "task_dag",
        }
    if validation.graph.task_schema_version != schema_version:
        return {
            "ok": False,
            "reason": (
                f"Task DAG schema version must be '{ schema_version }', "
                f"got '{ validation.graph.task_schema_version }'."
            ),
            "validator_name": "task_dag.schema_version",
        }
    return True


def compile_task_dag(
    graph: TaskDAG | Mapping[str, Any],
    *,
    resolver: DynamicTaskResolver | Mapping[str, Any] | None = None,
    flow: "TriggerFlow | None" = None,
    name: str | None = None,
) -> CompiledTaskDAG:
    from .TriggerFlow import TriggerFlow

    resolved_resolver = _coerce_resolver(resolver)
    validation = validate_task_dag(graph, resolver=resolved_resolver)
    normalized = validation.graph
    target_flow = flow if flow is not None else TriggerFlow(name=name or f"dynamic-task:{ normalized.graph_id }")
    _assert_graph_signature_compatible(target_flow, normalized)

    cache = _get_compile_cache(target_flow)
    result_lock = cache["result_locks"].setdefault(normalized.graph_id, asyncio.Lock())

    kickoff = _cached_handler(
        cache,
        normalized.graph_id,
        "kickoff",
        "*",
        lambda: _make_kickoff_handler(normalized, validation.root_task_ids),
    )
    target_flow.to(kickoff, name=_chunk_name(normalized.graph_id, "kickoff", "*"))

    for task in normalized.tasks:
        runner = _cached_handler(
            cache,
            normalized.graph_id,
            "run",
            task.id,
            lambda task=task: _make_task_runner(
                graph=normalized,
                task=task,
                resolver=resolved_resolver,
                result_lock=result_lock,
            ),
        )
        trigger = _task_trigger(target_flow, task)
        trigger.to(runner, name=_chunk_name(normalized.graph_id, "run", task.id))

    finalize = _cached_handler(
        cache,
        normalized.graph_id,
        "finalize",
        "*",
        lambda: _make_finalize_handler(normalized),
    )
    target_flow.when(_done_graph_event(normalized.graph_id)).to(
        finalize,
        name=_chunk_name(normalized.graph_id, "finalize", "*"),
    )
    return CompiledTaskDAG(
        graph=normalized,
        flow=target_flow,
        validation=validation,
    )


def _get_compile_cache(flow: "TriggerFlow") -> dict[str, Any]:
    cache = getattr(flow, _DYNAMIC_CACHE_ATTR, None)
    if cache is None:
        cache = {
            "graph_signatures": {},
            "handlers": {},
            "result_locks": {},
        }
        setattr(flow, _DYNAMIC_CACHE_ATTR, cache)
    return cache


def _assert_graph_signature_compatible(flow: "TriggerFlow", graph: TaskDAG) -> None:
    cache = _get_compile_cache(flow)
    signature = _graph_signature(graph)
    existing = cache["graph_signatures"].get(graph.graph_id)
    if existing is not None and existing != signature:
        raise ValueError(
            f"Task DAG '{ graph.graph_id }' was already compiled with a different definition."
        )
    cache["graph_signatures"][graph.graph_id] = signature


def _cached_handler(
    cache: dict[str, Any],
    graph_id: str,
    phase: str,
    task_id: str,
    factory: Callable[[], Callable[[TriggerFlowRuntimeData], Any]],
):
    key = (graph_id, phase, task_id)
    if key not in cache["handlers"]:
        cache["handlers"][key] = factory()
    return cache["handlers"][key]


def _make_kickoff_handler(
    graph: TaskDAG,
    root_task_ids: tuple[str, ...],
):
    async def kickoff(data: TriggerFlowRuntimeData):
        await data.async_set_state("graph_id", graph.graph_id, emit=False)
        await data.async_set_state("graph_input", data.value, emit=False)
        await data.async_set_state("task_results", {}, emit=False)
        await data.async_set_state("task_statuses", {}, emit=False)
        await data.async_set_state("task_failures", {}, emit=False)
        await data.async_set_state("artifact_refs", {}, emit=False)
        await data.async_set_state("semantic_outputs", {}, emit=False)
        await data.async_set_state("task_dag", graph.to_dict(), emit=False)
        for task_id in root_task_ids:
            data.emit_nowait(_start_task_event(task_id), {"task_id": task_id, "graph_id": graph.graph_id})

    return kickoff


def _make_task_runner(
    *,
    graph: TaskDAG,
    task: TaskDAGNode,
    resolver: DynamicTaskResolver,
    result_lock: asyncio.Lock,
):
    async def run_task(data: TriggerFlowRuntimeData):
        graph_input = data.get_state("graph_input")
        task_results = dict(data.get_state("task_results", {}) or {})
        dependency_results = {dependency: task_results[dependency] for dependency in task.depends_on}
        task_input = {
            "task_id": task.id,
            "task": task.to_dict(),
            "graph_id": graph.graph_id,
            "graph_input": graph_input,
            "inputs": task.inputs,
            "deps": dependency_results,
            "dependency_payload": data.value,
        }
        await _put_task_event(data, graph, task, "start", input=task_input)

        try:
            if _approval_required(task) and not data.is_resume:
                await _put_task_event(data, graph, task, "approval_required", input=task_input)
                return await data.async_pause_for(
                    type=_approval_type(task),
                    payload=_approval_payload(task, task_input),
                    interrupt_id=f"task:{ graph.graph_id }:{ task.id }",
                    resume_to="self",
                )
            output = data.resume.value if _is_approval_task(task) and data.is_resume else None
            if not _is_approval_task(task):
                context = DynamicTaskContext(
                    graph=graph,
                    task=task,
                    task_input=task_input,
                    graph_input=graph_input,
                    dependency_results=dependency_results,
                    dependency_payload=data.value,
                    resources=data.resources.to_dict(),
                    runtime_data=data,
                )
                handler = resolver.resolve(task)
                output = await _execute_handler(handler, context)
        except Exception as error:
            await _record_task_failure(data, graph, task, error, result_lock=result_lock)
            await _put_task_event(data, graph, task, "fail", error=str(error))
            if _fallback_action(task) == "skip":
                output = {"status": "skipped", "reason": str(error)}
                await _record_task_success(data, graph, task, output, result_lock=result_lock)
                await _put_task_event(data, graph, task, "skipped", output=output)
                return output
            raise

        await _record_task_success(data, graph, task, output, result_lock=result_lock)
        await _put_task_event(data, graph, task, "complete", output=output)
        return output

    return run_task


def _make_finalize_handler(graph: TaskDAG):
    async def finalize(data: TriggerFlowRuntimeData):
        task_results = dict(data.get_state("task_results", {}) or {})
        artifact_refs = dict(data.get_state("artifact_refs", {}) or {})
        semantic_outputs = _collect_semantic_outputs(graph, task_results, artifact_refs)
        await data.async_set_state("semantic_outputs", semantic_outputs, emit=False)
        execution_result = {
            "graph_id": graph.graph_id,
            "task_results": task_results,
            "artifact_refs": artifact_refs,
            "semantic_outputs": semantic_outputs,
            "diagnostics": [dict(item) for item in graph.diagnostics],
        }
        await data.async_set_state("task_dag_execution", execution_result, emit=False)
        await _put_graph_event(data, graph, "complete", result=execution_result)
        return execution_result

    return finalize


async def _execute_handler(handler: Any, context: DynamicTaskContext):
    from .TriggerFlow import TriggerFlow

    if isinstance(handler, TriggerFlow):
        execution = handler.create_execution(
            auto_close=True,
            runtime_resources=dict(context.resources),
            parent_run_context=context.runtime_data.chunk_run_context,
        )
        return await execution.async_start(dict(context.task_input))
    if callable(handler):
        return await FunctionShifter.asyncify(handler)(context)
    raise ValueError(
        f"Dynamic task '{ context.task.id }' kind '{ context.task.kind }' has no executable handler."
    )


async def _record_task_success(
    data: TriggerFlowRuntimeData,
    graph: TaskDAG,
    task: TaskDAGNode,
    output: Any,
    *,
    result_lock: asyncio.Lock,
) -> None:
    async with result_lock:
        results = dict(data.get_state("task_results", {}) or {})
        statuses = dict(data.get_state("task_statuses", {}) or {})
        artifact_refs = dict(data.get_state("artifact_refs", {}) or {})
        results[task.id] = output
        statuses[task.id] = "completed"
        extracted_artifacts = _extract_artifact_refs(output)
        if extracted_artifacts:
            artifact_refs[task.id] = extracted_artifacts
        await data.async_set_state("task_results", results, emit=False)
        await data.async_set_state("task_statuses", statuses, emit=False)
        if extracted_artifacts:
            await data.async_set_state("artifact_refs", artifact_refs, emit=False)
        data.emit_nowait(_done_task_event(task.id), {"task_id": task.id, "result": output})
        if len(results) == len(graph.tasks):
            data.emit_nowait(_done_graph_event(graph.graph_id), dict(results))


async def _record_task_failure(
    data: TriggerFlowRuntimeData,
    graph: TaskDAG,
    task: TaskDAGNode,
    error: Exception,
    *,
    result_lock: asyncio.Lock,
) -> None:
    async with result_lock:
        failures = dict(data.get_state("task_failures", {}) or {})
        statuses = dict(data.get_state("task_statuses", {}) or {})
        failures[task.id] = {
            "type": type(error).__name__,
            "message": str(error),
        }
        statuses[task.id] = "failed"
        await data.async_set_state("task_failures", failures, emit=False)
        await data.async_set_state("task_statuses", statuses, emit=False)
        data.emit_nowait(_failed_task_event(task.id), failures[task.id])


async def _put_task_event(
    data: TriggerFlowRuntimeData,
    graph: TaskDAG,
    task: TaskDAGNode,
    action: Literal["start", "complete", "fail", "skipped", "approval_required"],
    **payload: Any,
) -> None:
    await data.execution.async_put_into_stream(
        {
            "type": "task_dag.task",
            "action": action,
            "graph_id": graph.graph_id,
            "task_id": task.id,
            "task_kind": task.kind,
            "payload": payload,
        },
        _skip_contract_validation=True,
    )


async def _put_graph_event(
    data: TriggerFlowRuntimeData,
    graph: TaskDAG,
    action: Literal["complete"],
    **payload: Any,
) -> None:
    await data.execution.async_put_into_stream(
        {
            "type": "task_dag.graph",
            "action": action,
            "graph_id": graph.graph_id,
            "payload": payload,
        },
        _skip_contract_validation=True,
    )


def _task_trigger(flow: "TriggerFlow", task: TaskDAGNode):
    if not task.depends_on:
        return flow.when(_start_task_event(task.id))
    if len(task.depends_on) == 1:
        return flow.when(_done_task_event(task.depends_on[0]))
    return flow.when(
        {"event": [_done_task_event(dependency) for dependency in task.depends_on]},
        mode="and",
    )


def _coerce_resolver(value: DynamicTaskResolver | Mapping[str, Any] | None) -> DynamicTaskResolver:
    if isinstance(value, DynamicTaskResolver):
        return value
    return DynamicTaskResolver(value)


def _prune_unresolved_optional_tasks(
    graph: TaskDAG,
    tasks: list[TaskDAGNode],
    task_by_id: dict[str, TaskDAGNode],
    roots: tuple[str, ...],
    ordered: tuple[str, ...],
    resolver: DynamicTaskResolver,
) -> tuple[TaskDAG, list[TaskDAGNode], dict[str, TaskDAGNode], tuple[str, ...], tuple[str, ...]]:
    required_ids = _semantic_required_task_ids(graph, task_by_id)
    pruned: set[str] = set()
    diagnostics: list[Mapping[str, Any]] = [dict(item) for item in graph.diagnostics]

    def fail_or_prune(task: TaskDAGNode, reason: str):
        if (
            task.id in required_ids
            or _approval_required(task)
            or bool(task.side_effect_policy)
        ):
            raise ValueError(
                f"Dynamic task '{ task.id }' kind '{ task.kind }' has no executor resolver entry."
            )
        pruned.add(task.id)
        diagnostics.append(
            {
                "level": "warning",
                "code": reason,
                "task_id": task.id,
                "kind": task.kind,
                "binding": task.binding,
            }
        )

    for task in tasks:
        if _is_approval_task(task):
            continue
        if resolver.resolve(task) is None:
            fail_or_prune(task, "dynamic_task.unknown_optional_binding_skipped")

    changed = True
    while changed:
        changed = False
        for task in tasks:
            if task.id in pruned:
                continue
            missing_pruned_dependencies = [dependency for dependency in task.depends_on if dependency in pruned]
            if missing_pruned_dependencies:
                if task.id in required_ids:
                    raise ValueError(
                        f"Dynamic task '{ task.id }' depends on skipped optional task(s): "
                        f"{ ', '.join(missing_pruned_dependencies) }."
                    )
                pruned.add(task.id)
                diagnostics.append(
                    {
                        "level": "warning",
                        "code": "dynamic_task.optional_dependent_skipped",
                        "task_id": task.id,
                        "dependencies": missing_pruned_dependencies,
                    }
                )
                changed = True

    if not pruned:
        return graph, tasks, task_by_id, roots, ordered

    kept_tasks = [task for task in tasks if task.id not in pruned]
    if not kept_tasks:
        raise ValueError("Task DAG has no executable tasks after pruning unresolved optional tasks.")
    kept_ids = {task.id for task in kept_tasks}
    kept_by_id = {task.id: task for task in kept_tasks}
    kept_roots = tuple(task.id for task in kept_tasks if not task.depends_on)
    if not kept_roots:
        raise ValueError("Task DAG has no root task after pruning unresolved optional tasks.")
    kept_ordered = tuple(task_id for task_id in ordered if task_id in kept_ids)
    return (
        replace(graph, tasks=tuple(kept_tasks), diagnostics=tuple(diagnostics)),
        kept_tasks,
        kept_by_id,
        kept_roots,
        kept_ordered,
    )


def _semantic_required_task_ids(
    graph: TaskDAG,
    task_by_id: Mapping[str, TaskDAGNode],
) -> set[str]:
    required = set(_semantic_output_task_refs(graph.semantic_outputs).values())
    queue = deque(required)
    while queue:
        task_id = queue.popleft()
        task = task_by_id.get(task_id)
        if task is None:
            continue
        for dependency in task.depends_on:
            if dependency not in required:
                required.add(dependency)
                queue.append(dependency)
    return required


def _is_task_resolver_factory(binding: Any) -> bool:
    marker = getattr(binding, "dynamic_task_resolver_factory", False)
    return bool(marker)


def dynamic_task_resolver_factory(func: Callable[[TaskDAGNode], Any]):
    setattr(func, "dynamic_task_resolver_factory", True)
    return func


async def _default_validate_task(context: DynamicTaskContext):
    return {
        "ok": True,
        "task_id": context.task.id,
        "inputs": context.task.inputs,
        "dependency_results": dict(context.dependency_results),
    }


async def _default_emit_task(context: DynamicTaskContext):
    payload = context.task.inputs
    await context.runtime_data.execution.async_put_into_stream(
        {
            "type": "dynamic_task.emit",
            "graph_id": context.graph.graph_id,
            "task_id": context.task.id,
            "payload": payload,
        },
        _skip_contract_validation=True,
    )
    return payload


def _is_approval_task(task: TaskDAGNode) -> bool:
    return task.kind == "approval"


def _approval_required(task: TaskDAGNode) -> bool:
    if _is_approval_task(task):
        return True
    approval = task.approval
    if approval is True:
        return True
    if isinstance(approval, Mapping):
        return bool(approval.get("required") or approval.get("mode") in {"required", "pause"})
    return False


def _approval_type(task: TaskDAGNode) -> str:
    if isinstance(task.approval, Mapping) and task.approval.get("type"):
        return str(task.approval["type"])
    return "dynamic_task_approval"


def _approval_payload(task: TaskDAGNode, task_input: Mapping[str, Any]):
    if isinstance(task.approval, Mapping) and "payload" in task.approval:
        return task.approval["payload"]
    return {
        "task_id": task.id,
        "kind": task.kind,
        "title": task.title,
        "purpose": task.purpose,
        "input": dict(task_input),
    }


def _fallback_action(task: TaskDAGNode) -> str | None:
    if isinstance(task.fallback, str):
        return task.fallback
    if isinstance(task.fallback, Mapping):
        value = task.fallback.get("on_error") or task.fallback.get("action")
        return str(value) if value is not None else None
    return None


def _validate_semantic_outputs(
    graph: TaskDAG,
    task_by_id: Mapping[str, TaskDAGNode],
) -> None:
    for role, task_id in _semantic_output_task_refs(graph.semantic_outputs).items():
        if task_id not in task_by_id:
            raise ValueError(
                f"Task DAG semantic output '{ role }' references missing task '{ task_id }'."
            )


def _validate_side_effects(graph: TaskDAG) -> None:
    approval_policy = str(graph.policies.get("approval", graph.policies.get("side_effect_approval", "allow")))
    if approval_policy not in {"require", "required", "fail_closed"}:
        return
    for task in graph.tasks:
        side_effects = task.side_effect_policy
        if not side_effects:
            continue
        has_external_write = bool(
            side_effects.get("external_write")
            or side_effects.get("credential_usage")
            or side_effects.get("local_write")
            or side_effects.get("network")
        )
        if has_external_write and not _approval_required(task):
            raise ValueError(
                f"Dynamic task '{ task.id }' declares side effects but has no approval policy."
            )


def _collect_semantic_outputs(
    graph: TaskDAG,
    task_results: Mapping[str, Any],
    artifact_refs: Mapping[str, Any],
) -> dict[str, Any]:
    outputs: dict[str, Any] = {}
    refs = _semantic_output_task_refs(graph.semantic_outputs)
    for role, task_id in refs.items():
        if task_id in artifact_refs:
            outputs[role] = {"task_id": task_id, "artifact_refs": artifact_refs[task_id]}
        elif task_id in task_results:
            outputs[role] = {"task_id": task_id, "result": task_results[task_id]}
    for task in graph.tasks:
        for item in task.produces:
            role = _produce_role(item)
            if role and role not in outputs and task.id in task_results:
                if task.id in artifact_refs:
                    outputs[role] = {"task_id": task.id, "artifact_refs": artifact_refs[task.id]}
                else:
                    outputs[role] = {"task_id": task.id, "result": task_results[task.id]}
    return outputs


def _semantic_output_task_refs(semantic_outputs: Any) -> dict[str, str]:
    refs: dict[str, str] = {}
    if isinstance(semantic_outputs, Mapping):
        for role, spec in semantic_outputs.items():
            if isinstance(spec, str):
                refs[str(role)] = spec
            elif isinstance(spec, Mapping):
                task_id = spec.get("task_id") or spec.get("from_task")
                if task_id is not None:
                    refs[str(role)] = str(task_id)
    elif isinstance(semantic_outputs, list | tuple):
        for item in semantic_outputs:
            if isinstance(item, Mapping):
                role = item.get("role") or item.get("name")
                task_id = item.get("task_id") or item.get("from_task")
                if role is not None and task_id is not None:
                    refs[str(role)] = str(task_id)
    return refs


def _produce_role(item: Any) -> str | None:
    if isinstance(item, str):
        return item
    if isinstance(item, Mapping):
        role = item.get("role") or item.get("name")
        return str(role) if role is not None else None
    return None


def _extract_artifact_refs(output: Any):
    if not isinstance(output, Mapping):
        return None
    refs = output.get("artifact_refs")
    if refs is None:
        refs = output.get("artifacts")
    return refs


def _graph_signature(graph: TaskDAG) -> tuple[Any, ...]:
    return tuple(
        (
            task.id,
            task.kind,
            task.depends_on,
            task.binding if isinstance(task.binding, str) else None,
            task.approval,
            task.fallback,
        )
        for task in graph.tasks
    )


def _chunk_name(graph_id: str, phase: str, task_id: str):
    return f"dynamic:{ graph_id }:{ phase }:{ task_id }"


def _start_task_event(task_id: str):
    return f"start:{ task_id }"


def _done_task_event(task_id: str):
    return f"done:{ task_id }"


def _failed_task_event(task_id: str):
    return f"failed:{ task_id }"


def _done_graph_event(graph_id: str):
    return f"done:graph:{ graph_id }"
