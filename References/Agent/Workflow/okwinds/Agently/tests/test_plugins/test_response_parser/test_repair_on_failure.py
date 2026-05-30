import asyncio
from typing import Any, cast

import pytest

import agently.base

from agently.builtins.plugins.ResponseParser.AgentlyResponseParser import AgentlyResponseParser
from agently.types.data.prompt import PromptModel
from agently.utils import DataLocator, Settings


class DummyPrompt:
    def __init__(self, output):
        self._prompt_object = PromptModel(output=output, output_format="json")

    def to_prompt_object(self):
        return self._prompt_object

    def to_output_model(self):
        return None


async def _noop_async_emit_runtime(_event):
    return None


def create_response_parser(events, output_schema):
    async def response_generator():
        for event, data in events:
            yield event, data

    return AgentlyResponseParser(
        agent_name="test-agent",
        response_id="resp-1",
        prompt=cast(Any, DummyPrompt(output_schema)),
        response_generator=response_generator(),
        settings=Settings(),
    )


@pytest.mark.asyncio
async def test_response_parser_only_repairs_after_parse_failure(monkeypatch):
    monkeypatch.setattr(agently.base, "async_emit_runtime", _noop_async_emit_runtime)

    repair_calls = 0
    original_repair = DataLocator.repair_json_fragment

    def track_repair_calls(text: str) -> str:
        nonlocal repair_calls
        repair_calls += 1
        return original_repair(text)

    monkeypatch.setattr(DataLocator, "repair_json_fragment", track_repair_calls)

    parser = create_response_parser(
        [("done", '{"name": "Alice", "quote": "她说：“你好”"}')],
        {"name": None, "quote": None},
    )

    parsed = await parser.async_get_data()

    assert parsed["name"] == "Alice"
    assert parsed["quote"] == "她说：“你好”"
    assert repair_calls == 0


@pytest.mark.asyncio
async def test_response_parser_repairs_structural_quotes_and_preserves_value_quotes(monkeypatch):
    monkeypatch.setattr(agently.base, "async_emit_runtime", _noop_async_emit_runtime)

    parser = create_response_parser(
        [("done", '{“quote”: "她说：“你好”", “name”: "Alice"}')],
        {"quote": None, "name": None},
    )

    parsed = await parser.async_get_data()
    result = await parser.async_get_data(type="all")

    assert parsed["quote"] == "她说：“你好”"
    assert parsed["name"] == "Alice"
    assert result["cleaned_result"] is not None
    assert '“你好”' in result["cleaned_result"]
    assert '"quote"' in result["cleaned_result"]
    assert '"name"' in result["cleaned_result"]


@pytest.mark.asyncio
async def test_instant_async_generator_streams_valid_json_before_done(monkeypatch):
    monkeypatch.setattr(agently.base, "async_emit_runtime", _noop_async_emit_runtime)

    release_done = asyncio.Event()

    async def response_generator():
        yield "delta", '{"name": "Ali'
        await release_done.wait()
        yield "done", '{"name": "Alice"}'

    parser = AgentlyResponseParser(
        agent_name="test-agent",
        response_id="resp-2",
        prompt=cast(Any, DummyPrompt({"name": None})),
        response_generator=response_generator(),
        settings=Settings(),
    )

    generator = parser.get_async_generator(type="instant")
    first_event = await asyncio.wait_for(anext(generator), timeout=1)

    assert first_event.path == "name"
    assert first_event.event_type == "delta"
    assert first_event.value == "Ali"
    assert first_event.delta == "Ali"

    release_done.set()

    second_event = await asyncio.wait_for(anext(generator), timeout=1)
    third_event = await asyncio.wait_for(anext(generator), timeout=1)

    assert second_event.path == "name"
    assert second_event.event_type == "delta"
    assert second_event.value == "Alice"
    assert second_event.delta == "ce"

    assert third_event.path == "name"
    assert third_event.event_type == "done"
    assert third_event.value == "Alice"

    with pytest.raises(StopAsyncIteration):
        await anext(generator)


