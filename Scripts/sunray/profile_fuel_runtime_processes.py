#!/usr/bin/env python3
"""Collect interval CPU and memory samples for the FUEL ROS1 runtime chain.

The sampler intentionally observes only the current Sunray/Gazebo runtime.  It
does not publish ROS messages, change launch parameters, or control a process.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import signal
import statistics
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProcessSnapshot:
    pid: int
    start_ticks: int
    cpu_ticks: int
    rss_kb: int
    group: str
    command: str


RUNNING = True


def classify_process(comm: str, command: str) -> str | None:
    """Return a stable label for an expensive FUEL runtime process."""
    if command.startswith("/bin/sh ") and "gazebo_ros/gzserver" in command:
        return None
    if command.startswith("bash -c sleep ") and "mavros_node" in command:
        return None
    if comm == "gzserver" or "gzserver" in command:
        return "gzserver"
    if comm == "fastlio_mapping" or "fast_lio/fastlio_mapping" in command:
        return "fastlio_mapping"
    if "goal4_pointcloud_to_world_node.py" in command:
        return "pointcloud_world_transform"
    if "pointcloud2_to_livox_custom_msg.py" in command:
        return "livox_custom_conversion"
    if "exploration_node" in command:
        return "fuel_exploration"
    if "accumulate_pointcloud_review.py" in command:
        return "review_accumulation"
    if comm == "px4ctrl_node" or "/px4ctrl_node" in command:
        return "px4ctrl"
    if comm == "mavros_node" or "/mavros_node" in command:
        return "mavros"
    if comm == "px4" and ("sunray_px4" in command or "px4_ros1_runtime_overlay" in command):
        return "px4_sitl"
    return None


def parse_proc_stat(raw: str) -> tuple[int, int, int, int]:
    """Return start ticks, CPU ticks, and resident pages from /proc/<pid>/stat."""
    try:
        trailing = raw.rsplit(")", 1)[1].split()
        utime = int(trailing[11])
        stime = int(trailing[12])
        start_ticks = int(trailing[19])
        resident_pages = int(trailing[21])
    except (IndexError, ValueError) as exc:
        raise ValueError("unexpected /proc stat format") from exc
    return start_ticks, utime + stime, resident_pages, len(trailing)


def read_process_snapshot(proc_root: Path, pid: int, page_size_kb: int) -> ProcessSnapshot | None:
    proc_dir = proc_root / str(pid)
    try:
        stat = (proc_dir / "stat").read_text(encoding="utf-8")
        comm = (proc_dir / "comm").read_text(encoding="utf-8").strip()
        command = (proc_dir / "cmdline").read_bytes().replace(b"\0", b" ").decode(
            "utf-8", errors="replace"
        ).strip()
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return None
    command = command or comm
    group = classify_process(comm, command)
    if group is None:
        return None
    try:
        start_ticks, cpu_ticks, resident_pages, _ = parse_proc_stat(stat)
    except ValueError:
        return None
    return ProcessSnapshot(
        pid=pid,
        start_ticks=start_ticks,
        cpu_ticks=cpu_ticks,
        rss_kb=resident_pages * page_size_kb,
        group=group,
        command=command,
    )


def collect_snapshots(proc_root: Path, page_size_kb: int) -> list[ProcessSnapshot]:
    snapshots: list[ProcessSnapshot] = []
    for child in proc_root.iterdir():
        if not child.name.isdigit():
            continue
        snapshot = read_process_snapshot(proc_root, int(child.name), page_size_kb)
        if snapshot is not None:
            snapshots.append(snapshot)
    return sorted(snapshots, key=lambda item: (item.group, item.pid))


def percentile(values: list[float], quantile: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    index = int(round((len(values) - 1) * quantile))
    return values[index]


def summarize(rows: list[dict]) -> dict:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        if row["cpu_percent"] is not None:
            grouped[row["group"]].append(row)
    groups: dict[str, dict] = {}
    for group, group_rows in sorted(grouped.items()):
        cpu_values = [float(row["cpu_percent"]) for row in group_rows]
        rss_values = [float(row["rss_mb"]) for row in group_rows]
        groups[group] = {
            "samples": len(group_rows),
            "pids": sorted({int(row["pid"]) for row in group_rows}),
            "cpu_percent_mean": round(statistics.fmean(cpu_values), 3),
            "cpu_percent_p95": round(percentile(cpu_values, 0.95) or 0.0, 3),
            "cpu_percent_max": round(max(cpu_values), 3),
            "rss_mb_mean": round(statistics.fmean(rss_values), 3),
            "rss_mb_max": round(max(rss_values), 3),
        }
    return groups


def request_stop(_signum: int, _frame: object) -> None:
    global RUNNING
    RUNNING = False


def run_sampler(args: argparse.Namespace) -> int:
    output_csv = Path(args.output_csv).resolve()
    output_json = Path(args.output_json).resolve()
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    proc_root = Path(args.proc_root)
    page_size_kb = max(1, os.sysconf("SC_PAGE_SIZE") // 1024)
    clock_ticks = max(1, int(os.sysconf("SC_CLK_TCK")))
    start_monotonic = time.monotonic()
    previous: dict[tuple[int, int], tuple[int, float]] = {}
    rows: list[dict] = []
    observed_groups: set[str] = set()
    sample_count = 0

    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)

    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "sample_index",
                "wall_time_s",
                "elapsed_s",
                "group",
                "pid",
                "cpu_percent",
                "rss_mb",
                "command",
            ],
        )
        writer.writeheader()
        while RUNNING:
            now = time.monotonic()
            elapsed_s = now - start_monotonic
            if elapsed_s >= args.max_runtime_s:
                break
            snapshots = collect_snapshots(proc_root, page_size_kb)
            for snapshot in snapshots:
                observed_groups.add(snapshot.group)
                key = (snapshot.pid, snapshot.start_ticks)
                old = previous.get(key)
                cpu_percent = None
                if old is not None:
                    old_ticks, old_time = old
                    interval_s = now - old_time
                    if interval_s > 0.0:
                        cpu_percent = 100.0 * (snapshot.cpu_ticks - old_ticks) / (clock_ticks * interval_s)
                previous[key] = (snapshot.cpu_ticks, now)
                row = {
                    "sample_index": sample_count,
                    "wall_time_s": round(time.time(), 6),
                    "elapsed_s": round(elapsed_s, 6),
                    "group": snapshot.group,
                    "pid": snapshot.pid,
                    "cpu_percent": None if cpu_percent is None else round(max(0.0, cpu_percent), 4),
                    "rss_mb": round(snapshot.rss_kb / 1024.0, 4),
                    "command": snapshot.command,
                }
                rows.append(row)
                writer.writerow(row)
            handle.flush()
            sample_count += 1
            if not observed_groups and elapsed_s >= args.startup_wait_s:
                break
            time.sleep(args.sample_period_s)

    payload = {
        "schema": "mosim.fuel_runtime_process_profile.v1",
        "status": "sampled" if rows else "no_matching_processes",
        "sample_period_s": args.sample_period_s,
        "max_runtime_s": args.max_runtime_s,
        "startup_wait_s": args.startup_wait_s,
        "elapsed_s": round(time.monotonic() - start_monotonic, 3),
        "sample_count": sample_count,
        "observed_groups": sorted(observed_groups),
        "groups": summarize(rows),
        "csv": str(output_csv),
    }
    output_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0 if rows else 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-csv", default="")
    parser.add_argument("--output-json", default="")
    parser.add_argument("--sample-period-s", type=float, default=1.0)
    parser.add_argument("--startup-wait-s", type=float, default=180.0)
    parser.add_argument("--max-runtime-s", type=float, default=900.0)
    parser.add_argument("--proc-root", default="/proc")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.sample_period_s <= 0.0:
        parser.error("--sample-period-s must be positive")
    if args.startup_wait_s < 0.0:
        parser.error("--startup-wait-s must be non-negative")
    if args.max_runtime_s <= 0.0:
        parser.error("--max-runtime-s must be positive")
    if not args.self_test and (not args.output_csv or not args.output_json):
        parser.error("--output-csv and --output-json are required unless --self-test is used")
    return args


def self_test() -> int:
    assert classify_process("gzserver", "gzserver -e ode") == "gzserver"
    assert classify_process("gzserver", "/bin/sh /opt/ros/noetic/lib/gazebo_ros/gzserver -e ode") is None
    assert classify_process("python3", "goal4_pointcloud_to_world_node.py") == "pointcloud_world_transform"
    assert classify_process("fastlio_mapping", "/opt/fast_lio/fastlio_mapping") == "fastlio_mapping"
    assert classify_process("python3", "unrelated.py") is None
    fields = ["R", "1"] + ["0"] * 9 + ["12", "13"] + ["0"] * 6 + ["55", "0", "99"]
    start_ticks, cpu_ticks, resident_pages, count = parse_proc_stat("123 (demo worker) " + " ".join(fields))
    assert start_ticks == 55
    assert cpu_ticks == 25
    assert resident_pages == 99
    assert count == len(fields)
    return 0


def main() -> None:
    args = parse_args()
    if args.self_test:
        raise SystemExit(self_test())
    raise SystemExit(run_sampler(args))


if __name__ == "__main__":
    main()
