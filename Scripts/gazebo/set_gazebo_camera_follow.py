#!/usr/bin/env python3
"""Request Gazebo GUI camera tracking for the UAV review target."""

from __future__ import annotations

import argparse
import json
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


def request_service(
    command: str,
    service: str,
    reqtype: str,
    reptype: str,
    req: str,
    timeout_s: float,
) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            [
                command,
                "service",
                "-s",
                service,
                "--reqtype",
                reqtype,
                "--reptype",
                reptype,
                "--timeout",
                str(int(max(0.1, timeout_s) * 1000)),
                "--req",
                req,
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
    except FileNotFoundError as exc:
        return 127, "", f"{command} not found: {exc}"
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or f"{service} request timeout"
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return 124, stdout, stderr


def request_vector3d_service(
    command: str,
    service: str,
    xyz: tuple[float, float, float],
    timeout_s: float,
) -> tuple[int, str, str]:
    x, y, z = xyz
    return request_service(
        command,
        service,
        "ignition.msgs.Vector3d",
        "ignition.msgs.Boolean",
        f"x: {x:.6f} y: {y:.6f} z: {z:.6f}",
        timeout_s,
    )


def publish_follow(
    command: str,
    topic: str,
    target: str,
    timeout_s: float,
    *,
    offset: tuple[float, float, float],
    min_dist: float,
    max_dist: float,
    inherit_yaw: bool,
    use_model_frame: bool,
) -> tuple[int, str, str]:
    x, y, z = offset
    payload = (
        f'name: "{target}" '
        f"min_dist: {min_dist:.6f} "
        f"max_dist: {max_dist:.6f} "
        f"static: false "
        f"use_model_frame: {'true' if use_model_frame else 'false'} "
        f"xyz {{ x: {x:.6f} y: {y:.6f} z: {z:.6f} }} "
        f"inherit_yaw: {'true' if inherit_yaw else 'false'}"
    )
    try:
        completed = subprocess.run(
            [command, "topic", "-t", topic, "-m", "ignition.msgs.TrackVisual", "-p", payload],
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=max(0.1, timeout_s),
        )
        return int(completed.returncode), completed.stdout, completed.stderr
    except FileNotFoundError as exc:
        return 127, "", f"{command} not found: {exc}"
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or "camera follow publish timeout"
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return 124, stdout, stderr


def activate_follow(
    command: str,
    topic: str,
    target: str,
    timeout_s: float,
    *,
    offset: tuple[float, float, float],
    min_dist: float,
    max_dist: float,
    inherit_yaw: bool,
    use_model_frame: bool,
    allow_service_fallback: bool,
) -> tuple[int, str, str, str]:
    if allow_service_fallback:
        rc0, stdout0, stderr0 = request_service(
            command,
            "/gui/follow",
            "ignition.msgs.StringMsg",
            "ignition.msgs.Boolean",
            f'data: "{target}"',
            timeout_s,
        )
        rc1, stdout1, stderr1 = request_vector3d_service(command, "/gui/follow/offset", offset, timeout_s)
        if (
            rc0 == 0
            and rc1 == 0
            and "Unable to create message" not in stderr0
            and "Unable to create message" not in stderr1
            and "timeout" not in stderr0.lower()
            and "timeout" not in stderr1.lower()
        ):
            return (
                0,
                (stdout0 + "\n" + stdout1)[-1000:],
                (stderr0 + "\n" + stderr1)[-1000:],
                "service:/gui/follow+/gui/follow/offset",
            )
    rc, stdout, stderr = publish_follow(
        command,
        topic,
        target,
        timeout_s,
        offset=offset,
        min_dist=min_dist,
        max_dist=max_dist,
        inherit_yaw=inherit_yaw,
        use_model_frame=use_model_frame,
    )
    if rc == 0 and "Unable to create message" not in stderr and "timeout" not in stderr.lower():
        return rc, stdout, stderr, f"topic:{topic}:TrackVisual"
    if not allow_service_fallback:
        return rc, stdout, stderr, f"topic:{topic}:TrackVisual"
    rc2, stdout2, stderr2 = request_service(
        command,
        "/gui/follow",
        "ignition.msgs.StringMsg",
        "ignition.msgs.Boolean",
        f'data: "{target}"',
        timeout_s,
    )
    if rc2 == 0 and "Unable to create message" not in stderr2 and "timeout" not in stderr2.lower():
        return rc2, stdout2, stderr2, "service:/gui/follow"
    rc3, stdout3, stderr3 = request_service(
        command,
        "/gui/move_to",
        "ignition.msgs.StringMsg",
        "ignition.msgs.Boolean",
        f'data: "{target}"',
        timeout_s,
    )
    return rc3, stdout3, stderr3, "service:/gui/move_to"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default="/gui/track")
    parser.add_argument("--target", default="sunray150_assembled")
    parser.add_argument("--command", default="ign")
    parser.add_argument("--offset-x-m", type=float, default=-0.233)
    parser.add_argument("--offset-y-m", type=float, default=-0.933)
    parser.add_argument("--offset-z-m", type=float, default=0.467)
    parser.add_argument("--min-dist-m", type=float, default=0.8)
    parser.add_argument("--max-dist-m", type=float, default=5.0)
    parser.add_argument("--inherit-yaw", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--use-model-frame", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--allow-service-fallback", action="store_true")
    parser.add_argument("--start-delay-s", type=float, default=2.0)
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--interval-s", type=float, default=0.5)
    parser.add_argument("--timeout-s", type=float, default=1.5)
    parser.add_argument("--summary-json", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary_json = project_path(args.summary_json)
    offset = (args.offset_x_m, args.offset_y_m, args.offset_z_m)
    payload: dict[str, Any] = {
        "schema": "mosim.gazebo_camera_follow_request.v1",
        "status": "starting",
        "topic": args.topic,
        "target": args.target,
        "offset_m": [args.offset_x_m, args.offset_y_m, args.offset_z_m],
        "offset_source": "body-frame left-rear-up review camera: +X nose, -X rear, +Y left, +Z up; default ratio back:left:up = 4:1:2",
        "min_dist_m": args.min_dist_m,
        "max_dist_m": args.max_dist_m,
        "inherit_yaw": bool(args.inherit_yaw),
        "use_model_frame": bool(args.use_model_frame),
        "allow_service_fallback": bool(args.allow_service_fallback),
        "attempts": 0,
        "successes": 0,
        "last_method": "",
        "last_rc": None,
        "last_stdout": "",
        "last_stderr": "",
        "claim_boundary": "GUI camera-follow request only; visual acceptance still depends on live Gazebo review. Service fallback is disabled by default because /gui/follow does not carry the review offset.",
    }
    write_json(summary_json, payload)
    time.sleep(max(0.0, args.start_delay_s))

    attempts = 0
    successes = 0
    last_rc: int | None = None
    last_stdout = ""
    last_stderr = ""
    last_method = ""
    for _ in range(max(1, args.repeat)):
        attempts += 1
        rc, stdout, stderr, method = activate_follow(
            args.command,
            args.topic,
            args.target,
            args.timeout_s,
            offset=offset,
            min_dist=args.min_dist_m,
            max_dist=args.max_dist_m,
            inherit_yaw=bool(args.inherit_yaw),
            use_model_frame=bool(args.use_model_frame),
            allow_service_fallback=bool(args.allow_service_fallback),
        )
        last_rc = rc
        last_stdout = stdout[-500:]
        last_stderr = stderr[-500:]
        last_method = method
        if rc == 0 and "Unable to create message" not in stderr and "timeout" not in stderr.lower():
            successes += 1
        payload.update(
            {
                "status": "published" if successes else "attempting",
                "attempts": attempts,
                "successes": successes,
                "last_method": last_method,
                "last_rc": last_rc,
                "last_stdout": last_stdout,
                "last_stderr": last_stderr,
            }
        )
        write_json(summary_json, payload)
        time.sleep(max(0.0, args.interval_s))

    payload.update({"status": "published" if successes else "blocked"})
    write_json(summary_json, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if successes else 2


if __name__ == "__main__":
    raise SystemExit(main())
