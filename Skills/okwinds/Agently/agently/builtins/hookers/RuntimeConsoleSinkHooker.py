# Copyright 2023-2026 AgentEra(Agently.Tech)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from typing import TYPE_CHECKING, Any, Literal, TypeAlias, cast

from agently.types.data.event import (
    get_triggerflow_event_aliases,
    normalize_triggerflow_event_type,
)
from agently.types.plugins import EventHooker
from agently.utils import DataFormatter, Settings

if TYPE_CHECKING:
    from agently.types.data import ObservationEvent


RuntimeLogProfile: TypeAlias = Literal["off", "simple", "detail"]


_VALID_RUNTIME_LOG_PROFILES = frozenset({"off", "simple", "detail"})
_ALWAYS_VISIBLE_LEVELS = frozenset({"WARNING", "ERROR", "CRITICAL"})
_CONSOLE_EVENT_FAMILIES = frozenset({"model", "action", "triggerflow", "runtime"})
_RUNTIME_PRINT_EVENTS = frozenset({"runtime.print"})
_SIMPLE_EVENT_TYPES = {
    "model": frozenset(
        {
            "model.requesting",
            "model.completed",
            "model.failed",
            "model.parse_failed",
            "model.request_failed",
            "model.retrying",
            "model.requester.error",
            "model.streaming_canceled",
            "model.validation_error",
            "model.validation_failed",
        }
    ),
    "action": frozenset(
        {
            "action.loop_started",
            "action.loop_completed",
            "action.loop_failed",
            "action.started",
            "action.completed",
            "action.failed",
            "tool.loop_started",
            "tool.loop_completed",
            "tool.loop_failed",
        }
    ),
    "triggerflow": frozenset(
        {
            "triggerflow.execution_started",
            "triggerflow.execution_completed",
            "triggerflow.execution_failed",
            "triggerflow.execution_resumed",
            "triggerflow.interrupt_raised",
        }
    ),
    "runtime": frozenset(
        {
            "runtime.print",
        }
    ),
}
_FAMILY_SETTINGS_KEYS = {
    "model": "runtime.show_model_logs",
    "action": "runtime.show_action_logs",
    "triggerflow": "runtime.show_trigger_flow_logs",
    "runtime": "runtime.show_runtime_logs",
}


def normalize_runtime_log_profile(value: Any, *, default: RuntimeLogProfile | str = "off") -> RuntimeLogProfile | str:
    if isinstance(value, bool):
        return "simple" if value else "off"
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in _VALID_RUNTIME_LOG_PROFILES:
            return normalized  # type: ignore[return-value]
        if normalized in {"true", "on"}:
            return "simple"
        if normalized in {"false", "none", "quiet"}:
            return "off"
        if normalized in {"summary", "verbose", "detailed"}:
            return "simple" if normalized == "summary" else "detail"
    return default


def coerce_runtime_log_profile(value: Any) -> RuntimeLogProfile:
    normalized = normalize_runtime_log_profile(value, default="")
    if normalized:
        return cast(RuntimeLogProfile, normalized)
    raise ValueError(
        '`debug` only accepts False | True | "simple" | "detail" | "off".'
    )


def resolve_runtime_event_family(event_type: str | None) -> str:
    if isinstance(event_type, str):
        if event_type.startswith("model."):
            return "model"
        if event_type.startswith(("action.", "tool.")):
            return "action"
        if any(alias.startswith("triggerflow.") for alias in get_triggerflow_event_aliases(event_type)):
            return "triggerflow"
    return "runtime"


def _payload_value(event: "ObservationEvent", key: str, default: Any = None) -> Any:
    if isinstance(event.payload, dict):
        return event.payload.get(key, default)
    return default


def _settings_layer_value(settings: Settings, key: str) -> Any:
    value = settings.get(key, None, inherit=False)
    if value is not None:
        return value
    parent = getattr(settings, "parent", None)
    if parent is not None:
        return _settings_layer_value(parent, key)
    return None


