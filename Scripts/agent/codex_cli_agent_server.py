#!/usr/bin/env python3
"""Loopback-only Codex CLI backend for the Model Studio AI tab."""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import tomllib
import uuid
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "Config" / "control_platform" / "model_studio_codex_cli_v1.toml"
LOGGER = logging.getLogger("mosim.model_studio_codex_cli")


@dataclass(frozen=True)
class CodexCliConfig:
    host: str
    port: int
    binary_env: str
    windows_binary: str
    unix_binary: str
    max_question_chars: int
    max_context_chars: int
    max_answer_chars: int
    request_timeout_s: int
    sandbox: str
    approval_policy: str


def load_config(config_path: Path = CONFIG_PATH) -> CodexCliConfig:
    with config_path.open("rb") as handle:
        document = tomllib.load(handle)
    if document.get("schema") != "mosim.model_studio_codex_cli.v1":
        raise RuntimeError("model_studio_codex_cli_config_schema_mismatch")
    service = document.get("service", {})
    cli = document.get("codex_cli", {})
    limits = document.get("limits", {})
    safety = document.get("safety", {})
    config = CodexCliConfig(
        host=str(service.get("host", "127.0.0.1")),
        port=int(service.get("port", 8765)),
        binary_env=str(cli.get("binary_env", "MOSIM_CODEX_BIN")),
        windows_binary=str(cli["windows_binary"]),
        unix_binary=str(cli["unix_binary"]),
        max_question_chars=int(limits.get("max_question_chars", 6000)),
        max_context_chars=int(limits.get("max_context_chars", 2400)),
        max_answer_chars=int(limits.get("max_answer_chars", 2400)),
        request_timeout_s=int(limits.get("request_timeout_s", 110)),
        sandbox=str(safety.get("sandbox", "read-only")),
        approval_policy=str(safety.get("approval_policy", "never")),
    )
    if config.sandbox != "read-only":
        raise RuntimeError("model_studio_codex_cli_requires_read_only_sandbox")
    if config.approval_policy != "never":
        raise RuntimeError("model_studio_codex_cli_requires_never_approval_policy")
    return config


CONFIG = load_config()


SYSTEM_PROMPT = """你是 MoSim Studio 的只读 AI 助手。

只使用当前仓库中可验证的源码、配置和既有结果回答简洁中文问题。清楚区分“已实现”、
“可打开”、“已验证”和“待验证”。不得修改任何文件，不得启动 CheckModel、仿真、
代码生成或编译，不得发送 QGC、Gazebo、PX4、ROS、MAVROS、飞控或电机命令。
不得读取、索取、复述或输出任何凭据、令牌、环境变量或用户配置。不要把 UI 状态、截图
或目录存在误报为仿真或运行时通过。缺少证据时明确写“待验证”，并给出人工下一步。
"""


def project_binary_relative_path(config: CodexCliConfig) -> str:
    return config.windows_binary if os.name == "nt" else config.unix_binary


def resolve_codex_binary(config: CodexCliConfig = CONFIG) -> Path | None:
    root = ROOT.resolve()
    override = os.environ.get(config.binary_env, "").strip()
    if override:
        candidate = Path(override).expanduser().resolve()
        try:
            candidate.relative_to(root)
        except ValueError:
            return None
        return candidate if candidate.is_file() else None
    candidate = (root / project_binary_relative_path(config)).resolve()
    return candidate if candidate.is_file() else None


def safe_child_environment() -> dict[str, str]:
    """Keep Codex login storage, but never expose API-key env vars to its shell tools."""
    environment = os.environ.copy()
    for key in (
        "OPENAI_API_KEY",
        "CODEX_API_KEY",
        "CODEX_ACCESS_TOKEN",
        "MOSIM_OPENAI_API_KEY",
    ):
        environment.pop(key, None)
    return environment


