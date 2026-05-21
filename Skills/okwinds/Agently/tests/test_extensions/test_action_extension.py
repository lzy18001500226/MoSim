import pytest
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import json
import os
import asyncio
import time
from collections.abc import AsyncGenerator
from types import SimpleNamespace
from typing import Any
from agently import Agently
from agently.core import PluginManager
from agently.types.data import AgentlyRequestData
from agently.types.data import StreamingData
from agently.utils import Settings


class MockActionExtensionRequester:
    name = "MockActionExtensionRequester"
    DEFAULT_SETTINGS: dict[str, object] = {}

    def __init__(self, prompt, settings):
        self.prompt = prompt
        self.settings = settings

    @staticmethod
    def _on_register():
        pass

    @staticmethod
    def _on_unregister():
        pass

    def generate_request_data(self):
        prompt_object = self.prompt.to_prompt_object()
        return AgentlyRequestData(
            client_options={},
            headers={},
            data={
                "messages": self.prompt.to_messages(),
                "prompt_text": self.prompt.to_text(),
                "output_format": prompt_object.output_format,
                "action_results": self.prompt.get("action_results"),
            },
            request_options={"stream": True},
            request_url="mock://tool-extension",
        )

    async def request_model(self, request_data: AgentlyRequestData):
        action_results = request_data.data.get("action_results", {})
        if isinstance(action_results, dict):
            result_value = action_results.get("Use add")
            if result_value is None:
                result_value = action_results.get("Use add (2)")
        else:
            result_value = None
        yield "message", json.dumps({"result": result_value}, ensure_ascii=False)

    async def broadcast_response(
        self,
        response_generator: AsyncGenerator[tuple[str, object], None],
    ):
        response_text = ""
        async for event, data in response_generator:
            if event == "message":
                response_text += str(data)
        yield "done", response_text
        yield "meta", {"provider": "mock-tool-extension"}


def _create_test_agent():
    settings = Settings(name="ActionExtensionTestSettings", parent=Agently.settings)
    plugin_manager = PluginManager(settings, parent=Agently.plugin_manager, name="ActionExtensionTestPluginManager")
    plugin_manager.register("ModelRequester", MockActionExtensionRequester, activate=True)
    return Agently.AgentType(
        plugin_manager,
        parent_settings=settings,
        name="tool-extension-agent",
    )


def test_action_extension():
    agent = _create_test_agent()

    @agent.tool_func
    async def add(a: int, b: int) -> int:
        """
        Get result of `a(int)` add `b(int)`
        """
        await asyncio.sleep(1)
        assert a == 34643523
        return a + b

    async def fake_plan_handler(
        context,
        request,
    ):
        _ = request
        done_plans = context.get("done_plans", [])
        if len(done_plans) == 0:
            return {
                "next_action": "execute",
                "execution_commands": [
                    {
                        "purpose": "Use add",
                        "tool_name": "add",
                        "tool_kwargs": {"a": 34643523, "b": 52131231},
                        "todo_suggestion": "respond",
                    }
                ],
            }
        return {
            "next_action": "response",
            "execution_commands": [],
        }

    agent.register_tool_plan_analysis_handler(fake_plan_handler)

    result = (
        agent.input("34643523+52131231=? Use tool to calculate!")
        .use_tool(add)
        .output(
            {
                "result": (int,),
            }
        )
        .start()
    )
    assert result["result"] == 86774754


def test_action_extension_set_tool_loop_config():
    agent = Agently.create_agent()
    assert agent.action is agent.tool
    assert callable(agent.use_actions)
    assert callable(agent.action_func)
    agent.set_tool_loop(
        enabled=True,
        max_rounds=3,
        concurrency=2,
        timeout=6.5,
    )
    assert agent.settings.get("tool.loop.enabled") is True
    assert agent.settings.get("tool.loop.max_rounds") == 3
    assert agent.settings.get("tool.loop.concurrency") == 2
    assert agent.settings.get("tool.loop.timeout") == 6.5


