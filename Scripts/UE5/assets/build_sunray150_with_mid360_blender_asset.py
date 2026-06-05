#!/usr/bin/env python3
"""Build a Blender/UE-ready Sunray150 visual asset from the local DAE.

Blender 5.0 no longer exposes the old Collada importer in this environment, so
this script parses the local Sunray DAE directly and rebuilds named mesh groups
inside Blender. Run it from Blender Python.
"""

from __future__ import annotations

import json
import math
import os
import re
import struct
import sys
import time
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DAE_PATH = PROJECT_ROOT / "References" / "Sunray" / "simulation" / "sunray_simulator" / "models" / "drone_models" / "sunray150_with_mid360" / "meshes" / "150.dae"
TRI_BLADE_PROP_STL = PROJECT_ROOT / "References" / "Sunray" / "simulation" / "sunray_simulator" / "models" / "drone_models" / "sunray150_with_mid360" / "meshes" / "sunray_cw.stl"
OUT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150"
DAE_UNIT_METER = 0.0254
SDF_METER_TO_DAE_UNIT = 1.0 / DAE_UNIT_METER
STL_MM_TO_DAE_UNIT = 0.001 / DAE_UNIT_METER

NS = {"c": "http://www.collada.org/2005/11/COLLADASchema"}
FBX_ASC_RE = re.compile(r"FBXASC(\d{3})")


PALETTE = {
    "CarbonFrame": {
        "rgba": (0.03, 0.032, 0.035, 1.0),
        "roughness": 0.46,
        "metallic": 0.0,
    },
    "DarkGuards": {
        "rgba": (0.025, 0.026, 0.028, 1.0),
        "roughness": 0.42,
        "metallic": 0.0,
    },
    "Mid360BaseGrey": {
        "rgba": (0.78, 0.78, 0.76, 1.0),
        "roughness": 0.36,
        "metallic": 0.0,
    },
    "Mid360DomeBlue": {
        "rgba": (0.00, 0.34, 0.86, 0.78),
        "roughness": 0.08,
        "metallic": 0.0,
        "alpha": 0.78,
    },
    "PCBGreen": {
        "rgba": (0.02, 0.25, 0.12, 1.0),
        "roughness": 0.5,
        "metallic": 0.0,
    },
    "CableBlack": {
        "rgba": (0.018, 0.018, 0.018, 1.0),
        "roughness": 0.60,
        "metallic": 0.0,
    },
    "MetalFasteners": {
        "rgba": (0.34, 0.34, 0.34, 1.0),
        "roughness": 0.32,
        "metallic": 0.65,
    },
    "ConnectorGold": {
        "rgba": (0.95, 0.62, 0.16, 1.0),
        "roughness": 0.32,
        "metallic": 0.35,
    },
    "LightPlastic": {
        "rgba": (0.72, 0.72, 0.70, 0.72),
        "roughness": 0.24,
        "metallic": 0.0,
        "alpha": 0.72,
    },
    "WireSignal": {
        "rgba": (0.95, 0.30, 0.08, 1.0),
        "roughness": 0.55,
        "metallic": 0.0,
    },
    "Propeller": {
        "rgba": (0.09, 0.09, 0.085, 1.0),
        "roughness": 0.38,
        "metallic": 0.0,
    },
}


def decode_fbx_name(name: str) -> str:
    return FBX_ASC_RE.sub(lambda m: chr(int(m.group(1))), name)


