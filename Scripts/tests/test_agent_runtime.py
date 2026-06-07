#!/usr/bin/env python3
"""Regression checks for the MoSim durable agent task runtime."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[2]


def load_runtime_module():
    path = ROOT / "CoAgent" / "runtime" / "mosim_agent_runtime.py"
    spec = importlib.util.spec_from_file_location("mosim_agent_runtime", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load mosim_agent_runtime.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run_runtime(module, temp_dir: Path, *args: str) -> dict:
    db = temp_dir / "tasks.sqlite3"
    events = temp_dir / "events.jsonl"
    argv = ["--db", str(db), "--events", str(events)]
    # Common options are subcommand-local.
    command = args[0]
    rest = list(args[1:])
    if command in {"create", "claim", "heartbeat", "checkpoint", "complete", "block", "fail", "cancel", "list", "show"}:
        argv = [command, "--db", str(db), "--events", str(events), *rest]
    else:
        argv = list(args)
    parser = module.build_parser()
    parsed = parser.parse_args(argv)
    return parsed.func(parsed)


def cleanup(path: Path) -> None:
    if not path.exists():
        return
    for item in sorted(path.glob("**/*"), key=lambda p: len(p.parts), reverse=True):
        if item.is_file():
            item.unlink()
        elif item.is_dir():
            item.rmdir()
    path.rmdir()


def test_agent_runtime_claim_checkpoint_complete_roundtrip() -> None:
    module = load_runtime_module()
    temp_dir = ROOT / ".tmp" / f"agent_runtime_{uuid4().hex}"
    try:
        temp_dir.mkdir(parents=True)
        created = run_runtime(
            module,
            temp_dir,
            "create",
            "--task-id",
            "task_fixture",
            "--objective",
            "Check docs",
            "--role",
            "DocsReviewer",
            "--read-scope",
            "Docs/Workflows",
            "--write-scope",
            "Docs/Workflows",
            "--acceptance",
            "review report exists",
            "--stop-condition",
            "done or blocked",
            "--metadata",
            '{"lane":"docs"}',
        )
        assert created["task_id"] == "task_fixture"
        assert created["state"] == "queued"
        assert [Path(item).as_posix() for item in created["read_scope"]] == ["Docs/Workflows"]

        claimed = run_runtime(module, temp_dir, "claim", "--owner", "DocsReviewer")
        assert claimed["task_id"] == "task_fixture"
        assert claimed["state"] == "claimed"
        token = claimed["claim_token"]

        checkpoint = run_runtime(
            module,
            temp_dir,
            "checkpoint",
            "--task-id",
            "task_fixture",
            "--actor",
            "DocsReviewer",
            "--claim-token",
            token,
            "--summary",
            "read first slice",
            "--data",
            '{"files":2}',
        )
        assert checkpoint["state"] == "running"

        completed = run_runtime(
            module,
            temp_dir,
            "complete",
            "--task-id",
            "task_fixture",
            "--actor",
            "DocsReviewer",
            "--claim-token",
            token,
            "--summary",
            "review complete",
        )
        assert completed["state"] == "done"

        shown = run_runtime(module, temp_dir, "show", "--task-id", "task_fixture")
        event_types = [item["event_type"] for item in shown["events"]]
        assert event_types == ["task_created", "task_claimed", "checkpoint", "task_completed"]

        events_path = temp_dir / "events.jsonl"
        lines = events_path.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 4
        assert json.loads(lines[-1])["event_type"] == "task_completed"
    finally:
        cleanup(temp_dir)
        tmp_root = ROOT / ".tmp"
        if tmp_root.exists() and not any(tmp_root.iterdir()):
            tmp_root.rmdir()


def test_agent_runtime_rejects_outside_scope() -> None:
    module = load_runtime_module()
    temp_dir = ROOT / ".tmp" / f"agent_runtime_scope_{uuid4().hex}"
    try:
        temp_dir.mkdir(parents=True)
        try:
            run_runtime(
                module,
                temp_dir,
                "create",
                "--objective",
                "Bad path",
                "--role",
                "SecurityOfficer",
                "--read-scope",
                "/mnt/c/Users/HP/Desktop",
                "--acceptance",
                "never",
                "--stop-condition",
                "blocked",
            )
        except SystemExit as exc:
            assert "outside MoSim" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("outside path was accepted")
    finally:
        cleanup(temp_dir)
        tmp_root = ROOT / ".tmp"
        if tmp_root.exists() and not any(tmp_root.iterdir()):
            tmp_root.rmdir()


def test_agent_runtime_requires_claim_token_for_claimed_tasks() -> None:
    module = load_runtime_module()
    temp_dir = ROOT / ".tmp" / f"agent_runtime_token_{uuid4().hex}"
    try:
        temp_dir.mkdir(parents=True)
        run_runtime(
            module,
            temp_dir,
            "create",
            "--task-id",
            "task_token_fixture",
            "--objective",
            "Check token",
            "--role",
            "SecurityOfficer",
            "--acceptance",
            "token enforced",
            "--stop-condition",
            "done",
        )
        run_runtime(module, temp_dir, "claim", "--owner", "SecurityOfficer")
        try:
            run_runtime(
                module,
                temp_dir,
                "complete",
                "--task-id",
                "task_token_fixture",
                "--actor",
                "SecurityOfficer",
                "--summary",
                "should fail without token",
            )
        except SystemExit as exc:
            assert "claim token required or mismatch" in str(exc)
        else:  # pragma: no cover
            raise AssertionError("claimed task was completed without token")
    finally:
        cleanup(temp_dir)
        tmp_root = ROOT / ".tmp"
        if tmp_root.exists() and not any(tmp_root.iterdir()):
            tmp_root.rmdir()
