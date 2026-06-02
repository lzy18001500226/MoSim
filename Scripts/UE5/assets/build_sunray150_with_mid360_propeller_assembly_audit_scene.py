#!/usr/bin/env python3
"""Build a Sunray150 propeller assembly audit scene.

This is not a visual tuning script. It creates an auditable Blender scene for
checking the mechanical assembly constraint inside
drone_models/sunray150_with_mid360 only: propeller mounting holes must align
with the two motor-top screw positions/assembly faces. It does not import
MWORKS runtime STL or standalone Livox/MID-360 assets.
"""

from __future__ import annotations

import json
import math
import re
import struct
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
DAE_PATH = PROJECT_ROOT / "References" / "Sunray" / "simulation" / "sunray_simulator" / "models" / "drone_models" / "sunray150_with_mid360" / "meshes" / "150.dae"
OUT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
OUT_BLEND = OUT_DIR / "sunray150_with_mid360_propeller_assembly_audit.blend"
OUT_MANIFEST = OUT_DIR / "sunray150_with_mid360_propeller_assembly_audit_manifest.json"

NS = {"c": "http://www.collada.org/2005/11/COLLADASchema"}
FBX_ASC_RE = re.compile(r"FBXASC(\d{3})")

# MWORKS full quadrotor model places the four propellers through these body-frame
# translations. The DAE semantic source uses the same physical motor centers.
ROTOR_CENTERS = [
    ("rotor_front_right", Vector((0.065, -0.065, -0.025))),
    ("rotor_back_left", Vector((-0.065, 0.065, -0.025))),
    ("rotor_front_left", Vector((0.065, 0.065, -0.025))),
    ("rotor_back_right", Vector((-0.065, -0.065, -0.025))),
]

@dataclass
class DaeObject:
    name: str
    verts: list[tuple[float, float, float]]
    faces: list[tuple[int, int, int]]
    min_bound: Vector
    max_bound: Vector
    center: Vector


def decode_fbx_name(name: str | None) -> str:
    return FBX_ASC_RE.sub(lambda m: chr(int(m.group(1))), name or "")


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


def make_material(name: str, rgba: tuple[float, float, float, float]) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = 0.55
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = rgba[3]
    if rgba[3] < 1.0:
        mat.blend_method = "BLEND"
        mat.use_screen_refraction = True
    return mat


def parse_dae_geometries(root: ET.Element) -> dict[str, dict]:
    geometries: dict[str, dict] = {}
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
        faces: list[tuple[int, int, int]] = []
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
        if verts and faces:
            geometries[geom.attrib["id"]] = {
                "name": decode_fbx_name(geom.attrib.get("name", geom.attrib["id"])),
                "verts": verts,
                "faces": faces,
            }
    return geometries


def recursive_instances(node: ET.Element, parent: Matrix, instances: list[dict]) -> None:
    matrix_elem = node.find("c:matrix", NS)
    current = parent @ collada_matrix(matrix_elem.text if matrix_elem is not None else None)
    inst = node.find("c:instance_geometry", NS)
    if inst is not None:
        url = inst.attrib.get("url", "")
        if url.startswith("#"):
            instances.append({"node_name": decode_fbx_name(node.attrib.get("name", url[1:])), "geom_id": url[1:], "matrix": current})
    for child in node.findall("c:node", NS):
        recursive_instances(child, current, instances)


def parse_dae_instances(root: ET.Element) -> list[dict]:
    instances: list[dict] = []
    for scene in root.findall(".//c:library_visual_scenes/c:visual_scene", NS):
        for node in scene.findall("c:node", NS):
            recursive_instances(node, Matrix.Identity(4), instances)
    return instances


def dae_objects(path: Path) -> list[DaeObject]:
    root = ET.parse(path).getroot()
    unit_meter = asset_unit_meter(root)
    geometries = parse_dae_geometries(root)
    instances = parse_dae_instances(root)
    y_up_to_z_up = Matrix.Rotation(math.radians(90.0), 4, "X")
    base = y_up_to_z_up @ matrix_scale_xyz(unit_meter, unit_meter, unit_meter)
    out: list[DaeObject] = []
    for inst in instances:
        geom = geometries.get(inst["geom_id"])
        if not geom:
            continue
        transform = base @ inst["matrix"]
        tv = []
        for v in geom["verts"]:
            w = transform @ Vector(v)
            tv.append((w.x, w.y, w.z))
        pts = [Vector(v) for v in tv]
        mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        center = sum(pts, Vector()) / len(pts)
        out.append(DaeObject(f"{inst['node_name']} | {geom['name']}", tv, geom["faces"], mn, mx, center))
    return out


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


