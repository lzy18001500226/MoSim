#!/usr/bin/env python3
"""Measure task-level RTF for one live qgc_realtime_goal run.

The task window starts when the bridge request is submitted and ends when the
runtime gate writes a terminal status. This is deliberately separate from
Gazebo sensor pacing measurements.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import tempfile
import threading
import time
from collections import deque
from typing import Any


TERMINAL_STATES = {"completed", "blocked"}


def _read_json(path: pathlib.Path) -> dict[str, Any] | None:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _finite(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _sha256(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return None
    return digest.hexdigest()


def _nearest_clock(
    samples: deque[tuple[float, float]],
    target_wall_s: float,
    current: tuple[float, float] | None,
) -> dict[str, float | str] | None:
    if samples:
        wall_s, sim_s = min(samples, key=lambda item: abs(item[0] - target_wall_s))
        return {
            "wall_unix_s": wall_s,
            "sim_s": sim_s,
            "wall_delta_s": wall_s - target_wall_s,
            "selection": "nearest_history_sample",
        }
    if current is None:
        return None
    wall_s, sim_s = current
    return {
        "wall_unix_s": wall_s,
        "sim_s": sim_s,
        "wall_delta_s": wall_s - target_wall_s,
        "selection": "latest_sample",
    }


def _atomic_write(path: pathlib.Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _configuration_snapshot(result_dir: pathlib.Path) -> dict[str, Any]:
    runtime_dir = result_dir / "runtime"
    overlay = _read_json(runtime_dir / "factory_l2_world_overlay.json")
    runtime_manifest = _read_json(runtime_dir / "RUN_MANIFEST.json")
    snapshot: dict[str, Any] = {
        "result_dir": str(result_dir),
        "artifacts": {},
    }
    for relative in (
        "factory_l2_model_overlay.txt",
        "sunray_livox_plugin_source.sha256",
        "sunray_livox_plugin.sha256",
        "runtime/mid360_ray_backend.txt",
        "runtime/factory_l2_world_overlay.json",
        "runtime/RUN_MANIFEST.json",
    ):
        path = result_dir / relative
        snapshot["artifacts"][relative] = {
            "path": str(path),
            "sha256": _sha256(path),
        }
    if overlay is not None:
        snapshot["world_overlay"] = {
            "source": overlay.get("source"),
            "output": overlay.get("output"),
            "world": overlay.get("world"),
        }
    if runtime_manifest is not None:
        snapshot["runtime_manifest"] = {
            "world_file": runtime_manifest.get("world_file"),
            "gazebo_launch_file": runtime_manifest.get("gazebo_launch_file"),
            "uav_init": runtime_manifest.get("uav_init"),
            "vehicle": runtime_manifest.get("vehicle"),
            "use_sim_time": runtime_manifest.get("use_sim_time"),
            "controller_core_profile": runtime_manifest.get("controller_core_profile"),
            "planner_variant": runtime_manifest.get("planner_variant"),
            "mission_mode": runtime_manifest.get("mission_mode"),
            "gazebo": runtime_manifest.get("gazebo"),
            "px4ctrl": runtime_manifest.get("px4ctrl"),
            "fastlio": runtime_manifest.get("fastlio"),
            "interactive_click_goal": runtime_manifest.get("interactive_click_goal"),
        }
    return snapshot


def _load_ros() -> tuple[Any, Any, Any]:
    import rosgraph  # type: ignore
    import rospy  # type: ignore
    from rosgraph_msgs.msg import Clock  # type: ignore

    return rosgraph, rospy, Clock


def run(args: argparse.Namespace) -> int:
    run_dir = pathlib.Path(args.run_dir).resolve()
    result_dir = pathlib.Path(args.result_dir).resolve()
    request_path = run_dir / "operator_goal" / "REQUEST.json"
    status_path = result_dir / "QGC_REALTIME_GOAL_RUNTIME_STATUS.json"
    output_path = pathlib.Path(args.output).resolve()
    samples: deque[tuple[float, float]] = deque(maxlen=4000)
    latest: list[tuple[float, float] | None] = [None]
    lock = threading.Lock()
    ros_started = False
    rospy = None

    try:
        rosgraph, rospy, clock_type = _load_ros()
    except ImportError as exc:
        _atomic_write(
            output_path,
            {
                "schema": "mosim.qgc_task_rtf.v1",
                "status": "blocked",
                "reason_code": "ros_python_import_failed",
                "error": str(exc),
                "run_id": args.run_id,
            },
        )
        return 2

    def on_clock(message: Any) -> None:
        sim_s = float(message.clock.secs) + float(message.clock.nsecs) * 1.0e-9
        wall_s = time.time()
        with lock:
            sample = (wall_s, sim_s)
            samples.append(sample)
            latest[0] = sample

    deadline = time.monotonic() + args.timeout_s
    request: dict[str, Any] | None = None
    start_wall_s: float | None = None
    start_clock: dict[str, Any] | None = None
    terminal_status: dict[str, Any] | None = None
    end_wall_s: float | None = None
    end_clock: dict[str, Any] | None = None

    while time.monotonic() < deadline:
        if not ros_started and rosgraph.is_master_online():
            try:
                rospy.init_node(
                    f"mosim_qgc_task_rtf_{args.run_id[-12:]}",
                    anonymous=True,
                    disable_signals=True,
                )
                rospy.Subscriber(args.clock_topic, clock_type, on_clock, queue_size=100)
                ros_started = True
            except Exception:
                ros_started = False

        if request is None:
            request = _read_json(request_path)
            submitted_at = _finite(request.get("submitted_at_unix_s")) if request else None
            if request and submitted_at is not None:
                with lock:
                    history = deque(samples)
                    current = latest[0]
                start_wall_s = submitted_at
                start_clock = _nearest_clock(history, submitted_at, current)

        if request is not None and terminal_status is None:
            candidate = _read_json(status_path)
            if candidate and candidate.get("run_id") == args.run_id and candidate.get("state") in TERMINAL_STATES:
                terminal_status = candidate
                end_wall_s = _finite(candidate.get("updated_at_unix_s")) or time.time()
                with lock:
                    history = deque(samples)
                    current = latest[0]
                end_clock = _nearest_clock(history, end_wall_s, current)
                break

        time.sleep(args.poll_s)

    terminal_before_request = (
        request is not None
        and terminal_status is not None
        and start_wall_s is not None
        and end_wall_s is not None
        and end_wall_s < start_wall_s
    )

    if request is None:
        status = "blocked"
        reason = "qgc_task_request_not_observed"
    elif terminal_status is None:
        status = "blocked"
        reason = "qgc_task_terminal_status_not_observed"
    elif terminal_before_request:
        status = "blocked"
        reason = "qgc_task_terminal_before_request"
    elif start_clock is None or end_clock is None or start_wall_s is None or end_wall_s is None:
        status = "blocked"
        reason = "qgc_task_clock_boundary_missing"
    else:
        status = "completed" if terminal_status.get("state") == "completed" else "blocked"
        reason = (
            "qgc_task_rtf_measured"
            if status == "completed"
            else str(terminal_status.get("reason_code") or "qgc_task_runtime_blocked")
        )

    wall_span_s = None
    clock_span_s = None
    task_rtf = None
    if start_clock and end_clock and start_wall_s is not None and end_wall_s is not None:
        wall_span_s = end_wall_s - start_wall_s
        clock_span_s = float(end_clock["sim_s"]) - float(start_clock["sim_s"])
        if wall_span_s > 0.0 and clock_span_s >= 0.0:
            task_rtf = clock_span_s / wall_span_s

    payload = {
        "schema": "mosim.qgc_task_rtf.v1",
        "status": status,
        "reason_code": reason,
        "run_id": args.run_id,
        "source": "live_ros1_clock_and_qgc_runtime_status",
        "task_boundary": {
            "start": "qgc_realtime_goal_request.submitted_at_unix_s",
            "end": "QGC_REALTIME_GOAL_RUNTIME_STATUS.updated_at_unix_s with terminal state",
            "excludes": ["Gazebo cold start before the goal request", "post-terminal cleanup"],
        },
        "request": {
            "path": str(request_path),
            "request_id": request.get("request_id") if request else None,
            "submitted_at_unix_s": _finite(request.get("submitted_at_unix_s")) if request else None,
        },
        "terminal_runtime_status": {
            "path": str(status_path),
            "state": terminal_status.get("state") if terminal_status else None,
            "reason_code": terminal_status.get("reason_code") if terminal_status else None,
            "updated_at_unix_s": end_wall_s,
        },
        "clock_topic": args.clock_topic,
        "clock_start": start_clock,
        "clock_end": end_clock,
        "wall_start_unix_s": start_wall_s,
        "wall_end_unix_s": end_wall_s,
        "wall_span_s": wall_span_s,
        "clock_span_s": clock_span_s,
        "task_rtf": task_rtf,
        "configuration": _configuration_snapshot(result_dir),
    }
    _atomic_write(output_path, payload)
    return 0 if status == "completed" and task_rtf is not None else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--result-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--clock-topic", default="/clock")
    parser.add_argument("--poll-s", type=float, default=0.10)
    parser.add_argument("--timeout-s", type=float, default=3600.0)
    args = parser.parse_args()
    if args.poll_s <= 0.0 or args.timeout_s <= 0.0:
        parser.error("--poll-s and --timeout-s must be positive")
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
