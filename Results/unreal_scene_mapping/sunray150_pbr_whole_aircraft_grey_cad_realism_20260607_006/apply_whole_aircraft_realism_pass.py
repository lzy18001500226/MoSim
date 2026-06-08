#!/usr/bin/env python3
"""Apply the 006 whole-aircraft Sunray150 PBR review pass.

This script edits only the current DAE-derived Blender audit asset and writes
task-local evidence. It does not touch geometry placement, dynamics,
extrinsics, ROS2/MWORKS/UE runtime, controller, planner, or References.
"""

from __future__ import annotations

import json
import math
import time
from pathlib import Path

import bpy
from mathutils import Vector


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BLEND = PROJECT_ROOT / "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Audit/sunray150_dae_mid360_realistic_material_audit.blend"
EVIDENCE_DIR = PROJECT_ROOT / "Results/unreal_scene_mapping/sunray150_pbr_whole_aircraft_grey_cad_realism_20260607_006"
MATERIAL_MANIFEST = EVIDENCE_DIR / "sunray150_whole_aircraft_material_manifest.json"

RENDER_SPECS = [
    {
        "name": "whole_aircraft_iso",
        "camera_offset": (0.26, -0.42, 0.22),
        "ortho_scale": 0.285,
        "resolution": (1800, 1350),
        "exposure": -2.35,
        "world": (0.012, 0.014, 0.016),
    },
    {
        "name": "top_electronics_mid360",
        "camera_offset": (0.02, -0.18, 0.30),
        "ortho_scale": 0.185,
        "resolution": (1800, 1350),
        "exposure": -2.45,
        "world": (0.012, 0.014, 0.016),
    },
    {
        "name": "front_camera_tfmini_electronics",
        "camera_offset": (0.10, -0.24, 0.085),
        "ortho_scale": 0.135,
        "resolution": (1800, 1350),
        "exposure": -2.35,
        "world": (0.012, 0.014, 0.016),
    },
    {
        "name": "transparent_guard_propeller_check",
        "camera_offset": (0.22, -0.24, 0.105),
        "ortho_scale": 0.210,
        "resolution": (1800, 1350),
        "exposure": -2.55,
        "world": (0.010, 0.012, 0.014),
    },
]

MATERIAL_FAMILY_KEYWORDS = {
    "carbon_frame": ("CARBON", "MAIN_STRUCTURE", "TOP_PANNEL", "Fill.1"),
    "pcb_electronics": ("PCB", "SPEEDYBEE", "MAIN_BOARD", "N150", "ESC_", "Part1", "Part2"),
    "connector_ports": ("USB", "HDMI", "RJ45", "NGFF", "PJ311", "CONNECTOR", "BM8B"),
    "cables_wires": ("CABLE", "WIRE", "wire_hint"),
    "battery_payload": ("BATTERY", "YUNDRONE_4S1P", "BATTERY_LIMITER"),
    "camera_tfmini": ("FRONT_CAMERA", "BOTTOM_CAMERA", "Sensor TF Mini", "TF Mini", "RANGING_LIDAR_CAMERA"),
    "mid360": ("AUDIT_STANDALONE_MID360", "MID360", "MID-360"),
    "transparent_guard_propeller": ("PROTECTIVE_RING", "LAND_GEAR", "TriBlade"),
    "motors_fasteners_standoffs": ("MOTOR_2104", "SCREW", "NUT", "AL_COLUMNS", "COLUMS"),
}


def set_input(bsdf: bpy.types.Node, names: tuple[str, ...], value) -> None:
    for name in names:
        if name in bsdf.inputs:
            bsdf.inputs[name].default_value = value
            return


def bsdf_for(mat: bpy.types.Material) -> bpy.types.Node | None:
    if not mat.use_nodes:
        mat.use_nodes = True
    return next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)


