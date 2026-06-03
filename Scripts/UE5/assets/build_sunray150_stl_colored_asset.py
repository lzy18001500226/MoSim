#!/usr/bin/env python3
"""Build a colored Sunray150 review asset from the accepted STL route.

This script does not use the rejected DAE radar/propeller assembly path. It
uses the manually accepted runtime geometry sources:

- body: sunray150_with_mid360/meshes/sunray.stl, which already contains MID-360
- propeller: sunray150_with_mid360/meshes/sunray_cw.stl

Because STL carries no part names or material slots, materials are assigned by
connected component geometry and spatial rules, with CUAV/YunZong reference
photos as the color source.
"""

from __future__ import annotations

import json
import math
import struct
import time
from collections import defaultdict, deque
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
SUNRAY_ROOT = PROJECT_ROOT / "References" / "Sunray" / "simulation" / "sunray_simulator" / "models" / "drone_models" / "sunray150_with_mid360"
BODY_STL = SUNRAY_ROOT / "meshes" / "sunray.stl"
ROTOR_STL = SUNRAY_ROOT / "meshes" / "sunray_cw.stl"
OUT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150"
OUT_BLEND = OUT_DIR / "sunray150_stl_colored.blend"
OUT_FBX = OUT_DIR / "sunray150_stl_colored.fbx"
OUT_GLB = OUT_DIR / "sunray150_stl_colored.glb"
OUT_MANIFEST = OUT_DIR / "sunray150_stl_colored_manifest.json"

BODY_TRANSFORM = Matrix.Translation((0, 0, 0.0525)) @ Euler((0, 0, -1.57), "XYZ").to_matrix().to_4x4() @ Matrix.Diagonal((0.03, 0.03, 0.03, 1.0))
ROTOR_VISUAL = Euler((0, 0, 0), "XYZ").to_matrix().to_4x4() @ Matrix.Diagonal((0.001, 0.001, 0.001, 1.0))
ROTOR_POSES = [
    ("front_right", 0.065, -0.065, -0.025),
    ("back_left", -0.065, 0.065, -0.025),
    ("front_left", 0.065, 0.065, -0.025),
    ("back_right", -0.065, -0.065, -0.025),
]

PALETTE = {
    "carbon_black": {"rgba": (0.018, 0.019, 0.021, 1.0), "roughness": 0.42, "metallic": 0.0},
    "guard_black": {"rgba": (0.026, 0.027, 0.030, 1.0), "roughness": 0.38, "metallic": 0.0},
    "rubber_black": {"rgba": (0.010, 0.010, 0.010, 1.0), "roughness": 0.62, "metallic": 0.0},
    "mid360_silver": {"rgba": (0.73, 0.72, 0.69, 1.0), "roughness": 0.30, "metallic": 0.08},
    "mid360_blue": {"rgba": (0.00, 0.32, 0.78, 0.76), "roughness": 0.08, "metallic": 0.0, "alpha": 0.76},
    "translucent_prop": {"rgba": (0.82, 0.83, 0.82, 0.42), "roughness": 0.18, "metallic": 0.0, "alpha": 0.42},
    "motor_black": {"rgba": (0.020, 0.020, 0.019, 1.0), "roughness": 0.30, "metallic": 0.18},
    "copper_winding": {"rgba": (0.95, 0.43, 0.09, 1.0), "roughness": 0.26, "metallic": 0.45},
    "metal_screw": {"rgba": (0.50, 0.48, 0.43, 1.0), "roughness": 0.22, "metallic": 0.65},
    "gold_standoff": {"rgba": (0.95, 0.64, 0.20, 1.0), "roughness": 0.28, "metallic": 0.50},
    "pcb_dark": {"rgba": (0.015, 0.035, 0.045, 1.0), "roughness": 0.46, "metallic": 0.0},
    "camera_glass": {"rgba": (0.005, 0.006, 0.007, 1.0), "roughness": 0.16, "metallic": 0.0},
}


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for item in list(block):
            block.remove(item)


def make_material(name: str, cfg: dict) -> bpy.types.Material:
    mat = bpy.data.materials.new(f"MoSim_{name}")
    mat.diffuse_color = cfg["rgba"]
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = cfg["rgba"]
        bsdf.inputs["Roughness"].default_value = cfg.get("roughness", 0.45)
        bsdf.inputs["Metallic"].default_value = cfg.get("metallic", 0.0)
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = cfg.get("alpha", cfg["rgba"][3])
    if cfg["rgba"][3] < 1.0:
        mat.blend_method = "BLEND"
        mat.show_transparent_back = True
    return mat


def read_stl(path: Path) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    data = path.read_bytes()
    if len(data) >= 84:
        tri_count = struct.unpack_from("<I", data, 80)[0]
        if 84 + tri_count * 50 == len(data):
            verts: list[tuple[float, float, float]] = []
            faces: list[tuple[int, int, int]] = []
            offset = 84
            for _ in range(tri_count):
                offset += 12
                face = []
                for _ in range(3):
                    verts.append(struct.unpack_from("<fff", data, offset))
                    face.append(len(verts) - 1)
                    offset += 12
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