def test_action_extension_use_sandbox_registers_agent_scoped_bash_action(tmp_path):
    agent = Agently.create_agent()
    action_id = f"agent_bash_sandbox_{ agent.name }"
    agent.use_sandbox(
        "bash",
        action_id=action_id,
        allowed_cmd_prefixes=["pwd"],
        allowed_workdir_roots=[str(tmp_path)],
    )

    action_list = agent.action.get_action_list(tags=[f"agent-{ agent.name }"])
    assert any(action.get("action_id") == action_id for action in action_list)

    result = agent.action.execute_action(
        action_id,
        {"cmd": "pwd", "workdir": str(tmp_path)},
    )
    assert result.get("status") == "success"
    assert str(tmp_path) in str(result.get("data"))


def test_action_extension_enable_python_registers_run_python_action():
    agent = Agently.create_agent()
    agent.enable_python(action_id="test_run_python", desc="Use this only for arithmetic tests.")

    action_list = agent.action.get_action_list(tags=[f"agent-{ agent.name }"])
    assert any(action.get("action_id") == "test_run_python" for action in action_list)
    spec = agent.action.action_registry.get_spec("test_run_python")
    assert spec is not None
    spec_desc = str(spec.get("desc", ""))
    assert "Run Python code in a managed safe sandbox" in spec_desc
    assert "Use this only for arithmetic tests." in spec_desc

    result = agent.action.execute_action(
        "test_run_python",
        {"python_code": ["numbers = [1, 2, 3]", "result = sum(numbers)"]},
    )
    assert result.get("status") == "success"
    assert result.get("data", {}).get("result") == 6
    assert Agently.execution_environment.list(scope="action_call") == []


def test_action_extension_enable_shell_registers_run_bash_action(tmp_path):
    agent = Agently.create_agent()
    agent.enable_shell(root=tmp_path, commands=["pwd"], action_id="test_run_bash", desc="Only inspect the cwd.")

    spec = agent.action.action_registry.get_spec("test_run_bash")
    assert spec is not None
    spec_desc = str(spec.get("desc", ""))
    assert "allowlisted shell command" in spec_desc
    assert "Only inspect the cwd." in spec_desc

    result = agent.action.execute_action(
        "test_run_bash",
        {"cmd": "pwd", "workdir": str(tmp_path)},
    )
    assert result.get("status") == "success"
    assert str(tmp_path) in str(result.get("data"))
    assert Agently.execution_environment.list(scope="action_call") == []


def test_action_extension_enable_helper_desc_modes():
    agent = Agently.create_agent()

    agent.enable_python(action_id="append_python", desc="Only use for sums.")
    append_spec = agent.action.action_registry.get_spec("append_python")
    assert append_spec is not None
    append_desc = str(append_spec.get("desc", ""))
    assert "Run Python code in a managed safe sandbox" in append_desc
    assert "Only use for sums." in append_desc

    agent.enable_python(action_id="override_python", desc="Custom calculator only.", desc_mode="override")
    override_spec = agent.action.action_registry.get_spec("override_python")
    assert override_spec is not None
    override_desc = str(override_spec.get("desc", ""))
    assert override_desc == "Custom calculator only."

    agent.enable_python(action_id="default_python", desc="Ignored guidance.", desc_mode="default")
    default_spec = agent.action.action_registry.get_spec("default_python")
    assert default_spec is not None
    default_desc = str(default_spec.get("desc", ""))
    assert "Run Python code in a managed safe sandbox" in default_desc
    assert "Ignored guidance." not in default_desc

    bad_mode: Any = "replace"
    with pytest.raises(ValueError, match="desc_mode"):
        agent.enable_python(action_id="bad_desc_mode", desc="x", desc_mode=bad_mode)


