"""Generic direct-prompt continuity for non-MoSim Codex sessions."""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


MOSIM_ROOT = Path(__file__).resolve().parents[2]
CODEX_HOME = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
STATE_ROOT = CODEX_HOME / "continuity_packs" / "global"
MAX_PROMPT_CHARS = 12_000
MAX_VISIBLE_CONTEXT_CHARS = 1_800
MAX_SESSIONS = 128
MAX_COMPACTION_CLAIMS = 512
MAX_SESSION_RESET_CLAIMS = 512
WRITE_RETRY_ATTEMPTS = 4
WRITE_RETRY_SECONDS = 0.05
GOAL_CONTEXT_OPEN_RE = re.compile(
    r"^\s*<codex_internal_context\b(?=[^>]*\bsource\s*=\s*(?:\"goal\"|'goal'|goal(?:\s|>|/)))[^>]*>",
    re.IGNORECASE,
)
TURN_ABORTED_CONTEXT_RE = re.compile(r"^\s*<turn_aborted\b[^>]*>[\s\S]*?</turn_aborted>\s*$", re.IGNORECASE)
PROJECT_CONTEXT_RE = re.compile(
    r"^\s*#\s*AGENTS\.md\s+instructions\s+for\s+[^\r\n]+\r?\n\s*<INSTRUCTIONS>[\s\S]*?</INSTRUCTIONS>"
    r"(?:\s*<environment_context>[\s\S]*?</environment_context>)?\s*$",
    re.IGNORECASE,
)
ASSIGNMENT_SECRET_RE = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|secret|password|credential)\b(\s*[:=]\s*)([^\s,;]+)"
)
URL_SECRET_RE = re.compile(
    r"(?i)([?&](?:api[_-]?key|access[_-]?token|refresh[_-]?token|secret|password|credential)=)[^&#\s]+"
)
API_KEY_RE = re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")
AUTHORIZATION_SECRET_RE = re.compile(r"(?i)(\bauthorization\b\s*[:=]\s*)(?:bearer\s+)?[^\s,;]+")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _read_input() -> dict[str, Any]:
    stream = getattr(sys.stdin, "buffer", None)
    raw = stream.read().decode("utf-8") if stream is not None else sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _is_mosim(cwd: object) -> bool:
    if not isinstance(cwd, str) or not cwd:
        return False
    try:
        resolved = Path(cwd).resolve()
    except OSError:
        return False
    return resolved == MOSIM_ROOT or MOSIM_ROOT in resolved.parents


def _text(value: object) -> str:
    if isinstance(value, str):
        return value
    return ""


def _redact(text: str) -> str:
    """Match the MoSim recovery pack's persisted-prompt redaction policy."""

    text = ASSIGNMENT_SECRET_RE.sub(r"\1\2[REDACTED]", text)
    text = URL_SECRET_RE.sub(r"\1[REDACTED]", text)
    text = API_KEY_RE.sub("[REDACTED]", text)
    return AUTHORIZATION_SECRET_RE.sub(r"\1[REDACTED]", text)