def make_material(
    name: str,
    rgba: tuple[float, float, float, float],
    *,
    roughness: float,
    metallic: float = 0.0,
    specular: float = 0.20,
    alpha: float | None = None,
    coat: float = 0.0,
    coat_roughness: float = 0.20,
    transmission: float = 0.0,
    emission: tuple[float, float, float, float] | None = None,
    emission_strength: float = 0.0,
) -> bpy.types.Material:
    existing = bpy.data.materials.get(name)
    mat = existing if existing else bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = bsdf_for(mat)
    if bsdf:
        set_input(bsdf, ("Base Color",), rgba)
        set_input(bsdf, ("Alpha",), rgba[3] if alpha is None else alpha)
        set_input(bsdf, ("Roughness",), roughness)
        set_input(bsdf, ("Metallic",), metallic)
        set_input(bsdf, ("Specular IOR Level", "Specular"), specular)
        set_input(bsdf, ("Coat Weight", "Clearcoat"), coat)
        set_input(bsdf, ("Coat Roughness", "Clearcoat Roughness"), coat_roughness)
        set_input(bsdf, ("Transmission Weight", "Transmission"), transmission)
        set_input(bsdf, ("IOR",), 1.48)
        if emission is not None:
            set_input(bsdf, ("Emission Color", "Emission"), emission)
            set_input(bsdf, ("Emission Strength",), emission_strength)
    if (alpha if alpha is not None else rgba[3]) < 1.0:
        mat.blend_method = "HASHED"
        mat.use_screen_refraction = True
        mat.show_transparent_back = True
    return mat


def clear_task_006_overlays() -> None:
    for obj in list(bpy.context.scene.objects):
        if obj.name.startswith("pbr006_"):
            bpy.data.objects.remove(obj, do_unlink=True)


def material_library() -> dict[str, bpy.types.Material]:
    return {
        "carbon_frame": make_material("PBR006_Dark_Woven_Carbon_Frame", (0.004, 0.006, 0.006, 1.0), roughness=0.58, specular=0.20, coat=0.12, coat_roughness=0.24),
        "pcb_deep": make_material("PBR006_Deep_Green_Black_PCB_With_Gold_Accents", (0.006, 0.085, 0.040, 1.0), roughness=0.43, specular=0.24),
        "connector_nickel": make_material("PBR006_Darker_Brushed_Nickel_Port_Shells", (0.22, 0.22, 0.205, 1.0), roughness=0.34, metallic=0.88, specular=0.48, coat=0.10),
        "connector_core": make_material("PBR006_Port_Black_Plastic_Cores", (0.006, 0.006, 0.005, 1.0), roughness=0.70, specular=0.10),
        "dark_hardware": make_material("PBR006_Dark_Anodized_Hardware", (0.018, 0.019, 0.018, 1.0), roughness=0.36, metallic=0.70, specular=0.42, coat=0.08),
        "camera_black": make_material("PBR006_USB_Camera_All_Black_Polymer", (0.0015, 0.0015, 0.0012, 1.0), roughness=0.86, specular=0.045),
        "tfmini_black": make_material("PBR006_TF_Mini_Black_Optical_Sensor", (0.0035, 0.0035, 0.0032, 1.0), roughness=0.76, specular=0.12),
        "battery_black": make_material("PBR006_Battery_Black_Heatshrink_With_Label_Cues", (0.005, 0.005, 0.0045, 1.0), roughness=0.68, specular=0.12),
        "liuli_guard": make_material("PBR006_Clear_Liuli_Glass_Guard_Landing_Gear", (0.010, 0.105, 0.155, 0.48), roughness=0.110, specular=0.54, alpha=0.48, coat=0.26, coat_roughness=0.115, transmission=0.04),
        "liuli_prop": make_material("PBR006_Clear_Liuli_Glass_Propeller", (0.008, 0.085, 0.135, 0.52), roughness=0.125, specular=0.48, alpha=0.52, coat=0.22, coat_roughness=0.125, transmission=0.03),
        "mid360_housing": make_material("PBR006_MID360_Satin_Darker_Grey_Metal_Housing", (0.20, 0.21, 0.20, 1.0), roughness=0.34, metallic=0.34, specular=0.42, coat=0.12, coat_roughness=0.22),
        "mid360_dome": make_material("PBR006_MID360_Dark_Blue_Mirror_Optical_Glass_Dome", (0.000, 0.010, 0.052, 0.98), roughness=0.010, specular=1.0, alpha=0.98, coat=1.0, coat_roughness=0.006, transmission=0.0),
        "red_wire": make_material("PBR006_Red_Silicone_Wire_Accent", (0.95, 0.030, 0.020, 1.0), roughness=0.55, specular=0.18),
        "blue_wire": make_material("PBR006_Blue_Silicone_Wire_Accent", (0.030, 0.12, 0.95, 1.0), roughness=0.55, specular=0.18),
        "yellow_wire": make_material("PBR006_Yellow_Silicone_Wire_Accent", (1.00, 0.72, 0.035, 1.0), roughness=0.55, specular=0.18),
        "gold_pad": make_material("PBR006_Electronics_Gold_Pad_Accent", (1.0, 0.70, 0.14, 1.0), roughness=0.28, metallic=0.82, specular=0.48),
        "white_label": make_material("PBR006_Battery_And_Module_Satin_Label", (0.88, 0.84, 0.70, 1.0), roughness=0.62, specular=0.10),
        "red_label": make_material("PBR006_Battery_Red_Warning_Label", (0.78, 0.028, 0.018, 1.0), roughness=0.64, specular=0.08),
        "mirror_white": make_material("PBR006_MID360_Mirror_White_Reflection_Strips", (0.75, 0.90, 1.0, 0.42), roughness=0.018, specular=1.0, alpha=0.42, coat=1.0, emission=(0.55, 0.78, 1.0, 1.0), emission_strength=0.18),
    }


