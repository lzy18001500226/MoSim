#!/usr/bin/env python3
"""Orbit the Gazebo GUI follow camera around the UAV with arrow keys."""

from __future__ import annotations

import argparse
import json
import math
import re
import select
import subprocess
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def parse_key_code(line: str) -> int | None:
    match = re.search(r"\bdata:\s*(-?\d+)", line)
    if not match:
        return None
    return int(match.group(1))


def request_vector3d_service(
    command: str,
    service: str,
    xyz: tuple[float, float, float],
    timeout_s: float,
) -> tuple[int, str, str]:
    x, y, z = xyz
    try:
        completed = subprocess.run(
            [
                command,
                "service",
                "-s",
                service,
                "--reqtype",
                "ignition.msgs.Vector3d",
                "--reptype",
                "ignition.msgs.Boolean",
                "--timeout",
                str(int(max(0.1, timeout_s) * 1000)),
                "--req",
                f"x: {x:.6f} y: {y:.6f} z: {z:.6f}",
            ],
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=max(0.1, timeout_s),
        )
        return int(completed.returncode), completed.stdout, completed.stderr
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or f"{service} request timeout"
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return 124, stdout, stderr


def spherical_from_xyz(x: float, y: float, z: float) -> tuple[float, float, float]:
    radius = math.sqrt(x * x + y * y + z * z)
    if radius <= 0.0:
        raise ValueError("camera radius must be positive")
    azimuth = math.atan2(y, x)
    elevation = math.asin(max(-1.0, min(1.0, z / radius)))
    return radius, azimuth, elevation