def clean_name(name: str) -> str:
    name = decode_fbx_name(name)
    for suffix in ("Mesh", "-lib"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    return name.replace("\\", "_").replace("/", "_")


def classify(name: str, source_mat: str | None) -> str:
    n = clean_name(name).upper()
    mat = (source_mat or "").upper()

    if "PROPELLER" in n:
        return "Propeller"
    # MID-360 protection structure is physical bracketry, not blue optics.
    if "MID360_PROTECT_ARC" in n:
        return "DarkGuards"
    if ("MID360" in n or "MID-360" in n) and (
        "DOME" in n
        or "LENS" in n
        or "GLASS" in n
        or "WINDOW" in n
        or "MANIFOLD_SOLID_BREP" in n
        or "03561" in mat
    ):
        return "Mid360DomeBlue"
    if "MID360" in n or "MID-360" in n or "LIVOX" in n:
        return "Mid360BaseGrey"
    if "PROTECTIVE_RING" in n or "LAND_GEAR" in n:
        return "LightPlastic" if "PROTECTIVE_RING" in n else "DarkGuards"
    if "CABLE" in n or "WIRE" in n:
        return "CableBlack"
    if any(k in n for k in ("SCREW", "HEX_NUT", "NUT", "COLUM", "COLUMN", "BUTTON_HEAD", "COUNTERSUNK", "PIN")):
        if "PIN" in n or "MaterialFBXASC032FBXASC03562".upper() in mat:
            return "ConnectorGold"
        return "MetalFasteners"
    if "ESC" in n or "BOARD" in n or "MAIN_BOARD" in n or "SPEEDYBEE" in n:
        return "PCBGreen"
    if any(k in n for k in ("SENSOR", "RANGING_LIDAR_CAMERA_BASE", "CAMERA", "GPS", "ANTENNA")):
        return "LightPlastic"
    if any(k in n for k in ("MAIN_STRUCTURE", "TOP_PANNEL", "PANNEL", "FRAME", "PARTBODY")):
        return "CarbonFrame"
    if source_mat:
        if "03562" in source_mat:
            return "ConnectorGold"
        if "03566" in source_mat:
            return "Mid360DomeBlue"
        if "03570" in source_mat:
            return "PCBGreen"
        if "03563" in source_mat or "03569" in source_mat or "03573" in source_mat:
            return "MetalFasteners"
        if "03564" in source_mat or "03568" in source_mat:
            return "LightPlastic"
    return "CarbonFrame"


def parse_float_array(text: str) -> list[float]:
    return [float(x) for x in text.split()]


def collada_matrix(text: str) -> Matrix:
    values = [float(x) for x in text.split()]
    if len(values) != 16:
        return Matrix.Identity(4)
    rows = [values[i : i + 4] for i in range(0, 16, 4)]
    return Matrix(rows)


def make_material(name: str, cfg: dict) -> bpy.types.Material:
    mat = bpy.data.materials.new(f"MoSim_{name}")
    mat.diffuse_color = cfg["rgba"]
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = cfg["rgba"]
        bsdf.inputs["Roughness"].default_value = cfg.get("roughness", 0.5)
        bsdf.inputs["Metallic"].default_value = cfg.get("metallic", 0.0)
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = cfg.get("alpha", cfg["rgba"][3])
    if cfg["rgba"][3] < 1.0:
        mat.blend_method = "BLEND"
        mat.use_screen_refraction = True
        mat.show_transparent_back = True
    return mat


def extract_geometries(root: ET.Element) -> dict[str, dict]:
    geometries = {}
    for geom in root.findall(".//c:library_geometries/c:geometry", NS):
        geom_id = geom.attrib["id"]
        mesh = geom.find("c:mesh", NS)
        if mesh is None:
            continue
        pos_source = None
        for source in mesh.findall("c:source", NS):
            source_id = source.attrib.get("id", "")
            if source_id.endswith("-POSITION") or "POSITION" in source_id:
                pos_source = source
                break
        if pos_source is None:
            continue
        arr = pos_source.find("c:float_array", NS)
        if arr is None or not arr.text:
            continue
        coords = parse_float_array(arr.text)
        verts = [tuple(coords[i : i + 3]) for i in range(0, len(coords), 3)]
        tri_elem = mesh.find("c:triangles", NS)
        if tri_elem is None:
            continue
        p = tri_elem.find("c:p", NS)
        if p is None or not p.text:
            continue
        stride = max(1, len(tri_elem.findall("c:input", NS)))
        indices = [int(x) for x in p.text.split()]
        faces = []
        for i in range(0, len(indices), stride * 3):
            try:
                faces.append((indices[i], indices[i + stride], indices[i + stride * 2]))
            except IndexError:
                break
        geometries[geom_id] = {
            "name": clean_name(geom.attrib.get("name", geom_id)),
            "verts": verts,
            "faces": faces,
            "source_material": tri_elem.attrib.get("material"),
        }
    return geometries


def extract_instances(root: ET.Element) -> list[dict]:
    instances = []
    for node in root.findall(".//c:library_visual_scenes//c:node", NS):
        inst = node.find("c:instance_geometry", NS)
        if inst is None:
            continue
        url = inst.attrib.get("url", "")
        if not url.startswith("#"):
            continue
        matrix_elem = node.find("c:matrix", NS)
        matrix = collada_matrix(matrix_elem.text) if matrix_elem is not None and matrix_elem.text else Matrix.Identity(4)
        instances.append(
            {
                "node_name": clean_name(node.attrib.get("name", url[1:])),
                "geom_id": url[1:],
                "matrix": matrix,
            }
        )
    return instances


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for item in list(block):
            block.remove(item)


def read_stl(path: Path) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    data = path.read_bytes()
    if len(data) >= 84:
        tri_count = struct.unpack_from("<I", data, 80)[0]
        expected = 84 + tri_count * 50
        if expected == len(data):
            verts: list[tuple[float, float, float]] = []
            faces: list[tuple[int, int, int]] = []
            offset = 84
            for _ in range(tri_count):
                offset += 12
                face = []
                for _ in range(3):
                    v = struct.unpack_from("<fff", data, offset)
                    offset += 12
                    verts.append(v)
                    face.append(len(verts) - 1)
                faces.append(tuple(face))
                offset += 2
            return verts, faces
    verts = []
    faces = []
    current = []
    for line in data.decode("utf-8", errors="ignore").splitlines():
        parts = line.strip().split()
        if len(parts) == 4 and parts[0].lower() == "vertex":
            verts.append((float(parts[1]), float(parts[2]), float(parts[3])))
            current.append(len(verts) - 1)
            if len(current) == 3:
                faces.append(tuple(current))
                current = []
    return verts, faces


def build_asset() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    start = time.time()
    root = ET.parse(DAE_PATH).getroot()
    geometries = extract_geometries(root)
    instances = extract_instances(root)

    reset_scene()
    materials = {name: make_material(name, cfg) for name, cfg in PALETTE.items()}
    grouped_verts: dict[str, list[tuple[float, float, float]]] = defaultdict(list)
    grouped_faces: dict[str, list[tuple[int, int, int]]] = defaultdict(list)
    independent_meshes: list[dict] = []
    mapping = []

    for inst in instances:
        geom = geometries.get(inst["geom_id"])
        if not geom:
            continue
        cls = classify(inst["node_name"] + "_" + geom["name"], geom["source_material"])
        if cls == "Propeller":
            mapping.append(
                {
                    "node": inst["node_name"],
                    "geometry": geom["name"],
                    "source_material": geom["source_material"],
                    "assigned_group": "SkippedDaePropeller",
                    "vertices": len(geom["verts"]),
                    "triangles": len(geom["faces"]),
                    "skip_reason": "Runtime visual uses tri-blade sunray150_with_mid360/meshes/sunray_cw.stl, not DAE PROPELLER_*.",
                }
            )
            continue
        matrix = inst["matrix"]
        # DAE declares Y_UP and centimeter units. Keep unit scale in mesh data;
        # only rotate from Y-up to Blender Z-up for review/export consistency.
        y_up_to_z_up = Matrix.Rotation(math.radians(90.0), 4, "X")
        transform = y_up_to_z_up @ matrix
        verts = []
        for v in geom["verts"]:
            tv = transform @ Vector(v)
            verts.append((tv.x, tv.y, tv.z))
        base = len(grouped_verts[cls])
        grouped_verts[cls].extend(verts)
        grouped_faces[cls].extend((a + base, b + base, c + base) for a, b, c in geom["faces"])
        mapping.append(
            {
                "node": inst["node_name"],
                "geometry": geom["name"],
                "source_material": geom["source_material"],
                "assigned_group": cls,
                "vertices": len(geom["verts"]),
                "triangles": len(geom["faces"]),
            }
        )

    prop_verts, prop_faces = read_stl(TRI_BLADE_PROP_STL)
    rotor_centers_m = [
        ("front_right", (0.053745, -0.05374, -0.014052)),
        ("back_left", (-0.053761, 0.05376, -0.014052)),
        ("front_left", (0.053746, 0.053759, -0.014052)),
        ("back_right", (-0.053761, -0.053739, -0.014052)),
    ]
    rotor_centers = [
        (name, tuple(coord * SDF_METER_TO_DAE_UNIT for coord in center))
        for name, center in rotor_centers_m
    ]
    prop_transform_base = Matrix.Diagonal((STL_MM_TO_DAE_UNIT, STL_MM_TO_DAE_UNIT, STL_MM_TO_DAE_UNIT, 1.0))
    for rotor_name, center in rotor_centers:
        transform = Matrix.Translation(center) @ prop_transform_base
        verts = []
        for v in prop_verts:
            tv = transform @ Vector(v)
            verts.append((tv.x, tv.y, tv.z))
        independent_meshes.append(
            {
                "name": f"sunray150_with_mid360_tri_blade_prop_{rotor_name}",
                "verts": verts,
                "faces": list(prop_faces),
                "class": "Propeller",
                "sdf_center_m": dict(rotor_centers_m)[rotor_name],
                "dae_center": center,
            }
        )

    objects = []
    for cls, verts in grouped_verts.items():
        if not verts:
            continue
        mesh = bpy.data.meshes.new(f"Sunray150_{cls}_Mesh")
        mesh.from_pydata(verts, [], grouped_faces[cls])
        mesh.update()
        obj = bpy.data.objects.new(f"Sunray150_{cls}", mesh)
        obj.data.materials.append(materials[cls])
        bpy.context.collection.objects.link(obj)
        objects.append(obj)

    for item in independent_meshes:
        mesh = bpy.data.meshes.new(f"{item['name']}_Mesh")
        mesh.from_pydata(item["verts"], [], item["faces"])
        mesh.update()
        obj = bpy.data.objects.new(item["name"], mesh)
        obj.data.materials.append(materials[item["class"]])
        bpy.context.collection.objects.link(obj)
        objects.append(obj)

    # The local DAE contains clear MID-360 bracket geometry but the optical dome
    # imports as a near-flat strip. Add a review-grade dome/base proxy using the
    # DAE MID-360 cue center so the visual matches the CUAV reference without
    # coloring the protective bracket blue.
    mid360_cue = grouped_verts.get("Mid360DomeBlue", [])
    if mid360_cue:
        cx = sum(v[0] for v in mid360_cue) / len(mid360_cue)
        cy = sum(v[1] for v in mid360_cue) / len(mid360_cue)
        cz = max(v[2] for v in mid360_cue)
    else:
        cx, cy, cz = 0.0, 1.32, 2.35

    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=1.0, depth=0.42, location=(cx, cy, cz - 0.22))
    base = bpy.context.object
    base.name = "Sunray150_Mid360BaseSupplement"
    base.scale.x = 1.08
    base.scale.y = 0.82
    base.data.materials.append(materials["Mid360BaseGrey"])
    objects.append(base)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=96, ring_count=32, radius=1.0, location=(cx, cy, cz + 0.12))
    dome = bpy.context.object
    dome.name = "Sunray150_Mid360DomeSupplement"
    dome.scale.x = 0.92
    dome.scale.y = 0.70
    dome.scale.z = 0.52
    dome.data.materials.append(materials["Mid360DomeBlue"])
    objects.append(dome)

    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0] if objects else None

    # Normalize origin and add review lighting/camera without changing mesh scale.
    if objects:
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
        bbox_min = Vector((min(v.co.x for o in objects for v in o.data.vertices), min(v.co.y for o in objects for v in o.data.vertices), min(v.co.z for o in objects for v in o.data.vertices)))
        bbox_max = Vector((max(v.co.x for o in objects for v in o.data.vertices), max(v.co.y for o in objects for v in o.data.vertices), max(v.co.z for o in objects for v in o.data.vertices)))
        center = (bbox_min + bbox_max) * 0.5
        for obj in objects:
            obj.location -= center
        extent = max((bbox_max - bbox_min).x, (bbox_max - bbox_min).y, (bbox_max - bbox_min).z)
    else:
        extent = 100.0

    light_data = bpy.data.lights.new("Sunray150_Key_Light", type="AREA")
    light_data.energy = 500
    light_data.size = max(40.0, extent * 0.4)
    light = bpy.data.objects.new("Sunray150_Key_Light", light_data)
    light.location = (extent * 0.4, -extent * 0.5, extent * 0.55)
    bpy.context.collection.objects.link(light)

    cam_data = bpy.data.cameras.new("Sunray150_Review_Camera")
    cam = bpy.data.objects.new("Sunray150_Review_Camera", cam_data)
    cam.location = (extent * 0.65, -extent * 0.95, extent * 0.45)
    cam.rotation_euler = (math.radians(64), 0, math.radians(38))
    cam_data.lens = 45
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    manifest = {
        "source": str(DAE_PATH),
        "outputs": {
            "blend": str(OUT_DIR / "sunray150_with_mid360_textured.blend"),
            "fbx": str(OUT_DIR / "sunray150_with_mid360_textured.fbx"),
            "glb": str(OUT_DIR / "sunray150_with_mid360_textured.glb"),
            "manifest": str(OUT_DIR / "sunray150_with_mid360_textured_manifest.json"),
        },
        "generated_by": "Scripts/UE5/assets/build_sunray150_with_mid360_blender_asset.py",
        "elapsed_sec": round(time.time() - start, 3),
        "geometry_count": len(geometries),
        "instance_count": len(instances),
        "group_counts": {
            cls: {
                "objects": sum(1 for item in mapping if item["assigned_group"] == cls),
                "vertices": len(grouped_verts[cls]),
                "triangles": len(grouped_faces[cls]),
            }
            for cls in sorted(grouped_verts)
        },
        "independent_objects": [
            {
                "name": item["name"],
                "class": item["class"],
                "vertices": len(item["verts"]),
                "triangles": len(item["faces"]),
                "source_rule": "Propeller remains an independent tri-blade STL runtime object so it can be reviewed/replaced without touching body or MID-360.",
                "source": str(TRI_BLADE_PROP_STL),
                "sdf_center_m": item["sdf_center_m"],
                "dae_center": item["dae_center"],
                "unit_rule": "SDF rotor centers are meters; tri-blade STL is millimeter-scale; both are converted into the DAE unit declared by 150.dae, meter=0.0254.",
            }
            for item in independent_meshes
        ],
        "supplemental_geometry": {
            "Sunray150_Mid360BaseSupplement": {
                "reason": "DAE MID-360 body shell is not visually complete after Blender 5.0 no-Collada fallback parsing.",
                "material": "Mid360BaseGrey",
                "center": [cx, cy, cz - 0.22],
            },
            "Sunray150_Mid360DomeSupplement": {
                "reason": "DAE blue optical cue imports as a near-flat strip, so add a review-grade blue optical dome proxy.",
                "material": "Mid360DomeBlue",
                "center": [cx, cy, cz + 0.12],
            },
        },
        "palette": {k: v["rgba"] for k, v in PALETTE.items()},
        "mapping": mapping,
        "notes": [
            "MID360_PROTECT_ARC* and MID360_PROTECT_ARC_CONNECTOR* are dark guard/bracket parts, not blue glass.",
            "Blue is reserved for explicit MID360 optical/dome/lens/window names or source material fallback 03566.",
            "This is a DAE-derived review asset; exact manufacturer decals still require manual/texture authoring.",
        ],
    }
    with open(OUT_DIR / "sunray150_with_mid360_textured_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_DIR / "sunray150_with_mid360_textured.blend"))
    bpy.ops.export_scene.fbx(filepath=str(OUT_DIR / "sunray150_with_mid360_textured.fbx"), use_selection=False, add_leaf_bones=False, path_mode="COPY")
    bpy.ops.export_scene.gltf(filepath=str(OUT_DIR / "sunray150_with_mid360_textured.glb"), export_format="GLB")
    return manifest


if __name__ == "__main__":
    result = build_asset()
    print(json.dumps(result, ensure_ascii=False, indent=2)[:6000])
