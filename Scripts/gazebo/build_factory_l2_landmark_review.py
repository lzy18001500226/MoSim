#!/usr/bin/env python3
"""Build Factory L2 UE-to-Gazebo landmark review artifacts.

This is a source/static coordinate review helper. It reads UE-exported
collision truth, selects named non-symmetric landmarks, converts their
MWORKS/Gazebo meter coordinates back to UE centimeters, and creates:

- a CSV/JSON anchor packet;
- a Gazebo Classic visual-only review world with colored or red-only landmark markers;
- a small RViz display config and command hints for MarkerArray review.

It does not start Gazebo, ROS, PX4, MAVROS, RViz, planners, or controllers.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TRUTH = ROOT / "UE5/MoSimSceneLibrary/Content/MworksData/scene_truth/factoryenvironmentcollect_collision_truth.json"
DEFAULT_SCENE_PROFILE = ROOT / "Config/gazebo/scene_profiles/factory_l2_static_sunray_scene_clean_candidate.json"
DEFAULT_CLEAN_MANIFEST = ROOT / "Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/MANIFEST.json"
DEFAULT_OUTPUT_ROOT = ROOT / "Results/unreal_scene_mapping"


SEED_ACTORS = [
    ("gate_left_west", "SM_GateLeft02", "west large gate leaf"),
    ("gate_border_west", "SM_GateBorder02", "west gate border"),
    ("gate_left_east", "SM_GateLeft3", "east large gate leaf"),
    ("gate_right_east", "SM_GateRight02", "east gate right leaf"),
    ("door_office", "SM_Door_A_7", "office door"),
    ("pillar_grid_a", "SM_ConcretePillar25", "known concrete pillar"),
    ("pillar_grid_b", "SM_ConcretePillar33", "different concrete pillar row"),
    ("column_south_east", "SM_Column_8", "south-east column"),
    ("column_south_mid", "SM_Column_13", "south-mid column"),
    ("machine_vending_local", "SM_VendingMachine3", "local vending machine"),
    ("machine_recycling_local", "SM_RecyclingMachine3", "local recycling machine"),
    ("stair_local", "SM_Stair_01", "local stair"),
    ("assembly_corner", "SM_AssemblyLine25", "assembly-line corner"),
    ("floor_tile_origin_side", "SM_FloorMat40", "small floor tile near local work area"),
    ("floor_tile_other_side", "SM_FloorMat68", "small floor tile on opposite side"),
    ("factory_floor_north_west", "SM_FactoryFloorLarge114", "large factory floor tile"),
    ("factory_floor_north_east", "SM_FactoryFloorLarge116", "large factory floor tile"),
    ("factory_floor_south_west", "SM_FactoryFloorLarge120", "large factory floor tile"),
    ("factory_floor_south_east", "SM_FactoryFloorLarge123", "large factory floor tile"),
    ("outdoor_hangar", "SM_Background2_Hangar", "outdoor hangar/background physical mesh"),
]


COLORS = {
    "origin": (1.0, 1.0, 1.0, 1.0),
    "scene_profile_spawn": (0.1, 0.45, 1.0, 1.0),
    "truth_aabb": (1.0, 0.85, 0.05, 1.0),
    "ue_landmark_gate": (1.0, 0.2, 0.1, 1.0),
    "ue_landmark_obstacle": (0.2, 1.0, 0.2, 1.0),
    "ue_landmark_terrain": (0.1, 0.8, 1.0, 1.0),
    "ue_landmark_building": (1.0, 0.45, 1.0, 1.0),
    "ue_landmark_sensor": (1.0, 0.55, 0.05, 1.0),
    "ue_landmark_wall": (0.8, 0.8, 0.8, 1.0),
}


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return payload


def sanitize_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_") or "anchor"


def mworks_to_unreal_cm(xyz_m: list[float]) -> list[float]:
    x_m, y_m, z_m = xyz_m
    return [x_m * 100.0, -y_m * 100.0, z_m * 100.0]


def add_anchor(
    anchors: list[dict[str, Any]],
    *,
    anchor_id: str,
    label: str,
    anchor_type: str,
    xyz_m: list[float],
    source: str,
    semantic_type: str = "",
    source_actor: str = "",
    source_mesh: str = "",
    size_m: list[float] | None = None,
    min_m: list[float] | None = None,
    max_m: list[float] | None = None,
    review_hint: str = "",
) -> None:
    unreal_xyz_cm = mworks_to_unreal_cm(xyz_m)
    anchors.append({
        "id": sanitize_name(anchor_id),
        "label": label,
        "type": anchor_type,
        "source": source,
        "semantic_type": semantic_type,
        "source_actor": source_actor,
        "source_mesh": source_mesh,
        "mworks_xyz_m": xyz_m,
        "gazebo_xyz_m": xyz_m,
        "unreal_xyz_cm": unreal_xyz_cm,
        "size_m": size_m or [0.0, 0.0, 0.0],
        "min_m": min_m or xyz_m,
        "max_m": max_m or xyz_m,
        "review_hint": review_hint,
    })


def truth_bounds(proxies: list[dict[str, Any]]) -> dict[str, list[float]]:
    mins = [float("inf"), float("inf"), float("inf")]
    maxs = [float("-inf"), float("-inf"), float("-inf")]
    for proxy in proxies:
        min_m = proxy.get("min_m")
        max_m = proxy.get("max_m")
        if not (isinstance(min_m, list) and isinstance(max_m, list) and len(min_m) >= 3 and len(max_m) >= 3):
            continue
        for index in range(3):
            mins[index] = min(mins[index], float(min_m[index]))
            maxs[index] = max(maxs[index], float(max_m[index]))
    return {
        "min_m": mins,
        "max_m": maxs,
        "center_m": [(mins[index] + maxs[index]) * 0.5 for index in range(3)],
        "size_m": [maxs[index] - mins[index] for index in range(3)],
    }


def actor_index(proxies: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for proxy in proxies:
        actor = str(proxy.get("source_actor", ""))
        if actor and actor not in indexed:
            indexed[actor] = proxy
    return indexed


def select_anchors(truth: dict[str, Any], scene_profile: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    proxies = [p for p in truth.get("collision_proxies", []) if isinstance(p, dict)]
    bounds = truth_bounds(proxies)
    anchors: list[dict[str, Any]] = []
    missing_seed_actors: list[str] = []

    add_anchor(
        anchors,
        anchor_id="world_origin",
        label="world origin",
        anchor_type="origin",
        xyz_m=[0.0, 0.0, 0.0],
        source="coordinate_contract",
        review_hint="Gazebo/MWORKS world origin; this is not automatically the takeoff home point.",
    )
    for name, xyz in (
        ("truth_bounds_min", bounds["min_m"]),
        ("truth_bounds_max", bounds["max_m"]),
        ("truth_bounds_center", bounds["center_m"]),
    ):
        add_anchor(
            anchors,
            anchor_id=name,
            label=name.replace("_", " "),
            anchor_type="truth_aabb",
            xyz_m=[float(v) for v in xyz],
            source="ue_collision_truth_aabb",
            review_hint="Scene AABB anchor from UE collision truth; use only for coarse extent/origin sanity.",
        )

    for spawn in scene_profile.get("default_spawn_points", []):
        if not isinstance(spawn, dict):
            continue
        uav = spawn.get("uav", "unknown")
        xyz = [float(spawn.get("x", 0.0)), float(spawn.get("y", 0.0)), float(spawn.get("z", 0.0))]
        add_anchor(
            anchors,
            anchor_id=f"default_spawn_uav{uav}",
            label=f"default spawn uav{uav}",
            anchor_type="scene_profile_spawn",
            xyz_m=xyz,
            source="clean_scene_profile",
            review_hint="Configured Gazebo spawn point; compare with home/origin audit before flight.",
        )

    by_actor = actor_index(proxies)
    for anchor_id, actor, hint in SEED_ACTORS:
        proxy = by_actor.get(actor)
        if proxy is None:
            missing_seed_actors.append(actor)
            continue
        semantic = str(proxy.get("semantic_type", ""))
        add_anchor(
            anchors,
            anchor_id=anchor_id,
            label=actor,
            anchor_type=f"ue_landmark_{semantic or 'unknown'}",
            xyz_m=[float(v) for v in proxy.get("center_m", [0.0, 0.0, 0.0])[:3]],
            source="ue_collision_truth_named_proxy",
            semantic_type=semantic,
            source_actor=actor,
            source_mesh=str(proxy.get("source_mesh", "")),
            size_m=[float(v) for v in proxy.get("size_m", [0.0, 0.0, 0.0])[:3]],
            min_m=[float(v) for v in proxy.get("min_m", proxy.get("center_m", [0.0, 0.0, 0.0]))[:3]],
            max_m=[float(v) for v in proxy.get("max_m", proxy.get("center_m", [0.0, 0.0, 0.0]))[:3]],
            review_hint=hint,
        )
    return anchors, missing_seed_actors


def write_anchor_csv(path: Path, anchors: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id",
        "label",
        "type",
        "source",
        "semantic_type",
        "source_actor",
        "mworks_x_m",
        "mworks_y_m",
        "mworks_z_m",
        "unreal_x_cm",
        "unreal_y_cm",
        "unreal_z_cm",
        "size_x_m",
        "size_y_m",
        "size_z_m",
        "review_hint",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for anchor in anchors:
            m = anchor["mworks_xyz_m"]
            u = anchor["unreal_xyz_cm"]
            s = anchor["size_m"]
            writer.writerow({
                "id": anchor["id"],
                "label": anchor["label"],
                "type": anchor["type"],
                "source": anchor["source"],
                "semantic_type": anchor["semantic_type"],
                "source_actor": anchor["source_actor"],
                "mworks_x_m": m[0],
                "mworks_y_m": m[1],
                "mworks_z_m": m[2],
                "unreal_x_cm": u[0],
                "unreal_y_cm": u[1],
                "unreal_z_cm": u[2],
                "size_x_m": s[0],
                "size_y_m": s[1],
                "size_z_m": s[2],
                "review_hint": anchor["review_hint"],
            })


def marker_color(anchor_type: str) -> tuple[float, float, float, float]:
    return COLORS.get(anchor_type, COLORS.get(anchor_type.rsplit("_", 1)[0], (1.0, 1.0, 1.0, 1.0)))


def material_element(rgba: tuple[float, float, float, float]) -> ET.Element:
    r, g, b, a = rgba
    material = ET.Element("material")
    ambient = ET.SubElement(material, "ambient")
    ambient.text = f"{r:.3f} {g:.3f} {b:.3f} {a:.3f}"
    diffuse = ET.SubElement(material, "diffuse")
    diffuse.text = f"{r:.3f} {g:.3f} {b:.3f} {a:.3f}"
    emissive = ET.SubElement(material, "emissive")
    emissive.text = f"{0.35*r:.3f} {0.35*g:.3f} {0.35*b:.3f} {a:.3f}"
    return material


def append_box_visual(parent: ET.Element, anchor: dict[str, Any], rgba: tuple[float, float, float, float]) -> None:
    size = [max(0.2, float(v)) for v in anchor.get("size_m", [0.0, 0.0, 0.0])[:3]]
    if max(size) <= 0.2:
        return
    visual = ET.SubElement(parent, "visual", {"name": "anchor_red_box"})
    ET.SubElement(visual, "transparency").text = "0.35"
    geometry = ET.SubElement(visual, "geometry")
    box = ET.SubElement(geometry, "box")
    ET.SubElement(box, "size").text = " ".join(f"{v:.3f}" for v in size)
    visual.append(material_element(rgba))


def append_gazebo_markers(
    clean_world: Path,
    output_world: Path,
    anchors: list[dict[str, Any]],
    *,
    radius_m: float,
    red_review: bool,
) -> None:
    tree = ET.parse(clean_world)
    root = tree.getroot()
    world = root.find("world")
    if world is None:
        raise ValueError(f"world element not found: {clean_world}")
    for index, anchor in enumerate(anchors):
        x, y, z = anchor["gazebo_xyz_m"]
        model = ET.SubElement(world, "model", {"name": f"coord_anchor_{index:03d}_{anchor['id']}"})
        ET.SubElement(model, "static").text = "true"
        ET.SubElement(model, "pose").text = f"{x:.6f} {y:.6f} {z:.6f} 0 0 0"
        link = ET.SubElement(model, "link", {"name": "link"})
        visual = ET.SubElement(link, "visual", {"name": "anchor_sphere"})
        geometry = ET.SubElement(visual, "geometry")
        sphere = ET.SubElement(geometry, "sphere")
        ET.SubElement(sphere, "radius").text = f"{radius_m:.3f}"
        rgba = (1.0, 0.0, 0.0, 1.0) if red_review and anchor["type"].startswith("ue_landmark_") else marker_color(anchor["type"])
        visual.append(material_element(rgba))
        if red_review and anchor["type"].startswith("ue_landmark_"):
            append_box_visual(link, anchor, (1.0, 0.0, 0.0, 1.0))
    output_world.parent.mkdir(parents=True, exist_ok=True)
    tree.write(output_world, encoding="utf-8", xml_declaration=True)


def write_rviz_config(path: Path, marker_topic: str, fixed_frame: str) -> None:
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
            "    - Alpha: 0.5",
            "      Cell Size: 10",
            "      Class: rviz/Grid",
            "      Color: 160; 160; 164",
            "      Enabled: true",
            "      Name: Grid",
            "      Plane: XY",
            "      Plane Cell Count: 200",
            f"      Reference Frame: {fixed_frame}",
            "      Value: true",
            "    - Class: rviz/MarkerArray",
            "      Enabled: true",
            f"      Marker Topic: {marker_topic}",
            "      Name: Factory L2 UE Landmark Anchors",
            "      Queue Size: 10",
            "      Value: true",
            "  Enabled: true",
            "  Global Options:",
            "    Background Color: 42; 42; 42",
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
            "      Distance: 180",
            "      Focal Point:",
            "        X: 0",
            "        Y: 0",
            "        Z: 8",
            "      Name: Current View",
            "      Pitch: 0.72",
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scene-truth", type=Path, default=DEFAULT_TRUTH)
    parser.add_argument("--scene-profile", type=Path, default=DEFAULT_SCENE_PROFILE)
    parser.add_argument("--clean-manifest", type=Path, default=DEFAULT_CLEAN_MANIFEST)
    parser.add_argument("--result-dir", type=Path, default=None)
    parser.add_argument("--marker-topic", default="/mosim/factory_l2/anchor_markers")
    parser.add_argument("--fixed-frame", default="camera_init")
    parser.add_argument("--gazebo-marker-radius-m", type=float, default=1.6)
    parser.add_argument("--red-review", action="store_true", help="render UE landmarks as red dots with red box overlays")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scene_truth = project_path(args.scene_truth)
    scene_profile = project_path(args.scene_profile)
    clean_manifest_path = project_path(args.clean_manifest)
    result_dir = (
        project_path(args.result_dir)
        if args.result_dir is not None
        else DEFAULT_OUTPUT_ROOT / f"factory_l2_landmark_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    result_dir.mkdir(parents=True, exist_ok=True)

    truth_payload = read_json(scene_truth)
    profile_payload = read_json(scene_profile)
    clean_manifest = read_json(clean_manifest_path)
    anchors, missing_seed_actors = select_anchors(truth_payload, profile_payload)

    anchor_csv = result_dir / "factory_l2_landmark_anchors.csv"
    write_anchor_csv(anchor_csv, anchors)

    clean_world = project_path(str(clean_manifest["review_world_path"]))
    landmark_world = result_dir / "worlds" / "factoryenvironmentcollect_l2_static_landmark_review.sdf"
    append_gazebo_markers(
        clean_world,
        landmark_world,
        anchors,
        radius_m=args.gazebo_marker_radius_m,
        red_review=args.red_review,
    )

    rviz_config = result_dir / "rviz" / "factory_l2_coordinate_landmarks.rviz"
    write_rviz_config(rviz_config, args.marker_topic, args.fixed_frame)

    packet = {
        "schema": "mosim.factory_l2_landmark_review.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "review_required",
        "claim_boundary": [
            "UE-derived named landmark review only.",
            "This packet helps the user visually verify UE->Gazebo/RViz coordinate mapping.",
            "It does not prove ROS/PX4/MAVROS/RViz runtime success, localization, planning, or controller performance.",
            "The Gazebo landmark world is visual-only and must not replace the clean runtime scene profile.",
        ],
        "coordinate_contract": {
            "unreal_to_gazebo": "gazebo_x_m=UE_X_cm/100; gazebo_y_m=-UE_Y_cm/100; gazebo_z_m=UE_Z_cm/100",
            "gazebo_to_unreal": "UE_X_cm=gazebo_x_m*100; UE_Y_cm=-gazebo_y_m*100; UE_Z_cm=gazebo_z_m*100",
        },
        "inputs": {
            "scene_truth": rel(scene_truth),
            "scene_profile": rel(scene_profile),
            "clean_manifest": rel(clean_manifest_path),
            "clean_world": rel(clean_world),
        },
        "outputs": {
            "anchor_csv": rel(anchor_csv),
            "landmark_world": rel(landmark_world),
            "rviz_config": rel(rviz_config),
            "packet": rel(result_dir / "FACTORY_L2_LANDMARK_REVIEW.json"),
        },
        "marker_topic": args.marker_topic,
        "fixed_frame": args.fixed_frame,
        "anchor_count": len(anchors),
        "missing_seed_actors": missing_seed_actors,
        "anchors": anchors,
        "review_protocol": [
            "Open the clean Factory geometry or the visual-only landmark Gazebo world.",
            "Start the RViz marker publisher with this CSV and this marker topic.",
            "For each non-symmetric landmark, verify the marker is on the matching UE object: gates, door, pillars, column row, machines, stairs, floor tiles, outdoor hangar.",
            "Specifically check left/right and front/back landmarks; a Y-axis sign error will swap those landmarks.",
            "Do not accept the clean Factory scene profile until the user visually accepts these landmarks.",
        ],
        "open_commands": {
            "gazebo_landmark_review_wsl": (
                "cd /mnt/c/Users/HP/Desktop/MoSim && "
                "GAZEBO_MODEL_PATH=\"$PWD/Results/unreal_scene_mapping/factory_l2_static_import/gazebo_review_clean/models:$GAZEBO_MODEL_PATH\" "
                f"gazebo --verbose \"{rel(landmark_world)}\""
            ),
            "rviz_marker_publisher_wsl": (
                "cd /mnt/c/Users/HP/Desktop/MoSim && "
                "source /opt/ros/noetic/setup.bash && "
                f"python3 Scripts/sunray/publish_factory_l2_anchor_markers.py --anchor-csv \"{rel(anchor_csv)}\" "
                f"--marker-topic {args.marker_topic} --frame-id {args.fixed_frame}"
            ),
            "rviz_open_wsl": (
                "cd /mnt/c/Users/HP/Desktop/MoSim && "
                "source /opt/ros/noetic/setup.bash && "
                f"rviz -d \"{rel(rviz_config)}\""
            ),
        },
    }
    packet_path = result_dir / "FACTORY_L2_LANDMARK_REVIEW.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary_path = result_dir / "SUMMARY.md"
    summary_path.write_text(
        "\n".join([
            "# Factory L2 Landmark Review",
            "",
            "- status: `review_required`",
            f"- anchor count: `{len(anchors)}`",
            f"- anchor csv: `{rel(anchor_csv)}`",
            f"- landmark Gazebo world: `{rel(landmark_world)}`",
            f"- RViz config: `{rel(rviz_config)}`",
            f"- marker topic: `{args.marker_topic}`",
            "",
            "This packet is for joint human review. It proves neither runtime success nor controller/planner correctness.",
            "",
        ]),
        encoding="utf-8",
    )

    print(json.dumps({"status": "review_required", "packet": rel(packet_path), "summary": rel(summary_path)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
