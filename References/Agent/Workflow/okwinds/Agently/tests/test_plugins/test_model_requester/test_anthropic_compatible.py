import asyncio
import json

import pytest

from agently import Agently
from agently.core.Prompt import Prompt
from agently.utils import Settings
from agently.builtins.plugins.ModelRequester.AnthropicCompatible import (
    AnthropicCompatible,
)
from agently.types.plugins import ModelRequester
import agently.builtins.plugins.ModelRequester.AnthropicCompatible as anthropic_module


def build_plugin(config: dict, prompt_values: dict | None = None):
    settings = Settings(parent=Agently.settings)
    settings.update({"plugins": {"ModelRequester": {"AnthropicCompatible": config}}})
    prompt = Prompt(plugin_manager=Agently.plugin_manager, parent_settings=settings)
    for key, value in (prompt_values or {}).items():
        prompt.set(key, value)
    return AnthropicCompatible(prompt, settings)


def generate_request(config: dict, prompt_values: dict | None = None):
    return build_plugin(config, prompt_values).generate_request_data().model_dump()


async def capture_request_headers(monkeypatch: pytest.MonkeyPatch, config: dict, prompt_values: dict | None = None):
    captured: dict = {}

    class FakeResponse:
        status_code = 200
        content = b'{"id":"msg_1","type":"message","role":"assistant","model":"claude-sonnet-4-20250514","content":[{"type":"text","text":"hello"}],"stop_reason":"end_turn","usage":{"input_tokens":1,"output_tokens":1}}'
        text = content.decode()
        headers = {"Content-Type": "application/json"}

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            self.headers = {}
            captured["client_kwargs"] = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json=None, headers=None):
            captured["url"] = url
            captured["json"] = json
            captured["headers"] = dict(self.headers if headers is None else headers)
            return FakeResponse()

        async def aclose(self):
            return None

    monkeypatch.setattr(anthropic_module, "AsyncClient", FakeAsyncClient)
    plugin = build_plugin(config, prompt_values)
    request_data = plugin.generate_request_data()
    async for _event, _payload in plugin.request_model(request_data):
        pass
    return captured


def collect_events(plugin: AnthropicCompatible, request_events: list[tuple[str, str]]):
    async def _run():
        async def generator():
            for event, payload in request_events:
                yield event, payload

        collected = []
        async for event, data in plugin.broadcast_response(generator()):
            collected.append((event, data))
        return collected

    return asyncio.run(_run())


def test_generate_request_uses_messages_path_and_default_model():
    request = generate_request(
        {
            "base_url": "https://api.anthropic.example/v1",
        },
        {"input": "hello"},
    )

    assert request["request_url"] == "https://api.anthropic.example/v1/messages"
    assert request["request_options"]["model"] == "claude-sonnet-4-20250514"
    assert request["request_options"]["stream"] is True
    assert request["request_options"]["max_tokens"] == 4096
    assert request["headers"]["anthropic-version"] == "2023-06-01"
    assert request["data"]["messages"] == [{"role": "user", "content": "hello"}]


def test_inherits_model_requester_protocol_instead_of_responses_plugin():
    assert AnthropicCompatible.__bases__ == (ModelRequester,)


def test_generate_request_maps_system_and_rich_content():
    request = generate_request(
        {
            "base_url": "https://api.anthropic.example/v1",
        },
        {
            "instruct": "Be concise.",
            "input": "Describe this image.",
            "attachment": [{"type": "image_url", "image_url": "https://example.com/cat.png"}],
        },
    )

    assert "system" not in request["data"]
    assert request["data"]["messages"][0]["role"] == "user"
    content = request["data"]["messages"][0]["content"]
    assert content[0]["type"] == "text"
    assert "[INSTRUCT]:" in content[0]["text"]
    assert "Be concise." in content[0]["text"]
    assert "Describe this image." in content[0]["text"]
    assert content[1] == {
        "type": "image",
        "source": {"type": "url", "url": "https://example.com/cat.png"},
    }


def test_prompt_tools_are_converted_and_explicit_tools_override_by_name():
    request = generate_request(
        {
            "base_url": "https://api.anthropic.example/v1",
            "request_options": {
                "tools": [
                    {
                        "name": "search_docs",
                        "description": "explicit override",
                        "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}},
                    }
                ]
            },
        },
        {
            "input": "Find docs.",
            "tools": [
                {
                    "name": "search_docs",
                    "desc": "Search the documentation.",
                    "kwargs": {"query": (str, "query text"), "limit": (int, "max result count")},
                },
                {
                    "name": "lookup_issue",
                    "desc": "Lookup a GitHub issue.",
                    "kwargs": {"issue_id": (str, "Issue id")},
                },
            ],
        },
    )

    tools = request["request_options"]["tools"]
    search_docs = next(tool for tool in tools if tool.get("name") == "search_docs")
    lookup_issue = next(tool for tool in tools if tool.get("name") == "lookup_issue")

    assert search_docs["description"] == "explicit override"
    assert lookup_issue["input_schema"]["properties"]["issue_id"]["type"] == "string"
    assert lookup_issue["input_schema"]["additionalProperties"] is False


