"""SDK 错误模型（Python）。

约束：
- 对外抛出的异常必须可序列化（to_dict），且不包含鉴权私钥原文。
- 错误需携带必要上下文（operation_id、request_id、HTTP status、api_code 等）。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ErrorContext:
    """错误上下文（用于日志、hook 与排障）。"""

    request_id: str
    operation_id: str
    method: str
    path: str
    url: str
    status_code: int | None = None
    api_code: int | str | None = None


class WkteamError(RuntimeError):
    """SDK 统一错误基类。"""

    def __init__(self, message: str, *, context: ErrorContext, cause: BaseException | None = None) -> None:
        super().__init__(message)
        self.context = context
        self.cause = cause

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.__class__.__name__,
            "message": str(self),
            "context": {
                "request_id": self.context.request_id,
                "operation_id": self.context.operation_id,
                "method": self.context.method,
                "path": self.context.path,
                "url": self.context.url,
                "status_code": self.context.status_code,
                "api_code": self.context.api_code,
            },
            "cause": repr(self.cause) if self.cause else None,
        }


class WkteamValidationError(WkteamError):
    """输入参数或配置校验失败。"""


class WkteamNetworkError(WkteamError):
    """网络层错误（DNS/连接失败/连接重置等）。"""


class WkteamTimeoutError(WkteamError):
    """请求超时。"""


class WkteamHttpError(WkteamError):
    """HTTP 非 2xx。"""


class WkteamParseError(WkteamError):
    """响应解析失败（例如 JSON 无法解析或 envelope 缺字段）。"""


class WkteamApiBusinessError(WkteamError):
    """业务错误：HTTP 200 但 code != success。"""

    def __init__(
        self,
        message: str,
        *,
        context: ErrorContext,
        api_code: int | str | None,
        api_message: str | None,
        raw: Any,
        cause: BaseException | None = None,
    ) -> None:
        super().__init__(message, context=context, cause=cause)
        self.api_code = api_code
        self.api_message = api_message
        self.raw = raw

    def to_dict(self) -> dict[str, Any]:
        base = super().to_dict()
        base["context"]["api_code"] = self.api_code
        base["api_message"] = self.api_message
        base["raw"] = self.raw
        return base

