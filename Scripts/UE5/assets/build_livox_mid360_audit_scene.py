#!/usr/bin/env python3
"""Build a standalone Blender audit scene for model://livox_mid360."""

from __future__ import annotations

import json
import math
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MID360_ROOT = PROJECT_ROOT / "References" / "Sunray" / "simulation" / "sunray_simulator" / "models" / "sensor_models" / "livox_mid360"
MID360_SDF = MID360_ROOT / "livox_mid360.sdf"
MID360_DAE = MID360_ROOT / "meshes" / "test2.dae"
OUT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
OUT_BLEND = OUT_DIR / "livox_mid360_standalone_audit.blend"
OUT_MANIFEST = OUT_DIR / "livox_mid360_standalone_audit_manifest.json"

NS = {"c": "http://www.collada.org/2005/11/COLLADASchema"}
FBX_ASC_RE = re.compile(r"FBXASC(\d{3})")


def decode_fbx_name(name: str) -> str:
    return FBX_ASC_RE.sub(lambda m: chr(int(m.group(1))), name)


def clean_name(name: str, max_len: int = 96) -> str:
    name = decode_fbx_name(name).replace("\\", "_").replace("/", "_")
    name = re.sub(r"[^A-Za-z0-9_.# -]+", "_", name)
    return name[:max_len]


def parse_floats(text: str | None) -> list[float]:
    return [float(x) for x in (text or "").split()]


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for item in list(block):
            block.remove(item)


def matrix_scale_xyz(x: float, y: float, z: float) -> Matrix:
    mat = Matrix.Identity(4)
    mat[0][0] = x
    mat[1][1] = y
    mat[2][2] = z
    return mat


def pose_matrix(x: float, y: float, z: float, roll: float, pitch: float, yaw: float) -> Matrix:
    return Matrix.Translation((x, y, z)) @ Euler((roll, pitch, yaw), "XYZ").to_matrix().to_4x4()


def make_material(name: str, rgba: tuple[float, float, float, float]) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
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


def collada_matrix(text: str | None) -> Matrix:
    values = parse_floats(text)
    if len(values) != 16:
        return Matrix.Identity(4)
    return Matrix([values[i : i + 4] for i in range(0, 16, 4)])


def asset_unit_meter(root: ET.Element) -> float:
    unit = root.find(".//c:asset/c:unit", NS)
    if unit is None:
        return 1.0
    return float(unit.attrib.get("meter", "1.0"))


def effect_colors(root: ET.Element) -> dict[str, tuple[float, float, float, float]]:
    effects = {}
    for effect in root.findall(".//c:library_effects/c:effect", NS):
        diffuse = effect.find(".//c:diffuse/c:color", NS)
        color = tuple(parse_floats(diffuse.text)[:4]) if diffuse is not None else (0.7, 0.7, 0.7, 1.0)
        effects[effect.attrib["id"]] = color if len(color) == 4 else (0.7, 0.7, 0.7, 1.0)
    material_to_color = {}
    for mat in root.findall(".//c:library_materials/c:material", NS):
        inst = mat.find("c:instance_effect", NS)
        url = (inst.attrib.get("url", "") if inst is not None else "").lstrip("#")
        material_to_color[mat.attrib["id"]] = effects.get(url, (0.7, 0.7, 0.7, 1.0))
    return material_to_color


def parse_dae_geometries(root: ET.Element) -> dict[str, dict]:
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
            inputs = tri_elem.findall("c:input", NS)
            stride = max(1, max(int(inp.attrib.get("offset", "0")) for inp in inputs) + 1)
            vertex_offset = next((int(inp.attrib.get("offset", "0")) for inp in inputs if inp.attrib.get("semantic") == "VERTEX"), 0)
            values = [int(x) for x in p.text.split()]
            faces = []
            for i in range(0, len(values), stride * 3):
                try:
                    faces.append((values[i + vertex_offset], values[i + stride + vertex_offset], values[i + stride * 2 + vertex_offset]))
                except IndexError:
                    break
            parts.append({"material": tri_elem.attrib.get("material", "unknown"), "faces": faces})
        if verts and parts:
            geometries[geom.attrib["id"]] = {"name": clean_name(geom.attrib.get("name", geom.attrib["id"])), "verts": verts, "parts": parts}
    return geometries