def transformed_mesh(verts: list[tuple[float, float, float]], faces: list[tuple[int, int, int]], transform: Matrix) -> tuple[list[Vector], list[tuple[int, int, int]]]:
    return [transform @ Vector(v) for v in verts], list(faces)


def connected_components(verts: list[Vector], faces: list[tuple[int, int, int]], weld_tol: float = 1e-6) -> list[dict]:
    key_to_welded: dict[tuple[int, int, int], int] = {}
    welded: list[Vector] = []
    remap: list[int] = []
    inv_tol = 1.0 / weld_tol
    for v in verts:
        key = (round(v.x * inv_tol), round(v.y * inv_tol), round(v.z * inv_tol))
        if key not in key_to_welded:
            key_to_welded[key] = len(welded)
            welded.append(v)
        remap.append(key_to_welded[key])
    wfaces = [tuple(remap[i] for i in f) for f in faces]
    vert_faces: dict[int, list[int]] = defaultdict(list)
    for fi, face in enumerate(wfaces):
        for vi in set(face):
            vert_faces[vi].append(fi)
    seen = [False] * len(wfaces)
    comps = []
    for start in range(len(wfaces)):
        if seen[start]:
            continue
        q = deque([start])
        seen[start] = True
        comp_faces = []
        comp_verts: set[int] = set()
        while q:
            fi = q.popleft()
            comp_faces.append(fi)
            for vi in wfaces[fi]:
                comp_verts.add(vi)
                for nxt in vert_faces[vi]:
                    if not seen[nxt]:
                        seen[nxt] = True
                        q.append(nxt)
        pts = [welded[i] for i in comp_verts]
        mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        center = sum(pts, Vector()) / len(pts)
        comps.append({"faces": comp_faces, "verts": list(comp_verts), "min": mn, "max": mx, "center": center, "size": mx - mn})
    return comps


def classify_component(comp: dict) -> str:
    c = comp["center"]
    s = comp["size"]
    radial = math.hypot(c.x, c.y)
    area_xy = s.x * s.y
    max_xy = max(s.x, s.y)
    min_xy = min(s.x, s.y)

    # Large circular duct/prop guards and prop disks are translucent in the CUAV
    # reference photos.
    if radial > 0.035 and max_xy > 0.020 and s.z < 0.020:
        return "translucent_prop"

    # Rotor/motor assemblies sit at the four corners below the body.
    if radial > 0.055 and -0.030 < c.z < 0.010:
        if area_xy > 0.00025:
            return "motor_black"
        if s.z < 0.006 and max_xy < 0.012:
            return "copper_winding"
        return "motor_black"

    # MID-360 sits high on the vehicle; dome is blue, base is silver/grey, guard
    # arch is black.
    if c.z > 0.082:
        if s.z > 0.035 and max_xy > 0.035:
            return "guard_black"
        if c.z > 0.104 and max_xy < 0.080:
            return "mid360_blue"
        if max_xy < 0.095:
            return "mid360_silver"
        return "guard_black"

    if c.z > 0.060 and radial < 0.055:
        return "mid360_silver" if max_xy < 0.090 else "guard_black"

    # Camera and central PCB.
    if abs(c.x) < 0.030 and c.y < -0.010 and -0.010 < c.z < 0.045:
        return "camera_glass" if max_xy < 0.035 else "pcb_dark"

    # Tiny high-metal components: screws and standoffs.
    if max_xy < 0.012 and s.z > 0.010:
        return "gold_standoff"
    if max_xy < 0.015 and s.z < 0.010:
        return "metal_screw"

    # Main frame plates, posts, mounts, battery shell, and brackets are black.
    return "carbon_black"


