"""回调 payload 解析与去重 key helper。

权威来源：`docs/api/api-wen-dang2/xiao-xi-jie-shou/shou-xiao-xi/callback.md`
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def parse_callback(payload: Mapping[str, Any] | str | bytes) -> dict[str, Any]:
    """解析回调 payload 并返回规范化结构。

    Args:
        payload: dict / JSON 字符串 / bytes。

    Returns:
        规范化 dict（尽量保持字段原样，不做业务解释）。

    Raises:
        ValueError: payload 非法或缺少必要字段。
    """

    if isinstance(payload, (str, bytes)):
        try:
            obj = json.loads(payload)
        except Exception as exc:  # noqa: BLE001
            raise ValueError("callback payload JSON 解析失败") from exc
    else:
        obj = dict(payload)

    if not isinstance(obj, dict):
        raise ValueError("callback payload 必须为 JSON 对象")

    data = obj.get("data")
    if data is not None and not isinstance(data, dict):
        raise ValueError("callback payload.data 必须为对象")

    message_type = obj.get("messageType")
    wc_id = obj.get("wcId")

    if message_type is None:
        raise ValueError("callback payload 缺少 messageType")
    if wc_id is None:
        # 文档中 wcId 为必填，但部分网关可能不同；保持严格以尽早暴露问题
        raise ValueError("callback payload 缺少 wcId")

    normalized: dict[str, Any] = {
        "wcId": wc_id,
        "account": obj.get("account"),
        "messageType": str(message_type),
        "data": data or {},
    }
    return normalized


def dedup_key(payload: Mapping[str, Any] | str | bytes) -> str:
    """生成消息去重 key。

    文档提示：由于重放/重连等原因可能重复推送历史消息，调用方必须排重；
    推荐使用 `data.newMsgId` 或 `data.timestamp`。
    """

    obj = parse_callback(payload)
    data = obj.get("data") or {}
    if not isinstance(data, dict):
        data = {}

    new_msg_id = data.get("newMsgId")
    msg_id = data.get("msgId")
    ts = data.get("timestamp")
    wc_id = obj.get("wcId")
    mtype = obj.get("messageType")

    if new_msg_id is not None:
        return f"wkteam:{wc_id}:{mtype}:newMsgId:{new_msg_id}"
    if msg_id is not None:
        return f"wkteam:{wc_id}:{mtype}:msgId:{msg_id}"
    if ts is not None:
        return f"wkteam:{wc_id}:{mtype}:ts:{ts}"
    return f"wkteam:{wc_id}:{mtype}:unknown"


__all__ = ["parse_callback", "dedup_key"]

