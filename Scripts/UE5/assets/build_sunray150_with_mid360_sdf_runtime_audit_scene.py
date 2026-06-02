#!/usr/bin/env python3
"""Build a Blender audit scene from the Sunray SDF runtime visual sources.

This audit scene follows `sunray150_with_mid360.sdf(.jinja)` as the primary
source. It is intentionally separate from MWORKS runtime STL parity checks.
The camera is a review aid only; it must not be interpreted as model yaw,
pitch, or roll.
"""

from __future__ import annotations

import json
import math
import re
import struct
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
SUNRAY_MODELS = PROJECT_ROOT / "References" / "Sunray" / "simulation" / "sunray_simulator" / "models"
SDF_MODEL = SUNRAY_MODELS / "drone_models" / "sunray150_with_mid360" / "sunray150_with_mid360.sdf"
SDF_TEMPLATE = SUNRAY_MODELS / "drone_models" / "sunray150_with_mid360" / "sunray150_with_mid360.sdf.jinja"
BODY_STL = SUNRAY_MODELS / "drone_models" / "sunray150_with_mid360" / "meshes" / "sunray.stl"
ROTOR_STL = SUNRAY_MODELS / "drone_models" / "sunray150_with_mid360" / "meshes" / "sunray_cw.stl"
OUT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
OUT_BLEND = OUT_DIR / "sunray150_with_mid360_sdf_runtime_audit.blend"
OUT_MANIFEST = OUT_DIR / "sunray150_with_mid360_sdf_runtime_audit_manifest.json"
ROTOR_YAW_OFFSET_DEG = 0.0

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


def make_material(name: str, rgba: tuple[float, float, float, float], roughness: float = 0.45) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = roughness
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = rgba[3]
    if rgba[3] < 1.0:
        mat.blend_method = "BLEND"
    return mat


def add_axis_markers(length: float = 0.18) -> None:
    """Add body-frame axes so review screenshots cannot hide a yaw mistake."""
    mats = {
        "X_forward_red": make_material("Audit_X_Forward_Red", (0.9, 0.05, 0.03, 1.0)),
        "Y_left_green": make_material("Audit_Y_Left_Green", (0.05, 0.75, 0.08, 1.0)),
        "Z_up_blue": make_material("Audit_Z_Up_Blue", (0.05, 0.20, 0.9, 1.0)),
    }
    axes = [
        ("Audit_X_forward_axis", Vector((length, 0, 0)), mats["X_forward_red"]),
        ("Audit_Y_left_axis", Vector((0, length, 0)), mats["Y_left_green"]),
        ("Audit_Z_up_axis", Vector((0, 0, length * 0.65)), mats["Z_up_blue"]),
    ]
    for name, end, mat in axes:
        curve = bpy.data.curves.new(name, type="CURVE")
        curve.dimensions = "3D"
        curve.bevel_depth = 0.0025
        spline = curve.splines.new("POLY")
        spline.points.add(1)
        spline.points[0].co = (0, 0, 0, 1)
        spline.points[1].co = (end.x, end.y, end.z, 1)
        obj = bpy.data.objects.new(name, curve)
        obj.data.materials.append(mat)
        bpy.context.collection.objects.link(obj)


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


def add_mesh_object(
    name: str,
    verts: list[tuple[float, float, float]],
    faces: list[tuple[int, int, int]],
    transform: Matrix,
    material: bpy.types.Material,
) -> bpy.types.Object:
    tv = []
    for v in verts:
        w = transform @ Vector(v)
        tv.append((w.x, w.y, w.z))
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata(tv, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(material)
    bpy.context.collection.objects.link(obj)
    return obj


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
        if len(color) != 4:
            color = (0.7, 0.7, 0.7, 1.0)
        effects[effect.attrib["id"]] = color
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
            vertex_offset = 0
            for inp in inputs:
                if inp.attrib.get("semantic") == "VERTEX":
                    vertex_offset = int(inp.attrib.get("offset", "0"))
                    break
            values = [int(x) for x in p.text.split()]
            faces = []
            for i in range(0, len(values), stride * 3):
                try:
                    faces.append(
                        (
                            values[i + vertex_offset],
                            values[i + stride + vertex_offset],
                            values[i + stride * 2 + vertex_offset],
                        )
                    )
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
    return {"source": str(path), "unit_meter": unit_meter, "created_objects": created}


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


def add_review_camera(name: str, center: Vector, extent: float, offset: Vector, ortho_scale: float) -> bpy.types.Object:
    cam_data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cam_data)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ortho_scale
    cam.location = center + offset
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(cam)
    return cam


