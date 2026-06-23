#!/usr/bin/env python3
"""Step through Gazebo camera direction candidates for Sunray150 review."""

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


def activate_follow_target(command: str, target: str, timeout_s: float) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            [
                command,
                "service",
                "-s",
                "/gui/follow",
                "--reqtype",
                "ignition.msgs.StringMsg",
                "--reptype",
                "ignition.msgs.Boolean",
                "--timeout",
                str(int(max(0.1, timeout_s) * 1000)),
                "--req",
                f'data: "{target}"',
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
        stderr = exc.stderr or "/gui/follow request timeout"
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return 124, stdout, stderr


def candidate_offsets(back_m: float, left_m: float, up_m: float) -> list[dict[str, Any]]:
    return [
        {
            "id": "A",
            "offset_m": [-back_m, -left_m, up_m],
            "hypothesis": "current runner default: model -X rear, model -Y visual-left candidate",
        },
        {
            "id": "B",
            "offset_m": [-back_m, left_m, up_m],
            "hypothesis": "model -X rear, model +Y visual-left candidate",
        },
        {
            "id": "C",
            "offset_m": [-left_m, -back_m, up_m],
            "hypothesis": "model -Y rear, model -X visual-left candidate",
        },
        {
            "id": "D",
            "offset_m": [left_m, -back_m, up_m],
            "hypothesis": "model -Y rear, model +X visual-left candidate",
        },
        {
            "id": "E",
            "offset_m": [back_m, -left_m, up_m],
            "hypothesis": "model +X rear, model -Y visual-left candidate",
        },
        {
            "id": "F",
            "offset_m": [back_m, left_m, up_m],
            "hypothesis": "model +X rear, model +Y visual-left candidate",
        },
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--command", default="ign")
    parser.add_argument("--target", default="sunray150_assembled")
    parser.add_argument("--offset-service", default="/gui/follow/offset")
    parser.add_argument("--back-m", type=float, default=1.4)
    parser.add_argument("--left-m", type=float, default=0.35)
    parser.add_argument("--up-m", type=float, default=0.7)
    parser.add_argument("--hold-s", type=float, default=8.0)
    parser.add_argument("--timeout-s", type=float, default=1.0)
    parser.add_argument("--summary-json", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary_json = project_path(args.summary_json)
    summary_json.parent.mkdir(parents=True, exist_ok=True)

    follow_rc, follow_stdout, follow_stderr = activate_follow_target(args.command, args.target, args.timeout_s)
    rows: list[dict[str, Any]] = []
    for candidate in candidate_offsets(args.back_m, args.left_m, args.up_m):
        offset = tuple(float(value) for value in candidate["offset_m"])
        rc, stdout, stderr = request_vector3d_service(args.command, args.offset_service, offset, args.timeout_s)
        rows.append(
            {
                **candidate,
                "rc": rc,
                "stdout_tail": stdout[-300:],
                "stderr_tail": stderr[-300:],
                "review_instruction": f"Candidate {candidate['id']}: tell Codex if this is the actual rear-left-up view.",
            }
        )
        print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
        time.sleep(max(0.0, args.hold_s))

    status = "completed" if any(row["rc"] == 0 for row in rows) else "blocked"
    payload = {
        "schema": "mosim.gazebo_camera_direction_calibration.v1",
        "status": status,
        "target": args.target,
        "follow_rc": follow_rc,
        "follow_stdout_tail": follow_stdout[-300:],
        "follow_stderr_tail": follow_stderr[-300:],
        "offset_service": args.offset_service,
        "candidates": rows,
        "expected_user_response": "A/B/C/D/E/F, whichever visually matches rear-left-up around the accepted Sunray150 mesh.",
        "claim_boundary": "Camera direction calibration only; no model, controller, trajectory, actuator, or ROS2 topics are modified.",
    }
    summary_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if status == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
