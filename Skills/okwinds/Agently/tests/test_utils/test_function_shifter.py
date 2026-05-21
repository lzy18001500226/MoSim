import asyncio
import threading

import pytest
from agently.utils import FunctionShifter


def test_kwargs():
    def test_func(*, a: str, b: int):
        return int(a) + b

    options = {
        "a": "1",
        "b": 2,
        "c": 3,
    }

    with pytest.raises(Exception):
        test_func(**options)

    new_test_func = FunctionShifter.auto_options_func(test_func)
    assert new_test_func(**options) == 3


@pytest.mark.asyncio
async def test_asyncify_sync_generator_yields_items():
    def sync_gen():
        for i in range(3):
            yield i

    result = []
    async for item in FunctionShifter.asyncify_sync_generator(sync_gen()):
        result.append(item)

    assert result == [0, 1, 2]


@pytest.mark.asyncio
async def test_asyncify_sync_generator_raises_error():
    def sync_gen():
        yield "ok"
        raise ValueError("boom")

    result = []
    with pytest.raises(ValueError, match="boom"):
        async for item in FunctionShifter.asyncify_sync_generator(sync_gen()):
            result.append(item)

    assert result == ["ok"]


@pytest.mark.asyncio
async def test_asyncify_sync_generator_closes_on_break():
    closed = threading.Event()

    def sync_gen():
        try:
            i = 0
            while True:
                yield i
                i += 1
        finally:
            closed.set()

    async for item in FunctionShifter.asyncify_sync_generator(sync_gen()):
        assert item == 0
        break

    assert await asyncio.to_thread(closed.wait, 1.0)
