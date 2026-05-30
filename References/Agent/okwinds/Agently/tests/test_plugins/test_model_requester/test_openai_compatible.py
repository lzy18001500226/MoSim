import pytest
import asyncio

import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from typing import cast
from agently import Agently
from agently.core.Prompt import Prompt
from agently.utils import SerializableStateDataNamespace
from agently.utils import Settings
from agently.builtins.plugins.ModelRequester.OpenAICompatible import (
    OpenAICompatible,
    ModelRequesterSettings,
)
import agently.builtins.plugins.ModelRequester.OpenAICompatible as openai_module
from collections import Counter
from types import SimpleNamespace

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")


def build_plugin(config: dict, prompt_values: dict | None = None):
    settings = Settings(parent=Agently.settings)
    settings.update({"plugins": {"ModelRequester": {"OpenAICompatible": config}}})
    prompt = Prompt(plugin_manager=Agently.plugin_manager, parent_settings=settings)
    for key, value in (prompt_values or {}).items():
        prompt.set(key, value)
    return OpenAICompatible(prompt, settings)


def generate_request(config: dict, prompt_values: dict | None = None):
    return build_plugin(config, prompt_values).generate_request_data().model_dump()


async def capture_request_headers(monkeypatch: pytest.MonkeyPatch, config: dict, prompt_values: dict | None = None):
    captured: dict = {}

    class FakeResponse:
        status_code = 200
        content = b'{"ok": true}'
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

    monkeypatch.setattr(openai_module, "AsyncClient", FakeAsyncClient)
    plugin = build_plugin(config, prompt_values)
    request_data = plugin.generate_request_data()
    async for _event, _payload in plugin.request_model(request_data):
        pass
    return captured


@pytest.mark.asyncio
async def test_main(require_ollama):
    request_settings = cast(
        ModelRequesterSettings,
        SerializableStateDataNamespace(Agently.settings, "plugins.ModelRequester.OpenAICompatible"),
    )
    request_settings["base_url"] = OLLAMA_BASE_URL
    request_settings["model"] = OLLAMA_MODEL
    request_settings["model_type"] = "chat"
    request_settings["auth"] = None
    prompt = Agently.create_prompt()

    openai_compatible = OpenAICompatible(
        prompt,
        Agently.settings,
    )

    try:
        prompt.set("input", "ni hao")
        request_data = openai_compatible.generate_request_data()
        request_response = openai_compatible.request_model(request_data)
        response = openai_compatible.broadcast_response(request_response)
        async for event, message in response:
            print(event, message)
    except Exception as e:
        raise e


def test_plugin_root_options_are_treated_as_request_options():
    request = generate_request(
        {
            "base_url": "https://api.example.com/v1",
            "model": "m1",
            "options": {"temperature": 0.7, "top_p": 0.9},
        },
        {"input": "hello"},
    )

    assert request["request_options"] == {"temperature": 0.7, "top_p": 0.9, "model": "m1", "stream": True}


def test_request_options_override_legacy_plugin_root_options():
    request = generate_request(
        {
            "base_url": "https://api.example.com/v1",
            "model": "m1",
            "options": {"temperature": 0.7, "top_p": 0.9},
            "request_options": {"temperature": 0.2},
        },
        {"input": "hello", "options": {"top_p": 0.5}},
    )

    assert request["request_options"] == {"temperature": 0.2, "top_p": 0.5, "model": "m1", "stream": True}


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


@pytest.mark.asyncio
async def test_auth_headers_are_kept_when_api_key_sets_authorization(monkeypatch: pytest.MonkeyPatch):
    captured = await capture_request_headers(
        monkeypatch,
        {
            "base_url": "https://api.example.com/v1",
            "model": "m1",
            "stream": False,
            "api_key": "KEY2",
            "auth": {"headers": {"X-Test": "1"}},
        },
        {"input": "hello"},
    )

    assert captured["headers"]["Authorization"] == "Bearer KEY2"
    assert captured["headers"]["X-Test"] == "1"


@pytest.mark.asyncio
async def test_streaming_done_is_not_emitted_twice(monkeypatch: pytest.MonkeyPatch):
    class FakeSSE:
        def __init__(self, event: str, data: str):
            self.event = event
            self.data = data
            self.id = None
            self.retry = None

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
        async def generator():
            yield FakeSSE(
                "message",
                '{"id":"1","choices":[{"delta":{"content":"hello"},"finish_reason":"stop"}],"usage":{"total_tokens":1}}',
            )
            yield FakeSSE("message", "[DONE]")

        return generator()

    monkeypatch.setattr(openai_module, "AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(OpenAICompatible, "_aiter_sse_with_retry", fake_aiter_sse_with_retry)

    plugin = build_plugin(
        {
            "base_url": "https://api.example.com/v1",
            "model": "m1",
            "stream": True,
        },
        {"input": "hello"},
    )
    request_data = plugin.generate_request_data()
    response = plugin.broadcast_response(plugin.request_model(request_data))

    events = []
    async for event, data in response:
        events.append((event, data))

    counts = Counter(event for event, _ in events)
    assert counts["done"] == 1
    assert counts["reasoning_done"] == 1
    assert counts["meta"] == 1


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
            yield SimpleNamespace(event="message", data='{"choices":[{"delta":{"content":"hello"}}]}')
            yield SimpleNamespace(event="message", data="[DONE]")

        return generator()

    monkeypatch.setattr(openai_module, "AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(OpenAICompatible, "_aiter_sse_with_retry", fake_aiter_sse_with_retry)

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
            yield SimpleNamespace(event="message", data='{"choices":[{"delta":{"content":"hello"}}]}')
            yield SimpleNamespace(event="message", data="[DONE]")

        return generator()

    monkeypatch.setattr(openai_module, "AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(OpenAICompatible, "_aiter_sse_with_retry", fake_aiter_sse_with_retry)

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
            yield SimpleNamespace(event="message", data='{"choices":[{"delta":{"content":"hello"}}]}')

        return generator()

    monkeypatch.setattr(openai_module, "AsyncClient", FakeAsyncClient)
    monkeypatch.setattr(OpenAICompatible, "_aiter_sse_with_retry", fake_aiter_sse_with_retry)

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
