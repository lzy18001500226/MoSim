#!/usr/bin/env python3
"""Compare Sunray150 STL and DAE geometry units/transforms through Blender.

Run:
  python3 Scripts/UE5/assets/compare_sunray_stl_dae_parameters.py
"""

from __future__ import annotations

import json
import math
import re
import struct
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MESH_DIR = (
    PROJECT_ROOT
    / "References"
    / "Sunray"
    / "simulation"
    / "sunray_simulator"
    / "models"
    / "drone_models"
    / "sunray150_with_mid360"
    / "meshes"
)
OUT_PATH = PROJECT_ROOT / "Results" / "unreal_scene_mapping" / "sunray_stl_dae_parameter_compare_20260604.json"


NS = {"c": "http://www.collada.org/2005/11/COLLADASchema"}


def bbox_from_points(points: list[list[float]] | np.ndarray) -> dict[str, list[float]] | None:
    if len(points) == 0:
        return None
    arr = np.asarray(points, dtype=float)
    mn = arr.min(axis=0).tolist()
    mx = arr.max(axis=0).tolist()
    return {
        "min": mn,
        "max": mx,
        "size": [mx[i] - mn[i] for i in range(3)],
        "center": [(mx[i] + mn[i]) / 2 for i in range(3)],
    }


def transform_bbox(bbox: dict[str, list[float]], matrix: np.ndarray) -> dict[str, list[float]]:
    mn = bbox["min"]
    mx = bbox["max"]
    corners = []
    for x in (mn[0], mx[0]):
        for y in (mn[1], mx[1]):
            for z in (mn[2], mx[2]):
                p = matrix @ np.array([x, y, z, 1.0])
                corners.append(p[:3].tolist())
    return bbox_from_points(corners) or {"min": [], "max": [], "size": [], "center": []}


