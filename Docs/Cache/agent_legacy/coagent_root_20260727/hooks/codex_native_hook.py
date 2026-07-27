#!/usr/bin/env python
"""Codex native hook adapter for MoSim.

This adapter is intentionally thin: Codex owns lifecycle dispatch, while the
project-local preflight remains the policy implementation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
ALLOWED_ROOT = ROOT.resolve()


def _read_input() -> dict[str, Any]:
    try:
        payload = sys.stdin.read()
        if not payload.strip():
            return {}
        data = json.loads(payload)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _json(data: dict[str, Any]) -> None:
    print(json.dumps(data, ensure_ascii=False, separators=(",", ":")))


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


def _run_preflight(args: list[str]) -> dict[str, Any]:
    command = [sys.executable, str(ROOT / "CoAgent" / "hooks" / "preflight.py"), "--json", *args]
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


def _session_start(payload: dict[str, Any]) -> int:
    message = (
        "MoSim native Codex hook active. For this project, load AGENTS.md and "
        "Docs/Workflows/new_conversation_context.md first; hooks are hard "
        "guardrails, while skills/workflows are loaded on demand."
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


def _stop(payload: dict[str, Any]) -> int:
    # Do not auto-continue turns globally. Stop hooks are available for future
    # targeted completion gates, but using them broadly would create loops.
    return 0


def main() -> int:
    payload = _read_input()
    if not _is_mosim_cwd(payload.get("cwd") if isinstance(payload.get("cwd"), str) else None):
        return 0

    event = str(payload.get("hook_event_name") or "")
    if event == "PreToolUse":
        return _pretool(payload)
    if event == "SessionStart":
        return _session_start(payload)
    if event == "Stop":
        return _stop(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
