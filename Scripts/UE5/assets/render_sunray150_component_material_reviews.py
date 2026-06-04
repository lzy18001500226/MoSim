#!/usr/bin/env python3
"""Render component-level Sunray150 material review images.

This is the material workflow's primary audit surface. Whole-aircraft renders
are only a final consistency check; component families are reviewed one by one.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(__file__).resolve().parents[3]
AUDIT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
BLEND = AUDIT_DIR / "sunray150_dae_mid360_realistic_material_audit.blend"
OUT_DIR = AUDIT_DIR / "component_material_reviews"
MANIFEST = OUT_DIR / "sunray150_component_material_reviews_manifest.json"


COMPONENTS = [
    {
        "name": "mid360_sensor",
        "center": (0.0, 0.028, 0.084),
        "camera_offset": (0.010, -0.120, 0.018),
        "ortho_scale": 0.074,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -3.20,
        "world_color": (0.035, 0.037, 0.040),
        "light_scale": 0.20,
        "target_object_keys": ("AUDIT_STANDALONE_MID360",),
        "material_gate": "silver-grey MID-360 housing, dark blue/teal glossy optical dome, black connector/base, readable screws.",
    },
    {
        "name": "mid360_protection_frame",
        "center": (0.0, 0.028, 0.076),
        "camera_offset": (0.018, -0.140, 0.026),
        "ortho_scale": 0.108,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -1.65,
        "world_color": (0.58, 0.59, 0.60),
        "light_scale": 0.34,
        "review_material": "satin_dark_grey",
        "target_object_keys": ("MID360_PROTECT_ARC", "MID-360_4_ASM"),
        "material_gate": "black/dark grey MID-360 protection frame and mount hardware, not white CAD.",
    },
    {
        "name": "carbon_frame",
        "center": (0.0, 0.008, 0.018),
        "camera_offset": (0.095, -0.105, 0.052),
        "ortho_scale": 0.115,
        "target_object_keys": ("MAIN_STRUCTURE", "TOP_PANNEL", "BOT_PANNEL", "Fill.1", "PROTECTIVE_RING"),
        "material_gate": "dark woven carbon plates/arms with visible diagonal weave and no white CAD fallback.",
    },
    {
        "name": "aluminum_standoffs",
        "center": (0.040, 0.020, 0.020),
        "camera_offset": (0.090, -0.080, 0.045),
        "ortho_scale": 0.090,
        "target_object_keys": ("AL_COLUMNS", "AL_COLUMS", "YUNDRONE_AL_COLUMNS"),
        "material_gate": "gold anodized 7-series aluminum, metallic/satin, not plastic yellow.",
    },
    {
        "name": "front_camera",
        "center": (0.0, 0.096, 0.003),
        "camera_offset": (0.0, -0.085, 0.010),
        "ortho_scale": 0.052,
        "target_object_keys": ("FRONT_CAMERA", "CAMERA_SHIM", "FRONT_CAMERA_CONNECTOR"),
        "material_gate": "black USB camera body, dark glass lens, visible bracket/screw detail.",
    },
    {
        "name": "electronics_connectors",
        "center": (0.028, 0.050, 0.015),
        "camera_offset": (0.090, -0.075, 0.030),
        "ortho_scale": 0.080,
        "target_object_keys": ("N150_AllCATPart", "ESC_SPEEDYBEE", "A_USB", "HDMI", "NGFF", "PJ311", "CABLE", "WIRE"),
        "material_gate": "dark PCB/soldermask, nickel connector shells, black plastic cores, readable cable colors.",
    },
    {
        "name": "motor_propeller",
        "center": (0.055, 0.055, -0.011),
        "camera_offset": (0.045, -0.052, 0.045),
        "ortho_scale": 0.061,
        "target_object_keys": ("MOTOR_2104", "TriBlade", "SCREW_BUTTON_HEAD_M2_8MM"),
        "material_gate": "black motor bell, copper windings, steel screws, dark smoked tri-blade propeller without white patches.",
    },
    {
        "name": "guard_landing_gear",
        "center": (0.0, 0.000, -0.018),
        "camera_offset": (0.120, -0.115, 0.050),
        "ortho_scale": 0.155,
        "target_object_keys": ("PROTECTIVE_RING", "LAND_GEAR"),
        "material_gate": "smoked/dark protective ring and landing gear, not opaque white CAD.",
    },
    {
        "name": "battery",
        "center": (0.0, 0.022, 0.032),
        "camera_offset": (-0.075, -0.105, 0.030),
        "ortho_scale": 0.080,
        "target_object_keys": ("YUNDRONE_4S1P", "BATTERY", "BATTERY_CLIP"),
        "material_gate": "black heat-shrink battery/clip with subtle surface wrinkles/label cue.",
    },
]


def make_context_material() -> bpy.types.Material:
    mat = bpy.data.materials.new("Sunray150_ComponentReview_Context_Ghost")
    mat.diffuse_color = (0.010, 0.010, 0.010, 1.0)
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (0.010, 0.010, 0.010, 1.0)
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = 1.0
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.82
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
    mat.blend_method = "OPAQUE"
    mat.show_transparent_back = False
    return mat


def make_debug_override_material(name: str, rgba: tuple[float, float, float, float]) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = rgba
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = rgba[3]
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 0.78
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def make_debug_emission_material(name: str, rgba: tuple[float, float, float, float]) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    out = nodes.new(type="ShaderNodeOutputMaterial")
    emission = nodes.new(type="ShaderNodeEmission")
    emission.inputs["Color"].default_value = rgba
    emission.inputs["Strength"].default_value = 1.0
    mat.node_tree.links.new(emission.outputs["Emission"], out.inputs["Surface"])
    return mat


def make_review_principled_material(name: str, rgba: tuple[float, float, float, float], *, roughness: float, metallic: float = 0.0, specular: float = 0.12) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = rgba
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = rgba[3]
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Specular IOR Level" in bsdf.inputs:
            bsdf.inputs["Specular IOR Level"].default_value = specular
        elif "Specular" in bsdf.inputs:
            bsdf.inputs["Specular"].default_value = specular
    return mat


def light_snapshot() -> dict[str, dict]:
    return {
        obj.name: {
            "energy": obj.data.energy,
            "size": getattr(obj.data, "size", None),
        }
        for obj in bpy.context.scene.objects
        if obj.type == "LIGHT"
    }


def restore_lights(snapshot: dict[str, dict]) -> None:
    for obj in bpy.context.scene.objects:
        if obj.type != "LIGHT" or obj.name not in snapshot:
            continue
        state = snapshot[obj.name]
        obj.data.energy = state["energy"]
        if state["size"] is not None and hasattr(obj.data, "size"):
            obj.data.size = state["size"]


def is_target_object(obj: bpy.types.Object, keys: tuple[str, ...]) -> bool:
    return obj.type != "MESH" or any(key in obj.name for key in keys)


def snapshot_object_state() -> dict[str, dict]:
    return {
        obj.name: {
            "materials": [slot.material for slot in obj.material_slots],
            "hide_render": obj.hide_render,
            "hide_viewport": obj.hide_viewport,
        }
        for obj in bpy.context.scene.objects
        if obj.type == "MESH"
    }


def restore_object_state(snapshot: dict[str, dict]) -> None:
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.name not in snapshot:
            continue
        state = snapshot[obj.name]
        obj.hide_render = state["hide_render"]
        obj.hide_viewport = state["hide_viewport"]
        for idx, mat in enumerate(state["materials"]):
            if idx < len(obj.material_slots):
                obj.material_slots[idx].material = mat


def apply_component_isolation(component: dict, context_mat: bpy.types.Material) -> dict:
    keys = tuple(component["target_object_keys"])
    debug_override = os.environ.get("COMPONENT_DEBUG_OVERRIDE", "").strip().lower()
    if "--debug-override" in sys.argv:
        idx = sys.argv.index("--debug-override")
        if idx + 1 < len(sys.argv):
            debug_override = sys.argv[idx + 1].strip().lower()
    override_mat = None
    if debug_override == "red":
        override_mat = make_debug_override_material("Sunray150_ComponentReview_Debug_Red", (0.85, 0.02, 0.01, 1.0))
    elif debug_override == "black":
        override_mat = make_debug_emission_material("Sunray150_ComponentReview_Debug_Emission_Black", (0.002, 0.002, 0.002, 1.0))
    review_material = component.get("review_material")
    if review_material == "satin_black" and override_mat is None:
        override_mat = make_review_principled_material(
            "Sunray150_ComponentReview_Satin_Black_Physical_Audit",
            (0.018, 0.019, 0.018, 1.0),
            roughness=0.70,
            metallic=0.02,
            specular=0.16,
        )
    elif review_material == "satin_dark_grey" and override_mat is None:
        override_mat = make_debug_emission_material(
            "Sunray150_ComponentReview_Satin_Dark_Grey_Protection_Audit",
            (0.055, 0.058, 0.056, 1.0),
        )
    target_count = 0
    context_count = 0
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        if is_target_object(obj, keys):
            obj.hide_render = False
            obj.hide_viewport = False
            if override_mat is not None:
                obj.data.materials.clear()
                obj.data.materials.append(override_mat)
                for poly in obj.data.polygons:
                    poly.material_index = 0
            target_count += 1
            continue
        # Hide non-target geometry for the primary component pass. The review
        # goal is material identity, so unrelated white CAD surfaces must not
        # dominate or wash out the component under audit.
        obj.hide_render = True
        obj.hide_viewport = True
        if obj.material_slots:
            for slot in obj.material_slots:
                slot.material = context_mat
        else:
            obj.data.materials.append(context_mat)
        context_count += 1
    return {"target_object_count": target_count, "context_object_count": context_count}


def setup_render() -> None:
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 64
    bpy.context.scene.render.resolution_x = 1400
    bpy.context.scene.render.resolution_y = 1050
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"
    bpy.context.scene.view_settings.exposure = -1.55
    bpy.context.scene.view_settings.gamma = 1.0
    bpy.context.scene.world.color = (0.12, 0.12, 0.12)
    for light in [o for o in bpy.context.scene.objects if o.type == "LIGHT"]:
        light.data.energy *= 0.35
        if hasattr(light.data, "size"):
            light.data.size *= 1.6

    for name, loc, energy, size in [
        ("ComponentReview_Key", (0.055, -0.140, 0.115), 360, 0.30),
        ("ComponentReview_SoftTop", (-0.090, -0.020, 0.165), 220, 0.42),
        ("ComponentReview_Rim", (-0.130, 0.095, 0.090), 120, 0.32),
    ]:
        light_data = bpy.data.lights.new(name, type="AREA")
        light_data.energy = energy
        light_data.size = size
        light = bpy.data.objects.new(name, light_data)
        light.location = loc
        bpy.context.collection.objects.link(light)


def apply_component_render_settings(component: dict) -> dict:
    original = {
        "view_transform": bpy.context.scene.view_settings.view_transform,
        "look": bpy.context.scene.view_settings.look,
        "exposure": bpy.context.scene.view_settings.exposure,
        "world_color": tuple(bpy.context.scene.world.color),
        "lights": light_snapshot(),
    }
    if "view_transform" in component:
        bpy.context.scene.view_settings.view_transform = component["view_transform"]
    if "look" in component:
        bpy.context.scene.view_settings.look = component["look"]
    if "exposure" in component:
        bpy.context.scene.view_settings.exposure = component["exposure"]
    if "world_color" in component:
        bpy.context.scene.world.color = component["world_color"]
    light_scale = float(component.get("light_scale", 1.0))
    if abs(light_scale - 1.0) > 1e-9:
        for obj in bpy.context.scene.objects:
            if obj.type == "LIGHT":
                obj.data.energy *= light_scale
    return original


def restore_component_render_settings(original: dict) -> None:
    bpy.context.scene.view_settings.view_transform = original["view_transform"]
    bpy.context.scene.view_settings.look = original["look"]
    bpy.context.scene.view_settings.exposure = original["exposure"]
    bpy.context.scene.world.color = original["world_color"]
    restore_lights(original["lights"])


def ensure_camera() -> bpy.types.Object:
    cam = bpy.context.scene.camera
    if cam is None:
        cam_data = bpy.data.cameras.new("Sunray150_ComponentReview_Camera")
        cam = bpy.data.objects.new("Sunray150_ComponentReview_Camera", cam_data)
        bpy.context.collection.objects.link(cam)
        bpy.context.scene.camera = cam
    cam.data.type = "ORTHO"
    return cam


def material_names_for_keys(keys: tuple[str, ...]) -> list[dict]:
    rows = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        if not any(key in obj.name for key in keys):
            continue
        rows.append(
            {
                "object": obj.name,
                "materials": [mat.name if mat else None for mat in obj.data.materials],
            }
        )
    return rows


def render_component(component: dict) -> dict:
    context_mat = make_context_material()
    object_snapshot = snapshot_object_state()
    render_snapshot = apply_component_render_settings(component)
    isolation = apply_component_isolation(component, context_mat)
    cam = ensure_camera()
    center = Vector(component["center"])
    offset = Vector(component["camera_offset"])
    cam.location = center + offset
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.ortho_scale = component["ortho_scale"]
    out = OUT_DIR / f"{component['name']}.png"
    bpy.context.scene.render.filepath = str(out)
    bpy.ops.render.render(write_still=True)
    restore_object_state(object_snapshot)
    restore_component_render_settings(render_snapshot)
    return {
        "name": component["name"],
        "path": str(out),
        "project_relative_path": str(out.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "center_m": list(component["center"]),
        "camera_offset_m": list(component["camera_offset"]),
        "ortho_scale": component["ortho_scale"],
        "exposure": component.get("exposure"),
        "world_color": component.get("world_color"),
        "light_scale": component.get("light_scale"),
        "target_object_keys": list(component["target_object_keys"]),
        "material_gate": component["material_gate"],
        "isolation": isolation,
        "matched_materials": material_names_for_keys(component["target_object_keys"])[:120],
    }


def selected_components() -> list[dict]:
    only_arg = ""
    if "--only" in sys.argv:
        idx = sys.argv.index("--only")
        if idx + 1 < len(sys.argv):
            only_arg = sys.argv[idx + 1]
    only = {item.strip() for item in (only_arg or os.environ.get("COMPONENT_ONLY", "")).split(",") if item.strip()}
    if not only:
        return COMPONENTS
    return [component for component in COMPONENTS if component["name"] in only]


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    setup_render()
    outputs = [render_component(component) for component in selected_components()]
    previous_outputs = []
    if MANIFEST.exists():
        try:
            previous_outputs = json.loads(MANIFEST.read_text(encoding="utf-8")).get("outputs", [])
        except json.JSONDecodeError:
            previous_outputs = []
    by_name = {item.get("name"): item for item in previous_outputs if item.get("name")}
    for item in outputs:
        by_name[item["name"]] = item
    ordered = [by_name[component["name"]] for component in COMPONENTS if component["name"] in by_name]
    MANIFEST.write_text(
        json.dumps(
            {
                "source_blend": str(BLEND),
                "source_blend_project_relative": str(BLEND.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "workflow": "component-first material review; whole-aircraft render is final consistency only",
                "outputs": ordered,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(str(MANIFEST))


if __name__ == "__main__":
    main()