def mesh_object(name: str, verts: list[Vector], faces: list[tuple[int, int, int]], mat: bpy.types.Material) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    mesh.from_pydata([(v.x, v.y, v.z) for v in verts], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj


def build_body_objects(materials: dict[str, bpy.types.Material]) -> tuple[list[bpy.types.Object], dict]:
    verts_raw, faces_raw = read_stl(BODY_STL)
    verts, faces = transformed_mesh(verts_raw, faces_raw, BODY_TRANSFORM)
    comps = connected_components(verts, faces)
    groups: dict[str, list[tuple[int, dict]]] = defaultdict(list)
    for idx, comp in enumerate(comps):
        groups[classify_component(comp)].append((idx, comp))

    objects = []
    summary = {}
    for cls, items in sorted(groups.items()):
        out_verts: list[Vector] = []
        out_faces: list[tuple[int, int, int]] = []
        face_count = 0
        for _, comp in items:
            used = sorted({vi for fi in comp["faces"] for vi in faces[fi]})
            remap = {old: len(out_verts) + i for i, old in enumerate(used)}
            out_verts.extend(verts[old] for old in used)
            out_faces.extend(tuple(remap[vi] for vi in faces[fi]) for fi in comp["faces"])
            face_count += len(comp["faces"])
        objects.append(mesh_object(f"Sunray150_body_{cls}", out_verts, out_faces, materials[cls]))
        summary[cls] = {"components": len(items), "triangles": face_count}
    return objects, {"source": str(BODY_STL), "triangles": len(faces), "components": len(comps), "material_groups": summary}


def build_rotors(materials: dict[str, bpy.types.Material]) -> tuple[list[bpy.types.Object], list[dict]]:
    verts_raw, faces = read_stl(ROTOR_STL)
    objects = []
    manifest = []
    for rotor_name, x, y, z in ROTOR_POSES:
        transform = Matrix.Translation((x, y, z)) @ ROTOR_VISUAL
        verts, _ = transformed_mesh(verts_raw, faces, transform)
        obj = mesh_object(f"Sunray150_rotor_{rotor_name}_translucent", verts, faces, materials["translucent_prop"])
        objects.append(obj)
        manifest.append({"name": obj.name, "source": str(ROTOR_STL), "pose_xyz_m": [x, y, z], "triangles": len(faces), "material": "translucent_prop"})
    return objects, manifest


def frame_scene(objects: list[bpy.types.Object]) -> dict:
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for obj in objects:
        for corner in obj.bound_box:
            w = obj.matrix_world @ Vector(corner)
            mn.x = min(mn.x, w.x)
            mn.y = min(mn.y, w.y)
            mn.z = min(mn.z, w.z)
            mx.x = max(mx.x, w.x)
            mx.y = max(mx.y, w.y)
            mx.z = max(mx.z, w.z)
    center = (mn + mx) * 0.5
    extent = max((mx - mn).x, (mx - mn).y, (mx - mn).z, 0.22)

    light_data = bpy.data.lights.new("Sunray150_Colored_Key_Light", type="AREA")
    light_data.energy = 650
    light_data.size = extent * 0.75
    light = bpy.data.objects.new("Sunray150_Colored_Key_Light", light_data)
    light.location = center + Vector((extent * 0.45, -extent * 0.55, extent * 0.80))
    bpy.context.collection.objects.link(light)

    fill_data = bpy.data.lights.new("Sunray150_Colored_Fill_Light", type="POINT")
    fill_data.energy = 95
    fill = bpy.data.objects.new("Sunray150_Colored_Fill_Light", fill_data)
    fill.location = center + Vector((-extent * 0.55, extent * 0.45, extent * 0.35))
    bpy.context.collection.objects.link(fill)

    cam_data = bpy.data.cameras.new("Sunray150_Colored_Review_Camera")
    cam = bpy.data.objects.new("Sunray150_Colored_Review_Camera", cam_data)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = extent * 1.15
    cam.location = center + Vector((extent * 0.75, -extent * 1.15, extent * 0.62))
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return {"bounds_min": [mn.x, mn.y, mn.z], "bounds_max": [mx.x, mx.y, mx.z], "active_camera": cam.name}


def build_asset() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reset_scene()
    start = time.time()
    materials = {name: make_material(name, cfg) for name, cfg in PALETTE.items()}
    body_objects, body_manifest = build_body_objects(materials)
    rotor_objects, rotor_manifest = build_rotors(materials)
    objects = body_objects + rotor_objects
    camera_info = frame_scene(objects)
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.world.color = (0.78, 0.80, 0.83)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
    bpy.ops.export_scene.fbx(filepath=str(OUT_FBX), use_selection=False, add_leaf_bones=False, path_mode="COPY")
    bpy.ops.export_scene.gltf(filepath=str(OUT_GLB), export_format="GLB")

    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "purpose": "Colored Sunray150 review asset from accepted STL runtime geometry; radar is colored in place, not remounted.",
        "sources": {
            "body_stl": str(BODY_STL),
            "rotor_stl": str(ROTOR_STL),
            "reference_images": [
                str(PROJECT_ROOT / "References" / "CUAV" / "Sunray150-正.png"),
                str(PROJECT_ROOT / "References" / "CUAV" / "Sunray150-侧.png"),
                str(PROJECT_ROOT / "References" / "CUAV" / "MId360.png"),
                str(PROJECT_ROOT / "References" / "CUAV" / "motor.png"),
            ],
            "web_reference": "https://wiki.yundrone.cn/docs/dong-li-xi-tong",
        },
        "body": body_manifest,
        "rotors": rotor_manifest,
        "palette": {k: v["rgba"] for k, v in PALETTE.items()},
        "review_camera": camera_info,
        "rules": [
            "Do not use the rejected DAE radar/propeller assembly path for this asset.",
            "sunray.stl already contains the MID-360; color that geometry in place.",
            "STL has no material names, so this is connected-component geometric coloring and requires manual visual audit.",
            "CUAV reference photos show black carbon frame/guards, silver MID-360 body, blue MID-360 dome, translucent grey ducts/propellers, black motors with copper windings, and metal/gold fasteners.",
        ],
        "elapsed_sec": round(time.time() - start, 3),
        "outputs": {"blend": str(OUT_BLEND), "fbx": str(OUT_FBX), "glb": str(OUT_GLB), "manifest": str(OUT_MANIFEST)},
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2)[:8000])
    return manifest


if __name__ == "__main__":
    build_asset()