def _resolve_action_log_setting(settings: Settings) -> Any:
    current: Settings | None = settings
    while current is not None:
        action_value = current.get("runtime.show_action_logs", None, inherit=False)
        if action_value is not None:
            return action_value
        tool_value = current.get("runtime.show_tool_logs", None, inherit=False)
        if tool_value is not None:
            return tool_value
        current = getattr(current, "parent", None)
    return "off"


def resolve_runtime_log_profile(settings: Settings, event_type: str | None) -> RuntimeLogProfile:
    family = resolve_runtime_event_family(event_type)
    if family == "action":
        return cast(RuntimeLogProfile, normalize_runtime_log_profile(_resolve_action_log_setting(settings)))
    key = _FAMILY_SETTINGS_KEYS[family]
    return cast(RuntimeLogProfile, normalize_runtime_log_profile(_settings_layer_value(settings, key)))


def is_simple_runtime_event(event: "ObservationEvent") -> bool:
    family = resolve_runtime_event_family(event.event_type)
    if family not in _SIMPLE_EVENT_TYPES:
        return event.event_type in _RUNTIME_PRINT_EVENTS
    event_type = event.event_type
    if family == "triggerflow":
        event_type = normalize_triggerflow_event_type(event.event_type)
    return event_type in _SIMPLE_EVENT_TYPES[family]


def should_render_console_event(event: "ObservationEvent", settings: Settings) -> bool:
    if _is_compat_alias_event(event) and resolve_runtime_log_profile(settings, event.meta.get("compat_alias_for")) != "off":
        return False
    family = resolve_runtime_event_family(event.event_type)
    if family not in _CONSOLE_EVENT_FAMILIES:
        return False
    profile = resolve_runtime_log_profile(settings, event.event_type)
    if profile == "off":
        return False
    if profile == "detail":
        return True
    if event.level in _ALWAYS_VISIBLE_LEVELS:
        return True
    return is_simple_runtime_event(event)


def should_render_storage_event(event: "ObservationEvent", settings: Settings) -> bool:
    if _is_compat_alias_event(event):
        return False
    if event.event_type in _RUNTIME_PRINT_EVENTS:
        return resolve_runtime_log_profile(settings, event.event_type) == "off"

    family = resolve_runtime_event_family(event.event_type)
    profile = resolve_runtime_log_profile(settings, event.event_type)

    if family in _CONSOLE_EVENT_FAMILIES:
        if profile == "off":
            return event.level in _ALWAYS_VISIBLE_LEVELS
        return False

    if event.level in _ALWAYS_VISIBLE_LEVELS:
        return True

    if profile == "detail":
        return True

    return False


COLORS = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
    "gray": 90,
}


def color_text(text: str, color: str | None = None, bold: bool = False, underline: bool = False) -> str:
    codes = []
    if bold:
        codes.append("1")
    if underline:
        codes.append("4")
    if color and color in COLORS:
        codes.append(str(COLORS[color]))
    if not codes:
        return text
    return f"\x1b[{';'.join(codes)}m{text}\x1b[0m"


def _stringify_payload(payload: Any, *, indent: int | None = None) -> str:
    if payload is None:
        return ""
    sanitized = DataFormatter.sanitize(payload)
    try:
        return json.dumps(sanitized, ensure_ascii=False, indent=indent)
    except TypeError:
        return str(sanitized)


def _event_detail(event: "ObservationEvent", *, pretty_payload: bool = False) -> str:
    if event.message:
        return event.message
    if event.error is not None:
        return event.error.message
    return _stringify_payload(event.payload, indent=2 if pretty_payload else None)


def _resolve_agent_name(event: "ObservationEvent") -> str | None:
    agent_name = _payload_value(event, "agent_name")
    if isinstance(agent_name, str) and agent_name:
        return agent_name
    if event.run is not None and event.run.agent_name:
        return event.run.agent_name
    meta_agent_name = event.meta.get("agent_name")
    return str(meta_agent_name) if isinstance(meta_agent_name, str) and meta_agent_name else None


