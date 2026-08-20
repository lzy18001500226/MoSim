"""Regression checks for native Codex delegation transport parsing."""

from __future__ import annotations

from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "Scripts" / "hooks" / "authorization_guard.py"


def load_module():
    spec = importlib.util.spec_from_file_location("mosim_authorization_guard", MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_delegation_transport_is_metadata_and_nested_input_is_extractable() -> None:
    module = load_module()

    prompt = (
        "<codex_delegation>\n"
        "<source_thread_id>019e9bc1-ea9f-7102-b41a-4ef9b2308992</source_thread_id>\n"
        "<input>继续执行当前消息并报告结果。</input>\n"
        "</codex_delegation>"
    )
    assert module.is_delegation_context(prompt)
    assert module.delegated_task_input(prompt) == "继续执行当前消息并报告结果。"


def test_delegation_parser_accepts_extra_wrapper_text_and_prompt_tag() -> None:
    module = load_module()

    prompt = (
        "前置内部字段\n"
        "<codex_delegation source=internal>"
        "<source_thread_id>019e9bc1-ea9f-7102-b41a-4ef9b2308992</source_thread_id>"
        "<prompt>正常转发消息。</prompt>"
        "</codex_delegation>"
        "后置字段"
    )
    assert module.delegated_task_input(prompt) == "正常转发消息。"


def test_delegation_parser_drops_source_metadata_when_input_tag_is_absent() -> None:
    module = load_module()

    prompt = (
        "<codex_delegation>"
        "<source_thread_id>019e9bc1-ea9f-7102-b41a-4ef9b2308992</source_thread_id>"
        "继续执行当前消息。"
        "</codex_delegation>"
    )
    assert module.delegated_task_input(prompt) == "继续执行当前消息。"
