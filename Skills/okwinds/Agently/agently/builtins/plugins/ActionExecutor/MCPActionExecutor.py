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

import json
from typing import Any


class MCPActionExecutor:
    name = "MCPActionExecutor"
    DEFAULT_SETTINGS = {}

    kind = "mcp"
    sandboxed = False

    def __init__(self, action_id: str, transport: Any):
        self.action_id = action_id
        self.transport = transport

    @staticmethod
    def _on_register():
        pass

    @staticmethod
    def _on_unregister():
        pass

    async def execute(self, *, spec, action_call, policy, settings) -> Any:
        _ = (spec, policy, settings)
        from fastmcp import Client
        from mcp.types import AudioContent, EmbeddedResource, ImageContent, ResourceLink, TextContent

        action_input = action_call.get("action_input", {})
        if not isinstance(action_input, dict):
            action_input = {}
        environment_resources = action_call.get("execution_environment_resources", {})
        transport = self.transport
        if isinstance(environment_resources, dict) and self.action_id in environment_resources:
            transport = environment_resources[self.action_id]

        async with Client(transport) as client:  # type: ignore[arg-type]
            mcp_result = await client.call_tool(
                name=self.action_id,
                arguments=action_input,
                raise_on_error=False,
            )
            if mcp_result.is_error:
                return {"error": mcp_result.content[0].text}  # type: ignore[index]
            if mcp_result.structured_content:
                return mcp_result.structured_content
            try:
                result = mcp_result.content[0]
                if isinstance(result, TextContent):
                    try:
                        return json.loads(result.text)
                    except json.JSONDecodeError:
                        return result.text
                if isinstance(result, (ImageContent, AudioContent, ResourceLink, EmbeddedResource)):
                    return result.model_dump()
            except Exception:
                return None
