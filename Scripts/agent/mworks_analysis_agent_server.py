#!/usr/bin/env python3
"""Local, read-only OpenAI Responses-compatible backend for MoSim Studio.

The server binds only to loopback.  It never reads an API key from a project
file: the key must be supplied in the process environment.  The supported
tools are implemented in ``model_studio_agent_tools.py`` and are read-only.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import time
import tomllib
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from model_studio_agent_tools import call_tool, openai_tool_definitions


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "Config" / "control_platform" / "model_studio_agent_v1.toml"
LOGGER = logging.getLogger("mosim.model_studio_agent")


@dataclass(frozen=True)
class AgentConfig:
    host: str
    port: int
    base_url: str
    base_url_env: str
    api_key_env: str
    fallback_api_key_env: str
    model_provider: str
    model: str
    review_model: str
    reasoning_effort: str
    disable_response_storage: bool
    network_access: str
    max_question_chars: int
    max_answer_chars: int
    max_tool_rounds: int
    max_tools_per_turn: int
    request_timeout_s: int

    @property
    def api_key(self) -> str:
        return os.environ.get(self.api_key_env, "") or os.environ.get(self.fallback_api_key_env, "")

    @property
    def resolved_base_url(self) -> str:
        return (os.environ.get(self.base_url_env, "") or self.base_url).rstrip("/")


def load_config(config_path: Path = CONFIG_PATH) -> AgentConfig:
    """Load non-secret Agent configuration from the repository."""
    with config_path.open("rb") as handle:
        document = tomllib.load(handle)
    if document.get("schema") != "mosim.model_studio_agent.v1":
        raise RuntimeError("model_studio_agent_config_schema_mismatch")
    service = document.get("service", {})
    provider = document.get("provider", {})
    limits = document.get("limits", {})
    return AgentConfig(
        host=str(service.get("host", "127.0.0.1")),
        port=int(service.get("port", 8765)),
        base_url=str(provider["base_url"]),
        base_url_env=str(provider.get("base_url_env", "MOSIM_AGENT_BASE_URL")),
        api_key_env=str(provider.get("api_key_env", "MOSIM_OPENAI_API_KEY")),
        fallback_api_key_env=str(provider.get("fallback_api_key_env", "OPENAI_API_KEY")),
        model_provider=str(provider.get("model_provider", "OpenAI")),
        model=str(provider["model"]),
        review_model=str(provider.get("review_model", provider["model"])),
        reasoning_effort=str(provider.get("model_reasoning_effort", "high")),
        disable_response_storage=bool(provider.get("disable_response_storage", True)),
        network_access=str(provider.get("network_access", "enabled")),
        max_question_chars=int(limits.get("max_question_chars", 6000)),
        max_answer_chars=int(limits.get("max_answer_chars", 2400)),
        max_tool_rounds=int(limits.get("max_tool_rounds", 4)),
        max_tools_per_turn=int(limits.get("max_tools_per_turn", 6)),
        request_timeout_s=int(limits.get("request_timeout_s", 60)),
    )


CONFIG = load_config()


SYSTEM_PROMPT = """你是 MoSim Studio 内置的 MWORKS 仿真分析助手。

职责：基于当前 Studio 配置和只读项目证据，解释控制链、任务路由、场景参数、已有结果与手动操作步骤。回答使用简洁中文，所有结论应区分“实现/可打开/已验证/待验证”。

强制边界：
1. 只能调用给出的只读工具；不能修改 Models、Config、Results、代码或文档。
2. 不能启动 CheckModel、仿真、代码生成、编译或任何 MWORKS 自动化动作。
3. 不能发送或建议已经发送 QGC、Gazebo、PX4、ROS、MAVROS、飞控或电机命令。
4. 不得把 Studio 页面状态、模型可打开、静态源码、截图或目录存在误报为仿真/运行时通过。
5. 不得读取、索取、复述或输出 API key、令牌、环境变量或本机配置。
6. 对于未找到证据的结论，明确写“待验证”并给出可人工执行的下一步。

