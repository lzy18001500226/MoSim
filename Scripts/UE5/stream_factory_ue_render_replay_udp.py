#!/usr/bin/env python3
"""Stream mosim.ue_render_frame.v1 replay JSONL to UE UDP ports.

The default port mapping is one vehicle per port: uav1->5005, uav2->5006,
uav3->5007. This is a display-only sidecar; it must never feed data back into
Gazebo, PX4, MAVROS, planners, FAST-LIO, or px4ctrl.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
FRAME_SCHEMA = "mosim.ue_render_frame.v1"
DEFAULT_REPLAY = (
    ROOT
    / "Results"
    / "unreal_scene_mapping"
    / "factory_l2_ue_render_mirror_20260702_045816"
    / "ue_render_frame.jsonl"
)


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def load_frames(path: Path) -> list[dict[str, Any]]:
    frames: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if payload.get("schema") != FRAME_SCHEMA:
                raise ValueError(f"unsupported frame schema at {rel(path)}:{line_number}")
            if "vehicle_id" not in payload or "timestamp_ros_s" not in payload:
                raise ValueError(f"frame missing vehicle_id/timestamp at {rel(path)}:{line_number}")
            frames.append(payload)
    if not frames:
        raise ValueError(f"no replay frames: {rel(path)}")
    frames.sort(key=lambda frame: (float(frame["timestamp_ros_s"]), str(frame["vehicle_id"])))
    return frames


def parse_port_map(value: str, vehicles: list[str], base_port: int) -> dict[str, int]:
    if not value:
        return {vehicle: base_port + index for index, vehicle in enumerate(vehicles)}
    mapping: dict[str, int] = {}
    for item in value.split(","):
        if not item.strip():
            continue
        vehicle, port = item.split(":", 1)
        mapping[vehicle.strip()] = int(port.strip())
    missing = [vehicle for vehicle in vehicles if vehicle not in mapping]
    if missing:
        raise ValueError(f"--port-map missing vehicles: {missing}")
    return mapping


def send_frames(args: argparse.Namespace) -> dict[str, Any]:
    replay = repo_path(args.replay_jsonl)
    frames = load_frames(replay)
    vehicles = sorted({str(frame["vehicle_id"]) for frame in frames})
    if args.vehicles:
        requested = [item.strip() for item in args.vehicles.split(",") if item.strip()]
        frames = [frame for frame in frames if str(frame["vehicle_id"]) in requested]
        vehicles = requested
    port_map = parse_port_map(args.port_map, vehicles, args.base_port)
    if args.max_frames_per_vehicle > 0:
        counts: dict[str, int] = {vehicle: 0 for vehicle in vehicles}
        selected: list[dict[str, Any]] = []
        for frame in frames:
            vehicle = str(frame["vehicle_id"])
            if counts.get(vehicle, 0) >= args.max_frames_per_vehicle:
                continue
            selected.append(frame)
            counts[vehicle] = counts.get(vehicle, 0) + 1
        frames = selected

    frames.sort(key=lambda frame: (float(frame["timestamp_ros_s"]), str(frame["vehicle_id"])))
    sent_counts = {vehicle: 0 for vehicle in vehicles}
    sockets: dict[str, socket.socket] = {}
    loop_count = 0
    try:
        if not args.dry_run:
            for vehicle in vehicles:
                sockets[vehicle] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sockets[vehicle].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        start_wall = time.monotonic()
        while True:
            previous_t = float(frames[0]["timestamp_ros_s"])
            for index, frame in enumerate(frames):
                vehicle = str(frame["vehicle_id"])
                timestamp = float(frame["timestamp_ros_s"])
                if (index > 0 or loop_count > 0) and not args.no_sleep and not args.dry_run:
                    dt = max(0.0, timestamp - previous_t) / max(args.replay_speed, 1.0e-6)
                    if args.fps > 0:
                        dt = 1.0 / args.fps
                    time.sleep(dt)
                previous_t = timestamp
                if args.dry_run:
                    if index < args.print_limit:
                        print(json.dumps(frame, ensure_ascii=False, indent=2))
                else:
                    data = json.dumps(frame, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                    sockets[vehicle].sendto(data, (args.host, port_map[vehicle]))
                sent_counts[vehicle] = sent_counts.get(vehicle, 0) + 1
            loop_count += 1
            if not args.loop:
                break
            if args.max_loops > 0 and loop_count >= args.max_loops:
                break
            if args.loop_delay_s > 0 and not args.no_sleep and not args.dry_run:
                time.sleep(args.loop_delay_s)
        elapsed = time.monotonic() - start_wall
    finally:
        for sock in sockets.values():
            sock.close()

    return {
        "schema": "mosim.factory_l2_ue_render_udp_stream.v1",
        "status": "dry_run_passed" if args.dry_run else "sent",
        "replay_jsonl": rel(replay),
        "host": args.host,
        "port_map": port_map,
        "vehicle_count": len(vehicles),
        "frame_count": len(frames),
        "sent_counts": sent_counts,
        "loop": args.loop,
        "loop_count": loop_count,
        "dry_run": args.dry_run,
        "ue_editor_opened": False,
        "feedback_to_runtime": False,
        "elapsed_wall_s": elapsed,
        "claim_boundary": "one-way display UDP stream only; no UE runtime acknowledgement unless paired with UE screenshot/log evidence",
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay-jsonl", default=str(DEFAULT_REPLAY))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--base-port", type=int, default=5005)
    parser.add_argument("--port-map", default="")
    parser.add_argument("--vehicles", default="")
    parser.add_argument("--max-frames-per-vehicle", type=int, default=0)
    parser.add_argument("--fps", type=float, default=0.0)
    parser.add_argument("--replay-speed", type=float, default=1.0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-sleep", action="store_true")
    parser.add_argument("--print-limit", type=int, default=3)
    parser.add_argument("--loop", action="store_true", help="Repeat the replay until interrupted or --max-loops is reached")
    parser.add_argument("--max-loops", type=int, default=0, help="Maximum replay loops; 0 means unlimited when --loop is set")
    parser.add_argument("--loop-delay-s", type=float, default=0.5, help="Delay between replay loops")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        summary = send_frames(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
