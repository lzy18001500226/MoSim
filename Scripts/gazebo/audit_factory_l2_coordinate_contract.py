#!/usr/bin/env python3
"""Audit Factory L2 UE/Gazebo coordinate and static-mesh bounds.

This is a source/static audit. It does not launch Gazebo, PX4, ROS, RViz, or
UE. The goal is to prove the axis/unit contract and catch scene-export objects
that pollute the global Gazebo physical world.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_EXPORT_ROOT = ROOT / "Results/unreal_scene_mapping/factory_l2_static_import"
DEFAULT_TRUTH = ROOT / "UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/factoryenvironmentcollect_collision_truth.json"
DEFAULT_SCENE_PROFILE = ROOT / "Config/gazebo/scene_profiles/factory_l2_static_sunray_scene.json"
DEFAULT_F7_RUN = ROOT / "Results/sunray_ros1/factory_l2_racer_swarm_l1_awff_pairguard10_20260702_044053"


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def update_bounds(mins: list[float], maxs: list[float], values: list[float] | tuple[float, float, float]) -> None:
    for index, value in enumerate(values):
        if math.isfinite(float(value)):
            mins[index] = min(mins[index], float(value))
            maxs[index] = max(maxs[index], float(value))


def bounds_payload(mins: list[float], maxs: list[float]) -> dict[str, Any]:
    return {
        "min_m": mins,
        "max_m": maxs,
        "size_m": [maxs[index] - mins[index] for index in range(3)],
        "center_m": [(maxs[index] + mins[index]) * 0.5 for index in range(3)],
    }


def truth_bounds(path: Path) -> dict[str, Any]:
    payload = read_json(path)
    proxies = payload.get("collision_proxies", [])
    if not isinstance(proxies, list):
        raise ValueError(f"collision_proxies must be a list: {path}")
    mins = [float("inf"), float("inf"), float("inf")]
    maxs = [float("-inf"), float("-inf"), float("-inf")]
    proxy_count = 0
    for proxy in proxies:
        if not isinstance(proxy, dict):
            continue
        min_m = proxy.get("min_m")
        max_m = proxy.get("max_m")
        if not (isinstance(min_m, list) and isinstance(max_m, list) and len(min_m) >= 3 and len(max_m) >= 3):
            continue
        proxy_count += 1
        update_bounds(mins, maxs, [float(value) for value in min_m[:3]])
        update_bounds(mins, maxs, [float(value) for value in max_m[:3]])
    return {
        "path": rel(path),
        "coordinate_system": payload.get("coordinate_system", {}),
        "collision_proxy_count": proxy_count,
        "bounds": bounds_payload(mins, maxs),
    }


def glb_json(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        magic, version, _length = struct.unpack("<4sII", handle.read(12))
        if magic != b"glTF" or version != 2:
            raise ValueError(f"not a GLB v2 file: {path}")
        chunk_length, chunk_type = struct.unpack("<II", handle.read(8))
        if chunk_type != 0x4E4F534A:
            raise ValueError(f"first GLB chunk is not JSON: {path}")
        return json.loads(handle.read(chunk_length).decode("utf-8"))


def suspect_glb_nodes(path: Path, *, suspect_terms: list[str]) -> dict[str, Any]:
    payload = glb_json(path)
    nodes = payload.get("nodes", [])
    suspects: list[dict[str, Any]] = []
    for index, node in enumerate(nodes):
        if not isinstance(node, dict) or "mesh" not in node:
            continue
        name = str(node.get("name", ""))
        if any(term.lower() in name.lower() for term in suspect_terms):
            suspects.append({
                "node_index": index,
                "name": name,
                "mesh": node.get("mesh"),
                "translation": node.get("translation", [0.0, 0.0, 0.0]),
                "rotation": node.get("rotation", [0.0, 0.0, 0.0, 1.0]),
                "scale": node.get("scale", [1.0, 1.0, 1.0]),
            })
    return {
        "path": rel(path),
        "node_count": len(nodes),
        "mesh_count": len(payload.get("meshes", [])),
        "suspect_terms": suspect_terms,
        "suspect_mesh_nodes": suspects,
    }


def binary_stl_bounds(path: Path) -> dict[str, Any]:
    mins = [float("inf"), float("inf"), float("inf")]
    maxs = [float("-inf"), float("-inf"), float("-inf")]
    extreme_triangle_count = 0
    with path.open("rb") as handle:
        handle.read(80)
        raw_count = handle.read(4)
        if len(raw_count) < 4:
            raise ValueError(f"invalid STL: {path}")
        triangle_count = struct.unpack("<I", raw_count)[0]
        expected_size = 84 + triangle_count * 50
        if expected_size != path.stat().st_size:
            raise ValueError(f"only binary STL is supported here: {path}")
        for _ in range(triangle_count):
            data = handle.read(50)
            if len(data) < 50:
                break
            values = struct.unpack("<12fH", data)
            triangle_is_extreme = False
            for start in (3, 6, 9):
                vertex = [values[start], values[start + 1], values[start + 2]]
                update_bounds(mins, maxs, vertex)
                if any(abs(float(component)) >= 2000.0 for component in vertex):
                    triangle_is_extreme = True
            if triangle_is_extreme:
                extreme_triangle_count += 1
    max_abs = max(abs(value) for value in mins + maxs)
    return {
        "path": rel(path),
        "size_bytes": path.stat().st_size,
        "triangle_count": triangle_count,
        "bounds": bounds_payload(mins, maxs),
        "max_abs_coordinate_m": max_abs,
        "extreme_triangle_count_ge_2000m": extreme_triangle_count,
    }


def conversion_bounds(path: Path, *, pollution_threshold_m: float) -> dict[str, Any]:
    payload = read_json(path)
    chunks = payload.get("chunks", [])
    if not isinstance(chunks, list):
        raise ValueError(f"chunks must be a list: {path}")
    mins = [float("inf"), float("inf"), float("inf")]
    maxs = [float("-inf"), float("-inf"), float("-inf")]
    chunk_reports: list[dict[str, Any]] = []
    polluted_chunks: list[dict[str, Any]] = []
    for chunk in chunks:
        if not isinstance(chunk, dict):
            continue
        chunk_path = Path(str(chunk.get("path") or ""))
        if not chunk_path.is_absolute():
            chunk_path = ROOT / chunk_path
        if not chunk_path.exists():
            chunk_reports.append({
                "chunk_index": chunk.get("chunk_index"),
                "path": rel(chunk_path),
                "missing": True,
            })
            continue
        report = binary_stl_bounds(chunk_path)
        report["chunk_index"] = chunk.get("chunk_index")
        report["object_count"] = chunk.get("object_count")
        report["mesh_names_sample"] = chunk.get("mesh_names_sample", [])
        update_bounds(mins, maxs, report["bounds"]["min_m"])
        update_bounds(mins, maxs, report["bounds"]["max_m"])
        if float(report["max_abs_coordinate_m"]) > pollution_threshold_m:
            polluted_chunks.append(report)
        chunk_reports.append(report)
    return {
        "path": rel(path),
        "ok": payload.get("ok"),
        "chunk_count": len(chunks),
        "exclude_name_regex": payload.get("exclude_name_regex", []),
        "excluded_mesh_object_count": payload.get("excluded_mesh_object_count", 0),
        "excluded_mesh_names": payload.get("excluded_mesh_names", []),
        "bounds": bounds_payload(mins, maxs),
        "pollution_threshold_m": pollution_threshold_m,
        "polluted_chunk_count": len(polluted_chunks),
        "polluted_chunks": polluted_chunks,
        "chunk_reports_sample": chunk_reports[:5],
    }


def f7_trajectory_bounds(run_dir: Path) -> dict[str, Any]:
    mins = [float("inf"), float("inf"), float("inf")]
    maxs = [float("-inf"), float("-inf"), float("-inf")]
    row_count = 0
    files: list[str] = []
    for path in sorted(run_dir.glob("uav*_truth.csv")):
        files.append(rel(path))
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                keys = [
                    next((candidate for candidate in ("x", "pos_x", "position_x", "truth_x") if candidate in row), None),
                    next((candidate for candidate in ("y", "pos_y", "position_y", "truth_y") if candidate in row), None),
                    next((candidate for candidate in ("z", "pos_z", "position_z", "truth_z") if candidate in row), None),
                ]
                if any(key is None for key in keys):
                    continue
                values = [float(row[key]) for key in keys if key is not None]
                row_count += 1
                update_bounds(mins, maxs, values)
    if row_count == 0:
        return {"path": rel(run_dir), "row_count": 0, "files": files}
    return {
        "path": rel(run_dir),
        "row_count": row_count,
        "files": files,
        "bounds": bounds_payload(mins, maxs),
    }


def anchor_points(truth: dict[str, Any], scene_profile: dict[str, Any]) -> list[dict[str, Any]]:
    bounds = truth["bounds"]
    min_m = bounds["min_m"]
    max_m = bounds["max_m"]
    center_m = bounds["center_m"]
    anchors = [
        {"id": "world_origin", "type": "origin", "mworks_xyz_m": [0.0, 0.0, 0.0]},
        {"id": "truth_bounds_min", "type": "truth_aabb_corner", "mworks_xyz_m": min_m},
        {"id": "truth_bounds_max", "type": "truth_aabb_corner", "mworks_xyz_m": max_m},
        {"id": "truth_bounds_center", "type": "truth_aabb_center", "mworks_xyz_m": center_m},
    ]
    for spawn in scene_profile.get("default_spawn_points", []):
        if isinstance(spawn, dict):
            anchors.append({
                "id": f"default_spawn_uav{spawn.get('uav', 'unknown')}",
                "type": "scene_profile_spawn",
                "mworks_xyz_m": [float(spawn.get("x", 0.0)), float(spawn.get("y", 0.0)), float(spawn.get("z", 0.0))],
                "yaw_rad": float(spawn.get("yaw", 0.0)),
            })
    for anchor in anchors:
        x_m, y_m, z_m = anchor["mworks_xyz_m"]
        anchor["unreal_xyz_cm"] = [x_m * 100.0, -y_m * 100.0, z_m * 100.0]
    return anchors


def write_anchor_csv(path: Path, anchors: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "type",
                "mworks_x_m",
                "mworks_y_m",
                "mworks_z_m",
                "unreal_x_cm",
                "unreal_y_cm",
                "unreal_z_cm",
            ],
        )
        writer.writeheader()
        for anchor in anchors:
            writer.writerow({
                "id": anchor["id"],
                "type": anchor["type"],
                "mworks_x_m": anchor["mworks_xyz_m"][0],
                "mworks_y_m": anchor["mworks_xyz_m"][1],
                "mworks_z_m": anchor["mworks_xyz_m"][2],
                "unreal_x_cm": anchor["unreal_xyz_cm"][0],
                "unreal_y_cm": anchor["unreal_xyz_cm"][1],
                "unreal_z_cm": anchor["unreal_xyz_cm"][2],
            })


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export-root", type=Path, default=DEFAULT_EXPORT_ROOT)
    parser.add_argument("--scene-truth", type=Path, default=DEFAULT_TRUTH)
    parser.add_argument("--scene-profile", type=Path, default=DEFAULT_SCENE_PROFILE)
    parser.add_argument("--conversion-manifest", type=Path, default=None)
    parser.add_argument("--f7-run-dir", type=Path, default=DEFAULT_F7_RUN)
    parser.add_argument("--result-dir", type=Path, default=None)
    parser.add_argument("--pollution-threshold-m", type=float, default=2000.0)
    parser.add_argument("--suspect-term", action="append", default=["SkySphere", "Sky"])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    export_root = project_path(args.export_root)
    scene_truth = project_path(args.scene_truth)
    scene_profile_path = project_path(args.scene_profile)
    conversion_manifest = (
        project_path(args.conversion_manifest)
        if args.conversion_manifest is not None
        else export_root / "manifests" / "blender_chunked_stl_conversion.json"
    )
    export_manifest = read_json(export_root / "manifests" / "unreal_level_gltf_export.json")
    source_glb = Path(str(export_manifest["glb_output"]))
    if not source_glb.is_absolute():
        source_glb = ROOT / source_glb
    source_glb = project_path(source_glb)

    result_dir = (
        project_path(args.result_dir)
        if args.result_dir is not None
        else ROOT / "Results/unreal_scene_mapping" / f"factory_l2_coordinate_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    result_dir.mkdir(parents=True, exist_ok=True)

    truth_report = truth_bounds(scene_truth)
    scene_profile = read_json(scene_profile_path)
    anchors = anchor_points(truth_report, scene_profile)
    anchor_csv = result_dir / "factory_l2_anchor_points.csv"
    write_anchor_csv(anchor_csv, anchors)

    conversion_report = conversion_bounds(conversion_manifest, pollution_threshold_m=args.pollution_threshold_m)
    glb_report = suspect_glb_nodes(source_glb, suspect_terms=list(args.suspect_term))
    trajectory_report = f7_trajectory_bounds(project_path(args.f7_run_dir))

    axis_policy = truth_report["coordinate_system"].get("axis_policy")
    axis_policy_ok = axis_policy == "mworks_x=unreal_x, mworks_y=-unreal_y, mworks_z=unreal_z"
    polluted = int(conversion_report["polluted_chunk_count"]) > 0
    status = "passed" if axis_policy_ok and not polluted else "blocked_needs_clean_import"
    packet = {
        "schema": "mosim.factory_l2_coordinate_audit.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "claim_boundary": [
            "This is a source/static coordinate and mesh-bound audit only.",
            "It proves or blocks the Factory static-map coordinate contract; it does not prove ROS/PX4/MAVROS/RViz runtime success.",
            "UE remains display/review support and does not feed truth, localization, planning, or control.",
        ],
        "coordinate_contract": {
            "mworks_to_unreal_position": "UE_X_cm = MWORKS_X_m * 100; UE_Y_cm = -MWORKS_Y_m * 100; UE_Z_cm = MWORKS_Z_m * 100",
            "unreal_to_mworks_position": "MWORKS_X_m = UE_X_cm / 100; MWORKS_Y_m = -UE_Y_cm / 100; MWORKS_Z_m = UE_Z_cm / 100",
            "axis_policy_from_truth": axis_policy,
            "axis_policy_ok": axis_policy_ok,
        },
        "inputs": {
            "scene_truth": rel(scene_truth),
            "scene_profile": rel(scene_profile_path),
            "ue_export_manifest": rel(export_root / "manifests" / "unreal_level_gltf_export.json"),
            "source_glb": rel(source_glb),
            "conversion_manifest": rel(conversion_manifest),
            "f7_run_dir": rel(project_path(args.f7_run_dir)),
        },
        "truth": truth_report,
        "glb_suspects": glb_report,
        "gazebo_chunks": conversion_report,
        "f7_runtime_coverage": trajectory_report,
        "anchor_points_csv": rel(anchor_csv),
        "anchor_points": anchors,
        "decision": {
            "factory_static_import_clean": bool(not polluted),
            "requires_filtered_reexport": bool(polluted),
            "primary_reason": (
                "No chunk exceeds the pollution threshold."
                if not polluted
                else "At least one Gazebo STL chunk exceeds the pollution threshold; filter nonphysical UE scene objects and rebuild the review world."
            ),
        },
    }

    packet_path = result_dir / "FACTORY_L2_COORDINATE_AUDIT.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_path = result_dir / "SUMMARY.md"
    summary_path.write_text(
        "\n".join([
            "# Factory L2 Coordinate Audit",
            "",
            f"- status: `{status}`",
            f"- axis policy: `{axis_policy}`",
            f"- polluted chunk count: `{conversion_report['polluted_chunk_count']}`",
            f"- truth bounds size m: `{truth_report['bounds']['size_m']}`",
            f"- gazebo chunk bounds size m: `{conversion_report['bounds']['size_m']}`",
            f"- anchor csv: `{rel(anchor_csv)}`",
            "",
            "This audit is source/static only. Runtime validation must be rerun after a clean scene profile is promoted.",
            "",
        ]),
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "packet": rel(packet_path), "summary": rel(summary_path)}, ensure_ascii=False, indent=2))
    return 0 if status == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
