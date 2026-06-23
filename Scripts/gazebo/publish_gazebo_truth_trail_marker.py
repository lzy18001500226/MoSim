#!/usr/bin/env python3
"""Publish a continuous Gazebo GUI trail marker from the vehicle truth pose.

This is visual-review support only. It samples the Gazebo transport truth pose
topic, keeps the visited XY/Z points, and republishes the actual flown trail as
a Gazebo GUI LINE_STRIP marker. It does not publish control commands.
"""

from __future__ import annotations

import argparse
import json
import math
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
for helper_dir in (ROOT / "Scripts" / "gazebo", ROOT / "Scripts" / "ros"):
    if str(helper_dir) not in sys.path:
        sys.path.insert(0, str(helper_dir))

from capture_gazebo_pose_truth_topic import parse_samples, run_sample  # noqa: E402
from gazebo_truth_planner_setpoint_tracker import (  # noqa: E402
    iter_stdin_message_chunks,
    parse_truth_samples,
)


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def marker_color_text(r: float, g: float, b: float, a: float) -> str:
    return (
        "material { "
        f"ambient {{ r: {r:.3f} g: {g:.3f} b: {b:.3f} a: {a:.3f} }} "
        f"diffuse {{ r: {r:.3f} g: {g:.3f} b: {b:.3f} a: {a:.3f} }} "
        f"emissive {{ r: {0.55 * r:.3f} g: {0.55 * g:.3f} b: {0.55 * b:.3f} a: {a:.3f} }} "
        "}"
    )


def marker_text(
    *,
    namespace: str,
    marker_id: int,
    marker_type: str,
    points: list[tuple[float, float, float]],
    scale_m: float,
    color: tuple[float, float, float, float],
) -> str:
    point_text = " ".join(f"point {{ x: {x:.4f} y: {y:.4f} z: {z:.4f} }}" for x, y, z in points)
    color_text = marker_color_text(*color)
    return (
        'action: ADD_MODIFY '
        f'ns: "{namespace}" '
        f"id: {marker_id} "
        "layer: 9 "
        f"type: {marker_type} "
        "visibility: GUI "
        f"scale {{ x: {scale_m:.4f} y: {scale_m:.4f} z: {scale_m:.4f} }} "
        f"{color_text} "
        f"{point_text}"
    )


def delete_marker_text(namespace: str, marker_id: int) -> str:
    return f'action: DELETE_MARKER ns: "{namespace}" id: {marker_id}'