@pytest.mark.asyncio
async def test_instant_async_generator_waits_until_done_before_repair(monkeypatch):
    monkeypatch.setattr(agently.base, "async_emit_runtime", _noop_async_emit_runtime)

    release_done = asyncio.Event()

    async def response_generator():
        yield "delta", '{“name”: “Ali'
        await release_done.wait()
        yield "done", '{“name”: “Alice”}'

    parser = AgentlyResponseParser(
        agent_name="test-agent",
        response_id="resp-3",
        prompt=cast(Any, DummyPrompt({"name": None})),
        response_generator=response_generator(),
        settings=Settings(),
    )

    generator = parser.get_async_generator(type="instant")
    first_event_task = asyncio.create_task(anext(generator))

    await asyncio.sleep(0.05)
    assert not first_event_task.done()

    release_done.set()

    first_event = await asyncio.wait_for(first_event_task, timeout=1)
    second_event = await asyncio.wait_for(anext(generator), timeout=1)

    assert first_event.path == "name"
    assert first_event.event_type == "delta"
    assert first_event.value == "Alice"
    assert first_event.delta == "Alice"

    assert second_event.path == "name"
    assert second_event.event_type == "done"
    assert second_event.value == "Alice"

    with pytest.raises(StopAsyncIteration):
        await anext(generator)


@pytest.mark.asyncio
async def test_instant_async_generator_does_not_emit_done_when_final_parse_fails(monkeypatch):
    monkeypatch.setattr(agently.base, "async_emit_runtime", _noop_async_emit_runtime)

    async def response_generator():
        yield "delta", '{"name": "Ali'
        yield "done", '{"name": "Alice" "age": 1}'

    parser = AgentlyResponseParser(
        agent_name="test-agent",
        response_id="resp-4",
        prompt=cast(Any, DummyPrompt({"name": None, "age": None})),
        response_generator=response_generator(),
        settings=Settings(),
    )

    events = []
    async for event in parser.get_async_generator(type="instant"):
        events.append((event.path, event.event_type, event.value, event.delta))

    assert events == [("name", "delta", "Ali", "Ali")]
    assert await parser.async_get_data() is None


@pytest.mark.asyncio
async def test_instant_multiple_consumers_share_single_final_parse(monkeypatch):
    monkeypatch.setattr(agently.base, "async_emit_runtime", _noop_async_emit_runtime)

    parser = create_response_parser(
        [
            ("delta", '{"name": "Ali'),
            ("done", '{"name": "Alice"}'),
        ],
        {"name": None},
    )

    parse_calls = 0
    original_parse = parser._parse_json_output

    def track_parse_calls(text: str):
        nonlocal parse_calls
        parse_calls += 1
        return original_parse(text)

    monkeypatch.setattr(parser, "_parse_json_output", track_parse_calls)

    first_events = []
    second_events = []

    async for event in parser.get_async_generator(type="instant"):
        first_events.append((event.path, event.event_type, event.value, event.delta))

    async for event in parser.get_async_generator(type="instant"):
        second_events.append((event.path, event.event_type, event.value, event.delta))

    assert parse_calls == 1
    assert first_events == second_events


def test_instant_sync_generator_replays_final_result(monkeypatch):
    monkeypatch.setattr(agently.base, "async_emit_runtime", _noop_async_emit_runtime)

    parser = create_response_parser(
        [
            ("delta", '{"name": "Ali'),
            ("done", '{"name": "Alice"}'),
        ],
        {"name": None},
    )

    events = list(parser.get_generator(type="instant"))

    assert [event.event_type for event in events] == ["delta", "delta", "done"]
    assert [event.path for event in events] == ["name", "name", "name"]
    assert events[0].value == "Ali"
    assert events[1].value == "Alice"
    assert events[1].delta == "ce"
    assert events[2].value == "Alice"
