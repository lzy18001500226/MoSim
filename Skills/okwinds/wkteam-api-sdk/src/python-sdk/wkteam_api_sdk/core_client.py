"""核心请求管线（sync/async）。

本模块不包含具体 endpoint wrapper；wrappers 由 `generated_api.py` 生成并调用 `call()`。
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any, Literal, Protocol

import httpx

from .config import (
    AsyncWkteamClientConfig,
    Hooks,
    LogLevel,
    RetryConfig,
    WkteamClientConfig,
    normalize_base_url,
)
from .errors import (
    ErrorContext,
    WkteamApiBusinessError,
    WkteamHttpError,
    WkteamNetworkError,
    WkteamParseError,
    WkteamTimeoutError,
    WkteamValidationError,
)
from .redaction import redact_headers


RetryCategory = Literal["safe", "side_effect"]


class Logger(Protocol):
    """日志器协议（可注入）。"""

    def debug(self, msg: str, extra: Mapping[str, Any] | None = None) -> None: ...
    def info(self, msg: str, extra: Mapping[str, Any] | None = None) -> None: ...
    def warn(self, msg: str, extra: Mapping[str, Any] | None = None) -> None: ...
    def error(self, msg: str, extra: Mapping[str, Any] | None = None) -> None: ...


class StdLogger:
    """基于标准库 logging 的 Logger 适配器。"""

    def __init__(self, name: str = "wkteam_api_sdk") -> None:
        self._logger = logging.getLogger(name)

    def debug(self, msg: str, extra: Mapping[str, Any] | None = None) -> None:
        self._logger.debug(msg, extra={"extra": dict(extra or {})})

    def info(self, msg: str, extra: Mapping[str, Any] | None = None) -> None:
        self._logger.info(msg, extra={"extra": dict(extra or {})})

    def warn(self, msg: str, extra: Mapping[str, Any] | None = None) -> None:
        self._logger.warning(msg, extra={"extra": dict(extra or {})})

    def error(self, msg: str, extra: Mapping[str, Any] | None = None) -> None:
        self._logger.error(msg, extra={"extra": dict(extra or {})})


def _log_level_rank(level: LogLevel) -> int:
    return {"silent": 0, "error": 1, "warn": 2, "info": 3, "debug": 4}.get(level, 3)


def _should_log(level: LogLevel, kind: Literal["error", "warn", "info", "debug"]) -> bool:
    return _log_level_rank(level) >= _log_level_rank(kind)  # type: ignore[arg-type]


def _join_url(base_url: str, path: str) -> str:
    if not path.startswith("/"):
        return f"{base_url}/{path}"
    return f"{base_url}{path}"


def _default_request_id() -> str:
    return f"req_{random.random():.8f}_{int(time.time() * 1000)}".replace(".", "")


def _sleep_ms_sync(ms: int) -> None:
    if ms <= 0:
        return
    time.sleep(ms / 1000)


async def _sleep_ms_async(ms: int) -> None:
    if ms <= 0:
        return
    await asyncio.sleep(ms / 1000)


def _resolve_backoff_ms(backoff: int | Callable[[int], int], attempt: int) -> int:
    if isinstance(backoff, int):
        return backoff
    return int(backoff(attempt))


def _is_success_code(code: Any) -> bool:
    if code == 1000:
        return True
    if isinstance(code, str) and code.strip() == "1000":
        return True
    return False


@dataclass(frozen=True, slots=True)
class RequestOptions:
    """单次请求的可选覆盖项。"""

    request_id: str | None = None
    timeout_ms: int | None = None
    headers: Mapping[str, str] | None = None


TransportResponse = dict[str, Any]
TransportSync = Callable[[dict[str, Any]], TransportResponse]
TransportAsync = Callable[[dict[str, Any]], Awaitable[TransportResponse]]


def _default_transport_sync(http_client: httpx.Client) -> TransportSync:
    def _transport(req: dict[str, Any]) -> TransportResponse:
        resp = http_client.request(
            method=req["method"],
            url=req["url"],
            headers=dict(req.get("headers") or {}),
            content=req.get("body_text"),
            timeout=req.get("timeout_ms", 15000) / 1000,
        )
        return {"status": resp.status_code, "headers": dict(resp.headers), "body_text": resp.text}

    return _transport


def _default_transport_async(http_client: httpx.AsyncClient) -> TransportAsync:
    async def _transport(req: dict[str, Any]) -> TransportResponse:
        resp = await http_client.request(
            method=req["method"],
            url=req["url"],
            headers=dict(req.get("headers") or {}),
            content=req.get("body_text"),
            timeout=req.get("timeout_ms", 15000) / 1000,
        )
        return {"status": resp.status_code, "headers": dict(resp.headers), "body_text": resp.text}

    return _transport


class WkteamCoreClient:
    """同步 Core Client：负责请求管线与通用能力。"""

    def __init__(self, config: WkteamClientConfig | Mapping[str, Any]) -> None:
        cfg = config if isinstance(config, WkteamClientConfig) else WkteamClientConfig(**dict(config))
        if not cfg.base_url:
            raise WkteamValidationError(
                "base_url 不能为空",
                context=ErrorContext(
                    request_id="init",
                    operation_id="init",
                    method="INIT",
                    path="",
                    url="",
                ),
            )
        if not cfg.authorization:
            raise WkteamValidationError(
                "authorization 不能为空",
                context=ErrorContext(
                    request_id="init",
                    operation_id="init",
                    method="INIT",
                    path="",
                    url="",
                ),
            )

        self._config = cfg
        self._base_url = normalize_base_url(cfg.base_url)
        self._http_client = httpx.Client()
        self._transport: TransportSync = cfg.transport or _default_transport_sync(self._http_client)
        self._logger: Logger = cfg.logger or StdLogger()
        self._semaphore = None
        if isinstance(cfg.concurrency, int) and cfg.concurrency > 0:
            import threading

            self._semaphore = threading.Semaphore(cfg.concurrency)

    def close(self) -> None:
        """关闭底层资源（httpx.Client）。"""

        self._http_client.close()

    def _resolve_authorization(self) -> str:
        raw = self._config.authorization() if callable(self._config.authorization) else self._config.authorization
        prefix = self._config.authorization_prefix
        return f"{prefix}{raw}" if prefix else raw

    def call(
        self,
        *,
        operation_id: str,
        method: str,
        path: str,
        requires_auth: bool,
        retry_category: RetryCategory,
        params: Mapping[str, Any] | None,
        request_options: RequestOptions | None,
    ) -> Any:
        """发起请求并返回 envelope.data（成功）或抛出 SDK 错误。"""

        request_id = request_options.request_id if request_options and request_options.request_id else _default_request_id()
        url = _join_url(self._base_url, path)

        headers: dict[str, str] = {}
        if self._config.default_headers:
            headers.update(dict(self._config.default_headers))
        if request_options and request_options.headers:
            headers.update(dict(request_options.headers))
        if self._config.user_agent:
            headers["user-agent"] = self._config.user_agent

        if requires_auth:
            headers[self._config.authorization_header_name] = self._resolve_authorization()

        body_text: str | None = None
        is_get = method.upper() == "GET"
        if is_get:
            # 当前离线文档均为 POST；这里保留通用编码逻辑
            if params:
                from urllib.parse import urlencode

                def _flatten() -> list[tuple[str, str]]:
                    out: list[tuple[str, str]] = []
                    for k, v in params.items():
                        if v is None:
                            continue
                        if isinstance(v, list):
                            out.extend([(k, str(i)) for i in v])
                        elif isinstance(v, dict):
                            out.append((k, json.dumps(v, ensure_ascii=False)))
                        else:
                            out.append((k, str(v)))
                    return out

                q = urlencode(_flatten())
                if q:
                    url = f"{url}?{q}"
        else:
            body_text = json.dumps(dict(params or {}), ensure_ascii=False)
            headers["content-type"] = "application/json"

        redacted_headers = redact_headers(
            headers,
            enabled=self._config.redaction.enabled,
            header_names=self._config.redaction.headers,
        )

        timeout_ms = (
            request_options.timeout_ms
            if request_options and request_options.timeout_ms is not None
            else self._config.timeout_ms
        )

        retry_cfg: RetryConfig = self._config.retry
        can_retry_endpoint = retry_category == "safe" or retry_cfg.allow_side_effect
        max_attempts = max(1, int(retry_cfg.max_attempts))

        for attempt in range(1, max_attempts + 1):
            started_at_ms = int(time.time() * 1000)
            self._emit_hook(self._config.hooks, "on_request", request_id, operation_id, method, path, attempt, redacted_headers)
            if _should_log(self._config.log_level, "debug"):
                self._logger.debug(
                    "wkteam.http.request",
                    extra={"request_id": request_id, "operation_id": operation_id, "method": method, "path": path, "attempt": attempt},
                )

            release = None
            try:
                if self._semaphore:
                    self._semaphore.acquire()
                    release = self._semaphore.release

                resp = self._transport(
                    {"url": url, "method": method, "headers": headers, "body_text": body_text, "timeout_ms": timeout_ms}
                )
                return self._handle_response(
                    request_id=request_id,
                    operation_id=operation_id,
                    method=method,
                    path=path,
                    url=url,
                    attempt=attempt,
                    started_at_ms=started_at_ms,
                    response=resp,
                    redacted_headers=redacted_headers,
                )
            except Exception as exc:  # noqa: BLE001
                err = self._map_exception(
                    exc,
                    request_id=request_id,
                    operation_id=operation_id,
                    method=method,
                    path=path,
                    url=url,
                )
                if attempt < max_attempts and retry_cfg.enabled and can_retry_endpoint and self._should_retry_error(err, retry_cfg):
                    backoff = _resolve_backoff_ms(retry_cfg.backoff_ms, attempt)
                    self._emit_hook(
                        self._config.hooks,
                        "on_retry",
                        request_id,
                        operation_id,
                        method,
                        path,
                        attempt,
                        redacted_headers,
                        extra={"backoff_ms": backoff, "error": err.to_dict()},
                    )
                    _sleep_ms_sync(backoff)
                    continue
                self._emit_hook(
                    self._config.hooks,
                    "on_error",
                    request_id,
                    operation_id,
                    method,
                    path,
                    attempt,
                    redacted_headers,
                    extra={"error": err.to_dict()},
                )
                raise err from exc
            finally:
                if release:
                    release()

        raise RuntimeError("unreachable")

    def _emit_hook(
        self,
        hooks: Hooks,
        hook_name: Literal["on_request", "on_response", "on_retry", "on_error"],
        request_id: str,
        operation_id: str,
        method: str,
        path: str,
        attempt: int,
        headers: Mapping[str, str],
        *,
        extra: Mapping[str, Any] | None = None,
    ) -> None:
        fn = getattr(hooks, hook_name, None)
        if not fn:
            return
        payload: dict[str, Any] = {
            "request_id": request_id,
            "operation_id": operation_id,
            "method": method,
            "path": path,
            "attempt": attempt,
            "headers": dict(headers),
        }
        if extra:
            payload.update(dict(extra))
        try:
            fn(payload)
        except Exception:  # noqa: BLE001
            # hook 不应影响主流程
            return

    def _should_retry_error(self, err: Exception, retry_cfg: RetryConfig) -> bool:
        retry_on = set(retry_cfg.retry_on)
        if isinstance(err, WkteamNetworkError):
            return "network" in retry_on
        if isinstance(err, WkteamTimeoutError):
            return "timeout" in retry_on
        if isinstance(err, WkteamHttpError) and err.context.status_code:
            if err.context.status_code == 429:
                return "http429" in retry_on
            if 500 <= err.context.status_code <= 599:
                return "http5xx" in retry_on
        return False

    def _map_exception(
        self,
        exc: BaseException,
        *,
        request_id: str,
        operation_id: str,
        method: str,
        path: str,
        url: str,
    ) -> Exception:
        ctx = ErrorContext(request_id=request_id, operation_id=operation_id, method=method, path=path, url=url)
        if isinstance(
            exc,
            (
                WkteamValidationError,
                WkteamNetworkError,
                WkteamTimeoutError,
                WkteamHttpError,
                WkteamParseError,
                WkteamApiBusinessError,
            ),
        ):
            return exc  # type: ignore[return-value]
        if isinstance(exc, httpx.TimeoutException):
            return WkteamTimeoutError("请求超时", context=ctx, cause=exc)
        if isinstance(exc, httpx.RequestError):
            return WkteamNetworkError("网络错误", context=ctx, cause=exc)
        return WkteamNetworkError("未知网络错误", context=ctx, cause=exc)

    def _handle_response(
        self,
        *,
        request_id: str,
        operation_id: str,
        method: str,
        path: str,
        url: str,
        attempt: int,
        started_at_ms: int,
        response: TransportResponse,
        redacted_headers: Mapping[str, str],
    ) -> Any:
        status = int(response.get("status") or 0)
        body_text = str(response.get("body_text") or "")

        elapsed_ms = int(time.time() * 1000) - started_at_ms
        self._emit_hook(
            self._config.hooks,
            "on_response",
            request_id,
            operation_id,
            method,
            path,
            attempt,
            redacted_headers,
            extra={"status": status, "elapsed_ms": elapsed_ms},
        )

        if status < 200 or status >= 300:
            ctx = ErrorContext(
                request_id=request_id,
                operation_id=operation_id,
                method=method,
                path=path,
                url=url,
                status_code=status,
            )
            raise WkteamHttpError(f"HTTP 状态码异常：{status}", context=ctx)

        try:
            obj = json.loads(body_text) if body_text else {}
        except Exception as exc:  # noqa: BLE001
            ctx = ErrorContext(request_id=request_id, operation_id=operation_id, method=method, path=path, url=url, status_code=status)
            raise WkteamParseError("响应 JSON 解析失败", context=ctx, cause=exc) from exc

        if not isinstance(obj, dict):
            ctx = ErrorContext(request_id=request_id, operation_id=operation_id, method=method, path=path, url=url, status_code=status)
            raise WkteamParseError("响应不是 JSON 对象", context=ctx)

        code = obj.get("code")
        msg = obj.get("message") or obj.get("msg")
        data = obj.get("data")

        if _is_success_code(code):
            return data

        ctx = ErrorContext(
            request_id=request_id,
            operation_id=operation_id,
            method=method,
            path=path,
            url=url,
            status_code=status,
            api_code=code,
        )
        raise WkteamApiBusinessError(
            "API 业务错误",
            context=ctx,
            api_code=code,
            api_message=str(msg) if msg is not None else None,
            raw=obj,
        )


class AsyncWkteamCoreClient:
    """异步 Core Client：负责请求管线与通用能力。"""

    def __init__(self, config: AsyncWkteamClientConfig | Mapping[str, Any]) -> None:
        cfg = config if isinstance(config, AsyncWkteamClientConfig) else AsyncWkteamClientConfig(**dict(config))
        if not cfg.base_url:
            raise WkteamValidationError(
                "base_url 不能为空",
                context=ErrorContext(
                    request_id="init",
                    operation_id="init",
                    method="INIT",
                    path="",
                    url="",
                ),
            )
        if not cfg.authorization:
            raise WkteamValidationError(
                "authorization 不能为空",
                context=ErrorContext(
                    request_id="init",
                    operation_id="init",
                    method="INIT",
                    path="",
                    url="",
                ),
            )

        self._config = cfg
        self._base_url = normalize_base_url(cfg.base_url)
        self._http_client = httpx.AsyncClient()
        self._transport: TransportAsync = cfg.transport or _default_transport_async(self._http_client)
        self._logger: Logger = cfg.logger or StdLogger()
        self._semaphore: asyncio.Semaphore | None = None
        if isinstance(cfg.concurrency, int) and cfg.concurrency > 0:
            self._semaphore = asyncio.Semaphore(cfg.concurrency)

    async def aclose(self) -> None:
        """关闭底层资源（httpx.AsyncClient）。"""

        await self._http_client.aclose()

    async def __aenter__(self) -> "AsyncWkteamCoreClient":
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        await self.aclose()

    async def _resolve_authorization(self) -> str:
        raw = self._config.authorization
        if callable(raw):
            value = raw()
            raw_value = await value if isinstance(value, Awaitable) else value
        else:
            raw_value = raw
        prefix = self._config.authorization_prefix
        return f"{prefix}{raw_value}" if prefix else str(raw_value)

    async def call(
        self,
        *,
        operation_id: str,
        method: str,
        path: str,
        requires_auth: bool,
        retry_category: RetryCategory,
        params: Mapping[str, Any] | None,
        request_options: RequestOptions | None,
    ) -> Any:
        request_id = request_options.request_id if request_options and request_options.request_id else _default_request_id()
        url = _join_url(self._base_url, path)

        headers: dict[str, str] = {}
        if self._config.default_headers:
            headers.update(dict(self._config.default_headers))
        if request_options and request_options.headers:
            headers.update(dict(request_options.headers))
        if self._config.user_agent:
            headers["user-agent"] = self._config.user_agent

        if requires_auth:
            headers[self._config.authorization_header_name] = await self._resolve_authorization()

        body_text: str | None = None
        is_get = method.upper() == "GET"
        if is_get:
            if params:
                from urllib.parse import urlencode

                def _flatten() -> list[tuple[str, str]]:
                    out: list[tuple[str, str]] = []
                    for k, v in params.items():
                        if v is None:
                            continue
                        if isinstance(v, list):
                            out.extend([(k, str(i)) for i in v])
                        elif isinstance(v, dict):
                            out.append((k, json.dumps(v, ensure_ascii=False)))
                        else:
                            out.append((k, str(v)))
                    return out

                q = urlencode(_flatten())
                if q:
                    url = f"{url}?{q}"
        else:
            body_text = json.dumps(dict(params or {}), ensure_ascii=False)
            headers["content-type"] = "application/json"

        redacted_headers = redact_headers(
            headers,
            enabled=self._config.redaction.enabled,
            header_names=self._config.redaction.headers,
        )

        timeout_ms = (
            request_options.timeout_ms
            if request_options and request_options.timeout_ms is not None
            else self._config.timeout_ms
        )

        retry_cfg: RetryConfig = self._config.retry
        can_retry_endpoint = retry_category == "safe" or retry_cfg.allow_side_effect
        max_attempts = max(1, int(retry_cfg.max_attempts))

        for attempt in range(1, max_attempts + 1):
            started_at_ms = int(time.time() * 1000)
            self._emit_hook(self._config.hooks, "on_request", request_id, operation_id, method, path, attempt, redacted_headers)
            if _should_log(self._config.log_level, "debug"):
                self._logger.debug(
                    "wkteam.http.request",
                    extra={"request_id": request_id, "operation_id": operation_id, "method": method, "path": path, "attempt": attempt},
                )

            try:
                if self._semaphore:
                    async with self._semaphore:
                        resp = await self._transport(
                            {"url": url, "method": method, "headers": headers, "body_text": body_text, "timeout_ms": timeout_ms}
                        )
                else:
                    resp = await self._transport(
                        {"url": url, "method": method, "headers": headers, "body_text": body_text, "timeout_ms": timeout_ms}
                    )
                return self._handle_response(
                    request_id=request_id,
                    operation_id=operation_id,
                    method=method,
                    path=path,
                    url=url,
                    attempt=attempt,
                    started_at_ms=started_at_ms,
                    response=resp,
                    redacted_headers=redacted_headers,
                )
            except Exception as exc:  # noqa: BLE001
                err = self._map_exception(
                    exc,
                    request_id=request_id,
                    operation_id=operation_id,
                    method=method,
                    path=path,
                    url=url,
                )
                if attempt < max_attempts and retry_cfg.enabled and can_retry_endpoint and self._should_retry_error(err, retry_cfg):
                    backoff = _resolve_backoff_ms(retry_cfg.backoff_ms, attempt)
                    self._emit_hook(
                        self._config.hooks,
                        "on_retry",
                        request_id,
                        operation_id,
                        method,
                        path,
                        attempt,
                        redacted_headers,
                        extra={"backoff_ms": backoff, "error": err.to_dict()},
                    )
                    await _sleep_ms_async(backoff)
                    continue
                self._emit_hook(
                    self._config.hooks,
                    "on_error",
                    request_id,
                    operation_id,
                    method,
                    path,
                    attempt,
                    redacted_headers,
                    extra={"error": err.to_dict()},
                )
                raise err from exc

        raise RuntimeError("unreachable")

    def _emit_hook(
        self,
        hooks: Hooks,
        hook_name: Literal["on_request", "on_response", "on_retry", "on_error"],
        request_id: str,
        operation_id: str,
        method: str,
        path: str,
        attempt: int,
        headers: Mapping[str, str],
        *,
        extra: Mapping[str, Any] | None = None,
    ) -> None:
        fn = getattr(hooks, hook_name, None)
        if not fn:
            return
        payload: dict[str, Any] = {
            "request_id": request_id,
            "operation_id": operation_id,
            "method": method,
            "path": path,
            "attempt": attempt,
            "headers": dict(headers),
        }
        if extra:
            payload.update(dict(extra))
        try:
            fn(payload)
        except Exception:  # noqa: BLE001
            return

    def _should_retry_error(self, err: Exception, retry_cfg: RetryConfig) -> bool:
        retry_on = set(retry_cfg.retry_on)
        if isinstance(err, WkteamNetworkError):
            return "network" in retry_on
        if isinstance(err, WkteamTimeoutError):
            return "timeout" in retry_on
        if isinstance(err, WkteamHttpError) and err.context.status_code:
            if err.context.status_code == 429:
                return "http429" in retry_on
            if 500 <= err.context.status_code <= 599:
                return "http5xx" in retry_on
        return False

    def _map_exception(
        self,
        exc: BaseException,
        *,
        request_id: str,
        operation_id: str,
        method: str,
        path: str,
        url: str,
    ) -> Exception:
        ctx = ErrorContext(request_id=request_id, operation_id=operation_id, method=method, path=path, url=url)
        if isinstance(
            exc,
            (
                WkteamValidationError,
                WkteamNetworkError,
                WkteamTimeoutError,
                WkteamHttpError,
                WkteamParseError,
                WkteamApiBusinessError,
            ),
        ):
            return exc  # type: ignore[return-value]
        if isinstance(exc, httpx.TimeoutException):
            return WkteamTimeoutError("请求超时", context=ctx, cause=exc)
        if isinstance(exc, httpx.RequestError):
            return WkteamNetworkError("网络错误", context=ctx, cause=exc)
        return WkteamNetworkError("未知网络错误", context=ctx, cause=exc)

    def _handle_response(
        self,
        *,
        request_id: str,
        operation_id: str,
        method: str,
        path: str,
        url: str,
        attempt: int,
        started_at_ms: int,
        response: TransportResponse,
        redacted_headers: Mapping[str, str],
    ) -> Any:
        status = int(response.get("status") or 0)
        body_text = str(response.get("body_text") or "")

        elapsed_ms = int(time.time() * 1000) - started_at_ms
        self._emit_hook(
            self._config.hooks,
            "on_response",
            request_id,
            operation_id,
            method,
            path,
            attempt,
            redacted_headers,
            extra={"status": status, "elapsed_ms": elapsed_ms},
        )

        if status < 200 or status >= 300:
            ctx = ErrorContext(
                request_id=request_id,
                operation_id=operation_id,
                method=method,
                path=path,
                url=url,
                status_code=status,
            )
            raise WkteamHttpError(f"HTTP 状态码异常：{status}", context=ctx)

        try:
            obj = json.loads(body_text) if body_text else {}
        except Exception as exc:  # noqa: BLE001
            ctx = ErrorContext(request_id=request_id, operation_id=operation_id, method=method, path=path, url=url, status_code=status)
            raise WkteamParseError("响应 JSON 解析失败", context=ctx, cause=exc) from exc

        if not isinstance(obj, dict):
            ctx = ErrorContext(request_id=request_id, operation_id=operation_id, method=method, path=path, url=url, status_code=status)
            raise WkteamParseError("响应不是 JSON 对象", context=ctx)

        code = obj.get("code")
        msg = obj.get("message") or obj.get("msg")
        data = obj.get("data")

        if _is_success_code(code):
            return data

        ctx = ErrorContext(
            request_id=request_id,
            operation_id=operation_id,
            method=method,
            path=path,
            url=url,
            status_code=status,
            api_code=code,
        )
        raise WkteamApiBusinessError(
            "API 业务错误",
            context=ctx,
            api_code=code,
            api_message=str(msg) if msg is not None else None,
            raw=obj,
        )


__all__ = ["RequestOptions", "WkteamCoreClient", "AsyncWkteamCoreClient", "Logger"]
