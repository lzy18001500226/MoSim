#!/usr/bin/env python3
"""Loopback-only Codex CLI backend for the Model Studio AI tab."""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import threading
import time
import tomllib
import uuid
from dataclasses import dataclass, field
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "Config" / "control_platform" / "model_studio_codex_cli_v1.toml"
LOGGER = logging.getLogger("mosim.model_studio_codex_cli")
DEFAULT_AGENT_MODEL = "gpt-5.5"


@dataclass
class TurnRecord:
    """In-memory state for one non-blocking Studio turn.

    Codex owns the durable conversation transcript under CODEX_HOME.  The
    bridge intentionally keeps only status and public activity labels here.
    """

    request_id: str
    codex_thread_id: str = ""
    status: str = "queued"
    answer: str = ""
    partial_answer: str = ""
    error_code: str = ""
    error: str = ""
    activities: list[str] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)
    process: Any = None
    created_at: float = field(default_factory=time.monotonic)
    finished_at: float | None = None


class TurnRegistry:
    """Small loopback-only turn registry; no transcript or credential storage."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._records: dict[str, TurnRecord] = {}

    def create(self, record: TurnRecord) -> None:
        with self._lock:
            self._records[record.request_id] = record

    def get(self, request_id: str) -> TurnRecord | None:
        with self._lock:
            return self._records.get(request_id)

    def payload(self, request_id: str) -> dict[str, Any] | None:
        with self._lock:
            record = self._records.get(request_id)
            return turn_payload(record) if record is not None else None

    def cancel(self, request_id: str) -> dict[str, Any] | None:
        with self._lock:
            record = self._records.get(request_id)
            if record is None:
                return None
            if record.status in {"completed", "failed", "cancelled"}:
                return turn_payload(record)
            record.status = "cancelled"
            record.error_code = "turn_cancelled"
            record.error = "用户已停止本轮只读分析。"
            record.finished_at = time.monotonic()
            _add_activity(record, "用户已停止本轮分析")
            process = record.process
        if process is not None:
            try:
                process.terminate()
            except OSError:
                pass
        return self.payload(request_id)


TURNS = TurnRegistry()


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


def codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME", "").strip()
    if configured:
        return Path(configured).expanduser()
    user_profile = os.environ.get("USERPROFILE", "").strip()
    return Path(user_profile) / ".codex" if user_profile else Path.home() / ".codex"


def installed_codex_binaries() -> list[Path]:
    candidates: list[Path] = []
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
        if local_app_data:
            install_root = Path(local_app_data) / "OpenAI" / "Codex" / "bin"
            if install_root.is_dir():
                candidates.extend(
                    sorted(
                        install_root.glob("*/codex.exe"),
                        key=lambda item: item.stat().st_mtime,
                        reverse=True,
                    )
                )
                candidates.append(install_root / "codex.exe")
    for command in (("codex.exe", "codex") if os.name == "nt" else ("codex",)):
        discovered = shutil.which(command)
        if discovered:
            candidates.append(Path(discovered))

    unique: list[Path] = []
    seen: set[Path] = set()
    for candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
        except OSError:
            continue
        if resolved.is_file() and resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    return unique


def resolve_codex_binary(config: CodexCliConfig = CONFIG) -> Path | None:
    override = os.environ.get(config.binary_env, "").strip()
    if override:
        candidate = Path(override).expanduser().resolve()
        return candidate if candidate.is_file() else None
    installed = installed_codex_binaries()
    if installed:
        return installed[0]
    root = ROOT.resolve()
    candidate = (root / project_binary_relative_path(config)).resolve()
    return candidate if candidate.is_file() else None


def safe_child_environment() -> dict[str, str]:
    """Keep Codex login storage, but never expose API-key env vars to its shell tools."""
    environment = os.environ.copy()
    environment["CODEX_HOME"] = str(codex_home())
    for key in (
        "OPENAI_API_KEY",
        "CODEX_API_KEY",
        "CODEX_ACCESS_TOKEN",
        "MOSIM_OPENAI_API_KEY",
    ):
        environment.pop(key, None)
    return environment


def _toml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def codex_connection_overrides() -> list[str]:
    """Load only non-secret provider routing from the local Codex config."""
    config_path = codex_home() / "config.toml"
    try:
        with config_path.open("rb") as handle:
            document = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError):
        return []

    provider_name = str(document.get("model_provider", "")).strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", provider_name):
        return []
    providers = document.get("model_providers", {})
    provider = providers.get(provider_name, {}) if isinstance(providers, dict) else {}
    if not isinstance(provider, dict):
        return []

    overrides = [f"model_provider={_toml_string(provider_name)}"]
    for field in ("name", "base_url", "wire_api"):
        value = provider.get(field)
        if isinstance(value, str) and value.strip():
            overrides.append(
                f"model_providers.{provider_name}.{field}={_toml_string(value.strip())}"
            )
    requires_auth = provider.get("requires_openai_auth")
    if isinstance(requires_auth, bool):
        overrides.append(
            f"model_providers.{provider_name}.requires_openai_auth={str(requires_auth).lower()}"
        )
    return overrides


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


def _validate_model(model: str) -> str:
    value = model.strip()
    if not value:
        return ""
    if len(value) > 100 or not re.fullmatch(r"[A-Za-z0-9._:-]+", value):
        raise ValueError("invalid_model")
    return value


def _resolve_attachments(attachments: list[str] | None) -> tuple[list[Path], list[str]]:
    resolved: list[Path] = []
    project_files: list[str] = []
    allowed_images = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    allowed_text = {".csv", ".json", ".md", ".mo", ".toml", ".txt"}
    for raw in (attachments or [])[:4]:
        value = str(raw).strip()
        if not value:
            continue
        candidate = (ROOT / value).resolve()
        try:
            relative = candidate.relative_to(ROOT.resolve()).as_posix()
        except ValueError as exc:
            raise ValueError("attachment_outside_project") from exc
        if not candidate.is_file():
            raise ValueError("attachment_not_found")
        if candidate.stat().st_size > 8 * 1024 * 1024:
            raise ValueError("attachment_too_large")
        suffix = candidate.suffix.lower()
        if suffix not in allowed_images and suffix not in allowed_text:
            raise ValueError("attachment_type_not_allowed")
        resolved.append(candidate)
        project_files.append(relative)
    return resolved, project_files


def build_command(
    binary: Path,
    prompt: str,
    config: CodexCliConfig = CONFIG,
    model: str = "",
    attachments: list[Path] | None = None,
) -> list[str]:
    command = [
        str(binary),
        "exec",
        "--json",
        "--ignore-user-config",
        "--sandbox",
        config.sandbox,
        "--config",
        f'approval_policy="{config.approval_policy}"',
        "--cd",
        str(ROOT),
    ]
    for override in codex_connection_overrides():
        command.extend(["--config", override])
    selected_model = _validate_model(model)
    active_model = selected_model or os.environ.get("MOSIM_CODEX_MODEL", DEFAULT_AGENT_MODEL).strip()
    if active_model:
        command.extend(["--model", _validate_model(active_model)])
    for attachment in attachments or []:
        if attachment.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            command.extend(["--image", str(attachment)])
    command.append(prompt)
    return command


def build_resume_command(
    binary: Path,
    codex_thread_id: str,
    prompt: str,
    config: CodexCliConfig = CONFIG,
    model: str = "",
    attachments: list[Path] | None = None,
) -> list[str]:
    """Resume one persisted Codex CLI thread without loading user MCP/plugins."""
    if not re.fullmatch(r"[A-Za-z0-9_-]{8,160}", codex_thread_id):
        raise ValueError("invalid_codex_thread_id")
    command = [
        str(binary),
        "exec",
        "resume",
        "--json",
        "--ignore-user-config",
        "--config",
        f'approval_policy="{config.approval_policy}"',
    ]
    for override in codex_connection_overrides():
        command.extend(["--config", override])
    selected_model = _validate_model(model)
    active_model = selected_model or os.environ.get("MOSIM_CODEX_MODEL", DEFAULT_AGENT_MODEL).strip()
    if active_model:
        command.extend(["--model", _validate_model(active_model)])
    for attachment in attachments or []:
        if attachment.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
            command.extend(["--image", str(attachment)])
    command.extend([codex_thread_id, prompt])
    return command


def _add_activity(record: TurnRecord, value: str) -> None:
    """Keep only public lifecycle labels; never surface prompts, commands, or reasoning."""
    if value and (not record.activities or record.activities[-1] != value):
        record.activities.append(value)
        del record.activities[:-16]


def _append_diagnostic(record: TurnRecord, value: str) -> None:
    if value:
        record.diagnostics.append(value[-400:])
        del record.diagnostics[:-8]


def _event_error(event: dict[str, Any]) -> str:
    detail = event.get("error", event.get("message", ""))
    if isinstance(detail, dict):
        return str(detail.get("message", detail.get("code", "turn_failed")))
    return str(detail or "turn_failed")


def _record_stream_event(record: TurnRecord, event: dict[str, Any]) -> None:
    event_type = str(event.get("type", ""))
    if event_type == "thread.started":
        thread_id = event.get("thread_id", "")
        if isinstance(thread_id, str) and re.fullmatch(r"[A-Za-z0-9_-]{8,160}", thread_id):
            record.codex_thread_id = thread_id
            _add_activity(record, "已建立可续接会话")
        return
    if event_type == "turn.started":
        _add_activity(record, "开始只读分析")
        return
    if event_type == "turn.completed":
        _add_activity(record, "分析完成")
        return
    if event_type in {"turn.failed", "error"}:
        record.error = _event_error(event)
        _add_activity(record, "服务返回错误")
        return

    item = event.get("item", {})
    if not isinstance(item, dict):
        return
    item_type = str(item.get("type", ""))
    if item_type == "command_execution":
        _add_activity(record, "只读项目检索")
    elif item_type in {"file_search", "mcp_tool_call", "function_call"}:
        _add_activity(record, "只读工具调用")
    elif item_type in {"agent_message", "agentMessage"}:
        text = item.get("text", "")
        if isinstance(text, str) and text.strip():
            record.answer = text.strip()
            record.partial_answer = record.answer
            _add_activity(record, "已生成回答")

    # Current and older Codex CLI JSONL variants use different names for deltas.
    delta = event.get("delta", item.get("delta", ""))
    if isinstance(delta, str) and delta:
        record.partial_answer = (record.partial_answer + delta)[-6000:]
        _add_activity(record, "正在生成回答")


def parse_event_stream(output: str) -> tuple[str, str]:
    answer, error, _ = parse_event_stream_details(output)
    return answer, error


def parse_event_stream_details(output: str) -> tuple[str, str, list[str]]:
    record = TurnRecord(request_id="parse")
    for line in output.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            _record_stream_event(record, event)
    return record.answer, record.error, record.activities


def command_failure_code(diagnostics: list[str]) -> str:
    diagnostic = "\n".join(diagnostics).lower()
    if any(token in diagnostic for token in ("login", "auth", "api key", "credential", "unauthorized")):
        return "codex_auth_required"
    return "codex_cli_failed"


def turn_payload(record: TurnRecord) -> dict[str, Any]:
    terminal = record.status in {"completed", "failed", "cancelled"}
    return {
        "ok": record.status in {"queued", "running", "completed"},
        "request_id": record.request_id,
        "codex_thread_id": record.codex_thread_id,
        "status": record.status,
        "terminal": terminal,
        "answer": record.answer,
        "partial_answer": record.partial_answer,
        "error_code": record.error_code,
        "error": record.error,
        "activities": list(record.activities),
        "tools_used": ["Codex CLI（只读会话）"] + list(record.activities),
    }


def _fail_turn(record: TurnRecord, code: str, message: str) -> dict[str, Any]:
    record.status = "failed"
    record.error_code = code
    record.error = message
    record.answer = message
    record.finished_at = time.monotonic()
    _add_activity(record, "本轮分析未完成")
    TURNS.create(record)
    return turn_payload(record)


def _turn_prompt(question: str, context_text: str, attachment_names: list[str], config: CodexCliConfig, resume: bool) -> str:
    context = context_text.strip()[: config.max_context_chars] or "未提供当前 Studio 上下文。"
    attachment_text = "\n项目内附件：\n" + "\n".join(attachment_names) if attachment_names else ""
    if not resume:
        return build_prompt(question, context + attachment_text, config)
    return (
        "当前 Studio 配置更新（以此为准）：\n"
        + context
        + attachment_text
        + "\n\n用户本轮问题：\n"
        + question.strip()
    )


def _timeout_turn(request_id: str) -> None:
    with TURNS._lock:
        record = TURNS._records.get(request_id)
        if record is None or record.status in {"completed", "failed", "cancelled"}:
            return
        record.status = "failed"
        record.error_code = "codex_timeout"
        record.error = "Codex CLI 响应超时，请缩小问题范围后重试。"
        record.answer = record.error
        record.finished_at = time.monotonic()
        _add_activity(record, "本轮分析超时")
        process = record.process
    if process is not None:
        try:
            process.terminate()
        except OSError:
            pass


def _run_turn(record: TurnRecord, command: list[str], config: CodexCliConfig) -> None:
    timer: threading.Timer | None = None
    try:
        process = subprocess.Popen(
            command,
            cwd=ROOT,
            env=safe_child_environment(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )
    except OSError:
        with TURNS._lock:
            if record.status != "cancelled":
                record.status = "failed"
                record.error_code = "codex_cli_unavailable"
                record.error = "项目 Codex CLI 无法启动，请重新构建并验证 --version。"
                record.answer = record.error
                record.finished_at = time.monotonic()
                _add_activity(record, "Codex CLI 无法启动")
        return

    with TURNS._lock:
        record.process = process
        if record.status != "cancelled":
            record.status = "running"
            _add_activity(record, "已启动本机 Codex CLI")
    timer = threading.Timer(config.request_timeout_s, _timeout_turn, args=(record.request_id,))
    timer.daemon = True
    timer.start()

    try:
        assert process.stdout is not None
        for line in process.stdout:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                event = json.loads(stripped)
            except json.JSONDecodeError:
                with TURNS._lock:
                    _append_diagnostic(record, stripped)
                continue
            if isinstance(event, dict):
                with TURNS._lock:
                    _record_stream_event(record, event)
        return_code = process.wait()
    finally:
        if timer is not None:
            timer.cancel()

    with TURNS._lock:
        record.process = None
        if record.status == "cancelled":
            return
        if record.status == "failed":
            return
        if record.error:
            record.status = "failed"
            record.error_code = record.error_code or "codex_stream_error"
            record.answer = "Codex CLI 返回错误，请检查本机登录与 Provider 配置。"
            record.finished_at = time.monotonic()
            _add_activity(record, "本轮分析未完成")
            return
        if return_code != 0:
            record.status = "failed"
            record.error_code = command_failure_code(record.diagnostics)
            record.error = (
                "Codex 尚未完成 GPT 登录或 Provider 配置。"
                if record.error_code == "codex_auth_required"
                else "Codex CLI 请求失败，请检查本机 Codex 登录与配置。"
            )
            record.answer = record.error
            record.finished_at = time.monotonic()
            _add_activity(record, "本轮分析未完成")
            LOGGER.warning("request=%s status=%s", record.request_id, record.error_code)
            return
        if not record.answer and record.partial_answer:
            record.answer = record.partial_answer
        if not record.answer:
            record.status = "failed"
            record.error_code = "codex_empty_response"
            record.error = "Codex 未返回可显示的回答，请检查本机登录状态后重试。"
            record.answer = record.error
            record.finished_at = time.monotonic()
            _add_activity(record, "本轮分析未完成")
            LOGGER.warning("request=%s status=empty_response", record.request_id)
            return
        record.answer = record.answer[: config.max_answer_chars]
        record.partial_answer = record.partial_answer[: config.max_answer_chars]
        record.status = "completed"
        record.finished_at = time.monotonic()
        _add_activity(record, "分析完成")
        LOGGER.info("request=%s status=ok", record.request_id)


def start_turn(
    question: str,
    context_text: str = "",
    config: CodexCliConfig = CONFIG,
    model: str = "",
    attachments: list[str] | None = None,
    codex_thread_id: str = "",
) -> dict[str, Any]:
    record = TurnRecord(request_id=uuid.uuid4().hex[:12])
    if not isinstance(question, str) or not question.strip():
        return _fail_turn(record, "empty_question", "请先输入一个问题。")
    if len(question) > config.max_question_chars:
        return _fail_turn(record, "question_too_long", f"问题超过 {config.max_question_chars} 个字符，请缩短后重试。")
    try:
        selected_model = _validate_model(model)
        resolved_attachments, attachment_names = _resolve_attachments(attachments)
    except ValueError as exc:
        return _fail_turn(record, str(exc), "附件或模型参数不符合只读助手的安全限制。")
    binary = resolve_codex_binary(config)
    if binary is None:
        return _fail_turn(record, "codex_not_built", "未检测到 Codex CLI。请按发布清单安装或构建后重试。")

    thread_id = codex_thread_id.strip()
    try:
        if thread_id:
            record.codex_thread_id = thread_id
            command = build_resume_command(
                binary,
                thread_id,
                _turn_prompt(question, context_text, attachment_names, config, resume=True),
                config,
                selected_model,
                resolved_attachments,
            )
            _add_activity(record, "正在恢复上一轮会话")
        else:
            command = build_command(
                binary,
                _turn_prompt(question, context_text, attachment_names, config, resume=False),
                config,
                selected_model,
                resolved_attachments,
            )
            _add_activity(record, "正在创建新会话")
    except ValueError as exc:
        return _fail_turn(record, str(exc), "Codex 会话或模型参数无效，请新建对话后重试。")

    TURNS.create(record)
    threading.Thread(target=_run_turn, args=(record, command, config), daemon=True).start()
    return turn_payload(record)


def query_agent(
    question: str,
    context_text: str = "",
    config: CodexCliConfig = CONFIG,
    model: str = "",
    attachments: list[str] | None = None,
) -> dict[str, Any]:
    """Compatibility endpoint for callers that still require one synchronous answer."""
    started = start_turn(question, context_text, config, model, attachments)
    request_id = str(started.get("request_id", ""))
    deadline = time.monotonic() + config.request_timeout_s + 2.0
    while request_id and time.monotonic() < deadline:
        payload = TURNS.payload(request_id)
        if payload is not None and payload["terminal"]:
            return payload
        time.sleep(0.08)
    return TURNS.cancel(request_id) or started


class AgentRequestHandler(BaseHTTPRequestHandler):
    server_version = "MoSimCodexCli/2.0"

    def _send_json(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "http://127.0.0.1")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _read_payload(self) -> dict[str, Any] | None:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 32_000:
                raise ValueError("invalid_content_length")
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
            return payload if isinstance(payload, dict) else None
        except (ValueError, json.JSONDecodeError):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "invalid_json_request"})
            return None

    def _turn_id_from_path(self, suffix: str = "") -> str:
        path = urlparse(self.path).path
        prefix = "/mworks/turns/"
        if not path.startswith(prefix):
            return ""
        tail = path[len(prefix) :]
        if suffix:
            if not tail.endswith(suffix):
                return ""
            tail = tail[: -len(suffix)]
        return tail if re.fullmatch(r"[A-Za-z0-9]{8,160}", tail) else ""

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            self._send_json(HTTPStatus.OK, health_payload())
            return
        request_id = self._turn_id_from_path()
        if request_id:
            payload = TURNS.payload(request_id)
            if payload is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "turn_not_found"})
            else:
                self._send_json(HTTPStatus.OK, payload)
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/mworks/turns":
            payload = self._read_payload()
            if payload is None:
                return
            self._send_json(
                HTTPStatus.ACCEPTED,
                start_turn(
                    str(payload.get("question", "")),
                    str(payload.get("context_text", "")),
                    model=str(payload.get("model", "")),
                    attachments=payload.get("attachments", []),
                    codex_thread_id=str(payload.get("codex_thread_id", "")),
                ),
            )
            return
        request_id = self._turn_id_from_path("/cancel")
        if request_id:
            payload = TURNS.cancel(request_id)
            if payload is None:
                self._send_json(HTTPStatus.NOT_FOUND, {"error": "turn_not_found"})
            else:
                self._send_json(HTTPStatus.OK, payload)
            return
        if path == "/mworks/query":
            payload = self._read_payload()
            if payload is None:
                return
            self._send_json(
                HTTPStatus.OK,
                query_agent(
                    str(payload.get("question", "")),
                    str(payload.get("context_text", "")),
                    model=str(payload.get("model", "")),
                    attachments=payload.get("attachments", []),
                ),
            )
            return
        self._send_json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

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
