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

from typing import Any


class PythonSandboxActionExecutor:
    name = "PythonSandboxActionExecutor"
    DEFAULT_SETTINGS = {}

    kind = "python_sandbox"
    sandboxed = True

    def __init__(
        self,
        *,
        preset_objects: dict[str, object] | None = None,
        base_vars: dict[str, Any] | None = None,
        allowed_return_types: list[type] | None = None,
    ):
        self.preset_objects = preset_objects
        self.base_vars = base_vars
        self.allowed_return_types = allowed_return_types

    @staticmethod
    def _on_register():
        pass

    @staticmethod
    def _on_unregister():
        pass

    async def execute(self, *, spec, action_call, policy, settings) -> Any:
        _ = (spec, policy, settings)
        from agently.utils import PythonSandbox

        action_input = action_call.get("action_input", {})
        python_code = ""
        if isinstance(action_input, dict):
            raw_code = action_input.get("python_code", "")
            if isinstance(raw_code, list):
                python_code = "\n".join(str(line) for line in raw_code)
            else:
                python_code = str(raw_code)
        action_id = str(spec.get("action_id", "python_sandbox"))
        environment_resources = action_call.get("execution_environment_resources", {})
        if isinstance(environment_resources, dict):
            sandbox = environment_resources.get(action_id)
            if sandbox is not None and hasattr(sandbox, "run"):
                return sandbox.run(python_code)

        sandbox_kwargs = {
            "preset_objects": self.preset_objects,
            "base_vars": self.base_vars,
        }
        if self.allowed_return_types is not None:
            sandbox_kwargs["allowed_return_types"] = self.allowed_return_types
        sandbox = PythonSandbox(**sandbox_kwargs)
        return sandbox.run(python_code)
