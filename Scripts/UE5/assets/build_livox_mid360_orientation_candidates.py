#!/usr/bin/env python3
"""Build orientation candidates for model://livox_mid360 visual audit."""

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
OUT_BLEND = OUT_DIR / "livox_mid360_orientation_candidates.blend"
OUT_MANIFEST = OUT_DIR / "livox_mid360_orientation_candidates_manifest.json"


def load_helper():
    spec = importlib.util.spec_from_file_location("livox_mid360_audit_helper", HELPER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {HELPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def add_label(text: str, location: tuple[float, float, float]) -> None:
    font_curve = bpy.data.curves.new(f"Label_{text}", type="FONT")
    font_curve.body = text
    font_curve.size = 0.018
    font_curve.align_x = "CENTER"
    obj = bpy.data.objects.new(f"Label_{text}", font_curve)
    obj.location = location
    obj.rotation_euler = (math.radians(70), 0, 0)
    bpy.context.collection.objects.link(obj)


def frame_camera() -> dict:
    objs = [o for o in bpy.context.scene.objects if o.type in {"MESH", "FONT"}]
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
    light_data = bpy.data.lights.new("LivoxMid360_Orientation_Key_Light", type="AREA")
    light_data.energy = 900
    light_data.size = max(extent * 0.5, 0.25)
    light = bpy.data.objects.new("LivoxMid360_Orientation_Key_Light", light_data)
    light.location = center + Vector((extent * 0.2, -extent * 0.35, extent * 0.45))
    bpy.context.collection.objects.link(light)
    cam_data = bpy.data.cameras.new("LivoxMid360_Orientation_Review_Camera")
    cam = bpy.data.objects.new("LivoxMid360_Orientation_Review_Camera", cam_data)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(extent * 1.2, 0.45)
    cam.location = center + Vector((0, -extent * 1.4, extent * 0.35))
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
        ("A_sdf_roll90_yaw180", (1.57, 0, 3.14159)),
        ("B_roll90_yaw0", (1.57, 0, 0)),
        ("C_identity", (0, 0, 0)),
        ("D_roll90_yaw90", (1.57, 0, math.radians(90))),
        ("E_roll90_yaw270", (1.57, 0, math.radians(270))),
        ("F_yaw180_only", (0, 0, 3.14159)),
    ]
    spacing = 0.18
    imported = []
    for idx, (name, rpy) in enumerate(variants):
        x = (idx - (len(variants) - 1) / 2.0) * spacing
        transform = (
            helper.pose_matrix(x, 0, 0, 0, 0, 0)
            @ helper.pose_matrix(0, 0, 0, rpy[0], rpy[1], rpy[2])
            @ helper.matrix_scale_xyz(1.2, 1.2, 1.2)
        )
        result = helper.import_dae(helper.MID360_DAE, name, transform)
        add_label(name, (x, -0.08, -0.07))
        imported.append({"name": name, "rpy": list(rpy), "result": result})

    camera_info = frame_camera()
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.world.color = (0.86, 0.87, 0.88)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "purpose": "Direction candidates for model://livox_mid360. User selects the visually correct orientation before updating the final asset rule.",
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
