#!/usr/bin/env python3
"""Bind reviewed Sunray150 materials to the runtime UE StaticMesh.

The reviewed Blender/FBX export already carries material slot names such as
Sunray150_Texture_CarbonFiber_Woven_Graphite and
MID360_Texture_Satin_Silver_Grey_Coated_Metal_Housing. A prior UE import kept
those slot names but bound old MoSim_* fallback materials or WorldGridMaterial.
This script creates explicit UE material assets from the reviewed texture maps
and assigns them by StaticMesh slot name.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from run_scene_truth_export import (
    ENGINE_ROOT_BY_VERSION,
    resolve_editor_cmd,
    tail_lines,
    to_windows_path,
)


ROOT = Path(__file__).resolve().parents[2]
RENDERER_UPROJECT = ROOT / "UE5/MoSimSceneLibrary/MoSimSceneLibrary.uproject"
DEFAULT_ASSET_PATH = "/Game/Sunray150/sunray150_with_mid360_textured"
TEXTURE_DIR = ROOT / "UE5/MoSimSceneLibrary/SourceAssets/Sunray150/Textures"
UE_TEXTURE_DIR = "/Game/Sunray150/Textures"
UE_MATERIAL_DIR = "/Game/Sunray150/Materials"


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def output_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


MATERIAL_CONFIG: dict[str, dict[str, object]] = {
    "MID360_Texture_Black_Base": {
        "family": "black_rubber",
        "base": "sunray150_black_rubber_base.png",
        "roughness": "sunray150_black_rubber_roughness.png",
        "normal": "sunray150_black_rubber_bump.png",
        "metallic": 0.02,
        "roughness_default": 0.72,
    },
    "MID360_Texture_Black_M12_Connector": {
        "family": "black_rubber",
        "base": "sunray150_black_rubber_base.png",
        "roughness": "sunray150_black_rubber_roughness.png",
        "normal": "sunray150_black_rubber_bump.png",
        "metallic": 0.0,
        "roughness_default": 0.68,
    },
    "MID360_Texture_Black_Mount_Inserts": {
        "family": "dark_metal",
        "base": "sunray150_dark_anodized_metal_base.png",
        "roughness": "sunray150_dark_anodized_metal_roughness.png",
        "normal": "sunray150_dark_anodized_metal_bump.png",
        "metallic": 0.65,
        "roughness_default": 0.42,
    },
    "MID360_Texture_Dark_Blue_Mirror_Coated_Optical_Dome": {
        "family": "mid360_window",
        "base": "mid360_blue_optical_window_base.png",
        "roughness": "mid360_blue_optical_window_roughness.png",
        "normal": "mid360_blue_optical_window_bump.png",
        "metallic": 0.05,
        "roughness_default": 0.18,
        "specular": 0.85,
    },
    "MID360_Texture_Satin_Black_Protection_Frame": {
        "family": "dark_metal",
        "base": "sunray150_dark_anodized_metal_base.png",
        "roughness": "sunray150_dark_anodized_metal_roughness.png",
        "normal": "sunray150_dark_anodized_metal_bump.png",
        "metallic": 0.45,
        "roughness_default": 0.58,
    },
    "MID360_Texture_Satin_Silver_Grey_Coated_Metal_Housing": {
        "family": "mid360_silver",
        "base": "mid360_silver_grey_aluminum_base.png",
        "roughness": "mid360_silver_grey_aluminum_roughness.png",
        "normal": "mid360_silver_grey_aluminum_bump.png",
        "metallic": 0.72,
        "roughness_default": 0.38,
    },
    "Mount_Rectangle_Green": {
        "family": "mount_debug_green",
        "color": [0.05, 0.35, 0.10, 1.0],
        "metallic": 0.0,
        "roughness_default": 0.55,
    },
    "Selected_TopPanel_Holes_Gold": {
        "family": "gold_aluminum",
        "base": "sunray150_gold_anodized_aluminum_base.png",
        "roughness": "sunray150_gold_anodized_aluminum_roughness.png",
        "normal": "sunray150_gold_anodized_aluminum_bump.png",
        "metallic": 0.85,
        "roughness_default": 0.35,
    },
    "Audit_Text_Dark": {
        "family": "text_dark",
        "color": [0.01, 0.01, 0.01, 1.0],
        "metallic": 0.0,
        "roughness_default": 0.72,
    },
    "Sunray150_Texture_Black_Heatshrink_Battery": {
        "family": "battery_heatshrink",
        "base": "sunray150_battery_heatshrink_base.png",
        "roughness": "sunray150_battery_heatshrink_roughness.png",
        "normal": "sunray150_battery_heatshrink_bump.png",
        "metallic": 0.0,
        "roughness_default": 0.62,
    },
    "Sunray150_Texture_Black_Motor_Bell": {
        "family": "dark_metal",
        "base": "sunray150_dark_anodized_metal_base.png",
        "roughness": "sunray150_dark_anodized_metal_roughness.png",
        "normal": "sunray150_dark_anodized_metal_bump.png",
        "metallic": 0.7,
        "roughness_default": 0.38,
    },
    "Sunray150_Texture_CarbonFiber_Woven_Graphite": {
        "family": "carbon_fiber",
        "base": "sunray150_carbon_fiber_base.png",
        "roughness": "sunray150_carbon_fiber_roughness.png",
        "normal": "sunray150_carbon_fiber_bump.png",
        "metallic": 0.0,
        "roughness_default": 0.46,
        "specular": 0.35,
    },
    "Sunray150_Texture_Clear_Liuli_Glass_Prop_Guard": {
        "family": "smoked_guard",
        "base": "sunray150_smoked_translucent_guard_base.png",
        "roughness": "sunray150_smoked_translucent_guard_roughness.png",
        "normal": "sunray150_smoked_translucent_guard_bump.png",
        "metallic": 0.0,
        "roughness_default": 0.16,
        "alpha": 0.42,
    },
    "Sunray150_Texture_Clear_Liuli_Glass_Propeller": {
        "family": "smoked_propeller",
        "base": "sunray150_smoked_propeller_base.png",
        "roughness": "sunray150_smoked_propeller_roughness.png",
        "normal": "sunray150_smoked_propeller_bump.png",
        "metallic": 0.0,
        "roughness_default": 0.12,
        "alpha": 0.38,
    },
    "Sunray150_Texture_Copper_Motor_Windings": {
        "family": "copper_windings",
        "color": [0.72, 0.30, 0.08, 1.0],
        "metallic": 0.9,
        "roughness_default": 0.32,
    },
    "Sunray150_Texture_Dark_Anodized_Aluminum": {
        "family": "dark_metal",
        "base": "sunray150_dark_anodized_metal_base.png",
        "roughness": "sunray150_dark_anodized_metal_roughness.png",
        "normal": "sunray150_dark_anodized_metal_bump.png",
        "metallic": 0.7,
        "roughness_default": 0.42,
    },
    "Sunray150_Texture_Dark_Chromoly_Steel_Screws": {
        "family": "dark_metal",
        "base": "sunray150_dark_anodized_metal_base.png",
        "roughness": "sunray150_dark_anodized_metal_roughness.png",
        "normal": "sunray150_dark_anodized_metal_bump.png",
        "metallic": 0.9,
        "roughness_default": 0.32,
    },
    "Sunray150_Texture_Gold_7075_Aluminum_Standoffs": {
        "family": "gold_aluminum",
        "base": "sunray150_gold_anodized_aluminum_base.png",
        "roughness": "sunray150_gold_anodized_aluminum_roughness.png",
        "normal": "sunray150_gold_anodized_aluminum_bump.png",
        "metallic": 0.85,
        "roughness_default": 0.35,
    },
    "Sunray150_Texture_Matte_Black_Plastic": {
        "family": "camera_polymer",
        "base": "sunray150_camera_black_polymer_base.png",
        "roughness": "sunray150_camera_black_polymer_roughness.png",
        "normal": "sunray150_camera_black_polymer_bump.png",
        "metallic": 0.0,
        "roughness_default": 0.72,
    },
    "Sunray150_Texture_N150_Black_Cooling_Fan": {
        "family": "camera_polymer",
        "base": "sunray150_camera_black_polymer_base.png",
        "roughness": "sunray150_camera_black_polymer_roughness.png",
        "normal": "sunray150_camera_black_polymer_bump.png",
        "metallic": 0.0,
        "roughness_default": 0.65,
    },
    "Sunray150_Texture_N150_M2_Storage_Module": {
        "family": "nickel_connector",
        "base": "sunray150_nickel_connector_base.png",
        "roughness": "sunray150_nickel_connector_roughness.png",
        "normal": "sunray150_nickel_connector_bump.png",
        "metallic": 0.75,
        "roughness_default": 0.38,
    },
    "Sunray150_Texture_PCB_Black_Soldermask": {
        "family": "pcb_black",
        "base": "sunray150_pcb_black_base.png",
        "roughness": "sunray150_pcb_black_roughness.png",
        "normal": "sunray150_pcb_black_bump.png",
        "metallic": 0.0,
        "roughness_default": 0.54,
    },
    "Sunray150_Texture_Rubber_Cable_Black": {
        "family": "black_rubber",
        "base": "sunray150_black_rubber_base.png",
        "roughness": "sunray150_black_rubber_roughness.png",
        "normal": "sunray150_black_rubber_bump.png",
        "metallic": 0.0,
        "roughness_default": 0.68,
    },
    "Sunray150_Texture_TF_Mini_Black_Sensor": {
        "family": "camera_polymer",
        "base": "sunray150_camera_black_polymer_base.png",
        "roughness": "sunray150_camera_black_polymer_roughness.png",
        "normal": "sunray150_camera_black_polymer_bump.png",
        "metallic": 0.0,
        "roughness_default": 0.68,
    },
    "Sunray150_Texture_USB_Camera_Matte_Black_Housing": {
        "family": "camera_polymer",
        "base": "sunray150_camera_black_polymer_base.png",
        "roughness": "sunray150_camera_black_polymer_roughness.png",
        "normal": "sunray150_camera_black_polymer_bump.png",
        "metallic": 0.0,
        "roughness_default": 0.72,
    },
    "Sunray150_Texture_USB_HDMI_Nickel_Shell": {
        "family": "nickel_connector",
        "base": "sunray150_nickel_connector_base.png",
        "roughness": "sunray150_nickel_connector_roughness.png",
        "normal": "sunray150_nickel_connector_bump.png",
        "metallic": 0.75,
        "roughness_default": 0.38,
    },
}


def write_editor_script(
    script_path: Path,
    *,
    asset_path: str,
    texture_dir: Path,
    evidence_path: Path,
) -> None:
    asset_name = asset_path.rsplit("/", 1)[-1]
    object_path = asset_path + "." + asset_name
    config_json = json.dumps(MATERIAL_CONFIG, ensure_ascii=False, sort_keys=True)
    source = f"""
