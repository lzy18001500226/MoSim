#!/usr/bin/env python3
"""Transport adapter interface for CoAgent visible conversation dispatch."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class TransportRequest:
    task_id: str
    department: str
    thread_id: str
    thread_name: str
    packet_path: Path
    result_path: Path
    packet_text: str


@dataclass(frozen=True)
class TransportPlan:
    adapter: str
    thread_id: str
    thread_name: str
    packet_path: str
    result_path: str
    command: list[str] = field(default_factory=list)
    command_shell: str = ""
    env: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    dry_run: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapter": self.adapter,
            "thread_id": self.thread_id,
            "thread_name": self.thread_name,
            "packet_path": self.packet_path,
            "result_path": self.result_path,
            "command": self.command,
            "command_shell": self.command_shell,
            "env": self.env,
            "metadata": self.metadata,
            "dry_run": self.dry_run,
        }


@dataclass(frozen=True)
class TransportStart:
    adapter: str
    pid: int
    stdout_log: str
    stderr_log: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "adapter": self.adapter,
            "pid": self.pid,
            "stdout_log": self.stdout_log,
            "stderr_log": self.stderr_log,
            "metadata": self.metadata,
        }


class TransportAdapter(Protocol):
    name: str

    def plan(self, request: TransportRequest) -> TransportPlan:
        ...

    def start(self, request: TransportRequest, plan: TransportPlan) -> TransportStart:
        ...
