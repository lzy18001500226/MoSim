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

from typing import TYPE_CHECKING, Any, Protocol

from .base import AgentlyPlugin
from .ActionRuntime import ActionExecutionHandler, ActionPlanningHandler

if TYPE_CHECKING:
    from agently.core import Prompt
    from agently.core.Action import Action
    from agently.core.PluginManager import PluginManager
    from agently.types.data import ActionResult
    from agently.utils import Settings


class ActionFlow(AgentlyPlugin, Protocol):
    """
    Action loop orchestration plugin.

    Implement this protocol when a third-party plugin needs to replace how the
    action loop is staged, branched, paused, resumed, or observed. It receives
    planning and execution handlers from the active `ActionRuntime`; it should
    call those handlers through the `handler(context, request)` contract.
    """

    plugin_manager: "PluginManager"
    settings: "Settings"

    def __init__(self, *, plugin_manager: "PluginManager", settings: "Settings"): ...

    async def async_run(
        self,
        *,
        action: "Action",
        prompt: "Prompt",
        settings: "Settings",
        action_list: list[dict[str, Any]],
        agent_name: str = "Manual",
        parent_run_context: Any = None,
        planning_handler: ActionPlanningHandler | None = None,
        execution_handler: ActionExecutionHandler | None = None,
        max_rounds: int | None = None,
        concurrency: int | None = None,
        timeout: float | None = None,
        planning_protocol: str | None = None,
    ) -> list["ActionResult"]: ...