import json
from pathlib import Path
import unreal

asset_path = {asset_path!r}
object_path = {object_path!r}
texture_dir = Path({to_windows_path(texture_dir)!r})
ue_texture_dir = {UE_TEXTURE_DIR!r}
ue_material_dir = {UE_MATERIAL_DIR!r}
evidence_path = Path({to_windows_path(evidence_path)!r})
material_config = json.loads({config_json!r})

asset_lib = unreal.EditorAssetLibrary
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary

for directory in (ue_texture_dir, ue_material_dir):
    if not asset_lib.does_directory_exist(directory):
        asset_lib.make_directory(directory)

def load_or_import_texture(filename):
    source = texture_dir / filename
    if not source.exists():
        raise RuntimeError("Missing reviewed texture: " + str(source))
    dest_name = source.stem
    object_path = ue_texture_dir + "/" + dest_name + "." + dest_name
    existing = unreal.load_asset(object_path)
    if existing:
        return existing
    task = unreal.AssetImportTask()
    task.filename = str(source)
    task.destination_path = ue_texture_dir
    task.destination_name = dest_name
    task.automated = True
    task.save = True
    task.replace_existing = True
    asset_tools.import_asset_tasks([task])
    texture = unreal.load_asset(object_path)
    if not texture:
        raise RuntimeError("Failed to import texture: " + str(source))
    return texture

