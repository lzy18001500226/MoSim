#!/usr/bin/env python3
"""Historical bootstrap helper for visible CoAgent department conversations.

This command creates lightweight real Codex sessions for permanent CoAgent
departments and then syncs their metadata into the WSL and Windows Codex homes
so the front ends can list them.

Current MoSim dispatch uses the user-confirmed allowlist in
CoAgent/dispatch/department_threads.json. The old permanent-department
bootstrap set is intentionally disabled so this helper cannot recreate deleted
legacy departments by accident. Future PMO-approved thread creation should add
new current DepartmentSpec entries explicitly.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CODEX = Path(
    os.environ.get(
        "COAGENT_CODEX_BIN",
        shutil.which("codex")
        or "/mnt/c/Users/HP/.vscode/extensions/openai.chatgpt-26.527.31454-win32-x64/bin/linux-x86_64/codex",
    )
)
WSL_CODEX_HOME = Path("/home/linux/.codex")
WINDOWS_CODEX_HOME = Path("/mnt/c/Users/HP/.codex")
REGISTRY = ROOT / "CoAgent" / "dispatch" / "department_threads.json"
CANONICAL_CWD = "/mnt/c/Users/HP/Desktop/MoSim"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from CoAgent.dispatch import codex_session_repair


@dataclass(frozen=True)
class DepartmentSpec:
    department: str
    thread_name: str
    mission: str
    accountable_to: str


PERMANENT_DEPARTMENTS = []  # Disabled: current registry is user-confirmed allowlist only.


def load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"threads": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save_registry(data: dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def registry_by_department(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {item.get("department", ""): item for item in data.get("threads", [])}


def selected_department_specs(args: argparse.Namespace) -> list[DepartmentSpec]:
    requested = set(getattr(args, "department", []) or [])
    if not requested:
        return PERMANENT_DEPARTMENTS
    known = {spec.department for spec in PERMANENT_DEPARTMENTS}
    unknown = sorted(requested - known)
    if unknown:
        raise SystemExit(f"unknown department(s): {', '.join(unknown)}")
    return [spec for spec in PERMANENT_DEPARTMENTS if spec.department in requested]


def project_rollouts_for_title(title: str) -> list[Path]:
    sessions = WSL_CODEX_HOME / "sessions"
    if not sessions.exists():
        return []
    matches: list[Path] = []
    for path in sessions.rglob("rollout-*.jsonl"):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if title in text:
            matches.append(path)
    return sorted(matches, key=lambda p: p.stat().st_mtime, reverse=True)


def is_bootstrap_rollout(path: Path, spec: DepartmentSpec) -> bool:
    try:
        records = [
            json.loads(line)
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines()
            if line.strip()
        ]
    except (OSError, json.JSONDecodeError):
        return False
    saw_prompt = False
    saw_reply = False
    prompt_marker = f"请创建一个标题为 {spec.thread_name} 的 CoAgent 常驻部门对话。"
    reply_marker = f"{spec.thread_name} 已建立，等待任务单。"
    for item in records:
        payload = item.get("payload", {})
        if item.get("type") == "event_msg" and payload.get("type") == "user_message":
            saw_prompt = prompt_marker in payload.get("message", "")
        if item.get("type") == "event_msg" and payload.get("type") == "agent_message":
            saw_reply = reply_marker in payload.get("message", "")
        if item.get("type") == "response_item" and payload.get("type") == "message":
            text = json.dumps(payload.get("content", []), ensure_ascii=False)
            saw_reply = saw_reply or reply_marker in text
    return saw_prompt and saw_reply


def bootstrap_rollouts_for_spec(spec: DepartmentSpec) -> list[Path]:
    sessions = WSL_CODEX_HOME / "sessions"
    if not sessions.exists():
        return []
    matches = [path for path in sessions.rglob("rollout-*.jsonl") if is_bootstrap_rollout(path, spec)]
    return sorted(matches, key=lambda p: p.stat().st_mtime, reverse=True)


def thread_id_from_rollout(path: Path) -> str:
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if item.get("type") == "session_meta":
            payload = item.get("payload", {})
            if isinstance(payload, dict) and payload.get("id"):
                return str(payload["id"])
    raise SystemExit(f"rollout missing session_meta id: {path}")


def create_codex_thread(spec: DepartmentSpec, *, timeout: int) -> str:
    prompt = (
        f"请创建一个标题为 {spec.thread_name} 的 CoAgent 常驻部门对话。\n"
        f"部门职责：{spec.mission}\n"
        f"对齐对象：{spec.accountable_to}\n"
        "这是部门入口初始化，不要读写文件，不要运行命令，不要派发业务任务。\n"
        f"只回复一句：{spec.thread_name} 已建立，等待任务单。"
    )
    before = {path.resolve() for path in bootstrap_rollouts_for_spec(spec)}
    codex_args = [
        str(CODEX),
        "--no-alt-screen",
        "-C",
        CANONICAL_CWD,
        "-c",
        'model_provider="OpenAI"',
        "-c",
        'model_reasoning_effort="high"',
        "-m",
        "gpt-5.5",
        "-a",
        "never",
        "--sandbox",
        "danger-full-access",
        prompt,
    ]
    command = [
        "timeout",
        f"{timeout}s",
        "script",
        "-qfec",
        " ".join(shlex.quote(arg) for arg in codex_args),
        "/dev/null",
    ]
    proc = subprocess.run(
        command,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout + 5,
        check=False,
    )
    matches = bootstrap_rollouts_for_spec(spec)
    for rollout in matches:
        if rollout.resolve() not in before:
            return thread_id_from_rollout(rollout)
    # Some TUI exits return timeout/non-zero even though the rollout is valid.
    if matches:
        latest = matches[0]
        if latest.stat().st_mtime >= time.time() - (timeout + 10):
            return thread_id_from_rollout(latest)
    raise SystemExit(
        json.dumps(
            {
                "ok": False,
                "department": spec.department,
                "reason": "interactive bootstrap did not produce a discoverable rollout",
                "returncode": proc.returncode,
                "stdout": proc.stdout[-2000:],
                "stderr": proc.stderr[-2000:],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def get_or_create_thread_id(spec: DepartmentSpec, *, timeout: int, recreate: bool) -> tuple[str, str]:
    if not recreate:
        matches = bootstrap_rollouts_for_spec(spec)
        if matches:
            return thread_id_from_rollout(matches[0]), "reused_existing_bootstrap_rollout"
    return create_codex_thread(spec, timeout=timeout), "created_new_codex_tui_thread"


def sync_visible(thread_id: str, thread_name: str, mission: str, *, apply: bool) -> dict[str, Any]:
    args = argparse.Namespace(
        thread_id=thread_id,
        thread_name=thread_name,
        preview=f"{thread_name} 已建立，等待任务单。职责：{mission}",
        cwd=CANONICAL_CWD,
        source_codex_home=WSL_CODEX_HOME,
        target_codex_home=[WSL_CODEX_HOME, WINDOWS_CODEX_HOME],
        apply=apply,
    )
    if apply:
        codex_session_repair.cmd_sync_visible(args)
    return codex_session_repair.sync_visible_plan(args)


def build_registry_entry(spec: DepartmentSpec, thread_id: str, status: str) -> dict[str, Any]:
    return {
        "department": spec.department,
        "thread_name": spec.thread_name,
        "thread_id": thread_id,
        "surface": "codex_app_or_vscode",
        "status": status,
        "agent_type": "permanent",
        "mission": spec.mission,
        "accountable_to": spec.accountable_to,
    }


def cmd_plan(args: argparse.Namespace) -> int:
    data = load_registry(args.registry)
    existing = registry_by_department(data)
    rows = []
    for spec in selected_department_specs(args):
        item = existing.get(spec.department, {})
        rows.append(
            {
                "department": spec.department,
                "thread_name": spec.thread_name,
                "existing_thread_id": item.get("thread_id", ""),
                "existing_status": item.get("status", ""),
                "existing_title_rollouts": [str(path) for path in project_rollouts_for_title(spec.thread_name)[:3]],
                "existing_bootstrap_rollouts": [str(path) for path in bootstrap_rollouts_for_spec(spec)[:3]],
                "create": spec.department != "MainAgent" and (args.recreate or item.get("status") != "active_visible"),
            }
        )
    print(json.dumps({"ok": True, "registry": str(args.registry), "departments": rows}, ensure_ascii=False, indent=2))
    return 0


def cmd_create(args: argparse.Namespace) -> int:
    data = load_registry(args.registry)
    existing = registry_by_department(data)
    created: list[dict[str, Any]] = []
    merged = dict(existing)
    for spec in selected_department_specs(args):
        old = existing.get(spec.department, {})
        if spec.department == "MainAgent":
            thread_id = old.get("thread_id") or "019e0198-a041-77f1-84d0-c5524bfd4b81"
            merged[spec.department] = build_registry_entry(spec, thread_id, "active_visible")
            if args.apply_registry:
                save_registry({"threads": list(merged.values())}, args.registry)
            continue
        should_create = args.recreate or old.get("status") != "active_visible"
        if should_create:
            thread_id, source = get_or_create_thread_id(spec, timeout=args.timeout, recreate=args.recreate)
            sync_visible(thread_id, spec.thread_name, spec.mission, apply=args.apply_sync)
            status = "visible_pending_user_confirmation"
            created.append({"department": spec.department, "thread_name": spec.thread_name, "thread_id": thread_id, "source": source})
        else:
            thread_id = old.get("thread_id", "")
            status = old.get("status", "active_visible")
        merged[spec.department] = build_registry_entry(spec, thread_id, status)
        if args.apply_registry:
            save_registry({"threads": list(merged.values())}, args.registry)
    entries = []
    by_department = registry_by_department({"threads": list(merged.values())})
    for spec in PERMANENT_DEPARTMENTS:
        if spec.department in by_department:
            entries.append(by_department[spec.department])
    for department, entry in by_department.items():
        if department not in {spec.department for spec in PERMANENT_DEPARTMENTS}:
            entries.append(entry)
    data = {"threads": entries}
    if args.apply_registry:
        save_registry(data, args.registry)
    print(
        json.dumps(
            {
                "ok": True,
                "created": created,
                "registry_updated": args.apply_registry,
                "sync_applied": args.apply_sync,
                "next": "Ask the user to confirm all visible_pending_user_confirmation conversations are visible, then promote them to active_visible.",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--timeout", type=int, default=60)
    sub = parser.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan")
    plan.add_argument("--recreate", action="store_true")
    plan.add_argument("--department", action="append", default=[])
    plan.set_defaults(func=cmd_plan)
    create = sub.add_parser("create")
    create.add_argument("--recreate", action="store_true")
    create.add_argument("--apply-sync", action="store_true")
    create.add_argument("--apply-registry", action="store_true")
    create.add_argument("--department", action="append", default=[])
    create.set_defaults(func=cmd_create)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