@pytest.mark.asyncio
async def test_auth_headers_are_preserved_in_outgoing_request(monkeypatch: pytest.MonkeyPatch):
    captured = await capture_request_headers(
        monkeypatch,
        {
            "base_url": "https://api.anthropic.example/v1",
            "model": "claude-sonnet-4-20250514",
            "stream": False,
            "auth": {"headers": {"X-Test": "1"}, "api_key": "claude-secret"},
            "anthropic_beta": ["tools-2024-04-04"],
        },
        {"input": "hello"},
    )

    assert captured["headers"]["x-api-key"] == "claude-secret"
    assert captured["headers"]["X-Test"] == "1"
    assert captured["headers"]["anthropic-version"] == "2023-06-01"
    assert captured["headers"]["anthropic-beta"] == "tools-2024-04-04"


def test_broadcast_response_maps_text_stream_and_meta():
    plugin = build_plugin({"base_url": "https://api.anthropic.example/v1"}, {"input": "hello"})
    events = collect_events(
        plugin,
        [
            (
                "message_start",
                json.dumps(
                    {
                        "type": "message_start",
                        "message": {
                            "id": "msg_1",
                            "type": "message",
                            "role": "assistant",
                            "model": "claude-sonnet-4-20250514",
                            "content": [],
                            "usage": {"input_tokens": 1, "output_tokens": 0},
                        },
                    }
                ),
            ),
            ("content_block_start", json.dumps({"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}})),
            ("content_block_delta", json.dumps({"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "Hello "}})),
            ("content_block_delta", json.dumps({"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": "world"}})),
            ("content_block_stop", json.dumps({"type": "content_block_stop", "index": 0})),
            (
                "message_delta",
                json.dumps(
                    {
                        "type": "message_delta",
                        "delta": {"stop_reason": "end_turn", "stop_sequence": None},
                        "usage": {"input_tokens": 1, "output_tokens": 2},
                    }
                ),
            ),
            ("message_stop", json.dumps({"type": "message_stop"})),
        ],
    )

    assert ("delta", "Hello ") in events
    assert ("delta", "world") in events
    assert ("done", "Hello world") in events
    assert ("reasoning_done", "") in events
    meta = next(data for event, data in events if event == "meta")
    assert meta["id"] == "msg_1"
    assert meta["finish_reason"] == "stop"
    assert meta["usage"]["output_tokens"] == 2


def test_broadcast_response_maps_tool_use_to_tool_calls():
    plugin = build_plugin({"base_url": "https://api.anthropic.example/v1"}, {"input": "Find docs"})
    events = collect_events(
        plugin,
        [
            (
                "message_start",
                json.dumps(
                    {
                        "type": "message_start",
                        "message": {
                            "id": "msg_2",
                            "type": "message",
                            "role": "assistant",
                            "model": "claude-sonnet-4-20250514",
                            "content": [],
                            "usage": {"input_tokens": 3, "output_tokens": 0},
                        },
                    }
                ),
            ),
            (
                "content_block_start",
                json.dumps(
                    {
                        "type": "content_block_start",
                        "index": 0,
                        "content_block": {"type": "tool_use", "id": "toolu_1", "name": "search_docs", "input": {}},
                    }
                ),
            ),
            (
                "content_block_delta",
                json.dumps(
                    {
                        "type": "content_block_delta",
                        "index": 0,
                        "delta": {"type": "input_json_delta", "partial_json": "{\"query\":\"anthropic\"}"},
                    }
                ),
            ),
            ("content_block_stop", json.dumps({"type": "content_block_stop", "index": 0})),
            (
                "message_delta",
                json.dumps(
                    {
                        "type": "message_delta",
                        "delta": {"stop_reason": "tool_use", "stop_sequence": None},
                        "usage": {"input_tokens": 3, "output_tokens": 4},
                    }
                ),
            ),
            ("message_stop", json.dumps({"type": "message_stop"})),
        ],
    )

    tool_call_event = next(data for event, data in events if event == "tool_calls")
    assert tool_call_event["id"] == "toolu_1"
    assert tool_call_event["function"]["name"] == "search_docs"
    assert tool_call_event["function"]["arguments"] == "{\"query\":\"anthropic\"}"
    meta = next(data for event, data in events if event == "meta")
    assert meta["finish_reason"] == "tool_calls"
