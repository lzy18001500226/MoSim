#!/usr/bin/env python3
"""Codex CLI resume transport adapter.

This adapter is intentionally project-local and file based. It prepares a
shadow Codex home under ignored `Results/` paths and runs `codex exec resume`
against a visible conversation thread.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Any
from uuid import uuid4

from CoAgent.transport.adapter import TransportPlan
from CoAgent.transport.adapter import TransportRequest
from CoAgent.transport.adapter import TransportStart


ROOT = Path(__file__).resolve().parents[2]
TMP_DIR = ROOT / "Results" / "coagent_transport"
SHADOW_SQLITE_ROOT = TMP_DIR / "sqlite_home"
SHADOW_CODEX_ROOT = TMP_DIR / "codex_home"
RUNS_DIR = TMP_DIR / "runs"


def session_meta_matches_thread(path: Path, thread_id: str) -> bool:
    """Return true only when a rollout file identifies itself as thread_id."""
    if thread_id in path.name:
        return True
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            first_line = handle.readline()
    except OSError:
        return False
    if not first_line:
        return False
    try:
        first_record = json.loads(first_line)
    except json.JSONDecodeError:
        return False
    if first_record.get("type") != "session_meta":
        return False
    payload = first_record.get("payload")
    return isinstance(payload, dict) and payload.get("id") == thread_id


def project_rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT)).replace("\\", "/")


class CodexExecResumeAdapter:
    name = "codex_exec_resume"

    def __init__(self, *, source_home: Path | None = None) -> None:
        self.source_home = source_home or Path("/home/linux/.codex")
        self._shadow_cache: dict[str, dict[str, Any]] = {}
        self.shadow_id = f"pid_{os.getpid()}_{uuid4().hex[:8]}"
        self.shadow_sqlite_home = SHADOW_SQLITE_ROOT / self.shadow_id
        self.shadow_codex_home = SHADOW_CODEX_ROOT / self.shadow_id

    def ensure_dirs(self) -> None:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        RUNS_DIR.mkdir(parents=True, exist_ok=True)
        self.shadow_sqlite_home.mkdir(parents=True, exist_ok=True)
        self.shadow_codex_home.mkdir(parents=True, exist_ok=True)

    def reset_shadow_sessions(self) -> None:
        sessions = self.shadow_codex_home / "sessions"
        if sessions.exists():
            shutil.rmtree(sessions, ignore_errors=True)
        sessions.mkdir(parents=True, exist_ok=True)

    def build_resume_command(self, thread_id: str, result_path: Path) -> list[str]:
        return [
            "codex",
            "exec",
            "resume",
            thread_id,
            "-m",
            "gpt-5.5",
            "-c",
            "model_reasoning_effort=\"high\"",
            "-c",
            f"sqlite_home={json.dumps(str(self.shadow_sqlite_home))}",
            "--dangerously-bypass-approvals-and-sandbox",
            "--output-last-message",
            str(result_path),
            "-",
        ]

    def prepare_shadow_home(self, thread_id: str) -> dict[str, Any]:
        if thread_id in self._shadow_cache:
            return self._shadow_cache[thread_id]
        self.ensure_dirs()
        self.reset_shadow_sessions()
        copied: list[str] = []
        for name in ["auth.json", "config.toml", "session_index.jsonl"]:
            src = self.source_home / name
            if src.exists():
                dst = self.shadow_codex_home / name
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
                copied.append(project_rel(dst))
        session_files: list[str] = []
        sessions_src = self.source_home / "sessions"
        sessions_src.mkdir(parents=True, exist_ok=True)
        for src in sessions_src.rglob("*.jsonl"):
            if not session_meta_matches_thread(src, thread_id):
                continue
            rel = src.relative_to(self.source_home)
            dst = self.shadow_codex_home / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            rel_dst = project_rel(dst)
            copied.append(rel_dst)
            session_files.append(rel_dst)
        result = {
            "shadow_codex_home": project_rel(self.shadow_codex_home),
            "shadow_sqlite_home": project_rel(self.shadow_sqlite_home),
            "copied_files": copied,
            "session_files": session_files,
            "shadow_id": self.shadow_id,
        }
        self._shadow_cache[thread_id] = result
        return result

    def plan(self, request: TransportRequest) -> TransportPlan:
        self.ensure_dirs()
        shadow = self.prepare_shadow_home(request.thread_id)
        request.packet_path.parent.mkdir(parents=True, exist_ok=True)
        request.result_path.parent.mkdir(parents=True, exist_ok=True)
        request.packet_path.write_text(request.packet_text.rstrip() + "\n", encoding="utf-8")
        command = self.build_resume_command(request.thread_id, request.result_path)
        command_shell = " ".join(shlex.quote(part) for part in command) + f" < {shlex.quote(str(request.packet_path))}"
        metadata = {
            "codex_home": shadow["shadow_codex_home"],
            "sqlite_home": shadow["shadow_sqlite_home"],
            "copied_files": shadow["copied_files"],
            "session_files": shadow["session_files"],
            "shadow_id": shadow["shadow_id"],
        }
        return TransportPlan(
            adapter=self.name,
            thread_id=request.thread_id,
            thread_name=request.thread_name,
            packet_path=project_rel(request.packet_path),
            result_path=project_rel(request.result_path),
            command=command,
            command_shell=command_shell,
            env={
                "CODEX_HOME": str(ROOT / shadow["shadow_codex_home"]),
                "CODEX_SQLITE_HOME": str(ROOT / shadow["shadow_sqlite_home"]),
            },
            metadata=metadata,
            dry_run=True,
        )

    def start(self, request: TransportRequest, plan: TransportPlan) -> TransportStart:
        self.ensure_dirs()
        if not plan.metadata.get("session_files"):
            raise RuntimeError(f"no matching Codex session file for thread_id={request.thread_id}")
        stdout_log = RUNS_DIR / f"{request.task_id}.stdout.log"
        stderr_log = RUNS_DIR / f"{request.task_id}.stderr.log"
        env = {**dict(**os.environ), **plan.env}
        with request.packet_path.open("r", encoding="utf-8") as handle, stdout_log.open("w", encoding="utf-8") as out, stderr_log.open("w", encoding="utf-8") as err:
            proc = subprocess.Popen(
                plan.command,
                cwd=ROOT,
                stdin=handle,
                stdout=out,
                stderr=err,
                text=True,
                env=env,
                start_new_session=True,
            )
        return TransportStart(
            adapter=self.name,
            pid=proc.pid,
            stdout_log=project_rel(stdout_log),
            stderr_log=project_rel(stderr_log),
            metadata=plan.metadata,
        )
