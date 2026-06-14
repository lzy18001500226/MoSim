#!/usr/bin/env python3
"""Build a UE replay input bundle for the accepted MWORKS single-UAV run.

This is a source-static preparation step. It validates the current closeout
gate, checks the accepted raw/metrics/replay/figure artifacts, and dry-runs the
UDP packet contract without opening Unreal Editor or sending UDP packets.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CLOSEOUT = (
    ROOT
    / "Results"
    / "mworks_model_hygiene"
    / "20260612_single_uav_pre_multi_uav_closeout_gate"
    / "single_uav_pre_multi_uav_closeout_gate.json"
)
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "Results"
    / "ue_replay_input"
    / "20260612_rotor1_loss15_linear_mpc_online_fault_allocation"
)
DEFAULT_SCENE_ID = "robust_rotor1_loss15_example1"
DEFAULT_MAP_ID = "local_factoryenvironmentcollect"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def repo_path(value: str | Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be an object: {rel(path)}")
    return data


def extract_json_objects(text: str) -> list[dict[str, Any]]:
    decoder = json.JSONDecoder()
    objects: list[dict[str, Any]] = []
    index = 0
    while index < len(text):
        start = text.find("{", index)
        if start < 0:
            break
        try:
            value, end = decoder.raw_decode(text[start:])
        except json.JSONDecodeError:
            index = start + 1
            continue
        if isinstance(value, dict):
            objects.append(value)
        index = start + end
    return objects


def csv_summary(path: Path) -> dict[str, Any]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        rows = list(reader)
    if not rows:
        raise ValueError(f"raw CSV has no rows: {rel(path)}")
    required = ["time", "x", "y", "z", "x_ref", "y_ref", "z_ref", "roll", "pitch", "yaw", "u1", "u2", "u3", "u4"]
    missing = [name for name in required if name not in headers]
    if missing:
        raise ValueError(f"raw CSV missing UE replay columns {missing}: {rel(path)}")
    return {
        "path": rel(path),
        "headers": headers,
        "row_count": len(rows),
        "time_start_s": float(rows[0]["time"]),
        "time_end_s": float(rows[-1]["time"]),
        "required_columns_present": not missing,
    }


def require_file(path: Path, label: str) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size <= 0:
        raise FileNotFoundError(f"missing or empty {label}: {rel(path)}")
    return {"path": rel(path), "bytes": path.stat().st_size}


def stream_dry_run(raw_path: Path, scene_id: str, map_id: str) -> dict[str, Any]:
    command = [
        sys.executable,
        "Scripts/UE5/stream_unreal_udp.py",
        rel(raw_path),
        "--scene-id",
        scene_id,
        "--map-id",
        map_id,
        "--max-frames",
        "1",
        "--dry-run",
        "--no-sleep",
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"stream_unreal_udp.py dry-run failed: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    packets = extract_json_objects(result.stdout)
    packet_types = [str(packet.get("type")) for packet in packets]
    frame = next((packet for packet in packets if packet.get("type") == "frame"), None)
    if frame is None:
        raise ValueError("stream dry-run emitted no frame packet")
    for field in ["scene_id", "map_id", "uav", "reference", "status"]:
        if field not in frame:
            raise ValueError(f"stream dry-run frame missing field: {field}")
    uav = frame.get("uav", {})
    if not isinstance(uav, dict):
        raise ValueError("stream dry-run frame.uav must be an object")
    for field in ["position_m", "rpy_rad", "motor_command"]:
        if field not in uav:
            raise ValueError(f"stream dry-run frame.uav missing field: {field}")
    if frame.get("scene_id") != scene_id or frame.get("map_id") != map_id:
        raise ValueError("stream dry-run frame scene/map mismatch")
    return {
        "command": " ".join(command),
        "packet_types": packet_types,
        "frame_schema": frame.get("schema"),
        "frame_scene_id": frame.get("scene_id"),
        "frame_map_id": frame.get("map_id"),
        "frame_status": frame.get("status"),
    }


def build_bundle(closeout_path: Path, output_dir: Path, scene_id: str, map_id: str) -> dict[str, Any]:
    closeout = read_json(closeout_path)
    current = closeout.get("current_candidate_rerun_evidence", {})
    if closeout.get("status") != "single_uav_gate_ready_for_ue_prep":
        raise ValueError(f"closeout gate is not UE-prep-ready: {closeout.get('status')}")
    if current.get("accepted_current_rerun") is not True:
        raise ValueError("closeout gate does not have accepted current-rerun evidence")

    candidate = closeout.get("rotor1_candidate_summary", {}).get("best_rmse_candidate", {})
    if not isinstance(candidate, dict) or not candidate:
        raise ValueError("closeout gate has no best candidate")

    raw_path = repo_path(str(current["raw_file"]))
    metrics_path = repo_path(str(current["metrics_file"]))
    scenario_path = repo_path(str(candidate["scenario"]))
    metrics = read_json(metrics_path)

    scenario = read_json(scenario_path) if scenario_path.suffix.lower() == ".json" else None
    if scenario is not None:
        replay_ref = scenario.get("result", {}).get("replay_file")
        figure_dir_ref = scenario.get("result", {}).get("figure_dir")
    else:
        # The project YAML reader is intentionally not imported here; the
        # accepted convention places replay and figures beside raw/metrics.
        result_root = raw_path.parents[1]
        replay_ref = result_root / "replay" / f"{candidate['experiment_id']}.json"
        figure_dir_ref = result_root / "figures"
    replay_path = repo_path(replay_ref)
    figure_dir = repo_path(figure_dir_ref)

    raw = csv_summary(raw_path)
    replay = require_file(replay_path, "replay JSON")
    figures = sorted(path for path in figure_dir.glob("*") if path.is_file() and path.stat().st_size > 0)
    if not figures:
        raise FileNotFoundError(f"no non-empty figures found: {rel(figure_dir)}")

    dry_run = stream_dry_run(raw_path, scene_id, map_id)
    bundle = {
        "schema": "mosim.ue_replay_input_bundle.v1",
        "status": "ready_for_source_static_ue_replay_input",
        "source_static_only": True,
        "ue_editor_opened": False,
        "ue_runtime_started": False,
        "udp_sent": False,
        "closeout_gate": rel(closeout_path),
        "scene_binding": {
            "scene_id": scene_id,
            "map_id": map_id,
            "map_id_role": "registry_scene_source_id_for_AQuadrotorMworksMapActor.ResolveSceneSourceId",
            "scenario_visual_label": "open_grass_robustness",
            "coordinate_frame": "MWORKS world, meters, z-up",
            "unreal_conversion": "X=mworks_x*100, Y=-mworks_y*100, Z=mworks_z*100",
            "display_only": True,
        },
        "accepted_candidate": {
            "scenario": candidate.get("scenario"),
            "controller_id": candidate.get("controller_id"),
            "model_name": candidate.get("model_name"),
            "experiment_id": candidate.get("experiment_id"),
            "quality_status": candidate.get("quality_status"),
            "position_rmse_m": candidate.get("position_rmse_m"),
            "total_health_score": candidate.get("total_health_score"),
        },
        "artifacts": {
            "scenario": require_file(scenario_path, "scenario config"),
            "raw": raw,
            "metrics": require_file(metrics_path, "metrics JSON"),
            "replay": replay,
            "figures": [{"path": rel(path), "bytes": path.stat().st_size} for path in figures],
        },
        "metrics_summary": {
            "source": metrics.get("source"),
            "quality_checked_at": metrics.get("quality_checked_at"),
            "row_count": metrics.get("row_count"),
            "duration_s": metrics.get("duration_s"),
            "position_rmse_m": metrics.get("position_rmse_m"),
            "max_position_error_m": metrics.get("max_position_error_m"),
            "steady_state_error_m": metrics.get("steady_state_error_m"),
            "disturbance_peak_error_m": metrics.get("disturbance_peak_error_m"),
            "disturbance_recovery_time_s": metrics.get("disturbance_recovery_time_s"),
            "total_health_score": metrics.get("total_health_score"),
        },
        "stream_contract_dry_run": dry_run,
        "next_allowed_actions": [
            "If the user has authorized direct continuation, run the next bounded UE replay/render readiness step without waiting for PMO idleness.",
            "Use stream_unreal_udp.py with the same raw CSV, scene_id, and map_id when the UE workflow gate authorizes UDP/runtime scope.",
            "Keep UE output as visual/replay evidence only; MWORKS metrics remain the controller-performance source.",
        ],
        "forbidden_claims": [
            "UE runtime success",
            "UE editor/build acceptance",
            "closed_loop success beyond the MWORKS evidence scope",
            "planner_ready",
            "multi-UAV formation readiness",
        ],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ue_replay_input_bundle.json").write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# UE Replay Input Bundle",
        "",
        f"Status: `{bundle['status']}`",
        f"Scene: `{scene_id}`",
        f"Map: `{map_id}`",
        f"Controller: `{bundle['accepted_candidate']['controller_id']}`",
        f"Raw rows: `{raw['row_count']}`",
        f"Quality: `{bundle['accepted_candidate']['quality_status']}`",
        "",
        "This bundle did not open Unreal Editor, start UE runtime, or send UDP.",
        "",
        "## Artifacts",
        "",
        f"- Raw: `{raw['path']}`",
        f"- Metrics: `{bundle['artifacts']['metrics']['path']}`",
        f"- Replay: `{replay['path']}`",
        f"- Figures: `{len(figures)}` non-empty files",
        "",
        "## Boundary",
        "",
    ]
    lines.extend(f"- {item}" for item in bundle["forbidden_claims"])
    (output_dir / "ue_replay_input_bundle.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return bundle


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--closeout-gate", type=Path, default=DEFAULT_CLOSEOUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--scene-id", default=DEFAULT_SCENE_ID)
    parser.add_argument("--map-id", default=DEFAULT_MAP_ID)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    bundle = build_bundle(
        repo_path(args.closeout_gate),
        repo_path(args.output_dir),
        args.scene_id,
        args.map_id,
    )
    print(json.dumps(bundle, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