def _excerpt(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    head = max(1, limit // 2 - 24)
    tail = max(1, limit - head - 48)
    return f"{text[:head]}\n[...truncated for bounded recovery...]\n{text[-tail:]}"


def _prompt_text(value: object) -> str:
    """Normalize the documented prompt fields used by local Codex surfaces."""

    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = [_prompt_text(item) for item in value]
        return "\n".join(part for part in parts if part)
    if isinstance(value, dict):
        for key in ("text", "prompt", "user_prompt", "userPrompt", "value", "message"):
            rendered = _prompt_text(value.get(key))
            if rendered:
                return rendered
        content = value.get("content")
        rendered = _prompt_text(content)
        if rendered:
            return rendered
        for key in ("path", "file_path", "filePath", "image_path", "imagePath", "url"):
            rendered = _text(value.get(key))
            if rendered:
                return rendered
    return ""


def _safe_component(value: object, fallback: str) -> str:
    raw = str(value or "").strip()
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32] if raw else fallback


def _payload_text(payload: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = _text(payload.get(key)).strip()
        if value:
            return value
    return ""


def _session_path(payload: dict[str, Any]) -> Path:
    session_id = _payload_text(payload, "session_id", "sessionId", "thread_id", "threadId") or os.environ.get(
        "CODEX_THREAD_ID", ""
    ).strip()
    return STATE_ROOT / f"{_safe_component(session_id, 'unknown-session')}.json"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(json.dumps(payload, ensure_ascii=True, separators=(",", ":")) + "\n", encoding="utf-8")
        for attempt in range(WRITE_RETRY_ATTEMPTS):
            try:
                temporary.replace(path)
                break
            except OSError:
                if attempt + 1 == WRITE_RETRY_ATTEMPTS:
                    return
                time.sleep(WRITE_RETRY_SECONDS)
    except OSError:
        return
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        except OSError:
            pass

    try:
        sessions = sorted(STATE_ROOT.glob("*.json"), key=lambda candidate: candidate.stat().st_mtime_ns)
    except OSError:
        return
    for stale in sessions[:-MAX_SESSIONS]:
        try:
            stale.unlink()
        except OSError:
            continue


def _emit_context(context: str, *, event_name: str = "SessionStart") -> None:
    payload = json.dumps(
        {
            "hookSpecificOutput": {
                "hookEventName": event_name,
                "additionalContext": context,
            }
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    stream = getattr(sys.stdout, "buffer", None)
    if stream is None:
        print(payload)
        return
    stream.write((payload + "\n").encode("utf-8"))
    stream.flush()


def _capture_prompt(payload: dict[str, Any]) -> None:
    prompt = ""
    for key in ("prompt", "user_prompt", "userPrompt", "input"):
        prompt = _prompt_text(payload.get(key)).strip()
        if prompt:
            break
    if (
        not prompt
        or GOAL_CONTEXT_OPEN_RE.match(prompt)
        or TURN_ABORTED_CONTEXT_RE.match(prompt)
        or PROJECT_CONTEXT_RE.match(prompt)
    ):
        return
    prompt = _redact(prompt)[:MAX_PROMPT_CHARS]
    path = _session_path(payload)
    state = _read_json(path)
    state.update(
        {
            "schema_version": 1,
            "active_prompt": prompt,
            "active_turn_id": _payload_text(payload, "turn_id", "turnId"),
            "capture_id": uuid.uuid4().hex,
            "captured_at": _utc_now(),
        }
    )
    _write_json(path, state)


def _mark_compaction(payload: dict[str, Any]) -> None:
    path = _session_path(payload)
    state = _read_json(path)
    state.update(
        {
            "compaction_id": uuid.uuid4().hex,
            "compacted_at": _utc_now(),
            "compaction_turn_id": _payload_text(payload, "turn_id", "turnId"),
            "compaction_capture_id": _text(state.get("capture_id")),
        }
    )
    _write_json(path, state)


def _claim_compaction(path: Path, compaction_id: str) -> bool:
    marker_dir = STATE_ROOT / "compaction_claims"
    marker = marker_dir / f"{path.stem}-{_safe_component(compaction_id, 'compaction')}.claimed"
    try:
        marker_dir.mkdir(parents=True, exist_ok=True)
        with marker.open("x", encoding="utf-8") as stream:
            stream.write(_utc_now() + "\n")
    except FileExistsError:
        return False
    except OSError:
        # Storage errors must not prevent a legitimate continuation.
        return True

    try:
        markers = sorted(marker_dir.glob("*.claimed"), key=lambda candidate: candidate.stat().st_mtime_ns)
    except OSError:
        return True
    for stale in markers[:-MAX_COMPACTION_CLAIMS]:
        try:
            stale.unlink()
        except OSError:
            continue
    return True


def _compact_context(payload: dict[str, Any]) -> str:
    path = _session_path(payload)
    state = _read_json(path)
    compaction_id = _text(state.get("compaction_id"))
    compacted_capture_id = _text(state.get("compaction_capture_id"))
    active_capture_id = _text(state.get("capture_id"))
    # A newer direct user submission has its own immediate model request. Do
    # not inject it into a pending compact restart for an older turn.
    if compaction_id and compacted_capture_id and compacted_capture_id != active_capture_id:
        return ""
    if compaction_id and not _claim_compaction(path, compaction_id):
        return ""

    prompt = state.get("active_prompt")
    if not isinstance(prompt, str) or not prompt:
        return (
            "Codex continuity guard: compaction is not task completion. No captured direct user request is available. "
            "Use current-thread history only when exposed, then request the minimum missing source; do not select "
            "replacement work or end silently."
        )

    return (
        "Codex continuity guard: context compaction is an internal continuation boundary, not task completion. "
        "Continue this direct user request in the same turn after loading required workspace guidance. Do not replace "
        "it with repository status, memory, or an older plan.\n\n[Captured direct user request]\n"
        f"{_excerpt(prompt, MAX_VISIBLE_CONTEXT_CHARS)}"
    )


def _claim_session_reset(path: Path, reset_id: str) -> bool:
    marker_dir = STATE_ROOT / "session_reset_claims"
    marker = marker_dir / f"{path.stem}-{_safe_component(reset_id, 'session-reset')}.claimed"
    try:
        marker_dir.mkdir(parents=True, exist_ok=True)
        with marker.open("x", encoding="utf-8") as stream:
            stream.write(_utc_now() + "\n")
    except FileExistsError:
        return False
    except OSError:
        return True

    try:
        markers = sorted(marker_dir.glob("*.claimed"), key=lambda candidate: candidate.stat().st_mtime_ns)
    except OSError:
        return True
    for stale in markers[:-MAX_SESSION_RESET_CLAIMS]:
        try:
            stale.unlink()
        except OSError:
            continue
    return True


def _session_reset_context(payload: dict[str, Any], source: str) -> str:
    path = _session_path(payload)
    state = _read_json(path)
    prompt = _text(state.get("active_prompt"))
    if not prompt:
        return (
            f"Codex continuity guard: session {source} is not task completion. No captured direct user request is available. "
            "Use current-thread history only when exposed, then request the minimum missing source; do not select replacement work or end silently."
        )

    reset_id = ":".join(
        (
            source,
            _payload_text(payload, "turn_id", "turnId") or "unknown-turn",
            _text(state.get("active_turn_id")) or "unknown-direct-turn",
            _text(state.get("capture_id")) or hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:24],
        )
    )
    if not _claim_session_reset(path, reset_id):
        return ""
    return (
        f"Codex continuity guard: session {source} is an internal continuation boundary, not task completion. "
        "Continue this direct user request in the same turn after loading required workspace guidance. Do not replace "
        "it with repository status, memory, or an older plan.\n\n[Captured direct user request]\n"
        f"{_excerpt(prompt, MAX_VISIBLE_CONTEXT_CHARS)}"
    )


def _project_context_recovery(payload: dict[str, Any]) -> str:
    state = _read_json(_session_path(payload))
    prompt = _text(state.get("active_prompt"))
    message = (
        "Codex injected a full AGENTS.md project-context envelope. It is not a direct user request and must not replace "
        "the newest direct prompt or trigger a generic task-selection reply."
    )
    if prompt:
        return (
            f"{message}\n\n[Previously captured direct user request]\n"
            f"{_excerpt(prompt, MAX_VISIBLE_CONTEXT_CHARS)}"
        )
    return f"{message}\n\nNo direct user request is locally captured; wait for an actual direct user message."


def handle_event(payload: dict[str, Any]) -> int:
    """Handle only non-MoSim lifecycle events routed by the global hook config."""

    if _is_mosim(payload.get("cwd")):
        return 0
    event = str(payload.get("hook_event_name") or "")
    if event == "UserPromptSubmit":
        prompt = ""
        for key in ("prompt", "user_prompt", "userPrompt", "input"):
            prompt = _prompt_text(payload.get(key)).strip()
            if prompt:
                break
        if PROJECT_CONTEXT_RE.match(prompt):
            _emit_context(_project_context_recovery(payload), event_name="UserPromptSubmit")
        else:
            _capture_prompt(payload)
    elif event == "PreCompact":
        _mark_compaction(payload)
    elif event == "SessionStart":
        source = str(payload.get("source") or "")
        context = _compact_context(payload) if source == "compact" else (
            _session_reset_context(payload, source) if source in {"clear", "resume"} else ""
        )
        if context:
            _emit_context(context)
    return 0


def main() -> int:
    return handle_event(_read_input())


if __name__ == "__main__":
    raise SystemExit(main())
