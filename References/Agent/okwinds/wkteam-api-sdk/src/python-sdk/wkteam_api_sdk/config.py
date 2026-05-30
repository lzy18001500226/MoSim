"""SDK 配置结构与默认值（Python）。"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any, Literal


RetryOn = Literal["network", "timeout", "http5xx", "http429"]
LogLevel = Literal["silent", "error", "warn", "info", "debug"]


@dataclass(frozen=True, slots=True)
class RetryConfig:
    """重试策略（分类重试：safe vs side_effect）。"""

    enabled: bool = True
    max_attempts: int = 2
    backoff_ms: int | Callable[[int], int] = 200
    retry_on: tuple[RetryOn, ...] = ("network", "timeout", "http5xx")
    allow_side_effect: bool = False


@dataclass(frozen=True, slots=True)
class Hooks:
    """生命周期 hook（用于可观测性/审计/埋点）。"""

    on_request: Callable[[dict[str, Any]], None] | None = None
    on_response: Callable[[dict[str, Any]], None] | None = None
    on_retry: Callable[[dict[str, Any]], None] | None = None
    on_error: Callable[[dict[str, Any]], None] | None = None


AuthorizationSync = str | Callable[[], str]
AuthorizationAsync = str | Callable[[], str | Awaitable[str]]

TransportSync = Callable[[dict[str, Any]], dict[str, Any]]
TransportAsync = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


@dataclass(frozen=True, slots=True)
class RedactionConfig:
    """脱敏配置（至少覆盖 Authorization header）。"""

    enabled: bool = True
    headers: tuple[str, ...] = ("authorization", "cookie")


@dataclass(frozen=True, slots=True)
class WkteamClientConfig:
    """客户端配置（sync）。"""

    base_url: str
    authorization: AuthorizationSync
    authorization_header_name: str = "Authorization"
    authorization_prefix: str | None = None
    timeout_ms: int = 15000
    retry: RetryConfig = RetryConfig()
    concurrency: int | None = None
    log_level: LogLevel = "info"
    logger: Any | None = None
    transport: TransportSync | None = None
    default_headers: Mapping[str, str] | None = None
    user_agent: str | None = None
    hooks: Hooks = Hooks()
    redaction: RedactionConfig = RedactionConfig()


@dataclass(frozen=True, slots=True)
class AsyncWkteamClientConfig:
    """客户端配置（async）。"""

    base_url: str
    authorization: AuthorizationAsync
    authorization_header_name: str = "Authorization"
    authorization_prefix: str | None = None
    timeout_ms: int = 15000
    retry: RetryConfig = RetryConfig()
    concurrency: int | None = None
    log_level: LogLevel = "info"
    logger: Any | None = None
    transport: TransportAsync | None = None
    default_headers: Mapping[str, str] | None = None
    user_agent: str | None = None
    hooks: Hooks = Hooks()
    redaction: RedactionConfig = RedactionConfig()


def normalize_base_url(base_url: str) -> str:
    """归一化 baseUrl（移除尾部 `/`）。"""

    b = (base_url or "").strip()
    if b.endswith("/"):
        return b[:-1]
    return b
