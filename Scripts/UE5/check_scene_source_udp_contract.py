#!/usr/bin/env python3
"""Validate the UDP contract for registry-backed Unreal scene sources.

This is a source/packet-level check. It does not open Unreal Editor. The check
proves that the current primary scene source can be selected by `map_id` in the
MWORKS-to-Unreal stream and that the packet remains explicitly render-only
unless separate planning evidence is supplied.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from build_scene_source_registry import validate_registry


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / "UE5/MoSimSceneLibrary/Content/MworksData/scene_source_registry.json"
DEFAULT_RAW = (
    ROOT
    / "Results/planning/single_obstacle_astar_awff/"
    / "sunray150_planning_open_blocks_linear_mpc_sysblock/raw/"
    / "sunray150_planning_open_blocks_linear_mpc_height_profile_0p2_sensor_20hz.csv"
)
DEFAULT_SCENE_ID = "derelict_scene_source_contract"


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{rel(path)} root must be a JSON object")
    return payload


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


def source_by_id(registry: dict[str, Any], source_id: str) -> dict[str, Any]:
    fallback = registry.get("local_editable_fallback", {})
    if not isinstance(fallback, dict):
        raise ValueError("local_editable_fallback must be an object")
    sources = fallback.get("scene_sources", [])
    if not isinstance(sources, list):
        raise ValueError("local_editable_fallback.scene_sources must be a list")
    for source in sources:
        if isinstance(source, dict) and source.get("scene_source_id") == source_id:
            return source
    raise ValueError(f"scene source not found in registry: {source_id}")


def validate_primary_source(registry: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    errors = validate_registry(registry)
    if errors:
        raise ValueError("registry validation failed:\n- " + "\n- ".join(errors))

    policy = registry.get("policy", {})
    if not isinstance(policy, dict):
        raise ValueError("registry.policy must be an object")
    primary = str(policy.get("primary_scene_source_id", ""))
    if not primary:
        raise ValueError("registry.policy.primary_scene_source_id is empty")

    source = source_by_id(registry, primary)
    if source.get("status") != "accepted_local_truth_fallback":
        raise ValueError(f"{primary} is not accepted_local_truth_fallback")
    for key in ["editable_candidate", "renderable_candidate", "planning_truth_ready"]:
        if source.get(key) is not True:
            raise ValueError(f"{primary} missing true gate: {key}")

    artifacts = source.get("truth_artifacts", [])
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError(f"{primary} has no truth artifacts")
    missing = [artifact for artifact in artifacts if not (ROOT / str(artifact)).exists()]
    if missing:
        raise ValueError(f"{primary} missing truth artifact files: {', '.join(map(str, missing))}")
    return primary, source


def run_stream_dry_run(raw_csv: Path, scene_id: str, map_id: str) -> list[dict[str, Any]]:
    if not raw_csv.exists():
        raise FileNotFoundError(f"sample raw CSV not found: {rel(raw_csv)}")
    command = [
        sys.executable,
        "Scripts/UE5/stream_unreal_udp.py",
        rel(raw_csv),
        "--scene-id",
        scene_id,
        "--map-id",
        map_id,
        "--max-frames",
        "1",
        "--dry-run",
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(
            "stream_unreal_udp.py dry-run failed with "
            f"{result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
    packets = extract_json_objects(result.stdout)
    if not packets:
        raise ValueError("stream_unreal_udp.py dry-run emitted no JSON packets")
    return packets


def validate_packets(packets: list[dict[str, Any]], *, scene_id: str, map_id: str) -> dict[str, Any]:
    typed = {str(packet.get("type")): packet for packet in packets}
    for packet_type in ["hello", "frame", "end"]:
        if packet_type not in typed:
            raise ValueError(f"missing UDP packet type: {packet_type}")

    hello = typed["hello"]
    frame = typed["frame"]
    end = typed["end"]
    for packet in [hello, frame, end]:
        if packet.get("scene_id") != scene_id:
            raise ValueError(f"{packet.get('type')} scene_id mismatch: {packet.get('scene_id')}")
    if hello.get("map_id") != map_id or frame.get("map_id") != map_id:
        raise ValueError("hello/frame map_id does not select the primary scene source")

    local_known_map = frame.get("local_known_map")
    local_plan = frame.get("local_plan")
    status = frame.get("status")
    if not isinstance(local_known_map, dict):
        raise ValueError("frame.local_known_map must be an object")
    if not isinstance(local_plan, dict):
        raise ValueError("frame.local_plan must be an object")
    if not isinstance(status, dict):
        raise ValueError("frame.status must be an object")
    if local_known_map.get("render_only") is not True or local_known_map.get("evidence_backed") is not False:
        raise ValueError("local_known_map must stay render_only and not evidence-backed in this dry-run")
    if local_plan.get("source") != "preview_from_reference":
        raise ValueError("dry-run local_plan source should be preview_from_reference")
    if local_plan.get("render_only") is not True or local_plan.get("evidence_backed") is not False:
        raise ValueError("preview local_plan must stay render_only and not evidence-backed")
    if status.get("evidence_level") != "render_only_preview":
        raise ValueError("dry-run status.evidence_level must be render_only_preview")
    return frame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--raw-csv", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--scene-id", default=DEFAULT_SCENE_ID)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = load_json(args.registry)
    primary, source = validate_primary_source(registry)
    packets = run_stream_dry_run(args.raw_csv, args.scene_id, primary)
    frame = validate_packets(packets, scene_id=args.scene_id, map_id=primary)
    print("[OK] scene-source UDP contract")
    print(f"scene_source_id: {primary}")
    print(f"source_status: {source['status']}")
    print(f"truth_artifacts: {len(source.get('truth_artifacts', []))}")
    print(f"frame_seq: {frame.get('seq')} t={frame.get('t')}")
    print("scope: packet/source-level only; visual import remains a separate UE review gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