def frame_camera() -> dict:
    _, _, center, extent = scene_bounds()
    light_data = bpy.data.lights.new("SDF_Audit_Key_Light", type="AREA")
    light_data.energy = 900
    light_data.size = max(extent, 0.6)
    light = bpy.data.objects.new("SDF_Audit_Key_Light", light_data)
    light.location = center + Vector((extent * 0.4, -extent * 0.7, extent * 0.8))
    bpy.context.collection.objects.link(light)
    ortho = max(extent * 1.18, 0.45)
    top = add_review_camera("SDF_Audit_Top_Camera_No_Model_Rotation", center, extent, Vector((0, 0, extent * 2.2)), ortho)
    add_review_camera("SDF_Audit_Front_Camera_X", center, extent, Vector((extent * 2.2, 0, 0)), ortho)
    add_review_camera("SDF_Audit_Left_Camera_Y", center, extent, Vector((0, -extent * 2.2, 0)), ortho)
    add_review_camera("SDF_Audit_Oblique_Camera_Review_Only", center, extent, Vector((extent * 0.65, -extent * 1.15, extent * 0.55)), ortho)
    bpy.context.scene.camera = top
    return {
        "active_camera": top.name,
        "camera_policy": "Top camera is active to avoid mistaking review-camera oblique angle for UAV/model yaw. Other cameras are review-only.",
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reset_scene()
    start = time.time()

    body_mat = make_material("SDF_Body_DarkGrey", (0.16, 0.16, 0.15, 1.0))
    rotor_red = make_material("SDF_Rotor_Red", (0.70, 0.05, 0.03, 1.0))
    rotor_blue = make_material("SDF_Rotor_Blue", (0.04, 0.20, 0.82, 1.0))

    body_verts, body_faces = read_stl(BODY_STL)
    rotor_verts, rotor_faces = read_stl(ROTOR_STL)

    body_transform = pose_matrix(0, 0, 0.0525, 0, 0, -1.57) @ matrix_scale_xyz(0.03, 0.03, 0.03)
    add_mesh_object("SDF_body_sunray_stl", body_verts, body_faces, body_transform, body_mat)

    rotor_poses = [
        ("rotor_0_red", 0.065, -0.065, -0.025, rotor_red),
        ("rotor_1_blue", -0.065, 0.065, -0.025, rotor_blue),
        ("rotor_2_red", 0.065, 0.065, -0.025, rotor_red),
        ("rotor_3_blue", -0.065, -0.065, -0.025, rotor_blue),
    ]
    # The selected sunray150_with_mid360 propeller STL is already in the
    # horizontal rotor plane. Applying the SDF roll=1.57 here turns it vertical.
    rotor_visual = (
        pose_matrix(0, 0, 0, 0, 0, math.radians(ROTOR_YAW_OFFSET_DEG))
        @ matrix_scale_xyz(0.001, 0.001, 0.001)
    )
    for name, x, y, z, mat in rotor_poses:
        add_mesh_object(f"SDF_{name}_sunray_cw_stl", rotor_verts, rotor_faces, pose_matrix(x, y, z, 0, 0, 0) @ rotor_visual, mat)

    add_axis_markers()

    mid360 = None
    camera_info = frame_camera()
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.world.color = (0.86, 0.87, 0.88)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))

    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "purpose": "Sunray SDF runtime visual audit: body STL + SDF-referenced rotor STL; MWORKS runtime STL is not used as placement authority.",
        "sources": {
            "sdf": str(SDF_MODEL),
            "sdf_template": str(SDF_TEMPLATE),
            "selected_folder": str(SUNRAY_MODELS / "drone_models" / "sunray150_with_mid360"),
            "rotor_source": str(ROTOR_STL),
            "source_note": "User-gated source rule: use files inside sunray150_with_mid360 only. The SDF text references model://sunray150/meshes/sunray_cw.stl, but this audit intentionally uses sunray150_with_mid360/meshes/sunray_cw.stl.",
        },
        "body": {"source": str(BODY_STL), "pose_xyz_rpy": [0, 0, 0.0525, 0, 0, -1.57], "pose_deg": [0, 0, 0, 0, 0, -89.954], "scale": [0.03, 0.03, 0.03], "triangles": len(body_faces)},
        "rotor": {
            "source": str(ROTOR_STL),
            "poses_xyz": [[x, y, z] for _, x, y, z, _ in rotor_poses],
            "visual_pose_xyz_rpy": [0, 0, 0, 0, 0, math.radians(ROTOR_YAW_OFFSET_DEG)],
            "visual_pose_deg": [0, 0, 0, 0, 0, ROTOR_YAW_OFFSET_DEG],
            "yaw_offset_deg": ROTOR_YAW_OFFSET_DEG,
            "scale": [0.001, 0.001, 0.001],
            "triangles_per_rotor": len(rotor_faces),
            "orientation_note": "sunray150_with_mid360/meshes/sunray_cw.stl is already horizontal; SDF roll=1.57 is not applied for this selected STL.",
        },
        "mid360": {
            "source_rule": "Do not import standalone sensor_models/livox_mid360 in this audit. Current visual source is limited to drone_models/sunray150_with_mid360.",
        },
        "camera_mounts_from_sdf": {
            "camera_front": {"pose_xyz_rpy": [0.12, 0, 0.025, 0, 0, 0], "pose_deg": [0.12, 0, 0.025, 0, 0, 0]},
            "camera_down": {"pose_xyz_rpy": [-0.01, 0, -0.02, 0, 1.5707963, 3.14], "pose_deg": [-0.01, 0, -0.02, 0, 90.0, 179.909]},
            "note": "No SDF mount uses 45 deg. The apparent 45 deg issue is likely a review camera, mesh-axis conversion, or UE import transform issue, not the camera_front SDF pose.",
        },
        "review_camera": camera_info,
        "elapsed_sec": round(time.time() - start, 3),
        "outputs": {"blend": str(OUT_BLEND), "manifest": str(OUT_MANIFEST)},
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2)[:8000])


if __name__ == "__main__":
    main()
