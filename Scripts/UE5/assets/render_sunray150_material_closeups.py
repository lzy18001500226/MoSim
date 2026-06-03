#!/usr/bin/env python3
"""Render close-up material audit PNGs for the Sunray150 assembly."""

from __future__ import annotations

import json
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(__file__).resolve().parents[3]
AUDIT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
BLEND = AUDIT_DIR / "sunray150_dae_mid360_realistic_material_audit.blend"
OUT_DIR = AUDIT_DIR / "material_closeups"
MANIFEST = OUT_DIR / "sunray150_material_closeups_manifest.json"


VIEWS = [
    {
        "name": "mid360_housing_window_connector",
        "center": (0.0, 0.032, 0.086),
        "camera_offset": (0.030, -0.115, 0.030),
        "ortho_scale": 0.105,
        "purpose": "MID-360 silver housing, blue optical window, black connector, screw details, and protection arc.",
    },
    {
        "name": "front_usb_camera_battery",
        "center": (0.0, 0.072, 0.019),
        "camera_offset": (0.018, -0.120, 0.020),
        "ortho_scale": 0.115,
        "purpose": "Front USB camera, battery pack area, connector holes, and black camera/glass material.",
    },
    {
        "name": "pcb_connectors_cables",
        "center": (0.030, 0.052, 0.017),
        "camera_offset": (0.085, -0.080, 0.035),
        "ortho_scale": 0.085,
        "purpose": "N150/ESC PCB stack, USB/HDMI connector metal, and colored cable hints.",
    },
    {
        "name": "carbon_frame_gold_standoffs",
        "center": (0.0, 0.006, 0.020),
        "camera_offset": (0.090, -0.105, 0.055),
        "ortho_scale": 0.135,
        "purpose": "Carbon fiber plates, gold aluminum standoffs, screws, and stack separation.",
    },
    {
        "name": "motor_prop_guard",
        "center": (0.055, 0.055, -0.012),
        "camera_offset": (0.055, -0.070, 0.040),
        "ortho_scale": 0.080,
        "purpose": "Motor bell, copper windings, propeller material, screws, and smoked guard.",
    },
]


def setup_render() -> None:
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 32
    bpy.context.scene.render.resolution_x = 1400
    bpy.context.scene.render.resolution_y = 1000
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"
    bpy.context.scene.view_settings.exposure = -2.25
    bpy.context.scene.view_settings.gamma = 1.0
    bpy.context.scene.world.color = (0.16, 0.16, 0.16)
    for light in [o for o in bpy.context.scene.objects if o.type == "LIGHT"]:
        light.data.energy *= 0.65


def ensure_camera() -> bpy.types.Object:
    cam = bpy.context.scene.camera
    if cam is None:
        cam_data = bpy.data.cameras.new("MaterialCloseup_Camera")
        cam = bpy.data.objects.new("MaterialCloseup_Camera", cam_data)
        bpy.context.collection.objects.link(cam)
        bpy.context.scene.camera = cam
    cam.data.type = "ORTHO"
    return cam


def render_view(view: dict) -> dict:
    cam = ensure_camera()
    center = Vector(view["center"])
    offset = Vector(view["camera_offset"])
    cam.location = center + offset
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = view["ortho_scale"]
    out = OUT_DIR / f"{view['name']}.png"
    bpy.context.scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    return {
        "name": view["name"],
        "path": str(out),
        "center_m": list(view["center"]),
        "camera_offset_m": list(view["camera_offset"]),
        "ortho_scale": view["ortho_scale"],
        "purpose": view["purpose"],
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    setup_render()
    selected = VIEWS
    only = {item.strip() for item in __import__("os").environ.get("CLOSEUP_ONLY", "").split(",") if item.strip()}
    if only:
        selected = [view for view in VIEWS if view["name"] in only]
    outputs = [render_view(view) for view in selected]
    MANIFEST.write_text(json.dumps({"source_blend": str(BLEND), "outputs": outputs}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(MANIFEST))


if __name__ == "__main__":
    main()
