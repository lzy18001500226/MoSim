#!/usr/bin/env python3
"""Build a full Sunray150 DAE + standalone MID-360 assembly audit scene.

This scene keeps aircraft frame, brackets, protection arcs, and non-propeller
parts visible. User-confirmed DAE propeller pattern objects are removed for the
MID-360 mount audit. The only added object is the standalone MID-360 visual at
the manually selected top-panel mount rectangle.
"""

from __future__ import annotations

import importlib.util
import json
import math
import os
import sys
import time
from pathlib import Path

import bpy
from mathutils import Euler, Matrix, Vector


PROJECT_ROOT = Path(r"C:\Users\HP\Desktop\MoSim")
PROP_AUDIT = PROJECT_ROOT / "Scripts" / "UE5" / "assets" / "build_sunray150_with_mid360_propeller_assembly_audit_scene.py"
LIVOX_AUDIT = PROJECT_ROOT / "Scripts" / "UE5" / "assets" / "build_livox_mid360_audit_scene.py"
OUT_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Audit"
OUT_BLEND = OUT_DIR / "sunray150_dae_mid360_realistic_material_audit.blend"
OUT_MANIFEST = OUT_DIR / "sunray150_dae_mid360_realistic_material_audit_manifest.json"
TEXTURE_DIR = PROJECT_ROOT / "UE5" / "MoSimSceneLibrary" / "SourceAssets" / "Sunray150" / "Textures"
TRI_BLADE_PROP_STL = PROJECT_ROOT / "References" / "Sunray" / "simulation" / "sunray_simulator" / "models" / "drone_models" / "sunray150_with_mid360" / "meshes" / "sunray_cw.stl"
AUDIT_VIEW = os.environ.get("AUDIT_VIEW", "full_assembly").strip().lower()
MATERIAL_REVIEW = os.environ.get("MATERIAL_REVIEW", "1").strip().lower() not in {"0", "false", "no"}
SHOW_AUDIT_MARKERS = os.environ.get("SHOW_AUDIT_MARKERS", "0").strip().lower() in {"1", "true", "yes"}
MID360_BASE_VISUAL_SCALE = 1.2
MID360_HOLE_FIT_RELATIVE_SCALE = 1.0
MID360_VISUAL_SCALE = MID360_BASE_VISUAL_SCALE * MID360_HOLE_FIT_RELATIVE_SCALE
MATERIAL_CACHE: dict[str, bpy.types.Material] | None = None

# User-confirmed top-panel hole-loop groups for the MID-360 mount.
TOP_PANEL_MOUNT_HOLES = [
    ("front_left_H20_H21_H22", Vector((-0.018000, 0.056283, 0.050167))),
    ("front_right_H19_H23_H24", Vector((0.017981, 0.056332, 0.050167))),
    ("rear_right_H44_H47_H48", Vector((0.018000, 0.008283, 0.050167))),
    ("rear_left_H43_H45_H46", Vector((-0.018000, 0.008283, 0.050167))),
]

USER_CONFIRMED_PROPELLER_OBJECT_KEYS = (
    "CircPattern.1 | CircPattern.1Mesh",
    "CircPattern.1_ncl1_1 | CircPattern.1_ncl1_1Mesh",
    "CircPattern.1_ncl1_2 | CircPattern.1_ncl1_2Mesh",
    "CircPattern.1_ncl1_3 | CircPattern.1_ncl1_3Mesh",
    "CircPattern.2 | CircPattern.2Mesh",
    "CircPattern.2_ncl1_1 | CircPattern.2_ncl1_1Mesh",
    "PROPELLER_CCW.1\\Scale1 | PROPELLER_CCW.1\\Scale1Mesh",
    "PROPELLER_CCW.2\\Scale1 | PROPELLER_CCW.2\\Scale1Mesh",
    "PROPELLER_CW.1\\NONE | PROPELLER_CW.1\\NONEMesh",
    "PROPELLER_CW.2\\NONE | PROPELLER_CW.2\\NONEMesh",
)

ROTOR_POSES = [
    ("rotor_0_front_right", Vector((0.065, -0.065, -0.025)), "red"),
    ("rotor_1_back_left", Vector((-0.065, 0.065, -0.025)), "blue"),
    ("rotor_2_front_left", Vector((0.065, 0.065, -0.025)), "red"),
    ("rotor_3_back_right", Vector((-0.065, -0.065, -0.025)), "blue"),
]

TRI_BLADE_LOCAL_SCREW_HOLES_MM = (Vector((0.0, -2.5, 2.5)), Vector((0.0, 2.5, 2.5)))
PROP_ORIENTATION_MODE = os.environ.get("PROP_ORIENTATION_MODE", "flipped_around_screw_axis").strip().lower()
# User-audited propeller Z alignment. Units are meters in the assembled scene.
PROP_BASE_TRANSLATION_Z_M = -0.0161
PROP_AUDITED_CONTACT_PLANE_Z_M = -0.021098
PROP_TARGET_SCREW_PLANE_Z_M = -0.0193
PROP_CLEARANCE_M = 0.0001
PROP_USER_FINE_TUNE_Z_M = 0.00015
PROP_TARGET_TRANSLATION_Z_M = (
    PROP_BASE_TRANSLATION_Z_M
    + (PROP_TARGET_SCREW_PLANE_Z_M + PROP_CLEARANCE_M - PROP_AUDITED_CONTACT_PLANE_Z_M)
    + PROP_USER_FINE_TUNE_Z_M
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


prop = load_module(PROP_AUDIT, "sunray_prop_audit_full_mid360")
livox = load_module(LIVOX_AUDIT, "livox_mid360_audit_full_mid360")


def reset_scene() -> None:
    global MATERIAL_CACHE
    MATERIAL_CACHE = None
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.images):
        for item in list(block):
            block.remove(item)


def set_principled_input(bsdf: bpy.types.Node, names: tuple[str, ...], value) -> None:
    for name in names:
        if name in bsdf.inputs:
            bsdf.inputs[name].default_value = value
            return


