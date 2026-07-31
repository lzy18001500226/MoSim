#!/usr/bin/env python3
"""Validate a completed standalone UE replay receiver capture.

This is an evidence reader only. It never starts Unreal, Gazebo, ROS, QGC, or
any controller. It binds the one-way replay contract, UE receiver metrics,
UE frame timing, and the operator's pointer-release review into an F7B status
file beside the existing F7A replay bundle.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
STATUS_SCHEMA = "mosim.ue_render_runtime_receiver_status.v1"


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"missing required evidence: {rel(path)}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON evidence: {rel(path)}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON evidence must be an object: {rel(path)}")
    return value


def numeric(value: Any, *, field: str, issues: list[str]) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        issues.append(f"{field}_not_numeric")
        return 0.0
    return parsed


def log_evidence(path: Path, *, scene_id: str, map_id: str, port: int) -> dict[str, Any]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return {"path": rel(path), "status": "missing", "listener_found": False, "first_frame_found": False}

    listener_token = f"listening on 0.0.0.0:{port}"
    first_frame_token = "UDP first frame:"
    listener_lines = [line.strip() for line in lines if listener_token in line]
    first_frame_lines = [line.strip() for line in lines if first_frame_token in line]
    matching_first_frames = [line for line in first_frame_lines if f"scene={scene_id}" in line and f"map={map_id}" in line]
    return {
        "path": rel(path),
        "status": "passed" if listener_lines and matching_first_frames else "incomplete",
        "listener_found": bool(listener_lines),
        "first_frame_found": bool(matching_first_frames),
        "listener_line": listener_lines[-1] if listener_lines else None,
        "first_frame_line": matching_first_frames[-1] if matching_first_frames else None,
    }


def validate(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    replay_dir = repo_path(args.replay_dir)
    manifest_path = replay_dir / "UE_RENDER_STREAM_MANIFEST.json"
    contract_path = replay_dir / "UE_RENDER_STREAM_VALIDATION.json"
    receiver_path = replay_dir / args.receiver_metrics_name
    frame_path = replay_dir / args.frame_metrics_name
    output_path = repo_path(args.output) if args.output else replay_dir / "F7B_UE_RUNTIME_RECEIVER_STATUS.json"
    ue_log_path = repo_path(args.ue_log)

    issues: list[str] = []
    try:
        manifest = read_json(manifest_path)
        contract = read_json(contract_path)
        receiver = read_json(receiver_path)
        frame = read_json(frame_path)
    except ValueError as exc:
        payload = {
            "schema": STATUS_SCHEMA,
            "status": "blocked",
            "reason": str(exc),
            "claim_boundary": "No runtime acceptance is inferred when required evidence is missing or malformed.",
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return payload, 1

    run_id = str(args.run_id or manifest.get("run_id", ""))
    scene_id = str(manifest.get("scene_id", ""))
    map_id = str(manifest.get("map_id", ""))
    transport = manifest.get("transport_profile") if isinstance(manifest.get("transport_profile"), dict) else {}

    if not run_id:
        issues.append("missing_run_id")
    if manifest.get("status") != "replay_contract_passed":
        issues.append("replay_contract_not_passed")
    if contract.get("status") != "passed":
        issues.append("replay_frame_validation_not_passed")
    if transport.get("feedback_to_runtime") is not False:
        issues.append("replay_contract_allows_or_omits_runtime_feedback_guard")
    if receiver.get("run_id") != run_id:
        issues.append("receiver_run_id_mismatch")
    if frame.get("run_id") != run_id:
        issues.append("frame_timing_run_id_mismatch")

    received_frames = numeric(receiver.get("received_frames"), field="received_frames", issues=issues)
    receive_rate_hz = numeric(receiver.get("receive_rate_hz"), field="receive_rate_hz", issues=issues)
    ue_fps = numeric(frame.get("ue_fps"), field="ue_fps", issues=issues)
    if received_frames <= 0:
        issues.append("receiver_has_no_frames")
    if receive_rate_hz <= 0:
        issues.append("receiver_has_no_positive_rate")
    if ue_fps <= 0:
        issues.append("ue_has_no_positive_frame_rate")

    log = log_evidence(ue_log_path, scene_id=scene_id, map_id=map_id, port=args.port)
    if not log["listener_found"]:
        issues.append("ue_log_missing_udp_listener")
    if not log["first_frame_found"]:
        issues.append("ue_log_missing_matching_first_frame")
    if not args.pointer_release_operator_confirmed:
        issues.append("pointer_release_operator_review_not_confirmed")

    observations = {
        "sequence_gap_count": receiver.get("sequence_gap_count"),
        "receiver_drop_rate": receiver.get("receiver_drop_rate"),
        "hitch_count_50ms": frame.get("hitch_count_50ms"),
        "note": "These are recorded observations, not performance thresholds for the functional display gate.",
    }
    payload = {
        "schema": STATUS_SCHEMA,
        "status": "passed" if not issues else "blocked",
        "run_id": run_id,
        "scene_id": scene_id,
        "map_id": map_id,
        "mode": "standalone_ue_display_only",
        "transport": {
            "port": args.port,
            "one_way": True,
            "feedback_to_runtime": False,
            "gzclient_started_by_this_probe": False,
            "qgc_started_by_this_probe": False,
        },
        "source_evidence": {
            "replay_manifest": rel(manifest_path),
            "replay_validation": rel(contract_path),
            "receiver_metrics": rel(receiver_path),
            "frame_metrics": rel(frame_path),
            "ue_log": log,
        },
        "receiver": {
            "received_frames": received_frames,
            "receive_rate_hz": receive_rate_hz,
            "sequence_gap_count": receiver.get("sequence_gap_count"),
            "receiver_drop_rate": receiver.get("receiver_drop_rate"),
            "payload_bytes_per_s": receiver.get("payload_bytes_per_s"),
        },
        "frame_timing": {
            "ue_fps": ue_fps,
            "ue_frame_ms_mean": frame.get("ue_frame_ms_mean"),
            "ue_frame_ms_max": frame.get("ue_frame_ms_max"),
            "hitch_count_50ms": frame.get("hitch_count_50ms"),
        },
        "operator_review": {
            "pointer_release_status": "passed" if args.pointer_release_operator_confirmed else "not_confirmed",
            "evidence": "operator confirmed standalone UE mouse pointer is usable" if args.pointer_release_operator_confirmed else "no operator confirmation supplied",
        },
        "observations": observations,
        "issues": issues,
        "claim_boundary": [
            "F7B proves the standalone UE receiver accepted the replay stream and wrote local receiver/frame metrics.",
            "UE remains a one-way display consumer; it does not control Gazebo, PX4, MAVROS, px4ctrl, a planner, or an estimator.",
            "This does not prove Factory physical collision/planning validation, controller robustness, or fault tolerance.",
        ],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload, 0 if not issues else 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay-dir", required=True, help="F7A replay output directory")
    parser.add_argument("--run-id", default=None, help="Expected run_id; defaults to the F7A manifest run_id")
    parser.add_argument("--port", type=int, default=5005)
    parser.add_argument("--ue-log", default="UE5/MoSimSceneLibrary/Saved/Logs/MoSimSceneLibrary.log")
    parser.add_argument("--receiver-metrics-name", default="ue_receiver_metrics.json")
    parser.add_argument("--frame-metrics-name", default="ue_frame_metrics.json")
    parser.add_argument("--pointer-release-operator-confirmed", action="store_true")
    parser.add_argument("--output", default=None)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    payload, code = validate(args)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
