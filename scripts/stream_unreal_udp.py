#!/usr/bin/env python3
"""Stream MWORKS raw CSV frames to an external Unreal renderer over UDP.

The stream is display-only. It must not be used as simulation evidence or fed
back into the controller/planner.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import socket
import sys
import time
from pathlib import Path
from typing import Any


REQUIRED_COLUMNS = ("time", "x", "y", "z")
REFERENCE_COLUMNS = ("x_ref", "y_ref", "z_ref")
RPY_COLUMNS = ("roll", "pitch", "yaw")
MOTOR_COLUMNS = ("u1", "u2", "u3", "u4")
SCHEMA_VERSION = "quadrotor.unreal_state.v1"


def finite(value: float | None, fallback: float = 0.0) -> float:
    if value is None or math.isnan(value) or math.isinf(value):
        return fallback
    return value


def parse_float(value: str | None) -> float:
    if value is None or value == "":
        return math.nan
    return float(value)


def read_rows(path: Path) -> tuple[list[str], list[dict[str, float]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        missing = [name for name in REQUIRED_COLUMNS if name not in reader.fieldnames]
        if missing:
            raise ValueError(f"Missing required columns in {path}: {', '.join(missing)}")

        rows: list[dict[str, float]] = []
        for row in reader:
            parsed: dict[str, float] = {}
            for name in reader.fieldnames:
                parsed[name] = parse_float(row.get(name))
            rows.append(parsed)
    if not rows:
        raise ValueError(f"CSV has no data rows: {path}")
    return list(reader.fieldnames), rows


def select_rows(
    rows: list[dict[str, float]],
    *,
    start_time: float | None,
    end_time: float | None,
    stride: int,
    max_frames: int | None,
) -> list[dict[str, float]]:
    selected = []
    for row in rows:
        t = finite(row.get("time"))
        if start_time is not None and t < start_time:
            continue
        if end_time is not None and t > end_time:
            continue
        selected.append(row)

    selected = selected[:: max(1, stride)]
    if max_frames is not None:
        selected = selected[:max_frames]
    if not selected:
        raise ValueError("No rows selected; check --start-time/--end-time/--stride")
    return selected


def make_frame(
    row: dict[str, float],
    *,
    sequence: int,
    scene_id: str,
    near_radius_m: float,
    far_radius_m: float,
    fov_deg: float,
) -> dict[str, Any]:
    position = [finite(row.get("x")), finite(row.get("y")), finite(row.get("z"))]
    rpy = [finite(row.get(name)) for name in RPY_COLUMNS]
    reference = [finite(row.get(name), math.nan) for name in REFERENCE_COLUMNS]
    motor = [finite(row.get(name), math.nan) for name in MOTOR_COLUMNS]
    yaw = rpy[2]
    return {
        "schema": SCHEMA_VERSION,
        "type": "frame",
        "scene_id": scene_id,
        "seq": sequence,
        "t": finite(row.get("time")),
        "units": {"position": "m", "angle": "rad", "time": "s"},
        "uav": {
            "id": "uav_1",
            "position_m": position,
            "rpy_rad": rpy,
            "motor_command": motor,
        },
        "reference": {
            "position_m": reference,
        },
        "perception": {
            "radar_origin_m": position,
            "yaw_rad": yaw,
            "near_radius_m": near_radius_m,
            "far_radius_m": far_radius_m,
            "fov_deg": fov_deg,
        },
        "local_plan": {
            "points_m": [position, reference] if all(math.isfinite(v) for v in reference) else [position],
        },
    }


def dumps_packet(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def send_packet(sock: socket.socket, address: tuple[str, int], payload: dict[str, Any], dry_run: bool) -> None:
    data = dumps_packet(payload)
    if len(data) > 60_000:
        raise ValueError(f"UDP packet too large: {len(data)} bytes")
    if dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        sock.sendto(data, address)


def stream_rows(args: argparse.Namespace) -> int:
    fieldnames, rows = read_rows(args.raw_csv)
    rows = select_rows(
        rows,
        start_time=args.start_time,
        end_time=args.end_time,
        stride=args.stride,
        max_frames=args.max_frames,
    )
    scene_id = args.scene_id or args.raw_csv.stem
    address = (args.host, args.port)
    interval_override = 1.0 / args.fps if args.fps and args.fps > 0 else None

    hello = {
        "schema": SCHEMA_VERSION,
        "type": "hello",
        "scene_id": scene_id,
        "source": str(args.raw_csv),
        "fieldnames": fieldnames,
        "frame_count": len(rows),
        "units": {"position": "m", "angle": "rad", "time": "s"},
        "coordinate_policy": "MWORKS meters/radians; Unreal receiver converts to centimeters if needed",
        "render_only": True,
    }
    goodbye = {
        "schema": SCHEMA_VERSION,
        "type": "end",
        "scene_id": scene_id,
        "frame_count": len(rows),
        "render_only": True,
    }

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        loops = 0
        while True:
            send_packet(sock, address, hello, args.dry_run)
            previous_t = finite(rows[0].get("time"))
            start_wall = time.monotonic()
            for seq, row in enumerate(rows):
                frame = make_frame(
                    row,
                    sequence=seq,
                    scene_id=scene_id,
                    near_radius_m=args.near_radius_m,
                    far_radius_m=args.far_radius_m,
                    fov_deg=args.fov_deg,
                )
                if seq > 0 and not args.no_sleep and not args.dry_run:
                    current_t = finite(row.get("time"), previous_t)
                    dt = interval_override if interval_override is not None else max(0.0, current_t - previous_t)
                    time.sleep(max(0.0, dt / args.replay_speed))
                    previous_t = current_t
                send_packet(sock, address, frame, args.dry_run)
                if args.print_every and seq % args.print_every == 0:
                    elapsed = time.monotonic() - start_wall
                    print(f"sent seq={seq} t={frame['t']:.3f}s elapsed={elapsed:.2f}s", file=sys.stderr)
            send_packet(sock, address, goodbye, args.dry_run)
            loops += 1
            if not args.loop or (args.loop_count and loops >= args.loop_count):
                break
    finally:
        sock.close()
    print(f"Streamed {len(rows)} frames to udp://{args.host}:{args.port} scene={scene_id}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_csv", type=Path, help="Standard MWORKS raw CSV")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5005)
    parser.add_argument("--scene-id", default=None)
    parser.add_argument("--start-time", type=float, default=None)
    parser.add_argument("--end-time", type=float, default=None)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--max-frames", type=int, default=None)
    parser.add_argument("--fps", type=float, default=None, help="Override CSV time spacing with a fixed send FPS")
    parser.add_argument("--replay-speed", type=float, default=1.0, help="1.0 real time, 2.0 twice as fast")
    parser.add_argument("--near-radius-m", type=float, default=6.0)
    parser.add_argument("--far-radius-m", type=float, default=9.0)
    parser.add_argument("--fov-deg", type=float, default=120.0)
    parser.add_argument("--loop", action="store_true")
    parser.add_argument("--loop-count", type=int, default=0)
    parser.add_argument("--no-sleep", action="store_true", help="Send as fast as possible")
    parser.add_argument("--dry-run", action="store_true", help="Print packets instead of sending UDP")
    parser.add_argument("--print-every", type=int, default=0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.replay_speed <= 0:
        raise ValueError("--replay-speed must be positive")
    if args.port <= 0 or args.port > 65535:
        raise ValueError("--port must be in 1..65535")
    return stream_rows(args)


if __name__ == "__main__":
    raise SystemExit(main())
