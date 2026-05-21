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

from collections.abc import Mapping
from typing import Any, cast

from agently.core.TaskDAGExecutor import (
    _GRAPH_SCHEMA_VERSION,
    _TASK_ID_PATTERN,
    TaskDAGValidator,
    task_dag_planner_ensure_keys,
    task_dag_planner_output_schema,
)
from agently.types.plugins import TaskDAGPlanner
from agently.utils import FunctionShifter, SettingsNamespace


class AgentlyTaskDAGPlanner(TaskDAGPlanner):
    name = "AgentlyTaskDAGPlanner"

    DEFAULT_SETTINGS = {
        "$mappings": {
            "path_mappings": {
                "AgentlyTaskDAGPlanner": "plugins.TaskDAGPlanner.AgentlyTaskDAGPlanner",
                "TaskDAGPlanner": "plugins.TaskDAGPlanner.AgentlyTaskDAGPlanner",
            },
        },
        "schema_version": _GRAPH_SCHEMA_VERSION,
        "available_bindings": [],
        "max_tasks": None,
    }

    def __init__(
        self,
        settings: Any = None,
        *,
        validator: TaskDAGValidator | None = None,
        resolver: Any = None,
        available_bindings: list[str] | tuple[str, ...] | None = None,
        max_tasks: int | None = None,
    ):
        if resolver is None and isinstance(settings, Mapping):
            resolver = settings
            settings = None
        plugin_settings = None
        if settings is not None:
            plugin_settings = SettingsNamespace(settings, f"plugins.TaskDAGPlanner.{ self.name }")
        schema_version = (
            str(plugin_settings.get("schema_version", _GRAPH_SCHEMA_VERSION))
            if plugin_settings is not None
            else _GRAPH_SCHEMA_VERSION
        )
        self.validator = (
            validator
            if validator is not None
            else TaskDAGValidator(resolver=resolver, schema_version=schema_version)
        )
        configured_bindings = cast(Any, plugin_settings).get("available_bindings", []) if plugin_settings is not None else []
        binding_source = available_bindings if available_bindings is not None else configured_bindings
        self.available_bindings = tuple(binding_source or sorted(self.validator.resolver.keys()))
        configured_max_tasks = (
            cast(Any, plugin_settings).get("max_tasks", None)
            if plugin_settings is not None
            else None
        )
        self.max_tasks = max_tasks if max_tasks is not None else configured_max_tasks

    @staticmethod
    def _on_register():
        pass

    @staticmethod
    def _on_unregister():
        pass

    def output_schema(self) -> dict[str, Any]:
        return task_dag_planner_output_schema()

    def ensure_keys(self) -> list[str]:
        return task_dag_planner_ensure_keys()

    def validate_output(self, result: dict[str, Any], context: Any = None):
        return self.validator.validate_planner_output(result, context)

    def instructions(self) -> list[str]:
        constraints = [
            "Return one executable Task DAG object only.",
            f"Set task_schema_version to '{ self.validator.schema_version }'.",
            "Use stable task ids that match letters, digits, underscore, dot, or dash.",
            "Reference dependencies only by upstream task id in depends_on.",
            "Keep depends_on empty for root tasks and never create dependency cycles.",
            "Do not place dependency results inside task.inputs; executor injects dependency_results at runtime.",
            "Use semantic_outputs to map each final deliverable role to a source task id.",
            "Declare side_effect_policy for network, local_write, external_write, or credential_usage tasks.",
            "Add approval.required=true for side-effect tasks when graph policy requires approval.",
            "Do not mark ordinary model tasks as network side effects only because they call the model provider; the executor manages provider access.",
            "Keep approval empty for read-only model analysis, synthesis, drafting, validation, or final response tasks unless the user explicitly asks for a human approval gate.",
            "Do not invent executor handlers; use only task kinds or binding names that the resolver declares as available.",
        ]
        if self.available_bindings:
            constraints.append("Available task kinds and bindings: " + ", ".join(self.available_bindings) + ".")
        if self.max_tasks is not None:
            constraints.append(f"Use no more than { self.max_tasks } tasks unless the user explicitly asks for more.")
        return constraints

    def plugin_constraints(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "schema_version": self.validator.schema_version,
            "available_bindings": list(self.available_bindings),
            "task_id_pattern": _TASK_ID_PATTERN.pattern,
            "required_keys": self.ensure_keys(),
            "max_tasks": self.max_tasks,
            "request_contract": {
                "output_schema": "Task DAG v1 Agently output schema",
                "ensure_keys": self.ensure_keys(),
                "validate_handler": "validate_output",
                "retryable": True,
            },
            "validation": [
                "schema_version",
                "duplicate_task_ids",
                "missing_dependencies",
                "dependency_cycles",
                "binding_availability",
                "semantic_output_refs",
                "side_effect_approval_policy",
            ],
            "forbidden": [
                "unstable_or_generated_task_ids_on_retry",
                "dependency_results_inside_task_inputs",
                "task_kinds_or_bindings_without_resolver_entries",
                "implicit_external_side_effects",
                "agent_or_provider_assumptions_inside_executor",
            ],
        }

    def prepare_request(self, request: Any, graph_input: Any = None):
        prepared = request
        if graph_input is not None and hasattr(prepared, "input"):
            prepared = prepared.input(graph_input)
        if hasattr(prepared, "instruct"):
            prepared = prepared.instruct(self.instructions())
        if hasattr(prepared, "output"):
            prepared = prepared.output(self.output_schema())
        if hasattr(prepared, "validate"):
            prepared = prepared.validate(self.validate_output)
        return prepared

    async def async_plan(
        self,
        request: Any,
        graph_input: Any = None,
        *,
        max_retries: int = 3,
    ) -> Any:
        prepared = self.prepare_request(request, graph_input)
        if not hasattr(prepared, "async_start"):
            raise TypeError("Task DAG planner request must provide async_start(...).")
        return await prepared.async_start(
            ensure_keys=self.ensure_keys(),
            validate_handler=self.validate_output,
            max_retries=max_retries,
        )

    def plan(
        self,
        request: Any,
        graph_input: Any = None,
        *,
        max_retries: int = 3,
    ) -> Any:
        return FunctionShifter.syncify(self.async_plan)(
            request,
            graph_input,
            max_retries=max_retries,
        )