def recursive_instances(node: ET.Element, parent: Matrix, instances: list[dict]) -> None:
    matrix_elem = node.find("c:matrix", NS)
    current = parent @ collada_matrix(matrix_elem.text if matrix_elem is not None else None)
    inst = node.find("c:instance_geometry", NS)
    if inst is not None:
        url = inst.attrib.get("url", "")
        if url.startswith("#"):
            instances.append({"node_name": clean_name(node.attrib.get("name", url[1:])), "geom_id": url[1:], "matrix": current})
    for child in node.findall("c:node", NS):
        recursive_instances(child, current, instances)


def parse_dae_instances(root: ET.Element) -> list[dict]:
    instances: list[dict] = []
    for scene in root.findall(".//c:library_visual_scenes/c:visual_scene", NS):
        for node in scene.findall("c:node", NS):
            recursive_instances(node, Matrix.Identity(4), instances)
    return instances


def import_dae(path: Path, prefix: str, base_transform: Matrix) -> dict:
    root = ET.parse(path).getroot()
    unit_meter = asset_unit_meter(root)
    colors = effect_colors(root)
    geometries = parse_dae_geometries(root)
    instances = parse_dae_instances(root)
    y_up_to_z_up = Matrix.Rotation(math.radians(90.0), 4, "X")
    mats: dict[str, bpy.types.Material] = {}
    created = 0
    triangles = 0
    for idx, inst in enumerate(instances):
        geom = geometries.get(inst["geom_id"])
        if not geom:
            continue
        faces = []
        face_material_indices = []
        mat_names = []
        for mat_index, part in enumerate(geom["parts"]):
            mat_key = f"{prefix}_{part['material']}"
            if mat_key not in mats:
                mats[mat_key] = make_material(mat_key, colors.get(part["material"], (0.7, 0.7, 0.7, 1.0)))
            mat_names.append(mat_key)
            faces.extend(part["faces"])
            face_material_indices.extend([mat_index] * len(part["faces"]))
        transform = base_transform @ y_up_to_z_up @ matrix_scale_xyz(unit_meter, unit_meter, unit_meter) @ inst["matrix"]
        tv = []
        for v in geom["verts"]:
            w = transform @ Vector(v)
            tv.append((w.x, w.y, w.z))
        mesh = bpy.data.meshes.new(f"{prefix}_{idx:03d}_{geom['name']}_Mesh")
        mesh.from_pydata(tv, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(clean_name(f"{prefix}_{idx:03d}_{inst['node_name']}", 128), mesh)
        for mat_name in mat_names:
            obj.data.materials.append(mats[mat_name])
        for poly, mat_index in zip(obj.data.polygons, face_material_indices):
            poly.material_index = mat_index
        bpy.context.collection.objects.link(obj)
        created += 1
        triangles += len(faces)
    return {"source": str(path), "unit_meter": unit_meter, "created_objects": created, "triangles": triangles}


def scene_bounds() -> tuple[Vector, Vector, Vector, float]:
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for obj in objs:
        for c in obj.bound_box:
            w = obj.matrix_world @ Vector(c)
            mn.x = min(mn.x, w.x)
            mn.y = min(mn.y, w.y)
            mn.z = min(mn.z, w.z)
            mx.x = max(mx.x, w.x)
            mx.y = max(mx.y, w.y)
            mx.z = max(mx.z, w.z)
    center = (mn + mx) * 0.5
    extent = max((mx - mn).x, (mx - mn).y, (mx - mn).z)
    return mn, mx, center, extent


def recenter_mesh_objects_to_base_mount_center() -> dict:
    """Move imported MID-360 visual mesh objects so the circular base center is at origin."""
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    bounds = []
    for obj in objs:
        mn = Vector((1e9, 1e9, 1e9))
        mx = Vector((-1e9, -1e9, -1e9))
        for c in obj.bound_box:
            w = obj.matrix_world @ Vector(c)
            mn.x = min(mn.x, w.x)
            mn.y = min(mn.y, w.y)
            mn.z = min(mn.z, w.z)
            mx.x = max(mx.x, w.x)
            mx.y = max(mx.y, w.y)
            mx.z = max(mx.z, w.z)
        size = mx - mn
        center = (mn + mx) * 0.5
        bounds.append({"obj": obj, "min": mn, "max": mx, "size": size, "center": center})

    candidates = [
        item
        for item in bounds
        if item["size"].x > 0.05
        and item["size"].y > 0.05
        and item["size"].z < 0.02
        and abs(item["size"].x - item["size"].y) < 0.003
    ]
    if not candidates:
        raise RuntimeError("Cannot identify Livox MID-360 circular base mesh for mounting-center recentering.")
    base = max(candidates, key=lambda item: item["size"].x * item["size"].y)
    center = base["center"]
    for obj in objs:
        obj.location -= center
    return {
        "base_mount_object": base["obj"].name,
        "base_mount_bbox_min_before": list(base["min"]),
        "base_mount_bbox_max_before": list(base["max"]),
        "base_mount_center_before": list(center),
        "applied_translation": list(-center),
        "moved_mesh_objects": len(objs),
    }


def frame_camera() -> dict:
    mn, mx, center, extent = scene_bounds()
    light_data = bpy.data.lights.new("LivoxMid360_Audit_Key_Light", type="AREA")
    light_data.energy = 700
    light_data.size = max(extent, 0.15)
    light = bpy.data.objects.new("LivoxMid360_Audit_Key_Light", light_data)
    light.location = center + Vector((extent * 0.6, -extent * 0.8, extent * 0.7))
    bpy.context.collection.objects.link(light)
    cam_data = bpy.data.cameras.new("LivoxMid360_Audit_Oblique_Camera")
    cam = bpy.data.objects.new("LivoxMid360_Audit_Oblique_Camera", cam_data)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(extent * 1.35, 0.12)
    cam.location = center + Vector((extent * 1.2, -extent * 1.5, extent * 0.75))
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return {"active_camera": cam.name, "bounds_min": list(mn), "bounds_max": list(mx), "extent": extent}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reset_scene()
    start = time.time()
    # Manual visual audit accepted F_yaw180_only: connector faces UAV tail (-X).
    visual_transform = pose_matrix(0, 0, 0, 0, 0, 3.14159) @ matrix_scale_xyz(1.2, 1.2, 1.2)
    import_result = import_dae(MID360_DAE, "livox_mid360", visual_transform)
    recenter_result = recenter_mesh_objects_to_base_mount_center()
    camera_info = frame_camera()
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.world.color = (0.86, 0.87, 0.88)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "purpose": "Standalone audit for Gazebo model://livox_mid360.",
        "model_uri": "model://livox_mid360",
        "model_root": str(MID360_ROOT),
        "sdf": str(MID360_SDF),
        "visual_mesh": str(MID360_DAE),
        "sdf_visual_pose_xyz_rpy": [0, 0, 0, 1.57, 0, 3.14159],
        "accepted_visual_pose_xyz_rpy": [0, 0, 0, 0, 0, 3.14159],
        "accepted_rule": "Manual audit accepted F_yaw180_only; connector/port faces UAV tail (-X). Do not apply SDF roll=1.57 for Blender/UE visual orientation.",
        "center_rule": "Manual audit rejected the raw DAE/SDF visual origin and full visual bbox center as off-axis. Imported MID-360 visual mesh is recentered so the circular radar base mounting center is the Blender/UE origin.",
        "sdf_visual_scale": [1.2, 1.2, 1.2],
        "import_result": import_result,
        "recenter_result": recenter_result,
        "review_camera": camera_info,
        "elapsed_sec": round(time.time() - start, 3),
        "outputs": {"blend": str(OUT_BLEND), "manifest": str(OUT_MANIFEST)},
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2)[:4000])


if __name__ == "__main__":
    main()
