#!/usr/bin/env python3
"""Build a Blender audit scene from the sunray150_with_mid360 DAE source.

This scene is for manual source review only. It reads only files from
drone_models/sunray150_with_mid360 and does not add standalone Livox/MID-360
sources, proxy geometry, or the UE textured review asset.
"""

from __future__ import annotations

import json
import math
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
UAV_DAE = PROJECT_ROOT / "References" / "Sunray" / "simulation" / "sunray_simulator" / "models" / "drone_models" / "sunray150_with_mid360" / "meshes" / "150.dae"
OUT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
OUT_BLEND = OUT_DIR / "sunray150_with_mid360_dae_source_audit.blend"
OUT_MANIFEST = OUT_DIR / "sunray150_with_mid360_dae_source_audit_manifest.json"

NS = {"c": "http://www.collada.org/2005/11/COLLADASchema"}
FBX_ASC_RE = re.compile(r"FBXASC(\d{3})")


def decode_fbx_name(name: str) -> str:
    return FBX_ASC_RE.sub(lambda m: chr(int(m.group(1))), name)


def clean_name(name: str, max_len: int = 96) -> str:
    name = decode_fbx_name(name).replace("\\", "_").replace("/", "_")
    for suffix in ("Mesh", "-lib"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
    name = re.sub(r"[^A-Za-z0-9_.# -]+", "_", name)
    return name[:max_len]


def parse_floats(text: str | None) -> list[float]:
    return [float(x) for x in (text or "").split()]


def collada_matrix(text: str | None) -> Matrix:
    values = parse_floats(text)
    if len(values) != 16:
        return Matrix.Identity(4)
    return Matrix([values[i : i + 4] for i in range(0, 16, 4)])


def matrix_scale_xyz(x: float, y: float, z: float) -> Matrix:
    mat = Matrix.Identity(4)
    mat[0][0] = x
    mat[1][1] = y
    mat[2][2] = z
    return mat


def pose_matrix_xyz_rpy(x: float, y: float, z: float, roll: float, pitch: float, yaw: float) -> Matrix:
    return Matrix.Translation((x, y, z)) @ Euler((roll, pitch, yaw), "XYZ").to_matrix().to_4x4()


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for item in list(block):
            block.remove(item)


def effect_colors(root: ET.Element) -> dict[str, tuple[float, float, float, float]]:
    effects = {}
    for effect in root.findall(".//c:library_effects/c:effect", NS):
        diffuse = effect.find(".//c:diffuse/c:color", NS)
        color = tuple(parse_floats(diffuse.text)[:4]) if diffuse is not None else (0.6, 0.6, 0.6, 1.0)
        if len(color) != 4:
            color = (0.6, 0.6, 0.6, 1.0)
        effects[effect.attrib["id"]] = color

    material_to_color = {}
    for mat in root.findall(".//c:library_materials/c:material", NS):
        inst = mat.find("c:instance_effect", NS)
        url = (inst.attrib.get("url", "") if inst is not None else "").lstrip("#")
        material_to_color[mat.attrib["id"]] = effects.get(url, (0.6, 0.6, 0.6, 1.0))
    return material_to_color


def asset_unit_meter(root: ET.Element) -> float:
    unit = root.find(".//c:asset/c:unit", NS)
    if unit is None:
        return 1.0
    try:
        return float(unit.attrib.get("meter", "1.0"))
    except ValueError:
        return 1.0


def make_material(name: str, rgba: tuple[float, float, float, float], highlight: bool = False) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    if highlight:
        rgba = (min(1.0, rgba[0] + 0.25), min(1.0, rgba[1] + 0.18), min(1.0, rgba[2] + 0.08), 1.0)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = 0.42
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = rgba[3]
    if rgba[3] < 1.0:
        mat.blend_method = "BLEND"
    return mat


def parse_geometries(root: ET.Element) -> dict[str, dict]:
    geometries = {}
    for geom in root.findall(".//c:library_geometries/c:geometry", NS):
        mesh = geom.find("c:mesh", NS)
        if mesh is None:
            continue
        pos_source = None
        for source in mesh.findall("c:source", NS):
            sid = source.attrib.get("id", "")
            if sid.endswith("-POSITION") or "POSITION" in sid:
                pos_source = source
                break
        if pos_source is None:
            continue
        arr = pos_source.find("c:float_array", NS)
        coords = parse_floats(arr.text if arr is not None else None)
        verts = [tuple(coords[i : i + 3]) for i in range(0, len(coords), 3)]
        parts = []
        for tri_elem in mesh.findall("c:triangles", NS):
            p = tri_elem.find("c:p", NS)
            if p is None or not p.text:
                continue
            stride = max(1, len(tri_elem.findall("c:input", NS)))
            values = [int(x) for x in p.text.split()]
            faces = []
            for i in range(0, len(values), stride * 3):
                try:
                    faces.append((values[i], values[i + stride], values[i + stride * 2]))
                except IndexError:
                    break
            parts.append({"material": tri_elem.attrib.get("material", "unknown"), "faces": faces})
        if verts and parts:
            geometries[geom.attrib["id"]] = {
                "name": clean_name(geom.attrib.get("name", geom.attrib["id"])),
                "verts": verts,
                "parts": parts,
            }
    return geometries


def recursive_instances(node: ET.Element, parent: Matrix, instances: list[dict]) -> None:
    matrix_elem = node.find("c:matrix", NS)
    local = collada_matrix(matrix_elem.text if matrix_elem is not None else None)
    current = parent @ local
    inst = node.find("c:instance_geometry", NS)
    if inst is not None:
        url = inst.attrib.get("url", "")
        if url.startswith("#"):
            instances.append(
                {
                    "node_name": clean_name(node.attrib.get("name", url[1:])),
                    "geom_id": url[1:],
                    "matrix": current,
                }
            )
    for child in node.findall("c:node", NS):
        recursive_instances(child, current, instances)


def parse_instances(root: ET.Element) -> list[dict]:
    instances = []
    for scene in root.findall(".//c:library_visual_scenes/c:visual_scene", NS):
        for node in scene.findall("c:node", NS):
            recursive_instances(node, Matrix.Identity(4), instances)
    return instances


def is_radar_related(name: str) -> bool:
    n = name.upper()
    return "MID360" in n or "MID-360" in n or "RANGING_LIDAR" in n or "LIVOX" in n or "PROTECT_ARC" in n


def import_dae_as_objects(path: Path, prefix: str, base_transform: Matrix) -> dict:
    root = ET.parse(path).getroot()
    geometries = parse_geometries(root)
    instances = parse_instances(root)
    colors = effect_colors(root)
    mats: dict[str, bpy.types.Material] = {}
    unit_meter = asset_unit_meter(root)
    y_up_to_z_up = Matrix.Rotation(math.radians(90.0), 4, "X")
    created = []
    radar_objects = []
    propeller_objects = []

    for idx, inst in enumerate(instances):
        geom = geometries.get(inst["geom_id"])
        if not geom:
            continue
        related = is_radar_related(inst["node_name"] + " " + geom["name"])
        is_propeller = "PROPELLER" in (inst["node_name"] + " " + geom["name"]).upper()
        mat_names = []
        for part in geom["parts"]:
            source_mat = part["material"]
            mat_key = f"{prefix}_{source_mat}{'_RADAR' if related else ''}{'_PROP' if is_propeller else ''}"
            if mat_key not in mats:
                mats[mat_key] = make_material(
                    mat_key,
                    colors.get(source_mat, (0.58, 0.58, 0.58, 1.0)),
                    highlight=related or is_propeller,
                )
            mat_names.append(mat_key)

        transform = base_transform @ y_up_to_z_up @ matrix_scale_xyz(unit_meter, unit_meter, unit_meter) @ inst["matrix"]
        verts = []
        for v in geom["verts"]:
            tv = transform @ Vector(v)
            verts.append((tv.x, tv.y, tv.z))
        faces = []
        face_material_indices = []
        for mat_index, part in enumerate(geom["parts"]):
            faces.extend(part["faces"])
            face_material_indices.extend([mat_index] * len(part["faces"]))
        mesh = bpy.data.meshes.new(f"{prefix}_{idx:03d}_{geom['name']}_Mesh")
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj_name = f"{prefix}_{idx:03d}_{inst['node_name']}"
        obj = bpy.data.objects.new(clean_name(obj_name, max_len=128), mesh)
        for mat_name in mat_names:
            obj.data.materials.append(mats[mat_name])
        for poly, mat_index in zip(obj.data.polygons, face_material_indices):
            poly.material_index = mat_index
        bpy.context.collection.objects.link(obj)
        created.append(obj)
        if related:
            radar_objects.append(obj.name)
        if is_propeller:
            propeller_objects.append(obj.name)

    return {
        "source": str(path),
        "unit_meter": unit_meter,
        "geometry_count": len(geometries),
        "instance_count": len(instances),
        "created_objects": len(created),
        "radar_related_objects": radar_objects,
        "propeller_objects": propeller_objects,
    }


def frame_scene() -> None:
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    if not objs:
        return
    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    for obj in objs:
        for c in obj.bound_box:
            w = obj.matrix_world @ Vector(c)
            mins.x = min(mins.x, w.x)
            mins.y = min(mins.y, w.y)
            mins.z = min(mins.z, w.z)
            maxs.x = max(maxs.x, w.x)
            maxs.y = max(maxs.y, w.y)
            maxs.z = max(maxs.z, w.z)
    center = (mins + maxs) * 0.5
    extent = max((maxs - mins).x, (maxs - mins).y, (maxs - mins).z)

    light_data = bpy.data.lights.new("Audit_Key_Light", type="AREA")
    light_data.energy = 1800
    light_data.size = extent * 0.6
    light = bpy.data.objects.new("Audit_Key_Light", light_data)
    light.location = center + Vector((extent * 0.2, -extent * 0.45, extent * 0.6))
    bpy.context.collection.objects.link(light)

    cam_data = bpy.data.cameras.new("Audit_Review_Camera")
    cam = bpy.data.objects.new("Audit_Review_Camera", cam_data)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = extent * 0.62
    cam.location = center + Vector((extent * 0.38, -extent * 0.62, extent * 0.35))
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam


def add_audit_label(name: str, text: str, location: tuple[float, float, float]) -> None:
    font_curve = bpy.data.curves.new(name, type="FONT")
    font_curve.body = text
    font_curve.align_x = "CENTER"
    font_curve.align_y = "CENTER"
    font_curve.size = 0.32
    font_curve.extrude = 0.006
    obj = bpy.data.objects.new(name, font_curve)
    obj.location = location
    obj.rotation_euler = (math.radians(65.0), 0.0, 0.0)
    mat = make_material(f"{name}_Mat", (0.04, 0.04, 0.04, 1.0))
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reset_scene()
    start = time.time()
    uav = import_dae_as_objects(UAV_DAE, "SUNRAY150_WITH_MID360_DAE_SOURCE", Matrix.Identity(4))
    add_audit_label(
        "Audit_Label_sunray150_with_mid360",
        "sunray150_with_mid360/meshes/150.dae only",
        (0.0, -0.55, 0.42),
    )
    frame_scene()
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.world.color = (0.86, 0.87, 0.88)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "purpose": "sunray150_with_mid360 DAE source audit; only drone_models/sunray150_with_mid360/meshes/150.dae is imported.",
        "sunray150_with_mid360_source": uav,
        "forbidden_sources": ["sensor_models/livox_mid360"],
        "elapsed_sec": round(time.time() - start, 3),
        "outputs": {"blend": str(OUT_BLEND), "manifest": str(OUT_MANIFEST)},
    }
    with open(OUT_MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(json.dumps(manifest, ensure_ascii=False, indent=2)[:8000])


if __name__ == "__main__":
    main()
