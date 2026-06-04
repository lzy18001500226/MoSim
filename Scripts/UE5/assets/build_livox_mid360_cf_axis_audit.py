#!/usr/bin/env python3
"""Build C/F MID-360 orientation audit with explicit UAV body axes."""

from __future__ import annotations

import importlib.util
import json
import math
import time
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(__file__).resolve().parents[3]
HELPER_PATH = PROJECT_ROOT / "Scripts" / "UE5" / "assets" / "build_livox_mid360_audit_scene.py"
OUT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
OUT_BLEND = OUT_DIR / "livox_mid360_cf_axis_audit.blend"
OUT_MANIFEST = OUT_DIR / "livox_mid360_cf_axis_audit_manifest.json"


def load_helper():
    spec = importlib.util.spec_from_file_location("livox_mid360_audit_helper", HELPER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {HELPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add_mat(name: str, color: tuple[float, float, float, float]) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    return mat


def add_curve_line(name: str, start: Vector, end: Vector, mat: bpy.types.Material, bevel: float = 0.0025) -> None:
    curve = bpy.data.curves.new(name, type="CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = bevel
    spline = curve.splines.new("POLY")
    spline.points.add(1)
    spline.points[0].co = (start.x, start.y, start.z, 1)
    spline.points[1].co = (end.x, end.y, end.z, 1)
    obj = bpy.data.objects.new(name, curve)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)


def add_label(text: str, location: tuple[float, float, float], size: float = 0.022) -> None:
    font_curve = bpy.data.curves.new(f"Label_{text}", type="FONT")
    font_curve.body = text
    font_curve.size = size
    font_curve.align_x = "CENTER"
    obj = bpy.data.objects.new(f"Label_{text}", font_curve)
    obj.location = location
    obj.rotation_euler = (math.radians(70), 0, 0)
    bpy.context.collection.objects.link(obj)


def add_body_axes(origin: Vector, length: float = 0.11) -> None:
    red = add_mat("Axis_Red_Nose_X", (0.9, 0.02, 0.02, 1))
    green = add_mat("Axis_Green_Left_Y", (0.02, 0.75, 0.05, 1))
    blue = add_mat("Axis_Blue_Up_Z", (0.02, 0.16, 0.9, 1))
    gray = add_mat("Axis_Gray_Tail_NegX", (0.45, 0.45, 0.45, 1))
    add_curve_line("Axis_Nose_plus_X_red", origin, origin + Vector((length, 0, 0)), red)
    add_curve_line("Axis_Tail_minus_X_gray", origin, origin + Vector((-length, 0, 0)), gray)
    add_curve_line("Axis_Left_plus_Y_green", origin, origin + Vector((0, length * 0.8, 0)), green)
    add_curve_line("Axis_Up_plus_Z_blue", origin, origin + Vector((0, 0, length * 0.7)), blue)
    add_label("Nose +X", tuple(origin + Vector((length + 0.018, 0, 0))))
    add_label("Tail -X", tuple(origin + Vector((-length - 0.018, 0, 0))))
    add_label("Left +Y", tuple(origin + Vector((0, length * 0.9, 0))))
    add_label("Up +Z", tuple(origin + Vector((0, 0, length * 0.82))))


def frame_camera() -> dict:
    objs = [o for o in bpy.context.scene.objects if o.type in {"MESH", "FONT", "CURVE"}]
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
    light_data = bpy.data.lights.new("LivoxMid360_CF_Key_Light", type="AREA")
    light_data.energy = 900
    light_data.size = max(extent * 0.7, 0.25)
    light = bpy.data.objects.new("LivoxMid360_CF_Key_Light", light_data)
    light.location = center + Vector((extent * 0.15, -extent * 0.45, extent * 0.5))
    bpy.context.collection.objects.link(light)
    cam_data = bpy.data.cameras.new("LivoxMid360_CF_Axis_Review_Camera")
    cam = bpy.data.objects.new("LivoxMid360_CF_Axis_Review_Camera", cam_data)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(extent * 1.25, 0.35)
    cam.location = center + Vector((extent * 0.35, -extent * 1.6, extent * 0.45))
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return {"active_camera": cam.name, "bounds_min": list(mn), "bounds_max": list(mx), "extent": extent}


def main() -> None:
    helper = load_helper()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    helper.reset_scene()
    start = time.time()

    variants = [
        ("C_identity", (0, 0, 0), -0.13),
        ("F_yaw180_only", (0, 0, 3.14159), 0.13),
    ]
    imported = []
    for name, rpy, y in variants:
        transform = (
            helper.pose_matrix(0, y, 0, 0, 0, 0)
            @ helper.pose_matrix(0, 0, 0, rpy[0], rpy[1], rpy[2])
            @ helper.matrix_scale_xyz(1.2, 1.2, 1.2)
        )
        result = helper.import_dae(helper.MID360_DAE, name, transform)
        add_label(name, (0, y - 0.075, -0.07))
        imported.append({"name": name, "rpy": list(rpy), "row_y": y, "result": result})

    add_body_axes(Vector((0, 0, -0.085)))
    camera_info = frame_camera()
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.world.color = (0.86, 0.87, 0.88)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "purpose": "Compare C/F MID-360 orientation with explicit UAV body axes. Reference frame: +X nose, -X tail, +Y left, +Z up.",
        "expected_user_rule": "MID-360 connector/port should face tail, i.e. -X.",
        "model_uri": "model://livox_mid360",
        "source": str(helper.MID360_DAE),
        "variants": imported,
        "review_camera": camera_info,
        "elapsed_sec": round(time.time() - start, 3),
        "outputs": {"blend": str(OUT_BLEND), "manifest": str(OUT_MANIFEST)},
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2)[:5000])


if __name__ == "__main__":
    main()
