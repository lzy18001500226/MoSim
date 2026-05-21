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

from typing import Any, Literal, TypeAlias

from typing_extensions import TypedDict


ExecutionEnvironmentKind: TypeAlias = Literal["mcp", "bash", "python"] | str
ExecutionEnvironmentScope: TypeAlias = Literal[
    "global",
    "agent",
    "session",
    "request",
    "execution",
    "action_call",
]
ExecutionEnvironmentStatus: TypeAlias = Literal[
    "declared",
    "pending_approval",
    "ensuring",
    "ready",
    "unhealthy",
    "releasing",
    "released",
    "failed",
]


class ExecutionEnvironmentPolicy(TypedDict, total=False):
    approval_mode: Literal["auto", "always", "never"]
    workspace_roots: list[str]
    path_allowlist: list[str]
    path_denylist: list[str]
    allowed_cmd_prefixes: list[str]
    network_mode: Literal["inherit", "enabled", "disabled"]
    timeout_seconds: float
    max_output_bytes: int
    read_only: bool
    allow_create: bool
    allow_update: bool
    allow_delete: bool
    auto_release: bool


class ExecutionEnvironmentRequirement(TypedDict, total=False):
    requirement_id: str
    kind: ExecutionEnvironmentKind
    scope: ExecutionEnvironmentScope
    owner_id: str
    resource_key: str
    config: dict[str, Any]
    policy: ExecutionEnvironmentPolicy
    reuse_key: str
    approval_required: bool
    health_check: dict[str, Any]
    meta: dict[str, Any]


class ExecutionEnvironmentHandle(TypedDict, total=False):
    handle_id: str
    requirement_id: str
    kind: ExecutionEnvironmentKind
    scope: ExecutionEnvironmentScope
    owner_id: str
    resource_key: str
    status: ExecutionEnvironmentStatus
    resource: Any
    policy: ExecutionEnvironmentPolicy
    ref_count: int
    meta: dict[str, Any]


class ExecutionEnvironmentDecision(TypedDict, total=False):
    approved: bool
    reason: str
    policy_override: ExecutionEnvironmentPolicy
    meta: dict[str, Any]
