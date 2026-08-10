"""Bounded task and resource recovery state for MoSim Codex hooks."""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTEXT_ROOT = ROOT / "Results" / "context_packs"
SCHEMA_VERSION = 1
MAX_STORED_PROMPT_CHARS = 12_000
MAX_VISIBLE_PROMPT_CHARS = 1_200
MAX_VISIBLE_CONTEXT_CHARS = 2_400
MAX_RESOURCE_BUNDLES = 6
MAX_RESOURCES_PER_BUNDLE = 16
MAX_REFERENCED_BUNDLES = 2
MAX_VISIBLE_RESOURCES = 16
MAX_PLAN_STEPS = 6
MAX_TURN_RECORDS = 12
MAX_COMPACTION_MARKERS = 8
MAX_CONTINUATION_GUARDS = 8
MAX_INTERNAL_CONTINUATION_MARKERS = 8
MAX_VISIBLE_GOAL_CHARS = 1_200
MAX_TRANSCRIPT_TAIL_BYTES = 256 * 1024
MAX_TRANSCRIPT_LINES = 1_600

URL_RE = re.compile(r"https?://[^\s<>\[\]{}\"']+", re.IGNORECASE)
WINDOWS_PATH_RE = re.compile(r"(?i)(?<![A-Za-z0-9_])([A-Z]:[\\/][^\r\n<>|\"?*]+)")
PRIOR_RESOURCE_RE = re.compile(
    r"(?:上面|上述|前面|之前|刚才|这些|那些|这八篇|那八篇|那几篇|这些文章|那些文章|这些链接|那些链接|这个附件|那个附件|这张图|那张图|\bthat\b|\bthose\b|\babove\b|\bprevious\b|\bearlier\b)",
    re.IGNORECASE,
)
CONTINUITY_DIAGNOSIS_RE = re.compile(
    r"(?:为什么|为何|原因|怎么).{0,48}(?:停下来|停止|阻塞|卡住|中断)"
    r"|(?:停下来|停止|阻塞|卡住|中断).{0,48}(?:为什么|为何|原因)"
    r"|\b(?:why|reason).{0,80}\b(?:stop(?:ped|ping)?|block(?:ed|ing)?|stall(?:ed|ing)?|interrupt(?:ed|ing)?)\b"
    r"|\b(?:stop(?:ped|ping)?|block(?:ed|ing)?|stall(?:ed|ing)?|interrupt(?:ed|ing)?).{0,80}\b(?:why|reason)\b",
    re.IGNORECASE | re.DOTALL,
)
ASSIGNMENT_SECRET_RE = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|secret|password|credential)\b(\s*[:=]\s*)([^\s,;]+)"
)
URL_SECRET_RE = re.compile(
    r"(?i)([?&](?:api[_-]?key|access[_-]?token|refresh[_-]?token|secret|password|credential)=)[^&#\s]+"
)
API_KEY_RE = re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b")
GOAL_CONTEXT_OPEN_RE = re.compile(
    r"^\s*<codex_internal_context\b(?=[^>]*\bsource\s*=\s*(?:\"goal\"|'goal'|goal(?:\s|>|/)))[^>]*>",
    re.IGNORECASE,
)
TRAILING_SOURCE_PUNCTUATION = ".,;:!?)]}>，。；：！？）】》\"'"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _text(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _payload_text(payload: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = _text(payload.get(key)).strip()
        if value:
            return value
    return ""


def _prompt_text(value: Any) -> str:
    """Normalize documented text prompts and bounded App bridge envelopes."""

    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = [_prompt_text(item) for item in value]
        return "\n".join(part for part in parts if part)
    if not isinstance(value, dict):
        return ""

    direct = _payload_text(value, "text", "prompt", "user_prompt", "userPrompt", "value", "message")
    if direct:
        return direct

    content = value.get("content")
    if isinstance(content, list):
        rendered = _prompt_text(content)
        if rendered:
            return rendered

    # Keep attachment identities available to the existing resource extractor.
    return _payload_text(value, "path", "file_path", "filePath", "image_path", "imagePath", "url")


def direct_user_prompt(payload: dict[str, Any]) -> str:
    """Return the direct prompt from the standard hook schema or App envelopes."""

    for key in ("prompt", "user_prompt", "userPrompt", "input"):
        rendered = _prompt_text(payload.get(key))
        if rendered.strip():
            return rendered
    return ""


def is_generated_goal_context(prompt: str) -> bool:
    """Recognize App Goal continuations without treating them as user input."""

    return bool(GOAL_CONTEXT_OPEN_RE.match(prompt))


def is_continuity_diagnosis(prompt: str) -> bool:
    """Return whether the direct user request is about an unexpected stop itself."""

    return bool(CONTINUITY_DIAGNOSIS_RE.search(prompt))


def _safe_component(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return (cleaned or fallback)[:120]


def _context_root() -> Path:
    override = os.environ.get("MOSIM_CONTEXT_PACK_ROOT")
    return Path(override).expanduser() if override else DEFAULT_CONTEXT_ROOT


def _session_id(payload: dict[str, Any]) -> str:
    """Resolve the Codex session identity across lifecycle event envelopes."""

    return _payload_text(payload, "session_id", "sessionId", "thread_id", "threadId") or os.environ.get(
        "CODEX_THREAD_ID", ""
    ).strip()


def _session_dir(payload: dict[str, Any]) -> Path | None:
    session_id = _session_id(payload)
    if not session_id:
        return None
    return _context_root() / _safe_component(session_id, "session")


def _turn_id(payload: dict[str, Any]) -> str | None:
    value = _payload_text(payload, "turn_id", "turnId")
    return _safe_component(value, "turn") if value else None


def _capture_turn_id(payload: dict[str, Any], prompt: str) -> str:
    """Use the native turn id when present, otherwise create a direct-input id."""

    return _turn_id(payload) or f"captured-{uuid.uuid4().hex}"


def _record_path(session_dir: Path, turn_id: str) -> Path:
    return session_dir / "turns" / f"{turn_id}.json"


def _prune_turn_records(session_dir: Path, active_turn_id: str) -> None:
    turns_dir = session_dir / "turns"
    try:
        records = sorted(
            turns_dir.glob("*.json"),
            key=lambda path: (path.stat().st_mtime_ns, path.name),
        )
    except OSError:
        return
    while len(records) > MAX_TURN_RECORDS:
        candidate = next((path for path in records if path.stem != active_turn_id), None)
        if candidate is None:
            return
        try:
            candidate.unlink()
        except OSError:
            return
        records.remove(candidate)


def _read_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = None
    return data if isinstance(data, dict) else (default or {})


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _redact(text: str) -> str:
    text = ASSIGNMENT_SECRET_RE.sub(r"\1\2[REDACTED]", text)
    text = URL_SECRET_RE.sub(r"\1[REDACTED]", text)
    return API_KEY_RE.sub("[REDACTED]", text)


def _excerpt(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    head = max(1, limit // 2 - 24)
    tail = max(1, limit - head - 48)
    return f"{text[:head]}\n[...truncated for bounded recovery...]\n{text[-tail:]}", True


def _trim_source(value: str) -> str:
    return value.strip().rstrip(TRAILING_SOURCE_PUNCTUATION)


def extract_resources(prompt: str) -> list[dict[str, str]]:
    matches: list[tuple[int, str, str]] = []
    for match in URL_RE.finditer(prompt):
        value = _trim_source(match.group(0))
        if value:
            matches.append((match.start(), "url", value))
    for match in WINDOWS_PATH_RE.finditer(prompt):
        value = _trim_source(match.group(1))
        if value:
            matches.append((match.start(), "local_path", value))

    resources: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for _, kind, value in sorted(matches, key=lambda item: item[0]):
        key = (kind, value.casefold() if kind == "local_path" else value)
        if key in seen:
            continue
        seen.add(key)
        resources.append({"id": f"user-{kind}-{len(resources) + 1}", "kind": kind, "value": value})
    return resources


def _catalog_entry(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "turn_id": record["turn_id"],
        "captured_at": record["captured_at"],
        "prompt_sha256": record["prompt_sha256"],
        "prompt_excerpt": _excerpt(record["user_prompt"], 320)[0],
        "resources": record["resources"],
        "resources_detected_count": record.get("resources_detected_count", len(record["resources"])),
        "resources_truncated": bool(record.get("resources_truncated")),
    }


def _load_catalog(session_dir: Path) -> dict[str, Any]:
    catalog = _read_json(session_dir / "resource_catalog.json")
    bundles = catalog.get("bundles")
    if not isinstance(bundles, list):
        bundles = []
    return {"schema_version": SCHEMA_VERSION, "bundles": bundles}


def _recent_resource_bundles(session_dir: Path) -> list[dict[str, Any]]:
    catalog = _load_catalog(session_dir)
    bundles = [bundle for bundle in catalog["bundles"] if isinstance(bundle, dict) and bundle.get("resources")]
    return bundles[-MAX_REFERENCED_BUNDLES:]


def _references_prior_resources(prompt: str) -> bool:
    return bool(PRIOR_RESOURCE_RE.search(prompt))


def _direct_record_for_turn(session_dir: Path, turn_id: str | None) -> tuple[dict[str, Any], Path] | tuple[None, None]:
    if not turn_id:
        return None, None
    path = _record_path(session_dir, turn_id)
    record = _read_json(path)
    if record.get("kind") != "mosim_direct_user_input" or _text(record.get("turn_id")) != turn_id:
        return None, None
    # Older hook versions could persist the App's Goal continuation envelope
    # as a user record. Keep it on disk for diagnostics, but never recover it.
    if is_generated_goal_context(_text(record.get("user_prompt"))):
        return None, None
    return record, path


def _compaction_direct_turn_id(payload: dict[str, Any]) -> str | None:
    """Return an explicit user-turn id when a lifecycle envelope provides one."""

    value = _payload_text(payload, "direct_user_turn_id", "directUserTurnId", "user_turn_id", "userTurnId")
    return _safe_component(value, "user-turn") if value else None


def _capture_direct_user_prompt(
    payload: dict[str, Any],
    prompt: str,
    *,
    capture_source: str,
    turn_id: str | None = None,
) -> str:
    """Persist a bounded direct prompt supplied by a trusted hook source."""

    session_dir = _session_dir(payload)
    resolved_turn_id = turn_id or _turn_id(payload)
    if session_dir is None or resolved_turn_id is None or not prompt.strip():
        return ""

    sanitized = _redact(prompt)
    stored_prompt, was_truncated = _excerpt(sanitized, MAX_STORED_PROMPT_CHARS)
    detected_resources = extract_resources(stored_prompt)
    resources = detected_resources[:MAX_RESOURCES_PER_BUNDLE]
    referenced_bundles = _recent_resource_bundles(session_dir) if _references_prior_resources(stored_prompt) else []
    session_id = _session_id(payload)
    record = {
        "schema_version": SCHEMA_VERSION,
        "kind": "mosim_direct_user_input",
        "capture_source": capture_source,
        "session_id": session_id,
        "turn_id": resolved_turn_id,
        "captured_at": _utc_now(),
        "prompt_sha256": hashlib.sha256(sanitized.encode("utf-8")).hexdigest(),
        "user_prompt": stored_prompt,
        "user_prompt_truncated": was_truncated,
        "resources": resources,
        "resources_detected_count": len(detected_resources),
        "resources_truncated": len(detected_resources) > len(resources),
        "referenced_resource_bundles": referenced_bundles,
    }
    _write_json(_record_path(session_dir, resolved_turn_id), record)

    active = _read_json(session_dir / "active.json")
    active.update(
        {
            "schema_version": SCHEMA_VERSION,
            "session_id": session_id,
            "active_turn_id": resolved_turn_id,
            "last_captured_turn_id": resolved_turn_id,
            "updated_at": _utc_now(),
        }
    )
    _write_json(session_dir / "active.json", active)
    _clear_pending_native_history_guards(session_dir)

    if resources:
        catalog = _load_catalog(session_dir)
        bundles = [bundle for bundle in catalog["bundles"] if bundle.get("turn_id") != resolved_turn_id]
        bundles.append(_catalog_entry(record))
        catalog["bundles"] = bundles[-MAX_RESOURCE_BUNDLES:]
        catalog["updated_at"] = _utc_now()
        _write_json(session_dir / "resource_catalog.json", catalog)

    _prune_turn_records(session_dir, resolved_turn_id)

    return render_prompt_context(record)


def capture_user_prompt(payload: dict[str, Any]) -> str:
    """Persist a bounded copy of the direct UserPromptSubmit input."""

    prompt = direct_user_prompt(payload)
    if is_generated_goal_context(prompt):
        return ""
    return _capture_direct_user_prompt(
        payload,
        prompt,
        capture_source="user_prompt_submit",
        turn_id=_capture_turn_id(payload, prompt) if prompt.strip() else None,
    )


def record_plan(payload: dict[str, Any]) -> None:
    """Capture the bounded plan state when Codex updates its local task plan."""

    session_dir = _session_dir(payload)
    turn_id = _turn_id(payload)
    tool_input = payload.get("tool_input")
    if session_dir is None or turn_id is None or not isinstance(tool_input, dict):
        return

    path = _record_path(session_dir, turn_id)
    record = _read_json(path)
    if not record:
        return

    raw_plan = tool_input.get("plan")
    steps: list[dict[str, str]] = []
    if isinstance(raw_plan, list):
        for item in raw_plan[:MAX_PLAN_STEPS]:
            if not isinstance(item, dict):
                continue
            step = _excerpt(_redact(_text(item.get("step"))), 180)[0]
            status = _excerpt(_redact(_text(item.get("status"))), 32)[0]
            if step:
                steps.append({"step": step, "status": status or "unknown"})

    explanation = _excerpt(_redact(_text(tool_input.get("explanation"))), 420)[0]
    record["plan_checkpoint"] = {
        "captured_at": _utc_now(),
        "source": "update_plan",
        "explanation": explanation,
        "steps": steps,
    }
    _write_json(path, record)


def _goal_from_tool_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Extract the model-facing goal result from supported local goal tools."""

    response = _mapping(payload.get("tool_response"))
    structured = _mapping(response.get("structuredContent"))
    candidates = [response.get("goal"), structured.get("goal"), response, structured]
    for candidate in candidates:
        if isinstance(candidate, dict) and _text(candidate.get("objective")):
            return candidate
    return {}


def _goal_checkpoint(session_dir: Path, active_only: bool = False) -> dict[str, Any] | None:
    active = _read_json(session_dir / "active.json")
    raw_checkpoint = active.get("goal_checkpoint")
    if not isinstance(raw_checkpoint, dict):
        return None

    objective = _text(raw_checkpoint.get("objective")).strip()
    status = _text(raw_checkpoint.get("status")).strip().lower() or "active"
    if not objective or (active_only and status != "active"):
        return None

    captured_at = _text(raw_checkpoint.get("captured_at"))
    source = _text(raw_checkpoint.get("source"))
    turn_id = _text(raw_checkpoint.get("turn_id"))
    checkpoint: dict[str, Any] = {
        "objective": objective,
        "status": status,
        "captured_at": captured_at,
        "source": source,
        "turn_id": turn_id,
    }
    token_budget = raw_checkpoint.get("token_budget")
    if isinstance(token_budget, int) and not isinstance(token_budget, bool):
        checkpoint["token_budget"] = token_budget
    elif token_budget is None and "token_budget" in raw_checkpoint:
        checkpoint["token_budget"] = None
    return checkpoint


def active_direct_user_prompt(payload: dict[str, Any]) -> str:
    """Return the latest captured direct prompt for a same-session hook event."""

    session_dir = _session_dir(payload)
    if session_dir is None:
        return ""
    active = _read_json(session_dir / "active.json")
    record, _ = _direct_record_for_turn(session_dir, _text(active.get("active_turn_id")))
    return _text(record.get("user_prompt")) if record is not None else ""


def record_goal(payload: dict[str, Any]) -> None:
    """Persist the active Goal-mode contract independently of a prompt pack."""

    session_dir = _session_dir(payload)
    if session_dir is None:
        return

    tool_input = _mapping(payload.get("tool_input"))
    returned_goal = _goal_from_tool_response(payload)
    existing = _goal_checkpoint(session_dir)

    objective = _text(returned_goal.get("objective")).strip() or _text(tool_input.get("objective")).strip()
    if not objective and existing:
        objective = existing["objective"]
    if not objective:
        return

    status = _text(returned_goal.get("status")).strip().lower() or _text(tool_input.get("status")).strip().lower()
    if not status and existing:
        status = existing["status"]
    if not status:
        status = "active"

    raw_budget: Any = None
    budget_recorded = False
    for candidate in (returned_goal, tool_input, existing or {}):
        for key in ("tokenBudget", "token_budget"):
            if key in candidate:
                raw_budget = candidate[key]
                budget_recorded = True
                break
        if budget_recorded:
            break

    checkpoint: dict[str, Any] = {
        "captured_at": _utc_now(),
        "source": _text(payload.get("tool_name")) or "goal_tool",
        "turn_id": _turn_id(payload) or "",
        "objective": _excerpt(_redact(objective), MAX_VISIBLE_GOAL_CHARS)[0],
        "status": status,
    }
    if isinstance(raw_budget, int) and not isinstance(raw_budget, bool):
        checkpoint["token_budget"] = raw_budget
    elif budget_recorded:
        checkpoint["token_budget"] = None
    active = _read_json(session_dir / "active.json")
    active["goal_checkpoint"] = checkpoint
    active["updated_at"] = _utc_now()
    _write_json(session_dir / "active.json", active)

    record, path = _direct_record_for_turn(session_dir, _text(active.get("active_turn_id")))
    if record is not None and path is not None:
        record["goal_checkpoint"] = checkpoint
        _write_json(path, record)


def mark_compaction(payload: dict[str, Any], stage: str) -> None:
    """Bind compaction to a direct prompt without confusing it with an execution turn."""

    session_dir = _session_dir(payload)
    if session_dir is None:
        return
    active = _read_json(session_dir / "active.json")
    execution_turn_id = _turn_id(payload)
    explicit_direct_turn_id = _compaction_direct_turn_id(payload)

    direct_turn_id: str | None = None
    recovery_source = "missing_direct_record"
    if explicit_direct_turn_id:
        if _direct_record_for_turn(session_dir, explicit_direct_turn_id)[0] is not None:
            direct_turn_id = explicit_direct_turn_id
            recovery_source = "explicit_direct_turn"
    elif _direct_record_for_turn(session_dir, execution_turn_id)[0] is not None:
        direct_turn_id = execution_turn_id
        recovery_source = "matching_direct_turn"
    elif execution_turn_id:
        # Codex currently supplies an assistant execution turn here, while
        # UserPromptSubmit supplies a different direct-user turn. Preserve the
        # latest stored direct input rather than overwriting it with the
        # execution id and forcing a false continuity_unresolved result.
        for candidate in (_text(active.get("active_turn_id")), _text(active.get("last_captured_turn_id"))):
            if _direct_record_for_turn(session_dir, candidate)[0] is not None:
                direct_turn_id = candidate
                recovery_source = "latest_direct_record"
                break

    current_turn_capture_missing = direct_turn_id is None
    if direct_turn_id:
        active["active_turn_id"] = direct_turn_id
    elif execution_turn_id:
        active["active_turn_id"] = execution_turn_id
    active["last_compaction"] = {
        "compaction_id": uuid.uuid4().hex,
        "stage": stage,
        "turn_id": execution_turn_id,
        "direct_turn_id": direct_turn_id or "",
        "recovery_source": recovery_source,
        "current_turn_capture_missing": current_turn_capture_missing,
        "trigger": _text(payload.get("trigger")),
        "recorded_at": _utc_now(),
    }
    active["updated_at"] = _utc_now()
    _write_json(session_dir / "active.json", active)


def compaction_lacks_current_turn_capture(payload: dict[str, Any]) -> bool:
    """Return whether a compacted direct-user turn lacks any safe local record."""

    session_dir = _session_dir(payload)
    if session_dir is None:
        return False
    compaction = _read_json(session_dir / "active.json").get("last_compaction")
    if not isinstance(compaction, dict):
        return False
    return bool(compaction.get("current_turn_capture_missing"))


def _claim_compaction_marker(session_dir: Path, compaction_id: str) -> bool:
    marker_dir = session_dir / "compactions"
    marker = marker_dir / f"{_safe_component(compaction_id, 'compaction')}.claimed"
    try:
        marker_dir.mkdir(parents=True, exist_ok=True)
        with marker.open("x", encoding="utf-8") as stream:
            stream.write(_utc_now() + "\n")
    except FileExistsError:
        return False
    except OSError:
        # Storage trouble must not suppress recovery; only successful claims
        # participate in de-duplication.
        return True

    try:
        markers = sorted(
            marker_dir.glob("*.claimed"),
            key=lambda path: (path.stat().st_mtime_ns, path.name),
        )
    except OSError:
        return True
    for stale in markers[:-MAX_COMPACTION_MARKERS]:
        try:
            stale.unlink()
        except OSError:
            continue
    return True


def _continuation_guard_dir(session_dir: Path) -> Path:
    return session_dir / "continuation_guards"


def _clear_pending_native_history_guards(session_dir: Path) -> None:
    """A newer direct user request supersedes any unclaimed compact fallback."""

    guard_dir = _continuation_guard_dir(session_dir)
    try:
        pending = list(guard_dir.glob("*.pending.json"))
    except OSError:
        return
    for path in pending:
        try:
            path.unlink()
        except OSError:
            continue
    _clear_pending_internal_continuations(session_dir)


def _internal_continuation_dir(session_dir: Path) -> Path:
    return session_dir / "internal_continuations"


def _prompt_digest(prompt: str) -> str:
    return hashlib.sha256(_redact(prompt).encode("utf-8")).hexdigest()


def _clear_pending_internal_continuations(session_dir: Path) -> None:
    try:
        pending = list(_internal_continuation_dir(session_dir).glob("*.pending.json"))
    except OSError:
        return
    for path in pending:
        try:
            path.unlink()
        except OSError:
            continue


def _prune_internal_continuation_markers(session_dir: Path) -> None:
    marker_dir = _internal_continuation_dir(session_dir)
    try:
        markers = sorted(
            [*marker_dir.glob("*.pending.json"), *marker_dir.glob("*.claimed")],
            key=lambda path: (path.stat().st_mtime_ns, path.name),
        )
    except OSError:
        return
    for stale in markers[:-MAX_INTERNAL_CONTINUATION_MARKERS]:
        try:
            stale.unlink()
        except OSError:
            continue


def arm_internal_continuation(payload: dict[str, Any], prompt: str) -> None:
    """Mark the one Stop-generated prompt so it cannot replace direct input."""

    session_dir = _session_dir(payload)
    prompt = prompt.strip()
    if session_dir is None or not prompt:
        return
    digest = _prompt_digest(prompt)
    marker_dir = _internal_continuation_dir(session_dir)
    _write_json(
        marker_dir / f"{digest}.pending.json",
        {
            "schema_version": SCHEMA_VERSION,
            "kind": "mosim_internal_continuation",
            "prompt_sha256": digest,
            "armed_turn_id": _turn_id(payload) or "",
            "armed_at": _utc_now(),
        },
    )
    _prune_internal_continuation_markers(session_dir)


def consume_internal_continuation(payload: dict[str, Any], prompt: str) -> bool:
    """Claim a known Stop-generated prompt without making it active input."""

    session_dir = _session_dir(payload)
    prompt = prompt.strip()
    if session_dir is None or not prompt:
        return False
    digest = _prompt_digest(prompt)
    pending = _internal_continuation_dir(session_dir) / f"{digest}.pending.json"
    marker = _read_json(pending)
    if marker.get("kind") != "mosim_internal_continuation":
        return False
    claimed = pending.with_name(f"{digest}.claimed")
    try:
        claimed.parent.mkdir(parents=True, exist_ok=True)
        with claimed.open("x", encoding="utf-8") as stream:
            stream.write(_utc_now() + "\n")
    except (FileExistsError, OSError):
        return False
    try:
        pending.unlink()
    except OSError:
        pass
    _prune_internal_continuation_markers(session_dir)
    return True


def _is_known_internal_continuation(session_dir: Path, prompt: str) -> bool:
    digest = _prompt_digest(prompt)
    marker_dir = _internal_continuation_dir(session_dir)
    return any(
        (marker_dir / f"{digest}{suffix}").is_file()
        for suffix in (".pending.json", ".claimed")
    )


def _read_transcript_tail(transcript_path: str) -> str:
    """Read a small tail of a hook-provided transcript without retaining it."""

    try:
        path = Path(transcript_path).expanduser()
        if not path.is_file():
            return ""
        size = path.stat().st_size
        with path.open("rb") as stream:
            start = max(0, size - MAX_TRANSCRIPT_TAIL_BYTES)
            stream.seek(start)
            raw = stream.read(MAX_TRANSCRIPT_TAIL_BYTES)
    except OSError:
        return ""

    text = raw.decode("utf-8", errors="replace")
    if start:
        separator = text.find("\n")
        text = text[separator + 1 :] if separator >= 0 else ""
    return text


def _transcript_user_prompt(record: dict[str, Any]) -> str | None:
    """Return a prompt only from a recognized direct-user transcript record."""

    payload = _mapping(record.get("payload"))
    item = _mapping(record.get("item"))
    candidates = (record, payload, item)
    for candidate in candidates:
        role = _text(candidate.get("role")).strip().lower()
        kind = _text(candidate.get("type")).strip().lower()
        if role != "user" and kind not in {"user_message", "usermessage"}:
            continue
        for key in ("content", "prompt", "user_prompt", "userPrompt", "input", "message"):
            prompt = _prompt_text(candidate.get(key)).strip()
            if prompt:
                return prompt
        return ""
    return None


def _latest_transcript_user_prompt(payload: dict[str, Any], session_dir: Path) -> str:
    transcript_path = _text(payload.get("transcript_path")).strip()
    if not transcript_path:
        return ""

    lines = _read_transcript_tail(transcript_path).splitlines()
    for line in reversed(lines[-MAX_TRANSCRIPT_LINES:]):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        prompt = _transcript_user_prompt(record)
        if prompt is None:
            continue
        # The latest recognized user entry must be the current direct input.
        # Never skip it to revive an earlier request from the transcript.
        if (
            not prompt
            or is_generated_goal_context(prompt)
            or _is_known_internal_continuation(session_dir, prompt)
        ):
            return ""
        return prompt
    return ""


def capture_transcript_user_prompt(payload: dict[str, Any]) -> str:
    """Recover one current direct prompt from a hook-provided transcript path.

    ``transcript_path`` is not a stable Codex interface, so this is deliberately
    a last-resort parser for known JSONL user-message records only.
    """

    session_dir = _session_dir(payload)
    if session_dir is None:
        return ""
    prompt = _latest_transcript_user_prompt(payload, session_dir)
    if not prompt:
        return ""

    active = _read_json(session_dir / "active.json")
    compaction = active.get("last_compaction")
    compacted_turn_id = _text(compaction.get("turn_id")) if isinstance(compaction, dict) else ""
    turn_id = compacted_turn_id or _turn_id(payload)
    if not turn_id:
        turn_id = f"transcript-{_prompt_digest(prompt)[:24]}"
    if not _capture_direct_user_prompt(
        payload,
        prompt,
        capture_source="transcript_path_fallback",
        turn_id=_safe_component(turn_id, "transcript-turn"),
    ):
        return ""
    return render_compact_context(payload)


def _compaction_id(payload: dict[str, Any]) -> str:
    session_dir = _session_dir(payload)
    if session_dir is None:
        return ""
    active = _read_json(session_dir / "active.json")
    compaction = active.get("last_compaction")
    if isinstance(compaction, dict):
        value = _text(compaction.get("compaction_id"))
        if value:
            return _safe_component(value, "compaction")

    session_id = _session_id(payload)
    turn_id = _turn_id(payload) or "unknown-turn"
    digest = hashlib.sha256(f"{session_id}:{turn_id}".encode("utf-8")).hexdigest()[:24]
    return f"compact-{digest}"


def arm_native_history_guard(payload: dict[str, Any]) -> None:
    """Require one bounded current-thread recovery pass when no pack exists."""

    session_dir = _session_dir(payload)
    if session_dir is None:
        return
    compaction_id = _compaction_id(payload)
    if not compaction_id:
        return

    guard_dir = _continuation_guard_dir(session_dir)
    guard_path = guard_dir / f"{compaction_id}.pending.json"
    _write_json(
        guard_path,
        {
            "schema_version": SCHEMA_VERSION,
            "kind": "mosim_native_history_guard",
            "compaction_id": compaction_id,
            "armed_turn_id": _turn_id(payload) or "",
            "armed_at": _utc_now(),
        },
    )

    try:
        guards = sorted(
            guard_dir.glob("*.pending.json"),
            key=lambda path: (path.stat().st_mtime_ns, path.name),
        )
    except OSError:
        return
    for stale in guards[:-MAX_CONTINUATION_GUARDS]:
        try:
            stale.unlink()
        except OSError:
            continue


def consume_native_history_guard(payload: dict[str, Any]) -> bool:
    """Claim the current compact fallback exactly once for the active session."""

    session_dir = _session_dir(payload)
    if session_dir is None:
        return False
    guard_dir = _continuation_guard_dir(session_dir)
    compaction_id = _compaction_id(payload)
    pending = guard_dir / f"{compaction_id}.pending.json" if compaction_id else None
    if pending is None or not pending.is_file():
        try:
            pending_guards = sorted(
                guard_dir.glob("*.pending.json"),
                key=lambda path: (path.stat().st_mtime_ns, path.name),
            )
        except OSError:
            return False
        pending = pending_guards[-1] if pending_guards else None
    if pending is None:
        return False

    guard = _read_json(pending)
    if guard.get("kind") != "mosim_native_history_guard":
        return False

    # SessionStart and Stop are scoped to the same session, but Codex does not
    # promise that they share a turn ID after compaction. The per-compaction
    # claim below is the loop-prevention boundary.
    guard_id = _safe_component(_text(guard.get("compaction_id")), pending.stem)
    claimed = guard_dir / f"{guard_id}.claimed"
    try:
        guard_dir.mkdir(parents=True, exist_ok=True)
        with claimed.open("x", encoding="utf-8") as stream:
            stream.write(_utc_now() + "\n")
    except (FileExistsError, OSError):
        return False
    return True


def consume_compact_context(
    payload: dict[str, Any], *, allow_latest_direct_record: bool = True
) -> str | None:
    """Return one recovery injection per marked compaction, or ``None`` if claimed."""

    session_dir = _session_dir(payload)
    if session_dir is None:
        return ""
    active = _read_json(session_dir / "active.json")
    compaction = active.get("last_compaction")
    direct_turn_id = _text(compaction.get("direct_turn_id")) if isinstance(compaction, dict) else ""
    recovery_source = _text(compaction.get("recovery_source")) if isinstance(compaction, dict) else ""
    last_captured_turn_id = _text(active.get("last_captured_turn_id"))
    active_turn_id = _text(active.get("active_turn_id"))
    # Older hook versions replaced active_turn_id with the assistant execution
    # ID even when no direct-input record existed for that ID. Detect only that
    # legacy shape so it can be repaired without weakening an explicit newer
    # direct-user turn boundary.
    legacy_execution_pointer = (
        not direct_turn_id
        and isinstance(compaction, dict)
        and "direct_turn_id" not in compaction
        and "recovery_source" not in compaction
        and active_turn_id
        and last_captured_turn_id
        and active_turn_id != last_captured_turn_id
        and _direct_record_for_turn(session_dir, active_turn_id)[0] is None
    )
    if direct_turn_id and last_captured_turn_id and direct_turn_id != last_captured_turn_id:
        # A newer direct submission won the race with compaction. Its normal
        # UserPromptSubmit context is authoritative, so do not inject stale
        # recovery context for the previous execution turn.
        return None
    if recovery_source == "latest_direct_record" and not allow_latest_direct_record:
        return ""

    record, _ = _direct_record_for_turn(session_dir, direct_turn_id)
    if record is None and not direct_turn_id:
        for candidate in (active_turn_id, last_captured_turn_id):
            record, _ = _direct_record_for_turn(session_dir, candidate)
            if record is not None:
                break
    if record is None:
        return ""

    if legacy_execution_pointer:
        restored_turn_id = _text(record.get("turn_id"))
        if restored_turn_id:
            active["active_turn_id"] = restored_turn_id
            compaction["direct_turn_id"] = restored_turn_id
            compaction["recovery_source"] = "legacy_latest_direct_record"
            compaction["current_turn_capture_missing"] = False
            active["last_compaction"] = compaction
            active["updated_at"] = _utc_now()
            _write_json(session_dir / "active.json", active)

    compaction_id = _text(compaction.get("compaction_id")) if isinstance(compaction, dict) else ""
    if compaction_id and not _claim_compaction_marker(session_dir, compaction_id):
        return None
    return render_compact_context(payload)


def _resource_lines(resources: Any, prefix: str = "") -> list[str]:
    if not isinstance(resources, list):
        return []
    lines: list[str] = []
    for resource in resources[:MAX_VISIBLE_RESOURCES]:
        if not isinstance(resource, dict):
            continue
        identifier = _text(resource.get("id")) or "user-source"
        value = _text(resource.get("value"))
        if value:
            lines.append(f"- {prefix}[{identifier}] {value}")
    return lines


def render_prompt_context(record: dict[str, Any]) -> str:
    resources = _resource_lines(record.get("resources"))
    referenced = record.get("referenced_resource_bundles")
    lines: list[str] = [
        "[MoSim Goal bootstrap]",
        "For a new non-trivial direct-user task, establish or refresh a same-session Goal when Goal mode is exposed, with an outcome, constraints, and verification. Do not create a duplicate active Goal; do not let Goal state override a newer direct user instruction.",
    ]
    if resources:
        lines.extend(
            [
            "[MoSim exact user-source capture]",
            "The following URLs/paths were supplied in this direct user prompt. They are source identities, not local saved copies.",
            *resources,
            ]
        )
        if record.get("resources_truncated"):
            lines.append("This bounded manifest omitted additional direct resources; inspect the direct prompt pack or ask the user instead of guessing them.")

    if isinstance(referenced, list) and referenced:
        lines.extend(
            [
                "[MoSim recent user-source inventory]",
                "The user refers to earlier resources. These are reference-only and must not select or revive an old task.",
            ]
        )
        for bundle in referenced:
            if not isinstance(bundle, dict):
                continue
            lines.extend(_resource_lines(bundle.get("resources"), prefix=f"turn {bundle.get('turn_id', 'unknown')} "))
            if bundle.get("resources_truncated"):
                lines.append(f"- turn {bundle.get('turn_id', 'unknown')} has additional bounded-out resources; do not infer them.")
    if is_continuity_diagnosis(_text(record.get("user_prompt"))):
        lines.extend(
            [
                "[MoSim Continuity Diagnosis]",
                "The newest direct user request asks why execution stopped. Treat that diagnosis as an independently executable task: inspect the active recovery hook and task-continuity rules before asking for a source from the interrupted work. Do not use the diagnosis to revive or modify that interrupted business task.",
            ]
        )
    if lines:
        lines.append("Do not replace sources with similarly named repository files or infer their identity from timestamps or memory.")
    return "\n".join(lines)


def _relative_path(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def render_compact_context(payload: dict[str, Any]) -> str:
    """Build compact continuation context from a previous UserPromptSubmit capture."""

    session_dir = _session_dir(payload)
    if session_dir is None:
        return ""
    active = _read_json(session_dir / "active.json")
    record, record_path = _direct_record_for_turn(session_dir, _text(active.get("active_turn_id")))
    if record is None or record_path is None:
        return ""

    prompt_excerpt, _ = _excerpt(_text(record.get("user_prompt")), MAX_VISIBLE_PROMPT_CHARS)
    capture_source = _text(record.get("capture_source"))
    capture_description = (
        "This is a bounded fallback extracted from the hook-provided transcript_path after UserPromptSubmit capture was unavailable. It accepts only the latest recognized direct-user JSONL record; its format is not a stable Codex hook interface. It identifies scope and source references only; a newer direct user message always wins."
        if capture_source == "transcript_path_fallback"
        else "This is a bounded pre-compaction capture of the active direct-user input. It identifies scope and source references only; a newer direct user message always wins."
    )
    lines = [
        "[MoSim Task Recovery Pack]",
        capture_description,
        f"Pack: {_relative_path(record_path)}",
        "Direct user input:",
        prompt_excerpt,
    ]
    continuity_diagnosis = is_continuity_diagnosis(_text(record.get("user_prompt")))
    if continuity_diagnosis:
        lines.extend(
            [
                "[MoSim Continuity Diagnosis]",
                "The newest direct user request asks why execution stopped. Treat that diagnosis as an independently executable task: inspect the active recovery hook and task-continuity rules before asking for a source from the interrupted work. Do not use the diagnosis to revive or modify that interrupted business task.",
            ]
        )

    resource_lines = _resource_lines(record.get("resources"))
    if resource_lines:
        lines.extend(["Exact user-supplied resources:", *resource_lines])
        if record.get("resources_truncated"):
            lines.append("Additional direct resources exceeded the bounded manifest; inspect Pack or ask the user instead of inferring them.")

    referenced = record.get("referenced_resource_bundles")
    if isinstance(referenced, list) and referenced:
        lines.append("Earlier resource bundles referenced by this direct input (reference-only; never task authority):")
        for bundle in referenced:
            if isinstance(bundle, dict):
                lines.extend(_resource_lines(bundle.get("resources"), prefix=f"turn {bundle.get('turn_id', 'unknown')} "))
                if bundle.get("resources_truncated"):
                    lines.append(f"- turn {bundle.get('turn_id', 'unknown')} has additional bounded-out resources; do not infer them.")

    checkpoint = record.get("plan_checkpoint")
    if isinstance(checkpoint, dict):
        lines.append("Task tracking checkpoint (non-authoritative):")
        explanation = _text(checkpoint.get("explanation"))
        if explanation:
            lines.append(f"- {explanation}")
        for step in checkpoint.get("steps", []):
            if isinstance(step, dict) and _text(step.get("step")):
                lines.append(f"- [{_text(step.get('status'))}] {_text(step.get('step'))}")

    if continuity_diagnosis:
        lines.append("Do not request a missing source from the interrupted work merely to perform this diagnosis.")
    else:
        lines.append(
            "Before asking the user for a requested source absent from this pack, use `codex_app__read_thread` only for the current thread when that capability is exposed. Ask only if that bounded read does not recover the source."
        )
    lines.append("Never infer a user-supplied source from repository files, import times, memory, or a broad search.")
    context, _ = _excerpt("\n".join(lines), MAX_VISIBLE_CONTEXT_CHARS)
    return context
