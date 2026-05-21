"""生命周期 hook 的事件结构（可选）。

约定：
- hook 主要用于可观测性/审计/埋点，不应影响主流程（core_client 中会吞掉 hook 异常）。
- hook 的 payload 为 dict，字段尽量稳定；其中 headers 必须是脱敏后的版本。
"""

from __future__ import annotations

from typing import Any, TypedDict


class HookBasePayload(TypedDict):
    request_id: str
    operation_id: str
    method: str
    path: str
    attempt: int
    headers: dict[str, str]


class HookResponsePayload(HookBasePayload, total=False):
    status: int
    elapsed_ms: int


class HookRetryPayload(HookBasePayload, total=False):
    backoff_ms: int
    error: dict[str, Any]


class HookErrorPayload(HookBasePayload, total=False):
    error: dict[str, Any]


__all__ = [
    "HookBasePayload",
    "HookResponsePayload",
    "HookRetryPayload",
    "HookErrorPayload",
]

