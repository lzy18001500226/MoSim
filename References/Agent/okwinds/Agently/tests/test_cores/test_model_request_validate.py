import json
from collections.abc import AsyncGenerator
from typing import Any

import pytest

from agently import Agently
from agently.core import ModelRequest, PluginManager
from agently.types.data import AgentlyRequestData
from agently.utils import Settings


class MockValidateJSONRequester:
    name = "MockValidateJSONRequester"
    DEFAULT_SETTINGS: dict[str, Any] = {}
    attempts = 0
    responses: list[Any] = []

    def __init__(self, prompt, settings):
        self.prompt = prompt
        self.settings = settings

    @classmethod
    def reset(cls, responses: list[Any]):
        cls.attempts = 0
        cls.responses = list(responses)

    @staticmethod
    def _on_register():
        pass

    @staticmethod
    def _on_unregister():
        pass

    def generate_request_data(self):
        type(self).attempts += 1
        prompt_object = self.prompt.to_prompt_object()
        return AgentlyRequestData(
            client_options={},
            headers={},
            data={
                "attempt": type(self).attempts,
                "output_format": prompt_object.output_format,
            },
            request_options={"stream": True},
            request_url="mock://validate-json-requester",
        )

    async def request_model(self, request_data: AgentlyRequestData):
        attempt = int(request_data.data.get("attempt", 1))
        index = min(attempt - 1, len(type(self).responses) - 1)
        yield "message", json.dumps(type(self).responses[index], ensure_ascii=False)

    async def broadcast_response(
        self,
        response_generator: AsyncGenerator[tuple[str, Any], None],
    ):
        response_text = ""
        async for event, data in response_generator:
            if event == "message":
                response_text += str(data)
        yield "done", response_text
        yield "meta", {"provider": "mock-validate", "model": "json"}


class MockValidateScalarRequester:
    name = "MockValidateScalarRequester"
    DEFAULT_SETTINGS: dict[str, Any] = {}
    attempts = 0
    responses: list[Any] = []

    def __init__(self, prompt, settings):
        self.prompt = prompt
        self.settings = settings

    @classmethod
    def reset(cls, responses: list[Any]):
        cls.attempts = 0
        cls.responses = list(responses)

    @staticmethod
    def _on_register():
        pass

    @staticmethod
    def _on_unregister():
        pass

    def generate_request_data(self):
        type(self).attempts += 1
        return AgentlyRequestData(
            client_options={},
            headers={},
            data={"attempt": type(self).attempts},
            request_options={"stream": True},
            request_url="mock://validate-scalar-requester",
        )

    async def request_model(self, request_data: AgentlyRequestData):
        attempt = int(request_data.data.get("attempt", 1))
        index = min(attempt - 1, len(type(self).responses) - 1)
        yield "payload", type(self).responses[index]

    async def broadcast_response(
        self,
        response_generator: AsyncGenerator[tuple[str, Any], None],
    ):
        payload = None
        async for event, data in response_generator:
            if event == "payload":
                payload = data
        yield "done", payload
        yield "meta", {"provider": "mock-validate", "model": "scalar"}


def _create_request(requester_cls: type[Any], name: str) -> ModelRequest:
    settings = Settings(name=f"{ name }-Settings", parent=Agently.settings)
    plugin_manager = PluginManager(settings, parent=Agently.plugin_manager, name=f"{ name }-PluginManager")
    plugin_manager.register("ModelRequester", requester_cls, activate=True)
    return ModelRequest(
        plugin_manager,
        agent_name=name,
        agent_id=f"{ name }-id",
        parent_settings=settings,
    )


def _create_agent(requester_cls: type[Any], name: str):
    settings = Settings(name=f"{ name }-AgentSettings", parent=Agently.settings)
    plugin_manager = PluginManager(settings, parent=Agently.plugin_manager, name=f"{ name }-AgentPluginManager")
    plugin_manager.register("ModelRequester", requester_cls, activate=True)
    return Agently.AgentType(
        plugin_manager,
        parent_settings=settings,
        name=name,
    )


