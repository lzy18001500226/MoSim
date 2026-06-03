#!/usr/bin/env python3
"""Render preview PNGs for the Sunray150 material audit asset."""

from __future__ import annotations

from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
BLEND = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit" / "sunray150_dae_mid360_realistic_material_audit.blend"
OUT = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit" / "sunray150_dae_mid360_realistic_material_preview.png"


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    for light in [o for o in bpy.context.scene.objects if o.type == "LIGHT"]:
        light.data.energy *= 0.20
    objs = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.hide_render]
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for obj in objs:
        for c in obj.bound_box:
            w = obj.matrix_world @ Vector(c)
            mn.x, mn.y, mn.z = min(mn.x, w.x), min(mn.y, w.y), min(mn.z, w.z)
            mx.x, mx.y, mx.z = max(mx.x, w.x), max(mx.y, w.y), max(mx.z, w.z)
    center = (mn + mx) * 0.5
    extent = max((mx - mn).x, (mx - mn).y, (mx - mn).z, 0.22)
    cam = bpy.context.scene.camera
    if cam:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = extent * 1.08
        cam.location = center + Vector((extent * 0.35, -extent * 1.75, extent * 0.38))
        cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.render.resolution_x = 1800
    bpy.context.scene.render.resolution_y = 1200
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"
    bpy.context.scene.view_settings.exposure = -2.55
    bpy.context.scene.view_settings.gamma = 1.0
    bpy.context.scene.world.color = (0.24, 0.24, 0.24)
    bpy.context.scene.render.filepath = str(OUT)
    bpy.ops.render.render(write_still=True)
    print(str(OUT))


if __name__ == "__main__":
    main()
