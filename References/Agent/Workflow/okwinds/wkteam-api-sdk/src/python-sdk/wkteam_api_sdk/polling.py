"""轮询 helper（用于“异步发送/异步下载”等接口模式）。

离线文档中典型模式：
1) 发起任务（返回 taskId 或类似字段）
2) 轮询查询结果（建议每隔 1~2 秒）
3) 或通过回调消息获取完成通知
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar


T = TypeVar("T")


def poll_until(
    *,
    run: Callable[[], T],
    is_done: Callable[[T], bool],
    initial_delay_ms: int = 500,
    interval_ms: int = 1000,
    timeout_ms: int = 60000,
    max_attempts: int | None = None,
) -> T:
    """同步轮询直到条件满足或超时。

    Args:
        run: 执行一次轮询请求的函数。
        is_done: 判定结果是否完成的函数。
        initial_delay_ms: 首次轮询前等待时间。
        interval_ms: 轮询间隔。
        timeout_ms: 总超时。
        max_attempts: 最大尝试次数（包含首次）。为 None 时由 timeout 控制。

    Returns:
        最后一次 `run()` 的结果（通常为完成态）。

    Raises:
        TimeoutError: 超时仍未完成。
    """

    started = time.time()
    attempts = 0
    if initial_delay_ms > 0:
        time.sleep(initial_delay_ms / 1000)

    while True:
        attempts += 1
        res = run()
        if is_done(res):
            return res

        if max_attempts is not None and attempts >= max_attempts:
            raise TimeoutError("poll_until 超过最大尝试次数仍未完成")

        if (time.time() - started) * 1000 >= timeout_ms:
            raise TimeoutError("poll_until 超时仍未完成")

        if interval_ms > 0:
            time.sleep(interval_ms / 1000)


async def async_poll_until(
    *,
    run: Callable[[], Awaitable[T]],
    is_done: Callable[[T], bool],
    initial_delay_ms: int = 500,
    interval_ms: int = 1000,
    timeout_ms: int = 60000,
    max_attempts: int | None = None,
) -> T:
    """异步轮询直到条件满足或超时。"""

    started = time.time()
    attempts = 0
    if initial_delay_ms > 0:
        await asyncio.sleep(initial_delay_ms / 1000)

    while True:
        attempts += 1
        res = await run()
        if is_done(res):
            return res

        if max_attempts is not None and attempts >= max_attempts:
            raise TimeoutError("async_poll_until 超过最大尝试次数仍未完成")

        if (time.time() - started) * 1000 >= timeout_ms:
            raise TimeoutError("async_poll_until 超时仍未完成")

        if interval_ms > 0:
            await asyncio.sleep(interval_ms / 1000)


__all__ = ["poll_until", "async_poll_until"]