def stl_bbox(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) > 84:
        n_triangles = struct.unpack("<I", data[80:84])[0]
        if 84 + n_triangles * 50 == len(data):
            points = []
            offset = 84
            for _ in range(n_triangles):
                values = struct.unpack("<12f", data[offset : offset + 48])
                points.extend(
                    [
                        [values[3], values[4], values[5]],
                        [values[6], values[7], values[8]],
                        [values[9], values[10], values[11]],
                    ]
                )
                offset += 50
            return {"format": "binary", "triangle_count": n_triangles, "bbox_raw": bbox_from_points(points)}

    text = data.decode("utf-8", errors="ignore")
    points = [
        [float(x), float(y), float(z)]
        for x, y, z in re.findall(
            r"vertex\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)",
            text,
        )
    ]
    return {"format": "ascii", "triangle_count": len(points) // 3, "bbox_raw": bbox_from_points(points)}


def rot_z(theta: float) -> np.ndarray:
    c = math.cos(theta)
    s = math.sin(theta)
    return np.array(
        [
            [c, -s, 0.0, 0.0],
            [s, c, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )


def scale_matrix(s: float) -> np.ndarray:
    return np.diag([s, s, s, 1.0])


def translate_matrix(x: float, y: float, z: float) -> np.ndarray:
    mat = np.identity(4)
    mat[:3, 3] = [x, y, z]
    return mat


def parse_dae(path: Path) -> dict:
    tree = ET.parse(path)
    root = tree.getroot()
    asset = root.find("c:asset", NS)
    unit = asset.find("c:unit", NS) if asset is not None else None
    up_axis = asset.findtext("c:up_axis", default="", namespaces=NS) if asset is not None else ""
    meter = float(unit.attrib.get("meter", "1")) if unit is not None else 1.0
    unit_name = unit.attrib.get("name", "") if unit is not None else ""

    geometry_bboxes: dict[str, dict] = {}
    for geometry in root.findall(".//c:library_geometries/c:geometry", NS):
        gid = geometry.attrib.get("id", "")
        gname = geometry.attrib.get("name", "")
        points = []
        for source in geometry.findall(".//c:source", NS):
            float_array = source.find("c:float_array", NS)
            if float_array is None or not float_array.text:
                continue
            sid = source.attrib.get("id", "").lower()
            if "position" not in sid and "positions" not in sid:
                continue
            values = [float(x) for x in float_array.text.split()]
            points.extend(values[i : i + 3] for i in range(0, len(values), 3) if i + 2 < len(values))
        geometry_bboxes[gid] = {"name": gname, "bbox_dae_units": bbox_from_points(points), "point_count": len(points)}

    node_results = []
    transformed_boxes = []
    for node in root.findall(".//c:library_visual_scenes//c:node", NS):
        instance = node.find("c:instance_geometry", NS)
        if instance is None:
            continue
        url = instance.attrib.get("url", "").lstrip("#")
        bbox = geometry_bboxes.get(url, {}).get("bbox_dae_units")
        if bbox is None:
            continue
        matrix_node = node.find("c:matrix", NS)
        if matrix_node is not None and matrix_node.text:
            values = [float(x) for x in matrix_node.text.split()]
            matrix = np.asarray(values, dtype=float).reshape((4, 4))
        else:
            matrix = np.identity(4)
        transformed = transform_bbox(bbox, matrix)
        transformed_m = {
            key: ([v * meter for v in value] if isinstance(value, list) else value)
            for key, value in transformed.items()
        }
        transformed_boxes.append(transformed_m)
        node_results.append(
            {
                "id": node.attrib.get("id", ""),
                "name": node.attrib.get("name", ""),
                "geometry": url,
                "matrix_row_major": matrix.tolist(),
                "bbox_dae_units_after_node": transformed,
                "bbox_meters_after_unit": transformed_m,
            }
        )

    all_points = []
    for box in transformed_boxes:
        mn = box["min"]
        mx = box["max"]
        for x in (mn[0], mx[0]):
            for y in (mn[1], mx[1]):
                for z in (mn[2], mx[2]):
                    all_points.append([x, y, z])

    return {
        "unit_meter": meter,
        "unit_name": unit_name,
        "up_axis": up_axis,
        "geometry_count": len(geometry_bboxes),
        "node_geometry_count": len(node_results),
        "total_bbox_meters_after_node_unit": bbox_from_points(all_points),
        "geometry_names_first80": [
            {"id": gid, "name": data["name"], "bbox_dae_units": data["bbox_dae_units"]}
            for gid, data in list(geometry_bboxes.items())[:80]
        ],
        "node_results_first80": node_results[:80],
    }


def main() -> None:
    body_sdf_matrix = translate_matrix(0.0, 0.0, 0.0525) @ rot_z(-1.57) @ scale_matrix(0.03)
    prop_sdf_visual_matrix = rot_z(0.0) @ scale_matrix(0.03)
    prop_mm_to_dae_matrix = scale_matrix(0.001 / 0.0254)

    sunray = stl_bbox(MESH_DIR / "sunray.stl")
    sunray["bbox_sdf_visual_meters"] = transform_bbox(sunray["bbox_raw"], body_sdf_matrix)

    sunray_alt = stl_bbox(MESH_DIR / "sunray_.stl")
    sunray_alt["bbox_sdf_visual_meters"] = transform_bbox(sunray_alt["bbox_raw"], body_sdf_matrix)

    prop = stl_bbox(MESH_DIR / "sunray_cw.stl")
    prop["bbox_sdf_visual_if_scale_0p03_meters"] = transform_bbox(prop["bbox_raw"], prop_sdf_visual_matrix)
    prop["bbox_if_mm_to_dae_units"] = transform_bbox(prop["bbox_raw"], prop_mm_to_dae_matrix)

    results = {
        "dae_150": parse_dae(MESH_DIR / "150.dae"),
        "stl_sunray": sunray,
        "stl_sunray_alt": sunray_alt,
        "stl_sunray_cw": prop,
        "sdf_reference": {
            "body_uri": "model://sunray150_with_mid360/meshes/sunray.stl",
            "body_pose": [0, 0, 0.0525, 0, 0, -1.57],
            "body_scale": [0.03, 0.03, 0.03],
            "rotor_centers_meters": [
                [0.065, -0.065, -0.025],
                [-0.065, 0.065, -0.025],
                [0.065, 0.065, -0.025],
                [-0.065, -0.065, -0.025],
            ],
            "rotor_visual_pose": [0, 0, 0, 1.57, 0, 0],
            "rotor_visual_scale": [0.03, 0.03, 0.03],
        },
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(OUT_PATH)
    print(json.dumps(results, indent=2)[:9000])


if __name__ == "__main__":
    main()