@pytest.mark.asyncio
async def test_request_validate_chain_and_runtime_handler_order():
    MockValidateJSONRequester.reset([{"answer": "ok"}])
    request = _create_request(MockValidateJSONRequester, "validate-order")
    request.output({"answer": (str,)})

    seen: list[tuple[str, dict[str, Any], int]] = []

    def first(result, context):
        seen.append(("first", dict(result), context.attempt_index))
        return True

    async def second(result, context):
        seen.append(("second", dict(result), context.attempt_index))
        return True

    def third(result, context):
        seen.append(("third", dict(result), context.attempt_index))
        return True

    data = await request.validate(first).validate(second).async_start(validate_handler=third)

    assert data == {"answer": "ok"}
    assert [name for name, _, _ in seen] == ["first", "second", "third"]
    assert all(result == {"answer": "ok"} for _, result, _ in seen)
    assert all(attempt_index == 1 for _, _, attempt_index in seen)


@pytest.mark.asyncio
async def test_agent_validate_failure_retries_and_emits_runtime_events():
    MockValidateJSONRequester.reset([{"status": "draft"}, {"status": "ready"}])
    agent = _create_agent(MockValidateJSONRequester, "validate-agent")
    agent.output({"status": (str,)})
    agent.validate(lambda result, context: result["status"] == "ready")

    captured = []

    async def capture(event):
        captured.append(event)

    hook_name = "test_model_request_validate.agent_retry"
    Agently.event_center.register_hook(capture, hook_name=hook_name)
    try:
        data = await agent.async_start(max_retries=1)
    finally:
        Agently.event_center.unregister_hook(hook_name)

    assert data == {"status": "ready"}
    assert MockValidateJSONRequester.attempts == 2

    validation_event = next(event for event in captured if event.event_type == "model.validation_failed")
    assert validation_event.payload["validator_name"] == "<lambda>"
    assert validation_event.payload["reason"] == "Validation failed in <lambda>."
    assert validation_event.payload["retry_count"] == 0
    assert validation_event.payload["max_retries"] == 1
    assert validation_event.payload["response_text"] == '{"status": "draft"}'

    retry_event = next(event for event in captured if event.event_type == "model.retrying")
    assert retry_event.payload["retry_reason"] == "validate"
    assert retry_event.payload["validation_reason"] == "Validation failed in <lambda>."
    assert retry_event.payload["next_attempt_index"] == 2


@pytest.mark.asyncio
async def test_validate_no_retry_can_return_last_result_when_raise_disabled():
    MockValidateJSONRequester.reset([{"status": "draft"}])
    request = _create_request(MockValidateJSONRequester, "validate-no-retry")
    request.output({"status": (str,)})

    data = await request.async_start(
        validate_handler=lambda result, context: {
            "ok": False,
            "reason": "draft is not publishable",
            "no_retry": True,
        },
        max_retries=3,
        raise_ensure_failure=False,
    )

    assert data == {"status": "draft"}
    assert MockValidateJSONRequester.attempts == 1


@pytest.mark.asyncio
async def test_validate_stop_raises_without_retry():
    MockValidateJSONRequester.reset([{"status": "draft"}])
    request = _create_request(MockValidateJSONRequester, "validate-stop")
    request.output({"status": (str,)})

    with pytest.raises(ValueError, match="stop immediately"):
        await request.async_start(
            validate_handler=lambda result, context: {
                "ok": False,
                "reason": "stop immediately",
                "stop": True,
            },
            max_retries=3,
        )

    assert MockValidateJSONRequester.attempts == 1


@pytest.mark.asyncio
async def test_validate_raise_value_stops_with_explicit_exception():
    MockValidateJSONRequester.reset([{"status": "draft"}])
    request = _create_request(MockValidateJSONRequester, "validate-raise")
    request.output({"status": (str,)})

    with pytest.raises(RuntimeError, match="fatal validation"):
        await request.async_start(
            validate_handler=lambda result, context: {
                "ok": False,
                "raise": RuntimeError("fatal validation"),
            },
            max_retries=3,
        )

    assert MockValidateJSONRequester.attempts == 1


