import logging
import pytest
import yaml
from agently import Agently
from agently.compatibility import (
    get_current_release_manifest,
    get_devtools_compatibility_manifest,
    get_skills_compatibility_manifest,
)


_RUNTIME_LOG_KEYS = (
    "debug",
    "runtime.show_model_logs",
    "runtime.show_action_logs",
    "runtime.show_tool_logs",
    "runtime.show_trigger_flow_logs",
    "runtime.show_runtime_logs",
    "runtime.httpx_log_level",
)


def _snapshot_runtime_log_settings():
    return {key: Agently.settings.get(key, None) for key in _RUNTIME_LOG_KEYS}


def _restore_runtime_log_settings(snapshot):
    for key, value in snapshot.items():
        Agently.settings.set(key, value)
    level_name = Agently.settings.get("runtime.httpx_log_level", "WARNING")
    level = getattr(logging, str(level_name).upper(), logging.WARNING)
    logging.getLogger("httpx").setLevel(level)
    logging.getLogger("httpcore").setLevel(level)


@pytest.mark.asyncio
async def test_settings():
    Agently.set_settings("test", "test")
    assert Agently.settings["test"] == "test"


def test_agently_set_api_key_and_alias_mapping():
    original_api_key = Agently.settings.get("agently.api_key", None)
    try:
        Agently.set_api_key("official-key")
        assert Agently.settings["agently.api_key"] == "official-key"

        Agently.set_settings("agently_api_key", "official-key-alias")
        assert Agently.settings["agently.api_key"] == "official-key-alias"
    finally:
        Agently.set_settings("agently.api_key", original_api_key)


def test_action_executor_plugins_registered():
    plugin_list = Agently.plugin_manager.get_plugin_list("ActionExecutor")
    assert "LocalFunctionActionExecutor" in plugin_list
    assert "MCPActionExecutor" in plugin_list
    assert "PythonSandboxActionExecutor" in plugin_list
    assert "BashSandboxActionExecutor" in plugin_list


def test_action_runtime_and_flow_plugins_registered():
    runtime_plugins = Agently.plugin_manager.get_plugin_list("ActionRuntime")
    flow_plugins = Agently.plugin_manager.get_plugin_list("ActionFlow")
    plugin_map = Agently.plugin_manager.get_plugin_list()

    assert "AgentlyActionRuntime" in runtime_plugins
    assert "TriggerFlowActionFlow" in flow_plugins
    assert getattr(Agently.action_runtime, "name", "") == "AgentlyActionRuntime"
    assert getattr(Agently.action_flow, "name", "") == "TriggerFlowActionFlow"
    assert "ToolManager" not in plugin_map


def test_dynamic_task_plugin_registered():
    planner_plugins = Agently.plugin_manager.get_plugin_list("TaskDAGPlanner")
    task = Agently.create_dynamic_task(
        "demo",
        plan={
            "graph_id": "registered",
            "tasks": [{"id": "a", "kind": "local", "binding": "local_handler"}],
        },
        handlers={"local_handler": lambda context: context.task.id},
    )

    assert "AgentlyTaskDAGPlanner" in planner_plugins
    assert task.planner.name == "AgentlyTaskDAGPlanner"
    assert "local_handler" in task.resolver.keys()


def test_agent_can_create_dynamic_task():
    agent = Agently.create_agent("graph-agent")
    task = agent.create_dynamic_task(
        "demo",
        plan={
            "graph_id": "agent-task",
            "tasks": [{"id": "a", "kind": "local", "binding": "local_handler"}],
        },
        handlers={"local_handler": lambda context: context.task.id},
    )

    assert task.name == "graph-agent-DynamicTask"
    assert task.settings.parent is agent.settings


@pytest.mark.asyncio
async def test_dynamic_task_runs_submitted_plan():
    async def run_task(context):
        if context.dependency_results:
            return f"{ context.task.id }:{ context.dependency_results['a'] }"
        return f"{ context.task.id }:{ context.graph_input['value'] }"

    graph = {
        "graph_id": "main-package-workflow",
        "tasks": [
            {"id": "a", "kind": "local", "binding": "local_handler"},
            {"id": "b", "kind": "local", "binding": "local_handler", "depends_on": ["a"]},
        ],
        "semantic_outputs": {"final": "b"},
    }
    task = Agently.create_dynamic_task(
        "run planned graph",
        plan=graph,
        handlers={"local_handler": run_task},
    )

    snapshot = await task.async_run(graph_input={"value": "ok"}, timeout=1)

    assert snapshot["task_results"] == {"a": "a:ok", "b": "b:a:ok"}
    assert snapshot["semantic_outputs"]["final"]["task_id"] == "b"