def test_action_extension_enable_workspace_registers_file_actions(tmp_path):
    agent = Agently.create_agent()
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "todo.txt").write_text("fix runtime docs\nship examples\n", encoding="utf-8")

    agent.enable_workspace(root=tmp_path, write=True, desc="Project notes workspace.")

    spec = agent.action.action_registry.get_spec("read_file")
    assert spec is not None
    spec_desc = str(spec.get("desc", ""))
    assert "Read a UTF-8 text file" in spec_desc
    assert "Project notes workspace." in spec_desc

    listed = agent.action.execute_action("list_files", {"path": "notes"})
    assert listed.get("status") == "success"
    assert listed.get("data") == ["notes/todo.txt"]

    searched = agent.action.execute_action("search_files", {"query": "runtime", "path": "notes"})
    assert searched.get("status") == "success"
    assert searched.get("data", [])[0]["line"] == 1

    read = agent.action.execute_action("read_file", {"path": "notes/todo.txt"})
    assert read.get("status") == "success"
    assert "ship examples" in read.get("data", {}).get("content", "")

    written = agent.action.execute_action("write_file", {"path": "notes/out.txt", "content": "ok"})
    assert written.get("status") == "success"
    assert (tmp_path / "notes" / "out.txt").read_text(encoding="utf-8") == "ok"

    outside = agent.action.execute_action("read_file", {"path": "../outside.txt"})
    assert outside.get("status") == "error"


@pytest.mark.asyncio
async def test_action_extension_request_prefix_injects_action_results(monkeypatch):
    agent = Agently.create_agent()
    request = agent.create_request()
    prompt = request.prompt
    prompt.set("input", "test tool loop")

    monkeypatch.setattr(
        agent.action,
        "get_action_list",
        lambda tags=None: [
            {"name": "dummy_tool", "desc": "dummy", "kwargs": {}},
        ],
    )

    async def fake_loop(**kwargs):
        _ = kwargs
        return [
            {
                "purpose": "fetch_dummy",
                "tool_name": "dummy_tool",
                "kwargs": {},
                "next": "respond",
                "success": True,
                "result": {"ok": 1},
                "error": "",
            }
        ]

    monkeypatch.setattr(agent.tool, "async_plan_and_execute", fake_loop)

    await agent._ActionExtension__request_prefix(prompt, None)  # type: ignore

    action_results = prompt.get("action_results")
    assert isinstance(action_results, dict)
    assert action_results.get("fetch_dummy") == {"ok": 1}
    assert "extra_instruction" in prompt


@pytest.mark.asyncio
async def test_action_extension_broadcast_prefix_keeps_action_and_tool_logs():
    agent = Agently.create_agent()
    full_result_data: dict[str, object] = {}
    agent._ActionExtension__action_logs = [  # type: ignore[attr-defined]
        {
            "purpose": "visible action",
            "action_id": "visible_action",
            "tool_name": "visible_action",
            "kwargs": {},
            "success": True,
            "result": {"ok": 1},
            "status": "success",
            "expose_to_model": True,
        },
        {
            "purpose": "hidden action",
            "action_id": "hidden_action",
            "tool_name": "hidden_action",
            "kwargs": {},
            "success": True,
            "result": {"ok": 2},
            "status": "success",
            "expose_to_model": False,
        },
    ]

    events = [event async for event in agent._ActionExtension__broadcast_prefix(full_result_data, None)]  # type: ignore[attr-defined]
    assert events[0][0] == "action"
    assert events[1][0] == "action"
    assert events[2][0] == "tool"
    assert full_result_data["extra"]["action_logs"][0]["action_id"] == "visible_action"  # type: ignore[index]
    assert len(full_result_data["extra"]["action_logs"]) == 2  # type: ignore[index]
    assert len(full_result_data["extra"]["tool_logs"]) == 1  # type: ignore[index]


