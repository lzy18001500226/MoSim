"""Regression checks for generic non-MoSim Codex compact recovery."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "Scripts" / "hooks" / "codex_native_hook.py"


def _run_hook(payload: dict[str, object], codex_home: Path) -> dict[str, object]:
    environment = dict(os.environ)
    environment["CODEX_HOME"] = str(codex_home)
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        cwd=ROOT,
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
        check=False,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout) if result.stdout.strip() else {}


def _payload(event: str, session_id: str, turn_id: str, **extra: object) -> dict[str, object]:
    return {
        "cwd": r"C:\Users\HP\Desktop\OtherProject",
        "hook_event_name": event,
        "session_id": session_id,
        "turn_id": turn_id,
        **extra,
    }


def test_non_mosim_prompt_survives_compaction_once() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        codex_home = Path(temporary)
        prompt = "修复当前文档并验证，不要切换任务。"
        _run_hook(_payload("UserPromptSubmit", "global-session", "direct-turn", prompt=prompt), codex_home)
        _run_hook(_payload("PreCompact", "global-session", "execution-turn", trigger="auto"), codex_home)

        recovered = _run_hook(
            _payload("SessionStart", "global-session", "execution-turn", source="compact"), codex_home
        )
        context = recovered["hookSpecificOutput"]["additionalContext"]
        assert prompt in context
        assert _run_hook(
            _payload("SessionStart", "global-session", "execution-turn", source="compact"), codex_home
        ) == {}


def test_non_mosim_prompt_survives_clear_and_resume_once() -> None:
    for source in ("clear", "resume"):
        with tempfile.TemporaryDirectory() as temporary:
            codex_home = Path(temporary)
            prompt = f"{source} 后继续当前任务。"
            _run_hook(_payload("UserPromptSubmit", f"global-{source}", "direct-turn", prompt=prompt), codex_home)

            recovered = _run_hook(
                _payload("SessionStart", f"global-{source}", "reset-turn", source=source), codex_home
            )
            context = recovered["hookSpecificOutput"]["additionalContext"]
            assert f"session {source}" in context
            assert prompt in context
            assert _run_hook(
                _payload("SessionStart", f"global-{source}", "reset-turn", source=source), codex_home
            ) == {}


def test_non_mosim_generated_goal_and_abort_envelopes_are_not_captured() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        codex_home = Path(temporary)
        _run_hook(
            _payload(
                "UserPromptSubmit",
                "global-generated-session",
                "goal-turn",
                prompt='<codex_internal_context source="goal">resume</codex_internal_context>',
            ),
            codex_home,
        )
        _run_hook(
            _payload(
                "UserPromptSubmit",
                "global-generated-session",
                "abort-turn",
                prompt="<turn_aborted>interrupted</turn_aborted>",
            ),
            codex_home,
        )
        _run_hook(_payload("PreCompact", "global-generated-session", "execution-turn", trigger="auto"), codex_home)

        recovered = _run_hook(
            _payload("SessionStart", "global-generated-session", "execution-turn", source="compact"), codex_home
        )
        context = recovered["hookSpecificOutput"]["additionalContext"]
        assert "No captured direct user request" in context


def test_non_mosim_prompt_redacts_sensitive_values_before_persisting_or_recovery() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        codex_home = Path(temporary)
        session_id = "global-redaction-session"
        secrets = (
            "access-token-value",
            "password-value",
            "credential-value",
            "api-key-value",
            "authorization-value",
        )
        prompt = (
            "检查 https://example.invalid/report?access_token=access-token-value "
            "password=password-value credential=credential-value api_key=api-key-value "
            "Authorization: Bearer authorization-value"
        )

        _run_hook(_payload("UserPromptSubmit", session_id, "direct-turn", prompt=prompt), codex_home)
        stored = next((codex_home / "continuity_packs" / "global").glob("*.json")).read_text(encoding="utf-8")
        assert all(secret not in stored for secret in secrets)
        assert "[REDACTED]" in stored

        _run_hook(_payload("PreCompact", session_id, "execution-turn", trigger="auto"), codex_home)
        recovered = _run_hook(
            _payload("SessionStart", session_id, "execution-turn", source="compact"), codex_home
        )
        context = recovered["hookSpecificOutput"]["additionalContext"]
        assert all(secret not in context for secret in secrets)
        assert "[REDACTED]" in context


def test_non_mosim_recovery_context_is_bounded_and_preserves_prompt_ends() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        codex_home = Path(temporary)
        prompt = "head-sentinel " + ("middle-content " * 300) + "tail-sentinel"
        _run_hook(_payload("UserPromptSubmit", "global-bounded-session", "direct-turn", prompt=prompt), codex_home)
        _run_hook(_payload("PreCompact", "global-bounded-session", "execution-turn", trigger="auto"), codex_home)

        recovered = _run_hook(
            _payload("SessionStart", "global-bounded-session", "execution-turn", source="compact"), codex_home
        )
        context = recovered["hookSpecificOutput"]["additionalContext"]
        assert "head-sentinel" in context
        assert "tail-sentinel" in context
        assert "[...truncated for bounded recovery...]" in context
        assert len(context) <= 2_300


def test_non_mosim_project_context_preserves_the_prior_direct_prompt() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        codex_home = Path(temporary)
        session_id = "global-project-context-session"
        direct_prompt = "继续修复当前文档，不要切换任务。"
        project_prompt = (
            "# AGENTS.md instructions for C:\\Users\\HP\\Desktop\\OtherProject\n\n"
            "<INSTRUCTIONS>\nProject guidance.\n</INSTRUCTIONS>"
        )
        _run_hook(_payload("UserPromptSubmit", session_id, "direct-turn", prompt=direct_prompt), codex_home)
        project = _run_hook(
            _payload("UserPromptSubmit", session_id, "project-turn", prompt=project_prompt), codex_home
        )
        assert project["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
        project_context = project["hookSpecificOutput"]["additionalContext"]
        assert "not a direct user request" in project_context
        assert direct_prompt in project_context

        _run_hook(_payload("PreCompact", session_id, "execution-turn"), codex_home)
        recovered = _run_hook(
            _payload("SessionStart", session_id, "execution-turn", source="compact"), codex_home
        )
        context = recovered["hookSpecificOutput"]["additionalContext"]
        assert direct_prompt in context
        assert project_prompt not in context


def test_non_mosim_structured_prompt_and_thread_identity_survive_compaction() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        codex_home = Path(temporary)
        attachment = r"C:\Users\HP\Desktop\OtherProject\brief.md"
        prompt = "修复当前解析器并保留附件身份。"
        submitted = {
            "cwd": r"C:\Users\HP\Desktop\OtherProject",
            "hook_event_name": "UserPromptSubmit",
            "threadId": "global-structured-session",
            "turnId": "global-structured-turn",
            "input": [
                {"type": "input_text", "text": prompt},
                {"type": "localFile", "path": attachment},
            ],
        }
        _run_hook(submitted, codex_home)
        _run_hook(
            {
                "cwd": r"C:\Users\HP\Desktop\OtherProject",
                "hook_event_name": "PreCompact",
                "threadId": "global-structured-session",
                "turnId": "execution-turn",
            },
            codex_home,
        )
        recovered = _run_hook(
            {
                "cwd": r"C:\Users\HP\Desktop\OtherProject",
                "hook_event_name": "SessionStart",
                "threadId": "global-structured-session",
                "source": "compact",
            },
            codex_home,
        )
        context = recovered["hookSpecificOutput"]["additionalContext"]
        assert prompt in context
        assert attachment in context


def test_non_mosim_newer_prompt_suppresses_stale_compact_injection() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        codex_home = Path(temporary)
        _run_hook(
            _payload("UserPromptSubmit", "global-race-session", "old-turn", prompt="处理旧任务。"),
            codex_home,
        )
        _run_hook(_payload("PreCompact", "global-race-session", "execution-turn"), codex_home)
        _run_hook(
            _payload("UserPromptSubmit", "global-race-session", "new-turn", prompt="处理新的直接任务。"),
            codex_home,
        )

        assert _run_hook(
            _payload("SessionStart", "global-race-session", "execution-turn", source="compact"),
            codex_home,
        ) == {}


def test_non_mosim_concurrent_compact_starts_inject_once() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        codex_home = Path(temporary)
        payload = _payload("SessionStart", "global-concurrent-session", "execution-turn", source="compact")
        _run_hook(
            _payload("UserPromptSubmit", "global-concurrent-session", "direct-turn", prompt="继续当前任务。"),
            codex_home,
        )
        _run_hook(_payload("PreCompact", "global-concurrent-session", "execution-turn"), codex_home)

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: _run_hook(payload, codex_home), range(2)))

        assert sum("hookSpecificOutput" in result for result in results) == 1
        assert not list((codex_home / "continuity_packs" / "global").rglob("*.tmp"))
