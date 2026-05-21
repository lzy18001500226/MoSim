import ast
import warnings
from pathlib import Path

import pytest

from agently import Agently, TriggerFlow
from agently.core.Session import Session
from agently.utils import (
    DeprecationWarnings,
    log_deprecated_once,
    reset_deprecation_warning_registry,
    warn_deprecated_once,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AGENTLY_ROOT = PROJECT_ROOT / "agently"
WARNING_HELPER = AGENTLY_ROOT / "utils" / "DeprecationWarnings.py"


def _collect_call_text(call: ast.Call) -> str:
    values: list[str] = []
    for node in ast.walk(call):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            values.append(node.value)
        elif isinstance(node, ast.Name):
            values.append(node.id)
        elif isinstance(node, ast.Attribute):
            values.append(node.attr)
    return " ".join(values)


def _is_warnings_warn_call(call: ast.Call) -> bool:
    func = call.func
    if isinstance(func, ast.Attribute):
        return isinstance(func.value, ast.Name) and func.value.id == "warnings" and func.attr == "warn"
    return isinstance(func, ast.Name) and func.id == "warn"


def _is_warning_log_call(call: ast.Call) -> bool:
    return isinstance(call.func, ast.Attribute) and call.func.attr == "warning"


def test_deprecation_warning_helpers_use_class_closure_exports():
    assert warn_deprecated_once is DeprecationWarnings.warn_deprecated_once
    assert log_deprecated_once is DeprecationWarnings.log_deprecated_once
    assert reset_deprecation_warning_registry is DeprecationWarnings.reset_registry


def test_warn_deprecated_once_preserves_deprecation_warning_category():
    def deprecated_api():
        warn_deprecated_once("test.deprecated", "deprecated")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        deprecated_api()
        deprecated_api()

    assert len(caught) == 1
    assert issubclass(caught[0].category, DeprecationWarning)
    assert Path(caught[0].filename) == Path(__file__)


def test_reset_deprecation_warning_registry_allows_deprecation_warning_again():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        warn_deprecated_once("test.reset.deprecated", "first")
        reset_deprecation_warning_registry()
        warn_deprecated_once("test.reset.deprecated", "second")

    assert [str(item.message) for item in caught] == ["first", "second"]


def test_deprecation_warning_setting_defaults_to_enabled():
    assert Agently.settings.get("runtime.show_deprecation_warnings") is True


def test_deprecation_warning_setting_can_disable_and_reenable_warnings():
    original_value = Agently.settings.get("runtime.show_deprecation_warnings", True)
    try:
        Agently.set_settings("runtime.show_deprecation_warnings", False)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            warn_deprecated_once("test.disabled.deprecated", "disabled")
        assert caught == []

        Agently.set_settings("runtime.show_deprecation_warnings", True)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            warn_deprecated_once("test.disabled.deprecated", "enabled")
            warn_deprecated_once("test.disabled.deprecated", "enabled")
        assert [str(item.message) for item in caught] == ["enabled"]
    finally:
        Agently.set_settings("runtime.show_deprecation_warnings", original_value)


def test_deprecation_warning_setting_accepts_off_string():
    original_value = Agently.settings.get("runtime.show_deprecation_warnings", True)
    try:
        Agently.set_settings("runtime.show_deprecation_warnings", "off")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            warn_deprecated_once("test.off.deprecated", "off")
        assert caught == []
    finally:
        Agently.set_settings("runtime.show_deprecation_warnings", original_value)


def test_log_deprecated_once_respects_deprecation_warning_setting():
    class Logger:
        def __init__(self):
            self.messages: list[str] = []

        def warning(self, message: str):
            self.messages.append(message)

    original_value = Agently.settings.get("runtime.show_deprecation_warnings", True)
    logger = Logger()
    try:
        Agently.set_settings("runtime.show_deprecation_warnings", False)
        log_deprecated_once("test.log.deprecated", logger, "disabled")
        assert logger.messages == []

        Agently.set_settings("runtime.show_deprecation_warnings", True)
        log_deprecated_once("test.log.deprecated", logger, "enabled")
        log_deprecated_once("test.log.deprecated", logger, "enabled")
        assert logger.messages == ["enabled"]
    finally:
        Agently.set_settings("runtime.show_deprecation_warnings", original_value)


def test_deprecated_triggerflow_runtime_data_warns_once_per_method():
    execution = TriggerFlow().create_execution()

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        execution.get_runtime_data("missing")
        execution.get_runtime_data("missing")
        execution.set_runtime_data("value", 1)
        execution.set_runtime_data("value", 2)

    messages = [str(item.message) for item in caught if issubclass(item.category, DeprecationWarning)]
    assert len(messages) == 2
    assert any("get_runtime_data" in message for message in messages)
    assert any("async_set_runtime_data" in message for message in messages)


def test_deprecated_triggerflow_result_apis_warn_once_each():
    execution = TriggerFlow().create_execution()

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        execution.set_result("one")
        execution.set_result("two")
        execution.get_result(timeout=0)
        execution.get_result(timeout=0)

    messages = [str(item.message) for item in caught if issubclass(item.category, DeprecationWarning)]
    assert len(messages) == 2
    assert any("set_result()" in message for message in messages)
    assert any("get_result()/async_get_result()" in message for message in messages)


def test_deprecated_action_aliases_warn_once_per_alias():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        _ = Agently.action.tool_manager
        _ = Agently.action.tool_manager
        _ = Agently.action.action_manager
        _ = Agently.action.action_manager

    messages = [str(item.message) for item in caught if issubclass(item.category, DeprecationWarning)]
    assert len(messages) == 2
    assert any("Action.tool_manager" in message for message in messages)
    assert any("Action.action_manager" in message for message in messages)


@pytest.mark.asyncio
async def test_deprecated_session_aliases_warn_once_per_alias():
    session = Session(auto_resize=False)

    async def execution_handler(full_context, context_window, memo, session_settings):
        _ = (full_context, context_window, session_settings)
        return None, [], memo

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        session.register_execution_handlers("legacy_drop", execution_handler)
        session.register_execution_handlers("legacy_drop_again", execution_handler)
        await session.async_execute_strategy("legacy_drop")
        await session.async_execute_strategy("legacy_drop_again")

    messages = [str(item.message) for item in caught if issubclass(item.category, DeprecationWarning)]
    assert len(messages) == 2
    assert any("register_execution_handlers" in message for message in messages)
    assert any("async_execute_strategy" in message for message in messages)


def test_deprecated_warnings_use_once_helper():
    violations: list[str] = []
    for path in AGENTLY_ROOT.rglob("*.py"):
        if path == WARNING_HELPER:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            call_text = _collect_call_text(node)
            direct_deprecation_warning = _is_warnings_warn_call(node) and (
                "DeprecationWarning" in call_text or "deprecated" in call_text
            )
            direct_deprecation_log = _is_warning_log_call(node) and "deprecated" in call_text
            if direct_deprecation_warning or direct_deprecation_log:
                relative = path.relative_to(PROJECT_ROOT)
                violations.append(f"{relative}:{node.lineno}")

    assert violations == []
