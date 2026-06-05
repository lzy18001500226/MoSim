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
TEXTURE_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Textures"
BLEND = AUDIT_DIR / "sunray150_dae_mid360_realistic_material_audit.blend"
OUT_DIR = AUDIT_DIR / "component_material_reviews"
MANIFEST = OUT_DIR / "sunray150_component_material_reviews_manifest.json"
TEXTURE_MAP_PROP = "_sunray150_review_texture_maps_json"


COMPONENTS = [
    {
        "name": "mid360_sensor",
        "center": (0.0, 0.028, 0.084),
        "camera_offset": (0.058, -0.118, 0.040),
        "ortho_scale": 0.074,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -2.90,
        "world_color": (0.035, 0.037, 0.040),
        "absolute_light_energy": 9.0,
        "target_object_keys": ("AUDIT_STANDALONE_MID360",),
        "keep_font_keys": ("decal_mid360_livox_front",),
        "material_gate": "silver-grey MID-360 housing, dark blue/teal glossy optical dome, black connector/base, readable screws.",
    },
    {
        "name": "mid360_protection_frame",
        "center": (0.0, 0.028, 0.076),
        "camera_offset": (0.018, -0.140, 0.026),
        "ortho_scale": 0.108,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": 0.0,
        "world_color": (0.62, 0.63, 0.64),
        "absolute_light_energy": 0.0,
        "review_material": "satin_dark_grey",
        "target_object_keys": ("MID360_PROTECT_ARC", "MID-360_4_ASM"),
        "material_gate": "black/dark grey MID-360 protection frame and mount hardware, not white CAD.",
    },
    {
        "name": "carbon_frame",
        "center": (0.0, 0.008, 0.018),
        "camera_offset": (0.070, -0.092, 0.060),
        "ortho_scale": 0.100,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": 0.0,
        "world_color": (0.42, 0.43, 0.44),
        "absolute_light_energy": 0.0,
        "review_material": "carbon_fiber_pbr_maps",
        "target_material_names": ("Sunray150_Texture_CarbonFiber_Woven_Graphite",),
        "target_object_keys": (
            "DAE_FULL_MAIN_STRUCTURE.1_MAIN_STRUCTURE",
            "DAE_FULL_TOP_PANNEL.1_TOP",
            "DAE_FULL_Fill.1",
        ),
        "material_gate": "dark woven carbon plates/arms with visible diagonal weave from PBR maps and no white CAD fallback.",
    },
    {
        "name": "aluminum_standoffs",
        "center": (0.040, 0.020, 0.020),
        "camera_offset": (0.080, -0.086, 0.056),
        "ortho_scale": 0.105,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -1.20,
        "world_color": (0.10, 0.105, 0.105),
        "absolute_light_energy": 6.0,
        "review_material": "gold_anodized_aluminum",
        "target_material_names": ("Sunray150_Texture_Gold_7075_Aluminum_Standoffs",),
        "target_object_keys": ("AL_COLUMNS", "AL_COLUMS", "YUNDRONE_AL_COLUMNS"),
        "material_gate": "gold anodized 7-series aluminum, metallic/satin, not plastic yellow.",
    },
    {
        "name": "front_camera",
        "center": (0.0, 0.09365, 0.0260),
        "camera_offset": (0.030, -0.075, 0.028),
        "ortho_scale": 0.058,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -0.60,
        "world_color": (0.16, 0.165, 0.17),
        "absolute_light_energy": 14.0,
        "review_material": "camera_matte_black",
        "auto_center_from_targets": True,
        "target_object_keys": (
            "front_usb_camera_lens_glass_overlay",
            "DAE_FULL_FRONT_CAMERA_PartBody",
            "DAE_FULL_FRONT_CAMERA_CONNECTOR.1",
        ),
        "exclude_object_keys": ("CABLE_FRONT_CAMERA", "CABLE_BOTTOM_CAMERA"),
        "material_gate": "black USB camera body, dark glass lens, visible bracket/screw detail.",
    },
    {
        "name": "steel_fasteners",
        "center": (0.018, 0.026, 0.010),
        "camera_offset": (0.065, -0.076, 0.050),
        "ortho_scale": 0.092,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -1.15,
        "world_color": (0.070, 0.074, 0.076),
        "absolute_light_energy": 5.0,
        "review_material": "dark_chromoly_steel",
        "target_material_names": ("Sunray150_Texture_Dark_Chromoly_Steel_Screws",),
        "target_object_keys": (),
        "material_gate": "dark chromoly/alloy steel screws, nuts, and inserts with visible metal highlights and hex/socket detail.",
    },
    {
        "name": "electronics_connectors",
        "center": (0.028, 0.050, 0.015),
        "camera_offset": (0.090, -0.075, 0.030),
        "ortho_scale": 0.080,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -2.25,
        "world_color": (0.045, 0.047, 0.049),
        "absolute_light_energy": 4.5,
        "target_object_keys": ("N150_AllCATPart", "ESC_SPEEDYBEE", "A_USB", "HDMI", "NGFF", "PJ311", "CABLE", "WIRE"),
        "material_gate": "dark PCB/soldermask, nickel connector shells, black plastic cores, readable cable colors.",
    },
    {
        "name": "pcb_boards",
        "center": (0.026, 0.048, 0.017),
        "camera_offset": (0.080, -0.070, 0.034),
        "ortho_scale": 0.072,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -1.70,
        "world_color": (0.050, 0.052, 0.052),
        "absolute_light_energy": 5.5,
        "target_material_names": ("Sunray150_Texture_PCB_Black_Soldermask", "Sunray150_Texture_PCB_Green_Soldermask"),
        "target_object_keys": ("ESC_SPEEDYBEE", "MAIN_BOARD", "PCBModel", "N150_AllCATPart.1_Part1", "N150_AllCATPart.1_Part2"),
        "material_gate": "black/dark-green PCB soldermask with readable pads, traces, IC packages, and board edge.",
    },
    {
        "name": "n150_stack_boards",
        "center": (0.0, 0.050, 0.0155),
        "camera_offset": (0.050, -0.070, 0.026),
        "ortho_scale": 0.062,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -1.90,
        "world_color": (0.050, 0.052, 0.052),
        "absolute_light_energy": 4.8,
        "auto_center_from_targets": True,
        "target_object_keys": (
            "N150_AllCATPart.1_Part1",
            "N150_AllCATPart.1_Part2",
            "N150_AllCATPart.1_TN_MTS400",
            "N150_AllCATPart.1_TURBO_FAN",
            "decal_n150",
        ),
        "keep_font_keys": ("decal_n150",),
        "target_material_names": ("Sunray150_Texture_PCB_Black_Soldermask",),
        "material_gate": "shell-removed N150: exposed PCB/board stack, M.2 storage, fan/heatsink cues, not a closed mini-PC shell.",
    },
    {
        "name": "n150_internal_pcb_audit",
        "center": (0.0, 0.050, 0.0155),
        "camera_offset": (0.024, -0.034, 0.050),
        "ortho_scale": 0.040,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -1.55,
        "world_color": (0.052, 0.054, 0.056),
        "absolute_light_energy": 6.0,
        "auto_center_from_targets": True,
        "target_object_keys": (
            "decal_n150_ic_package",
            "decal_n150_gold_pad_bank",
            "decal_n150_m2_label",
            "decal_n150_m2_label_text",
        ),
        "keep_font_keys": ("decal_n150_m2_label_text",),
        "exclude_object_keys": (
            "N150_AllCATPart.1_TURBO_FAN",
            "N150_AllCATPart.1_Part2",
        ),
        "material_gate": "shell-removed N150 internal board audit: hidden cooling geometry excluded so exposed black PCB, IC packages, M.2 label cue, pads/traces can be checked separately.",
    },
    {
        "name": "n150_ports",
        "center": (0.028, 0.047, 0.018),
        "camera_offset": (0.042, -0.070, 0.014),
        "ortho_scale": 0.052,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -1.50,
        "world_color": (0.055, 0.056, 0.058),
        "absolute_light_energy": 6.3,
        "auto_center_from_targets": True,
        "target_material_names": ("Sunray150_Texture_USB_HDMI_Nickel_Shell", "Sunray150_Texture_Connector_Black_Core"),
        "target_object_keys": (
            "N150_AllCATPart.1_A_USB_9P",
            "N150_AllCATPart.1_A_USB_24P",
            "N150_AllCATPart.1_HDMI connector",
            "N150_AllCATPart.1_PJ311D",
            "N150_AllCATPart.1_A_NGFF",
            "N150_AllCATPart.1_C-3-1734795-2",
            "decal_n150",
        ),
        "keep_font_keys": ("decal_n150",),
        "material_gate": "shell-removed N150 interface side: nickel port shells, black plastic cores, visible USB/HDMI/Type-C/RJ45/NGFF connector separation.",
    },
    {
        "name": "n150_cooling_storage",
        "center": (0.000, 0.048, 0.033),
        "camera_offset": (0.042, -0.052, 0.032),
        "ortho_scale": 0.054,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -1.45,
        "world_color": (0.052, 0.054, 0.056),
        "absolute_light_energy": 5.8,
        "auto_center_from_targets": True,
        "target_object_keys": (
            "N150_AllCATPart.1_TN_MTS400",
            "N150_AllCATPart.1_TURBO_FAN",
            "N150_AllCATPart.1_Part1",
            "N150_AllCATPart.1_Part2",
            "decal_n150",
        ),
        "keep_font_keys": ("decal_n150",),
        "material_gate": "shell-removed N150 cooling/storage area: black PCB, dark ICs, metallic M.2/SSD label cue, black fan or heatsink detail.",
    },
    {
        "name": "esc_board",
        "center": (0.0, 0.00065, -0.0027),
        "camera_offset": (0.040, -0.048, 0.032),
        "ortho_scale": 0.045,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -1.65,
        "world_color": (0.050, 0.052, 0.052),
        "absolute_light_energy": 5.5,
        "target_object_keys": ("ESC_SPEEDYBEE", "MAIN_BOARD"),
        "target_material_names": ("Sunray150_Texture_PCB_Black_Soldermask",),
        "material_gate": "ESC board black soldermask with small connector pins/components visible, not a flat grey plate.",
    },
    {
        "name": "connector_shells",
        "center": (0.034, 0.060, 0.010),
        "camera_offset": (0.075, -0.062, 0.026),
        "ortho_scale": 0.058,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -1.45,
        "world_color": (0.055, 0.056, 0.058),
        "absolute_light_energy": 6.5,
        "target_material_names": ("Sunray150_Texture_USB_HDMI_Nickel_Shell", "Sunray150_Texture_Connector_Black_Core"),
        "target_object_keys": ("A_USB", "HDMI", "RJ45", "NGFF", "PJ311", "CONNECTOR"),
        "material_gate": "nickel/silver connector shells, black plastic cores, visible port openings and pin detail.",
    },
    {
        "name": "cables_wires",
        "center": (0.010, 0.040, 0.004),
        "camera_offset": (0.095, -0.082, 0.030),
        "ortho_scale": 0.085,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -1.35,
        "world_color": (0.055, 0.056, 0.058),
        "absolute_light_energy": 7.5,
        "target_material_names": (
            "Sunray150_Texture_Rubber_Cable_Black",
            "Sunray150_Texture_Red_Silicone_Wire",
            "Sunray150_Texture_Blue_Silicone_Wire",
            "Sunray150_Texture_Yellow_Silicone_Wire",
        ),
        "target_object_keys": ("CABLE", "WIRE", "red_wire_hint", "blue_wire_hint", "yellow_wire_hint"),
        "material_gate": "black rubber/silicone cable plus readable red/blue/yellow signal-wire cues.",
    },
    {
        "name": "motor_propeller",
        "center": (0.055, 0.055, -0.011),
        "camera_offset": (0.045, -0.052, 0.045),
        "ortho_scale": 0.061,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -1.85,
        "world_color": (0.048, 0.050, 0.052),
        "absolute_light_energy": 6.0,
        "target_object_keys": ("MOTOR_2104", "TriBlade", "SCREW_BUTTON_HEAD_M2_8MM"),
        "material_gate": "black motor bell, copper windings, steel screws, dark smoked tri-blade propeller without white patches.",
    },
    {
        "name": "motor_only",
        "center": (0.055, 0.055, -0.006),
        "camera_offset": (0.036, -0.044, 0.034),
        "ortho_scale": 0.044,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -1.70,
        "world_color": (0.050, 0.052, 0.054),
        "absolute_light_energy": 6.5,
        "target_object_keys": ("MOTOR_2104", "SCREW_BUTTON_HEAD_M2_8MM", "decal_motor_yundrone", "decal_motor_lava"),
        "exclude_object_keys": ("decal_motor_gold_ring",),
        "material_gate": "dark motor bell, copper windings, steel screws, subtle YUN DRONE/LAVA label cues.",
    },
    {
        "name": "tri_blade_propeller",
        "center": (0.054, 0.054, -0.014),
        "camera_offset": (0.052, -0.050, 0.038),
        "ortho_scale": 0.058,
        "view_transform": "Standard",
        "look": "Medium High Contrast",
        "exposure": -2.30,
        "world_color": (0.030, 0.031, 0.032),
        "absolute_light_energy": 2.2,
        "auto_center_from_targets": True,
        "review_material": "smoked_propeller",
        "target_object_keys": ("TriBlade_flipped_around_screw_axis_rotor_0_front_right",),
        "material_gate": "accepted tri-blade propeller, smoked translucent plastic with visible grey thickness and no white audit-color washout.",
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


def add_review_image_texture(
    mat: bpy.types.Material,
    image_name: str,
    *,
    target: str,
    non_color: bool = False,
    strength: float | None = None,
    distance: float = 0.0006,
) -> bool:
    path = TEXTURE_DIR / image_name
    if not path.exists() or not mat.use_nodes:
        return False
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return False
    texcoord = next((node for node in nodes if node.type == "TEX_COORD"), None)
    if texcoord is None:
        texcoord = nodes.new(type="ShaderNodeTexCoord")
    mapping = nodes.new(type="ShaderNodeMapping")
    vector_output = texcoord.outputs.get("Generated") or texcoord.outputs.get("Object")
    if vector_output is not None:
        links.new(vector_output, mapping.inputs["Vector"])
    tex = nodes.new(type="ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(path), check_existing=True)
    if non_color:
        tex.image.colorspace_settings.name = "Non-Color"
    links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
    if target == "Base Color" and "Base Color" in bsdf.inputs:
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    elif target == "Roughness" and "Roughness" in bsdf.inputs:
        links.new(tex.outputs["Color"], bsdf.inputs["Roughness"])
    elif target == "Bump" and "Normal" in bsdf.inputs:
        bump = nodes.new(type="ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.035 if strength is None else strength
        bump.inputs["Distance"].default_value = distance
        links.new(tex.outputs["Color"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    else:
        return False
    try:
        records = json.loads(mat.get(TEXTURE_MAP_PROP, "[]"))
    except json.JSONDecodeError:
        records = []
    records.append(
        {
            "target": target,
            "image": image_name,
            "project_relative_path": str(path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "colorspace": tex.image.colorspace_settings.name,
        }
    )
    mat[TEXTURE_MAP_PROP] = json.dumps(records, ensure_ascii=False)
    return True


def review_texture_maps(mat: bpy.types.Material | None) -> list[dict]:
    if mat is None:
        return []
    try:
        value = mat.get(TEXTURE_MAP_PROP, "[]")
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []


def make_review_pbr_map_material(
    name: str,
    *,
    fallback_rgba: tuple[float, float, float, float],
    prefix: str,
    roughness: float,
    metallic: float = 0.0,
    specular: float = 0.12,
    bump_strength: float = 0.025,
    bump_distance: float = 0.0006,
) -> bpy.types.Material:
    mat = make_review_principled_material(
        name,
        fallback_rgba,
        roughness=roughness,
        metallic=metallic,
        specular=specular,
    )
    add_review_image_texture(mat, f"{prefix}_base.png", target="Base Color")
    add_review_image_texture(mat, f"{prefix}_roughness.png", target="Roughness", non_color=True)
    add_review_image_texture(
        mat,
        f"{prefix}_bump.png",
        target="Bump",
        non_color=True,
        strength=bump_strength,
        distance=bump_distance,
    )
    return mat


def make_review_carbon_pbr_map_material() -> bpy.types.Material:
    return make_review_pbr_map_material(
        "Sunray150_ComponentReview_Dark_Woven_Carbon_PBR_Map_Audit",
        fallback_rgba=(0.010, 0.012, 0.012, 1.0),
        prefix="sunray150_carbon_fiber",
        roughness=0.48,
        metallic=0.0,
        specular=0.24,
        bump_strength=0.055,
        bump_distance=0.0007,
    )


def make_review_smoked_propeller_pbr_map_material() -> bpy.types.Material:
    mat = bpy.data.materials.new("Sunray150_ComponentReview_Smoked_Translucent_Plastic_Propeller_PBR_Map_Audit")
    mat.diffuse_color = (0.038, 0.043, 0.041, 0.68)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type="ShaderNodeOutputMaterial")
    mix = nodes.new(type="ShaderNodeMixShader")
    transparent = nodes.new(type="ShaderNodeBsdfTransparent")
    principled = nodes.new(type="ShaderNodeBsdfPrincipled")
    translucent = nodes.new(type="ShaderNodeBsdfTranslucent")
    plastic_mix = nodes.new(type="ShaderNodeMixShader")

    mix.inputs["Fac"].default_value = 0.08
    plastic_mix.inputs["Fac"].default_value = 0.10
    transparent.inputs["Color"].default_value = (0.035, 0.040, 0.038, 1.0)
    translucent.inputs["Color"].default_value = (0.070, 0.082, 0.078, 1.0)
    if "Base Color" in principled.inputs:
        principled.inputs["Base Color"].default_value = (0.038, 0.043, 0.041, 1.0)
    if "Roughness" in principled.inputs:
        principled.inputs["Roughness"].default_value = 0.36
    if "Metallic" in principled.inputs:
        principled.inputs["Metallic"].default_value = 0.0
    if "Specular IOR Level" in principled.inputs:
        principled.inputs["Specular IOR Level"].default_value = 0.32
    elif "Specular" in principled.inputs:
        principled.inputs["Specular"].default_value = 0.32
    if "Coat Weight" in principled.inputs:
        principled.inputs["Coat Weight"].default_value = 0.12
    if "Coat Roughness" in principled.inputs:
        principled.inputs["Coat Roughness"].default_value = 0.24

    links.new(principled.outputs["BSDF"], plastic_mix.inputs[1])
    links.new(translucent.outputs["BSDF"], plastic_mix.inputs[2])
    links.new(plastic_mix.outputs["Shader"], mix.inputs[1])
    links.new(transparent.outputs["BSDF"], mix.inputs[2])
    links.new(mix.outputs["Shader"], output.inputs["Surface"])

    add_review_image_texture(mat, "sunray150_smoked_propeller_base.png", target="Base Color")
    add_review_image_texture(mat, "sunray150_smoked_propeller_roughness.png", target="Roughness", non_color=True)
    add_review_image_texture(
        mat,
        "sunray150_smoked_propeller_bump.png",
        target="Bump",
        non_color=True,
        strength=0.007,
        distance=0.00016,
    )
    # The accepted STL has no authored UVs. In Blender 5.0, the generated
    # object-space texture is only a procedural starting point. Keep all three
    # PBR audit maps connected, but avoid glass-like transmission; thin
    # propellers should read as smoked translucent grey plastic, not clear glass
    # or opaque carbon.
    mat.blend_method = "HASHED"
    mat.use_screen_refraction = False
    mat.show_transparent_back = True
    return mat


def make_review_gold_anodized_aluminum_material() -> bpy.types.Material:
    mat = make_review_principled_material(
        "Sunray150_ComponentReview_Gold_Anodized_Aluminum_Audit",
        (0.235, 0.145, 0.038, 1.0),
        roughness=0.46,
        metallic=0.92,
        specular=0.26,
    )
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if not bsdf:
        return mat

    noise = nodes.new(type="ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 85.0
    noise.inputs["Detail"].default_value = 12.0
    noise.inputs["Roughness"].default_value = 0.58

    ramp = nodes.new(type="ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.18
    ramp.color_ramp.elements[0].color = (0.145, 0.082, 0.018, 1.0)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (0.430, 0.275, 0.072, 1.0)

    bump = nodes.new(type="ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.030
    bump.inputs["Distance"].default_value = 0.00042

    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    if "Base Color" in bsdf.inputs:
        links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    if "Normal" in bsdf.inputs:
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def make_review_dark_chromoly_steel_material() -> bpy.types.Material:
    mat = make_review_principled_material(
        "Sunray150_ComponentReview_Dark_Chromoly_Steel_Audit",
        (0.018, 0.018, 0.016, 1.0),
        roughness=0.50,
        metallic=0.86,
        specular=0.14,
    )
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if not bsdf:
        return mat

    noise = nodes.new(type="ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 115.0
    noise.inputs["Detail"].default_value = 10.0
    noise.inputs["Roughness"].default_value = 0.62

    bump = nodes.new(type="ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.018
    bump.inputs["Distance"].default_value = 0.00020

    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    if "Normal" in bsdf.inputs:
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
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


def is_target_object(obj: bpy.types.Object, component: dict) -> bool:
    if obj.type != "MESH":
        keys = tuple(component.get("keep_font_keys", ()))
        return obj.type == "FONT" and bool(keys) and any(key in obj.name for key in keys)
    exclude_keys = tuple(component.get("exclude_object_keys", ()))
    if exclude_keys and any(key in obj.name for key in exclude_keys):
        return False
    keys = tuple(component.get("target_object_keys", ()))
    material_names = tuple(component.get("target_material_names", ()))
    key_match = bool(keys) and any(key in obj.name for key in keys)
    material_match = bool(material_names) and any(
        mat is not None and mat.name in material_names
        for mat in obj.data.materials
    )
    if material_names and keys:
        return key_match or material_match
    if material_names:
        return material_match
    return key_match


def snapshot_object_state() -> dict[str, dict]:
    return {
        obj.name: {
            "materials": [slot.material for slot in obj.material_slots],
            "hide_render": obj.hide_render,
            "hide_viewport": obj.hide_viewport,
        }
        for obj in bpy.context.scene.objects
        if obj.type in {"MESH", "FONT"}
    }


def restore_object_state(snapshot: dict[str, dict]) -> None:
    for obj in bpy.context.scene.objects:
        if obj.type not in {"MESH", "FONT"} or obj.name not in snapshot:
            continue
        state = snapshot[obj.name]
        obj.hide_render = state["hide_render"]
        obj.hide_viewport = state["hide_viewport"]
        if obj.type != "MESH":
            continue
        for idx, mat in enumerate(state["materials"]):
            if idx < len(obj.material_slots):
                obj.material_slots[idx].material = mat


def apply_component_isolation(component: dict, context_mat: bpy.types.Material) -> dict:
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
            (0.105, 0.110, 0.108, 1.0),
        )
    elif review_material == "carbon_fiber" and override_mat is None:
        override_mat = make_review_carbon_emission_material()
    elif review_material == "carbon_fiber_pbr_maps" and override_mat is None:
        override_mat = make_review_carbon_pbr_map_material()
    elif review_material == "carbon_fiber_principled" and override_mat is None:
        override_mat = make_review_carbon_material()
    elif review_material == "gold_anodized_aluminum" and override_mat is None:
        override_mat = make_review_gold_anodized_aluminum_material()
    elif review_material == "dark_chromoly_steel" and override_mat is None:
        override_mat = make_review_dark_chromoly_steel_material()
    elif review_material == "camera_matte_black" and override_mat is None:
        override_mat = make_review_principled_material(
            "Sunray150_ComponentReview_Camera_Matte_Black_Polymer_Audit",
            (0.010, 0.010, 0.009, 1.0),
            roughness=0.74,
            metallic=0.0,
            specular=0.20,
        )
    elif review_material == "smoked_propeller" and override_mat is None:
        override_mat = make_review_smoked_propeller_pbr_map_material()
    target_count = 0
    context_count = 0
    for obj in bpy.context.scene.objects:
        if obj.type in {"CAMERA", "LIGHT"}:
            continue
        if obj.type != "MESH":
            keep_non_mesh = is_target_object(obj, component)
            obj.hide_render = not keep_non_mesh
            obj.hide_viewport = not keep_non_mesh
            if keep_non_mesh:
                target_count += 1
            else:
                context_count += 1
            continue
        if is_target_object(obj, component):
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
    return {
        "target_object_count": target_count,
        "context_object_count": context_count,
        "override_material": override_mat.name if override_mat is not None else None,
        "override_texture_maps": review_texture_maps(override_mat),
    }


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
    if "absolute_light_energy" in component:
        for obj in bpy.context.scene.objects:
            if obj.type == "LIGHT":
                obj.data.energy = float(component["absolute_light_energy"])
    light_scale = float(component.get("light_scale", 1.0))
    if "absolute_light_energy" not in component and abs(light_scale - 1.0) > 1e-9:
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


def make_review_carbon_material() -> bpy.types.Material:
    mat = bpy.data.materials.new("Sunray150_ComponentReview_Dark_Woven_Carbon_Audit")
    mat.diffuse_color = (0.010, 0.012, 0.012, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if not bsdf:
        return mat
    if "Base Color" in bsdf.inputs:
        bsdf.inputs["Base Color"].default_value = (0.010, 0.012, 0.012, 1.0)
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = 0.48
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = 0.0
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.24
    elif "Specular" in bsdf.inputs:
        bsdf.inputs["Specular"].default_value = 0.24
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.18
    if "Coat Roughness" in bsdf.inputs:
        bsdf.inputs["Coat Roughness"].default_value = 0.20

    wave_a = nodes.new(type="ShaderNodeTexWave")
    wave_a.inputs["Scale"].default_value = 38.0
    wave_a.inputs["Distortion"].default_value = 8.0
    wave_b = nodes.new(type="ShaderNodeTexWave")
    wave_b.inputs["Scale"].default_value = 38.0
    wave_b.inputs["Distortion"].default_value = 8.0
    wave_b.bands_direction = "DIAGONAL"
    mix = nodes.new(type="ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.factor_mode = "UNIFORM"
    mix.inputs["Factor"].default_value = 0.5
    bump = nodes.new(type="ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.055
    bump.inputs["Distance"].default_value = 0.0007
    links.new(wave_a.outputs["Color"], mix.inputs["A"])
    links.new(wave_b.outputs["Color"], mix.inputs["B"])
    links.new(mix.outputs["Result"], bump.inputs["Height"])
    if "Normal" in bsdf.inputs:
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def make_review_carbon_emission_material() -> bpy.types.Material:
    mat = bpy.data.materials.new("Sunray150_ComponentReview_Dark_Woven_Carbon_Emission_Audit")
    mat.diffuse_color = (0.026, 0.030, 0.029, 1.0)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    out = nodes.new(type="ShaderNodeOutputMaterial")
    texcoord = nodes.new(type="ShaderNodeTexCoord")
    mapping = nodes.new(type="ShaderNodeMapping")
    wave_a = nodes.new(type="ShaderNodeTexWave")
    wave_b = nodes.new(type="ShaderNodeTexWave")
    mix = nodes.new(type="ShaderNodeMix")
    ramp = nodes.new(type="ShaderNodeValToRGB")
    emission = nodes.new(type="ShaderNodeEmission")

    mapping.inputs["Scale"].default_value = (1.0, 1.0, 1.0)
    wave_a.inputs["Scale"].default_value = 72.0
    wave_a.inputs["Distortion"].default_value = 1.2
    wave_b.inputs["Scale"].default_value = 72.0
    wave_b.inputs["Distortion"].default_value = 1.2
    try:
        wave_b.bands_direction = "DIAGONAL"
    except TypeError:
        pass
    mix.data_type = "RGBA"
    mix.factor_mode = "UNIFORM"
    mix.inputs["Factor"].default_value = 0.5
    ramp.color_ramp.elements[0].position = 0.14
    ramp.color_ramp.elements[0].color = (0.016, 0.018, 0.018, 1.0)
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = (0.060, 0.068, 0.065, 1.0)
    emission.inputs["Strength"].default_value = 1.0

    links.new(texcoord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], wave_a.inputs["Vector"])
    links.new(mapping.outputs["Vector"], wave_b.inputs["Vector"])
    links.new(wave_a.outputs["Color"], mix.inputs["A"])
    links.new(wave_b.outputs["Color"], mix.inputs["B"])
    links.new(mix.outputs["Result"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], out.inputs["Surface"])
    return mat


def ensure_camera() -> bpy.types.Object:
    cam = bpy.context.scene.camera
    if cam is None:
        cam_data = bpy.data.cameras.new("Sunray150_ComponentReview_Camera")
        cam = bpy.data.objects.new("Sunray150_ComponentReview_Camera", cam_data)
        bpy.context.collection.objects.link(cam)
        bpy.context.scene.camera = cam
    cam.data.type = "ORTHO"
    cam.data.clip_start = 0.001
    cam.data.clip_end = 100.0
    return cam


def material_names_for_component(component: dict) -> list[dict]:
    rows = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        if not is_target_object(obj, component):
            continue
        rows.append(
            {
                "object": obj.name,
                "materials": [mat.name if mat else None for mat in obj.data.materials],
            }
        )
    return rows


def target_bbox_center(component: dict) -> Vector | None:
    coords: list[Vector] = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or not is_target_object(obj, component):
            continue
        coords.extend(obj.matrix_world @ Vector(corner) for corner in obj.bound_box)
    if not coords:
        return None
    mins = Vector((min(point.x for point in coords), min(point.y for point in coords), min(point.z for point in coords)))
    maxs = Vector((max(point.x for point in coords), max(point.y for point in coords), max(point.z for point in coords)))
    return (mins + maxs) * 0.5


def render_component(component: dict) -> dict:
    context_mat = make_context_material()
    object_snapshot = snapshot_object_state()
    render_snapshot = apply_component_render_settings(component)
    isolation = apply_component_isolation(component, context_mat)
    cam = ensure_camera()
    center = target_bbox_center(component) if component.get("auto_center_from_targets") else None
    if center is None:
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
        "absolute_light_energy": component.get("absolute_light_energy"),
        "target_object_keys": list(component["target_object_keys"]),
        "target_material_names": list(component.get("target_material_names", ())),
        "material_gate": component["material_gate"],
        "isolation": isolation,
        "matched_materials": material_names_for_component(component)[:120],
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
