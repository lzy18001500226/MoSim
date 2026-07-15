#!/usr/bin/env python3
"""Build Factory L2 UE/Gazebo calibration-rig review artifacts.

This is a source/static review helper. It creates one coordinate contract and
derives all review surfaces from that contract:

- JSON contract and CSV line segments;
- Unreal Python placement script for three rectangular line frames;
- Gazebo Classic visual-only overlay world;
- RViz config and a ROS1 MarkerArray publisher script.

It does not start UE, Gazebo, ROS, PX4, MAVROS, planners, or controllers.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENE_PROFILE = ROOT / "Config/gazebo/scene_profiles/factory_l2_static_sunray_scene_clean_candidate.json"
DEFAULT_CLEAN_MANIFEST = ROOT / "Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/MANIFEST.json"
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"


AXIS_COLORS = {
    "x": (1.0, 0.05, 0.03, 1.0),
    "y": (0.05, 0.85, 0.08, 1.0),
    "z": (0.08, 0.25, 1.0, 1.0),
    "xy": (1.0, 0.8, 0.05, 1.0),
    "xz": (1.0, 0.2, 0.9, 1.0),
    "yz": (0.1, 0.9, 1.0, 1.0),
    "origin": (1.0, 1.0, 1.0, 1.0),
    "purple": (0.72, 0.20, 1.0, 1.0),
    "orange": (1.0, 0.45, 0.03, 1.0),
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


def unreal_to_gazebo_m(xyz_cm: list[float]) -> list[float]:
    x_cm, y_cm, z_cm = xyz_cm
    return [x_cm / 100.0, -y_cm / 100.0, z_cm / 100.0]


def add(a: list[float], b: list[float]) -> list[float]:
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]


def sub(a: list[float], b: list[float]) -> list[float]:
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def mul(a: list[float], scale: float) -> list[float]:
    return [a[0] * scale, a[1] * scale, a[2] * scale]


def norm(a: list[float]) -> float:
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def midpoint(a: list[float], b: list[float]) -> list[float]:
    return [(a[0] + b[0]) * 0.5, (a[1] + b[1]) * 0.5, (a[2] + b[2]) * 0.5]


def unit(a: list[float]) -> list[float]:
    length = norm(a)
    if length <= 1e-9:
        return [1.0, 0.0, 0.0]
    return [a[0] / length, a[1] / length, a[2] / length]


def material_element(rgba: tuple[float, float, float, float]) -> ET.Element:
    r, g, b, a = rgba
    material = ET.Element("material")
    ET.SubElement(material, "ambient").text = f"{r:.3f} {g:.3f} {b:.3f} {a:.3f}"
    ET.SubElement(material, "diffuse").text = f"{r:.3f} {g:.3f} {b:.3f} {a:.3f}"
    ET.SubElement(material, "emissive").text = f"{0.35 * r:.3f} {0.35 * g:.3f} {0.35 * b:.3f} {a:.3f}"
    return material


def box_pose_and_size(a: list[float], b: list[float], thickness: float) -> tuple[list[float], list[float]]:
    center = midpoint(a, b)
    delta = sub(b, a)
    length = max(norm(delta), thickness)
    axis = unit(delta)
    size = [thickness, thickness, thickness]
    major = max(range(3), key=lambda i: abs(axis[i]))
    size[major] = length
    return center, size


def append_box_segment(parent: ET.Element, segment: dict[str, Any], thickness: float) -> None:
    start = segment["start_gazebo_m"]
    end = segment["end_gazebo_m"]
    center, size = box_pose_and_size(start, end, thickness)
    model = ET.SubElement(parent, "model", {"name": f"calib_{segment['id']}"})
    ET.SubElement(model, "static").text = "true"
    ET.SubElement(model, "pose").text = f"{center[0]:.6f} {center[1]:.6f} {center[2]:.6f} 0 0 0"
    link = ET.SubElement(model, "link", {"name": "link"})
    visual = ET.SubElement(link, "visual", {"name": "visual"})
    geometry = ET.SubElement(visual, "geometry")
    box = ET.SubElement(geometry, "box")
    ET.SubElement(box, "size").text = f"{size[0]:.4f} {size[1]:.4f} {size[2]:.4f}"
    visual.append(material_element(tuple(segment["rgba"])))


def append_box_marker(parent: ET.Element, marker: dict[str, Any]) -> None:
    x, y, z = marker["gazebo_m"]
    sx, sy, sz = marker["size_m"]
    model = ET.SubElement(parent, "model", {"name": f"calib_{marker['id']}"})
    ET.SubElement(model, "static").text = "true"
    ET.SubElement(model, "pose").text = f"{x:.6f} {y:.6f} {z:.6f} 0 0 0"
    link = ET.SubElement(model, "link", {"name": "link"})
    visual = ET.SubElement(link, "visual", {"name": "visual"})
    geometry = ET.SubElement(visual, "geometry")
    box = ET.SubElement(geometry, "box")
    ET.SubElement(box, "size").text = f"{sx:.4f} {sy:.4f} {sz:.4f}"
    visual.append(material_element(tuple(marker["rgba"])))


def make_segments(origin: list[float], x_len: float, y_len: float, z_len: float) -> list[dict[str, Any]]:
    ox, oy, oz = origin
    x0, x1 = ox - x_len * 0.5, ox + x_len * 0.5
    y0, y1 = oy - y_len * 0.5, oy + y_len * 0.5
    z0, z1 = oz, oz + z_len
    rects = {
        "xy": [
            ([x0, y0, oz], [x1, y0, oz], "x", "xy_bottom_x"),
            ([x1, y0, oz], [x1, y1, oz], "y", "xy_pos_y_edge"),
            ([x1, y1, oz], [x0, y1, oz], "x", "xy_top_x"),
            ([x0, y1, oz], [x0, y0, oz], "y", "xy_neg_x_edge"),
        ],
        "xz": [
            ([x0, oy, z0], [x1, oy, z0], "x", "xz_bottom_x"),
            ([x1, oy, z0], [x1, oy, z1], "z", "xz_pos_z_edge"),
            ([x1, oy, z1], [x0, oy, z1], "x", "xz_top_x"),
            ([x0, oy, z1], [x0, oy, z0], "z", "xz_neg_x_edge"),
        ],
        "yz": [
            ([ox, y0, z0], [ox, y1, z0], "y", "yz_bottom_y"),
            ([ox, y1, z0], [ox, y1, z1], "z", "yz_pos_z_edge"),
            ([ox, y1, z1], [ox, y0, z1], "y", "yz_top_y"),
            ([ox, y0, z1], [ox, y0, z0], "z", "yz_neg_y_edge"),
        ],
    }
    directional = [
        ([x1, oy, oz], [x1 + 0.9, oy, oz], "x", "tick_positive_x_long"),
        ([ox, y1, oz], [ox, y1 + 0.65, oz], "y", "tick_positive_y_mid"),
        ([ox, oy, z1], [ox, oy, z1 + 0.45], "z", "tick_positive_z_short"),
        ([x0, oy, oz], [x0 - 0.35, oy, oz], "x", "tick_negative_x_short"),
    ]
    segments: list[dict[str, Any]] = []
    for plane, entries in rects.items():
        for start, end, axis, name in entries:
            segments.append({
                "id": f"{plane}_{name}",
                "plane": plane,
                "axis_color": axis,
                "start_gazebo_m": start,
                "end_gazebo_m": end,
                "start_unreal_cm": gazebo_to_unreal_cm(start),
                "end_unreal_cm": gazebo_to_unreal_cm(end),
                "rgba": AXIS_COLORS[axis],
            })
    for start, end, axis, name in directional:
        segments.append({
            "id": name,
            "plane": "directional_tick",
            "axis_color": axis,
            "start_gazebo_m": start,
            "end_gazebo_m": end,
            "start_unreal_cm": gazebo_to_unreal_cm(start),
            "end_unreal_cm": gazebo_to_unreal_cm(end),
            "rgba": AXIS_COLORS[axis],
        })
    return segments


def make_calibration_markers(origin: list[float]) -> list[dict[str, Any]]:
    """Create non-symmetric visible markers for map-level registration.

    These markers are intentionally not tied to Factory walls, doors, or pillars.
    They are authored in the Gazebo/MWORKS frame and transformed to UE from the
    same contract, so a mirror, axis swap, scale error, or origin offset becomes
    visually obvious without relying on ambiguous building features.
    """

    specs = [
        {
            "id": "rig_origin_white_cube",
            "label": "origin / uav1 anchor",
            "offset_m": [0.0, 0.0, 0.0],
            "shape": "box",
            "size_m": [0.35, 0.35, 0.35],
            "rgba": AXIS_COLORS["origin"],
        },
        {
            "id": "rig_x_red_cube_1m",
            "label": "+X 1m marker",
            "offset_m": [1.0, 0.0, 0.0],
            "shape": "box",
            "size_m": [0.28, 0.28, 0.28],
            "rgba": AXIS_COLORS["x"],
        },
        {
            "id": "rig_y_green_cube_2m",
            "label": "+Y 2m marker",
            "offset_m": [0.0, 2.0, 0.0],
            "shape": "box",
            "size_m": [0.42, 0.42, 0.42],
            "rgba": AXIS_COLORS["y"],
        },
        {
            "id": "rig_z_blue_cube_1m",
            "label": "+Z 1m marker",
            "offset_m": [0.0, 0.0, 1.0],
            "shape": "box",
            "size_m": [0.30, 0.30, 0.30],
            "rgba": AXIS_COLORS["z"],
        },
        {
            "id": "rig_xyz_purple_cube_asymmetric",
            "label": "asymmetric 2m/1m/0.5m marker",
            "offset_m": [2.0, 1.0, 0.5],
            "shape": "box",
            "size_m": [0.38, 0.26, 0.52],
            "rgba": AXIS_COLORS["purple"],
        },
        {
            "id": "rig_neg_y_orange_cube_guard",
            "label": "-Y 1m sign guard",
            "offset_m": [-1.0, -1.0, 0.25],
            "shape": "box",
            "size_m": [0.26, 0.50, 0.34],
            "rgba": AXIS_COLORS["orange"],
        },
    ]
    markers: list[dict[str, Any]] = []
    for spec in specs:
        gazebo_m = add(origin, spec["offset_m"])
        size_m = [float(value) for value in spec["size_m"]]
        markers.append({
            "id": spec["id"],
            "label": spec["label"],
            "shape": spec["shape"],
            "offset_m": spec["offset_m"],
            "gazebo_m": gazebo_m,
            "unreal_cm": gazebo_to_unreal_cm(gazebo_m),
            "size_m": size_m,
            "size_unreal_cm": [value * 100.0 for value in size_m],
            "rgba": spec["rgba"],
        })
    return markers


def write_segments_csv(path: Path, segments: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "id", "plane", "axis_color",
        "start_gazebo_x_m", "start_gazebo_y_m", "start_gazebo_z_m",
        "end_gazebo_x_m", "end_gazebo_y_m", "end_gazebo_z_m",
        "start_unreal_x_cm", "start_unreal_y_cm", "start_unreal_z_cm",
        "end_unreal_x_cm", "end_unreal_y_cm", "end_unreal_z_cm",
        "rgba_r", "rgba_g", "rgba_b", "rgba_a",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for segment in segments:
            sg, eg = segment["start_gazebo_m"], segment["end_gazebo_m"]
            su, eu = segment["start_unreal_cm"], segment["end_unreal_cm"]
            r, g, b, a = segment["rgba"]
            writer.writerow({
                "id": segment["id"],
                "plane": segment["plane"],
                "axis_color": segment["axis_color"],
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


def write_calibration_markers_csv(path: Path, markers: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "id", "label", "shape",
        "offset_x_m", "offset_y_m", "offset_z_m",
        "gazebo_x_m", "gazebo_y_m", "gazebo_z_m",
        "unreal_x_cm", "unreal_y_cm", "unreal_z_cm",
        "size_x_m", "size_y_m", "size_z_m",
        "rgba_r", "rgba_g", "rgba_b", "rgba_a",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for marker in markers:
            gm = marker["gazebo_m"]
            uc = marker["unreal_cm"]
            offset = marker["offset_m"]
            size = marker["size_m"]
            r, g, b, a = marker["rgba"]
            writer.writerow({
                "id": marker["id"],
                "label": marker["label"],
                "shape": marker["shape"],
                "offset_x_m": offset[0],
                "offset_y_m": offset[1],
                "offset_z_m": offset[2],
                "gazebo_x_m": gm[0],
                "gazebo_y_m": gm[1],
                "gazebo_z_m": gm[2],
                "unreal_x_cm": uc[0],
                "unreal_y_cm": uc[1],
                "unreal_z_cm": uc[2],
                "size_x_m": size[0],
                "size_y_m": size[1],
                "size_z_m": size[2],
                "rgba_r": r,
                "rgba_g": g,
                "rgba_b": b,
                "rgba_a": a,
            })


def default_spawns(scene_profile: dict[str, Any]) -> list[dict[str, float]]:
    spawns = scene_profile.get("default_spawn_points", [])
    out: list[dict[str, float]] = []
    if isinstance(spawns, list):
        for spawn in spawns:
            if not isinstance(spawn, dict):
                continue
            out.append({
                "uav": int(spawn.get("uav", len(out) + 1)),
                "x": float(spawn.get("x", 0.0)),
                "y": float(spawn.get("y", 0.0)),
                "z": max(0.2, float(spawn.get("z", 0.2))),
                "yaw": float(spawn.get("yaw", 0.0)),
            })
    return sorted(out, key=lambda row: row["uav"])


def marker_color_for_uav(uav: int) -> tuple[float, float, float, float]:
    if uav == 1:
        return AXIS_COLORS["origin"]
    if uav == 2:
        return AXIS_COLORS["xy"]
    if uav == 3:
        return AXIS_COLORS["yz"]
    return (0.85, 0.85, 0.85, 1.0)


def make_spawn_markers(scene_profile: dict[str, Any], origin: list[float]) -> list[dict[str, Any]]:
    spawns = default_spawns(scene_profile)
    if not spawns:
        spawns = [{"uav": 1, "x": origin[0], "y": origin[1], "z": origin[2], "yaw": 0.0}]

    base = next((spawn for spawn in spawns if int(spawn["uav"]) == 1), spawns[0])
    markers: list[dict[str, Any]] = []
    for spawn in spawns:
        shifted = [
            origin[0] + (spawn["x"] - base["x"]),
            origin[1] + (spawn["y"] - base["y"]),
            origin[2] + (spawn["z"] - base["z"]),
        ]
        uav = int(spawn["uav"])
        markers.append({
            "id": f"uav{uav}_spawn",
            "uav": uav,
            "source_spawn_gazebo_m": [spawn["x"], spawn["y"], spawn["z"]],
            "gazebo_m": shifted,
            "unreal_cm": gazebo_to_unreal_cm(shifted),
            "yaw_rad": spawn["yaw"],
            "rgba": marker_color_for_uav(uav),
            "radius_cm": 12.0 if uav == 1 else 10.0,
        })
    return markers


def write_spawn_markers_csv(path: Path, markers: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "id", "gazebo_x_m", "gazebo_y_m", "gazebo_z_m",
        "unreal_x_cm", "unreal_y_cm", "unreal_z_cm",
        "rgba_r", "rgba_g", "rgba_b", "rgba_a", "radius_cm",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for marker in markers:
            gm = marker["gazebo_m"]
            uc = marker["unreal_cm"]
            r, g, b, a = marker["rgba"]
            writer.writerow({
                "id": marker["id"],
                "gazebo_x_m": gm[0],
                "gazebo_y_m": gm[1],
                "gazebo_z_m": gm[2],
                "unreal_x_cm": uc[0],
                "unreal_y_cm": uc[1],
                "unreal_z_cm": uc[2],
                "rgba_r": r,
                "rgba_g": g,
                "rgba_b": b,
                "rgba_a": a,
                "radius_cm": marker["radius_cm"],
            })


def write_ue_python(path: Path, contract_rel: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'''# Unreal Editor Python helper generated by MoSim.
# Run inside Unreal Editor after opening the Factory level.
# It creates visual-only debug line cylinders and asymmetric calibration blocks
# from the same coordinate contract used by Gazebo and RViz.

import json
import math
from pathlib import Path

import unreal

CONTRACT = Path(r"C:/Users/HP/Desktop/MoSim/{contract_rel}")
FOLDER = "MoSim/CoordinateCalibration"
CYLINDER = "/Engine/BasicShapes/Cylinder.Cylinder"
CUBE = "/Engine/BasicShapes/Cube.Cube"
BASIC_MATERIAL = "/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"
THICKNESS_CM = 8.0


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
        print("MoSim calibration material color skipped:", actor.get_actor_label(), exc)


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

    # Remove previous calibration actors generated by this script.
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_folder_path() == FOLDER:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    for segment in payload["segments"]:
        start = segment["start_unreal_cm"]
        end = segment["end_unreal_cm"]
        center = midpoint(start, end)
        delta = [end[i] - start[i] for i in range(3)]
        seg_len = max(length(start, end), THICKNESS_CM)

        # The basic cylinder is vertical by default. We only use this helper
        # for axis-aligned line frames, so select rotation/scale by dominant
        # segment direction instead of arbitrary quaternion math.
        axis = max(range(3), key=lambda i: abs(delta[i]))
        if axis == 0:
            rotation = unreal.Rotator(0.0, 90.0, 0.0)
        elif axis == 1:
            rotation = unreal.Rotator(90.0, 0.0, 0.0)
        else:
            rotation = unreal.Rotator(0.0, 0.0, 0.0)
        spawn_mesh(
            CYLINDER,
            "MoSim_CalibLine_" + segment["id"],
            center,
            rotation,
            [THICKNESS_CM / 100.0, THICKNESS_CM / 100.0, seg_len / 100.0],
            segment["rgba"],
        )

    for marker in payload.get("calibration_markers", []):
        loc = marker["unreal_cm"]
        sx, sy, sz = marker["size_unreal_cm"]
        spawn_mesh(
            CUBE,
            "MoSim_CalibBlock_" + marker["id"],
            loc,
            unreal.Rotator(0.0, 0.0, 0.0),
            [sx / 100.0, sy / 100.0, sz / 100.0],
            marker["rgba"],
        )

    unreal.EditorLevelLibrary.save_current_level()
    print("MoSim calibration rig actors generated from", CONTRACT)


main()
''',
        encoding="utf-8",
        newline="\n",
    )


def write_rviz_publisher(path: Path, contract_rel: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'''#!/usr/bin/env python3
"""Publish Factory L2 calibration rig as RViz MarkerArray."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
DEFAULT_CONTRACT = ROOT / "{contract_rel}"


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract-json", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--marker-topic", default="/mosim/factory_l2/calibration_frame_markers")
    parser.add_argument("--frame-id", default="camera_init")
    parser.add_argument("--publish-hz", type=float, default=2.0)
    parser.add_argument("--line-width-m", type=float, default=0.10)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    path = args.contract_json if args.contract_json.is_absolute() else ROOT / args.contract_json
    payload = json.loads(path.read_text(encoding="utf-8"))
    if args.dry_run:
        print(json.dumps({{
            "status": "dry_run_passed",
            "segment_count": len(payload["segments"]),
            "calibration_marker_count": len(payload.get("calibration_markers", [])),
        }}, indent=2))
        return 0

    import rospy
    from geometry_msgs.msg import Point
    from visualization_msgs.msg import Marker, MarkerArray

    rospy.init_node("mosim_factory_l2_calibration_frame_markers", anonymous=False)
    publisher = rospy.Publisher(args.marker_topic, MarkerArray, queue_size=1, latch=True)
    rate = rospy.Rate(max(0.1, args.publish_hz))
    while not rospy.is_shutdown():
        stamp = rospy.Time.now()
        markers = MarkerArray()
        for index, segment in enumerate(payload["segments"]):
            marker = Marker()
            marker.header.frame_id = args.frame_id
            marker.header.stamp = stamp
            marker.ns = "factory_l2_calibration_frame"
            marker.id = index
            marker.type = Marker.LINE_LIST
            marker.action = Marker.ADD
            marker.scale.x = args.line_width_m
            r, g, b, a = segment["rgba"]
            marker.color.r = r
            marker.color.g = g
            marker.color.b = b
            marker.color.a = a
            s = segment["start_gazebo_m"]
            e = segment["end_gazebo_m"]
            marker.points = [Point(x=s[0], y=s[1], z=s[2]), Point(x=e[0], y=e[1], z=e[2])]
            markers.markers.append(marker)
        base_id = 1000
        for index, block in enumerate(payload.get("calibration_markers", [])):
            marker = Marker()
            marker.header.frame_id = args.frame_id
            marker.header.stamp = stamp
            marker.ns = "factory_l2_calibration_blocks"
            marker.id = base_id + index
            marker.type = Marker.CUBE
            marker.action = Marker.ADD
            x, y, z = block["gazebo_m"]
            marker.pose.position.x = x
            marker.pose.position.y = y
            marker.pose.position.z = z
            marker.pose.orientation.w = 1.0
            sx, sy, sz = block["size_m"]
            marker.scale.x = sx
            marker.scale.y = sy
            marker.scale.z = sz
            r, g, b, a = block["rgba"]
            marker.color.r = r
            marker.color.g = g
            marker.color.b = b
            marker.color.a = a
            markers.markers.append(marker)
        publisher.publish(markers)
        rate.sleep()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''',
        encoding="utf-8",
        newline="\n",
    )


def write_rviz_config(path: Path, marker_topic: str, fixed_frame: str, focal_point: list[float]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join([
            "Panels:",
            "  - Class: rviz/Displays",
            "    Name: Displays",
            "  - Class: rviz/Views",
            "    Name: Views",
            "Visualization Manager:",
            "  Class: \"\"",
            "  Displays:",
            "    - Alpha: 0.45",
            "      Cell Size: 1",
            "      Class: rviz/Grid",
            "      Color: 160; 160; 164",
            "      Enabled: true",
            "      Name: Grid",
            "      Plane: XY",
            "      Plane Cell Count: 80",
            f"      Reference Frame: {fixed_frame}",
            "      Value: true",
            "    - Class: rviz/MarkerArray",
            "      Enabled: true",
            f"      Marker Topic: {marker_topic}",
            "      Name: Factory L2 Calibration Frames",
            "      Queue Size: 10",
            "      Value: true",
            "  Enabled: true",
            "  Global Options:",
            "    Background Color: 35; 35; 35",
            "    Default Light: true",
            f"    Fixed Frame: {fixed_frame}",
            "    Frame Rate: 30",
            "  Name: root",
            "  Tools:",
            "    - Class: rviz/Interact",
            "    - Class: rviz/MoveCamera",
            "    - Class: rviz/Select",
            "    - Class: rviz/FocusCamera",
            "    - Class: rviz/Measure",
            "  Value: true",
            "  Views:",
            "    Current:",
            "      Class: rviz/Orbit",
            "      Distance: 18",
            "      Focal Point:",
            f"        X: {focal_point[0]:.3f}",
            f"        Y: {focal_point[1]:.3f}",
            f"        Z: {focal_point[2]:.3f}",
            "      Name: Current View",
            "      Pitch: 0.58",
            "      Yaw: 0.78",
            "Window Geometry:",
            "  Height: 900",
            "  Width: 1400",
            "  X: 80",
            "  Y: 80",
            "",
        ]),
        encoding="utf-8",
        newline="\n",
    )


def write_gazebo_world(
    clean_world: Path,
    output_world: Path,
    segments: list[dict[str, Any]],
    calibration_markers: list[dict[str, Any]],
    thickness: float,
) -> None:
    tree = ET.parse(clean_world)
    root = tree.getroot()
    world = root.find("world")
    if world is None:
        raise ValueError(f"world element not found: {clean_world}")
    for segment in segments:
        append_box_segment(world, segment, thickness)
    for marker in calibration_markers:
        append_box_marker(world, marker)
    output_world.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_world, encoding="utf-8", xml_declaration=True)


def default_origin(scene_profile: dict[str, Any]) -> list[float]:
    spawns = scene_profile.get("default_spawn_points", [])
    if isinstance(spawns, list):
        for spawn in spawns:
            if not isinstance(spawn, dict):
                continue
            if int(spawn.get("uav", 0)) == 1:
                return [
                    float(spawn.get("x", 0.0)),
                    float(spawn.get("y", 0.0)),
                    max(0.2, float(spawn.get("z", 0.2))),
                ]
    return [0.0, 0.0, 0.2]


def parse_origin(value: str | None, fallback: list[float]) -> list[float]:
    if value is None:
        return fallback
    parts = [float(part.strip()) for part in value.split(",")]
    if len(parts) != 3:
        raise SystemExit("--origin-m must have exactly three comma-separated values")
    return parts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-profile", type=Path, default=DEFAULT_SCENE_PROFILE)
    parser.add_argument("--clean-manifest", type=Path, default=DEFAULT_CLEAN_MANIFEST)
    parser.add_argument("--result-dir", type=Path)
    parser.add_argument("--origin-m", help="Gazebo/MWORKS origin for the calibration frame, x,y,z")
    parser.add_argument("--x-len-m", type=float, default=5.0)
    parser.add_argument("--y-len-m", type=float, default=3.0)
    parser.add_argument("--z-len-m", type=float, default=2.0)
    parser.add_argument("--gazebo-line-thickness-m", type=float, default=0.08)
    parser.add_argument("--marker-topic", default="/mosim/factory_l2/calibration_frame_markers")
    parser.add_argument("--fixed-frame", default="camera_init")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scene_profile_path = project_path(args.scene_profile)
    clean_manifest_path = project_path(args.clean_manifest)
    scene_profile = read_json(scene_profile_path)
    clean_manifest = read_json(clean_manifest_path)
    result_dir = (
        project_path(args.result_dir)
        if args.result_dir is not None
        else DEFAULT_OUTPUT_ROOT / f"factory_l2_calibration_frame_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    result_dir.mkdir(parents=True, exist_ok=True)

    origin = parse_origin(args.origin_m, default_origin(scene_profile))
    segments = make_segments(origin, args.x_len_m, args.y_len_m, args.z_len_m)
    calibration_markers = make_calibration_markers(origin)
    spawn_markers = make_spawn_markers(scene_profile, origin)
    clean_world = project_path(str(clean_manifest["review_world_path"]))

    contract_path = result_dir / "FACTORY_L2_CALIBRATION_FRAME_CONTRACT.json"
    segments_csv = result_dir / "factory_l2_calibration_segments.csv"
    calibration_markers_csv = result_dir / "factory_l2_calibration_markers.csv"
    spawn_markers_csv = result_dir / "factory_l2_spawn_markers.csv"
    gazebo_world = result_dir / "worlds" / "factoryenvironmentcollect_l2_static_calibration_review.sdf"
    rviz_config = result_dir / "rviz" / "factory_l2_calibration_frames.rviz"
    ue_script = result_dir / "ue" / "place_factory_l2_calibration_frames.py"
    rviz_publisher = result_dir / "ros" / "publish_factory_l2_calibration_frames.py"

    contract = {
        "schema": "mosim.factory_l2_calibration_frame_contract.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "review_required",
        "calibration_purpose": [
            "Verify UE/Gazebo origin alignment near the UAV spawn frame.",
            "Verify X/Y/Z axis mapping and sign, especially Gazebo Y = -UE Y.",
            "Verify UE centimeter to Gazebo meter scale.",
            "Provide non-symmetric directional ticks so mirrored axes are visible.",
            "Use project-owned asymmetric calibration blocks instead of ambiguous Factory walls, doors, or pillars.",
        ],
        "claim_boundary": [
            "Source/static calibration geometry only.",
            "This does not prove UE runtime bridge, ROS/PX4/MAVROS runtime success, localization, planning, or controller performance.",
            "The generated Gazebo world is visual-only review support and must not become the runtime scene profile.",
            "Landmark review can remain auxiliary; this calibration frame is the primary F0.5 coordinate acceptance surface.",
        ],
        "coordinate_contract": {
            "gazebo_to_unreal": "UE_X_cm=gazebo_x_m*100; UE_Y_cm=-gazebo_y_m*100; UE_Z_cm=gazebo_z_m*100",
            "unreal_to_gazebo": "gazebo_x_m=UE_X_cm/100; gazebo_y_m=-UE_Y_cm/100; gazebo_z_m=UE_Z_cm/100",
            "gazebo_frame": "Gazebo world / MWORKS world, meters, z-up",
            "unreal_frame": "UE world, centimeters",
        },
        "origin_gazebo_m": origin,
        "origin_unreal_cm": gazebo_to_unreal_cm(origin),
        "dimensions_m": {
            "xy_rect_x_len": args.x_len_m,
            "xy_rect_y_len": args.y_len_m,
            "xz_rect_x_len": args.x_len_m,
            "xz_rect_z_len": args.z_len_m,
            "yz_rect_y_len": args.y_len_m,
            "yz_rect_z_len": args.z_len_m,
        },
        "axis_colors": AXIS_COLORS,
        "inputs": {
            "scene_profile": rel(scene_profile_path),
            "clean_manifest": rel(clean_manifest_path),
            "clean_world": rel(clean_world),
        },
        "outputs": {
            "contract": rel(contract_path),
            "segments_csv": rel(segments_csv),
            "calibration_markers_csv": rel(calibration_markers_csv),
            "spawn_markers_csv": rel(spawn_markers_csv),
            "gazebo_calibration_world": rel(gazebo_world),
            "rviz_config": rel(rviz_config),
            "ue_placement_script": rel(ue_script),
            "rviz_marker_publisher": rel(rviz_publisher),
        },
        "review_protocol": [
            "Agent performs backend checks on the Gazebo/RViz/log source data: coordinate contract, segment endpoints, SDF validity, runtime trajectory source, frame IDs, units, and the documented Y sign flip.",
            "User performs visual acceptance in UE only: verify the calibration/audit frame, expected trajectory, and actual trajectory appear in the intended Factory area.",
            "User rejects the UE display if the UAV starts outside the audit frame, moves in a mirrored/reversed direction, exceeds the task audit frame unexpectedly, or shows obvious position/scale/attitude drift.",
            "Do not require the user to visually compare Gazebo and RViz unless the UE display is suspicious and the source of the mismatch must be isolated.",
            "After UE visual acceptance and backend source checks pass, promote the clean scene profile and rerun the smallest Factory runtime regression gates.",
        ],
        "open_commands": {
            "gazebo_calibration_review_wsl": (
                "cd /mnt/c/Users/HP/Desktop/MoSim && "
                "GAZEBO_MODEL_PATH=\"$PWD/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/models:$GAZEBO_MODEL_PATH\" "
                f"gazebo --verbose \"{rel(gazebo_world)}\""
            ),
            "rviz_marker_publisher_wsl": (
                "cd /mnt/c/Users/HP/Desktop/MoSim && source /opt/ros/noetic/setup.bash && "
                f"python3 \"{rel(rviz_publisher)}\" --contract-json \"{rel(contract_path)}\" "
                f"--marker-topic {args.marker_topic} --frame-id {args.fixed_frame}"
            ),
            "rviz_open_wsl": (
                "cd /mnt/c/Users/HP/Desktop/MoSim && source /opt/ros/noetic/setup.bash && "
                f"rviz -d \"{rel(rviz_config)}\""
            ),
            "unreal_python_script": rel(ue_script),
        },
        "calibration_marker_policy": {
            "primary_acceptance_surface": True,
            "building_landmarks_are_auxiliary_only": True,
            "why": "Factory features have thickness, unclear boundaries, and possible visual/collision differences; the rig is project-owned geometry generated from one coordinate contract.",
            "visual_rejection_conditions": [
                "white origin block is not at the intended uav1/audit anchor",
                "red +X, green +Y, and blue +Z markers point in unexpected directions",
                "purple asymmetric block appears mirrored or in the wrong quadrant",
                "orange -Y guard appears on the same side as the green +Y marker",
                "sizes are visibly off by more than a gross review tolerance",
            ],
        },
        "calibration_markers": calibration_markers,
        "spawn_markers": spawn_markers,
        "segments": segments,
    }

    contract_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_segments_csv(segments_csv, segments)
    write_calibration_markers_csv(calibration_markers_csv, calibration_markers)
    write_spawn_markers_csv(spawn_markers_csv, spawn_markers)
    write_gazebo_world(clean_world, gazebo_world, segments, calibration_markers, args.gazebo_line_thickness_m)
    write_rviz_config(rviz_config, args.marker_topic, args.fixed_frame, [origin[0], origin[1], origin[2] + 1.2])
    write_ue_python(ue_script, rel(contract_path))
    write_rviz_publisher(rviz_publisher, rel(contract_path))

    summary_path = result_dir / "SUMMARY.md"
    summary_path.write_text(
        "\n".join([
            "# Factory L2 Calibration Frame Review",
            "",
            "- status: `review_required`",
            f"- origin gazebo m: `{origin}`",
            f"- origin unreal cm: `{gazebo_to_unreal_cm(origin)}`",
            f"- segment count: `{len(segments)}`",
            f"- calibration marker count: `{len(calibration_markers)}`",
            f"- contract: `{rel(contract_path)}`",
            f"- segments csv: `{rel(segments_csv)}`",
            f"- calibration markers csv: `{rel(calibration_markers_csv)}`",
            f"- spawn markers csv: `{rel(spawn_markers_csv)}`",
            f"- Gazebo world: `{rel(gazebo_world)}`",
            f"- RViz config: `{rel(rviz_config)}`",
            f"- UE placement script: `{rel(ue_script)}`",
            "",
            "This is the primary F0.5 coordinate acceptance surface. It is not runtime evidence.",
            "",
        ]),
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps({"status": "review_required", "contract": rel(contract_path), "summary": rel(summary_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
