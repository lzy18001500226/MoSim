#!/usr/bin/env python3
"""Build a Gazebo collision world from UE scene occupancy truth.

The first conversion target is a collision-equivalent world for LiDAR/local-map
runtime review. It intentionally uses merged box obstacles from the exported UE
occupancy grid instead of trying to preserve UE materials or meshes.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENE = "factoryenvironmentcollect"
DEFAULT_MAPPING_ROOT = ROOT / "Results" / "unreal_scene_mapping"
DEFAULT_WORLD_DIR = ROOT / "Config" / "gazebo" / "worlds"
DEFAULT_REPORT_DIR = ROOT / "Results" / "gazebo_ros2" / "ue_truth_gazebo_worlds"


@dataclass(frozen=True)
class Rect:
    x0: int
    y0: int
    width: int
    height: int

    @property
    def area(self) -> int:
        return self.width * self.height


def project_path(path: str | Path) -> Path:
    raw = Path(path)
    candidate = raw if raw.is_absolute() else ROOT / raw
    resolved = candidate.resolve()
    root = ROOT.resolve()
    if not (resolved == root or root in resolved.parents):
        raise SystemExit(f"path is outside MoSim: {path}")
    return resolved


def sanitize_name(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]+", "_", value.strip())
    return cleaned.strip("_") or "scene"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def greedy_rectangles(cells: set[tuple[int, int]], *, max_rectangles: int) -> list[Rect]:
    """Merge occupied grid cells into axis-aligned rectangles.

    This keeps the generated SDF small enough for Gazebo while preserving a
    collision-conservative obstacle layout.
    """
    remaining = set(cells)
    rectangles: list[Rect] = []
    while remaining and len(rectangles) < max_rectangles:
        x0, y0 = min(remaining, key=lambda item: (item[1], item[0]))
        width = 1
        while (x0 + width, y0) in remaining:
            width += 1
        height = 1
        while True:
            row = {(x, y0 + height) for x in range(x0, x0 + width)}
            if row.issubset(remaining):
                height += 1
            else:
                break
        for y in range(y0, y0 + height):
            for x in range(x0, x0 + width):
                remaining.discard((x, y))
        rectangles.append(Rect(x0=x0, y0=y0, width=width, height=height))

    # If the cap is reached, preserve a conservative summary box for leftovers.
    if remaining:
        xs = [item[0] for item in remaining]
        ys = [item[1] for item in remaining]
        rectangles.append(
            Rect(
                x0=min(xs),
                y0=min(ys),
                width=max(xs) - min(xs) + 1,
                height=max(ys) - min(ys) + 1,
            )
        )
    return rectangles


def element(parent: ET.Element, tag: str, text: str | None = None, **attrs: str) -> ET.Element:
    child = ET.SubElement(parent, tag, attrs)
    if text is not None:
        child.text = text
    return child


def add_box_model(
    world: ET.Element,
    *,
    name: str,
    pose: tuple[float, float, float, float, float, float],
    size: tuple[float, float, float],
    color: tuple[float, float, float, float],
) -> None:
    model = element(world, "model", name=name)
    element(model, "static", "true")
    element(model, "pose", " ".join(f"{value:.6g}" for value in pose))
    link = element(model, "link", name="link")
    collision = element(link, "collision", name="collision")
    geometry = element(collision, "geometry")
    box = element(geometry, "box")
    element(box, "size", " ".join(f"{value:.6g}" for value in size))

    visual = element(link, "visual", name="visual")
    geometry = element(visual, "geometry")
    box = element(geometry, "box")
    element(box, "size", " ".join(f"{value:.6g}" for value in size))
    material = element(visual, "material")
    color_text = " ".join(f"{value:.4g}" for value in color)
    element(material, "ambient", color_text)
    element(material, "diffuse", color_text)


def add_world_plugins(world: ET.Element, *, render_engine: str) -> None:
    element(
        world,
        "plugin",
        filename="ignition-gazebo-physics-system",
        name="ignition::gazebo::systems::Physics",
    )
    element(
        world,
        "plugin",
        filename="ignition-gazebo-user-commands-system",
        name="ignition::gazebo::systems::UserCommands",
    )
    element(
        world,
        "plugin",
        filename="ignition-gazebo-scene-broadcaster-system",
        name="ignition::gazebo::systems::SceneBroadcaster",
    )
    sensors = element(
        world,
        "plugin",
        filename="ignition-gazebo-sensors-system",
        name="ignition::gazebo::systems::Sensors",
    )
    element(sensors, "render_engine", render_engine)
    element(
        world,
        "plugin",
        filename="ignition-gazebo-imu-system",
        name="ignition::gazebo::systems::Imu",
    )


def add_light(world: ET.Element) -> None:
    light = element(world, "light", name="sun", type="directional")
    element(light, "cast_shadows", "true")
    element(light, "pose", "0 0 30 0 0 0")
    element(light, "diffuse", "0.8 0.8 0.8 1")
    element(light, "specular", "0.2 0.2 0.2 1")
    attenuation = element(light, "attenuation")
    element(attenuation, "range", "1000")
    element(attenuation, "constant", "0.9")
    element(attenuation, "linear", "0.01")
    element(attenuation, "quadratic", "0.001")
    element(light, "direction", "-0.5 0.1 -0.9")


def build_world(args: argparse.Namespace) -> dict[str, Any]:
    scene_id = sanitize_name(args.scene_id)
    mapping_root = project_path(args.mapping_root)
    scene_root = mapping_root / scene_id
    occupancy_path = scene_root / "occupancy_grid.json"
    planner_path = scene_root / "planner_summary.json"
    if not occupancy_path.exists():
        raise SystemExit(f"missing occupancy grid: {occupancy_path}")
    if not planner_path.exists():
        raise SystemExit(f"missing planner summary: {planner_path}")

    occupancy = load_json(occupancy_path)
    planner = load_json(planner_path)
    grid = occupancy["grid"]
    origin_x, origin_y = [float(value) for value in grid["origin_xy_m"]]
    resolution = float(grid["resolution_m"])
    size_x, size_y = [int(value) for value in grid["size"]]
    occupied_cells = {(int(x), int(y)) for x, y in grid["occupied_cells_xy"]}
    flight_z = float(occupancy.get("flight_z_m", planner.get("start_m", [0.0, 0.0, 1.5])[2]))
    start_m = tuple(float(value) for value in planner.get("start_m", [0.0, 0.0, flight_z]))
    goal_m = tuple(float(value) for value in planner.get("goal_m", [start_m[0] + 5.0, start_m[1], flight_z]))
    offset_x = -start_m[0] if args.center_on_start else 0.0
    offset_y = -start_m[1] if args.center_on_start else 0.0
    offset_z = 0.0

    rectangles = greedy_rectangles(occupied_cells, max_rectangles=int(args.max_rectangles))
    world_name = args.world_name or f"mosim_ue_{scene_id}"

    sdf = ET.Element("sdf", version="1.9")
    world = element(sdf, "world", name=world_name)
    physics = element(world, "physics", name="default_physics", type="ignored")
    element(physics, "max_step_size", "0.001")
    element(physics, "real_time_factor", "1.0")
    element(physics, "real_time_update_rate", "1000")
    add_world_plugins(world, render_engine=args.render_engine)
    add_light(world)

    world_width = max(size_x * resolution, 40.0)
    world_height = max(size_y * resolution, 40.0)
    grid_center_x = origin_x + size_x * resolution / 2.0 + offset_x
    grid_center_y = origin_y + size_y * resolution / 2.0 + offset_y
    add_box_model(
        world,
        name="ue_truth_ground",
        pose=(grid_center_x, grid_center_y, -0.025, 0.0, 0.0, 0.0),
        size=(world_width, world_height, 0.05),
        color=(0.34, 0.36, 0.38, 1.0),
    )

    obstacle_height = float(args.obstacle_height_m)
    z_center = obstacle_height / 2.0
    for index, rect in enumerate(rectangles):
        cx = origin_x + (rect.x0 + rect.width / 2.0) * resolution + offset_x
        cy = origin_y + (rect.y0 + rect.height / 2.0) * resolution + offset_y
        sx = max(rect.width * resolution, resolution)
        sy = max(rect.height * resolution, resolution)
        color = (0.58, 0.42, 0.25, 1.0) if rect.area < 25 else (0.45, 0.36, 0.30, 1.0)
        add_box_model(
            world,
            name=f"ue_occ_{index:04d}",
            pose=(cx, cy, z_center, 0.0, 0.0, 0.0),
            size=(sx, sy, obstacle_height),
            color=color,
        )

    marker_height = 0.08
    add_box_model(
        world,
        name="ue_truth_start_marker",
        pose=(0.0 if args.center_on_start else start_m[0], 0.0 if args.center_on_start else start_m[1], marker_height / 2.0, 0.0, 0.0, 0.0),
        size=(0.8, 0.8, marker_height),
        color=(0.05, 0.45, 0.95, 1.0),
    )
    add_box_model(
        world,
        name="ue_truth_goal_marker",
        pose=(goal_m[0] + offset_x, goal_m[1] + offset_y, marker_height / 2.0, 0.0, 0.0, 0.0),
        size=(0.8, 0.8, marker_height),
        color=(0.05, 0.75, 0.25, 1.0),
    )

    include = element(world, "include")
    element(include, "uri", "model://sunray150")
    element(include, "pose", f"{0.0 if args.center_on_start else start_m[0]:.6g} {0.0 if args.center_on_start else start_m[1]:.6g} {flight_z:.6g} 0 0 0")

    ET.indent(sdf, space="  ")
    output_world = project_path(args.output_world or (DEFAULT_WORLD_DIR / f"ue_{scene_id}_collision_world.sdf"))
    output_world.parent.mkdir(parents=True, exist_ok=True)
    output_world.write_text("<?xml version=\"1.0\" ?>\n" + ET.tostring(sdf, encoding="unicode") + "\n", encoding="utf-8")

    report_dir = project_path(args.report_dir or (DEFAULT_REPORT_DIR / scene_id))
    report_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "schema": "mosim.ue_truth_to_gazebo_world.v1",
        "status": "gazebo_collision_world_ready",
        "scene_id": scene_id,
        "source_occupancy_grid": str(occupancy_path.relative_to(ROOT).as_posix()),
        "source_planner_summary": str(planner_path.relative_to(ROOT).as_posix()),
        "output_world": str(output_world.relative_to(ROOT).as_posix()),
        "world_name": world_name,
        "frame_policy": {
            "source_frame": occupancy.get("frame", "mworks_world"),
            "gazebo_frame": "gazebo_world",
            "center_on_start": bool(args.center_on_start),
            "translation_m": [offset_x, offset_y, offset_z],
            "rotation_rpy_rad": [0.0, 0.0, 0.0],
        },
        "source_grid": {
            "origin_xy_m": [origin_x, origin_y],
            "resolution_m": resolution,
            "size": [size_x, size_y],
            "occupied_cell_count": len(occupied_cells),
            "flight_z_m": flight_z,
        },
        "generated": {
            "rectangle_count": len(rectangles),
            "obstacle_height_m": obstacle_height,
            "start_pose_gazebo_m": [0.0 if args.center_on_start else start_m[0], 0.0 if args.center_on_start else start_m[1], flight_z],
            "goal_pose_gazebo_m": [goal_m[0] + offset_x, goal_m[1] + offset_y, goal_m[2] if len(goal_m) > 2 else flight_z],
        },
        "claim_boundary": [
            "Generated world is collision-equivalent from UE occupancy truth.",
            "It does not preserve UE materials, mesh detail, lighting, semantics, or final visual quality.",
            "It is intended for Gazebo LiDAR/local-map runtime review before richer mesh/semantic conversion.",
        ],
    }
    report_path = report_dir / f"{scene_id}_gazebo_world_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene-id", default=DEFAULT_SCENE)
    parser.add_argument("--mapping-root", default=str(DEFAULT_MAPPING_ROOT))
    parser.add_argument("--output-world", default="")
    parser.add_argument("--report-dir", default="")
    parser.add_argument("--world-name", default="")
    parser.add_argument("--render-engine", default="ogre")
    parser.add_argument("--obstacle-height-m", type=float, default=3.0)
    parser.add_argument("--max-rectangles", type=int, default=1400)
    parser.add_argument("--center-on-start", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()
    build_world(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
