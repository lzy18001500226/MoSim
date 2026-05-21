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

from __future__ import annotations

import asyncio
import inspect
import warnings

from typing import Any, AsyncGenerator, Literal, TYPE_CHECKING, cast, overload, Generator, Mapping, Sequence

from agently.core.RuntimeContext import bind_runtime_context
from agently.utils import DeprecationWarnings, FunctionShifter, DataFormatter, DataLocator, DataPathBuilder

if TYPE_CHECKING:
    from pydantic import BaseModel

    from agently.core import Prompt, ExtensionHandlers
    from agently.core.PluginManager import PluginManager
    from agently.utils import Settings
    from agently.types.data import (
        AgentlyModelResponseMessage,
        InstantStreamingContentType,
        OutputValidateContext,
        OutputValidateHandler,
        OutputValidateResult,
        OutputValidateResultDict,
        ResponseContentType,
        RunContext,
        SpecificEvents,
        StreamingData,
    )
    from agently.types.plugins import ResponseParser


DEFAULT_SPECIFIC_EVENTS: "SpecificEvents" = [
    "reasoning_delta",
    "delta",
    "reasoning_done",
    "done",
    "tool_calls",
]


class ModelResponseResult:
    def __init__(
        self,
        agent_name: str,
        response_id: str,
        prompt: "Prompt",
        response_generator: AsyncGenerator["AgentlyModelResponseMessage", None],
        plugin_manager: "PluginManager",
        settings: "Settings",
        extension_handlers: "ExtensionHandlers",
        *,
        request_run_context: "RunContext | None" = None,
        model_run_context: "RunContext | None" = None,
        attempt_index: int = 1,
    ):
        self.agent_name = agent_name
        self.plugin_manager = plugin_manager
        self.settings = settings
        self.request_run_context = request_run_context
        self.model_run_context = model_run_context
        self.run_context = request_run_context
        self.attempt_index = attempt_index
        ResponseParser = cast(
            type["ResponseParser"],
            self.plugin_manager.get_plugin(
                "ResponseParser",
                str(self.settings["plugins.ResponseParser.activate"]),
            ),
        )
        self._response_id = response_id
        self._extension_handlers = extension_handlers
        self._response_parser = ResponseParser(
            agent_name,
            response_id,
            prompt,
            response_generator,
            self.settings,
            run_context=self.model_run_context,
        )
        self._finally_handlers_ran = False
        self._finally_handlers_lock = asyncio.Lock()
        self._run_finally_handlers_once_sync = FunctionShifter.syncify(self._run_finally_handlers_once)
        self.prompt = prompt
        self._auto_ensure_keys_cache: dict[str, list[str]] = {}
        self._validate_outcome: dict[str, Any] | None = None
        self._validate_lock = asyncio.Lock()
        self._validate_handler_signature: tuple[int, ...] | None = None
        self.full_result_data = self._response_parser.full_result_data
        self.get_meta = FunctionShifter.syncify(self.async_get_meta)
        self.get_text = FunctionShifter.syncify(self.async_get_text)
        self.get_data = FunctionShifter.syncify(self.async_get_data)
        self.get_data_object = FunctionShifter.syncify(self.async_get_data_object)

    def _get_auto_ensure_keys(self, *, key_style: Literal["dot", "slash"] = "dot") -> list[str]:
        cache_key = key_style
        if cache_key in self._auto_ensure_keys_cache:
            return self._auto_ensure_keys_cache[cache_key]

        try:
            prompt_output = self.prompt.to_prompt_object().output
        except Exception:
            prompt_output = None

        if not isinstance(prompt_output, (Mapping, Sequence)) or isinstance(prompt_output, str):
            self._auto_ensure_keys_cache[cache_key] = []
            return []

        try:
            ensure_keys = DataPathBuilder.extract_ensure_paths(prompt_output, style=key_style)
        except Exception:
            ensure_keys = []

        self._auto_ensure_keys_cache[cache_key] = ensure_keys
        return ensure_keys

    @staticmethod
    def _merge_ensure_keys(auto_keys: list[str], explicit_keys: list[str]) -> list[str]:
        merged: list[str] = []
        seen: set[str] = set()
        for key in [*auto_keys, *explicit_keys]:
            if key not in seen:
                seen.add(key)
                merged.append(key)
        return merged

    def _is_strict_output_enabled(self) -> bool:
        try:
            prompt_object = self.prompt.to_prompt_object()
            return bool(getattr(prompt_object, "ensure_all_keys", False)) and prompt_object.output_format == "json"
        except Exception:
            return False

    @staticmethod
    def _handler_name(handler: Any, index: int) -> str:
        name = getattr(handler, "__name__", None)
        if isinstance(name, str) and name:
            return name
        return f"validate_handler_{ index + 1 }"

    def _resolve_validate_handlers(
        self,
        validate_handler: "OutputValidateHandler | list[OutputValidateHandler] | None" = None,
    ) -> list["OutputValidateHandler"]:
        handlers = self._extension_handlers.get("validate_handlers", [])
        resolved: list["OutputValidateHandler"] = list(handlers) if isinstance(handlers, list) else []
        if validate_handler is None:
            return resolved
        if isinstance(validate_handler, list):
            resolved.extend(validate_handler)
        else:
            resolved.append(validate_handler)
        return resolved

    async def _build_validate_result_snapshot(self) -> dict[str, Any]:
        parsed_result = self._response_parser.full_result_data.get("parsed_result")
        if isinstance(parsed_result, dict):
            return parsed_result.copy()
        if isinstance(parsed_result, Mapping):
            return dict(parsed_result)
        result_object = self._response_parser.full_result_data.get("result_object")
        model_dump = getattr(result_object, "model_dump", None)
        if callable(model_dump):
            dumped = model_dump()
            if isinstance(dumped, dict):
                return dumped
            if isinstance(dumped, Mapping):
                return dict(dumped)
        return {"value": parsed_result}

    async def _build_validate_context(
        self,
        *,
        value: dict[str, Any],
        retry_count: int,
        max_retries: int,
        meta: dict[str, Any] | None = None,
    ):
        from agently.types.data import OutputValidateContext

        response_text = await self._response_parser.async_get_text()
        return OutputValidateContext(
            value=value,
            agent_name=self.agent_name,
            response_id=self._response_id,
            attempt_index=self.attempt_index,
            retry_count=retry_count,
            max_retries=max_retries,
            prompt=self.prompt,
            settings=self.settings,
            request_run_context=self.request_run_context,
            model_run_context=self.model_run_context,
            response_text=response_text,
            parsed_result=self._response_parser.full_result_data.get("parsed_result"),
            result_object=self._response_parser.full_result_data.get("result_object"),
            meta=meta,
        )

    @staticmethod
    def _exception_to_raise(error: BaseException | str | None):
        if error is None:
            return None
        if isinstance(error, BaseException):
            return error
        return ValueError(str(error))

    def _normalize_validate_result(
        self,
        raw_result: "OutputValidateResult",
        *,
        validator_name: str,
    ) -> dict[str, Any]:
        if isinstance(raw_result, bool):
            return {
                "ok": raw_result,
                "kind": "passed" if raw_result else "failed",
                "reason": None if raw_result else f"Validation failed in { validator_name }.",
                "payload": None,
                "validator_name": validator_name,
                "retryable": not raw_result,
                "no_retry": False,
                "stop": False,
                "raise_value": None,
                "error": None,
            }

        if isinstance(raw_result, dict):
            ok = bool(raw_result.get("ok", False))
            reason_value = raw_result.get("reason")
            reason = str(reason_value) if reason_value is not None else None
            payload = raw_result.get("payload")
            validation_payload = payload if isinstance(payload, dict) else None
            no_retry = bool(raw_result.get("no_retry", False))
            stop = bool(raw_result.get("stop", False))
            explicit_raise = raw_result.get("raise", raw_result.get("error", raw_result.get("exception")))
            validator_name_value = raw_result.get("validator_name")
            return {
                "ok": ok,
                "kind": "passed" if ok else "failed",
                "reason": reason if reason is not None else (None if ok else f"Validation failed in { validator_name }."),
                "payload": validation_payload,
                "validator_name": str(validator_name_value) if validator_name_value is not None else validator_name,
                "retryable": False if ok else not (no_retry or stop or explicit_raise is not None),
                "no_retry": no_retry,
                "stop": stop,
                "raise_value": None if ok else explicit_raise,
                "error": None,
            }

        return {
            "ok": False,
            "kind": "error",
            "reason": f"Unsupported validation result from { validator_name }: { type(raw_result).__name__ }",
            "payload": {"return_type": type(raw_result).__name__},
            "validator_name": validator_name,
            "retryable": True,
            "no_retry": False,
            "stop": False,
            "raise_value": None,
            "error": None,
        }

    def _normalize_validate_error(
        self,
        error: BaseException,
        *,
        validator_name: str,
    ) -> dict[str, Any]:
        return {
            "ok": False,
            "kind": "error",
            "reason": str(error) if str(error) else f"Validation handler { validator_name } raised an exception.",
            "payload": None,
            "validator_name": validator_name,
            "retryable": True,
            "no_retry": False,
            "stop": False,
            "raise_value": None,
            "error": error,
        }

    async def _emit_validation_runtime_event(
        self,
        event_type: str,
        *,
        level: str,
        message: str,
        outcome: dict[str, Any],
        retry_count: int,
        max_retries: int,
        response_text: str,
    ):
        from agently.base import async_emit_runtime

        error = outcome.get("error")
        await async_emit_runtime(
            {
                "event_type": event_type,
                "source": "ModelResponseResult",
                "level": level,
                "message": message,
                "payload": {
                    "agent_name": self.agent_name,
                    "response_id": self._response_id,
                    "attempt_index": self.attempt_index,
                    "retry_count": retry_count,
                    "max_retries": max_retries,
                    "validator_name": outcome.get("validator_name"),
                    "reason": outcome.get("reason"),
                    "stop": outcome.get("stop", False),
                    "no_retry": outcome.get("no_retry", False),
                    "error_kind": type(error).__name__ if isinstance(error, BaseException) else None,
                    "validation_payload": DataFormatter.sanitize(outcome.get("payload")),
                    "response_text": response_text,
                },
                "error": error if isinstance(error, BaseException) else None,
                "run": self.request_run_context,
            }
        )

    async def _run_validate_handlers_once(
        self,
        handlers: list["OutputValidateHandler"],
        *,
        retry_count: int,
        max_retries: int,
    ) -> dict[str, Any] | None:
        if self._validate_outcome is not None:
            signature = tuple(id(handler) for handler in handlers)
            if len(handlers) > 0 and self._validate_handler_signature is not None and signature != self._validate_handler_signature:
                warnings.warn(
                    "Validation already finalized for this response result. New validate handlers are ignored.",
                    stacklevel=2,
                )
            return self._validate_outcome

        if len(handlers) == 0:
            return None

        signature = tuple(id(handler) for handler in handlers)
        async with self._validate_lock:
            if self._validate_outcome is not None:
                if self._validate_handler_signature is not None and signature != self._validate_handler_signature:
                    warnings.warn(
                        "Validation already finalized for this response result. New validate handlers are ignored.",
                        stacklevel=2,
                    )
                return self._validate_outcome

            validate_value = await self._build_validate_result_snapshot()
            response_text = await self._response_parser.async_get_text()
            for index, handler in enumerate(handlers):
                validator_name = self._handler_name(handler, index)
                context = await self._build_validate_context(
                    value=validate_value,
                    retry_count=retry_count,
                    max_retries=max_retries,
                    meta={"validator_name": validator_name},
                )
                try:
                    raw_result = handler(validate_value, context)
                    if inspect.isawaitable(raw_result):
                        raw_result = await raw_result
                    outcome = self._normalize_validate_result(
                        cast("OutputValidateResult", raw_result),
                        validator_name=validator_name,
                    )
                except BaseException as error:
                    outcome = self._normalize_validate_error(error, validator_name=validator_name)

                if not outcome["ok"]:
                    event_type = "model.validation_error" if outcome["kind"] == "error" else "model.validation_failed"
                    level = "ERROR" if outcome["kind"] == "error" else "WARNING"
                    await self._emit_validation_runtime_event(
                        event_type,
                        level=level,
                        message=f"Output validation failed in { outcome['validator_name'] }.",
                        outcome=outcome,
                        retry_count=retry_count,
                        max_retries=max_retries,
                        response_text=response_text,
                    )
                    self._validate_outcome = outcome
                    self._validate_handler_signature = signature
                    return outcome

            self._validate_outcome = {
                "ok": True,
                "kind": "passed",
                "reason": None,
                "payload": None,
                "validator_name": None,
                "retryable": False,
                "no_retry": False,
                "stop": False,
                "raise_value": None,
                "error": None,
            }
            self._validate_handler_signature = signature
            return self._validate_outcome

    async def _emit_retrying_event(
        self,
        *,
        retry_count: int,
        response_text: str,
        active_ensure_keys: list[str],
        strict_output: bool,
        key_style: str,
        validation_outcome: dict[str, Any] | None = None,
        retry_reason: str = "output_constraints",
        message: str | None = None,
    ):
        from agently.base import async_emit_runtime

        payload = {
            "agent_name": self.agent_name,
            "response_id": self._response_id,
            "retry_count": retry_count,
            "attempt_index": self.attempt_index,
            "next_attempt_index": self.attempt_index + 1,
            "model_run_id": self.model_run_context.run_id if self.model_run_context is not None else None,
            "response_text": response_text,
            "ensure_keys": active_ensure_keys,
            "strict_output": strict_output,
            "key_style": key_style,
            "retry_reason": retry_reason,
        }
        if validation_outcome is not None:
            payload.update(
                {
                    "validator_name": validation_outcome.get("validator_name"),
                    "validation_reason": validation_outcome.get("reason"),
                    "validation_stop": validation_outcome.get("stop", False),
                    "validation_no_retry": validation_outcome.get("no_retry", False),
                    "validation_payload": DataFormatter.sanitize(validation_outcome.get("payload")),
                }
            )
        with bind_runtime_context(
            parent_run_context=self.request_run_context,
            request_run_context=self.request_run_context,
            model_run_context=self.model_run_context,
            settings=self.settings,
        ):
            await async_emit_runtime(
                {
                    "event_type": "model.retrying",
                    "source": "ModelResponseResult",
                    "level": "WARNING",
                    "message": (
                        message
                        if message is not None
                        else (
                            "Output validation failed. Preparing retry."
                            if validation_outcome is not None
                            else "No target data in response. Preparing retry."
                        )
                    ),
                    "payload": payload,
                    "run": self.request_run_context,
                }
            )

    @staticmethod
    def _build_validation_failure_exception(outcome: dict[str, Any]):
        explicit_error = ModelResponseResult._exception_to_raise(cast(BaseException | str | None, outcome.get("raise_value")))
        if explicit_error is not None:
            return explicit_error
        validator_name = outcome.get("validator_name")
        reason = outcome.get("reason")
        if validator_name:
            return ValueError(f"Output validation failed in { validator_name }: { reason or 'unknown reason' }")
        return ValueError(reason or "Output validation failed.")

    @staticmethod
    def _build_output_retry_failure_exception(
        *,
        active_ensure_keys: list[str],
        strict_output: bool,
        max_retries: int,
    ) -> ValueError:
        constraints: list[str] = []
        if strict_output:
            constraints.append("strict output")
        if active_ensure_keys:
            constraints.append(f"ensure keys { active_ensure_keys }")
        constraint_text = " and ".join(constraints) if constraints else "output constraints"
        return ValueError(f"Can not satisfy { constraint_text } within { max_retries } retries.")

    async def _retry_get_data(
        self,
        *,
        type: Literal["original", "parsed", "all"],
        ensure_keys: list[str],
        validate_handler: "OutputValidateHandler | list[OutputValidateHandler] | None",
        key_style: Literal["dot", "slash"],
        max_retries: int,
        raise_ensure_failure: bool,
        retry_count: int,
    ) -> Any:
        from agently.core.ModelResponse import ModelResponse

        return await ModelResponse(
            self.agent_name,
            self.plugin_manager,
            self.settings,
            self.prompt,
            self._extension_handlers,
            run_context=self.request_run_context,
            attempt_index=self.attempt_index + 1,
        ).result.async_get_data(
            type=type,
            ensure_keys=ensure_keys,
            validate_handler=validate_handler,
            key_style=key_style,
            max_retries=max_retries,
            raise_ensure_failure=raise_ensure_failure,
            _retry_count=retry_count,
        )

    async def _run_finally_handlers_once(self):
        if self._finally_handlers_ran:
            return
        async with self._finally_handlers_lock:
            if self._finally_handlers_ran:
                return
            # Mark as executed before invoking handlers so handlers can safely
            # call result getters without re-entering this hook chain.
            self._finally_handlers_ran = True
            finally_handlers = self._extension_handlers.get("finally", [])
            with bind_runtime_context(
                parent_run_context=self.request_run_context,
                request_run_context=self.request_run_context,
                model_run_context=self.model_run_context,
                settings=self.settings,
            ):
                for handler in finally_handlers:
                    if inspect.iscoroutinefunction(handler):
                        await handler(
                            self,
                            self.settings,
                        )
                    elif inspect.isgeneratorfunction(handler):
                        for _ in handler(
                            self,
                            self.settings,
                        ):
                            pass
                    elif inspect.isasyncgenfunction(handler):
                        async for _ in handler(
                            self,
                            self.settings,
                        ):
                            pass
                    elif inspect.isfunction(handler):
                        handler(
                            self,
                            self.settings,
                        )

    @overload
    async def async_get_data(
        self,
        *,
        type: Literal['parsed'],
        ensure_keys: list[str],
        validate_handler: "OutputValidateHandler | list[OutputValidateHandler] | None" = None,
        key_style: Literal["dot", "slash"] = "dot",
        max_retries: int = 3,
        raise_ensure_failure: bool = True,
        _retry_count: int = 0,
    ) -> dict[str, Any]: ...

    @overload
    async def async_get_data(
        self,
        *,
        type: Literal['original', 'parsed', 'all'] = "parsed",
        ensure_keys: list[str] | None = None,
        validate_handler: "OutputValidateHandler | list[OutputValidateHandler] | None" = None,
        key_style: Literal["dot", "slash"] = "dot",
        max_retries: int = 3,
        raise_ensure_failure: bool = True,
        _retry_count: int = 0,
    ) -> Any: ...

    async def async_get_data(
        self,
        *,
        type: Literal['original', 'parsed', 'all'] = "parsed",
        ensure_keys: list[str] | None = None,
        validate_handler: "OutputValidateHandler | list[OutputValidateHandler] | None" = None,
        key_style: Literal["dot", "slash"] = "dot",
        max_retries: int = 3,
        raise_ensure_failure: bool = True,
        _retry_count: int = 0,
    ) -> Any:
        auto_ensure_keys = self._get_auto_ensure_keys(key_style=key_style)
        strict_output = self._is_strict_output_enabled()
        active_validate_handlers = self._resolve_validate_handlers(validate_handler)
        if ensure_keys is None:
            active_ensure_keys = auto_ensure_keys
        elif len(ensure_keys) == 0:
            active_ensure_keys = []
        else:
            active_ensure_keys = self._merge_ensure_keys(auto_ensure_keys, ensure_keys)
        should_validate = bool(active_validate_handlers) or self._validate_outcome is not None
        needs_constraint_flow = (type in ("parsed", "all") and (active_ensure_keys or strict_output)) or should_validate
        if not needs_constraint_flow:
            try:
                return await self._response_parser.async_get_data(type=type)
            finally:
                await self._run_finally_handlers_once()

        try:
            data = await self._response_parser.async_get_data(type=type)
            try:
                if strict_output:
                    parsed_result = self._response_parser.full_result_data.get("parsed_result")
                    result_object = self._response_parser.full_result_data.get("result_object")
                    if parsed_result is None or result_object is None:
                        raise ValueError(
                            "Strict output validation failed: parsed result or strict result object is missing."
                        )
                if active_ensure_keys:
                    for ensure_key in active_ensure_keys:
                        EMPTY = object()
                        if DataLocator.locate_path_in_dict(data, ensure_key, key_style, default=EMPTY) is EMPTY:
                            raise ValueError(f"Missing ensure key: { ensure_key }")
            except Exception:
                await self._emit_retrying_event(
                    retry_count=_retry_count,
                    response_text=await self._response_parser.async_get_text(),
                    active_ensure_keys=active_ensure_keys,
                    strict_output=strict_output,
                    key_style=key_style,
                    retry_reason="output_constraints",
                )

                if _retry_count < max_retries:
                    return await self._retry_get_data(
                        type=type,
                        ensure_keys=active_ensure_keys,
                        validate_handler=validate_handler,
                        key_style=key_style,
                        max_retries=max_retries,
                        raise_ensure_failure=raise_ensure_failure,
                        retry_count=_retry_count + 1,
                    )
                if raise_ensure_failure:
                    raise self._build_output_retry_failure_exception(
                        active_ensure_keys=active_ensure_keys,
                        strict_output=strict_output,
                        max_retries=max_retries,
                    )
                return await self._response_parser.async_get_data(type=type)

            validation_outcome = await self._run_validate_handlers_once(
                active_validate_handlers,
                retry_count=_retry_count,
                max_retries=max_retries,
            )
            if validation_outcome is not None and not validation_outcome["ok"]:
                if validation_outcome.get("retryable", True) and _retry_count < max_retries:
                    await self._emit_retrying_event(
                        retry_count=_retry_count,
                        response_text=await self._response_parser.async_get_text(),
                        active_ensure_keys=active_ensure_keys,
                        strict_output=strict_output,
                        key_style=key_style,
                        validation_outcome=validation_outcome,
                        retry_reason="validate",
                    )
                    return await self._retry_get_data(
                        type=type,
                        ensure_keys=active_ensure_keys,
                        validate_handler=validate_handler,
                        key_style=key_style,
                        max_retries=max_retries,
                        raise_ensure_failure=raise_ensure_failure,
                        retry_count=_retry_count + 1,
                    )
                if validation_outcome.get("raise_value") is not None or raise_ensure_failure:
                    raise self._build_validation_failure_exception(validation_outcome)
                return await self._response_parser.async_get_data(type=type)
            return data
        finally:
            await self._run_finally_handlers_once()

    @overload
    async def async_get_data_object(
        self,
    ) -> "BaseModel | None": ...

    @overload
    async def async_get_data_object(
        self,
        *,
        ensure_keys: list[str],
        validate_handler: "OutputValidateHandler | list[OutputValidateHandler] | None" = None,
        key_style: Literal["dot", "slash"] = "dot",
        max_retries: int = 3,
        raise_ensure_failure: bool = True,
    ) -> "BaseModel": ...

    @overload
    async def async_get_data_object(
        self,
        *,
        ensure_keys: None,
        validate_handler: "OutputValidateHandler | list[OutputValidateHandler] | None" = None,
        key_style: Literal["dot", "slash"] = "dot",
        max_retries: int = 3,
        raise_ensure_failure: bool = True,
    ) -> "BaseModel | None": ...

    async def async_get_data_object(
        self,
        *,
        ensure_keys: list[str] | None = None,
        validate_handler: "OutputValidateHandler | list[OutputValidateHandler] | None" = None,
        key_style: Literal["dot", "slash"] = "dot",
        max_retries: int = 3,
        raise_ensure_failure: bool = True,
    ):
        auto_ensure_keys = self._get_auto_ensure_keys(key_style=key_style)
        strict_output = self._is_strict_output_enabled()
        active_validate_handlers = self._resolve_validate_handlers(validate_handler)
        if ensure_keys is None:
            active_ensure_keys = auto_ensure_keys
        elif len(ensure_keys) == 0:
            active_ensure_keys = []
        else:
            active_ensure_keys = self._merge_ensure_keys(auto_ensure_keys, ensure_keys)
        if active_ensure_keys or strict_output or bool(active_validate_handlers) or self._validate_outcome is not None:
            await self.async_get_data(
                ensure_keys=active_ensure_keys,
                validate_handler=validate_handler,
                key_style=key_style,
                max_retries=max_retries,
                _retry_count=0,
                raise_ensure_failure=raise_ensure_failure,
            )
            result_object = await self._response_parser.async_get_data_object()
            await self._run_finally_handlers_once()
            return result_object
        result_object = await self._response_parser.async_get_data_object()
        await self._run_finally_handlers_once()
        return result_object

    async def async_get_meta(self):
        meta = await self._response_parser.async_get_meta()
        await self._run_finally_handlers_once()
        return meta

    async def async_get_text(self):
        text = await self._response_parser.async_get_text()
        await self._run_finally_handlers_once()
        return text

    @overload
    def get_generator(
        self,
        type: "InstantStreamingContentType",
        *,
        specific: "SpecificEvents" = DEFAULT_SPECIFIC_EVENTS,
    ) -> Generator["StreamingData", None, None]: ...

    @overload
    def get_generator(
        self,
        type: Literal["all"],
        *,
        specific: "SpecificEvents" = DEFAULT_SPECIFIC_EVENTS,
    ) -> Generator[tuple[str, Any], None, None]: ...

    @overload
    def get_generator(
        self,
        type: Literal["delta", "specific", "original"],
        *,
        specific: "SpecificEvents" = DEFAULT_SPECIFIC_EVENTS,
    ) -> Generator[str, None, None]: ...

    @overload
    def get_generator(
        self,
        type: "ResponseContentType | None" = "delta",
        *,
        specific: "SpecificEvents" = DEFAULT_SPECIFIC_EVENTS,
    ) -> Generator: ...

    def get_generator(
        self,
        type: "ResponseContentType | None" = None,
        content: "ResponseContentType | None" = None,
        *,
        specific: "SpecificEvents" = DEFAULT_SPECIFIC_EVENTS,
    ) -> Generator:
        if type is None:
            if content is not None:
                DeprecationWarnings.warn_deprecated_once(
                    "ModelResponseResult.get_generator.content",
                    "Parameter `content` in method .get_generator() is  deprecated and will be removed in future "
                    "version, please use parameter `type` instead.",
                    stacklevel=2,
                )
                type = content
            else:
                type = "delta"
        parsed_generator = self._response_parser.get_generator(type=type, specific=specific)
        completed = False
        for data in parsed_generator:
            yield data
        completed = True
        if completed:
            self._run_finally_handlers_once_sync()

    @overload
    def get_async_generator(
        self,
        type: "InstantStreamingContentType",
        *,
        specific: "SpecificEvents" = DEFAULT_SPECIFIC_EVENTS,
    ) -> AsyncGenerator["StreamingData", None]: ...

    @overload
    def get_async_generator(
        self,
        type: Literal["all"],
        *,
        specific: "SpecificEvents" = DEFAULT_SPECIFIC_EVENTS,
    ) -> AsyncGenerator[tuple[str, Any], None]: ...

    @overload
    def get_async_generator(
        self,
        type: Literal["delta", "specific", "original"],
        *,
        specific: "SpecificEvents" = DEFAULT_SPECIFIC_EVENTS,
    ) -> AsyncGenerator[str, None]: ...

    @overload
    def get_async_generator(
        self,
        type: "ResponseContentType | None" = "delta",
        *,
        specific: "SpecificEvents" = DEFAULT_SPECIFIC_EVENTS,
    ) -> AsyncGenerator: ...

    async def get_async_generator(
        self,
        type: "ResponseContentType | None" = None,
        content: "ResponseContentType | None" = None,
        *,
        specific: "SpecificEvents" = DEFAULT_SPECIFIC_EVENTS,
    ) -> AsyncGenerator:
        if type is None:
            if content is not None:
                DeprecationWarnings.warn_deprecated_once(
                    "ModelResponseResult.get_async_generator.content",
                    "Parameter `content` in method .get_async_generator() is  deprecated and will be removed in "
                    "future version, please use parameter `type` instead.",
                    stacklevel=2,
                )
                type = content
            else:
                type = "delta"
        parsed_generator = self._response_parser.get_async_generator(type=type, specific=specific)
        completed = False
        async for data in parsed_generator:
            yield data
        completed = True
        if completed:
            await self._run_finally_handlers_once()
