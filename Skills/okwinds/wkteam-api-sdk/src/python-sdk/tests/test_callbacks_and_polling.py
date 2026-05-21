from __future__ import annotations

import asyncio

import pytest

from wkteam_api_sdk import async_poll_until, dedup_key, parse_callback, poll_until


def test_parse_callback_and_dedup_key() -> None:
    payload = {
        "wcId": "wxid_xxx",
        "account": "17200000000",
        "messageType": "60001",
        "data": {"newMsgId": 123, "timestamp": 456},
    }
    parsed = parse_callback(payload)
    assert parsed["wcId"] == "wxid_xxx"
    assert parsed["messageType"] == "60001"
    assert dedup_key(payload) == "wkteam:wxid_xxx:60001:newMsgId:123"


def test_poll_until() -> None:
    state = {"n": 0}

    def run() -> int:
        state["n"] += 1
        return state["n"]

    def done(v: int) -> bool:
        return v >= 3

    assert poll_until(run=run, is_done=done, interval_ms=1, initial_delay_ms=0, timeout_ms=1000) == 3


@pytest.mark.asyncio
async def test_async_poll_until() -> None:
    state = {"n": 0}

    async def run() -> int:
        state["n"] += 1
        await asyncio.sleep(0)
        return state["n"]

    def done(v: int) -> bool:
        return v >= 3

    assert await async_poll_until(run=run, is_done=done, interval_ms=1, initial_delay_ms=0, timeout_ms=1000) == 3