def _resolve_response_id(event: "ObservationEvent") -> str | None:
    response_id = _payload_value(event, "response_id")
    if isinstance(response_id, str) and response_id:
        return response_id
    if event.run is not None and event.run.response_id:
        return event.run.response_id
    return None


def _resolve_execution_id(event: "ObservationEvent") -> str | None:
    execution_id = event.meta.get("execution_id")
    if isinstance(execution_id, str) and execution_id:
        return execution_id
    if event.run is not None and event.run.execution_id:
        return event.run.execution_id
    return None


def _resolve_tool_stage(event: "ObservationEvent") -> str:
    stage_mapping = {
        "tool.loop_started": "Started",
        "tool.loop_completed": "Completed",
        "tool.loop_failed": "Failed",
        "tool.plan_ready": "Plan Ready",
    }
    if event.event_type in stage_mapping:
        return stage_mapping[event.event_type]
    success = _payload_value(event, "success", None)
    if isinstance(success, bool):
        return "Completed" if success else "Failed"
    if event.level in ("ERROR", "CRITICAL"):
        return "Failed"
    if event.level == "WARNING":
        return "Warning"
    return "Info"


def _is_compat_alias_event(event: "ObservationEvent") -> bool:
    return event.meta.get("compat_event_alias") is True


def _is_tool_loop_event(event: "ObservationEvent") -> bool:
    return event.event_type in {"tool.loop_started", "tool.loop_completed", "tool.loop_failed", "tool.plan_ready"}


def _is_action_loop_event(event: "ObservationEvent") -> bool:
    return event.event_type in {"action.loop_started", "action.loop_completed", "action.loop_failed", "action.plan_ready"}


def _resolve_tool_name(event: "ObservationEvent") -> str | None:
    for key in ("tool_name", "action_name"):
        value = _payload_value(event, key)
        if isinstance(value, str) and value:
            return value

    record = _payload_value(event, "record")
    if isinstance(record, dict):
        for key in ("tool_name", "action_name", "action_id"):
            value = record.get(key)
            if isinstance(value, str) and value:
                return value

    command = _payload_value(event, "command")
    if isinstance(command, dict):
        for key in ("tool_name", "action_name", "action_id"):
            value = command.get(key)
            if isinstance(value, str) and value:
                return value

    if event.run is not None:
        value = event.run.meta.get("action_name")
        if isinstance(value, str) and value:
            return value

    return None


def _resolve_action_name(event: "ObservationEvent") -> str:
    action_name = _payload_value(event, "action_name")
    if isinstance(action_name, str) and action_name:
        return action_name
    record = _payload_value(event, "record")
    if isinstance(record, dict):
        for key in ("action_name", "action_id", "tool_name"):
            value = record.get(key)
            if isinstance(value, str) and value:
                return value
    command = _payload_value(event, "command")
    if isinstance(command, dict):
        for key in ("action_name", "action_id", "tool_name"):
            value = command.get(key)
            if isinstance(value, str) and value:
                return value
    if event.run is not None:
        action_name = event.run.meta.get("action_name")
        if isinstance(action_name, str) and action_name:
            return action_name
    return "unknown"


def _resolve_action_type(event: "ObservationEvent") -> str | None:
    action_type = _payload_value(event, "action_type")
    if isinstance(action_type, str) and action_type:
        return action_type
    if event.run is not None:
        action_type = event.run.meta.get("action_type")
        if isinstance(action_type, str) and action_type:
            return action_type
    return None


def _resolve_action_stage(event: "ObservationEvent") -> str:
    stage_mapping = {
        "action.loop_started": "Started",
        "action.loop_completed": "Completed",
        "action.loop_failed": "Failed",
        "action.plan_ready": "Plan Ready",
        "action.started": "Started",
        "action.completed": "Completed",
        "action.failed": "Failed",
    }
    if event.event_type in stage_mapping:
        return stage_mapping[event.event_type]
    return _resolve_tool_stage(event)


