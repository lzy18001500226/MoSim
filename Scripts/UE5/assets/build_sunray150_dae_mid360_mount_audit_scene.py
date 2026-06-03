#!/usr/bin/env python3
"""Build a DAE-based MID-360 mount audit scene.

This scene is for manual alignment review only. It uses the Sunray150 DAE as
the colored/semantic aircraft source, hides the DAE's own radar and propellers,
then imports the standalone Livox MID-360 visual with the reviewed local origin.
The first gate is visual: aircraft frame screw candidates must match the radar
bottom mount holes before this route can become a runtime visual asset.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
PROP_AUDIT = PROJECT_ROOT / "Scripts" / "UE5" / "assets" / "build_sunray150_with_mid360_propeller_assembly_audit_scene.py"
LIVOX_AUDIT = PROJECT_ROOT / "Scripts" / "UE5" / "assets" / "build_livox_mid360_audit_scene.py"
OUT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
OUT_BLEND = OUT_DIR / "sunray150_dae_mid360_mount_audit.blend"
OUT_MANIFEST = OUT_DIR / "sunray150_dae_mid360_mount_audit_manifest.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


prop = load_module(PROP_AUDIT, "sunray_prop_audit")
livox = load_module(LIVOX_AUDIT, "livox_mid360_audit")


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for item in list(block):
            block.remove(item)


def make_material(name: str, rgba: tuple[float, float, float, float]) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = 0.48
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = rgba[3]
    if rgba[3] < 1.0:
        mat.blend_method = "BLEND"
    return mat


def clean_name(name: str) -> str:
    return prop.clean_name(name, 128)


def add_mesh(name: str, verts: list[tuple[float, float, float]], faces: list[tuple[int, int, int]], mat: bpy.types.Material) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(f"{clean_name(name)}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(clean_name(name), mesh)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj


def add_sphere(name: str, loc: Vector, radius: float, mat: bpy.types.Material) -> None:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = clean_name(name)
    obj.data.materials.append(mat)


def add_cylinder_between(name: str, a: Vector, b: Vector, radius: float, mat: bpy.types.Material) -> None:
    direction = b - a
    if direction.length < 1e-8:
        return
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=direction.length, location=(a + b) * 0.5)
    obj = bpy.context.object
    obj.name = clean_name(name)
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)


def add_text(name: str, text: str, loc: Vector, size: float, mat: bpy.types.Material) -> None:
    curve = bpy.data.curves.new(clean_name(name), type="FONT")
    curve.body = text
    curve.size = size
    curve.align_x = "CENTER"
    obj = bpy.data.objects.new(clean_name(name), curve)
    obj.location = loc
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)


def is_hidden_dae_part(name: str) -> bool:
    upper = name.upper()
    hidden_keys = ("PROPELLER", "MID360", "MID-360", "RANGING_LIDAR", "LIVOX", "PROTECT_ARC")
    return any(k in upper for k in hidden_keys)


def choose_mount_screws(dae_objects: list) -> list:
    """Pick DAE screw candidates around the existing DAE MID-360 mount pattern."""
    screws = [o for o in dae_objects if "SCREW" in o.name.upper()]
    radar_hole_like = [o for o in dae_objects if "MID-360_4_ASM" in o.name.upper()]
    if len(radar_hole_like) >= 4:
        center = sum((o.center for o in radar_hole_like), Vector()) / len(radar_hole_like)
    else:
        center = Vector((0.0, 0.0335, 0.0597))
    return sorted(screws, key=lambda o: (o.center - center).length)[:4]


def livox_base_center_before_recenter(prefix: str) -> Vector:
    candidates = []
    for obj in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith(prefix)]:
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
        if size.x > 0.05 and size.y > 0.05 and size.z < 0.02 and abs(size.x - size.y) < 0.003:
            candidates.append((obj, mn, mx, size, (mn + mx) * 0.5))
    if not candidates:
        raise RuntimeError("Cannot identify Livox circular base mesh.")
    return max(candidates, key=lambda item: item[3].x * item[3].y)[4]


def translate_objects(prefix: str, translation: Vector) -> None:
    for obj in [o for o in bpy.context.scene.objects if o.name.startswith(prefix)]:
        obj.location += translation


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
    extent = max((mx - mn).x, (mx - mn).y, (mx - mn).z, 0.18)
    light_data = bpy.data.lights.new("Mid360MountAudit_Key_Light", type="AREA")
    light_data.energy = 900
    light_data.size = extent
    light = bpy.data.objects.new("Mid360MountAudit_Key_Light", light_data)
    light.location = center + Vector((extent * 0.45, -extent * 0.55, extent * 0.8))
    bpy.context.collection.objects.link(light)
    cam_data = bpy.data.cameras.new("Mid360MountAudit_Camera")
    cam = bpy.data.objects.new("Mid360MountAudit_Camera", cam_data)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = extent * 1.15
    cam.location = center + Vector((extent * 0.4, -extent * 1.0, extent * 0.55))
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reset_scene()

    body_mat = make_material("DAE_Cleaned_Body_Grey", (0.28, 0.28, 0.27, 0.38))
    screw_mat = make_material("DAE_Frame_Mount_Screws_Gold", (1.0, 0.66, 0.04, 1.0))
    radar_mat = make_material("Standalone_MID360_BlueGrey", (0.08, 0.16, 0.28, 0.82))
    line_mat = make_material("Mount_Match_Lines_Green", (0.0, 0.85, 0.16, 1.0))
    text_mat = make_material("Audit_Text_Black", (0.02, 0.02, 0.02, 1.0))

    dae = prop.dae_objects(prop.DAE_PATH)
    hidden_count = 0
    for obj in dae:
        if is_hidden_dae_part(obj.name):
            hidden_count += 1
            continue
        add_mesh(f"DAE_body_clean_{obj.name}", obj.verts, obj.faces, body_mat)

    mount_screws = choose_mount_screws(dae)
    mount_center = sum((o.center for o in mount_screws), Vector()) / len(mount_screws)
    for idx, screw in enumerate(mount_screws):
        add_mesh(f"DAE_mid360_mount_screw_{idx}_{screw.name}", screw.verts, screw.faces, screw_mat)
        add_sphere(f"DAE_mid360_mount_screw_center_{idx}", screw.center, 0.0016, screw_mat)
        add_cylinder_between(f"DAE_mount_center_to_screw_{idx}", mount_center, screw.center, 0.0003, line_mat)

    # Import standalone MID-360 with the reviewed connector direction, then move
    # its circular base center to the DAE screw pattern center for first audit.
    prefix = "AUDIT_livox_mid360"
    livox.import_dae(
        livox.MID360_DAE,
        prefix,
        livox.pose_matrix(0, 0, 0, 0, 0, 3.14159) @ livox.matrix_scale_xyz(1.2, 1.2, 1.2),
    )
    base_center = livox_base_center_before_recenter(prefix)
    translate_objects(prefix, -base_center)
    translate_objects(prefix, mount_center)
    for obj in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith(prefix)]:
        obj.data.materials.clear()
        obj.data.materials.append(radar_mat)

    add_sphere("DAE_mid360_mount_pattern_center", mount_center, 0.0022, line_mat)
    add_text(
        "mount_audit_label",
        "MID-360 mount audit: gold = DAE frame screw candidates, green = candidate mount center/lines",
        mount_center + Vector((0, -0.06, 0.055)),
        0.005,
        text_mat,
    )

    frame_camera()
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.world.color = (0.86, 0.88, 0.90)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "purpose": "DAE-derived aircraft cleaning route, MID-360 mount audit only. DAE radar/propellers are hidden; standalone MID-360 is placed at frame screw-pattern center for manual review.",
        "sources": {
            "dae_aircraft": str(prop.DAE_PATH),
            "standalone_mid360": str(livox.MID360_DAE),
        },
        "hidden_dae_parts": {
            "rule": "hide DAE PROPELLER/MID360/RANGING_LIDAR/LIVOX/PROTECT_ARC parts before replacement",
            "count": hidden_count,
        },
        "mount_screws": [
            {
                "name": o.name,
                "center_m": [round(o.center.x, 6), round(o.center.y, 6), round(o.center.z, 6)],
                "bounds_min_m": [round(o.min_bound.x, 6), round(o.min_bound.y, 6), round(o.min_bound.z, 6)],
                "bounds_max_m": [round(o.max_bound.x, 6), round(o.max_bound.y, 6), round(o.max_bound.z, 6)],
            }
            for o in mount_screws
        ],
        "candidate_mount_center_m": [round(mount_center.x, 6), round(mount_center.y, 6), round(mount_center.z, 6)],
        "mid360_rule": "standalone MID-360 uses reviewed yaw=pi and local origin at circular base center before translation to candidate mount center",
        "status": "manual_review_required_before_using_as_runtime_visual",
        "elapsed_sec": round(time.time() - start, 3),
        "outputs": {"blend": str(OUT_BLEND), "manifest": str(OUT_MANIFEST)},
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2)[:8000])


if __name__ == "__main__":
    main()
