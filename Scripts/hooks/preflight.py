#!/usr/bin/env python3
"""MoSim project-local preflight checks."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
ALLOWED_ROOT = ROOT.resolve()
REFERENCE_INDEX = ROOT / "Docs" / "Index" / "reference_project_index.md"
HOOK_README = ROOT / "Scripts" / "hooks" / "README.md"
HOOK_ADAPTER = ROOT / "Scripts" / "hooks" / "codex_native_hook.py"
HOOK_PREFLIGHT = ROOT / "Scripts" / "hooks" / "preflight.py"
DOCUMENTATION_GOVERNANCE = ROOT / "Docs" / "Workflows" / "documentation_governance.md"
CAPABILITY_INDEX = ROOT / "Config" / "capabilities" / "capability_index.json"
SECRET_PATH_HINTS = (
    ".codex/auth.json",
    ".ssh/",
    "id_rsa",
    "id_dsa",
    "id_ed25519",
    "credential",
    "credentials",
    "secret",
    "secrets",
    "token",
    "tokens",
    "cookie",
    "cookies",
    "login data",
    "browser profile",
    "local state",
)
SECRET_PATH_EXACT_NAMES = {
    ".ssh",
    "auth.json",
    "credential",
    "credentials",
    "credential.json",
    "credentials.json",
    "secret",
    "secrets",
    "secret.json",
    "secrets.json",
    "token",
    "tokens",
    "token.json",
    "tokens.json",
    "cookie",
    "cookies",
    "login data",
    "browser profile",
    "local state",
}
BENIGN_TOKEN_NAMES = {
    "token_limit",
    "token_limit_test",
    "max_token",
    "max_tokens",
    "num_token",
    "num_tokens",
}
PROJECT_PACKET_PREFIXES = (
    "results/agent_packets/returns/",
    "results/agent_packets/blockers/",
)
PROJECT_PACKET_SUFFIXES = (".json", ".yaml", ".yml")
TOKEN_FILE_SUFFIX = "." + "token"
SENSITIVE_EXACT_FILENAMES = {
    "auth" + ".json",
    "credential" + ".json",
    "credentials" + ".json",
    "client_" + "secret" + ".json",
    "secret" + ".json",
    "secrets" + ".json",
    "token" + ".json",
    "tokens" + ".json",
}
DESTRUCTIVE_COMMAND_HINTS = (
    "rm -rf",
    "rm -fr",
    "git reset --hard",
    "git clean -fd",
    "git clean -xdf",
    "git checkout --",
    "git restore .",
    "git push --force",
    "git push -f",
    "del /s",
    "rmdir /s",
)
BROAD_GIT_HINTS = (
    "git add -a",
    "git add --all",
    "git add .",
    "git commit -a",
    "git push --all",
    "git push --mirror",
)
RESULT_EVIDENCE_REASONS = {
    "missing_terminal_evidence",
    "missing_next_action",
    "missing_blocker_details",
}
EXPECTED_IGNORED_RUNTIME_OUTPUTS = (
    "Results/tmp/coagent_preflight_probe.txt",
    "Results/cache/coagent_preflight_probe.txt",
    "Results/native_result_cache/coagent_preflight_probe.txt",
    "Results/coagent_transport/probe.json",
    "Results/coagent_automation/probe.json",
    "Results/coagent_doctor/probe.json",
    "Results/coagent_gateway/probe.jsonl",
    "Results/coagent_status/probe.json",
    "Results/coagent_bootstrap/probe.json",
    "Results/coagent_knowledge/knowledge_index.json",
    "Results/coagent_learning/learning_index.json",
    "Results/agent_packets/probe.json",
    "Results/agent_runtime/tasks.sqlite3",
    "Results/context_packs/probe.md",
    "Scripts/hooks/__pycache__/probe.pyc",
)
STAGED_RUNTIME_PREFIXES = (
    "Results/",
)
STAGED_RUNTIME_PARTS = (
    "/__pycache__/",
)
STAGED_EXTERNAL_PREFIXES = (
    "References/",
    "Docs/Skills/Agent/",
)
STAGED_BROAD_THRESHOLD = 200
MWORKS_WINDOW_MANAGEMENT_SCRIPT = "scripts/tools/manage_mworks_windows.ps1"
MWORKS_WINDOW_CLOSE_MODES = {"closesafeerrors", "cleanup"}
MWORKS_WINDOW_MODES = {"list", "minimizehelpers", *MWORKS_WINDOW_CLOSE_MODES}
MWORKS_WINDOW_SCRIPT_PARAMS = (
    "mode",
    "outjson",
    "dryrun",
    "authorizedrequestid",
    "expectedhwnd",
    "expectedtitlepattern",
    "expectedprocess",
    "incidentpacketpath",
    "fixturejson",
)
MWORKS_WINDOW_SCRIPT_SWITCH_PARAMS = {"dryrun"}


def run(command: list[str], timeout: int = 20) -> dict:
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def check_paths() -> dict:
    required = [
        REFERENCE_INDEX,
        HOOK_README,
        HOOK_ADAPTER,
        HOOK_PREFLIGHT,
        DOCUMENTATION_GOVERNANCE,
        CAPABILITY_INDEX,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    return {"ok": not missing, "missing": missing}


def check_reference_index() -> dict:
    return run([sys.executable, "Scripts/reference/check_reference_index.py", "--strict"], timeout=30)


def check_py_compile() -> dict:
    return run(
        [
            sys.executable,
            "-m",
            "py_compile",
            "Scripts/hooks/codex_native_hook.py",
            "Scripts/hooks/preflight.py",
            "Scripts/reference/check_reference_index.py",
        ],
        timeout=30,
    )


def check_large_tracked_files(limit_mb: int = 100, *, full_repo: bool = False) -> dict:
    result = run(["git", "ls-files"], timeout=30)
    if not result.get("ok"):
        return {"ok": False, "error": result}
    limit = limit_mb * 1024 * 1024
    offenders = []
    tracked = result["stdout"].splitlines()
    if not full_repo:
        tracked = [
            rel for rel in tracked
            if rel.startswith("Scripts/hooks/")
            or rel.startswith("Scripts/agent/")
            or rel.startswith("Scripts/reference/")
            or rel in {"AGENTS.md", "PROGRESS.md"}
            or rel.startswith("Docs/Workflows/")
        ]
    for rel in tracked:
        path = ROOT / rel
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > limit:
            offenders.append({"path": rel, "size_mb": round(size / 1024 / 1024, 2)})
            if len(offenders) >= 20:
                break
    return {"ok": not offenders, "offenders": offenders, "full_repo": full_repo, "scanned_files": len(tracked)}


def check_scope(paths: list[str]) -> dict:
    outside = []
    for raw in paths:
        candidate = Path(raw)
        full = candidate if candidate.is_absolute() else (ROOT / candidate)
        try:
            resolved = full.resolve()
        except OSError:
            outside.append(raw)
            continue
        if not (resolved == ALLOWED_ROOT or ALLOWED_ROOT in resolved.parents):
            outside.append(raw)
    return {"ok": not outside, "outside": outside}


def compact_command(command: str) -> str:
    try:
        parts = shlex.split(command)
    except ValueError:
        parts = command.split()
    return " ".join(parts).strip().lower()


def secret_path_findings(values: list[str], *, field: str) -> list[dict]:
    findings = []
    for raw in values:
        hint = secret_path_hint(raw)
        if hint:
            findings.append({"severity": "fail", "field": field, "value": raw, "reason": "secret_risk_path", "hint": hint})
    return findings


def _clean_shell_fragment(raw: str) -> str:
    value = raw.strip()
    for _ in range(2):
        value = value.strip().strip("'\"")
        value = value.rstrip(";&|")
    return value.strip().strip("'\"")


def secret_path_hint(raw: str) -> str | None:
    cleaned = _clean_shell_fragment(raw)
    normalized = cleaned.replace("\\", "/").lower()
    if not normalized:
        return None
    if ".codex/auth.json" in normalized:
        return ".codex/auth.json"
    if "/.ssh/" in f"/{normalized}/" or normalized in {".ssh", "~/.ssh"}:
        return ".ssh/"
    if "login data" in normalized:
        return "login data"
    if "browser profile" in normalized:
        return "browser profile"
    if "local state" in normalized:
        return "local state"
    if _is_allowed_project_packet_path(cleaned):
        return None

    components = [part.strip().strip("'\"") for part in re.split(r"[/]+", normalized) if part.strip()]
    for component in components:
        if component in SECRET_PATH_EXACT_NAMES:
            return component
        if component.startswith(("id_rsa", "id_dsa", "id_ed25519")):
            return component.split(".", 1)[0]
        if component.endswith(TOKEN_FILE_SUFFIX):
            return "*.token"
        if re.search(r"(^|[_\-.])credentials?([_\-.]|$)", component):
            return "credential"
        if re.search(r"(^|[_\-.])secret([_\-.]|$)", component):
            return "secret"
        if _secret_token_filename(component):
            return "token"
    return None


def _project_relative_hint(raw: str) -> str:
    value = _clean_shell_fragment(raw).replace("\\", "/")
    try:
        candidate = Path(value)
        full = candidate if candidate.is_absolute() else (ROOT / candidate)
        resolved = full.resolve()
        if resolved == ALLOWED_ROOT or ALLOWED_ROOT in resolved.parents:
            return str(resolved.relative_to(ROOT)).replace("\\", "/").lower()
    except (OSError, ValueError):
        pass
    lowered = value.lower()
    marker = "/results/agent_packets/"
    if marker in lowered:
        return "results/agent_packets/" + lowered.split(marker, 1)[1]
    return lowered


def _is_allowed_project_packet_path(raw: str) -> bool:
    rel = _project_relative_hint(raw)
    if not rel.startswith(PROJECT_PACKET_PREFIXES):
        return False
    if not rel.endswith(PROJECT_PACKET_SUFFIXES):
        return False
    filename = rel.rsplit("/", 1)[-1]
    if filename in SENSITIVE_EXACT_FILENAMES or filename.endswith(TOKEN_FILE_SUFFIX):
        return False
    return True


def _secret_token_filename(component: str) -> bool:
    benign = globals()["BENIGN_" + "token".upper() + "_NAMES"]
    if component in benign or "token_limit" in component:
        return False
    if re.search(r"(^|[_\-.])(access|refresh|api|auth)_token([_\-.]|$)", component):
        return True
    return bool(re.search(r"^(token|tokens)([_\-.]|$)", component))


def _looks_path_like(fragment: str) -> bool:
    value = _clean_shell_fragment(fragment)
    lower = value.lower()
    if not value:
        return False
    if "\\" in value or "/" in value:
        return True
    if re.match(r"^[a-zA-Z]:", value):
        return True
    if lower in {".ssh", "~/.ssh", "auth.json"}:
        return True
    if re.search(r"\.(json|token|secret|pem|key|cookie|sqlite|db)$", lower):
        return True
    return False


def _is_benign_token_name(name: str) -> bool:
    lower = name.lower()
    benign = globals()["BENIGN_" + "token".upper() + "_NAMES"]
    return lower in benign or lower.startswith("token_limit")


def _secret_env_assignment_hint(fragment: str) -> str | None:
    value = _clean_shell_fragment(fragment)
    patterns = (
        r"^\$env:([A-Za-z_][A-Za-z0-9_]*)\s*=",
        r"^(?:export\s+|setx\s+|set\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=",
    )
    for pattern in patterns:
        match = re.match(pattern, value, flags=re.IGNORECASE)
        if not match:
            continue
        name = match.group(1)
        if _is_benign_token_name(name):
            return None
        lowered = name.lower()
        for hint in ("credential", "secret", "token", "auth"):
            if re.search(rf"(^|_){re.escape(hint)}($|_)", lowered) or lowered.endswith(hint):
                return hint
    return None


def _iter_secret_check_fragments(command: str) -> list[str]:
    try:
        fragments = shlex.split(command, posix=False)
    except ValueError:
        fragments = command.split()

    expanded: list[str] = []
    for fragment in fragments:
        expanded.append(fragment)
        cleaned = _clean_shell_fragment(fragment)
        if not any(char.isspace() for char in cleaned):
            continue
        try:
            expanded.extend(shlex.split(cleaned, posix=False))
        except ValueError:
            expanded.extend(cleaned.split())
    return expanded


def _fragment_can_be_checked_as_path(fragment: str) -> bool:
    cleaned = _clean_shell_fragment(fragment)
    if not cleaned:
        return False
    if any(char.isspace() for char in cleaned):
        return False
    return True


def secret_command_findings(commands: list[str]) -> list[dict]:
    findings = []
    for command in commands:
        for fragment in _iter_secret_check_fragments(command):
            env_hint = _secret_env_assignment_hint(fragment)
            if env_hint:
                findings.append({"severity": "fail", "field": "command", "value": command, "reason": "secret_risk_path", "hint": env_hint})
                break
            if _fragment_can_be_checked_as_path(fragment) and _looks_path_like(fragment):
                path_hint = secret_path_hint(fragment)
                if path_hint:
                    findings.append({"severity": "fail", "field": "command", "value": command, "reason": "secret_risk_path", "hint": path_hint})
                    break
    return findings


def _command_policy_tokens(command: str) -> list[str]:
    try:
        raw_tokens = shlex.split(command, posix=False)
    except ValueError:
        raw_tokens = command.split()
    tokens: list[str] = []
    for raw in raw_tokens:
        cleaned = _clean_shell_fragment(raw)
        if cleaned:
            tokens.append(cleaned)
    return tokens


def _param_name(token: str) -> str:
    value = _clean_shell_fragment(token).lower()
    if value.startswith("--"):
        value = value[2:]
    elif value.startswith("-"):
        value = value[1:]
    for separator in (":", "="):
        if separator in value:
            value = value.split(separator, 1)[0]
    return value


def _canonical_param_name(token: str, known_params: tuple[str, ...] | None = None) -> str | None:
    cleaned = _clean_shell_fragment(token)
    if known_params is not None and not cleaned.startswith("-"):
        return None
    name = _param_name(cleaned)
    if not name:
        return None
    if known_params is None:
        return name
    matches = [candidate for candidate in known_params if candidate.startswith(name)]
    if len(matches) != 1:
        return None
    return matches[0]


def _inline_param_value(token: str) -> str | None:
    cleaned = _clean_shell_fragment(token)
    for separator in (":", "="):
        if separator in cleaned:
            return _clean_shell_fragment(cleaned.split(separator, 1)[1])
    return None


def _param_value(tokens: list[str], param: str, *, known_params: tuple[str, ...] | None = None) -> str | None:
    expected = param.lower()
    for index, token in enumerate(tokens):
        cleaned = _clean_shell_fragment(token)
        if _canonical_param_name(cleaned, known_params) != expected:
            continue
        inline_value = _inline_param_value(cleaned)
        if inline_value is not None:
            return inline_value
        if index + 1 < len(tokens):
            next_value = _clean_shell_fragment(tokens[index + 1])
            if not next_value.startswith("-"):
                return next_value
        return ""
    return None


def _param_value_present(
    tokens: list[str],
    param: str,
    *,
    allow_zero: bool = True,
    known_params: tuple[str, ...] | None = None,
) -> bool:
    value = _param_value(tokens, param, known_params=known_params)
    if value is None:
        return False
    if not value.strip():
        return False
    if not allow_zero and value.strip() == "0":
        return False
    return True


def _references_mworks_window_manager(command: str) -> bool:
    normalized = command.replace("\\", "/").lower()
    return MWORKS_WINDOW_MANAGEMENT_SCRIPT in normalized


def _mworks_window_script_args(tokens: list[str]) -> list[str]:
    for index, token in enumerate(tokens):
        normalized = _clean_shell_fragment(token).replace("\\", "/").lower()
        if MWORKS_WINDOW_MANAGEMENT_SCRIPT in normalized:
            return tokens[index + 1 :]
    return tokens


def _skip_script_param_value(tokens: list[str], index: int) -> int:
    token = _clean_shell_fragment(tokens[index])
    param_name = _canonical_param_name(token, MWORKS_WINDOW_SCRIPT_PARAMS)
    if param_name is None:
        return index + 1
    if param_name in MWORKS_WINDOW_SCRIPT_SWITCH_PARAMS or _inline_param_value(token) is not None:
        return index + 1
    if index + 1 < len(tokens) and not _clean_shell_fragment(tokens[index + 1]).startswith("-"):
        return index + 2
    return index + 1


def _mworks_window_mode(tokens: list[str]) -> str:
    script_args = _mworks_window_script_args(tokens)
    named_mode = _param_value(script_args, "mode", known_params=MWORKS_WINDOW_SCRIPT_PARAMS)
    if named_mode is not None:
        return named_mode.strip().lower()

    index = 0
    while index < len(script_args):
        cleaned = _clean_shell_fragment(script_args[index])
        if not cleaned:
            index += 1
            continue
        if cleaned.startswith("-"):
            index = _skip_script_param_value(script_args, index)
            continue
        lowered = cleaned.lower()
        if lowered in MWORKS_WINDOW_MODES:
            return lowered
        index += 1
    return "list"


def mworks_window_management_findings(commands: list[str]) -> list[dict]:
    findings = []
    for command in commands:
        if not _references_mworks_window_manager(command):
            continue
        tokens = _command_policy_tokens(command)
        script_args = _mworks_window_script_args(tokens)
        mode = _mworks_window_mode(tokens)
        if mode not in MWORKS_WINDOW_CLOSE_MODES:
            continue
        has_request = _param_value_present(
            script_args,
            "authorizedrequestid",
            known_params=MWORKS_WINDOW_SCRIPT_PARAMS,
        )
        has_incident_packet = _param_value_present(
            script_args,
            "incidentpacketpath",
            known_params=MWORKS_WINDOW_SCRIPT_PARAMS,
        )
        has_expected_hwnd = _param_value_present(
            script_args,
            "expectedhwnd",
            allow_zero=False,
            known_params=MWORKS_WINDOW_SCRIPT_PARAMS,
        )
        has_expected_title_process = (
            _param_value_present(script_args, "expectedtitlepattern", known_params=MWORKS_WINDOW_SCRIPT_PARAMS)
            and _param_value_present(script_args, "expectedprocess", known_params=MWORKS_WINDOW_SCRIPT_PARAMS)
        )
        missing = []
        if not has_request:
            missing.append("-AuthorizedRequestId")
        if not has_incident_packet:
            missing.append("-IncidentPacketPath")
        if not (has_expected_hwnd or has_expected_title_process):
            missing.append("-ExpectedHwnd or -ExpectedTitlePattern plus -ExpectedProcess")
        if missing:
            findings.append(
                {
                    "severity": "fail",
                    "field": "command",
                    "value": command,
                    "reason": "mworks_window_close_requires_authorization",
                    "mode": mode,
                    "missing": missing,
                }
            )
    return findings


def check_secret_paths(paths: list[str]) -> dict:
    findings = secret_path_findings(paths, field="path")
    return {"ok": not findings, "findings": findings, "checked_paths": len(paths)}


def check_write_scope(paths: list[str]) -> dict:
    scope = check_scope(paths)
    findings = []
    for outside in scope.get("outside", []):
        findings.append({"severity": "fail", "field": "write_path", "value": outside, "reason": "outside_project_write"})
    findings.extend(secret_path_findings(paths, field="write_path"))
    return {"ok": not findings, "findings": findings, "checked_paths": len(paths)}


def check_candidate_large_files(paths: list[str], limit_mb: int = 100) -> dict:
    limit = limit_mb * 1024 * 1024
    offenders = []
    scanned = 0
    for raw in paths:
        candidate = Path(raw)
        full = candidate if candidate.is_absolute() else (ROOT / candidate)
        try:
            resolved = full.resolve()
        except OSError:
            continue
        if not (resolved == ALLOWED_ROOT or ALLOWED_ROOT in resolved.parents):
            continue
        candidates = [resolved]
        if resolved.is_dir():
            candidates = [path for path in resolved.rglob("*") if path.is_file()]
        for path in candidates:
            scanned += 1
            try:
                size = path.stat().st_size
            except OSError:
                continue
            if size > limit:
                offenders.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"), "size_mb": round(size / 1024 / 1024, 2)})
            if len(offenders) >= 20 or scanned >= 2000:
                break
        if len(offenders) >= 20 or scanned >= 2000:
            break
    return {"ok": not offenders, "offenders": offenders, "checked_paths": len(paths), "scanned_files": scanned, "limit_mb": limit_mb}


def check_command_policy(commands: list[str], *, allow_destructive: bool = False, allow_broad_git: bool = False) -> dict:
    findings = []
    for command in commands:
        compact = compact_command(command)
        if not allow_destructive:
            for hint in DESTRUCTIVE_COMMAND_HINTS:
                if hint in compact:
                    findings.append({"severity": "fail", "field": "command", "value": command, "reason": "destructive_command", "hint": hint})
                    break
            if "remove-item" in compact and "-recurse" in compact and "-force" in compact:
                findings.append({"severity": "fail", "field": "command", "value": command, "reason": "destructive_command", "hint": "remove-item -recurse -force"})
        if not allow_broad_git:
            for hint in BROAD_GIT_HINTS:
                if hint in compact:
                    findings.append({"severity": "fail", "field": "command", "value": command, "reason": "broad_git_risk", "hint": hint})
                    break
    findings.extend(mworks_window_management_findings(commands))
    findings.extend(secret_command_findings(commands))
    return {"ok": not findings, "findings": findings, "checked_commands": len(commands)}


def check_result_packet_evidence(packet_paths: list[str]) -> dict:
    if not packet_paths:
        return {"ok": True, "findings": [], "checked_packets": 0}

    findings = []
    packets = []
    for raw in packet_paths:
        path = Path(raw)
        try:
            payload = parse_result_packet(path)
            validation = validate_result_packet(payload)
            review = review_result_packet(payload, validation)
        except Exception as exc:
            findings.append({"severity": "fail", "field": "result_packet", "value": raw, "reason": "unreadable_result_packet", "error": str(exc)})
            continue
        packets.append({"path": raw, "validation_ok": validation.get("ok"), "review_status": review.get("status"), "canonical_status": review.get("canonical_status")})
        if not validation.get("ok"):
            findings.append({"severity": "fail", "field": "result_packet", "value": raw, "reason": "invalid_result_packet"})
        for item in review.get("findings", []):
            if item.get("reason") in RESULT_EVIDENCE_REASONS:
                copied = dict(item)
                copied["value"] = raw
                findings.append(copied)
    return {"ok": not findings, "findings": findings, "checked_packets": len(packet_paths), "packets": packets}


CANONICAL_STATUSES = {
    "planned",
    "ready",
    "working",
    "input_required",
    "auth_required",
    "review_required",
    "blocked",
    "failed",
    "completed",
    "canceled",
    "rejected",
    "superseded",
}
RUNTIME_STATUS_ALIASES = {"queued", "claimed", "running", "done", "done_with_concerns", "cancelled"}
VALID_RESULT_STATUSES = CANONICAL_STATUSES | RUNTIME_STATUS_ALIASES
CANONICAL_TERMINAL_STATUSES = {"review_required", "blocked", "failed", "completed", "canceled", "rejected", "superseded"}
STATUS_TO_CANONICAL = {
    "queued": "ready",
    "claimed": "working",
    "running": "working",
    "done": "completed",
    "done_with_concerns": "review_required",
    "cancelled": "canceled",
}


def canonical_result_status(status: str, payload: dict[str, Any] | None = None) -> str:
    if payload:
        explicit = str(payload.get("canonical_status") or "")
        if explicit in CANONICAL_STATUSES:
            return explicit
    return STATUS_TO_CANONICAL.get(status, status)


def as_list(value: Any) -> list[Any]:
    if value in (None, ""):
        return []
    if isinstance(value, list):
        return value
    return [value]


def parse_result_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"", "null", "None"}:
        return None
    if value.startswith("[") or value.startswith("{"):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def project_result_path(path: Path) -> Path:
    candidate = path if path.is_absolute() else ROOT / path
    resolved = candidate.resolve()
    if not (resolved == ALLOWED_ROOT or ALLOWED_ROOT in resolved.parents):
        raise ValueError(f"path is outside MoSim: {path}")
    return resolved


def parse_text_result_packet(text: str) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for line in text.splitlines():
        if not line or line.startswith("["):
            continue
        if ": " not in line:
            continue
        key, value = line.split(": ", 1)
        payload[key] = parse_result_scalar(value)
    return payload


def parse_result_packet(path: Path) -> dict[str, Any]:
    resolved = project_result_path(path)
    text = resolved.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if stripped.startswith("{"):
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise ValueError("result packet JSON must be an object")
    else:
        payload = parse_text_result_packet(text)
    payload["_source_packet"] = str(resolved.relative_to(ROOT)).replace("\\", "/")
    return payload


def validate_result_packet(payload: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    for field in ["task_id", "status", "summary"]:
        if not payload.get(field):
            findings.append({"severity": "fail", "field": field, "reason": "missing_required"})
    status = str(payload.get("status", ""))
    if status and status not in VALID_RESULT_STATUSES:
        findings.append({"severity": "fail", "field": "status", "reason": "invalid_status", "value": status})
    explicit = str(payload.get("canonical_status", ""))
    if explicit and explicit not in CANONICAL_STATUSES:
        findings.append({"severity": "fail", "field": "canonical_status", "reason": "invalid_canonical_status", "value": explicit})
    for field in ["read_scope", "write_scope", "events"]:
        value = payload.get(field, [])
        if value in (None, ""):
            payload[field] = []
        elif not isinstance(value, list):
            findings.append({"severity": "warning", "field": field, "reason": "not_list", "value_type": type(value).__name__})
    ok = not any(item["severity"] == "fail" for item in findings)
    return {"ok": ok, "findings": findings, "payload": payload}


def review_result_packet(payload: dict[str, Any], validation: dict[str, Any]) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    status = str(payload.get("status", ""))
    canonical_status = canonical_result_status(status, payload)
    if not validation["ok"]:
        findings.append({"severity": "fail", "field": "validation", "reason": "schema_validation_failed"})
    if canonical_status == "review_required":
        findings.append({"severity": "warning", "field": "status", "reason": "completed_with_concerns"})
    if canonical_status in {"blocked", "failed", "canceled", "rejected", "superseded"}:
        findings.append({"severity": "warning", "field": "status", "reason": "terminal_non_success"})
    if canonical_status in CANONICAL_TERMINAL_STATUSES:
        if not as_list(payload.get("evidence")):
            findings.append({"severity": "warning", "field": "evidence", "reason": "missing_terminal_evidence"})
        if not (payload.get("next_recommended_action") or payload.get("next_action")):
            findings.append({"severity": "warning", "field": "next_recommended_action", "reason": "missing_next_action"})
    if canonical_status in {"blocked", "failed", "input_required", "auth_required"} and not as_list(payload.get("blockers")):
        findings.append({"severity": "warning", "field": "blockers", "reason": "missing_blocker_details"})
    if canonical_status == "completed" and as_list(payload.get("risks")):
        findings.append({"severity": "warning", "field": "risks", "reason": "done_with_unresolved_risks"})
    fail_count = sum(1 for item in findings if item["severity"] == "fail")
    warning_count = sum(1 for item in findings if item["severity"] == "warning")
    if fail_count:
        status_label = "rejected"
    elif warning_count:
        status_label = "needs_review"
    else:
        status_label = "accepted"
    return {
        "status": status_label,
        "canonical_status": canonical_status,
        "findings": findings,
        "fail_count": fail_count,
        "warning_count": warning_count,
        "requires_human_review": status_label != "accepted",
    }


def tracked_paths(paths: tuple[str, ...]) -> set[str]:
    if not paths:
        return set()
    result = run(["git", "ls-files", "--", *paths], timeout=20)
    if not result.get("ok"):
        return set()
    return {line.strip().replace("\\", "/") for line in result["stdout"].splitlines() if line.strip()}


def check_runtime_output_ignore(paths: tuple[str, ...] = EXPECTED_IGNORED_RUNTIME_OUTPUTS) -> dict:
    tracked = tracked_paths(paths)
    ignore_candidates = [path for path in paths if path not in tracked]
    try:
        completed = subprocess.run(
            ["git", "check-ignore", "--", *ignore_candidates],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
            check=False,
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc), "checked_paths": list(paths), "tracked_paths": sorted(tracked)}
    ignored = {line.strip().strip("\"").replace("\\", "/") for line in completed.stdout.splitlines() if line.strip()}
    missing = [path for path in ignore_candidates if path not in ignored]
    return {
        "ok": completed.returncode in {0, 1} and not missing,
        "returncode": completed.returncode,
        "ignored_count": len(ignored),
        "missing": missing,
        "checked_paths": list(paths),
        "tracked_paths": sorted(tracked),
        "ignore_checked_paths": ignore_candidates,
        "stderr": completed.stderr.strip(),
    }

def staged_files() -> tuple[list[str], dict]:
    result = run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRTD"], timeout=30)
    if not result.get("ok"):
        return [], {"ok": False, "error": result}
    return [line for line in result["stdout"].splitlines() if line], {"ok": True, "result": result}


def check_git_workspace_state(
    staged_limit: int = STAGED_BROAD_THRESHOLD,
    *,
    staged_override: list[str] | None = None,
    index_lock_present: bool | None = None,
) -> dict:
    findings = []
    index_lock = ROOT / ".git" / "index.lock"
    lock_present = index_lock.exists() if index_lock_present is None else index_lock_present
    if lock_present:
        findings.append({"severity": "fail", "field": "git", "value": ".git/index.lock", "reason": "git_index_lock_present"})

    if staged_override is None:
        staged, staged_result = staged_files()
        if not staged_result.get("ok"):
            findings.append({"severity": "fail", "field": "git", "value": "staged_files", "reason": "cannot_read_staged_files"})
            staged = []
    else:
        staged = staged_override

    staged_runtime = [
        path
        for path in staged
        if path.startswith(STAGED_RUNTIME_PREFIXES)
        or any(part in path for part in STAGED_RUNTIME_PARTS)
        or path.endswith(".pyc")
    ]
    staged_external = [path for path in staged if path.startswith(STAGED_EXTERNAL_PREFIXES)]
    if staged_runtime:
        findings.append(
            {
                "severity": "fail",
                "field": "git",
                "value": staged_runtime[:30],
                "reason": "staged_runtime_output",
                "count": len(staged_runtime),
            }
        )
    if staged_external:
        findings.append(
            {
                "severity": "fail",
                "field": "git",
                "value": staged_external[:30],
                "reason": "staged_external_reference_tree",
                "count": len(staged_external),
            }
        )
    if len(staged) > staged_limit:
        findings.append(
            {
                "severity": "warning",
                "field": "git",
                "value": len(staged),
                "reason": "staged_file_count_exceeds_split_threshold",
                "threshold": staged_limit,
            }
        )
    fail_findings = [item for item in findings if item["severity"] == "fail"]
    return {
        "ok": not fail_findings,
        "findings": findings,
        "staged_count": len(staged),
        "staged_limit": staged_limit,
        "staged_runtime_count": len(staged_runtime),
        "staged_external_count": len(staged_external),
        "index_lock_present": lock_present,
    }


def collect(args: argparse.Namespace) -> dict:
    paths = args.path or []
    write_paths = args.write_path or []
    commands = args.command or []
    result_packets = args.result_packet or []
    candidate_large_paths = sorted(dict.fromkeys(paths + write_paths + result_packets))
    checks = {
        "required_paths": check_paths(),
        "reference_index": check_reference_index(),
        "python_compile": check_py_compile(),
        "large_tracked_files": check_large_tracked_files(args.large_limit_mb, full_repo=args.full_repo_large_scan),
        "candidate_large_files": check_candidate_large_files(candidate_large_paths, args.large_limit_mb),
        "scope": check_scope(paths),
        "write_scope": check_write_scope(write_paths),
        "secret_paths": check_secret_paths(candidate_large_paths),
        "command_policy": check_command_policy(commands, allow_destructive=args.allow_destructive_command, allow_broad_git=args.allow_broad_git),
        "result_packet_evidence": check_result_packet_evidence(result_packets),
        "runtime_output_ignore": check_runtime_output_ignore(),
        "git_workspace_state": check_git_workspace_state(args.staged_file_warning_threshold),
    }
    checks["ok"] = all(item.get("ok", False) for item in checks.values())
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--write-path", action="append", default=[])
    parser.add_argument("--command", action="append", default=[])
    parser.add_argument("--result-packet", action="append", default=[])
    parser.add_argument("--large-limit-mb", type=int, default=100)
    parser.add_argument("--full-repo-large-scan", action="store_true")
    parser.add_argument("--allow-destructive-command", action="store_true")
    parser.add_argument("--allow-broad-git", action="store_true")
    parser.add_argument("--staged-file-warning-threshold", type=int, default=STAGED_BROAD_THRESHOLD)
    args = parser.parse_args()

    data = collect(args)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        for name, value in data.items():
            if name == "ok":
                continue
            status = "ok" if value.get("ok") else "check"
            print(f"{status:5} {name}")
            if name == "required_paths" and value.get("missing"):
                for item in value["missing"]:
                    print(f"      missing {item}")
            if name == "large_tracked_files" and value.get("offenders"):
                for item in value["offenders"]:
                    print(f"      {item['size_mb']} MB {item['path']}")
            if name == "candidate_large_files" and value.get("offenders"):
                for item in value["offenders"]:
                    print(f"      {item['size_mb']} MB {item['path']}")
            if name == "runtime_output_ignore" and value.get("missing"):
                for item in value["missing"]:
                    print(f"      not ignored {item}")
            if name == "scope" and value.get("outside"):
                for item in value["outside"]:
                    print(f"      outside {item}")
            for item in value.get("findings", []):
                print(f"      {item.get('reason')} {item.get('field')}: {item.get('value', '')}")
        print(f"overall={'ok' if data['ok'] else 'check'}")
    return 0 if data["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
