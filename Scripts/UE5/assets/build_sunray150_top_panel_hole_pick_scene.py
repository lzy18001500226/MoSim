#!/usr/bin/env python3
"""Build a manual pick scene for TOP_PANNEL hole centers.

This is for the DAE-derived visual route. It extracts boundary loops from the
carbon top-plate mesh instead of guessing screw-object centers. The user picks
the four `Hxx` labels on the carbon plate that correspond to the MID-360 mount,
then maps them to the ordered four `Bxx` radar bottom candidates.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import time
from collections import defaultdict, deque
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROP_AUDIT = PROJECT_ROOT / "Scripts" / "UE5" / "assets" / "build_sunray150_with_mid360_propeller_assembly_audit_scene.py"
LIVOX_AUDIT = PROJECT_ROOT / "Scripts" / "UE5" / "assets" / "build_livox_mid360_audit_scene.py"
OUT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
OUT_BLEND = OUT_DIR / "sunray150_top_panel_hole_pick.blend"
OUT_MANIFEST = OUT_DIR / "sunray150_top_panel_hole_pick_manifest.json"

PANEL_OFFSET = Vector((-0.12, 0.0, 0.0))
RADAR_OFFSET = Vector((0.14, 0.0, 0.0))


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


prop = load_module(PROP_AUDIT, "sunray_prop_audit_top_panel")
livox = load_module(LIVOX_AUDIT, "livox_mid360_audit_top_panel")


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


def add_mesh(name: str, verts: list[tuple[float, float, float]], faces: list[tuple[int, int, int]], mat: bpy.types.Material, offset: Vector) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(f"{prop.clean_name(name, 128)}_Mesh")
    mesh.from_pydata([(x + offset.x, y + offset.y, z + offset.z) for x, y, z in verts], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(prop.clean_name(name, 128), mesh)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj


def add_sphere(name: str, loc: Vector, radius: float, mat: bpy.types.Material) -> None:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = prop.clean_name(name, 96)
    obj.data.materials.append(mat)


def add_text(name: str, text: str, loc: Vector, size: float, mat: bpy.types.Material) -> None:
    curve = bpy.data.curves.new(prop.clean_name(name, 96), type="FONT")
    curve.body = text
    curve.size = size
    curve.align_x = "CENTER"
    obj = bpy.data.objects.new(prop.clean_name(name, 96), curve)
    obj.location = loc
    obj.rotation_euler = (math.radians(65), 0, 0)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)


def quantize(v: tuple[float, float, float], tol: float = 1e-6) -> tuple[int, int, int]:
    return (round(v[0] / tol), round(v[1] / tol), round(v[2] / tol))


def welded_faces(verts: list[tuple[float, float, float]], faces: list[tuple[int, int, int]]) -> tuple[list[Vector], list[tuple[int, int, int]]]:
    key_to_index: dict[tuple[int, int, int], int] = {}
    welded: list[Vector] = []
    remap: dict[int, int] = {}
    for idx, v in enumerate(verts):
        key = quantize(v)
        if key not in key_to_index:
            key_to_index[key] = len(welded)
            welded.append(Vector(v))
        remap[idx] = key_to_index[key]
    new_faces = []
    for f in faces:
        rf = (remap[f[0]], remap[f[1]], remap[f[2]])
        if len(set(rf)) == 3:
            new_faces.append(rf)
    return welded, new_faces


def boundary_components(verts: list[tuple[float, float, float]], faces: list[tuple[int, int, int]]) -> list[dict]:
    welded, wfaces = welded_faces(verts, faces)
    edge_count: dict[tuple[int, int], int] = defaultdict(int)
    for a, b, c in wfaces:
        for u, v in ((a, b), (b, c), (c, a)):
            edge_count[tuple(sorted((u, v)))] += 1
    boundary_edges = [e for e, count in edge_count.items() if count == 1]
    graph: dict[int, set[int]] = defaultdict(set)
    for a, b in boundary_edges:
        graph[a].add(b)
        graph[b].add(a)

    seen: set[int] = set()
    comps = []
    for start in graph:
        if start in seen:
            continue
        q = deque([start])
        seen.add(start)
        nodes = []
        while q:
            node = q.popleft()
            nodes.append(node)
            for nxt in graph[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        pts = [welded[i] for i in nodes]
        mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        size = mx - mn
        center = sum(pts, Vector()) / len(pts)
        comps.append({"nodes": nodes, "center": center, "min": mn, "max": mx, "size": size, "count": len(nodes)})
    return comps


def choose_top_panel(dae_objects: list):
    panels = [o for o in dae_objects if "TOP_PANNEL.1" in o.name.upper() and "TOP" in o.name.upper()]
    if panels:
        return max(panels, key=lambda o: len(o.faces))
    panels = [o for o in dae_objects if "TOP_PANNEL" in o.name.upper()]
    if panels:
        return max(panels, key=lambda o: len(o.faces))
    raise RuntimeError("Cannot find TOP_PANNEL object in DAE.")


def hole_candidates(panel) -> list[dict]:
    comps = boundary_components(panel.verts, panel.faces)
    # Keep non-outer small and medium cutout loops. The largest component is the
    # outer carbon-plate silhouette and is excluded.
    outer = max(comps, key=lambda c: c["size"].x * c["size"].y)
    candidates = []
    for comp in comps:
        if comp is outer:
            continue
        sx, sy = comp["size"].x, comp["size"].y
        area_box = sx * sy
        # Exclude the large long slots/triangles; keep screw-hole-scale and
        # small square/round features visible on the carbon plate.
        if 0.000002 <= area_box <= 0.0008 and max(sx, sy) <= 0.035:
            candidates.append(comp)
    return sorted(candidates, key=lambda c: (-c["center"].y, c["center"].x, c["center"].z))


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
            candidates.append((obj, size, (mn + mx) * 0.5))
    if not candidates:
        raise RuntimeError("Cannot identify Livox circular base mesh.")
    return max(candidates, key=lambda item: item[1].x * item[1].y)[2]


def translate_objects(prefix: str, translation: Vector) -> None:
    for obj in [o for o in bpy.context.scene.objects if o.name.startswith(prefix)]:
        obj.location += translation


def radar_candidates() -> list[tuple[str, Vector]]:
    dx = 0.024584
    dy = 0.018776
    r = 0.028
    return [
        ("B01", Vector((-dx, -dy, 0.0))),
        ("B02", Vector((dx, -dy, 0.0))),
        ("B03", Vector((-dx, dy, 0.0))),
        ("B04", Vector((dx, dy, 0.0))),
        ("B05", Vector((-r, 0.0, 0.0))),
        ("B06", Vector((r, 0.0, 0.0))),
        ("B07", Vector((0.0, -r, 0.0))),
        ("B08", Vector((0.0, r, 0.0))),
    ]


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
    extent = max((mx - mn).x, (mx - mn).y, (mx - mn).z, 0.33)
    light_data = bpy.data.lights.new("TopPanelHolePick_Key_Light", type="AREA")
    light_data.energy = 1100
    light_data.size = extent
    light = bpy.data.objects.new("TopPanelHolePick_Key_Light", light_data)
    light.location = center + Vector((extent * 0.25, -extent * 0.45, extent * 0.8))
    bpy.context.collection.objects.link(light)
    cam_data = bpy.data.cameras.new("TopPanelHolePick_Camera")
    cam = bpy.data.objects.new("TopPanelHolePick_Camera", cam_data)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = extent * 1.0
    cam.location = center + Vector((0.0, 0.0, extent * 1.8))
    cam.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reset_scene()

    panel_mat = make_material("DAE_TOP_PANNEL_Transparent_Carbon", (0.20, 0.20, 0.18, 0.35))
    hole_mat = make_material("H_Carbon_Plate_Hole_Magenta", (1.0, 0.08, 0.75, 1.0))
    radar_mat = make_material("Standalone_MID360_BlueGrey", (0.08, 0.17, 0.28, 0.68))
    b_mat = make_material("B_Radar_Candidate_Cyan", (0.0, 0.8, 1.0, 1.0))
    text_mat = make_material("HolePick_Text_Black", (0.02, 0.02, 0.02, 1.0))

    dae = prop.dae_objects(prop.DAE_PATH)
    panel = choose_top_panel(dae)
    add_mesh("DAE_TOP_PANNEL_only", panel.verts, panel.faces, panel_mat, PANEL_OFFSET)

    holes = hole_candidates(panel)
    h_manifest = []
    for idx, hole in enumerate(holes, start=1):
        label = f"H{idx:02d}"
        loc = hole["center"] + PANEL_OFFSET
        radius = min(max(max(hole["size"].x, hole["size"].y) * 0.18, 0.001), 0.003)
        add_sphere(f"{label}_hole_center", loc, radius, hole_mat)
        add_text(f"{label}_label", label, loc + Vector((0, 0, 0.006)), 0.0045, text_mat)
        h_manifest.append(
            {
                "label": label,
                "center_m": [round(hole["center"].x, 6), round(hole["center"].y, 6), round(hole["center"].z, 6)],
                "size_m": [round(hole["size"].x, 6), round(hole["size"].y, 6), round(hole["size"].z, 6)],
                "boundary_vertex_count": hole["count"],
            }
        )

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
    for label, local in radar_candidates():
        loc = local + RADAR_OFFSET
        add_sphere(f"{label}_candidate", loc, 0.0018, b_mat)
        add_text(f"{label}_label", label, loc + Vector((0, 0, 0.006)), 0.0045, text_mat)
        b_manifest.append({"label": label, "local_point_m": [round(local.x, 6), round(local.y, 6), round(local.z, 6)]})

    add_text("H_title", "H: TOP_PANNEL boundary hole candidates", PANEL_OFFSET + Vector((0.0, -0.12, 0.09)), 0.006, text_mat)
    add_text("B_title", "B: MID-360 bottom mount candidates", RADAR_OFFSET + Vector((0.0, -0.12, 0.09)), 0.006, text_mat)
    add_text("instruction", "Reply: Hxx Hxx Hxx Hxx -> Bxx Bxx Bxx Bxx", Vector((0.0, -0.16, 0.13)), 0.006, text_mat)

    frame_camera()
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.world.color = (0.86, 0.88, 0.90)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))

    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "purpose": "Manual selection of TOP_PANNEL hole centers for MID-360 mounting. Uses boundary loops from the DAE carbon plate, not screw objects.",
        "sources": {"dae_aircraft": str(prop.DAE_PATH), "standalone_mid360": str(livox.MID360_DAE)},
        "panel_object": panel.name,
        "panel_offset": list(PANEL_OFFSET),
        "radar_offset": list(RADAR_OFFSET),
        "H_top_panel_hole_candidates": h_manifest,
        "B_radar_mount_candidates": b_manifest,
        "instruction": "User must choose ordered four H labels and ordered four B labels before transform/scale solving.",
        "status": "manual_pick_required",
        "elapsed_sec": round(time.time() - start, 3),
        "outputs": {"blend": str(OUT_BLEND), "manifest": str(OUT_MANIFEST)},
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2)[:10000])


if __name__ == "__main__":
    main()
