#!/usr/bin/env python3
"""Collect process-tree and GPU resource samples for a bounded Factory L2 probe."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STOP_REQUESTED = threading.Event()


def project_result_path(value: str) -> Path:
    path = Path(value)
    resolved = (path if path.is_absolute() else ROOT / path).resolve()
    results_root = (ROOT / "Results").resolve()
    if resolved != results_root and results_root not in resolved.parents:
        raise ValueError(f"--output must remain below {results_root}: {value}")
    return resolved


def parse_process_rows(output: str) -> list[dict[str, Any]]:
    processes: list[dict[str, Any]] = []
    for line in output.splitlines():
        fields = line.strip().split(None, 6)
        if len(fields) != 7:
            continue
        try:
            processes.append(
                {
                    "pid": int(fields[0]),
                    "ppid": int(fields[1]),
                    "cpu_percent": float(fields[2]),
                    "memory_percent": float(fields[3]),
                    "rss_kib": int(fields[4]),
                    "command": fields[5],
                    "arguments": fields[6],
                }
            )
        except ValueError:
            continue
    return processes


def descendant_process_ids(processes: list[dict[str, Any]], root_pid: int) -> set[int]:
    children: dict[int, list[int]] = {}
    known_pids: set[int] = set()
    for process in processes:
        pid = int(process["pid"])
        known_pids.add(pid)
        children.setdefault(int(process["ppid"]), []).append(pid)
    if root_pid not in known_pids:
        return set()

    descendants = {root_pid}
    pending = [root_pid]
    while pending:
        parent_pid = pending.pop()
        for child_pid in children.get(parent_pid, []):
            if child_pid not in descendants:
                descendants.add(child_pid)
                pending.append(child_pid)
    return descendants


def process_snapshot() -> tuple[list[dict[str, Any]], str | None]:
    environment = dict(os.environ)
    environment["LC_ALL"] = "C"
    environment["LANG"] = "C"
    try:
        completed = subprocess.run(
            ["ps", "-eo", "pid=,ppid=,pcpu=,pmem=,rss=,comm=,args="],
            check=False,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=environment,
        )
    except OSError as exc:
        return [], str(exc)
    if completed.returncode != 0:
        return [], completed.stderr.strip() or f"ps exited {completed.returncode}"
    return parse_process_rows(completed.stdout), None


def gpu_snapshot() -> dict[str, Any]:
    command = [
        "nvidia-smi",
        "--query-gpu=timestamp,utilization.gpu,utilization.memory,memory.used,power.draw,pstate",
        "--format=csv,noheader,nounits",
    ]
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        return {"available": False, "error": str(exc), "rows": []}
    if completed.returncode != 0:
        return {
            "available": False,
            "error": completed.stderr.strip() or f"nvidia-smi exited {completed.returncode}",
            "rows": [],
        }

    names = [
        "timestamp",
        "utilization_gpu_percent",
        "utilization_memory_percent",
        "memory_used_mib",
        "power_draw_w",
        "pstate",
    ]
    rows = []
    for line in completed.stdout.splitlines():
        values = [value.strip() for value in line.split(",")]
        if len(values) == len(names):
            rows.append(dict(zip(names, values)))
    return {"available": True, "error": "", "rows": rows}


def write_sample(handle: Any, root_pid: int) -> bool:
    processes, process_error = process_snapshot()
    descendant_ids = descendant_process_ids(processes, root_pid)
    payload = {
        "schema": "mosim.factory_l2_runtime_resource_sample.v1",
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "root_pid": root_pid,
        "root_alive": root_pid in descendant_ids,
        "process_snapshot_error": process_error or "",
        "processes": [process for process in processes if int(process["pid"]) in descendant_ids],
        "gpu": gpu_snapshot(),
    }
    handle.write(json.dumps(payload, sort_keys=True) + "\n")
    handle.flush()
    return bool(payload["root_alive"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="JSONL output path below Results/")
    parser.add_argument("--root-pid", type=int, required=True)
    parser.add_argument("--interval-s", type=float, default=1.0)
    args = parser.parse_args()
    if args.root_pid <= 0:
        parser.error("--root-pid must be positive")
    if args.interval_s <= 0:
        parser.error("--interval-s must be positive")
    return args


def request_stop(_signal: int, _frame: Any) -> None:
    STOP_REQUESTED.set()


def main() -> int:
    args = parse_args()
    output_path = project_result_path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    with output_path.open("w", encoding="utf-8") as handle:
        while not STOP_REQUESTED.is_set():
            root_alive = write_sample(handle, args.root_pid)
            if not root_alive:
                break
            STOP_REQUESTED.wait(args.interval_s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