def publish_marker(
    command: str,
    topic: str,
    text: str,
    timeout_s: float,
    *,
    transport_mode: str,
) -> tuple[int, str, str]:
    if transport_mode == "topic":
        argv = [
            command,
            "topic",
            "-t",
            topic,
            "-m",
            "ignition.msgs.Marker",
            "-p",
            text,
        ]
    elif transport_mode == "service" and topic.endswith("_array"):
        argv = [
            command,
            "service",
            "-s",
            topic,
            "--reqtype",
            "ignition.msgs.Marker_V",
            "--reptype",
            "ignition.msgs.Boolean",
            "--timeout",
            str(int(max(0.1, timeout_s) * 1000)),
            "--req",
            f"marker {{ {text} }}",
        ]
    else:
        argv = [
            command,
            "service",
            "-s",
            topic,
            "--reqtype",
            "ignition.msgs.Marker",
            "--reptype",
            "ignition.msgs.Boolean",
            "--timeout",
            str(int(max(0.1, timeout_s) * 1000)),
            "--req",
            text,
        ]
    try:
        completed = subprocess.run(
            argv,
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
        stderr = exc.stderr or "marker publish timeout"
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return 124, stdout, stderr


def publish_marker_array(
    command: str,
    topic: str,
    markers: list[str],
    timeout_s: float,
) -> tuple[int, str, str]:
    argv = [
        command,
        "service",
        "-s",
        topic,
        "--reqtype",
        "ignition.msgs.Marker_V",
        "--reptype",
        "ignition.msgs.Boolean",
        "--timeout",
        str(int(max(0.1, timeout_s) * 1000)),
        "--req",
        " ".join(f"marker {{ {marker} }}" for marker in markers),
    ]
    try:
        completed = subprocess.run(
            argv,
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
        stderr = exc.stderr or "marker array publish timeout"
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return 124, stdout, stderr


def entity_factory_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def segment_pose_rpy(
    start_point: tuple[float, float, float],
    end_point: tuple[float, float, float],
) -> tuple[float, float, float, float, float, float, float]:
    x1, y1, z1 = start_point
    x2, y2, z2 = end_point
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 1e-9:
        return x1, y1, z1, 0.0, 0.0, 0.0, 0.0
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(math.hypot(dx, dy), dz)
    return (0.5 * (x1 + x2), 0.5 * (y1 + y2), 0.5 * (z1 + z2), 0.0, pitch, yaw, length)


def trail_segment_sdf(
    *,
    name: str,
    start_point: tuple[float, float, float],
    end_point: tuple[float, float, float],
    radius_m: float,
    color: tuple[float, float, float, float],
) -> tuple[str, float]:
    x, y, z, roll, pitch, yaw, length = segment_pose_rpy(start_point, end_point)
    r, g, b, a = color
    sdf = (
        "<sdf version='1.7'>"
        f"<model name='{name}'>"
        "<static>true</static>"
        f"<pose>{x:.6f} {y:.6f} {z:.6f} {roll:.6f} {pitch:.6f} {yaw:.6f}</pose>"
        "<link name='link'>"
        "<visual name='red_truth_trail_segment'>"
        "<cast_shadows>false</cast_shadows>"
        "<geometry>"
        f"<cylinder><radius>{radius_m:.6f}</radius><length>{length:.6f}</length></cylinder>"
        "</geometry>"
        "<material>"
        f"<ambient>{r:.3f} {g:.3f} {b:.3f} {a:.3f}</ambient>"
        f"<diffuse>{r:.3f} {g:.3f} {b:.3f} {a:.3f}</diffuse>"
        f"<emissive>{r:.3f} {g:.3f} {b:.3f} {a:.3f}</emissive>"
        "</material>"
        "</visual>"
        "</link>"
        "</model>"
        "</sdf>"
    )
    return sdf, length


def trail_segment_visual_xml(
    *,
    visual_name: str,
    start_point: tuple[float, float, float],
    end_point: tuple[float, float, float],
    radius_m: float,
    color: tuple[float, float, float, float],
) -> tuple[str, float]:
    x, y, z, roll, pitch, yaw, length = segment_pose_rpy(start_point, end_point)
    r, g, b, a = color
    return (
        f"<visual name='{visual_name}'>"
        "<cast_shadows>false</cast_shadows>"
        f"<pose>{x:.6f} {y:.6f} {z:.6f} {roll:.6f} {pitch:.6f} {yaw:.6f}</pose>"
        "<geometry>"
        f"<cylinder><radius>{radius_m:.6f}</radius><length>{length:.6f}</length></cylinder>"
        "</geometry>"
        "<material>"
        f"<ambient>{r:.3f} {g:.3f} {b:.3f} {a:.3f}</ambient>"
        f"<diffuse>{r:.3f} {g:.3f} {b:.3f} {a:.3f}</diffuse>"
        f"<emissive>{r:.3f} {g:.3f} {b:.3f} {a:.3f}</emissive>"
        "</material>"
        "</visual>",
        length,
    )


def trail_segment_batch_sdf(
    *,
    name: str,
    segments: list[tuple[tuple[float, float, float], tuple[float, float, float]]],
    radius_m: float,
    color: tuple[float, float, float, float],
) -> tuple[str, int]:
    visual_items: list[str] = []
    valid_count = 0
    for index, (start_point, end_point) in enumerate(segments, start=1):
        visual_xml, length = trail_segment_visual_xml(
            visual_name=f"red_truth_trail_segment_{index:03d}",
            start_point=start_point,
            end_point=end_point,
            radius_m=radius_m,
            color=color,
        )
        if length <= 1e-9:
            continue
        valid_count += 1
        visual_items.append(visual_xml)
    sdf = (
        "<sdf version='1.7'>"
        f"<model name='{name}'>"
        "<static>true</static>"
        "<pose>0 0 0 0 0 0</pose>"
        "<link name='link'>"
        + "".join(visual_items)
        + "</link>"
        "</model>"
        "</sdf>"
    )
    return sdf, valid_count


def spawn_trail_segment_entity(
    command: str,
    world_name: str,
    name: str,
    start_point: tuple[float, float, float],
    end_point: tuple[float, float, float],
    radius_m: float,
    timeout_s: float,
) -> tuple[int, str, str, float]:
    sdf, length = trail_segment_sdf(
        name=name,
        start_point=start_point,
        end_point=end_point,
        radius_m=radius_m,
        color=(1.0, 0.0, 0.0, 1.0),
    )
    request = f'sdf: "{entity_factory_escape(sdf)}" name: "{name}" allow_renaming: false'
    try:
        completed = subprocess.run(
            [
                command,
                "service",
                "-s",
                f"/world/{world_name}/create",
                "--reqtype",
                "ignition.msgs.EntityFactory",
                "--reptype",
                "ignition.msgs.Boolean",
                "--timeout",
                str(int(max(0.1, timeout_s) * 1000)),
                "--req",
                request,
            ],
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=max(0.1, timeout_s),
        )
        return int(completed.returncode), completed.stdout, completed.stderr, length
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or "entity trail segment spawn timeout"
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return 124, stdout, stderr, length


def spawn_trail_segment_batch_entity(
    command: str,
    world_name: str,
    name: str,
    segments: list[tuple[tuple[float, float, float], tuple[float, float, float]]],
    radius_m: float,
    timeout_s: float,
) -> tuple[int, str, str, int]:
    sdf, valid_count = trail_segment_batch_sdf(
        name=name,
        segments=segments,
        radius_m=radius_m,
        color=(1.0, 0.0, 0.0, 1.0),
    )
    if valid_count <= 0:
        return 0, "data: true\n\n", "", 0
    request = f'sdf: "{entity_factory_escape(sdf)}" name: "{name}" allow_renaming: false'
    try:
        completed = subprocess.run(
            [
                command,
                "service",
                "-s",
                f"/world/{world_name}/create",
                "--reqtype",
                "ignition.msgs.EntityFactory",
                "--reptype",
                "ignition.msgs.Boolean",
                "--timeout",
                str(int(max(0.1, timeout_s) * 1000)),
                "--req",
                request,
            ],
            check=False,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=max(0.1, timeout_s),
        )
        return int(completed.returncode), completed.stdout, completed.stderr, valid_count
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or "entity trail segment batch spawn timeout"
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        return 124, stdout, stderr, valid_count


def start_truth_stream(command: str, topic: str) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [command, "topic", "-e", "-t", topic],
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def start_stream_reader(
    proc: subprocess.Popen[str],
    *,
    model_name: str,
    topic: str,
    frame_id: str,
) -> tuple[queue.Queue[list[dict[str, Any]]], queue.Queue[str], threading.Thread, threading.Thread]:
    sample_queue: queue.Queue[list[dict[str, Any]]] = queue.Queue()
    stderr_queue: queue.Queue[str] = queue.Queue()

    def read_stdout() -> None:
        if proc.stdout is None:
            return
        try:
            for chunk in iter_stdin_message_chunks(proc.stdout):
                samples = parse_truth_samples(chunk, model_name=model_name, topic=topic, frame_id=frame_id)
                if samples:
                    sample_queue.put(samples)
        except Exception as exc:
            stderr_queue.put(f"stream stdout reader error: {exc.__class__.__name__}: {exc}")

    def read_stderr() -> None:
        if proc.stderr is None:
            return
        try:
            tail = ""
            for line in proc.stderr:
                tail = (tail + line)[-1000:]
                stderr_queue.put(tail)
        except Exception as exc:
            stderr_queue.put(f"stream stderr reader error: {exc.__class__.__name__}: {exc}")

    stdout_thread = threading.Thread(target=read_stdout, daemon=True)
    stderr_thread = threading.Thread(target=read_stderr, daemon=True)
    stdout_thread.start()
    stderr_thread.start()
    return sample_queue, stderr_queue, stdout_thread, stderr_thread


def should_add_point(
    points: list[tuple[float, float, float]],
    position: tuple[float, float, float],
    min_distance_m: float,
) -> bool:
    if not points:
        return True
    lx, ly, lz = points[-1]
    x, y, z = position
    return math.dist((lx, ly, lz), (x, y, z)) >= min_distance_m


def in_center_revisit_band(position: tuple[float, float, float], center_x: float, center_y: float, radius_m: float) -> bool:
    return math.hypot(position[0] - center_x, position[1] - center_y) <= radius_m


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--truth-topic", required=True)
    parser.add_argument("--model-name", default="sunray150_assembled")
    parser.add_argument("--frame-id", default="world")
    parser.add_argument("--marker-topic", default="/marker_array")
    parser.add_argument("--command", default="ign")
    parser.add_argument("--transport-mode", choices=["topic", "service"], default="service")
    parser.add_argument("--capture-mode", choices=["stream", "sample"], default="stream")
    parser.add_argument("--duration-s", type=float, default=60.0)
    parser.add_argument("--sample-rate-hz", type=float, default=24.0)
    parser.add_argument("--publish-rate-hz", type=float, default=1.0)
    parser.add_argument("--sample-timeout-s", type=float, default=1.0)
    parser.add_argument("--publish-timeout-s", type=float, default=4.0)
    parser.add_argument("--min-point-distance-m", type=float, default=0.004)
    parser.add_argument("--max-points", type=int, default=5000)
    parser.add_argument("--z-offset-m", type=float, default=0.0)
    parser.add_argument("--line-scale-m", type=float, default=0.010)
    parser.add_argument("--entity-trail", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--world-name", default="")
    parser.add_argument("--entity-segment-radius-m", type=float, default=0.018)
    parser.add_argument("--entity-segment-min-distance-m", type=float, default=0.12)
    parser.add_argument("--entity-segments-per-publish", type=int, default=12)
    parser.add_argument("--center-x-m", type=float, default=0.0)
    parser.add_argument("--center-y-m", type=float, default=1.0)
    parser.add_argument("--center-revisit-radius-m", type=float, default=0.10)
    parser.add_argument("--namespace", default="mosim_actual_truth_trail")
    parser.add_argument("--summary-json", required=True, type=Path)
    parser.add_argument("--trace-jsonl", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.duration_s <= 0 or args.sample_rate_hz <= 0 or args.publish_rate_hz <= 0:
        raise SystemExit("duration and rates must be positive")
    if args.max_points < 2:
        raise SystemExit("max-points must be >= 2")

    summary_json = project_path(args.summary_json)
    trace_jsonl = project_path(args.trace_jsonl)
    if trace_jsonl.exists():
        trace_jsonl.unlink()

    points: list[tuple[float, float, float]] = []
    entity_points: list[tuple[float, float, float]] = []
    pending_entity_segments: list[tuple[tuple[float, float, float], tuple[float, float, float]]] = []
    pre_revisit_points: list[tuple[float, float, float]] = []
    revisit_points: list[tuple[float, float, float]] = []
    was_in_center_band = False
    center_band_entry_count = 0
    start = time.monotonic()
    next_sample = start
    next_publish = start
    sample_attempts = 0
    parsed_samples = 0
    marker_publish_attempts = 0
    marker_publish_success = 0
    entity_spawn_attempts = 0
    entity_spawn_success = 0
    entity_spawned_segment_count = 0
    last_marker_rc: int | None = None
    last_marker_stderr = ""
    last_entity_rc: int | None = None
    last_entity_stdout = ""
    last_entity_stderr = ""
    last_sample_stderr = ""
    stream_proc: subprocess.Popen[str] | None = None
    stream_queue: queue.Queue[list[dict[str, Any]]] | None = None
    stream_stderr_queue: queue.Queue[str] | None = None

    # Remove stale markers from a previous review run. Marker 2 was used by
    # the older two-color center-revisit overlay; delete it so the review
    # surface is always one unambiguous red truth trail.
    for marker_id in (1, 2):
        publish_marker(
            args.command,
            args.marker_topic,
            delete_marker_text(args.namespace, marker_id),
            args.publish_timeout_s,
            transport_mode=args.transport_mode,
        )

    if args.capture_mode == "stream":
        stream_proc = start_truth_stream(args.command, args.truth_topic)
        stream_queue, stream_stderr_queue, _stdout_thread, _stderr_thread = start_stream_reader(
            stream_proc,
            model_name=args.model_name,
            topic=args.truth_topic,
            frame_id=args.frame_id,
        )

    def consume_sample(sample: dict[str, Any]) -> None:
        nonlocal parsed_samples, points, entity_points, pending_entity_segments, pre_revisit_points, revisit_points, was_in_center_band, center_band_entry_count
        raw_position = sample.get("position_m")
        if not isinstance(raw_position, list) or len(raw_position) != 3:
            return
        position = (
            float(raw_position[0]),
            float(raw_position[1]),
            float(raw_position[2]) + float(args.z_offset_m),
        )
        if should_add_point(points, position, args.min_point_distance_m):
            previous_position = points[-1] if points else None
            points.append(position)
            points = points[-args.max_points :]
            is_in_center_band = in_center_revisit_band(
                position,
                args.center_x_m,
                args.center_y_m,
                args.center_revisit_radius_m,
            )
            if is_in_center_band and not was_in_center_band:
                center_band_entry_count += 1
            was_in_center_band = is_in_center_band
            if center_band_entry_count >= 2:
                # Visual review wants a continuous color switch after the
                # second center pass. Seed the blue strip with the previous
                # sample so there is no visual gap at the switch point.
                if not revisit_points and previous_position is not None:
                    px, py, pz = previous_position
                    revisit_points.append((px, py, pz))
                bx, by, bz = position
                revisit_points.append((bx, by, bz))
                revisit_points = revisit_points[-args.max_points :]
            else:
                pre_revisit_points.append(position)
                pre_revisit_points = pre_revisit_points[-args.max_points :]
            append_jsonl(
                trace_jsonl,
                {
                    "schema": "mosim.gazebo_truth_trail_marker_sample.v1",
                    "elapsed_s": round(time.monotonic() - start, 6),
                    "position_m": [round(value, 6) for value in position],
                    "point_count": len(points),
                    "center_band_entry_count": center_band_entry_count,
                    "center_revisit_highlight": bool(center_band_entry_count >= 2),
                    "source_time_s": sample.get("time"),
                    "capture_mode": args.capture_mode,
                },
            )
        if args.entity_trail and args.world_name:
            entity_position = position
            if should_add_point(entity_points, entity_position, args.entity_segment_min_distance_m):
                previous_entity_position = entity_points[-1] if entity_points else None
                entity_points.append(entity_position)
                if previous_entity_position is not None:
                    pending_entity_segments.append((previous_entity_position, entity_position))

    while time.monotonic() - start < args.duration_s:
        now = time.monotonic()
        if now >= next_sample:
            sample_attempts += 1
            if args.capture_mode == "stream" and stream_queue is not None:
                drained = False
                while True:
                    try:
                        samples = stream_queue.get_nowait()
                    except queue.Empty:
                        break
                    drained = True
                    parsed_samples += len(samples)
                    for sample in samples:
                        consume_sample(sample)
                if stream_stderr_queue is not None:
                    while True:
                        try:
                            last_sample_stderr = stream_stderr_queue.get_nowait()[-500:]
                        except queue.Empty:
                            break
                if not drained and stream_proc is not None and stream_proc.poll() is not None:
                    last_sample_stderr = (last_sample_stderr + f" stream exited rc={stream_proc.returncode}")[-500:]
            else:
                stdout, stderr, returncode = run_sample(args.command, args.truth_topic, args.sample_timeout_s)
                last_sample_stderr = stderr[-500:]
                if returncode == 0 and stdout.strip():
                    samples = parse_samples(
                        stdout,
                        model_name=args.model_name,
                        topic=args.truth_topic,
                        frame_id=args.frame_id,
                    )
                    parsed_samples += len(samples)
                    for sample in samples:
                        consume_sample(sample)
            next_sample += 1.0 / args.sample_rate_hz

        if now >= next_publish and len(points) >= 2:
            marker_publish_attempts += 1
            line_marker = marker_text(
                    namespace=args.namespace,
                    marker_id=1,
                    marker_type="LINE_STRIP",
                    points=points,
                    scale_m=args.line_scale_m,
                    color=(1.0, 0.02, 0.0, 1.0),
            )
            markers = [line_marker]
            highlight_rc = 0
            highlight_stderr = ""
            if args.transport_mode == "service" and args.marker_topic.endswith("_array"):
                line_rc, _line_stdout, line_stderr = publish_marker_array(
                    args.command,
                    args.marker_topic,
                    markers,
                    args.publish_timeout_s,
                )
                highlight_rc = line_rc
                highlight_stderr = line_stderr
            else:
                line_rc, _line_stdout, line_stderr = publish_marker(
                    args.command,
                    args.marker_topic,
                    line_marker,
                    args.publish_timeout_s,
                    transport_mode=args.transport_mode,
                )
            last_marker_rc = highlight_rc if line_rc == 0 else line_rc
            last_marker_stderr = (highlight_stderr if highlight_rc else line_stderr)[-500:]
            marker_publish_success += int(line_rc == 0 and highlight_rc == 0)
            if args.entity_trail and args.world_name and pending_entity_segments:
                batch: list[tuple[tuple[float, float, float], tuple[float, float, float]]] = []
                for _ in range(max(1, args.entity_segments_per_publish)):
                    if not pending_entity_segments:
                        break
                    batch.append(pending_entity_segments.pop(0))
                if batch:
                    entity_spawn_attempts += 1
                    entity_name = f"{args.namespace}_red_batch_{entity_spawn_attempts:04d}"
                    entity_rc, entity_stdout, entity_stderr, valid_count = spawn_trail_segment_batch_entity(
                        args.command,
                        args.world_name,
                        entity_name,
                        batch,
                        args.entity_segment_radius_m,
                        args.publish_timeout_s,
                    )
                    last_entity_rc = entity_rc
                    last_entity_stdout = entity_stdout[-500:]
                    last_entity_stderr = entity_stderr[-500:]
                    if entity_rc == 0 and "data: true" in entity_stdout:
                        entity_spawn_success += 1
                        entity_spawned_segment_count += valid_count
            next_publish += 1.0 / args.publish_rate_hz

        time.sleep(0.01)

    if stream_proc is not None and stream_proc.poll() is None:
        stream_proc.terminate()
        try:
            stream_proc.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            stream_proc.kill()
            stream_proc.wait(timeout=1.0)

    status = "published" if marker_publish_success > 0 and len(points) >= 2 else "blocked"
    summary = {
        "schema": "mosim.gazebo_truth_trail_marker.v1",
        "status": status,
        "truth_topic": args.truth_topic,
        "marker_topic": args.marker_topic,
        "transport_mode": args.transport_mode,
        "model_name": args.model_name,
        "duration_s": args.duration_s,
        "capture_mode": args.capture_mode,
        "sample_attempts": sample_attempts,
        "parsed_samples": parsed_samples,
        "point_count": len(points),
        "visual_mode": "single_red_actual_truth_center_line",
        "line_scale_m": args.line_scale_m,
        "z_offset_m": args.z_offset_m,
        "center_revisit_radius_m": args.center_revisit_radius_m,
        "center_band_entry_count": center_band_entry_count,
        "revisit_highlight_point_count": len(revisit_points),
        "marker_publish_attempts": marker_publish_attempts,
        "marker_publish_success": marker_publish_success,
        "last_marker_rc": last_marker_rc,
        "last_marker_stderr": last_marker_stderr,
        "entity_trail_enabled": bool(args.entity_trail and args.world_name),
        "entity_trail_world_name": args.world_name,
        "entity_segment_radius_m": args.entity_segment_radius_m,
        "entity_segment_min_distance_m": args.entity_segment_min_distance_m,
        "entity_spawn_attempts": entity_spawn_attempts,
        "entity_spawn_success": entity_spawn_success,
        "entity_spawned_segment_count": entity_spawned_segment_count,
        "entity_pending_segment_count": len(pending_entity_segments),
        "last_entity_rc": last_entity_rc,
        "last_entity_stdout": last_entity_stdout,
        "last_entity_stderr": last_entity_stderr,
        "last_sample_stderr": last_sample_stderr,
        "trace_jsonl": str(trace_jsonl),
        "claim_boundary": [
            "Gazebo GUI trail marker only; it visualizes actual sampled truth pose.",
            "No control, planner, localization, controller-performance, or acceptance claim is made by this marker.",
        ],
    }
    write_json(summary_json, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if status == "published" else 2


if __name__ == "__main__":
    raise SystemExit(main())
