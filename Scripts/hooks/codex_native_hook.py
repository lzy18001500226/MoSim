#!/usr/bin/env python
"""Codex native hook adapter for MoSim.

This adapter is intentionally thin: Codex owns lifecycle dispatch, while the
project-local preflight remains the policy implementation.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    from .global_context_continuity import handle_event as handle_global_continuity_event
    from .context_recovery import (
        capture_transcript_user_prompt,
        compaction_lacks_current_turn_capture,
        active_direct_user_prompt,
        capture_user_prompt,
        consume_compact_context,
        consume_session_reset_context,
        consume_internal_continuation,
        direct_user_prompt,
        is_generated_goal_context,
        is_generated_project_context,
        is_generated_turn_aborted_context,
        mark_compaction,
        record_recovery_decision,
        record_goal,
        record_plan,
        render_generated_project_context,
        unresolved_recovery_message,
    )
    from .task_terminal_email import emit_terminal_email
except ImportError:  # Direct hook execution has no package parent.
    from global_context_continuity import handle_event as handle_global_continuity_event  # type: ignore[no-redef]
    from context_recovery import (  # type: ignore[no-redef]
        capture_transcript_user_prompt,
        compaction_lacks_current_turn_capture,
        active_direct_user_prompt,
        capture_user_prompt,
        consume_compact_context,
        consume_session_reset_context,
        consume_internal_continuation,
        direct_user_prompt,
        is_generated_goal_context,
        is_generated_project_context,
        is_generated_turn_aborted_context,
        mark_compaction,
        record_recovery_decision,
        record_goal,
        record_plan,
        render_generated_project_context,
        unresolved_recovery_message,
    )
    from task_terminal_email import emit_terminal_email


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_ROOT = ROOT.resolve()
GOAL_BUDGET_TERMS = re.compile(r"token[_\s-]?budget|token\s*预算|令牌\s*预算", re.IGNORECASE)
GOAL_BUDGET_ASSIGNMENT = re.compile(r"\s*(?:=|:|：|为|是|应为|应该为|设为|设置为|设定为|限制为|上限为|限额为)\s*", re.IGNORECASE)
GOAL_BUDGET_NEGATION = re.compile(r"不要|不(?:要|应|允许)|禁止|勿|\bdon't\b|\bdo not\b|\bnever\b", re.IGNORECASE)
GOAL_BUDGET_NUMBER = re.compile(r"(?<![A-Za-z0-9_])\d[\d_,]*(?![A-Za-z0-9_])")

def _read_input() -> dict[str, Any]:
    try:
        # Codex sends hook JSON as UTF-8 bytes even when Windows uses CP936.
        stream = getattr(sys.stdin, "buffer", None)
        payload = stream.read().decode("utf-8") if stream is not None else sys.stdin.read()
        if not payload.strip():
            return {}
        data = json.loads(payload)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _json(data: dict[str, Any]) -> None:
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    stream = getattr(sys.stdout, "buffer", None)
    if stream is None:
        print(payload)
        return
    stream.write((payload + "\n").encode("utf-8"))
    stream.flush()


def _is_mosim_cwd(raw_cwd: str | None) -> bool:
    if not raw_cwd:
        return False
    try:
        cwd = Path(raw_cwd).resolve()
    except OSError:
        return False
    return cwd == ALLOWED_ROOT or ALLOWED_ROOT in cwd.parents


def _normalize_rel_or_abs(raw: str) -> str:
    try:
        path = Path(raw)
        if path.is_absolute():
            resolved = path.resolve()
            try:
                return str(resolved.relative_to(ROOT)).replace("\\", "/")
            except ValueError:
                return str(resolved)
    except OSError:
        pass
    return raw.replace("\\", "/")


def _extract_command(tool_input: Any) -> str | None:
    if isinstance(tool_input, dict):
        value = tool_input.get("command")
        if isinstance(value, str):
            return value
    return None


def _extract_write_paths(tool_name: str, tool_input: Any) -> list[str]:
    paths: list[str] = []
    if isinstance(tool_input, dict):
        for key in ("path", "file", "filename"):
            value = tool_input.get(key)
            if isinstance(value, str):
                paths.append(_normalize_rel_or_abs(value))
        # apply_patch hooks report the patch as tool_input.command. The
        # project preflight cannot parse patch hunks yet, so command policy is
        # the primary hard gate for apply_patch today.
    return paths


def _goal_budget_value(tool_input: Any) -> int | None:
    if not isinstance(tool_input, dict) or "token_budget" not in tool_input:
        return None
    value = tool_input.get("token_budget")
    if value is None:
        return None
    return value if isinstance(value, int) and not isinstance(value, bool) else -1


def _direct_prompt_authorizes_goal_budget(payload: dict[str, Any], budget: int) -> bool:
    prompt = direct_user_prompt(payload) or active_direct_user_prompt(payload)
    if not prompt or not GOAL_BUDGET_TERMS.search(prompt):
        return False
    for term in GOAL_BUDGET_TERMS.finditer(prompt):
        if GOAL_BUDGET_NEGATION.search(prompt[max(0, term.start() - 64) : term.end()]):
            continue
        window = prompt[max(0, term.start() - 96) : term.end() + 96]
        for match in GOAL_BUDGET_NUMBER.finditer(window):
            if int(match.group(0).replace(",", "").replace("_", "")) != budget:
                continue
            absolute_start = max(0, term.start() - 96) + match.start()
            if absolute_start >= term.end():
                assignment = prompt[term.end() : absolute_start]
            else:
                assignment = prompt[absolute_start + len(match.group(0)) : term.start()]
            if GOAL_BUDGET_ASSIGNMENT.fullmatch(assignment):
                return True
    return False


def _deny_goal_budget() -> int:
    _json(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "MoSim Goal Budget Gate: create_goal token_budget requires a same-turn direct user request "
                    "that explicitly sets the exact numeric value."
                ),
            }
        }
    )
    return 0


def _run_preflight(args: list[str]) -> dict[str, Any]:
    command = [sys.executable, str(ROOT / "Scripts" / "hooks" / "preflight.py"), "--json", *args]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        check=False,
    )
    try:
        data = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError:
        data = {}
    data["_adapter_returncode"] = completed.returncode
    if completed.stderr.strip():
        data["_adapter_stderr"] = completed.stderr.strip()
    return data


def _format_findings(preflight: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    interactive_gate_names = {
        "scope",
        "write_scope",
        "secret_paths",
        "command_policy",
        "candidate_large_files",
        "result_packet_evidence",
        "git_workspace_state",
    }
    for name, value in preflight.items():
        if name not in interactive_gate_names:
            continue
        if not isinstance(value, dict) or value.get("ok", True):
            continue
        for item in value.get("findings", []):
            reason = item.get("reason", "policy_check")
            field = item.get("field", name)
            subject = item.get("value", "")
            lines.append(f"{reason} {field}: {subject}".strip())
        if name == "scope":
            lines.extend(f"outside_project_scope: {path}" for path in value.get("outside", []))
        if name == "candidate_large_files":
            lines.extend(f"large_file: {item.get('path')} {item.get('size_mb')} MB" for item in value.get("offenders", []))
    return lines


def _pretool(payload: dict[str, Any]) -> int:
    tool_name = str(payload.get("tool_name") or "")
    tool_input = payload.get("tool_input")
    args: list[str] = []

    if tool_name == "create_goal":
        budget = _goal_budget_value(tool_input)
        if budget is not None and (budget < 0 or not _direct_prompt_authorizes_goal_budget(payload, budget)):
            return _deny_goal_budget()

    command = _extract_command(tool_input)
    if command:
        args.extend(["--command", command])

    for path in _extract_write_paths(tool_name, tool_input):
        args.extend(["--write-path", path])

    if not args:
        return 0

    preflight = _run_preflight(args)
    findings = _format_findings(preflight)
    hard_reasons = (
        "destructive_command",
        "broad_git_risk",
        "outside_project_write",
        "secret_risk_path",
        "large_file",
    )
    hard = [line for line in findings if any(reason in line for reason in hard_reasons)]
    if hard:
        _json(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": "MoSim Codex global hook blocked this tool call: " + "; ".join(hard[:6]),
                }
            }
        )
        return 0

    if findings:
        _json(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "additionalContext": "MoSim preflight warnings: " + "; ".join(findings[:6]),
                }
            }
        )
    return 0


def _posttool(payload: dict[str, Any]) -> int:
    # Local function outputs are available only after Codex accepts the call.
    # Plans and Goals remain tracking state. Compact recovery is based only on
    # a validated direct-user record, never a Goal continuation envelope.
    tool_name = str(payload.get("tool_name") or "")
    if tool_name == "update_plan":
        record_plan(payload)
    elif tool_name in {"create_goal", "get_goal", "update_goal"}:
        record_goal(payload)
        if tool_name == "update_goal":
            try:
                emit_terminal_email(payload)
            except Exception:
                # Notification failure must not invalidate the completed Goal tool call.
                pass
    return 0


def _session_start(payload: dict[str, Any]) -> int:
    source = str(payload.get("source") or "")
    if source == "compact":
        # A transcript can reveal a newer direct-user message than the latest
        # saved record. Defer only the execution-turn fallback until that
        # bounded check has had a chance to win.
        recovery_context = consume_compact_context(payload, allow_latest_direct_record=False)
        if recovery_context is None:
            record_recovery_decision(
                payload,
                boundary="compaction",
                outcome="recovery_suppressed_after_claim_or_newer_direct_user",
            )
            return 0
        recovered_from_transcript = False
        if not recovery_context:
            transcript_context = capture_transcript_user_prompt(payload)
            if transcript_context:
                recovery_context = transcript_context
                recovered_from_transcript = True
            elif not compaction_lacks_current_turn_capture(payload):
                recovery_context = consume_compact_context(payload)
                if recovery_context is None:
                    record_recovery_decision(
                        payload,
                        boundary="compaction",
                        outcome="recovery_suppressed_after_claim_or_newer_direct_user",
                    )
                    return 0
        message = (
            "MoSim native Codex hook active for a compact continuation. "
            "Context compaction is not task completion: preserve and continue "
            "the newest direct user task already in this conversation. Read "
            "AGENTS.md and Docs/Workflows/new_conversation_context.md as "
            "required context, then continue the active task in this same "
            "turn. Do not ask for a replacement task or report completion "
            "solely because the startup files were re-read. A recovered "
            "Codex local goal, task plan, completion record, or get_goal "
            "result is non-authoritative tracking state, including if it was "
            "injected during compaction. Never use recovered state to select "
            "work or override that newest user task; ignore it on conflict. "
            "If the direct user task is not recoverable, do not end silently: "
            "use the bounded current-thread recovery check when exposed, then "
            "issue one concise request for only the minimum recovery input in "
            "this same turn rather than using recovered state as a fallback."
        )
        if recovery_context:
            record_recovery_decision(
                payload,
                boundary="compaction",
                outcome="recovery_context_injected",
                recovery_source="transcript_path_fallback" if recovered_from_transcript else "",
            )
            message += "\n\n" + recovery_context
        else:
            capture_missing = compaction_lacks_current_turn_capture(payload)
            record_recovery_decision(
                payload,
                boundary="compaction",
                outcome="continuity_unresolved",
                recovery_source="missing_direct_user_capture" if capture_missing else "",
            )
            message += "\n\n" + unresolved_recovery_message(
                current_turn_capture_missing=capture_missing
            )
    elif source in {"clear", "resume"}:
        recovery_context = consume_session_reset_context(payload, source)
        if recovery_context is None:
            record_recovery_decision(
                payload,
                boundary=source,
                outcome="recovery_suppressed_after_claim",
            )
            return 0
        recovered_from_transcript = False
        if not recovery_context:
            transcript_context = capture_transcript_user_prompt(payload)
            if transcript_context:
                # The fallback creates the first safe direct record. Claim the
                # same reset afterward so a duplicate SessionStart cannot
                # inject that just-recovered task again.
                recovery_context = consume_session_reset_context(payload, source)
                recovered_from_transcript = True
                if recovery_context is None:
                    record_recovery_decision(
                        payload,
                        boundary=source,
                        outcome="recovery_suppressed_after_claim",
                    )
                    return 0
        message = (
            f"MoSim native Codex hook active for a {source} continuation. "
            "Clearing or resuming a session is not task completion: preserve and continue "
            "the newest direct user task already in this conversation. Read AGENTS.md and "
            "Docs/Workflows/new_conversation_context.md as required context, then continue "
            "the active task in this same turn. Do not treat generated project context as a "
            "new user task or ask for replacement work solely because startup files were re-read."
        )
        if recovery_context:
            record_recovery_decision(
                payload,
                boundary=source,
                outcome="recovery_context_injected",
                recovery_source="transcript_path_fallback" if recovered_from_transcript else "active_direct_record",
            )
            message += "\n\n" + recovery_context
        else:
            record_recovery_decision(
                payload,
                boundary=source,
                outcome="continuity_unresolved",
                recovery_source="missing_direct_user_capture",
            )
            message += "\n\n" + unresolved_recovery_message()
    else:
        message = (
            "MoSim native Codex hook active. For this project, load AGENTS.md "
            "and Docs/Workflows/new_conversation_context.md first; hooks are "
            "hard guardrails, while skills/workflows are loaded on demand."
        )
    _json(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": message,
            }
        }
    )
    return 0


def _user_prompt_submit(payload: dict[str, Any]) -> int:
    prompt = direct_user_prompt(payload)
    if is_generated_project_context(prompt):
        _json(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": render_generated_project_context(payload),
                }
            }
        )
        return 0
    if is_generated_goal_context(prompt):
        _json(
            {
                "decision": "block",
                "reason": "MoSim hook rejected an internal Goal continuation envelope; send a direct user task instead.",
            }
        )
        return 0
    if is_generated_turn_aborted_context(prompt):
        _json(
            {
                "decision": "block",
                "reason": "MoSim hook rejected an App-generated turn-aborted envelope; it is not a direct user task.",
            }
        )
        return 0
    if consume_internal_continuation(payload, prompt):
        return 0
    context = capture_user_prompt(payload)
    if context:
        _json(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": context,
                }
            }
        )
    return 0


def _precompact(payload: dict[str, Any]) -> int:
    mark_compaction(payload, "pre")
    return 0


def _stop(payload: dict[str, Any]) -> int:
    # A missing current prompt is unrecoverable without an explicit source.
    # Stop must not create a synthetic user prompt that loops back into this
    # same unresolved state.
    return 0


def main() -> int:
    payload = _read_input()
    if not _is_mosim_cwd(payload.get("cwd") if isinstance(payload.get("cwd"), str) else None):
        return handle_global_continuity_event(payload)

    event = str(payload.get("hook_event_name") or "")
    if event == "PreToolUse":
        return _pretool(payload)
    if event == "PostToolUse":
        return _posttool(payload)
    if event == "SessionStart":
        return _session_start(payload)
    if event == "UserPromptSubmit":
        return _user_prompt_submit(payload)
    if event == "PreCompact":
        return _precompact(payload)
    if event == "Stop":
        return _stop(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
