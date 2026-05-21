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

if TYPE_CHECKING:
    from agently.types.data import ActionCall, ActionPolicy, ActionSpec
    from agently.utils import Settings


class ActionExecutor(AgentlyPlugin, Protocol):
    """
    Atomic action backend plugin.

    Implement this protocol when a third-party action changes only the execution
    backend, for example Docker, SandLock, a remote runner, or a vendor tool API.
    The dispatcher owns policy merging and result normalization; executors should
    focus on performing one action call.
    """

    kind: str
    sandboxed: bool

    def __init__(self, *args: Any, **kwargs: Any): ...

    async def execute(
        self,
        *,
        spec: "ActionSpec",
        action_call: "ActionCall",
        policy: "ActionPolicy",
        settings: "Settings",
    ) -> Any: ...
