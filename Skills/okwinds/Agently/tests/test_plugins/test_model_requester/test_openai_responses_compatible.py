import asyncio
import json

import pytest

from types import SimpleNamespace

from agently import Agently
from agently.core.Prompt import Prompt
from agently.utils import Settings
from agently.builtins.plugins.ModelRequester.OpenAIResponsesCompatible import (
    OpenAIResponsesCompatible,
)
from agently.types.plugins import ModelRequester
import agently.builtins.plugins.ModelRequester.OpenAIResponsesCompatible as responses_module


def build_plugin(config: dict, prompt_values: dict | None = None):
    settings = Settings(parent=Agently.settings)
    settings.update({"plugins": {"ModelRequester": {"OpenAIResponsesCompatible": config}}})
    prompt = Prompt(plugin_manager=Agently.plugin_manager, parent_settings=settings)
    for key, value in (prompt_values or {}).items():
        prompt.set(key, value)
    return OpenAIResponsesCompatible(prompt, settings)


def generate_request(config: dict, prompt_values: dict | None = None):
    return build_plugin(config, prompt_values).generate_request_data().model_dump()


async def capture_request_headers(monkeypatch: pytest.MonkeyPatch, config: dict, prompt_values: dict | None = None):
    captured: dict = {}

    class FakeResponse:
        status_code = 200
        content = b'{"id":"resp_1","object":"response","status":"completed","output":[]}'
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

    monkeypatch.setattr(responses_module, "AsyncClient", FakeAsyncClient)
    plugin = build_plugin(config, prompt_values)
    request_data = plugin.generate_request_data()
    async for _event, _payload in plugin.request_model(request_data):
        pass
    return captured


def collect_events(plugin: OpenAIResponsesCompatible, request_events: list[tuple[str, str]]):
    async def _run():
        async def generator():
            for event, payload in request_events:
                yield event, payload

        collected = []
        async for event, data in plugin.broadcast_response(generator()):
            collected.append((event, data))
        return collected

    return asyncio.run(_run())


def test_generate_request_uses_responses_path_and_latest_default_model():
    request = generate_request(
        {
            "base_url": "https://api.example.com/v1",
        },
        {"input": "hello"},
    )

    assert request["request_url"] == "https://api.example.com/v1/responses"
    assert request["request_options"]["model"] == "gpt-5.5"
    assert request["request_options"]["stream"] is True
    assert request["data"]["input"] == [
        {
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": "hello"}],
        }
    ]


def test_inherits_model_requester_protocol_instead_of_openai_plugin():
    assert OpenAIResponsesCompatible.__bases__ == (ModelRequester,)


def test_generate_request_maps_rich_content_and_preserves_instructions():
    request = generate_request(
        {
            "base_url": "https://api.example.com/v1",
            "request_options": {"instructions": "Be concise."},
        },
        {
            "input": "Describe this file.",
            "attachment": [
                {"type": "text", "text": "extra text"},
                {"type": "image_url", "image_url": "https://example.com/cat.png"},
                {"type": "input_file", "file_id": "file_123"},
            ],
        },
    )

    assert request["request_options"]["instructions"] == "Be concise."
    content = request["data"]["input"][0]["content"]
    assert content[0]["type"] == "input_text"
    assert "Describe this file." in content[0]["text"]
    assert content[1] == {"type": "input_text", "text": "extra text"}
    assert content[2] == {"type": "input_image", "image_url": "https://example.com/cat.png"}
    assert content[3] == {"type": "input_file", "file_id": "file_123"}


