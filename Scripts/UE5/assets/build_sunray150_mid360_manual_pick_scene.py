#!/usr/bin/env python3
"""Build a manual pick scene for Sunray150 MID-360 mounting points.

The scene is deliberately not an automatic alignment result. It lays out:

- Axx: candidate aircraft-frame screw points from the Sunray150 DAE.
- Bxx: candidate standalone MID-360 bottom mounting-hole reference points.

The user picks two ordered sets of four labels. A later script can compute the
rigid transform/scale check from those two sets.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import time
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROP_AUDIT = PROJECT_ROOT / "Scripts" / "UE5" / "assets" / "build_sunray150_with_mid360_propeller_assembly_audit_scene.py"
LIVOX_AUDIT = PROJECT_ROOT / "Scripts" / "UE5" / "assets" / "build_livox_mid360_audit_scene.py"
OUT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
OUT_BLEND = OUT_DIR / "sunray150_mid360_manual_pick.blend"
OUT_MANIFEST = OUT_DIR / "sunray150_mid360_manual_pick_manifest.json"

AIRCRAFT_OFFSET = Vector((-0.14, 0.0, 0.0))
RADAR_OFFSET = Vector((0.14, 0.0, 0.0))


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


prop = load_module(PROP_AUDIT, "sunray_prop_audit_manual_pick")
livox = load_module(LIVOX_AUDIT, "livox_mid360_audit_manual_pick")


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
        bsdf.inputs["Roughness"].default_value = 0.5
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = rgba[3]
    if rgba[3] < 1.0:
        mat.blend_method = "BLEND"
    return mat


def clean_name(name: str) -> str:
    return prop.clean_name(name, 128)


def add_mesh(name: str, verts: list[tuple[float, float, float]], faces: list[tuple[int, int, int]], mat: bpy.types.Material, offset: Vector) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(f"{clean_name(name)}_Mesh")
    mesh.from_pydata([(x + offset.x, y + offset.y, z + offset.z) for x, y, z in verts], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(clean_name(name), mesh)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj


def add_sphere(name: str, loc: Vector, radius: float, mat: bpy.types.Material) -> None:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = clean_name(name)
    obj.data.materials.append(mat)


def add_text(name: str, text: str, loc: Vector, size: float, mat: bpy.types.Material) -> None:
    curve = bpy.data.curves.new(clean_name(name), type="FONT")
    curve.body = text
    curve.size = size
    curve.align_x = "CENTER"
    obj = bpy.data.objects.new(clean_name(name), curve)
    obj.location = loc
    obj.rotation_euler = (math.radians(65), 0, 0)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)


def add_cylinder_between(name: str, a: Vector, b: Vector, radius: float, mat: bpy.types.Material) -> None:
    direction = b - a
    if direction.length < 1e-8:
        return
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=direction.length, location=(a + b) * 0.5)
    obj = bpy.context.object
    obj.name = clean_name(name)
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)


def is_hidden_dae_part(name: str) -> bool:
    upper = name.upper()
    return any(k in upper for k in ("PROPELLER", "MID360", "MID-360", "RANGING_LIDAR", "LIVOX", "PROTECT_ARC"))


def candidate_aircraft_screws(dae_objects: list, limit: int = 28) -> list:
    screws = [o for o in dae_objects if "SCREW" in o.name.upper()]
    # Center of the four tiny MID-360 hole/reference objects in the DAE source.
    radar_hole_like = [o for o in dae_objects if "MID-360_4_ASM" in o.name.upper()]
    if radar_hole_like:
        center = sum((o.center for o in radar_hole_like), Vector()) / len(radar_hole_like)
    else:
        center = Vector((0.0, 0.0335, 0.0597))
    return sorted(screws, key=lambda o: (o.center - center).length)[:limit]


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


def livox_mount_point_candidates() -> list[tuple[str, Vector]]:
    """Initial manual-pick points on the reviewed local-origin MID-360 base.

    These are not committed geometry facts. They are only numbered visual pick
    helpers around the bottom mount rectangle/ring, so the user can choose the
    correct four after inspecting the model.
    """
    # DAE MID-360_4_ASM hole-like reference rectangle, recentered around its
    # average. It gives useful candidate spacing without using the DAE radar as
    # final geometry.
    dx = 0.024584
    dy = 0.018776
    ring = [
        ("B01", Vector((-dx, -dy, 0.0))),
        ("B02", Vector((dx, -dy, 0.0))),
        ("B03", Vector((-dx, dy, 0.0))),
        ("B04", Vector((dx, dy, 0.0))),
    ]
    # Extra cardinal candidates on the circular base in case the visible holes
    # are better picked from the base disk rather than the DAE hole rectangle.
    r = 0.028
    ring.extend(
        [
            ("B05", Vector((-r, 0.0, 0.0))),
            ("B06", Vector((r, 0.0, 0.0))),
            ("B07", Vector((0.0, -r, 0.0))),
            ("B08", Vector((0.0, r, 0.0))),
        ]
    )
    return ring


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
    extent = max((mx - mn).x, (mx - mn).y, (mx - mn).z, 0.35)
    light_data = bpy.data.lights.new("ManualPick_Key_Light", type="AREA")
    light_data.energy = 1200
    light_data.size = extent
    light = bpy.data.objects.new("ManualPick_Key_Light", light_data)
    light.location = center + Vector((extent * 0.25, -extent * 0.45, extent * 0.8))
    bpy.context.collection.objects.link(light)
    cam_data = bpy.data.cameras.new("ManualPick_Review_Camera")
    cam = bpy.data.objects.new("ManualPick_Review_Camera", cam_data)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = extent * 1.05
    cam.location = center + Vector((extent * 0.25, -extent * 0.95, extent * 0.6))
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reset_scene()

    body_mat = make_material("DAE_Frame_Transparent_Grey", (0.32, 0.32, 0.30, 0.24))
    screw_mat = make_material("A_Frame_Screw_Gold", (1.0, 0.62, 0.02, 1.0))
    radar_mat = make_material("Standalone_MID360_BlueGrey", (0.08, 0.17, 0.28, 0.70))
    b_mat = make_material("B_Radar_Hole_Cyan", (0.0, 0.8, 1.0, 1.0))
    line_mat = make_material("Candidate_Line_Green", (0.0, 0.88, 0.18, 1.0))
    text_mat = make_material("ManualPick_Text_Black", (0.02, 0.02, 0.02, 1.0))

    dae = prop.dae_objects(prop.DAE_PATH)
    hidden = 0
    for obj in dae:
        if is_hidden_dae_part(obj.name):
            hidden += 1
            continue
        add_mesh(f"A_DAE_frame_{obj.name}", obj.verts, obj.faces, body_mat, AIRCRAFT_OFFSET)

    a_candidates = candidate_aircraft_screws(dae)
    a_manifest = []
    for idx, screw in enumerate(a_candidates, start=1):
        label = f"A{idx:02d}"
        loc = screw.center + AIRCRAFT_OFFSET
        add_mesh(f"{label}_mesh_{screw.name}", screw.verts, screw.faces, screw_mat, AIRCRAFT_OFFSET)
        add_sphere(f"{label}_center", loc, 0.0018, screw_mat)
        add_text(f"{label}_label", label, loc + Vector((0, 0, 0.006)), 0.0048, text_mat)
        a_manifest.append({"label": label, "name": screw.name, "center_m": [round(screw.center.x, 6), round(screw.center.y, 6), round(screw.center.z, 6)]})

    prefix = "B_livox_mid360"
    livox.import_dae(
        livox.MID360_DAE,
        prefix,
        livox.pose_matrix(0, 0, 0, 0, 0, 3.14159) @ livox.matrix_scale_xyz(1.2, 1.2, 1.2),
    )
    base_center = livox_base_center_before_recenter(prefix)
    translate_objects(prefix, -base_center + RADAR_OFFSET)
    for obj in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith(prefix)]:
        obj.data.materials.clear()
        obj.data.materials.append(radar_mat)

    b_manifest = []
    for label, local in livox_mount_point_candidates():
        loc = local + RADAR_OFFSET
        add_sphere(f"{label}_candidate", loc, 0.0018, b_mat)
        add_text(f"{label}_label", label, loc + Vector((0, 0, 0.006)), 0.0048, text_mat)
        add_cylinder_between(f"{label}_to_B_origin", RADAR_OFFSET, loc, 0.00022, line_mat)
        b_manifest.append({"label": label, "local_point_m": [round(local.x, 6), round(local.y, 6), round(local.z, 6)]})

    add_sphere("B00_mid360_base_origin", RADAR_OFFSET, 0.0022, line_mat)
    add_text("A_title", "A: aircraft frame screw candidates", AIRCRAFT_OFFSET + Vector((0.0, -0.105, 0.11)), 0.007, text_mat)
    add_text("B_title", "B: MID-360 bottom mount candidates", RADAR_OFFSET + Vector((0.0, -0.105, 0.11)), 0.007, text_mat)
    add_text("instruction", "Reply with ordered labels, e.g. A03 A04 A09 A10 -> B01 B02 B03 B04", Vector((0.0, -0.15, 0.15)), 0.006, text_mat)

    frame_camera()
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.world.color = (0.86, 0.88, 0.90)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))

    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "purpose": "Manual point picking for DAE-derived Sunray150 MID-360 replacement. No automatic alignment is accepted from this scene.",
        "sources": {"dae_aircraft": str(prop.DAE_PATH), "standalone_mid360": str(livox.MID360_DAE)},
        "hidden_dae_parts_count": hidden,
        "aircraft_offset": list(AIRCRAFT_OFFSET),
        "radar_offset": list(RADAR_OFFSET),
        "A_aircraft_screw_candidates": a_manifest,
        "B_radar_mount_candidates": b_manifest,
        "instruction": "User must pick ordered four A labels and ordered four B labels before transform/scale solving.",
        "status": "manual_pick_required",
        "elapsed_sec": round(time.time() - start, 3),
        "outputs": {"blend": str(OUT_BLEND), "manifest": str(OUT_MANIFEST)},
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2)[:10000])


if __name__ == "__main__":
    main()