@pytest.mark.asyncio
async def test_dynamic_task_model_output_schema_uses_agently_request_pipeline():
    schema = {
        "brief": (str, "customer-facing briefing", True),
        "next_update": (str, "next update timing", True),
    }

    class FakeModelRequest:
        def __init__(self):
            self.output_schema = None
            self.start_kwargs = None

        def input(self, value):
            return self

        def instruct(self, value):
            return self

        def output(self, value):
            self.output_schema = value
            return self

        async def async_start(self, **kwargs):
            self.start_kwargs = kwargs
            return {"brief": "Latency is resolved.", "next_update": "After duplicate checks finish."}

    request = FakeModelRequest()
    task = Agently.create_dynamic_task(
        "brief an incident",
        plan={
            "graph_id": "model-output-contract",
            "task_schema_version": "task_dag/v1",
            "tasks": [{"id": "write_brief", "kind": "model"}],
            "semantic_outputs": {"frontstage": "write_brief"},
        },
        model=request,
        output_schema=schema,
        ensure_keys=["brief", "next_update"],
    )

    snapshot = await task.async_run(timeout=1)

    assert request.output_schema == schema
    assert request.start_kwargs == {"ensure_keys": ["brief", "next_update"]}
    assert snapshot["semantic_outputs"]["frontstage"]["result"]["brief"] == "Latency is resolved."


def test_dynamic_task_can_be_created_without_explicit_model_source():
    task = Agently.create_dynamic_task("needs planning")

    assert "model" in task.resolver.keys()
    assert "action" not in task.resolver.keys()
    assert task.planner.available_bindings == ("model",)


def test_dynamic_task_exposes_actions_only_when_explicit():
    task = Agently.create_dynamic_task("needs action", actions=Agently.action)

    assert "action" in task.resolver.keys()
    assert task.planner.available_bindings == ("model", "action")


def test_deprecated_action_manager_aliases_warn():
    with pytest.warns(DeprecationWarning):
        assert Agently.action.tool_manager is not None
    with pytest.warns(DeprecationWarning):
        assert Agently.action.action_manager is not None


def test_tool_manager_plugin_registration_warns():
    from agently.builtins.plugins.ToolManager.AgentlyToolManager import AgentlyToolManager
    from agently.core import PluginManager
    from agently.utils import Settings

    settings = Settings(name="DeprecatedToolManagerSettings", parent=Agently.settings)
    plugin_manager = PluginManager(settings, parent=Agently.plugin_manager, name="DeprecatedToolManagerPluginManager")

    with pytest.warns(DeprecationWarning):
        plugin_manager.register("ToolManager", AgentlyToolManager)


def test_action_plugin_protocols_exported_for_third_party_plugins():
    from agently.types.plugins import (
        ActionExecutionHandler,
        ActionExecutor,
        ActionFlow,
        ActionPlanningHandler,
        ActionRuntime,
        StandardActionExecutionHandler,
        StandardActionPlanningHandler,
    )

    assert ActionExecutor is not None
    assert ActionRuntime is not None
    assert ActionFlow is not None
    assert ActionPlanningHandler is not None
    assert ActionExecutionHandler is not None
    assert StandardActionPlanningHandler is not None
    assert StandardActionExecutionHandler is not None


def test_agently_load_settings_file(tmp_path, monkeypatch):
    config_path = tmp_path / "settings.yaml"
    env_path = tmp_path / ".env"

    config_path.write_text(
        yaml.safe_dump(
            {
                "test_main_package": {
                    "base_url": "${ENV.TEST_MAIN_PACKAGE_BASE_URL}",
                }
            }
        ),
        encoding="utf-8",
    )
    env_path.write_text("TEST_MAIN_PACKAGE_BASE_URL=https://example.com\n", encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("TEST_MAIN_PACKAGE_BASE_URL", raising=False)

    Agently.load_settings("yaml_file", str(config_path), auto_load_env=True)

    assert Agently.settings["test_main_package.base_url"] == "https://example.com"


def test_agently_load_settings_refresh_httpx_log_level(tmp_path):
    config_path = tmp_path / "settings.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "runtime": {
                    "httpx_log_level": "INFO",
                }
            }
        ),
        encoding="utf-8",
    )

    Agently.load_settings("yaml_file", str(config_path))

    assert logging.getLogger("httpx").level == logging.INFO
    assert logging.getLogger("httpcore").level == logging.INFO