def binary_version(binary: Path) -> str:
    try:
        completed = subprocess.run(
            [str(binary), "--version"],
            cwd=ROOT,
            env=safe_child_environment(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "unavailable"
    if completed.returncode != 0:
        return "unavailable"
    return completed.stdout.strip().splitlines()[0][:160] if completed.stdout.strip() else "unavailable"


def health_payload(config: CodexCliConfig = CONFIG) -> dict[str, Any]:
    binary = resolve_codex_binary(config)
    return {
        "status": "ok",
        "configured": binary is not None,
        "backend": "codex_cli",
        "binary_found": binary is not None,
        "binary_path": project_binary_relative_path(config),
        "binary_version": binary_version(binary) if binary else "not_built",
        "authentication": "codex_login_required",
        "read_only": True,
        "bind_scope": "loopback_only",
    }


def build_prompt(question: str, context_text: str, config: CodexCliConfig = CONFIG) -> str:
    context = context_text.strip()[: config.max_context_chars] or "未提供当前 Studio 上下文。"
    return f"{SYSTEM_PROMPT}\n当前 Studio 上下文：\n{context}\n\n用户问题：\n{question.strip()}"


def build_command(binary: Path, prompt: str, config: CodexCliConfig = CONFIG) -> list[str]:
    return [
        str(binary),
        "exec",
        "--json",
        "--ephemeral",
        "--sandbox",
        config.sandbox,
        "--config",
        f'approval_policy="{config.approval_policy}"',
        "--cd",
        str(ROOT),
        prompt,
    ]


def parse_event_stream(output: str) -> tuple[str, str]:
    answer = ""
    error = ""
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        event_type = event.get("type")
        if event_type == "item.completed":
            item = event.get("item", {})
            if isinstance(item, dict) and item.get("type") == "agent_message":
                text = item.get("text")
                if isinstance(text, str) and text.strip():
                    answer = text.strip()
        elif event_type == "turn.failed":
            failure = event.get("error", {})
            if isinstance(failure, dict):
                error = str(failure.get("message", "turn_failed"))
        elif event_type == "error":
            error = str(event.get("message", "codex_stream_error"))
    return answer, error


def command_failure_code(stdout: str, stderr: str) -> str:
    diagnostic = (stdout + "\n" + stderr).lower()
    if any(token in diagnostic for token in ("login", "auth", "api key", "credential", "unauthorized")):
        return "codex_auth_required"
    return "codex_cli_failed"


def query_agent(question: str, context_text: str = "", config: CodexCliConfig = CONFIG) -> dict[str, Any]:
    request_id = uuid.uuid4().hex[:12]
    if not isinstance(question, str) or not question.strip():
        return {"ok": False, "request_id": request_id, "error_code": "empty_question", "answer": "请先输入一个问题。", "tools_used": []}
    if len(question) > config.max_question_chars:
        return {
            "ok": False,
            "request_id": request_id,
            "error_code": "question_too_long",
            "answer": f"问题超过 {config.max_question_chars} 个字符，请缩短后重试。",
            "tools_used": [],
        }
    binary = resolve_codex_binary(config)
    if binary is None:
        return {
            "ok": False,
            "request_id": request_id,
            "error_code": "codex_not_built",
            "answer": "未检测到项目构建的 Codex CLI。请按发布清单在 src/Agent 中执行构建脚本。",
            "tools_used": [],
        }
    try:
        completed = subprocess.run(
            build_command(binary, build_prompt(question, context_text, config), config),
            cwd=ROOT,
            env=safe_child_environment(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=config.request_timeout_s,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "request_id": request_id,
            "error_code": "codex_timeout",
            "answer": "Codex CLI 响应超时，请缩小问题范围后重试。",
            "tools_used": [],
        }
    except OSError:
        return {
            "ok": False,
            "request_id": request_id,
            "error_code": "codex_cli_unavailable",
            "answer": "项目 Codex CLI 无法启动，请重新构建并验证 --version。",
            "tools_used": [],
        }

    answer, stream_error = parse_event_stream(completed.stdout)
    if completed.returncode != 0:
        error_code = command_failure_code(completed.stdout, completed.stderr)
        message = "Codex 尚未完成 GPT 登录或 Provider 配置。" if error_code == "codex_auth_required" else "Codex CLI 请求失败，请查看本机 Codex 登录与配置。"
        LOGGER.warning("request=%s status=%s", request_id, error_code)
        return {"ok": False, "request_id": request_id, "error_code": error_code, "answer": message, "tools_used": []}
    if not answer:
        LOGGER.warning("request=%s status=empty_response detail=%s", request_id, bool(stream_error))
        return {
            "ok": False,
            "request_id": request_id,
            "error_code": "codex_empty_response",
            "answer": "Codex 未返回可显示的回答，请检查本机登录状态后重试。",
            "tools_used": [],
        }
    LOGGER.info("request=%s status=ok", request_id)
    return {
        "ok": True,
        "request_id": request_id,
        "error_code": "",
        "answer": answer[: config.max_answer_chars],
        "tools_used": ["Codex CLI（只读会话）"],
    }


class AgentRequestHandler(BaseHTTPRequestHandler):
    server_version = "MoSimCodexCli/1.0"

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

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
        except (ValueError, json.JSONDecodeError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_json_request"})
            return
        self._send_json(
            HTTPStatus.OK,
            query_agent(str(payload.get("question", "")), str(payload.get("context_text", ""))),
        )

    def log_message(self, format: str, *args: Any) -> None:
        LOGGER.debug("http=" + format, *args)


def serve(host: str, port: int) -> None:
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Only loopback binding is allowed for the Model Studio Codex backend.")
    httpd = ThreadingHTTPServer((host, port), AgentRequestHandler)
    LOGGER.info("serving Codex CLI bridge on http://%s:%d", host, port)
    httpd.serve_forever(poll_interval=0.5)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=CONFIG.host)
    parser.add_argument("--port", type=int, default=CONFIG.port)
    parser.add_argument("--health", action="store_true", help="Print key-free health JSON and exit.")
    args = parser.parse_args()
    logging.basicConfig(level=os.environ.get("MOSIM_AGENT_LOG_LEVEL", "INFO"), format="%(levelname)s %(message)s")
    if args.health:
        print(json.dumps(health_payload(), ensure_ascii=False))
        return 0
    serve(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