def make_material(
    name: str,
    rgba: tuple[float, float, float, float],
    *,
    roughness: float = 0.55,
    metallic: float = 0.0,
    alpha: float | None = None,
) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    if alpha is None:
        alpha = rgba[3]
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = next((node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        set_principled_input(bsdf, ("Base Color",), rgba)
        set_principled_input(bsdf, ("Roughness",), roughness)
        set_principled_input(bsdf, ("Metallic",), metallic)
        set_principled_input(bsdf, ("Alpha",), alpha)
    if alpha < 1.0:
        mat.blend_method = "BLEND"
        mat.use_screen_refraction = True
    return mat


def texture_path(name: str) -> Path:
    return TEXTURE_DIR / name


def add_image_texture(mat: bpy.types.Material, image_name: str, *, target: str = "Base Color", non_color: bool = False, strength: float | None = None) -> None:
    if not mat.use_nodes:
        return
    path = texture_path(image_name)
    if not path.exists():
        return
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if not bsdf:
        return
    tex = nodes.new(type="ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(path), check_existing=True)
    if non_color:
        tex.image.colorspace_settings.name = "Non-Color"
    if target == "Base Color" and "Base Color" in bsdf.inputs:
        links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    elif target == "Roughness" and "Roughness" in bsdf.inputs:
        links.new(tex.outputs["Color"], bsdf.inputs["Roughness"])
    elif target == "Bump" and "Normal" in bsdf.inputs:
        bump = nodes.new(type="ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.055 if strength is None else strength
        bump.inputs["Distance"].default_value = 0.0010
        links.new(tex.outputs["Color"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def assign_single_material(obj: bpy.types.Object, mat: bpy.types.Material) -> None:
    """Replace all material slots and force faces to the first slot."""
    if obj.type != "MESH":
        return
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    for poly in obj.data.polygons:
        poly.material_index = 0


def link_noise_to_bump(mat: bpy.types.Material, *, scale: float, detail: float, strength: float, distance: float) -> None:
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if not bsdf:
        return
    noise = nodes.new(type="ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = detail
    noise.inputs["Roughness"].default_value = 0.62
    bump = nodes.new(type="ShaderNodeBump")
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = distance
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    if "Normal" in bsdf.inputs:
        links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def make_carbon_material() -> bpy.types.Material:
    mat = make_material("Sunray150_Texture_CarbonFiber_Woven_Graphite", (0.020, 0.023, 0.023, 1.0), roughness=0.34)
    add_image_texture(mat, "sunray150_carbon_fiber_base.png", target="Base Color")
    add_image_texture(mat, "sunray150_carbon_fiber_roughness.png", target="Roughness", non_color=True)
    add_image_texture(mat, "sunray150_carbon_fiber_bump.png", target="Bump", non_color=True, strength=0.070)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        set_principled_input(bsdf, ("Base Color",), (0.018, 0.020, 0.020, 1.0))
        set_principled_input(bsdf, ("Roughness",), 0.29)
        set_principled_input(bsdf, ("Metallic",), 0.0)
        wave = nodes.new(type="ShaderNodeTexWave")
        wave.inputs["Scale"].default_value = 34.0
        wave.inputs["Distortion"].default_value = 4.0
        bump = nodes.new(type="ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.030
        bump.inputs["Distance"].default_value = 0.00055
        links.new(wave.outputs["Color"], bump.inputs["Height"])
        if "Normal" in bsdf.inputs:
            links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    link_noise_to_bump(mat, scale=145.0, detail=14.0, strength=0.055, distance=0.0011)
    return mat


def make_warm_anodized_material(name: str, rgba: tuple[float, float, float, float], *, roughness: float) -> bpy.types.Material:
    mat = make_material(name, rgba, roughness=roughness, metallic=0.82)
    add_image_texture(mat, "sunray150_gold_anodized_aluminum_base.png", target="Base Color")
    add_image_texture(mat, "sunray150_gold_anodized_aluminum_roughness.png", target="Roughness", non_color=True)
    add_image_texture(mat, "sunray150_gold_anodized_aluminum_bump.png", target="Bump", non_color=True, strength=0.028)
    link_noise_to_bump(mat, scale=135.0, detail=12.0, strength=0.018, distance=0.00045)
    return mat


def make_scratched_metal_material(name: str, rgba: tuple[float, float, float, float], *, roughness: float, metallic: float) -> bpy.types.Material:
    mat = make_material(name, rgba, roughness=roughness, metallic=metallic)
    if "MID360" in name:
        prefix = "mid360_silver_grey_aluminum"
    else:
        prefix = "sunray150_dark_anodized_metal"
    add_image_texture(mat, f"{prefix}_base.png", target="Base Color")
    add_image_texture(mat, f"{prefix}_roughness.png", target="Roughness", non_color=True)
    add_image_texture(mat, f"{prefix}_bump.png", target="Bump", non_color=True, strength=0.030)
    link_noise_to_bump(mat, scale=95.0, detail=10.0, strength=0.020, distance=0.00065)
    return mat


def make_plastic_material(name: str, rgba: tuple[float, float, float, float], *, roughness: float) -> bpy.types.Material:
    mat = make_material(name, rgba, roughness=roughness, metallic=0.0)
    if "Rubber" in name or "Cable" in name or "Battery" in name:
        add_image_texture(mat, "sunray150_black_rubber_base.png", target="Base Color")
        add_image_texture(mat, "sunray150_black_rubber_roughness.png", target="Roughness", non_color=True)
        add_image_texture(mat, "sunray150_black_rubber_bump.png", target="Bump", non_color=True, strength=0.045)
    elif "Guard" in name:
        add_image_texture(mat, "sunray150_smoked_translucent_guard_base.png", target="Base Color")
        add_image_texture(mat, "sunray150_smoked_translucent_guard_roughness.png", target="Roughness", non_color=True)
        add_image_texture(mat, "sunray150_smoked_translucent_guard_bump.png", target="Bump", non_color=True, strength=0.020)
    link_noise_to_bump(mat, scale=120.0, detail=8.0, strength=0.012, distance=0.00045)
    return mat


def make_translucent_guard_material() -> bpy.types.Material:
    mat = make_material("Sunray150_Texture_Smoked_Translucent_Prop_Guard", (0.22, 0.24, 0.25, 0.50), roughness=0.22, alpha=0.50)
    nodes = mat.node_tree.nodes
    bsdf = next((node for node in nodes if node.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        set_principled_input(bsdf, ("Alpha",), 0.46)
        set_principled_input(bsdf, ("Roughness",), 0.20)
        set_principled_input(bsdf, ("Metallic",), 0.0)
    mat.blend_method = "BLEND"
    mat.use_screen_refraction = True
    link_noise_to_bump(mat, scale=95.0, detail=7.0, strength=0.010, distance=0.00022)
    return mat


def make_battery_material() -> bpy.types.Material:
    mat = make_material("Sunray150_Texture_Black_Heatshrink_Battery", (0.010, 0.010, 0.009, 1.0), roughness=0.70)
    add_image_texture(mat, "sunray150_black_rubber_base.png", target="Base Color")
    add_image_texture(mat, "sunray150_black_rubber_roughness.png", target="Roughness", non_color=True)
    add_image_texture(mat, "sunray150_black_rubber_bump.png", target="Bump", non_color=True, strength=0.045)
    link_noise_to_bump(mat, scale=55.0, detail=9.0, strength=0.018, distance=0.0005)
    return mat


def realistic_materials() -> dict[str, bpy.types.Material]:
    global MATERIAL_CACHE
    if MATERIAL_CACHE is not None:
        return MATERIAL_CACHE
    MATERIAL_CACHE = {
        "carbon": make_carbon_material(),
        "matte_black_plastic": make_plastic_material("Sunray150_Texture_Matte_Black_Plastic", (0.020, 0.021, 0.020, 1.0), roughness=0.72),
        "satin_black_plastic": make_plastic_material("Sunray150_Texture_Satin_Black_Plastic", (0.048, 0.050, 0.049, 1.0), roughness=0.58),
        "translucent_guard": make_translucent_guard_material(),
        "dark_anodized": make_scratched_metal_material("Sunray150_Texture_Dark_Anodized_Aluminum", (0.060, 0.062, 0.060, 1.0), roughness=0.32, metallic=0.72),
        "steel": make_scratched_metal_material("Sunray150_Texture_Dark_Chromoly_Steel_Screws", (0.17, 0.165, 0.150, 1.0), roughness=0.24, metallic=0.90),
        "aluminum": make_warm_anodized_material("Sunray150_Texture_Gold_7075_Aluminum_Standoffs", (0.70, 0.43, 0.11, 1.0), roughness=0.31),
        "copper": make_scratched_metal_material("Sunray150_Texture_Copper_Motor_Windings", (0.78, 0.35, 0.12, 1.0), roughness=0.34, metallic=0.95),
        "motor": make_scratched_metal_material("Sunray150_Texture_Black_Motor_Bell", (0.025, 0.026, 0.025, 1.0), roughness=0.25, metallic=0.82),
        "prop": make_plastic_material("Sunray150_Texture_Smoked_Grey_Composite_Propeller", (0.23, 0.23, 0.22, 1.0), roughness=0.44),
        "rubber": make_plastic_material("Sunray150_Texture_Rubber_Cable_Black", (0.010, 0.010, 0.009, 1.0), roughness=0.88),
        "wire_red": make_plastic_material("Sunray150_Texture_Red_Silicone_Wire", (0.75, 0.045, 0.025, 1.0), roughness=0.62),
        "wire_blue": make_plastic_material("Sunray150_Texture_Blue_Silicone_Wire", (0.030, 0.12, 0.75, 1.0), roughness=0.62),
        "wire_yellow": make_plastic_material("Sunray150_Texture_Yellow_Silicone_Wire", (0.90, 0.64, 0.04, 1.0), roughness=0.62),
        "pcb_green": make_material("Sunray150_Texture_PCB_Green_Soldermask", (0.020, 0.185, 0.080, 1.0), roughness=0.46),
        "pcb_black": make_material("Sunray150_Texture_PCB_Black_Soldermask", (0.012, 0.014, 0.012, 1.0), roughness=0.48),
        "battery": make_battery_material(),
        "camera_body": make_plastic_material("Sunray150_Texture_USB_Camera_Dark_Housing", (0.018, 0.019, 0.018, 1.0), roughness=0.58),
        "camera_lens": make_material("Sunray150_Texture_Camera_Lens_Glass", (0.005, 0.009, 0.014, 0.72), roughness=0.04, metallic=0.0, alpha=0.72),
        "connector_shell": make_scratched_metal_material("Sunray150_Texture_USB_HDMI_Nickel_Shell", (0.44, 0.43, 0.39, 1.0), roughness=0.25, metallic=0.92),
        "connector_core": make_plastic_material("Sunray150_Texture_Connector_Black_Core", (0.008, 0.008, 0.008, 1.0), roughness=0.64),
        "tfmini_body": make_plastic_material("Sunray150_Texture_TF_Mini_Black_Sensor", (0.018, 0.018, 0.017, 1.0), roughness=0.52),
        "mid360_body": make_scratched_metal_material("MID360_Texture_Silver_Grey_Aluminum_Housing", (0.46, 0.455, 0.425, 1.0), roughness=0.26, metallic=0.62),
        "mid360_base": make_plastic_material("MID360_Texture_Black_Base", (0.020, 0.021, 0.021, 1.0), roughness=0.58),
        "mid360_window": make_material("MID360_Texture_Blue_Glossy_Optical_Window", (0.020, 0.130, 0.460, 0.70), roughness=0.035, alpha=0.70),
        "mid360_connector": make_plastic_material("MID360_Texture_Black_M12_Connector", (0.008, 0.008, 0.008, 1.0), roughness=0.66),
        "mid360_mount": make_plastic_material("MID360_Texture_Black_Mount_Inserts", (0.006, 0.006, 0.006, 1.0), roughness=0.74),
        "neutral": make_material("Sunray150_Texture_Neutral_Dark_Grey_Unclassified", (0.060, 0.060, 0.055, 1.0), roughness=0.66),
    }
    add_image_texture(MATERIAL_CACHE["pcb_black"], "sunray150_pcb_black_base.png", target="Base Color")
    add_image_texture(MATERIAL_CACHE["pcb_black"], "sunray150_pcb_black_roughness.png", target="Roughness", non_color=True)
    add_image_texture(MATERIAL_CACHE["pcb_black"], "sunray150_pcb_black_bump.png", target="Bump", non_color=True, strength=0.020)
    return MATERIAL_CACHE


def shade_smooth_if_reasonable(obj: bpy.types.Object) -> None:
    if obj.type != "MESH":
        return
    for poly in obj.data.polygons:
        poly.use_smooth = True


def add_mesh(name: str, verts: list[tuple[float, float, float]], faces: list[tuple[int, int, int]], mat: bpy.types.Material) -> bpy.types.Object:
    mesh = bpy.data.meshes.new(f"{prop.clean_name(name, 128)}_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(prop.clean_name(name, 128), mesh)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj


def pose_matrix(x: float, y: float, z: float, roll: float, pitch: float, yaw: float) -> Matrix:
    return Matrix.Translation((x, y, z)) @ Euler((roll, pitch, yaw), "XYZ").to_matrix().to_4x4()


def matrix_scale_xyz(x: float, y: float, z: float) -> Matrix:
    mat = Matrix.Identity(4)
    mat[0][0] = x
    mat[1][1] = y
    mat[2][2] = z
    return mat


def add_transformed_mesh(
    name: str,
    verts: list[tuple[float, float, float]],
    faces: list[tuple[int, int, int]],
    transform: Matrix,
    mat: bpy.types.Material,
) -> bpy.types.Object:
    transformed = []
    for v in verts:
        w = transform @ Vector(v)
        transformed.append((w.x, w.y, w.z))
    return add_mesh(name, transformed, faces, mat)


def add_sphere(name: str, loc: Vector, radius: float, mat: bpy.types.Material) -> None:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=radius, location=loc)
    obj = bpy.context.object
    obj.name = prop.clean_name(name, 96)
    obj.data.materials.append(mat)


def add_cylinder_between(name: str, a: Vector, b: Vector, radius: float, mat: bpy.types.Material) -> None:
    direction = b - a
    if direction.length < 1e-8:
        return
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=direction.length, location=(a + b) * 0.5)
    obj = bpy.context.object
    obj.name = prop.clean_name(name, 96)
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(mat)


def add_text(name: str, text: str, loc: Vector, size: float, mat: bpy.types.Material) -> None:
    curve = bpy.data.curves.new(prop.clean_name(name, 96), type="FONT")
    curve.body = text
    curve.size = size
    curve.align_x = "CENTER"
    obj = bpy.data.objects.new(prop.clean_name(name, 96), curve)
    obj.location = loc
    obj.rotation_euler = (math.radians(70), 0.0, 0.0)
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)


def add_label_plate(name: str, text: str, loc: Vector, size: float, mat: bpy.types.Material, *, rotation=(math.radians(90), 0.0, 0.0)) -> bpy.types.Object:
    curve = bpy.data.curves.new(prop.clean_name(name, 96), type="FONT")
    curve.body = text
    curve.size = size
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    obj = bpy.data.objects.new(prop.clean_name(name, 96), curve)
    obj.location = loc
    obj.rotation_euler = rotation
    obj.data.materials.append(mat)
    bpy.context.collection.objects.link(obj)
    return obj


def add_visual_detail_overlays() -> dict:
    """Add non-physical review decals that document intended texture details."""
    rmats = realistic_materials()
    white = make_material("Sunray150_Decal_White_Ink", (0.92, 0.92, 0.88, 1.0), roughness=0.42)
    black = make_material("Sunray150_Decal_Black_Ink", (0.004, 0.004, 0.004, 1.0), roughness=0.50)
    livox = make_material("Sunray150_Decal_Livox_Black", (0.002, 0.002, 0.002, 1.0), roughness=0.45)
    lens = rmats["camera_lens"]
    added = []

    added.append(add_label_plate("decal_mid360_livox_front", "LIVOX  MID-360", Vector((0.0, -0.020, 0.0805)), 0.0042, livox, rotation=(math.radians(75), 0.0, 0.0)).name)
    for x, y in [(0.0537, 0.0537), (-0.0537, 0.0537), (0.0537, -0.0537), (-0.0537, -0.0537)]:
        added.append(add_label_plate(f"decal_motor_yundrone_{x:.3f}_{y:.3f}", "YUN DRONE", Vector((x, y, -0.0005)), 0.0030, white, rotation=(0.0, 0.0, math.radians(45))).name)

    # Camera glass discs make front/down USB cameras visually readable even
    # when the DAE splits their detailed submeshes into many small BREP parts.
    for name, loc, rot in [
        ("front_usb_camera_lens_glass_overlay", Vector((0.0, 0.1032, 0.0185)), (math.radians(90), 0.0, 0.0)),
        ("bottom_usb_camera_lens_glass_overlay", Vector((0.0, 0.0145, -0.0263)), (0.0, 0.0, 0.0)),
    ]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.0062, depth=0.00045, location=loc, rotation=rot)
        obj = bpy.context.object
        obj.name = prop.clean_name(name, 96)
        assign_single_material(obj, lens)
        shade_smooth_if_reasonable(obj)
        added.append(obj.name)

    # Small colored cable sleeves follow the official photo cue without
    # changing the accepted aircraft geometry.
    cable_specs = [
        ("red_wire_hint", Vector((0.018, 0.044, 0.010)), Vector((0.044, 0.074, 0.012)), rmats["wire_red"]),
        ("blue_wire_hint", Vector((0.014, 0.039, 0.009)), Vector((0.040, 0.070, 0.011)), rmats["wire_blue"]),
        ("yellow_wire_hint", Vector((0.010, 0.034, 0.008)), Vector((0.036, 0.066, 0.010)), rmats["wire_yellow"]),
    ]
    for name, a, b, mat in cable_specs:
        add_cylinder_between(name, a, b, 0.00055, mat)
        added.append(name)

    return {
        "added_overlay_count": len(added),
        "added_overlays": added,
        "overlay_rule": "Review decals and cable hints are non-physical texture intent markers: LIVOX/MID-360 logo, YUN DRONE motor marks, USB camera lens glass, and colored cable sleeves. They do not alter accepted MID-360/propeller placement.",
    }


def aircraft_material_key(name: str) -> str:
    upper = name.upper()
    if "PROPELLER" in upper:
        return "prop"
    if "CIRCPATTERN" in upper:
        return "prop"
    if "PROTECTIVE_RING" in upper:
        return "translucent_guard"
    if "LAND_GEAR" in upper:
        return "translucent_guard"
    if "MID360_PROTECT_ARC" in upper:
        return "matte_black_plastic"
    if "SHOCK_ABSORBING" in upper or "RUBBER" in upper or "DAMP" in upper:
        return "rubber"
    if "AL_COLUMNS" in upper or "AL_COLUMS" in upper or "SPACER" in upper or "STAND" in upper or "COLUMN" in upper:
        return "aluminum"
    if "YUNDRONE_4S1P" in upper or "BATTERY" in upper:
        return "battery"
    if "FILL." in upper:
        return "carbon"
    if "STATOR WIRE" in upper or "COPPER" in upper:
        return "copper"
    if "MOTOR" in upper:
        return "motor"
    if "CABLE" in upper or "WIRE" in upper:
        if "RED" in upper:
            return "wire_red"
        if "BLUE" in upper:
            return "wire_blue"
        if "YELLOW" in upper:
            return "wire_yellow"
        if "USB" in upper or "HDMI" in upper or "CONNECTOR" in upper or "MANIFOLD_SOLID_BREP" in upper:
            return "connector_shell"
        return "rubber"
    if "USB" in upper or "HDMI" in upper or "CONNECTOR" in upper:
        if "PIN" in upper or "SHELL" in upper or "KÖRPER" in name or "KÃ" in upper or "MANIFOLD_SOLID_BREP" in upper:
            return "connector_shell"
        return "connector_core"
    if "FRONT_CAMERA" in upper or "BOTTOM_CAMERA" in upper:
        if "LENS" in upper:
            return "camera_lens"
        return "camera_body"
    if "RANGING_LIDAR_CAMERA_BASE" in upper or "CAMERA_SHIM" in upper:
        return "matte_black_plastic"
    if "TF MINI" in upper or "SENSOR TF" in upper:
        return "tfmini_body"
    if "ESC_SPEEDYBEE" in upper or "MAIN_BOARD" in upper or "PCBMODEL" in upper or "N150_ALLCATPART.1\\PART1" in upper:
        return "pcb_black"
    if "PIN" in upper:
        return "connector_shell"
    if "SCREW" in upper or "NUT" in upper or "WASHER" in upper or "BOLT" in upper:
        return "steel"
    if (
        "TOP_PANNEL" in upper
        or "BOT_PANNEL" in upper
        or upper.startswith("MAIN_STRUCTURE.")
        or "\\TOP" in upper
        or "\\BOTTOM" in upper
        or "\\PANNEL" in upper
        or "BATTERY_LIMITER" in upper
    ):
        return "carbon"
    if "MID360" in upper:
        return "satin_black_plastic"
    if "BATTERY_CLIP" in upper:
        return "satin_black_plastic"
    return "neutral"


def import_full_aircraft() -> dict:
    dae_objects = prop.dae_objects(prop.DAE_PATH)
    collections: dict[str, bpy.types.Collection] = {}
    rmats = realistic_materials()
    mats = rmats
    for cname in mats:
        coll = bpy.data.collections.new(f"aircraft_{cname}")
        bpy.context.scene.collection.children.link(coll)
        collections[cname] = coll

    counts = {k: 0 for k in mats}
    assignments: dict[str, str] = {}
    removed_propellers = []
    for src in dae_objects:
        if src.name in USER_CONFIRMED_PROPELLER_OBJECT_KEYS:
            removed_propellers.append(src.name)
            continue
        key = aircraft_material_key(src.name)
        obj = add_mesh(f"DAE_FULL_{src.name}", src.verts, src.faces, mats[key])
        assign_single_material(obj, mats[key])
        shade_smooth_if_reasonable(obj)
        bpy.context.collection.objects.unlink(obj)
        collections[key].objects.link(obj)
        counts[key] += 1
        assignments[obj.name] = key
    return {
        "source": str(prop.DAE_PATH),
        "object_count": len(dae_objects),
        "imported_object_count": len(dae_objects) - len(removed_propellers),
        "category_counts": counts,
        "component_material_assignments": assignments,
        "removed_user_confirmed_propellers": removed_propellers,
        "visibility_rule": "aircraft frame, cameras, boards, connectors, cables, brackets, protection arcs, and non-propeller parts are kept visible; only user-confirmed DAE propeller pattern objects are removed",
        "material_rule": "Component-name-driven material assignment based on the local DAE probe: carbon frame, plastic brackets/rings, black/green PCB, USB/HDMI shells, rubber cables, camera bodies/lenses, TF Mini, motor bell/copper windings, steel screws, aluminum standoffs.",
    }


def extract_propeller_screw_pairs() -> dict[str, dict]:
    dae_objects = prop.dae_objects(prop.DAE_PATH)
    screws = [o for o in dae_objects if "SCREW_BUTTON_HEAD_M2_8MM" in o.name]
    pairs: dict[str, dict] = {}
    for rotor_name, rotor_center, _ in ROTOR_POSES:
        nearest = sorted(screws, key=lambda o: (o.center - rotor_center).length)[:2]
        if len(nearest) != 2:
            raise RuntimeError(f"Cannot find two M2x8 propeller screws for {rotor_name}")
        a, b = nearest[0].center.copy(), nearest[1].center.copy()
        pairs[rotor_name] = {
            "screws": nearest,
            "points": (a, b),
            "center": (a + b) * 0.5,
            "distance_m": (a - b).length,
        }
    return pairs


def propeller_hole_fit_transform(screw_a: Vector, screw_b: Vector, flip_around_screw_axis: bool = False) -> tuple[Matrix, dict]:
    src_a = TRI_BLADE_LOCAL_SCREW_HOLES_MM[0]
    src_b = TRI_BLADE_LOCAL_SCREW_HOLES_MM[1]
    src_vec_m = (src_b - src_a) * 0.001
    dst_vec = screw_b - screw_a
    src_dist = src_vec_m.length
    dst_dist = dst_vec.length
    scale = dst_dist / src_dist if src_dist > 1e-12 else 1.0

    src_angle = math.atan2(src_vec_m.y, src_vec_m.x)
    dst_angle = math.atan2(dst_vec.y, dst_vec.x)
    yaw = dst_angle - src_angle
    local_mid_m = (src_a + src_b) * (0.5 * 0.001 * scale)
    rotated_mid = Matrix.Rotation(yaw, 4, "Z") @ local_mid_m.to_4d()
    # XY comes from the two screw centers. Z is an explicit user-reviewed audit
    # parameter because the screw-head/contact surface is visually audited in
    # Blender and should not be inferred from ambiguous STL surfaces.
    dst_mid = (screw_a + screw_b) * 0.5
    translation = Vector((dst_mid.x - rotated_mid.x, dst_mid.y - rotated_mid.y, dst_mid.z - rotated_mid.z))
    fitted_translation_z = translation.z
    translation.z = PROP_TARGET_TRANSLATION_Z_M
    base = Matrix.Translation(translation) @ Matrix.Rotation(yaw, 4, "Z")
    flip = Matrix.Rotation(math.pi, 4, "Y") if flip_around_screw_axis else Matrix.Identity(4)
    transform = base @ flip @ matrix_scale_xyz(0.001 * scale, 0.001 * scale, 0.001 * scale)
    return transform, {
        "source_hole_centers_mm": [[round(src_a.x, 6), round(src_a.y, 6), round(src_a.z, 6)], [round(src_b.x, 6), round(src_b.y, 6), round(src_b.z, 6)]],
        "source_hole_distance_m_after_base_scale": round(src_dist, 6),
        "target_screw_distance_m": round(dst_dist, 6),
        "scale_correction": round(scale, 6),
        "yaw_deg": round(math.degrees(yaw), 6),
        "flip_around_screw_axis": flip_around_screw_axis,
        "fitted_translation_z_before_user_override_m": round(fitted_translation_z, 6),
        "user_audited_base_translation_z_m": round(PROP_BASE_TRANSLATION_Z_M, 6),
        "user_audited_contact_plane_z_m": round(PROP_AUDITED_CONTACT_PLANE_Z_M, 6),
        "target_screw_plane_z_m": round(PROP_TARGET_SCREW_PLANE_Z_M, 6),
        "clearance_m": round(PROP_CLEARANCE_M, 6),
        "user_fine_tune_z_m": round(PROP_USER_FINE_TUNE_Z_M, 6),
        "user_requested_translation_z_m": round(PROP_TARGET_TRANSLATION_Z_M, 6),
        "translation_m": [round(translation.x, 6), round(translation.y, 6), round(translation.z, 6)],
    }


def object_world_bounds(objs: list[bpy.types.Object]) -> tuple[Vector, Vector]:
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
    return mn, mx


def find_mid360_base_mount_center(objs: list[bpy.types.Object]) -> dict:
    candidates = []
    for obj in objs:
        mn, mx = object_world_bounds([obj])
        size = mx - mn
        if size.x > 0.04 and size.y > 0.04 and size.z < 0.02 and abs(size.x - size.y) < 0.004:
            candidates.append((obj, mn, mx, size, (mn + mx) * 0.5))
    if not candidates:
        mn, mx = object_world_bounds(objs)
        return {
            "method": "fallback_full_bbox_base_center",
            "object": None,
            "center": Vector(((mn.x + mx.x) * 0.5, (mn.y + mx.y) * 0.5, mn.z)),
            "bbox_min": mn,
            "bbox_max": mx,
        }
    obj, mn, mx, size, center = max(candidates, key=lambda item: item[3].x * item[3].y)
    return {
        "method": "circular_base_mesh_center",
        "object": obj.name,
        "center": center,
        "bbox_min": mn,
        "bbox_max": mx,
    }


def mid360_mount_hole_objects(objs: list[bpy.types.Object]) -> list[bpy.types.Object]:
    out = []
    for obj in objs:
        if not obj.name.startswith("AUDIT_STANDALONE_MID360_"):
            continue
        suffix = obj.name.removeprefix("AUDIT_STANDALONE_MID360_")[:3]
        if suffix in {"000", "001", "002", "003"}:
            out.append(obj)
    if len(out) != 4:
        raise RuntimeError(f"Expected four MID-360 mount-hole objects 000..003, found {len(out)}")
    return sorted(out, key=lambda obj: obj.name)


def object_center(obj: bpy.types.Object) -> Vector:
    mn, mx = object_world_bounds([obj])
    return (mn + mx) * 0.5


def fit_mid360_holes_to_frame_holes(radar_objs: list[bpy.types.Object], frame_points: list[Vector]) -> dict:
    hole_objs = mid360_mount_hole_objects(radar_objs)
    radar_points = [object_center(obj) for obj in hole_objs]
    zero = Vector((0.0, 0.0, 0.0))
    frame_center = sum(frame_points, zero.copy()) / len(frame_points)
    radar_center = sum(radar_points, zero.copy()) / len(radar_points)
    frame_radius = math.sqrt(sum((p - frame_center).length_squared for p in frame_points) / len(frame_points))
    radar_radius = math.sqrt(sum((p - radar_center).length_squared for p in radar_points) / len(radar_points))
    scale = frame_radius / radar_radius if radar_radius > 1e-12 else 1.0
    translation = Vector(
        (
            frame_center.x - scale * radar_center.x,
            frame_center.y - scale * radar_center.y,
            0.0,
        )
    )
    for obj in radar_objs:
        for vertex in obj.data.vertices:
            p = obj.matrix_world @ vertex.co
            mapped = Vector((scale * p.x + translation.x, scale * p.y + translation.y, p.z * scale))
            vertex.co = obj.matrix_world.inverted() @ mapped
        obj.data.update()
    bpy.context.view_layer.update()
    fitted_points = [scale * p + translation for p in radar_points]
    return {
        "method": "direct_four_mount_hole_object_centers_000_001_002_003",
        "hole_object_names": [obj.name for obj in hole_objs],
        "radar_hole_centers_before_fit_m": [[round(p.x, 6), round(p.y, 6), round(p.z, 6)] for p in radar_points],
        "frame_hole_centers_m": [[round(p.x, 6), round(p.y, 6), round(p.z, 6)] for p in frame_points],
        "radar_center_before_fit_m": [round(radar_center.x, 6), round(radar_center.y, 6), round(radar_center.z, 6)],
        "frame_center_m": [round(frame_center.x, 6), round(frame_center.y, 6), round(frame_center.z, 6)],
        "uniform_scale": round(scale, 6),
        "xy_translation_m": [round(translation.x, 6), round(translation.y, 6), 0.0],
        "fitted_radar_hole_centers_m": [[round(p.x, 6), round(p.y, 6), round(p.z, 6)] for p in fitted_points],
        "radar_rms_radius_before_m": round(radar_radius, 6),
        "frame_rms_radius_m": round(frame_radius, 6),
    }


def import_and_place_mid360(mount_center: Vector, panel_top_z: float) -> dict:
    prefix = "AUDIT_STANDALONE_MID360"
    # Manual review requested rotating the previous yaw=180 deg pose by +90 deg.
    visual_yaw = math.radians(270.0)
    visual_transform = livox.pose_matrix(0, 0, 0, 0, 0, visual_yaw) @ livox.matrix_scale_xyz(MID360_VISUAL_SCALE, MID360_VISUAL_SCALE, MID360_VISUAL_SCALE)
    import_result = livox.import_dae(livox.MID360_DAE, prefix, visual_transform)
    radar_objs = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name.startswith(prefix)]
    if not radar_objs:
        raise RuntimeError("MID-360 import produced no mesh objects")

    hole_fit = fit_mid360_holes_to_frame_holes(radar_objs, [p for _, p in TOP_PANEL_MOUNT_HOLES])
    mn, mx = object_world_bounds(radar_objs)
    translation = Vector((0.0, 0.0, panel_top_z - mn.z))
    for obj in radar_objs:
        obj.location += translation
    bpy.context.view_layer.update()

    rmats = realistic_materials()
    mid360_material_rule = {
        "000": "mid360_mount",
        "001": "mid360_mount",
        "002": "mid360_mount",
        "003": "mid360_mount",
        "004": "dark_anodized",
        "005": "dark_anodized",
        "006": "dark_anodized",
        "007": "dark_anodized",
        "008": "mid360_connector",
        "009": "mid360_connector",
        "010": "mid360_connector",
        "011": "mid360_connector",
        "012": "mid360_connector",
        "013": "mid360_body",
        "014": "mid360_body",
        "015": "mid360_window",
        "016": "mid360_base",
        "017": "mid360_connector",
        "018": "mid360_mount",
        "019": "mid360_mount",
        "020": "mid360_mount",
        "021": "mid360_mount",
    }
    assigned_materials: dict[str, str] = {}
    for obj in radar_objs:
        suffix = obj.name.removeprefix(f"{prefix}_")[:3]
        mat_key = mid360_material_rule.get(suffix, "mid360_body")
        assign_single_material(obj, rmats[mat_key])
        shade_smooth_if_reasonable(obj)
        assigned_materials[obj.name] = mat_key

    bpy.context.view_layer.update()
    mn_after, mx_after = object_world_bounds(radar_objs)
    return {
        "source": str(livox.MID360_DAE),
        "import_result": import_result,
        "orientation_rule": "yaw=270deg; user requested rotating the previous yaw=180deg radar pose by +90deg for direction audit",
        "yaw_deg": 270.0,
        "scale": [round(MID360_VISUAL_SCALE, 6), round(MID360_VISUAL_SCALE, 6), round(MID360_VISUAL_SCALE, 6)],
        "scale_rule": "Import at base visual scale 1.2, then directly fit the four user-identified MID-360 mount-hole object centers 000..003 to the four user-selected frame holes.",
        "hole_fit": hole_fit,
        "placement_rule": "XY is fitted from the four named MID-360 mount-hole object centers; Z snaps full visual bottom to selected top-panel z plane.",
        "bbox_before": {"min": [round(mn.x, 6), round(mn.y, 6), round(mn.z, 6)], "max": [round(mx.x, 6), round(mx.y, 6), round(mx.z, 6)]},
        "translation_m": [round(translation.x, 6), round(translation.y, 6), round(translation.z, 6)],
        "bbox_after": {"min": [round(mn_after.x, 6), round(mn_after.y, 6), round(mn_after.z, 6)], "max": [round(mx_after.x, 6), round(mx_after.y, 6), round(mx_after.z, 6)]},
        "material_rule": "MID-360 uses per-submesh texture materials: 015 glossy blue optical window, 013/014 dark semi-metallic housing, 016 black base, 017 and rear details black M12 connector, 000..003 black mount inserts, 004..007 dark metal bosses.",
        "assigned_materials": assigned_materials,
    }


def import_and_place_tri_blade_propellers() -> dict:
    prop_verts, prop_faces = prop.read_stl(TRI_BLADE_PROP_STL)
    screw_pairs = extract_propeller_screw_pairs()
    rmats = realistic_materials()
    prop_mats = {"red": rmats["prop"], "blue": rmats["prop"]}
    coll = bpy.data.collections.new("tri_blade_propellers")
    bpy.context.scene.collection.children.link(coll)
    created = []
    for rotor_name, center, color_key in ROTOR_POSES:
        pair = screw_pairs[rotor_name]
        variants = [("normal", False)]
        if PROP_ORIENTATION_MODE == "candidates":
            variants.append(("flipped_around_screw_axis", True))
        elif PROP_ORIENTATION_MODE in {"flipped", "flip", "flipped_around_screw_axis"}:
            variants = [("flipped_around_screw_axis", True)]
        for variant_name, do_flip in variants:
            transform, fit = propeller_hole_fit_transform(pair["points"][0], pair["points"][1], do_flip)
            obj = add_transformed_mesh(
                f"TriBlade_{variant_name}_{rotor_name}_sunray_cw_stl",
                prop_verts,
                prop_faces,
                transform,
                prop_mats[color_key],
            )
            assign_single_material(obj, prop_mats[color_key])
            shade_smooth_if_reasonable(obj)
            if variant_name == "flipped_around_screw_axis" and PROP_ORIENTATION_MODE == "candidates":
                obj.location.z += 0.010
                obj.display_type = "TEXTURED"
            bpy.context.collection.objects.unlink(obj)
            coll.objects.link(obj)
            mn, mx = object_world_bounds([obj])
            created.append(
                {
                    "name": obj.name,
                    "variant": variant_name,
                    "rotor": rotor_name,
                    "sdf_rotor_center_m": [round(center.x, 6), round(center.y, 6), round(center.z, 6)],
                    "target_screw_names": [s.name for s in pair["screws"]],
                    "target_screw_centers_m": [
                        [round(p.x, 6), round(p.y, 6), round(p.z, 6)]
                        for p in pair["points"]
                    ],
                    "target_screw_mid_m": [round(pair["center"].x, 6), round(pair["center"].y, 6), round(pair["center"].z, 6)],
                    "fit": fit,
                    "z_policy": "User-audited face alignment: move measured propeller contact plane z=-0.021098m toward screw plane z=-0.0193m with 0.1mm nominal clearance, then fine-tune propellers upward by 0.15mm. XY screw-hole fit and flipped orientation are unchanged.",
                    "color": color_key,
                    "material": "black composite propeller; previous red/blue audit colors removed for realistic material review",
                    "review_offset_note": "flipped candidate is lifted +10mm only in candidates mode so both sides are visible simultaneously" if variant_name == "flipped_around_screw_axis" and PROP_ORIENTATION_MODE == "candidates" else "",
                    "bounds_min_m": [round(mn.x, 6), round(mn.y, 6), round(mn.z, 6)],
                    "bounds_max_m": [round(mx.x, 6), round(mx.y, 6), round(mx.z, 6)],
                }
            )
    return {
        "source": str(TRI_BLADE_PROP_STL),
        "source_rule": "Use sunray150_with_mid360/meshes/sunray_cw.stl as the required three-blade propeller source; DAE propeller objects remain deleted.",
        "placement_rule": "Fit the two detected STL screw holes (0,+/-2.5,2.5 mm) to each DAE M2x8 screw pair. Scale correction is applied only from screw-hole distance ratio.",
        "z_rule": "Final propeller transform translation.z is computed from user-audited planes and fine tune: base -0.0161m + ((-0.0193m + 0.0001m) - -0.021098m) + 0.00015m = -0.014052m.",
        "orientation_mode": PROP_ORIENTATION_MODE,
        "orientation_warning": "Hole fitting alone does not decide propeller front/back side. User manually accepted flipped_around_screw_axis; candidates mode remains available for future review.",
        "screw_source": "DAE SCREW_BUTTON_HEAD_M2_8MM.1..8 nearest two screws per SDF rotor center",
        "triangles_per_propeller": len(prop_faces),
        "created": created,
        "status": "manual_review_required_for_hole/shaft alignment",
    }


def apply_audit_view_visibility() -> dict:
    if MATERIAL_REVIEW and not SHOW_AUDIT_MARKERS:
        hidden_markers = []
        marker_prefixes = (
            "selected_top_panel_mount_",
            "selected_mount_rectangle_edge_",
            "selected_mount_center",
            "label_",
            "full_assembly_audit_label",
        )
        for obj in bpy.context.scene.objects:
            if obj.name.startswith(marker_prefixes):
                obj.hide_viewport = True
                obj.hide_render = True
                hidden_markers.append(obj.name)
        if AUDIT_VIEW != "radar_mount":
            return {
                "audit_view": AUDIT_VIEW,
                "visibility": "realistic material review: full assembly visible; audit markers hidden by default",
                "material_review": True,
                "show_audit_markers": SHOW_AUDIT_MARKERS,
                "hidden_marker_count": len(hidden_markers),
            }

    if AUDIT_VIEW != "radar_mount":
        return {
            "audit_view": AUDIT_VIEW,
            "visibility": "full assembly visible",
            "material_review": MATERIAL_REVIEW,
            "show_audit_markers": SHOW_AUDIT_MARKERS,
        }

    visible_collections = {"aircraft_carbon", "aircraft_bracket"}
    visible_name_prefixes = ("AUDIT_STANDALONE_MID360",)
    hidden = []
    visible = []
    for obj in bpy.context.scene.objects:
        keep = (
            any(coll.name in visible_collections for coll in obj.users_collection)
            or obj.name.startswith(visible_name_prefixes)
            or obj.type in {"CAMERA", "LIGHT"}
        )
        obj.hide_viewport = not keep
        obj.hide_render = not keep
        if keep:
            visible.append(obj.name)
        else:
            hidden.append(obj.name)
    return {
        "audit_view": AUDIT_VIEW,
        "visibility": "radar mount review: only aircraft carbon/bracket collections, standalone MID-360, camera, and light are visible",
        "visible_collection_names": sorted(visible_collections),
        "visible_name_prefixes": list(visible_name_prefixes),
        "visible_object_count": len(visible),
        "hidden_object_count": len(hidden),
    }


def frame_camera() -> dict:
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
    extent = max((mx - mn).x, (mx - mn).y, (mx - mn).z, 0.22)
    light_data = bpy.data.lights.new("FullMid360Audit_Key_Light", type="AREA")
    light_data.energy = 1800
    light_data.size = extent * 0.75
    light = bpy.data.objects.new("FullMid360Audit_Key_Light", light_data)
    light.location = center + Vector((extent * 0.45, -extent * 0.55, extent * 0.9))
    bpy.context.collection.objects.link(light)
    fill_data = bpy.data.lights.new("FullMid360Audit_Soft_Fill_Light", type="AREA")
    fill_data.energy = 350
    fill_data.size = extent * 1.2
    fill = bpy.data.objects.new("FullMid360Audit_Soft_Fill_Light", fill_data)
    fill.location = center + Vector((-extent * 0.75, extent * 0.55, extent * 0.45))
    bpy.context.collection.objects.link(fill)
    cam_data = bpy.data.cameras.new("FullMid360Audit_Camera")
    cam = bpy.data.objects.new("FullMid360Audit_Camera", cam_data)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = extent * 1.05
    cam.location = center + Vector((extent * 0.45, -extent * 0.95, extent * 0.55))
    cam.rotation_euler = (center - cam.location).to_track_quat("-Z", "Y").to_euler()
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return {
        "active_camera": cam.name,
        "bounds_min": [round(mn.x, 6), round(mn.y, 6), round(mn.z, 6)],
        "bounds_max": [round(mx.x, 6), round(mx.y, 6), round(mx.z, 6)],
        "extent": round(extent, 6),
        "lighting": "area key light plus soft fill light for visible reflections on glass, metal, and carbon-fiber materials",
    }


def main() -> None:
    start = time.time()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    reset_scene()

    aircraft_info = import_full_aircraft()
    hole_mat = make_material("Selected_TopPanel_Holes_Gold", (1.0, 0.68, 0.0, 1.0))
    line_mat = make_material("Mount_Rectangle_Green", (0.0, 0.85, 0.15, 1.0))
    text_mat = make_material("Audit_Text_Dark", (0.02, 0.02, 0.02, 1.0))

    mount_center = sum((p for _, p in TOP_PANEL_MOUNT_HOLES), Vector()) / len(TOP_PANEL_MOUNT_HOLES)
    panel_top_z = max(p.z for _, p in TOP_PANEL_MOUNT_HOLES)
    for label, point in TOP_PANEL_MOUNT_HOLES:
        add_sphere(f"selected_top_panel_mount_{label}", point, 0.0016, hole_mat)
        add_text(f"label_{label}", label, point + Vector((0.0, 0.0, 0.006)), 0.0032, text_mat)

    ordered_points = [p for _, p in TOP_PANEL_MOUNT_HOLES]
    for idx, (a, b) in enumerate(
        [
            (ordered_points[0], ordered_points[1]),
            (ordered_points[1], ordered_points[2]),
            (ordered_points[2], ordered_points[3]),
            (ordered_points[3], ordered_points[0]),
        ]
    ):
        add_cylinder_between(f"selected_mount_rectangle_edge_{idx}", a, b, 0.00035, line_mat)
    add_sphere("selected_mount_center", mount_center, 0.0021, line_mat)

    radar_info = import_and_place_mid360(mount_center, panel_top_z)
    propeller_info = import_and_place_tri_blade_propellers()
    detail_overlay_info = add_visual_detail_overlays()
    add_text(
        "full_assembly_audit_label",
        "DAE frame kept visible. Added MID-360 and official tri-blade propellers.",
        mount_center + Vector((0.0, -0.075, 0.07)),
        0.005,
        text_mat,
    )
    visibility_info = apply_audit_view_visibility()

    camera_info = frame_camera()
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.world.color = (0.86, 0.88, 0.90)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))

    manifest = {
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "purpose": "Full Sunray150 150.dae visible plus standalone Livox MID-360 mount audit. This is a manual review scene, not a final runtime asset.",
        "aircraft": aircraft_info,
        "mount_reference": {
            "source": "user-reviewed TOP_PANNEL hole-loop groups from sunray150_top_panel_hole_pick_manifest.json",
            "holes": [{"label": label, "center_m": [round(p.x, 6), round(p.y, 6), round(p.z, 6)]} for label, p in TOP_PANEL_MOUNT_HOLES],
            "mount_center_m": [round(mount_center.x, 6), round(mount_center.y, 6), round(mount_center.z, 6)],
            "rectangle_size_m": [0.036, 0.048],
            "panel_top_z_m": round(panel_top_z, 6),
        },
        "mid360": radar_info,
        "propellers": propeller_info,
        "material_detail_overlays": detail_overlay_info,
        "visibility": visibility_info,
        "review_instruction": "User audits radar x/y/z placement, connector direction, radar scale, and later four official tri-blade propeller shaft/hole alignment. In radar_mount view, non-radar clutter and propellers are hidden only for review.",
        "camera": camera_info,
        "elapsed_sec": round(time.time() - start, 3),
        "outputs": {"blend": str(OUT_BLEND), "manifest": str(OUT_MANIFEST)},
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2)[:8000])


if __name__ == "__main__":
    main()