def add_mesh(name: str, verts: list[tuple[float, float, float]], faces: list[tuple[int, int, int]], material: bpy.types.Material, offset: Vector = Vector()) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata([(x + offset.x, y + offset.y, z + offset.z) for x, y, z in verts], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(clean_name(name, 128), mesh)
    obj.data.materials.append(material)
    bpy.context.collection.objects.link(obj)
    return obj


def add_uv_sphere(name: str, loc: Vector, radius: float, material: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = clean_name(name, 96)
    obj.data.materials.append(material)
    return obj


def add_cylinder_between(name: str, a: Vector, b: Vector, radius: float, material: bpy.types.Material) -> None:
    mid = (a + b) * 0.5
    direction = b - a
    length = direction.length
    if length < 1e-8:
        return
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=length, location=mid)
    obj = bpy.context.object
    obj.name = clean_name(name, 96)
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(material)


def add_text(name: str, text: str, loc: Vector, size: float, material: bpy.types.Material) -> None:
    font_curve = bpy.data.curves.new(clean_name(name), "FONT")
    font_curve.body = text
    font_curve.size = size
    font_curve.align_x = "CENTER"
    obj = bpy.data.objects.new(clean_name(name), font_curve)
    obj.location = loc
    obj.data.materials.append(material)
    bpy.context.collection.objects.link(obj)


def choose_semantic_parts(objects: list[DaeObject]) -> tuple[list[DaeObject], list[DaeObject], list[DaeObject], list[DaeObject]]:
    propellers = [o for o in objects if "PROPELLER" in o.name.upper()]
    propeller_patterns = [o for o in objects if "CIRCPATTERN" in o.name.upper()]
    motors = [o for o in objects if "MOTOR_2104" in o.name.upper() and ("MOTOR_ROTOR" in o.name.upper() or "MOTOR_STATOR" in o.name.upper())]
    screws = [o for o in objects if "SCREW_BUTTON_HEAD_M2_8MM" in o.name.upper()]
    return propellers, propeller_patterns, motors, screws


def nearest_pair_screws(screws: list[DaeObject], center: Vector) -> list[DaeObject]:
    # The DAE source has two M2x8 propeller screws around each motor. Pick the
    # two nearest screw objects to each propeller/motor center.
    candidates = sorted(screws, key=lambda o: (Vector((o.center.x, o.center.y, 0)) - Vector((center.x, center.y, 0))).length)
    return candidates[:2]


def frame_camera() -> None:
    objs = [o for o in bpy.context.scene.objects if o.type in {"MESH", "FONT"}]
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for obj in objs:
        if obj.type == "FONT":
            loc = obj.location
            mn.x, mn.y, mn.z = min(mn.x, loc.x), min(mn.y, loc.y), min(mn.z, loc.z)
            mx.x, mx.y, mx.z = max(mx.x, loc.x), max(mx.y, loc.y), max(mx.z, loc.z)
            continue
        for c in obj.bound_box:
            w = obj.matrix_world @ Vector(c)
            mn.x = min(mn.x, w.x)
            mn.y = min(mn.y, w.y)
            mn.z = min(mn.z, w.z)
            mx.x = max(mx.x, w.x)
            mx.y = max(mx.y, w.y)
            mx.z = max(mx.z, w.z)
    center = (mn + mx) * 0.5
    extent = max((mx - mn).x, (mx - mn).y, (mx - mn).z, 0.25)
    light_data = bpy.data.lights.new("Assembly_Audit_Key_Light", type="AREA")
    light_data.energy = 850
    light_data.size = extent
    light = bpy.data.objects.new("Assembly_Audit_Key_Light", light_data)
    light.location = center + Vector((extent * 0.4, -extent * 0.6, extent * 0.8))
    bpy.context.collection.objects.link(light)
    cam_data = bpy.data.cameras.new("Assembly_Audit_Camera")
    cam = bpy.data.objects.new("Assembly_Audit_Camera", cam_data)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = extent * 1.35
    cam.location = center + Vector((extent * 0.55, -extent * 1.0, extent * 0.65))
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reset_scene()

    dae_prop_mat = make_material("DAE_Propeller_Semantic", (0.08, 0.38, 0.95, 0.82))
    dae_pattern_mat = make_material("DAE_CircPattern_Possible_Full_Prop", (0.95, 0.18, 0.08, 0.50))
    motor_mat = make_material("DAE_Motor_Semantic", (0.08, 0.08, 0.08, 0.55))
    screw_mat = make_material("DAE_Screw_Candidates_Gold", (1.0, 0.68, 0.08, 1.0))
    line_mat = make_material("Assembly_Match_Lines_Green", (0.0, 0.85, 0.18, 1.0))
    text_mat = make_material("Audit_Text_Black", (0.02, 0.02, 0.02, 1.0))

    dae = dae_objects(DAE_PATH)
    semantic_props, semantic_patterns, semantic_motors, semantic_screws = choose_semantic_parts(dae)

    manifest_rotors = []
    for rotor_name, center in ROTOR_CENTERS:
        sem_prop = min(semantic_props, key=lambda o: (Vector((o.center.x, o.center.y, 0)) - Vector((center.x, center.y, 0))).length)
        add_mesh(f"{rotor_name}_DAE_semantic_propeller", sem_prop.verts, sem_prop.faces, dae_prop_mat)
        sem_pattern = min(semantic_patterns, key=lambda o: (Vector((o.center.x, o.center.y, 0)) - Vector((center.x, center.y, 0))).length)
        add_mesh(f"{rotor_name}_DAE_circpattern_possible_full_prop", sem_pattern.verts, sem_pattern.faces, dae_pattern_mat)
        nearby_motors = sorted(semantic_motors, key=lambda o: (Vector((o.center.x, o.center.y, 0)) - Vector((center.x, center.y, 0))).length)[:3]
        for mi, motor in enumerate(nearby_motors[:2]):
            add_mesh(f"{rotor_name}_DAE_motor_part_{mi}", motor.verts, motor.faces, motor_mat)

        screw_pair = nearest_pair_screws(semantic_screws, sem_prop.center)
        screw_centers = []
        for si, screw in enumerate(screw_pair):
            screw_centers.append(screw.center)
            add_mesh(f"{rotor_name}_DAE_prop_screw_{si}", screw.verts, screw.faces, screw_mat)
            add_uv_sphere(f"{rotor_name}_screw_center_{si}", screw.center, 0.0014, screw_mat)

        for si, screw_center in enumerate(screw_centers):
            add_cylinder_between(f"{rotor_name}_rotor_center_to_screw_candidate_{si}", center, screw_center, 0.00035, line_mat)

        add_text(
            f"{rotor_name}_label",
            rotor_name,
            center + Vector((0.0, 0.0, 0.035)),
            0.006,
            text_mat,
        )
        manifest_rotors.append(
            {
                "rotor": rotor_name,
                "runtime_center_m": [round(center.x, 6), round(center.y, 6), round(center.z, 6)],
                "dae_semantic_propeller": sem_prop.name,
                "dae_semantic_propeller_center_m": [round(sem_prop.center.x, 6), round(sem_prop.center.y, 6), round(sem_prop.center.z, 6)],
                "dae_circpattern_possible_full_prop": sem_pattern.name,
                "dae_circpattern_center_m": [round(sem_pattern.center.x, 6), round(sem_pattern.center.y, 6), round(sem_pattern.center.z, 6)],
                "dae_circpattern_bounds_min_m": [round(sem_pattern.min_bound.x, 6), round(sem_pattern.min_bound.y, 6), round(sem_pattern.min_bound.z, 6)],
                "dae_circpattern_bounds_max_m": [round(sem_pattern.max_bound.x, 6), round(sem_pattern.max_bound.y, 6), round(sem_pattern.max_bound.z, 6)],
                "dae_candidate_screws": [
                    {
                        "name": s.name,
                        "center_m": [round(s.center.x, 6), round(s.center.y, 6), round(s.center.z, 6)],
                        "bounds_min_m": [round(s.min_bound.x, 6), round(s.min_bound.y, 6), round(s.min_bound.z, 6)],
                        "bounds_max_m": [round(s.max_bound.x, 6), round(s.max_bound.y, 6), round(s.max_bound.z, 6)],
                    }
                    for s in screw_pair
                ],
            }
        )

    add_text(
        "assembly_rule_label",
        "sunray150_with_mid360 propeller assembly audit: blue = DAE propellers, gold = DAE screw candidates, green = rotor-center candidate lines",
        Vector((0.0, -0.12, 0.08)),
        0.005,
        text_mat,
    )

    frame_camera()
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.world.color = (0.86, 0.88, 0.90)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))

    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "purpose": "sunray150_with_mid360 propeller mechanical assembly audit. Only drone_models/sunray150_with_mid360/meshes/150.dae is imported.",
        "sources": {
            "dae_semantic_source": str(DAE_PATH),
        },
        "detected_semantic_counts": {
            "propellers": len(semantic_props),
            "circpattern_possible_full_propellers": len(semantic_patterns),
            "motor_parts": len(semantic_motors),
            "m2_8_screw_candidates": len(semantic_screws),
        },
        "forbidden_sources": ["References/MWORKS/QuadrotorModel/Resources/Visualization", "sensor_models/livox_mid360"],
        "rotors": manifest_rotors,
        "status": "audit_only_not_runtime_parameter_commit",
        "elapsed_sec": round(time.time() - start, 3),
        "outputs": {"blend": str(OUT_BLEND), "manifest": str(OUT_MANIFEST)},
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2)[:8000])


if __name__ == "__main__":
    main()