@pytest.mark.asyncio
async def test_action_extension_plan_handler_instant_response_short_circuit(monkeypatch):
    agent = Agently.create_agent()
    request = agent.create_request()
    prompt = request.prompt
    prompt.set("input", "hello")
    prompt.set("instruct", "just answer directly")

    closed = False

    async def fake_close():
        nonlocal closed
        closed = True

    async def fake_async_get_data():
        raise AssertionError("async_get_data should not be called when next_action is response")

    class FakeResponse:
        def __init__(self):
            self.result = SimpleNamespace(
                async_get_data=fake_async_get_data,
                _response_parser=SimpleNamespace(
                    _response_consumer=SimpleNamespace(
                        close=fake_close,
                    )
                ),
            )

        def get_async_generator(self, type=None, **kwargs):
            _ = kwargs
            assert type == "instant"

            async def gen():
                yield StreamingData(
                    path="$.next_action",
                    value="response",
                    is_complete=True,
                )

            return gen()

    class FakeModelRequest:
        def __init__(self, *args, **kwargs):
            _ = (args, kwargs)

        def input(self, *args, **kwargs):
            _ = (args, kwargs)
            return self

        def info(self, *args, **kwargs):
            _ = (args, kwargs)
            return self

        def instruct(self, *args, **kwargs):
            _ = (args, kwargs)
            return self

        def output(self, *args, **kwargs):
            _ = (args, kwargs)
            return self

        def get_response(self, *, parent_run_context=None):
            _ = parent_run_context
            return FakeResponse()

    import agently.core as core_module

    monkeypatch.setattr(core_module, "ModelRequest", FakeModelRequest)

    decision = await agent.tool._default_plan_analysis_handler(  # type: ignore[attr-defined]
        {
            "prompt": prompt,
            "settings": agent.settings,
            "agent_name": agent.name,
            "round_index": 0,
            "max_rounds": 3,
            "done_plans": [],
            "last_round_records": [],
            "action": agent.tool,
            "runtime": agent.tool.action_runtime,
        },
        {
            "action_list": [{"name": "dummy_tool", "desc": "dummy", "kwargs": {}}],
            "planning_protocol": "structured_plan",
        },
    )

    assert decision.get("next_action") == "response"
    assert decision.get("execution_commands") == []
    assert closed is True


@pytest.mark.asyncio
async def test_action_extension_generate_tool_command_only(monkeypatch):
    agent = Agently.create_agent()
    agent.input("find docs")

    monkeypatch.setattr(
        agent.tool,
        "get_tool_list",
        lambda tags=None: [{"name": "search", "desc": "search", "kwargs": {"query": ("str", "")}}],
    )

    async def fake_plan_handler(
        context,
        request,
    ):
        _ = (context, request)
        return {
            "next_action": "execute",
            "execution_commands": [
                {
                    "purpose": "search docs",
                    "tool_name": "search",
                    "tool_kwargs": {"query": "Agently TriggerFlow"},
                    "todo_suggestion": "browse best result",
                }
            ],
        }

    agent.register_tool_plan_analysis_handler(fake_plan_handler)

    called = False

    async def fake_async_call_tool(*_args, **_kwargs):
        nonlocal called
        called = True
        raise AssertionError("Tool should not be called in generate_tool_command")

    monkeypatch.setattr(agent.tool, "async_call_tool", fake_async_call_tool)

    commands = await agent.async_generate_tool_command()
    assert called is False
    assert len(commands) == 1
    assert commands[0].get("tool_name") == "search"
    assert commands[0].get("tool_kwargs") == {"query": "Agently TriggerFlow"}


@pytest.mark.asyncio
async def test_action_extension_get_action_result_runs_action_loop_without_reply(monkeypatch):
    agent = Agently.create_agent()
    agent.input("normalize this title")

    action_list = [
        {
            "action_id": "normalize_title",
            "name": "normalize_title",
            "desc": "Normalize title text",
            "kwargs": {"text": ("str", "raw title")},
        }
    ]
    monkeypatch.setattr(agent.action, "get_action_list", lambda tags=None: action_list)

    async def fake_plan_and_execute(**kwargs):
        assert kwargs["prompt"] is agent.request.prompt
        assert kwargs["settings"] is agent.settings
        assert kwargs["action_list"] == action_list
        assert kwargs["agent_name"] == agent.name
        assert kwargs["max_rounds"] == 2
        assert kwargs["concurrency"] == 1
        assert kwargs["timeout"] == 3.0
        assert kwargs["planning_protocol"] == "structured_plan"
        return [
            {
                "ok": True,
                "status": "success",
                "purpose": "normalize",
                "action_id": "normalize_title",
                "kwargs": {"text": "  Hello  "},
                "result": "hello",
                "data": "hello",
                "success": True,
                "error": "",
            }
        ]

    monkeypatch.setattr(agent.action, "async_plan_and_execute", fake_plan_and_execute)

    records = await agent.async_get_action_result(
        max_rounds=2,
        concurrency=1,
        timeout=3.0,
        planning_protocol="structured_plan",
    )

    assert len(records) == 1
    assert records[0].get("action_id") == "normalize_title"
    assert records[0].get("result") == "hello"
    assert agent.request.prompt.get("action_results") == {"normalize": "hello"}


