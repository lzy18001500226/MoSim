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

from typing import Any, Protocol

from .base import AgentlyPlugin


class TaskDAGPlanner(AgentlyPlugin, Protocol):
    name: str
    DEFAULT_SETTINGS: dict[str, Any] = {}

    @staticmethod
    def _on_register(): ...

    @staticmethod
    def _on_unregister(): ...

    def output_schema(self) -> dict[str, Any]: ...

    def ensure_keys(self) -> list[str]: ...

    def instructions(self) -> list[str]: ...

    def plugin_constraints(self) -> dict[str, Any]: ...

    def validate_output(self, result: dict[str, Any], context: Any = None): ...

    def prepare_request(self, request: Any, graph_input: Any = None) -> Any: ...

    async def async_plan(
        self,
        request: Any,
        graph_input: Any = None,
        *,
        max_retries: int = 3,
    ) -> Any: ...

    def plan(
        self,
        request: Any,
        graph_input: Any = None,
        *,
        max_retries: int = 3,
    ) -> Any: ...
