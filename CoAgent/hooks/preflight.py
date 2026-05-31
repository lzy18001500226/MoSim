#!/usr/bin/env python3
"""CoAgent project-local preflight checks."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
ALLOWED_ROOT = ROOT.resolve()
REFERENCE_INDEX = ROOT / "CoAgent" / "docs" / "research" / "REFERENCE_PROJECT_INDEX.md"
RUNTIME_FILE = ROOT / "CoAgent" / "runtime" / "mosim_agent_runtime.py"
DISPATCH_FILE = ROOT / "CoAgent" / "dispatch" / "dispatch_helper.py"
THREAD_REGISTRY = ROOT / "CoAgent" / "dispatch" / "department_threads.json"
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
    "CoAgent/runtime/__pycache__/probe.pyc",
)
STAGED_RUNTIME_PREFIXES = (
    "Results/",
    "CoAgent/__pycache__/",
)
STAGED_RUNTIME_PARTS = (
    "/__pycache__/",
)
STAGED_EXTERNAL_PREFIXES = (
    "References/",
    "Docs/Skills/Agent/",
)
STAGED_BROAD_THRESHOLD = 200


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
        RUNTIME_FILE,
        DISPATCH_FILE,
        THREAD_REGISTRY,
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    return {"ok": not missing, "missing": missing}


def check_reference_index() -> dict:
    return run(["python3", "Scripts/reference/check_reference_index.py", "--strict"], timeout=30)


def check_py_compile() -> dict:
    return run(
        [
            "python3",
            "-m",
            "py_compile",
            "CoAgent/runtime/mosim_agent_runtime.py",
            "CoAgent/dispatch/dispatch_helper.py",
            "Scripts/agent/mosim_agent_runtime.py",
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
            if rel.startswith("CoAgent/")
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
        normalized = raw.replace("\\", "/").lower()
        for hint in SECRET_PATH_HINTS:
            if hint in normalized:
                findings.append({"severity": "fail", "field": field, "value": raw, "reason": "secret_risk_path", "hint": hint})
                break
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
        findings.extend(secret_path_findings([command], field="command"))
    return {"ok": not findings, "findings": findings, "checked_commands": len(commands)}


def check_result_packet_evidence(packet_paths: list[str]) -> dict:
    if not packet_paths:
        return {"ok": True, "findings": [], "checked_packets": 0}
    from CoAgent.result_router import result_router

    findings = []
    packets = []
    for raw in packet_paths:
        path = Path(raw)
        try:
            payload = result_router.parse_packet(path)
            validation = result_router.validate_packet(payload)
            review = result_router.review_packet(payload, validation)
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


def check_runtime_output_ignore(paths: tuple[str, ...] = EXPECTED_IGNORED_RUNTIME_OUTPUTS) -> dict:
    try:
        completed = subprocess.run(
            ["git", "check-ignore", "--stdin"],
            cwd=ROOT,
            input="\n".join(paths) + "\n",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
            check=False,
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc), "checked_paths": list(paths)}
    ignored = set(completed.stdout.splitlines())
    missing = [path for path in paths if path not in ignored]
    return {
        "ok": completed.returncode in {0, 1} and not missing,
        "returncode": completed.returncode,
        "ignored_count": len(ignored),
        "missing": missing,
        "checked_paths": list(paths),
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
