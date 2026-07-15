#!/usr/bin/env python3
"""Monitor one Factory Diff coverage run and send one terminal email."""

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


def summarize(run_dir: Path, payload: dict, manifest: dict, metrics: dict, coverage: dict) -> tuple[str, str]:
    goals = payload.get("goals") if isinstance(payload.get("goals"), list) else []
    completed = payload.get("completed_goal_count", len(goals))
    loaded = payload.get("loaded_route_goal_count")
    blockers = payload.get("blockers")
    skips = sum(1 for goal in goals if isinstance(goal, dict) and goal.get("runtime_skipped_goal"))
    stuck = sum(1 for goal in goals if isinstance(goal, dict) and goal.get("attitude_stuck_violation"))
    rejoin = len(payload.get("route_rejoin_events") or [])
    manifest_status = manifest.get("status", "missing")
    metrics_status = metrics.get("status", "missing")
    coverage_status = coverage.get("status", "missing")
    coverage_ratio = (
        coverage.get("acceptance", {}).get("merged_sensor_footprint_coverage_ratio")
        if isinstance(coverage.get("acceptance"), dict)
        else None
    )
    subject = f"MoSim Factory覆盖终态: {payload.get('status', 'unknown')}/{manifest_status}"
    body = "\n".join(
        [
            "Factory L2 单机同飞行覆盖建图终态",
            "",
            f"status: {payload.get('status', 'unknown')}",
            f"manifest_status: {manifest_status}",
            f"metrics_status: {metrics_status}",
            f"coverage_status: {coverage_status}",
            f"coverage_ratio: {coverage_ratio}",
            f"completed: {completed}/{loaded}",
            f"blockers: {blockers}",
            f"runtime_skipped_goals: {skips}",
            f"attitude_stuck: {stuck}",
            f"route_rejoin_events: {rejoin}",
            f"run_dir: {run_dir}",
            f"generated_at: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        ]
    )
    return subject, body


def send_email(subject: str, body: str, cooldown_key: str) -> dict:
    cmd = [
        sys.executable,
        str(ROOT / "Scripts" / "agent" / "send_gateway_email_alert.py"),
        "--subject",
        subject,
        "--body",
        body,
        "--cooldown-key",
        cooldown_key,
        "--cooldown-minutes",
        "0",
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
    args = parser.parse_args()

    run_dir = args.run_dir.resolve()
    root = ROOT.resolve()
    if not (run_dir == root or root in run_dir.parents):
        raise SystemExit(f"run-dir outside MoSim workspace: {run_dir}")

    final_json = run_dir / "DIFF_INTERACTIVE_COVERAGE_GOAL_CHAIN_PROBE.json"
    partial_json = run_dir / "DIFF_INTERACTIVE_COVERAGE_GOAL_CHAIN_PROBE.partial.json"
    manifest_json = run_dir / "FACTORY_L2_DIFF_INTERACTIVE_COVERAGE_PROBE.json"
    metrics_json = run_dir / "EGO_SINGLE_METRICS.json"
    coverage_json = run_dir / "coverage_packet" / "FACTORY_L2_INDOOR_COVERAGE_PACKET.json"
    monitor_json = run_dir / "terminal_monitor.json"
    cooldown_key = f"factory_diff_coverage_terminal:{run_dir.name}"
    deadline = time.time() + max(0.1, args.max_hours) * 3600.0

    while time.time() < deadline:
        source = final_json if final_json.exists() else partial_json
        payload = read_json(source)
        status = str(payload.get("status") or "")
        blockers = payload.get("blockers")
        manifest = read_json(manifest_json)
        metrics = read_json(metrics_json)
        coverage = read_json(coverage_json)
        terminal = bool(blockers) or status in {"failed", "blocked", "review_required_or_blocked"}
        if source == final_json and status == "passed":
            terminal = manifest_json.exists()
        if terminal or blockers:
            subject, body = summarize(run_dir, payload, manifest, metrics, coverage)
            email = send_email(subject, body, cooldown_key)
            record = {
                "status": "terminal_observed",
                "source": str(source),
                "observed_status": status,
                "blockers": blockers,
                "email": email,
                "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            }
            monitor_json.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return 0 if email.get("returncode") == 0 else 2
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
