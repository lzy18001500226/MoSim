"""脱敏工具（最小实现：header 脱敏）。"""

from __future__ import annotations

from collections.abc import Mapping


def redact_headers(
    headers: Mapping[str, str],
    *,
    enabled: bool,
    header_names: tuple[str, ...],
    replacement: str = "***REDACTED***",
) -> dict[str, str]:
    """对敏感 header 做脱敏。

    Args:
        headers: 原始 headers（key 不区分大小写）
        enabled: 是否启用
        header_names: 需要脱敏的 header 名称（小写）
        replacement: 替换文本

    Returns:
        新 dict（不会修改输入对象）。
    """

    if not enabled:
        return dict(headers)

    targets = {h.lower() for h in header_names}
    out: dict[str, str] = {}
    for k, v in headers.items():
        if k.lower() in targets:
            out[k] = replacement
        else:
            out[k] = v
    return out

