#!/usr/bin/env python3
"""Build center/origin audit markers for model://livox_mid360."""

from __future__ import annotations

import importlib.util
import json
import math
import time
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
HELPER_PATH = PROJECT_ROOT / "Scripts" / "UE5" / "assets" / "build_livox_mid360_audit_scene.py"
OUT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
OUT_BLEND = OUT_DIR / "livox_mid360_center_audit.blend"
OUT_MANIFEST = OUT_DIR / "livox_mid360_center_audit_manifest.json"


def load_helper():
    spec = importlib.util.spec_from_file_location("livox_mid360_audit_helper", HELPER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {HELPER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_mat(name: str, color: tuple[float, float, float, float]) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = color
    return mat


def add_marker(name: str, location: Vector, radius: float, color: tuple[float, float, float, float], label: str) -> None:
    mat = make_mat(f"Mat_{name}", color)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    font_curve = bpy.data.curves.new(f"Label_{name}", type="FONT")
    font_curve.body = label
    font_curve.size = 0.006
    font_curve.align_x = "CENTER"
    text = bpy.data.objects.new(f"Label_{name}", font_curve)
    text.location = location + Vector((0, -0.028, radius * 1.8))
    text.rotation_euler = (math.radians(70), 0, 0)
    bpy.context.collection.objects.link(text)


def scene_bounds() -> tuple[Vector, Vector, Vector, float]:
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
    return mn, mx, center, extent


def frame_camera() -> dict:
    mn, mx, center, extent = scene_bounds()
    light_data = bpy.data.lights.new("LivoxMid360_Center_Key_Light", type="AREA")
    light_data.energy = 900
    light_data.size = max(extent * 0.7, 0.15)
    light = bpy.data.objects.new("LivoxMid360_Center_Key_Light", light_data)
    light.location = center + Vector((extent * 0.3, -extent * 0.6, extent * 0.5))
    bpy.context.collection.objects.link(light)
    cam_data = bpy.data.cameras.new("LivoxMid360_Center_Review_Camera")
    cam = bpy.data.objects.new("LivoxMid360_Center_Review_Camera", cam_data)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = max(extent * 1.35, 0.14)
    cam.location = center + Vector((extent * 0.8, -extent * 1.6, extent * 0.65))
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return {"active_camera": cam.name, "bounds_min": list(mn), "bounds_max": list(mx), "extent": extent}


def mesh_bounds() -> tuple[Vector, Vector, Vector]:
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.name.startswith("Center_")]
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
    return mn, mx, (mn + mx) * 0.5


def main() -> None:
    helper = load_helper()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    helper.reset_scene()
    start = time.time()
    accepted_transform = helper.pose_matrix(0, 0, 0, 0, 0, 3.14159) @ helper.matrix_scale_xyz(1.2, 1.2, 1.2)
    import_result = helper.import_dae(helper.MID360_DAE, "livox_mid360_center_audit", accepted_transform)
    recenter_result = helper.recenter_mesh_objects_to_base_mount_center()
    mn, mx, bbox_center = mesh_bounds()
    base_link_origin = Vector((0, 0, 0))
    laser_sensor_origin = Vector((0, 0, 0.1))
    imu_origin = Vector((0, 0, 0))
    add_marker("Center_base_link_and_imu_origin", base_link_origin, 0.004, (0.95, 0.05, 0.05, 1), "base_link / imu origin")
    add_marker("Center_laser_sensor_origin", laser_sensor_origin, 0.004, (0.05, 0.2, 0.95, 1), "laser sensor origin z=0.1")
    add_marker("Center_visual_bbox_center", bbox_center, 0.004, (0.05, 0.8, 0.08, 1), "visual bbox center")
    camera_info = frame_camera()
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.world.color = (0.86, 0.87, 0.88)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "purpose": "Standalone center/origin audit for model://livox_mid360 using accepted F_yaw180_only orientation.",
        "model_uri": "model://livox_mid360",
        "source": str(helper.MID360_DAE),
        "accepted_visual_pose_xyz_rpy": [0, 0, 0, 0, 0, 3.14159],
        "sdf_base_link_origin": list(base_link_origin),
        "sdf_imu_origin": list(imu_origin),
        "sdf_laser_sensor_origin": list(laser_sensor_origin),
        "visual_bbox_min": list(mn),
        "visual_bbox_max": list(mx),
        "visual_bbox_center": list(bbox_center),
        "center_rule": "Manual audit rejected the raw DAE/SDF visual origin and full visual bbox center as off-axis. The imported visual mesh is recentered so the circular radar base mounting center becomes the Blender/UE origin.",
        "recommendation": "Use the corrected radar-base mounting center origin for Blender/UE mounting. Keep SDF base_link and laser sensor origins documented separately for Gazebo/sensor-frame parity.",
        "import_result": import_result,
        "recenter_result": recenter_result,
        "review_camera": camera_info,
        "elapsed_sec": round(time.time() - start, 3),
        "outputs": {"blend": str(OUT_BLEND), "manifest": str(OUT_MANIFEST)},
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2)[:5000])


if __name__ == "__main__":
    main()
