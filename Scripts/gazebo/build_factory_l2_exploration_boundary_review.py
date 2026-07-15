#!/usr/bin/env python3
"""Build Factory L2 exploration-boundary review artifacts.

This is a source/static visual-review helper. It reads the current Factory L2
exploration envelope and creates a UE placement script plus simple CSV/JSON
evidence so the user can visually accept or reject the intended exploration
boundary before any full-map exploration run.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ENVELOPE = ROOT / "Config/gazebo/scene_profiles/factory_l2_exploration_envelope.json"
DEFAULT_SCENE_TRUTH = ROOT / "UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/factoryenvironmentcollect_collision_truth.json"
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"

COLORS = {
    "boundary": (1.0, 0.05, 0.03, 1.0),
    "top_boundary": (0.08, 0.25, 1.0, 1.0),
    "corner": (1.0, 0.80, 0.04, 1.0),
    "spawn": (1.0, 1.0, 1.0, 1.0),
    "center": (0.15, 0.95, 0.15, 1.0),
}


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


def gazebo_to_unreal_cm(xyz_m: list[float]) -> list[float]:
    x_m, y_m, z_m = xyz_m
    return [x_m * 100.0, -y_m * 100.0, z_m * 100.0]


def midpoint(a: list[float], b: list[float]) -> list[float]:
    return [(a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5, (a[2] + b[2]) * 0.5]


def make_segment(segment_id: str, start: list[float], end: list[float], color_key: str, role: str) -> dict[str, Any]:
    return {
        "id": segment_id,
        "role": role,
        "start_gazebo_m": start,
        "end_gazebo_m": end,
        "start_unreal_cm": gazebo_to_unreal_cm(start),
        "end_unreal_cm": gazebo_to_unreal_cm(end),
        "rgba": COLORS[color_key],
    }


def make_marker(marker_id: str, label: str, xyz_m: list[float], size_m: list[float], color_key: str) -> dict[str, Any]:
    return {
        "id": marker_id,
        "label": label,
        "shape": "box",
        "gazebo_m": xyz_m,
        "unreal_cm": gazebo_to_unreal_cm(xyz_m),
        "size_m": size_m,
        "size_unreal_cm": [v * 100.0 for v in size_m],
        "rgba": COLORS[color_key],
    }


def derive_wall_center_boundary(scene_truth: dict[str, Any]) -> dict[str, Any]:
    proxies = scene_truth.get("collision_proxies", [])
    if not isinstance(proxies, list):
        raise ValueError("scene_truth.collision_proxies must be a list")
    selected = []
    for proxy in proxies:
        if not isinstance(proxy, dict):
            continue
        text = " ".join([
            str(proxy.get("source_actor", "")),
            str(proxy.get("source_mesh", "")),
            str(proxy.get("semantic_type", "")),
        ]).lower()
        if ("wall" in text or "fence" in text) and proxy.get("min_m") and proxy.get("max_m"):
            selected.append(proxy)
    if not selected:
        raise ValueError("no wall/fence collision proxies found")

    min_x = min(float(item["min_m"][0]) for item in selected)
    max_x = max(float(item["max_m"][0]) for item in selected)
    min_y = min(float(item["min_m"][1]) for item in selected)
    max_y = max(float(item["max_m"][1]) for item in selected)
    center_x = (min_x + max_x) * 0.5
    center_y = (min_y + max_y) * 0.5
    return {
        "basis": "wall_fence_collision_truth_aabb_centerline_candidate",
        "source": rel(DEFAULT_SCENE_TRUTH),
        "selected_proxy_count": len(selected),
        "min_x_m": min_x,
        "max_x_m": max_x,
        "min_y_m": min_y,
        "max_y_m": max_y,
        "size_x_m": max_x - min_x,
        "size_y_m": max_y - min_y,
        "center_x_m": center_x,
        "center_y_m": center_y,
        "policy": "Review-only candidate derived from wall/fence collision proxies. Promote to runtime envelope only after UE visual acceptance."
    }


def build_contract(envelope: dict[str, Any], result_dir: Path, boundary_override: dict[str, Any] | None = None) -> dict[str, Any]:
    boundary = boundary_override or envelope["exploration_boundary"]
    z_policy = envelope["z_policy"]
    min_x = float(boundary["min_x_m"])
    max_x = float(boundary["max_x_m"])
    min_y = float(boundary["min_y_m"])
    max_y = float(boundary["max_y_m"])
    center_x = float(boundary["center_x_m"])
    center_y = float(boundary["center_y_m"])
    floor_z = float(z_policy["pointcloud_min_world_z_m"])
    review_z = floor_z + 0.08
    top_z = float(z_policy["fixed_z_m"])

    corners = {
        "south_west": [min_x, min_y, review_z],
        "south_east": [max_x, min_y, review_z],
        "north_east": [max_x, max_y, review_z],
        "north_west": [min_x, max_y, review_z],
    }
    top_corners = {
        key: [value[0], value[1], top_z]
        for key, value in corners.items()
    }

    segments = [
        make_segment("floor_south_edge_min_y", corners["south_west"], corners["south_east"], "boundary", "floor_boundary"),
        make_segment("floor_east_edge_max_x", corners["south_east"], corners["north_east"], "boundary", "floor_boundary"),
        make_segment("floor_north_edge_max_y", corners["north_east"], corners["north_west"], "boundary", "floor_boundary"),
        make_segment("floor_west_edge_min_x", corners["north_west"], corners["south_west"], "boundary", "floor_boundary"),
        make_segment("top_south_edge_min_y", top_corners["south_west"], top_corners["south_east"], "top_boundary", "z_band_top_reference"),
        make_segment("top_east_edge_max_x", top_corners["south_east"], top_corners["north_east"], "top_boundary", "z_band_top_reference"),
        make_segment("top_north_edge_max_y", top_corners["north_east"], top_corners["north_west"], "top_boundary", "z_band_top_reference"),
        make_segment("top_west_edge_min_x", top_corners["north_west"], top_corners["south_west"], "top_boundary", "z_band_top_reference"),
    ]

    marker_size = [4.0, 4.0, 4.0]
    markers = [
        make_marker(f"corner_{name}", f"boundary corner {name}", [xyz[0], xyz[1], review_z + 2.0], marker_size, "corner")
        for name, xyz in corners.items()
    ]
    for spawn in envelope.get("spawn_points", []):
        markers.append(make_marker(
            f"spawn_uav{spawn['uav']}",
            f"uav{spawn['uav']} spawn",
            [float(spawn["x"]), float(spawn["y"]), review_z + 1.0],
            [2.0, 2.0, 2.0],
            "spawn",
        ))
    markers.append(make_marker(
        "boundary_center",
        "exploration boundary center",
        [center_x, center_y, review_z + 1.0],
        [3.0, 3.0, 3.0],
        "center",
    ))

    contract_path = result_dir / "FACTORY_L2_EXPLORATION_BOUNDARY_REVIEW.json"
    segments_csv = result_dir / "factory_l2_exploration_boundary_segments.csv"
    markers_csv = result_dir / "factory_l2_exploration_boundary_markers.csv"
    ue_script = result_dir / "ue" / "place_factory_l2_exploration_boundary.py"

    return {
        "schema": "mosim.factory_l2_exploration_boundary_review.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "review_required",
        "purpose": [
            "Let the user visually audit the Factory L2 exploration boundary in UE before full-map exploration.",
            "Confirm the selected boundary includes the intended supported floor area and excludes unsupported exterior/no-floor regions.",
            "Confirm large-scale coordinate mapping still looks aligned after the smaller calibration rig passed."
        ],
        "claim_boundary": [
            "Source/static visual-review geometry only.",
            "This does not prove full-map exploration, planner coverage, localization, controller performance, or UE runtime bridge correctness.",
            "Do not use this packet to command exploration until the user accepts or adjusts the boundary."
        ],
        "coordinate_contract": envelope["coordinate_contract"],
        "source_envelope": rel(DEFAULT_ENVELOPE),
        "world_path": envelope.get("world_path"),
        "gazebo_model_path": envelope.get("gazebo_model_path"),
        "boundary": boundary,
        "original_envelope_boundary": envelope["exploration_boundary"],
        "z_policy": z_policy,
        "review_geometry_policy": {
            "floor_boundary_z_m": review_z,
            "top_reference_z_m": top_z,
            "floor_boundary_color": "red",
            "top_reference_color": "blue",
            "corner_marker_color": "yellow",
            "spawn_marker_color": "white",
            "center_marker_color": "green",
            "line_thickness_cm": 120.0,
            "why_thick_lines": "The boundary is about 1196 m by 531 m, so thin debug lines are not reliable for UE visual review."
        },
        "segments": segments,
        "markers": markers,
        "review_protocol": [
            "Open the Factory UE level and run the generated UE Python script.",
            "User reviews UE only: the red rectangle should frame the intended full exploration floor boundary.",
            "White spawn markers must be inside the rectangle; yellow corner blocks must appear at the four extreme boundary corners.",
            "Reject if the rectangle is mirrored, shifted, obviously too large/small, excludes intended floor, includes unsupported no-floor area, or disagrees with the accepted Factory scene.",
            "After acceptance, use this boundary as the runtime exploration envelope; if rejected, update the envelope before exploration."
        ],
        "outputs": {
            "contract": rel(contract_path),
            "segments_csv": rel(segments_csv),
            "markers_csv": rel(markers_csv),
            "ue_placement_script": rel(ue_script),
        },
        "open_commands": {
            "unreal_python_script": rel(ue_script),
        },
    }


def write_csvs(result_dir: Path, contract: dict[str, Any]) -> None:
    segment_path = result_dir / "factory_l2_exploration_boundary_segments.csv"
    with segment_path.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "id", "plane", "axis_color",
            "start_gazebo_x_m", "start_gazebo_y_m", "start_gazebo_z_m",
            "end_gazebo_x_m", "end_gazebo_y_m", "end_gazebo_z_m",
            "start_unreal_x_cm", "start_unreal_y_cm", "start_unreal_z_cm",
            "end_unreal_x_cm", "end_unreal_y_cm", "end_unreal_z_cm",
            "rgba_r", "rgba_g", "rgba_b", "rgba_a",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for segment in contract["segments"]:
            sg = segment["start_gazebo_m"]
            eg = segment["end_gazebo_m"]
            su = segment["start_unreal_cm"]
            eu = segment["end_unreal_cm"]
            r, g, b, a = segment["rgba"]
            writer.writerow({
                "id": segment["id"],
                "plane": segment["role"],
                "axis_color": segment["role"],
                "start_gazebo_x_m": sg[0],
                "start_gazebo_y_m": sg[1],
                "start_gazebo_z_m": sg[2],
                "end_gazebo_x_m": eg[0],
                "end_gazebo_y_m": eg[1],
                "end_gazebo_z_m": eg[2],
                "start_unreal_x_cm": su[0],
                "start_unreal_y_cm": su[1],
                "start_unreal_z_cm": su[2],
                "end_unreal_x_cm": eu[0],
                "end_unreal_y_cm": eu[1],
                "end_unreal_z_cm": eu[2],
                "rgba_r": r,
                "rgba_g": g,
                "rgba_b": b,
                "rgba_a": a,
            })

    marker_path = result_dir / "factory_l2_exploration_boundary_markers.csv"
    with marker_path.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "id", "label", "shape", "offset_x_m", "offset_y_m", "offset_z_m",
            "gazebo_x_m", "gazebo_y_m", "gazebo_z_m",
            "unreal_x_cm", "unreal_y_cm", "unreal_z_cm",
            "size_x_m", "size_y_m", "size_z_m",
            "rgba_r", "rgba_g", "rgba_b", "rgba_a",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for marker in contract["markers"]:
            gm = marker["gazebo_m"]
            uc = marker["unreal_cm"]
            sm = marker["size_m"]
            r, g, b, a = marker["rgba"]
            writer.writerow({
                "id": marker["id"],
                "label": marker["label"],
                "shape": marker["shape"],
                "offset_x_m": 0.0,
                "offset_y_m": 0.0,
                "offset_z_m": 0.0,
                "gazebo_x_m": gm[0],
                "gazebo_y_m": gm[1],
                "gazebo_z_m": gm[2],
                "unreal_x_cm": uc[0],
                "unreal_y_cm": uc[1],
                "unreal_z_cm": uc[2],
                "size_x_m": sm[0],
                "size_y_m": sm[1],
                "size_z_m": sm[2],
                "rgba_r": r,
                "rgba_g": g,
                "rgba_b": b,
                "rgba_a": a,
            })


def write_ue_python(path: Path, contract_rel: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'''# Unreal Editor Python helper generated by MoSim.
# Run inside Unreal Editor after opening the Factory level.
# It creates visual-only boundary review geometry from the Factory L2
# exploration envelope. It does not affect Gazebo, ROS, planners, or control.

import json
import math
from pathlib import Path

import unreal

CONTRACT = Path(r"C:/Users/HP/Desktop/MoSim/{contract_rel}")
FOLDER = "MoSim/ExplorationBoundaryReview"
CYLINDER = "/Engine/BasicShapes/Cylinder.Cylinder"
CUBE = "/Engine/BasicShapes/Cube.Cube"
BASIC_MATERIAL = "/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"


def midpoint(a, b):
    return [(a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5, (a[2] + b[2]) * 0.5]


def length(a, b):
    return math.sqrt(sum((b[i] - a[i]) ** 2 for i in range(3)))


def try_apply_color(actor, rgba):
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    material = unreal.load_asset(BASIC_MATERIAL)
    if component is None or material is None:
        return
    try:
        dynamic = unreal.MaterialInstanceDynamic.create(material, actor)
        dynamic.set_vector_parameter_value("Color", unreal.LinearColor(rgba[0], rgba[1], rgba[2], rgba[3]))
        component.set_material(0, dynamic)
    except Exception as exc:
        print("MoSim boundary material color skipped:", actor.get_actor_label(), exc)


def spawn_mesh(asset_path, label, location, rotation, scale, rgba):
    asset = unreal.load_asset(asset_path)
    if asset is None:
        raise RuntimeError("Cannot load asset: " + asset_path)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_object(
        asset,
        unreal.Vector(location[0], location[1], location[2]),
        rotation,
    )
    actor.set_actor_label(label)
    actor.set_folder_path(FOLDER)
    actor.set_actor_scale3d(unreal.Vector(scale[0], scale[1], scale[2]))
    try_apply_color(actor, rgba)
    return actor


def main():
    payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
    thickness_cm = float(payload["review_geometry_policy"]["line_thickness_cm"])

    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_folder_path() == FOLDER:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    for segment in payload["segments"]:
        start = segment["start_unreal_cm"]
        end = segment["end_unreal_cm"]
        center = midpoint(start, end)
        delta = [end[i] - start[i] for i in range(3)]
        seg_len = max(length(start, end), thickness_cm)
        axis = max(range(3), key=lambda i: abs(delta[i]))
        if axis == 0:
            rotation = unreal.Rotator(0.0, 90.0, 0.0)
        elif axis == 1:
            rotation = unreal.Rotator(90.0, 0.0, 0.0)
        else:
            rotation = unreal.Rotator(0.0, 0.0, 0.0)
        spawn_mesh(
            CYLINDER,
            "MoSim_BoundaryLine_" + segment["id"],
            center,
            rotation,
            [thickness_cm / 100.0, thickness_cm / 100.0, seg_len / 100.0],
            segment["rgba"],
        )

    for marker in payload["markers"]:
        loc = marker["unreal_cm"]
        sx, sy, sz = marker["size_unreal_cm"]
        spawn_mesh(
            CUBE,
            "MoSim_BoundaryMarker_" + marker["id"],
            loc,
            unreal.Rotator(0.0, 0.0, 0.0),
            [sx / 100.0, sy / 100.0, sz / 100.0],
            marker["rgba"],
        )

    unreal.EditorLevelLibrary.save_current_level()
    print("MoSim Factory L2 exploration boundary actors generated from", CONTRACT)


main()
''',
        encoding="utf-8",
        newline="\n",
    )


def write_summary(result_dir: Path, contract: dict[str, Any]) -> None:
    boundary = contract["boundary"]
    summary = result_dir / "SUMMARY.md"
    summary.write_text(
        "\n".join([
            "# Factory L2 Exploration Boundary Review",
            "",
            "Status: `review_required`.",
            "",
            "This packet creates visual-only UE geometry for auditing the Factory L2 exploration boundary before full-map exploration.",
            "",
            "Boundary:",
            f"- X: `{boundary['min_x_m']}` to `{boundary['max_x_m']}` m",
            f"- Y: `{boundary['min_y_m']}` to `{boundary['max_y_m']}` m",
            f"- Size: `{boundary['size_x_m']}` x `{boundary['size_y_m']}` m",
            f"- Center: `({boundary['center_x_m']}, {boundary['center_y_m']})` m",
            "",
            "UE review protocol:",
            "- Red rectangle: selected floor exploration boundary.",
            "- Blue rectangle: fixed flight-height reference at the current Z policy.",
            "- Yellow blocks: four boundary corners.",
            "- White blocks: UAV spawn points.",
            "- Green block: boundary center.",
            "",
            "Acceptance is visual and user-owned: reject if this frame includes unsupported/no-floor areas, excludes intended flyable area, or appears mirrored/shifted/scaled incorrectly.",
            "",
            f"UE script: `{contract['outputs']['ue_placement_script']}`",
            f"Contract: `{contract['outputs']['contract']}`",
            "",
        ]),
        encoding="utf-8",
        newline="\n",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--envelope", type=Path, default=DEFAULT_ENVELOPE)
    parser.add_argument("--scene-truth", type=Path, default=DEFAULT_SCENE_TRUTH)
    parser.add_argument(
        "--boundary-mode",
        choices=["envelope", "wall-center"],
        default="envelope",
        help="Use existing envelope boundary or derive a review-only wall/fence centered candidate.",
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--tag", default=None, help="Optional result directory suffix.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    envelope_path = project_path(args.envelope)
    scene_truth_path = project_path(args.scene_truth)
    output_root = project_path(args.output_root)
    envelope = read_json(envelope_path)
    if envelope.get("schema") != "mosim.factory_l2_exploration_envelope.v1":
        raise SystemExit(f"unexpected envelope schema: {envelope.get('schema')}")
    boundary_override = None
    if args.boundary_mode == "wall-center":
        scene_truth = read_json(scene_truth_path)
        boundary_override = derive_wall_center_boundary(scene_truth)

    tag = args.tag or datetime.now().strftime("%Y%m%d_%H%M%S")
    result_dir = output_root / f"factory_l2_exploration_boundary_review_{tag}"
    result_dir.mkdir(parents=True, exist_ok=True)

    contract = build_contract(envelope, result_dir, boundary_override)
    contract["boundary_mode"] = args.boundary_mode
    contract_rel = contract["outputs"]["contract"]
    write_csvs(result_dir, contract)
    write_ue_python(result_dir / "ue" / "place_factory_l2_exploration_boundary.py", contract_rel)
    write_summary(result_dir, contract)
    (result_dir / "FACTORY_L2_EXPLORATION_BOUNDARY_REVIEW.json").write_text(
        json.dumps(contract, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(json.dumps({
        "status": "review_required",
        "result_dir": rel(result_dir),
        "contract": contract["outputs"]["contract"],
        "ue_script": contract["outputs"]["ue_placement_script"],
        "segments": len(contract["segments"]),
        "markers": len(contract["markers"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