当问题涉及当前配置时，先使用传入的 Studio 上下文；需要证据时再调用最少量的只读工具。工具结果中的路径均为项目内相对路径。不要声称执行了工具以外的操作。
"""


def health_payload(config: AgentConfig = CONFIG) -> dict[str, Any]:
    """Build a key-free health payload."""
    return {
        "status": "ok",
        "configured": bool(config.api_key),
        "model_provider": config.model_provider,
        "model": config.model,
        "api_key_env": config.api_key_env,
        "base_url_configured": bool(config.resolved_base_url),
        "tools_count": len(openai_tool_definitions()),
        "read_only": True,
        "bind_scope": "loopback_only",
    }


def _response_request(config: AgentConfig, payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        config.resolved_base_url + "/responses",
        data=body,
        headers={
            "Authorization": "Bearer " + config.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=config.request_timeout_s) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"model_http_{exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("model_network_unavailable") from exc
    except TimeoutError as exc:
        raise RuntimeError("model_request_timeout") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError("model_invalid_json") from exc


def _message_text(response: dict[str, Any]) -> str:
    direct = response.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()
    fragments: list[str] = []
    for item in response.get("output", []):
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if not isinstance(content, dict):
                continue
            text = content.get("text")
            if isinstance(text, str) and text.strip():
                fragments.append(text.strip())
            elif isinstance(content.get("text"), dict):
                value = content["text"].get("value")
                if isinstance(value, str) and value.strip():
                    fragments.append(value.strip())
    return "\n".join(fragments).strip()


def _function_calls(response: dict[str, Any]) -> list[dict[str, Any]]:
    calls = []
    for item in response.get("output", []):
        if isinstance(item, dict) and item.get("type") == "function_call":
            calls.append(item)
    return calls


def _initial_payload(config: AgentConfig, question: str, context_text: str) -> dict[str, Any]:
    context = context_text.strip()[:2400] if context_text else "未提供当前 Studio 上下文。"
    return {
        "model": config.model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "当前 Studio 上下文：\n" + context + "\n\n用户问题：\n" + question,
                    }
                ],
            },
        ],
        "tools": openai_tool_definitions(),
        "tool_choice": "auto",
        "store": not config.disable_response_storage,
        "reasoning": {"effort": config.reasoning_effort},
    }


def _follow_up_payload(config: AgentConfig, response_id: str, outputs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "model": config.model,
        "previous_response_id": response_id,
        "input": outputs,
        "tools": openai_tool_definitions(),
        "tool_choice": "auto",
        "store": not config.disable_response_storage,
        "reasoning": {"effort": config.reasoning_effort},
    }


def query_agent(question: str, context_text: str = "", config: AgentConfig = CONFIG) -> dict[str, Any]:
    """Run a bounded Responses tool loop and return a safe UI payload."""
    request_id = uuid.uuid4().hex[:12]
    if not isinstance(question, str) or not question.strip():
        return {
            "ok": False,
            "request_id": request_id,
            "error_code": "empty_question",
            "answer": "请先输入一个问题。",
            "tools_used": [],
        }
    if len(question) > config.max_question_chars:
        return {
            "ok": False,
            "request_id": request_id,
            "error_code": "question_too_long",
            "answer": f"问题超过 {config.max_question_chars} 个字符，请缩短后重试。",
            "tools_used": [],
        }
    if not config.api_key:
        return {
            "ok": False,
            "request_id": request_id,
            "error_code": "model_not_configured",
            "answer": f"未检测到 {config.api_key_env}；助手已保留本地只读指引。",
            "tools_used": [],
        }

    tools_used: list[str] = []
    try:
        response = _response_request(config, _initial_payload(config, question.strip(), context_text))
        for _ in range(config.max_tool_rounds):
            calls = _function_calls(response)
            answer = _message_text(response)
            if not calls:
                final_answer = answer or "模型未返回可显示的文本，请换一种问法。"
                LOGGER.info("request=%s status=ok tools=%s", request_id, ",".join(tools_used) or "none")
                return {
                    "ok": True,
                    "request_id": request_id,
                    "answer": final_answer[: config.max_answer_chars],
                    "tools_used": tools_used,
                }
            if len(calls) > config.max_tools_per_turn:
                calls = calls[: config.max_tools_per_turn]
            outputs = []
            for call in calls:
                name = str(call.get("name", ""))
                call_id = str(call.get("call_id") or call.get("id") or uuid.uuid4().hex)
                raw_arguments = call.get("arguments", "{}")
                try:
                    arguments = json.loads(raw_arguments) if isinstance(raw_arguments, str) else raw_arguments
                except json.JSONDecodeError:
                    arguments = {}
                    tool_result = {"ok": False, "error": "invalid_arguments", "message": "模型返回的工具参数不是 JSON。"}
                else:
                    tool_result = call_tool(name, arguments)
                tools_used.append(name)
                outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": json.dumps(tool_result, ensure_ascii=False),
                    }
                )
            response_id = response.get("id")
            if not isinstance(response_id, str) or not response_id:
                raise RuntimeError("model_response_id_missing")
            response = _response_request(config, _follow_up_payload(config, response_id, outputs))
        LOGGER.info("request=%s status=tool_limit tools=%s", request_id, ",".join(tools_used))
        return {
            "ok": False,
            "request_id": request_id,
            "error_code": "tool_round_limit",
            "answer": "已达到只读工具调用上限。请把问题缩小到一个控制器、任务或结果目录后重试。",
            "tools_used": tools_used,
        }
    except RuntimeError as exc:
        code = str(exc)
        LOGGER.warning("request=%s status=%s tools=%s", request_id, code, ",".join(tools_used) or "none")
        messages = {
            "model_network_unavailable": "无法连接模型服务。请检查网络或本机 MOSIM_AGENT_BASE_URL 配置。",
            "model_request_timeout": "模型服务请求超时，请稍后重试。",
            "model_invalid_json": "模型服务返回了无法解析的响应。",
            "model_response_id_missing": "模型服务不支持所需的 Responses 工具续接格式。",
        }
        return {
            "ok": False,
            "request_id": request_id,
            "error_code": code,
            "answer": messages.get(code, "模型服务请求失败：" + code),
            "tools_used": tools_used,
        }


class AgentRequestHandler(BaseHTTPRequestHandler):
    """Minimal stdlib fallback when FastAPI is not installed."""

    server_version = "MoSimAgent/1.0"

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send_json(HTTPStatus.OK, health_payload())
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/mworks/query":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})
            return
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 32_000:
                raise ValueError("invalid_content_length")
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            result = query_agent(str(payload.get("question", "")), str(payload.get("context_text", "")))
            self._send_json(HTTPStatus.OK, result)
        except (ValueError, json.JSONDecodeError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_json_request"})

    def log_message(self, format: str, *args: Any) -> None:
        LOGGER.debug("http=" + format, *args)


def serve_stdlib(host: str, port: int) -> None:
    """Serve the small local API with Python's standard library."""
    httpd = ThreadingHTTPServer((host, port), AgentRequestHandler)
    LOGGER.info("serving stdlib backend on http://%s:%d", host, port)
    httpd.serve_forever(poll_interval=0.5)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=CONFIG.host)
    parser.add_argument("--port", type=int, default=CONFIG.port)
    parser.add_argument("--health", action="store_true", help="Print key-free health JSON and exit.")
    parser.add_argument("--stdlib", action="store_true", help="Force the dependency-free HTTP server.")
    args = parser.parse_args()
    logging.basicConfig(level=os.environ.get("MOSIM_AGENT_LOG_LEVEL", "INFO"), format="%(levelname)s %(message)s")
    if args.health:
        print(json.dumps(health_payload(), ensure_ascii=False))
        return 0
    if args.host not in {"127.0.0.1", "localhost", "::1"}:
        raise SystemExit("Only loopback binding is allowed for the Model Studio agent.")
    if args.stdlib:
        serve_stdlib(args.host, args.port)
        return 0
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        import uvicorn
    except ImportError:
        serve_stdlib(args.host, args.port)
        return 0

    app = FastAPI(title="MoSim Model Studio Agent", docs_url=None, redoc_url=None)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1", "http://localhost"],
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/health")
    def health() -> dict[str, Any]:
        return health_payload()

    @app.post("/mworks/query")
    def query(payload: dict[str, Any]) -> dict[str, Any]:
        return query_agent(str(payload.get("question", "")), str(payload.get("context_text", "")))

    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
