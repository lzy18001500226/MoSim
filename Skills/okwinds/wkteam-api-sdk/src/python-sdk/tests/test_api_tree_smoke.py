from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx
import pytest

from wkteam_api_sdk import AsyncWkteamClient, WkteamClient
from wkteam_api_sdk.core_client import RequestOptions
from wkteam_api_sdk.errors import WkteamNetworkError
from wkteam_api_sdk.manifest import endpoint_defs


@dataclass(slots=True)
class CapturedRequest:
    url: str
    method: str
    headers: dict[str, str]
    body_text: str | None
    timeout_ms: int


class FakeTransport:
    def __init__(self) -> None:
        self.requests: list[CapturedRequest] = []

    def __call__(self, req: dict[str, Any]) -> dict[str, Any]:
        self.requests.append(
            CapturedRequest(
                url=str(req["url"]),
                method=str(req["method"]),
                headers=dict(req.get("headers") or {}),
                body_text=req.get("body_text"),
                timeout_ms=int(req.get("timeout_ms") or 0),
            )
        )
        return {"status": 200, "headers": {"content-type": "application/json"}, "body_text": json.dumps({"code": 1000, "data": {"ok": True}})}


class FlakyNetworkTransport:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, req: dict[str, Any]) -> dict[str, Any]:
        self.calls += 1
        if self.calls == 1:
            raise httpx.ConnectError("boom", request=httpx.Request("POST", str(req["url"])))
        return {"status": 200, "headers": {}, "body_text": json.dumps({"code": 1000, "data": {"ok": True}})}


def _dummy_value(type_text: str) -> Any:
    t = (type_text or "").lower()
    if "string" in t:
        return "x"
    if any(x in t for x in ["int", "integer", "long", "double", "float", "number"]):
        return 1
    if any(x in t for x in ["boolean", "bool"]):
        return False
    if any(x in t for x in ["array", "list", "jsonarray"]):
        return []
    if any(x in t for x in ["object", "jsonobject", "map"]):
        return {}
    return "x"


def test_every_endpoint_callable_and_builds_request() -> None:
    """离线 smoke：遍历 127 endpoints，验证 method/path/鉴权 header 与 JSON body 构造。"""

    transport = FakeTransport()
    token = "token_raw_should_not_leak"
    client = WkteamClient(
        base_url="https://api.example.com",
        authorization=token,
        transport=transport,
        log_level="silent",
    )

    for d in endpoint_defs:
        module = getattr(client.api, d["module_attr"])
        fn = getattr(module, d["method_name"])

        kwargs: dict[str, Any] = {}
        for p in d["params"]:
            if p["required"]:
                kwargs[p["name"]] = _dummy_value(p["type"])

        res = fn(request_options=RequestOptions(request_id="t_smoke"), **kwargs)
        assert res == {"ok": True}

        last = transport.requests[-1]
        assert last.method.upper() == d["method"].upper()
        assert last.url.endswith(d["path"])

        if d["requires_auth"]:
            assert "Authorization" in last.headers
            assert last.headers["Authorization"] == token
        else:
            assert "Authorization" not in last.headers

        assert last.body_text is not None
        body_obj = json.loads(last.body_text)
        for k, v in kwargs.items():
            assert body_obj.get(k) == v


def test_retry_only_for_safe_category_by_default() -> None:
    safe = next(d for d in endpoint_defs if d["retry_category"] == "safe")
    side_effect = next(d for d in endpoint_defs if d["retry_category"] == "side_effect")

    safe_transport = FlakyNetworkTransport()
    safe_client = WkteamClient(
        base_url="https://api.example.com",
        authorization="t",
        transport=safe_transport,
        log_level="silent",
    )

    safe_module = getattr(safe_client.api, safe["module_attr"])
    safe_fn = getattr(safe_module, safe["method_name"])
    kwargs_safe = {p["name"]: "x" for p in safe["params"] if p["required"]}
    assert safe_fn(**kwargs_safe) == {"ok": True}
    assert safe_transport.calls == 2

    side_transport = FlakyNetworkTransport()
    side_client = WkteamClient(
        base_url="https://api.example.com",
        authorization="t",
        transport=side_transport,
        log_level="silent",
    )
    side_module = getattr(side_client.api, side_effect["module_attr"])
    side_fn = getattr(side_module, side_effect["method_name"])
    kwargs_side = {p["name"]: "x" for p in side_effect["params"] if p["required"]}

    with pytest.raises(WkteamNetworkError):
        side_fn(**kwargs_side)
    assert side_transport.calls == 1


@pytest.mark.asyncio
async def test_async_client_smoke_single_endpoint() -> None:
    """异步客户端最小 smoke（避免全量 async 遍历造成测试时间过长）。"""

    captured: list[dict[str, Any]] = []

    async def transport(req: dict[str, Any]) -> dict[str, Any]:
        captured.append(req)
        return {"status": 200, "headers": {}, "body_text": json.dumps({"code": 1000, "data": {"ok": True}})}

    d = endpoint_defs[0]
    client = AsyncWkteamClient(
        base_url="https://api.example.com",
        authorization="t",
        transport=transport,
        log_level="silent",
    )
    module = getattr(client.api, d["module_attr"])
    fn = getattr(module, d["method_name"])
    kwargs = {p["name"]: "x" for p in d["params"] if p["required"]}
    res = await fn(**kwargs)
    assert res == {"ok": True}
    assert captured and str(captured[-1]["url"]).endswith(d["path"])