def test_agently_set_debug_mapping_profiles():
    snapshot = _snapshot_runtime_log_settings()
    try:
        Agently.set_settings("debug", True)
        assert Agently.settings["debug"] == "simple"
        assert Agently.settings["runtime.show_model_logs"] == "simple"
        assert Agently.settings["runtime.show_action_logs"] == "simple"
        assert Agently.settings["runtime.show_tool_logs"] == "simple"
        assert Agently.settings["runtime.show_trigger_flow_logs"] == "simple"
        assert Agently.settings["runtime.show_runtime_logs"] == "simple"
        assert logging.getLogger("httpx").level == logging.WARNING

        Agently.set_settings("debug", "detail")
        assert Agently.settings["debug"] == "detail"
        assert Agently.settings["runtime.show_model_logs"] == "detail"
        assert Agently.settings["runtime.show_action_logs"] == "detail"
        assert Agently.settings["runtime.show_runtime_logs"] == "detail"
        assert logging.getLogger("httpx").level == logging.INFO

        Agently.set_settings("debug", False)
        assert Agently.settings["debug"] == "off"
        assert Agently.settings["runtime.show_model_logs"] == "off"
        assert Agently.settings["runtime.show_action_logs"] == "off"
        assert Agently.settings["runtime.show_tool_logs"] == "off"
        assert Agently.settings["runtime.show_trigger_flow_logs"] == "off"
        assert Agently.settings["runtime.show_runtime_logs"] == "off"
        assert logging.getLogger("httpx").level == logging.WARNING
    finally:
        _restore_runtime_log_settings(snapshot)


def test_agently_load_settings_applies_debug_mapping(tmp_path):
    snapshot = _snapshot_runtime_log_settings()
    try:
        config_path = tmp_path / "settings.yaml"
        config_path.write_text(yaml.safe_dump({"debug": "detail"}), encoding="utf-8")

        Agently.load_settings("yaml_file", str(config_path))

        assert Agently.settings["debug"] == "detail"
        assert Agently.settings["runtime.show_model_logs"] == "detail"
        assert Agently.settings["runtime.show_action_logs"] == "detail"
        assert Agently.settings["runtime.show_tool_logs"] == "detail"
        assert Agently.settings["runtime.show_trigger_flow_logs"] == "detail"
        assert Agently.settings["runtime.show_runtime_logs"] == "detail"
        assert logging.getLogger("httpx").level == logging.INFO
    finally:
        _restore_runtime_log_settings(snapshot)


def test_request_quick_prompt_supports_key_value_and_kwargs():
    request = Agently.create_request()

    request.info("context", "Public-facing API handler", framework="FastAPI")

    assert request.prompt.to_prompt_object().info == {
        "context": "Public-facing API handler",
        "framework": "FastAPI",
    }


def test_request_quick_prompt_preserves_explicit_mappings():
    request = Agently.create_request()

    request.instruct("Hello ${name}", mappings={"name": "Alice"})

    assert request.prompt.to_prompt_object().instruct == "Hello Alice"


def test_devtools_compatibility_manifest_declares_runtime_protocol():
    manifest = get_devtools_compatibility_manifest()

    assert manifest["companion_package"] == "agently-devtools"
    assert manifest["runtime_protocol"].startswith("agently-devtools.observation-runtime.v")
    assert manifest["recommended_version_specifier"]
    assert manifest["framework_version"] == get_current_release_manifest()["framework_version"]


def test_skills_compatibility_manifest_declares_authoring_protocols():
    manifest = get_skills_compatibility_manifest()

    assert manifest["repository"] == "Agently-Skills"
    assert manifest["authoring_protocol"].startswith("agently-skills.authoring.v")
    assert manifest["devtools_guidance_protocol"].startswith(
        "agently-skills.devtools-guidance.v"
    )


def test_agent_quick_prompt_supports_key_value_and_kwargs():
    agent = Agently.create_agent()

    agent.info("context", "Public-facing API handler", framework="FastAPI", always=True)

    assert agent.agent_prompt.to_prompt_object().info == {
        "context": "Public-facing API handler",
        "framework": "FastAPI",
    }