def _render_block(header: str, stage: str, detail: str, *, detail_color: str = "gray", end: str = "\n"):
    header_text = color_text(header, color="blue", bold=True)
    stage_label = color_text("Stage:", color="cyan", bold=True)
    stage_value = color_text(stage, color="yellow", underline=True)
    detail_label = color_text("Detail:", color="cyan", bold=True)
    detail_text = color_text(detail, color=detail_color)
    print(f"{header_text}\n{stage_label} {stage_value}\n{detail_label}\n{detail_text}", end=end, flush=True)


def _render_line(prefix: str, detail: str, *, color: str = "gray"):
    title = color_text(prefix, color="yellow", bold=True)
    body = color_text(detail, color=color)
    print(f"{title} {body}")


class RuntimeConsoleSinkHooker(EventHooker):
    name = "RuntimeConsoleSinkHooker"
    event_types = None

    _streaming_key: tuple[str | None, str | None] | None = None

    @staticmethod
    def _on_register():
        RuntimeConsoleSinkHooker._streaming_key = None

    @staticmethod
    def _on_unregister():
        RuntimeConsoleSinkHooker._streaming_key = None

    @staticmethod
    def _close_stream_if_needed():
        if RuntimeConsoleSinkHooker._streaming_key is not None:
            print()
            RuntimeConsoleSinkHooker._streaming_key = None

    @staticmethod
    def _handle_model_event(event: "ObservationEvent", profile: "RuntimeLogProfile"):
        agent_name = _resolve_agent_name(event) or event.source
        response_id = _resolve_response_id(event)
        response_label = f"[Agent-{ agent_name }]"
        if response_id:
            response_label = f"{ response_label } - [Response-{ response_id }]"

        if event.event_type == "model.streaming" and profile == "detail":
            delta = _payload_value(event, "delta", event.message or "")
            if not isinstance(delta, str):
                delta = str(delta)
            stream_key = (agent_name, response_id)
            if RuntimeConsoleSinkHooker._streaming_key == stream_key:
                print(color_text(delta, color="gray"), end="", flush=True)
                return
            RuntimeConsoleSinkHooker._close_stream_if_needed()
            _render_block(response_label, "Streaming", delta, detail_color="green", end="")
            RuntimeConsoleSinkHooker._streaming_key = stream_key
            return

        RuntimeConsoleSinkHooker._close_stream_if_needed()

        stage_mapping = {
            "model.requesting": "Requesting",
            "model.completed": "Done",
            "model.failed": "Failed",
            "model.parse_failed": "Parse Failed",
            "model.request_failed": "Request Failed",
            "model.retrying": "Retrying",
            "model.streaming_canceled": "Streaming Canceled",
            "model.requester.error": "Requester Error",
            "model.validation_error": "Validation Error",
            "model.validation_failed": "Validation Failed",
        }
        detail = event.message or ""
        if profile == "simple":
            if event.event_type == "model.retrying":
                retry_count = _payload_value(event, "retry_count")
                retry_label = f" (retry={ retry_count })" if retry_count is not None else ""
                detail = f"{ event.message or 'Model response retrying.' }{ retry_label }"
            elif event.error is not None:
                detail = event.error.message
            else:
                detail = event.message or stage_mapping.get(event.event_type, event.event_type)
        elif event.event_type == "model.requesting":
            request_text = _payload_value(event, "request_text")
            detail = str(request_text) if request_text else _stringify_payload(_payload_value(event, "request"), indent=2)
        elif event.event_type == "model.completed":
            detail = _stringify_payload(_payload_value(event, "result"), indent=2) or detail
        elif event.event_type == "model.retrying":
            response_text = _payload_value(event, "response_text")
            retry_count = _payload_value(event, "retry_count")
            detail = f"[Response]: { response_text }\n[Retried Times]: { retry_count }"
        elif event.error is not None:
            detail = event.error.message
        if not detail:
            detail = _stringify_payload(event.payload, indent=2)
        detail_color = "red" if event.level in ("WARNING", "ERROR", "CRITICAL") else "gray"
        _render_block(response_label, stage_mapping.get(event.event_type, event.event_type), detail, detail_color=detail_color)

    @staticmethod
    def _handle_tool_event(event: "ObservationEvent", profile: "RuntimeLogProfile"):
        RuntimeConsoleSinkHooker._close_stream_if_needed()
        agent_name = _resolve_agent_name(event)
        tool_name = _resolve_tool_name(event)
        header = "[ToolLoop]" if _is_tool_loop_event(event) else f"[Tool-{ tool_name or 'unknown' }]"
        if agent_name:
            header = f"[Agent-{ agent_name }] - { header }"
        stage = _resolve_tool_stage(event)
        if profile == "simple":
            detail = event.message or stage
        else:
            detail = _stringify_payload(event.payload, indent=2) or _event_detail(event, pretty_payload=True)
        detail_color = "red" if stage in ("Failed", "Warning") else "gray"
        _render_block(header, stage, detail, detail_color=detail_color)

    @staticmethod
    def _handle_action_event(event: "ObservationEvent", profile: "RuntimeLogProfile"):
        RuntimeConsoleSinkHooker._close_stream_if_needed()
        action_name = _resolve_action_name(event)
        action_type = _resolve_action_type(event)
        agent_name = _resolve_agent_name(event)
        header = "[ActionLoop]" if _is_action_loop_event(event) else f"[Action-{ action_name }]"
        if action_type and not _is_action_loop_event(event):
            header = f"{ header } [type={ action_type }]"
        if agent_name:
            header = f"[Agent-{ agent_name }] - { header }"
        stage = _resolve_action_stage(event)
        if profile == "simple":
            detail = event.message or stage
        else:
            detail = _stringify_payload(event.payload, indent=2) or _event_detail(event, pretty_payload=True)
        detail_color = "red" if stage in ("Failed", "Warning") else "gray"
        _render_block(header, stage, detail, detail_color=detail_color)

    @staticmethod
    def _handle_trigger_flow_event(event: "ObservationEvent", profile: "RuntimeLogProfile"):
        RuntimeConsoleSinkHooker._close_stream_if_needed()
        execution_id = _resolve_execution_id(event)
        prefix = "[TriggerFlow]"
        if execution_id:
            prefix = f"{ prefix } [Execution-{ execution_id }]"
        detail = event.message or event.event_type if profile == "simple" else _event_detail(event, pretty_payload=True)
        color = "red" if event.level in ("WARNING", "ERROR", "CRITICAL") else "yellow" if event.level == "DEBUG" else "gray"
        _render_line(prefix, detail, color=color)

    @staticmethod
    def _handle_generic_event(event: "ObservationEvent"):
        RuntimeConsoleSinkHooker._close_stream_if_needed()
        detail = _event_detail(event, pretty_payload=True)
        prefix = f"[{ event.source }] [{ event.event_type }]"
        color = "gray"
        if event.level in ("WARNING", "ERROR", "CRITICAL"):
            color = "red"
        elif event.level == "INFO":
            color = "green"
        _render_line(prefix, detail, color=color)

    @staticmethod
    async def handler(event: "ObservationEvent"):
        from agently.base import settings
        from agently.core.RuntimeContext import get_current_settings

        current_settings = get_current_settings()
        active_settings = current_settings if current_settings is not None else settings
        if not should_render_console_event(event, active_settings):
            return
        profile = resolve_runtime_log_profile(active_settings, event.event_type)
        family = resolve_runtime_event_family(event.event_type)
        if family == "model":
            RuntimeConsoleSinkHooker._handle_model_event(event, profile)
            return
        if family == "triggerflow":
            RuntimeConsoleSinkHooker._handle_trigger_flow_event(event, profile)
            return
        if event.event_type.startswith("action."):
            RuntimeConsoleSinkHooker._handle_action_event(event, profile)
            return
        if event.event_type.startswith("tool."):
            RuntimeConsoleSinkHooker._handle_tool_event(event, profile)
            return
        RuntimeConsoleSinkHooker._handle_generic_event(event)
