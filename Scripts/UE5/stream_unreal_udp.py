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


def load_local_known_map_frames(path: Path | None) -> dict[int, dict[str, Any]]:
    if path is None:
        return {}
    frames: dict[int, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if payload.get("schema") != "mosim.local_known_map_frame.v1":
                raise ValueError(f"unsupported local known map schema at {path}:{line_number}")
            seq = int(payload.get("seq", len(frames)))
            frames[seq] = payload
    return frames


def load_lidar_point_frames(path: Path | None) -> dict[int, dict[str, Any]]:
    if path is None:
        return {}
    frames: dict[int, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if payload.get("schema") != "mosim.lidar_point_frame.v1":
                raise ValueError(f"unsupported lidar point frame schema at {path}:{line_number}")
            seq = int(payload.get("seq", len(frames)))
            frames[seq] = payload
    return frames


def load_local_plan_frames(path: Path | None) -> dict[int, dict[str, Any]]:
    if path is None:
        return {}
    frames: dict[int, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if payload.get("schema") != "mosim.local_plan_frame.v1":
                raise ValueError(f"unsupported local plan frame schema at {path}:{line_number}")
            seq = int(payload.get("seq", len(frames)))
            frames[seq] = payload
    return frames


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


def resample_rows(rows: list[dict[str, float]], output_hz: float | None) -> list[dict[str, float]]:
    if output_hz is None or output_hz <= 0 or len(rows) < 2:
        return rows

    start_time = finite(rows[0].get("time"))
    end_time = finite(rows[-1].get("time"), start_time)
    if end_time <= start_time:
        return rows

    step = 1.0 / output_hz
    resampled: list[dict[str, float]] = []
    source_index = 0
    t = start_time
    while t < end_time:
        while source_index + 1 < len(rows) and finite(rows[source_index + 1].get("time"), t) < t:
            source_index += 1
        left = rows[source_index]
        right = rows[min(source_index + 1, len(rows) - 1)]
        left_t = finite(left.get("time"), t)
        right_t = finite(right.get("time"), left_t)
        alpha = 0.0 if right_t <= left_t else max(0.0, min(1.0, (t - left_t) / (right_t - left_t)))
        row: dict[str, float] = {}
        for name, left_value in left.items():
            right_value = right.get(name, left_value)
            if name == "time":
                row[name] = t
            elif math.isfinite(left_value) and math.isfinite(right_value):
                row[name] = left_value + alpha * (right_value - left_value)
            else:
                row[name] = left_value if alpha < 0.5 else right_value
        resampled.append(row)
        t += step
    resampled.append(dict(rows[-1]))
    return resampled


def make_frame(
    row: dict[str, float],
    *,
    sequence: int,
    rows: list[dict[str, float]],
    scene_id: str,
    map_id: str,
    near_radius_m: float,
    far_radius_m: float,
    fov_deg: float,
    local_map_grid_m: float,
    local_map_radius_m: float,
    local_map_cells: int,
    local_known_map_frame: dict[str, Any] | None,
    local_plan_frame: dict[str, Any] | None,
    lidar_point_frame: dict[str, Any] | None,
    lidar_point_limit: int,
    local_plan_source: str,
    coordinate_policy: str,
    visual_helpers_enabled: bool,
) -> dict[str, Any]:
    position = [finite(row.get("x")), finite(row.get("y")), finite(row.get("z"))]
    rpy = [finite(row.get(name)) for name in RPY_COLUMNS]
    reference = [finite(row.get(name), math.nan) for name in REFERENCE_COLUMNS]
    motor = [finite(row.get(name), math.nan) for name in MOTOR_COLUMNS]
    yaw = rpy[2]
    local_plan = [position]
    if all(math.isfinite(v) for v in reference):
        for i in range(1, 9):
            alpha = i / 8.0
            # Render-side preview only. True planning evidence stays in MWORKS raw/native outputs.
            bend = math.sin(alpha * math.pi) * 0.18
            dx = reference[0] - position[0]
            dy = reference[1] - position[1]
            length = math.hypot(dx, dy)
            nx = -dy / length if length > 1e-9 else 0.0
            ny = dx / length if length > 1e-9 else 0.0
            local_plan.append([
                position[0] + alpha * dx + bend * nx,
                position[1] + alpha * dy + bend * ny,
                position[2] + alpha * (reference[2] - position[2]),
            ])
    if not visual_helpers_enabled:
        local_plan = []
    if local_plan_frame:
        local_plan = list(local_plan_frame.get("points_m", local_plan))
        local_plan_source = str(local_plan_frame.get("source", local_plan_source))
        local_plan_render_only = bool(local_plan_frame.get("render_only", False))
        local_plan_evidence_backed = bool(local_plan_frame.get("evidence_backed", True))
        local_plan_valid = bool(local_plan_frame.get("valid", True))
    else:
        local_plan_render_only = local_plan_source == "preview_from_reference"
        local_plan_evidence_backed = local_plan_source != "preview_from_reference"
        local_plan_valid = local_plan_source != "preview_from_reference"
    if local_known_map_frame:
        local_known_map = {
            "schema": "quadrotor.local_known_map.v1",
            "origin_m": local_known_map_frame.get("origin_m", position),
            "grid_m": float(local_known_map_frame.get("grid_m", local_map_grid_m)),
            "radius_m": float(local_known_map_frame.get("radius_m", local_map_radius_m)),
            "cells": [] if not visual_helpers_enabled else list(local_known_map_frame.get("cells", []))[: max(local_map_cells, 0)] if local_map_cells > 0 else list(local_known_map_frame.get("cells", [])),
            "render_only": bool(local_known_map_frame.get("render_only", False)),
            "evidence_backed": bool(local_known_map_frame.get("evidence_backed", True)),
        }
        local_known_map_flag = "evidence_backed_local_known_map"
        planner_state = "unknown_map_local_lidar_replay"
        evidence_level = "scene_truth_pipeline_replay"
        status_notes = "local_known_map is generated from scene-truth-derived local LiDAR frames; planner still did not receive global truth"
    else:
        local_known_map = {
            "schema": "quadrotor.local_known_map.v1",
            "origin_m": position,
            "grid_m": local_map_grid_m,
            "radius_m": local_map_radius_m,
            "cells": [] if not visual_helpers_enabled else [
                {
                    "offset": [0, 0, 0],
                    "state": "observed_free",
                    "source": "render_contract_smoke",
                }
            ][: max(local_map_cells, 0)],
            "render_only": True,
            "evidence_backed": False,
        }
        local_known_map_flag = "render_only_local_known_map"
        planner_state = "render_contract_smoke"
        evidence_level = "render_only_preview"
        status_notes = "local_known_map and preview local_plan are display contracts unless evidence_backed=true"
    if lidar_point_frame:
        lidar_points = {
            "schema": "quadrotor.lidar_points.v1",
            "coordinate_frame": lidar_point_frame.get("coordinate_frame", coordinate_policy),
            "points_m": [] if not visual_helpers_enabled else list(lidar_point_frame.get("points_m", []))[: max(lidar_point_limit, 0)] if lidar_point_limit > 0 else list(lidar_point_frame.get("points_m", [])),
            "render_only": bool(lidar_point_frame.get("render_only", False)),
            "evidence_backed": bool(lidar_point_frame.get("evidence_backed", True)),
            "source": lidar_point_frame.get("source", "scene_truth_pipeline_lidar_replay"),
        }
        lidar_flag = "evidence_backed_lidar_points"
    else:
        lidar_points = {
            "schema": "quadrotor.lidar_points.v1",
            "coordinate_frame": coordinate_policy,
            "points_m": [],
            "render_only": True,
            "evidence_backed": False,
            "source": "no_lidar_points",
        }
        lidar_flag = "no_lidar_points"
    return {
        "schema": SCHEMA_VERSION,
        "type": "frame",
        "scene_id": scene_id,
        "map_id": map_id,
        "seq": sequence,
        "t": finite(row.get("time")),
        "units": {"position": "m", "angle": "rad", "time": "s"},
        "coordinate_policy": coordinate_policy,
        "uav": {
            "id": "uav_1",
            "position_m": position,
            "rpy_rad": rpy,
            "motor_command": motor,
        },
        "reference": {
            "position_m": reference,
        },
        "mission": {
            "start_m": [
                finite(rows[0].get("x")),
                finite(rows[0].get("y")),
                finite(rows[0].get("z")),
            ],
            "goal_m": [
                finite(rows[-1].get("x_ref"), finite(rows[-1].get("x"))),
                finite(rows[-1].get("y_ref"), finite(rows[-1].get("y"))),
                finite(rows[-1].get("z_ref"), finite(rows[-1].get("z"))),
            ],
            "current_goal_m": reference,
        },
        "perception": {
            "radar_origin_m": position,
            "yaw_rad": yaw,
            "near_radius_m": near_radius_m if visual_helpers_enabled else 0.0,
            "far_radius_m": far_radius_m if visual_helpers_enabled else 0.0,
            "fov_deg": fov_deg if visual_helpers_enabled else 0.0,
        },
        "local_known_map": local_known_map,
        "lidar_points": lidar_points,
        "local_plan": {
            "points_m": local_plan,
            "source": local_plan_source,
            "render_only": local_plan_render_only,
            "evidence_backed": local_plan_evidence_backed,
            "valid": local_plan_valid,
        },
        "status": {
            "controller_mode": "unknown",
            "planner_state": planner_state,
            "safety_state": "unknown",
            "evidence_level": evidence_level,
            "notes": status_notes,
        },
        "overlays": {
            "scene_label": scene_id,
            "map_label": map_id,
            "quality_flags": [
                "render_only_local_plan" if local_plan_source == "preview_from_reference" else "evidence_backed_local_plan",
                local_known_map_flag,
                lidar_flag,
            ],
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
    local_known_map_frames = load_local_known_map_frames(args.local_known_map_jsonl)
    local_plan_frames = load_local_plan_frames(args.local_plan_jsonl)
    lidar_point_frames = load_lidar_point_frames(args.lidar_point_frames_jsonl)
    rows = select_rows(
        rows,
        start_time=args.start_time,
        end_time=args.end_time,
        stride=args.stride,
        max_frames=args.max_frames,
    )
    rows = resample_rows(rows, args.resample_hz)
    scene_id = args.scene_id or args.raw_csv.stem
    address = (args.host, args.port)
    interval_override = 1.0 / args.fps if args.fps and args.fps > 0 else None

    hello = {
        "schema": SCHEMA_VERSION,
        "type": "hello",
        "scene_id": scene_id,
        "map_id": args.map_id,
        "source": str(args.raw_csv),
        "fieldnames": fieldnames,
        "frame_count": len(rows),
        "units": {"position": "m", "angle": "rad", "time": "s"},
        "coordinate_policy": "MWORKS meters/radians; Unreal receiver converts to centimeters if needed",
        "frame_coordinate_policy": args.coordinate_policy,
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
                    rows=rows,
                    scene_id=scene_id,
                    map_id=args.map_id,
                    near_radius_m=args.near_radius_m,
                    far_radius_m=args.far_radius_m,
                    fov_deg=args.fov_deg,
                    local_map_grid_m=args.local_map_grid_m,
                    local_map_radius_m=args.local_map_radius_m,
                    local_map_cells=args.local_map_cells,
                    local_known_map_frame=local_known_map_frames.get(seq),
                    local_plan_frame=local_plan_frames.get(seq),
                    lidar_point_frame=lidar_point_frames.get(seq),
                    lidar_point_limit=args.lidar_point_limit,
                    local_plan_source=args.local_plan_source,
                    coordinate_policy=args.coordinate_policy,
                    visual_helpers_enabled=not args.disable_visual_helpers,
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
    parser.add_argument("--map-id", default="map_open_blocks")
    parser.add_argument("--start-time", type=float, default=None)
    parser.add_argument("--end-time", type=float, default=None)
    parser.add_argument("--stride", type=int, default=1)
    parser.add_argument("--max-frames", type=int, default=None)
    parser.add_argument("--fps", type=float, default=None, help="Override CSV time spacing with a fixed send FPS")
    parser.add_argument("--resample-hz", type=float, default=None, help="Linearly resample CSV state rows before streaming; use 60 Hz for render-frame playback and keep controller evidence separate.")
    parser.add_argument("--replay-speed", type=float, default=1.0, help="1.0 real time, 2.0 twice as fast")
    parser.add_argument("--near-radius-m", type=float, default=6.0)
    parser.add_argument("--far-radius-m", type=float, default=9.0)
    parser.add_argument("--fov-deg", type=float, default=120.0)
    parser.add_argument("--local-map-grid-m", type=float, default=0.6)
    parser.add_argument("--local-map-radius-m", type=float, default=6.0)
    parser.add_argument("--local-map-cells", type=int, default=320, help="Maximum local map cells per UDP frame; 0 sends all cells")
    parser.add_argument("--local-known-map-jsonl", type=Path, default=None, help="Evidence-backed local-known-map frames generated by scene_truth_pipeline.py")
    parser.add_argument("--local-plan-jsonl", type=Path, default=None, help="Evidence-backed local-plan frames generated by scene_truth_pipeline.py")
    parser.add_argument("--lidar-point-frames-jsonl", type=Path, default=None, help="Evidence-backed per-frame LiDAR point replay generated by scene_truth_pipeline.py")
    parser.add_argument("--lidar-point-limit", type=int, default=220, help="Maximum LiDAR points per UDP frame; 0 sends all points")
    parser.add_argument("--local-plan-source", default="preview_from_reference")
    parser.add_argument("--disable-visual-helpers", action="store_true", help="Send only UAV pose/reference data; hide render-only radar/map/lidar/local-plan helpers.")
    parser.add_argument(
        "--coordinate-policy",
        choices=("mworks_world_m_z_up", "ue_world_m_z_up"),
        default="mworks_world_m_z_up",
        help="Coordinate convention for position/local-plan vectors in this stream.",
    )
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
    if args.local_map_grid_m <= 0:
        raise ValueError("--local-map-grid-m must be positive")
    if args.local_map_radius_m <= 0:
        raise ValueError("--local-map-radius-m must be positive")
    return stream_rows(args)


if __name__ == "__main__":
    raise SystemExit(main())