def assign_single(obj: bpy.types.Object, mat: bpy.types.Material) -> None:
    if obj.type != "MESH":
        return
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.material_index = 0


def add_noise_bump(mat: bpy.types.Material, *, scale: float, strength: float, distance: float) -> None:
    bsdf = bsdf_for(mat)
    if bsdf is None or "Normal" not in bsdf.inputs:
        return
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    noise = nodes.new(type="ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 10.0
    noise.inputs["Roughness"].default_value = 0.62
    bump = nodes.new(type="ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = distance
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def enhance_existing_materials(lib: dict[str, bpy.types.Material]) -> list[dict]:
    edited = []
    texture_mats = {
        "Sunray150_Texture_PCB_Black_Soldermask": ("pcb_deep", 150.0, 0.030, 0.00045),
        "Sunray150_Texture_CarbonFiber_Woven_Graphite": ("carbon_frame", 120.0, 0.040, 0.00055),
        "Sunray150_Texture_USB_HDMI_Nickel_Shell": ("connector_nickel", 110.0, 0.020, 0.00035),
        "Sunray150_Texture_Connector_Black_Core": ("connector_core", 70.0, 0.014, 0.00025),
        "Sunray150_Texture_USB_Camera_Matte_Black_Housing": ("camera_black", 80.0, 0.016, 0.00030),
        "Sunray150_Texture_TF_Mini_Black_Sensor": ("tfmini_black", 75.0, 0.014, 0.00028),
        "Sunray150_Texture_Black_Heatshrink_Battery": ("battery_black", 52.0, 0.020, 0.00045),
        "Sunray150_Texture_Clear_Liuli_Glass_Prop_Guard": ("liuli_guard", 55.0, 0.0012, 0.00004),
        "Sunray150_Texture_Clear_Liuli_Glass_Propeller": ("liuli_prop", 62.0, 0.0012, 0.00004),
        "MID360_Texture_Satin_Silver_Grey_Coated_Metal_Housing": ("mid360_housing", 90.0, 0.018, 0.00032),
        "MID360_Texture_Dark_Blue_Mirror_Coated_Optical_Dome": ("mid360_dome", 40.0, 0.0008, 0.00003),
    }
    for old_name, (key, scale, strength, distance) in texture_mats.items():
        mat = bpy.data.materials.get(old_name)
        if not mat:
            continue
        replacement = lib[key]
        for obj in bpy.context.scene.objects:
            if obj.type != "MESH":
                continue
            for slot in obj.material_slots:
                if slot.material == mat:
                    slot.material = replacement
        add_noise_bump(replacement, scale=scale, strength=strength, distance=distance)
        edited.append({"source_material": old_name, "replacement_material": replacement.name, "route": "material-parameter-and-node replacement; no geometry edit"})
    return edited


def classify_object(obj: bpy.types.Object) -> str:
    upper = obj.name.upper()
    if "MAIN_STRUCTURE.1_MAIN_STRUCTURE" in upper or "TOP_PANNEL.1_TOP" in upper or "DAE_FULL_FILL.1" in upper:
        return "carbon_frame"
    if "AUDIT_STANDALONE_MID360_015" in upper:
        return "mid360_dome"
    if "AUDIT_STANDALONE_MID360_013" in upper or "AUDIT_STANDALONE_MID360_014" in upper:
        return "mid360_housing"
    if "CABLE_FRONT_CAMERA" in upper or "CABLE_BOTTOM_CAMERA" in upper:
        return "cables"
    if (
        "FRONT_CAMERA" in upper
        or "BOTTOM_CAMERA" in upper
        or "RANGING_LIDAR_CAMERA_BASE" in upper
        or "CAMERA_SHIM" in upper
    ):
        return "camera_black"
    if "SENSOR TF MINI" in upper or "TF MINI" in upper or "RESSALTO-EXTRUS" in upper:
        return "tfmini_black"
    if "PROTECTIVE_RING" in upper or "LAND_GEAR" in upper:
        return "liuli_guard"
    if "TRIBLADE" in upper:
        return "liuli_prop"
    if "BATTERY" in upper or "YUNDRONE_4S1P" in upper:
        return "battery_black"
    if "CABLE" in upper or "WIRE" in upper:
        return "cables"
    if any(word in upper for word in ("USB", "HDMI", "RJ45", "NGFF", "PJ311", "CONNECTOR", "BM8B")):
        return "connector_nickel"
    if "N150" in upper and any(word in upper for word in ("AL_COLUMNS", "SMT_NUT", "NUT", "SCREW")):
        return "dark_hardware"
    if "N150" in upper and any(word in upper for word in ("TURBO_FAN", "FAN")):
        return "connector_core"
    if "N150" in upper and "TN_MTS400" in upper:
        return "white_label"
    if any(word in upper for word in ("N150", "SPEEDYBEE", "MAIN_BOARD", "PCBMODEL")):
        return "pcb_deep"
    return ""


def apply_object_level_corrections(lib: dict[str, bpy.types.Material]) -> list[dict]:
    rows = []
    wire_cycle = [lib["red_wire"], lib["blue_wire"], lib["yellow_wire"]]
    wire_idx = 0
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        key = classify_object(obj)
        if not key:
            continue
        if key == "cables":
            mat = wire_cycle[wire_idx % len(wire_cycle)] if ("RED" in obj.name.upper() or "BLUE" in obj.name.upper() or "YELLOW" in obj.name.upper()) else None
            if mat is None:
                mat = bpy.data.materials.get("Sunray150_Texture_Rubber_Cable_Black") or lib["connector_core"]
            wire_idx += 1
        else:
            mat = lib[key]
        assign_single(obj, mat)
        rows.append({"object": obj.name, "assigned_review_family": key, "material": mat.name})
    return rows


def flat_box(name: str, loc: Vector, scale: tuple[float, float, float], mat: bpy.types.Material) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    assign_single(obj, mat)
    return obj


def cylinder_between(name: str, a: Vector, b: Vector, radius: float, mat: bpy.types.Material) -> bpy.types.Object:
    mid = (a + b) * 0.5
    length = (b - a).length
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=length, location=mid)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    assign_single(obj, mat)
    return obj


def add_visual_accents(lib: dict[str, bpy.types.Material]) -> list[dict]:
    rows = []
    # Board-level visible accents: small pads, IC blocks, port cores, and labels
    # are audit texture cues, not accepted geometry truth.
    for idx, (loc, scale, mat_key) in enumerate(
        [
            ((-0.018, 0.036, 0.0169), (0.009, 0.006, 0.00018), "connector_core"),
            ((0.005, 0.061, 0.0169), (0.010, 0.006, 0.00018), "connector_core"),
            ((0.018, 0.040, 0.0169), (0.007, 0.005, 0.00018), "connector_core"),
            ((-0.010, 0.030, 0.0172), (0.016, 0.0013, 0.00016), "gold_pad"),
            ((0.016, 0.056, 0.0172), (0.014, 0.0013, 0.00016), "gold_pad"),
            ((0.003, 0.047, 0.0104), (0.017, 0.030, 0.00015), "white_label"),
            ((0.026, 0.069, 0.0125), (0.010, 0.0010, 0.0040), "connector_core"),
            ((0.029, 0.068, 0.0237), (0.007, 0.0012, 0.0038), "connector_core"),
        ]
    ):
        obj = flat_box(f"pbr006_n150_pcb_accent_{idx:02d}", Vector(loc), scale, lib[mat_key])
        rows.append({"object": obj.name, "purpose": "whole-aircraft electronics accent", "material": lib[mat_key].name})
    for idx, (a, b, mat_key) in enumerate(
        [
            ((0.012, 0.034, 0.008), (0.045, 0.073, 0.012), "red_wire"),
            ((0.006, 0.038, 0.009), (0.036, 0.071, 0.011), "blue_wire"),
            ((0.018, 0.041, 0.010), (0.046, 0.064, 0.013), "yellow_wire"),
            ((-0.018, 0.030, 0.006), (-0.044, 0.062, 0.010), "red_wire"),
        ]
    ):
        obj = cylinder_between(f"pbr006_colored_wire_accent_{idx:02d}", Vector(a), Vector(b), 0.00085, lib[mat_key])
        rows.append({"object": obj.name, "purpose": "whole-aircraft colored wire accent", "material": lib[mat_key].name})
    for idx, (loc, scale, mat_key) in enumerate(
        [
            ((0.000, 0.021, 0.036), (0.032, 0.017, 0.00020), "white_label"),
            ((0.000, 0.021, 0.0363), (0.019, 0.004, 0.00020), "red_label"),
        ]
    ):
        obj = flat_box(f"pbr006_battery_label_accent_{idx:02d}", Vector(loc), scale, lib[mat_key])
        rows.append({"object": obj.name, "purpose": "battery heat-shrink label cue", "material": lib[mat_key].name})
    # Reassert strong mirror strip highlights on MID-360 dome for the user's
    # reflective-glass concern.
    for idx, (loc, scale) in enumerate(
        [
            ((-0.010, 0.032, 0.1111), (0.0030, 0.019, 0.00014)),
            ((0.002, 0.032, 0.1114), (0.0024, 0.022, 0.00014)),
            ((0.014, 0.032, 0.1110), (0.0018, 0.018, 0.00014)),
        ]
    ):
        obj = flat_box(f"pbr006_mid360_mirror_reflection_strip_{idx:02d}", Vector(loc), scale, lib["mirror_white"])
        obj.rotation_euler[2] = math.radians(8.0)
        rows.append({"object": obj.name, "purpose": "MID-360 mirror-like white reflection strip", "material": lib["mirror_white"].name})
    return rows


def object_bounds(objs: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for obj in objs:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            p = obj.matrix_world @ Vector(corner)
            mn.x = min(mn.x, p.x)
            mn.y = min(mn.y, p.y)
            mn.z = min(mn.z, p.z)
            mx.x = max(mx.x, p.x)
            mx.y = max(mx.y, p.y)
            mx.z = max(mx.z, p.z)
    return mn, mx


def setup_camera_and_lights() -> dict:
    mesh_objs = [obj for obj in bpy.context.scene.objects if obj.type == "MESH" and not obj.hide_render]
    mn, mx = object_bounds(mesh_objs)
    center = (mn + mx) * 0.5
    for obj in list(bpy.context.scene.objects):
        if obj.name.startswith("pbr006_review_light_") or obj.name.startswith("PBR006_Render_Camera"):
            bpy.data.objects.remove(obj, do_unlink=True)
    for name, loc, energy, size in [
        ("pbr006_review_light_key_large", center + Vector((0.18, -0.33, 0.30)), 165.0, 0.38),
        ("pbr006_review_light_soft_top", center + Vector((-0.16, -0.04, 0.38)), 70.0, 0.50),
        ("pbr006_review_light_front_strip", center + Vector((0.02, -0.30, 0.075)), 55.0, 0.20),
        ("pbr006_review_light_glass_rim", center + Vector((-0.22, 0.16, 0.16)), 85.0, 0.18),
    ]:
        data = bpy.data.lights.new(name, type="AREA")
        data.energy = energy
        data.size = size
        obj = bpy.data.objects.new(name, data)
        obj.location = loc
        bpy.context.collection.objects.link(obj)
    cam_data = bpy.data.cameras.new("PBR006_Render_Camera")
    cam = bpy.data.objects.new("PBR006_Render_Camera", cam_data)
    cam.data.type = "ORTHO"
    cam.data.clip_start = 0.001
    cam.data.clip_end = 100.0
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return {"bounds_min": [round(v, 6) for v in mn], "bounds_max": [round(v, 6) for v in mx], "center": [round(v, 6) for v in center]}


def configure_cycles(spec: dict) -> None:
    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 80
    bpy.context.scene.render.resolution_x = spec["resolution"][0]
    bpy.context.scene.render.resolution_y = spec["resolution"][1]
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"
    bpy.context.scene.view_settings.exposure = spec["exposure"]
    bpy.context.scene.view_settings.gamma = 1.0
    bpy.context.scene.world.color = spec["world"]


def render_outputs(center: Vector) -> list[dict]:
    out_rows = []
    cam = bpy.context.scene.camera
    assert cam is not None
    for spec in RENDER_SPECS:
        configure_cycles(spec)
        offset = Vector(spec["camera_offset"])
        cam.location = center + offset
        cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
        cam.data.ortho_scale = spec["ortho_scale"]
        out = EVIDENCE_DIR / f"{spec['name']}.png"
        bpy.context.scene.render.filepath = str(out)
        bpy.ops.render.render(write_still=True)
        out_rows.append({
            "name": spec["name"],
            "path": project_relative(out),
            "ortho_scale": spec["ortho_scale"],
            "camera_offset": list(spec["camera_offset"]),
            "claim": "rendered Blender visual/PBR review evidence only",
        })
    return out_rows


def project_relative(path: Path) -> str:
    return path.resolve().relative_to(PROJECT_ROOT.resolve()).as_posix()


def material_stats() -> dict:
    rows = []
    greyish = []
    family_counts = {key: 0 for key in MATERIAL_FAMILY_KEYWORDS}
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        combined = obj.name
        for family, keys in MATERIAL_FAMILY_KEYWORDS.items():
            if any(key.upper() in combined.upper() for key in keys):
                family_counts[family] += 1
                break
        mats = []
        for slot in obj.material_slots:
            mat = slot.material
            if mat is None:
                continue
            rgba = list(mat.diffuse_color)
            r, g, b, a = rgba
            mx = max(r, g, b)
            mn = min(r, g, b)
            sat = 0.0 if mx <= 1e-9 else (mx - mn) / mx
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            row = {
                "object": obj.name,
                "material": mat.name,
                "diffuse": [round(v, 4) for v in rgba],
                "saturation": round(sat, 4),
                "luminance": round(lum, 4),
                "alpha": round(a, 4),
                "blend": mat.blend_method,
            }
            mats.append(row)
            if sat < 0.10 and 0.18 < lum < 0.82 and a > 0.85 and not mat.name.startswith(("PBR006_Darker_Brushed_Nickel", "PBR006_MID360_Satin")):
                greyish.append(row)
        if mats:
            rows.extend(mats)
    return {
        "mesh_object_count": len([obj for obj in bpy.context.scene.objects if obj.type == "MESH"]),
        "material_assignment_count": len(rows),
        "family_object_counts": family_counts,
        "remaining_low_saturation_mid_luminance_risk_count": len(greyish),
        "remaining_low_saturation_mid_luminance_sample": greyish[:80],
    }


def main() -> None:
    start = time.time()
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))

    clear_task_006_overlays()
    lib = material_library()
    material_edits = enhance_existing_materials(lib)
    object_edits = apply_object_level_corrections(lib)
    overlay_rows = add_visual_accents(lib)
    scene_bounds = setup_camera_and_lights()
    center = Vector(scene_bounds["center"])
    render_rows = render_outputs(center)
    stats = material_stats()
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND))

    manifest = {
        "schema_version": "mosim.sunray150_pbr_whole_aircraft_realism.v1",
        "request_id": "RFLY-MOSIM-SUNRAY150-PBR-WHOLE-AIRCRAFT-GREY-CAD-REALISM-20260607-006",
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "source_blend": project_relative(BLEND),
        "edited_blend": project_relative(BLEND),
        "department_local_goal": "Reduce whole-aircraft grey CAD appearance in the accepted DAE-derived Sunray150 Blender audit asset while preserving geometry and simulation boundaries.",
        "material_edits": material_edits,
        "object_level_reassignments": object_edits,
        "review_overlays": overlay_rows,
        "render_outputs": render_rows,
        "scene_bounds": scene_bounds,
        "stats": stats,
        "manual_review_status": "pending_user_visual_pass_fail",
        "claim_boundary": {
            "visual_asset_only": True,
            "final_material_acceptance": False,
            "ue_import_export_final_acceptance": False,
            "geometry_modified": False,
            "rotor_centers_modified": False,
            "dynamics_modified": False,
            "fast_lio_extrinsics_modified": False,
            "ros2_mworks_ue_runtime_modified": False,
            "controller_or_planner_modified": False,
        },
        "elapsed_sec": round(time.time() - start, 3),
    }
    MATERIAL_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(project_relative(MATERIAL_MANIFEST))
    for row in render_rows:
        print(row["path"])


if __name__ == "__main__":
    main()