def xyz_from_spherical(radius: float, azimuth: float, elevation: float) -> tuple[float, float, float]:
    horizontal = radius * math.cos(elevation)
    return (
        horizontal * math.cos(azimuth),
        horizontal * math.sin(azimuth),
        radius * math.sin(elevation),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", default="ign")
    parser.add_argument("--target", default="sunray150_assembled")
    parser.add_argument("--keyboard-topic", default="/keyboard/keypress")
    parser.add_argument("--offset-service", default="/gui/follow/offset")
    parser.add_argument("--initial-offset-x-m", type=float, default=-0.233)
    parser.add_argument("--initial-offset-y-m", type=float, default=-0.933)
    parser.add_argument("--initial-offset-z-m", type=float, default=0.467)
    parser.add_argument("--azimuth-step-deg", type=float, default=8.0)
    parser.add_argument("--elevation-step-deg", type=float, default=5.0)
    parser.add_argument("--min-elevation-deg", type=float, default=8.0)
    parser.add_argument("--max-elevation-deg", type=float, default=75.0)
    parser.add_argument("--left-key", type=int, default=16777234)
    parser.add_argument("--up-key", type=int, default=16777235)
    parser.add_argument("--right-key", type=int, default=16777236)
    parser.add_argument("--down-key", type=int, default=16777237)
    parser.add_argument("--duration-s", type=float, default=60.0)
    parser.add_argument("--timeout-s", type=float, default=1.0)
    parser.add_argument("--summary-json", required=True, type=Path)
    parser.add_argument("--trace-jsonl", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary_json = project_path(args.summary_json)
    trace_jsonl = project_path(args.trace_jsonl)
    trace_jsonl.parent.mkdir(parents=True, exist_ok=True)
    trace_jsonl.write_text("", encoding="utf-8")

    radius, azimuth, elevation = spherical_from_xyz(
        args.initial_offset_x_m,
        args.initial_offset_y_m,
        args.initial_offset_z_m,
    )
    azimuth_step = math.radians(args.azimuth_step_deg)
    elevation_step = math.radians(args.elevation_step_deg)
    min_elevation = math.radians(args.min_elevation_deg)
    max_elevation = math.radians(args.max_elevation_deg)
    deadline = time.monotonic() + max(0.0, args.duration_s)
    key_counts = {
        "left": 0,
        "right": 0,
        "up": 0,
        "down": 0,
        "unmapped": 0,
    }
    service_successes = 0
    service_failures = 0
    last_offset = xyz_from_spherical(radius, azimuth, elevation)
    last_rc: int | None = None
    last_stdout = ""
    last_stderr = ""

    rc, stdout, stderr = request_vector3d_service(args.command, args.offset_service, last_offset, args.timeout_s)
    last_rc = rc
    last_stdout = stdout[-500:]
    last_stderr = stderr[-500:]
    if rc == 0 and "timeout" not in stderr.lower() and "Unable to create message" not in stderr:
        service_successes += 1
    else:
        service_failures += 1
    append_jsonl(
        trace_jsonl,
        {
            "event": "initial_offset",
            "target": args.target,
            "offset_m": list(last_offset),
            "radius_m": radius,
            "rc": rc,
            "stderr": last_stderr,
        },
    )

    try:
        proc = subprocess.Popen(
            [args.command, "topic", "-e", "-t", args.keyboard_topic],
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        write_json(
            summary_json,
            {
                "schema": "mosim.gazebo_camera_orbit.v1",
                "status": "blocked",
                "reason": f"missing command: {args.command}",
                "error": str(exc),
            },
        )
        return 2

    try:
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                break
            if proc.stdout is None:
                break
            readable, _, _ = select.select([proc.stdout], [], [], 0.25)
            if not readable:
                continue
            line = proc.stdout.readline()
            if not line:
                continue
            code = parse_key_code(line)
            if code is None:
                continue
            direction = "unmapped"
            if code == args.left_key:
                azimuth += azimuth_step
                direction = "left"
            elif code == args.right_key:
                azimuth -= azimuth_step
                direction = "right"
            elif code == args.up_key:
                elevation = min(max_elevation, elevation + elevation_step)
                direction = "up"
            elif code == args.down_key:
                elevation = max(min_elevation, elevation - elevation_step)
                direction = "down"
            key_counts[direction] += 1
            if direction == "unmapped":
                append_jsonl(
                    trace_jsonl,
                    {
                        "event": "unmapped_key",
                        "key_code": code,
                        "raw": line.strip(),
                    },
                )
                continue
            last_offset = xyz_from_spherical(radius, azimuth, elevation)
            rc, stdout, stderr = request_vector3d_service(
                args.command,
                args.offset_service,
                last_offset,
                args.timeout_s,
            )
            last_rc = rc
            last_stdout = stdout[-500:]
            last_stderr = stderr[-500:]
            if rc == 0 and "timeout" not in stderr.lower() and "Unable to create message" not in stderr:
                service_successes += 1
            else:
                service_failures += 1
            append_jsonl(
                trace_jsonl,
                {
                    "event": "orbit_key",
                    "key_code": code,
                    "direction": direction,
                    "offset_m": list(last_offset),
                    "radius_m": radius,
                    "azimuth_deg": math.degrees(azimuth),
                    "elevation_deg": math.degrees(elevation),
                    "rc": rc,
                    "stderr": last_stderr,
                },
            )
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                proc.kill()
        stderr_tail = ""
        if proc.stderr is not None:
            try:
                stderr_tail = proc.stderr.read()[-500:]
            except Exception:
                stderr_tail = ""

    status = "running" if service_successes > 0 else "blocked"
    payload: dict[str, Any] = {
        "schema": "mosim.gazebo_camera_orbit.v1",
        "status": status,
        "target": args.target,
        "keyboard_topic": args.keyboard_topic,
        "offset_service": args.offset_service,
        "initial_offset_m": [args.initial_offset_x_m, args.initial_offset_y_m, args.initial_offset_z_m],
        "last_offset_m": list(last_offset),
        "radius_m": radius,
        "radius_preserved": abs(math.sqrt(sum(v * v for v in last_offset)) - radius) < 1e-6,
        "body_frame": "+X nose/front, -X tail/rear, +Y left, +Z up",
        "default_view": "left-rear-up, back:left:up = 4:1:2",
        "arrow_key_codes": {
            "left": args.left_key,
            "up": args.up_key,
            "right": args.right_key,
            "down": args.down_key,
        },
        "key_counts": key_counts,
        "service_successes": service_successes,
        "service_failures": service_failures,
        "last_rc": last_rc,
        "last_stdout": last_stdout,
        "last_stderr": last_stderr,
        "topic_stderr_tail": stderr_tail,
        "trace_jsonl": str(trace_jsonl),
        "claim_boundary": "Gazebo GUI camera offset only; this script never publishes UAV control, setpoint, actuator, planner, or ROS2 command topics.",
    }
    write_json(summary_json, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if service_successes > 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
