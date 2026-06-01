"""Multi-endpoint chat completion clients with graceful retry."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence, Type, Union

import openai

from .create_utils import create_client_from_config
from .messages import CreateResult, LLMMessage, Tool, ToolSchema
from .wrapper import ChatCompletionClient


_KWARGS_JSON_KEY = "CHAT_COMPLETION_KWARGS_JSON"


def _sanitize_extra_args_for_log(extra_create_args: Mapping[str, Any]) -> dict:
    sanitized: Dict[str, Any] = {}
    for k, v in extra_create_args.items():
        if k == "input" and isinstance(v, list):
            sanitized[k] = f"[{len(v)} items]"
        else:
            sanitized[k] = v
    return sanitized


class GracefulRetryClient(ChatCompletionClient):
    """A multi-endpoint client that retries across endpoints on failure.

    Each ``create()`` round-robins over a pool of underlying
    :class:`ChatCompletionClient` wrappers, escalating to a different
    endpoint on transient errors and blocklisting endpoints that 4xx
    permanently.
    """

    def __init__(
        self,
        clients: List[ChatCompletionClient],
        support_json: bool = True,
        logger: Optional[logging.Logger] = None,
        max_retries: int = 8,
        max_tokens: int = 115000,
        timeout: Optional[float] = None,
    ):
        super().__init__(max_tokens=max_tokens)
        if not clients:
            raise ValueError("GracefulRetryClient requires at least one client")
        self._clients = clients
        self.logger = logger or logging.getLogger(__name__)
        self.max_retries = max_retries
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.support_json = support_json
        self.blocklist: set = set()
        self._client_idx = random.randint(0, len(clients) - 1)

    def convert_client_type(self, new_client_type: Type[ChatCompletionClient]) -> None:
        for client in self._clients:
            convert = getattr(client, "convert_client_type", None)
            if callable(convert):
                convert(new_client_type)

    @staticmethod
    def _should_include_model(
        model_name: str, model_name_filter: Union[str, List[str]]
    ) -> bool:
        """Return True if ``model_name`` matches ``model_name_filter``.

        ``model_name_filter`` may be a single string or list. ``"*"``
        matches everything. Comparison is exact match per filter entry.
        """
        if isinstance(model_name_filter, str):
            model_name_filter = [model_name_filter]
        return any(f == "*" or model_name == f for f in model_name_filter)

    @staticmethod
    def from_files(
        files: Sequence[os.PathLike],
        logger: logging.Logger,
        eval_model: Union[str, List[str]] = "gpt-4o",
    ) -> "GracefulRetryClient":
        client_jsons = []
        for client_config in files:
            with open(client_config) as f:
                config_openai = json.load(f)
            model_name = config_openai[_KWARGS_JSON_KEY]["model"]
            if GracefulRetryClient._should_include_model(model_name, eval_model):
                client_jsons.append(config_openai)

        clients = [create_client_from_config(config=cfg) for cfg in client_jsons]
        if not clients:
            raise ValueError(
                f"Error! None of the models in the input judge config files match "
                f"--eval_model={eval_model} in {list(files)}"
            )
        return GracefulRetryClient(clients=clients, logger=logger)

    @staticmethod
    def from_path(
        path: os.PathLike,
        logger: logging.Logger,
        eval_model: Union[str, List[str]] = "gpt-4o",
    ) -> "GracefulRetryClient":
        endpoint_config = Path(path).resolve()
        if not endpoint_config.exists():
            raise ValueError(f"Endpoint config file {endpoint_config} does not exist.")

        if endpoint_config.is_dir():
            files: List[Path] = [
                p for p in endpoint_config.iterdir() if p.suffix == ".json"
            ]
        else:
            files = [endpoint_config]

        logger.info(f"loaded {len(files)} endpoint configuration files: {path}")
        client_group = GracefulRetryClient.from_files(
            files=files, logger=logger, eval_model=eval_model
        )
        logger.info(
            f"Instantiated {len(client_group._clients)} clients for the {eval_model} endpoints"
        )
        return client_group

    def supports_json(self) -> bool:
        return self.support_json

    @staticmethod
    def _is_reasoning_model(description: str) -> bool:
        return any(tag in description for tag in ("o1", "o3", "o4", "gpt-5"))

    def _remove_reasoning_effort_if_needed(
        self, client: ChatCompletionClient, extra_create_args: Mapping[str, Any]
    ) -> None:
        if (
            not self._is_reasoning_model(client.description)
            and "reasoning_effort" in extra_create_args
        ):
            del extra_create_args["reasoning_effort"]

    def _validate_token_limit(self, request_tokens: int) -> None:
        if request_tokens and request_tokens > self.max_tokens:
            error_msg = (
                f"PromptTooLargeError: Requesting {request_tokens} tokens exceeding "
                f"{self.max_tokens} is forbidden -- abandoning request"
            )
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

    def next_client(self, no_increment: bool = False) -> ChatCompletionClient:
        valid_clients = [c for c in self._clients if c.endpoint not in self.blocklist]
        if not valid_clients:
            raise RuntimeError(
                f"All {len(self._clients)} endpoints are blocked/down. "
                f"Blocklist: {self.blocklist}"
            )
        client = valid_clients[self._client_idx % len(valid_clients)]
        if not no_increment:
            self._client_idx = (self._client_idx + 1) % len(valid_clients)
        return client

    async def close(self) -> None:
        for client in self._clients:
            await client.close()

    async def create(
        self,
        messages: Sequence[LLMMessage],
        tools: Sequence[Tool | ToolSchema] = (),
        json_output: Optional[bool] = None,
        extra_create_args: Mapping[str, Any] = {},
    ) -> CreateResult:
        tries = self.max_retries
        last_error: Optional[Exception] = None
        client = self.next_client(no_increment=True)
        # Mutable copy so we can mutate per-request without affecting callers.
        extra = dict(extra_create_args)

        while tries > 0:
            request_tokens = client.count_tokens(messages=messages)
            self._remove_reasoning_effort_if_needed(client, extra)
            self.logger.info(
                f"GracefulRetryClient.create(): {client.description}, "
                f"request_tokens: {request_tokens}, "
                f"extra_create_args={_sanitize_extra_args_for_log(extra)}"
            )
            self._validate_token_limit(request_tokens)

            try:
                if self.timeout is not None:
                    result = await asyncio.wait_for(
                        client.create(
                            messages=messages,
                            tools=tools,
                            json_output=json_output,
                            extra_create_args=extra,
                        ),
                        timeout=self.timeout,
                    )
                else:
                    result = await client.create(
                        messages=messages,
                        tools=tools,
                        json_output=json_output,
                        extra_create_args=extra,
                    )
                return result
            except asyncio.TimeoutError:
                tries -= 1
                self.logger.error(
                    f"GracefulRetryClient.create() TimeoutError: {client.description} "
                    f"timed out after {self.timeout}s, switching client"
                )
                client = self.next_client()
                await asyncio.sleep(1)
                continue
            except openai.BadRequestError as e:
                if "check-access-response-enc" in str(e):
                    self.logger.error(
                        f"GracefulRetryClient.create() AccessTokenError: {client.description}, refreshing credentials\n{e}"
                    )
                    if hasattr(client, "refresh_credentials"):
                        client.refresh_credentials()
                    client = self.next_client()
                    await asyncio.sleep(1)
                    continue
                if "previous_response_not_found" in str(e):
                    self.logger.warning(
                        f"GracefulRetryClient.create() previous_response_not_found: {client.description}\n{e}"
                    )
                    tries -= 1
                    last_error = e
                    client = self.next_client()
                    await asyncio.sleep(0.5)
                    continue
                if (
                    "Invalid prompt" in str(e)
                    or "content management policy" in str(e)
                    or "Please try again with a different prompt" in str(e)
                ):
                    self.logger.error(
                        f"GracefulRetryClient.create() Invalid prompt: {client.description}\n{e}"
                    )
                    tries -= 1
                    last_error = e
                    client = self.next_client()
                    await asyncio.sleep(0.5)
                    continue
                self.logger.error(
                    f"GracefulRetryClient.create() {client.description} Raising openai.BadRequestError: {e}"
                )
                raise
            except openai.InternalServerError as e:
                self.logger.error(
                    f"GracefulRetryClient.create() InternalServerError: {client.description}, switching client: {e}"
                )
                tries -= 1
                client = self.next_client()
                await asyncio.sleep(2)
                continue
            except openai.RateLimitError as e:
                tries -= 1
                sleep_time = 2 ** (self.max_retries - tries)
                self.logger.error(
                    f"GracefulRetryClient.create() RateLimitError: {client.description}, sleeping {sleep_time}s: {e}"
                )
                client = self.next_client()
                await asyncio.sleep(sleep_time)
                continue
            except openai.NotFoundError as e:
                self.logger.error(
                    f"GracefulRetryClient.create() NotFoundError: {client.description}, BLOCKING {client.endpoint}: {e}"
                )
                self.blocklist.add(client.endpoint)
                client = self.next_client()
                await asyncio.sleep(1)
                continue
            except openai.PermissionDeniedError as e:
                self.logger.error(
                    f"GracefulRetryClient.create() PermissionDeniedError: {client.description}, BLOCKING {client.endpoint}: {e}"
                )
                self.blocklist.add(client.endpoint)
                client = self.next_client()
                await asyncio.sleep(1)
                continue
            except openai.APIConnectionError as e:
                self.logger.error(
                    f"GracefulRetryClient.create() APIConnectionError: {client.description}, BLOCKING {client.endpoint}: {e}"
                )
                self.blocklist.add(client.endpoint)
                client = self.next_client()
                await asyncio.sleep(1)
                continue
            except openai.AuthenticationError as e:
                self.logger.error(
                    f"GracefulRetryClient.create() AuthenticationError: {client.description}: {e}"
                )
                if hasattr(client, "refresh_credentials"):
                    client.refresh_credentials()
                client = self.next_client()
                continue
            except openai.APIStatusError as e:
                if "Prompt is too large" in str(e):
                    self.logger.error(
                        f"GracefulRetryClient.create() PromptTooLargeError: ({request_tokens} tokens) is too big\n{e}"
                    )
                if "DeploymentNotFound" in str(e):
                    self.logger.error(
                        f"GracefulRetryClient.create() DeploymentNotFound: {client.description}, BLOCKING {client.endpoint}: {e}"
                    )
                    self.blocklist.add(client.endpoint)
                    client = self.next_client()
                    await asyncio.sleep(1)
                    continue
                if "Request body too large" in str(e):
                    self.logger.error(
                        f"GracefulRetryClient.create() Request body too large: {client.description}\n{e}"
                    )
                    tries -= 1
                    client = self.next_client()
                    await asyncio.sleep(1)
                    continue
                raise
            except Exception as e:
                if "please try again" in str(e).lower():
                    tries -= 1
                    self.logger.error(
                        f"GracefulRetryClient.create() Generic Exception: {client.description}: {e}"
                    )
                    client = self.next_client()
                    sleep_time = 2 ** (self.max_retries - tries)
                    await asyncio.sleep(sleep_time)
                    continue
                self.logger.error(
                    f"GracefulRetryClient.create() {client.description} Raising Exception: {e}"
                )
                raise

        if last_error:
            raise last_error
        valid_clients = [c for c in self._clients if c.endpoint not in self.blocklist]
        raise Exception(
            f"GracefulRetryClient.create(): all clients exhausted after {self.max_retries} retries; "
            f"{len(valid_clients)}/{len(self._clients)} clients reachable. Blocklist size: {len(self.blocklist)}"
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {"LlmClient": self._clients[0].description}


class ResponsesGracefulRetryClient(GracefulRetryClient):
    """Variant that targets the Responses API (codex / gpt-5 family)."""

    @staticmethod
    def from_files(
        files: Sequence[os.PathLike],
        logger: logging.Logger,
        eval_model: Union[str, List[str]] = "gpt-4o",
    ) -> "ResponsesGracefulRetryClient":
        client_jsons = []
        for client_config in files:
            with open(client_config) as f:
                config_openai = json.load(f)
            model_name = config_openai[_KWARGS_JSON_KEY]["model"]
            if GracefulRetryClient._should_include_model(model_name, eval_model):
                client_jsons.append(config_openai)
        clients = [create_client_from_config(config=cfg, use_responses_api=True) for cfg in client_jsons]
        if not clients:
            raise ValueError(
                f"Error! None of the models in the input config files match --eval_model={eval_model} in {list(files)}"
            )
        return ResponsesGracefulRetryClient(clients=clients, logger=logger)

    @staticmethod
    def from_path(
        path: os.PathLike,
        logger: logging.Logger,
        eval_model: Union[str, List[str]] = "gpt-4o",
    ) -> "ResponsesGracefulRetryClient":
        endpoint_config = Path(path).resolve()
        if not endpoint_config.exists():
            raise ValueError(f"Endpoint config file {endpoint_config} does not exist.")
        files = (
            [p for p in endpoint_config.iterdir() if p.suffix == ".json"]
            if endpoint_config.is_dir()
            else [endpoint_config]
        )
        logger.info(f"loaded {len(files)} endpoint configuration files: {path}")
        client_group = ResponsesGracefulRetryClient.from_files(
            files=files, logger=logger, eval_model=eval_model
        )
        logger.info(
            f"Instantiated {len(client_group._clients)} clients for the {eval_model} endpoints"
        )
        return client_group
