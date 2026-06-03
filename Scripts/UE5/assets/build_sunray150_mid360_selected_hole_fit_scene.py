#!/usr/bin/env python3
"""Build selected-hole MID-360 fit audit scenes.

Uses the user-selected TOP_PANNEL boundary-loop groups as four physical mount
holes and compares them with the standalone MID-360 bottom candidates.

The radar connector must face the aircraft tail, and the MID-360 bottom face
must sit on the top surface of the carbon TOP_PANNEL. This scene shows explicit
90/270 degree radar-body rotation candidates for manual audit. This is a
diagnostic, not an accepted runtime asset.
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
TOP_PICK_SCRIPT = PROJECT_ROOT / "Scripts" / "UE5" / "assets" / "build_sunray150_top_panel_hole_pick_scene.py"
LIVOX_AUDIT = PROJECT_ROOT / "Scripts" / "UE5" / "assets" / "build_livox_mid360_audit_scene.py"
TOP_PICK_MANIFEST = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit" / "sunray150_top_panel_hole_pick_manifest.json"
OUT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
OUT_BLEND = OUT_DIR / "sunray150_mid360_selected_hole_fit.blend"
OUT_MANIFEST = OUT_DIR / "sunray150_mid360_selected_hole_fit_manifest.json"

HOLE_GROUPS = {
    "P01_left_upper": ["H20", "H21", "H22"],
    "P02_right_upper": ["H19", "H23", "H24"],
    "P03_right_lower": ["H44", "H47", "H48"],
    "P04_left_lower": ["H43", "H45", "H46"],
}

# Current radar bottom candidates. User said to use the visible radar points in
# the picture; this is still a diagnostic until those B points are accepted.
RADAR_POINTS = {
    "B01_left_lower": Vector((-0.024584, -0.018776, 0.0)),
    "B02_right_lower": Vector((0.024584, -0.018776, 0.0)),
    "B03_left_upper": Vector((-0.024584, 0.018776, 0.0)),
    "B04_right_upper": Vector((0.024584, 0.018776, 0.0)),
}

PANEL_CORNER_ORDER = [
    ("P03_right_lower", "right_lower"),
    ("P04_left_lower", "left_lower"),
    ("P02_right_upper", "right_upper"),
    ("P01_left_upper", "left_upper"),
]

YAW_CANDIDATES = [
    {
        "name": "MID360_tail_connector_yaw90",
        "yaw_deg": 90.0,
        "display_offset": Vector((-0.13, 0.0, 0.0)),
        "note": "Candidate with radar body rotated +90 deg; connector must face tail -X and bottom face must sit on TOP_PANNEL top surface.",
    },
    {
        "name": "MID360_tail_connector_yaw270",
        "yaw_deg": 270.0,
        "display_offset": Vector((0.13, 0.0, 0.0)),
        "note": "Candidate with radar body rotated -90/270 deg; connector must face tail -X and bottom face must sit on TOP_PANNEL top surface.",
    },
]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


top_pick = load_module(TOP_PICK_SCRIPT, "sunray_top_pick_fit")
livox = load_module(LIVOX_AUDIT, "livox_mid360_fit")


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


def add_sphere(name: str, loc: Vector, radius: float, mat: bpy.types.Material) -> None:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = top_pick.prop.clean_name(name, 96)
    obj.data.materials.append(mat)


def add_text(name: str, text: str, loc: Vector, size: float, mat: bpy.types.Material) -> None:
    curve = bpy.data.curves.new(top_pick.prop.clean_name(name, 96), type="FONT")
    curve.body = text
    curve.size = size
    curve.align_x = "CENTER"
    obj = bpy.data.objects.new(top_pick.prop.clean_name(name, 96), curve)
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
    obj.name = top_pick.prop.clean_name(name, 96)
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)


def add_mesh(
    name: str,
    verts: list[tuple[float, float, float]],
    faces: list[tuple[int, int, int]],
    mat: bpy.types.Material,
    offset: Vector | None = None,
) -> None:
    offset = offset or Vector()
    mesh = bpy.data.meshes.new(f"{top_pick.prop.clean_name(name, 128)}_Mesh")
    mesh.from_pydata([(x + offset.x, y + offset.y, z + offset.z) for x, y, z in verts], [], faces)
    mesh.update()
    obj = bpy.data.objects.new(top_pick.prop.clean_name(name, 128), mesh)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)


def selected_panel_points() -> dict[str, Vector]:
    data = json.loads(TOP_PICK_MANIFEST.read_text(encoding="utf-8"))
    lookup = {h["label"]: Vector(h["center_m"]) for h in data["H_top_panel_hole_candidates"]}
    out = {}
    for name, labels in HOLE_GROUPS.items():
        pts = [lookup[label] for label in labels]
        out[name] = sum(pts, Vector()) / len(pts)
    return out


def rotate_z(point: Vector, theta: float) -> Vector:
    c, s = math.cos(theta), math.sin(theta)
    return Vector((c * point.x - s * point.y, s * point.x + c * point.y, point.z))


def quadrant_lookup(points: dict[str, Vector]) -> dict[str, tuple[str, Vector]]:
    center = sum(points.values(), Vector()) / len(points)
    out: dict[str, tuple[str, Vector]] = {}
    for name, point in points.items():
        x_side = "right" if point.x >= center.x else "left"
        y_side = "upper" if point.y >= center.y else "lower"
        out[f"{x_side}_{y_side}"] = (name, point)
    return out


def fit_similarity_2d(src: list[Vector], dst: list[Vector]) -> tuple[float, float, Vector, list[Vector], float]:
    """Fit uniform-scale 2D similarity from src XY to dst XY."""
    src_c = sum(src, Vector()) / len(src)
    dst_c = sum(dst, Vector()) / len(dst)
    x = [p - src_c for p in src]
    y = [p - dst_c for p in dst]
    a = sum(xi.x * yi.x + xi.y * yi.y for xi, yi in zip(x, y))
    b = sum(xi.x * yi.y - xi.y * yi.x for xi, yi in zip(x, y))
    denom = sum(xi.x * xi.x + xi.y * xi.y for xi in x)
    scale = math.sqrt(a * a + b * b) / denom if denom > 1e-12 else 1.0
    theta = math.atan2(b, a)
    c, s = math.cos(theta), math.sin(theta)
    fitted = []
    errors = []
    z = sum(p.z for p in dst) / len(dst)
    for p, q in zip(src, dst):
        rel = p - src_c
        mapped = Vector((scale * (c * rel.x - s * rel.y), scale * (s * rel.x + c * rel.y), 0.0)) + Vector((dst_c.x, dst_c.y, z))
        fitted.append(mapped)
        errors.append((mapped - q).length)
    rms = math.sqrt(sum(e * e for e in errors) / len(errors))
    return scale, theta, Vector((dst_c.x, dst_c.y, z)) - Vector((scale * (c * src_c.x - s * src_c.y), scale * (s * src_c.x + c * src_c.y), 0.0)), fitted, rms


def fit_fixed_yaw_2d(src_rotated: list[Vector], dst: list[Vector]) -> tuple[float, Vector, list[Vector], float]:
    """Fit translation and uniform scale after a fixed yaw has already been applied."""
    src_c = sum(src_rotated, Vector()) / len(src_rotated)
    dst_c = sum(dst, Vector()) / len(dst)
    x = [p - src_c for p in src_rotated]
    y = [p - dst_c for p in dst]
    denom = sum(p.x * p.x + p.y * p.y for p in x)
    numer = sum(xi.x * yi.x + xi.y * yi.y for xi, yi in zip(x, y))
    scale = numer / denom if denom > 1e-12 else 1.0
    z = sum(p.z for p in dst) / len(dst)
    translation = Vector((dst_c.x, dst_c.y, z)) - Vector((scale * src_c.x, scale * src_c.y, 0.0))
    fitted = [Vector((scale * p.x, scale * p.y, 0.0)) + translation for p in src_rotated]
    errors = [(mapped - target).length for mapped, target in zip(fitted, dst)]
    rms = math.sqrt(sum(e * e for e in errors) / len(errors))
    return scale, translation, fitted, rms


def ordered_radar_points_for_yaw(theta: float) -> tuple[list[Vector], list[str]]:
    rotated = {name: rotate_z(point, theta) for name, point in RADAR_POINTS.items()}
    by_quadrant = quadrant_lookup(rotated)
    ordered = []
    labels = []
    for _, quadrant in PANEL_CORNER_ORDER:
        label, point = by_quadrant[quadrant]
        labels.append(label)
        ordered.append(point)
    return ordered, labels


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


def livox_bounds(prefix: str) -> tuple[Vector, Vector]:
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for obj in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith(prefix)]:
        for v in obj.data.vertices:
            w = obj.matrix_world @ v.co
            mn.x = min(mn.x, w.x)
            mn.y = min(mn.y, w.y)
            mn.z = min(mn.z, w.z)
            mx.x = max(mx.x, w.x)
            mx.y = max(mx.y, w.y)
            mx.z = max(mx.z, w.z)
    return mn, mx


def transform_livox_objects(scale: float, theta: float, translation_xy: Vector, prefix: str) -> None:
    c, s = math.cos(theta), math.sin(theta)
    for obj in [o for o in bpy.context.scene.objects if o.name.startswith(prefix)]:
        # Object vertices are already baked in world coordinates. Apply transform
        # by editing vertex coordinates directly for audit clarity.
        if obj.type != "MESH":
            continue
        for v in obj.data.vertices:
            p = obj.matrix_world @ v.co
            mapped = Vector((scale * (c * p.x - s * p.y), scale * (s * p.x + c * p.y), p.z * scale)) + translation_xy
            v.co = obj.matrix_world.inverted() @ mapped
        obj.data.update()


def translate_livox_z(prefix: str, delta_z: float) -> None:
    for obj in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith(prefix)]:
        for v in obj.data.vertices:
            p = obj.matrix_world @ v.co
            p.z += delta_z
            v.co = obj.matrix_world.inverted() @ p
        obj.data.update()


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
        for corner in obj.bound_box:
            w = obj.matrix_world @ Vector(corner)
            mn.x = min(mn.x, w.x)
            mn.y = min(mn.y, w.y)
            mn.z = min(mn.z, w.z)
            mx.x = max(mx.x, w.x)
            mx.y = max(mx.y, w.y)
            mx.z = max(mx.z, w.z)
    center = (mn + mx) * 0.5
    extent = max((mx - mn).x, (mx - mn).y, (mx - mn).z, 0.18)
    light_data = bpy.data.lights.new("SelectedHoleFit_Key_Light", type="AREA")
    light_data.energy = 1000
    light_data.size = extent
    light = bpy.data.objects.new("SelectedHoleFit_Key_Light", light_data)
    light.location = center + Vector((extent * 0.25, -extent * 0.45, extent * 0.8))
    bpy.context.collection.objects.link(light)
    cam_data = bpy.data.cameras.new("SelectedHoleFit_Top_Camera")
    cam = bpy.data.objects.new("SelectedHoleFit_Top_Camera", cam_data)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = extent * 1.25
    cam.location = center + Vector((0, 0, extent * 1.8))
    cam.rotation_euler = (0, 0, 0)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reset_scene()

    panel_mat = make_material("TOP_PANNEL_Transparent", (0.20, 0.20, 0.18, 0.35))
    hole_mat = make_material("Selected_TOP_PANNEL_Holes_Magenta", (1.0, 0.05, 0.75, 1.0))
    radar_mat = make_material("Fitted_MID360_Blue", (0.05, 0.18, 0.42, 0.82))
    line_mat = make_material("Fit_Lines_Green", (0.0, 0.85, 0.18, 1.0))
    text_mat = make_material("Fit_Text_Black", (0.02, 0.02, 0.02, 1.0))

    dae = top_pick.prop.dae_objects(top_pick.prop.DAE_PATH)
    panel = top_pick.choose_top_panel(dae)
    panel_points = selected_panel_points()
    dst = [panel_points[name] for name, _ in PANEL_CORNER_ORDER]
    panel_top_z = max(v[2] for v in panel.verts)
    candidates = []

    for candidate in YAW_CANDIDATES:
        theta = math.radians(candidate["yaw_deg"])
        display_offset = candidate["display_offset"]
        add_mesh(f"{candidate['name']}_TOP_PANNEL_reference", panel.verts, panel.faces, panel_mat, display_offset)

        for name, p in panel_points.items():
            loc = p + display_offset
            add_sphere(f"{candidate['name']}_{name}", loc, 0.002, hole_mat)
            add_text(f"{candidate['name']}_{name}_label", name, loc + Vector((0, 0, 0.006)), 0.004, text_mat)

        src_rotated, source_labels = ordered_radar_points_for_yaw(theta)
        scale, translation, fitted, rms = fit_fixed_yaw_2d(src_rotated, dst)

        prefix = candidate["name"]
        livox.import_dae(
            livox.MID360_DAE,
            prefix,
            livox.pose_matrix(0, 0, 0, 0, 0, 3.14159) @ livox.matrix_scale_xyz(1.2, 1.2, 1.2),
        )
        base_center = livox_base_center_before_recenter(prefix)
        for obj in [o for o in bpy.context.scene.objects if o.name.startswith(prefix)]:
            obj.location -= base_center
        transform_livox_objects(scale, theta, translation + display_offset, prefix)
        mn, mx = livox_bounds(prefix)
        bottom_z_before_snap = mn.z
        z_snap_delta = panel_top_z - bottom_z_before_snap
        translate_livox_z(prefix, z_snap_delta)
        mn_after, mx_after = livox_bounds(prefix)
        for obj in [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith(prefix)]:
            obj.data.materials.clear()
            obj.data.materials.append(radar_mat)

        for idx, (a, b) in enumerate(zip(fitted, dst), start=1):
            add_sphere(f"{candidate['name']}_fitted_B{idx}", a + display_offset, 0.0014, line_mat)
            add_cylinder_between(f"{candidate['name']}_fit_error_line_{idx}", a + display_offset, b + display_offset, 0.00025, line_mat)

        add_cylinder_between(
            f"{candidate['name']}_tail_axis_minus_x",
            Vector((0.055, -0.055, panel_top_z + 0.01)) + display_offset,
            Vector((-0.055, -0.055, panel_top_z + 0.01)) + display_offset,
            0.00055,
            line_mat,
        )
        add_text(
            f"{candidate['name']}_label",
            f"{candidate['name']}  scale={scale:.3f}  fixed_yaw={candidate['yaw_deg']:.0f}deg  rms={rms*1000:.2f}mm",
            Vector((0, -0.13, 0.11)) + display_offset,
            0.0042,
            text_mat,
        )
        add_text(
            f"{candidate['name']}_tail_label",
            "TAIL -X / connector must face this direction",
            Vector((0.0, -0.064, panel_top_z + 0.017)) + display_offset,
            0.0038,
            text_mat,
        )
        candidates.append(
            {
                "name": candidate["name"],
                "fixed_yaw_deg": candidate["yaw_deg"],
                "source_labels_in_panel_order": source_labels,
                "scale": scale,
                "rms_m": rms,
                "translation_m": [translation.x, translation.y, translation.z],
                "panel_top_z_m": panel_top_z,
                "radar_bottom_z_before_snap_m": bottom_z_before_snap,
                "z_snap_delta_m": z_snap_delta,
                "radar_bounds_after_snap_m": {
                    "min": [mn_after.x, mn_after.y, mn_after.z],
                    "max": [mx_after.x, mx_after.y, mx_after.z],
                },
                "display_offset_m": [display_offset.x, display_offset.y, display_offset.z],
                "note": candidate["note"],
            }
        )

    frame_camera()
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.world.color = (0.86, 0.88, 0.90)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "purpose": "Fit diagnostic using user-selected TOP_PANNEL hole groups and explicit MID-360 90/270 body-rotation candidates. The radar bottom face is snapped to the TOP_PANNEL top surface.",
        "hole_groups": HOLE_GROUPS,
        "panel_points_m": {k: [round(v.x, 6), round(v.y, 6), round(v.z, 6)] for k, v in panel_points.items()},
        "radar_points_m": {k: [round(v.x, 6), round(v.y, 6), round(v.z, 6)] for k, v in RADAR_POINTS.items()},
        "connector_tail_rule": "MID-360 connector/port must face aircraft tail (-X). User correction requires rotating the radar body 90/270 degrees, not merely changing point correspondence.",
        "mount_surface_rule": "The MID-360 bottom face must sit on the TOP_PANNEL upper surface. Fit XY from selected holes, then snap radar mesh minimum Z to panel_top_z.",
        "fit_candidates": candidates,
        "panel_top_z_m": panel_top_z,
        "status": "diagnostic_manual_review_required",
        "elapsed_sec": round(time.time() - start, 3),
        "outputs": {"blend": str(OUT_BLEND), "manifest": str(OUT_MANIFEST)},
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2)[:8000])


if __name__ == "__main__":
    main()
