"""对外 Client（sync/async）。

约定：
- 对外入口类负责挂载 `client.api.*`（由 codegen 生成）。
- 请求管线逻辑在 `core_client.py`，避免 wrapper 重复实现。
"""

from __future__ import annotations

from typing import Any

from .config import AsyncWkteamClientConfig, AuthorizationAsync, AuthorizationSync, WkteamClientConfig
from .core_client import AsyncWkteamCoreClient, WkteamCoreClient
from .generated_api import AsyncWkteamApi, WkteamApi


class WkteamClient(WkteamCoreClient):
    """同步客户端（挂载 `client.api.*`）。"""

    api: WkteamApi

    def __init__(
        self,
        *,
        base_url: str,
        authorization: AuthorizationSync,
        **kwargs: Any,
    ) -> None:
        """创建同步客户端。

        Args:
            base_url: API baseUrl（必填）。
            authorization: Authorization 原始值（必填）或函数（用于动态读取/刷新）。
            **kwargs: 其余配置项（参见 `WkteamClientConfig`）。
        """

        cfg = WkteamClientConfig(base_url=base_url, authorization=authorization, **kwargs)
        super().__init__(cfg)
        self.api = WkteamApi(self)

    def __enter__(self) -> "WkteamClient":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()


class AsyncWkteamClient(AsyncWkteamCoreClient):
    """异步客户端（挂载 `client.api.*`）。"""

    api: AsyncWkteamApi

    def __init__(
        self,
        *,
        base_url: str,
        authorization: AuthorizationAsync,
        **kwargs: Any,
    ) -> None:
        """创建异步客户端。

        Args:
            base_url: API baseUrl（必填）。
            authorization: Authorization 原始值（必填）或函数（sync/async）。
            **kwargs: 其余配置项（参见 `AsyncWkteamClientConfig`）。
        """

        cfg = AsyncWkteamClientConfig(base_url=base_url, authorization=authorization, **kwargs)
        super().__init__(cfg)
        self.api = AsyncWkteamApi(self)