@pytest.mark.asyncio
async def test_action_extension_get_action_result_can_skip_reply_storage(monkeypatch):
    agent = Agently.create_agent()
    agent.input("normalize this title")

    monkeypatch.setattr(
        agent.action,
        "get_action_list",
        lambda tags=None: [{"action_id": "normalize_title", "desc": "Normalize title text", "kwargs": {}}],
    )

    async def fake_plan_and_execute(**kwargs):
        _ = kwargs
        return [
            {
                "ok": True,
                "status": "success",
                "purpose": "normalize",
                "action_id": "normalize_title",
                "kwargs": {},
                "result": "hello",
                "data": "hello",
                "success": True,
                "error": "",
            }
        ]

    monkeypatch.setattr(agent.action, "async_plan_and_execute", fake_plan_and_execute)

    records = await agent.async_get_action_result(store_for_reply=False)

    assert records[0].get("result") == "hello"
    assert agent.request.prompt.get("action_results") is None


@pytest.mark.asyncio
async def test_action_extension_request_prefix_reuses_stored_action_result(monkeypatch):
    agent = Agently.create_agent()
    request = agent.create_request()
    prompt = request.prompt
    prompt.set("input", "use stored result")
    prompt.set("action_results", {"normalize": "hello"})
    prompt.set("extra_instruction", agent.action.ACTION_RESULT_QUOTE_NOTICE)
    agent._ActionExtension__action_logs = [  # type: ignore[attr-defined]
        {
            "ok": True,
            "status": "success",
            "purpose": "normalize",
            "action_id": "normalize_title",
            "kwargs": {},
            "result": "hello",
            "data": "hello",
            "success": True,
            "error": "",
            "expose_to_model": True,
        }
    ]
    agent._ActionExtension__prepared_action_results = {"normalize": "hello"}  # type: ignore[attr-defined]

    async def fake_plan_and_execute(**kwargs):
        _ = kwargs
        raise AssertionError("Stored action_results should skip action loop execution")

    monkeypatch.setattr(agent.action, "async_plan_and_execute", fake_plan_and_execute)

    await agent._ActionExtension__request_prefix(prompt, None)  # type: ignore[attr-defined]

    full_result_data: dict[str, object] = {}
    events = [event async for event in agent._ActionExtension__broadcast_prefix(full_result_data, None)]  # type: ignore[attr-defined]
    assert events[0][0] == "action"
    assert full_result_data["extra"]["action_logs"][0]["result"] == "hello"  # type: ignore[index]


def test_action_extension_must_call_soft_compatible(monkeypatch):
    agent = Agently.create_agent()
    agent.input("find docs")

    monkeypatch.setattr(
        agent.tool,
        "get_tool_list",
        lambda tags=None: [{"name": "search", "desc": "search", "kwargs": {"query": ("str", "")}}],
    )

    async def fake_plan_handler(
        context,
        request,
    ):
        _ = (context, request)
        return {
            "next_action": "execute",
            "execution_commands": [
                {
                    "purpose": "search docs",
                    "tool_name": "search",
                    "tool_kwargs": {"query": "Agently TriggerFlow"},
                    "todo_suggestion": "browse best result",
                }
            ],
        }

    agent.register_tool_plan_analysis_handler(fake_plan_handler)

    with pytest.warns(DeprecationWarning):
        commands = agent.must_call()
    assert len(commands) == 1
    assert commands[0].get("tool_name") == "search"
