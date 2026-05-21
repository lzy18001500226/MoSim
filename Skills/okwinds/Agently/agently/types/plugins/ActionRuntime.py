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

from typing import TYPE_CHECKING, Any, Awaitable, Callable, Protocol
from typing_extensions import Self

from .base import AgentlyPlugin
from agently.types.data import (
    ActionCall,
    ActionDecision,
    ActionExecutionRequest,
    ActionPlanningRequest,
    ActionResult,
    ActionRunContext,
)

if TYPE_CHECKING:
    from agently.core import Prompt
    from agently.core.Action import Action
    from agently.core.PluginManager import PluginManager
    from agently.utils import Settings


ActionPlanningHandler = Callable[
    [ActionRunContext, ActionPlanningRequest],
    ActionDecision | dict[str, Any] | Awaitable[ActionDecision | dict[str, Any]],
]

StandardActionPlanningHandler = Callable[
    [ActionRunContext, ActionPlanningRequest],
    Awaitable[ActionDecision | dict[str, Any]],
]

ActionExecutionHandler = Callable[
    [ActionRunContext, ActionExecutionRequest],
    list[ActionResult] | list[dict[str, Any]] | Awaitable[list[ActionResult] | list[dict[str, Any]]],
]

StandardActionExecutionHandler = Callable[
    [ActionRunContext, ActionExecutionRequest],
    Awaitable[list[ActionResult] | list[dict[str, Any]]],
]


class ActionRuntime(AgentlyPlugin, Protocol):
    """
    Action planning and execution runtime plugin.

    Implement this protocol when a third-party plugin needs to replace planning
    protocol selection, model-to-action-call normalization, or default action
    execution orchestration. Keep the handler contract compact:
    `handler(context, request)`.
    """

    action: "Action"
    plugin_manager: "PluginManager"
    settings: "Settings"

    def __init__(self, *, action: "Action", plugin_manager: "PluginManager", settings: "Settings"): ...

    async def async_generate_action_call(
        self,
        *,
        prompt: "Prompt",
        settings: "Settings",
        action_list: list[dict[str, Any]],
        agent_name: str = "Manual",
        planning_handler: ActionPlanningHandler | None = None,
        done_plans: list["ActionResult"] | None = None,
        last_round_records: list["ActionResult"] | None = None,
        round_index: int = 0,
        max_rounds: int | None = None,
        planning_protocol: str | None = None,
    ) -> list["ActionCall"]: ...

    async def async_generate_tool_command(
        self,
        *,
        prompt: "Prompt",
        settings: "Settings",
        tool_list: list[dict[str, Any]],
        agent_name: str = "Manual",
        plan_analysis_handler: ActionPlanningHandler | None = None,
        done_plans: list["ActionResult"] | None = None,
        last_round_records: list["ActionResult"] | None = None,
        round_index: int = 0,
        max_rounds: int | None = None,
    ) -> list["ActionCall"]: ...

    def register_action_planning_handler(self, handler: ActionPlanningHandler | None) -> Self: ...

    def register_action_execution_handler(self, handler: ActionExecutionHandler | None) -> Self: ...

    def resolve_planning_handler(
        self,
        handler: ActionPlanningHandler | None = None,
    ) -> StandardActionPlanningHandler: ...

    def resolve_execution_handler(
        self,
        handler: ActionExecutionHandler | None = None,
    ) -> StandardActionExecutionHandler: ...

    def resolve_planning_protocol(self, settings: "Settings", planning_protocol: str | None = None) -> str: ...

    async def _default_structured_planning_handler(
        self,
        context: "ActionRunContext",
        request: "ActionPlanningRequest",
    ) -> ActionDecision | dict[str, Any]: ...

    async def _default_native_tool_call_planning_handler(
        self,
        context: "ActionRunContext",
        request: "ActionPlanningRequest",
    ) -> ActionDecision | dict[str, Any]: ...

    async def _default_planning_handler(
        self,
        context: "ActionRunContext",
        request: "ActionPlanningRequest",
    ) -> ActionDecision | dict[str, Any]: ...

    async def _default_action_execution_handler(
        self,
        context: "ActionRunContext",
        request: "ActionExecutionRequest",
    ) -> list[ActionResult] | list[dict[str, Any]]: ...
