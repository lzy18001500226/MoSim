import json
import logging
import os
import re
from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import requests

from .oai_clients import (
    ChatCompletionClient,
    ModelCapabilities,
    create_completion_client_from_env as _create_client,
)
from .systems.messages import (
    AgentEvent,
    OrchestrationEvent,
    WebSurferEvent,
)

ENVIRON_KEY_CHAT_COMPLETION_PROVIDER = "CHAT_COMPLETION_PROVIDER"
ENVIRON_KEY_CHAT_COMPLETION_KWARGS_JSON = "CHAT_COMPLETION_KWARGS_JSON"


@dataclass
class LLMCallEvent:
    """Structured log event emitted by :class:`LogHandler` to record token usage."""

    prompt_tokens: int
    completion_tokens: int


def replace_url_with_netloc(text):
    """Replace a string containing a URL with just the netloc."""

    def replace_func(match):
        url = match.group(0)
        return urlparse(url).netloc

    return re.sub(r'https?://[^\s"]+', replace_func, text)


def attempt_parse_json(json_str: str) -> Dict[str, Any]:
    assert isinstance(json_str, str)
    if "```json" in json_str:
        json_str = json_str.split("```json")[1].split("```")[0].strip()
    elif "```" in json_str:
        json_str = json_str.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return eval(json_str)


def create_completion_client_from_env(
    env: Optional[Dict[str, Any]] = None, **kwargs: Any
) -> ChatCompletionClient:
    """Construct a chat completion client from a config dict.

    ``env`` is the same dict shape used elsewhere in webeval (with
    ``CHAT_COMPLETION_PROVIDER`` and ``CHAT_COMPLETION_KWARGS_JSON``
    keys). Any extra ``**kwargs`` override the parsed kwargs (e.g.
    swapping the model name at call sites).
    """
    if env is None:
        env_copy: Dict[str, Any] = dict(os.environ)
    else:
        env_copy = deepcopy(env)

    raw_kwargs = env_copy.get(ENVIRON_KEY_CHAT_COMPLETION_KWARGS_JSON, "{}")
    if isinstance(raw_kwargs, str):
        raw_kwargs = json.loads(raw_kwargs)
    raw_kwargs = dict(raw_kwargs)
    raw_kwargs.update(kwargs)

    if "model_capabilities" in raw_kwargs and isinstance(raw_kwargs["model_capabilities"], dict):
        caps = raw_kwargs["model_capabilities"]
        raw_kwargs["model_capabilities"] = ModelCapabilities(
            vision=bool(caps.get("vision", False)),
            function_calling=bool(caps.get("function_calling", True)),
            json_output=bool(caps.get("json_output", True)),
        )

    config = {
        ENVIRON_KEY_CHAT_COMPLETION_PROVIDER: env_copy.get(
            ENVIRON_KEY_CHAT_COMPLETION_PROVIDER, "openai"
        ),
        ENVIRON_KEY_CHAT_COMPLETION_KWARGS_JSON: raw_kwargs,
    }
    return _create_client(config)


def download_file(url: str, filepath: str) -> None:
    response = requests.get(url)
    response.raise_for_status()
    with open(filepath, "wb") as file:
        file.write(response.content)


def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as file:
        return [json.loads(line) for line in file]


def load_json(filepath: str) -> Dict[str, Any]:
    with open(filepath, "r", encoding="utf-8") as file:
        return json.load(file)


def dict_2_str(d: Dict[str, Any]) -> str:
    return ".".join(f"{k}-{d[k]}" for k in sorted(d.keys()))


class LogHandler(logging.FileHandler):
    """File handler that serialises structured webeval events to JSONL."""

    def __init__(self, filename: str = "log.jsonl") -> None:
        super().__init__(filename)
        self.logs_list: List[Dict[str, Any]] = []

    def emit(self, record: logging.LogRecord) -> None:
        try:
            ts = datetime.fromtimestamp(record.created).isoformat()
            if isinstance(record.msg, OrchestrationEvent):
                payload = {
                    "timestamp": ts,
                    "source": record.msg.source,
                    "message": record.msg.message,
                    "type": "OrchestrationEvent",
                }
                record.msg = json.dumps(payload)
                self.logs_list.append(payload)
                super().emit(record)
            elif isinstance(record.msg, AgentEvent):
                payload = {
                    "timestamp": ts,
                    "source": record.msg.source,
                    "message": record.msg.message,
                    "type": "AgentEvent",
                }
                record.msg = json.dumps(payload)
                self.logs_list.append(payload)
                super().emit(record)
            elif isinstance(record.msg, WebSurferEvent):
                payload = {"timestamp": ts, "type": "WebSurferEvent"}
                payload.update(asdict(record.msg))
                record.msg = json.dumps(payload)
                self.logs_list.append(payload)
                super().emit(record)
            elif isinstance(record.msg, LLMCallEvent):
                payload = {
                    "timestamp": ts,
                    "prompt_tokens": record.msg.prompt_tokens,
                    "completion_tokens": record.msg.completion_tokens,
                    "type": "LLMCallEvent",
                }
                record.msg = json.dumps(payload)
                self.logs_list.append(payload)
                super().emit(record)
            else:
                try:
                    payload = asdict(record.msg)
                except Exception:
                    payload = {"message": str(record.msg)}
                payload["timestamp"] = ts
                payload["type"] = "OtherEvent"
                record.msg = json.dumps(payload)
                self.logs_list.append(payload)
                super().emit(record)
        except Exception:
            self.handleError(record)
