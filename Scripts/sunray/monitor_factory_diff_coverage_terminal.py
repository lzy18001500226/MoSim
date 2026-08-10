#!/usr/bin/env python3
"""Monitor one Factory Diff coverage run and optionally send one terminal email."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_task_notification_status(run_dir: Path, source: Path, payload: dict, blockers: object) -> Path:
    observed_status = str(payload.get("status") or "unknown")
    terminal_status = "completed" if observed_status == "passed" and not blockers else "blocked"
    status_path = run_dir / "terminal_task_notification_status.json"
    status_path.write_text(
        json.dumps(
            {
                "status": terminal_status,
                "task": "Factory L2 单机同飞行覆盖建图",
                "failure_kind": "factory_diff_coverage_terminal",
                "observed_error": f"运行终态：{observed_status}",
                "minimal_user_action": "无需处理。" if terminal_status == "completed" else "查看终态证据并处理阻塞项。",
                "latest_snapshot": str(source),
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return status_path


def send_email(status_path: Path) -> dict:
    cmd = [
        sys.executable,
        str(ROOT / "Scripts" / "agent" / "send_gateway_email_alert.py"),
        "--status-json",
        str(status_path),
        "--task-notification",
    ]
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True, timeout=60)
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-4000:],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--poll-s", type=float, default=300.0)
    parser.add_argument("--max-hours", type=float, default=18.0)
    parser.add_argument(
        "--send-task-email",
        action="store_true",
        help="send the terminal task notification only when explicitly requested for this run",
    )
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    root = ROOT.resolve()
    if not (run_dir == root or root in run_dir.parents):
        raise SystemExit(f"run-dir outside MoSim workspace: {run_dir}")

    final_json = run_dir / "DIFF_INTERACTIVE_COVERAGE_GOAL_CHAIN_PROBE.json"
    partial_json = run_dir / "DIFF_INTERACTIVE_COVERAGE_GOAL_CHAIN_PROBE.partial.json"
    monitor_json = run_dir / "terminal_monitor.json"
    deadline = time.time() + max(0.1, args.max_hours) * 3600.0

    while time.time() < deadline:
        source = final_json if final_json.exists() else partial_json
        payload = read_json(source)
        status = str(payload.get("status") or "")
        blockers = payload.get("blockers")
        terminal = bool(blockers) or status in {"failed", "blocked", "review_required_or_blocked"}
        if source == final_json and status == "passed":
            terminal = (run_dir / "FACTORY_L2_DIFF_INTERACTIVE_COVERAGE_PROBE.json").exists()
        if terminal or blockers:
            email = (
                send_email(write_task_notification_status(run_dir, source, payload, blockers))
                if args.send_task_email
                else {"attempted": False, "reason": "task_notification_not_requested"}
            )
            record = {
                "status": "terminal_observed",
                "source": str(source),
                "observed_status": status,
                "blockers": blockers,
                "email": email,
                "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            }
            monitor_json.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return 0 if not email.get("attempted") or email.get("returncode") == 0 else 2
        time.sleep(max(15.0, args.poll_s))

    record = {
        "status": "monitor_timeout",
        "source": str(partial_json),
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    monitor_json.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