@pytest.mark.asyncio
async def test_validate_handler_exception_retries_and_emits_validation_error():
    MockValidateJSONRequester.reset([{"answer": "ok"}, {"answer": "ok"}])
    request = _create_request(MockValidateJSONRequester, "validate-error")
    request.output({"answer": (str,)})

    attempts: list[int] = []

    def flaky_validator(result, context):
        del result
        attempts.append(context.attempt_index)
        if context.attempt_index == 1:
            raise RuntimeError("validator boom")
        return True

    captured = []

    async def capture(event):
        captured.append(event)

    hook_name = "test_model_request_validate.validation_error"
    Agently.event_center.register_hook(capture, hook_name=hook_name)
    try:
        data = await request.async_start(validate_handler=flaky_validator, max_retries=1)
    finally:
        Agently.event_center.unregister_hook(hook_name)

    assert data == {"answer": "ok"}
    assert attempts == [1, 2]

    validation_error_event = next(event for event in captured if event.event_type == "model.validation_error")
    assert validation_error_event.payload["validator_name"] == "flaky_validator"
    assert validation_error_event.payload["error_kind"] == "RuntimeError"
    assert validation_error_event.payload["reason"] == "validator boom"
    assert validation_error_event.payload["response_text"] == '{"answer": "ok"}'


@pytest.mark.asyncio
async def test_validate_returns_latest_result_when_retries_exhausted_and_raise_disabled():
    MockValidateJSONRequester.reset([{"status": "draft"}, {"status": "still-draft"}])
    request = _create_request(MockValidateJSONRequester, "validate-latest")
    request.output({"status": (str,)})

    data = await request.async_start(
        validate_handler=lambda result, context: False,
        max_retries=1,
        raise_ensure_failure=False,
    )

    assert data == {"status": "still-draft"}
    assert MockValidateJSONRequester.attempts == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("responses", "expected_validate_result", "expected_return"),
    [
        ([7], {"value": 7}, 7),
        ([["a", "b"]], {"value": ["a", "b"]}, ["a", "b"]),
    ],
)
async def test_validate_receives_canonical_scalar_and_list_snapshots(
    responses: list[Any],
    expected_validate_result: dict[str, Any],
    expected_return: Any,
):
    MockValidateScalarRequester.reset(responses)
    request = _create_request(MockValidateScalarRequester, "validate-canonical")
    request.input("Return the prepared payload.")

    seen: list[dict[str, Any]] = []

    def validator(result, context):
        del context
        seen.append(dict(result))
        return True

    data = await request.async_start(validate_handler=validator)

    assert data == expected_return
    assert seen == [expected_validate_result]


@pytest.mark.asyncio
async def test_validate_runs_once_per_response_and_context_exposes_result_object():
    MockValidateJSONRequester.reset([{"status": "OPEN", "priority": 1}])
    request = _create_request(MockValidateJSONRequester, "validate-response-cache")
    request.output(
        {
            "status": (str,),
            "priority": (int,),
        }
    )

    calls: list[dict[str, Any]] = []
    contexts = []

    def validator(result, context):
        calls.append(dict(result))
        contexts.append(context)
        return True

    response = request.validate(validator).get_response()
    result_object = await response.async_get_data_object()
    parsed_result = await response.async_get_data()

    assert result_object is not None
    assert parsed_result == {"status": "OPEN", "priority": 1}
    assert calls == [{"status": "OPEN", "priority": 1}]
    assert contexts[0].result_object is not None
    assert contexts[0].typed is result_object


@pytest.mark.asyncio
async def test_ensure_keys_runs_before_validate_handlers():
    MockValidateJSONRequester.reset(
        [
            {"summary": "draft"},
            {"summary": "ready", "reply": "done"},
        ]
    )
    request = _create_request(MockValidateJSONRequester, "validate-after-ensure")
    request.output(
        {
            "summary": (str,),
            "reply": (str,),
        }
    )

    seen: list[dict[str, Any]] = []

    def validator(result, context):
        del context
        seen.append(dict(result))
        return True

    data = await request.async_start(
        ensure_keys=["reply"],
        validate_handler=validator,
        max_retries=1,
    )

    assert data == {"summary": "ready", "reply": "done"}
    assert seen == [{"summary": "ready", "reply": "done"}]
