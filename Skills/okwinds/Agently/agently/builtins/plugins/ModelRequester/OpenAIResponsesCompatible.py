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

import asyncio
import json
import time
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncGenerator,
    Literal,
    cast,
    get_args,
    get_origin,
)
from typing_extensions import TypedDict

from httpx import AsyncClient, ReadError, HTTPStatusError, RequestError, Timeout
from httpx_sse import aconnect_sse, SSEError
from stamina import retry

from agently.types.plugins import ModelRequester
from agently.types.data import AgentlyRequestData, SerializableValue
from agently.utils import DataFormatter, SettingsNamespace

if TYPE_CHECKING:
    from agently.core.Prompt import Prompt
    from agently.types.data import AgentlyRequestDataDict, AgentlyResponseGenerator
    from agently.utils import Settings


class OpenAIResponsesCompatibleSettings(TypedDict, total=False):
    model: str
    timeout_mode: Literal["http", "first_token"]
    client_options: dict[str, "SerializableValue"]
    headers: dict[str, "SerializableValue"]
    proxy: str
    request_options: dict[str, "SerializableValue"]
    base_url: str
    full_url: str
    auth: "SerializableValue"
    stream: bool
    rich_content: bool
    strict_role_orders: bool


class OpenAIResponsesCompatible(ModelRequester):
    name = "OpenAIResponsesCompatible"

    DEFAULT_SETTINGS = {
        "$mappings": {
            "path_mappings": {
                "OpenAIResponsesCompatible": "plugins.ModelRequester.OpenAIResponsesCompatible",
                "OpenAIResponses": "plugins.ModelRequester.OpenAIResponsesCompatible",
            },
        },
        "model": None,
        "default_model": "gpt-5.5",
        "timeout_mode": "first_token",
        "client_options": {},
        "headers": {},
        "proxy": None,
        "request_options": {},
        "base_url": "https://api.openai.com/v1",
        "full_url": None,
        "auth": None,
        "stream": True,
        "rich_content": True,
        "strict_role_orders": True,
        "timeout": {
            "connect": 30.0,
            "read": 600.0,
            "write": 30.0,
            "pool": 30.0,
        },
    }

    def __init__(
        self,
        prompt: "Prompt",
        settings: "Settings",
    ):
        from agently.base import event_center

        self.prompt = prompt
        self.settings = settings
        self.plugin_settings = SettingsNamespace(self.settings, f"plugins.ModelRequester.{ self.name }")
        self._emitter = event_center.create_emitter(self.name)

        if self.prompt["attachment"]:
            self.plugin_settings["rich_content"] = True

    @staticmethod
    def _on_register():
        pass

    @staticmethod
    def _on_unregister():
        pass

    def _get_timeout_mode(self) -> Literal["http", "first_token"]:
        timeout_mode = self.plugin_settings.get("timeout_mode", "first_token")
        if timeout_mode == "http":
            return "http"
        return "first_token"

    def _get_timeout_configs(self) -> dict[str, Any]:
        return DataFormatter.to_str_key_dict(
            self.plugin_settings.get(
                "timeout",
                {
                    "connect": 30.0,
                    "read": 120.0,
                    "write": 30.0,
                    "pool": 30.0,
                },
            ),
            default_value={},
        )

    def _get_http_timeout(self, *, disable_read: bool = False) -> Timeout:
        timeout_configs = self._get_timeout_configs().copy()
        if disable_read:
            timeout_configs["read"] = None
        return Timeout(**timeout_configs)

    def _get_first_token_timeout_seconds(self) -> float | None:
        read_timeout = self._get_timeout_configs().get("read")
        if isinstance(read_timeout, (int, float)) and read_timeout > 0:
            return float(read_timeout)
        return None

    def _should_use_first_token_timeout(self, request_data: "AgentlyRequestData") -> bool:
        return self._get_timeout_mode() == "first_token" and bool(request_data.stream)

    async def _aiter_with_first_token_timeout(
        self,
        generator: AsyncGenerator[Any, None],
        *,
        timeout_seconds: float | None,
    ) -> AsyncGenerator[Any, None]:
        if timeout_seconds is None:
            async for item in generator:
                yield item
            return

        try:
            first_item = await asyncio.wait_for(anext(generator), timeout=timeout_seconds)
        except asyncio.TimeoutError as e:
            await generator.aclose()
            raise TimeoutError(f"First token timeout after { timeout_seconds } seconds.") from e

        yield first_item
        async for item in generator:
            yield item

    async def _aiter_sse_with_retry(
        self,
        client: AsyncClient,
        method: str,
        url: str,
        *,
        headers: dict[str, Any],
        json: "SerializableValue",
    ):
        last_event_id = ""
        reconnection_delay = 0.0

        @retry(on=ReadError)
        async def _aiter_sse():
            nonlocal last_event_id, reconnection_delay
            time.sleep(reconnection_delay)
            headers.update({"Accept": "text/event-stream"})
            if last_event_id:
                headers.update({"Last-Event-ID": last_event_id})

            async with aconnect_sse(client, method, url, headers=headers, json=json) as event_source:
                try:
                    async for sse in event_source.aiter_sse():
                        last_event_id = sse.id
                        if sse.retry is not None:
                            reconnection_delay = sse.retry / 1000
                        yield sse
                except GeneratorExit:
                    pass

        return _aiter_sse()

    @staticmethod
    def _build_simple_type_schema(type_name: str) -> dict[str, Any]:
        normalized = type_name.strip()
        scalar_mapping = {
            "str": "string",
            "string": "string",
            "int": "integer",
            "integer": "integer",
            "float": "number",
            "number": "number",
            "bool": "boolean",
            "boolean": "boolean",
            "None": "null",
            "none": "null",
        }
        if normalized in scalar_mapping:
            return {"type": scalar_mapping[normalized]}
        if normalized in {"Any", "any", "unknown", "object"}:
            return {}
        if normalized.startswith("list[") and normalized.endswith("]"):
            item_type = normalized[5:-1].strip()
            return {"type": "array", "items": OpenAIResponsesCompatible._build_simple_type_schema(item_type)}
        if normalized.startswith("dict[") and normalized.endswith("]"):
            return {"type": "object"}
        if normalized.startswith("Literal[") and normalized.endswith("]"):
            literal_body = normalized[len("Literal[") : -1]
            values = [item.strip() for item in literal_body.split(",") if item.strip()]
            enum_values = []
            for value in values:
                try:
                    enum_values.append(json.loads(value))
                except Exception:
                    enum_values.append(value.strip("'\""))
            schema: dict[str, Any] = {"enum": enum_values}
            if len(enum_values) > 0:
                if all(isinstance(item, str) for item in enum_values):
                    schema["type"] = "string"
                elif all(isinstance(item, bool) for item in enum_values):
                    schema["type"] = "boolean"
                elif all(isinstance(item, int) and not isinstance(item, bool) for item in enum_values):
                    schema["type"] = "integer"
                elif all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in enum_values):
                    schema["type"] = "number"
            return schema
        if "|" in normalized:
            options = [part.strip() for part in normalized.split("|") if part.strip()]
            return {"anyOf": [OpenAIResponsesCompatible._build_simple_type_schema(option) for option in options]}
        return {}

    @classmethod
    def _annotation_to_schema(cls, annotation: Any) -> dict[str, Any]:
        if annotation is None:
            return {"type": "null"}
        if isinstance(annotation, dict):
            return cls._kwargs_to_json_schema(cast(dict[str, Any], annotation))
        if isinstance(annotation, str):
            return cls._build_simple_type_schema(annotation)

        origin = get_origin(annotation)
        if origin is list:
            args = get_args(annotation)
            item_annotation = args[0] if args else Any
            return {"type": "array", "items": cls._annotation_to_schema(item_annotation)}
        if origin is dict:
            return {"type": "object"}
        if origin is Literal:
            literal_values = list(get_args(annotation))
            schema: dict[str, Any] = {"enum": literal_values}
            if len(literal_values) > 0:
                first_value = literal_values[0]
                if isinstance(first_value, str):
                    schema["type"] = "string"
                elif isinstance(first_value, bool):
                    schema["type"] = "boolean"
                elif isinstance(first_value, int) and not isinstance(first_value, bool):
                    schema["type"] = "integer"
                elif isinstance(first_value, float):
                    schema["type"] = "number"
            return schema
        if origin is not None:
            return cls._build_simple_type_schema(str(DataFormatter.sanitize(annotation)))

        if isinstance(annotation, type):
            base_mapping = {
                str: {"type": "string"},
                int: {"type": "integer"},
                float: {"type": "number"},
                bool: {"type": "boolean"},
            }
            if annotation in base_mapping:
                return base_mapping[annotation].copy()
            if hasattr(annotation, "model_json_schema"):
                try:
                    return cast(dict[str, Any], annotation.model_json_schema())
                except Exception:
                    return {"type": "object"}
        sanitized = DataFormatter.sanitize(annotation)
        if isinstance(sanitized, dict):
            return cls._kwargs_to_json_schema(cast(dict[str, Any], sanitized))
        if isinstance(sanitized, str):
            return cls._build_simple_type_schema(sanitized)
        return {}

    @classmethod
    def _kwargs_to_json_schema(cls, kwargs_schema: dict[str, Any] | None) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        additional_properties: bool | dict[str, Any] = False
        if not isinstance(kwargs_schema, dict) or len(kwargs_schema) == 0:
            return {"type": "object", "properties": {}}

        for key, raw_value in kwargs_schema.items():
            if key == "<*>":
                wildcard_value = raw_value
                wildcard_annotation = wildcard_value[0] if isinstance(wildcard_value, tuple) and wildcard_value else wildcard_value
                wildcard_schema = cls._annotation_to_schema(wildcard_annotation)
                additional_properties = wildcard_schema if len(wildcard_schema) > 0 else True
                continue

            annotation = raw_value
            description = None
            if isinstance(raw_value, tuple):
                annotation = raw_value[0] if len(raw_value) > 0 else Any
                if len(raw_value) > 1 and isinstance(raw_value[1], str) and raw_value[1]:
                    description = raw_value[1]
            schema = cls._annotation_to_schema(annotation)
            if description:
                schema = schema.copy()
                schema["description"] = description
            properties[str(key)] = schema

        result: dict[str, Any] = {
            "type": "object",
            "properties": properties,
        }
        if additional_properties is not False:
            result["additionalProperties"] = additional_properties
        else:
            result["additionalProperties"] = False
        return result

    @classmethod
    def _tool_name(cls, tool: dict[str, Any]) -> str | None:
        name = tool.get("name", tool.get("action_id"))
        return str(name) if isinstance(name, str) and name.strip() else None

    @staticmethod
    def _create_tool_call_state(call_id: str, index: int) -> dict[str, Any]:
        return {
            "call_id": call_id,
            "index": index,
            "name": "",
            "arguments": "",
            "name_emitted": False,
            "any_argument_delta_emitted": False,
        }

    @staticmethod
    def _emit_tool_call_chunk(
        tool_state: dict[str, Any],
        *,
        arguments_delta: str | None = None,
        name_only: bool = False,
    ) -> dict[str, Any]:
        function_payload: dict[str, Any] = {}
        if not tool_state.get("name_emitted") and tool_state.get("name"):
            function_payload["name"] = str(tool_state["name"])
            tool_state["name_emitted"] = True
        if not name_only and arguments_delta is not None:
            function_payload["arguments"] = arguments_delta
            tool_state["any_argument_delta_emitted"] = True
        return {
            "index": int(tool_state.get("index", 0)),
            "id": str(tool_state.get("call_id", "")),
            "type": "function",
            "function": function_payload,
        }

    @staticmethod
    def _collect_output_items(completed_output_items: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
        return [completed_output_items[index] for index in sorted(completed_output_items.keys())]

    @classmethod
    def _convert_prompt_tools(cls, prompt_tools: Any) -> list[dict[str, Any]]:
        if not isinstance(prompt_tools, list):
            return []
        result: list[dict[str, Any]] = []
        for tool in prompt_tools:
            if not isinstance(tool, dict):
                continue
            name = cls._tool_name(tool)
            if name is None:
                continue
            description = tool.get("desc", tool.get("description", ""))
            parameters = cls._kwargs_to_json_schema(cast(dict[str, Any] | None, tool.get("kwargs")))
            result.append(
                {
                    "type": "function",
                    "name": name,
                    "description": str(description) if description is not None else "",
                    "parameters": parameters,
                    "strict": False,
                }
            )
        return result

    @classmethod
    def _merge_tools(cls, auto_tools: list[dict[str, Any]], explicit_tools: Any) -> list[dict[str, Any]]:
        if not isinstance(explicit_tools, list) or len(explicit_tools) == 0:
            return auto_tools

        merged_named: dict[str, dict[str, Any]] = {}
        ordered: list[dict[str, Any]] = []
        for tool in auto_tools:
            tool_name = tool.get("name")
            if isinstance(tool_name, str) and tool_name:
                merged_named[tool_name] = tool
            else:
                ordered.append(tool)

        explicit_non_named: list[dict[str, Any]] = []
        for tool in explicit_tools:
            if not isinstance(tool, dict):
                continue
            tool_name = tool.get("name")
            if tool.get("type") == "function" and isinstance(tool_name, str) and tool_name:
                merged_named[tool_name] = tool
            else:
                explicit_non_named.append(tool)

        merged_tools = list(merged_named.values())
        merged_tools.extend(ordered)
        merged_tools.extend(explicit_non_named)
        return merged_tools

    @staticmethod
    def _message_text_to_content(text: Any) -> dict[str, Any]:
        return {"type": "input_text", "text": str(text)}

    @classmethod
    def _normalize_content_part(cls, part: Any) -> dict[str, Any]:
        if isinstance(part, str):
            return cls._message_text_to_content(part)
        if not isinstance(part, dict):
            return cls._message_text_to_content(part)

        part_type = part.get("type")
        if part_type == "text":
            return {"type": "input_text", "text": str(part.get("text", ""))}
        if part_type == "image_url":
            image_value = part.get("image_url")
            mapped: dict[str, Any] = {"type": "input_image"}
            if isinstance(image_value, dict):
                if "url" in image_value:
                    mapped["image_url"] = image_value["url"]
                if "detail" in image_value:
                    mapped["detail"] = image_value["detail"]
                if "file_id" in image_value:
                    mapped["file_id"] = image_value["file_id"]
            else:
                mapped["image_url"] = image_value
            return mapped
        if part_type in ("input_text", "input_image", "input_file"):
            mapped = dict(part)
            if mapped.get(str(part_type)) is None:
                del mapped[str(part_type)]
            return mapped
        raise TypeError(
            f"Plugin Name: { cls.name }\n"
            f"Error: Unsupported rich content type for Responses input: '{ part_type }'\n"
            f"Content: { part }"
        )

    def _build_input_items(self) -> list[dict[str, Any]]:
        messages = self.prompt.to_messages(
            rich_content=True,
            strict_role_orders=bool(self.plugin_settings.get("strict_role_orders", True)),
        )
        input_items: list[dict[str, Any]] = []
        for message in messages:
            if not isinstance(message, dict):
                continue
            role = str(message.get("role", "user"))
            raw_content = message.get("content", "")
            if isinstance(raw_content, list):
                content = [self._normalize_content_part(part) for part in raw_content]
            else:
                content = [self._normalize_content_part(raw_content)]
            input_items.append({"type": "message", "role": role, "content": content})
        return input_items

    def generate_request_data(self) -> "AgentlyRequestData":
        agently_request_dict: AgentlyRequestDataDict = {
            "client_options": {},
            "headers": {},
            "data": {},
            "request_options": {},
            "request_url": "",
        }

        agently_request_dict["data"] = {
            "input": self._build_input_items(),
        }

        headers: dict[str, str] = DataFormatter.to_str_key_dict(
            self.plugin_settings.get("headers"),
            value_format="str",
            default_value={},
        )
        headers.update({"Connection": "close"})
        agently_request_dict["headers"] = headers

        client_options = DataFormatter.to_str_key_dict(self.plugin_settings.get("client_options"), default_value={})
        proxy = self.plugin_settings.get("proxy", None)
        if proxy:
            client_options.update({"proxy": proxy})
        client_options.update({"timeout": self._get_http_timeout()})
        agently_request_dict["client_options"] = client_options

        legacy_options = DataFormatter.to_str_key_dict(
            self.plugin_settings.get("options"),
            value_format="serializable",
            default_value={},
        )
        request_options = DataFormatter.to_str_key_dict(
            self.plugin_settings.get("request_options"),
            value_format="serializable",
            default_value={},
        )
        request_options = {**legacy_options, **request_options}
        request_options_in_prompt = self.prompt.get("options", {})
        if request_options_in_prompt:
            request_options.update(request_options_in_prompt)
            request_options = DataFormatter.to_str_key_dict(
                request_options,
                value_format="serializable",
                default_value={},
            )

        request_options.update(
            {
                "model": self.plugin_settings.get(
                    "model",
                    self.plugin_settings.get("default_model", "gpt-5.5"),
                )
            }
        )

        is_stream = self.plugin_settings.get("stream")
        request_options.update({"stream": True if is_stream is None else bool(is_stream)})

        auto_tools = self._convert_prompt_tools(self.prompt.to_prompt_object().tools)
        merged_tools = self._merge_tools(auto_tools, request_options.get("tools"))
        if len(merged_tools) > 0:
            request_options["tools"] = merged_tools

        agently_request_dict["request_options"] = request_options

        full_url = self.plugin_settings.get("full_url")
        base_url = str(self.plugin_settings.get("base_url"))
        base_url = base_url[:-1] if base_url[-1] == "/" else base_url
        agently_request_dict["request_url"] = str(full_url) if isinstance(full_url, str) else f"{ base_url }/responses"

        return AgentlyRequestData(**agently_request_dict)

    @staticmethod
    def _collect_assistant_text(output_items: Any) -> str:
        if not isinstance(output_items, list):
            return ""
        texts: list[str] = []
        for item in output_items:
            if not isinstance(item, dict):
                continue
            if item.get("type") != "message":
                continue
            if item.get("role") != "assistant":
                continue
            content = item.get("content", [])
            if not isinstance(content, list):
                continue
            for part in content:
                if isinstance(part, dict) and part.get("type") == "output_text":
                    texts.append(str(part.get("text", "")))
        return "".join(texts)

    @staticmethod
    def _extract_reasoning_summary(response_record: dict[str, Any]) -> str:
        reasoning = response_record.get("reasoning")
        if not isinstance(reasoning, dict):
            return ""
        summary = reasoning.get("summary")
        if isinstance(summary, str):
            return summary
        if isinstance(summary, list):
            texts: list[str] = []
            for item in summary:
                if isinstance(item, str):
                    texts.append(item)
                elif isinstance(item, dict):
                    if isinstance(item.get("text"), str):
                        texts.append(str(item["text"]))
                    elif isinstance(item.get("summary_text"), str):
                        texts.append(str(item["summary_text"]))
            return "".join(texts)
        return ""

    @staticmethod
    def _has_function_call_output(output_items: Any) -> bool:
        if not isinstance(output_items, list):
            return False
        for item in output_items:
            if isinstance(item, dict) and item.get("type") == "function_call":
                return True
        return False

    @classmethod
    def _build_finish_reason(cls, response_record: dict[str, Any]) -> str:
        output_items = response_record.get("output", [])
        if cls._has_function_call_output(output_items):
            return "tool_calls"
        incomplete_details = response_record.get("incomplete_details")
        if isinstance(incomplete_details, dict) and incomplete_details.get("reason") == "max_output_tokens":
            return "length"
        return "stop"

    def _build_headers_with_auth(self, request_data: "AgentlyRequestData") -> dict[str, Any]:
        auth = DataFormatter.to_str_key_dict(
            self.plugin_settings.get("auth", "None"),
            value_format="serializable",
            default_key="api_key",
        )
        api_key = self.plugin_settings.get("api_key", None)
        auth_api_key = auth.get("api_key", "None")
        if api_key is not None and auth_api_key == "None":
            auth["api_key"] = str(api_key)
            auth_api_key = auth["api_key"]

        headers_with_auth = request_data.headers.copy()
        if "headers" in auth and isinstance(auth["headers"], dict):
            headers_with_auth.update(
                DataFormatter.to_str_key_dict(
                    auth["headers"],
                    value_format="str",
                    default_value={},
                )
            )
        if "body" in auth and isinstance(auth["body"], dict):
            request_data.data.update(**auth["body"])
        if auth_api_key != "None":
            headers_with_auth["Authorization"] = f"Bearer { auth_api_key }"
        return headers_with_auth

    async def request_model(self, request_data: "AgentlyRequestData") -> AsyncGenerator[tuple[str, Any], None]:
        headers_with_auth = self._build_headers_with_auth(request_data)
        full_request_data = DataFormatter.to_str_key_dict(
            request_data.data,
            value_format="serializable",
            default_value={},
        )
        full_request_data.update(request_data.request_options)

        if request_data.stream:
            client_options = request_data.client_options.copy()
            if self._should_use_first_token_timeout(request_data):
                client_options.update({"timeout": self._get_http_timeout(disable_read=True)})

            async with AsyncClient(**client_options) as client:
                client.headers.update(headers_with_auth)
                try:
                    sse_generator = await self._aiter_sse_with_retry(
                        client,
                        "POST",
                        request_data.request_url,
                        json=full_request_data,
                        headers=headers_with_auth,
                    )
                    if self._should_use_first_token_timeout(request_data):
                        sse_generator = self._aiter_with_first_token_timeout(
                            sse_generator,
                            timeout_seconds=self._get_first_token_timeout_seconds(),
                        )
                    async for sse in sse_generator:
                        if sse.data.strip() == "[DONE]":
                            continue
                        yield sse.event, sse.data
                except SSEError:
                    response = await client.post(
                        request_data.request_url,
                        json=full_request_data,
                        headers=headers_with_auth,
                    )
                    if response.status_code >= 400:
                        error = RequestError(
                            f"Status Code: { response.status_code }\n"
                            f"Detail: { response.text }\n"
                            f"Request Data: { full_request_data }"
                        )
                        await self._emitter.async_error(
                            error,
                            event_type="model.requester.error",
                            payload={"request_data": full_request_data},
                        )
                        yield "error", error
                    else:
                        yield "response.completed", response.content.decode()
                except HTTPStatusError as e:
                    await self._emitter.async_error(
                        "Error: HTTP Status Error\n"
                        f"Detail: { e.response.status_code } - { e.response.text }\n"
                        f"Request Data: { full_request_data }",
                        event_type="model.requester.error",
                        payload={"request_data": full_request_data},
                    )
                    yield "error", e
                except TimeoutError as e:
                    await self._emitter.async_error(
                        "Error: Timeout Error\n" f"Detail: { e }\n" f"Request Data: { full_request_data }",
                        event_type="model.requester.error",
                        payload={"request_data": full_request_data},
                    )
                    yield "error", e
                except RequestError as e:
                    await self._emitter.async_error(
                        "Error: Request Error\n" f"Detail: { e }\n" f"Request Data: { full_request_data }",
                        event_type="model.requester.error",
                        payload={"request_data": full_request_data},
                    )
                    yield "error", e
                except Exception as e:
                    await self._emitter.async_error(
                        "Error: Unknown Error\n" f"Detail: { e }\n" f"Request Data: { full_request_data }",
                        event_type="model.requester.error",
                        payload={"request_data": full_request_data},
                    )
                    yield "error", e
                finally:
                    await client.aclose()
            return

        async with AsyncClient(**request_data.client_options) as client:
            client.headers.update(headers_with_auth)
            try:
                response = await client.post(
                    request_data.request_url,
                    json=full_request_data,
                )
                if response.status_code >= 400:
                    error = RequestError(
                        f"Status Code: { response.status_code }\n"
                        f"Detail: { response.text }\n"
                        f"Request Data: { full_request_data }"
                    )
                    await self._emitter.async_error(
                        error,
                        event_type="model.requester.error",
                        payload={"request_data": full_request_data},
                    )
                    yield "error", error
                else:
                    yield "response.completed", response.content.decode()
            except HTTPStatusError as e:
                await self._emitter.async_error(
                    "Error: HTTP Status Error\n"
                    f"Detail: { e.response.status_code } - { e.response.text }\n"
                    f"Request Data: { full_request_data }",
                    event_type="model.requester.error",
                    payload={"request_data": full_request_data},
                )
                yield "error", e
            except RequestError as e:
                await self._emitter.async_error(
                    "Error: Request Error\n" f"Detail: { e }\n" f"Request Data: { full_request_data }",
                    event_type="model.requester.error",
                    payload={"request_data": full_request_data},
                )
                yield "error", e
            except Exception as e:
                await self._emitter.async_error(
                    "Error: Unknown Error\n" f"Detail: { e }\n" f"Request Data: { full_request_data }",
                    event_type="model.requester.error",
                    payload={"request_data": full_request_data},
                )
                yield "error", e
            finally:
                await client.aclose()

    async def broadcast_response(self, response_generator: AsyncGenerator) -> "AgentlyResponseGenerator":
        meta: dict[str, Any] = {}
        content_buffer = ""
        reasoning_buffer = ""
        response_record: dict[str, Any] = {}
        completed_output_items: dict[int, dict[str, Any]] = {}
        tool_call_states: dict[str, dict[str, Any]] = {}
        completed = False
        saw_any_event = False

        async for event, message in response_generator:
            if event == "error":
                yield "error", message
                continue

            saw_any_event = True
            if not isinstance(message, str):
                message = json.dumps(message, ensure_ascii=False)
            yield "original_delta", message

            loaded_message = json.loads(message)
            payload_type = str(loaded_message.get("type", event))

            if payload_type in {"response.created", "response.in_progress"}:
                base_response = loaded_message.get("response", loaded_message)
                if isinstance(base_response, dict):
                    response_record.update(base_response)
                    if "id" in base_response:
                        meta["id"] = base_response["id"]
                    if "model" in base_response:
                        meta["model"] = base_response["model"]
                    if "status" in base_response:
                        meta["status"] = base_response["status"]
                continue

            if payload_type == "response.output_text.delta":
                delta = str(loaded_message.get("delta", ""))
                content_buffer += delta
                yield "delta", delta
                continue

            if payload_type == "response.output_text.done":
                final_text = str(loaded_message.get("text", ""))
                if final_text and not content_buffer:
                    content_buffer = final_text
                continue

            if payload_type == "response.function_call_arguments.delta":
                call_id = str(loaded_message.get("call_id", ""))
                if call_id == "":
                    continue
                delta = str(loaded_message.get("delta", ""))
                output_index = loaded_message.get("output_index", len(tool_call_states))
                index = int(output_index) if isinstance(output_index, int) else len(tool_call_states)
                tool_state = tool_call_states.setdefault(call_id, self._create_tool_call_state(call_id, index))
                tool_state["arguments"] = str(tool_state.get("arguments", "")) + delta
                yield "tool_calls", self._emit_tool_call_chunk(tool_state, arguments_delta=delta)
                continue

            if payload_type == "response.function_call_arguments.done":
                call_id = str(loaded_message.get("call_id", ""))
                if call_id and call_id in tool_call_states and isinstance(loaded_message.get("arguments"), str):
                    tool_call_states[call_id]["arguments"] = loaded_message["arguments"]
                continue

            if payload_type in {"response.output_item.added", "response.output_item.done"}:
                item = loaded_message.get("item")
                output_index = loaded_message.get("output_index", 0)
                if not isinstance(item, dict) or not isinstance(output_index, int):
                    continue
                item_type = item.get("type")
                if payload_type == "response.output_item.done":
                    completed_output_items[output_index] = item

                if item_type == "function_call":
                    call_id = str(item.get("call_id", ""))
                    if call_id == "":
                        continue
                    tool_state = tool_call_states.setdefault(call_id, self._create_tool_call_state(call_id, output_index))
                    tool_state["index"] = output_index
                    if isinstance(item.get("name"), str):
                        tool_state["name"] = item["name"]
                    if isinstance(item.get("arguments"), str):
                        tool_state["arguments"] = item["arguments"]
                    if payload_type == "response.output_item.done":
                        if not tool_state.get("any_argument_delta_emitted"):
                            yield "tool_calls", self._emit_tool_call_chunk(
                                tool_state,
                                arguments_delta=str(tool_state.get("arguments", "")),
                            )
                        elif not tool_state.get("name_emitted") and tool_state.get("name"):
                            yield "tool_calls", self._emit_tool_call_chunk(
                                tool_state,
                                arguments_delta=None,
                                name_only=True,
                            )
                continue

            if payload_type == "response.completed":
                response_payload = loaded_message.get("response", loaded_message)
                if isinstance(response_payload, dict):
                    response_record.update(response_payload)
                completed = True
                break

        if not saw_any_event:
            return

        if not completed:
            output_items = self._collect_output_items(completed_output_items)
            if len(output_items) > 0:
                response_record["output"] = output_items
            response_record.setdefault("status", "completed")
            response_record.setdefault("object", "response")
            if "id" in meta:
                response_record.setdefault("id", meta["id"])
            if "model" in meta:
                response_record.setdefault("model", meta["model"])

        response_output_items = response_record.get("output")
        if isinstance(response_output_items, list) and len(response_output_items) == 0 and len(completed_output_items) > 0:
            response_record["output"] = self._collect_output_items(completed_output_items)
            response_output_items = response_record["output"]

        done_content = self._collect_assistant_text(response_output_items)
        if done_content == "":
            done_content = content_buffer
        reasoning_buffer = self._extract_reasoning_summary(response_record)

        yield "done", done_content
        yield "reasoning_done", reasoning_buffer
        yield "original_done", response_record

        if "id" in response_record:
            meta["id"] = response_record["id"]
        if "model" in response_record:
            meta["model"] = response_record["model"]
        if "status" in response_record:
            meta["status"] = response_record["status"]
        if "usage" in response_record:
            meta["usage"] = response_record["usage"]
        meta["finish_reason"] = self._build_finish_reason(response_record)
        yield "meta", meta