def test_prompt_tools_are_converted_and_explicit_tools_override_by_name():
    request = generate_request(
        {
            "base_url": "https://api.example.com/v1",
            "request_options": {
                "tools": [
                    {
                        "type": "function",
                        "name": "search_docs",
                        "description": "explicit override",
                        "parameters": {"type": "object", "properties": {"query": {"type": "string"}}},
                        "strict": True,
                    },
                    {
                        "type": "web_search_preview",
                    },
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
    web_search = next(tool for tool in tools if tool.get("type") == "web_search_preview")

    assert search_docs["description"] == "explicit override"
    assert search_docs["strict"] is True
    assert lookup_issue["strict"] is False
    assert lookup_issue["parameters"]["properties"]["issue_id"]["type"] == "string"
    assert lookup_issue["parameters"]["additionalProperties"] is False
    assert web_search == {"type": "web_search_preview"}


@pytest.mark.asyncio
async def test_auth_headers_are_preserved_in_outgoing_request(monkeypatch: pytest.MonkeyPatch):
    captured = await capture_request_headers(
        monkeypatch,
        {
            "base_url": "https://api.example.com/v1",
            "model": "m1",
            "stream": False,
            "auth": {"headers": {"Authorization": "Custom ABC", "X-Test": "1"}},
        },
        {"input": "hello"},
    )

    assert captured["headers"]["Authorization"] == "Custom ABC"
    assert captured["headers"]["X-Test"] == "1"


def test_broadcast_response_maps_text_stream_and_meta():
    plugin = build_plugin({"base_url": "https://api.example.com/v1"}, {"input": "hello"})
    final_response = {
        "id": "resp_1",
        "object": "response",
        "status": "completed",
        "model": "gpt-5.5",
        "output": [
            {
                "id": "msg_1",
                "type": "message",
                "status": "completed",
                "role": "assistant",
                "content": [{"type": "output_text", "text": "Hello world"}],
            }
        ],
        "usage": {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3},
        "incomplete_details": None,
    }
    events = collect_events(
        plugin,
        [
            ("response.created", json.dumps({"type": "response.created", "response": {"id": "resp_1", "model": "gpt-5.5", "status": "in_progress"}})),
            ("response.output_text.delta", json.dumps({"type": "response.output_text.delta", "delta": "Hello "})),
            ("response.output_text.delta", json.dumps({"type": "response.output_text.delta", "delta": "world"})),
            (
                "response.output_item.done",
                json.dumps(
                    {
                        "type": "response.output_item.done",
                        "output_index": 0,
                        "item": final_response["output"][0],
                    }
                ),
            ),
            ("response.completed", json.dumps({"type": "response.completed", "response": final_response})),
        ],
    )

    assert [data for event, data in events if event == "delta"] == ["Hello ", "world"]
    assert ("done", "Hello world") in events
    assert ("reasoning_done", "") in events
    assert ("original_done", final_response) in events
    assert ("meta", {"id": "resp_1", "model": "gpt-5.5", "status": "completed", "usage": {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3}, "finish_reason": "stop"}) in events


def test_broadcast_response_synthesizes_tool_call_done_without_completed_event():
    plugin = build_plugin({"base_url": "https://api.example.com/v1"}, {"input": "hello"})
    events = collect_events(
        plugin,
        [
            ("response.created", json.dumps({"type": "response.created", "response": {"id": "resp_tool", "model": "gpt-5.5", "status": "in_progress"}})),
            (
                "response.output_item.done",
                json.dumps(
                    {
                        "type": "response.output_item.done",
                        "output_index": 0,
                        "item": {
                            "type": "function_call",
                            "call_id": "call_1",
                            "name": "search_docs",
                            "arguments": '{"query":"Agently"}',
                            "status": "completed",
                        },
                    }
                ),
            ),
        ],
    )

    tool_chunk = next(data for event, data in events if event == "tool_calls")
    meta = next(data for event, data in events if event == "meta")
    original_done = next(data for event, data in events if event == "original_done")

    assert tool_chunk["id"] == "call_1"
    assert tool_chunk["function"]["name"] == "search_docs"
    assert tool_chunk["function"]["arguments"] == '{"query":"Agently"}'
    assert ("done", "") in events
    assert meta["finish_reason"] == "tool_calls"
    assert original_done["output"][0]["type"] == "function_call"


def test_function_call_argument_deltas_can_be_consumed_by_action_normalizer():
    plugin = build_plugin(
        {"base_url": "https://api.example.com/v1"},
        {
            "input": "Find docs.",
            "tools": [{"name": "search_docs", "desc": "Search docs.", "kwargs": {"query": (str, "")}}],
        },
    )
    events = collect_events(
        plugin,
        [
            (
                "response.output_item.added",
                json.dumps(
                    {
                        "type": "response.output_item.added",
                        "output_index": 0,
                        "item": {
                            "type": "function_call",
                            "call_id": "call_2",
                            "name": "search_docs",
                            "arguments": "",
                            "status": "in_progress",
                        },
                    }
                ),
            ),
            (
                "response.function_call_arguments.delta",
                json.dumps(
                    {
                        "type": "response.function_call_arguments.delta",
                        "output_index": 0,
                        "call_id": "call_2",
                        "delta": '{"query":"Agently',
                    }
                ),
            ),
            (
                "response.function_call_arguments.delta",
                json.dumps(
                    {
                        "type": "response.function_call_arguments.delta",
                        "output_index": 0,
                        "call_id": "call_2",
                        "delta": ' TriggerFlow"}',
                    }
                ),
            ),
            (
                "response.output_item.done",
                json.dumps(
                    {
                        "type": "response.output_item.done",
                        "output_index": 0,
                        "item": {
                            "type": "function_call",
                            "call_id": "call_2",
                            "name": "search_docs",
                            "arguments": '{"query":"Agently TriggerFlow"}',
                            "status": "completed",
                        },
                    }
                ),
            ),
        ],
    )

    tool_call_chunks = [data for event, data in events if event == "tool_calls"]
    action_calls = Agently.action._normalize_native_action_calls(tool_call_chunks)

    assert action_calls == [
        {
            "purpose": "Use search_docs",
            "action_id": "search_docs",
            "action_input": {"query": "Agently TriggerFlow"},
            "policy_override": {},
            "source_protocol": "native_tool_calls",
            "todo_suggestion": "",
            "next": "",
            "tool_name": "search_docs",
            "tool_kwargs": {"query": "Agently TriggerFlow"},
        }
    ]


@pytest.mark.asyncio
async def test_streaming_uses_first_token_timeout_mode_by_default(monkeypatch: pytest.MonkeyPatch):
    captured: dict = {}

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            self.headers = {}
            captured["client_kwargs"] = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def aclose(self):
            return None

    async def fake_aiter_sse_with_retry(self, client, method, url, *, headers, json):
        del self, client, method, url, headers, json

        async def generator():
            yield SimpleNamespace(event="response.completed", data='{"type":"response.completed","response":{"id":"resp_1","status":"completed","output":[]}}')

        return generator()

    monkeypatch.setattr(responses_module, "AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(OpenAIResponsesCompatible, "_aiter_sse_with_retry", fake_aiter_sse_with_retry)

    plugin = build_plugin(
        {
            "base_url": "https://api.example.com/v1",
            "model": "m1",
            "stream": True,
            "timeout": {"connect": 1.0, "read": 9.0, "write": 2.0, "pool": 3.0},
        },
        {"input": "hello"},
    )
    request_data = plugin.generate_request_data()

    async for _event, _payload in plugin.request_model(request_data):
        pass

    timeout = captured["client_kwargs"]["timeout"]
    assert timeout.connect == 1.0
    assert timeout.read is None
    assert timeout.write == 2.0
    assert timeout.pool == 3.0


@pytest.mark.asyncio
async def test_streaming_http_timeout_mode_preserves_http_read_timeout(monkeypatch: pytest.MonkeyPatch):
    captured: dict = {}

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            self.headers = {}
            captured["client_kwargs"] = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def aclose(self):
            return None

    async def fake_aiter_sse_with_retry(self, client, method, url, *, headers, json):
        del self, client, method, url, headers, json

        async def generator():
            yield SimpleNamespace(event="response.completed", data='{"type":"response.completed","response":{"id":"resp_1","status":"completed","output":[]}}')

        return generator()

    monkeypatch.setattr(responses_module, "AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(OpenAIResponsesCompatible, "_aiter_sse_with_retry", fake_aiter_sse_with_retry)

    plugin = build_plugin(
        {
            "base_url": "https://api.example.com/v1",
            "model": "m1",
            "stream": True,
            "timeout_mode": "http",
            "timeout": {"connect": 1.0, "read": 9.0, "write": 2.0, "pool": 3.0},
        },
        {"input": "hello"},
    )
    request_data = plugin.generate_request_data()

    async for _event, _payload in plugin.request_model(request_data):
        pass

    timeout = captured["client_kwargs"]["timeout"]
    assert timeout.connect == 1.0
    assert timeout.read == 9.0
    assert timeout.write == 2.0
    assert timeout.pool == 3.0


@pytest.mark.asyncio
async def test_first_token_timeout_returns_timeout_error_event(monkeypatch: pytest.MonkeyPatch):
    class FakeAsyncClient:
        def __init__(self, **kwargs):
            self.headers = {}

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def aclose(self):
            return None

    async def fake_aiter_sse_with_retry(self, client, method, url, *, headers, json):
        del self, client, method, url, headers, json

        async def generator():
            await asyncio.sleep(0.05)
            yield SimpleNamespace(event="response.completed", data='{"type":"response.completed","response":{"id":"resp_1","status":"completed","output":[]}}')

        return generator()

    monkeypatch.setattr(responses_module, "AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(OpenAIResponsesCompatible, "_aiter_sse_with_retry", fake_aiter_sse_with_retry)

    plugin = build_plugin(
        {
            "base_url": "https://api.example.com/v1",
            "model": "m1",
            "stream": True,
            "timeout": {"connect": 1.0, "read": 0.01, "write": 2.0, "pool": 3.0},
        },
        {"input": "hello"},
    )

    async def fake_async_error(*args, **kwargs):
        del args, kwargs
        return None

    plugin._emitter.async_error = fake_async_error  # type: ignore[method-assign]
    request_data = plugin.generate_request_data()

    events = []
    async for event, payload in plugin.request_model(request_data):
        events.append((event, payload))

    assert len(events) == 1
    assert events[0][0] == "error"
    assert isinstance(events[0][1], TimeoutError)
    assert "First token timeout after 0.01 seconds." in str(events[0][1])