def safe_set(obj, prop, value):
    try:
        obj.set_editor_property(prop, value)
        return True
    except Exception:
        return False

def expression_input(expr, names):
    for name in names:
        if hasattr(expr, "get_editor_property"):
            try:
                inputs = expr.get_editor_property("inputs")
                for item in inputs:
                    if str(getattr(item, "input_name", "")) == name:
                        return name
            except Exception:
                pass
    return names[0]

def scalar_expr(material, value, x, y):
    expr = mel.create_material_expression(material, unreal.MaterialExpressionConstant, x, y)
    safe_set(expr, "r", float(value))
    return expr

def color_expr(material, rgba, x, y):
    expr = mel.create_material_expression(material, unreal.MaterialExpressionConstant4Vector, x, y)
    safe_set(expr, "constant", unreal.LinearColor(float(rgba[0]), float(rgba[1]), float(rgba[2]), float(rgba[3])))
    return expr

def texture_sample(material, texture, x, y):
    expr = mel.create_material_expression(material, unreal.MaterialExpressionTextureSample, x, y)
    safe_set(expr, "texture", texture)
    return expr

def connect_prop(material, expr, out_name, prop_name):
    prop = getattr(unreal.MaterialProperty, prop_name, None)
    if prop is None:
        prop = getattr(unreal, prop_name, None)
    if prop is None:
        return False
    try:
        return bool(mel.connect_material_property(expr, out_name, prop))
    except Exception:
        return False

