#!/usr/bin/env python3
"""Regression checks for bounded MoSim Codex compaction recovery."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "Scripts" / "hooks" / "codex_native_hook.py"


def _run_hook(
    payload: dict[str, object], context_root: Path, *, environment_overrides: dict[str, str] | None = None
) -> dict[str, object]:
    environment = dict(os.environ)
    environment["MOSIM_CONTEXT_PACK_ROOT"] = str(context_root)
    environment["MOSIM_TASK_NOTIFICATION_ROOT"] = str(context_root / "terminal_emails")
    environment["MOSIM_EMAIL_ALERT_ROOT"] = str(context_root / "email_audits")
    environment["MOSIM_TASK_NOTIFICATION_DRY_RUN"] = "1"
    if environment_overrides:
        environment.update(environment_overrides)
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


def _run_hook_utf8_bytes(payload: dict[str, object], context_root: Path) -> bytes:
    environment = dict(os.environ)
    environment["MOSIM_CONTEXT_PACK_ROOT"] = str(context_root)
    environment["MOSIM_TASK_NOTIFICATION_ROOT"] = str(context_root / "terminal_emails")
    environment["MOSIM_EMAIL_ALERT_ROOT"] = str(context_root / "email_audits")
    environment["MOSIM_TASK_NOTIFICATION_DRY_RUN"] = "1"
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        cwd=ROOT,
        input=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=environment,
        check=False,
        timeout=20,
    )
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    return result.stdout


def _payload(event: str, session_id: str, turn_id: str, **extra: object) -> dict[str, object]:
    return {
        "cwd": str(ROOT),
        "hook_event_name": event,
        "session_id": session_id,
        "turn_id": turn_id,
        **extra,
    }


def _write_transcript(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )


def test_project_does_not_register_duplicate_hooks() -> None:
    assert not (ROOT / ".codex" / "hooks.json").exists()


def test_hook_transport_preserves_utf8_input_and_output() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-utf8-transport"
        turn_id = "turn-utf8-transport"
        prompt = "同意\n"

        submitted = _run_hook_utf8_bytes(
            _payload("UserPromptSubmit", session_id, turn_id, prompt=prompt),
            context_root,
        )
        assert json.loads(submitted.decode("utf-8"))["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
        record = json.loads(
            (context_root / session_id / "turns" / f"{turn_id}.json").read_text(encoding="utf-8")
        )
        assert record["user_prompt"] == prompt

        _run_hook_utf8_bytes(_payload("PreCompact", session_id, turn_id, trigger="auto"), context_root)
        recovered = _run_hook_utf8_bytes(
            _payload("SessionStart", session_id, turn_id, source="compact"),
            context_root,
        )
        context = json.loads(recovered.decode("utf-8"))["hookSpecificOutput"]["additionalContext"]
        assert prompt.strip() in context


def test_missing_compact_pack_remains_unresolved_without_a_stop_continuation() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-missing-compact-pack"
        turn_id = "turn-missing-pack"

        session_start = _payload("SessionStart", session_id, turn_id, source="compact")
        del session_start["turn_id"]
        started = _run_hook(session_start, context_root)
        context = started["hookSpecificOutput"]["additionalContext"]
        assert "No bounded task recovery pack or recognized transcript_path user message was available" in context
        assert "codex_app__read_thread" in context
        assert "Before asking the user for a missing source or marking the task blocked" in context
        assert not list((context_root / session_id / "continuation_guards").glob("*.pending.json"))

        assert _run_hook(_payload("Stop", session_id, "turn-after-compact"), context_root) == {}
        assert _run_hook(_payload("Stop", session_id, turn_id), context_root) == {}


def test_stop_never_generates_a_synthetic_user_prompt() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-native-stop-flag"

        _run_hook(_payload("SessionStart", session_id, "turn-compact", source="compact"), context_root)

        already_continued = _run_hook(
            _payload("Stop", session_id, "turn-after-compact", stop_hook_active=True),
            context_root,
        )
        assert already_continued == {}

        no_continuation = _run_hook(
            _payload("Stop", session_id, "turn-after-compact", stop_hook_active=False),
            context_root,
        )
        assert no_continuation == {}


def test_transcript_fallback_recovers_only_the_latest_direct_user_message() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary) / "context"
        transcript = Path(temporary) / "rollout.jsonl"
        session_id = "session-transcript-fallback"
        previous_turn = "turn-previous"
        compacted_turn = "turn-current"
        current_prompt = "修复当前恢复路径 https://example.test/current"
        attachment = r"C:\Users\HP\Desktop\MoSim\Results\current.png"

        _run_hook(
            _payload("UserPromptSubmit", session_id, previous_turn, prompt="关闭旧窗口。"),
            context_root,
        )
        _run_hook(
            _payload(
                "PostToolUse",
                session_id,
                previous_turn,
                tool_name="create_goal",
                tool_input={"objective": "关闭旧窗口。"},
                tool_response={"goal": {"objective": "关闭旧窗口。", "status": "active"}},
            ),
            context_root,
        )
        _run_hook(_payload("PreCompact", session_id, compacted_turn, trigger="auto"), context_root)
        _write_transcript(
            transcript,
            [
                {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": current_prompt},
                            {"type": "localImage", "path": attachment},
                        ],
                    },
                },
                {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": "working"}],
                    },
                },
            ],
        )

        session_start = _payload(
            "SessionStart",
            session_id,
            compacted_turn,
            source="compact",
            transcript_path=str(transcript),
        )
        del session_start["turn_id"]
        started = _run_hook(session_start, context_root)
        context = started["hookSpecificOutput"]["additionalContext"]
        active = json.loads((context_root / session_id / "active.json").read_text(encoding="utf-8"))
        record = json.loads(
            (context_root / session_id / "turns" / f"{compacted_turn}.json").read_text(encoding="utf-8")
        )

        assert "transcript_path after UserPromptSubmit capture was unavailable" in context
        assert current_prompt in context
        assert attachment in context
        assert "关闭旧窗口。" not in context
        assert record["capture_source"] == "transcript_path_fallback"
        assert active["active_turn_id"] == compacted_turn
        assert _run_hook(_payload("Stop", session_id, "turn-after-compact"), context_root) == {}


def test_execution_turn_preserves_the_latest_captured_direct_record() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-distinct-turns"
        direct_turn = "user-turn"
        execution_turn = "assistant-execution-turn"
        prompt = "继续完成当前 MWORKS 回归，不要中断任务。"

        _run_hook(
            _payload("UserPromptSubmit", session_id, direct_turn, prompt=prompt),
            context_root,
        )
        _run_hook(
            _payload("PreCompact", session_id, execution_turn, trigger="auto"),
            context_root,
        )
        recovered = _run_hook(
            _payload("SessionStart", session_id, execution_turn, source="compact"),
            context_root,
        )
        context = recovered["hookSpecificOutput"]["additionalContext"]
        active = json.loads((context_root / session_id / "active.json").read_text(encoding="utf-8"))

        assert "[MoSim Task Recovery Pack]" in context
        assert prompt in context
        assert active["active_turn_id"] == direct_turn
        assert active["last_compaction"]["turn_id"] == execution_turn
        assert active["last_compaction"]["direct_turn_id"] == direct_turn
        assert active["last_compaction"]["recovery_source"] == "latest_direct_record"
        assert active["last_compaction"]["current_turn_capture_missing"] is False


def test_legacy_execution_turn_pointer_is_repaired_from_last_captured_record() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-legacy-execution-pointer"
        direct_turn = "legacy-user-turn"
        execution_turn = "legacy-assistant-turn"
        prompt = "继续处理当前 Word/MathType 文档，不要提前停止。"

        _run_hook(
            _payload("UserPromptSubmit", session_id, direct_turn, prompt=prompt),
            context_root,
        )
        active_path = context_root / session_id / "active.json"
        active = json.loads(active_path.read_text(encoding="utf-8"))
        active["active_turn_id"] = execution_turn
        active["last_compaction"] = {
            "compaction_id": "legacy-compaction",
            "stage": "pre",
            "turn_id": execution_turn,
            "current_turn_capture_missing": True,
            "trigger": "auto",
        }
        active_path.write_text(json.dumps(active, ensure_ascii=False) + "\n", encoding="utf-8")

        recovered = _run_hook(
            _payload("SessionStart", session_id, execution_turn, source="compact"),
            context_root,
        )
        context = recovered["hookSpecificOutput"]["additionalContext"]
        repaired = json.loads(active_path.read_text(encoding="utf-8"))

        assert "[MoSim Task Recovery Pack]" in context
        assert prompt in context
        assert repaired["active_turn_id"] == direct_turn
        assert repaired["last_compaction"]["direct_turn_id"] == direct_turn
        assert repaired["last_compaction"]["recovery_source"] == "legacy_latest_direct_record"
        assert repaired["last_compaction"]["current_turn_capture_missing"] is False


def test_prompt_capture_uses_thread_environment_and_generated_turn_id() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-environment-fallback"
        payload = _payload("UserPromptSubmit", "discarded-session", "discarded-turn")
        del payload["session_id"]
        del payload["turn_id"]
        payload["input"] = [{"type": "input_text", "text": "修复当前 hook 捕获。"}]

        captured = _run_hook(
            payload,
            context_root,
            environment_overrides={"CODEX_THREAD_ID": session_id},
        )
        active = json.loads((context_root / session_id / "active.json").read_text(encoding="utf-8"))

        assert captured["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
        assert active["session_id"] == session_id
        assert active["active_turn_id"].startswith("captured-")
        assert (context_root / session_id / "turns" / f"{active['active_turn_id']}.json").is_file()


def test_transcript_fallback_does_not_skip_a_stop_generated_user_message() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary) / "context"
        transcript = Path(temporary) / "rollout.jsonl"
        session_id = "session-transcript-internal"

        stop_reason = "Context continuity guard: legacy synthetic user prompt."
        digest = hashlib.sha256(stop_reason.encode("utf-8")).hexdigest()
        marker_dir = context_root / session_id / "internal_continuations"
        marker_dir.mkdir(parents=True)
        (marker_dir / f"{digest}.claimed").write_text("legacy\n", encoding="utf-8")
        _write_transcript(
            transcript,
            [
                {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": "旧的直接任务。"}],
                    },
                },
                {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": stop_reason}],
                    },
                },
            ],
        )

        started = _run_hook(
            _payload("SessionStart", session_id, "turn-next", source="compact", transcript_path=str(transcript)),
            context_root,
        )
        context = started["hookSpecificOutput"]["additionalContext"]
        assert "旧的直接任务。" not in context
        assert "No bounded task recovery pack" in context


def test_goal_continuation_envelope_does_not_replace_direct_user_input() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-goal-envelope-submit"
        direct_turn = "turn-direct"
        goal_turn = "turn-goal-envelope"
        execution_turn = "turn-execution"
        direct_prompt = "Repair the current hook without changing the task scope."
        goal_objective = "Never treat this Goal envelope as a user task."
        goal_prompt = (
            '<codex_internal_context source="goal">\n'
            "Continue working toward the active thread goal.\n"
            f"<objective>{goal_objective}</objective>\n"
            "</codex_internal_context>"
        )

        _run_hook(
            _payload("UserPromptSubmit", session_id, direct_turn, prompt=direct_prompt),
            context_root,
        )
        blocked = _run_hook(
            _payload("UserPromptSubmit", session_id, goal_turn, prompt=goal_prompt),
            context_root,
        )
        assert blocked["decision"] == "block"
        assert "Goal continuation envelope" in blocked["reason"]

        active = json.loads((context_root / session_id / "active.json").read_text(encoding="utf-8"))
        assert active["active_turn_id"] == direct_turn
        assert not (context_root / session_id / "turns" / f"{goal_turn}.json").exists()

        _run_hook(_payload("PreCompact", session_id, execution_turn, trigger="auto"), context_root)
        started = _run_hook(
            _payload("SessionStart", session_id, execution_turn, source="compact"),
            context_root,
        )
        context = started["hookSpecificOutput"]["additionalContext"]
        assert direct_prompt in context
        assert goal_objective not in context


def test_goal_continuation_transcript_and_legacy_record_remain_unresolved() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary) / "context"
        transcript = Path(temporary) / "rollout.jsonl"
        session_id = "session-goal-envelope-transcript"
        goal_turn = "turn-legacy-goal-envelope"
        execution_turn = "turn-execution"
        goal_objective = "A stale Goal objective must never select the current task."
        goal_prompt = (
            '<codex_internal_context source="goal">\n'
            "Continue working toward the active thread goal.\n"
            f"<objective>{goal_objective}</objective>\n"
            "</codex_internal_context>"
        )
        session_dir = context_root / session_id
        turns_dir = session_dir / "turns"
        turns_dir.mkdir(parents=True)
        (turns_dir / f"{goal_turn}.json").write_text(
            json.dumps(
                {
                    "kind": "mosim_direct_user_input",
                    "turn_id": goal_turn,
                    "user_prompt": goal_prompt,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        (session_dir / "active.json").write_text(
            json.dumps({"active_turn_id": goal_turn, "last_captured_turn_id": goal_turn}) + "\n",
            encoding="utf-8",
        )
        _run_hook(_payload("PreCompact", session_id, execution_turn, trigger="auto"), context_root)
        _write_transcript(
            transcript,
            [
                {
                    "type": "response_item",
                    "payload": {
                        "type": "message",
                        "role": "user",
                        "content": [{"type": "input_text", "text": goal_prompt}],
                    },
                }
            ],
        )

        started = _run_hook(
            _payload(
                "SessionStart",
                session_id,
                execution_turn,
                source="compact",
                transcript_path=str(transcript),
            ),
            context_root,
        )
        context = started["hookSpecificOutput"]["additionalContext"]
        active = json.loads((session_dir / "active.json").read_text(encoding="utf-8"))
        assert "direct user input for this compacted turn was not captured" in context
        assert goal_objective not in context
        assert active["last_compaction"]["current_turn_capture_missing"] is True
        assert not (turns_dir / f"{execution_turn}.json").exists()


def test_legacy_internal_continuation_marker_does_not_replace_direct_input_capture() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-internal-continuation"
        original_turn = "turn-original"

        _run_hook(
            _payload("UserPromptSubmit", session_id, original_turn, prompt="继续执行原始任务。"),
            context_root,
        )
        legacy_reason = "Context continuity guard: legacy synthetic user prompt."
        digest = hashlib.sha256(legacy_reason.encode("utf-8")).hexdigest()
        marker_dir = context_root / session_id / "internal_continuations"
        marker_dir.mkdir(parents=True)
        (marker_dir / f"{digest}.pending.json").write_text(
            json.dumps({"kind": "mosim_internal_continuation", "prompt_sha256": digest}) + "\n",
            encoding="utf-8",
        )

        internal_turn = "turn-internal-continuation"
        assert _run_hook(
            _payload("UserPromptSubmit", session_id, internal_turn, prompt=legacy_reason),
            context_root,
        ) == {}
        active = json.loads((context_root / session_id / "active.json").read_text(encoding="utf-8"))
        assert active["active_turn_id"] == original_turn
        assert not (context_root / session_id / "turns" / f"{internal_turn}.json").exists()


def test_new_direct_input_clears_pending_internal_continuation() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-direct-input-wins"

        marker_dir = context_root / session_id / "internal_continuations"
        legacy_reason = "Context continuity guard: legacy synthetic user prompt."
        digest = hashlib.sha256(legacy_reason.encode("utf-8")).hexdigest()
        marker_dir.mkdir(parents=True)
        (marker_dir / f"{digest}.pending.json").write_text("{}\n", encoding="utf-8")
        assert list(marker_dir.glob("*.pending.json"))

        direct_turn = "turn-direct-input"
        captured = _run_hook(
            _payload("UserPromptSubmit", session_id, direct_turn, prompt="用户的新任务优先。"),
            context_root,
        )
        assert captured["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
        active = json.loads((context_root / session_id / "active.json").read_text(encoding="utf-8"))
        assert active["active_turn_id"] == direct_turn
        assert not list(marker_dir.glob("*.pending.json"))

        # The old internal reason cannot be consumed after the direct input
        # has superseded its pending marker.
        late_internal = _run_hook(
            _payload("UserPromptSubmit", session_id, "turn-late-internal", prompt=legacy_reason),
            context_root,
        )
        assert late_internal["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
        assert (context_root / session_id / "turns" / "turn-late-internal.json").is_file()


def test_missing_direct_prompt_does_not_replay_an_active_same_session_goal() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-same-session-goal"
        first_turn = "turn-first-task"
        newer_turn = "turn-continuation"

        _run_hook(
            _payload("UserPromptSubmit", session_id, first_turn, prompt="完成任务 A。"),
            context_root,
        )
        _run_hook(
            _payload(
                "PostToolUse",
                session_id,
                first_turn,
                tool_name="create_goal",
                tool_input={"objective": "只恢复任务 A。"},
                tool_response={"goal": {"objective": "只恢复任务 A。", "status": "active"}},
            ),
            context_root,
        )
        _run_hook(
            _payload("UserPromptSubmit", session_id, newer_turn, prompt="继续完成任务 A。"),
            context_root,
        )
        (context_root / session_id / "turns" / f"{newer_turn}.json").unlink()
        _run_hook(_payload("PreCompact", session_id, newer_turn, trigger="auto"), context_root)

        started = _run_hook(
            _payload("SessionStart", session_id, newer_turn, source="compact"),
            context_root,
        )
        context = started["hookSpecificOutput"]["additionalContext"]
        assert "direct user input for this compacted turn was not captured" in context
        assert "[MoSim Goal Continuity Fallback]" not in context
        assert "只恢复任务 A。" not in context


def test_uncaptured_compaction_turn_does_not_replay_a_prior_prompt_or_goal() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-missing-current-capture"
        previous_turn = "turn-previous"
        compacted_turn = "turn-current"

        _run_hook(
            _payload("UserPromptSubmit", session_id, previous_turn, prompt="直接关闭旧窗口。"),
            context_root,
        )
        _run_hook(
            _payload(
                "PostToolUse",
                session_id,
                previous_turn,
                tool_name="create_goal",
                tool_input={"objective": "关闭旧窗口。"},
                tool_response={"goal": {"objective": "关闭旧窗口。", "status": "active"}},
            ),
            context_root,
        )

        # An explicit direct-user turn is authoritative. Its absent record must
        # not fall back to the previous direct input just because the execution
        # turn is different.
        execution_turn = "assistant-turn-current"
        _run_hook(
            _payload(
                "PreCompact",
                session_id,
                execution_turn,
                trigger="auto",
                direct_user_turn_id=compacted_turn,
            ),
            context_root,
        )
        started = _run_hook(
            _payload("SessionStart", session_id, execution_turn, source="compact"),
            context_root,
        )
        context = started["hookSpecificOutput"]["additionalContext"]
        active = json.loads((context_root / session_id / "active.json").read_text(encoding="utf-8"))

        assert "direct user input for this compacted turn was not captured" in context
        assert "关闭旧窗口。" not in context
        assert "[MoSim Goal Continuity Fallback]" not in context
        assert "codex_app__read_thread" in context
        assert active["active_turn_id"] == execution_turn
        assert active["last_compaction"]["direct_turn_id"] == ""
        assert active["last_compaction"]["current_turn_capture_missing"] is True


def test_turnless_compaction_does_not_replay_an_active_goal() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-turnless-compaction"
        prior_turn = "turn-prior"

        _run_hook(
            _payload("UserPromptSubmit", session_id, prior_turn, prompt="编辑旧 DOCX。"),
            context_root,
        )
        _run_hook(
            _payload(
                "PostToolUse",
                session_id,
                prior_turn,
                tool_name="create_goal",
                tool_input={"objective": "完成旧 DOCX 编辑。"},
                tool_response={"goal": {"objective": "完成旧 DOCX 编辑。", "status": "active"}},
            ),
            context_root,
        )
        (context_root / session_id / "turns" / f"{prior_turn}.json").unlink()

        precompact = _payload("PreCompact", session_id, "", trigger="auto")
        del precompact["turn_id"]
        _run_hook(precompact, context_root)
        started = _run_hook(
            _payload("SessionStart", session_id, "", source="compact"),
            context_root,
        )
        context = started["hookSpecificOutput"]["additionalContext"]
        active = json.loads((context_root / session_id / "active.json").read_text(encoding="utf-8"))

        assert "direct user input for this compacted turn was not captured" in context
        assert "[MoSim Goal Continuity Fallback]" not in context
        assert "完成旧 DOCX 编辑。" not in context
        assert not active["last_compaction"]["turn_id"]
        assert active["last_compaction"]["current_turn_capture_missing"] is True


def test_pretool_does_not_require_a_goal_for_an_ordinary_command() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        output = _run_hook(
            _payload(
                "PreToolUse",
                "session-no-goal-gate",
                "turn-no-goal-gate",
                tool_name="shell_command",
                tool_input={"command": "Get-ChildItem"},
            ),
            Path(temporary),
        )
        hook_output = output.get("hookSpecificOutput", {})
        assert hook_output.get("permissionDecision") != "deny"
        assert "Goal Gate" not in hook_output.get("permissionDecisionReason", "")


def test_pretool_rejects_an_unrequested_goal_token_budget() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-goal-budget-reject"
        turn_id = "turn-goal-budget-reject"
        _run_hook(
            _payload(
                "UserPromptSubmit",
                session_id,
                turn_id,
                prompt="请修复 Hook 的 Goal 生命周期问题并完成回归测试。",
            ),
            context_root,
        )

        output = _run_hook(
            _payload(
                "PreToolUse",
                session_id,
                turn_id,
                tool_name="create_goal",
                tool_input={"objective": "修复 Goal 生命周期。", "token_budget": 12000},
            ),
            context_root,
        )
        hook_output = output["hookSpecificOutput"]
        assert hook_output["permissionDecision"] == "deny"
        assert "Goal Budget Gate" in hook_output["permissionDecisionReason"]

        without_budget = _run_hook(
            _payload(
                "PreToolUse",
                session_id,
                turn_id,
                tool_name="create_goal",
                tool_input={"objective": "修复 Goal 生命周期。"},
            ),
            context_root,
        )
        assert without_budget.get("hookSpecificOutput", {}).get("permissionDecision") != "deny"


def test_pretool_allows_an_explicit_same_turn_goal_token_budget() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-goal-budget-allow"
        turn_id = "turn-goal-budget-allow"
        _run_hook(
            _payload(
                "UserPromptSubmit",
                session_id,
                turn_id,
                prompt="请为本任务设置 token_budget 为 12000，然后完成检查。",
            ),
            context_root,
        )

        output = _run_hook(
            _payload(
                "PreToolUse",
                session_id,
                turn_id,
                tool_name="create_goal",
                tool_input={"objective": "完成预算授权任务。", "token_budget": 12000},
            ),
            context_root,
        )
        assert output.get("hookSpecificOutput", {}).get("permissionDecision") != "deny"


def test_pretool_rejects_a_negated_goal_token_budget_reference() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-goal-budget-negated"
        turn_id = "turn-goal-budget-negated"
        _run_hook(
            _payload(
                "UserPromptSubmit",
                session_id,
                turn_id,
                prompt="不要设置 token_budget 为 12000；应保持不设预算。",
            ),
            context_root,
        )

        output = _run_hook(
            _payload(
                "PreToolUse",
                session_id,
                turn_id,
                tool_name="create_goal",
                tool_input={"objective": "完成无预算任务。", "token_budget": 12000},
            ),
            context_root,
        )
        assert output["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_goal_checkpoint_records_token_budget_from_goal_result() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-goal-budget-audit"
        turn_id = "turn-goal-budget-audit"
        _run_hook(
            _payload("UserPromptSubmit", session_id, turn_id, prompt="请完成一次长期任务。"),
            context_root,
        )
        _run_hook(
            _payload(
                "PostToolUse",
                session_id,
                turn_id,
                tool_name="create_goal",
                tool_input={"objective": "完成一次长期任务。", "token_budget": 12000},
                tool_response={
                    "goal": {
                        "objective": "完成一次长期任务。",
                        "status": "active",
                        "tokenBudget": 12000,
                    }
                },
            ),
            context_root,
        )
        active = json.loads((context_root / session_id / "active.json").read_text(encoding="utf-8"))
        assert active["goal_checkpoint"]["token_budget"] == 12000


def test_direct_prompt_bootstraps_goal_without_selecting_a_task() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        submitted = _run_hook(
            _payload(
                "UserPromptSubmit",
                "session-goal-bootstrap",
                "turn-goal-bootstrap",
                prompt="请修复这个非 trivial 的连续性问题并完成测试。",
            ),
            Path(temporary),
        )
        context = submitted["hookSpecificOutput"]["additionalContext"]
        assert "[MoSim Goal bootstrap]" in context
        assert "outcome, constraints, and verification" in context
        assert "newer direct user instruction" in context


def test_get_goal_tracks_a_goal_without_recovering_a_missing_direct_prompt() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-goal-read-refresh"
        turn_id = "turn-goal-read-refresh"

        _run_hook(
            _payload("UserPromptSubmit", session_id, turn_id, prompt="继续处理已存在的长期任务。"),
            context_root,
        )
        _run_hook(
            _payload(
                "PostToolUse",
                session_id,
                turn_id,
                tool_name="get_goal",
                tool_input={},
                tool_response={
                    "goal": {
                        "objective": "恢复升级前创建的同会话 Goal。",
                        "status": "active",
                    }
                },
            ),
            context_root,
        )
        active = json.loads((context_root / session_id / "active.json").read_text(encoding="utf-8"))
        assert active["goal_checkpoint"]["objective"] == "恢复升级前创建的同会话 Goal。"

        (context_root / session_id / "turns" / f"{turn_id}.json").unlink()
        _run_hook(_payload("PreCompact", session_id, turn_id, trigger="auto"), context_root)
        started = _run_hook(
            _payload("SessionStart", session_id, turn_id, source="compact"),
            context_root,
        )
        context = started["hookSpecificOutput"]["additionalContext"]
        assert "direct user input for this compacted turn was not captured" in context
        assert "恢复升级前创建的同会话 Goal。" not in context


def test_missing_direct_prompt_does_not_resume_an_active_goal() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-goal-fallback"
        turn_id = "turn-goal-fallback"

        _run_hook(
            _payload("UserPromptSubmit", session_id, turn_id, prompt="先完成一个长期任务。"),
            context_root,
        )
        _run_hook(
            _payload(
                "PostToolUse",
                session_id,
                turn_id,
                tool_name="create_goal",
                tool_input={"objective": "修复压缩恢复，保留用户资源并通过回归测试。"},
                tool_response={
                    "goal": {
                        "objective": "修复压缩恢复，保留用户资源并通过回归测试。",
                        "status": "active",
                    }
                },
            ),
            context_root,
        )
        active = json.loads((context_root / session_id / "active.json").read_text(encoding="utf-8"))
        assert active["goal_checkpoint"]["status"] == "active"

        # Simulate the reported failure: the prompt pack is absent, while the
        # same-session Goal state still exists.
        (context_root / session_id / "turns" / f"{turn_id}.json").unlink()
        _run_hook(_payload("PreCompact", session_id, turn_id, trigger="auto"), context_root)

        started = _run_hook(
            _payload("SessionStart", session_id, turn_id, source="compact"),
            context_root,
        )
        context = started["hookSpecificOutput"]["additionalContext"]
        assert "direct user input for this compacted turn was not captured" in context
        assert "[MoSim Goal Continuity Fallback]" not in context
        assert "修复压缩恢复，保留用户资源并通过回归测试。" not in context
        assert "codex_app__read_thread" in context

        # Unresolved recovery does not arm the history-only Stop guard.
        assert _run_hook(_payload("Stop", session_id, "turn-after-compact"), context_root) == {}


def test_completed_goal_does_not_revive_a_missing_prompt_pack() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-completed-goal"
        turn_id = "turn-completed-goal"

        _run_hook(
            _payload("UserPromptSubmit", session_id, turn_id, prompt="完成后不要重启旧任务。"),
            context_root,
        )
        _run_hook(
            _payload(
                "PostToolUse",
                session_id,
                turn_id,
                tool_name="create_goal",
                tool_input={"objective": "完成一次性任务。"},
                tool_response={"goal": {"objective": "完成一次性任务。", "status": "active"}},
            ),
            context_root,
        )
        _run_hook(
            _payload(
                "PostToolUse",
                session_id,
                turn_id,
                tool_name="update_goal",
                tool_input={"status": "complete"},
                tool_response={"goal": {"objective": "完成一次性任务。", "status": "complete"}},
            ),
            context_root,
        )
        (context_root / session_id / "turns" / f"{turn_id}.json").unlink()

        started = _run_hook(
            _payload("SessionStart", session_id, turn_id, source="compact"),
            context_root,
        )
        context = started["hookSpecificOutput"]["additionalContext"]
        assert "[MoSim Goal Continuity Fallback]" not in context
        assert "No bounded task recovery pack or recognized transcript_path user message was available" in context


def test_newer_direct_prompt_supersedes_an_unclaimed_compact_guard() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-superseded-compact-guard"

        _run_hook(
            _payload("SessionStart", session_id, "turn-compact", source="compact"),
            context_root,
        )
        _run_hook(
            _payload("UserPromptSubmit", session_id, "turn-newer", prompt="请处理新的明确任务。"),
            context_root,
        )

        stopped = _run_hook(_payload("Stop", session_id, "turn-newer"), context_root)
        assert stopped == {}


def test_compaction_reinjects_direct_scope_sources_and_plan_checkpoint() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-context-recovery"
        source_urls = [f"https://papers.example.test/{index}" for index in range(1, 9)]
        direct_prompt = "请基于这八篇论文修复解析器：" + " ".join(source_urls)

        submitted = _run_hook(
            _payload("UserPromptSubmit", session_id, "turn-a", prompt=direct_prompt),
            context_root,
        )
        submitted_context = submitted["hookSpecificOutput"]["additionalContext"]
        assert submitted["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
        for source in source_urls:
            assert source in submitted_context

        _run_hook(
            _payload(
                "PostToolUse",
                session_id,
                "turn-a",
                tool_name="create_goal",
                tool_input={"objective": "基于八篇论文修复解析器并完成验证。"},
                tool_response={
                    "goal": {
                        "objective": "基于八篇论文修复解析器并完成验证。",
                        "status": "active",
                    }
                },
            ),
            context_root,
        )

        plan = [
            {"step": "定位解析入口", "status": "completed"},
            {"step": "实现资源清单", "status": "in_progress"},
        ]
        checkpointed = _run_hook(
            _payload(
                "PostToolUse",
                session_id,
                "turn-a",
                tool_name="update_plan",
                tool_input={"explanation": "保留用户给出的八篇论文。", "plan": plan},
            ),
            context_root,
        )
        assert checkpointed == {}

        _run_hook(
            _payload("PreCompact", session_id, "turn-a", trigger="auto"),
            context_root,
        )
        recovered = _run_hook(
            _payload("SessionStart", session_id, "turn-a", source="compact"),
            context_root,
        )
        recovery_context = recovered["hookSpecificOutput"]["additionalContext"]
        assert "[MoSim Task Recovery Pack]" in recovery_context
        assert direct_prompt in recovery_context
        for source in source_urls:
            assert source in recovery_context
        assert "Active same-session goal" not in recovery_context
        assert "基于八篇论文修复解析器并完成验证。" not in recovery_context
        assert "[completed] 定位解析入口" in recovery_context
        assert "[in_progress] 实现资源清单" in recovery_context
        assert "non-authoritative" in recovery_context

        no_guard = _run_hook(_payload("Stop", session_id, "turn-a"), context_root)
        assert no_guard == {}

        duplicate = _run_hook(
            _payload("SessionStart", session_id, "turn-a", source="compact"),
            context_root,
        )
        assert duplicate == {}

        active = json.loads((context_root / session_id / "active.json").read_text(encoding="utf-8"))
        assert active["active_turn_id"] == "turn-a"
        assert active["last_compaction"]["stage"] == "pre"
        catalog = json.loads((context_root / session_id / "resource_catalog.json").read_text(encoding="utf-8"))
        assert len(catalog["bundles"]) == 1
        assert [resource["value"] for resource in catalog["bundles"][0]["resources"]] == source_urls


def test_compaction_missing_source_requires_current_thread_read_before_asking_user() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-missing-markdown-source"
        turn_id = "turn-missing-markdown-source"

        _run_hook(
            _payload(
                "UserPromptSubmit",
                session_id,
                turn_id,
                prompt="继续处理已经讨论过的两份 Markdown，不要生成 Word。",
            ),
            context_root,
        )
        _run_hook(_payload("PreCompact", session_id, turn_id, trigger="auto"), context_root)

        recovered = _run_hook(
            _payload("SessionStart", session_id, turn_id, source="compact"),
            context_root,
        )
        context = recovered["hookSpecificOutput"]["additionalContext"]

        assert "`codex_app__read_thread` only for the current thread" in context
        assert "Ask only if that bounded read does not recover the source." in context
        assert "Never infer a user-supplied source from repository files" in context


def test_continuity_diagnosis_does_not_require_the_interrupted_source() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-continuity-diagnosis"
        turn_id = "turn-continuity-diagnosis"
        prompt = "文档的问题还是什么？为什么会停下来？先解决这个问题。"

        submitted = _run_hook(
            _payload("UserPromptSubmit", session_id, turn_id, prompt=prompt),
            context_root,
        )
        submitted_context = submitted["hookSpecificOutput"]["additionalContext"]
        assert "[MoSim Continuity Diagnosis]" in submitted_context
        assert "independently executable task" in submitted_context

        _run_hook(_payload("PreCompact", session_id, turn_id, trigger="auto"), context_root)
        recovered = _run_hook(
            _payload("SessionStart", session_id, turn_id, source="compact"),
            context_root,
        )
        context = recovered["hookSpecificOutput"]["additionalContext"]

        assert "[MoSim Continuity Diagnosis]" in context
        assert "Do not request a missing source from the interrupted work" in context
        assert "Before asking the user for a requested source absent from this pack" not in context


def test_structured_app_prompt_preserves_text_and_attachment_identity() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-structured-prompt"
        turn_id = "turn-structured-prompt"
        document_path = r"C:\Users\HP\Desktop\MoSim\Results\pilot.docx"
        source_url = "https://example.test/reference"
        payload = {
            "cwd": str(ROOT),
            "hook_event_name": "UserPromptSubmit",
            "sessionId": session_id,
            "turnId": turn_id,
            "prompt": {
                "content": [
                    {"type": "text", "text": f"修复 {source_url}"},
                    {"type": "localImage", "path": document_path},
                ]
            },
        }

        submitted = _run_hook(payload, context_root)
        assert submitted["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
        record = json.loads(
            (context_root / session_id / "turns" / f"{turn_id}.json").read_text(encoding="utf-8")
        )
        assert source_url in record["user_prompt"]
        assert document_path in record["user_prompt"]
        assert [resource["value"] for resource in record["resources"]] == [source_url, document_path]

        _run_hook(
            {
                "cwd": str(ROOT),
                "hook_event_name": "PreCompact",
                "sessionId": session_id,
                "turnId": turn_id,
                "trigger": "auto",
            },
            context_root,
        )
        recovered = _run_hook(
            {
                "cwd": str(ROOT),
                "hook_event_name": "SessionStart",
                "sessionId": session_id,
                "source": "compact",
            },
            context_root,
        )
        context = recovered["hookSpecificOutput"]["additionalContext"]
        assert source_url in context
        assert document_path in context


def test_later_reference_recovers_prior_sources_without_transcript_parsing() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-prior-resources"
        source = "https://papers.example.test/prior-source"
        _run_hook(
            _payload("UserPromptSubmit", session_id, "turn-1", prompt=f"先阅读 {source}"),
            context_root,
        )
        _run_hook(
            _payload("UserPromptSubmit", session_id, "turn-2", prompt="请继续比较上述链接，不要换成仓库中的同名文件。"),
            context_root,
        )
        _run_hook(
            _payload("PreCompact", session_id, "turn-2", trigger="manual"),
            context_root,
        )
        recovered = _run_hook(
            _payload("SessionStart", session_id, "turn-2", source="compact"),
            context_root,
        )
        recovery_context = recovered["hookSpecificOutput"]["additionalContext"]
        assert "请继续比较上述链接" in recovery_context
        assert source in recovery_context
        assert "reference-only" in recovery_context
        assert "transcript" not in recovery_context.lower()


def test_concurrent_compact_session_starts_inject_only_once() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-concurrent-compact"
        _run_hook(
            _payload(
                "UserPromptSubmit",
                session_id,
                "turn-concurrent",
                prompt="继续实现同一任务：https://papers.example.test/concurrent",
            ),
            context_root,
        )
        _run_hook(
            _payload("PreCompact", session_id, "turn-concurrent", trigger="auto"),
            context_root,
        )

        environment = dict(os.environ)
        environment["MOSIM_CONTEXT_PACK_ROOT"] = str(context_root)
        payload = json.dumps(
            _payload("SessionStart", session_id, "turn-concurrent", source="compact"),
            ensure_ascii=False,
        )
        processes = [
            subprocess.Popen(
                [sys.executable, str(HOOK)],
                cwd=ROOT,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=environment,
            )
            for _ in range(2)
        ]
        outputs = [process.communicate(payload, timeout=20) for process in processes]
        assert all(process.returncode == 0 for process in processes)
        rendered = [stdout for stdout, _ in outputs if stdout.strip()]
        assert sum("[MoSim Task Recovery Pack]" in stdout for stdout in rendered) == 1


def test_resource_manifest_and_turn_history_are_bounded() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        session_id = "session-bounded-manifest"
        sources = [f"https://papers.example.test/{index}" for index in range(1, 19)]
        _run_hook(
            _payload("UserPromptSubmit", session_id, "turn-many", prompt=" ".join(sources)),
            context_root,
        )
        catalog = json.loads((context_root / session_id / "resource_catalog.json").read_text(encoding="utf-8"))
        bundle = catalog["bundles"][0]
        assert len(bundle["resources"]) == 16
        assert bundle["resources_truncated"] is True
        assert bundle["resources_detected_count"] == len(sources)

        for index in range(1, 7):
            _run_hook(
                _payload(
                    "UserPromptSubmit",
                    session_id,
                    f"turn-source-{index}",
                    prompt=f"https://papers.example.test/source-{index}",
                ),
                context_root,
            )
        catalog = json.loads((context_root / session_id / "resource_catalog.json").read_text(encoding="utf-8"))
        assert len(catalog["bundles"]) == 6
        catalog_turns = [bundle["turn_id"] for bundle in catalog["bundles"]]
        assert "turn-many" not in catalog_turns
        assert "turn-source-6" in catalog_turns

        for index in range(1, 15):
            _run_hook(
                _payload("UserPromptSubmit", session_id, f"turn-{index}", prompt=f"任务 {index}"),
                context_root,
            )
        turns = list((context_root / session_id / "turns").glob("*.json"))
        assert len(turns) == 12
        assert (context_root / session_id / "turns" / "turn-14.json").is_file()


def test_recovery_state_redacts_secret_like_user_input() -> None:
    with tempfile.TemporaryDirectory() as temporary:
        context_root = Path(temporary)
        _run_hook(
            _payload(
                "UserPromptSubmit",
                "session-redaction",
                "turn-secret",
                prompt="检查 https://example.test/report?access_token=do-not-store api_key=also-do-not-store",
            ),
            context_root,
        )
        record = (context_root / "session-redaction" / "turns" / "turn-secret.json").read_text(encoding="utf-8")
        assert "do-not-store" not in record
        assert "also-do-not-store" not in record
        assert "[REDACTED]" in record