def create_or_update_material(slot_name, cfg):
    mat_obj_path = ue_material_dir + "/" + slot_name + "." + slot_name
    material = unreal.load_asset(mat_obj_path)
    if not material:
        material = asset_tools.create_asset(slot_name, ue_material_dir, unreal.Material, unreal.MaterialFactoryNew())
    if not material:
        raise RuntimeError("Failed to create material " + mat_obj_path)

    mel.delete_all_material_expressions(material)

    x = -760
    if "base" in cfg:
        base_tex = load_or_import_texture(cfg["base"])
        base = texture_sample(material, base_tex, x, -220)
        connect_prop(material, base, "RGB", "MP_BASE_COLOR")
    else:
        base = color_expr(material, cfg.get("color", [0.03, 0.03, 0.03, 1.0]), x, -220)
        connect_prop(material, base, "", "MP_BASE_COLOR")

    if "roughness" in cfg:
        rough_tex = load_or_import_texture(cfg["roughness"])
        rough = texture_sample(material, rough_tex, x, 120)
        connect_prop(material, rough, "R", "MP_ROUGHNESS")
    else:
        rough = scalar_expr(material, cfg.get("roughness_default", 0.55), x, 120)
        connect_prop(material, rough, "", "MP_ROUGHNESS")

    # The reviewed Blender scene uses grayscale bump/height maps. Importing
    # those directly as UE Normal samples makes D3D compilation fall back to
    # Default Material. Keep the texture asset imported, but do not wire it to
    # MP_NORMAL until a true tangent-space normal map is generated.
    if "normal" in cfg:
        normal_tex = load_or_import_texture(cfg["normal"])
        safe_set(normal_tex, "srgb", False)

    metallic = scalar_expr(material, cfg.get("metallic", 0.0), x, 260)
    connect_prop(material, metallic, "", "MP_METALLIC")

    if "specular" in cfg:
        spec = scalar_expr(material, cfg.get("specular", 0.5), x, 340)
        connect_prop(material, spec, "", "MP_SPECULAR")

    if "alpha" in cfg:
        alpha_value = float(cfg.get("alpha", 1.0))
        safe_set(material, "blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
        safe_set(material, "two_sided", True)
        alpha = scalar_expr(material, alpha_value, x, 500)
        connect_prop(material, alpha, "", "MP_OPACITY")
    else:
        safe_set(material, "blend_mode", unreal.BlendMode.BLEND_OPAQUE)
        safe_set(material, "two_sided", False)

    safe_set(material, "use_material_attributes", False)
    mel.recompile_material(material)
    asset_lib.save_asset(mat_obj_path, only_if_is_dirty=False)
    return material

mesh = unreal.load_asset(object_path)
if not mesh:
    raise RuntimeError("StaticMesh asset not found: " + object_path)

static_materials = list(mesh.get_editor_property("static_materials"))
bindings = []
created = []
missing_slots = []
for index, entry in enumerate(static_materials):
    slot_name = str(getattr(entry, "material_slot_name", ""))
    cfg = material_config.get(slot_name)
    if not cfg:
        missing_slots.append(slot_name)
        continue
    mat = create_or_update_material(slot_name, cfg)
    entry.material_interface = mat
    static_materials[index] = entry
    bindings.append({{
        "index": index,
        "slot_name": slot_name,
        "material_path": str(mat.get_path_name()),
        "family": cfg.get("family", ""),
    }})
    created.append(str(mat.get_path_name()))

mesh.set_editor_property("static_materials", static_materials)
asset_lib.save_asset(object_path, only_if_is_dirty=False)
asset_lib.save_directory("/Game/Sunray150", only_if_is_dirty=False, recursive=True)

after = []
for index, entry in enumerate(mesh.get_editor_property("static_materials")):
    mat = getattr(entry, "material_interface", None)
    after.append({{
        "index": index,
        "slot_name": str(getattr(entry, "material_slot_name", "")),
        "material_name": str(mat.get_name()) if mat else "",
        "material_path": str(mat.get_path_name()) if mat else "",
    }})

payload = {{
    "schema": "mosim.sunray150_runtime_material_binding_fix.v1",
    "ok": True,
    "asset_path": asset_path,
    "object_path": object_path,
    "texture_dir": str(texture_dir),
    "ue_texture_dir": ue_texture_dir,
    "ue_material_dir": ue_material_dir,
    "configured_material_count": len(material_config),
    "bound_slot_count": len(bindings),
    "missing_config_slots": missing_slots,
    "bindings": bindings,
    "after_slots": after,
    "claim_boundary": [
        "UE StaticMesh material binding fix only.",
        "Does not alter geometry, camera, MWORKS, ROS2, controller, planner, or runtime truth.",
        "Still requires runtime screenshot and user visual review before final material acceptance."
    ],
}}
evidence_path.parent.mkdir(parents=True, exist_ok=True)
evidence_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
"""
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(source.strip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-path", default=DEFAULT_ASSET_PATH)
    parser.add_argument("--engine-version", default="5.5")
    parser.add_argument("--engine-root", type=Path, default=None)
    parser.add_argument("--editor-cmd", type=Path, default=None)
    parser.add_argument(
        "--script-path",
        type=Path,
        default=ROOT / "Results/tmp/fix_sunray150_runtime_material_bindings_editor.py",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=ROOT / "Results/tmp/fix_sunray150_runtime_material_bindings_latest.json",
    )
    parser.add_argument("--log-output", type=Path, default=None)
    parser.add_argument("--timeout-seconds", type=float, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    script_path = args.script_path if args.script_path.is_absolute() else ROOT / args.script_path
    evidence_path = args.json_output if args.json_output.is_absolute() else ROOT / args.json_output
    engine_root = args.engine_root or ENGINE_ROOT_BY_VERSION.get(args.engine_version)
    editor_cmd = resolve_editor_cmd(RENDERER_UPROJECT, engine_root, args.editor_cmd)

    write_editor_script(
        script_path,
        asset_path=args.asset_path,
        texture_dir=TEXTURE_DIR,
        evidence_path=evidence_path,
    )
    command = [
        str(editor_cmd),
        to_windows_path(RENDERER_UPROJECT),
        "-run=pythonscript",
        f"-script={to_windows_path(script_path)}",
        "-nosplash",
        "-NoSound",
        "-stdout",
        "-FullStdOutLogOutput",
        "-unattended",
    ]
    payload: dict[str, Any] = {
        "renderer_uproject": rel(RENDERER_UPROJECT),
        "asset_path": args.asset_path,
        "editor_cmd": to_windows_path(editor_cmd),
        "script_path": rel(script_path),
        "json_output": rel(evidence_path),
        "command": command,
    }
    try:
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=args.timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        if args.log_output:
            log_path = args.log_output if args.log_output.is_absolute() else ROOT / args.log_output
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log_path.write_text(output_text(exc.stdout) + output_text(exc.stderr), encoding="utf-8", errors="replace")
            payload["log_output"] = rel(log_path)
            payload["tail"] = tail_lines(log_path, 80)
        payload.update({"ok": False, "reason": "timeout", "timeout_seconds": args.timeout_seconds})
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 124
    if args.log_output:
        log_path = args.log_output if args.log_output.is_absolute() else ROOT / args.log_output
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text((completed.stdout or "") + (completed.stderr or ""), encoding="utf-8", errors="replace")
        payload["log_output"] = rel(log_path)
        payload["tail"] = tail_lines(log_path, 80)
    if evidence_path.exists():
        payload["binding_fix"] = json.loads(evidence_path.read_text(encoding="utf-8"))
    payload["returncode"] = completed.returncode
    payload["ok"] = completed.returncode == 0 and bool(payload.get("binding_fix", {}).get("ok"))
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["ok"] else completed.returncode or 1


if __name__ == "__main__":
    raise SystemExit(main())
